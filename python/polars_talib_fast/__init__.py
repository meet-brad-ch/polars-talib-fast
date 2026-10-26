"""TA-Lib for Polars expressions.

Every TA-Lib function is a module-level function returning a ``pl.Expr``; multi-output
functions return a struct with TA-Lib's output names. Signatures, defaults and docstrings
come from TA-Lib itself (see ``_build``), grouped into one module per TA-Lib group.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

from . import _polars_talib_fast
from ._build import MODULES, expression, specs
from .cycle import *  # noqa: F403
from .math_operators import *  # noqa: F403
from .math_transform import *  # noqa: F403
from .momentum import *  # noqa: F403
from .overlap import *  # noqa: F403
from .pattern import *  # noqa: F403
from .price_transform import *  # noqa: F403
from .statistic import *  # noqa: F403
from .volatility import *  # noqa: F403
from .volume import *  # noqa: F403

if TYPE_CHECKING:
    from polars._typing import IntoExpr

__talib_version__ = _polars_talib_fast.version().split(" ")[0]


def get_functions() -> list[str]:
    return [s.python_name for s in specs()]


def get_function_groups() -> dict[str, list[str]]:
    return {group: [s.python_name for s in specs() if s.group == group] for group in MODULES}


def supersmoother(real: IntoExpr = "close", period: float = 10.0) -> pl.Expr:
    """Ehlers' 2-pole SuperSmoother, a low-pass IIR filter with about half the lag of an
    EMA of the same cut-off. Coefficients as AmiBroker's IIR() documents them (1.41421 for
    sqrt 2), seeded with the first two values; leading NaN rows are skipped. Not a TA-Lib
    function."""
    return expression("supersmoother", [real], {"period": period})
