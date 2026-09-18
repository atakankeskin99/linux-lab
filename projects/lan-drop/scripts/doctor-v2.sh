#!/usr/bin/env bash
set -u

failed=0

check_ap_mode() {
    local wiphy_index
    # shellcheck source=/dev/null
    source /etc/lan-drop/v2.env
    wiphy_index="$(iw dev "${WIFI_INTERFACE}" info | awk '$1 == "wiphy" {print $2; exit}')"
    [[ ${wiphy_index} =~ ^[0-9]+$ ]] || return 1
    iw phy "phy${wiphy_index}" info | grep -Eq '^[[:space:]]*\* AP$'
}

check() {
    local description="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        printf '[PASS] %s\n' "${description}"
    else
        printf '[FAIL] %s\n' "${description}"
        failed=1
    fi
}

check "V1 service installed" test -f /etc/systemd/system/lan-drop.service
check "V2 configuration installed" test -r /etc/lan-drop/v2.env
check "V2 launcher installed" test -x /usr/local/bin/lan-drop
check "NetworkManager profile installed" nmcli connection show LAN-Drop
check "selected Wi-Fi interface advertises AP mode" check_ap_mode
check "certificate contains hotspot address" sh -c \
    "openssl x509 -in /etc/lan-drop/tls/server.crt -noout -ext subjectAltName | grep -Fq 'IP Address:10.42.0.1'"

exit "${failed}"
