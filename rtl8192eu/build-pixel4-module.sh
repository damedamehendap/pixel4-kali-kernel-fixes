#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/pixel4-clang/clang-r416183b/bin:$HOME/pixel4-gcc-aarch64/bin:$HOME/pixel4-gcc-arm32/bin:$PATH"
exec make -C "$HOME/pixel4-msm" O="$HOME/pixel4-out-rtl8192eu" \
  M="$HOME/rtl8192eu" ARCH=arm64 CONFIG_RTL8192EU=m \
  CC=clang LD=ld.lld AR=llvm-ar NM=llvm-nm \
  CROSS_COMPILE=aarch64-linux-android- CROSS_COMPILE_ARM32=arm-linux-androideabi- \
  CLANG_TRIPLE=aarch64-linux-gnu- -j4 modules "$@"
