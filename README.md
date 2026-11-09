# Pixel 4: Kali package-upgrade kernel fixes

Pixel 4 (`flame`) のAndroidカーネルに `STATX_MNT_ID` を追加し、PID namespaceを有効化した作業記録と再現資料です。目的は、Kali chrootで途中停止した `apt upgrade` を完了させることでした。

The tested setup completed a Kali package upgrade after a statx mount-ID backport and enabling PID namespaces. This is a device-specific engineering report, not a claim of a first implementation or a universal fix.

## Results

- Kernel: `4.14.276-dirty`, Android Clang 12.0.5 (`clang-r416183b`).
- Tested source commit: `e333cb8619d0d2b22b6bcaefb50f1c51779510f5` in [Android kernel/msm](https://android.googlesource.com/kernel/msm/).
- `statx` structure remains 256 bytes; mount ID occupies the former spare field at offset `0x90`.
- Existing `struct kstat` and exported `vfs_statx` interface preserved.
- Existing 11,799 exported symbol CRCs unchanged relative to the previous statx build; enabling PID namespaces added `put_pid_ns`.
- Saved device modules: 32 checked; 2,464 comparable symbol references matched, 468 references lacked provider CRC evidence.
- Real-device test: PID-namespace child had PID 1; `statx(/proc)` returned `STATX_MNT_ID` and the same mount ID as `/proc/self/mountinfo`.
- Temporary boot, then normal boot after installing to the active boot partition, succeeded. Wi-Fi and audio modules were observed loaded; this is not exhaustive hardware testing.
- Kali package repair and upgrade: 798 upgraded, zero removed; exit 0. `dpkg --audit` was empty and `apt-get check` succeeded. 79 packages remained held back by the ordinary upgrade plan.

## Original failure and limits

The old apt log showed systemd 262-1 configuration failing with:

```text
Cannot open '/etc/machine-id': Protocol driver not attached
```

Under the new kernel, systemd package configuration succeeded. Interrupted-upgrade version mismatches were repaired, Kali-specific PATH/TMPDIR were used instead of inherited Android values, and network connectivity was restored before upgrading.

**Causality is not fully isolated:** the work does not establish that PID namespaces were required for the successful package upgrade, or that the kernel patch alone explains every improvement. Running systemd as PID 1 was not necessary to demonstrate this result and was not tested as an acceptance criterion.

Symlink-size warnings and chroot runlevel warnings remained in the apt output, but the package operation and final consistency checks succeeded.

## Contents

- `patches/0001-statx-mount-id.patch`: kernel changes to two files.
- `configs/flame-tested.config`: configuration extracted from the tested kernel.
- `scripts/build-kernel.sh`: build-only helper using an existing source tree and toolchains.
- `scripts/runtime_probe.py`: AArch64 Linux PID namespace and mount-ID probe; requires root and a mounted `/proc`.
- `docs/REPRODUCE.md`: build and verification notes.
- `docs/VALIDATION.md`: artifact hashes and tested scope.

No boot images, ramdisks, device backups, binaries, raw device logs, serial numbers, or account credentials are included. This repository does not contain the complete kernel source or toolchains. Obtain matching sources separately; do not treat this repository as a complete binary-distribution source offer.

Kernel-derived material is provided under GPL-2.0; see `COPYING`. New helper scripts in this repository are also GPL-2.0-only. Original upstream notices remain applicable.

## RTL8192EU USB Wi-Fi fixes

[RTL8192EU build and CFI fixes, automatic connection, and validation](rtl8192eu/README.md) documents the external USB Wi-Fi work. Automatic insertion and unplug/replug communication were tested; Android's default network is preserved, and reboot startup has not been tested.

