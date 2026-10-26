"""Writes the golden data the plugin's tests compare against, from TA-Lib's C library.

    uv run --no-sync maturin develop --uv --release -m tools/c_oracle/Cargo.toml
    uv run --no-sync python tools/c_oracle/generate.py [--out DIR]

(``generate.sh`` runs both.) The ``c_oracle`` module is TA-Lib's C library at the tag the
``tools/c_oracle/ta-lib`` submodule is checked out at. Written into ``--out`` (default
``tests/golden``):

- ``functions.json``: the C library's version and its description of every function;
- ``<platform>/<frame>.npz`` (``windows``, ``linux``, ``macos``): per frame of ``tests/data.py``,
  per input dtype (``f64``, ``f32`` cast) and per variant (``default`` parameters, and
  ``timeperiod=<w>`` for a short window ``w`` where there is a ``timeperiod``), every output,
  keyed ``<dtype>/<NAME>/<variant>/<output>``. Per platform because the functions TA-Lib
  flags ``USES_TRANSCENDENTAL`` call the platform's libm (``sin``, ``exp``, ``log``...), whose
  last bit differs between platforms; on one platform, the C library and the crate agree.
- ``<platform>/vmath.json``: whether the C library's math kernel is active there and the
  functions it computes (see ``MathKernel``).

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

import c_oracle
import numpy as np
import numpy.typing as npt
import polars as pl


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
    """The C library's description of one function, as far as a call needs it."""

    name: str
    columns: tuple[str, ...]
    params: tuple[Param, ...]
    outputs: tuple[Output, ...]

    @staticmethod
    def of(f: dict[str, Any]) -> Spec:
        return Spec(
            name=f["name"],
            columns=tuple(part for name, parts in f["inputs"] for part in (parts or [name])),
            params=tuple(
                Param(name, integer, default) for name, integer, default, _ in f["params"]
            ),
            outputs=tuple(Output(name, integer) for name, integer in f["outputs"]),
        )


class ReferenceData:
    """TA-Lib's ``*_daily_ref_0`` regression arrays, from the submodule to a CSV."""

    ARRAY = re.compile(r"TA_Real\s+TA_SREF_(\w+)_daily_ref_0_PRIV\[252\]\s*=\s*\{(.*?)\};", re.S)
    COLUMNS = ("open", "high", "low", "close", "volume")
    ROWS = 252

    def __init__(self, test_data_c: Path, csv: Path) -> None:
        self.test_data_c = test_data_c
        self.csv = csv

    def write(self, version: str) -> None:
        """The arrays as CSV, values written exactly (``repr``)."""
        arrays = {
            name: [float(v) for v in re.split(r"[,\s]+", body.strip())]
            for name, body in self.ARRAY.findall(self.test_data_c.read_text())
        }
        if tuple(arrays) != self.COLUMNS:
            raise RuntimeError(
                f"{self.test_data_c}: expected arrays {self.COLUMNS}, got {tuple(arrays)}"
            )
        lines = [
            "# TA-Lib's *_daily_ref_0 regression data, src/tools/ta_regtest/test_data.c of TA-Lib "
            f"{version}.",
            "# Copyright (c) 1999-2026, Mario Fortier, BSD-3-Clause (LICENSES/TA-Lib.txt).",
            "# Written by tools/c_oracle/generate.py.",
            ",".join(self.COLUMNS),
        ]
        lines += [",".join(repr(arrays[c][i]) for c in self.COLUMNS) for i in range(self.ROWS)]
        self.csv.parent.mkdir(parents=True, exist_ok=True)
        self.csv.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


