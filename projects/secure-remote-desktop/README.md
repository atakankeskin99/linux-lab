# Secure Remote Desktop

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)
![Type](https://img.shields.io/badge/Type-Remote%20Access%20Lab-purple.svg)


A Linux lab for securely accessing and controlling a physical Linux desktop remotely using Tailscale, SSH local port forwarding, and x11vnc.

The setup keeps the VNC server bound to localhost instead of exposing it directly to the network. Persistent systemd services are used for remote desktop access and lightweight connectivity monitoring.

## Architecture

```text
Windows PC
    |
    | Tailscale
    v
Linux Host
    |
    | SSH local port forwarding
    | localhost:5900
    v
x11vnc
    |
    v
Physical Xorg Display (:0)
```

The remote VNC client connects to `localhost:5900` on the client machine. SSH forwards that connection through Tailscale to the localhost-only x11vnc server on the Linux host.

## Features

- Remote control of the physical Linux desktop
- Tailscale connectivity between hosts
- SSH local port forwarding
- x11vnc bound only to localhost
- Password-protected VNC access
- Persistent x11vnc systemd service
- Persistent network monitoring service
- Router, Internet, Tailscale, and Wi-Fi signal monitoring
- Timestamped connectivity logs for troubleshooting

## Project Structure

```text
secure-remote-desktop/
├── README.md
├── docs/
│   ├── 01-remote-desktop-setup.md
│   └── 02-connectivity-monitoring.md
├── scripts/
│   └── network-watch.sh
└── systemd/
    ├── network-watch.service
    └── x11vnc.service
```

## Documentation

- [Remote Desktop Setup](docs/01-remote-desktop-setup.md)
- [Connectivity Monitoring](docs/02-connectivity-monitoring.md)

## Failure Diagnosis

The monitoring component helps distinguish between several failure domains:

```text
router=FAIL
└── Local Wi-Fi / access point connectivity

router=OK internet=FAIL
└── Internet gateway / upstream connectivity

internet=OK tailscale=FAIL
└── Tailscale connectivity

router=OK internet=OK tailscale=OK
└── Investigate SSH tunnel, x11vnc, or VNC client
```

This was added after a real remote-access failure where the Linux host became unreachable through both VNC and SSH. System logs showed loss of global network connectivity followed by failed Tailscale DERP connections.

Rather than automatically restarting services, the monitoring service records connectivity state so the underlying failure can be diagnosed first.

## Security Notes

- x11vnc is configured to listen only on localhost.
- VNC traffic is not exposed directly to the Internet.
- Remote access is carried through an SSH tunnel over Tailscale.
- VNC authentication is enabled.
- Credentials, private IP addresses, SSIDs, and machine-specific configuration should not be committed to the repository.
- Example configuration files must be adapted before deployment.

## Status

Working lab setup.

Planned improvements include easier client-side connection setup and additional monitoring/diagnostic capabilities.