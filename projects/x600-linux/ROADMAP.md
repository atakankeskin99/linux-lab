# Roadmap

## Short term

- Stabilize `sshd` under Android background-process management.
- Make VNC/XFCE process detection accurate.
- Read Android battery state through a more reliable Android-aware interface.
- Improve storage reporting so it represents useful device storage instead of only the Termux root view.
- Add periodic metric refresh without manually reloading the page.

## Next application milestone

Turn the browser dashboard into a lightweight XFCE desktop application with a launcher icon.

Possible implementation directions:

- Tkinter for minimum dependencies
- Qt/PySide for a richer native desktop UI

The system-metric functions should remain separate from the UI so both web and desktop frontends can reuse them.

## Long term

Revisit the MediaTek/native Linux path as a separate research branch, with emphasis on:

- reproducible kernel build environment
- known-good vendor toolchain
- boot image structure
- device tree / DTBO
- display and touch support
- storage and USB support
- recovery strategy before any boot experiments

## Android process-management investigation

Before changing the remote-access architecture, run a controlled A/B test for the Android 12 phantom-process hypothesis.

1. Record a clean baseline with the exact number of SSH sessions.
2. Start the Flask dashboard without debugger/reloader mode.
3. Start TigerVNC/XFCE and wait for the desktop process tree to settle.
4. Launch Firefox inside XFCE and capture the process tree immediately.
5. Repeat the same sequence after changing Android 12 `max_phantom_processes` through ADB.
6. Compare which processes disappear and whether SSH, dashboard, VNC and XFCE remain available.

Do not treat `ps` counts under `u0_a30` as Android's internal phantom-process count. Root access is out of scope for this stage; complete the non-root ADB experiment first.
