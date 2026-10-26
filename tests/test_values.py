"""Every function computes exactly what TA-Lib's C library computes on the same platform: the
golden data in ``tests/golden/<platform>``, written by ``tools/c_oracle`` from the C library at
the tag of the ``ta-lib`` crate. On the synthetic frame (leading NaN rows, a null) and on
TA-Lib's own 252-bar reference data, on float64 and float32 input, for TA-Lib's defaults and
for a short window. Per-group evaluation gives per-group results. Per platform, because the
functions TA-Lib flags ``USES_TRANSCENDENTAL`` use the platform's libm."""

import json
from pathlib import Path

import numpy as np
import numpy.typing as npt
import polars as pl
import pytest

import polars_talib_fast as plta
from data import frame, platform, talib_reference
from polars_talib_fast._build import Spec, specs

GOLDEN = Path(__file__).parent / "golden"
FRAMES = {"synthetic": frame(), "talib-reference": talib_reference()}
DTYPES = {"f64": pl.Float64, "f32": pl.Float32}


class Golden:
    """The C library's outputs for one frame, by dtype, function, variant and output."""

    def __init__(self, frame_name: str) -> None:
        path = GOLDEN / platform() / f"{frame_name}.npz"
        if not path.exists():
            raise FileNotFoundError(f"{path}: run tools/c_oracle/generate.sh on this platform")
        with np.load(path) as arrays:
            self.arrays = {key: arrays[key] for key in arrays.files}

    def variants(self, dtype: str, spec: Spec) -> list[str]:
        prefix = f"{dtype}/{spec.name}/"
        return sorted({k[len(prefix) :].split("/")[0] for k in self.arrays if k.startswith(prefix)})

    def outputs(self, dtype: str, spec: Spec, variant: str) -> list[npt.NDArray[np.generic]]:
        return [self.arrays[f"{dtype}/{spec.name}/{variant}/{o.name}"] for o in spec.outputs]

    @staticmethod
    def kwargs(variant: str) -> dict[str, int]:
        """``default`` → no arguments; ``timeperiod=4`` → ``{"timeperiod": 4}``."""
        if variant == "default":
            return {}
        name, value = variant.split("=")
        return {name: int(value)}


class MathKernel:
    """Where TA-Lib's C library computes element-wise math with a platform kernel (vForce on
    macOS arm64), it differs from the crate's scalar libm in the last bits. TA-Lib's own tests
    hold a kernel value against a libm value with ``fuzz_vmath_near`` (ta_regtest/fuzz_data.h):
    both NaN or equal; else no infinity, the same sign, at most 8 ULP apart. This is a port of
    that rule; everything else is compared bit for bit."""

    MAX_STEPS = 8

    def __init__(self) -> None:
        path = GOLDEN / platform() / "vmath.json"
        if not path.exists():
            raise FileNotFoundError(f"{path}: run tools/c_oracle/generate.sh on this platform")
        kernel = json.loads(path.read_text(encoding="utf-8"))
        self.functions: set[str] = (
            set(kernel["functions"]) if kernel["vmath_transcendental"] else set()
        )

    @classmethod
    def near(cls, a: npt.NDArray[np.float64], b: npt.NDArray[np.float64]) -> npt.NDArray[np.bool_]:
        """Element-wise ``fuzz_vmath_near``."""
        both_nan = np.isnan(a) & np.isnan(b)
        any_nan = np.isnan(a) | np.isnan(b)
        equal = a == b
        ua, ub = a.view(np.uint64), b.view(np.uint64)
        same_sign = (ua >> np.uint64(63)) == (ub >> np.uint64(63))
        steps = np.where(ua > ub, ua - ub, ub - ua)
        close = ~any_nan & ~np.isinf(a) & ~np.isinf(b) & same_sign & (steps <= cls.MAX_STEPS)
        result: npt.NDArray[np.bool_] = both_nan | (~any_nan & equal) | close
        return result


GOLDEN_DATA = {name: Golden(name) for name in FRAMES}
KERNEL = MathKernel()


def assert_same(
    expr: pl.Expr, df: pl.DataFrame, expected: list[npt.NDArray[np.generic]], kernel: bool
) -> None:
    got = df.select(expr.alias("out"))["out"]
    columns = [got.struct.field(f) for f in got.struct.fields] if len(expected) > 1 else [got]
    assert len(columns) == len(expected)
    for column, values in zip(columns, expected, strict=True):
        assert column.dtype == (pl.Int32 if values.dtype == np.int32 else pl.Float64)
        if kernel:
            near = MathKernel.near(column.to_numpy(), values.astype(np.float64))
            assert near.all(), f"{int((~near).sum())} rows more than 8 ULP from the kernel"
        else:
            np.testing.assert_array_equal(column.to_numpy(), values)


@pytest.mark.parametrize("dtype", DTYPES, ids=list(DTYPES))
@pytest.mark.parametrize("frame_name", FRAMES, ids=list(FRAMES))
@pytest.mark.parametrize("spec", specs(), ids=lambda s: s.python_name)
def test_equals_c_library(frame_name: str, spec: Spec, dtype: str) -> None:
    golden = GOLDEN_DATA[frame_name]
    df = FRAMES[frame_name].cast(DTYPES[dtype])
    fn = getattr(plta, spec.python_name)
    variants = golden.variants(dtype, spec)
    expected_variants = 2 if any(p.name == "timeperiod" for p in spec.params) else 1
    assert "default" in variants and len(variants) == expected_variants, variants
    kernel = spec.name in KERNEL.functions
    for variant in variants:
        expected = golden.outputs(dtype, spec, variant)
        assert_same(fn(**Golden.kwargs(variant)), df, expected, kernel)


def test_math_kernel_rule_is_talibs() -> None:
    """The edges of ``fuzz_vmath_near``: 8 ULP pass, 9 fail; sign, infinity and NaN."""
    one = np.array([1.0])
    up = one.view(np.uint64)
    assert MathKernel.near(one, (up + np.uint64(8)).view(np.float64)).all()
    assert not MathKernel.near(one, (up + np.uint64(9)).view(np.float64)).any()
    assert MathKernel.near(np.array([np.nan]), np.array([np.nan])).all()
    assert not MathKernel.near(np.array([np.nan]), one).any()
    assert not MathKernel.near(np.array([np.inf]), np.array([1.7976931348623157e308])).any()
    assert MathKernel.near(np.array([np.inf]), np.array([np.inf])).all()
    assert MathKernel.near(np.array([0.0]), np.array([-0.0])).all()  # equal in C
    tiny = np.array([5e-324])
    assert not MathKernel.near(tiny, -tiny).any()


@pytest.mark.parametrize("expr", [plta.sma(), plta.macd(), plta.cdldoji(), plta.obv()])
def test_over_groups_evaluates_each_group_alone(ohlcv: pl.DataFrame, expr: pl.Expr) -> None:
    alone = ohlcv.select(expr.alias("out"))
    two = pl.concat([ohlcv.with_columns(pl.lit(s).alias("symbol")) for s in ("A", "B")]).select(
        expr.over("symbol").alias("out")
    )
    assert two.equals(pl.concat([alone, alone]))
