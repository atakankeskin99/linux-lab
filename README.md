<div align="center">

# Linux Lab

Hands-on Linux, networking, security, and container experiments.<br>
Built on available hardware. Documented from first attempt to measured result.

[![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](#lab-environment)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](#projects)
[![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)](#utilities)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](#investigations)

[![LAN Drop security tests](https://github.com/atakankeskin99/linux-lab/actions/workflows/lan-drop-security-tests.yml/badge.svg?branch=main)](https://github.com/atakankeskin99/linux-lab/actions/workflows/lan-drop-security-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-a78bfa.svg)](LICENSE)
![Learning lab](https://img.shields.io/badge/Focus-hands--on%20learning-06b6d4)

**[Lab status](#lab-status) · [Projects](#projects) · [Utilities](#utilities) · [Investigations](#investigations) · [Explore the repo](#explore-the-repo)**

</div>

---

## About the Lab

This repository started with Linux Mint XFCE on an old ASUS X550CA and a small Bash script for displaying system information. It grew into a collection of tools, services, and investigations built around practical questions:

- Can I turn a Linux laptop into a browser-based file-transfer service—and make it provide its own Wi-Fi network?
- Can an Android phone host a usable Linux desktop and an application of its own?
- How do I reach a machine behind CGNAT, then diagnose the connection when it disappears?
- Does a smaller container image actually mean lower memory use or faster startup?

Each project preserves the implementation alongside the decisions, tests, failed approaches, and open questions. Some tools are usable today. Some experiments reached their learning objective. Others remain unresolved, with evidence pointing toward the next test.

<a id="lab-status"></a>

## Lab Status

**4 projects · 2 utilities · 3 standalone investigations**

| Project / investigation | Area | Status | Where it stands |
| --- | --- | --- | --- |
| [**LAN Drop**](projects/lan-drop/) | File transfer & security | ![Working](https://img.shields.io/badge/Working-22c55e) | HTTPS service, V1/V2 installers, systemd hardening, and application security regression tests. |
| [**X600 Linux**](projects/x600-linux/) | Android-hosted Linux | ![Experimental](https://img.shields.io/badge/Experimental-f59e0b) | XFCE, SSH, VNC, and dashboard working; service loss under heavier workloads remains under investigation. |
| [**WireGuard Remote Access**](projects/wireguard-remote-access/) | VPN & CGNAT | ![Completed](https://img.shields.io/badge/Completed-3b82f6) | Manual WireGuard/VPS lab completed; VPS retired and everyday remote access moved to Tailscale. |
| [**Secure Remote Desktop**](projects/secure-remote-desktop/) | Remote access & monitoring | ![Working](https://img.shields.io/badge/Working-22c55e) | Physical desktop shared through SSH/Tailscale; monitoring added to investigate intermittent connectivity loss. |
| [**sysinfo-lite**](utilities/sysinfo-lite/) | Bash utility | ![Working](https://img.shields.io/badge/Working-22c55e) | Minimal CLI for host, CPU, memory, and root-filesystem information. |
| [**Port Inspector**](utilities/port-inspector/) | Network utility | ![v0.1](https://img.shields.io/badge/v0.1-06b6d4) | IPv4 TCP listeners, bind scope, process/PID lookup, and single-port filtering. |
| [**Alpine vs Debian Slim**](investigations/container-base-image-evaluation/) | Container benchmarking | ![Completed](https://img.shields.io/badge/Completed-3b82f6) | Same-workload comparison with recorded measurements and corrected startup methodology. |
| [**Kali Live USB Performance**](investigations/kali-live-usb-performance.md) | Storage & desktop performance | ![Baseline recorded](https://img.shields.io/badge/Baseline%20recorded-a855f7) | Two-host comparison complete; repeat tests on faster storage are planned. |
| [**Wake-on-LAN — ASUS X550CA**](investigations/wake-on-lan-asus-x550ca.md) | Hardware & power management | ![Unresolved](https://img.shields.io/badge/Unresolved-ef4444) | No successful wake from suspend or shutdown; checks and negative results preserved. |

*Statuses describe documented outcomes. “Working” means demonstrated in the lab; “Completed” means the experiment met its stated objective. The CI badge above covers LAN Drop's application tests.*

<a id="projects"></a>

## Projects

### LAN Drop

**A small file-transfer tool that grew into a Linux service and security lab.**

LAN Drop lets devices on a trusted local network upload, download, and delete files through a browser. It runs over HTTPS with a six-digit PIN, session authentication, and a systemd-managed Gunicorn process.

The project developed in three directions:

- **V1 — Existing LAN:** an on-demand file service with installation, removal, and diagnostic scripts, a dedicated service user, and a local certificate authority.
- **V2 — Self-hosted Wi-Fi:** NetworkManager access-point mode and a launcher that coordinates the hotspot with the application. It works without a router, but switching networks makes V1 more convenient for ordinary use.
- **Security hardening:** session-bound CSRF tokens, PIN throttling, a 100 MiB request limit, duplicate filename preservation, TLS identity verification, and systemd sandboxing.

**Evidence:** the documented hardening pass reduced the `systemd-analyze security` exposure score from **9.2 to 4.4**. Application-level regression tests run in GitHub Actions; host-dependent TLS and sandbox findings are documented separately. The exposure score measures the service unit's isolation, not overall application security.

**Explore:** [Project overview](projects/lan-drop/) · [V1 installation](projects/lan-drop/docs/03-installation.md) · [V2 hotspot](projects/lan-drop/docs/04-v2-installation.md) · [Security review](projects/lan-drop/docs/02-security-hardening.md) · [Tests](projects/lan-drop/tests/test_security.py)

---

### X600 Linux

**An OMIX X600 repurposed as an Android-hosted Linux desktop and application environment.**

The first attempt followed the native Linux route into MediaTek kernel sources and driver build failures. The project then pivoted to the working Android kernel, with Termux, Termux:X11, XFCE, TigerVNC, and an optional Ubuntu PRoot environment above it.

- Remote shell access and graphical desktop control from a Windows workstation.
- A custom Flask dashboard using `/proc`, sysfs, Android properties, and shell commands, with unavailable metrics handled as `N/A`.
- A documented investigation into selective process termination when SSH, Flask, VNC/XFCE, and Firefox run together.

**Open question:** Android child/phantom-process management is the leading hypothesis, not a confirmed root cause. The next planned experiment repeats the same workload before and after changing `max_phantom_processes`. Termux-visible process counts are explicitly kept separate from Android's internal phantom-process accounting.

**Explore:** [Project overview](projects/x600-linux/) · [Native Linux attempt](projects/x600-linux/docs/01-native-linux-attempt.md) · [Dashboard](projects/x600-linux/dashboard/) · [Process investigation](projects/x600-linux/docs/05-android-process-management-investigation.md) · [Roadmap](projects/x600-linux/ROADMAP.md)

---

### WireGuard Remote Access

**Reaching a Linux host behind CGNAT—and understanding every hop along the way.**

A public VPS served as a WireGuard hub between the Linux host and a Windows client. Building the path manually exposed the practical roles of `AllowedIPs`, Linux forwarding, `iptables` INPUT/FORWARD rules, persistent keepalives, and cloud firewall configuration.

End-to-end SSH access and reboot persistence were validated. Once the learning objective was complete, the VPS was retired and Tailscale became the everyday remote-access layer.

The operational follow-up covers direct peer connections, DERP fallback, MagicDNS, and lid-closed access to the powered-on laptop. It preserves both the manual setup and the reasoning behind simplifying it.

**Explore:** [Project overview](projects/wireguard-remote-access/) · [WireGuard through CGNAT](projects/wireguard-remote-access/docs/01-remote-access-through-cgnat.md) · [Tailscale follow-up](projects/wireguard-remote-access/docs/02-tailscale-operational-follow-up.md)

---

### Secure Remote Desktop

**Control of the physical Linux desktop, with monitoring for the network underneath it.**

This setup shares the existing Xorg display through x11vnc, bound only to localhost. A remote client reaches it through SSH local port forwarding over Tailscale, with systemd managing the server and connectivity monitor.

An intermittent outage affected both VNC and SSH. That shifted the investigation toward the underlying network and led to `network-watch.sh`, which records router reachability, Internet connectivity, a Tailscale peer, and Wi-Fi signal state for comparison with system logs.

**Current boundary:** remote desktop access works; the original outage's exact cause remains unproven. The monitor collects evidence without changing routes or restarting network services.

**Explore:** [Project overview](projects/secure-remote-desktop/) · [Desktop setup](projects/secure-remote-desktop/docs/01-remote-desktop-setup.md) · [Connectivity investigation](projects/secure-remote-desktop/docs/02-connectivity-monitoring.md) · [Monitor script](projects/secure-remote-desktop/scripts/network-watch.sh)

<a id="utilities"></a>

## Utilities

### [sysinfo-lite](utilities/sysinfo-lite/)

The first tool in the lab: a Bash script that prints the current user, hostname, kernel, architecture, CPU model, memory usage, and root-filesystem usage. The accompanying case study covers permissions, pipes, `$PATH`, and turning a local script into a global command.

```bash
bash utilities/sysinfo-lite/sysinfo.sh
```

### [Port Inspector](utilities/port-inspector/)

A Python CLI that combines `ss` socket data with `ip` interface data to show listening IPv4 TCP ports, bind addresses, scope labels, and associated processes. It supports multiple processes per socket and filtering by port, using only Python's standard library and Linux networking tools.

```bash
sudo python3 utilities/port-inspector/port_inspector.py --port 8080
```

It was validated against LAN Drop's start/stop lifecycle. Its scope labels describe socket binding; they do not establish external reachability through firewalls or NAT.

<a id="investigations"></a>

## Investigations

### [Container Base Image Evaluation — Alpine vs Debian Slim](investigations/container-base-image-evaluation/)

The same Python/Flask application, built on two base images and measured on the same host.

| Measurement | Alpine | Debian Slim |
| --- | ---: | ---: |
| Application image disk usage | **90.5 MB** | 197 MB |
| Idle memory | 24.24 MiB | **22.05 MiB** |
| Build time, three-run average | 33.83 s | **29.93 s** |

**Finding:** Alpine's storage advantage did not translate into lower idle RAM or faster builds in this workload. Startup testing also led to a methodology correction: pre-create containers, then measure `docker start` to HTTP readiness separately from container creation.

These are local, small-sample results. Build timings used locally available base images with application-layer caching disabled.

[Methodology and interpretation](investigations/container-base-image-evaluation/) · [Recorded results](investigations/container-base-image-evaluation/results/benchmark-results.md) · [CSV data](investigations/container-base-image-evaluation/results/benchmark-results.csv)

### [Kali Live USB Performance](investigations/kali-live-usb-performance.md)

The same encrypted-persistence USB drive was tested on two hosts. It negotiated **5000M** and wrote at **9.2 MB/s** on one, versus **480M** and **4.1 MB/s** on the ASUS X550CA. Disabling XFCE compositing on the first host also improved desktop responsiveness.

**Finding:** storage throughput and graphics/compositor behavior contributed separate limitations. The measurements establish a baseline for repeating the tests with faster storage.

### [Wake-on-LAN — ASUS X550CA](investigations/wake-on-lan-asus-x550ca.md)

NIC capabilities, magic-packet delivery while awake, ACPI wake permissions, BIOS settings, two Realtek drivers, and two Ethernet cables were checked. The laptop still did not wake from suspend or shutdown.

**Finding:** a reported NIC capability does not guarantee a working platform-wide wake path. A firmware or power-management limitation remains the leading explanation, but the precise cause was not proven. The machine was restored to its stock driver configuration.

<a id="lab-environment"></a>

## Lab Environment

| Environment | Role in the lab |
| --- | --- |
| **ASUS X550CA · Linux Mint XFCE** | Linux services, file transfer, remote desktop, networking experiments, and hardware investigations. |
| **OMIX X600 · Android 12 · MediaTek MT6768 · ARM64** | Termux-hosted Linux desktop, Flask dashboard, and process-management experiments. |
| **Windows workstation** | Browser client, SSH administration, VNC viewer, and remote-access validation. |
| **Public VPS — retired** | WireGuard hub used to establish and investigate remote access through CGNAT. |
| **Docker on Linux Mint** | Alpine/Debian Slim builds and same-workload container measurements. |
| **Kali Live USB with LUKS persistence** | Cross-host storage and desktop-performance testing. |

The lab grows from the equipment available and the questions it raises.

<a id="explore-the-repo"></a>

## Explore the Repo

| If you want to… | Start here |
| --- | --- |
| Install a usable local service | [LAN Drop installation and client certificate trust](projects/lan-drop/docs/03-installation.md) |
| Follow a security review from findings to regression tests | [LAN Drop hardening](projects/lan-drop/docs/02-security-hardening.md) |
| See an architecture change after a failed approach | [X600's Android-hosted Linux pivot](projects/x600-linux/docs/02-android-linux-pivot.md) |
| Follow an unresolved debugging investigation | [X600 process management](projects/x600-linux/docs/05-android-process-management-investigation.md) |
| Understand VPN routing and firewall failures | [WireGuard through CGNAT](projects/wireguard-remote-access/docs/01-remote-access-through-cgnat.md) |
| Examine a benchmark and its limitations | [Container base-image evaluation](investigations/container-base-image-evaluation/) |

### Repository Structure

```text
linux-lab/
├── .github/workflows/             # CI workflows
├── projects/
│   ├── lan-drop/
│   ├── x600-linux/
│   ├── wireguard-remote-access/
│   └── secure-remote-desktop/
├── investigations/
│   ├── container-base-image-evaluation/
│   ├── kali-live-usb-performance.md
│   └── wake-on-lan-asus-x550ca.md
├── utilities/
│   ├── sysinfo-lite/
│   └── port-inspector/
├── LICENSE
└── README.md
```

<details>
<summary><strong>Full repository structure</strong></summary>

```text
linux-lab/
├── .github/
│   └── workflows/
│       └── lan-drop-security-tests.yml
├── projects/
│   ├── lan-drop/
│   │   ├── README.md
│   │   ├── .gitignore
│   │   ├── app.py
│   │   ├── assets/
│   │   │   ├── duplicate-filename-protection.png
│   │   │   ├── lan-drop-ui.png
│   │   │   ├── security-regression-summary.png
│   │   │   └── systemd-security-hardening.png
│   │   ├── docs/
│   │   │   ├── 01-lan-drop.md
│   │   │   ├── 01.1-lan-drop-v2.md
│   │   │   ├── 02-security-hardening.md
│   │   │   ├── 03-installation.md
│   │   │   └── 04-v2-installation.md
│   │   ├── install-v2.sh
│   │   ├── install.sh
│   │   ├── requirements.txt
│   │   ├── scripts/
│   │   │   ├── doctor-v2.sh
│   │   │   ├── doctor.sh
│   │   │   └── lan-drop
│   │   ├── systemd/
│   │   │   └── lan-drop.service
│   │   ├── tests/
│   │   │   └── test_security.py
│   │   ├── uninstall-v2.sh
│   │   └── uninstall.sh
│   ├── secure-remote-desktop/
│   │   ├── README.md
│   │   ├── docs/
│   │   │   ├── 01-remote-desktop-setup.md
│   │   │   └── 02-connectivity-monitoring.md
│   │   ├── scripts/
│   │   │   └── network-watch.sh
│   │   └── systemd/
│   │       ├── network-watch.service
│   │       └── x11vnc.service
│   ├── wireguard-remote-access/
│   │   ├── README.md
│   │   ├── assets/
│   │   │   ├── wireguard-ssh-validation.png
│   │   │   ├── wireguard-vps-peers.png
│   │   │   └── wireguard-windows-client.png
│   │   └── docs/
│   │       ├── 01-remote-access-through-cgnat.md
│   │       └── 02-tailscale-operational-follow-up.md
│   └── x600-linux/
│       ├── README.md
│       ├── ROADMAP.md
│       ├── .gitignore
│       ├── assets/
│       │   ├── x600-dashboard.png
│       │   ├── x600-ssh-remote-access.png
│       │   ├── x600-vnc-remote-access.png
│       │   └── x600-xfce-phone.png
│       ├── dashboard/
│       │   ├── README.md
│       │   └── app.py
│       ├── docs/
│       │   ├── 01-native-linux-attempt.md
│       │   ├── 02-android-linux-pivot.md
│       │   ├── 03-remote-access.md
│       │   ├── 04-dashboard.md
│       │   └── 05-android-process-management-investigation.md
│       └── scripts/
│           └── start-vnc.sh
├── investigations/
│   ├── container-base-image-evaluation/
│   │   ├── README.md
│   │   ├── alpine/
│   │   │   └── Dockerfile
│   │   ├── app/
│   │   │   ├── app.py
│   │   │   └── requirements.txt
│   │   ├── assets/
│   │   │   ├── alpine-baseline.png
│   │   │   ├── alpine-build-time.png
│   │   │   ├── application-image-size-comparison.png
│   │   │   ├── busybox-vs-debian-userspace.png
│   │   │   ├── debian-baseline.png
│   │   │   ├── debian-slim-build-time.png
│   │   │   ├── idle-memory-comparison.png
│   │   │   └── libc-comparison.png
│   │   ├── debian-slim/
│   │   │   └── Dockerfile
│   │   └── results/
│   │       ├── benchmark-results.csv
│   │       └── benchmark-results.md
│   ├── kali-live-usb-performance.md
│   └── wake-on-lan-asus-x550ca.md
├── utilities/
│   ├── port-inspector/
│   │   ├── README.md
│   │   └── port_inspector.py
│   └── sysinfo-lite/
│       ├── README.md
│       ├── LICENSE
│       └── sysinfo.sh
├── LICENSE
└── README.md
```

</details>

### Running the Lab

Clone the repository, then follow the setup instructions for the project you want to explore:

```bash
git clone https://github.com/atakankeskin99/linux-lab.git
cd linux-lab
```

The projects have different environments and prerequisites. LAN Drop's installer targets Ubuntu 24.04/Linux Mint 22; X600 is Android/Termux-specific; the remote desktop examples assume Xorg/LightDM and require host-specific configuration.

### Open Threads

- **X600:** controlled A/B testing of Android process management, more reliable service detection, and a future desktop version of the dashboard. [Roadmap →](projects/x600-linux/ROADMAP.md)
- **Remote desktop:** correlate the next connectivity failure with monitoring and system logs. [Investigation →](projects/secure-remote-desktop/docs/02-connectivity-monitoring.md)
- **Kali Live:** repeat the existing baseline on faster USB storage or an external SSD. [Test plan →](investigations/kali-live-usb-performance.md)

---

## How I Document the Work

A working setup is the beginning of the investigation. I keep the commands, measurements, corrections, and unsuccessful attempts that explain how it behaves—and distinguish observed results from hypotheses still waiting for a test.

That includes a kernel build that did not succeed, a Wake-on-LAN setup that never woke the machine, and benchmarks whose first methodology needed changing. Those records are part of the lab's value.

## License

[MIT](LICENSE) © Atakan Keskin
