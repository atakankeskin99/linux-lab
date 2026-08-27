# X600 Linux Lab

A learning-focused experiment that started as a tiny LAN file-transfer tool and turned into a full Android-hosted Linux desktop lab on an OMIX X600.

The goal of this repository is not to present a polished production system. It documents the engineering process: what we tried, what failed, why we changed direction, and what eventually worked.

## The journey

```text
LAN Drop
   │
   ├── local file transfer
   ├── Flask + systemd + SSH
   └── APK delivery to the phone
        │
        ▼
Native Linux attempt
   │
   ├── MT6768 kernel source
   ├── toolchain / build work
   ├── driver-specific compile failures
   └── device-specific complexity
        │
        ▼
Architecture pivot
   │
   └── keep Android kernel, move Linux to userspace
        │
        ▼
Termux + Termux:X11 + DroidDesk
   │
   ├── XFCE desktop
   ├── Ubuntu PRoot environment
   ├── SSH remote administration
   └── TigerVNC remote desktop
        │
        ▼
X600 System Dashboard
   └── small Flask service reading Android/Termux system metrics
```

## Hardware / environment

- **Device:** OMIX X600
- **Android:** 12 / SDK 31
- **Architecture:** `arm64-v8a` / `aarch64`
- **Platform:** MediaTek MT6768
- **Desktop:** XFCE4
- **Host model:** Android kernel + Termux userspace + X11/VNC

## Why this repo exists

The interesting part was not simply "running Linux on a phone". The interesting part was learning where the system boundaries actually are.

The first idea was to pursue a more native Linux path. That immediately exposed the cost of device-specific kernel work: vendor trees, old code, compiler warnings promoted to errors, drivers, boot assumptions, and hardware support. Instead of treating that as wasted time, the project pivoted while preserving the original learning goal.

The second architecture re-used the already-working Android kernel and moved the Linux desktop into userspace. That gave us a usable system much faster while keeping the native-kernel attempt as a documented experiment rather than hiding it.

## Current architecture

```text
                 Windows PC
                 /        \
                /          \
        SSH :8022          TigerVNC :5901
              /              \
             v                v
       ┌──────────────────────────┐
       │        OMIX X600         │
       │                          │
       │  Android 12 / MT6768     │
       │          │               │
       │       Termux             │
       │       /    \\            │
       │   sshd     XFCE4         │
       │              │           │
       │           TigerVNC       │
       │                          │
       │   optional PRoot Ubuntu  │
       └──────────────────────────┘
```

## Repository map

- [`docs/01-lan-drop.md`](docs/01-lan-drop.md) — the file-transfer project that accidentally became deployment infrastructure
- [`docs/02-native-linux-attempt.md`](docs/02-native-linux-attempt.md) — kernel build attempt, failures, and lessons
- [`docs/03-android-linux-pivot.md`](docs/03-android-linux-pivot.md) — moving to Termux/X11/DroidDesk
- [`docs/04-remote-access.md`](docs/04-remote-access.md) — SSH + VNC control from Windows
- [`docs/05-dashboard.md`](docs/05-dashboard.md) — the first application deployed on the phone-hosted Linux environment
- [`docs/06-android-process-management-investigation.md`](docs/06-android-process-management-investigation.md) — measured debugging investigation into SSH/VNC/XFCE/Firefox process pressure on Android 12
- [`scripts/start-vnc.sh`](scripts/start-vnc.sh) — helper script used to bring the XFCE/VNC session back up
- [`dashboard/app.py`](dashboard/app.py) — Android/Termux-friendly Flask dashboard

## Key lessons

1. **Running Linux and booting native Linux are different problems.**
2. **Vendor Android kernels are deeply device-specific.** A compile failure in a peripheral driver can stop the entire experiment long before userspace exists.
3. **A pivot can preserve the learning goal.** Using Android's kernel did not erase the kernel work; it changed the architecture after we understood the cost.
4. **Small tools become infrastructure.** LAN Drop started as a convenience project and later carried the APKs used to build the next stage of the lab.
5. **Remote access changes the workflow.** Once SSH and VNC worked, the phone could sit on a charger while being operated from a Windows workstation.
6. **Android is not a normal desktop Linux host.** `/proc` permissions, process lifecycle, battery optimization, graphics acceleration, and package behavior all differ.
7. **Process counts need context.** A Termux UID process count is useful for workload comparison, but it is not the same thing as Android's internal phantom-process count.
8. **A failure is data.** The process-management investigation records both stable and failed states and keeps unproven hypotheses explicitly provisional.

## Android process-management investigation

A combined SSH + Flask + TigerVNC + XFCE workload exposed intermittent selective process termination on Android 12. During measurement, the Termux-visible process footprint grew from the low twenties to roughly **55** with the full desktop stack. Firefox then produced an additional multi-process burst and coincided with repeatable service loss.

The current leading hypothesis is Android 12 child/phantom-process management, but the repository intentionally does **not** treat the visible Termux process count as Android's phantom-process counter. A controlled A/B test using the same workload before and after changing `max_phantom_processes` is the next planned experiment.

See [`docs/06-android-process-management-investigation.md`](docs/06-android-process-management-investigation.md) for the measurements, process-tree observations, rejected hypotheses, invalidated `8-process` observation, and next experiment.

## Project status

Working:

- [x] LAN file transfer service
- [x] ARM64 / Android / hardware identification
- [x] Termux installation
- [x] Termux:X11 installation
- [x] XFCE desktop on the phone
- [x] Direct SSH access from Windows
- [x] TigerVNC remote XFCE session
- [x] One-command VNC/XFCE helper script
- [x] Flask system dashboard reachable over the LAN

Still experimental / unfinished:

- [ ] Make SSH lifecycle fully reliable under Android background management
- [ ] Improve VNC stability under load
- [ ] A/B test Android 12 `max_phantom_processes` under the same SSH + Flask + VNC/XFCE + Firefox workload
- [ ] Replace browser dashboard with a native-looking XFCE desktop app
- [ ] Improve Android-specific battery, uptime, storage, VNC and XFCE detection
- [ ] Revisit the native Linux/kernel path as a separate long-term experiment

## External projects used

- [Termux](https://termux.dev/)
- [Termux:X11](https://github.com/termux/termux-x11)
- [DroidDesk](https://github.com/orailnoor/DroidDesk)
- [TigerVNC](https://github.com/TigerVNC/tigervnc)
- XFCE
- Flask

## Philosophy

This repository intentionally keeps the failed path in the story.

The kernel attempt matters because it changed the way the final architecture was understood. The finished system is useful, but the main artifact is the sequence of technical decisions that produced it.
