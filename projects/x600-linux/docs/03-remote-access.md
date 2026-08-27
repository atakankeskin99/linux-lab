# 03 — Remote Access: SSH + VNC

Once the XFCE desktop worked on the phone, the next goal was to stop typing on a phone keyboard.

The lab moved toward remote administration from a Windows PC.

## SSH directly into Termux

OpenSSH was installed inside Termux:

```bash
pkg install openssh
passwd
sshd
```

The Termux username was discovered with:

```bash
whoami
```

and the phone's Wi-Fi address with:

```bash
ip addr show wlan0
```

Termux SSH listened on port `8022`, so the Windows connection pattern became:

```bash
ssh -p 8022 <TERMUX_USER>@<PHONE_IP>
```

This removed the Linux laptop from the control path.

```text
Before:
Windows → SSH → Linux laptop → ADB → phone

After:
Windows → SSH → phone / Termux
```

## VNC for the graphical desktop

TigerVNC was added later so the XFCE desktop could be controlled from Windows with a normal keyboard and mouse.

Server package:

```bash
pkg install tigervnc
```

Password:

```bash
vncpasswd
```

The final session used display `:1`, which maps to TCP port `5901`:

```bash
vncserver -localhost no -geometry 1280x720 -depth 24 :1
```

Windows then connected with TigerVNC Viewer to:

```text
<PHONE_IP>:5901
```

## XFCE VNC startup environment

A working `~/.vnc/xstartup` required the graphics/environment variables used by DroidDesk rather than only a bare `startxfce4` call.

The important idea was that Android-hosted graphics have different assumptions from a normal desktop Linux installation.

## Recovery helper

A helper script was created so a broken or restarted GUI session could be recovered with one command:

```bash
bash ~/start-vnc.sh
```

The version tracked in this repository is in [`scripts/start-vnc.sh`](../scripts/start-vnc.sh).

## Process-lifecycle problem

SSH and VNC sometimes disappeared because Android background management killed Termux processes.

Mitigations explored:

```bash
termux-wake-lock
pkg install termux-services
sv-enable sshd
sv up sshd
```

and Android battery settings were changed so Termux / Termux:X11 could run without aggressive background restrictions.

This remains one of the important unfinished stability topics in the lab.
