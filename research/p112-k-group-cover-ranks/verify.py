#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact masked fitting ranks for orthonormal k-group covers of the P112 labels (k = 3, 4).

Contract (kport-group-scalar-endpoint-audit; Discussion 1587): each port i lies in a group E_i of
orthonormal labels; a scalar decoder K has K_ii = 1 and K_ij = 0 unless i, j lie in distinct,
mutually orthogonal groups. Labels and the shared checking primitives (load_model, rank_mod_p,
parity_dot) come from PR2484's verifier, imported unchanged under another module name.

Checks per cover: exact group sizes and orthonormality; a colouring of pairwise orthogonal groups;
supports (one per class and position) whose 0/1 sum fits the mask, with dense rank equal to the support
count mod 2, 3 and 1000003; a set of pairwise non-orthogonal groups whose ports force an identity block
of the same size. Global facts: no nine labels are orthonormal (exhaustive), so a colour class holds at
most two groups of size >= 3 and colourings need >= 57 (k = 3) or >= 56 (k = 4) supports.
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
_SPEC = importlib.util.spec_from_file_location("pr2484_verify", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(V)
need = V.need
dot = V.parity_dot


def labels():
    lab, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                             (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
    need(all(dot(q, q) == 1 for q in lab), "all 112 labels have norm one")
    return lab


def max_orthonormal(lab):
    """Exhaustive: the largest set of pairwise orthogonal labels, and the number of maximum sets."""
    n = len(lab)
    nb = [frozenset(j for j in range(n) if j != i and dot(lab[i], lab[j]) == 0) for i in range(n)]
    counts = {}

    def grow(size, last, cand):
        counts[size] = counts.get(size, 0) + 1
        for u in sorted(cand):
            if u > last:
                grow(size + 1, u, cand & nb[u])

    for v in range(n):
        grow(1, v, frozenset(u for u in nb[v] if u > v))
    top = max(counts)
    return top, counts[top]


def check_cover(lab, k, cover):
    groups, colour, clique = cover["groups"], cover["colour"], cover["clique_groups"]
    need(sorted(x for g in groups for x in g) == list(range(112)), "cover partitions the ports")
    sizes = sorted(len(g) for g in groups)
    need(sizes.count(k) == 112 // k and all(s == k for s in sizes[112 % k:]) and sum(sizes[:112 % k] if 112 % k else []) in (0, 112 % k),
         "exact k-groups (k = 3 leaves one singleton)")
    for g in groups:
        need(all(dot(lab[x], lab[y]) == 0 for x in g for y in g if x != y), "orthonormal group")
    n = len(groups)
    go = [[i != j and all(dot(lab[x], lab[y]) == 0 for x in groups[i] for y in groups[j]) for j in range(n)] for i in range(n)]
    need(all(go[i][j] for i in range(n) for j in range(n) if i != j and colour[i] == colour[j]), "colour classes orthogonal")
    supports = []
    for c in sorted(set(colour)):
        cls = [groups[i] for i in range(n) if colour[i] == c]
        need(sum(len(g) for g in cls) <= 8, "class spans at most eight orthonormal labels")
        for p in range(max(len(g) for g in cls)):
            supports.append([g[p] for g in cls if len(g) > p])
    owner = {x: i for i, g in enumerate(groups) for x in g}
    K = [[0] * 112 for _ in range(112)]
    for s in supports:
        for a in s:
            for b in s:
                K[a][b] += 1
    forced = 0
    for i in range(112):
        for j in range(112):
            if i == j or not go[owner[i]][owner[j]]:
                need(K[i][j] == int(i == j), "mask entry")
                forced += 1
    ranks = {str(p): V.rank_mod_p(K, p) for p in (2, 3, 1000003)}
    need(set(ranks.values()) == {len(supports)}, "dense rank equals support count")
    need(len(set(clique)) == len(clique) and all(not go[u][v] for u in clique for v in clique if u != v),
         "clique groups pairwise non-orthogonal")
    ports = [x for v in clique for x in groups[v]]
    need(all(i == j or not go[owner[i]][owner[j]] for i in ports for j in ports), "identity block forced")
    need(len(ports) == len(supports), "exact rank")
    full = [i for i in range(n) if len(groups[i]) == k]
    floor = k * -(-len(full) // 2)
    return dict(groups=n, group_sizes=sorted(set(sizes)), supports=len(supports), forced_entries=forced,
                ranks_mod_p=ranks, clique_groups=len(clique), exact_fitting_rank=len(supports), colouring_floor=floor)


def controls(lab, cover):
    out = {}
    g = [list(x) for x in cover["groups"]]
    bad = dict(cover, colour=[0] * len(g))
    try:
        check_cover(lab, 4, bad)
    except V.CheckFailure as error:
        out["single_colour_rejected"] = "rejected: " + str(error)
    else:
        raise AssertionError("single colour accepted")
    a, b = g[0], g[1]
    swap = next(((x, y) for x in a for y in b if any(dot(lab[y], lab[z]) for z in a if z != x)), None)
    need(swap is not None, "a non-orthonormal swap exists")
    g2 = [list(x) for x in g]
    g2[0] = [z if z != swap[0] else swap[1] for z in a]
    g2[1] = [z if z != swap[1] else swap[0] for z in b]
    try:
        check_cover(lab, 4, dict(cover, groups=g2))
    except V.CheckFailure as error:
        out["non_orthonormal_group_rejected"] = "rejected: " + str(error)
    else:
        raise AssertionError("non-orthonormal group accepted")
    return out


def main():
    lab = labels()
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    top, count = max_orthonormal(lab)
    need(top == 8 and count == 4032, "largest orthonormal label sets have size eight (4,032 of them)")
    result = {"status": "PASS_P112_K_GROUP_COVER_RANKS", "max_orthonormal_labels": top, "orthonormal_8_frames": count,
              "covers": {k: check_cover(lab, int(k), c) for k, c in sorted(cert["covers"].items())},
              "reference_k2_rank_pr3335": 34}
    result["controls"] = controls(lab, cert["covers"]["4"])
    path = HERE / "RESULT.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return
    need(json.loads(path.read_text(encoding="utf-8")) == json.loads(json.dumps(result)), "RESULT.json differs")
    print("PASS_P112_K_GROUP_COVER_RANKS k3=57(floor57) k4=68(floor56) max_orthonormal=8 no_new_kappa")


if __name__ == "__main__":
    main()
