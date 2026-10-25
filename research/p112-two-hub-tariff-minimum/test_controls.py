"""Actual rejecting controls for the two-hub tariff minimum package.

Every group mutates a real input or a real receipt, runs the real command in
a subprocess against an isolated copy, and requires a nonzero exit. The
positive controls re-run the unmodified inputs and require the exact
registered output.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MUTATIONS = 10


def commands(target):
    return (
        ("verify", [sys.executable, "-W", "error", "-B", str(target / "verify.py")]),
        (
            "independent",
            [sys.executable, "-W", "error", "-B", str(target / "independent.py")],
        ),
    )


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv, cwd):
    return subprocess.run(  # noqa: S603
        argv, cwd=cwd, capture_output=True, text=True, check=False, timeout=600
    )


def stage(tmp, name):
    target = Path(tmp) / name
    shutil.copytree(ROOT, target)
    for path in target.rglob("__pycache__"):
        shutil.rmtree(path)
    return target


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def mutations():
    def broken_query(name):
        def apply(target):
            path = target / "predecessor" / "CONFIG.json"
            payload = json.loads(path.read_text())
            payload["queries"][name][1] = 1
            write_json(path, payload)
        return apply

    def swapped_marks(target):
        path = target / "predecessor" / "CONFIG.json"
        payload = json.loads(path.read_text())
        payload["marks"] = [payload["marks"][1], payload["marks"][0]]
        write_json(path, payload)

    def dropped_premise(target):
        path = target / "predecessor" / "CONFIG.json"
        payload = json.loads(path.read_text())
        payload["premises"]["reader"] = payload["premises"]["reader"][:-1]
        write_json(path, payload)

    def broken_functional(target):
        path = target / "predecessor" / "WITNESS.json"
        payload = json.loads(path.read_text())
        payload["functionals"][0] = [1, 0, 0, 1, 0]
        write_json(path, payload)

    def broken_reader(target):
        path = target / "predecessor" / "WITNESS.json"
        payload = json.loads(path.read_text())
        payload["readers"][4] = [1, 0, 1, 0, 0, 0, 0, 0, 0]
        write_json(path, payload)

    def altered_predecessor_bytes(target):
        path = target / "predecessor" / "PROOF.md"
        raw = path.read_bytes()
        path.write_bytes(raw + b"\n<!-- mutated -->\n")

    def understated_minimum(target):
        path = target / "RESULT.json"
        payload = json.loads(path.read_text())
        payload["minimum_charge"] = 42
        write_json(path, payload)

    def hidden_extra_row_unit(target):
        path = target / "RESULT.json"
        payload = json.loads(path.read_text())
        payload["row_minima"][4]["minimum"] = 0
        write_json(path, payload)

    def raised_reader_receipt(target):
        path = target / "RESULT.json"
        payload = json.loads(path.read_text())
        payload["witness_charges"] = [c + 2 for c in payload["witness_charges"]]
        write_json(path, payload)

    return [
        broken_query(0),
        broken_query(4),
        swapped_marks,
        dropped_premise,
        broken_functional,
        broken_reader,
        altered_predecessor_bytes,
        understated_minimum,
        hidden_extra_row_unit,
        raised_reader_receipt,
    ]


def main():
    require(len(mutations()) == MUTATIONS, "mutation count")
    with tempfile.TemporaryDirectory(prefix="two-hub-tariff-") as tmp:
        base = stage(tmp, "base")
        before = digest(base / "RESULT.json")
        for name, argv in commands(base):
            done = run(argv, base)
            require(done.returncode == 0, name + " positive control " + done.stderr)
            require("PASS_TWO_HUB_TARIFF_MINIMUM" in done.stdout, name + " banner")
        require(digest(base / "RESULT.json") == before, "receipt rewritten")
        failures = 0
        for number, mutate in enumerate(mutations(), start=1):
            work = stage(tmp, "mutant-" + str(number))
            mutate(work)
            for name, argv in commands(work):
                done = run(argv, work)
                require(
                    done.returncode != 0,
                    "mutation " + str(number) + " survived " + name,
                )
                failures += 1
        after = run(commands(base)[0][1], base)
        require(after.returncode == 0, "positive control after mutations")
        require(digest(base / "RESULT.json") == before, "receipt rewritten")
    print(
        "PASS_TWO_HUB_TARIFF_MINIMUM_CONTROLS "
        + json.dumps(
            {
                "mutation_groups": MUTATIONS,
                "rejecting_runs": failures,
                "positive_runs": 3,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()