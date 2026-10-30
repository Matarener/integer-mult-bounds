#!/usr/bin/env python3
"""Four-role SL2(F3) dirty-role conjugate triple; read-only default verify."""
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
    CALL_NAMES,
    C,
    E,
    ELEMENTS,
    EXPECTED_CALLS,
    EXPECTED_IDEM,
    GENERATOR_IDS,
    GROUP_INV,
    GROUP_MUL,
    GROUP_ORDER,
    I2,
    IW,
    KAPPA,
    ROLES,
    TARGET_DIAGONAL,
    W,
    call_name,
    direct_gate,
    formal_matrix_product,
    group_power,
    identity_state,
    make_direct_word,
    need,
    pair_state,
    right_call,
    search_through_four,
    state_digest,
    target_state,
    word_state,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"
PRED_CERT = ROOT / "research/sl2f3-conjugate-triple-seed592f/CERTIFICATE.json"


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
    """On-disk corruption of a temp copy must not match the recomputed cert."""
    with tempfile.TemporaryDirectory() as tmp:
        bad_path = Path(tmp) / "CERTIFICATE.json"
        corrupted = dict(expected)
        corrupted["result_minimum"] = int(expected["result_minimum"]) + 1
        bad_path.write_text(
            json.dumps(corrupted, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        loaded = load_json_reject_duplicates(bad_path)
        need(loaded != expected, "temp corruption must differ from committed receipt")


def generator_word_distance(target: int) -> int:
    frontier = [E]
    seen = {E: 0}
    while frontier:
        g = frontier.pop(0)
        if g == target:
            return seen[g]
        for h in GENERATOR_IDS:
            gh = GROUP_MUL[g][h]
            if gh not in seen:
                seen[gh] = seen[g] + 1
                frontier.append(gh)
    raise RuntimeError("target not generated")


def controls(call_index, direct, target):
    direct_state = word_state(tuple(CALLS[i] for i in direct))
    need(direct_state == target, "direct five-call identity failed")
    for pos in range(len(direct)):
        reduced = direct[:pos] + direct[pos + 1 :]
        need(
            word_state(tuple(CALLS[i] for i in reduced)) != target,
            f"omission control unexpectedly passed at direct position {pos}",
        )
    wrong = list(direct)
    old = CALLS[wrong[-1]]
    wrong[-1] = call_index[(GROUP_INV[old[0]], old[1], old[2])]
    need(
        word_state(tuple(CALLS[i] for i in wrong)) != target,
        "mutated-generator control unexpectedly passed",
    )
    # Dirty role must remain identity after the direct word.
    dirty_diag = target[ROLES * 3 + 3]
    need(dirty_diag == (1 << E), "direct word must restore dirty role to [e]")
    # Positive two-call control on roles 0,1 with dirty+role2 identity.
    positive = target_state((I2, W, E, E))
    positive_word = (call_index[(I2, 1, 1)], call_index[(W, 2, 2)])
    need(
        word_state(tuple(CALLS[i] for i in positive_word)) == positive,
        "two-call positive control failed",
    )
    return positive_word, positive


def build_certificate() -> dict:
    need(len(ELEMENTS) == GROUP_ORDER, "SL2(F3) must have 24 elements")
    need(len(GENERATOR_IDS) == 4 and len(set(GENERATOR_IDS)) == 4, "four distinct generators")
    need(len(CALLS) == EXPECTED_CALLS, f"expected {EXPECTED_CALLS} paid gates")
    need(EXPECTED_IDEM == len(CALLS) // 4, "idempotent count")

    generated = {E}
    frontier = [E]
    while frontier:
        a = frontier.pop()
        for g in GENERATOR_IDS:
            b = GROUP_MUL[a][g]
            if b not in generated:
                generated.add(b)
                frontier.append(b)
    need(len(generated) == GROUP_ORDER, "i and w do not generate all of SL2(F3)")
    need(group_power(I2, 4) == E and group_power(I2, 2) != E, "i must have order four")
    need(group_power(W, 3) == E and W != E, "w must have order three")
    need(group_power(C, 4) == E and group_power(C, 2) != E, "c must have order four")
    need(generator_word_distance(C) == 3, "three-letter word for c is not shortest")

    gates = tuple(right_call(identity_state(), call) for call in CALLS)
    need(
        all(gates[i] == direct_gate(call) for i, call in enumerate(CALLS)),
        "rank-one update and direct gate construction disagree",
    )
    call_index = {call: i for i, call in enumerate(CALLS)}
    call_inverse = tuple(call_index[(GROUP_INV[g], x, y)] for g, x, y in CALLS)
    identity = identity_state()
    for k, gate in enumerate(gates):
        need(
            right_call(gate, CALLS[call_inverse[k]]) == identity,
            f"inverse formula failed for {call_name(CALLS[k])}",
        )

    target = target_state(TARGET_DIAGONAL)
    direct = make_direct_word(call_index)
    positive_word, positive_target = controls(call_index, direct, target)

    pair_words: dict = {}
    cross_checks = 0
    for a, gate in enumerate(gates):
        for b, call in enumerate(CALLS):
            state = right_call(gate, call)
            need(
                state == formal_matrix_product(gate, gates[b]),
                f"rank-one transition disagrees with full convolution at pair ({a},{b})",
            )
            cross_checks += 1
            pair_words.setdefault(state, (a, b))
    need(cross_checks == EXPECTED_CALLS ** 2, "pair cross-check count")

    found = search_through_four(
        target, TARGET_DIAGONAL, gates, pair_words, call_inverse
    )
    if found is None:
        minimum = 5
        witness = direct
    else:
        minimum = len(found)
        witness = found
        need(
            word_state(tuple(CALLS[i] for i in witness)) == target,
            "reported short witness fails full group-algebra replay",
        )
    need(minimum == 5, f"expected exact minimum 5, got {minimum}")
    need(len(witness) == 5, "direct witness length")

    positive_found = search_through_four(
        positive_target, (I2, W, E, E), gates, pair_words, call_inverse
    )
    need(
        positive_found is not None and len(positive_found) == 2,
        "search failed its known two-call positive control",
    )
    need(
        word_state(tuple(CALLS[i] for i in positive_found)) == positive_target,
        "positive control witness incorrect",
    )

    pred = load_json_reject_duplicates(PRED_CERT)
    need(pred.get("result_minimum") == 5, "predecessor three-role minimum pin")
    need(pred.get("paid_call_alphabet") == 112, "predecessor alphabet pin")
    need(pred.get("group_order") == 24, "predecessor group order pin")

    return {
        "schema_version": 1,
        "model": "M4(F2[SL2(F3)])",
        "roles": ROLES,
        "dirty_roles": 1,
        "group_order": GROUP_ORDER,
        "group_generated_by": list(CALL_NAMES[g] for g in GENERATOR_IDS),
        "i_matrix_mod3": [[0, 1], [2, 0]],
        "w_matrix_mod3": [[0, 2], [1, 2]],
        "target_c": "w^-1*i*w",
        "target_diagonal": ["i", "w", "c", "e"],
        "rank_one_idempotents": EXPECTED_IDEM,
        "paid_call_alphabet": EXPECTED_CALLS,
        "direct_paid_bill": 5,
        "search_depth": 4,
        "one_call_states": len(set(gates)),
        "two_call_words": EXPECTED_CALLS ** 2,
        "two_call_distinct_states": len(pair_words),
        "two_call_full_convolution_cross_checks": cross_checks,
        "two_call_state_sha256": state_digest(pair_words),
        "result_minimum": minimum,
        "short_witness_indices": None,
        "short_witness": None,
        "dirty_role_lowers_minimum": False,
        "positive_control_minimum": len(positive_found),
        "direct_word": [call_name(CALLS[i]) for i in direct],
        "omission_controls": len(direct),
        "mutated_generator_control": True,
        "free_scalar_mixing_covered": True,
        "predecessor_three_role_minimum": 5,
        "predecessor_package": "research/sl2f3-conjugate-triple-seed592f",
        "selected_kappa": KAPPA,
        "no_new_kappa": True,
        "limitations": [
            "finite nonabelian address algebra only",
            "address-operation implementation cost not priced",
            "no selected supplier or kappa change claimed",
            "answers predecessor dirty-role OQ only for one restored dirty scalar",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate CERTIFICATE.json (explicit write path only)",
    )
    args = parser.parse_args()

    check_source_pins()
    cert = build_certificate()

    if args.write:
        CERT_PATH.write_text(
            json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    else:
        need(CERT_PATH.is_file(), "missing CERTIFICATE.json; run verify.py --write")
        expected = load_json_reject_duplicates(CERT_PATH)
        need(cert == expected, "recomputed certificate differs from CERTIFICATE.json")
        reject_certificate_corruption(expected)

    print(
        "PASS_SL2F3_DIRTY_ROLE_FOUR "
        f"group={GROUP_ORDER} roles={ROLES} calls={EXPECTED_CALLS} "
        f"idempotents={EXPECTED_IDEM} target_minimum={cert['result_minimum']} "
        f"pair_words={cert['two_call_words']} "
        f"distinct_pair_states={cert['two_call_distinct_states']} "
        f"dirty_lowers=false short_witness=none no_new_kappa"
    )


if __name__ == "__main__":
    main()
