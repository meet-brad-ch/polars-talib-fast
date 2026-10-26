"""Two frames the tests run on: a synthetic one with the awkward cases real input has
(leading NaN rows, a null in the middle, a ``periods`` column for MAVP), and TA-Lib's own
252-bar daily reference series from its regression tool, real prices with volume."""

import sys
from pathlib import Path

import numpy as np
import polars as pl

ROWS = 300
LEADING_NAN = 7
NULL_ROW = 150
SEED = 20260910
COLUMNS = ["open", "high", "low", "close", "volume"]

# TA-Lib's regression data, written from its test_data.c by tools/c_oracle/generate.py.
TALIB_REFERENCE = Path(__file__).parent / "golden" / "talib_reference.csv"
# Golden values are per platform: TA-Lib's transcendental functions use the platform's libm.
PLATFORMS = {"win32": "windows", "linux": "linux", "darwin": "macos"}


def platform() -> str:
    """The name of this platform's golden data directory."""
    if sys.platform not in PLATFORMS:
        raise RuntimeError(f"no golden data for platform {sys.platform}")
    return PLATFORMS[sys.platform]


def talib_reference() -> pl.DataFrame:
    """TA-Lib's ``*_daily_ref_0`` arrays: open, high, low, close, volume, 252 bars."""
    df = pl.read_csv(TALIB_REFERENCE, comment_prefix="#", schema=dict.fromkeys(COLUMNS, pl.Float64))
    assert df.height == 252, df.height
    rng = np.random.default_rng(SEED)
    return df.with_columns(pl.Series("periods", rng.integers(2, 30, 252).astype(np.float64)))


def frame() -> pl.DataFrame:
    rng = np.random.default_rng(SEED)
    close = 100.0 + np.cumsum(rng.normal(0.0, 1.0, ROWS))
    spread = rng.uniform(0.1, 2.0, ROWS)
    columns = {
        "open": close - rng.uniform(-1.0, 1.0, ROWS),
        "high": close + spread,
        "low": close - spread,
        "close": close,
        "volume": rng.integers(1_000, 100_000, ROWS).astype(np.float64),
        "periods": rng.integers(2, 30, ROWS).astype(np.float64),
    }
    for values in columns.values():
        values[:LEADING_NAN] = np.nan
    df = pl.DataFrame(columns)
    return df.with_columns(
        pl.when(pl.int_range(pl.len()) == NULL_ROW)
        .then(None)
        .otherwise(pl.col("close"))
        .alias("close")
    )
