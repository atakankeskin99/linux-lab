# LAN Drop

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Framework](https://img.shields.io/badge/framework-Flask-black)
![Service](https://img.shields.io/badge/service-systemd-orange)
![Status](https://img.shields.io/badge/status-active-success)

A lightweight, browser-based file transfer service for trusted local networks.

LAN Drop turns a Linux machine into an on-demand HTTPS file server with PIN authentication, multi-file upload, download, deletion, and systemd-managed operation. It can run on an existing local network or create its own Wi-Fi access point.

<p align="center">
  <img src="assets/lan-drop-ui.png"
       alt="LAN Drop web interface showing file upload, download, and delete actions"
       width="700">
</p>

<p align="center">
  <em>No dedicated client application is required—only a web browser.</em>
</p>

---

## Why this project exists

LAN Drop began as a simple way to move files between devices on the same network.

It evolved into a practical Linux lab covering:

* Flask application development
* HTTPS and local certificate trust
* Authentication and session handling
* CSRF and upload security
* systemd service management and sandboxing
* Wi-Fi access-point operation
* Runtime security testing and regression verification

The result is intentionally small in scope but implemented across several layers of the Linux and networking stack.

---

## Quick start — V1 existing LAN

The installer currently supports Ubuntu 24.04 and Linux Mint 22:

```bash
git clone https://github.com/atakankeskin99/linux-lab.git
cd linux-lab/projects/lan-drop
chmod +x install.sh uninstall.sh scripts/doctor.sh
sudo ./install.sh
```

Choose a six-digit PIN when prompted, then open one of the HTTPS URLs printed by the installer.

LAN Drop creates its own local certificate authority. To remove the browser certificate warning safely, install the generated **public CA certificate** on each client:

```text
/var/lib/lan-drop/lan-drop-ca.crt
```

[Read the complete installation, client trust, verification, and uninstall guide](docs/03-installation.md)

> LAN Drop is intended for trusted local networks. Do not expose TCP 8080 directly to the Internet.

---

## Features

### File transfer

* Browser-based interface
* Multi-file upload
* File listing, download, and deletion
* Duplicate filename preservation
* Filename sanitization
* 100 MiB request-size limit

### Security

* 6-digit PIN authentication
* Session-based access control
* PIN attempt throttling
* Session-bound CSRF tokens
* HTTPS with locally trusted certificates
* Secrets kept outside application source
* Restricted filesystem access
* Hardened systemd process sandbox

### Linux and networking

* On-demand systemd service
* Existing-LAN operation
* Optional self-hosted Wi-Fi network
* NetworkManager hotspot coordination
* SSH administration
* Bash lifecycle wrapper for V2

---

## How it works

```mermaid
flowchart LR
    A["Client browser"] -->|HTTPS| B["Linux host"]
    B --> C["Flask application"]
    C --> D["Upload directory"]
    E["systemd"] --> C
```

The browser acts as the client interface. Requests pass through TLS, PIN authentication, session validation, and CSRF validation before reaching file operations.

LAN Drop is designed for temporary use on a trusted local network rather than permanent public exposure.

---

## Operating modes

| Mode                         | Network source                          | Best suited for                   | Trade-off                                      |
| ---------------------------- | --------------------------------------- | --------------------------------- | ---------------------------------------------- |
| **V1 — Existing LAN**        | Existing router or local network        | Normal day-to-day use             | Requires both devices to share a network       |
| **V2 — Self-hosted network** | Linux host creates a Wi-Fi access point | Router-free or isolated transfers | Clients must temporarily switch Wi-Fi networks |

### V1 — Existing LAN

The Linux host and client connect to the same existing network. The client opens LAN Drop in a browser and transfers files without changing networks.

This is the preferred operating mode because it offers the simplest user experience.

[Read the V1 implementation and setup documentation](docs/01-lan-drop.md)

### V2 — Self-hosted network

The Linux Wi-Fi adapter switches into access-point mode and creates a dedicated `LAN-Drop` network. The host provides both the network and the application.

This removes the need for an existing router or Internet connection, but clients must leave their current Wi-Fi network during the transfer.

[Read the V2 access-point experiment](docs/01.1-lan-drop-v2.md)

---

## Security model

LAN Drop applies controls at multiple layers:

```mermaid
flowchart TD
    A["TLS encryption"] --> B["PIN authentication"]
    B --> C["Session and CSRF validation"]
    C --> D["Restricted file operations"]
    D --> E["systemd sandbox"]
```

Key controls include:

* Five failed PIN attempts trigger a 60-second IP-based lockout
* State-changing requests require a valid session-bound CSRF token
* Oversized requests are rejected before files are persisted
* Duplicate uploads receive numbered filenames instead of overwriting existing files
* Uploaded filenames are sanitized before filesystem use
* TLS certificates include the active endpoint as a Subject Alternative Name
* The service can write only to its designated upload directory

This is defense in depth for a local utility—not a claim that LAN Drop is suitable for direct Internet exposure or hostile multi-user environments.

---

## Security hardening results

The project was tested against the running service rather than reviewed only at source level.

| Area              | Initial observation                            | Remediation                               |
| ----------------- | ---------------------------------------------- | ----------------------------------------- |
| PIN guessing      | Repeated attempts were unrestricted            | 5-attempt / 60-second lockout             |
| CSRF              | No explicit application-level token validation | Session-bound CSRF tokens                 |
| Upload size       | No verified request boundary                   | 100 MiB request limit                     |
| Duplicate uploads | Existing files could be replaced               | Automatic `_1`, `_2`, … preservation      |
| TLS identity      | Certificate contained an outdated LAN IP       | SAN-correct certificate generated         |
| systemd isolation | `9.2 UNSAFE` exposure score                    | Hardened to `4.4 OKAY`                    |
| Path traversal    | Escape attempts required verification          | No escape observed during runtime testing |

<p align="center">
  <img src="assets/systemd-security-hardening.png"
       alt="systemd security analysis showing LAN Drop hardening from 9.2 UNSAFE to 4.4 OKAY"
       width="700">
</p>

<p align="center">
  <em>Measured with systemd-analyze before and after service hardening.</em>
</p>

[Read the complete security review and verification process](docs/02-security-hardening.md)

---

## Verified behavior

The final regression cycle confirmed:

* Service startup under the hardened systemd configuration
* Certificate trust and SAN validation without bypassing TLS checks
* Rejection of unauthenticated requests
* PIN rate limiting and lockout
* CSRF rejection with HTTP 403
* Normal and multi-file uploads
* Duplicate filename preservation
* Downloaded file integrity
* CSRF-protected deletion
* Rejection of a 101 MiB upload with HTTP 413
* No oversized file persisted to disk
* Continued application operation under the systemd sandbox

<p align="center">
  <img src="assets/security-regression-summary.png"
       alt="LAN Drop final security regression summary"
       width="700">
</p>

---

## Service lifecycle

On a configured host, LAN Drop is controlled through systemd:

```bash
sudo systemctl start lan-drop
systemctl status lan-drop --no-pager
sudo systemctl restart lan-drop
sudo systemctl stop lan-drop
```

The service is intentionally disabled at boot. LAN Drop is an on-demand utility, not permanent infrastructure.

Because systemd owns the process, an SSH session used to start or inspect the service does not need to remain open.

---

## V2 launcher

V2 includes a Bash wrapper that coordinates the Wi-Fi hotspot and application service:

```bash
lan-drop start
lan-drop status
lan-drop stop
```

The launcher is available at [`scripts/lan-drop`](scripts/lan-drop).

Network lifecycle and application lifecycle remain separate: the Flask application does not need to know whether connectivity comes from an existing router or the Linux host itself.

---

## Project structure

```text
lan-drop/
├── README.md
├── app.py
├── install.sh
├── requirements.txt
├── uninstall.sh
├── assets/
│   ├── lan-drop-ui.png
│   ├── duplicate-filename-protection.png
│   ├── security-regression-summary.png
│   └── systemd-security-hardening.png
├── docs/
│   ├── 01-lan-drop.md
│   ├── 01.1-lan-drop-v2.md
│   ├── 02-security-hardening.md
│   └── 03-installation.md
├── scripts/
│   ├── doctor.sh
│   └── lan-drop
└── systemd/
    └── lan-drop.service
```

---

## Documentation

* [LAN Drop V1 — application and local-network service](docs/01-lan-drop.md)
* [LAN Drop V2 — self-hosted Wi-Fi mode](docs/01.1-lan-drop-v2.md)
* [Security review, hardening, and regression testing](docs/02-security-hardening.md)
* [Installation and client CA trust](docs/03-installation.md)

---

## Key engineering lessons

LAN Drop demonstrates that even a small utility crosses several engineering boundaries:

* A working service is not necessarily a tested service
* Authentication and CSRF protection address different threats
* TLS trust and TLS endpoint identity are separate requirements
* Least privilege must be verified without breaking required behavior
* Greater infrastructure independence can reduce usability
* Security changes require regression testing after remediation

V1 showed how a small Flask application could become reusable local infrastructure. V2 explored whether the same host could provide its own network. The security review then tested the assumptions made by both the application and its Linux service environment.
