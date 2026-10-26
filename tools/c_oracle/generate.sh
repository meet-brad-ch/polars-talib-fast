#!/bin/bash
# Builds the C oracle from the tools/c_oracle/ta-lib submodule (checked out at the TA-Lib tag the
# plugin's `ta-lib` crate is) and writes tests/golden (or the directory given). Run from anywhere:
#
#   tools/c_oracle/generate.sh [out-dir]
#
# The environment is synced first (maturin, numpy, polars); every later step runs with --no-sync, because a sync
# would drop the oracle from the environment again.
set -euo pipefail
cd "$(dirname "$0")/../.."
say() { echo "[$(date +%T)] generate: $*"; }
say "syncing the environment"
uv sync -q || { say "FAILED sync"; exit 1; }
say "TA-Lib C $(cat tools/c_oracle/ta-lib/VERSION): building the oracle"
uv run --no-sync maturin develop --uv --release -q -m tools/c_oracle/Cargo.toml || { say "FAILED build"; exit 1; }
say "writing golden data"
uv run --no-sync python tools/c_oracle/generate.py ${1:+--out "$1"} || { say "FAILED generate"; exit 1; }
say "DONE"
