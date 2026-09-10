# Linux Lab

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

The project started as a simple way to move files between devices on the same LAN and gradually expanded into experiments with both application and network infrastructure.

The project currently includes and explores:

- HTTP/HTTPS file transfer
- multi-file uploads and file management
- PIN and session-based access
- Linux service management with systemd
- SSH administration
- local TLS and certificate trust
- Wi-Fi access-point mode
- NetworkManager
- self-hosted local networking
- Bash-based service and network lifecycle control

The original mode uses an existing LAN for convenient file transfer. A later experiment, **LAN Drop v2**, allows the Linux host to create its own Wi-Fi network and provide both the network infrastructure and the application service.

The experiment worked, but also exposed an important trade-off: removing the dependency on an existing LAN made the system more independent while making the common user workflow less convenient.

→ [`LAN Drop v1 documentation`](projects/lan-drop/docs/01-lan-drop.md)  
→ [`LAN Drop v2 — Self-Hosted Network Mode`](projects/lan-drop/docs/01.1-lan-drop-v2.md)

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

- [`docs/01-remote-access-through-cgnat.md`](projects/wireguard-remote-access/docs/01-remote-access-through-cgnat.md) — full investigation, architecture, implementation, troubleshooting, and validation

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

---

## Repository Structure

```text
linux-lab/
│
├── projects/
│   ├── lan-drop/
│   │   ├── assets/
│   │   ├── docs/
│   │   │   ├── 01-lan-drop.md
│   │   │   └── 01.1-lan-drop-v2.md
│   │   └── scripts/
│   │       └── lan-drop
│   │
│   ├── x600-linux/
│   │   ├── README.md
│   │   ├── ROADMAP.md
│   │   ├── dashboard/
│   │   ├── docs/
│   │   └── scripts/
│   │
│   └── wireguard-remote-access/
│       ├── assets/
│       └── docs/
│           └── 01-remote-access-through-cgnat.md
│
├── utilities/
│   └── sysinfo-lite/
│       ├── README.md
│       └── sysinfo.sh
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
