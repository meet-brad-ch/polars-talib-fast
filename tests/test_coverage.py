"""Every TA-Lib function is exposed, and its signature is what TA-Lib declares.

Two oracles: the C library's own description of every function (``tests/golden/functions.json``,
written by ``tools/c_oracle`` at the tag of the ``ta-lib`` crate) for all of them, and
ta-lib-python (``talib``) for the names, parameters, defaults and outputs of the functions it
has. ta-lib-python 0.8.2 bundles TA-Lib C 0.8.1, so it knows fewer functions than the crate.
"""

import inspect
import json
from pathlib import Path
from typing import Any

import polars as pl
import pytest
import talib
from talib import abstract

import polars_talib_fast as plta
from polars_talib_fast import _polars_talib_fast
from polars_talib_fast._build import DEFAULT_COLUMN, MODULES, specs

C_LIBRARY: dict[str, Any] = json.loads(
    (Path(__file__).parent / "golden" / "functions.json").read_text(encoding="utf-8")
)
NAMES = [s.name for s in specs()]
TALIB_PYTHON_NAMES = [n for n in NAMES if n in set(talib.get_functions())]
# Defaults TA-Lib changed after C 0.8.1, the version ta-lib-python 0.8.2 bundles.
CHANGED_SINCE_TALIB_PYTHON = {
    "PERCENTILE": {"timeperiod": 100},  # TA-Lib b7d27db69 "feat(percentile): default period 100"
}


def test_same_version_as_the_c_oracle() -> None:
    assert plta.__talib_version__ == C_LIBRARY["version"]


def in_module_order(functions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group by group in ``MODULES`` order, TA-Lib's order within a group. The raw order of the
    groups differs between the C library and the crate; the package's order is ``MODULES``."""
    return sorted(functions, key=lambda f: list(MODULES).index(f["group"]))


def test_description_equals_the_c_library() -> None:
    """Names, groups, hints, inputs, parameters (defaults, hints) and outputs."""
    ours = json.loads(json.dumps(_polars_talib_fast.functions()))  # tuples as lists, like JSON
    assert in_module_order(ours) == in_module_order(C_LIBRARY["functions"])


def test_every_function_is_there_and_nothing_else() -> None:
    assert NAMES == [f["name"] for f in in_module_order(C_LIBRARY["functions"])]
    assert plta.get_functions() == [n.lower() for n in NAMES]
    groups = {f["group"] for f in C_LIBRARY["functions"]}
    assert set(MODULES) == groups == set(talib.get_function_groups())
    assert plta.get_function_groups() == {
        g: [f["name"].lower() for f in C_LIBRARY["functions"] if f["group"] == g] for g in MODULES
    }


def test_every_talib_python_function_is_there() -> None:
    assert set(talib.get_functions()) <= set(NAMES)
    assert TALIB_PYTHON_NAMES == [n for n in talib.get_functions() if n in set(NAMES)]


@pytest.mark.parametrize("name", TALIB_PYTHON_NAMES)
def test_signature_matches_talib_python(name: str) -> None:
    info = abstract.Function(name).info  # type: ignore[attr-defined]  # absent from talib's stub
    fn = getattr(plta, name.lower())
    params = inspect.signature(fn).parameters

    expected_columns: list[str] = []
    for key, value in info["input_names"].items():
        expected_columns += value if isinstance(value, list) else [key.replace("price", "real")]
    columns = [p for p in params.values() if isinstance(p.default, pl.Expr)]
    assert [c.name for c in columns] == expected_columns
    for c in columns:
        assert c.default.meta.eq(pl.col(DEFAULT_COLUMN.get(c.name, c.name)))

    values = {p.name: p.default for p in params.values() if not isinstance(p.default, pl.Expr)}
    assert values == {**info["parameters"], **CHANGED_SINCE_TALIB_PYTHON.get(name, {})}
    assert all(type(values[k]) is type(v) for k, v in info["parameters"].items())

    outputs = fn.__doc__.rsplit(": ", 1)[1].split(", ")
    assert outputs == info["output_names"]
    assert fn.__doc__.startswith(f"{info['display_name']} ({info['group']})")
