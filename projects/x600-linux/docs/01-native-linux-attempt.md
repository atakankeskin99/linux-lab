# 01 — Native Linux Attempt

After working with the OMIX X600, the next question was more ambitious:

> Can this phone be pushed toward a more native Linux environment rather than merely running terminal tools inside Android?

The first route went through the device kernel.

## Device facts

The phone reported:

```text
CPU ABI  : arm64-v8a
Android  : 12
SDK      : 31
Hardware : mt6768
```

The hardware platform is MediaTek MT6768, which immediately made the project strongly device/vendor specific.

## What we tried

The experiment moved into Android kernel source and compilation work on a Linux laptop.

This included:

- identifying the vendor/device kernel tree
- preparing the build environment
- working with the Android/MediaTek source structure
- building the kernel
- reading build logs rather than only the final failure line
- isolating compiler failures with `grep`

One representative failure came from a MediaTek USB-related driver:

```text
drivers/misc/mediatek/c2k_usb/f_rawbulk.c
```

with compiler errors around one-bit bit-fields and warnings promoted to errors:

```text
implicit truncation from 'int' to a one-bit wide bit-field
changes value from 1 to -1
-Werror,-Wsingle-bit-bitfield-constant-conversion
```

## Why this path became expensive

A native kernel path is not simply:

```text
compile kernel → boot Linux
```

It is closer to:

```text
vendor kernel tree
    ↓
correct toolchain
    ↓
legacy compiler assumptions
    ↓
device configuration
    ↓
vendor drivers
    ↓
boot image / ramdisk / DT
    ↓
display / storage / USB / Wi-Fi / touch / power
    ↓
userspace
```

The failure was useful because it made the real scope visible.

A phone kernel contains vendor code that may have been written for a very specific compiler version and Android build system. Modern compilers can reject code that the original toolchain tolerated. Fixing one build error also says nothing about whether the finished kernel will boot or whether the hardware will work.

## Result

The native Linux attempt was **not completed**.

That is intentionally documented as a result rather than hidden as a failure.

What changed after the attempt was the architecture question itself:

> Do we actually need to replace the working Android kernel to achieve the learning objective right now?

The answer became "no".

That led to the pivot documented in the next section.

## What this stage taught

- kernel source is not the same thing as a portable Linux platform
- vendor drivers dominate the difficulty of mobile Linux work
- `-Werror` can turn old assumptions into hard build failures
- compile success would only be the beginning
- a usable Linux userspace and a native Linux boot path should be treated as separate goals
