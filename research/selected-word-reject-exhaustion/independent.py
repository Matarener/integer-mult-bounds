#!/usr/bin/env python3
"""Independent recompute of the length-≤2 divergence census and closed form.

Does not import verify.py. Standard library only.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_SELECTED_WORD_REJECT_INDEPENDENT "
    "len2_divergences=661 named_diverge=2 four_exhaustive=false"
)
D = 111
N = 661
A = 3


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def agree(d, srcs, n):
    sym = [0] * n
    sym[d] = 1
    for s in srcs:
        sym[s] ^= 1
    exp = [0] * n
    exp[d] = 1
    for s in srcs:
        if s == d:
            exp = [0] * n
        else:
            exp[s] ^= 1
    return sym == exp


def closed_form(d, srcs):
    if d not in srcs:
        return True
    last = max(i for i, s in enumerate(srcs) if s == d)
    if srcs.count(d) % 2 == 0:
        return False
    for s, count in Counter(srcs[:last]).items():
        if s != d and count % 2:
            return False
    return True


def main():
    # Closed form on a fresh small domain.
    for length in range(0, 5):
        for srcs in itertools.product(range(7), repeat=length):
            for d in range(7):
                need(agree(d, srcs, 7) == closed_form(d, srcs), "closed form")

    divergences = []
    for length in range(0, 3):
        for srcs in itertools.product(range(N), repeat=length):
            need(agree(D, srcs, N) == closed_form(D, srcs), "full closed form")
            if not agree(D, srcs, N):
                divergences.append(list(srcs))
    need(len(divergences) == N, "divergence count")
    need(divergences == [[a, D] for a in range(N)], "divergence set order")
    need([D, D] in divergences, "self_even present")
    need([A, D] in divergences, "dest_with_src present")
    need([D, A] not in divergences, "dest_then_src agrees")

    named = {
        "self_even": [D, D],
        "dest_with_src": [A, D],
        "dup_src": [A, A],
        "self_once": [D],
    }
    diverge_names = [k for k, v in named.items() if not closed_form(D, v)]
    need(diverge_names == ["self_even", "dest_with_src"], "named diverge")
    need(len(diverge_names) != len(divergences), "not exhaustive")

    cert = json.loads(
        (HERE / "CERTIFICATE.json").read_text(encoding="utf-8"),
        object_pairs_hook=pairs_unique,
    )
    need(cert["claim"]["length2"]["divergences"] == 661, "cert count")
    need(cert["claim"]["four_exhaustive_for_len2_divergence"] is False, "cert flag")
    need(cert["no_new_kappa"] is True, "no new kappa")
    print(MARKER)


if __name__ == "__main__":
    main()
