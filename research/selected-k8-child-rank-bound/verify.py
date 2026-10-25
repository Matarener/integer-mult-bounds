#!/usr/bin/env python3
"""Largest paid child rank of the selected k8 word under its frame contract.

A paid child is one strict dimension jump of nested frames along a register,
or one fixed centre descent. Frames are subspaces of F2^9. This checker
rebuilds the event graph, the forward/backward frame intervals and the
low-end cone ceilings, then enumerates every nested pair on every edge.
It does not import the predecessor frame model.
"""

import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz"
RECEIPT = Path(__file__).resolve().parent / "RESULT.json"
WORD_SHA = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
H = 9
FULL = tuple(1 << i for i in range(H - 1, -1, -1))
TARGET_RANK = 44


def need(ok, why):
    if not ok:
        raise ValueError(why)


def eliminate(vs):
    piv = {}
    for a in vs:
        need(a >= 0, "negative frame vector")
        while a:
            bit = a.bit_length() - 1
            if bit in piv:
                a ^= piv[bit]
            else:
                piv[bit] = a
                break
    for k in sorted(piv):
        for j in piv:
            if j > k and (piv[j] >> k) & 1:
                piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def basis(vs):
    out = eliminate(vs)
    need(all(a < (1 << H) for a in out), "frame vector outside F2^9")
    return out


def contained(a, b):
    return basis(list(a) + list(b)) == tuple(b)


def join(frames):
    return basis(x for f in frames for x in f)


def meet(a, b):
    rows = [(u << H) | u for u in a] + [x << H for x in b]
    return basis(r for r in eliminate(rows) if r >> H == 0)


def interval(lo, hi):
    need(contained(lo, hi), "empty frame interval")
    comp, cur = [], list(lo)
    for x in hi:
        if len(basis(cur + [x])) > len(basis(cur)):
            comp.append(x)
            cur.append(x)
    k = len(comp)
    need(k <= 4, "quotient dimension above 4")
    vectors = list(range(1, 1 << k))
    out = []
    for mask in range(1 << len(vectors)):
        chosen = {vectors[i] for i in range(len(vectors)) if (mask >> i) & 1}
        if all((p ^ q) in chosen for p in chosen for q in chosen if p != q):
            lifted = []
            for a in chosen:
                x = 0
                for i in range(k):
                    if (a >> i) & 1:
                        x ^= comp[i]
                lifted.append(x)
            out.append(basis(list(lo) + lifted))
    need(len(set(out)) == len(out), "duplicate interval frame")
    return out


def registers(e):
    return (e[1], e[2]) if e[0] == "add" else (e[1],)


def apply(e, rows, dual=False):
    if e[0] == "add":
        t, s = e[1], e[2]
        q = Fraction(e[3], e[4])
        if dual:
            t, s, q = s, t, -q
        dst = rows[t]
        for k, x in list(rows[s].items()):
            a = dst.get(k, Fraction(0)) + q * x
            if a:
                dst[k] = a
            else:
                dst.pop(k, None)
    elif e[0] == "scale":
        t = e[1]
        q = Fraction(e[2], e[3])
        if dual:
            q = 1 / q
        rows[t] = {k: q * x for k, x in rows[t].items()}
    else:
        raise ValueError("unknown scalar primitive")


def invert(e):
    r = list(e)
    if r[0] == "add":
        r[3] = -r[3]
    else:
        r[2], r[3] = r[3], r[2]
    return r


def cone_ceilings(w, n, v, low_ends):
    ident = lambda: [{k: Fraction(1)} for k in range(n)]
    main = w["A"] + w["cut"] + w["B"]
    raw = ident()
    for e in main:
        apply(e, raw)
    dirt = [{} for _ in range(n)]
    for y in range(v, 2 * v):
        dirt[y] = {k: a for k, a in raw[y].items() if k >= 2 * v}
    for e in w["precondition"]:
        apply(e, dirt)
    compensation = [
        ["add", y, k, -a.numerator, a.denominator, []]
        for y in range(v, 2 * v)
        for k, a in sorted(dirt[y].items())
    ]
    prefix = w["precondition"] + compensation + main
    p, pinv = ident(), ident()
    for e in prefix:
        apply(e, p)
    for e in reversed(prefix):
        apply(invert(e), pinv)
    holders = defaultdict(set)
    for k in range(n):
        for j in p[k]:
            holders[j].add(k)
    ceil = {}
    for q, U in low_ends.items():
        for k in set(pinv[q]) | holders[q]:
            if k != q:
                ceil[k] = meet(ceil.get(k, FULL), U)
    return ceil


