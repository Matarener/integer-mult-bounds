#!/usr/bin/env python3
"""Mathematical failure controls and optimized CLI mutation checks.

@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mixed_primary", HERE / "verify.py")
primary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(primary)


def require(value, message):
    if not value:
        raise ValueError(message)


def rejects(call, expected):
    try:
        call()
    except ValueError as error:
        require(expected in str(error), f"wrong rejection: {error}")
    else:
        raise ValueError("negative control accepted: " + expected)


def mathematical_controls(labels, groups):
    bad_groups = [g[:] for g in groups]
    bad_groups[1][0] = bad_groups[0][0]
    rejects(lambda: primary.validate_geometry(labels, bad_groups), "partition")
    bad_labels = labels[:]
    bad_labels[groups[0][0]] ^= 1
    rejects(lambda: primary.validate_geometry(bad_labels, groups), "orthonormal")

    ga, gb = groups[0], groups[1]
    planes = [g[j:j+2] for g in (ga, gb) for j in range(0, len(g), 2)]
    dense = primary.costs(labels, ga+gb, planes)
    full = len(dense)-1
    require(dense[full] < len(ga)+len(gb) <= 2*dense[full],
            "omitting second dense layer must create a false bargain")

    # The first dense query alone cannot give the a row: 2*(a+b) != a.
    directions = [(1, 1), (1, 2)]
    correct = tuple(2*directions[0][j]-directions[1][j] for j in range(2))
    omitted = tuple(2*directions[0][j] for j in range(2))
    require(correct == (1, 0) and omitted != (1, 0), "omitted dense query")

    # A plane reader costs two; counting only the target half costs one.
    closed = primary.costs(labels, ga, [ga[:2]])[1]
    half = primary.costs(labels, ga, [[ga[0]]])[1]
    require(closed == 2 and half == 1, "complete-plane closure is material")

    # Source self-cost does not lower-bound the actual rectangular term cost.
    actual = primary.costs(labels, ga+gb, [ga[:2]])[1]
    self_cost = dense[full]
    require(actual == 2 and actual < self_cost, "actual versus self cost distinction")

    # Same-group boundary: all dense and literal-axis realizations each cost 2m.
    for i, group in enumerate(groups):
        for state in (0, 3**len(group)-1):
            invoice = primary.check_operator(labels, groups, i, i, state, parity=(0, 1))
            require(sum(invoice) == 2*len(group), "same-group attainment")
    return 7


def cli_controls():
    with tempfile.TemporaryDirectory(prefix="mixed-reader-controls-") as work:
        root = Path(work)
        package = root / "research" / HERE.name
        package.mkdir(parents=True)
        for source in HERE.iterdir():
            if source.is_file():
                shutil.copyfile(source, package / source.name)
        live = root / primary.INPUT
        live.parent.mkdir(parents=True)
        shutil.copyfile(primary.ROOT / primary.INPUT, live)
        command = [sys.executable, "-I", "-OO", "-B", str(package / "verify.py"), "--root", str(root)]
        def run(expected=None):
            result = subprocess.run(command, text=True, capture_output=True, timeout=60)
            if expected is None:
                require(result.returncode == 0 and "PASS_MIXED_QUERY_READER_FLOOR" in result.stdout,
                        "restored optimized positive replay: " + result.stderr)
            else:
                require(result.returncode != 0 and expected in result.stderr,
                        "CLI corruption was not rejected: " + str(expected))
        original = live.read_bytes()
        live.write_bytes(original+b" ")
        run("source SHA256 mismatch")
        live.write_bytes(original)

        retained = package / "RETAINED-RANK32.json"
        original = retained.read_bytes()
        retained.write_bytes(original.replace(b"28", b"29", 1))
        run("source SHA256 mismatch")
        retained.write_bytes(original)

        receipt = package / "RESULT.json"
        original = receipt.read_bytes()
        mutant = json.loads(original)
        mutant["pairs"][0]["minimum"] -= 1
        receipt.write_text(json.dumps(mutant))
        run("complete receipt mismatch")
        receipt.write_bytes(original)
        run()
    return 3


def main():
    labels, groups = primary.load()
    mathematical = mathematical_controls(labels, groups)
    cli = cli_controls()
    print(f"PASS_MIXED_QUERY_CONTROLS math_groups={mathematical} cli_corruptions={cli} "
          "same_group_operators=32 restored_optimized_positive=1")


if __name__ == "__main__":
    main()
