#!/bin/bash

# Lightweight connectivity monitor for remote Linux hosts.
#
# Environment variables can be used to override these defaults:
#   ROUTER_IP
#   INTERNET_TARGET
#   TAILSCALE_PEER
#   WIFI_INTERFACE
#   INTERVAL

LOG="${LOG:-$HOME/network-watch.log}"

ROUTER_IP="${ROUTER_IP:-192.168.1.1}"
INTERNET_TARGET="${INTERNET_TARGET:-1.1.1.1}"
TAILSCALE_PEER="${TAILSCALE_PEER:-100.x.x.x}"
WIFI_INTERFACE="${WIFI_INTERFACE:-wlan0}"
INTERVAL="${INTERVAL:-30}"

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

check_host() {
    local host="$1"

    if ping -c 1 -W 2 "$host" >/dev/null 2>&1; then
        echo "OK"
    else
        echo "FAIL"
    fi
}

while true; do
    TS="$(timestamp)"

    ROUTER="$(check_host "$ROUTER_IP")"
    INTERNET="$(check_host "$INTERNET_TARGET")"
    TAILSCALE="$(check_host "$TAILSCALE_PEER")"

    SIGNAL="$(
        iw dev "$WIFI_INTERFACE" link 2>/dev/null |
        awk '/signal:/ {print $2 " dBm"}'
    )"

    if [ -z "$SIGNAL" ]; then
        SIGNAL="DISCONNECTED"
    fi

    echo "$TS | router=$ROUTER internet=$INTERNET tailscale=$TAILSCALE wifi=$SIGNAL" >> "$LOG"

    sleep "$INTERVAL"
done