#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/lan-drop"
CONFIG_DIR="/etc/lan-drop"
DATA_DIR="/var/lib/lan-drop"
SERVICE_FILE="/etc/systemd/system/lan-drop.service"
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

fail() {
    printf 'Error: %s\n' "$1" >&2
    exit 1
}

[[ ${EUID} -eq 0 ]] || fail "run this installer with sudo: sudo ./install.sh"
command -v apt-get >/dev/null || fail "this installer currently supports Ubuntu and Linux Mint"
[[ -t 0 ]] || fail "an interactive terminal is required to enter the LAN Drop PIN"

printf 'LAN Drop V1 installer (Ubuntu 24.04 / Linux Mint 22)\n\n'

while true; do
    read -r -s -p "Choose a 6-digit PIN: " lan_drop_pin
    printf '\n'
    [[ ${lan_drop_pin} =~ ^[0-9]{6}$ ]] || {
        printf 'The PIN must contain exactly 6 digits.\n'
        continue
    }

    read -r -s -p "Confirm the PIN: " pin_confirmation
    printf '\n'
    [[ ${lan_drop_pin} == "${pin_confirmation}" ]] && break
    printf 'The PINs did not match. Try again.\n'
done

printf '\nInstalling system dependencies...\n'
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-venv openssl

if ! getent group lan-drop >/dev/null; then
    groupadd --system lan-drop
fi

if ! id lan-drop >/dev/null 2>&1; then
    useradd --system --gid lan-drop --home-dir "${DATA_DIR}" --shell /usr/sbin/nologin lan-drop
fi

install -d -o root -g root -m 0755 "${APP_DIR}"
install -d -o root -g lan-drop -m 0750 "${CONFIG_DIR}" "${CONFIG_DIR}/tls"
install -d -o root -g root -m 0755 "${DATA_DIR}"
install -d -o lan-drop -g lan-drop -m 0750 "${DATA_DIR}/uploads"

install -o root -g root -m 0644 "${SOURCE_DIR}/app.py" "${APP_DIR}/app.py"
install -o root -g root -m 0644 "${SOURCE_DIR}/requirements.txt" "${APP_DIR}/requirements.txt"

python3 -m venv "${APP_DIR}/.venv"
"${APP_DIR}/.venv/bin/pip" install --disable-pip-version-check -r "${APP_DIR}/requirements.txt"

lan_drop_secret="$(openssl rand -hex 32)"
umask 0077
cat > "${CONFIG_DIR}/lan-drop.env" <<EOF
LAN_DROP_PIN=${lan_drop_pin}
LAN_DROP_SECRET=${lan_drop_secret}
LAN_DROP_UPLOAD_DIR=${DATA_DIR}/uploads
LAN_DROP_CERT_FILE=${CONFIG_DIR}/tls/server.crt
LAN_DROP_KEY_FILE=${CONFIG_DIR}/tls/server.key
EOF
chown root:lan-drop "${CONFIG_DIR}/lan-drop.env"
chmod 0640 "${CONFIG_DIR}/lan-drop.env"
unset lan_drop_pin pin_confirmation lan_drop_secret

hostname_value="$(hostname)"
mapfile -t ipv4_addresses < <(
    hostname -I \
        | tr ' ' '\n' \
        | grep -E '^[0-9]+(\.[0-9]+){3}$' \
        || true
)

san_entries="DNS:${hostname_value},DNS:localhost,IP:127.0.0.1"
for address in "${ipv4_addresses[@]}"; do
    san_entries+=",IP:${address}"
done

printf '\nGenerating a local CA and TLS certificate...\n'
if [[ ! -s ${CONFIG_DIR}/tls/ca.crt || ! -s ${CONFIG_DIR}/tls/ca.key ]]; then
    openssl req -x509 -newkey rsa:3072 -sha256 -days 3650 -nodes \
        -subj "/CN=LAN Drop Local CA" \
        -keyout "${CONFIG_DIR}/tls/ca.key" \
        -out "${CONFIG_DIR}/tls/ca.crt"
else
    printf 'Reusing the existing LAN Drop CA.\n'
fi

openssl req -newkey rsa:2048 -nodes \
    -subj "/CN=${hostname_value}" \
    -keyout "${CONFIG_DIR}/tls/server.key" \
    -out "${CONFIG_DIR}/tls/server.csr"

openssl x509 -req -sha256 -days 825 \
    -in "${CONFIG_DIR}/tls/server.csr" \
    -CA "${CONFIG_DIR}/tls/ca.crt" \
    -CAkey "${CONFIG_DIR}/tls/ca.key" \
    -CAcreateserial \
    -extfile <(printf 'subjectAltName=%s\nextendedKeyUsage=serverAuth\n' "${san_entries}") \
    -out "${CONFIG_DIR}/tls/server.crt"

rm -f "${CONFIG_DIR}/tls/server.csr" "${CONFIG_DIR}/tls/ca.srl"
chown -R root:lan-drop "${CONFIG_DIR}/tls"
chmod 0750 "${CONFIG_DIR}/tls"
chmod 0640 "${CONFIG_DIR}/tls/ca.key" "${CONFIG_DIR}/tls/server.key"
chmod 0644 "${CONFIG_DIR}/tls/ca.crt" "${CONFIG_DIR}/tls/server.crt"
install -o root -g root -m 0644 "${CONFIG_DIR}/tls/ca.crt" "${DATA_DIR}/lan-drop-ca.crt"

install -o root -g root -m 0644 "${SOURCE_DIR}/systemd/lan-drop.service" "${SERVICE_FILE}"
systemctl daemon-reload
systemctl disable lan-drop.service >/dev/null 2>&1 || true
systemctl restart lan-drop.service

sleep 1
systemctl is-active --quiet lan-drop.service || {
    journalctl -u lan-drop.service -n 30 --no-pager
    fail "the service failed to start"
}

printf '\nLAN Drop is installed and running.\n\n'
printf '  https://%s:8080\n' "${hostname_value}"
for address in "${ipv4_addresses[@]}"; do
    printf '  https://%s:8080\n' "${address}"
done
printf '\nThe service is disabled at boot and runs on demand.\n'
printf 'Public CA certificate: %s/lan-drop-ca.crt\n' "${DATA_DIR}"
printf 'Next: follow docs/03-installation.md to trust this CA on each client.\n'
