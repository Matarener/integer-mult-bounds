#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent check of the PR #3942 fixed-frame new-gap reduction.

This file does not import search.py. vendor/retiming.py is the predecessor
scalar-trace oracle, authenticated by SHA256 before it is loaded. The
interaction and new-gap claims are re-derived from that trace.
"""
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD = "1416f8cd6bfb2f2eb9aa5cc22f0388a85fdbac91"
DIGESTS = {
    "inputs/BORROW-WORD-43base.json.gz":
        "5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699",
    "inputs/BORROW-WORD-43extra.json.gz":
        "965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e",
    "vendor/retiming.py":
        "591d7278541ac4de9e9b6fc1e17aba23b205ac4b6c81824a28fc08294658ef0d",
}
# Published nonzero bridge rows of both RESULT-*.json files at HEAD.
PUBLISHED_NONZERO = (
    ("restore", 182, 178, 8, (0, 2, -1, 0, 0, 0, 0, 0, 0, 0)),
    ("restore", 191, 178, 8, (0, 2, -1, 0, 0, 0, 0, 0, 0, 0)),
    ("restore", 192, 178, 8, (0, 2, -1, 0, 0, 0, 0, 0, 0, 0)),
    ("restore", 193, 178, 8, (0, 2, -1, 0, 0, 0, 0, 0, 0, 0)),
)
PHASES = ("A", "B", "restore")


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def gauss(n, k):
    if k < 0 or k > n:
        return 0
    num = den = 1
    for i in range(k):
        num *= (1 << n) - (1 << i)
        den *= (1 << k) - (1 << i)
    return num // den


def load_retiming():
    path = HERE / "vendor/retiming.py"
    spec = importlib.util.spec_from_file_location("pinned_retiming", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_word(name):
    raw = (HERE / name).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == DIGESTS[name], "word digest " + name)
    return json.loads(gzip.decompress(raw))


def span_bit(mask, v):
    """Subspace join of a characteristic mask with the line through v."""
    added = 0
    points = mask
    while points:
        b = points & -points
        points -= b
        added |= 1 << ((b.bit_length() - 1) ^ v)
    return mask | added


def quotient_basis(low, high):
    """Closed F2 basis of high/low. Independent of one-vector frame walks."""
    covered = {x for x in range(512) if low >> x & 1}
    reps = []
    for v in range(512):
        if (high >> v) & 1 and v not in covered:
            reps.append(v)
            covered.update(v ^ x for x in tuple(covered))
    return reps, covered


def one_vector_counts(low, high, rank):
    """Fresh one-vector extension. Not the predecessor search.frames walker."""
    current = {low}
    counts = {rank(low): 1}
    guard = 0
    while True:
        expanded = set()
        for frame in current:
            for v in range(512):
                if (high >> v) & 1 and not (frame >> v) & 1:
                    expanded.add(span_bit(frame, v))
        if not expanded:
            break
        guard += 1
        require(guard <= 4, "one-vector walk exceeded quotient rank 4")
        current = expanded
        counts[rank(low) + guard] = len(current)
    return counts


def analyze(R, word):
    report = Counter()
    problems = []
    nonzero = []
    trace_case = None
    sensitive = None
    max_q = 0
    seen_intervals = set()
    for section in PHASES:
        gates = word[section]
        nodes, where, _bill = R.tracing(word)
        for lo, hi in R.segments(word, section):
            occ = defaultdict(list)
            for i in range(lo, hi):
                for r in R.touched(gates[i]):
                    occ[r].append(i)
            entries, exits = {}, {}
            for r, idxs in occ.items():
                entries[r] = nodes[r][where[((section, idxs[0]), r)]][2]
                last = where[((section, idxs[-1]), r)]
                require(nodes[r][last + 1][1] != "map", "missing exit")
                exits[r] = nodes[r][last + 1][3]
            removal = {}
            corridor = {}
            touched = {}
            adds = []
            for i in range(lo, hi):
                if gates[i][0] != "add":
                    continue
                regs = tuple(R.touched(gates[i]))
                touched[i] = set(regs)
                delta = [0] * 10
                for r in regs:
                    seq = nodes[r]
                    pos = where[((section, i), r)]
                    before, frame = seq[pos][2], seq[pos][3]
                    require(seq[pos + 1][1] != "map", "missing successor")
                    after = seq[pos + 1][3]
                    delta[R.rank(frame) - R.rank(before)] -= 1
                    delta[R.rank(after) - R.rank(frame)] -= 1
                    delta[R.rank(after) - R.rank(before)] += 1
                removal[i] = delta
                lower, upper = i, i + 1
                g = gates[i]
                while lower > lo and R.crosses(g, gates[lower - 1]):
                    lower -= 1
                while upper < hi and R.crosses(g, gates[upper]):
                    upper += 1
                corridor[i] = (lower, upper)
                adds.append(i)
                cuts = [c for c in (i - 1, i, i + 2) if lower <= c <= upper and c != i + 1]
                reduced = {r: tuple(x for x in occ[r] if x != i) for r in regs}
                for cut in cuts:
                    pair = []
                    for r in regs:
                        idxs = reduced[r]
                        k = bisect_left(idxs, cut)
                        before = R.span(tuple(gates[idxs[k - 1]][-1])) if k else entries[r]
                        after = R.span(tuple(gates[idxs[k]][-1])) if k < len(idxs) else exits[r]
                        pair.append((before, after))
                    low = R.join(pair[0][0], pair[1][0])
                    high = pair[0][1] & pair[1][1]
                    if not R.contained(low, high):
                        continue
                    q = R.rank(high) - R.rank(low)
                    max_q = max(max_q, q)
                    if q > 3:
                        problems.append(("quotient", section, i, cut, q))
                    key = (low, high)
                    if key not in seen_intervals:
                        seen_intervals.add(key)
                        reps, covered = quotient_basis(low, high)
                        require(len(reps) == q, "quotient basis rank")
                        require(sum(1 << x for x in covered) == high, "quotient basis misses high")
                        walked = one_vector_counts(low, high, R.rank)
                        for kdim in range(q + 1):
                            require(walked.get(R.rank(low) + kdim, 0) == gauss(q, kdim),
                                    "one-vector coverage")
                        report["intervals"] += 1
                        report["quotient_" + str(q)] += 1
                    report["first_dimensions"] += R.rank(high) - R.rank(low) + 1

            def bounds_at(j, cut, frame_of, index_of):
                packed = []
                for r in touched[j]:
                    idxs = [index_of(x) for x in occ[r] if x != j]
                    idxs.sort()
                    k = bisect_left(idxs, cut)
                    before = R.span(tuple(frame_of(idxs[k - 1]))) if k else entries[r]
                    after = R.span(tuple(frame_of(idxs[k]))) if k < len(idxs) else exits[r]
                    packed.append((before, after, R.rank(before), R.rank(after)))
                low = R.join(packed[0][0], packed[1][0])
                high = packed[0][1] & packed[1][1]
                if not R.contained(low, high):
                    return None
                return packed, R.rank(low), R.rank(high)

            def delta_list(j, packed, lo_rank, hi_rank):
                base = removal[j]
                out = []
                for dimension in range(lo_rank, hi_rank + 1):
                    delta = base.copy()
                    for _before, _after, a, b in packed:
                        delta[b - a] -= 1
                        delta[dimension - a] += 1
                        delta[b - dimension] += 1
                    delta[0] = 0
                    require(sum(r * n for r, n in enumerate(delta)) == 0, "rank mass")
                    out.append((dimension, tuple(delta)))
                return out

            def original_price(j, cut):
                packed = bounds_at(j, cut, lambda pos: gates[pos][-1], lambda x: x)
                if packed is None:
                    return None
                return delta_list(j, *packed)

            # Disjoint ADDs cross exactly when touched sets are the endpoint pairs.
            # Checked on every ADD, not by an n^2 search: crosses(g, h) for two
            # ADDs is g[1] != h[2] and h[1] != g[2].
            for i in adds:
                gi = gates[i]
                require(touched[i] == {gi[1], gi[2]}, "ADD touched set")
                report["adds"] += 1

            for p in range(lo, hi - 1):
                g, h = gates[p], gates[p + 1]
                if g[0] != "add" and h[0] != "add":
                    continue
                left_ok = g[0] == "add" and R.crosses(g, h)
                right_ok = h[0] == "add" and R.crosses(h, g)
                if not left_ok and not right_ok:
                    continue
                share = set(R.touched(g)) & set(R.touched(h))
                if share and R.span(tuple(g[-1])) != R.span(tuple(h[-1])):
                    report["unequal_shared"] += 1
                    for r in share:
                        pos = where[((section, p + 1), r)]
                        before = nodes[r][pos][2]
                        if before != R.span(tuple(g[-1])):
                            problems.append(("nesting", section, p, r))
                    continue
                report["fixed_pairs"] += 1
                tg, th = set(R.touched(g)), set(R.touched(h))

                def frame_sw(pos, p=p, g=g, h=h):
                    if pos == p:
                        return h[-1]
                    if pos == p + 1:
                        return g[-1]
                    return gates[pos][-1]

                def index_sw(x, p=p):
                    if x == p:
                        return p + 1
                    if x == p + 1:
                        return p
                    return x

                for j in adds:
                    if j in (p, p + 1):
                        continue
                    lower_j, upper_j = corridor[j]
                    if j > p + 1:
                        legal = lower_j <= p + 2 and R.crosses(gates[j], g)
                    else:
                        legal = upper_j >= p and R.crosses(gates[j], h)
                    if section == "restore" or report["fixed_pairs"] <= 40:
                        if j > p + 1:
                            crossed = (g, *gates[p + 2:j])
                        else:
                            crossed = (*gates[j + 1:p], h)
                        require(legal == all(R.crosses(gates[j], e) for e in crossed),
                                "fast corridor disagrees")
                        report["legality_oracle"] += 1
                    if not legal:
                        continue
                    report["legal_interior"] += 1
                    tj = touched[j]
                    both = bool(tj & tg) and bool(tj & th)
                    if not both:
                        if (tj & th) and not (tj & tg):
                            pred, label = p + 2, "only_right"
                        elif (tj & tg) and not (tj & th):
                            pred, label = p, "only_left"
                        else:
                            pred, label = p + 1, "neither"
                            # Neither gate meets this ADD, so the interior cut
                            # has the same neighbours before and after the swap.
                            if any(p in occ[r] or p + 1 in occ[r] for r in tj):
                                problems.append(("neither_seen", section, p, j))
                            report[label] += 1
                            continue
                        lower, upper = corridor[j]
                        if not lower <= pred <= upper:
                            problems.append(("pred_illegal", section, p, j, label))
                            continue
                        swapped = bounds_at(j, p + 1, frame_sw, index_sw)
                        original = bounds_at(j, pred, lambda pos: gates[pos][-1], lambda x: x)
                        if delta_list(j, *swapped) != delta_list(j, *original) if swapped and original else swapped != original:
                            problems.append(("localise", section, p, j, label))
                        else:
                            report[label] += 1
                            if sensitive is None and label == "only_left" and original is not None:
                                other = original_price(j, p + 1)
                                if other != delta_list(j, *original):
                                    sensitive = (section, p, j)
                        continue
                    report["bridge"] += 1
                    swapped = bounds_at(j, p + 1, frame_sw, index_sw)
                    packed = []
                    for r in tj:
                        idxs = [x for x in occ[r] if x != j]
                        left = bisect_left(idxs, p) - 1
                        before = R.span(tuple(gates[idxs[left]][-1])) if left >= 0 else entries[r]
                        right = bisect_left(idxs, p + 2)
                        after = R.span(tuple(gates[idxs[right]][-1])) if right < len(idxs) else exits[r]
                        if r in th:
                            before = R.span(tuple(h[-1]))
                        if r in tg:
                            after = R.span(tuple(g[-1]))
                        packed.append((before, after, R.rank(before), R.rank(after)))
                    low = R.join(packed[0][0], packed[1][0])
                    high = packed[0][1] & packed[1][1]
                    if not R.contained(low, high):
                        bridged = None
                    else:
                        bridged = (packed, R.rank(low), R.rank(high))
                    left_rows = None if swapped is None else delta_list(j, *swapped)
                    right_rows = None if bridged is None else delta_list(j, *bridged)
                    if left_rows != right_rows:
                        problems.append(("bridge", section, p, j))
                        continue
                    report["bridge_dimensions"] += 0 if left_rows is None else len(left_rows)
                    if left_rows:
                        for dimension, delta in left_rows:
                            if any(delta):
                                nonzero.append((section, p, j, dimension, delta))
                                if trace_case is None and left_ok:
                                    trace_case = (section, p, j, dimension, delta, g[-1])
    report["max_quotient"] = max_q
    report["nonzero"] = len(nonzero)
    return report, problems, nonzero, trace_case, sensitive


def trace_oracle(R, word, case):
    """One published nonzero row, priced from apply_move plus a fresh trace."""
    section, p, j, dimension, delta, frame = case
    require(word[section][p][0] == "add", "trace witness is not an ADD")
    middle = R.apply_move(word, section, p, p + 2, frame)
    nodes, where, _bill = R.tracing(middle)
    gates = middle[section]
    lo = hi = None
    for a, b in R.segments(middle, section):
        if a <= p < b:
            lo, hi = a, b
    occ = defaultdict(list)
    for i in range(lo, hi):
        for r in R.touched(gates[i]):
            occ[r].append(i)
    removal = [0] * 10
    regs = tuple(R.touched(gates[j]))
    for r in regs:
        seq = nodes[r]
        pos = where[((section, j), r)]
        before, fr = seq[pos][2], seq[pos][3]
        after = seq[pos + 1][3]
        removal[R.rank(fr) - R.rank(before)] -= 1
        removal[R.rank(after) - R.rank(fr)] -= 1
        removal[R.rank(after) - R.rank(before)] += 1
    masks = []
    for r in regs:
        idxs = [x for x in occ[r] if x != j]
        k = bisect_left(idxs, p + 1)
        if k:
            before = R.span(tuple(gates[idxs[k - 1]][-1]))
        else:
            before = nodes[r][where[((section, occ[r][0]), r)]][2]
        if k < len(idxs):
            after = R.span(tuple(gates[idxs[k]][-1]))
        else:
            last = occ[r][-1]
            after = nodes[r][where[((section, last), r)] + 1][3]
        masks.append((before, after))
    low = R.join(masks[0][0], masks[1][0])
    high = masks[0][1] & masks[1][1]
    require(R.contained(low, high), "trace witness interval empty")
    require(R.rank(low) <= dimension <= R.rank(high), "trace witness dimension")
    row = removal
    for before, after in masks:
        a, b = R.rank(before), R.rank(after)
        row[b - a] -= 1
        row[dimension - a] += 1
        row[b - dimension] += 1
    row[0] = 0
    require(tuple(row) == delta, "trace oracle delta " + repr(tuple(row)))


def synthetic_controls(R):
    """Known lattice and a crossing identity that does not use the big words."""
    zero = 1
    cube = R.span((1, 2, 4))
    require([one_vector_counts(zero, cube, R.rank)[d] for d in range(4)] == [1, 7, 7, 1],
            "F2^3 frame lattice")
    line = R.span((1,))
    reps, covered = quotient_basis(line, cube)
    require(len(reps) == 2 and sum(1 << x for x in covered) == cube, "quotient basis")
    require([gauss(2, k) for k in range(3)] == [1, 3, 1], "gauss F2^2")
    # Two disjoint ADDs cross; two ADDs sharing a destination/source do not.
    def add(d, s):
        return ["add", d, s, 1, 1, [1]]
    require(R.crosses(add(1, 2), add(3, 4)) and R.crosses(add(3, 4), add(1, 2)),
            "disjoint cross")
    require(not R.crosses(add(1, 2), add(2, 3)), "shared register blocks")
    # Every disjoint ADD pair crosses, because touched sets are the two endpoints.
    for d1, s1, d2, s2 in ((1, 2, 3, 4), (7, 7, 8, 9), (0, 5, 5, 0)):
        left, right = add(d1, s1), add(d2, s2)
        disjoint = {d1, s1}.isdisjoint({d2, s2})
        require(disjoint == (R.crosses(left, right) and R.crosses(right, left)),
                "disjoint crossing algebra")
    # A rightward scale crossing multiplies the coefficient.
    word_gate = ["add", 0, 1, 3, 2, [1]]
    scale = ["scale", 0, 2, 1, [1]]
    coefficient = Fraction(word_gate[3], word_gate[4]) * Fraction(scale[2], scale[3])
    require(coefficient == Fraction(3, 1), "scale factor")


def main():
    for name, digest in DIGESTS.items():
        raw = (HERE / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, name)
    R = load_retiming()
    synthetic_controls(R)
    summaries = {}
    for tag, name in (("base", "inputs/BORROW-WORD-43base.json.gz"),
                      ("extra", "inputs/BORROW-WORD-43extra.json.gz")):
        word = load_word(name)
        report, problems, nonzero, trace_case, sensitive = analyze(R, word)
        require(not problems, tag + " " + repr(problems[:6]))
        require(report["fixed_pairs"] == 4709, tag + " fixed pair count")
        require(report["bridge"] == 14966, tag + " bridge count")
        require(report["bridge_dimensions"] == 14693, tag + " bridge dimensions")
        require(report["max_quotient"] == 3, tag + " quotient")
        require(report["unequal_shared"] == 181, tag + " unequal shared")
        got = tuple(nonzero)
        require(got == PUBLISHED_NONZERO, tag + " nonzero rows " + repr(got))
        for _section, _p, _j, _dimension, delta in got:
            require(R.all_power_nonnegative(delta), tag + " bridge row improves")
        require(sensitive is not None, tag + " localisation control was vacuous")
        require(trace_case is not None, tag + " no trace witness")
        trace_oracle(R, word, trace_case)
        # Dropping the touch-both overwrite must move the published nonzero row.
        require(trace_case[4] != (0,) * 10, "witness delta is zero")
        summaries[tag] = {k: report[k] for k in (
            "fixed_pairs", "bridge", "bridge_dimensions", "legal_interior",
            "only_left", "only_right", "neither", "unequal_shared",
            "intervals", "max_quotient", "nonzero", "quotient_0",
            "quotient_1", "quotient_2", "quotient_3", "adds",
            "legality_oracle")}
    print("PASS_STAGED544_TWO_ADD_GAP_REVIEW", json.dumps(summaries, sort_keys=True))


if __name__ == "__main__":
    main()
