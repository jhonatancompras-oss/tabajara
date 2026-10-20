#!/usr/bin/env bash
set -euo pipefail
cd /workspace/tabajara
export CARGO_HOME=/workspace/.cargo RUSTUP_HOME=/workspace/.rustup
export PATH=/workspace/toolchain/bin:/workspace/toolchain/usr/bin:/workspace/.cargo/bin:$PATH
export CARGO_TARGET_X86_64_PC_WINDOWS_GNU_LINKER=x86_64-w64-mingw32-gcc
export CC_x86_64_pc_windows_gnu=x86_64-w64-mingw32-gcc
export NSISDIR=/workspace/toolchain/usr/share/nsis
mkdir -p dist
python scripts/apply-patches.py
sha256sum -c dictionaries/SHA256SUMS.txt
for package in wordcraft gridcraft; do
  if [[ "$package" == wordcraft ]]; then
    target=/workspace/wordcraft/target
  else
    target=/workspace/tabajara/build/gridcraft/target
  fi
  source_dir=/workspace/tabajara/build/$package
  CARGO_TARGET_DIR="$target" cargo build --manifest-path "$source_dir/Cargo.toml" --locked --release \
    -p "$package" -p "$package-cli" --target x86_64-pc-windows-gnu --jobs 3
done
makensis -V2 '-DAPP_NAME=Word Tab e Excel Tab' -DAPP_EXE=WordTab.exe \
  -DOUTPUT=/workspace/tabajara/dist/word-tab-excel-tab-instalador-windows-x64.exe \
  -DICON=/workspace/tabajara/assets/word-tab/icon.ico \
  -DSOURCE=/workspace/tabajara/build/wordcraft \
  -DSECOND_SOURCE=/workspace/tabajara/build/gridcraft \
  -DBINARY=/workspace/wordcraft/target/x86_64-pc-windows-gnu/release/wordcraft.exe \
  -DSECOND_BINARY=/workspace/tabajara/build/gridcraft/target/x86_64-pc-windows-gnu/release/gridcraft.exe \
  packaging/installer.nsi
cd dist
sha256sum *-instalador-windows-x64.exe > SHA256SUMS.txt
