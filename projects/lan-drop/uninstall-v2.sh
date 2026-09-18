#!/usr/bin/env bash
set -euo pipefail

CONNECTION_NAME="LAN-Drop"

[[ ${EUID} -eq 0 ]] || {
    printf 'Error: run with sudo: sudo ./uninstall-v2.sh\n' >&2
    exit 1
}

printf 'This removes only the V2 hotspot profile and launcher. V1 and uploaded files remain.\n'
read -r -p 'Continue? [y/N] ' answer
[[ ${answer} =~ ^[Yy]$ ]] || exit 0

systemctl stop lan-drop.service >/dev/null 2>&1 || true

if nmcli -t -f NAME connection show | grep -Fxq "${CONNECTION_NAME}"; then
    nmcli connection delete id "${CONNECTION_NAME}"
fi

rm -f /usr/local/bin/lan-drop /etc/lan-drop/v2.env
printf 'LAN Drop V2 was removed. The V1 installation remains available.\n'
