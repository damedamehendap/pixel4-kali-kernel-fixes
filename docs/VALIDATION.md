# Validation record

Dates: kernel build 2026-10-25 JST; real-device boot/install 2026-10-30 JST; Kali upgrade 2026-10-31 JST.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Image | 46,946,320 | `777426e4d818bb45910dcd5127a5a2b715d67aedf50d8f805970c95edf04d63d` |
| Image.lz4 | 20,865,363 | `c4e67a825e1b85bb5b29b0631b702cb66c51a0cab6a7e90fc88c5df6cc11500a` |
| Device-specific boot image | 67,108,864 | `6cf1451ef89bb81c3a0045ee7c7963696004bfb55f31435ec38e66782e073a9c` |

These are historical reference hashes, not a promise of bit-reproducible builds. Build timestamps, build number and local state affect the result. The binaries are not distributed here.

Embedded configuration matched the output `.config`. Kernel release was `4.14.276-dirty`, build #6, Clang 12.0.5. Configuration enabled PID_NS, NAMESPACES, COMPAT_VDSO, LTO_CLANG and CFI_CLANG.

`module_layout` CRC: `0x1ce527a0`. Release strings differed from the saved vendor modules; with CONFIG_MODVERSIONS and version sections, the tested loader compares the remaining vermagic fields. All 32 saved modules matched that rule. No mismatches among 2,464 comparable symbol references; 468 references were not fully verifiable. Successful module loading on this device supplements, but does not remove, that limitation.

The boot image was statically parsed and payloads re-extracted. Kernel bytes matched the build; ramdisk/DTB matched the known-working images. Header version 2, page 4096, header size 1660. Flash read-back SHA-256 exactly matched the intended image. A backup was retained privately. No slot change or other partition write was performed.

Runtime checks passed both during temporary boot and after normal boot from the installed image. The post-install probe reported child PID=1 and a statx mask of `0x17ff`; the mount ID matched the same process's mountinfo. Numeric mount IDs are transient and not a portable expected value.

Remaining limits: not a full filesystem or kernel test suite, no exhaustive hardware validation, no systemd-as-PID-1 acceptance test, no isolated proof that PID_NS was needed for apt. Existing CFI/kallsyms name-length warnings were not fixed.
