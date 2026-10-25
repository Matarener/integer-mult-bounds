#!/usr/bin/env python3
"""Behavioral CLI, provenance, mutation and Git-free relocation checks."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def run(
    script: Path, args: list[str], cwd: Path, good: bool
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    need((result.returncode == 0) == good, f"unexpected CLI result: {result.stderr}")
    if not good:
        need(not result.stdout, "rejected operation emitted a success payload")
    return result


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def parser_controls(scratch: Path) -> int:
    serializer = HERE / "serialize.py"
    example = json.loads((HERE / "EXAMPLE.json").read_text())
    valid = scratch / "valid.json"
    write(valid, example)
    result = run(serializer, [str(valid)], scratch, True)
    output = json.loads(result.stdout)
    need(
        output["roots"] == 1 and len(output["events"]) == len(example["events"]),
        "honest CLI",
    )
    maximal = {
        "sources": 8,
        "roots": 16,
        "targets": [0] * 255,
        "events": [["B", 0, 15]] * 4096,
    }
    maximum_path = scratch / "maximum-valid.json"
    write(maximum_path, maximal)
    maximum_result = json.loads(
        run(serializer, [str(maximum_path)], scratch, True).stdout
    )
    need(
        maximum_result["roots"] == 1 and len(maximum_result["events"]) == 4096,
        "accepted resource boundary",
    )
    mutants = []
    for key, value in (
        ("sources", True),
        ("sources", 9),
        ("roots", 17),
        ("targets", [True]),
        ("events", [["T", 0, 0]]),
        ("events", [["B", -1, 0]]),
        ("events", [["B", 0, True]]),
        ("events", [["B", 0, 16]]),
        ("events", []),
        ("events", [["B", 0, 0]] * 4097),
    ):
        mutants.append({**example, key: value})
    mutants.append({**example, "free_copy": True})
    mutants.append(
        {
            "sources": 1,
            "roots": 2,
            "targets": [1],
            "events": [["B", 0, 0], ["A", 0, 0], ["B", 0, 0], ["A", 0, 1]],
        }
    )
    for i, mutant in enumerate(mutants):
        path = scratch / f"mutant-{i}.json"
        write(path, mutant)
        run(serializer, [str(path)], scratch, False)
    for i, raw in enumerate(
        ('{"sources":1,"sources":2}', '{"sources":NaN}', "[" * 10000, " " * 1_048_577)
    ):
        path = scratch / f"raw-{i}.json"
        path.write_text(raw)
        run(serializer, [str(path)], scratch, False)
    return len(mutants) + 4


def counterexample_controls(scratch: Path) -> None:
    # Rebinding without grouping produces both sources in both outputs.
    word = {
        "sources": 2,
        "roots": 2,
        "targets": [1, 2],
        "events": [[kind, p, p] for kind in ("B", "A", "B", "A") for p in range(2)],
    }
    path = scratch / "interleaved.json"
    write(path, word)
    run(HERE / "serialize.py", [str(path)], scratch, True)
    word["roots"] = 1
    word["events"] = [[kind, index, 0] for kind, index, _ in word["events"]]
    write(path, word)
    run(HERE / "serialize.py", [str(path)], scratch, False)


def export_controls(scratch: Path) -> None:
    export = scratch / "git-free"
    package = export / "research" / HERE.name
    package.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file() and not path.is_symlink():
            shutil.copyfile(path, package / path.name)
    manifest = json.loads((HERE / "VERIFY.json").read_text())
    for relative in manifest["inputs"]:
        target = export / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    before = {
        str(p.relative_to(export)): p.read_bytes()
        for p in export.rglob("*")
        if p.is_file()
    }
    run(package / "verify.py", [], scratch, True)
    run(package / "independent.py", [], scratch, True)
    after = {
        str(p.relative_to(export)): p.read_bytes()
        for p in export.rglob("*")
        if p.is_file()
    }
    need(before == after, "default replay changed export bytes")
    receipt = package / "RESULT.json"
    data = json.loads(receipt.read_text())
    data["exhaustive"]["accepted"] = True
    write(receipt, data)
    run(package / "verify.py", [], scratch, False)
    receipt.write_bytes(before[str(receipt.relative_to(export))])
    source = export / "research/connector-all-tariff-optimum/README.md"
    source.write_bytes(source.read_bytes() + b"\n")
    run(package / "verify.py", [], scratch, False)


def producer_mutant(scratch: Path) -> None:
    mutant_dir = scratch / "mutant-producer"
    mutant_dir.mkdir()
    source = (HERE / "serialize.py").read_text()
    need(source.count("buckets[port].append") == 1, "producer mutant location")
    mutant = mutant_dir / "serialize.py"
    mutant.write_text(source.replace("buckets[port].append", "buckets[0].append"))
    word = {
        "sources": 2,
        "roots": 2,
        "targets": [1, 2],
        "events": [[kind, p, p] for kind in ("B", "A", "B", "A") for p in range(2)],
    }
    path = scratch / "producer-input.json"
    write(path, word)
    run(mutant, [str(path)], scratch, False)


def main() -> None:
    # In this session TMPDIR is explicitly the owned external output directory.
    with tempfile.TemporaryDirectory(prefix="connector-serialization-") as name:
        scratch = Path(name)
        parser_cases = parser_controls(scratch)
        counterexample_controls(scratch)
        producer_mutant(scratch)
        export_controls(scratch)
    need(not os.path.exists(name), "owned disposable export cleanup")
    print(
        f"PASS_SERIALIZATION_PACKAGE groups=4 parser_rejections={parser_cases} optimized_git_free_readonly"
    )


if __name__ == "__main__":
    main()
