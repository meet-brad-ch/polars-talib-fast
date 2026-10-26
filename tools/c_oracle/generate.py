"""Writes the golden data the plugin's tests compare against, from TA-Lib's C library.

    uv run maturin develop --release -m tools/c_oracle/Cargo.toml
    uv run --no-sync python tools/c_oracle/generate.py [--out DIR]

(``generate.sh`` runs both.) The ``c_oracle`` module is TA-Lib's C library at the tag the
``tools/c_oracle/ta-lib`` submodule is checked out at. Written into ``--out`` (default
``tests/golden``):

- ``functions.json``: the C library's version and its description of every function;
- ``<frame>.npz``: per frame of ``tests/data.py``, per input dtype (``f64``, ``f32`` cast) and
  per variant (``default`` parameters, and ``timeperiod=<w>`` for a short window ``w`` where
  there is a ``timeperiod``),
  every output, keyed ``<dtype>/<NAME>/<variant>/<output>``.

``tests/golden/talib_reference.csv`` (TA-Lib's 252-bar regression data, which ``tests/data.py``
reads) is always rewritten from the submodule first. Leading rows where any input is NaN are
cut off before the call, exactly as the plugin does.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import c_oracle  # type: ignore[import-not-found]
import numpy as np
import numpy.typing as npt
import polars as pl

ROOT = Path(__file__).resolve().parents[2]
TALIB = Path(__file__).resolve().parent / "ta-lib"
GOLDEN = ROOT / "tests" / "golden"
REFERENCE_CSV = GOLDEN / "talib_reference.csv"
TEST_DATA_C = TALIB / "src" / "tools" / "ta_regtest" / "test_data.c"
TALIB_ARRAY = re.compile(r"TA_Real\s+TA_SREF_(\w+)_daily_ref_0_PRIV\[252\]\s*=\s*\{(.*?)\};", re.S)
REFERENCE_COLUMNS = ["open", "high", "low", "close", "volume"]
DEFAULT_COLUMN = {"real": "close", "real0": "high", "real1": "low"}
DTYPES = {"f64": pl.Float64, "f32": pl.Float32}
SHORT_WINDOW = 3
MAX_WINDOW_TRIES = 8


@dataclass(frozen=True)
class Param:
    name: str
    integer: bool
    default: float

    @property
    def value(self) -> int | float:
        return int(self.default) if self.integer else self.default


@dataclass(frozen=True)
class Output:
    name: str
    integer: bool


@dataclass(frozen=True)
class Spec:
    name: str
    columns: tuple[str, ...]
    params: tuple[Param, ...]
    outputs: tuple[Output, ...]


def write_reference_csv() -> None:
    """TA-Lib's ``*_daily_ref_0`` arrays as CSV, values written exactly (``repr``)."""
    arrays = {
        name: [float(v) for v in re.split(r"[,\s]+", body.strip())]
        for name, body in TALIB_ARRAY.findall(TEST_DATA_C.read_text())
    }
    assert list(arrays) == REFERENCE_COLUMNS, list(arrays)
    lines = [
        f"# TA-Lib's *_daily_ref_0 regression data, src/tools/ta_regtest/test_data.c of TA-Lib "
        f"{c_oracle.version().split(' ')[0]}.",
        "# Copyright (c) 1999-2026, Mario Fortier, BSD-3-Clause (LICENSES/TA-Lib.txt).",
        "# Written by tools/c_oracle/generate.py.",
        ",".join(REFERENCE_COLUMNS),
    ]
    lines += [",".join(repr(arrays[c][i]) for c in REFERENCE_COLUMNS) for i in range(252)]
    GOLDEN.mkdir(parents=True, exist_ok=True)
    REFERENCE_CSV.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def specs(functions: list[dict[str, Any]]) -> list[Spec]:
    return [
        Spec(
            name=f["name"],
            columns=tuple(part for name, parts in f["inputs"] for part in (parts or [name])),
            params=tuple(Param(name, integer, default) for name, integer, default, _ in f["params"]),
            outputs=tuple(Output(name, integer) for name, integer in f["outputs"]),
        )
        for f in functions
    ]


def run(spec: Spec, df: pl.DataFrame, params: dict[str, int | float]) -> list[npt.NDArray[Any]]:
    """The C call the plugin makes: inputs as float64 (nulls NaN), leading NaN rows cut."""
    columns = [df[DEFAULT_COLUMN.get(c, c)].to_numpy().astype(np.float64) for c in spec.columns]
    finite = np.logical_and.reduce([~np.isnan(c) for c in columns])
    begin = int(np.argmax(finite)) if finite.any() else df.height
    values = [params[p.name] for p in spec.params]
    outputs = c_oracle.call(spec.name, [c[begin:].tolist() for c in columns], values, begin)
    return [
        np.asarray(values, dtype=np.int32 if o.integer else np.float64)
        for o, values in zip(spec.outputs, outputs, strict=True)
    ]


def short_window(spec: Spec, df: pl.DataFrame) -> int:
    """The smallest ``timeperiod`` from ``SHORT_WINDOW`` up that the function accepts (FRAMA,
    for one, wants an even period). Any error other than a rejected parameter is raised."""
    defaults = {p.name: p.value for p in spec.params}
    for window in range(SHORT_WINDOW, SHORT_WINDOW + MAX_WINDOW_TRIES):
        try:
            run(spec, df, {**defaults, "timeperiod": window})
        except RuntimeError as e:
            if "TA_BAD_PARAM" not in str(e):
                raise
            continue
        return window
    raise RuntimeError(f"{spec.name}: no timeperiod from {SHORT_WINDOW} accepted")


def golden(spec_list: list[Spec], frame: pl.DataFrame) -> dict[str, npt.NDArray[Any]]:
    """Variants: ``default``, and ``timeperiod=<w>`` with ``w`` from ``short_window``."""
    arrays: dict[str, npt.NDArray[Any]] = {}
    for dtype_name, dtype in DTYPES.items():
        df = frame.cast(dtype)
        for spec in spec_list:
            variants = {"default": {p.name: p.value for p in spec.params}}
            if any(p.name == "timeperiod" for p in spec.params):
                window = short_window(spec, df)
                variants[f"timeperiod={window}"] = {**variants["default"], "timeperiod": window}
            for variant, params in variants.items():
                for output, values in zip(spec.outputs, run(spec, df, params), strict=True):
                    arrays[f"{dtype_name}/{spec.name}/{variant}/{output.name}"] = values
    return arrays


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--out", type=Path, default=GOLDEN)
    out: Path = parser.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    version = c_oracle.version().split(" ")[0]
    print(f"TA-Lib C {version} -> {out}")

    write_reference_csv()
    sys.path.insert(0, str(ROOT / "tests"))
    from data import frame, talib_reference  # noqa: PLC0415  (reads the CSV just written)

    functions = c_oracle.functions()
    (out / "functions.json").write_text(
        json.dumps({"version": version, "functions": functions}, indent=1) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    spec_list = specs(functions)
    for name, df in {"synthetic": frame(), "talib-reference": talib_reference()}.items():
        arrays = golden(spec_list, df)
        np.savez_compressed(out / f"{name}.npz", allow_pickle=False, **arrays)
        print(f"{name}: {len(arrays)} arrays, {len(spec_list)} functions")


if __name__ == "__main__":
    main()
