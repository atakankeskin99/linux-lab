#!/data/data/com.termux/files/usr/bin/bash

# X600 Linux Lab - XFCE/TigerVNC recovery helper
# Assumes ~/.vnc/xstartup and VNC password are already configured.

echo "Starting X600 remote desktop..."

# Clear previous graphical sessions.
pkill -9 -f "termux.x11" 2>/dev/null
vncserver -kill :1 2>/dev/null
pkill -9 -f "Xvnc" 2>/dev/null
pkill -9 xfce4-session 2>/dev/null
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 2>/dev/null

# Audio.
pulseaudio --kill 2>/dev/null
sleep 1
pulseaudio --start --exit-idle-time=-1
export PULSE_SERVER=127.0.0.1

# VNC + XFCE.
vncserver -localhost no -geometry 1280x720 -depth 24 :1

DEVICE_IP=$(ip -4 addr show wlan0 2>/dev/null | awk '/inet / {print $2}' | cut -d/ -f1 | head -1)

echo ""
echo "======================================"
echo " X600 VNC READY"
[ -n "$DEVICE_IP" ] && echo " ${DEVICE_IP}:5901"
echo "======================================"
