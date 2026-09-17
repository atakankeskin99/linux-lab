# Linux Lab

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Status](https://img.shields.io/badge/status-active-success)
![Learning Lab](https://img.shields.io/badge/type-learning%20lab-purple)

A growing collection of hands-on Linux experiments, small projects, system configurations, and debugging notes created while learning Linux, networking, and infrastructure.

This repository is not a single project.

It is a **learning lab** — a place where I document what I build, break, investigate, fix, and learn along the way.

---

## About This Repository

Most of the work in this repository starts with a simple question:

> "What happens if I try this?"

Instead of only studying concepts theoretically, I use available hardware to experiment with Linux systems, networking, remote access, services, automation, and system administration.

The goal is to document not only the final working result, but also the process behind it:

- what I tried
- what worked
- what failed
- how problems were investigated
- what measurements were taken
- which assumptions turned out to be wrong
- what I learned from the process

Some experiments become small standalone projects. Others remain technical notes, debugging investigations, or stepping stones toward larger homelab projects.

---

## Lab Philosophy

The main principle behind this repository is simple:

**Learn by building, breaking, debugging, and documenting.**

A failed experiment can be just as useful as a successful one if the failure teaches something about how the system actually works.

For that reason, debugging sessions and unsuccessful approaches are intentionally documented instead of being removed from the project history.

---

## Current Projects

### LAN Drop

A lightweight local-network file transfer service that evolved into a broader Linux, networking, and security experiment.

The project currently explores:

- HTTP/HTTPS file transfer and file management
- PIN and session-based authentication
- CSRF protection, rate limiting, and upload controls
- local TLS and certificate trust
- systemd service management and sandboxing
- runtime security and regression testing
- SSH administration
- Wi-Fi access-point mode and NetworkManager
- self-hosted local networking

The project developed along two main paths: **LAN Drop v2** explored running both the application and its Wi-Fi network from the Linux host, while a later **security hardening** phase tested and strengthened the application, TLS configuration, file handling, and systemd service.

The result is a small file-transfer utility that also serves as a practical lab for understanding how applications, networks, and Linux services interact.

→ [View details](projects/lan-drop/)

---

### X600 Linux

An experiment in turning an Android-based Omix X600 smartphone into a remotely accessible Linux environment.

The project currently explores:

- Termux
- SSH
- TigerVNC
- XFCE
- remote Linux desktop access
- Flask-based system monitoring
- Android/Linux process behavior
- resource constraints
- Android phantom-process management
- debugging multi-process workloads

One of the ongoing investigations examines why SSH, Flask, VNC, XFCE, and Firefox behave differently when running simultaneously under Android's process-management environment.

→ [View details](projects/x600-linux/)

---

### WireGuard Remote Access

A remote-access networking lab built around WireGuard and a public VPS to reach a Linux host behind CGNAT.

The project explores:

- CGNAT and inbound connectivity limitations
- WireGuard peer routing and `AllowedIPs`
- Linux IP forwarding
- `iptables` INPUT and FORWARD chains
- UDP traversal and persistent keepalives
- cloud networking and firewall debugging
- persistent VPN services with systemd

Rather than using a higher-level solution such as Tailscale, the network was built manually to expose and understand the underlying routing, firewall, and WireGuard mechanisms.

After the manual WireGuard + VPS setup had completed its learning objective, the public VPS was retired and Tailscale was adopted as the practical day-to-day remote-access layer. The follow-up documents direct peer connectivity, DERP fallback, MagicDNS, reboot persistence, and lid-closed SSH access.

→ [View details](projects/wireguard-remote-access/)

---

### Secure Remote Desktop

A secure remote-access lab for controlling the physical desktop of a Linux host using Tailscale, SSH local port forwarding, and x11vnc.

The project explores:

- physical Xorg desktop sharing with x11vnc
- localhost-only VNC exposure
- SSH local port forwarding
- Tailscale-based private connectivity
- persistent remote desktop services with systemd
- connectivity monitoring with Bash
- NetworkManager and Tailscale log analysis
- layered failure diagnosis

The setup deliberately keeps x11vnc bound to localhost and carries VNC traffic through an SSH tunnel over Tailscale instead of exposing the VNC port directly.

A connectivity-monitoring component was later added after an intermittent remote-access failure, allowing router, Internet, Tailscale, and Wi-Fi state to be correlated with system logs during future incidents.

→ [View details](projects/secure-remote-desktop/)

---

## Utilities

### sysinfo-lite

A lightweight Bash utility that displays essential Linux system information directly in the terminal.

It reports basic details such as:

- Hostname
- Current user
- Kernel version
- Uptime
- Memory usage
- Disk usage

→ [View details](utilities/sysinfo-lite/)

---

### Port Inspector

A lightweight Linux CLI utility for inspecting listening IPv4 TCP ports and identifying the processes behind them.

It currently provides:

- listening port discovery
- bind-address inspection
- basic scope classification
- process and PID identification
- support for multiple processes on the same socket
- filtering by a specific port

→ [View details](utilities/port-inspector/)

---

## What I Am Learning

This repository currently touches several areas:

**Linux**
- processes and process trees
- services and daemons
- permissions
- shell usage
- environment configuration
- system monitoring

**Networking**
- LAN addressing
- Wi-Fi access-point mode
- NetworkManager
- local network creation
- SSH
- ports and sockets
- HTTP/HTTPS
- remote administration
- VNC
- WireGuard
- VPN routing
- CGNAT
- Tailscale

**Software**
- Python
- Flask
- Bash scripting
- simple web interfaces
- Git and GitHub

**Systems**
- client/server architecture
- process lifecycle
- resource constraints
- debugging
- Android/Linux interaction
- service orchestration
- systemd

---

## Repository Structure

```text
linux-lab/
│
├── projects/
│   ├── lan-drop/
│   │   ├── README.md
│   │   ├── app.py
│   │   ├── .gitignore
│   │   ├── assets/
│   │   ├── docs/
│   │   │   ├── 01-lan-drop.md
│   │   │   ├── 01.1-lan-drop-v2.md
│   │   │   └── 02-security-hardening.md
│   │   └── scripts/
│   │       └── lan-drop
│   │
│   ├── x600-linux/
│   │   ├── README.md
│   │   ├── ROADMAP.md
│   │   ├── assets/
│   │   ├── dashboard/
│   │   │   ├── README.md
│   │   │   └── app.py
│   │   ├── docs/
│   │   │   ├── 01-native-linux-attempt.md
│   │   │   ├── 02-android-linux-pivot.md
│   │   │   ├── 03-remote-access.md
│   │   │   ├── 04-dashboard.md
│   │   │   └── 05-android-process-management-investigation.md
│   │   └── scripts/
│   │       └── start-vnc.sh
│   │
│   ├── wireguard-remote-access/
│   │   ├── README.md
│   │   ├── assets/
│   │   └── docs/
│   │       ├── 01-remote-access-through-cgnat.md
│   │       └── 02-tailscale-operational-follow-up.md
│   │
│   └── secure-remote-desktop/
│       ├── README.md
│       ├── docs/
│       │   ├── 01-remote-desktop-setup.md
│       │   └── 02-connectivity-monitoring.md
│       ├── scripts/
│       │   └── network-watch.sh
│       └── systemd/
│           ├── network-watch.service
│           └── x11vnc.service
│
├── utilities/
│   ├── sysinfo-lite/
│   │   ├── README.md
│   │   └── sysinfo.sh
│   │
│   └── port-inspector/
│       ├── README.md
│       └── port_inspector.py
│
├── LICENSE
└── README.md
```

---

## Why Document Everything?

The purpose of this repository is not to present every experiment as a polished finished product.

It is meant to preserve the engineering process.

A working system shows **what works**.

A debugging log can show **why it works**.

And sometimes a failed experiment teaches more about the underlying system than the final solution.

As the lab grows, this repository will continue to document that process.

---

## License

This repository is licensed under the [MIT License](LICENSE).