"""Behavioral controls for the actual verifier CLI. Nick Petalas. Apache-2.0."""

import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = Path("research/adaptive-kernel-demotion/inputs/DATA-PHASES.json")


def need(value, message):
    if not value:
        raise ValueError(message)


def cli(package, expected, fragment="PASS_FOUR_TERM_PAIR"):
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")],
        cwd=package.parents[1],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    output = result.stdout + result.stderr
    need((result.returncode == 0) == expected, "actual optimized CLI exit")
    need(fragment in output, "actual optimized CLI diagnostic: " + fragment)


def local_controls():
    module = runpy.run_path(str(HERE / "verify.py"))
    solve, mul = module["solve"], module["mul"]
    need(
        solve([[1, 1], [1, -1]], [1, 0], 2) == [module["F"](1, 2)] * 2,
        "rational half solution",
    )
    need(solve([[1], [1]], [0, 1], 1) is None, "inconsistent source request")
    need(solve([[]], [1], 0, True) is None, "empty active reader")
    need(
        all(any(mul(a, b) == 1 for b in range(1, 16)) for a in range(1, 16)),
        "all GF16 inverses",
    )
    try:
        solve([[0] * 7], [0], 7)
    except ValueError as error:
        need("linear capacity" in str(error), "capacity diagnostic")
    else:
        raise ValueError("linear capacity accepted")
    need(module["degenerate_checks"]() == 256, "zero/parallel/rank-two requests")


def fault_controls():
    need(os.environ.get("TMPDIR"), "set a private external TMPDIR for controls")
    with tempfile.TemporaryDirectory(prefix="four-term-controls-") as tmp:
        root = Path(tmp)
        package = root / "research" / HERE.name
        shutil.copytree(
            HERE, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
        )
        target = root / INPUT
        target.parent.mkdir(parents=True)
        shutil.copyfile(HERE.parents[1] / INPUT, target)
        cli(package, True)
        faults = [
            (
                package / "TEMPLATES.json",
                b'"field_polynomial": 19',
                b'"field_polynomial": 17',
                "template polynomial",
            ),
            (
                package / "RESULT.json",
                b'"rational_configurations": 330',
                b'"rational_configurations": 331',
                "result receipt",
            ),
            (
                package / "RETAINED-RANK32.json",
                b'"schema_version": 1',
                b'"schema_version": 2',
                "source SHA256",
            ),
            (target, b'"port":0,', b'"port":999,', "source SHA256"),
            (
                package / "verify.py",
                b"actual = sum(u[i][p] * q[i][r] for i in range(4))",
                b"actual = sum(u[i][p] * q[i][r] for i in range(3))",
                "exact pair operator",
            ),
            (
                package / "verify.py",
                b"return rank(rows, len(t))",
                b"return 0",
                "original terms attain floor",
            ),
        ]
        for path, before, after, diagnostic in faults:
            original = path.read_bytes()
            need(original.count(before) == 1, "unique actual fault site: " + str(path))
            path.write_bytes(original.replace(before, after))
            cli(package, False, diagnostic)
            path.write_bytes(original)
        cli(package, True)
    return len(faults)


def main():
    local_controls()
    faults = fault_controls()
    print(
        "PASS_FOUR_TERM_CONTROLS",
        json.dumps(
            {"cli_faults": faults, "optimized_positive_replays": 2, "groups": 6},
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
