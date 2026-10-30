"""Failure behavior and real optimized CLI controls for the wider row contract."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import minimum
import runtime
import tape_checks
import tape_padding


def rejected(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError("invalid public input accepted")


def arithmetic():
    for values in (
        (True, 1, 2, 1, (0,)),
        (4, 0, 2, 1, (0,)),
        (4, 1, 2, 2, (0, 1)),
        (4, 1, 2, 1, (0, True, 2)),
        (4, 1, 2, 1, (0, 2, 1)),
        (4, 1, 2, 1, (0,)),
        (minimum.MAX_E + 1, 1, 2, 1, (0,)),
    ):
        rejected(lambda values=values: minimum.select(*values))
    minimum.require(
        minimum.select(9, 1, 2, 1, (0, 4, 4, 4)) == (4, 5, 0, 2),
        "tight strict-fit boundary",
    )
    return 7


def failed_return(padded, source, work, mode):
    from records import Tape

    if mode == "raise":
        raise ValueError("callee failure")
    if mode == "alias":
        return padded
    if mode == "source":
        return source
    output = Tape()
    work.append(output)
    bits = bytearray(tape_checks.payload(padded))
    if mode == "dirty":
        bits[-1] = 1
    if mode == "short":
        bits.pop()
    if mode == "long":
        bits.append(0)
    for bit in bits:
        output.append(bit)
    output.rewind()
    if mode == "head":
        output.step(1)
    return output


def row_failures(retained):
    from cardinal_counts import Count
    from records import Tape
    from words import BLANK, LEFT

    source = Tape()
    for bit in (1, 0, 1, 1, 0, 0, 1, 0):
        source.append(bit)
    source.rewind()
    counts = [Count.literal(n) for n in (1, 4, 6, 2)]
    saved = tape_checks.payload(source)
    work = []

    try:
        for mode in ("raise", "alias", "source", "dirty", "short", "long", "head"):
            rejected(
                lambda mode=mode: tape_padding.complete(
                    source,
                    *counts,
                    lambda p, _r: failed_return(p, source, work, mode),
                    retained,
                )
            )
            minimum.require(
                tape_checks.payload(source) == saved and source.head == 1,
                "failure preserves borrowed source",
            )
            minimum.require(
                all(
                    t.cells[0] == LEFT
                    and t.head == 1
                    and all(x == BLANK for x in t.cells[1:])
                    for t in work
                ),
                "failure erases owned returned outputs",
            )
    finally:
        source.clear()
        for count in counts:
            count.close()
    return 7


def capacities(retained):
    from cardinal_counts import Count

    rows, stock = Count.literal(1), Count.literal(2)
    try:
        rejected(lambda: tape_padding.plan_rows(rows, stock, retained))
        rows.multiply_small(2)
        padded, added = tape_padding.plan_rows(rows, rows, retained)
        try:
            minimum.require(
                tape_checks.decode(padded) == 2 and tape_checks.decode(added) == 0,
                "aliased equal borrowed counts",
            )
        finally:
            padded.close()
            added.close()
        stock.close()
        stock = Count.literal(1 << tape_padding.MAX_COUNT_BITS)
        rejected(lambda: tape_padding.plan_rows(rows, stock, retained))
    finally:
        rows.close()
        stock.close()
    return 3


def activation_guard():
    from types import ModuleType

    sentinel = ModuleType("padding")
    minimum.require("padding" not in sys.modules, "clean control namespace")
    sys.modules["padding"] = sentinel
    try:
        try:
            with runtime.installed():
                raise RuntimeError("foreign padding module accepted")
        except ValueError:
            minimum.require(
                sys.modules.get("padding") is sentinel, "preserve foreign module"
            )
    finally:
        del sys.modules["padding"]
    return 1


def mutations(package, root):
    return [
        (package / "RESULT.json", b'"schema_version": 1', b'"schema_version": true'),
        (
            package / "RESULT.json",
            b'"schema_version": 1',
            b'"schema_version": 1, "schema_version": 1',
        ),
        (package / "RESULT.json", b'"newly_fitted": 32', b'"newly_fitted": 31'),
        (package / "minimum.py", b"2 * power > stock", b"2 * power >= stock"),
        (
            package / "tape_padding.py",
            b"compare(stock, twice) < 0",
            b"compare(stock, twice) > 0",
        ),
        (package / "comparison/PR3486-PROOF.md", b"fixed", b"wrong"),
        (
            root / "research/ordinary-one-factor-stock/PROOF.md",
            b"Conditional",
            b"Corrupted",
        ),
    ]


def cli():
    failures = 0
    with TemporaryDirectory(prefix="strict-padding-cli-") as temporary:
        root = Path(temporary)
        package = root / "research/strict-padding-borrowing"
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((HERE / "SOURCES.json").read_text())
        for row in sources["files"]:
            if row["usage"] != "input":
                continue
            target = root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row["path"], target)
        argv = [
            sys.executable,
            "-I",
            "-O",
            "-W",
            "error",
            "-B",
            str(package / "verify.py"),
        ]
        good = subprocess.run(
            argv, cwd=root, capture_output=True, timeout=30, check=False
        )
        minimum.require(
            good.returncode == 0 and b"PASS strict-padding" in good.stdout,
            "real optimized Git-free good CLI",
        )
        for target, before, after in mutations(package, root):
            original = target.read_bytes()
            minimum.require(before in original, "live CLI mutation target")
            try:
                target.write_bytes(original.replace(before, after, 1))
                failed = subprocess.run(
                    argv, cwd=root, capture_output=True, timeout=30, check=False
                )
                minimum.require(failed.returncode != 0, "actual corrupted CLI rejects")
                failures += 1
            finally:
                target.write_bytes(original)
    return failures


def main():
    invalid = arithmetic()
    namespace = activation_guard()
    with runtime.installed() as retained:
        returns = row_failures(retained)
        limits = capacities(retained)
    failures = cli()
    print(
        json.dumps(
            {
                "invalid_arithmetic": invalid,
                "preloaded_padding_rejected": namespace,
                "callee_failures": returns,
                "capacity_alias_boundaries": limits,
                "optimized_cli_faults": failures,
            }
        )
    )


if __name__ == "__main__":
    main()
