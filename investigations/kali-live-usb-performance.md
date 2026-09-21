# Kali Live USB Performance Investigation

## Overview

This investigation documents the behavior and storage performance of a Kali Linux Live environment running from a USB flash drive on an ASUS X550CA.

The test started after noticeable desktop lag and slow I/O were observed while using Kali Live with encrypted persistence.

The goal was to verify that persistence was working correctly, inspect how the USB device was connected, and measure actual write performance rather than relying on the advertised USB specification.

## Test Environment

- Host: ASUS X550CA
- OS: Kali Linux Live
- Boot mode: UEFI
- Storage device: 32 GB USB flash drive
- Device-reported model: `USB DISK 3.0`
- Persistence: LUKS-encrypted ext4
- Wi-Fi: detected and operational

## Persistence Verification

Persistence was first verified by creating a test file, rebooting into the persistent Kali Live environment, and checking that the file remained available.

The persistence volume was also visible through `lsblk`:

```text
sdb      usb   29.5G   USB DISK 3.0
├─sdb1          5.1G   iso9660   /run/live/medium
├─sdb2          4.1M   vfat
└─sdb3         24.3G   crypto_LUKS
  └─sdb3       24.3G   ext4      /run/live/persistence
```

Result:

**PASS — encrypted persistence survived a reboot and was mounted correctly.**

## USB Connection Investigation

The USB topology was inspected with:

```bash
lsusb -t
```

The system exposed an xHCI controller capable of SuperSpeed operation:

```text
Driver=xhci_hcd/4p, 5000M
```

However, the Kali Live mass-storage device itself was connected at:

```text
Class=Mass Storage, Driver=usb-storage, 480M
```

This indicates that although the machine exposes a 5 Gbit/s USB controller and the flash drive identifies itself as `USB DISK 3.0`, the storage device negotiated a 480 Mbit/s USB connection during this test.

## Persistence Write Test

Sequential write performance was measured by writing a 256 MiB temporary file to the persistent filesystem:

```bash
dd if=/dev/zero of=~/usb-speed-test.bin bs=1M count=256 conv=fdatasync status=progress
```

Result:

```text
268435456 bytes (268 MB, 256 MiB) copied, 65.5577 s, 4.1 MB/s
```

Measured sequential write throughput:

**4.1 MB/s**

The temporary benchmark file was removed after the test:

```bash
rm ~/usb-speed-test.bin
```

## Observations

The main observations from the session were:

- Kali Live booted successfully on the ASUS X550CA.
- Wi-Fi worked without additional configuration.
- Encrypted persistence operated correctly across reboots.
- The USB device was detected as `USB DISK 3.0`.
- The host exposed a 5000M xHCI USB controller.
- The Kali mass-storage device nevertheless operated at 480M during the test.
- Sequential writes to the encrypted persistence filesystem reached approximately 4.1 MB/s.
- Noticeable desktop lag was observed while running Kali from this device.

The measured write performance provides a plausible storage-side explanation for at least part of the poor interactive experience, particularly when applications generate persistent writes.

The benchmark does not isolate USB bus speed, flash-memory performance, encryption overhead, filesystem behavior, or workload characteristics individually.

## Next Steps

The current flash drive is not intended to remain the long-term Kali Live storage device.

A higher-performance USB flash drive or external SSD is planned as a replacement.

Once the replacement storage is available, the same tests can be repeated:

```bash
lsusb -t
lsblk -o NAME,TRAN,SIZE,MODEL,FSTYPE,MOUNTPOINTS
```

followed by the same persistence write benchmark:

```bash
dd if=/dev/zero of=~/usb-speed-test.bin bs=1M count=256 conv=fdatasync status=progress
```

This will allow a direct comparison of:

- negotiated USB link speed
- persistence layout
- sequential write throughput
- desktop responsiveness

The current **4.1 MB/s** result therefore serves as a baseline for the future storage upgrade.

## Conclusion

The Kali Live environment itself operated correctly on the ASUS X550CA, including networking and encrypted persistence.

The primary limitation observed during this session was storage performance. Despite the flash drive identifying itself as a USB 3.0 device and the host exposing a SuperSpeed-capable controller, the device operated at 480M and achieved only **4.1 MB/s** sequential writes to the encrypted persistence filesystem.

A future test with a faster USB flash drive or external SSD will determine how much of the observed desktop latency can be reduced by improving the storage path.