# polars-talib-fast

[![CI](https://github.com/meet-brad-ch/polars-talib-fast/actions/workflows/ci.yml/badge.svg)](https://github.com/meet-brad-ch/polars-talib-fast/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/meet-brad-ch/polars-talib-fast?label=release)](https://github.com/meet-brad-ch/polars-talib-fast/releases/latest)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-windows%20x64%20%7C%20linux%20x64%20%7C%20macOS%20arm64-lightgrey)
![TA-Lib](https://img.shields.io/badge/TA--Lib-0.8.3-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/meet-brad-ch/polars-talib-fast/blob/main/LICENSE)

Every [TA-Lib](https://ta-lib.org) function, 237 of them, as a [Polars](https://pola.rs)
expression. TA-Lib comes from [`ta-lib`](https://crates.io/crates/ta-lib), TA-Lib's official
Rust port.

```python
import polars as pl
import polars_talib_fast as plta

df.with_columns(
    plta.sma(timeperiod=20).alias("sma20"),
    plta.macd().over("symbol").alias("macd"),  # struct: macd, macdsignal, macdhist
    plta.atr(pl.col("high"), pl.col("low"), pl.col("close"), timeperiod=14).alias("atr"),
    plta.cdlengulfing().alias("engulfing"),  # Int32, as TA-Lib reports patterns
)
```

Inputs default to the columns TA-Lib's own conventions name (`close` for a single series,
`open`/`high`/`low`/`close`/`volume` for price functions), parameters default to TA-Lib's
values, and multi-output functions return a struct with TA-Lib's output names. Nulls and
leading NaN rows are handled as ta-lib-python does: the output is NaN (or 0 for integer
outputs) until the function has enough data.

## Or ta-lib-python?

[ta-lib-python](https://github.com/TA-Lib/ta-lib-python) accepts a Polars `Series` and is
the simplest tool for one array and one indicator. Inside a Polars query it needs a
`map_batches` wrapper per indicator. The example above, written with ta-lib-python, gives
the same four columns:

```python
import talib


def macd(close: pl.Series) -> pl.Series:
    m, s, h = talib.MACD(close.to_numpy(), 12, 26, 9)
    return pl.DataFrame({"macd": m, "macdsignal": s, "macdhist": h}).to_struct("macd")


def atr(cols: pl.Series) -> pl.Series:
    c = cols.struct
    return pl.Series(
        talib.ATR(
            c.field("high").to_numpy(), c.field("low").to_numpy(), c.field("close").to_numpy(), 14
        )
    )


def engulfing(cols: pl.Series) -> pl.Series:
    c = cols.struct
    return pl.Series(
        talib.CDLENGULFING(*(c.field(k).to_numpy() for k in ("open", "high", "low", "close")))
    )


MACD = pl.Struct({"macd": pl.Float64, "macdsignal": pl.Float64, "macdhist": pl.Float64})

df.with_columns(
    pl.col("close")
    .map_batches(lambda s: pl.Series(talib.SMA(s.to_numpy(), 20)), return_dtype=pl.Float64)
    .alias("sma20"),
    pl.col("close").map_batches(macd, return_dtype=MACD).over("symbol").alias("macd"),
    pl.struct("high", "low", "close").map_batches(atr, return_dtype=pl.Float64).alias("atr"),
    pl.struct("open", "high", "low", "close")
    .map_batches(engulfing, return_dtype=pl.Int32)
    .alias("engulfing"),
)
```

Speed is not the difference. Measured on the same machine, one indicator on a million rows
costs about the same on both (EMA: 1.7 ms here, 2.2 ms with ta-lib-python 0.8.2). Per symbol
it is: under `.over("symbol")` the plugin runs the function per group without a Python call.
The comparison with thousands of symbols and with several indicators in one `select` is in
[ARCHITECTURE.md](https://github.com/meet-brad-ch/polars-talib-fast/blob/main/ARCHITECTURE.md), section 6.
The difference is that every function is a native expression with TA-Lib's names,
defaults, struct outputs, integer types, docstrings and type stubs, generated from TA-Lib's
own metadata.

## How it works

The design is described in [ARCHITECTURE.md](https://github.com/meet-brad-ch/polars-talib-fast/blob/main/ARCHITECTURE.md). In short: TA-Lib
describes its own functions through its *abstract API*: inputs, parameters
with defaults, outputs, group, hint. This library has **one** Rust expression that runs
any TA-Lib function by name through that API, and builds the Python API from the
same metadata at import time. No function is written by hand, so a new TA-Lib release is
a version bump of the `ta-lib` crate plus new golden test data from the C library at the
same tag:

```
# Cargo.toml: ta-lib = "=<version>"
git -C tools/c_oracle/ta-lib checkout v<version>
tools/c_oracle/generate.sh                    # golden data from the C library
uv sync                                       # builds the extension
uv run python -m polars_talib_fast._stubs     # regenerate the .pyi stubs
uv run pytest
```

## Install

Windows x64, Linux x64 (glibc 2.17 or newer) and macOS on Apple silicon, Python 3.10 or
newer:

```
pip install polars-talib-fast
```

The same wheels are attached to each
[release](https://github.com/meet-brad-ch/polars-talib-fast/releases). All three platforms run
the full test suite in CI; Linux is also run locally in WSL2 with `tools/wsl_test.sh`.

## Tests

The oracle is TA-Lib's C library at the same tag as the crate. `tools/c_oracle` builds it
and writes `tests/golden`, and the oracle itself is checked against ta-lib-python, bit for bit,
on the TA-Lib versions ta-lib-python ships (0.7.1 and 0.8.1). Every function is checked for
the description TA-Lib's C library gives (names, defaults, hints, outputs) and for
bit-identical values on float64 and float32 input, on a synthetic frame with leading NaN rows
and a null, and on TA-Lib's own 252-bar reference data. The values are per platform: the
functions that call `sin`, `exp` or `log` follow the platform's math library in the last bit,
and on each platform the C library and the crate agree bit for bit (Windows and Linux golden
data are committed, Linux written in WSL by `tools/c_oracle/wsl_generate.sh`; the macOS CI job
writes its own). ta-lib-python 0.8.2 checks the names and signatures of the 201 functions it
has. `supersmoother`, which TA-Lib does not have, is
checked against its recursion.

## Beyond TA-Lib

`supersmoother` (Ehlers' 2-pole low-pass filter, with AmiBroker's IIR() coefficients) is a
Rust expression of its own in `src/extra.rs`. An indicator lives here only while TA-Lib does
not have it: `hma` was one until TA-Lib 0.8 added `HMA`, which a test shows to be the same
Hull composition.

## Build

```
git clone https://github.com/meet-brad-ch/polars-talib-fast
uv sync                                  # builds the extension
uv run pytest
```

Needs a Rust toolchain. The C oracle (`tools/c_oracle`, only for new golden data) also needs
the submodule (`git submodule update --init`) and a C compiler.

## License

MIT. The wheels contain TA-Lib, BSD-3-Clause, Copyright (c) 1999-2026 Mario Fortier:
[LICENSES/TA-Lib.txt](https://github.com/meet-brad-ch/polars-talib-fast/blob/main/LICENSES/TA-Lib.txt).

The idea of exposing TA-Lib as Polars expressions comes from
[Yvictor/polars_ta_extension](https://github.com/Yvictor/polars_ta_extension).
