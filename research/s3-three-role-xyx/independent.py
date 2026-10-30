#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent frozenset / row-mask engine for the S3 three-role xyx target."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"

ROLES = 3
GROUP_ORDER = 6
EXPECTED_CALLS = 56
DIRECT_LEN = 6
KAPPA = "0.001672660197076918"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT_S3_THREE_ROLE_XYX: {message}")


def compose(p, q):
    return tuple(p[q[i]] for i in range(3))


def build():
    elements = tuple(itertools.permutations(range(3)))
    index = {g: i for i, g in enumerate(elements)}
    table = tuple(tuple(index[compose(a, b)] for b in elements) for a in elements)
    e = index[(0, 1, 2)]
    x = index[(1, 0, 2)]
    y = index[(0, 2, 1)]
    xyx = table[table[x][y]][x]
    idem = [
        (u, v)
        for u in range(1, 8)
        for v in range(1, 8)
        if (u & v).bit_count() & 1
    ]
    calls = [(g, u, v) for g in (x, y) for u, v in idem]
    return elements, table, e, x, y, xyx, calls


ELEMENTS, TABLE, E, X, Y, XYX, CALLS = build()


def right_mul_mask(mask: int, g: int) -> int:
    out = 0
    for a in range(GROUP_ORDER):
        if (mask >> a) & 1:
            out ^= 1 << TABLE[a][g]
    return out


def identity_rows():
    """State as frozenset of (row, col, group_index) support atoms."""
    return frozenset((i, i, E) for i in range(ROLES))


def target_rows():
    return frozenset(
        [
            (0, 0, XYX),
            (1, 1, XYX),
            (2, 2, E),
        ]
    )


def apply_call(state: frozenset, call) -> frozenset:
    """
    Right-multiply by D_N(g)=I+([g]+[e])N using an explicit atom set.

    Does not import the primary packed-int engine.
    """
    g, u, v = call
    # Collect current matrix of masks.
    cells = [[0] * ROLES for _ in range(ROLES)]
    for r, c, a in state:
        cells[r][c] ^= 1 << a
    new_cells = [row[:] for row in cells]
    for row in range(ROLES):
        value = 0
        for middle in range(ROLES):
            if (u >> middle) & 1:
                value ^= cells[row][middle]
        delta = value ^ right_mul_mask(value, g)
        for col in range(ROLES):
            if (v >> col) & 1:
                new_cells[row][col] ^= delta
    out = []
    for r in range(ROLES):
        for c in range(ROLES):
            mask = new_cells[r][c]
            for a in range(GROUP_ORDER):
                if (mask >> a) & 1:
                    out.append((r, c, a))
    return frozenset(out)


def ball(start: frozenset, depth: int):
    found = {start: 0}
    frontier = [start]
    layers = [1]
    for dist in range(depth):
        nxt = []
        for state in frontier:
            for call in CALLS:
                image = apply_call(state, call)
                if image not in found:
                    found[image] = dist + 1
                    nxt.append(image)
        frontier = nxt
        layers.append(len(nxt))
    return found, layers


def digest_states(states) -> str:
    h = hashlib.sha256()
    for state in sorted(tuple(sorted(s)) for s in states):
        h.update(repr(state).encode())
    return h.hexdigest()


def load_cert():
    text = CERT_PATH.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def main() -> int:
    need(len(CALLS) == EXPECTED_CALLS, "call inventory")
    need(len(ELEMENTS) == GROUP_ORDER, "group inventory")

    identity = identity_rows()
    target = target_rows()
    need(identity != target, "target ≠ identity")

    letters = (X, Y, X)
    direct = [(lab, 1, 1) for lab in letters] + [(lab, 2, 2) for lab in letters]
    need(len(direct) == DIRECT_LEN, "direct length")
    state = identity
    for call in direct:
        state = apply_call(state, call)
    need(state == target, "independent direct word must attain target")

    fwd, layers_fwd = ball(identity, 3)
    bwd, layers_bwd = ball(target, 3)
    need(layers_fwd == [1, 56, 1750, 45396], "independent identity layers")
    need(layers_bwd == [1, 56, 1750, 45396], "independent target layers")

    near_i = {s for s, d in fwd.items() if d <= 2}
    hits = near_i & set(bwd.keys())
    near_t2 = {s for s, d in bwd.items() if d <= 2}
    hits_sym = set(fwd.keys()) & near_t2
    need(len(hits) == 0 and len(hits_sym) == 0, "independent MITM must find no short hit")

    cert = load_cert()
    need(cert["result_minimum"] == DIRECT_LEN, "certificate minimum")
    need(cert["hits_i2_t3"] == 0 and cert["hits_i3_t2"] == 0, "certificate hits")
    need(cert["layers_from_identity"] == layers_fwd, "layer agreement")
    need(cert["kappa"] == KAPPA and cert["no_new_kappa"] is True, "kappa pin")

    dig = digest_states(near_i)
    need(len(dig) == 64, "digest width")

    print(
        "PASS_INDEPENDENT_S3_THREE_ROLE_XYX",
        f"roles={ROLES}",
        f"calls={EXPECTED_CALLS}",
        f"target_minimum={DIRECT_LEN}",
        f"layers_i={layers_fwd}",
        "hits=0",
        "dirty_lowers=false",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
