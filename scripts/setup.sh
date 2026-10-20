#!/usr/bin/env bash
set -euo pipefail
export CARGO_HOME=/workspace/.cargo RUSTUP_HOME=/workspace/.rustup
export PATH=/workspace/.cargo/bin:$PATH
if ! command -v rustup >/dev/null; then
  curl -fsSL https://sh.rustup.rs -o /tmp/tab-rustup.sh
  sh /tmp/tab-rustup.sh -y --no-modify-path --profile minimal --default-toolchain 1.95.0
fi
rustup toolchain install 1.95.0 --profile minimal
rustup default 1.95.0
rustup target add x86_64-pc-windows-gnu
mkdir -p /workspace/apt/state/lists/partial /workspace/apt/cache/archives/partial /workspace/toolchain/bin
printf '%s\n' 'deb https://deb.debian.org/debian trixie main' > /workspace/apt/sources.list
apt_options=(-o Debug::NoLocking=1 -o Dir::State=/workspace/apt/state
  -o Dir::State::status=/var/lib/dpkg/status -o Dir::Cache=/workspace/apt/cache
  -o Dir::Etc::sourcelist=/workspace/apt/sources.list -o Dir::Etc::sourceparts=-)
apt-get "${apt_options[@]}" update
apt-get "${apt_options[@]}" --download-only -y --no-install-recommends install \
  gcc-mingw-w64-x86-64 g++-mingw-w64-x86-64 nsis wine64 xvfb proot
for archive in /workspace/apt/cache/archives/*.deb; do
  dpkg-deb -x "$archive" /workspace/toolchain
done
ln -sf ../usr/bin/x86_64-w64-mingw32-gcc-win32 /workspace/toolchain/bin/x86_64-w64-mingw32-gcc
ln -sf ../usr/bin/x86_64-w64-mingw32-g++-win32 /workspace/toolchain/bin/x86_64-w64-mingw32-g++
ln -sf wineserver64 /workspace/toolchain/usr/lib/wine/wineserver
for spec in \
  'wordcraft d1b0bfc3f9dd83126b162a42b667facecb003b7f' \
  'sheetcraft 68e58a2eae462ba997a8ba5a1269e03a79b61136'; do
  read -r repo revision <<< "$spec"
  if [[ ! -d /workspace/$repo/.git ]]; then
    git clone "https://github.com/storytold/$repo.git" "/workspace/$repo"
    git -C "/workspace/$repo" checkout --detach "$revision"
  fi
  [[ "$(git -C "/workspace/$repo" rev-parse HEAD)" == "$revision" ]] || {
    echo "Unexpected upstream revision in $repo; preserving checkout." >&2; exit 1;
  }
  cargo fetch --locked --manifest-path "/workspace/$repo/Cargo.toml"
done
if [[ ! -d /workspace/tabajara/build/wordcraft && ! -d /workspace/tabajara/build/gridcraft ]]; then
  python /workspace/tabajara/scripts/prepare.py
fi
python /workspace/tabajara/scripts/apply-patches.py