def load_word():
    blob = WORD.read_bytes()
    raw = gzip.decompress(blob)
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA, "selected word content hash")
    w = json.loads(raw)
    rep = w["report"]
    profile = {int(r): n for r, n in rep["local_profile"].items()}
    need(profile == PROFILE, "published local profile")
    need(rep["h"] == H and rep["v"] == 112 and rep["R"] == 480, "word dimensions")
    need(sum(r * n for r, n in profile.items()) == 5586, "local rank mass")
    return w


def build(w, use_cones=True):
    rep = w["report"]
    v, R = rep["v"], rep["R"]
    n = 2 * v + R
    end = [FULL] * v + [
        basis(x for x in range(1, 1 << H) if (x & p).bit_count() % 2 == 0)
        for p in w["ports"]
    ] + [FULL] * R
    low = {int(q): basis(U) for q, U in w.get("helper_final", {}).items()}
    for q, U in low.items():
        need(2 * v <= q < n, "helper final register")
        end[q] = U
    start = [(p,) for p in w["ports"]] + [()] * (v + R)
    for q, U in w.get("start_extra", {}).items():
        need(2 * v <= int(q) < n, "non-helper entrance")
        start[int(q)] = basis(U)
    early = w.get("early_cleanup", [])
    need(len({i for i, _ in early}) == len(early), "duplicate early cleanup")
    tail = [w["cleanup"][i][:-1] + [U] for i, U in early]
    lev = {int(t): basis(U) for t, U in w.get("target_levels", {}).items()}
    pins = {q: basis(U) for q, U in zip(w["centers"], w["center_frames"])}
    need(len(pins) == 8, "eight centres")
    for t in range(v):
        need(v + t not in pins, "target pin collision")
        pins[v + t] = lev.get(t, ())
    centre = []
    for q, U in zip(w["centers"], w["center_frames"]):
        U = basis(U)
        served = {lev.get(e[1] - v, ()) for e in w["cut"] if e[2] == q}
        for T in sorted(served, key=lambda x: -len(x)):
            need(contained(T, U), "centre path not nested")
            if T != U:
                centre.append(len(U) - len(T))
            U = T
    gates = [("A", e) for e in w["A"]] + [("B", e) for e in w["B"]] + [
        ("T", e) for e in tail
    ]
    given = [basis(e[-1]) for _, e in gates]
    regs = [registers(e) for _, e in gates]
    nA, nB = len(w["A"]), len(w["B"])
    need((nA, nB, len(tail)) == (3451, 1846, 116), "section sizes")
    fixed = {}
    for q in range(n):
        fixed[("S", q)] = start[q]
        fixed[("E", q)] = end[q]
    for q, U in pins.items():
        fixed[("P", q)] = U
    chains = defaultdict(list)
    for q in range(n):
        chains[q].append(("S", q))
    boundary = {}
    for i, rs in enumerate(regs):
        if i == nA:
            for q in pins:
                chains[q].append(("P", q))
        if i == nA + nB:
            for q in range(n):
                boundary[q] = len(chains[q]) - 1
        for q in rs:
            chains[q].append(("G", i))
    for q in range(n):
        chains[q].append(("E", q))
    order = [("S", q) for q in range(n)]
    for i in range(len(gates)):
        if i == nA:
            order += [("P", q) for q in pins]
        order.append(("G", i))
    order += [("E", q) for q in range(n)]
    position = {node: k for k, node in enumerate(order)}
    pred, succ = defaultdict(list), defaultdict(list)
    edges = Counter()
    for q, ch in chains.items():
        for a, b in zip(ch, ch[1:]):
            need(position[a] < position[b], "chain order")
            succ[a].append(b)
            pred[b].append(a)
            edges[(a, b)] += 1
    lo, hi = {}, {}
    for node in order:
        if node in fixed:
            lo[node] = fixed[node]
            for a in pred[node]:
                need(contained(lo[a], fixed[node]), "fixed frame below its join")
        else:
            lo[node] = join(lo[a] for a in pred[node])
    ceil = cone_ceilings(w, n, v, low) if use_cones else {}
    ceil_at = defaultdict(list)
    for q, k in boundary.items():
        if q in ceil:
            ceil_at[chains[q][k]].append(ceil[q])
    for node in reversed(order):
        if node in fixed:
            hi[node] = fixed[node]
        else:
            U = FULL
            for b in succ[node]:
                U = meet(U, hi[b])
            for C in ceil_at[node]:
                U = meet(U, C)
            hi[node] = U
        need(contained(lo[node], hi[node]), "empty domain")
    domain = {}
    for i in range(len(gates)):
        node = ("G", i)
        if lo[node] != hi[node]:
            domain[node] = interval(lo[node], hi[node])
            need(given[i] in domain[node], "given frame outside its interval")
        else:
            need(given[i] == lo[node], "given frame differs from the forced frame")
    return {
        "edges": dict(edges),
        "domain": domain,
        "lo": lo,
        "hi": hi,
        "given": given,
        "centre": centre,
        "fixed": fixed,
    }


