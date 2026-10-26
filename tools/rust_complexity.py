"""Cyclomatic complexity gate for the Rust sources: every function below 10.

    python tools/rust_complexity.py src tools/c_oracle/src

Reads rust-code-analysis-cli (``cargo install --locked rust-code-analysis-cli``, 0.0.25), which
parses Rust with tree-sitter. lizard is not used: it reads lifetimes (``'_``, ``'static``) as char
literals and silently loses functions. A closure counts into the function that contains it.
A function may stay at 10 or more only with ``// complexity: <reason>`` on the line above it.
Prints every function at or over the limit and the maximum; exits 1 on an unjustified one.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Measured:
    file: Path
    name: str
    line: int
    complexity: int


class RustComplexity:
    LIMIT = 10
    JUSTIFICATION = "// complexity:"

    def __init__(self, roots: list[Path]) -> None:
        self.roots = roots

    def measure(self) -> list[Measured]:
        found: list[Measured] = []
        for root in self.roots:
            for file in sorted(root.rglob("*.rs")):
                found += self._file(file)
        return found

    def _file(self, file: Path) -> list[Measured]:
        result = subprocess.run(
            ["rust-code-analysis-cli", "-m", "-O", "json", "-p", str(file)],
            capture_output=True,
            text=True,
            check=True,
        )
        unit = json.loads(result.stdout.splitlines()[0])
        found: list[Measured] = []
        self._walk(file, unit, found)
        return found

    def _walk(self, file: Path, space: dict[str, Any], found: list[Measured]) -> None:
        for child in space.get("spaces", []):
            if child["kind"] == "function" and child["name"] != "<anonymous>":
                complexity = int(child["metrics"]["cyclomatic"]["sum"])
                found.append(Measured(file, child["name"], child["start_line"], complexity))
            else:
                self._walk(file, child, found)

    def justified(self, m: Measured) -> bool:
        lines = m.file.read_text(encoding="utf-8").splitlines()
        above = lines[m.line - 2].strip() if m.line >= 2 else ""
        return above.startswith(self.JUSTIFICATION)

    def run(self) -> int:
        measured = self.measure()
        if not measured:
            print("FAILED no functions measured")
            return 1
        failing = 0
        for m in sorted(measured, key=lambda m: -m.complexity):
            if m.complexity < self.LIMIT:
                break
            ok = self.justified(m)
            failing += not ok
            mark = "justified" if ok else "FAIL"
            print(f"{mark} {m.file}:{m.line} {m.name} CC {m.complexity}")
        top = max(measured, key=lambda m: m.complexity)
        print(f"{len(measured)} functions, max CC {top.complexity} ({top.name}), {failing} failing")
        return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(RustComplexity([Path(a) for a in sys.argv[1:]]).run())
