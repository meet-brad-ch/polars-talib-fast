# Architecture

This document describes how polars-talib-fast is built and why. It uses one name for each
thing. A *function* is one of the 237 indicators that TA-Lib provides. An *expression* is
a Polars `Expr`. The *plugin* is the compiled module `polars_talib_fast._polars_talib_fast`.

## 1. The idea

TA-Lib describes each of its functions at run time. This description is the *abstract
API*, `ta_lib::abstract_api` in the `ta-lib` crate (TA-Lib's official Rust port; the C
library has the same in `ta_abstract.h`). For each function, it gives:

- the inputs, as single series or as price bundles (open, high, low, close, volume),
- the parameters, with their type (integer or real) and their default value,
- the outputs, with their type (integer or real),
- the group and a one-line hint.

polars-talib-fast reads this description and lets it drive everything. One Rust expression runs
any function by name. Python builds the public API from the same description at import
time. No function is written by hand. A new TA-Lib release adds its new functions without
a code change.

## 2. The parts

```
Cargo.toml                     the ta-lib crate, pinned exactly
src/talib.rs                   safe layer: Function (metadata) and Function::call
src/plugin.rs                  the one expression, `call`
src/extra.rs                   expressions for indicators TA-Lib does not have
src/lib.rs                     the Python module: version(), functions()
python/polars_talib_fast/_build.py  builds a Python function from each description
python/polars_talib_fast/<group>.py ten modules, one per TA-Lib group
python/polars_talib_fast/<group>.pyi generated type stubs for the same modules
python/polars_talib_fast/_stubs.py  the stub generator
python/polars_talib_fast/__init__.py exports, get_functions, supersmoother
tests/                         pytest; oracle: golden data from TA-Lib's C library
tests/golden/                  functions.json, talib_reference.csv, <platform>/*.npz
tools/c_oracle/                TA-Lib's C library (submodule) as a Python module; writes tests/golden
tools/bench.py                 timings of two builds, interleaved
tools/rust_complexity.py       cyclomatic complexity gate for the Rust sources
tools/wsl_test.sh              the CI steps on Linux in WSL
```

### 2.1 TA-Lib as a dependency

TA-Lib is the `ta-lib` crate from crates.io, pinned exactly (`ta-lib = "=0.8.3"`). It is pure
Rust, so the build needs no C compiler. `talib::Library::version()` reads the version from
that pin, so the version is written in one place.

To move to a new TA-Lib release:

1. Set the new version in `Cargo.toml`.
2. Check out the same tag in `tools/c_oracle/ta-lib` and write new golden data: run
   `tools/c_oracle/generate.sh` on Windows and `tools/c_oracle/wsl_generate.sh` in WSL
   (section 4). The macOS CI job writes its own.
3. Run `uv sync`. This rebuilds the plugin.
4. Run `uv run python -m polars_talib_fast._stubs`. This regenerates the stubs.
5. Run `uv run pytest`. The coverage test lists the functions the new release added.

### 2.2 The safe layer (`src/talib.rs`)

`Table::build` reads TA-Lib's registry (`abstract_api::FUNCS`) once and turns every
function's description into plain Rust values; `Function::get(name)` serves every later
call from that table without allocating. The description holds:

- `inputs`: a list of `Input::Real(name)` or `Input::Price(parts)`. An integer input is
  an error; no TA-Lib function has one.
- `params`: name, integer flag, default value, hint,
- `outputs`: name, integer flag.

Names are spelled the way ta-lib-python spells them. `optInFastPeriod` becomes
`fastperiod`. `outRealUpperBand` becomes `upperband`. `Library::plain` does this.

`Function::table()` lists every function, group by group, by name within a group.

`Function::call(columns, values, offset)` runs the function:

1. Check the inputs: the declared number of series, all of one length, and no more rows
   than a 32-bit position counts. `Function::rows` does this; the expression calls it too,
   before it looks at any value.
