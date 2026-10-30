#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Three-role S3 longest Coxeter target; read-only default verify."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from model import (  # noqa: E402
    CALLS,
    CALL_INDEX,
    DIRECT_LEN,
    E,
    ELEMENTS,
    EXPECTED_CALLS,
    EXPECTED_IDEM,
    GROUP_MUL,
    GROUP_ORDER,
    KAPPA,
    ROLES,
    SHORT_DEPTH,
    X,
    XYX,
    Y,
    YXY,
    ball,
    formal_matrix_product,
    identity_state,
    make_direct_word,
    mitm_short_hits,
    need,
    state_digest,
    target_state,
    unpack,
    word_state,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"
PRED_CERT = ROOT / "research/bit-s3-two-target-census-seed36501/CERTIFICATE.json"


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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_source_pins() -> None:
    sources = load_json_reject_duplicates(SOURCES_PATH)
    need(
        sources["base_commit"] == "bb4bccbf42844d2801487450727c2f63e10d1d0f",
        "base_commit pin",
    )
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = ROOT / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256_file(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")


def reject_certificate_corruption(expected: dict) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bad_path = Path(tmp) / "CERTIFICATE.json"
        corrupted = dict(expected)
        corrupted["result_minimum"] = int(expected["result_minimum"]) + 1
        bad_path.write_text(
            json.dumps(corrupted, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        loaded = load_json_reject_duplicates(bad_path)
        need(loaded != expected, "temp corruption must differ from committed receipt")


def controls(direct, target):
    direct_state = word_state(direct)
    need(direct_state == target, "direct six-call identity failed")
    literal = formal_matrix_product(tuple(CALL_INDEX[c] for c in direct))
    need(pack_cells(literal) == target, "literal formal product disagrees with step")
    for pos in range(len(direct)):
        reduced = direct[:pos] + direct[pos + 1 :]
        need(
            word_state(reduced) != target,
            f"omission control unexpectedly passed at direct position {pos}",
        )
    # Mutate last projector column bit.
    g, u, v = direct[-1]
    mutated = list(direct)
    mutated[-1] = (g, u, v ^ 1 if v != 1 else v ^ 2)
    need(mutated[-1] in CALL_INDEX, "mutated call must remain a paid factor")
    need(
        word_state(tuple(mutated)) != target,
        "mutated-projector control unexpectedly passed",
    )
    dirty = unpack(target)[ROLES * 2 + 2]
    need(dirty == (1 << E), "direct word must restore dirty role to [e]")
    # Positive shorter control: single xyx on role 0 only.
    positive_target_cells = [0] * (ROLES * ROLES)
    positive_target_cells[0] = 1 << XYX
    positive_target_cells[ROLES + 1] = 1 << E
    positive_target_cells[2 * ROLES + 2] = 1 << E
    positive = pack_cells(positive_target_cells)
    pos_word = ((X, 1, 1), (Y, 1, 1), (X, 1, 1))
    need(word_state(pos_word) == positive, "three-call positive control failed")
    return pos_word, positive


def pack_cells(cells) -> int:
    state = 0
    for i, cell in enumerate(cells):
        state |= int(cell) << (6 * i)
    return state


def build_certificate() -> dict:
    need(len(ELEMENTS) == GROUP_ORDER, "S3 inventory")
    need(GROUP_MUL[X][X] == E and GROUP_MUL[Y][Y] == E, "transpositions involute")
    need(XYX == YXY and XYX != E, "xyx is the longest Coxeter element")
    need(len(CALLS) == EXPECTED_CALLS, f"expected {EXPECTED_CALLS} paid gates")
    need(EXPECTED_IDEM == len(CALLS) // 2, "idempotent count")

    identity = identity_state()
    target = target_state()
    need(identity != target, "target is not the identity")

    direct = make_direct_word()
    need(len(direct) == DIRECT_LEN, "direct length")
    need(word_state(direct) == target, "direct word must attain the target")

    search = mitm_short_hits(identity, target)
    need(search["hits_i2_t3"] == 0, "MITM i2∩t3 must be empty through length 5")
    need(search["hits_i3_t2"] == 0, "MITM i3∩t2 must be empty through length 5")
    need(search["short_witness"] is None, "no short witness through length 5")
    need(
        search["layers_from_identity"] == [1, 56, 1750, 45396],
        "identity ball layer sizes",
    )
    need(
        search["layers_from_target"] == [1, 56, 1750, 45396],
        "target ball layer sizes",
    )

    pos_word, positive = controls(direct, target)

    # Predecessor two-register certificate pin (live input).
    pred = load_json_reject_duplicates(PRED_CERT)
    need(isinstance(pred, dict) and pred, "predecessor certificate must load")
    pred_text = json.dumps(pred, sort_keys=True)
    need("6" in pred_text, "predecessor certificate must record cost 6")

    fwd_digest = state_digest(set(ball(identity, 2)[0].keys()))

    cert = {
        "schema_version": 1,
        "package": "research/s3-three-role-xyx",
        "group": "S3",
        "group_order": GROUP_ORDER,
        "roles": ROLES,
        "paid_labels": ["x", "y"],
        "idempotents": EXPECTED_IDEM,
        "paid_calls": EXPECTED_CALLS,
        "target": "diag([xyx],[xyx],[e])",
        "direct_length": DIRECT_LEN,
        "short_depth": SHORT_DEPTH,
        "layers_from_identity": search["layers_from_identity"],
        "layers_from_target": search["layers_from_target"],
        "ball_i2": search["ball_i2"],
        "ball_t3": search["ball_t3"],
        "ball_i3": search["ball_i3"],
        "ball_t2": search["ball_t2"],
        "hits_i2_t3": search["hits_i2_t3"],
        "hits_i3_t2": search["hits_i3_t2"],
        "short_witness": None,
        "result_minimum": DIRECT_LEN,
        "dirty_lowers": False,
        "identity_ball2_digest": fwd_digest,
        "positive_control_calls": 3,
        "kappa": KAPPA,
        "no_new_kappa": True,
    }
    # touch positive bindings so controls stay load-bearing
    need(len(pos_word) == 3 and positive != identity, "positive control bindings")
    return cert


def compare_certificate(fresh: dict, committed: dict) -> None:
    for key, value in fresh.items():
        need(key in committed, f"missing committed key {key}")
        need(committed[key] == value, f"certificate drift at {key}: {committed[key]!r} vs {value!r}")
    need(set(committed) == set(fresh), "committed certificate has extra keys")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="Regenerate CERTIFICATE.json (explicit write path only).",
    )
    args = parser.parse_args(argv)

    check_source_pins()
    fresh = build_certificate()

    if args.write:
        CERT_PATH.write_text(
            json.dumps(fresh, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(
            "WROTE_S3_THREE_ROLE_XYX",
            f"minimum={fresh['result_minimum']}",
            f"calls={fresh['paid_calls']}",
            "no_new_kappa",
        )
        return 0

    need(CERT_PATH.is_file(), "missing CERTIFICATE.json")
    committed = load_json_reject_duplicates(CERT_PATH)
    compare_certificate(fresh, committed)
    reject_certificate_corruption(committed)

    print(
        "PASS_S3_THREE_ROLE_XYX",
        f"roles={ROLES}",
        f"calls={EXPECTED_CALLS}",
        f"idempotents={EXPECTED_IDEM}",
        f"target_minimum={DIRECT_LEN}",
        f"layers_i={fresh['layers_from_identity']}",
        f"hits_i2_t3={fresh['hits_i2_t3']}",
        f"hits_i3_t2={fresh['hits_i3_t2']}",
        "dirty_lowers=false",
        "short_witness=none",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
