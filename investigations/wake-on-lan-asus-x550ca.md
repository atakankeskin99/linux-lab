# Wake-on-LAN Investigation — ASUS X550CA

## Overview

This investigation documents an unsuccessful attempt to enable Wake-on-LAN (WoL) on an ASUS X550CA running Linux Mint.

The goal was to determine whether the laptop could be powered on or resumed remotely by sending a Wake-on-LAN magic packet to its wired Ethernet interface.

The investigation focused on:

- NIC Wake-on-LAN capability
- Linux driver configuration
- ACPI wake permissions
- kernel wakeup state
- magic-packet delivery
- suspend and shutdown behavior
- BIOS power-management settings
- Linux driver alternatives

The final result was negative: the machine did not wake from either suspend or shutdown despite the operating system, network driver, and packet-delivery checks appearing to be configured correctly.

Because of that outcome, this document is intentionally kept as an investigation rather than presented as a working project.

---

## Test System

The test machine was an ASUS X550CA.

Relevant Ethernet hardware:

```text
Interface: enp3s0f2
PCI device: 03:00.2
Vendor/device ID: 10ec:8168
Subsystem: 1043:200f
```

The controller was detected as a Realtek RTL8111/8168-family Ethernet device.

The actual MAC address is intentionally omitted.

---

## Investigation Summary

| Check | Result |
|---|---|
| Ethernet interface operational | PASS |
| NIC reports Wake-on-LAN support | PASS |
| Magic-packet mode (`g`) enabled | PASS |
| Magic packet observed on the host | PASS |
| ACPI `GLAN` wake entry enabled | PASS |
| Kernel device wakeup enabled | PASS |
| BIOS power-saving option adjusted | PASS |
| Wake from suspend (S3) | FAIL |
| Wake from shutdown (S5) | FAIL |
| Stock `r8169` driver | FAIL |
| Alternative `r8168` driver | FAIL |
| Second Ethernet cable | FAIL |
| System restored to stock driver state | PASS |

---

## Wake-on-LAN Requirements

Wake-on-LAN depends on more than simply sending a magic packet.

For the complete wake path to work:

```text
Remote sender
      |
      v
Ethernet network
      |
      v
NIC receives magic packet
      |
      v
NIC remains powered in sleep/off state
      |
      v
Firmware / ACPI accepts wake event
      |
      v
System powers on or resumes
```

A failure at any one of these layers prevents Wake-on-LAN from working.

---

## NIC Capability Check

The Ethernet interface was inspected with `ethtool`:

```bash
sudo ethtool enp3s0f2
```

The driver reported:

```text
Supports Wake-on: pumbg
```

The `g` flag indicates support for waking on a magic packet.

Magic-packet mode was enabled with:

```bash
sudo ethtool -s enp3s0f2 wol g
```

The interface then reported:

```text
Wake-on: g
```

At the Linux driver level, the NIC therefore appeared to support the required wake mode and accepted the configuration successfully.

---

## Magic-Packet Delivery

Before testing suspend or shutdown states, packet delivery was verified while the machine was running.

A packet capture confirmed that the Wake-on-LAN magic packet reached the ASUS machine.

This ruled out several simple causes:

- incorrect destination network
- a sender-side failure
- broken Ethernet connectivity
- a missing packet on the local network

However, this only proves packet delivery while the operating system and NIC are fully powered.

It does **not** prove that the NIC continues listening for the same packet after suspend or shutdown.

That distinction became one of the key lessons from the investigation.

---

## ACPI and Kernel Wake Configuration

The system's ACPI wake table exposed the Ethernet wake entry as:

```text
GLAN
```

`GLAN` was enabled as a wake-capable device.

The Linux device wakeup state under sysfs was also enabled:

```text
/sys/.../power/wakeup
```

At this point, three important software-side conditions had been satisfied:

```text
NIC supports magic-packet wake
            +
ethtool Wake-on = g
            +
ACPI / kernel wake permission enabled
```

Despite this, the machine still did not wake.

---

## Suspend Test — S3

The system entered suspend-to-RAM and a Wake-on-LAN magic packet was sent from another machine.

Result:

```text
FAIL
```

The ASUS X550CA remained suspended.

The test was repeated after confirming the Wake-on-LAN and wake-permission settings.

The result did not change.

---

## Shutdown Test — S5

Wake behavior was also tested after a complete operating-system shutdown.

