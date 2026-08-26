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
