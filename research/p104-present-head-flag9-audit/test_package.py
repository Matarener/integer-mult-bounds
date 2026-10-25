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
        blob["basis_head_drop_event"] = 0
        path.write_text(json.dumps(blob), encoding="utf-8")
        bad = verify.read_json(path)
        try:
            verify.admit(observed, bad)
        except ValueError as exc:
            need(str(exc) == "certificate mismatch", "corruption message")
        else:
            need(False, "corrupt certificate accepted")
    live = verify.read_json(HERE / "CERTIFICATE.json")
    need(live["basis_head_drop_event"] == 500, "on-disk certificate mutated")
    need(live["basis_head_arrive_event"] == 3489, "arrive field mutated")


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


def test_sample_drop_and_arrive():
    drop = ["transport", "X4", [196], [8, 64, 132, 260], 2]
    frames = verify.annotated_frames(drop, "X4")
    need(frames[0] == ("before", [196]), "sample before")
    need(frames[1] == ("after", [8, 64, 132, 260]), "sample after")
    need(196 not in frames[1][1], "sample drop")
    arrive = [
        "transport",
        "Y23",
        [447, 127, 192],
        [467, 27, 196, 12, 124, 3, 7, 1],
        2,
    ]
    arrive_frames = verify.annotated_frames(arrive, "Y23")
    need(196 not in arrive_frames[0][1], "sample arrive before")
    need(196 in arrive_frames[1][1], "sample arrive after")
    folded = independent.frame_set([8, 64, 132, 260])
    need(196 not in folded and folded == frozenset((8, 64, 132, 260)), "sample set")


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
    need(left == right, "scanner disagreement")
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
    test_sample_drop_and_arrive()
    test_hash_rejection()
    test_scanners_agree()
    print("PASS_P104_PRESENT_HEAD_FLAG9_TESTS groups=6")


if __name__ == "__main__":
    main()
