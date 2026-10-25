#!/usr/bin/env python3
"""Independent modulo3 source replay for the symmetric normalization argument.

Replays just the eight selected helper basis columns over free warp words.
No normalization checker or Fraction source interpreter is imported.
Apache-2.0. Substantial OpenAI assistance under the user's direction.
"""
from argparse import ArgumentParser
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

PIVOTS = (224, 225, 227, 229, 240, 241, 256, 257)
RECEIPT_SHA = "7ddf3f80b2fa61d1ab12035da9ef1c95d43f76077df819d7683144d7862a3f93"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_into(target, source, value):
    for key, coefficient in source.items():
        next_value = (target.get(key, 0)+value*coefficient) % 3
        if next_value:
            target[key] = next_value
        else:
            target.pop(key, None)


def ratio(numerator, denominator):
    need(denominator % 3 != 0, "scalar denominator admits reduction modulo3")
    return numerator*pow(denominator, -1, 3) % 3


def prefix_minor(program, centers):
    state = {("L", r): ({(PIVOTS.index(r), ()): 1} if r in PIVOTS else {}) for r in range(632)}
    event_count = 0
    for event in program:
        kind = event[0]
        if event == ["phase", "centers"]:
            break
        event_count += 1
        if kind == "warp":
            reg, operation = tuple(event[1]), event[2]
            updated = {}
            for (column, history), value in state[reg].items():
                history = history[1:] if history and history[0] == -operation else (operation,)+history
                add_into(updated, {(column, history): value}, 1)
            state[reg] = updated
        elif kind == "zero_buffer":
            key = "Z", event[2]
            if event[1] == "alloc":
                state[key] = {}
            else:
                need(not state[key], "zero buffer restored in modular helper replay")
        elif kind == "scalar":
            gate = event[1]
            op, target = gate[0], tuple(gate[1])
            if op == "clear":
                state[target] = {}
            elif op == "copy":
                state[target] = dict(state[tuple(gate[2])])
            elif op == "scale":
                scale = ratio(gate[2], gate[3])
                state[target] = {k: scale*v % 3 for k, v in state[target].items() if scale*v % 3}
            else:
                need(op == "add" and target != tuple(gate[2]), "normalized nonaliasing addition")
                add_into(state[target], state[tuple(gate[2])], ratio(gate[3], gate[4]))
        else:
            need(kind in ("phase", "adapter", "residual_adapter", "climb"), "known normalized prefix event")
    minor = []
    for center in centers:
        row = state["L", center]
        need(all(not history for _, history in row), "selected helper columns have no residual formal warp")
        minor.append([row.get((column, ()), 0) for column in range(8)])
    return minor, event_count


def rank_mod3(matrix):
    rows = [[x % 3 for x in row] for row in matrix]
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, 3)
        rows[rank] = [x*inv % 3 for x in rows[rank]]
        for j in range(len(rows)):
            if j != rank:
                coefficient = rows[j][col]
                rows[j] = [(x-coefficient*y) % 3 for x, y in zip(rows[j], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def multiply(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("--followup", type=Path, required=True)
    ap.add_argument("--normalization-result", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    inp = args.followup / "artifact/recovered-involutory/modern-source/inputs"
    receipt_path = inp / "NATIVE-RECEIPT.json"
    need(sha(receipt_path) == RECEIPT_SHA, "attached actual native receipt")
    source_checks = {}
    for name, provider in read(receipt_path)["providers"].items():
        local = inp / "native-cache" / provider["word_sha256"] / "local"
        for filename in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            need(sha(local/filename) == provider["complete_native_files"]["local/"+filename], "provider source pin")
        word, programs = read(local/"CANONICAL-WORD.json.gz"), read(local/"LOCAL-PROGRAMS.json.gz")
        minor, events = prefix_minor(programs["forward"], word["centers"])
        need(rank_mod3(minor) == 8, "independently reconstructed H retains rank8 modulo3")
        source_checks[name] = {"word_sha256": provider["word_sha256"],
            "selected_helpers": list(PIVOTS), "mod3_minor": minor, "rank": 8,
            "prefix_events_replayed": events, "initial_basis_columns": 8}
    declared = read(args.normalization_result)
    # Derive quaternion multiplication, rather than loading its checker.
    b = [[1, -1, -1, 0], [1, 1, 0, 1], [1, 0, 1, -1], [0, -1, 1, 1]]
    bt = list(map(list, zip(*b)))
    need(multiply(b, bt) == [[3*int(i == j) for j in range(4)] for i in range(4)], "quaternion norm3 identity")
    a = [[4*b[i % 4][j % 4] if i//4 == j//4 else 0 for j in range(8)] for i in range(8)]
    inverse = [[-F(x, 12) for x in row] for row in zip(*[[x//4 for x in row] for row in a])]
    need(multiply(a, inverse) == [[-int(i == j) for j in range(8)] for i in range(8)], "imaginary factors multiply to the exact Gaussian identity")
    alt = declared["rational_eight_port_alternative"]
    need(a == alt["A_imaginary_integer_matrix"] and inverse == [[F(x) for x in row] for row in alt["A_inverse_imaginary_matrix"]], "rational factor agrees with the reviewed matrix")
    need(rank_mod3(a) == 4, "rational factor loses four rows modulo3")
    need(any(x.denominator % 3 == 0 for row in inverse for x in row), "inverse necessarily uses division3")
    result = {"status": "PASS_INDEPENDENT_MOD3_NORMALIZATION_REVIEW",
        "providers": source_checks,
        "proof_review": {
            "assumption": "B belongs to GL_408(Z[1/2,i]); both B and its inverse are Gaussian dyadic.",
            "field": "Modulo3 the ring is F9 because X^2+1 has no root in F3.",
            "rank_step": "The independently replayed H minor has rank8 modulo3; multiplying by invertible B preserves it, so A has row rank8.",
            "Gram_step": "D^2=I and full row rank Q imply QQ^T=8I; with RR^T=56I this gives AA^T=−48I, hence0 modulo3.",
            "dimension_step": "The8-dimensional row space U is contained in U-perp inside the nondegenerate k-dimensional bilinear dot space; therefore8≤k−8 and k≥16.",
            "scope": "This applies only to the stated helper-only invertible Gaussian-dyadic normalization and symmetric reflection. It is not a universal bound on changed local contracts."},
        "rational8": {"exact_factor_checked": True, "mod3_rank": 4,
                      "inverse_needs_division3": True},
        "normalization_result_sha256": sha(args.normalization_result),
        "native_receipt_sha256": RECEIPT_SHA,
        "independence": "Modular prefix replay over only8 selected helper basis columns; no import of the existing source interpreter or normalization checker. Native frame semantics remain inherited."}
    args.out.write_text(json.dumps(result, indent=2)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
