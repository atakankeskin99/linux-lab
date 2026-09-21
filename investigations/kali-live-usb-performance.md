# Kali Live USB Performance Investigation

## Overview

This investigation compares the behavior of the same Kali Linux Live USB environment on two different host systems.

The goal was to understand why the Live desktop felt sluggish and to establish a performance baseline before replacing the current flash drive with a faster USB device or external SSD.

The investigation focused on:

- USB link speed
- encrypted persistence
- sequential write performance
- desktop responsiveness
- possible CPU, memory and graphics-related bottlenecks

## Test Device

The same Kali Live USB was used on both systems.

- Capacity: approximately 32 GB
- Reported device model: `USB DISK 3.0`
- Kali Live system partition: approximately 5.1 GB
- Persistence partition: approximately 24.3 GB
- Persistence encryption: LUKS
- Persistence filesystem: ext4
- Desktop environment: XFCE

## Cross-Host Results

| Measurement | Windows Laptop | ASUS X550CA |
|---|---:|---:|
| Kali Live boot | PASS | PASS |
| USB link speed | 5000M | 480M |
| Persistence | PASS | PASS |
| Sequential persistence write | 9.2 MB/s | 4.1 MB/s |
| Desktop lag | Significant | Noticeable |
| XFCE compositor test | Tested | Not tested |
| Compositor disabled | Major improvement | — |
| Wi-Fi | Operational | Operational |

## Windows Laptop

The Kali USB negotiated a USB 3.x connection:

```bash
lsusb -t
```

Relevant result:

```text
5000M
```

This ruled out a USB 2.0 link as the immediate explanation for the poor performance on this host.

System resource checks also showed no obvious CPU or memory bottleneck:

- approximately 15 GiB RAM
- approximately 13 GiB available
- swap disabled
- CPU approximately 96% idle during observation

Sequential write performance to encrypted persistence was measured with:

```bash
dd if=/dev/zero of=~/usb-speed-test.bin bs=1M count=256 conv=fdatasync status=progress
```

Result:

```text
9.2 MB/s
```

Despite negotiating a 5 Gbit/s USB connection, the flash drive achieved only 9.2 MB/s sustained sequential writes.

Desktop responsiveness was also investigated independently.

XFCE compositing was disabled with:

```bash
xfconf-query -c xfwm4 -p /general/use_compositing -s false
```

This produced a substantial improvement in window movement, menus and general desktop responsiveness.

The system was using the Nouveau graphics driver, and earlier kernel output also contained Nouveau-related warnings.

This indicates that the visible desktop lag was not caused solely by storage performance.

Encrypted persistence was also verified successfully across reboot, including restoration of a test file and saved Wi-Fi configuration.

## ASUS X550CA

The same Kali Live USB was later tested on an ASUS X550CA.

Kali booted successfully, Wi-Fi worked without additional configuration, and encrypted persistence survived reboot.

The storage layout included:

```text
sdb      usb   29.5G   USB DISK 3.0
├─sdb1          5.1G   iso9660   /run/live/medium
├─sdb2          4.1M   vfat
└─sdb3         24.3G   crypto_LUKS
  └─sdb3       24.3G   ext4      /run/live/persistence
```

USB topology was inspected with:

```bash
lsusb -t
```

The host exposed a SuperSpeed-capable xHCI controller:

```text
5000M
```

However, the Kali mass-storage device itself operated at:

```text
480M
```

The same persistence write benchmark was then performed:

```bash
dd if=/dev/zero of=~/usb-speed-test.bin bs=1M count=256 conv=fdatasync status=progress
```

Result:

```text
268435456 bytes (268 MB, 256 MiB) copied, 65.5577 s, 4.1 MB/s
```

The ASUS therefore produced approximately:

**4.1 MB/s sequential persistence write throughput**

## Findings

The two hosts exposed different characteristics while using the same Kali Live USB.

On the Windows laptop, the drive negotiated a **5000M USB connection**, but sustained writes still reached only **9.2 MB/s**.

This shows that the USB interface itself was not the primary storage limitation on that system. The flash drive's real-world write performance remained far below the available link capacity.

On the ASUS X550CA, the same storage device negotiated only **480M** and achieved approximately **4.1 MB/s** sequential writes.

The Windows laptop also demonstrated a separate graphical performance issue. CPU and memory utilization were low, while disabling the XFCE compositor produced a major improvement in responsiveness.

The investigation therefore identified at least two distinct performance factors:

1. **Low flash-storage performance**
2. **Desktop composition / graphics-driver overhead**

The current data does not justify attributing all observed desktop lag to a single component.

## Next Steps

The current flash drive is planned to be replaced with either:

- a higher-performance USB flash drive
- or an external SSD

After the storage upgrade, the same tests should be repeated on both hosts.

USB topology:

```bash
lsusb -t
```

Storage layout:

```bash
lsblk -o NAME,TRAN,SIZE,MODEL,FSTYPE,MOUNTPOINTS
```

Persistence write benchmark:

```bash
dd if=/dev/zero of=~/usb-speed-test.bin bs=1M count=256 conv=fdatasync status=progress
```

The replacement device can then be compared against the current baseline:

```text
Windows laptop: 9.2 MB/s
ASUS X550CA:     4.1 MB/s
```

Desktop responsiveness should also be compared with XFCE compositing enabled and disabled where relevant.

## Conclusion

The Kali Live environment functioned correctly on both tested systems, including encrypted persistence and networking.

The current USB flash drive showed poor real-world write performance even when operating through a 5 Gbit/s connection, while performance degraded further when the same device operated at 480M on the ASUS X550CA.

The Windows laptop also exposed a separate graphics-related performance factor, as disabling XFCE compositing substantially improved desktop responsiveness.

These measurements establish a useful baseline for repeating the investigation after migrating Kali Live to faster USB storage or an external SSD.