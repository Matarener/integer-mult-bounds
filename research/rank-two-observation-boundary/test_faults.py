#!/usr/bin/env python3
"""Reject real faults in private package copies; never mutate the checkout.

@CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def faults():
    return (
        ("RESULT.json", '"update_rank": 2', '"update_rank": 1', "committed RESULT"),
        ("RESULT.json", '"partial": 10', '"partial": 9', "committed RESULT"),
        ("RESULT.json", '"completed_rank_two_chains": 3',
         '"completed_rank_two_chains": 4', "committed RESULT"),
        ("model.py", "PARTIAL_WORD = ((), (), ((2, 3),), ((3, 2),), ())",
         "PARTIAL_WORD = ((), (), ((2, 3),), (), ())", "positive coefficient word"),
        ("model.py", "PARTIAL_MASKS = (3, 2, 3, 3)",
         "PARTIAL_MASKS = (3, 3, 3, 3)", "positive coefficient word"),
        ("model.py", "CHILDREN = ((0, 1, 0), (0, 0, 0), (0, 0, 0), (1, 0, 1))",
         "CHILDREN = ((0, 1, 0), (0, 0, 0), (0, 0, 0), (1, 1, 1))",
         "independent final updates"),
        ("model.py", "PARTIAL_WORD = ((), (), ((2, 3),), ((3, 2),), ())",
         "PARTIAL_WORD = (((2, 0),), (), ((2, 3),), ((3, 2),), ())", "alphabet"),
    )


def run(copy, optimized, expected=None, extra=()):
    args = [sys.executable, "-I", "-W", "error", "-B"]
    if optimized:
        args.append("-O")
    result = subprocess.run([*args, str(copy / "verify.py"), *extra],
                            cwd=copy.parent.parent.parent, capture_output=True,
                            text=True, timeout=30, check=False)
    if expected is None:
        require(result.returncode == 0 and "PASS_RANK_TWO" in result.stdout,
                "private-copy positive control")
    else:
        require(result.returncode != 0 and expected in result.stderr,
                "fault not rejected for the expected reason: " + expected)


def main():
    require(not sys.argv[1:], "no fault-test arguments")
    sources = json.loads((HERE / "SOURCES.json").read_text())
    original = snapshot(HERE)
    cases = 0
    with tempfile.TemporaryDirectory(prefix="rank-two-boundary-faults-") as temp:
        root = Path(temp)
        copy = root / "research" / HERE.name
        shutil.copytree(HERE, copy)
        for row in sources["files"]:
            if row["usage"] == "input":
                dest = root / row["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], dest)
        for optimized in (False, True):
            before = snapshot(root)
            run(copy, optimized)
            require(snapshot(root) == before, "verification must be read-only")
            for filename, old, new, expected in faults():
                target = copy / filename
                saved = target.read_text()
                require(saved.count(old) == 1, "unique fault injection")
                target.write_text(saved.replace(old, new), encoding="utf-8")
                run(copy, optimized, expected)
                target.write_text(saved, encoding="utf-8")
                cases += 1
            source = root / "research/four-call-productive-observations/README.md"
            saved = source.read_bytes()
            source.write_bytes(saved + b"\ncorrupted source\n")
            run(copy, optimized, "source pin")
            source.write_bytes(saved)
            run(copy, optimized, "FileExistsError", ("--write-result", str(copy / "RESULT.json")))
            require(snapshot(root) == before, "controls must restore private copies")
            cases += 2
    require(snapshot(HERE) == original, "original package changed")
    print(f"PASS_RANK_TWO_BOUNDARY_FAULTS rejected={cases} modes=normal,optimized")


if __name__ == "__main__":
    main()
