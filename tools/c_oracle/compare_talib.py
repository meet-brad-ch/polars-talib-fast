"""Proves the oracle: golden data written by ``generate.py`` must be bit-identical to what the
installed ta-lib-python computes, for every function both have. Run it with the submodule at
the C version that ta-lib-python bundles (ta-lib-python 0.7.1 = C 0.7.1, 0.8.2 = C 0.8.1):

    tools/c_oracle/generate.sh <dir>
    <python with ta-lib-python, numpy, polars> tools/c_oracle/compare_talib.py <dir>

Prints one line per difference and a summary; exits 1 on any difference.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import polars as pl
import talib


@dataclass
class Summary:
    compared: int = 0
    differing: list[str] = field(default_factory=list)
    oracle_only: list[str] = field(default_factory=list)
    talib_only: list[str] = field(default_factory=list)


class OracleCheck:
    ROOT = Path(__file__).resolve().parents[2]
    DEFAULT_COLUMN = {"real": "close", "real0": "high", "real1": "low"}
    DTYPES = {"f64": pl.Float64, "f32": pl.Float32}

    def __init__(self, golden: Path) -> None:
        self.golden = golden
        functions = json.loads((golden / "functions.json").read_text())["functions"]
        self.functions: dict[str, dict[str, Any]] = {f["name"]: f for f in functions}
        self.summary = Summary(
            oracle_only=sorted(set(self.functions) - set(talib.get_functions())),
            talib_only=sorted(set(talib.get_functions()) - set(self.functions)),
        )

    def run(self) -> Summary:
        sys.path.insert(0, str(self.ROOT / "tests"))
        from data import frame, talib_reference  # noqa: PLC0415

        shared = [n for n in self.functions if n in set(talib.get_functions())]
        for frame_name, data in {
            "synthetic": frame(),
            "talib-reference": talib_reference(),
        }.items():
            with np.load(self.golden / f"{frame_name}.npz") as arrays:
                golden = {k: arrays[k] for k in arrays.files}
            for dtype_name, dtype in self.DTYPES.items():
                df = data.cast(dtype)
                for name in shared:
                    self._function(f"{frame_name}/{dtype_name}", golden, df, dtype_name, name)
        return self.summary

    def _function(
        self,
        where: str,
        golden: dict[str, npt.NDArray[Any]],
        df: pl.DataFrame,
        dtype: str,
        name: str,
    ) -> None:
        f = self.functions[name]
        columns = [part for n, parts in f["inputs"] for part in (parts or [n])]
        inputs = [df[self.DEFAULT_COLUMN.get(c, c)].to_numpy().astype(np.float64) for c in columns]
        prefix = f"{dtype}/{name}/"
        for variant in sorted(
            {k[len(prefix) :].split("/")[0] for k in golden if k.startswith(prefix)}
        ):
            kwargs = {} if variant == "default" else {"timeperiod": int(variant.split("=")[1])}
            expected = getattr(talib, name)(*inputs, **kwargs)
            expected = expected if isinstance(expected, tuple) else (expected,)
            for (output, _), values in zip(f["outputs"], expected, strict=True):
                self._compare(
                    f"{where}/{prefix}{variant}/{output}",
                    golden[f"{prefix}{variant}/{output}"],
                    values,
                )

    def _compare(self, key: str, got: npt.NDArray[Any], expected: npt.NDArray[Any]) -> None:
        self.summary.compared += 1
        same = got.shape == expected.shape and np.array_equal(
            got, expected, equal_nan=got.dtype.kind == "f"
        )
        if not same:
            delta = np.nanmax(np.abs(got.astype(np.float64) - expected))
            self.summary.differing.append(f"{key}: max |delta| {delta!r}")

    @staticmethod
    def report(summary: Summary) -> int:
        for line in summary.differing:
            print("DIFF", line)
        print(
            f"ta-lib-python {talib.__version__} (C {talib.__ta_version__.decode().split(' ')[0]})"
        )
        print(f"compared {summary.compared} arrays, {len(summary.differing)} differ")
        print(f"oracle only ({len(summary.oracle_only)}): {' '.join(summary.oracle_only)}")
        print(f"ta-lib-python only ({len(summary.talib_only)}): {' '.join(summary.talib_only)}")
        return 1 if summary.differing or summary.talib_only else 0


if __name__ == "__main__":
    sys.exit(OracleCheck.report(OracleCheck(Path(sys.argv[1])).run()))
