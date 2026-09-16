# 01 — LAN Drop

LAN Drop began as a small, learning-focused local-network file-transfer service hosted on a Linux Mint XFCE laptop.

The original goal was simple: move files between devices on the same LAN without relying on cloud storage, messaging apps, or cables. What started as a small Flask experiment gradually became a reusable internal service for the lab.

Over time, the project expanded beyond file transfer into authentication, HTTPS, Linux service management, runtime security testing, and systemd hardening.

## What it became

LAN Drop currently supports:

- browser-based file upload
- multiple-file uploads in a single request
- file listing
- file download
- file deletion
- duplicate filename preservation
- 6-digit PIN access
- session-based authentication
- PIN attempt throttling and temporary lockout
- explicit CSRF protection for state-changing operations
- a 100 MiB request-size limit
- filename sanitization with Werkzeug
- HTTPS/TLS with locally generated certificates using `mkcert`
- manual lifecycle management with `systemd`
- systemd process sandboxing and filesystem restrictions
- SSH administration from another machine on the LAN
- access from Windows, iPhone/iOS, Android-based devices, and other clients on the same local network

The service is intentionally **not enabled at boot**. It runs only when started manually.

## Architecture

```text
                            LOCAL NETWORK
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
         Windows PC          Apple iPhone        OMIX X600
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                             Wi-Fi / LAN
                                  │
                              HTTPS / TLS
                                  │
                                  ▼
                         Linux Mint laptop
                            192.0.2.10
                                  │
                         lan-drop.service
                              systemd
                                  │
                                  ▼
                             Flask app
                                  │
                   ┌──────────────┼──────────────┐
                   │              │              │
                Upload         Download        Delete
                   │              │              │
                   └────── Linux filesystem ─────┘
```

`192.0.2.10` is used here as a documentation-only example address.

The Linux laptop acts as the host. Windows, iOS, Android, and other devices on the LAN act as clients through a web browser.

<p align="center">
  <img src="../assets/lan-drop-ui.png"
       alt="LAN Drop web interface showing multi-file upload, download, and delete actions"
       width="700">
</p>

<p align="center">
  <em>LAN Drop web interface for local file transfer.</em>
</p>

## Request flow

A normal authenticated operation now passes through several layers:

```text
Client browser
      │
      ▼
https://192.0.2.10:8080
      │
      ▼
TLS connection
      │
      ▼
PIN / session authentication
      │
      ▼
CSRF validation
      │
      ▼
Flask route
      │
      ▼
file handling
      │
      ▼
Linux filesystem
```

Not every request reaches every layer.

For example, unauthenticated requests to protected routes are redirected to the login page before file handling occurs, while authenticated state-changing requests such as upload and delete must also pass CSRF validation.

## HTTPS and local certificate trust

LAN Drop originally ran over plain HTTP. HTTPS was later added using `mkcert`.

A local certificate authority was created on the Linux host, and that CA signed a certificate for the LAN Drop service.

```text
mkcert Local CA
      │
      │ signs
      ▼
LAN Drop certificate
      │
      ▼
LAN Drop HTTPS endpoint
```

A typical certificate covers endpoints such as:

```text
current LAN address
localhost
127.0.0.1
```

The active network address matters because TLS certificate identity is validated against the hostname or IP address used by the client.

During a later security review, the Linux host's DHCP address had changed while the existing certificate still contained the previous address. Normal certificate verification correctly rejected that mismatch.

A replacement certificate was generated with the current LAN address in its Subject Alternative Names, after which HTTPS verification succeeded without bypassing certificate checks.

This made the distinction between three related concepts much clearer:

```text
encryption
     │
certificate trust
     │
endpoint identity
```

A TLS connection can be encrypted while still failing identity verification if the requested hostname or IP address is not represented correctly in the certificate.

The local CA certificate can be installed into trusted client stores so browsers can validate LAN Drop normally.

Clients that do not trust the local CA may display a certificate warning.

For the detailed TLS tests and certificate remediation, see:

[Security review and hardening](02-security-hardening.md)

## PIN and session access

LAN Drop uses a simple 6-digit PIN gate before exposing the file interface.

The PIN and Flask session secret are not hard-coded into the application. They are supplied through an external environment file used by the systemd service.

This keeps application code and runtime configuration separate:

