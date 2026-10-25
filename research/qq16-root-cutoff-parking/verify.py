#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact corroboration of the root-dependent QQ16 parking/row-depth proof.

No floating point, numerical root search, native payload or predecessor replay.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
import argparse
from bisect import bisect_right
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from source_probe import check_source, need

DIMENSION = 73
ROW_FACTOR = 14336
SHIFT = Q(3456, 25)
CUTOFFS = (73, 74, 145, 146, 355, 356, 357, 511, 512, 1024)
WIDTH_LIMIT = 8192


def receipt_matches(raw, expected):
    def unique(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate receipt key")
            result[key] = value
        return result

    def no_float(value):
        raise ValueError("receipt numbers must be exact integers: "+value)

    saved = json.loads(raw, object_pairs_hook=unique, parse_float=no_float,
                       parse_constant=no_float)
    need(json.dumps(saved, sort_keys=True) == json.dumps(expected, sort_keys=True),
         "complete typed committed receipt")


def authenticate():
    manifest = json.loads((HERE/"SOURCES.json").read_text())
    raw = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            value = (ROOT/row["path"]).read_bytes()
            need(sha256(value).hexdigest() == row["sha256"], "source digest: "+row["path"])
            raw[row["path"]] = value
    result = json.loads(raw["research/qq16-nonterminal-c8-tree/RESULT.json"])
    ranks = {int(r): n for r, n in result["rank_histogram"].items()}
    need(ranks == {1:349604, 2:60192, 3:62585, 4:20448,
                   5:11808, 7:7, 8:1152, 48:4866}, "inherited complete histogram")
    return ranks, raw["research/physical-complex-controller/machine.py"].decode()


def cutoff(root):
    """Exact ceil(root**(1/1000)), with the source's width-73 floor."""
    need(type(root) is int and root >= 1 and root.bit_length() <= 21000,
         "bounded positive global root")
    lo, hi = 0, 1 << ((root.bit_length()+999)//1000)
    while hi-lo > 1:
        middle = (lo+hi)//2
        if middle**1000 >= root:
            hi = middle
        else:
            lo = middle
    return max(73, hi)


def longest(width, threshold):
    path = []
    while width >= threshold:
        need(len(path) < 40000, "depth resource cap")
        path.append(width)
        width = 48*(width//73)
    return path, width


def inverse_thresholds(width, threshold):
    """Smallest widths reaching successive division depths; includes sentinel."""
    levels = [threshold]
    while levels[-1] <= width:
        need(len(levels) < 40000, "inverse-depth resource cap")
        levels.append(73*((levels[-1]+47)//48))
    return levels


def depth_bounds(width, threshold, depth):
    if width < threshold:
        need(depth == 0, "terminal depth")
        return
    # Equivalent to the displayed logarithmic bounds, entirely integral.
    need((25*width+3456)*48**depth <= (25*(threshold-1)+3456)*73**depth,
         "affine lower bound on depth")
    need(width*48**(depth-1) >= threshold*73**(depth-1),
         "multiplicative upper bound on depth")


def tables(ranks, threshold):
    mass = [Q(0)]*(WIDTH_LIMIT+1)
    leaves = [Q(1)]*(WIDTH_LIMIT+1)
    depths = [0]*(WIDTH_LIMIT+1)
    thresholds = inverse_thresholds(WIDTH_LIMIT, threshold)
    c = Q(sum(ranks.values()), ROW_FACTOR)
    for width in range(threshold, WIDTH_LIMIT+1):
        children = [(r*(width//73), n) for r, n in ranks.items()]
        mass[width] = 1+sum((Q(n, ROW_FACTOR)*mass[v] for v, n in children), Q(0))
        leaves[width] = sum((Q(n, ROW_FACTOR)*leaves[v] for v, n in children), Q(0))
        depths[width] = 1+max(depths[v] for v, _ in children)
        need(depths[width] == 1+depths[48*(width//73)], "maximum-rank path is attained")
        need(leaves[width] == 1+(c-1)*mass[width], "weighted leaf/internal identity")
        need(depths[width] >= depths[width-1], "depth monotonicity")
        need(depths[width] == bisect_right(thresholds, width), "inverse threshold oracle")
        depth_bounds(width, threshold, depths[width])
    return mass, leaves, depths


def census(ranks, width, threshold):
    """Independent integer path counting by breadth, with Gamma symbolic."""
    frontier = Counter({width:1})
    internal, leaves, rows = Q(0), Q(0), []
    for depth in range(64):
        if not frontier:
            return internal, leaves, rows
        need(len(frontier) <= 4096, "frontier resource cap")
        active = sum(n for w, n in frontier.items() if w >= threshold)
        terminal = sum(n for w, n in frontier.items() if w < threshold)
        internal += Q(active, ROW_FACTOR**depth)
        leaves += Q(terminal, ROW_FACTOR**depth)
        rows.append((active, terminal))
        successor = Counter()
        for w, paths in frontier.items():
            if w < threshold:
                if depth:
                    need(threshold//73 <= w < threshold, "terminal width interval")
                continue
            for rank, n in ranks.items():
                successor[rank*(w//73)] += paths*n
        frontier = successor
    raise ValueError("census depth resource cap")


def stock_and_volume(ranks, width, threshold, mass, rows):
    path, _ = longest(width, threshold)
    depth = len(path)
    total = sum(ranks.values())
    for gamma in (1, 2, 7):
        f = ROW_FACTOR*gamma
        incoming = f**depth
        remaining = incoming
        for _ in path:
            remaining, remainder = divmod(remaining, f)
            need(remainder == 0 and remaining > 0, "sufficient positive stock")
        need(remaining == 1, "minimal stock reaches one at terminal depth")
        if depth:
            remaining = incoming//f
            for _ in path[:-1]:
                remaining //= f
            need(remaining == 1 and remaining % f != 0, "one-short stock fails")
            need(incoming+1 > incoming and (incoming+1) % f != 0,
                 "a size bound cannot replace exact divisibility")
        # The proof allows any admitted complete-bank volume v.
        paid = sum(active*gamma**j*(total*gamma)*Q(incoming, f**j)
                   for j, (active, _) in enumerate(rows))
        need(paid == total*gamma*incoming*mass, "full-volume Gamma cancellation")


def controls(ranks, source):
    rejected = []
    for name, changed in (
        ("height equality made terminal", source.replace(
            'if compare(test, self.c("root_width")) < 0:',
            'if compare(test, self.c("root_width")) <= 0:')),
        ("child resets global cutoff", source.replace(
            'else self.c(name)', 'else width if name == "root_width" else self.c(name)')),
        ("child omits row division", source.replace(
            'self.c("unused") if name == "rows"', 'self.c("rows") if name == "rows"')),
        ("child omits spectator tail", source.replace(
            'after.add(self.c("after"))', 'after = self.c("after")')),
    ):
        need(changed != source, "source mutation applied")
        try:
            check_source(changed, ranks, (73, 356))
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("source mutation survived: "+name)
    need(cutoff(356**1000+1) == 357, "moving cutoff distinguishes fixed-356 shortcut")
    rejected.append("frozen 356 used for every root")
    need(len(longest(356, 356)[0]) == 1 and len(longest(292, 356)[0]) == 0,
         "retesting reached remainder-stripped program changes tree")
    rejected.append("height retested after remainder stripping")
    need((SHIFT-Q(1,25))*25 < 48*72, "too-small affine shift fails")
    rejected.append("affine floor shift reduced below its allowed residue")
    need(len(longest(584, 356)[0]) == 2 and 8*(584//73) < 356,
         "dropping the positive rank-48 class underestimates depth")
    rejected.append("rank-48 child omitted from maximum depth")
    need(inverse_thresholds(584,356)[:2] == [356,584]
         and len(longest(73*(356//48),356)[0]) == 1,
         "inverse child threshold requires ceiling, not floor")
    rejected.append("inverse depth threshold rounded downward")
    for label, raw in (("boolean/integer receipt confusion", '{"x":[true]}'),
                       ("floating/integer receipt confusion", '{"x":[1.0]}'),
                       ("duplicate receipt key", '{"x":[1],"x":[1]}')):
        try:
            receipt_matches(raw, {"x":[1]})
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("receipt mutation survived: "+label)
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    ranks, source = authenticate()
    total = sum(ranks.values())
    c = Q(total, ROW_FACTOR)
    need(c > 1 and Q(sum(r*n for r,n in ranks.items()), 73*ROW_FACTOR) < 1,
         "unique moment exponent in (0,1)")
    shifts = [Q(r*delta, 73-r) for r in ranks for delta in range(73)]
    need(max(shifts) == SHIFT, "sharp affine residue constant")
    root_cases = []
    for k in (2, 72, 73, 74, 145, 356, 357, 1024, 4096, 10**6):
        for offset in (-1, 0, 1):
            d = k**1000+offset
            expected = max(73, k+(offset == 1))
            need(cutoff(d) == expected, "exact 1000th-power boundary")
            root_cases.append([k, offset, expected])
    sample_rows = []
    for t in CUTOFFS:
        mass, leaves, depths = tables(ranks, t)
        for w in sorted({t-1, t, t+1, 583, 584, 8192, 65536}):
            h, leaf, rows = census(ranks, w, t)
            need(leaf == 1+(c-1)*h, "breadth leaf identity")
            if w <= WIDTH_LIMIT:
                need(h == mass[w] and leaf == leaves[w], "independent breadth/DP agreement")
            stock_and_volume(ranks, w, t, h, rows)
            sample_rows.append({"cutoff": t, "width": w, "mass": str(h),
                                "depth": len(longest(w,t)[0])})
    d = isqrt(1 << 16949)
    t = cutoff(d)
    actual, last = longest(d,t)
    coarse, coarse_last = longest(d,73)
    reverse = inverse_thresholds(d,t)
    need(len(reverse)-1 == len(actual) and reverse[-2] <= d < reverse[-1],
         "independent giant-root inverse threshold")
    need((t,len(actual),len(coarse),last,coarse_last) == (356,13997,13999,240,48),
         "historical exact global-root depth")
    depth_bounds(d,t,len(actual))
    receipt = {
        "status": "PASS_QQ16_ROOT_CUTOFF_PARKING",
        "claim_kind": "scoped proof with exact finite corroboration",
        "dp_cutoffs": list(CUTOFFS), "dp_widths_per_cutoff": WIDTH_LIMIT+1,
        "affine_residue_cases": len(shifts), "root_boundaries": root_cases,
        "breadth_censuses": sample_rows,
        "source_descriptor_probe": check_source(source, ranks, CUTOFFS),
        "historical_root": {"definition": "isqrt(2**16949)", "cutoff": t,
                            "exact_division_depth": len(actual),
                            "coarse_division_depth": len(coarse),
                            "last_internal_threshold_hex_sha256": sha256(
                                hex(reverse[-2]).encode()).hexdigest(),
                            "next_threshold_hex_sha256": sha256(
                                hex(reverse[-1]).encode()).hexdigest()},
        "rejected_controls": controls(ranks,source),
        "stock_gamma_calibrations": [1,2,7],
        "histogram_census_replayed": False, "physical_execution": False,
        "full_cost_sign": "unresolved", "new_kappa": False,
    }
    target = HERE/"RESULT.json"
    if args.write:
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    else:
        receipt_matches(target.read_text(), receipt)
    print(receipt["status"])
    print(json.dumps({k:receipt[k] for k in ("historical_root", "source_descriptor_probe",
                                            "dp_widths_per_cutoff", "rejected_controls")},
                     sort_keys=True))


if __name__ == "__main__":
    main()
