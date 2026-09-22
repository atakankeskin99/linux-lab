# LAN Drop V2 hotspot installation

V2 adds an optional, self-hosted Wi-Fi network to an existing LAN Drop V1 installation. The application remains unchanged; NetworkManager provides the network and the **lan-drop** launcher coordinates the hotspot with the systemd service.

## Requirements

* a working V1 installation
* Ubuntu 24.04 or Linux Mint 22 using NetworkManager
* a Wi-Fi adapter and driver that advertise AP mode
* local terminal access for the first hotspot activation

V2 is designed for a host with one Wi-Fi adapter. Activating the hotspot disconnects that adapter from its current Wi-Fi network.

## Install

From the repository:

```bash
cd projects/lan-drop
chmod +x install-v2.sh uninstall-v2.sh scripts/doctor-v2.sh
sudo ./install-v2.sh
```

The installer:

* confirms that V1 is installed
* installs NetworkManager and **iw** when needed
* verifies that the Wi-Fi hardware advertises AP mode
* selects the Wi-Fi interface
* asks for an 8-63 character hotspot password
* creates a non-autoconnecting **LAN-Drop** NetworkManager profile
* reissues the server certificate with **10.42.0.1** in its Subject Alternative Names
* installs the launcher as **/usr/local/bin/lan-drop**

The existing CA is reused. Clients that already trust it do not need to import it again.

The installer does not activate the hotspot.

## Verify the installation

```bash
sudo ./scripts/doctor-v2.sh
```

This verifies the V1 dependency, V2 configuration, launcher, NetworkManager profile, AP-mode capability, and hotspot certificate identity.

## Start V2

Run this command locally on the Linux host:

```bash
sudo lan-drop start
```

Then connect a client to:

```text
SSID: LAN-Drop
URL:  https://10.42.0.1:8080
```

Use the hotspot password chosen during installation and the six-digit LAN Drop PIN chosen during V1 installation.

> On a single-adapter host, **lan-drop start** replaces the current Wi-Fi connection with the hotspot. An SSH or Tailscale session using that adapter will disconnect.

The launcher starts the application service before switching the Wi-Fi adapter. This allows LAN Drop to remain ready even if the administrative connection disappears during the network transition.

## Check status

```bash
sudo lan-drop status
```

The command reports the hotspot and application service independently.

## Stop V2

```bash
sudo lan-drop stop
```

This stops the application service and deactivates the hotspot. NetworkManager can then reconnect the host to an available saved Wi-Fi network.

## TLS trust

The V2 endpoint is:

```text
https://10.42.0.1:8080
```

The installer adds **10.42.0.1** to the server certificate. The client must still trust the V1 public CA certificate:

```text
/var/lib/lan-drop/lan-drop-ca.crt
```

See [LAN Drop V1 installation](03-installation.md) for client CA installation.

## Uninstall V2 only

```bash
sudo ./uninstall-v2.sh
```

This removes:

* the **LAN-Drop** NetworkManager profile
* **/usr/local/bin/lan-drop**
* **/etc/lan-drop/v2.env**

The V1 application, service, CA, secrets, and uploaded files remain installed.

Running the main V1 uninstaller also removes installed V2 network and launcher components before removing V1.

---

## Hardware validation

V2 was successfully validated on an ASUS X550CA running Linux Mint 22 XFCE.

The test covered hotspot activation, client association and DHCP, HTTPS access at `10.42.0.1:8080`, hotspot shutdown and Wi-Fi recovery, and V2 uninstallation.

All hardware acceptance checks passed.