```text
app.py
  │
  ├── application logic
  │
systemd service
  │
  ├── process lifecycle
  │
environment file
  │
  └── PIN / session secret
```

No real PINs or secrets are stored in this repository.

A successful PIN entry creates an authenticated Flask session.

Protected routes verify that session before allowing access.

The original implementation accepted repeated incorrect PIN attempts without throttling. After runtime testing exposed that behavior, a simple per-client-IP lockout mechanism was added.

Current policy:

```text
maximum failed attempts : 5
lockout duration        : 60 seconds
```

A successful login clears the stored failure state for that client.

The limiter is intentionally simple and stored in application memory, which means its state resets when the service restarts.

For the current single-process personal service, that trade-off is acceptable.

## CSRF protection

Authentication answers:

> Does this client have an authenticated session?

It does not automatically answer:

> Is this state-changing request legitimate?

For that reason, upload and deletion now use explicit CSRF protection.

After successful authentication, LAN Drop creates a random session-bound CSRF token.

The token is included in forms for operations such as:

```text
upload
delete
```

and validated by the server before the action is performed.

The resulting flow is:

```text
authenticated session?
        │
        ├── no  → reject / redirect
        │
        └── yes
              │
              ▼
        valid CSRF token?
              │
              ├── no  → 403
              │
              └── yes → perform operation
```

Runtime testing confirmed that an authenticated request without a valid CSRF token is rejected with:

```text
403 FORBIDDEN
```

while the same operation succeeds when the valid session token is supplied.

## Multiple-file upload

The first version accepted one file per request.

The frontend originally used:

```html
<input type="file" name="file" required>
```

It was later extended to:

```html
<input type="file" name="file" multiple required>
```

The Flask backend changed from handling one file:

```python
file = request.files["file"]
```

to handling the complete list:

```python
files = request.files.getlist("file")

for file in files:
    ...
```

This allowed multiple images, PDFs, and other files to be selected and uploaded in a single operation.

## Duplicate filename handling

The original application saved uploaded files directly under their sanitized filename.

That created one undesirable behavior:

```text
existing file
     │
     ▼
upload with same name
     │
     ▼
existing file overwritten
```

Runtime testing confirmed that a second upload using the same filename replaced the original file contents.

The upload path was later changed to preserve existing files.

The current behavior is:

```text
file.txt
file_1.txt
file_2.txt
file_3.txt
...
```

A duplicate upload therefore receives a new name instead of silently replacing the previous file.

<p align="center">
  <img src="../assets/duplicate-filename-protection.png"
       alt="LAN Drop interface showing duplicate filename preservation"
       width="700">
</p>

<p align="center">
  <em>Duplicate uploads are stored separately instead of overwriting the original file.</em>
</p>

This was also verified directly on the filesystem by confirming that the original and duplicate retained different contents.

## Upload-size limit

The initial application did not define an explicit request-size limit.

A later security review tested this behavior directly and confirmed that large uploads were accepted.

LAN Drop now configures:

```text
100 MiB
```

as the maximum HTTP request body size.

This is technically a request-size limit rather than a strict individual-file limit because multipart form overhead is also part of the HTTP request.

Regression testing confirmed:

```text
20 MiB request
    │
    └── accepted

101 MiB request
    │
    ├── 413 rejected
    └── file not written to disk
```

This adds a simple resource-abuse boundary without changing the normal file-transfer workflow.

## Filename and path handling

Uploaded filenames pass through Werkzeug's:

```python
secure_filename()
```

before being used as filesystem names.

For example, a test upload named:

```text
../../evil test<>.txt
```

was stored as:

```text
evil_test.txt
```

Download path traversal was also tested against controlled files outside the upload directory.

Both raw and URL-encoded parent-directory attempts returned:

```text
404 NOT FOUND
```

and did not expose the external test file.

This is recorded as an observed runtime result rather than as a formal proof against every possible filesystem attack.

## Linux service management

LAN Drop is registered with systemd as:

```text
lan-drop.service
```

The Flask application therefore runs independently from the SSH session used to administer the Linux host.

The service is deliberately kept **disabled** so it does not start automatically when Linux boots.

Typical lifecycle:

```bash
sudo systemctl start lan-drop

systemctl status lan-drop --no-pager

sudo systemctl restart lan-drop

sudo systemctl stop lan-drop
```

