#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="/etc/lan-drop"
TLS_DIR="${CONFIG_DIR}/tls"
CONNECTION_NAME="LAN-Drop"
HOTSPOT_SSID="LAN-Drop"
HOTSPOT_ADDRESS="10.42.0.1"
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

fail() {
    printf 'Error: %s\n' "$1" >&2
    exit 1
}

[[ ${EUID} -eq 0 ]] || fail "run this installer with sudo: sudo ./install-v2.sh"
[[ -t 0 ]] || fail "an interactive terminal is required"
command -v apt-get >/dev/null || fail "this installer currently supports Ubuntu and Linux Mint"
[[ -x /opt/lan-drop/.venv/bin/gunicorn ]] || fail "install V1 first with sudo ./install.sh"
[[ -f /etc/systemd/system/lan-drop.service ]] || fail "the V1 systemd service is not installed"
[[ -s ${TLS_DIR}/ca.crt && -s ${TLS_DIR}/ca.key ]] || fail "the V1 CA files are missing"

printf 'LAN Drop V2 hotspot installer\n\n'

service_was_active=false
if systemctl is-active --quiet lan-drop.service; then
    service_was_active=true
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y network-manager iw openssl

mapfile -t wifi_interfaces < <(
    nmcli -t -f DEVICE,TYPE device status \
        | awk -F: '$2 == "wifi" {print $1}'
)

(( ${#wifi_interfaces[@]} > 0 )) || fail "NetworkManager did not report a Wi-Fi interface"

if (( ${#wifi_interfaces[@]} == 1 )); then
    WIFI_INTERFACE="${wifi_interfaces[0]}"
else
    printf 'Available Wi-Fi interfaces:\n'
    select selected_interface in "${wifi_interfaces[@]}"; do
        [[ -n ${selected_interface:-} ]] || {
            printf 'Choose a valid interface number.\n'
            continue
        }
        WIFI_INTERFACE="${selected_interface}"
        break
    done
fi

wiphy_index="$(
    iw dev "${WIFI_INTERFACE}" info \
        | awk '$1 == "wiphy" {print $2; exit}'
)"
[[ ${wiphy_index} =~ ^[0-9]+$ ]] || fail "could not resolve the Wi-Fi radio for ${WIFI_INTERFACE}"
iw phy "phy${wiphy_index}" info | grep -Eq '^[[:space:]]*\* AP$' \
    || fail "${WIFI_INTERFACE} does not advertise AP mode"

while true; do
    read -r -s -p "Choose a hotspot password (8-63 characters): " hotspot_password
    printf '\n'
    (( ${#hotspot_password} >= 8 && ${#hotspot_password} <= 63 )) || {
        printf 'The hotspot password must contain 8-63 characters.\n'
        continue
    }

    read -r -s -p "Confirm the hotspot password: " password_confirmation
    printf '\n'
    [[ ${hotspot_password} == "${password_confirmation}" ]] && break
    printf 'The passwords did not match. Try again.\n'
done

if nmcli -t -f NAME connection show | grep -Fxq "${CONNECTION_NAME}"; then
    read -r -p "A ${CONNECTION_NAME} profile already exists. Replace it? [y/N] " replace_profile
    [[ ${replace_profile} =~ ^[Yy]$ ]] || fail "installation cancelled without changing the existing profile"
    nmcli connection delete id "${CONNECTION_NAME}"
fi

profile_created=false
certificate_temp_dir="$(mktemp -d)"
cleanup_failed_install() {
    if [[ ${profile_created} == true ]]; then
        nmcli connection delete id "${CONNECTION_NAME}" >/dev/null 2>&1 || true
    fi
}
cleanup_temp_files() {
    rm -rf -- "${certificate_temp_dir}"
}
trap cleanup_failed_install ERR
trap cleanup_temp_files EXIT

nmcli connection add \
    type wifi \
    ifname "${WIFI_INTERFACE}" \
    con-name "${CONNECTION_NAME}" \
    ssid "${HOTSPOT_SSID}"
profile_created=true

nmcli connection modify "${CONNECTION_NAME}" \
    802-11-wireless.mode ap \
    802-11-wireless.band bg \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "${hotspot_password}" \
    ipv4.method shared \
    ipv4.addresses "${HOTSPOT_ADDRESS}/24" \
    ipv6.method disabled \
    connection.autoconnect no

unset hotspot_password password_confirmation

cat > "${CONFIG_DIR}/v2.env" <<EOF
CONNECTION_NAME=${CONNECTION_NAME}
HOTSPOT_SSID=${HOTSPOT_SSID}
WIFI_INTERFACE=${WIFI_INTERFACE}
EOF
chown root:root "${CONFIG_DIR}/v2.env"
chmod 0644 "${CONFIG_DIR}/v2.env"

hostname_value="$(hostname)"
mapfile -t ipv4_addresses < <(
    hostname -I \
        | tr ' ' '\n' \
        | grep -E '^[0-9]+(\.[0-9]+){3}$' \
        || true
)

san_entries="DNS:${hostname_value},DNS:localhost,IP:127.0.0.1,IP:${HOTSPOT_ADDRESS}"
for address in "${ipv4_addresses[@]}"; do
    [[ ${address} == "${HOTSPOT_ADDRESS}" ]] || san_entries+=",IP:${address}"
done

printf '\nIssuing a server certificate that includes %s...\n' "${HOTSPOT_ADDRESS}"
openssl req -newkey rsa:2048 -nodes \
    -subj "/CN=${hostname_value}" \
    -keyout "${certificate_temp_dir}/server.key" \
    -out "${certificate_temp_dir}/server.csr"

openssl x509 -req -sha256 -days 825 \
    -in "${certificate_temp_dir}/server.csr" \
    -CA "${TLS_DIR}/ca.crt" \
    -CAkey "${TLS_DIR}/ca.key" \
    -CAserial "${certificate_temp_dir}/ca.srl" \
    -CAcreateserial \
    -extfile <(printf 'subjectAltName=%s\nextendedKeyUsage=serverAuth\n' "${san_entries}") \
    -out "${certificate_temp_dir}/server.crt"

install -o root -g lan-drop -m 0640 "${certificate_temp_dir}/server.key" "${TLS_DIR}/server.key"
install -o root -g lan-drop -m 0644 "${certificate_temp_dir}/server.crt" "${TLS_DIR}/server.crt"
install -o root -g root -m 0755 "${SOURCE_DIR}/scripts/lan-drop" /usr/local/bin/lan-drop

if [[ ${service_was_active} == true ]]; then
    systemctl restart lan-drop.service
fi
trap - ERR

printf '\nLAN Drop V2 is installed but the hotspot has not been activated.\n'
printf 'Interface: %s\n' "${WIFI_INTERFACE}"
printf 'SSID:      %s\n' "${HOTSPOT_SSID}"
printf 'URL:       https://%s:8080\n\n' "${HOTSPOT_ADDRESS}"
printf 'Start locally with: sudo lan-drop start\n'
printf 'Warning: activating the hotspot may disconnect SSH and Tailscale on a single-adapter host.\n'
