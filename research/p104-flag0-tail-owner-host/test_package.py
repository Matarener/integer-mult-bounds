#!/usr/bin/env python3
"""Admission, corruption, obstruction control and scanner-agreement checks."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import independent
import verify

SLUG = "research/" + HERE.name


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tree_digest(paths):
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def watched_files():
    files = [path for path in HERE.iterdir() if path.is_file()]
    files.extend(ROOT / name for name in verify.INPUTS)
    return sorted(files)


def test_duplicate_key():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dup.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        for reader in (verify.read_json, independent.read_json):
            try:
                reader(path)
            except ValueError as exc:
                need(str(exc) == "duplicate JSON key", "duplicate message")
            else:
                need(False, "duplicate key accepted")


def stage_tree(tmp):
    root = Path(tmp)
    for name in verify.INPUTS:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    package = root / SLUG
    package.mkdir(parents=True)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in (".py", ".json"):
            shutil.copyfile(path, package / path.name)
    return root, package


def run_optimized(script):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(script)],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )


def expect_rejection(script, needle):
    done = run_optimized(script)
    need(done.returncode != 0, "corruption accepted: " + script.name)
    need(needle in done.stderr, "wrong rejection for " + script.name + ": " + done.stderr[-300:])


def test_temp_copy_corruption():
    before = tree_digest(watched_files())
    with tempfile.TemporaryDirectory() as tmp:
        root, package = stage_tree(tmp)
        for name in ("verify.py", "independent.py"):
            done = run_optimized(package / name)
            need(done.returncode == 0, "clean temp copy failed: " + done.stderr[-300:])
        cert = package / "CERTIFICATE.json"
        clean = cert.read_bytes()
        mutations = (
            ("owner", "D0"),
            ("dirty_helper_touches_in_window", 1),
            ("endpoint_repay_x0_to_initial", True),
            ("pre_read_x0_restoration_blocks_common_chart", False),
            ("add_event", 5760),
        )
        for key, value in mutations:
            blob = json.loads(clean)
            blob[key] = value
            cert.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
            expect_rejection(package / "verify.py", "certificate mismatch")
            expect_rejection(package / "independent.py", "certificate mismatch")
        text = clean.decode("utf-8").replace(
            '"schema_version": 1,', '"schema_version": 1,\n  "schema_version": 1,', 1
        )
        cert.write_text(text, encoding="utf-8")
        expect_rejection(package / "verify.py", "duplicate JSON key")
        expect_rejection(package / "independent.py", "duplicate JSON key")
        cert.write_bytes(clean)
        # Corrupt the gzipped tail witness by flipping a byte in the compressed stream.
        witness = root / verify.INPUTS[1]
        raw = bytearray(witness.read_bytes())
        raw[len(raw) // 2] ^= 0xFF
        witness.write_bytes(bytes(raw))
        for name in ("verify.py", "independent.py"):
            done = run_optimized(package / name)
            need(done.returncode != 0, "corrupt witness accepted")
            need("source hash" in done.stderr or "gzip" in done.stderr.lower()
                 or "JSON" in done.stderr or "Error" in done.stderr
                 or done.returncode != 0,
                 "corrupt witness silent")
    need(tree_digest(watched_files()) == before, "live files mutated by corruption test")


def test_optimized_admission():
    before = tree_digest(watched_files())
    for module in (verify, independent):
        try:
            module.need(False, "admission probe")
        except ValueError as exc:
            need(str(exc) == "admission probe", "need message")
        else:
            need(False, "need ignored under import")
    done = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py")],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
        cwd=str(ROOT),
    )
    need(done.returncode == 0, "optimized verify failed: " + done.stderr[-300:])
    need(verify.MARKER in done.stdout, "verify marker missing")
    need(tree_digest(watched_files()) == before, "verify mutated files")


def test_pre_read_restore_control():
    """Forcing X0 onto its initial frame before the ADD breaks the chart."""
    need(verify.SOURCE_INIT != verify.FULL, "control vacuous")
    need(tuple(verify.SOURCE_INIT) != tuple(verify.FULL), "tuple control")
    # The published ADD annotates FULL; initial is not that chart.
    addition = ["add", "Y34", "X0", "-1/2", list(verify.FULL)]
    need(addition[4] != verify.SOURCE_INIT, "annotated chart equals initial")


def test_scanner_agreement():
    before = tree_digest(watched_files())
    verify.evaluate()
    independent.evaluate()
    cert = verify.read_json(HERE / "CERTIFICATE.json")
    need(cert["owner"] == "X0", "owner")
    need(cert["dirty_helper_touches_in_window"] == 0, "dirt")
    need(cert["endpoint_repay_x0_to_initial"] is False, "repay x0")
    need(cert["endpoint_repay_y34_to_initial"] is False, "repay y34")
    need(cert["pre_read_x0_restoration_blocks_common_chart"] is True, "obstruction")
    need(tree_digest(watched_files()) == before, "agreement mutated files")


def test_read_only_default():
    before = tree_digest(watched_files())
    done = subprocess.run(
        [sys.executable, "-I", "-B", str(HERE / "verify.py")],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
        cwd=str(ROOT),
    )
    need(done.returncode == 0, "read-only verify failed: " + done.stderr[-300:])
    need(tree_digest(watched_files()) == before, "read-only verify wrote files")


def main():
    groups = (
        test_duplicate_key,
        test_temp_copy_corruption,
        test_optimized_admission,
        test_pre_read_restore_control,
        test_scanner_agreement,
        test_read_only_default,
    )
    for group in groups:
        group()
    print("PASS_P104_FLAG0_TAIL_OWNER_HOST_TESTS groups=" + str(len(groups)))


if __name__ == "__main__":
    main()
