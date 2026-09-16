# LAN Drop

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Framework](https://img.shields.io/badge/framework-Flask-black)
![Service](https://img.shields.io/badge/service-systemd-orange)
![Status](https://img.shields.io/badge/status-active-success)

A lightweight local-network file transfer service built as part of the Linux Lab.

LAN Drop began as a small Flask application for moving files between devices on the same local network. It gradually evolved into a broader Linux and networking project involving HTTPS, authentication, service management, Wi-Fi access-point experiments, application security testing, and systemd sandboxing.

The project currently has two operating models:

- **LAN Drop v1** — runs inside an existing local network
- **LAN Drop v2** — lets the Linux host create the local network itself

V1 remains the preferred mode for normal use. V2 is an infrastructure experiment that trades convenience for independence from an existing LAN.

---

## Interface

<p align="center">
  <img src="assets/lan-drop-ui.png"
       alt="LAN Drop web interface showing file upload, download, and delete actions"
       width="700">
</p>

<p align="center">
  <em>LAN Drop running as a browser-based file transfer service on the local network.</em>
</p>

---

## Current capabilities

### File transfer

- Browser-based file upload
- Multiple files per upload request
- File listing
- File download
- File deletion
- Duplicate filename preservation
- 100 MiB request-size limit
- Filename sanitization with Werkzeug

### Access and application security

- 6-digit PIN authentication
- Session-based access control
- PIN attempt throttling
- 5 failed attempts before lockout
- 60-second lockout period
- Explicit CSRF tokens for state-changing operations
- Secrets supplied outside application source code

### Transport security

- HTTPS/TLS
- Locally generated certificates using `mkcert`
- Subject Alternative Names for the active LAN address and local endpoints
- Local CA trust on configured clients

### Linux integration

- Dedicated `systemd` service
- Manual service lifecycle
- Service disabled at boot by design
- Restricted filesystem write access
- systemd process sandboxing
- Capability restrictions
- Kernel and device protections

### Network experimentation

- Existing-LAN operation
- Self-hosted Wi-Fi access point mode
- NetworkManager hotspot management
- AP-mode experimentation
- Bash lifecycle wrapper
- SSH administration

---

# Architecture

In its normal V1 configuration, LAN Drop runs on a Linux host already connected to the same network as its clients.

```text
                         EXISTING LOCAL NETWORK
                                  │
               ┌──────────────────┼──────────────────┐
               │                  │                  │
          Windows PC          Mobile device      Other client
               │                  │                  │
               └──────────────────┼──────────────────┘
                                  │
                              HTTPS/TLS
                                  │
                                  ▼
                          Linux Mint host
                                  │
                         lan-drop.service
                              systemd
                                  │
                                  ▼
                             Flask app
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
              Upload           Download          Delete
                 │                │                │
                 └──────── Linux filesystem ──────┘
```

The browser is the client interface. No dedicated client application is required.

A normal request path looks like:

```text
Client
  │
  ▼
HTTPS / TLS
  │
  ▼
PIN authentication
  │
  ▼
Flask session
  │
  ▼
CSRF validation
  │
  ▼
Application route
  │
  ▼
Linux filesystem
```

Authentication protects access to the file interface, while CSRF validation protects state-changing authenticated operations such as upload and deletion.

---

# Versions

## LAN Drop v1 — Existing LAN mode

V1 assumes that the Linux host and client are already connected to the same local network.

```text
                 Existing Wi-Fi / LAN
                         │
              ┌──────────┴──────────┐
              │                     │
         Linux host              Client
              │                     │
         LAN Drop               Browser
```

The network already exists.

LAN Drop only needs to provide the application.

This remains the preferred operating mode because clients do not need to leave their existing Wi-Fi connection simply to transfer a file.

### V1 includes

- Flask file-transfer application
- Multi-file upload
- Download and deletion
- PIN authentication
- Session management
- CSRF protection
- HTTPS/TLS
- Duplicate filename handling
- Upload-size enforcement
- systemd service management
- systemd security hardening
- SSH administration

[Read the detailed LAN Drop v1 documentation](docs/01-lan-drop.md)

---

## LAN Drop v2 — Self-hosted network mode

V2 explores a different architecture:

> What if the Linux host provided the network as well as the application?

The Linux Wi-Fi adapter switches into access-point mode and creates a dedicated wireless network.

```text
                    Linux host
              ┌───────────────────┐
              │                   │
              │  Wi-Fi AP         │
              │  SSID: LAN-Drop   │
              │        +          │
              │  LAN Drop service │
              │                   │
              └─────────┬─────────┘
                        │
                      Wi-Fi
                        │
                        ▼
                     Client
```

This removes the requirement for:

- an existing Wi-Fi network
- a router
- Internet access
- additional networking hardware

The experiment worked.

However, it also exposed an important usability trade-off.

In V1, a client already connected to the local network can simply open LAN Drop.

In V2, the client must leave its current Wi-Fi network, connect to `LAN-Drop`, perform the transfer, and then reconnect to its previous network.

V2 is therefore more self-contained but usually less convenient.

It remains part of the project because the experiment demonstrated AP mode, NetworkManager shared networking, interface role changes, network/service coordination, and the difference between technical independence and practical usability.

[Read the detailed LAN Drop v2 documentation](docs/01.1-lan-drop-v2.md)

---

# Security model

LAN Drop is intentionally a small local-network service, but its security model became a significant part of the project as it evolved.

Rather than treating security as a single feature, the application now applies controls at several layers.

```text
                Client
                  │
                  ▼
            TLS encryption
                  │
                  ▼
          PIN authentication
                  │
                  ▼
             Session
                  │
                  ▼
          CSRF validation
                  │
                  ▼
          Flask application
                  │
                  ▼
      File handling restrictions
                  │
                  ▼
       systemd process sandbox
                  │
                  ▼
           Linux host
```

---

## PIN authentication

Access to the file interface requires a 6-digit PIN.

The PIN itself is not stored in the application source.

It is supplied to the process through the environment used by the systemd service.

The Flask session secret is handled the same way.

Conceptually:

```text
application source
       │
       └── application logic

systemd service
       │
       └── process configuration

environment file
       │
       ├── LAN_DROP_PIN
       └── LAN_DROP_SECRET
```

No real PINs or session secrets are stored in this repository.

---

## PIN rate limiting

Testing showed that the original PIN gate accepted repeated incorrect attempts without throttling.

A lockout mechanism was therefore added.

Current behavior:

```text
Maximum failed attempts : 5
Lockout period          : 60 seconds
Tracking scope          : client IP
```

Runtime regression testing produced:

```text
Attempt 1 → Incorrect PIN. 4 attempts remaining.
Attempt 2 → Incorrect PIN. 3 attempts remaining.
Attempt 3 → Incorrect PIN. 2 attempts remaining.
Attempt 4 → Incorrect PIN. 1 attempts remaining.
Attempt 5 → Too many incorrect attempts.
Attempt 6 → Too many incorrect attempts.
```

The purpose is not to turn a 6-digit PIN into a high-entropy credential. It is to prevent unrestricted rapid guessing against the local authentication gate.

---

## CSRF protection

Authenticated state-changing requests use an explicit CSRF token stored in the Flask session.

The token is generated with Python's `secrets` module and embedded into forms for operations such as:

- file upload
- file deletion

Submitted tokens are compared against the session token before the operation is allowed.

The behavior was verified at runtime.

An authenticated request without a valid token returned:

```text
HTTP 403 FORBIDDEN
```

The same operation with the session's valid token succeeded.

This separates two different questions:

```text
Is the client authenticated?
            │
            ▼
          session

Is this state-changing request valid?
            │
            ▼
           CSRF
```

Both conditions must be satisfied.

---

## Upload-size enforcement

The application limits incoming requests to:

```text
100 MiB
```

The limit is enforced through Flask's request-size configuration.

A regression test attempted to upload a 101 MiB file using an authenticated session and a valid CSRF token.

The server returned:

```text
HTTP 413
```

The filesystem was then checked separately.

The oversized file had not been written to the upload directory.

This verified both sides of the control:

```text
request rejected     ✅
file not persisted   ✅
```

---

## Duplicate filename protection

The original upload behavior could replace an existing file when another upload used the same sanitized filename.

The upload path now preserves the existing file and assigns a new filename to the incoming duplicate.

For example:

```text
report.txt
report_1.txt
report_2.txt
```

This prevents a normal duplicate upload from silently destroying the previous file.

<p align="center">
  <img src="assets/duplicate-filename-protection.png"
       alt="LAN Drop interface demonstrating preservation of files with duplicate filenames"
       width="700">
</p>

<p align="center">
  <em>Runtime verification of duplicate filename preservation.</em>
</p>

The behavior was also verified directly on the Linux filesystem by confirming that the original and duplicate files retained different contents.

---

## Filename handling

Uploaded filenames are passed through Werkzeug's:

```python
secure_filename()
```

before being used as filesystem names.

Download operations are served through Flask/Werkzeug's directory-aware file-serving mechanism.

Path traversal behavior was also tested during the security review.

Attempts such as requesting a parent-directory path did not expose files outside the configured upload directory during testing.

This is documented as an observed test result rather than as a claim that arbitrary filesystem behavior has been formally proven safe.

---

# HTTPS and certificate identity

LAN Drop uses HTTPS with locally generated certificates created through `mkcert`.

This provides encrypted transport on the local network while also making certificate identity and trust part of the project.

A certificate is only useful if the identity being accessed matches one of its Subject Alternative Names.

During testing, the Linux host's LAN address had changed while the existing certificate still contained the previous address.

The result was a proper certificate verification failure:

```text
SSL: no alternative certificate subject name matches target host name
```

A new certificate was generated with the current endpoints:

```text
DNS:localhost
IP Address:127.0.0.1
IP Address:192.168.1.109
```

The application was then updated to use the new certificate and key.

Final verification deliberately used `curl` **without** disabling certificate validation:

```text
https://192.168.1.109:8080
        │
        ▼
certificate trusted
        │
        ▼
SAN matches 192.168.1.109
        │
        ▼
HTTP 302 → /login
```

This confirmed both certificate trust and endpoint identity.

The current LAN address shown here is part of the documented lab state and may naturally change when DHCP assigns a different address.

---

# TLS protocol behavior

The service was also tested against different TLS protocol versions.

Observed behavior:

```text
TLS 1.0  → rejected
TLS 1.1  → rejected
TLS 1.2  → accepted
TLS 1.3  → accepted
```

This was verified through OpenSSL client connections against the running service.

---

# systemd service hardening

LAN Drop runs as a dedicated systemd-managed process.

A security review of the initial unit showed that the service worked but inherited substantially more host access than the application required.

`systemd-analyze security` initially reported:

```text
9.2 UNSAFE
```

The service unit was then hardened while preserving the filesystem access required by the application.

The hardening configuration introduced controls including:

- `ProtectSystem=strict`
- `ProtectHome=read-only`
- an explicit writable path for the upload directory
- `NoNewPrivileges=true`
- an empty capability bounding set
- `RestrictSUIDSGID=true`
- kernel tunable protection
- kernel module protection
- kernel log protection
- control-group protection
- private devices
- private temporary storage
- private mounts
- hostname protection
- native system-call architecture restriction
- realtime restrictions
- personality locking

The important filesystem model became:

```text
LAN Drop process
       │
       ├── host filesystem        read-only / restricted
       │
       ├── home directories       read-only
       │
       └── uploads/               read + write
```

This applies least-privilege principles without preventing LAN Drop from performing its actual job.

After hardening:

```text
Before : 9.2 UNSAFE
After  : 4.4 OKAY
```

<p align="center">
  <img src="assets/systemd-security-hardening.png"
       alt="systemd security analysis showing LAN Drop hardening from 9.2 UNSAFE to 4.4 OKAY"
       width="700">
</p>

<p align="center">
  <em>The final 4.4 result is a live systemd-analyze measurement; 9.2 records the pre-hardening baseline.</em>
</p>

The application was then regression-tested under the hardened service configuration to ensure that startup, upload, download, and deletion still worked.

---

# Security review and runtime testing

The security work was performed against the running service rather than being limited to source inspection.

The review covered several different surfaces:

```text
Authentication
     │
     ├── repeated incorrect PIN attempts
     └── authenticated session behavior

HTTP application
     │
     ├── CSRF behavior
     ├── upload-size enforcement
     ├── duplicate uploads
     └── file operations

Filesystem
     │
     ├── overwrite behavior
     ├── oversized-file persistence
     └── path traversal attempts

TLS
     │
     ├── certificate identity
     ├── SAN validation
     └── protocol negotiation

Network
     │
     └── listening service reachability

Linux service
     │
     ├── process identity
     ├── systemd permissions
     └── sandbox exposure
```

The review produced concrete changes rather than only observations.

| Area | Observed state | Result |
|---|---|---|
| PIN guessing | Repeated attempts were unrestricted | 5-attempt / 60-second lockout |
| CSRF | Explicit application-level token validation was absent | Session-bound CSRF tokens |
| Upload size | Large requests required explicit control | 100 MiB request limit |
| Duplicate uploads | Existing filename could be replaced | Automatic `_1`, `_2`, ... preservation |
| TLS identity | Certificate contained an outdated LAN IP | New SAN-correct certificate |
| systemd isolation | `9.2 UNSAFE` exposure assessment | Hardened to `4.4 OKAY` |
| Path traversal test | No escape from upload directory observed | Existing safe serving behavior retained |

A more detailed account of the review, remediation process, and verification is maintained separately:

[Read the security hardening documentation](docs/02-security-hardening.md)

---

# Final regression verification

After the changes were applied, the major application paths were tested again as one regression cycle.

The final verification covered:

```text
[PASS] Service startup
[PASS] HTTPS certificate validation without -k
[PASS] TLS SAN validation
[PASS] Unauthenticated redirect to /login
[PASS] Authenticated session
[PASS] PIN rate limiting
[PASS] CSRF token generation
[PASS] Missing CSRF token rejected with 403
[PASS] Valid CSRF request accepted
[PASS] Normal file upload
[PASS] Duplicate filename preservation
[PASS] Original file preservation
[PASS] File download and content integrity
[PASS] CSRF-protected deletion
[PASS] Filesystem deletion
[PASS] 100 MiB request limit
[PASS] 101 MiB request rejected with 413
[PASS] Oversized file not written to disk
[PASS] Hardened systemd service remains functional
[PASS] systemd security exposure remains 4.4 OKAY
```

<p align="center">
  <img src="assets/security-regression-summary.png"
       alt="LAN Drop final security regression summary"
       width="700">
</p>

<p align="center">
  <em>Summary captured after the remediation and runtime verification cycle.</em>
</p>

The goal of this regression pass was simple:

> A security change is not complete if it prevents the application from doing the work it is supposed to do.

---

# systemd lifecycle

LAN Drop is managed as:

```text
lan-drop.service
```

The service is intentionally not enabled at boot.

Typical lifecycle:

```bash
sudo systemctl start lan-drop

systemctl status lan-drop --no-pager

sudo systemctl restart lan-drop

sudo systemctl stop lan-drop
```

This keeps the service available when needed without leaving it running permanently.

Because systemd owns the process, an SSH session used to start or inspect LAN Drop does not need to remain open.

---

# V2 launcher

LAN Drop v2 adds a Bash launcher that coordinates the application service with the Wi-Fi hotspot.

The current script is available at:

[`scripts/lan-drop`](scripts/lan-drop)

Supported operations:

```bash
lan-drop start
lan-drop status
lan-drop stop
```

The responsibilities remain intentionally separated:

```text
lan-drop.service
      │
      └── Flask application lifecycle


lan-drop launcher
      │
      ├── Wi-Fi hotspot lifecycle
      └── systemd service coordination
```

The application itself does not need to know whether the network was provided by an existing router or created by the Linux host.

---

# Design decisions

## Browser instead of a dedicated client

LAN Drop uses a web interface so that different devices can use the service without installing a dedicated application.

The same server can therefore be accessed from:

- Windows
- Linux
- Android
- iOS
- other browser-capable clients

---

## Manual startup instead of boot-time startup

LAN Drop is a utility, not permanent infrastructure.

Keeping the service disabled at boot means the process exists only when the file-transfer service is actually needed.

---

## Preserve duplicates instead of overwrite

Silent overwrite is convenient until the wrong file is destroyed.

The current behavior favors preservation:

```text
file.txt
file_1.txt
file_2.txt
```

The user can explicitly delete files later.

---

## Explicit application security instead of relying only on network trust

LAN Drop started as a trusted-LAN experiment.

As the project evolved, relying solely on “it is only on my LAN” became less interesting than testing and controlling the application itself.

That led to:

```text
PIN gate
   ↓
sessions
   ↓
rate limiting
   ↓
CSRF protection
   ↓
request-size limits
   ↓
TLS identity verification
   ↓
service sandboxing
```

The local network remains part of the intended deployment model, but it is no longer the only security boundary.

---

## V1 remains preferred over V2

V2 proved that LAN Drop can create the network it needs.

That does not make it the better default.

```text
V1
existing LAN
    │
    ▼
open service
    │
    ▼
transfer file
```

versus:

```text
V2
leave current Wi-Fi
        │
        ▼
connect to LAN-Drop
        │
        ▼
transfer file
        │
        ▼
leave LAN-Drop
        │
        ▼
reconnect
```

V1 is less independent but more convenient.

V2 is more independent but introduces additional user interaction.

Keeping both versions documents the trade-off rather than hiding it.

---

# Project evolution

LAN Drop did not begin with this architecture.

It grew incrementally:

```text
simple Flask app
       │
       ▼
LAN file upload
       │
       ▼
download + delete
       │
       ▼
PIN authentication
       │
       ▼
multiple-file upload
       │
       ▼
HTTPS / local CA
       │
       ▼
systemd service
       │
       ▼
reusable lab infrastructure
       │
       ├─────────────────────────────┐
       │                             │
       ▼                             ▼
Wi-Fi AP experiment          security review
       │                             │
       ▼                             ▼
self-hosted LAN             runtime testing
       │                             │
       ▼                             ▼
V2 launcher                 application hardening
       │                             │
       ▼                             ▼
usability comparison        systemd sandboxing
                                     │
                                     ▼
                              regression testing
```

The two branches represent different kinds of experimentation.

V2 asks:

> Can the application provide its own network?

The security work asks:

> What assumptions does the running service make, and what happens when those assumptions are tested?

Both grew out of the same small utility.

---

# What this project taught me

LAN Drop has touched substantially more of the Linux stack than its original purpose suggested.

### Application

- Flask routing
- HTTP request handling
- multipart form uploads
- sessions
- authentication
- CSRF protection
- input and filename handling
- request-size enforcement
- file lifecycle management

### Transport

- HTTPS
- TLS
- certificate authorities
- certificate trust
- Subject Alternative Names
- certificate identity validation
- TLS protocol negotiation
- `mkcert`
- OpenSSL testing

### Linux

- Python virtual environments
- filesystem permissions
- environment variables
- systemd services
- systemd sandboxing
- capabilities
- process privilege reduction
- service lifecycle management
- journal inspection

### Networking

- private IPv4 addressing
- DHCP address changes
- listening sockets
- interface-specific reachability
- Wi-Fi managed mode
- Wi-Fi AP mode
- NetworkManager
- SSH administration
- local network debugging

### Security testing

- testing behavior rather than assuming it from source
- distinguishing authentication from request authorization
- negative testing
- rate-limit verification
- path traversal testing
- overwrite testing
- oversized-request testing
- TLS identity testing
- regression testing after remediation
- measuring service exposure before and after hardening

One of the most useful recurring debugging models was to separate problems by layer:

```text
Application
    ↑
HTTP
    ↑
TLS
    ↑
TCP
    ↑
IP
    ↑
Network interface
```

A browser reporting that a service “does not work” does not identify which of those layers failed.

LAN Drop repeatedly provided practical examples of that distinction.

---

# Project structure

```text
lan-drop/
│
├── README.md
│
├── assets/
│   ├── lan-drop-ui.png
│   ├── duplicate-filename-protection.png
│   ├── security-regression-summary.png
│   └── systemd-security-hardening.png
│
├── docs/
│   ├── 01-lan-drop.md
│   ├── 01.1-lan-drop-v2.md
│   └── 02-security-hardening.md
│
└── scripts/
    └── lan-drop
```

The repository documentation is intentionally split by purpose.

### `README.md`

Current project overview, architecture, capabilities, security model, and major engineering decisions.

### `docs/01-lan-drop.md`

The original LAN Drop development story and detailed V1 implementation.

### `docs/01.1-lan-drop-v2.md`

The self-hosted Wi-Fi experiment, AP-mode architecture, launcher, and the V1/V2 usability trade-off.

### `docs/02-security-hardening.md`

Security review methodology, observed behavior, remediation work, systemd hardening, and final runtime regression verification.

---

# Documentation

For the complete project history:

1. [LAN Drop v1 — application and local-network service](docs/01-lan-drop.md)
2. [LAN Drop v2 — self-hosted network mode](docs/01.1-lan-drop-v2.md)
3. [Security review and hardening](docs/02-security-hardening.md)

---

# Final perspective

LAN Drop is still a small file-transfer utility.

That is intentional.

What changed is the number of layers explored through that utility.

```text
file transfer
     │
     ▼
web application
     │
     ▼
Linux service
     │
     ▼
TLS endpoint
     │
     ▼
network service
     │
     ▼
self-hosted network experiment
     │
     ▼
security testing target
     │
     ▼
sandboxed Linux process
```

The project became useful not because the original problem was complicated, but because each working stage created a reason to inspect the next layer.

V1 demonstrated how a small application can become reusable local infrastructure.

V2 demonstrated that greater infrastructure independence can make the user experience worse.

The security review demonstrated that a working service and a tested service are not the same thing.

Together, those iterations are the point of LAN Drop within the Linux Lab.