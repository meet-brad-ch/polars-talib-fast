#!/bin/bash
# Runs the CI steps of this repository on Linux in WSL, from a clone on the Linux file system.
#
#   From Windows (Git Bash):
#     MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu-24.04 -- bash /mnt/c/Apps/Projects/polars-talib/tools/wsl_test.sh [branch]
#
# The clone ~/polars-talib is made from the Windows clone (its committed HEAD, or the given branch) and the ta-lib
# submodule from its recorded URL, so the run tests what is committed, not the working copy. Setup (once, in WSL):
# rustup (https://sh.rustup.rs) and uv (https://astral.sh/uv/install.sh); python3, gcc and cmake from apt.
# Logs: ~/polars-talib-logs/<step>.log (not /tmp, which WSL clears when it stops). Ends with DONE or FAILED.
set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
src=/mnt/c/Apps/Projects/polars-talib
branch=${1:-HEAD}
say() { echo "[$(date +%T)] wsl_test: $*"; }
for tool in cargo uv git; do command -v $tool >/dev/null || { say "FAILED $tool is not installed"; exit 1; }; done
mkdir -p ~/polars-talib-logs
rm -rf ~/polars-talib
git clone -q "$src" ~/polars-talib || { say "FAILED clone of $src"; exit 1; }
cd ~/polars-talib
[ "$branch" = HEAD ] || git checkout -q "$branch" || { say "FAILED no branch $branch"; exit 1; }
git submodule update --init -q || { say "FAILED submodule"; exit 1; }
say "testing $(git rev-parse --short HEAD) with $(cargo --version), $(uv --version)"
step() { local name=$1; shift; say "start $name"
  if "$@" > ~/polars-talib-logs/"$name".log 2>&1; then say "ok $name"
  else local code=$?; tail -25 ~/polars-talib-logs/"$name".log; say "FAILED $name (exit $code, ~/polars-talib-logs/$name.log)"; exit 1; fi; }
step sync uv sync
step ruff uv run ruff check .
step format uv run ruff format --check .
step mypy uv run mypy
step pytest uv run pytest -q
step build uv run maturin build --release --out dist
say "DONE $(grep -E 'passed' ~/polars-talib-logs/pytest.log | tail -1); wheel: $(ls dist/*.whl)"
