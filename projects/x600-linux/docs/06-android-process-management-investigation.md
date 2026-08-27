# Android Process-Management Investigation

> Status: **Open investigation**  
> Device: **OMIX X600**  
> Android: **12 / SDK 31**  
> Environment: **Termux + TigerVNC + XFCE + Flask + OpenSSH**

## Why this investigation exists

The X600 Linux environment was individually stable with SSH, the Flask dashboard, and the XFCE/VNC desktop. Problems appeared when those components were combined and the workload became process-heavy.

The most reproducible trigger so far has been launching Firefox inside the XFCE desktop. Under that workload, existing Termux processes sometimes disappear selectively: one SSH session may die while another survives, the SSH listener may disappear while an existing `sshd-session` remains alive, or several services may terminate in quick succession.

This document records the measurements and hypotheses without treating correlation as proof.

---

## Stack under test

```text
OMIX X600 / Android 12
│
└── Termux (u0_a30)
    ├── OpenSSH
    │   ├── sshd
    │   └── sshd-session → bash
    ├── Python / Flask dashboard
    ├── TigerVNC
    │   └── Xvnc :1
    ├── XFCE
    │   ├── xfce4-session
    │   ├── xfwm4
    │   ├── xfce4-panel
    │   ├── xfdesktop
    │   ├── Thunar
    │   ├── xfce4-power-manager
    │   └── supporting DBus/GVFS services
    └── Firefox
        └── multiple content processes
```

The VNC desktop is normally started at display `:1` and exposed on TCP port `5901`.

---

## Measurement method

The main count used during the experiment was:

```bash
ps -e -o user,pid,ppid,comm | grep "^u0_a30" | wc -l
```

The process tree was inspected with:

```bash
ps -e -o pid,ppid,comm,args
```

These commands measure **processes visible under the Termux UID (`u0_a30`)**.

They do **not** expose Android's internal phantom-process accounting. Therefore:

```text
Termux UID process count ≠ Android phantom-process count
```

The counts are useful for comparing workload growth, but they must not be treated as a direct reading of Android's `max_phantom_processes` counter.

Also note that the measurement pipeline itself briefly creates processes such as `ps`, `grep`, and `wc`, so the numbers should be interpreted as approximate snapshots rather than exact persistent counts.

---

## Observed snapshots

| Snapshot | State | Termux-visible processes | Notes |
|---|---|---:|---|
| A | Termux services + one SSH session; no VNC/XFCE | **23** | Initial baseline used during the investigation |
| B | Dashboard added | **27** | Flask was running with debug/reloader enabled during this measurement |
| C | VNC server started; desktop still spawning | **40** | Transitional snapshot, not a steady state |
| D | Full TigerVNC + XFCE desktop stack | **55** | SSH, Flask, VNC and XFCE were all still alive at this point |
| E | After first Firefox-triggered failure | **34** | One SSH session had already disappeared; many previously visible processes were gone |
| F | Firefox running again | **42** | Firefox parent + multiple content processes were visible; remaining services failed shortly afterwards |
| G | Later minimal state after XFCE had actually closed | **8** | **Discarded from the XFCE comparison**; useful only as a minimal-state snapshot |

### Why snapshot G is explicitly marked as discarded

A later count of `8` was initially thought to represent an active XFCE + Firefox desktop. The desktop had actually closed without being noticed. Repeating the measurement after noticing the closed XFCE session produced the same value.

That observation is therefore **not evidence that XFCE + Firefox can run in eight Termux processes**. It is retained here only to document the correction and avoid reusing the invalid comparison later.

---

## What VNC/XFCE actually adds

The full process tree showed that starting a VNC desktop is not equivalent to adding a single `Xvnc` process.

The desktop brought up a larger process graph including:

