"""Times the plugin on fixed scenarios, for like-for-like comparisons between two builds.

    python tools/bench.py compare --build A=<python A> --build B=<python B> --out results.jsonl

or by hand:

    <python of build A> tools/bench.py run --label A --out results.jsonl
    <python of build B> tools/bench.py run --label B --out results.jsonl
    ... (interleave A B A B, one process at a time, nothing else running)
    python tools/bench.py report results.jsonl

``run`` appends one JSON line per scenario: label, threads (``POLARS_MAX_THREADS``), scenario,
the median of ``--repeats`` timed runs in ms. ``report`` prints, per label, threads and
scenario, the median over the rounds and the spread (min..max) of the round medians.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import polars as pl


@dataclass(frozen=True)
class Timing:
    label: str
    threads: str
    scenario: str
    ms: float


class Scenarios:
    """The frames and the queries timed on them."""

    ROWS = 1_000_000
    SYMBOLS = 2_000
    SMALL = 100
    SEED = 20261025

    def __init__(self) -> None:
        import polars_talib_fast as plta  # noqa: PLC0415  (the build under test)

        self.plta = plta
        self.big = self.frame(self.ROWS)
        per_symbol = self.ROWS // self.SYMBOLS
        self.grouped = self.big.with_columns(
            (pl.int_range(pl.len()) // per_symbol).cast(pl.Int32).alias("symbol")
        )
        self.small = self.frame(self.SMALL)

    def frame(self, rows: int) -> pl.DataFrame:
        rng = np.random.default_rng(self.SEED)
        close = 100.0 + np.cumsum(rng.normal(0.0, 1.0, rows))
        spread = rng.uniform(0.1, 2.0, rows)
        return pl.DataFrame(
            {
                "open": close - rng.uniform(-1.0, 1.0, rows),
                "high": close + spread,
                "low": close - spread,
                "close": close,
                "volume": rng.integers(1_000, 100_000, rows).astype(np.float64),
            }
        )

    def all(self) -> dict[str, Callable[[], object]]:
        p = self.plta
        eight = [
            p.ema(timeperiod=30).alias("ema"),
            p.sma(timeperiod=30).alias("sma"),
            p.rsi().alias("rsi"),
            p.macd().alias("macd"),
            p.bbands().alias("bbands"),
            p.atr().alias("atr"),
            p.adx().alias("adx"),
            p.sar().alias("sar"),
        ]
        return {
            "ema 1M": lambda: self.big.select(p.ema(timeperiod=30)),
            "macd 1M": lambda: self.big.select(p.macd()),
            "atr 1M": lambda: self.big.select(p.atr()),
            "sar 1M": lambda: self.big.select(p.sar()),
            "8 indicators 1M": lambda: self.big.select(eight),
            "ema over 2000 symbols": lambda: self.grouped.select(
                p.ema(timeperiod=30).over("symbol")
            ),
            "ema 100 rows": lambda: self.small.select(p.ema(timeperiod=30)),
        }


class Bench:
    WARMUP = 3

    def __init__(self, label: str, out: Path, repeats: int) -> None:
        self.label = label
        self.out = out
        self.repeats = repeats
        self.threads = os.environ.get("POLARS_MAX_THREADS", "all")

    def time(self, query: Callable[[], object]) -> float:
        for _ in range(self.WARMUP):
            query()
        samples = []
        for _ in range(self.repeats):
            start = time.perf_counter()
            query()
            samples.append((time.perf_counter() - start) * 1000.0)
        return statistics.median(samples)

    def run(self) -> None:
        with self.out.open("a", encoding="utf-8") as f:
            for scenario, query in Scenarios().all().items():
                timing = Timing(self.label, self.threads, scenario, self.time(query))
                f.write(json.dumps(asdict(timing)) + "\n")
                print(f"{timing.label} threads={timing.threads} {scenario}: {timing.ms:.3f} ms")


@dataclass(frozen=True)
class Build:
    label: str
    python: str


class Compare:
    """Runs ``run`` for each build in turn, A B A B, one process at a time, for each thread
    setting, then prints the report. Every process prints its scenarios as it goes."""

    THREADS = ("all", "1")

    def __init__(self, builds: list[Build], out: Path, rounds: int, repeats: int) -> None:
        self.builds = builds
        self.out = out
        self.rounds = rounds
        self.repeats = repeats

    def run(self) -> None:
        import subprocess  # noqa: PLC0415

        for round_ in range(1, self.rounds + 1):
            for threads in self.THREADS:
                for build in self.builds:
                    env = dict(os.environ)
                    env.pop("POLARS_MAX_THREADS", None)
                    if threads != "all":
                        env["POLARS_MAX_THREADS"] = threads
                    stamp = time.strftime("%H:%M:%S")
                    print(f"[{stamp}] round {round_}/{self.rounds} threads={threads} {build.label}")
                    command = [build.python, "-I", __file__, "run", "--label", build.label]
                    command += ["--out", str(self.out), "--repeats", str(self.repeats)]
                    subprocess.run(command, env=env, check=True)
        Report(self.out).print()


class Report:
    def __init__(self, results: Path) -> None:
        lines = results.read_text(encoding="utf-8").splitlines()
        self.timings = [Timing(**json.loads(line)) for line in lines if line.strip()]

    def print(self) -> None:
        keys = sorted({(t.threads, t.scenario) for t in self.timings})
        labels = sorted({t.label for t in self.timings})
        print("| threads | scenario | " + " | ".join(labels) + " |")
        print("|---|---|" + "---:|" * len(labels))
        for threads, scenario in keys:
            cells = []
            for label in labels:
                ms = [
                    t.ms
                    for t in self.timings
                    if (t.label, t.threads, t.scenario) == (label, threads, scenario)
                ]
                cells.append(
                    f"{statistics.median(ms):.3f} ({min(ms):.3f}..{max(ms):.3f}, n={len(ms)})"
                )
            print(f"| {threads} | {scenario} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--label", required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--repeats", type=int, default=15)
    report = sub.add_parser("report")
    report.add_argument("results", type=Path)
    compare = sub.add_parser("compare")
    compare.add_argument("--build", action="append", required=True, help="LABEL=PYTHON")
    compare.add_argument("--out", type=Path, required=True)
    compare.add_argument("--rounds", type=int, default=4)
    compare.add_argument("--repeats", type=int, default=15)
    args = parser.parse_args()
    if args.command == "run":
        Bench(args.label, args.out, args.repeats).run()
    elif args.command == "compare":
        builds = [Build(*b.split("=", 1)) for b in args.build]
        Compare(builds, args.out, args.rounds, args.repeats).run()
    else:
        Report(args.results).print()
    sys.exit(0)
