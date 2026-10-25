#!/usr/bin/env python3
"""The fixed L/2 firing set at n = 5 beyond length 16: flat cap and census.

Model of #4322: canonical first-occurrence words on F_2^n, simple restored prefix walks,
universal when the difference set of the prefix states is all of F_2^n; a nonzero mask fires
when base < excess <= base + d^2, base(n, L) = (L/2)(L/2 - 1) - (2^(n-1) - 1).
This file proves soundness at n = 5 for L >= 26 by the 16-point flat cap, reruns the small
census in Python, and checks the recorded runs of census.c (local evidence) against #3699,
#3733 and #4322 on main or vendored, and for the new lengths. No code from #4322.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDORED_SHA256 = "b4f7196a7dff95973ce1c5ea52628fda5c992dc2cd7bde58734d4fe886bf33e0"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def base(n, L):
    return (L // 2) * (L // 2 - 1) - ((1 << (n - 1)) - 1)


def excess(points):
    diffs, k = set(), len(points)
    for i in range(k):
        for j in range(i + 1, k):
            diffs.add(points[i] ^ points[j])
    return k * (k - 1) // 2 - len(diffs)


def flat_caps(dim):
    """max excess of a k-subset of F_2^dim, every k, by full enumeration"""
    caps = [0] * ((1 << dim) + 1)
    for s in range(1 << (1 << dim)):
        pts = [x for x in range(1 << dim) if s >> x & 1]
        caps[len(pts)] = max(caps[len(pts)], excess(pts))
    return caps


def census(n, L):
    """(closed, universal, prunes, per-mask counts) over canonical words"""
    out = [0, 0, 0, {}]
    full = (1 << (1 << n)) - 1
    b = base(n, L)

    def rec(depth, state, visited, top, states):
        if depth == L:
            if state:
                return
            out[0] += 1
            diff = 0
            for x in states:
                for y in states:
                    diff |= 1 << (x ^ y)
            if diff != full:
                return
            out[1] += 1
            for m in range(1, 1 << n):
                sides = ([], [])
                for x in states:
                    sides[bin(x & m).count("1") & 1].append(x)
                e = excess(sides[0]) + excess(sides[1])
                d = (len(sides[0]) - len(sides[1])) // 2
                if b < e <= b + d * d:
                    out[2] += 1
                    out[3][m] = out[3].get(m, 0) + 1
            return
        for lab in range(min(top + 1, n - 1) + 1):
            nxt = state ^ (1 << lab)
            if depth == L - 1:
                if nxt == 0:
                    rec(depth + 1, 0, visited, max(top, lab), states)
            elif not visited >> nxt & 1:
                rec(depth + 1, nxt, visited | 1 << nxt, max(top, lab), states + [nxt])
    rec(0, 0, 1, -1, [0])
    return out


def main():
    # 1. the flat cap: at n = 5 a level set is an affine 4-flat, so a split (s, t) has excess <= e(s) + e(t)
    caps = flat_caps(4)
    need(caps == [0, 0, 0, 0, 3, 3, 8, 14, 21, 21, 30, 40, 51, 63, 76, 90, 105], "16-point flat caps")
    need(flat_caps(3) == [0, 0, 0, 0, 3, 3, 8, 14, 21], "8-point caps agree with #4322's table")
    open_lengths = []
    for L in range(12, 33, 2):
        live = [s for s in range(max(0, L - 16), min(16, L) + 1) if caps[s] + caps[L - s] > base(5, L)]
        if live:
            open_lengths.append(L)
    need(open_lengths == [12, 14, 16, 18, 20, 22, 24], "cap proves every subset sound at n = 5 exactly from L = 26")

    # 2. small census in Python, against #3699 / #3733 on main
    d3699 = {(r["n"], r["L"]): r for r in json.loads((ROOT / "research/f7-bit0-functional-classification/RESULT.json").read_text())["domains"]}
    d3733 = {(r["n"], r["L"]): r for r in json.loads((ROOT / "research/f7-functional-independent-check/RESULT.json").read_text())["new_domains"]}
    published = {k: {int(m): v["count"] for m, v in r["records"].items()} for k, r in d3699.items() if k[0] >= 4}
    published.update({k: {int(m): c for m, c in r["per_mask_counts"].items()} for k, r in d3733.items() if k[0] >= 4})
    raw = (HERE / "vendor/pr4322-verify.py").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == VENDORED_SHA256, "vendored #4322 verify.py")
    expected_5_16 = ast.literal_eval(re.search(r"EXPECTED_5_16 = (\{.*?\})\n", raw.decode(), re.S).group(1))
    published[5, 16] = expected_5_16
    totals = {}
    for key in [(4, 8), (4, 10), (4, 12), (4, 14), (4, 16), (5, 12), (5, 14), (5, 16)]:
        closed, univ, prunes, per = census(*key)
        totals[key] = (closed, univ, prunes)
        if key in published:
            need(per == published[key], f"Python census {key} matches the published per-mask row")
        else:
            need(prunes == 0, f"Python census {key}: nothing fires (#4322's theorem)")
    need(totals[5, 16] == (267890, 263140, 447912), "Python census (5,16) totals match #4322")

    # 3. recorded C runs: bound to census.c, matching every published row, then the new lengths
    text = (HERE / "evidence/CENSUS-RUNS.txt").read_text()
    need(f"census.c (SHA256 {hashlib.sha256((HERE / 'census.c').read_bytes()).hexdigest()})" in text, "runs recorded for this census.c")
    runs, cur = {}, None
    for line in text.splitlines():
        if line.startswith("n="):
            f = dict(kv.split("=") for kv in line.split())
            cur = (int(f["n"]), int(f["L"]))
            runs[cur] = {"closed": int(f["closed"]), "universal": int(f["universal"]),
                         "prunes": int(f["prunes"]), "firing": int(f["firing_masks"]), "per": {}}
        elif line.startswith("mask "):
            _, m, c = line.split()
            runs[cur]["per"][int(m)] = int(c)
    for key, row in published.items():
        if key in runs:
            need(runs[key]["per"] == row, f"C census {key} matches the published row")
    need(runs[5, 16]["per"] == expected_5_16 and (runs[5, 16]["closed"], runs[5, 16]["universal"], runs[5, 16]["prunes"]) == totals[5, 16], "C census (5,16) matches #4322 and the Python census")
    new = {L: runs[5, L] for L in (18, 20, 22, 24)}
    sets = {L: set(runs[5, L]["per"]) for L in (12, 14, 16, 18, 20, 22, 24)}
    order = sorted(sets)
    need([len(sets[L]) for L in order] == [24, 25, 25, 28, 30, 30, 28], "n = 5 firing-set sizes 24, 25, 25, 28, 30, 30, 28")
    need(all(sets[a] <= sets[b] for a, b in zip(order[:-1], order[1:-1])), "n = 5 firing sets nested from 12 through 22")
    need(sets[22] == set(range(1, 31)), "at L = 22 every mask but 31 fires")
    need(sets[24] == sets[22] - {15, 23}, "at L = 24 masks 15 and 23 fall silent: the n = 5 firing set is not monotone")
    need(all(r["closed"] == r["universal"] for L, r in new.items()), "from L = 18 every closed word is universal")
    need(runs[5, 24]["prunes"] > 0, "something still fires at L = 24, so with the cap the first all-sound length is 26")
    # at L = 24 the cap leaves only the (8, 16) split: every firing word there contains a whole level set of its mask
    need([s for s in range(8, 17) if caps[s] + caps[24 - s] > base(5, 24)] == [8, 16], "L = 24: only the 8/16 split survives the cap")

    print(json.dumps({
        "status": "PASS_F7_FIRING_N5_LENGTH_CENSUS",
        "cap_sound_from": 26,
        "cap_open_lengths": open_lengths,
        "n5": {str(L): {k: v for k, v in r.items() if k != "per"} for L, r in sorted(new.items())},
        "first_all_sound_length_n5": 26,
        "silent_at_24": sorted(set(range(1, 32)) - sets[24]),
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
