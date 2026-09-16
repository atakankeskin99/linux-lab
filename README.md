
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

A lightweight local-network file transfer service hosted on a Linux machine.

The project began as a simple way to move files between devices on the same LAN and gradually evolved into a broader experiment spanning application development, Linux service management, networking, and security hardening.

The project currently includes and explores:

- HTTP/HTTPS file transfer
- multi-file upload, download, and deletion
- PIN and session-based authentication
- PIN rate limiting and temporary lockout
- CSRF protection for state-changing operations
- filename sanitization and duplicate filename preservation
- request-size enforcement
- local TLS, certificate trust, and certificate identity
- Linux service management with systemd
- systemd sandboxing and least-privilege hardening
- runtime security and regression testing
- SSH administration
- Wi-Fi access-point mode
- NetworkManager
- self-hosted local networking
- Bash-based service and network lifecycle control

The project developed along two main experimental paths.

The first was **network evolution**. The original LAN Drop mode uses an existing local network for convenient file transfer. **LAN Drop v2** explored whether the Linux host could provide both the application and the network itself by operating as a Wi-Fi access point. The experiment succeeded technically, but also demonstrated an important engineering trade-off: greater infrastructure independence can produce a less convenient user workflow.

The second was **security evolution**. The running service was reviewed through source inspection and runtime testing across authentication, CSRF behavior, file handling, upload limits, TLS identity, network exposure, PIN guessing, and process privileges. The findings led to targeted changes including rate limiting, explicit CSRF validation, duplicate filename protection, request-size enforcement, certificate remediation, and systemd sandboxing.

The hardened service was then subjected to a final regression cycle to verify that the added controls did not break its intended functionality. As part of the service-level hardening work, the `systemd-analyze security` exposure assessment improved from **9.2 UNSAFE** to **4.4 OKAY**.

Together, these iterations turned LAN Drop from a small file-transfer utility into a practical lab for exploring how application behavior, networking, TLS, Linux services, and operating-system-level isolation interact.

→ [`projects/lan-drop/`](projects/lan-drop/)

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

→ [`projects/x600-linux/`](projects/x600-linux/)

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

→ [`projects/wireguard-remote-access/`](projects/wireguard-remote-access/)

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

→ [`utilities/sysinfo-lite/`](utilities/sysinfo-lite/)

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

→ [`utilities/port-inspector/`](utilities/port-inspector/)
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
│   └── wireguard-remote-access/
│       ├── README.md
│       ├── assets/
│       └── docs/
│           ├── 01-remote-access-through-cgnat.md
│           └── 02-tailscale-operational-follow-up.md
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
