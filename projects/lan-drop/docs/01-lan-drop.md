# 01 — LAN Drop

The story started before the phone/Linux experiment.

The first project was a small local-network file-transfer service hosted on a Linux Mint laptop. The goal was simple: move files between devices on the same LAN without cloud storage, messaging apps, or cables.

## What it became

The service grew to include:

- browser-based upload
- multiple-file uploads
- file listing
- download
- delete
- a simple PIN gate during part of the experiment
- systemd service management
- manual start/stop instead of automatic boot startup
- an HTTPS experiment with `mkcert`, later reverted to HTTP for simplicity
- SSH administration from the Windows PC

The Linux laptop acted as the host while Windows and the phone acted as clients.

```text
Windows PC ─────┐
                │
                ├──── Wi-Fi LAN ────> Linux Mint laptop / LAN Drop
                │
OMIX X600 ──────┘
```

## Why LAN Drop matters to the X600 story

It unexpectedly became deployment infrastructure.

When Termux and Termux:X11 APKs were needed for the X600, the files were downloaded on the PC, uploaded to LAN Drop, and then pulled from the phone browser.

So a project that originally existed only to simplify local file transfer directly enabled the next project.

That was the first important lesson of the lab: **small internal tools can become useful infrastructure later.**

## Operations learned

The project was also a practical introduction to:

- listening services on a LAN
- IP addressing and DHCP changes
- SSH administration
- Python virtual environments
- Flask basics
- Linux filesystem permissions
- service lifecycle with systemd
- debugging "service is running but I cannot connect" situations

## Typical lifecycle

The project was intentionally kept manual:

```bash
sudo systemctl start lan-drop
sudo systemctl status lan-drop
sudo systemctl stop lan-drop
```

Remote administration from the Windows PC used standard SSH to the Linux laptop.

## Connection to the rest of the repo

LAN Drop is not just a separate side project in this story. It is the point where the lab started developing a reusable workflow:

```text
build a tool
   ↓
use the tool
   ↓
discover a new problem
   ↓
reuse the old tool to solve part of the new problem
```