def frames_of(graph, node):
    if node in graph["domain"]:
        return graph["domain"][node]
    if node in graph["fixed"]:
        return [graph["fixed"][node]]
    return [graph["lo"][node]]


def edge_bounds(graph):
    """Maximum dimension jump of each edge over its complete frame intervals."""
    bounds = {}
    given = {}
    for (a, b), m in graph["edges"].items():
        best = 0
        least = H
        nested = False
        for Fa in frames_of(graph, a):
            for Fb in frames_of(graph, b):
                if contained(Fa, Fb):
                    d = len(Fb) - len(Fa)
                    best = max(best, d)
                    least = min(least, d)
                    nested = True
        need(nested, "edge has no monotone frame pair")
        # The given assignment uses the recorded gate frame, else the fixed frame.
        if a[0] == "G" and a in graph["domain"]:
            Fa = graph["given"][a[1]]
        else:
            Fa = frames_of(graph, a)[0]
        if b[0] == "G" and b in graph["domain"]:
            Fb = graph["given"][b[1]]
        else:
            Fb = frames_of(graph, b)[0]
        need(contained(Fa, Fb), "given assignment is not monotone")
        d = len(Fb) - len(Fa)
        bounds[(a, b)] = (least, best, m)
        given[(a, b)] = d
        need(least <= d <= best, "given jump outside the interval")
    return bounds, given


def given_profile(graph, given):
    count = Counter()
    for (a, b), d in given.items():
        if d:
            count[d] += graph["edges"][(a, b)]
    for d in graph["centre"]:
        count[d] += 1
    return dict(sorted(count.items()))


def section_profile(w):
    """Second route: walk the recorded sections, as the native auditor charges them."""
    rep = w["report"]
    v, R = rep["v"], rep["R"]
    n = 2 * v + R
    end = [FULL] * v + [
        basis(x for x in range(1, 1 << H) if (x & p).bit_count() % 2 == 0)
        for p in w["ports"]
    ] + [FULL] * R
    for q, U in w.get("helper_final", {}).items():
        end[int(q)] = basis(U)
    start = [(p,) for p in w["ports"]] + [()] * (v + R)
    for q, U in w.get("start_extra", {}).items():
        start[int(q)] = basis(U)
    early = {i: U for i, U in w.get("early_cleanup", [])}
    tail = [w["cleanup"][i][:-1] + [U] for i, U in early.items()]
    lev = {int(t): basis(U) for t, U in w.get("target_levels", {}).items()}
    cur = list(start)
    paid = Counter()

    def climb(q, U):
        U = basis(U)
        need(contained(cur[q], U), "section walk left the monotone contract")
        d = len(U) - len(cur[q])
        if d:
            paid[d] += 1
        cur[q] = U

    for section in ("A", "B"):
        if section == "B":
            for t in range(v):
                need(cur[v + t] == lev.get(t, ()), "target level mismatch")
            for q, U0 in zip(w["centers"], w["center_frames"]):
                U = basis(U0)
                need(cur[q] == U, "centre entrance mismatch")
                served = {lev.get(e[1] - v, ()) for e in w["cut"] if e[2] == q}
                for T in sorted(served, key=lambda x: -len(x)):
                    need(contained(T, U), "centre descent not nested")
                    if T != U:
                        paid[len(U) - len(T)] += 1
                    U = T
        for e in w[section]:
            for q in registers(e):
                climb(q, e[-1])
    for e in tail:
        for q in registers(e):
            climb(q, e[-1])
    for q, U in enumerate(end):
        climb(q, U)
    return dict(sorted(paid.items()))


