#!/usr/bin/env python3
"""Exact PR2298 §3 operation-count census; read-only default. Wentao Li + AI, Apache-2.0."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from schedule import (  # noqa: E402
    census,
    need,
    one_extra_bit_cases,
    physical_reversal_ok,
    reversal_schedule,
    tensor_map_schedule,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"
SELECTED_KAPPA = "0.001672660197076918"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def check_source_pins():
    sources = load_json_reject_duplicates(SOURCES_PATH)
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = ROOT / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")


def load_physical():
    path = ROOT / "research" / "synthetic-layout-independent" / "physical.py"
    need(path.is_file(), "missing synthetic-layout-independent/physical.py")
    import importlib.util

    spec = importlib.util.spec_from_file_location("physical_pin", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.move_address


def build_certificate():
    data = census(max_d=8, short=3, long=4)
    need(data["all_reversals_within_bound"], "reversal bound failed")
    need(data["all_tensors_within_bound"], "tensor bound failed")
    need(data["pattern_count"] == 510, "2+4+...+256 = 510 patterns for d=1..8")
    # Spot physical correctness on a representative mixed-width sample.
    move_address = load_physical()
    samples = [
        [3, 3],
        [4, 3],
        [3, 4, 3],
        [4, 4, 3, 3],
        [4, 3, 4, 3, 4],
        [3, 4, 3, 4, 3, 4, 3, 4],
    ]
    for widths in samples:
        need(physical_reversal_ok(widths, move_address), f"physical reversal {widths}")
        rev = reversal_schedule(list(widths))
        ten = tensor_map_schedule(list(widths))
        need(rev["exchanges"] == len(widths) // 2, "reversal exchange count")
        need(ten["exchanges"] == 2 * max(len(widths) - 1, 0), "tensor exchange count")
    unit = one_extra_bit_cases()
    need(unit[0]["bit_moves"] == 1 and unit[1]["bit_moves"] == 1, "unit one-extra-bit")
    need(unit[2]["bit_moves"] == 0, "unit equal pair")
    # Bound sharpness: d=8 all-long attains floor(8/2)=4 and 2*7=14.
    sharp = next(r for r in data["rows"] if r["widths"] == [4] * 8)
    need(sharp["reversal_exchanges"] == 4, "sharp reversal at d=8")
    need(sharp["tensor_exchanges"] == 14, "sharp tensor at d=8")
    return {
        "claim": (
            "PR2298 §3 operation counts hold on every mixed adjacent bit-width "
            "pattern at d<=8: reversal exchanges = floor(d/2), tensor-map "
            "exchanges = 2(d-1), each one-extra-bit pair uses exactly one "
            "interchange and one bit_move; equal pairs use one interchange."
        ),
        "kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
        "max_d": data["max_d"],
        "short_width": data["short_width"],
        "long_width": data["long_width"],
        "pattern_count": data["pattern_count"],
        "max_reversal_exchanges": data["max_reversal_exchanges"],
        "max_tensor_exchanges": data["max_tensor_exchanges"],
        "all_reversals_within_bound": True,
        "all_tensors_within_bound": True,
        "unit_one_extra_bit": data["unit_one_extra_bit"],
        "bounds": data["bounds"],
        "physical_samples": samples,
        "sharp_d8": {
            "widths": sharp["widths"],
            "reversal_exchanges": sharp["reversal_exchanges"],
            "tensor_exchanges": sharp["tensor_exchanges"],
        },
        # Compact digest of every row's counts (not full op lists) for receipt size.
        "row_digests": [
            {
                "d": r["d"],
                "widths": r["widths"],
                "rev": [r["reversal_exchanges"], r["reversal_interchanges"], r["reversal_bit_moves"]],
                "ten": [r["tensor_exchanges"], r["tensor_interchanges"], r["tensor_bit_moves"]],
            }
            for r in data["rows"]
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate CERTIFICATE.json")
    args = parser.parse_args(argv)
    check_source_pins()
    cert = build_certificate()
    if args.write:
        CERT_PATH.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE {CERT_PATH}")
    else:
        committed = load_json_reject_duplicates(CERT_PATH)
        need(committed == cert, "CERTIFICATE.json drift; pass --write to regenerate")
    print(
        "PASS_PR2298_SECTION3_OPCOUNTS "
        f"patterns={cert['pattern_count']} max_d={cert['max_d']} "
        f"rev_bound=floor(d/2) tensor_bound=2(d-1) "
        f"one_extra_bit=1+1 sharp_d8_rev={cert['sharp_d8']['reversal_exchanges']} "
        f"sharp_d8_tensor={cert['sharp_d8']['tensor_exchanges']} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as err:
        print(f"FAIL: {err}", file=sys.stderr)
        raise SystemExit(1)
