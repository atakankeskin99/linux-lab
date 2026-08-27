# 04 — First Deployed App: X600 System Dashboard

After the Linux environment became usable remotely, the project needed something of its own running on top of it.

The first application was a small Flask system dashboard.

## Goal

Expose basic X600/Termux metrics over the LAN:

- device model
- Android version
- architecture
- hostname
- Wi-Fi address
- RAM
- storage
- battery when accessible
- uptime when accessible
- SSH / VNC / XFCE process status

The browser on the Windows PC accessed the service at:

```text
http://<PHONE_IP>:5000
```

## First failure: psutil

The initial plan used `psutil`, but installing it under the Termux Python environment failed because its build rejected the Android platform:

```text
platform android is not supported
```

The project therefore changed to standard-library code plus `/proc`, `/sys`, `getprop`, `ip`, and process queries.

## Second failure: `/proc/loadavg`

The first working Flask version returned HTTP 500 because Android denied access to:

```text
/proc/loadavg
```

with:

```text
PermissionError: [Errno 13] Permission denied: '/proc/loadavg'
```

That changed the design again.

A system monitor should not crash because one metric is unavailable. The replacement implementation treats Android-specific metrics as optional and returns `N/A` when a source cannot be read.

## Result

The dashboard successfully served live data from the X600 to the Windows browser.

At one point it showed roughly:

```text
Device       X600
Android      12
Architecture aarch64
IP           local LAN address
RAM          live values
SSH          RUNNING
```

Some values remained incomplete because Android exposes or restricts them differently from normal Linux.

## Next version

The browser dashboard proved the environment could host an application, but the next design goal is more appropriate to the XFCE desktop:

> turn the monitor into a real desktop application launched from an XFCE icon instead of using a browser tab.

That can reuse the same metric functions while replacing Flask with a lightweight GUI toolkit.
