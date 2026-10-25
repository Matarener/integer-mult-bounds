#!/usr/bin/env python3
"""Admission, corruption, and scanner-agreement checks. No assert statements."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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
        blob["theorem"]["all_need_plus_two"] = False
        blob["theorem"]["counterexample"] = {"entry": [23, 4]}
        path.write_text(json.dumps(blob), encoding="utf-8")
        bad = verify.read_json(path)
        try:
            verify.admit(observed, bad)
        except ValueError as exc:
            need(str(exc) == "certificate mismatch", "corruption message")
        else:
            need(False, "corrupt certificate accepted")
    live = verify.read_json(HERE / "CERTIFICATE.json")
    need(live["theorem"]["all_need_plus_two"] is True, "on-disk certificate mutated")
    need(live["theorem"]["counterexample"] is None, "counterexample field mutated")
    need(live["theorem"]["checked_entries"] == 144, "entry count mutated")


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


def test_hash_rejection():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pkg = root / "research/p104-present-head-side-correction-full-row-census"
        pkg.mkdir(parents=True)
        for name in (
            "CERTIFICATE.json",
            "SOURCES.json",
            "verify.py",
            "independent.py",
        ):
            target = pkg / name
            if name.endswith(".py"):
                target.write_text((HERE / name).read_text(encoding="utf-8"), encoding="utf-8")
            else:
                target.write_bytes((HERE / name).read_bytes())
        native = root / "research/p104-native-channel/inputs"
        native.mkdir(parents=True)
        flags = root / "research/p104-joint-unit-flags"
        flags.mkdir(parents=True)
        mapping = {
            "research/p104-joint-unit-flags/CERTIFICATE.json": flags / "CERTIFICATE.json",
            "research/p104-native-channel/inputs/LOWRANK-WITNESS.json": native
            / "LOWRANK-WITNESS.json",
            "research/p104-native-channel/inputs/P104-FIXTURE.json": native
            / "P104-FIXTURE.json",
        }
        for rel, dest in mapping.items():
            dest.write_bytes((ROOT / rel).read_bytes())
        # Corrupt one pin target in the temp tree.
        bad = native / "LOWRANK-WITNESS.json"
        bad.write_bytes(bad.read_bytes() + b"\n")
        try:
            independent.main(root)
        except ValueError as exc:
            need(str(exc).startswith("pin:"), "pin rejection message")
        else:
            need(False, "corrupt pin accepted")


def test_scanner_agreement():
    observed = verify.evaluate()
    certificate = verify.read_json(HERE / "CERTIFICATE.json")
    verify.admit(observed, certificate)
    need(len(certificate["entries"]) == 144, "full-row entry count")
    need(certificate["theorem"]["pr3614_sample_entries_covered"] == 18, "sample cover")
    primaries = [
        row
        for row in certificate["entries"]
        if row["is_primary_present_head_entry"]
    ]
    need(len(primaries) == 3, "three primaries")
    expect = {
        1: ("X7", 387, 19),
        9: ("X58", 333, 25),
        43: ("X12", 131, 28),
    }
    for row in primaries:
        feeder = row["forcing"]["selected_feeder"]
        want = expect[row["flag_index"]]
        need(
            (feeder["from_register"], feeder["head"], row["insertion_classes"]) == want,
            f"primary {row['flag_index']}",
        )
    per_row = certificate["per_row"]
    for flag, target in (("1", 7), ("9", 23), ("43", 59)):
        need(per_row[flag]["target"] == target, f"row target {flag}")
        need(per_row[flag]["off_diagonal_nonzero_sources"] == 48, f"row size {flag}")
    sample = independent.frame_set([1, 2, 4])
    need(0 in sample and 7 in sample and 8 not in sample, "sample closure")
    need(len(sample) == 8, "sample dimension")


def test_sources_pins():
    manifest = verify.read_json(HERE / "SOURCES.json")
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], row["path"])


def main():
    test_duplicate_key()
    test_corrupt_certificate()
    test_optimized_admission()
    test_hash_rejection()
    test_scanner_agreement()
    test_sources_pins()
    print("PASS_P104_PRESENT_HEAD_SIDE_CORRECTION_FULL_ROW_CENSUS_TESTS groups=6")


if __name__ == "__main__":
    main()
