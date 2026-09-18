#!/usr/bin/env bash
set -euo pipefail

[[ ${EUID} -eq 0 ]] || {
    printf 'Error: run this uninstaller with sudo: sudo ./uninstall.sh\n' >&2
    exit 1
}

printf 'This removes the application and service but preserves uploaded files.\n'
read -r -p 'Continue? [y/N] ' answer
[[ ${answer} =~ ^[Yy]$ ]] || exit 0

systemctl disable --now lan-drop.service >/dev/null 2>&1 || true
rm -f /etc/systemd/system/lan-drop.service
systemctl daemon-reload
rm -rf /opt/lan-drop
rm -rf /etc/lan-drop

printf 'LAN Drop was removed. Uploaded files remain in /var/lib/lan-drop/uploads.\n'
printf 'Remove that directory and the lan-drop system user manually if no longer needed.\n'
