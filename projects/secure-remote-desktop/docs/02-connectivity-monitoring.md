# Connectivity Monitoring and Failure Diagnosis

This document describes the monitoring added after an intermittent remote-access failure occurred during testing.

The purpose of the monitoring is not to automatically restart services or hide failures. Instead, it records the state of several network layers so that future failures can be diagnosed using evidence.

## Background

During remote desktop testing, the VNC session unexpectedly disconnected.

At first, several components were possible causes:

- TigerVNC client
- SSH tunnel
- x11vnc
- Tailscale
- Linux Wi-Fi connection
- Local router or upstream Internet connectivity

The Linux host was still powered on, but it became unreachable through Tailscale.

An SSH connection to the host's Tailscale address also timed out.

This was an important distinction: if only the VNC client had failed, SSH and Tailscale connectivity should not necessarily have disappeared at the same time.

---

## 1. Inspecting Tailscale Logs

After connectivity was restored, logs from the previous boot were inspected:

```bash
journalctl -b -1 -u tailscaled --no-pager
```

Relevant errors included:

```text
network is unreachable
no route to host
context deadline exceeded
```

Tailscale was also unable to establish connections to DERP relay servers.

This indicated that the failure was occurring below the VNC layer.

The evidence did not show that TigerVNC or x11vnc itself caused the outage.

## 2. Inspecting NetworkManager

NetworkManager logs from the previous boot were inspected:

```bash
journalctl -b -1 -u NetworkManager --no-pager
```

The Wi-Fi interface had initially connected successfully, received an IPv4 address through DHCP, and established global connectivity.

Later, NetworkManager changed state from global connectivity to:

```text
CONNECTED_SITE
```

This suggested that local network connectivity may have remained available while global Internet connectivity was no longer considered available.

The logs narrowed the investigation toward the underlying network path rather than the remote desktop application itself.

## 3. Checking the Routing Table

The current routing table was inspected:

```bash
ip route
```

The expected default route remained associated with the Wi-Fi interface:

```text
default via ROUTER_IP dev WIFI_INTERFACE
```

Existing WireGuard interfaces were also present, but their routes were limited to their own private subnets.

They were therefore not identified as the cause of the default-route failure.

## 4. Checking Active Connections

Active NetworkManager connections were inspected with:

```bash
nmcli connection show --active
```

This confirmed the expected Wi-Fi, Tailscale, loopback, and existing WireGuard interfaces.

## 5. Testing Wi-Fi Power Saving

Because intermittent wireless failures can sometimes be related to power management, the current Wi-Fi power-save state was checked:

```bash
iw dev WIFI_INTERFACE get power_save
```

The result was:

```text
Power save: off
```

This removed Wi-Fi power saving as an immediate explanation for the observed failure.

## 6. Testing Local and Internet Connectivity

The router was tested independently:

```bash
ping -c 5 ROUTER_IP
```

External IP connectivity was then tested:

```bash
ping -c 5 1.1.1.1
```

At the time of testing, both completed without packet loss.

The Wi-Fi link was also inspected:

```bash
iw dev WIFI_INTERFACE link
```

The connection showed a strong signal and normal link operation.

These tests showed that the network was healthy after recovery, but they could not explain exactly what had happened during the earlier outage.

That created an observability problem: the failure was intermittent and disappeared before detailed diagnostics could be collected.

---

# Monitoring Approach

Instead of automatically restarting NetworkManager, Tailscale, or x11vnc, a lightweight monitoring script was introduced.

The script periodically records four independent signals:

```text
Router connectivity
Internet connectivity
Tailscale peer connectivity
Wi-Fi signal
```

Each observation is written with a timestamp.

Example:

```text
2026-09-17 21:08:40 | router=OK internet=OK tailscale=OK wifi=-37 dBm
2026-09-17 21:09:10 | router=OK internet=OK tailscale=OK wifi=-37 dBm
```

This creates a simple connectivity timeline that can be inspected after an intermittent failure.

## Failure Domains

