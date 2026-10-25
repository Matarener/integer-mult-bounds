#!/usr/bin/env python3
"""Small exact derivation witness; full-word semantics is a separate check.

New derivation: OpenAI Codex GPT-6.1 Sol, 2026-10-19. Apache-2.0.
Source words: Rohan Arun PR4076; predecessor sharing question: PR4096.
The credited frozen frame accountant is used only for the paid invoice.
"""
from argparse import ArgumentParser
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import json
import types


PINS = {
    "inputs/NEW-base.json.gz": "8159c67d29ab58efe546ebc4ce20872421996cc71b5f17737ff8b36cbc76d148",
    "inputs/NEW-extra.json.gz": "0147e6b30ef328e227e89113323eb0d02d116e125b0e7c99a00ea4f2652dcc80",
    "vendor/audit_core.py": "888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951",
}
E = [76, 45]
F = [144, 75, 42, 7]
PAIR = {608, 609}
LOCAL = [608, 609, 610, 612, 410, 417, 419, 421]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(d, s, n, den=1, frame=F):
    return ["add", d, s, n, den, list(frame)]


OLD = [
    add(610, 608, -1), add(608, 410, -1), add(610, 609, -1),
    add(609, 410, -1), add(610, 410, 1), add(608, 417, 1),
    add(609, 417, -1), add(612, 417, -1), add(608, 419, 1),
    add(610, 419, -1), add(612, 419, -1), add(609, 421, -1),
    add(610, 421, 1), add(612, 421, -1),
]
CHARTED = [
    add(610, 608, -1), add(608, 410, -2), add(609, 410, -1),
    add(610, 410, 1), add(609, 417, -1), add(612, 417, -1),
    add(608, 419, 1), add(610, 419, -1), add(612, 419, -1),
    add(608, 421, -1), add(609, 421, -1), add(610, 421, 1),
    add(612, 421, -1),
]
ENTER = add(608, 609, 1, frame=E)
EXIT = add(608, 609, -1)
LEGAL = [ENTER] + CHARTED + [EXIT]


def local_rows(seq):
    rows = {r: {s: Q(r == s) for s in LOCAL} for r in LOCAL}
    for op, d, s, n, den, _ in seq:
        need(op == "add" and d != s, "local primitive")
        rows[d] = {k: rows[d][k] + Q(n, den) * rows[s][k] for k in LOCAL}
    return rows


def inverse(seq):
    return [[op, d, s, -n, den, fr] for op, d, s, n, den, fr in reversed(seq)]


def nonzero_rows(rows):
    return {str(r): {str(s): str(q) for s, q in row.items() if q}
            for r, row in rows.items()}


def conj_s(g):
    """S g S^-1 for S:(x,y)->(x+y,y), on every actual scalar gate."""
    if g[0] != "add":
        need(g[0] == "scale" and g[1] not in PAIR, "source pair scale needs its own rule")
        return [list(g)]
    _, d, s, n, den, fr = g
    need(not (d in PAIR and s in PAIR), "source pair-pair gate needs its own rule")
    if d == 609:
        return [add(608, s, n, den, fr), list(g)]
    if s == 608:
        return [list(g), add(d, 609, -n, den, fr)]
    return [list(g)]


def persistent_s(w, core):
    z = deepcopy(w)
    z["B"] = []
    at = {}
    for p, g in enumerate(w["B"]):
        at[p] = len(z["B"])
        if p == 948:
            z["B"].append(ENTER)
        z["B"] += conj_s(g) if p >= 948 else [g]
    at[len(w["B"])] = len(z["B"])
    for rec in z["warps"]:
        rec[0] = at[rec[0]]
    need(not any(g[1] in PAIR or (g[0] == "add" and g[2] in PAIR)
                 for g in w["restore"]), "new pair restore source")
    need(not any(r[1] in PAIR for r in w["warps"]), "native warp on pair")
    z["cleanup"] = core.derive_cleanup(z)
    return z, at