```text
Xvnc
xfce4-session
xfwm4
xfsettingsd
xfce4-panel
Thunar --daemon
xfdesktop
xfce4-power-manager
xfce4-notifyd
dbus-launch
dbus-daemon
xfconfd
gvfsd
gvfsd-metadata
gvfsd-trash
tumblerd
upowerd
termux-battery-status
Termux API helper processes
panel plugin wrapper processes
...
```

This explains the large jump from the pre-desktop workload to the full XFCE state.

The early `40` measurement was taken while the desktop was still starting. Once the XFCE process graph had finished spawning, the count reached approximately `55`.

---

## Flask was also more expensive than it looked

During one snapshot, `python app.py` with Flask debug/reloader enabled produced a process tree similar to:

```text
python app.py
├── multiprocessing.resource_tracker
└── python app.py
    └── multiprocessing.resource_tracker
```

So the dashboard appeared as roughly four Termux-visible processes rather than one.

This was useful to identify, but disabling the Flask debugger/reloader did **not** eliminate the broader failure pattern. Therefore Flask debug mode is considered an unnecessary source of extra processes, but **not the current root-cause hypothesis**.

For normal use, the dashboard should run without the development reloader:

```bash
flask --app app run --host=0.0.0.0 --port=5000 --no-debugger --no-reload
```

or with an equivalent `debug=False, use_reloader=False` configuration in `app.py`.

---

## SSH behavior gave an important clue

One failure produced an unusual but informative state:

```text
existing SSH session    alive
new SSH connections     connection refused
```

Process inspection showed only existing session workers such as:

```text
sshd-session
└── sshd-session
    └── bash
```

while the main listener process was no longer visible.

This means an established SSH session can survive even after the process accepting **new** SSH connections has disappeared. It also explains why testing only an already-open SSH terminal can give the impression that the SSH service is healthy.

At other times the `sshd` listener was supervised by Termux `runit` services:

```text
runsvdir
└── runsv sshd
    └── sshd -D -e
```

The exact lifecycle of the listener under process pressure remains part of the investigation.

---

## Firefox as a workload trigger

Launching Firefox inside the XFCE desktop produced a multi-process tree rather than a single browser process.

A captured snapshot included a Firefox parent plus child processes for roles such as:

- fork server
- socket process
- browser tabs/content processes
- RDD/media process
- utility process

Example structure:

```text
firefox
└── firefox -contentproc ... forkserver
    ├── firefox -contentproc ... socket
    ├── firefox -contentproc ... tab
    ├── firefox -contentproc ... rdd
    ├── firefox -contentproc ... utility
    └── additional tab/content processes
```

During the second captured Firefox run, the Termux-visible process count moved from approximately `34` to `42`, and the remaining SSH/services terminated before a further SSH-specific snapshot could be captured.

The current interpretation is:

> Firefox is probably a **triggering workload**, not necessarily the underlying fault. Its rapid child-process burst increases pressure on an already process-heavy Termux desktop environment.

---

## Hypotheses tested so far

### 1. Flask debug/reloader is the root cause

**Result: weakened / mostly rejected.**

The reloader unnecessarily creates extra processes, but failures were still observed when Flask was run without debugger/reloader behavior.

### 2. `start-vnc.sh` cleanup commands are the root cause

The helper script contains aggressive cleanup commands such as:

```bash
pkill -9 -f "termux.x11"
vncserver -kill :1
pkill -9 -f "Xvnc"
pkill -9 xfce4-session
pulseaudio --kill
```

These commands deserve cleanup because broad `pkill -9` operations have unnecessary side effects.

However, the full workload could also exhibit failures when VNC was started directly with:

```bash
vncserver -localhost no -geometry 1280x720 -depth 24 :1
```

Therefore the helper script alone does not explain all observed failures.

### 3. TigerVNC itself immediately kills SSH/Flask

**Result: rejected as a simple explanation.**

A direct TigerVNC/XFCE session reached roughly `55` Termux-visible processes while SSH, Flask, VNC and XFCE all remained operational simultaneously.