2. Start a `ParamHolder` on the one shared `Core` (TA-Lib's default settings; immutable and
   `Sync`, so calls run in parallel without a lock).
3. Bind each input series in declaration order. A price input takes one series per
   component.
4. Bind each parameter. An integer parameter refuses a fractional value and a value that
   does not fit 32 bits.
5. Ask TA-Lib for the lookback. An error here means a parameter is out of range: the error
   names the function and every parameter with its value.
6. Allocate each output once, every row NaN (real) or 0 (integer), `offset` rows longer than
   the input. If the lookback is not shorter than the data, return them. This is not an
   error.
7. Otherwise bind the rows after `offset` plus lookback as TA-Lib's output and call it.
   TA-Lib must report exactly that range. This is the column the caller returns; nothing
   copies or fills it again.
8. For MAXINDEX, MININDEX and MINMAXINDEX, add `offset` to each position. These are the
   only functions whose output is a position in the input.

Every error from TA-Lib becomes an `Error` with the return code's name and meaning, for
example `BadParam (bad parameter)`, after the function and its parameter values.

### 2.3 The expression (`src/plugin.rs`)

The plugin exports one expression, `call`. Its kwargs carry the function name and the
parameters by name. The input series arrive in declaration order.

At plan time, Polars asks for the output type. `output_type` looks the function up and
answers: `Float64` for one real output, `Int32` for one integer output, and a `Struct` for
several outputs. The struct fields carry TA-Lib's output names.

At run time, `call` does the following:

1. Take the function from the table and its parameter values from the kwargs. A missing
   or unknown parameter is an error.
2. Take each input as `f64` values. A `Float64` column in one chunk without nulls is
   borrowed as it is, without a copy. Anything else is cast to `Float64` and copied chunk
   by chunk; nulls become NaN.
3. Check the inputs with `Function::rows`, then find the first row where no input is
   NaN. Rows before it are skipped. This is what ta-lib-python does. TA-Lib itself does
   not understand NaN.
4. Run `Function::call` on the remaining rows, with the number of skipped rows as `offset`.
   The outputs come back full length, the skipped rows already NaN or 0.
5. Return one series, or a struct of series.

The expression is not elementwise. Polars therefore evaluates it once per group under
`.over()` and once per frame otherwise.

### 2.4 Indicators beyond TA-Lib (`src/extra.rs`)

An indicator lives here only while TA-Lib does not have it. When TA-Lib adds one, TA-Lib's
replaces it, after a test shows the two are equivalent: `hma` was a composition of `wma`
calls until TA-Lib 0.8 added `HMA`; `test_api.py` shows `HMA` is that composition.

`supersmoother` is Ehlers' 2-pole filter, a Rust expression with a Python wrapper in
`__init__.py`. TA-Lib 0.8.3 has no SuperSmoother (its `SWAK_BUTTER` documentation says so).
Its test is a numpy version of the same recursion. The TA-Lib layer is never changed for it.

### 2.5 The Python module (`src/lib.rs`)

`lib.rs` exports two functions: `version()` returns TA-Lib's version, and `functions()`
returns the description of every function as a list of dicts.

### 2.6 The Python API (`python/polars_talib_fast/_build.py`)

`_build.py` turns each description into a Python function with a real signature:

1. `specs()` reads `functions()` once and keeps the result as `Spec` records. It orders
   the groups as ta-lib-python orders them.
2. `signature(spec)` builds an `inspect.Signature`. The input series come first, one
   parameter per series. A single series defaults to `pl.col("close")`, the two series of
   a pair default to `high` and `low`, and price components default to the column of their
   own name. The parameters come next with TA-Lib's defaults.
3. `function(spec)` returns a callable with that signature and a docstring built from the
   hint, the group, the parameter hints and the output names.
4. `group(name)` returns the functions of one TA-Lib group.

Each group module is three lines. It asks `_build` for its group and puts the functions
in its namespace. `__init__.py` re-exports the ten modules.