This provides a practical manual workflow: start the service when file transfer is needed, then stop it afterwards.

## systemd hardening

The first systemd unit successfully handled process lifecycle management and already ran the application as a non-root user.

However, it provided relatively little process isolation.

A later review used:

```bash
systemd-analyze security lan-drop.service
```

to inspect the service configuration.

The initial result was:

```text
9.2 UNSAFE
```

The unit was then hardened with restrictions including:

```text
ProtectSystem=strict
ProtectHome=read-only
NoNewPrivileges=true
CapabilityBoundingSet=
RestrictSUIDSGID=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectKernelLogs=true
ProtectControlGroups=true
PrivateDevices=true
PrivateTmp=true
PrivateMounts=true
ProtectHostname=true
SystemCallArchitectures=native
RestrictRealtime=true
LockPersonality=true
```

Because LAN Drop is a file-upload service, the application still requires one writable area.

That exception is explicitly limited to:

```text
/home/<user>/lan-drop/uploads
```

The resulting filesystem model is approximately:

```text
host filesystem
home directory
application files
      │
      └── restricted / read-only

uploads/
      │
      └── writable
```

After hardening:

```text
Before : 9.2 UNSAFE
After  : 4.4 OKAY
```

The lower exposure result is specifically a `systemd-analyze security` assessment of the unit's sandboxing configuration. It is not a universal application-security score.

The application was regression-tested after hardening to confirm that normal upload, download, authentication, and deletion still worked.

<p align="center">
  <img src="../assets/systemd-security-hardening.png"
       alt="LAN Drop systemd security hardening result"
       width="700">
</p>

<p align="center">
  <em>systemd service exposure before and after the hardening pass.</em>
</p>

## Remote administration

The Linux host can be managed remotely over SSH from another machine on the same LAN:

```bash
ssh <user>@192.0.2.10
```

Because systemd manages the application process, the SSH session can be closed after starting LAN Drop:

```bash
sudo systemctl start lan-drop
exit
```

LAN Drop continues running until explicitly stopped.

This separation became useful throughout later debugging because application lifecycle and remote shell lifecycle remained independent.

## Why LAN Drop matters to the X600 story

LAN Drop unexpectedly became deployment infrastructure.

When Termux and Termux:X11 APKs were needed for the OMIX X600, the files were downloaded on the PC, uploaded to LAN Drop, and then pulled from the phone browser.

```text
Windows PC
    │
    │ download APK
    ▼
LAN Drop
    │
    │ local transfer
    ▼
OMIX X600
```

A project originally created simply to make local file transfer easier directly enabled the next project.

That became one of the first important lessons of the lab:

> **Small internal tools can become useful infrastructure later.**

## Security review

The project eventually reached a point where simply knowing that it "worked" was no longer enough.

A dedicated runtime security review was performed against the service.

The review covered:

```text
route exposure
authentication behavior
CSRF
filename handling
path traversal
duplicate uploads
upload size
network interfaces
TLS identity
TLS protocol behavior
PIN brute-force resistance
process privileges
systemd isolation
logging
```

The important part of the review was that observations were followed by direct runtime tests.

Examples included:

```text
source inspection
        │
        ▼
form a security assumption
        │
        ▼
send a real request
        │
        ▼
observe actual behavior
```

Several tested behaviors resulted in remediation:

```text
unlimited PIN attempts
        │
        ▼
rate limiting

no explicit CSRF token
        │
        ▼
session-bound CSRF validation

silent filename overwrite
        │
        ▼
duplicate preservation

no upload-size boundary
        │
        ▼
100 MiB request limit

outdated certificate SAN
        │
        ▼
replacement certificate

minimal systemd sandboxing
        │
        ▼
service hardening
```

Other tests, such as the tested download traversal paths and TLS protocol behavior, did not reveal a condition requiring code changes.

The complete methodology, findings, remediation, and regression results are documented separately:

[Read the security review and hardening documentation](02-security-hardening.md)

## Final regression testing

After all security changes were combined, the service was tested again as a complete system.

The regression cycle covered:

```text
service startup
HTTPS validation
certificate identity
unauthenticated access
authenticated sessions
CSRF rejection
CSRF success path
normal upload
duplicate upload
download
delete
oversized upload
filesystem effects
PIN rate limiting
systemd hardening
```