def run_provider(w, core):
    need(w["B"][948:962] == OLD, "complete 14-gate source preimage")
    need(not any(948 < rec[0] < 962 for rec in w["warps"]), "native operation inside block")
    need([k for k, rec in enumerate(w["warps"], 1) if rec[0] == 948] == [33, 34, 35, 36], "four source-native cut")
    need(w["start_extra"]["608"] == w["start_extra"]["609"] == [97, 45], "pair entrance")
    need(not any(str(r) in w["helper_final"] for r in PAIR), "pair is a restored-buffer helper")
    need(core.span(E) == core.span([97, 45]), "equivalent rank-two entrance basis")
    before = core.frame_bill(w, lagrangian=True)
    z = deepcopy(w)
    z["B"][948:962] = LEGAL
    for rec in z["warps"]:
        if rec[0] >= 962:
            rec[0] += 1
    z["cleanup"] = core.derive_cleanup(z)
    after = core.frame_bill(z, lagrangian=True)
    need(before[:2] == after[:2] and before[3:] == after[3:], "complete invoice or endpoint inputs changed")
    paid = lambda chains: {r: [(d, m) for _, d, m in chain if d == "warp" or d > 0]
                            for r, chain in chains.items()}
    need(paid(before[2]) == paid(after[2]), "ordered paid chains changed")
    need(len(z["cleanup"]) == len(w["cleanup"]) + 1, "inverse count")
    need(local_rows(LEGAL) == local_rows(OLD), "full arbitrary-current-state local identity")
    need(local_rows(LEGAL + inverse(LEGAL)) == local_rows([]), "reverse-inverse identity")
    bad = deepcopy(LEGAL)
    bad[-1][3] = 1
    need(local_rows(bad) != local_rows(OLD), "wrong unmix was not detected")
    bad = deepcopy(CHARTED)
    del bad[2]
    need(local_rows([ENTER] + bad + [EXIT]) != local_rows(OLD), "omitted source410 pullback was not detected")
    U, V = core.span(w["B"][962][-1]), core.span(w["B"][963][-1])
    need(core.dim(U) == core.dim(V) == 6 and core.dim(U & V) == 5, "incomparable source-frame dimensions")
    need((U >> 26) & 1 and not ((V >> 26) & 1), "U outside V witness")
    need((V >> 3) & 1 and not ((U >> 3) & 1), "V outside U witness")
    need(core.dim(core.span(list(core.points(U)) + list(core.points(V)))) == 7, "join dimension")
    per, at = persistent_s(w, core)
    try:
        core.frame_bill(per, lagrangian=True)
    except core.AuditFailure as exc:
        failure = str(exc)
        need("frame containment fails" in failure and str(at[963]) in failure,
             "persistent chart failed at a different obligation: " + failure)
    else:
        raise ValueError("persistent sum chart unexpectedly frame legal")
    pair_sites = [(i, g) for i, g in enumerate(w["B"])
                  if g[1] in PAIR or (g[0] == "add" and g[2] in PAIR)]
    return {
        "complete_pair_B_sites": pair_sites,
        "complete_local_profile": {str(r): n for r, n in before[0].items()},
        "width_inventory": {str(r): n for r, n in before[1].items()},
        "ordered_paid_chains_equal": True,
        "scalar_delta": {"forward_adds": 1, "cleanup_adds": 1, "total": 2},
        "cleanup_lengths": [len(w["cleanup"]), len(z["cleanup"])],
        "persistent_literal_S_first_frame_failure": failure,
        "persistent_failure_original_B": 963,
        "persistent_failure_changed_B": at[963],
        "rank6_frame_witness": {"U_not_V": 26, "V_not_U": 3, "intersection_rank": 5, "join_rank": 7},
    }


def main():
    ap = ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "source4096/source4076")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    for path, pin in PINS.items():
        need(hashlib.sha256((args.source / path).read_bytes()).hexdigest() == pin, "source pin: " + path)
    core = types.ModuleType("frozen_frame_accountant")
    exec(compile((args.source / "vendor/audit_core.py").read_bytes(), "frozen audit_core.py", "exec"), core.__dict__)
    local = local_rows(OLD)
    source_columns = [[local[r][s] for s in (410, 417)] for r in (608, 609)]
    determinant = source_columns[0][0] * source_columns[1][1] - source_columns[0][1] * source_columns[1][0]
    need(determinant == 2, "actual source influence determinant")
    result = {
        "status": "PASS_LOCAL_WORD_AND_FRAME_WITNESSES",
        "proof_boundary": "Exact local rational matrices and frozen full invoice; all-GL2 and temporal statements are written proofs; no full-word semantic replay here.",
        "rank4_source_columns": [[str(q) for q in row] for row in source_columns],
        "rank4_source_minor": str(determinant),
        "local_map": nonzero_rows(local),
        "old_B_block": OLD,
        "legal_replacement": LEGAL,
        "providers": {},
    }
    for provider in ("base", "extra"):
        w = json.loads(gzip.decompress((args.source / f"inputs/NEW-{provider}.json.gz").read_bytes()))
        result["providers"][provider] = run_provider(w, core)
    data = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.write_text(data)
    print(json.dumps({"status": result["status"], "providers": list(result["providers"]),
                      "profile_delta": {}, "scalar_delta": 2, "rank4_source_minor": 2,
                      "rank6_join": 7}, sort_keys=True))


if __name__ == "__main__":
    main()
