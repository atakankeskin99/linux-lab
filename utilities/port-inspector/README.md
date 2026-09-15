# Port Inspector

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Network](https://img.shields.io/badge/network-TCP-orange)
![Status](https://img.shields.io/badge/status-v0.1-success)

A lightweight Linux CLI utility for inspecting listening TCP ports and identifying the processes behind them.

Port Inspector combines socket information from `ss` with local interface information from `ip` to provide a clearer view of what is listening on a Linux machine.

## What It Does

Port Inspector currently shows:

- listening IPv4 TCP ports
- local bind addresses
- basic bind-scope classification
- process names
- process IDs
- multiple processes associated with the same listening socket
- filtering by a specific port

Example output:

```text
PORT    ADDRESS           SCOPE             PROCESS
---------------------------------------------------------------------------
631     127.0.0.1         LOOPBACK          cupsd (954)
38969   100.106.144.23    TAILSCALE         tailscaled (958)
53      127.0.0.53        LOOPBACK          systemd-resolve (706)
22      0.0.0.0           ALL_INTERFACES    sshd (1337), systemd (1)
53      127.0.0.54        LOOPBACK          systemd-resolve (706)
```

## Usage

Show all detected listening IPv4 TCP ports:

```bash
sudo python3 port_inspector.py
```

Inspect a specific port:

```bash
sudo python3 port_inspector.py --port 22
```

Example:

```text
PORT    ADDRESS           SCOPE             PROCESS
---------------------------------------------------------------------------
22      0.0.0.0           ALL_INTERFACES    sshd (1337), systemd (1)
```

Another example:

```bash
sudo python3 port_inspector.py --port 631
```

```text
PORT    ADDRESS           SCOPE             PROCESS
---------------------------------------------------------------------------
631     127.0.0.1         LOOPBACK          cupsd (954)
```

Display CLI help:

```bash
python3 port_inspector.py --help
```

## Scope Classification

The current version performs basic bind-address classification.

| Bind Address | Classification |
| --- | --- |
| `127.x.x.x` | `LOOPBACK` |
| `0.0.0.0` | `ALL_INTERFACES` |
| Address assigned to `tailscale0` | `TAILSCALE` |
| Address assigned to another known local interface | Interface name |
| Unresolved address | `UNKNOWN` |

These classifications describe where a socket is bound.

They do not guarantee that the port is reachable from another device or from the public internet. Firewall rules, routing, NAT, and other network controls may still affect actual reachability.

## How It Works

Port Inspector uses standard Linux networking tools and Python's standard library.

Listening IPv4 TCP sockets are collected with:

```bash
ss -H -lntp4
```

Local IPv4 interface information is collected with:

```bash
ip -br -4 addr
```

The script then:

1. collects listening sockets
2. parses local addresses and ports
3. extracts process names and PIDs
4. handles multiple processes associated with the same listening socket
5. maps local addresses to interfaces
6. classifies the bind scope
7. optionally filters results by port

No third-party Python packages are currently required.

## Real-World Validation

The utility was tested against the LAN Drop service included in this repository.

With LAN Drop stopped:

```bash
sudo python3 port_inspector.py --port 8080
```

No listening socket was detected.

After starting LAN Drop:

```bash
sudo systemctl start lan-drop
```

Port Inspector detected:

```text
PORT    ADDRESS           SCOPE             PROCESS
---------------------------------------------------------------------------
8080    0.0.0.0           ALL_INTERFACES    python (3324)
```

The detected PID matched the Python process reported by `systemd`, and the LAN Drop service was independently confirmed to be reachable over the local network.

After stopping the service again:

```bash
sudo systemctl stop lan-drop
```

port `8080` disappeared from the Port Inspector output.

This validated the utility against a real service lifecycle rather than only static test data.

## Current Scope

Version `0.1` intentionally focuses on a small feature set:

- Linux only
- IPv4 only
- TCP listening sockets
- process and PID discovery
- basic bind-scope classification
- single-port filtering

The following are not currently implemented:

- UDP inspection
- IPv6 inspection
- firewall analysis
- external reachability testing
- public exposure detection

## Requirements

- Linux
- Python 3
- `iproute2`
  - `ss`
  - `ip`

Process and PID information may require elevated privileges, so the utility is normally run with `sudo`.

## License

Port Inspector is part of the Linux Lab repository and is covered by the repository's [MIT License](../../LICENSE).