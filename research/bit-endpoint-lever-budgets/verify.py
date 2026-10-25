#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Sharp bit-lever budgets at the +10% bit endpoint on the actual PR589 histogram (primary method).

Planning bound / scoped proof for the bit-helper-contract card; consuming decision: centre-path-sharing.
No construction, no kappa claim, not a multiplication theorem.

The exact moment enclosures (Navinor's selected-suppliers-de-diagnostic) and the bootstrap/outer formulas
(Wronskode's frontier1042-invoice-audit-seed81) are loaded unchanged as pinned Git blobs at BASE, as in
centre-sharing-overhead-budget. The bit bill is f(a) = (1/(mW)) sum_r n_r r (m/r)^a + c_s m^a with the surcharge
c_s = 32 m N / (1e16 W) recomputed from each histogram's child count N. It is linear in the counts n_r, so every
budget below is a sharp integer in its stated model: the stated count passes the exact test f(c*) < 1 and
one less fails (README lists the bounded exceptions).
Standard library and git only.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5).
"""
import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import subprocess
import sys
import types

if not __debug__:
    raise SystemExit("checks use assert; run without -O")
sys.set_int_max_str_digits(1000000)

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PINS = {"de": ("research/selected-suppliers-de-diagnostic/verify.py", "f9a9d5e5103b6ccbadb3f50fea34e25ccfce7ff1"),
        "seed81": ("research/frontier1042-invoice-audit-seed81/verify.py", "8ee1d7a01473e1b5674710165566e4e9761f7c65"),
        "assembly": ("research/community-frontier1094-audit/ASSEMBLY.json", "5fd676df060f3b450782fdf5ff5f6beb63a5eeb0"),
        "pr589": ("research/e8-bit-p111-tuned/tune/EXPECTED.json", "e293ddc557742637f9f679f083a1a282d87b1b13"),
        "predecessor": ("research/centre-sharing-overhead-budget/RESULT.json", "a3758cbd5f157a85e741912783b7203f4061429c")}
C_STAR = Q(921658892752012102303, 5 * 10 ** 23)   # centre-sharing-overhead-budget: bit endpoint for +10% kappa
GRID = Q(1, 10 ** 24)
ETA = BETA = Q(1, 10 ** 24)
B_CERTIFIED_K2 = Q(3, 1000)        # complex acceptance point with two-call sharing (predecessor's premise)
NEED_RANK1 = 649                   # predecessor's sharp rank-1 requirement, re-derived below
DELETION_MODELS = {"RANK1": {1: -8}, "TEMPLATE": {1: -2, 2: 2, 3: -1, 7: -1}}   # bit-deletion-ladder (per deletion)


def blob(key):
    path, sha = PINS[key]
    raw = subprocess.run(["git", "-C", str(ROOT), "show", BASE + ":" + path], capture_output=True, check=True).stdout
    assert hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == sha, "pinned blob differs: " + path
    return raw


def load_module(key):
    mod = types.ModuleType("pinned_" + key)
    mod.__file__ = str(ROOT / PINS[key][0])
    exec(compile(blob(key), mod.__file__, "exec"), mod.__dict__)
    return mod


def idle_window_ranks(K):
    """Idle-event ranks of the nine-stage recipe, transcribed from global_k.py (PR #463/#510 lineage)."""
    out = [7 * (s + 1) for s in range(1, 2 * K - 2, 2)]          # s odd, s <= 2K-3: pair (s+1)/2 waits s+1 levels
    out += [7 for s in range(2, 2 * K - 1, 2)]                   # s even, 2 <= s <= 2K-2: one level
    out += [7 * (2 * K - (2 * j + 2)) for j in range(K)]         # s = 2K: every pair from level 2j+2 to 2K
    return [r for r in out if r]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    de, s81 = load_module("de"), load_module("seed81")
    asm, expected, pred = (json.loads(blob(k)) for k in ("assembly", "pr589", "predecessor"))
    bit_bill, info = de.bit_ledger(asm, expected)
    m, W, T = info["m"], info["W"], info["T"]
    H = dict(bit_bill.hist)
    word = expected["word"]
    calls = 9 * T                                     # L = 9 stage calls per replica
    c_sel, k_sel = Q(asm["bit_lower"]), Q(asm["kappa"])
    assert C_STAR == Q(pred["ten_percent_target"]["bit_endpoint_needed"]), "endpoint differs from predecessor"
    out = {"endpoint": {"c_star": str(C_STAR), "c_star_decimal": "%.16f" % float(C_STAR), "next_grid": str(C_STAR + GRID)},
           "record": {"m": m, "W": W, "T": T, "calls": calls, "deficit": info["deficit"], "children": sum(H.values()),
                      "rank_mass": sum(r * n for r, n in H.items())}}

    unit_cache = {}

    def unit(r, a):
        """Certified enclosure of r (m/r)^a / (mW): the bill of one rank-r child, from the pinned engine."""
        if (r, a) not in unit_cache:
            lo, hi = de.Bill({r: 1}, m, W).residual(a)
            unit_cache[r, a] = (lo + 1, hi + 1)
        return unit_cache[r, a]

    def F(h, a):
        """Certified enclosure of f(a) for a histogram (fractional counts allowed), surcharge recomputed."""
        lo = hi = Q(0)
        for r, n in h.items():
            assert n >= 0 and 0 < r < m, "histogram range"
            if n:
                u = unit(r, a)
                lo, hi = lo + n * u[0], hi + n * u[1]
        cs = Q(32 * m, 10 ** 16 * W) * sum(h.values())     # c_s m^a = cs * (mW * unit(1))
        u1 = unit(1, a)
        return lo + cs * m * W * u1[0], hi + cs * m * W * u1[1]

    def verdict(h, a):
        lo, hi = F(h, a)
        return "pass" if hi < 1 else "fail" if lo > 1 else "undecided"

    def add(h, delta, k=1):
        o = Counter(h)
        for r, n in delta.items():
            o[r] += k * n
        assert all(n >= 0 for n in o.values()), "negative count"
        return {r: n for r, n in o.items() if n}

    def sharp_min(build, lo, hi):
        """Least k in (lo, hi] with build(k) passing at c*, given build(lo) fails and build(hi) passes."""
        assert verdict(build(lo), C_STAR) == "fail" and verdict(build(hi), C_STAR) == "pass"
        while hi - lo > 1:
            mid = (lo + hi) // 2
            v = verdict(build(mid), C_STAR)
            assert v != "undecided", "undecided boundary"
            lo, hi = (mid, hi) if v == "fail" else (lo, mid)
        return hi

    def sharp_max(build, lo, hi):
        """Largest k in [lo, hi) with build(k) passing at c*, given build(lo) passes and build(hi) fails."""
        assert verdict(build(lo), C_STAR) == "pass" and verdict(build(hi), C_STAR) == "fail"
        while hi - lo > 1:
            mid = (lo + hi) // 2
            v = verdict(build(mid), C_STAR)
            assert v != "undecided", "undecided boundary"
            lo, hi = (mid, hi) if v == "pass" else (lo, mid)
        return lo

    def units_saved(h, a=C_STAR):
        """Net bill reduction against the record, in rank-1 children (certified interval, rounded outward)."""
        r_lo, r_hi = F(H, a)
        l_lo, l_hi = F(h, a)
        u1 = unit(1, a)
        one = (u1[0] * (1 + Q(32 * m * m * W, 10 ** 16 * W)), u1[1] * (1 + Q(32 * m * m * W, 10 ** 16 * W)))
        d_lo, d_hi = r_lo - l_hi, r_hi - l_lo
        lo = d_lo / one[1] if d_lo >= 0 else d_lo / one[0]
        hi = d_hi / one[0] if d_hi >= 0 else d_hi / one[1]
        return [float(lo), float(hi)]

    boundary = []            # (label, histogram, expected verdict) for the next-grid and independent checks

    def record(label, h, v):
        assert verdict(h, C_STAR) == v, label
        boundary.append(dict(label=label, hist={str(r): str(n) for r, n in sorted(h.items())}, verdict=v))

    # ---- Controls -----------------------------------------------------------------------------------------
    assert F(H, c_sel) == tuple(x + 1 for x in bit_bill.residual(c_sel)), "F reproduces the pinned bill"
    assert verdict(H, c_sel) == "pass" and verdict(H, c_sel + GRID) == "fail", "selected bit endpoint"

    def kappa(b, c):
        a, _ = s81.bootstrap(b, c, ETA, BETA)
        k = s81.kappa_from(a, ETA)
        slacks, _ = s81.assembly_slacks(a, b, k, ETA, BETA)
        assert all(v > 0 for v in slacks.values()), "outer slack"
        return k
    assert kappa(Q(asm["complex_lower"]), c_sel) == k_sel, "selected kappa"
    target = k_sel * Q(11, 10)
    assert kappa(B_CERTIFIED_K2, C_STAR) >= target > kappa(B_CERTIFIED_K2, C_STAR - GRID), "c* is the +10% endpoint"
    assert kappa(C_STAR + GRID, C_STAR) >= target, "complex accepted at c* + 1e-24 suffices with bit at c*"
    assert kappa(C_STAR, C_STAR) >= target > kappa(C_STAR - GRID, C_STAR), "complex endpoint c* is necessary"
    assert target > kappa(C_STAR - GRID, B_CERTIFIED_K2), "complex below c* fails even with bit at 3/1000"
    assert verdict(H, C_STAR) == "fail", "the record fails at c*"
    out["controls"] = ["F equals the pinned D/E-diagnostic bill on the record",
                       "selected bit endpoint accepted, next grid rejected", "selected kappa recomputed",
                       "c* is the least grid point with kappa >= 1.1 x selected (complex at 3/1000)",
                       "complex endpoint c* + 1e-24 with bit endpoint c* already gives kappa >= 1.1 x selected",
                       "complex endpoint c* - 1e-24 fails the target with bit at c* and even with bit at 3/1000",
                       "the record fails at c*"]

    # ---- Baseline requirement (predecessor's sharp removal, re-derived) ------------------------------------
    need1 = sharp_min(lambda x: add(H, {1: -x}), 0, 2000)
    need42 = sharp_min(lambda x: add(H, {42: -x}), 0, 100)
    assert need1 == NEED_RANK1 and need42 == 16, "predecessor requirement"
    record("remove %d rank-1" % need1, add(H, {1: -need1}), "pass")
    record("remove %d rank-1" % (need1 - 1), add(H, {1: -(need1 - 1)}), "fail")
    out["requirement"] = dict(rank1_children=need1, rank42_children=need42, rank1_per_replica=round(need1 / T, 3))

    # ---- (a) idle cap / halving depth, and width-8 re-hosting in the actual windows -------------------------
    K, V, R = 4, word["v"], word["R"]
    local = {int(r): n for r, n in word["local_histogram"].items()}
    assert sum(r * n for r, n in local.items()) == word["legality"]["rank_mass"] == 5129
    ev = idle_window_ranks(K)
    assert sorted(ev) == [7, 7, 7, 14, 14, 28, 28, 42, 42]
    windows = Counter({r: 2 * V * c for r, c in Counter(ev).items()})            # per replica
    assert windows == Counter({7: 666, 14: 444, 28: 444, 42: 444})
    slots = {r: r // 8 for r in windows}                                         # width-8 helper slots per window
    spare = sum(windows[r] * slots[r] for r in windows) - 9 * R                  # 3996 - 3951 = 45 per replica
    assert spare == 45 and spare % slots[42] == 0
    rem = Counter({r % 8 if slots[r] else r: n for r, n in windows.items()})
    rem[42 % 8] -= spare // slots[42]
    rem[42] += spare // slots[42]
    idle = Counter(H)
    idle.subtract({r: calls * n for r, n in local.items()})
    assert +idle == Counter({r: T * n for r, n in rem.items()}), "record idle part = optimal width-8 remainder"
    caps = {}
    for hd in (2, 3, 4):
        caps[hd] = max(r for r in range(1, m) if 2 * r ** hd < m ** hd)
    assert caps == {2: 45, 3: 50, 4: 53} and expected["nine"]["bit"]["halving_depth"] == 2
    assert max(H) == max(windows) == 7 * (2 * K - 2) == 42 < caps[2], "the halving cap is slack"
    assert all(r % 8 for r in windows), "every window keeps a nonzero remainder: child count is fixed"
    q = {}
    for r, lo_rem in ((42, 2), (28, 4), (14, 6)):
        a_, b_ = unit(r, C_STAR), unit(lo_rem, C_STAR)
        q[r] = ((a_[0] - b_[1]) / slots[r], (a_[1] - b_[0]) / slots[r])
    assert q[42][1] < q[28][0] and q[42][1] < q[14][0], "emptying rank-42 windows is the cheapest use of a spare slot"
    for cs in (C_STAR, C_STAR + GRID):
        a_, b_ = unit(42, cs), unit(2, cs)
        c_, d_ = unit(28, cs), unit(4, cs)
        e_, f_ = unit(14, cs), unit(6, cs)
        assert (a_[1] - b_[0]) / 5 < (c_[0] - d_[1]) / 3 and (a_[1] - b_[0]) / 5 < e_[0] - f_[1]
    out["lever_a_idle_cap"] = dict(
        halving_caps=caps, max_child=max(H), window_ranks_per_replica=dict(sorted(windows.items())),
        record_remainder_per_replica={str(r): n for r, n in sorted((+rem).items())},
        per_slot_cost_rank1_units={str(r): [float(q[r][0] / unit(1, C_STAR)[1]), float(q[r][1] / unit(1, C_STAR)[0])]
                                   for r in q},
        net_rank1_units_hd3=0, net_rank1_units_hd4=0, rehost_net_rank1_units=0,
        note="every child is at most the largest idle window 42 < 45, so HD 3/4 caps admit no new histogram; "
             "spare width-8 slots are cheapest in emptied rank-42 windows, which the record already does")

    # ---- (b) copy charge: rank-8 carriage, fewer rank-7 copies, two-call bit centre sharing ------------------
    copies = calls * len(word["copy_ranks"])
    assert set(word["copy_ranks"]) == {7} and copies == 2592
    b1 = add(H, {7: -copies, 8: copies})
    record("rank-8 carriage of all 2592 copies (cst 72)", b1, "fail")
    x_star = sharp_min(lambda x: add(H, {7: -x}), 0, copies)
    record("remove %d rank-7 copies" % x_star, add(H, {7: -x_star}), "pass")
    record("remove %d rank-7 copies" % (x_star - 1), add(H, {7: -(x_star - 1)}), "fail")
    one_per_call = add(H, {7: -calls})
    shared = add(H, {7: -copies // 2})               # two calls share one centre path: 4.5 copies per call
    budget = {}
    for r in (1, 7, 42):
        y = sharp_max(lambda y: add(shared, {r: y}), 0, 20000 if r == 1 else 3000 if r == 7 else 400)
        record("two-call sharing + %d rank-%d overhead" % (y, r), add(shared, {r: y}), "pass")
        record("two-call sharing + %d rank-%d overhead" % (y + 1, r), add(shared, {r: y + 1}), "fail")
        budget[str(r)] = dict(total=y, per_call=round(y / calls, 3), mass_per_call=round(y * r / calls, 3))
    b1_net = units_saved(b1)
    assert b1_net[1] < 0, "rank-8 carriage must lose"
    out["lever_b_copy_charge"] = dict(
        copies=copies, cst_per_call=63,
        rank8_carriage=dict(cst_per_call=72, deficit=info["deficit"] - copies, net_rank1_units=b1_net),
        fewer_copies=dict(sharp_total_copies=x_star, per_call_uniform=1, deficit_one_fewer_per_call=info["deficit"] + 7 * calls,
                          net_rank1_units_one_fewer_per_call=units_saved(one_per_call)),
        two_call_bit_centre_sharing=dict(cst_per_call=31.5, copies_removed=copies // 2,
                                         net_rank1_units=units_saved(shared), overhead_budget=budget))

    # ---- (c) unpaid coordinates: one unit of rank mass is worth at most one rank-1 child ---------------------
    for r in range(2, max(H) + 1):
        a_, b_ = unit(r, C_STAR), unit(r - 1, C_STAR)
        assert a_[1] - b_[0] < unit(1, C_STAR)[0], "trimming one unit saves less than removing a rank-1 child"
    out["lever_c_unpaid"] = dict(families=W, sharp_families_needed_if_each_removes_a_rank1_child=need1,
                                 fraction=round(need1 / W, 5),
                                 note="necessary when each unpaid coordinate is a pure one-unit removal (no reshaping or merges); sufficient if every removed unit is a rank-1 child")

    # ---- (d) helper deletions with optimal width-8 re-hosting (stage-relaxed slot model) ---------------------
    def rehosted(h, d, upper):
        """Host the 45 + 9d spare width-8 slots per replica: explicit (upper) or concavity lower bound."""
        s = spare + 9 * d                                              # spare slots per replica
        if not upper:                                                  # fractional concavity bound (lower bill)
            return add(h, {42: Q(T * 9 * d, 5), 2: -Q(T * 9 * d, 5)})
        n, s0 = divmod(s, 5)
        assert n + (s0 > 0) <= windows[42]
        h = add(h, {42: T * (n - 9), 2: -T * (n - 9)})
        return add(h, {2 + 8 * s0: T, 2: -T}) if s0 else h

    def deletion(model, d, upper):
        return rehosted(add(H, DELETION_MODELS[model], calls * d), d, upper)
    assert deletion("RANK1", 0, True) == deletion("RANK1", 0, False) == H
    dels = {}
    for model, dm in DELETION_MODELS.items():
        d_max = min(local[r] // -n for r, n in dm.items() if n < 0)   # the word's climbs the model consumes
        d = 0
        while d <= d_max and verdict(deletion(model, d, True), C_STAR) != "pass":
            assert verdict(deletion(model, d, False), C_STAR) == "fail", "lower bound must fail below the boundary"
            d += 1
        if d > d_max:
            record("%s: %d deletions per call (model exhausted), concavity bound" % (model, d_max),
                   deletion(model, d_max, False), "fail")
            dels[model] = dict(per_call=None, exhausted_at=d_max, of_helpers=430,
                               net_rank1_units_at_exhaustion_explicit_hosting=units_saved(deletion(model, d_max, True)),
                               net_rank1_units_at_exhaustion_upper_bound=units_saved(deletion(model, d_max, False)),
                               note="the model's 19 rank-7 climbs include the 9 rank-7 copies; with copies kept it "
                                    "is exhausted at d = 10")
            continue
        assert verdict(deletion(model, d - 1, False), C_STAR) == "fail", "deletion boundary not sharp: " + model
        record("%s: %d deletions per call, explicit hosting" % (model, d), deletion(model, d, True), "pass")
        record("%s: %d deletions per call, concavity bound" % (model, d - 1), deletion(model, d - 1, False), "fail")
        dels[model] = dict(per_call=d, of_helpers=430, total=calls * d,
                           net_rank1_units=units_saved(deletion(model, d, True)))
    out["lever_d_helper_deletion"] = dict(models={k: {str(r): n for r, n in v.items()} for k, v in DELETION_MODELS.items()},
                                          sharp=dels, known_removable_helpers_of_the_fixed_word=1)

    # ---- (f) width-7 helper conversion (#1023's WINDOW-FREE placement and bracket; PR1736: unreachable under windows) --------------------------
    def width7(k, upper, pes=False):
        """k helpers per call converted to width 7: one unit removed from one local child per converted helper
        (rank-1 child removed, or largest child trimmed: #1023's bracket); the 9k width-7 residuals per replica fill
        9k empty 7-slots exactly; the freed width-8 slack is hosted as in (d)."""
        assert 9 * k <= windows[7], "this placement uses empty 7-slots only"
        delta, left = Counter({1: -k}), k
        if pes:
            delta = Counter()
            for r in sorted(local, reverse=True):
                take = min(left, local[r])
                delta[r] -= take
                delta[r - 1] += take if r > 1 else 0
                left -= take
                if not left:
                    break
            assert left == 0
        delta[7] -= k
        return rehosted(add(H, delta, calls), k, upper)
    assert width7(0, True) == width7(0, False) == width7(0, True, True) == H
    kmax = windows[7] // 9
    k7 = 0
    while k7 <= kmax and verdict(width7(k7, True), C_STAR) != "pass":
        assert verdict(width7(k7, False), C_STAR) == "fail"
        k7 += 1
    assert k7 <= kmax and verdict(width7(k7 - 1, False), C_STAR) == "fail"
    record("width-7: %d helpers per call, rank-1 removed, explicit hosting" % k7, width7(k7, True), "pass")
    record("width-7: %d helpers per call, rank-1 removed, concavity bound" % (k7 - 1), width7(k7 - 1, False), "fail")
    record("width-7: %d helpers per call, largest trimmed, concavity bound" % kmax, width7(kmax, False, True), "fail")
    out["lever_f_width7"] = dict(
        placement="#1023 window-free relaxation: width-7 residuals in empty 7-slots, width-8 slack in emptied rank-42 windows",
        window_respecting="PR1736 (bit589-width7-windows-seed72): under replica-local windows at most 3k of the 9k residuals fit; no partial conversion k <= 74 reaches c* (certified max 0.001809907119 at k = 74); cited, not re-derived here",
        max_per_call_in_this_placement=kmax,
        rank1_removed=dict(sharp_per_call=k7, total=calls * k7, net_rank1_units=units_saved(width7(k7, True))),
        largest_trimmed=dict(per_call=None, fails_at=kmax, net_rank1_units_at_max=units_saved(width7(kmax, True, True))),
        admitted=False)

    # ---- (e) local rank shape: replace the shipped word by the ideal in-window shapes in k calls -------------
    ideal = {7: 2 * V + 9, 8: R}
    assert sum(r * n for r, n in ideal.items()) == 5129
    delta = dict(Counter(ideal) - Counter(local)) | {r: -n for r, n in (Counter(local) - Counter(ideal)).items()}
    assert delta == {1: -1323, 2: -1342, 3: -79, 4: -44, 5: -102, 6: -11, 7: 212, 8: 439}
    k_star = sharp_min(lambda k: add(H, delta, k), 0, calls)
    record("ideal shapes in %d calls" % k_star, add(H, delta, k_star), "pass")
    record("ideal shapes in %d calls" % (k_star - 1), add(H, delta, k_star - 1), "fail")
    out["lever_e_local_shape"] = dict(ideal_per_call={str(r): n for r, n in ideal.items()}, sharp_calls=k_star,
                                      of_calls=calls, net_rank1_units_all_calls=units_saved(add(H, delta, calls)))

    # ---- Context: the complex side of the same route at c* (predecessor's two-call sharing model) -----------
    HC = {int(r): int(n) for r, n in asm["complex_profile"].items()}
    MC, WC, NC = 73, 14336, asm["provider_counts"]["gauge44"]
    shared_c = {**HC, 8: HC[8] // 2}

    def cverdict(h, a):
        lo, hi = de.Bill(h, MC, WC).residual(a)
        return "pass" if hi < 0 else "fail" if lo > 0 else "undecided"
    assert cverdict(HC, Q(asm["complex_lower"])) == "pass" and cverdict(HC, C_STAR) == "fail"
    assert cverdict(HC, Q(asm["complex_lower"]) + GRID) == "fail"   # selected complex endpoint is sharp
    assert cverdict(shared_c, B_CERTIFIED_K2) == "pass" and cverdict(shared_c, C_STAR) == "pass"
    complex_budget, complex_boundary = {}, []
    for r in (1, 8):
        lo, hi = 0, 9000 if r == 1 else 1150           # within the shared deficit 5120 + 4608
        assert cverdict(add(shared_c, {r: hi}), C_STAR) == "fail"
        while hi - lo > 1:
            mid = (lo + hi) // 2
            lo, hi = (mid, hi) if cverdict(add(shared_c, {r: mid}), C_STAR) == "pass" else (lo, mid)
        for y, v in ((lo, "pass"), (lo + 1, "fail")):
            h = add(shared_c, {r: y})
            assert all(cverdict(h, cs) == v for cs in (C_STAR - GRID, C_STAR, C_STAR + GRID))
            complex_boundary.append(dict(label="complex two-call sharing + %d rank-%d overhead" % (y, r),
                                         hist={str(q): n for q, n in sorted(h.items())}, verdict=v))
        complex_budget[str(r)] = dict(total=lo, per_call=round(lo / NC, 3), mass_per_call=round(lo * r / NC, 3))
    cneed = 0
    lo, hi = 0, 2000
    assert cverdict(add(HC, {1: -hi}), C_STAR) == "pass"
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if cverdict(add(HC, {1: -mid}), C_STAR) == "fail" else (lo, mid)
    cneed = hi
    for cs in (C_STAR - GRID, C_STAR, C_STAR + GRID):
        assert cverdict(add(HC, {1: -cneed}), cs) == "pass" and cverdict(add(HC, {1: -(cneed - 1)}), cs) == "fail"
    out["context_complex_at_c_star_need"] = dict(net_rank1_children=cneed, calls=NC, per_call=round(cneed / NC, 3),
                                                 note="PR1791 OQ1's >= 1.33 units per call holds only at the selected "
                                                      "bit endpoint; at c* the complex side needs this net saving")
    out["context_complex_at_c_star"] = dict(model="centre-sharing-overhead-budget k=2: 1152 -> 576 rank-8 centre children",
                                            overhead_budget=complex_budget, boundary_checks=complex_boundary)

    # ---- Adjacent grid points: every boundary verdict is unchanged at c* - 1e-24 and c* + 1e-24 ------------
    for b in boundary:
        h = {int(r): Q(n) for r, n in b["hist"].items()}
        for cs in (C_STAR - GRID, C_STAR + GRID):
            assert verdict(h, cs) == b["verdict"], "adjacent-grid verdict: %s at %s" % (b["label"], cs)
    out["boundary_checks"] = boundary
    admitted_max = max(out["lever_a_idle_cap"]["net_rank1_units_hd3"], out["lever_a_idle_cap"]["net_rank1_units_hd4"],
                       out["lever_a_idle_cap"]["rehost_net_rank1_units"], b1_net[1])
    assert admitted_max == 0
    out["status"] = "PASS_BIT_ENDPOINT_LEVER_BUDGETS"

    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    path = PKG / "RESULT.json"
    if args.write:
        path.write_text(text, encoding="utf-8", newline="\n")
        print("WROTE", path.relative_to(ROOT).as_posix())
    else:
        assert path.read_text(encoding="utf-8") == text, "RESULT.json differs from the regenerated result"
    print("%s need_rank1=%d admitted_levers_max_net=%d copies_sharp=%d deletions_per_call=%s width7_windowfree_per_call=%d "
          "ideal_shape_calls=%d complex_need_rank1=%d no_new_kappa"
          % (out["status"], need1, admitted_max, x_star, "/".join("%s:%s" % (k, v["per_call"]) for k, v in dels.items()),
             k7, k_star, cneed))


if __name__ == "__main__":
    main()
