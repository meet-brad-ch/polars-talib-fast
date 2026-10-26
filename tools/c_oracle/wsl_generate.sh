#!/bin/bash
# Writes the Linux golden data (tests/golden/linux) from TA-Lib's C library built on Linux in WSL, into the Windows
# working tree, from a fresh clone of the committed branch:
#
#   From Windows (Git Bash):
#     MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-24.04 -- bash /mnt/c/Apps/Projects/polars-talib/tools/c_oracle/wsl_generate.sh [branch]
#
# The platform-independent files (functions.json, talib_reference.csv) must come out unchanged; the run fails if not.
# Setup as for tools/wsl_test.sh. Logs: ~/polars-talib-logs/golden-*.log. Ends with DONE or FAILED.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
src=/mnt/c/Apps/Projects/polars-talib
work=~/polars-talib-golden
branch=${1:-HEAD}
say() { echo "[$(date +%T)] wsl_generate: $*"; }
for tool in cargo uv git gcc; do command -v $tool >/dev/null || { say "FAILED $tool is not installed"; exit 1; }; done
mkdir -p ~/polars-talib-logs
rm -rf "$work"
git clone -q "$src" "$work" || { say "FAILED clone of $src"; exit 1; }
cd "$work"
[ "$branch" = HEAD ] || git checkout -q "$branch" || { say "FAILED no branch $branch"; exit 1; }
git submodule update --init -q || { say "FAILED submodule"; exit 1; }
say "$(git rev-parse --short HEAD), TA-Lib C $(cat tools/c_oracle/ta-lib/VERSION), $(gcc --version | head -1)"
say "start generate"
if ! bash tools/c_oracle/generate.sh > ~/polars-talib-logs/golden-generate.log 2>&1; then
  tail -25 ~/polars-talib-logs/golden-generate.log; say "FAILED generate (~/polars-talib-logs/golden-generate.log)"; exit 1
fi
say "ok generate: $(grep -c 'arrays' ~/polars-talib-logs/golden-generate.log) files"
if ! git diff --quiet -- tests/golden/functions.json tests/golden/talib_reference.csv; then
  git diff --stat -- tests/golden/functions.json tests/golden/talib_reference.csv
  say "FAILED platform-independent golden files changed on Linux"; exit 1
fi
mkdir -p "$src/tests/golden/linux"
cp tests/golden/linux/*.npz tests/golden/linux/vmath.json "$src/tests/golden/linux/" || { say "FAILED copy to $src/tests/golden/linux"; exit 1; }
say "DONE $(ls tests/golden/linux | tr '\n' ' ')-> $src/tests/golden/linux"
