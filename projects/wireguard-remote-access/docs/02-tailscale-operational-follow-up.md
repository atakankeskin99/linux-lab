# Operational Follow-up — Replacing the Public VPS with Tailscale

## Context

The previous lab, [`01-remote-access-through-cgnat.md`](01-remote-access-through-cgnat.md), solved remote SSH access to a Linux Mint machine behind CGNAT by building the path manually.

That design used:

- a public Oracle Cloud VPS
- WireGuard peers on Windows, Linux Mint, and the VPS
- a routed overlay network
- Linux IP forwarding
- `iptables` INPUT and FORWARD rules
- persistent WireGuard services
- packet-level troubleshooting with `tcpdump`

The purpose of that setup was not simply to obtain remote access.

The real objective was to understand what has to happen at the networking layer when two machines cannot reach each other directly because one side is behind CGNAT.

By the end of the lab, that objective had been achieved.

The manual WireGuard + VPS design had already demonstrated:

- why normal inbound port forwarding fails behind CGNAT
- how a public rendezvous point solves reachability
- how WireGuard peers are routed through a hub
- how `AllowedIPs` affect routing
- why persistent keepalives matter
- how host and cloud firewalls interact
- how Linux forwarding changes a host into a router
- how to follow packets with `tcpdump`
- how to make the setup survive reboots

At that point, continuing to run and maintain the VPS no longer added much educational value for the original goal.

The manual setup had completed its mission.

For normal day-to-day remote access, a higher-level solution became the more sensible choice.

---

## Why Tailscale

Tailscale was chosen as the operational replacement for the manually maintained VPS-based WireGuard topology.

The reason was not that the original WireGuard design was wrong.

It worked.

The reason was that the difficult parts of the problem had already been explored manually, and there was no need to keep operating the infrastructure forever just to preserve remote access.

Tailscale keeps WireGuard as the encrypted transport foundation while abstracting much of the coordination work that had previously been handled manually.

This includes:

- peer discovery
- NAT traversal
- endpoint coordination
- stable overlay addressing
- key distribution
- roaming between networks
- fallback relaying when direct peer-to-peer connectivity cannot be established
- DNS naming through MagicDNS

The operational goal changed from:

> Build and understand the network path manually.

to:

> Keep reliable remote access without maintaining unnecessary infrastructure.

This is an important distinction.

The first lab was intentionally lower-level because the goal was learning.

The Tailscale setup is intentionally higher-level because the goal is now usability.

---

## Previous Architecture

The manual design looked like this:

```text
Windows Client
10.20.20.3
      |
      | WireGuard
      v
Public VPS
10.20.20.1
      |
      | routing + forwarding
      v
Linux Mint
10.20.20.2
      |
      v
SSH
```

The VPS was always part of the data path.

It provided the public Internet presence that the CGNAT-connected Linux machine could not provide itself.

That required maintaining:

- the cloud instance
- the public endpoint
- the WireGuard server configuration
- forwarding rules
- firewall rules
- persistence
- the VM lifecycle itself

Once the learning objective was complete, this was more infrastructure than the operational requirement actually needed.

---

## Retiring the VPS

The Oracle Cloud VM was intentionally terminated after the original lab was complete.

The cleanup included verifying that no unnecessary cloud resources remained:

- compute instance terminated
- boot volume terminated
- no extra block volumes
- no reserved public IPv4 address
- cost analysis remained at `0.00 EUR`

The purpose was to fully retire the manual infrastructure rather than leave an unused server running indefinitely.

The documentation remains in this repository because the value of the project is in the architecture, troubleshooting process, and lessons learned — not in keeping the VPS alive forever.

---

## Installing Tailscale on Linux Mint

Tailscale was installed on the Linux Mint host:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

The node was then authenticated with:

```bash
sudo tailscale up
```

After authentication:

```bash
tailscale status
tailscale ip -4
```

showed the Linux machine on the tailnet with the address:

```text
100.106.144.23
```

The hostname was:

```text
atakan-x550ca
```

---

## Adding the Windows Client

Tailscale was also installed on the Windows machine and authenticated into the same tailnet.

The resulting node addresses were:

```text
Linux Mint -> 100.106.144.23
Windows    -> 100.90.57.66
```

With both machines on the same local network, `tailscale status` showed a direct connection:

```text
active; direct 192.168.1.101:41641
```

This confirmed that Tailscale could establish a peer-to-peer path without relaying traffic when the network conditions allowed it.

---

## Remote Test Across Different Networks

The more important test was performed with the two machines on different networks.

The Linux Mint machine remained on the home Internet connection.

The Windows client was moved to a mobile hotspot.

This recreated the real remote-access scenario:

```text
Linux Mint
Home Network
    |
    | CGNAT / NAT
    v
Internet
    ^
    |
Mobile Network
    |
Windows
```

The Windows client then reached the Linux Mint Tailscale address:

```powershell
ping 100.106.144.23
```

and received replies successfully.

SSH was then opened through the Tailscale overlay:

```powershell
ssh atakan@100.106.144.23
```

The connection succeeded.

The Linux host recorded the source as:

