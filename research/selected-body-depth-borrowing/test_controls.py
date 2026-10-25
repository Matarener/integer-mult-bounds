"""Behavioral and actual optimized-CLI controls. Nick Petalas. Apache-2.0."""

import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import astuple
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from borrowing import MAX_E, ceil_log, depth, select, selected_digits  # noqa: E402
from verify import INPUTS, PROFILES  # noqa: E402


def require(condition, message):
    if not condition:
        raise ValueError(message)


def literal_depth(n, m, r):
    for d in range(256):
        if n < m:
            return d
        n = n // m * r
    raise ValueError("tiny oracle depth capacity")


def brute(e, w, m, r, q, b, compatibility):
    for k in range(min((e - 1) // 2, e - m * w) + 1):
        n, remainder = divmod(e - k, w)
        d = literal_depth(n, m, r)
        stock = compatibility * b**d if d else 1
        if q**k >= stock:
            padded = ((q**k + stock - 1) // stock) * stock
            require(q**k <= padded < 2 * q**k, "complete padding range")
            rows = padded
            for _ in range(d):
                require(rows % b == 0, "every actual fresh quotient is integral")
                rows //= b
                require(rows > 0 and rows % compatibility == 0, "every local Q guard")
            return [k, n, remainder, d, ceil_log(q, stock)]
    return None


def brute_controls():
    count = 0
    for m, r, q, b, compatibility in PROFILES:
        for e in range(1, 257):
            for w in range(1, 5):
                maximum = depth(e // w, m, r)
                digits = (
                    0,
                    *(ceil_log(q, compatibility * b**d) for d in range(1, maximum + 1)),
                )
                observed = select(e, w, m, r, digits)
                actual = None if observed is None else list(astuple(observed))
                require(actual == brute(e, w, m, r, q, b, compatibility), "least borrowing")
                count += 1
    return count


def capacity_controls():
    digits = selected_digits(2, depth(MAX_E // 2, 64, 42))
    require(select(MAX_E, 2, 64, 42, digits) is not None, "largest original width")
    digits = selected_digits(32, depth(1048576 // 32, 64, 42))
    require(select(1048576, 32, 64, 42, digits) is None, "largest atom width, no fit")
    invalid = (
        (0, 1, 2, 1, (0,)),
        (MAX_E + 1, 1, 2, 1, (0,)),
        (20, 33, 2, 1, (0,)),
        (20, 1, 2, 2, (0,)),
        (4, 1, 2, 1, (0, 3)),
        (4, 1, 2, 1, (0, 4, 3)),
        (4, 1, 2, 1, (0, True, 3)),
        (4, 1, 2, 1, (0, 1, 1 << 23)),
    )
    for args in invalid:
        try:
            select(*args)
        except ValueError:
            continue
        raise ValueError("invalid boundary accepted")
    try:
        selected_digits(2, 129)
    except ValueError:
        return len(invalid) + 1
    raise ValueError("selected depth capacity accepted")


def exported_fixture(root):
    destination = root / "research" / PACKAGE.name
    shutil.copytree(PACKAGE, destination)
    for name in INPUTS:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE.parent.parent / name, target)
    return destination


def cli(package, accepted):
    completed = subprocess.run(
        [sys.executable, "-I", "-O", "-W", "error", "-B", str(package / "verify.py")],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    passed = completed.returncode == 0 and completed.stdout.startswith("PASS_BODY_DEPTH_BORROWING ")
    require(passed == accepted, "actual optimized verifier status")
    if not accepted:
        require(completed.returncode != 0, "malformed producer exits unsuccessfully")


def cli_controls():
    with tempfile.TemporaryDirectory(prefix="body-depth-controls-") as temporary:
        package = exported_fixture(Path(temporary))
        cli(package, True)
        receipt = package / "RESULT.json"
        original = receipt.read_text()
        for mutated in (
            original.replace('"cases": 8192', '"cases": true'),
            original.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
            original.replace("122882", "122881"),
        ):
            require(mutated != original, "receipt control is active")
            receipt.write_text(mutated)
            cli(package, False)
        receipt.write_text(original)
        source = Path(temporary) / INPUTS[0]
        original_source = source.read_bytes()
        source.write_bytes(original_source + b"\nchanged\n")
        cli(package, False)
        source.unlink()
        cli(package, False)
        source.write_bytes(original_source)
        solver = package / "borrowing.py"
        original_solver = solver.read_text()
        for before, after in (
            ("middle >= digits[", "middle > digits["),
            ("depth((e - middle) // width, dimension, rank)", "depth(e // width, dimension, rank)"),
        ):
            require(before in original_solver, "arithmetic control is active")
            solver.write_text(original_solver.replace(before, after))
            cli(package, False)
        solver.write_text(original_solver)
        cli(package, True)
    return {"accepted": 2, "rejected": 7}


def main():
    result = {
        "brute_and_padded_guard_cases": brute_controls(),
        "capacity_rejections": capacity_controls(),
        "optimized_cli": cli_controls(),
    }
    print("PASS_BODY_DEPTH_CONTROLS " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
