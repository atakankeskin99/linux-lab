# LAN Drop

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Framework](https://img.shields.io/badge/framework-Flask-black)
![Service](https://img.shields.io/badge/service-systemd-orange)
![Status](https://img.shields.io/badge/status-active-success)

A lightweight local-network file transfer service built as part of the Linux Lab.

LAN Drop began as a simple Flask-based file transfer service for devices on the same LAN and later evolved into experiments with Linux service management, local HTTPS, authentication, and Wi-Fi access point infrastructure.

## Versions

### LAN Drop v1

Runs on an existing local network and provides browser-based file transfer between devices.

- Multi-file upload
- File listing, download, and deletion
- 6-digit PIN access
- Flask web interface
- systemd service
- SSH administration
- Local HTTPS experiments

[Read the LAN Drop v1 documentation](docs/01-lan-drop.md)

### LAN Drop v2

Extends the project by turning the Linux host into its own Wi-Fi access point, allowing devices to connect directly to the LAN Drop network.

- Dedicated Wi-Fi hotspot
- hostapd / NetworkManager experiments
- Local service access without an existing LAN
- Start/stop management script
- Network infrastructure experimentation

[Read the LAN Drop v2 documentation](docs/01.1-lan-drop-v2.md)

## Screenshot

![LAN Drop UI](assets/lan-drop-ui.png)

## Scripts

The current service management script is available here:

[`scripts/lan-drop`](scripts/lan-drop)