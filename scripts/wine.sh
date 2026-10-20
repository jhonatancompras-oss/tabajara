#!/usr/bin/env bash
set -euo pipefail
exec 9>/workspace/tab-wine.lock
flock 9
export WINEPREFIX=/workspace/wine-tab-runtime WINEARCH=win64
export WINEDEBUG=${WINEDEBUG:--all}
export XDG_CACHE_HOME=/workspace/tab-cache XDG_RUNTIME_DIR=/workspace/tab-runtime
mkdir -p "$XDG_CACHE_HOME" "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
mkdir -p "$WINEPREFIX/drive_c/windows/system32"
cp /workspace/toolchain/usr/x86_64-w64-mingw32/lib/zlib1.dll "$WINEPREFIX/drive_c/windows/system32/zlib1.dll"
export WINEPATH='Z:\workspace\toolchain\usr\x86_64-w64-mingw32\lib'
export LD_LIBRARY_PATH=/workspace/toolchain/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export WINEDLLPATH=/workspace/toolchain/usr/lib/x86_64-linux-gnu/wine
exec /workspace/toolchain/usr/bin/proot \
  -b /workspace/toolchain/usr/share/wine:/usr/share/wine \
  -b /workspace/toolchain/usr/lib/wine:/usr/lib/wine \
  /bin/bash -c '
    /workspace/toolchain/usr/lib/wine/wine64 "$@"
    result=$?
    /workspace/toolchain/usr/lib/wine/wineserver64 -k
    exit "$result"
  ' -- "$@"