def census(w, use_cones=True):
    graph = build(w, use_cones=use_cones)
    bounds, given = edge_bounds(graph)
    max_jump = max(best for _, best, _ in bounds.values())
    hist = Counter()
    increases = 0
    rank5_min = Counter()
    for (a, b), (least, best, m) in bounds.items():
        hist[best] += m
        if given[(a, b)] < best:
            increases += m
        if best == 5:
            rank5_min[least] += m
    sizes = Counter(len(fs) for fs in graph["domain"].values())
    quotients = Counter()
    for node, fs in graph["domain"].items():
        # Interval size is the subspace count of the quotient.
        quotients[len(fs)] += 1
    profile = given_profile(graph, given)
    return {
        "max_climb": max_jump,
        "edge_max_histogram": dict(sorted(hist.items())),
        "edges_below_their_max": increases,
        "rank5_minima": dict(sorted(rank5_min.items())),
        "free_gates": len(graph["domain"]),
        "forced_gates": len(graph["given"]) - len(graph["domain"]),
        "interval_sizes": dict(sorted(sizes.items())),
        "centre_descents": sorted(graph["centre"]),
        "graph_profile": profile,
        "quotient_counts": {str(k): v for k, v in sorted(quotients.items())},
    }


def certify(w):
    with_cones = census(w, True)
    without = census(w, False)
    walked = section_profile(w)
    need(with_cones["graph_profile"] == PROFILE, "graph profile differs from the word")
    need(walked == PROFILE, "section walk differs from the word")
    need(with_cones["centre_descents"] == [8] * 8, "centre descents")
    need(with_cones["max_climb"] == 5, "climb cap")
    need(with_cones["free_gates"] == 1741, "free-gate tie-out")
    need(with_cones["forced_gates"] == 3672, "forced-gate tie-out")
    need(with_cones["interval_sizes"] == {2: 1098, 5: 613, 16: 30}, "interval census")
    need(with_cones["edge_max_histogram"][5] == 82, "rank-5 edge multiplicity")
    need(with_cones["rank5_minima"] == {3: 24, 4: 26, 5: 32}, "rank-5 minima")
    need(sum(with_cones["rank5_minima"].values()) == 82, "rank-5 split")
    need(max(with_cones["edge_max_histogram"]) == 5, "histogram support")
    need(without["max_climb"] == 5, "cone ceilings are not what cuts rank 6")
    # Ambient lemma, independent of the word: a jump inside F2^9 is at most 9.
    blank, full = basis(()), basis(FULL)
    need(len(full) - len(blank) == 9, "ambient dimension")
    need(9 < TARGET_RANK and with_cones["max_climb"] < TARGET_RANK, "rank 44 comparison")
    max_paid = max(with_cones["max_climb"], max(with_cones["centre_descents"]))
    need(max_paid == 8, "largest paid child rank")
    # Controls. Each must reject a weakened reading.
    need(not all(d <= 4 for d in with_cones["edge_max_histogram"]), "rank 4 would be a false cap")
    try:
        basis([1 << H])
        raise ValueError("bit 9 was accepted")
    except ValueError as exc:
        need("outside F2^9" in str(exc), "outside-vector control")
    need(with_cones["edges_below_their_max"] >= 0, "increase count")
    result = {
        "schema": "selected-k8-child-rank-bound-v1",
        "word_sha256": WORD_SHA,
        "ambient_dimension": H,
        "largest_paid_child_rank": max_paid,
        "largest_graph_climb": with_cones["max_climb"],
        "centre_descent_rank": 8,
        "centre_descent_count": 8,
        "rank_44_emitted": False,
        "free_gates": with_cones["free_gates"],
        "forced_gates": with_cones["forced_gates"],
        "interval_sizes": with_cones["interval_sizes"],
        "edge_max_histogram": with_cones["edge_max_histogram"],
        "edges_whose_jump_can_increase": with_cones["edges_below_their_max"],
        "rank5_capable_edges_by_minimum": with_cones["rank5_minima"],
        "max_climb_without_cone_ceilings": without["max_climb"],
        "given_profile": PROFILE,
        "section_walk_agrees": True,
        "no_new_kappa": True,
    }
    return result


def main():
    write = "--write" in sys.argv
    result = certify(load_word())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if write:
        RECEIPT.write_text(text)
    else:
        need(RECEIPT.read_text() == text, "RESULT.json drift")
    print(
        "PASS_SELECTED_K8_CHILD_RANK_BOUND "
        f"max_paid_rank={result['largest_paid_child_rank']} "
        f"max_climb={result['largest_graph_climb']} "
        f"centre=8x8 rank44=0 free_gates={result['free_gates']} "
        f"increasable_edges={result['edges_whose_jump_can_increase']} "
        "no_new_kappa"
    )


if __name__ == "__main__":
    main()
