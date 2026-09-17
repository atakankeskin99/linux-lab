# Remote Desktop Setup

This document describes the setup used to remotely control the physical desktop of a Linux Mint host through Tailscale, SSH local port forwarding, and x11vnc.

## Goal

The objective was to access the existing graphical session of the Linux machine remotely while keeping all actions visible on its physical display.

A separate virtual desktop session was not desired. For this reason, x11vnc was used to share the existing Xorg display.

## Architecture

```text
Windows Client
     |
     | Tailscale
     v
Linux Mint Host
     |
     | SSH
     | local port forwarding
     v
localhost:5900
     |
     v
x11vnc
     |
     v
Xorg :0
     |
     v
Physical Display
```

The VNC server listens only on the Linux host's loopback interface.

The client therefore cannot connect directly to the VNC server. Instead, an SSH tunnel forwards a local port on the client to port 5900 on the Linux host.

---

## 1. Install x11vnc

On the Linux host:

```bash
sudo apt update
sudo apt install x11vnc
```

## 2. Identify the Physical Xorg Display

The running graphical session can be inspected with:

```bash
ps aux | grep -E 'Xorg|Xwayland|xfce4-session' | grep -v grep
```

In this setup, Xorg was running on:

```text
:0
```

The LightDM X authority file was:

```text
/var/run/lightdm/root/:0
```

These values may differ on other systems or display managers.

## 3. Configure VNC Authentication

Create a VNC password:

```bash
x11vnc -storepasswd
```

By default, the password file is stored under:

```text
~/.vnc/passwd
```

The password file must not be committed to version control.

## 4. Test x11vnc

Before creating a persistent service, x11vnc can be tested manually:

```bash
sudo x11vnc \
    -display :0 \
    -auth /var/run/lightdm/root/:0 \
    -rfbauth /home/YOUR_USER/.vnc/passwd \
    -forever \
    -shared \
    -localhost
```

Important options:

- `-display :0` — shares the physical Xorg display.
- `-auth` — provides the X authority file required to access the display.
- `-rfbauth` — enables VNC password authentication.
- `-forever` — keeps the server running after a client disconnects.
- `-shared` — allows shared VNC sessions.
- `-localhost` — prevents x11vnc from listening on external network interfaces.

A successful setup should expose VNC on:

```text
localhost:5900
```

## 5. Create a Persistent systemd Service

The example service is available at:

```text
systemd/x11vnc.service
```

Install it on the Linux host:

```bash
sudo cp systemd/x11vnc.service /etc/systemd/system/x11vnc.service
```

Edit the example configuration and replace `YOUR_USER` with the appropriate local username.

Then reload systemd and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now x11vnc
```

Check its status:

```bash
systemctl status x11vnc --no-pager
```

## 6. Verify Localhost-Only Binding

Verify which interface is listening on port 5900:

```bash
sudo ss -ltnp | grep 5900
```

The expected result is a listener on the loopback interface, for example:

```text
127.0.0.1:5900
```

The VNC port should not be directly exposed to the LAN or Internet.

## 7. Establish the SSH Tunnel

Both machines must be reachable through Tailscale.

From the remote client:

```bash
ssh -N \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -L 5900:localhost:5900 \
    YOUR_USER@TAILSCALE_IP
```

The forwarding rule means:

```text
Client localhost:5900
        |
        | SSH tunnel over Tailscale
        v
Linux localhost:5900
        |
        v
x11vnc
```

`-N` tells SSH not to start a remote shell because the connection is being used only for port forwarding.

`ServerAliveInterval` and `ServerAliveCountMax` help detect a dead SSH connection instead of leaving a stale tunnel running indefinitely.

The SSH process must remain running while the VNC connection is in use.

## 8. Connect with the VNC Client

On the remote machine, connect the VNC client to:

```text
localhost:5900
```

The client communicates only with the local SSH listener. SSH then carries the VNC traffic to the Linux host through Tailscale.

In the tested setup, TigerVNC Viewer was used as the Windows client.

## 9. Reboot Test

After enabling the systemd service, reboot the Linux host and verify:

```bash
systemctl status x11vnc --no-pager
```

The service should return to:

```text
active (running)
```

A new SSH tunnel must be established from the remote client after the Linux host reboots.

## Security Model

The design intentionally avoids:

```text
Internet -> exposed VNC port
```

Instead, access follows:

```text
Remote Client
      |
   Tailscale
      |
     SSH
      |
 localhost:5900
      |
   x11vnc
```

This provides multiple layers:

1. Tailscale provides private connectivity between the machines.
2. SSH provides authenticated and encrypted port forwarding.
3. x11vnc accepts connections only from localhost.
4. VNC authentication provides an additional authentication layer.

## Notes

This configuration assumes an Xorg session using LightDM.

Systems using Wayland or another display manager may require a different remote desktop approach or different authentication configuration.