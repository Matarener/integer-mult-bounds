#!/usr/bin/env python3
"""Independent recompute of the gate operand Sym/Exp lemma.

Does not import verify.py helpers. Standard library only.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_GATE_OPERAND_INDEPENDENT "
    "dest_free_agree=4686 dest_in_disagree>0 "
    "witnesses=self_even,dest_with_src"
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


def sym_coeffs(d, srcs, n):
    basis = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    acc = [0] * n
    for s in srcs:
        acc = [a ^ b for a, b in zip(acc, basis[s])]
    return tuple(a ^ b for a, b in zip(basis[d], acc))


def exp_coeffs(d, srcs, n):
    cur = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for s in srcs:
        cur[d] = [a ^ b for a, b in zip(cur[d], cur[s])]
    return tuple(cur[d])


def main():
    n = 6
    dest_free_agree = 0
    dest_free_disagree = 0
    dest_in_disagree = 0
    for length in range(0, 5):
        for srcs in itertools.product(range(n), repeat=length):
            for d in range(n):
                agree = sym_coeffs(d, srcs, n) == exp_coeffs(d, srcs, n)
                if d not in srcs:
                    if agree:
                        dest_free_agree += 1
                    else:
                        dest_free_disagree += 1
                elif not agree:
                    dest_in_disagree += 1
    need(dest_free_disagree == 0, "dest-free disagreement")
    need(dest_free_agree == 4686, "dest-free count")
    need(dest_in_disagree > 0, "dest-in disagreements exist")

    # Named witnesses over integer valuations (F2 action on each bit).
    def symbolic(d, srcs, val):
        out = list(val)
        acc = 0
        for s in srcs:
            acc ^= val[s]
        out[d] ^= acc
        return out

    def export_seq(d, srcs, val):
        out = list(val)
        for s in srcs:
            out[d] ^= out[s]
        return out

    need(symbolic(0, [0, 0], [7, 3, 5]) != export_seq(0, [0, 0], [7, 3, 5]),
         "self_even")
    need(symbolic(0, [1, 0], [7, 3, 5]) != export_seq(0, [1, 0], [7, 3, 5]),
         "dest_with_src")
    need(symbolic(0, [1, 1, 2], [7, 3, 5]) == export_seq(0, [1, 1, 2], [7, 3, 5]),
         "dest_free_dup")

    cert = json.loads(
        (HERE / "CERTIFICATE.json").read_text(),
        object_pairs_hook=pairs_unique,
    )
    need(cert["claim"]["small_domain"]["dest_free_agree"] == 4686, "cert census")
    need(cert["no_new_kappa"] is True, "no new kappa")
    print(MARKER)


if __name__ == "__main__":
    main()
