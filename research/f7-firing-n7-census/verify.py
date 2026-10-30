#!/usr/bin/env python3
"""The fixed L/2 firing census at n = 7, L = 18 and 20 (#4322's open question 2), and n = 6 to L = 20.

Model of #4322: canonical first-occurrence words on F_2^n, simple restored prefix walks, universal when the
difference set of the prefix states is all of F_2^n; a nonzero mask fires on a universal word when
base < excess <= base + d^2, base = (L/2)(L/2-1) - (2^(n-1)-1). A mask can fire only on a universal word.
This file reruns small domains in Python against #3699 on main, checks the recorded census.c runs
(local evidence; 128-bit state masks), and runs seeded random-walk controls at n = 7.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def census(n, L):
    """(closed, universal) over canonical simple restored words"""
    out = [0, 0]
    full = 1 << n

    def rec(depth, state, visited, top, states):
        if depth == L:
            if state == 0:
                out[0] += 1
                if len({a ^ b for a in states for b in states}) == full:
                    out[1] += 1
            return
        for lab in range(min(top + 1, n - 1) + 1):
            nxt = state ^ (1 << lab)
            if depth == L - 1:
                if nxt == 0:
                    rec(depth + 1, 0, visited, max(top, lab), states)
            elif not visited >> nxt & 1:
                rec(depth + 1, nxt, visited | 1 << nxt, max(top, lab), states + [nxt])
    rec(0, 0, 1, -1, [0])
    return tuple(out)


def random_walks(n, L, count, seed):
    """seeded random closed simple walks; how many are universal"""
    rng, found, made = random.Random(seed), 0, 0
    while made < count:
        st, seen, cur, ok = [0], {0}, 0, True
        for step in range(L - 1):
            opts = [cur ^ (1 << b) for b in range(n) if (cur ^ (1 << b)) not in seen]
            if step == L - 2:
                opts = [o for o in opts if bin(o).count("1") == 1]
            if not opts:
                ok = False
                break
            cur = rng.choice(opts)
            st.append(cur)
            seen.add(cur)
        if ok:
            made += 1
            found += len({a ^ b for a in st for b in st}) == 1 << n
    return found


def main():
    # 1. Python census against #3699's published zero-universal domains on main
    pub = {(r["n"], r["L"]): (r["simple_closed_words"], r["universal_words"])
           for r in json.loads((ROOT / "research/f7-bit0-functional-classification/RESULT.json").read_text())["domains"]}
    for key in [(6, 12), (6, 14), (7, 14)]:
        need(census(*key) == pub[key], f"Python census {key} equals #3699 {pub[key]}")

    # 2. recorded census.c runs
    text = (HERE / "evidence/CENSUS-RUNS.txt").read_text()
    need(f"census.c (SHA256 {hashlib.sha256((HERE / 'census.c').read_bytes()).hexdigest()})" in text, "runs recorded for this census.c")
    runs = {}
    for line in text.splitlines():
        if line.startswith("n="):
            f = dict(kv.split("=") for kv in line.split())
            runs[int(f["n"]), int(f["L"])] = {k: int(f[k]) for k in ("closed", "universal", "prunes", "firing_masks")}
    for key, (closed, universal) in pub.items():
        if key in runs:
            need((runs[key]["closed"], runs[key]["universal"]) == (closed, universal), f"C census {key} equals #3699")
    need(runs[5, 14]["closed"] == 33922 and runs[5, 14]["universal"] == 24787 and runs[5, 14]["prunes"] == 56686, "C census (5,14) equals #3733")
    need(runs[6, 16]["closed"] == 2262380, "C census (6,16) equals #4322's 2,262,380 closed words")
    for L in (16, 18, 20):
        need(runs[7, L]["universal"] == 0 and runs[7, L]["prunes"] == 0, f"(7,{L}): no universal word, so nothing fires")
    need(runs[7, 18]["closed"] == 133421988 and runs[7, 20]["closed"] == 3857028444, "(7,18) and (7,20) closed counts")

    # 3. controls at n = 7: random walks do find universal words at L = 26, none at L = 20
    need(random_walks(7, 26, 20000, 4322) > 0, "positive control: universal walks exist at (7,26)")
    need(random_walks(7, 20, 20000, 4322) == 0, "random corroboration: none at (7,20)")
    six = {L: runs[6, L] for L in (16, 18, 20) if (6, L) in runs}
    print(json.dumps({
        "status": "PASS_F7_FIRING_N7_CENSUS",
        "n7": {str(L): runs[7, L] for L in (14, 16, 18, 20)},
        "n6": {str(L): r for L, r in six.items()},
        "answer_4322_oq2": "no functional fires at (7,18) or (7,20): neither domain has a universal word",
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
