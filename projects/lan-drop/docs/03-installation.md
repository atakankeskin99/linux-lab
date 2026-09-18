# LAN Drop V1 installation

This guide installs LAN Drop on an existing local network. It currently targets Ubuntu 24.04 and Linux Mint 22.

## Requirements

- an Ubuntu 24.04 or Linux Mint 22 host using systemd
- `sudo` access
- an Internet connection during installation for APT and Python packages
- client devices connected to the same trusted LAN

## Install

From the repository:

```bash
cd projects/lan-drop
chmod +x install.sh uninstall.sh scripts/doctor.sh
sudo ./install.sh
```

The installer asks for a six-digit PIN and then:

- installs Python, `venv`, and OpenSSL when needed
- creates an isolated Python environment
- creates a dedicated `lan-drop` system user
- stores the application in `/opt/lan-drop`
- stores uploads in `/var/lib/lan-drop/uploads`
- stores secrets and TLS material in `/etc/lan-drop`
- installs and starts a hardened systemd service
- generates a local CA and a server certificate for the host's current IPv4 addresses

The service is deliberately left disabled at boot.

Open one of the URLs printed by the installer. Until the CA is trusted on the client, the browser will show a certificate warning.

## Trust the LAN Drop CA

The public CA certificate is:

```text
/var/lib/lan-drop/lan-drop-ca.crt
```

Copy this **public certificate only** to each client. Never copy `/etc/lan-drop/tls/ca.key`; that private key can issue trusted LAN Drop certificates.

One simple way to copy the certificate from another Linux machine is:

```bash
scp <host-user>@<host-ip>:/var/lib/lan-drop/lan-drop-ca.crt .
```

### Windows

1. Copy `lan-drop-ca.crt` to the Windows client.
2. Double-click it and select **Install Certificate**.
3. Select **Local Machine**.
4. Place it in **Trusted Root Certification Authorities**.
5. Restart the browser.

This grants trust to certificates signed by this private CA. Do it only on devices you control.

### Android

1. Copy `lan-drop-ca.crt` to the device.
2. Open **Settings → Security → Encryption & credentials**.
3. Choose **Install a certificate → CA certificate**.
4. Select `lan-drop-ca.crt` and accept Android's warning.

Menu names vary by Android vendor and version. Some browsers or apps may not honor user-installed CAs.

### Ubuntu / Linux Mint

```bash
sudo cp lan-drop-ca.crt /usr/local/share/ca-certificates/lan-drop-ca.crt
sudo update-ca-certificates
```

Restart the browser after updating the trust store.

## Verify the installation

Run the included diagnostic script on the host:

```bash
sudo ./scripts/doctor.sh
```

You can also verify the health endpoint using the generated CA:

```bash
curl --cacert /etc/lan-drop/tls/ca.crt https://<host-ip>:8080/healthz
```

Expected response:

```json
{"status":"ok"}
```

## Service lifecycle

```bash
sudo systemctl start lan-drop
systemctl status lan-drop --no-pager
sudo systemctl restart lan-drop
sudo systemctl stop lan-drop
journalctl -u lan-drop -n 50 --no-pager
```

## Address changes

The server certificate includes the IPv4 addresses detected during installation. If the host receives a different DHCP address, run the installer again. It reuses the existing CA and issues a new server certificate, so clients that already trust the CA do not need to import it again.

A DHCP reservation on the router is recommended for a stable URL.

## Uninstall

```bash
sudo ./uninstall.sh
```

The uninstaller removes the service, application, secrets, and certificates. Uploaded files are deliberately preserved in `/var/lib/lan-drop/uploads`.