The tested application paths remained functional.

<p align="center">
  <img src="../assets/security-regression-summary.png"
       alt="LAN Drop security regression summary"
       width="700">
</p>

<p align="center">
  <em>Regression summary after the security remediation cycle.</em>
</p>

This introduced another useful engineering rule into the project:

> **A security change is not complete if the intended application behavior no longer works after the change.**

## What I learned

LAN Drop provided hands-on experience with:

- LAN addressing and private IPv4 concepts
- DHCP address changes
- listening network services
- HTTP request handling
- multipart form uploads
- frontend/backend interaction
- Flask routing
- Python virtual environments
- Linux filesystem operations
- SSH administration
- environment variables
- session-based authentication
- PIN rate limiting
- CSRF protection
- filename sanitization
- duplicate filename handling
- request-size enforcement
- TLS and HTTPS
- certificates and certificate authorities
- Subject Alternative Names
- certificate identity validation
- local certificate trust stores
- `mkcert`
- OpenSSL testing
- Linux service lifecycle management
- `systemd`
- systemd sandboxing
- process privilege reduction
- filesystem isolation
- runtime security testing
- negative testing
- regression testing
- debugging connectivity across multiple layers

One particularly useful debugging model was separating a connection problem into layers instead of treating "the site does not open" as one issue:

```text
Application
    ↑
HTTP
    ↑
TLS
    ↑
TCP
    ↑
IP / LAN
```

The security review extended that model further:

```text
Can the service be reached?
           │
           ▼
Does TLS accept the connection?
           │
           ▼
Does the certificate identify the endpoint?
           │
           ▼
Is the client authenticated?
           │
           ▼
Is the request itself authorized?
           │
           ▼
What filesystem effect can it produce?
           │
           ▼
What can the service process do on the host?
```

This made debugging and security testing much less ambiguous.

## Security considerations

LAN Drop remains a learning-focused service intended primarily for controlled local-network use.

Current protections include:

- HTTPS/TLS for encrypted transport
- certificate identity validation for configured endpoints
- 6-digit PIN access
- session-based authentication
- PIN attempt throttling
- explicit CSRF protection for state-changing operations
- filename sanitization with Werkzeug
- duplicate filename preservation
- 100 MiB request-size enforcement
- secrets stored outside application source code
- non-root execution
- systemd filesystem and process isolation

The project does **not** attempt to provide:

- individual user accounts
- role-based access control
- persistent distributed rate-limit state
- a complete structured security audit trail
- automatic certificate management for DHCP address changes

Possible future experiments include:

- structured security-event logging
- explicit session lifetime policy
- explicit cookie-policy configuration
- file-count quotas
- disk-space checks before uploads
- a dedicated Linux service account
- additional compatible systemd restrictions
- automated regression tests
- automated local certificate regeneration

These are intentionally documented as future work rather than silently presented as already implemented protections.

## Project evolution

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
       ▼
security review
       │
       ▼
runtime attack testing
       │
       ▼
rate limiting + CSRF
       │
       ▼
file-handling hardening
       │
       ▼
TLS identity remediation
       │
       ▼
systemd sandboxing
       │
       ▼
final regression verification
```

The important change was not merely adding more features.

The project moved from:

```text
does it work?
```

toward:

```text
why does it work?

what assumptions does it make?

what happens when those assumptions are tested?

does it still work after hardening?
```

## Connection to the rest of the repo

LAN Drop is not just a separate side project in this story. It is the point where the lab started developing a reusable workflow:

```text
build a tool
   ↓
use the tool
   ↓
discover a new problem
   ↓
reuse the existing tool
   ↓
extend the lab
```

The project now connects several parts of the lab: the Linux host, the Windows workstation, the OMIX X600, Apple/iOS clients, local networking experiments, and later security-testing work.

Its development also produced two separate branches of experimentation:

```text
LAN Drop
   │
   ├── network evolution
   │      │
   │      └── LAN Drop v2
   │
   └── security evolution
          │
          └── security review and hardening
```

For the next stages of the project, see:

- [LAN Drop v2 — Self-Hosted Network Mode](01.1-lan-drop-v2.md)
- [LAN Drop Security Review and Hardening](02-security-hardening.md)