`expression(name, inputs, kwargs)` is the one call into Polars' plugin registry. Both the
generated functions and the wrappers in `__init__.py` use it.

### 2.7 Type stubs (`_stubs.py`)

Editors and type checkers cannot see functions that are built at import time. `_stubs.py`
renders one `.pyi` file per group module from the same `Spec` records. The stubs are
committed. A test fails while a committed stub differs from a fresh render.

## 3. Rules the code keeps

- Inputs are `Float64` inside the plugin. Integer and `Float32` columns are cast.
- A window longer than the data gives NaN or 0 rows, never an error. This keeps `.over()`
  groups that are shorter than the window from failing the whole query.
- Invalid parameters raise `ComputeError` with TA-Lib's return code and every parameter's
  value in the message.
- A fractional value for an integer parameter raises, and so does a value that does not
  fit 32 bits. Nothing is truncated.
- Input series of different lengths raise, naming each series and its length.
- Output names, parameter names and defaults are TA-Lib's. Nothing is renamed by hand.
- There are no fallbacks. A missing function, a wrong number of inputs or an unknown
  parameter is an error.

## 4. Tests

The oracle is TA-Lib's C library at the same tag as the crate. `tools/c_oracle` is the code
that ran the plugin before the port to the crate (the C declarations of the abstract
interface, `ffi.rs`, and the safe layer over it), built from the `ta-lib` submodule as a
Python module. `generate.py` runs every function on the test frames, the way the plugin
calls it, and writes `tests/golden`.

The oracle is itself checked: `compare_talib.py` compares its output with ta-lib-python,
an independent path to the same C code, bit for bit. Built at C 0.7.1 it equals
ta-lib-python 0.7.1 (968 arrays, 161 functions); built at C 0.8.1 it equals ta-lib-python
0.8.2 (1312 arrays, 201 functions).

The values are per platform (`tests/golden/windows`, `linux`, `macos`). The 32 functions
TA-Lib flags `USES_TRANSCENDENTAL` call the platform's libm (`sin`, `exp`, `log`, ...),
whose last bit differs between the Windows UCRT and glibc: 20 of them differ by 1 to 2 ULP
between the two on the test data. On one platform, the C library and the crate agree bit
for bit on all 237 functions. The Windows values come from `generate.sh`, the Linux values
from `wsl_generate.sh` (a C build with gcc in WSL), the macOS values from the C library on
the CI runner. `functions.json` and the reference CSV are the same on every platform; a
regeneration that changes them fails.

Every test is parametrized over the descriptions. No test names a function by hand,
except the tests for `hma`, `supersmoother` and the one default TA-Lib changed after the
version ta-lib-python bundles.

| File | What it proves |
|---|---|
| `test_coverage.py` | The description of every function equals the C library's. Every ta-lib-python function exists here, with the same parameters, defaults, types, output names and groups. |
| `test_values.py` | Every function gives bit-identical values to the C library on the same platform, on `Float64` and `Float32`, for the defaults and a short window, on two frames. Grouped evaluation equals per-group evaluation. |
| `test_edges.py` | Short windows, invalid parameters, fractional integers, integer columns, lazy and streaming evaluation. |
| `test_api.py` | `hma` is the Hull composition; `supersmoother` is its recursion. Stubs are current. Each function lives in its group module. |

The two frames are in `tests/data.py`: a synthetic frame with seven leading NaN rows, a
null in the middle and a `periods` column, and TA-Lib's own 252-bar daily reference series
from its regression tool (`tests/golden/talib_reference.csv`, written from the submodule).

## 5. Build and CI

- Rust stable and `uv`. The C oracle also needs the submodule and a C compiler.
- `uv sync` builds the plugin through maturin. `[tool.uv] cache-keys` lists the Rust
  sources, so a `.rs` change triggers a rebuild.
- The wheel is `abi3` for Python 3.10 and newer: `win_amd64`, `manylinux` x86_64 (glibc
  2.17 or newer, built in a manylinux container), `macosx` arm64.
