#!/usr/bin/env python3
"""Admission, corruption, and scanner-agreement checks. No assert statements."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent
import verify


def need(ok, message):
    if not ok:
        raise ValueError(message)


def test_duplicate_key():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dup.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        try:
            verify.read_json(path)
        except ValueError as exc:
            need(str(exc) == "duplicate JSON key", "duplicate message")
        else:
            need(False, "duplicate key accepted")


def test_corrupt_certificate():
    observed = verify.evaluate()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CERTIFICATE.json"
        blob = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        blob["shape_A"] = 1
        path.write_text(json.dumps(blob), encoding="utf-8")
        bad = verify.read_json(path)
        try:
            verify.admit(observed, bad)
        except ValueError as exc:
            need(str(exc) == "certificate mismatch", "corruption message")
        else:
            need(False, "corrupt certificate accepted")
    live = verify.read_json(HERE / "CERTIFICATE.json")
    need(live["shape_A"] == 0, "on-disk certificate mutated")


def test_optimized_admission():
    script = (
        "import sys\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {str(HERE)!r})\n"
        "import verify\n"
        "verify.need(__debug__ is False, 'optimization off')\n"
        "try:\n"
        "    verify.need(False, 'admission')\n"
        "except ValueError as exc:\n"
        "    if str(exc) != 'admission':\n"
        "        raise SystemExit('wrong admission')\n"
        "else:\n"
        "    raise SystemExit('admission skipped')\n"
        "print('PASS_OPTIMIZED_ADMISSION')\n"
    )
    done = subprocess.run(
        [sys.executable, "-O", "-I", "-B", "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    need(done.returncode == 0, "optimized admission failed: " + done.stderr)
    need("PASS_OPTIMIZED_ADMISSION" in done.stdout, "optimized marker")


def test_fake_w_control():
    need(not verify.no_atom_width_parameter("2^(n^2)*q^(w-1)"),
         "fake w accepted")
    need(verify.no_atom_width_parameter("2^(n^2)*prod (2^(2j)-1)"),
         "clean Sp formula rejected")


def test_hash_rejection():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "blob.txt"
        path.write_bytes(b"nope")
        try:
            verify.need(
                hashlib.sha256(path.read_bytes()).hexdigest() == "0" * 64,
                "source hash: temp",
            )
        except ValueError as exc:
            need("source hash" in str(exc), "hash message")
        else:
            need(False, "bad hash accepted")


def test_scanners_agree():
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HERE.iterdir()
        if path.is_file()
    }
    left = verify.evaluate()
    right = independent.evaluate()
    need(left["shape_A"] == right["shape_A"] == 0, "A disagreement")
    need(left["shape_B_bits"] == right["shape_B_bits"] == 2642, "B disagreement")
    need(left["marker"] == right["marker"], "marker disagreement")
    need(left["digit_tower_lift_in_complex_cover"] is False, "tower flag")
    verify.admit(left, verify.read_json(HERE / "CERTIFICATE.json"))
    after = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in HERE.iterdir()
        if path.is_file()
    }
    need(before == after, "package files mutated")


def main():
    test_duplicate_key()
    test_corrupt_certificate()
    test_optimized_admission()
    test_fake_w_control()
    test_hash_rejection()
    test_scanners_agree()
    print("PASS_SELECTED_STOCK_SHAPE_A_ZERO_TESTS groups=6")


if __name__ == "__main__":
    main()
