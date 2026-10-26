"""Proves the oracle: golden data written by ``generate.py`` must be bit-identical to what the
installed ta-lib-python computes, for every function both have. Run it with the submodule at
the C version that ta-lib-python bundles (ta-lib-python 0.7.1 = C 0.7.1, 0.8.2 = C 0.8.1):

    uv run --no-sync python tools/c_oracle/generate.py --out <dir>
    <python with ta-lib-python, numpy, polars> tools/c_oracle/compare_talib.py <dir>

Prints one line per difference and a summary; exits 1 on any difference.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import polars as pl
import talib  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COLUMN = {"real": "close", "real0": "high", "real1": "low"}
DTYPES = {"f64": pl.Float64, "f32": pl.Float32}


@dataclass(frozen=True)
class Summary:
    compared: int
    differing: list[str]
    oracle_only: list[str]
    talib_only: list[str]


def compare(golden: Path) -> Summary:
    sys.path.insert(0, str(ROOT / "tests"))
    from data import frame, talib_reference  # noqa: PLC0415

    functions = json.loads((golden / "functions.json").read_text())["functions"]
    ours = {f["name"]: f for f in functions}
    theirs = set(talib.get_functions())
    shared = [name for name in ours if name in theirs]
    differing: list[str] = []
    compared = 0
    for frame_name, data in {"synthetic": frame(), "talib-reference": talib_reference()}.items():
        arrays = np.load(golden / f"{frame_name}.npz")
        for dtype_name, dtype in DTYPES.items():
            df = data.cast(dtype)
            for name in shared:
                f = ours[name]
                columns = [part for n, parts in f["inputs"] for part in (parts or [n])]
                inputs = [df[DEFAULT_COLUMN.get(c, c)].to_numpy().astype(np.float64) for c in columns]
                prefix = f"{dtype_name}/{name}/"
                names = {k[len(prefix) :].split("/")[0] for k in arrays.files if k.startswith(prefix)}
                for variant in sorted(names):
                    kwargs = {} if variant == "default" else {"timeperiod": int(variant.split("=")[1])}
                    expected = getattr(talib, name)(*inputs, **kwargs)
                    expected = expected if isinstance(expected, tuple) else (expected,)
                    for (output, _), values in zip(f["outputs"], expected, strict=True):
                        key = f"{dtype_name}/{name}/{variant}/{output}"
                        compared += 1
                        got = arrays[key]
                        same = got.shape == values.shape and np.array_equal(
                            got, values, equal_nan=got.dtype.kind == "f"
                        )
                        if not same:
                            delta = np.nanmax(np.abs(got.astype(np.float64) - values))
                            differing.append(f"{frame_name}/{key}: max |delta| {delta!r}")
    return Summary(
        compared=compared,
        differing=differing,
        oracle_only=sorted(set(ours) - theirs),
        talib_only=sorted(theirs - set(ours)),
    )


def main() -> None:
    golden = Path(sys.argv[1])
    summary = compare(golden)
    for line in summary.differing:
        print("DIFF", line)
    print(f"ta-lib-python {talib.__version__} (C {talib.__ta_version__.decode().split(' ')[0]})")
    print(f"compared {summary.compared} arrays, {len(summary.differing)} differ")
    print(f"oracle only ({len(summary.oracle_only)}): {' '.join(summary.oracle_only)}")
    print(f"ta-lib-python only ({len(summary.talib_only)}): {' '.join(summary.talib_only)}")
    sys.exit(1 if summary.differing or summary.talib_only else 0)


if __name__ == "__main__":
    main()
