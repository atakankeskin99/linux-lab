# WireGuard Remote Access

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![VPN](https://img.shields.io/badge/VPN-WireGuard-blueviolet)
![Remote Access](https://img.shields.io/badge/remote-SSH-orange)
![Networking](https://img.shields.io/badge/network-CGNAT-lightgrey)
![Status](https://img.shields.io/badge/status-active-success)

A remote-access networking lab focused on reaching a Linux machine behind CGNAT.

The project explores self-hosted WireGuard infrastructure, VPS-based routing, SSH access, and the operational trade-offs between a manually managed WireGuard setup and Tailscale.

## Documentation

### WireGuard through CGNAT

A VPS is used as the publicly reachable WireGuard peer, allowing remote access to a Linux machine that cannot accept inbound connections directly.

[Read the WireGuard setup and investigation](docs/01-remote-access-through-cgnat.md)

### Tailscale Follow-up

A follow-up experiment comparing the self-managed WireGuard approach with Tailscale for day-to-day remote access.

[Read the Tailscale operational follow-up](docs/02-tailscale-operational-follow-up.md)

## Topics Explored

- WireGuard tunnels
- CGNAT traversal
- VPS networking
- SSH remote administration
- Peer routing
- Tailscale
- Operational complexity vs convenience