class Generator:
    """Runs every function of the C library on the test frames, the way the plugin calls it."""

    DEFAULT_COLUMN = {"real": "close", "real0": "high", "real1": "low"}
    DTYPES = {"f64": pl.Float64, "f32": pl.Float32}
    SHORT_WINDOW = 3
    MAX_WINDOW_TRIES = 8

    def __init__(self, specs: list[Spec]) -> None:
        self.specs = specs

    def run(
        self, spec: Spec, df: pl.DataFrame, params: dict[str, int | float]
    ) -> list[npt.NDArray[Any]]:
        """The C call the plugin makes: inputs as float64 (nulls NaN), leading NaN rows cut."""
        columns = [
            df[self.DEFAULT_COLUMN.get(c, c)].to_numpy().astype(np.float64) for c in spec.columns
        ]
        finite = np.logical_and.reduce([~np.isnan(c) for c in columns])
        begin = int(np.argmax(finite)) if finite.any() else df.height
        values = [params[p.name] for p in spec.params]
        outputs = c_oracle.call(spec.name, [c[begin:].tolist() for c in columns], values, begin)
        return [
            np.asarray(values, dtype=np.int32 if o.integer else np.float64)
            for o, values in zip(spec.outputs, outputs, strict=True)
        ]

    def short_window(self, spec: Spec, df: pl.DataFrame) -> int:
        """The smallest ``timeperiod`` from ``SHORT_WINDOW`` up that the function accepts (FRAMA,
        for one, wants an even period). Any error other than a rejected parameter is raised."""
        defaults = {p.name: p.value for p in spec.params}
        for window in range(self.SHORT_WINDOW, self.SHORT_WINDOW + self.MAX_WINDOW_TRIES):
            try:
                self.run(spec, df, {**defaults, "timeperiod": window})
            except RuntimeError as e:
                if "TA_BAD_PARAM" not in str(e):
                    raise
                continue
            return window
        raise RuntimeError(f"{spec.name}: no timeperiod from {self.SHORT_WINDOW} accepted")

    def variants(self, spec: Spec, df: pl.DataFrame) -> dict[str, dict[str, int | float]]:
        """``default``, and ``timeperiod=<w>`` with ``w`` from ``short_window``."""
        default: dict[str, int | float] = {p.name: p.value for p in spec.params}
        variants = {"default": default}
        if any(p.name == "timeperiod" for p in spec.params):
            window = self.short_window(spec, df)
            variants[f"timeperiod={window}"] = {**default, "timeperiod": window}
        return variants

    def golden(self, frame: pl.DataFrame) -> dict[str, npt.NDArray[Any]]:
        arrays: dict[str, npt.NDArray[Any]] = {}
        for dtype_name, dtype in self.DTYPES.items():
            df = frame.cast(dtype)
            for spec in self.specs:
                for variant, params in self.variants(spec, df).items():
                    outputs = zip(spec.outputs, self.run(spec, df, params), strict=True)
                    for output, values in outputs:
                        arrays[f"{dtype_name}/{spec.name}/{variant}/{output.name}"] = values
        return arrays


class MathKernel:
    """Where the C library computes element-wise math with a platform kernel (vForce on macOS
    arm64): whether it is active here, and the functions whose batch loop is a
    ``TA_VMATH_MAP`` in the C source. The crate computes them with scalar libm, which TA-Lib's
    own tests hold to within 8 ULP of the kernel (``fuzz_vmath_near``)."""

    MAP = re.compile(r"\bTA_VMATH_MAP\s*\(")

    def __init__(self, ta_func: Path) -> None:
        self.ta_func = ta_func

    def functions(self) -> list[str]:
        return sorted(
            source.stem.removeprefix("ta_")
            for source in self.ta_func.glob("ta_*.c")
            if self.MAP.search(source.read_text(encoding="utf-8", errors="replace"))
        )

    def write(self, path: Path) -> None:
        kernel = {"vmath_transcendental": c_oracle.vmath_kernel(), "functions": self.functions()}
        path.write_text(json.dumps(kernel, indent=1) + "\n", encoding="utf-8", newline="\n")


class GoldenData:
    """The command: reference CSV, then ``functions.json`` and one ``.npz`` per frame."""

    ROOT = Path(__file__).resolve().parents[2]
    GOLDEN = ROOT / "tests" / "golden"
    TALIB = Path(__file__).resolve().parent / "ta-lib"
    TEST_DATA_C = TALIB / "src" / "tools" / "ta_regtest" / "test_data.c"

    def __init__(self, out: Path) -> None:
        self.out = out

    def write(self) -> None:
        self.out.mkdir(parents=True, exist_ok=True)
        version = c_oracle.version().split(" ")[0]
        print(f"TA-Lib C {version} -> {self.out}")
        ReferenceData(self.TEST_DATA_C, self.GOLDEN / "talib_reference.csv").write(version)
        sys.path.insert(0, str(self.ROOT / "tests"))
        from data import frame, platform, talib_reference  # noqa: PLC0415  (reads the new CSV)

        functions = c_oracle.functions()
        (self.out / "functions.json").write_text(
            json.dumps({"version": version, "functions": functions}, indent=1) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        values = self.out / platform()
        values.mkdir(exist_ok=True)
        MathKernel(self.TALIB / "src" / "ta_func").write(values / "vmath.json")
        generator = Generator([Spec.of(f) for f in functions])
        for name, df in {"synthetic": frame(), "talib-reference": talib_reference()}.items():
            arrays = generator.golden(df)
            np.savez_compressed(values / f"{name}.npz", allow_pickle=False, **arrays)
            print(f"{values.name}/{name}: {len(arrays)} arrays, {len(generator.specs)} functions")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--out", type=Path, default=GoldenData.GOLDEN)
    GoldenData(parser.parse_args().out).write()