So simply crossing a large process count does not guarantee an immediate failure.

### 4. Android 12 child/phantom-process management

**Result: strongest current hypothesis, not yet proven.**

The failure pattern is consistent with selective process trimming under a large child-process workload:

- Termux remains alive while individual child processes disappear.
- Existing SSH sessions can survive while the listener disappears.
- VNC/XFCE creates a large process tree.
- Firefox adds another burst of child processes.
- Failures become reproducible under heavier combined workloads.

However, the observed `55` Termux processes are **not equivalent to 55 Android phantom processes**, and the system remained stable at that count for a period of time. The hypothesis therefore requires a controlled A/B test.

---

## Android 12 context

The Termux project warns that Android 12+ can terminate phantom processes when the system-wide phantom-process limit is exceeded, and notes a default limit of `32` across apps. AOSP's `ActivityManagerConstants` also defines `DEFAULT_MAX_PHANTOM_PROCESSES = 32` and the `max_phantom_processes` DeviceConfig key.

References:

- Termux Android 12+ warning: <https://github.com/termux/termux-app#readme>
- Termux issue #2366: <https://github.com/termux/termux-app/issues/2366>
- AOSP `ActivityManagerConstants`: <https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/core/java/com/android/server/am/ActivityManagerConstants.java>
- Phantom/cached/empty process notes referenced by Termux: <https://github.com/agnostic-apollo/Android-Docs/blob/master/en/docs/apps/processes/phantom-cached-and-empty-processes.md>

This context makes Android process management a plausible explanation, but it does not by itself prove that the X600 failures were caused by the phantom-process limit.

---

## Next experiment: A/B test

The next test should change **one variable only**.

### A — current Android configuration

Reproduce the workload:

```text
SSH
 + Flask dashboard
 + TigerVNC
 + XFCE
 + Firefox
```

Record:

- Termux-visible process count at each stage
- which SSH sessions survive
- whether the SSH listener survives
- dashboard availability
- VNC/XFCE availability
- Firefox process tree

### B — increased Android phantom-process limit

First read the current value over ADB:

```bash
adb shell "/system/bin/device_config get activity_manager max_phantom_processes"
```

On Android 12, the proposed non-root test is:

```bash
adb shell "/system/bin/device_config put activity_manager max_phantom_processes 2147483647"
```

Then reproduce the **same** workload in the **same order** and compare the result.

Interpretation:

```text
A fails + B remains stable
    → strong evidence supporting the phantom-process-limit hypothesis

A fails + B also fails
    → phantom limit alone is insufficient; investigate another Android/OEM
      process-management mechanism, CPU/memory pressure, or another source
```

Rooting the phone is **not part of the current experiment**. The next step is diagnosis using the non-root ADB test, not escalating privileges.

---

## Experimental discipline for the next session

Before every measurement, record the exact state:

```text
SSH sessions:     0 / 1 / 2 / ...
Flask:            on / off
VNC server:       on / off
XFCE:             on / off
Firefox:          on / off
Termux services:  relevant runit services
```

Then record both:

```bash
ps -e -o user,pid,ppid,comm | grep "^u0_a30" | wc -l
ps -e -o pid,ppid,comm,args
```

This avoids comparing snapshots taken from different system states and prevents transient startup counts from being mistaken for steady-state counts.

---

## Current conclusion

The X600 can run the complete SSH + Flask + TigerVNC + XFCE stack simultaneously; it was observed operating with roughly `55` Termux-visible processes.

The failures appear under heavier process bursts, particularly around Firefox startup, and resemble selective process termination rather than a total Termux crash.

The most plausible current explanation is interaction with Android 12 child/phantom-process management, but that conclusion remains **provisional** until the A/B test changes `max_phantom_processes` and reproduces the same workload.

The useful result so far is not merely a suspected fix. It is a reproducible debugging trail from symptom → measurement → rejected hypotheses → narrower hypothesis → controlled next experiment.
