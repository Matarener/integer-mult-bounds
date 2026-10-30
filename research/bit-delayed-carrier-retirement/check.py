#!/usr/bin/env python3
"""Exact source-bound delayed carrier retirement; Apache-2.0.

Ross Richardson, with substantial OpenAI Codex assistance.
No predecessor imports, finite-address samples, or external dependencies.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parent
N = 660
PINS = {
    "WORD.json.gz": "c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c",
    "GEOMETRY.json.gz": "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
}
DELETED = {53, 20255, 20256, 23408, 23409, 33620}
MOVED = {23405, 23406, 23407, 23515, 24189, 24190, 24515}
CONTEXT = {
    53: [1, 413, 469, -1, 0, 30],
    19794: [1, 221, 657, 1, 0, 10],
    20255: [0, 469, 0, 52, 1, 0],
    20256: [1, 469, 50, 1, 52, 2],
    23405: [0, 413, 509, 390, 2, 0],
    23406: [1, 413, 605, 1, 390, 2],
    23407: [0, 413, 390, 517, 1, 0],
    23408: [0, 469, 52, 517, 6, 0],
    23409: [1, 413, 469, 1, 517, 2],
    23515: [1, 478, 413, 1, 517, 2],
    23865: [1, 178, 660, 1, 0, 3],
    23889: [3, 476, 660, 515, 0, 3],
    23947: [2, 478, 660, 517, 0, 3],
    24189: [0, 178, 0, 52, 1, 0],
    24190: [1, 178, 50, 1, 52, 4],
    24515: [0, 50, 52, 509, 3, 0],
    33619: [0, 469, 517, 1, 1, 32],
    33620: [1, 469, 50, -1, 1, 32],
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode()


def digest(x):
    return sha256(canonical(x)).hexdigest()


def add(a, b, scale):
    out = a.copy()
    for j, value in b.items():
        out[j] = out.get(j, 0) + scale * value
        if out[j] == 0:
            del out[j]
    return out


def identities():
    return [{i: 1} for i in range(N)] + [{}]


def reduced(rows):
    return [{j: v % 2 for j, v in row.items() if v % 2} for row in rows]


def compensation(records):
    d = [Counter() for _ in range(N)]
    for op, target, source, coefficient, frame, section in records:
        if section == 10:
            need(op == 1 and frame == 0 and coefficient == 1, "D format")
            d[target][source] += coefficient
    delta = {t: d[t][413] - d[t][444] - d[t][391] for t in range(111, 222)}
    need(all((delta[t] - d[t][469]) % 2 == 0 for t in delta), "Boolean kernel")
    strict = {t: d[t][469] - delta[t] for t in delta}
    need(set(strict.values()) == {0, 2}, "unit signed replacement")
    need(sum(d[t][469] for t in delta) == 55, "55 original D reads")
    need(sum(strict.values()) == 102, "102 strict D reads")
    return d, delta, strict


def construct(word, mode="boolean"):
    """Literal recipe, indexed in the immutable original stream."""
    need(mode in ("boolean", "signed"), "candidate mode")
    records = word["records"]
    for i, expected in CONTEXT.items():
        need(records[i] == expected, "source edit context " + str(i))
    _, _, strict = compensation(records)
    out = []
    for i, record in enumerate(records):
        if i == 33619:
            out.append(("restore", [0, 469, 0, 517, 7, 32]))
        if (i not in DELETED | MOVED
                and not (record[5] == 10 and record[2] == 469)):
            out.append((str(i), record.copy()))
        if i == 19794 and mode == "signed":
            for t, coefficient in sorted(strict.items()):
                for j in range(coefficient):
                    out.append((f"comp:{t}:{j}", [1, t, 469, 1, 0, 10]))
        if i == 23889:
            out.extend((str(j), records[j].copy()) for j in (24189, 24190, 24515))
            out.append(("direct", [1, 413, 50, 1, 509, 2]))
            out.extend((str(j), records[j].copy()) for j in (23405, 23406, 23407, 23515))
    return out


def replay(word, tagged, inverse=False, initial=None, majorant=False):
    rows = identities() if initial is None else [x.copy() for x in initial]
    frames = word["final" if inverse else "start"][:] + [None]
    opened = None
    peak, copies = 1, 0
    ordered = reversed(tagged) if inverse else tagged
    for tag, (op, d, s, c, f, section) in ordered:
        if op == 0:
            before, after = (c, s) if inverse else (s, c)
            need(frames[d] == before, "MOVE frame at " + tag)
            need(opened is None, "recursive MOVE inside live COPY at " + tag)
            frames[d] = after
        elif op == 1:
            need(d != s and d < N and s <= N and c in (-1, 1), "unit ADD at " + tag)
            need(frames[d] == frames[s] == f, "ADD frame at " + tag)
            need(d != opened, "COPY source mutation at " + tag)
            coefficient = 1 if majorant else (-c if inverse else c)
            rows[d] = add(rows[d], rows[s], coefficient)
            peak = max(peak, sum(abs(v) for v in rows[d].values()))
        elif op == (3 if inverse else 2):
            need(s == N and opened is None and not rows[N], "COPY zero at " + tag)
            need(frames[d] == c and frames[N] is None, "COPY frame at " + tag)
            opened, rows[N], frames[N] = d, rows[d].copy(), f
            copies += 1
        else:
            need(op == (2 if inverse else 3), "known opcode")
            need(s == N and opened == d and frames[d] == c and frames[N] == f,
                 "ERASE frame/source at " + tag)
            need(rows[N] == rows[d], "ERASE equality at " + tag)
            opened, rows[N], frames[N] = None, {}, None
    need(opened is None and not rows[N] and frames[N] is None, "private restoration")
    need(frames[:N] == word["start" if inverse else "final"], "final frames")
    return rows, peak, copies


def orthogonal_basis(vectors):
    basis = []
    for raw in vectors:
        v = list(map(F, raw))
        for u in basis:
            c = sum(x*y for x, y in zip(v, u)) / sum(x*x for x in u)
            v = [x-c*y for x, y in zip(v, u)]
        if any(v):
            basis.append(v)
    return basis


def geometry_audit(geom, boundary, words):
    bases, projectors = [], []
    for labels in geom["frames"]:
        basis = orthogonal_basis([geom["lines"][i] for i in labels])
        bases.append(basis)
        p = [[sum((u[i]*u[j]/sum(x*x for x in u) for u in basis), F(0))
              for j in range(8)] for i in range(8)]
        need(all(x.denominator & (x.denominator-1) == 0 for r in p for x in r),
             "dyadic projector")
        projectors.append(p)
    need(len(bases[0]) == 0 and len(bases[1]) == 8, "ZERO/FULL")
    pairs = set()
    for tagged in words:
        for _, (op, d, s, c, f, section) in tagged:
            if op == 0:
                need(len(bases[c])-len(bases[s]) == f > 0, "MOVE exact rank")
                pairs.add((s, c))
            elif op in (2, 3):
                need(len(bases[c]) == 7 and len(bases[f]) == 0, "COPY rank seven")
                pairs.add((f, c))
    for a, b in sorted(pairs):
        p = projectors[b]
        for v in bases[a]:
            need([sum(p[i][j]*v[j] for j in range(8)) for i in range(8)] == v,
                 f"nested frames {a},{b}")
    widths = [len(bases[b])-len(bases[a])
              for a, b in zip(boundary["start"][222:], boundary["final"][222:])]
    need(Counter(widths) == {8: 433, 4: 5}, "complete helper widths")
    return {"frames": len(bases), "nested_pairs": len(pairs),
            "all_projectors_dyadic": True, "helper_widths": dict(Counter(widths)),
            "retired_helper_width": widths[469-222],
            "new_query_rank": len(bases[517])-len(bases[0]),
            "largest_query_rank": 7, "local_parent_dimension": 8}


def invoice(tagged):
    h, adds, copies = Counter(), 0, 0
    for _, (op, d, s, c, f, section) in tagged:
        if op == 0:
            h[f] += 1
        elif op == 2:
            h[7] += 1
            copies += 1
        elif op == 1:
            adds += 1
    return {"histogram": dict(sorted(h.items())), "queries": sum(h.values()),
            "rank_mass": sum(r*n for r, n in h.items()), "adds": adds,
            "copy_erase_pairs": copies, "records": len(tagged),
            "word_sha256": digest([g for _, g in tagged])}


def log_interval(q):
    """Positive rational atanh series; reduce q to [1,2)."""
    e = 0
    while q >= 2:
        q /= 2
        e += 1

    def series(x):
        t = (x-1)/(x+1)
        s = 2*sum((t**(2*k+1)/F(2*k+1) for k in range(40)), F(0))
        return s, s + 2*t**81/(81*(1-t*t))

    lo, hi = series(q)
    l2, u2 = series(F(2))
    return lo+e*l2, hi+e*u2


def exp_interval(lo, hi):
    def partial(x):
        term, total = F(1), F(1)
        for k in range(1, 25):
            term *= x/k
            total += term
        return total, term*x/25
    low, _ = partial(lo)
    high, next_term = partial(hi)
    need(0 <= lo <= hi < 1, "exp range")
    return low, high + next_term/(1-hi/26)


def price_interval(r):
    lo, hi = log_interval(F(64, r))
    lo, hi = exp_interval(lo/500, hi/500)
    return r*lo, r*hi


def floor_scaled(x, scale):
    return (x.numerator*scale)//x.denominator


def pricing():
    l1, u1 = price_interval(1)
    l6, u6 = price_interval(6)
    l7, u7 = price_interval(7)
    lo, hi = l1+l6-u7, u1+u6-l7
    scale = 10**24
    lower, upper = floor_scaled(lo, scale), floor_scaled(hi, scale)+1
    need(F(lower, scale) > 0 and upper-lower <= 2, "strict outward price bracket")
    return {"m": 64, "b": "1/500", "saving_lower": str(F(lower, scale)),
            "saving_upper": str(F(upper, scale)),
            "formula": "Phi_m(1) + Phi_m(6) - Phi_m(7)",
            "all_parameter_domain": "m>0 and 0<b<1"}


def controls(word, base_rows, boolean):
    """Each mutant targets an actual restoration, access or dirt obligation."""
    results = {}

    def rejected(name, tagged, expected=None, initial=None):
        try:
            rows, _, _ = replay(word, tagged, initial=initial)
        except ValueError as error:
            if expected is not None:
                need(expected in str(error), "wrong control reason: " + name)
            results[name] = str(error)
        else:
            need(expected is None and reduced(rows) != reduced(base_rows),
                 "undetected control: " + name)
            results[name] = "Boolean endpoint differs"

    rejected("omit_direct_source", [(t, g) for t, g in boolean if t != "direct"])
    rejected("omit_rank7_restoration", [(t, g) for t, g in boolean if t != "restore"],
             "MOVE frame")
    rejected("omit_final_rank1_completion", [(t, g) for t, g in boolean if t != "33619"],
             "final frames")
    late_read = []
    for t, g in boolean:
        if t not in ("24189", "24190"):
            late_read.append((t, g))
        if t == "24188":
            late_read.extend([("late178move", word["records"][24189]),
                              ("late178read", word["records"][24190])])
    rejected("early_source_without_target_read", late_read, "ADD frame")
    restored_d = []
    for t, g in boolean:
        restored_d.append((t, g))
        if t == "19794":
            restored_d.extend((f"oldD:{i}", g) for i, g in enumerate(word["records"])
                              if g[5] == 10 and g[2] == 469)
    rejected("retain_old_compensation", restored_d)
    pre = []
    for t, g in boolean:
        pre.append((t, g))
        if t == "52":
            pre.append(("oldprelude", word["records"][53]))
    rejected("retain_old_dirt_subtraction", pre)
    clean = identities()
    clean[N] = {N: 1}
    rejected("dirty_private_copy", boolean, "COPY zero", initial=clean)
    return results


def main():
    inputs = {}
    for name, pin in PINS.items():
        raw = (ROOT/"inputs"/name).read_bytes()
        need(sha256(raw).hexdigest() == pin, "input hash " + name)
        inputs[name] = json.loads(gzip.decompress(raw))
    word, geom = inputs["WORD.json.gz"], inputs["GEOMETRY.json.gz"]
    baseline = [(str(i), r) for i, r in enumerate(word["records"])]
    boolean, signed = construct(word), construct(word, "signed")
    # Independent cut calculation establishes the stated raw-dirt pullback.
    prefix = [r for r in baseline if r[1][5] == 30]
    rows_a, rows_b = identities(), identities()
    for tag, (_, d, s, c, _, _) in prefix:
        rows_a[d] = add(rows_a[d], rows_a[s], c)
        if tag != "53":
            rows_b[d] = add(rows_b[d], rows_b[s], c)
    difference = {i: add(b, a, -1) for i, (a, b) in enumerate(zip(rows_a, rows_b)) if a != b}
    need(difference == {391: {469: -1}, 413: {469: 1}, 444: {469: -1}},
         "prefix pullback")
    d, delta, strict = compensation(word["records"])
    base_rows, _, _ = replay(word, baseline)
    expect = identities()
    for i in range(111):
        expect[111+i][i] = 1
    need(reduced(base_rows) == expect, "baseline Boolean boundary")
    for i in list(range(111)) + list(range(222, N)):
        need(base_rows[i] == {i: 1}, "baseline exact restored row")
    result = {}
    for name, tagged in (("baseline", baseline), ("boolean", boolean), ("signed", signed)):
        rows, peak, copies = replay(word, tagged)
        inverse_rows, inverse_peak, inverse_copies = replay(word, tagged, inverse=True)
        need(copies == inverse_copies == 9, "all nine COPY pairs")
        need(reduced(rows) == reduced(base_rows), name + " Boolean endpoint")
        need(all(rows[i] == base_rows[i] for i in list(range(111))+list(range(222, N))),
             name + " integer source/helper restoration")
        if name == "signed":
            need(rows == base_rows, "complete signed endpoint")
        need(replay(word, tagged, inverse=True, initial=rows)[0] == identities(),
             name + " forward/inverse")
        need(replay(word, tagged, initial=inverse_rows)[0] == identities(),
             name + " inverse/forward")
        _, major_forward, _ = replay(word, tagged, majorant=True)
        _, major_reverse, _ = replay(word, tagged, inverse=True, majorant=True)
        result[name] = dict(invoice(tagged), integer_map_sha256=digest(rows),
                            boolean_map_sha256=digest(reduced(rows)),
                            row_l1={"forward": peak, "inverse": inverse_peak},
                            positive_majorant={"forward": major_forward, "inverse": major_reverse})
    need(result["boolean"]["adds"] == 35947 and result["signed"]["adds"] == 36049,
         "complete scalar invoices")
    need(result["baseline"]["queries"] == 2913 and
         result["boolean"]["queries"] == result["signed"]["queries"] == 2912, "query count")
    need(all(x["rank_mass"] == 5101 for x in result.values()), "complete rank mass")
    expected_histogram = {1: 1321, 2: 1342, 3: 79, 4: 39, 5: 102, 6: 10, 7: 19}
    need(result["boolean"]["histogram"] == result["signed"]["histogram"] == expected_histogram,
         "complete changed histogram and strict child ranks")
    geometry = geometry_audit(geom, word, [baseline, boolean, signed])
    failures = controls(word, base_rows, boolean)
    underpriced = [(t, g[:4]+[6]+g[5:] if t == "restore" else g) for t, g in boolean]
    try:
        geometry_audit(geom, word, [underpriced])
    except ValueError as error:
        need(str(error) == "MOVE exact rank", "wrong underpriced-query rejection")
        failures["underprice_new_query_rank6"] = str(error)
    else:
        raise ValueError("underpriced query accepted")
    report = {"status": "PASS", "inputs": PINS, "input_columns": N,
              "exact_integer_restored_non_targets": 549,
              "prefix_difference": difference,
              "old_compensation_reads": 55, "strict_replacement_unit_reads": 102,
              "strict_replacement_targets": [t for t, c in strict.items() if c],
              "words": result, "geometry": geometry,
              "price": pricing(), "controls": failures,
              "physical_helper_endpoint": "unchanged D_FULL for469, not physical identity",
              "no_new_kappa": True}
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
