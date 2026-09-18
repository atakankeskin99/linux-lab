#!/usr/bin/env bash
set -u

failed=0

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

check "systemd unit installed" test -f /etc/systemd/system/lan-drop.service
check "configuration installed" test -r /etc/lan-drop/lan-drop.env
check "CA certificate installed" test -r /etc/lan-drop/tls/ca.crt
check "server certificate installed" test -r /etc/lan-drop/tls/server.crt
check "upload directory writable by service" runuser -u lan-drop -- test -w /var/lib/lan-drop/uploads
check "service active" systemctl is-active --quiet lan-drop.service
check "TCP 8080 listening" sh -c "ss -ltn | awk '{print \$4}' | grep -Eq '(^|:)8080$'"

exit "${failed}"
