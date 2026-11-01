# Reproduction notes

This is a record of one tested setup. Other Android releases, boot images and vendor modules may be incompatible. The helper builds a kernel only; it does not install toolchains, download sources, package a boot image, or write to a phone.

1. Obtain the matching Android kernel/msm source at commit `e333cb8619d0d2b22b6bcaefb50f1c51779510f5`. This repository contains the patch, not the complete kernel tree.
2. Start from a clean working tree at that commit. Check the patch with `git apply --check /path/to/patches/0001-statx-mount-id.patch`, then apply it with `git apply`.
3. Prepare a separate output directory and copy `configs/flame-tested.config` to its `.config`.
4. Provide the existing Android Clang r416183b (12.0.5), its LLD, and matching AArch64/ARM32 GCC toolchains. The historical GCC revisions were not recorded here; toolchain provisioning remains a reproduction limitation.
5. Set `KERNEL_SRC`, `KERNEL_OUT`, `CLANG_BIN`, `GCC64_BIN`, `GCC32_BIN`, then run `bash scripts/build-kernel.sh`.

The nonempty `CROSS_COMPILE` value matters: in this kernel Makefile it triggers Clang's AArch64 target argument. Omitting it reproduced an inline-assembly immediate-constraint error even with `ARCH=arm64`.

The tested previous configuration already enabled `COMPAT_VDSO`. Compared with the previous kernel's embedded configuration, only `PID_NS` changed. The helper explicitly enables both to preserve the tested setting.

Before any device use, validate the LZ4 stream, ARM64 image, embedded config, statx changes, kernel release, exported symbol CRCs, and module compatibility. Successful compilation is not proof of device compatibility.

The tested boot image retained the known-working ramdisk, DTB, command line and header v2 parameters. Only the kernel payload, its size, and boot ID were changed. Old AVB metadata was omitted, producing an unsigned image for an already-unlocked test device. This repository intentionally contains no flashing automation.

## Runtime probe

Run `python3 scripts/runtime_probe.py` in a root AArch64 Linux environment on the tested kernel with `/proc` mounted. It creates a PID namespace in a disposable child and checks a statx mount ID against mountinfo. It exits nonzero on a failed check. It is architecture-specific and is not a broad statx regression suite.

For package recovery, first inspect `dpkg --audit`, the apt logs and the planned dependency changes. Use a Kali-specific PATH, HOME and TMPDIR. The tested operation repaired interrupted packages and then completed an ordinary upgrade with package removals disabled; it did not run a full-upgrade or autoremove. Do not blindly copy package-recovery commands into another damaged environment.