- CI runs on Windows, Linux and macOS: `uv sync`, ruff, ruff format, mypy strict, pytest,
  then the wheel. The macOS job first writes its golden data (section 4). A `v*` tag
  attaches the wheels to a GitHub release and uploads them to PyPI.
- `tools/wsl_test.sh` runs the same steps on Linux in WSL from a clone of a committed branch.

## 6. Performance

- TA-Lib is single-threaded per call. Polars runs independent expressions in parallel, and
  the shared `Core` needs no lock.
- A column with nulls, in several chunks, or not `Float64` is copied once per call. A
  dense single-chunk `Float64` column is not.

### 6.1 The crate against the C library

`tools/bench.py compare` times builds interleaved (A B C A B C, one process at a time, 4
rounds, the median of 15 runs per round, then the median of the rounds), on one machine
(24 threads, polars 1.44.2). The C columns are the plugin code before the port, built on
TA-Lib's C library 0.7.1 and 0.8.3; the last column is this code on the crate 0.8.3. One
thread (`POLARS_MAX_THREADS=1`), ms:

| scenario | C 0.7.1 | C 0.8.3 | crate 0.8.3 |
|---|---:|---:|---:|
| `ema`, 1M rows | 2.59 | 1.73 | 1.72 |
| `atr`, 1M rows | 7.01 | 2.24 | 1.97 |
| `macd`, 1M rows | 11.50 | 5.10 | 4.33 |
| `sar`, 1M rows | 5.55 | 5.72 | 5.03 |
| 8 indicators in one select, 1M rows | 49.0 | 38.5 | 28.7 |
| `ema`, 100 rows | 0.027 | 0.028 | 0.027 |
| `ema` over 2 000 symbols × 500 rows | 16.6 | 15.6 | 15.3 |
| `supersmoother` over the same groups (no TA-Lib) | 18.4 | 18.4 | 18.6 |
| Polars `ewm_mean` over the same groups | 12.4 | 12.6 | 12.8 |

With all threads, the 8 indicators take 21.1, 15.5 and 10.6 ms. Most of the gain from 0.7.1
is TA-Lib 0.8's own (the C 0.8.3 column). The crate is as fast as the C library or faster.

That holds only because outputs are allocated zeroed: the crate takes an initialised
slice to write into, and a NaN fill of every row first cost about 0.5 ms per million rows
and output (EMA 2.39 ms, MACD 6.13 ms). Now only the rows before the lookback are written
before TA-Lib runs.

Under `.over()` the cost per group is not TA-Lib's. An expression of this package that
calls no TA-Lib function costs more per group than `ema` through TA-Lib. Polars' own
expression is about 1.3 µs per group cheaper: that is the plugin call (kwargs, inputs,
outputs), which a TA-Lib-side dispatcher cannot change.

### 6.2 Against ta-lib-python

ta-lib-python runs TA-Lib's C code on numpy arrays, and `to_numpy()` is zero-copy for a
dense float column, so one indicator on one series costs the same on either route. The
plugin wins where Polars does the work around the call: independent expressions run in
parallel, and `.over()` runs the function per group without a Python call. Measured with
the plugin on TA-Lib's C library 0.7.1 (section 6.1 compares that build with the crate).
Median of 10 runs, same machine, the symbol rows each measured in a fresh process:

| scenario | plugin | ta-lib-python on `to_numpy` | ta-lib-python in `map_batches` |
|---|---:|---:|---:|
| 1 indicator, 1M rows | 2.6 ms | 2.6 ms | 2.7 ms |
| 8 indicators in one select, 1M rows | 13.3 ms | 33.2 ms | 34.3 ms |
| 8 indicators, 10M rows | 129 ms | 344 ms | 341 ms |
| 1 indicator over 2 000 symbols | 11.3 ms | 8.9 ms, hand-written loop | 35 ms |
| 1 indicator over 20 000 symbols | 72 ms | 54 ms, hand-written loop | 289 ms |
