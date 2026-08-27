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

The project started as a simple way to move files between devices on the same LAN and gradually became an experiment involving:

- HTTP file transfer
- multi-file uploads
- file management
- Linux services
- systemd
- SSH administration
- local HTTPS experiments
- basic service lifecycle management

→ `projects/lan-drop/`

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

→ `projects/x600-linux/`

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
- SSH
- ports and sockets
- HTTP
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

    linux-lab/
    │
    ├── projects/
    │   ├── lan-drop/
    │   │   └── ...
    │   │
    │   └── x600-linux/
    │       ├── README.md
    │       ├── ROADMAP.md
    │       ├── dashboard/
    │       ├── docs/
    │       └── scripts/
    │
    └── README.md

Each project contains its own documentation and technical notes.

---

## Why Document Everything?

The purpose of this repository is not to present every experiment as a polished finished product.

It is meant to preserve the engineering process.

A working system shows **what works**.

A debugging log can show **why it works**.

And sometimes a failed experiment teaches more about the underlying system than the final solution.

As the lab grows, this repository will continue to document that process.