The combination of results helps identify which layer failed.

### Local Network Failure

```text
router=FAIL
internet=FAIL
tailscale=FAIL
```

Likely investigation area:

```text
Wi-Fi interface
wireless driver
access point
local network
```

### Upstream Internet Failure

```text
router=OK
internet=FAIL
tailscale=FAIL
```

The host can still reach the local gateway, but external connectivity is unavailable.

Likely investigation area:

```text
router WAN connection
ISP
upstream routing
```

### Tailscale Failure

```text
router=OK
internet=OK
tailscale=FAIL
```

The underlying Internet connection is operational while the selected Tailscale peer cannot be reached.

Likely investigation area:

```text
tailscaled
Tailscale connectivity
DERP connectivity
peer availability
```

A failed peer ping alone does not prove that the local Tailscale daemon is broken, because the remote peer itself may also be offline.

Additional Tailscale diagnostics should therefore be collected before drawing a conclusion.

### Remote Desktop Failure

```text
router=OK
internet=OK
tailscale=OK
```

while the remote desktop remains unavailable.

Investigation can then move upward in the stack:

```text
SSH tunnel
x11vnc service
VNC client
```

---

# Monitoring Script

The repository contains:

```text
scripts/network-watch.sh
```

The script uses configurable values for:

```text
ROUTER_IP
INTERNET_TARGET
TAILSCALE_PEER
WIFI_INTERFACE
INTERVAL
```

A typical interval is 30 seconds.

The monitor intentionally performs observation only.

It does not:

```text
restart NetworkManager
restart tailscaled
restart x11vnc
reboot the host
modify routes
reconnect Wi-Fi
```

This is deliberate.

Automatically recovering from a failure before collecting evidence could hide the actual cause.

---

# Running the Monitor with systemd

The repository contains an example service:

```text
systemd/network-watch.service
```

After adapting the username and paths for the target machine, install it with:

```bash
sudo cp systemd/network-watch.service /etc/systemd/system/network-watch.service
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable and start the service:

```bash
sudo systemctl enable --now network-watch
```

Verify:

```bash
systemctl status network-watch --no-pager
```

The expected state is:

```text
active (running)
```

The service is enabled so monitoring resumes automatically after a reboot.

---

# Inspecting the Log

View recent observations:

```bash
tail -n 30 ~/network-watch.log
```

Search for detected failures:

```bash
grep FAIL ~/network-watch.log
```

When investigating an outage, the timestamps in this file can be correlated with system logs.

For example:

```bash
journalctl -u tailscaled
journalctl -u NetworkManager
```

For a previous boot:

```bash
journalctl -b -1 -u tailscaled
journalctl -b -1 -u NetworkManager
```

Kernel messages may also be useful when investigating wireless driver or interface problems:

```bash
journalctl -b -1 -k
```

---

# Troubleshooting Strategy

The resulting troubleshooting process is:

```text
Remote desktop unavailable
          |
          v
Check monitoring timeline
          |
          +--> Router failed?
          |       |
          |       +--> Investigate Wi-Fi / local network
          |
          +--> Internet failed?
          |       |
          |       +--> Investigate gateway / ISP
          |
          +--> Tailscale failed?
          |       |
          |       +--> Investigate Tailscale / peer reachability
          |
          +--> Everything still OK?
                  |
                  +--> Investigate SSH / x11vnc / VNC client
```

The key principle is to identify the lowest failing layer before troubleshooting applications above it.

# Current Status

The exact root cause of the original intermittent network failure has not yet been proven.

The investigation established that:

- the failure was not limited to the VNC client;
- SSH through Tailscale also became unreachable;
- Tailscale subsequently reported underlying network reachability errors;
- Wi-Fi power saving was disabled;
- routing appeared normal after recovery;
- local and external connectivity were healthy after reboot.

The monitoring service was therefore added to capture better evidence if the problem occurs again.

Future investigation should use the monitoring timestamps together with NetworkManager, kernel, and Tailscale logs before making configuration changes.