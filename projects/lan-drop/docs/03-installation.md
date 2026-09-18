# LAN Drop V1 installation

This guide installs LAN Drop on an existing local network. It currently targets Ubuntu 24.04 and Linux Mint 22.

## Requirements

* an Ubuntu 24.04 or Linux Mint 22 host using systemd
* `sudo` access
* an Internet connection during installation for APT and Python packages
* client devices connected to the same trusted LAN

## Install

From the repository:

```bash
cd projects/lan-drop
chmod +x install.sh uninstall.sh scripts/doctor.sh
sudo ./install.sh
```

The installer asks for a six-digit PIN and then:

* installs Python, `venv`, and OpenSSL when needed
* creates an isolated Python environment
* creates a dedicated `lan-drop` system user
* stores the application in `/opt/lan-drop`
* stores uploads in `/var/lib/lan-drop/uploads`
* stores secrets and TLS material in `/etc/lan-drop`
* installs and starts a hardened systemd service
* generates a local CA and a server certificate for the host's current IPv4 addresses

The service is deliberately left disabled at boot.

Open one of the URLs printed by the installer. Until the CA is trusted on the client, the browser will show a certificate warning.

## Trust the LAN Drop CA

The exported public CA certificate is:

```text
/var/lib/lan-drop/lan-drop-ca.crt
```

Copy this **public certificate only** to each client. Never copy `/etc/lan-drop/tls/ca.key`; that private key can issue certificates trusted by devices that install the LAN Drop CA.

One simple way to copy the public certificate to another machine is:

```bash
scp <host-user>@<host-ip>:/var/lib/lan-drop/lan-drop-ca.crt .
```

### Windows

1. Copy `lan-drop-ca.crt` to the Windows client.
2. Double-click it and select **Install Certificate**.
3. Select **Current User**.
4. Select **Place all certificates in the following store**.
5. Place it in **Trusted Root Certification Authorities**.
6. Complete the installation and restart the browser.

You can verify the installation from PowerShell:

```powershell
certutil -user -store Root "LAN Drop Local CA"
```

Installing this CA grants trust to certificates signed by the LAN Drop private CA. Do this only on devices you control.

### Android

1. Copy `lan-drop-ca.crt` to the device.
2. Open **Settings → Security → Encryption & credentials**.
3. Choose **Install a certificate → CA certificate**.
4. Select `lan-drop-ca.crt` and accept Android's warning.

Menu names vary by Android vendor and version. Some browsers or applications may not honor user-installed CAs.

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

The script checks:

* systemd unit installation
* configuration availability
* CA and server certificate availability
* upload-directory permissions
* service state
* TCP port 8080

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

The server certificate includes the IPv4 addresses detected during installation.

If the host receives a different DHCP address, run the installer again:

```bash
sudo ./install.sh
```

The installer reuses the existing CA and issues a new server certificate containing the currently detected IPv4 addresses. Clients that already trust the CA do not need to import it again.

A DHCP reservation on the router is recommended for a stable local URL.

## Uninstall

```bash
sudo ./uninstall.sh
```

The uninstaller:

* stops and removes the systemd service
* removes the application from `/opt/lan-drop`
* removes secrets, the private CA key, and server-side TLS material from `/etc/lan-drop`
* deliberately preserves `/var/lib/lan-drop` so uploaded files are not deleted automatically

Because `/var/lib/lan-drop` is preserved, the exported public CA certificate may remain at:

```text
/var/lib/lan-drop/lan-drop-ca.crt
```

After confirming that no required uploads remain, the preserved data and the dedicated system user can be removed manually:

```bash
sudo rm -rf -- /var/lib/lan-drop
sudo userdel lan-drop
```

CA certificates installed on client devices are not removed by the server-side uninstaller. They must be removed separately from each client's trust store.

For a Windows CA installed under the current user, first identify the certificate:

```powershell
certutil -user -store Root "LAN Drop Local CA"
```

Then remove it using the certificate's SHA-1 hash:

```powershell
certutil -user -delstore Root <certificate-sha1-hash>
```