```text
100.90.57.66
```

which was the Windows machine's Tailscale address.

This confirmed that the SSH session was traversing the tailnet rather than the normal LAN.

---

## Direct vs DERP

After the Windows machine moved to the mobile hotspot, Tailscale could no longer establish a direct peer-to-peer path.

The Linux host reported:

```text
active; relay "fra"
```

and:

```bash
tailscale ping 100.90.57.66
```

returned results similar to:

```text
pong from desktop-clgj3km (...) via DERP(fra)
```

followed by:

```text
direct connection not established
```

This was one of the most useful observations in the follow-up.

Tailscale first attempts direct connectivity between peers.

If NAT conditions prevent that, it can fall back to a DERP relay.

In this case, the relay was in Frankfurt.

That produced a path conceptually similar to:

```text
Windows
   |
   | encrypted Tailscale traffic
   v
DERP Frankfurt
   |
   v
Linux Mint
   |
   v
SSH
```

However, this is not identical to the previous VPS design.

The old VPS was always part of the route.

DERP is a fallback.

If direct peer-to-peer connectivity becomes possible, Tailscale can use it instead.

That distinction is important.

---

## MagicDNS

The next improvement was to remove the need to remember the Tailscale IP address.

Instead of:

```powershell
ssh atakan@100.106.144.23
```

the Windows machine could use:

```powershell
ssh atakan@atakan-x550ca
```

MagicDNS resolved:

```text
atakan-x550ca
```

to:

```text
100.106.144.23
```

This means the remote access workflow no longer depends on:

- the home LAN address
- the public WAN address
- the VPS address
- memorizing the overlay IP

The host can be reached using its Tailscale name.

---

## Reboot Persistence

The Linux Mint machine was rebooted remotely:

```bash
sudo reboot
```

The SSH session disconnected as expected.

After the machine started again, no manual `tailscale up` command was required.

From Windows:

```powershell
ping atakan-x550ca
```

resolved the MagicDNS name and reached the host again.

A new SSH session was then opened:

```powershell
ssh atakan@atakan-x550ca
```

and succeeded.

This verified that:

- `tailscaled` starts automatically
- the node rejoins the tailnet
- MagicDNS becomes available again
- standard OpenSSH remains reachable
- the system recovers after reboot without rebuilding the network setup

---

## Lid-Closed Remote Operation

The final operational goal was to use the Linux laptop as a small remotely managed node while its lid remained closed and the machine stayed connected to external power.

The systemd login configuration was adjusted:

```ini
HandleLidSwitch=suspend
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
```

This keeps the normal suspend behavior available in general while allowing the machine to remain running when used as an externally powered headless node.

After reboot, the lid was closed while the laptop remained on AC power.

The existing SSH session stayed alive.

More importantly, the existing session was then closed and a completely new connection was opened from Windows:

```powershell
ssh atakan@atakan-x550ca
```

The new connection succeeded while the laptop lid remained closed.

This confirmed that the machine could now operate as a headless Linux node reachable remotely through Tailscale.

---

## Final Operational Architecture

The active setup now looks like this:

```text
Windows
   |
   | Tailscale
   |
   | direct peer-to-peer when possible
   | DERP fallback when necessary
   v
Linux Mint
atakan-x550ca
100.106.144.23
   |
   v
OpenSSH
```

The system no longer depends on:

- a self-managed public VPS
- a public IPv4 address at home
- router port forwarding
- a fixed home WAN address
- manual WireGuard hub routing
- Linux forwarding on a cloud server
- custom VPS firewall rules
- a remembered overlay IP address

The Linux machine can remain behind CGNAT and still be reached remotely.

---

## Manual WireGuard vs Tailscale

The two solutions serve different purposes in this project.

### Manual WireGuard + VPS

Best for learning:

- exposed the network architecture
- required manual peer configuration
- required public infrastructure
- required firewall and forwarding work
- made the CGNAT problem visible
- forced packet-level troubleshooting
- demonstrated how routing actually worked

### Tailscale

Best for ongoing operation:

- dramatically reduces maintenance
- automatically coordinates peers
- handles network changes
- attempts direct connectivity
- falls back to DERP when necessary
- provides stable node identity
- provides MagicDNS
- preserves the same standard SSH workflow

The important point is that Tailscale did not replace the value of the original lab.

It became useful because the original lab had already made the hidden layers understandable.

---

## Final Result

The project now has two distinct phases.

### Phase 1 — Understand the Problem

Build the remote-access path manually with:

```text
CGNAT
  ↓
public VPS
  ↓
WireGuard
  ↓
routing
  ↓
firewall rules
  ↓
SSH
```

### Phase 2 — Operate the Solution

Replace the permanently maintained lab infrastructure with:

```text
Tailscale
  ↓
MagicDNS
  ↓
OpenSSH
```

while preserving remote access across different networks and behind CGNAT.

The original WireGuard setup completed its mission as a learning lab.

Tailscale is now the practical operational layer.

That transition is intentional.

The point of the project was never to prove that every layer must be managed manually forever.

The point was to understand those layers well enough to know what a higher-level tool is doing on their behalf.