A magic packet was sent after the machine entered the S5/off state.

Result:

```text
FAIL
```

The laptop did not power on.

This was useful because some systems support Wake-on-LAN from one power state but not another. On this machine, neither tested state produced a successful wake.

---

## BIOS Power-Management Check

The BIOS option:

```text
Power Off Energy Saving
```

was disabled during testing.

The goal was to avoid an aggressive power-saving mode that could potentially remove standby power from the Ethernet controller.

Wake-on-LAN was tested again after the change.

Result:

```text
FAIL
```

The BIOS change did not make the system wake from a magic packet.

---

## Driver Investigation

The machine initially used Linux's stock Realtek driver:

```text
r8169
```

Because RTL8111/8168-family hardware can also be used with the `r8168` driver, the driver itself was tested as another variable.

Testing was performed with both:

```text
r8169
r8168
```

Wake-on-LAN still failed.

After the experiment, the machine was returned to the stock driver configuration and the initramfs was restored.

This avoided leaving an unsuccessful workaround in place.

---

## Physical-Layer Sanity Check

Two Ethernet cables were tested.

Neither changed the result.

Because normal Ethernet connectivity worked and the magic packet could be observed while the machine was running, a basic cable or connectivity failure became unlikely as the primary cause.

---

## What Was Ruled Out

The failure could not be explained simply by:

- the NIC lacking Wake-on-LAN capability
- `ethtool` being left in a disabled state
- the magic packet never reaching the machine
- ACPI wake being disabled
- the Linux wakeup flag being disabled
- the tested BIOS energy-saving setting
- one specific Ethernet cable
- using only the stock `r8169` driver

The remaining failure was therefore deeper than the initial software configuration.

---

## Likely Limitation

The exact hardware-level cause was not proven.

After the software configuration, packet delivery, ACPI state, BIOS setting, driver choice, and physical connection had all been investigated, the remaining evidence pointed toward a platform-specific firmware or power-management limitation.

A Wake-on-LAN-capable Ethernet controller is not sufficient by itself.

The motherboard and firmware must also keep the relevant part of the NIC powered and route its wake signal correctly while the system is suspended or shut down.

The ASUS X550CA may not maintain that complete wake path in the tested states, even though Linux reports the Ethernet controller as Wake-on-LAN capable.

This is the leading explanation, not a conclusively proven root cause.

---

## Why the Failed Experiment Was Still Useful

The original expectation was simple:

```text
NIC supports WoL
        +
Wake-on = g
        =
machine wakes
```

The investigation showed that the real dependency chain is more complicated:

```text
Network
   |
Driver
   |
Kernel
   |
ACPI
   |
Firmware
   |
Motherboard power state
   |
NIC standby behavior
```

Seeing a magic packet arrive while the system is running does not prove that the NIC can receive it after shutdown.

Seeing `Wake-on: g` does not prove that firmware will honor the wake event.

Seeing an enabled ACPI wake entry does not prove that the motherboard supplies the required standby power.

The unsuccessful result therefore clarified where software observability ends and where firmware/hardware behavior begins.

---

## Final Result

Wake-on-LAN could not be made operational on the ASUS X550CA during this investigation.

The tested path included:

```text
NIC capability
      |
      v
Wake-on configuration
      |
      v
Magic-packet delivery
      |
      v
ACPI / kernel wake state
      |
      v
BIOS power setting
      |
      v
S3 and S5 testing
      |
      v
Alternative Realtek driver
      |
      v
No successful wake
```

The machine was left in a clean state using the normal Linux driver configuration.

Remote power-on therefore remained unsolved.

Later remote-access work could provide secure network access while the laptop was already powered on, but it did not remove this physical power-state limitation.

---

## Conclusion

This investigation did not produce a working Wake-on-LAN setup, but it did narrow the failure substantially.

Linux reported that the NIC supported magic-packet wake, the feature was enabled, the packet could reach the machine, ACPI and kernel wake settings were enabled, firmware power settings were tested, two Ethernet cables were tried, and both `r8169` and `r8168` drivers were evaluated.

The laptop still failed to wake from both S3 suspend and S5 shutdown.

The final evidence is most consistent with a platform-level firmware or power-delivery limitation, although the exact hardware cause was not proven.

The most important result was therefore not a successful wake event.

It was learning that a feature being exposed by the NIC and operating system does not guarantee that the complete hardware platform can actually support it.
