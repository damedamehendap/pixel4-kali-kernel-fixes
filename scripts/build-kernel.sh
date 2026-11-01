#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
: "${KERNEL_SRC:?Set KERNEL_SRC to the matching kernel source directory}"
: "${KERNEL_OUT:?Set KERNEL_OUT to an existing, configured output directory}"
: "${CLANG_BIN:?Set CLANG_BIN to clang-r416183b/bin}"
: "${GCC64_BIN:?Set GCC64_BIN to the AArch64 GCC toolchain bin directory}"
: "${GCC32_BIN:?Set GCC32_BIN to the ARM32 GCC toolchain bin directory}"
export PATH="$CLANG_BIN:$GCC64_BIN:$GCC32_BIN:$PATH"
args=(-C "$KERNEL_SRC" O="$KERNEL_OUT" ARCH=arm64 CC=clang LD=ld.lld
  CLANG_TRIPLE=aarch64-linux-gnu- CROSS_COMPILE=aarch64-linux-android-
  CROSS_COMPILE_ARM32=arm-linux-androideabi-)
"$KERNEL_SRC/scripts/config" --file "$KERNEL_OUT/.config" -e PID_NS -e COMPAT_VDSO
make "${args[@]}" olddefconfig
make "${args[@]}" -j"${JOBS:-4}" Image.lz4
