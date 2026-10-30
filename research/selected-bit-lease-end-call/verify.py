#!/usr/bin/env python3
"""Read-only verifier for PR2809 lease-end / CALL-cut audit.

Uses need() so admission survives python -O. Rejects duplicate JSON keys
and compares the on-disk certificate without rewriting it.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_BIT_LEASE_END_CALL "
    "stale_clear_preserves_borrower "
    "call_requires_empty_pool "
    "three_mutants "
    "no_new_kappa"
)
KAPPA_DECIMAL = "0.001672660197076918"
INPUTS = (
    "research/selected-bit-physical-caller/scratch_pool.py",
    "research/selected-bit-physical-caller/macro_machine.py",
    "research/selected-bit-physical-caller/PROOF.md",
    "docs/research/selected-bit-physical-contract-map.md",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def load_independent():
    spec = importlib.util.spec_from_file_location(
        "selected_bit_lease_end_independent", HERE / "independent.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
         "base pin")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(len(raw) <= 4_000_000, "source size")
        need(hashlib.sha256(raw).hexdigest() == row["sha256"],
             "source hash: " + row["path"])
        need(
            hashlib.sha1(
                b"blob " + str(len(raw)).encode() + b"\0" + raw
            ).hexdigest()
            == row["git_blob"],
            "git blob: " + row["path"],
        )
    selected = read_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == KAPPA_DECIMAL, "selected decimal")
    return selected


def admit(observed, certificate):
    need(certificate.get("status") == observed["status"], "certificate mismatch")
    need(certificate.get("marker") == observed["marker"], "certificate mismatch")
    need(certificate.get("kappa_decimal") == KAPPA_DECIMAL, "certificate mismatch")
    need(certificate.get("no_new_kappa") is True, "certificate mismatch")
    need(certificate.get("stale_clear_preserves_borrower") is True,
         "certificate mismatch")
    need(certificate.get("call_requires_empty_pool") is True,
         "certificate mismatch")
    need(certificate.get("mutants") == observed["mutants"], "certificate mismatch")
    need(certificate.get("source_correspondence") == observed["source_correspondence"],
         "certificate mismatch")


def evaluate():
    pin_sources()
    other = load_independent()
    report = other.evaluate()
    need(report["marker"] == MARKER, "marker")
    need(report["kappa_decimal"] == KAPPA_DECIMAL, "kappa")
    need(report["stale_clear_preserves_borrower"] is True, "borrower")
    need(report["call_requires_empty_pool"] is True, "call cut")
    need(len(report["mutants"]) == 3, "three mutants")
    need(all(report["mutants"].values()), "mutant flags")
    return report


def main():
    observed = evaluate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    admit(observed, certificate)
    print(observed["marker"])


if __name__ == "__main__":
    main()
