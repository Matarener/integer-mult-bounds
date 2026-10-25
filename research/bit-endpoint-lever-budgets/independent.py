#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent second method for bit-endpoint-lever-budgets.

Rebuilds every boundary histogram from the pinned PR589 and #1094 records with its own code, checks that it equals
the histogram in RESULT.json, and recomputes each pass/fail sign at c* - 1e-24, c* and c* + 1e-24 with the separate
interval arithmetic of bit-revision3-levers-seed03/levers.py (ln by atanh prime chains, exp by Taylor with a remainder
bound, outward dyadic rounding). It shares no arithmetic with verify.py, which uses the D/E-diagnostic engine. The
lever definitions, the hosting model and the boundary integers (read from RESULT.json) are shared with verify.py; only
the histogram code and the arithmetic are independent.
Standard library and git only.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5).
"""
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import subprocess
import sys
import types

if not __debug__:
    raise SystemExit("checks use assert; run without -O")

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PINS = {"levers": ("research/bit-revision3-levers-seed03/levers.py", "f2c4c00fc89ab561469df99dc4a20365e989c40e"),
        "assembly": ("research/community-frontier1094-audit/ASSEMBLY.json", "5fd676df060f3b450782fdf5ff5f6beb63a5eeb0"),
        "pr589": ("research/e8-bit-p111-tuned/tune/EXPECTED.json", "e293ddc557742637f9f679f083a1a282d87b1b13")}
GRID = Q(1, 10 ** 24)


def blob(key):
    path, sha = PINS[key]
    raw = subprocess.run(["git", "-C", str(ROOT), "show", BASE + ":" + path], capture_output=True, check=True).stdout
    assert hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == sha, "pinned blob differs: " + path
    return raw


def main(res=None):
    """Raise AssertionError unless every sign in res (default: RESULT.json) is reproduced."""
    lv = types.ModuleType("pinned_levers")
    exec(compile(blob("levers"), str(ROOT / PINS["levers"][0]), "exec"), lv.__dict__)
    asm, rec = json.loads(blob("assembly")), json.loads(blob("pr589"))
    res = res or json.loads((PKG / "RESULT.json").read_text(encoding="utf-8"))
    c = Q(res["endpoint"]["c_star"])
    assert c == Q(921658892752012102303, 5 * 10 ** 23)

    H0 = {int(r): Q(n) for r, n in rec["nine"]["profile"].items()}
    W, m, T, calls = rec["nine"]["bit"]["live"], 64, 32, 288
    assert sum(r * n for r, n in H0.items()) == m * W - 10272
    word = {int(r): n for r, n in rec["word"]["local_histogram"].items()}

    def shift(h, **moves):
        out = dict(h)
        for key, n in moves.items():
            r = int(key[1:])
            out[r] = out.get(r, Q(0)) + Q(n)
            assert out[r] >= 0
        return {r: n for r, n in out.items() if n}

    def bit_sign(h, a):
        return lv.verdict(h, m, Q(W), a, surcharge=True)

    # Own derivation of the record's idle remainder: profile minus 288 shipped words, per replica.
    idle = {r: (H0.get(r, 0) - calls * word.get(r, 0)) / T for r in set(H0) | set(word)}
    assert {r: n for r, n in idle.items() if n} == {2: 435, 4: 444, 6: 444, 7: 666, 42: 9}
    assert max(H0) == 42 and all(2 * 42 ** hd < 64 ** hd for hd in (2, 3, 4))

    a_req = res["requirement"]["rank1_children"]
    b = res["lever_b_copy_charge"]
    x = b["fewer_copies"]["sharp_total_copies"]
    sb = b["two_call_bit_centre_sharing"]["overhead_budget"]
    d40 = res["lever_d_helper_deletion"]["sharp"]["RANK1"]["per_call"]
    dT = res["lever_d_helper_deletion"]["sharp"]["TEMPLATE"]["exhausted_at"]
    k = res["lever_e_local_shape"]["sharp_calls"]
    shared = shift(H0, r7=-1296)

    def deletion(delta, d, upper, base=None):
        h = dict(base or H0)
        for r, n in delta.items():
            h = shift(h, **{"r%d" % r: calls * d * n})
        s = 45 + 9 * d
        if not upper:
            return shift(h, r42=Q(T * 9 * d, 5), r2=-Q(T * 9 * d, 5))
        n, s0 = divmod(s, 5)
        h = shift(h, r42=T * (n - 9), r2=-T * (n - 9))
        return shift(h, **{"r%d" % (2 + 8 * s0): T, "r2": -T}) if s0 else h

    def trimmed(k):
        """#1023's pessimistic bracket: trim one unit from the k largest local children of every call."""
        h, left = dict(H0), k
        for r in sorted(word, reverse=True):
            t = min(left, word[r])
            h = shift(h, **{"r%d" % r: -calls * t})
            if r > 1:
                h = shift(h, **{"r%d" % (r - 1): calls * t})
            left -= t
            if not left:
                return h

    w7 = res["lever_f_width7"]
    k7, kmax = w7["rank1_removed"]["sharp_per_call"], w7["max_per_call_in_this_placement"]
    assert kmax == 666 // 9 == w7["largest_trimmed"]["fails_at"]
    ideal_delta = {1: -1323, 2: -1342, 3: -79, 4: -44, 5: -102, 6: -11, 7: 212, 8: 439}

    def reshaped(kk):
        h = dict(H0)
        for r, n in ideal_delta.items():
            h = shift(h, **{"r%d" % r: kk * n})
        return h

    mine = [(shift(H0, r1=-a_req), "pass"), (shift(H0, r1=-(a_req - 1)), "fail"),
            (shift(H0, r7=-2592, r8=2592), "fail"),
            (shift(H0, r7=-x), "pass"), (shift(H0, r7=-(x - 1)), "fail")]
    for r in ("1", "7", "42"):
        y = sb[r]["total"]
        mine += [(shift(shared, **{"r" + r: y}), "pass"), (shift(shared, **{"r" + r: y + 1}), "fail")]
    mine += [(deletion({1: -8}, d40, True), "pass"), (deletion({1: -8}, d40 - 1, False), "fail"),
             (deletion({1: -2, 2: 2, 3: -1, 7: -1}, dT, False), "fail"),
             (deletion({1: -1, 7: -1}, k7, True), "pass"), (deletion({1: -1, 7: -1}, k7 - 1, False), "fail"),
             (deletion({7: -1}, kmax, False, base=trimmed(kmax)), "fail"),
             (reshaped(k), "pass"), (reshaped(k - 1), "fail")]
    recorded = res["boundary_checks"]
    assert len(recorded) == len(mine), "boundary row count"
    for (h, v), row in zip(mine, recorded):
        assert {str(r): str(n) for r, n in sorted(h.items())} == row["hist"], "histogram rebuilt differently: " + row["label"]
        assert row["verdict"] == v
        for a in (c - GRID, c, c + GRID):
            assert bit_sign(h, a) == v, "independent sign differs: %s at %s" % (row["label"], a)

    # The TEMPLATE deletion model really is exhausted: its rank-7 consumption equals the word's 19 rank-7 climbs.
    assert dT == word[7] == 19

    # Re-hosting: a spare width-8 slot is cheapest in an emptied rank-42 window (per-slot child-cost comparison).
    def ch(r, a):
        return lv.child(r, m, a)
    for a in (c, c + GRID):
        q42 = ((ch(42, a)[0] - ch(2, a)[1]) / 5, (ch(42, a)[1] - ch(2, a)[0]) / 5)
        q28 = ((ch(28, a)[0] - ch(4, a)[1]) / 3, (ch(28, a)[1] - ch(4, a)[0]) / 3)
        q14 = (ch(14, a)[0] - ch(6, a)[1], ch(14, a)[1] - ch(6, a)[0])
        assert q42[1] < q28[0] and q42[1] < q14[0], "re-hosting order"
        # Lever c lemma: trimming one unit from a rank-r child saves less than one rank-1 child.
        assert all(ch(r, a)[1] - ch(r - 1, a)[0] < ch(1, a)[0] for r in range(2, 43))

    # Context: complex side of the same route (no surcharge), boundary signs with levers.py.
    HC = {int(r): Q(n) for r, n in asm["complex_profile"].items()}
    assert HC[8] == 1152
    for row in res["context_complex_at_c_star"]["boundary_checks"]:
        y, r = (int(t) for t in row["label"].split("+ ")[1].split(" rank-")[0:1] +
                [row["label"].split("rank-")[1].split(" ")[0]])
        h = dict(HC)
        h[8] = Q(576)
        h[r] = h.get(r, Q(0)) + y
        assert {str(q): int(n) for q, n in sorted(h.items())} == row["hist"], "complex histogram: " + row["label"]
        for a in (c - GRID, c, c + GRID):
            assert lv.verdict(h, 73, Q(14336), a) == row["verdict"], "complex sign: " + row["label"]
    need = res["context_complex_at_c_star_need"]["net_rank1_children"]
    for x, v in ((need, "pass"), (need - 1, "fail")):
        h = dict(HC)
        h[1] -= x
        for a in (c - GRID, c, c + GRID):
            assert lv.verdict(h, 73, Q(14336), a) == v, "complex need sign: %d at %s" % (x, a)

    print("PASS_BIT_ENDPOINT_LEVER_BUDGETS_INDEPENDENT signs=%d at c*-1e-24, c* and c*+1e-24 (levers.py interval arithmetic)"
          % (3 * (len(recorded) + len(res["context_complex_at_c_star"]["boundary_checks"]) + 2)))


if __name__ == "__main__":
    sys.set_int_max_str_digits(1000000)
    main()
