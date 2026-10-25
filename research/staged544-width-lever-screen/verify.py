#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact width-lever screen of the staged544 fixed-T360 ideal (standard library only).

Model (PR3815 ceiling_certificate.py, PR3734 inventory): per owner replica, 9 calls of
408 helpers; idle bins {8:672,16:448,32:448,48:448}; each helper occupies its hosted
width in one bin and each bin remainder l>0 is paid as one rank-l child; local paid
profile per call; 896 live rank-73 families. F(a) = sum N_r r^(1-a) - 896*73^(1-a) over the full paid histogram N per
replica has the sign of a strictly increasing function, so "ceiling < a" iff F(a) > 0.

Checks (all exact rational arithmetic; h(l) = l^(1-a) enclosed by series with
remainder bounds, rounded outward to 1e-90):
  1. staged544 ceiling bracket (a_lo, a_hi) from an exact primal/dual pair (reproduces PR3815).
  2. monotone-price lemma: PR3815's basis dual (pi_4..9, mu) with the cheapest extension
     pi_1..3 := pi_4 is feasible on ALL 318,840 width-1..9 patterns (enumeration and an
     unbounded-knapsack recursion); also the two premises of the PROOF slack lemma
     (feasible on widths 4..9 and pi_4 <= -3), which imply the same.
  3. exact width-unit prices p(w->v) = pi_v - pi_w at a_hi with basis ranges; the tight
     extension of pi_1..3 and the exact 4->3 price h(5)-h(3)-1 on [0, 324/5] helper-calls.
  4. staging screens: single-child (rank-1 deletion) upper reference and the documented
     PR3605 staging signature {1:+3,2:+1,3:-2}.
  5. per-call conservation: local paid rank - hosted width = 1856 on both pinned
     (inventory, local) pairs; total paid rank on three pinned T360 profiles.
  6. PR3682 -> staged544 2x2 split of F at a_hi (four optimal LPs; interaction is
     identically 0 by separability).
  7. negative controls (each must fail) and one consistency check.
"""
import json
import math
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT = json.loads((HERE / "CERTIFICATE.json").read_text())
BINS = {8: 672, 16: 448, 32: 448, 48: 448}
CAPS = (8, 16, 32, 48)
WIDTHS = tuple(range(1, 10))
CALLS, LIVE, LIVE_RANK = 9, 896, 73
INV = {"staged544": {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213},
       "pr3682": {4: 26, 5: 2, 6: 18, 7: 52, 8: 97, 9: 213}}
LOC = {"staged544": {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8},
       "pr3682": {1: 2437, 2: 724, 3: 226, 4: 102, 5: 20, 8: 8}}
DEN = 10 ** 90


# ---------- outward rational enclosures of h(l) = l^(1-a) ----------
def atanh_enc(t, n=110):
    """sum_{k<n} t^(2k+1)/(2k+1) and the same plus a tail bound, for 0 <= t <= 1/3."""
    s, p, t2 = Q(0), Q(t), Q(t) * t
    for k in range(n):
        s += p / (2 * k + 1)
        p *= t2
    return s, s + p / ((2 * n + 1) * (1 - t2))


LN2 = tuple(2 * x for x in atanh_enc(Q(1, 3)))


def ln_enc(l):
    k = l.bit_length() - 1                        # l = 2^k * x with 1 <= x < 2
    t = Q(l - 2 ** k, l + 2 ** k)                 # 0 <= t < 1/3
    lo, hi = atanh_enc(t) if t else (Q(0), Q(0))
    return k * LN2[0] + 2 * lo, k * LN2[1] + 2 * hi


def exp_neg(u, odd):
    """Partial sum of e^-u through degree 41 (odd=True: lower bound) or 40 (upper), 0<=u<1."""
    n = 41 if odd else 40
    s, term = Q(1), Q(1)
    for j in range(1, n + 1):
        term = -term * u / j
        s += term
    return s


def floor_d(x):
    return Q(x.numerator * DEN // x.denominator, DEN)


def ceil_d(x):
    return Q(-((-x.numerator * DEN) // x.denominator), DEN)


LN = {l: ln_enc(l) for l in list(range(2, 49)) + [LIVE_RANK]}


def h_table(a):
    """l -> (lower, upper) enclosure of l^(1-a) for l in 0..48 and 73."""
    a = Q(a)
    assert 0 < a < Q(1, 100)
    tab = {0: (Q(0), Q(0)), 1: (Q(1), Q(1))}
    for l, (llo, lhi) in LN.items():
        lo = l * exp_neg(ceil_d(a * lhi), True)
        hi = l * exp_neg(floor_d(a * llo), False)
        tab[l] = (floor_d(lo), ceil_d(hi))
        assert tab[l][0] < tab[l][1] and hi - lo < Q(1, 10 ** 85)
    return tab


# ---------- patterns ----------
def patterns(cap, widths):
    """All count vectors (indexed by WIDTHS) of helpers of the given widths fitting cap."""
    out = []

    def rec(i, rest, cur):
        if i == len(widths):
            v = [0] * 9
            for w, k in zip(widths, cur):
                v[w - 1] = k
            out.append(tuple(v))
            return
        for k in range(rest // widths[i] + 1):
            rec(i + 1, rest - k * widths[i], cur + [k])
    rec(0, cap, [])
    return out


def left(cap, p):
    return cap - sum(k * w for k, w in zip(p, WIDTHS))


def solve(A, b):
    n = len(A)
    M = [[Q(x) for x in row] + [Q(y)] for row, y in zip(A, b)]
    for c in range(n):
        piv = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


# ---------- LP pieces ----------
def basis_of(name):
    return [(c, tuple(p)) for c, p in CERT["bases"][name]]


def used_widths(basis):
    return sorted({WIDTHS[i] for _, p in basis for i, k in enumerate(p) if k})


def primal(inv, basis):
    """Exact y on the basis: widths rows (=9 s_w) and bin rows (=B_c)."""
    ws = used_widths(basis)
    assert set(inv) == set(ws) and len(ws) + len(CAPS) == len(basis)
    A = [[p[w - 1] for _, p in basis] for w in ws] + [[1 if c == cap else 0 for c, _ in basis] for cap in CAPS]
    b = [CALLS * inv[w] for w in ws] + [BINS[c] for c in CAPS]
    y = solve(A, b)
    return y


def dual(basis, tab):
    """Exact (pi, mu) with pi.p + mu_c = h_lo(l_p) on the basis; pi_1..3 := pi_4."""
    ws = used_widths(basis)
    A = [[p[w - 1] for w in ws] + [1 if c == cap else 0 for cap in CAPS] for c, p in basis]
    b = [tab[left(c, p)][0] for c, p in basis]
    sol = solve(A, b)
    pi = dict(zip(ws, sol[:len(ws)]))
    for w in WIDTHS:
        if w not in pi:
            pi[w] = pi[min(ws)]                    # cheapest monotone extension
    return pi, dict(zip(CAPS, sol[len(ws):]))


def local_sum(loc, tab, k):
    return CALLS * sum(n * tab[r][k] for r, n in loc.items())


def min_reduced_cost_enum(pi, mu, tab, widths):
    """Exact minimum of h_lo(l_p) - pi.p - mu_c over every pattern (integer arithmetic)."""
    vals = list(pi.values()) + list(mu.values()) + [tab[l][0] for l in range(49)]
    L = 1
    for v in vals:
        L = L * v.denominator // math.gcd(L, v.denominator)
    P = [int(pi[w] * L) for w in widths]
    H = [int(tab[l][0] * L) for l in range(49)]
    worst, count, tight = None, 0, 0
    for cap in CAPS:
        M = int(mu[cap] * L)

        def rec(i, rest, acc, cur):
            nonlocal worst, count, tight
            if i == len(widths):
                rc = H[rest] - M - acc
                count += 1
                tight += rc == 0
                if worst is None or rc < worst[0]:
                    worst = (rc, cap, tuple(cur))
                return
            w = widths[i]
            for k in range(rest // w + 1):
                rec(i + 1, rest - k * w, acc + k * P[i], cur + [k])
        rec(0, cap, 0, [])
    return Q(worst[0], L), worst[1:], count, tight


def min_reduced_cost_knapsack(pi, mu, tab, widths):
    """Same minimum by an unbounded-knapsack recursion on used volume (independent)."""
    best = {0: Q(0)}
    for v in range(1, 49):
        c = [best[v - w] + pi[w] for w in widths if v - w in best]
        if c:
            best[v] = max(c)
    return min(tab[cap - v][0] - mu[cap] - best[v] for cap in CAPS for v in best if v <= cap)


def max_uniform_price(pi, mu, tab, free):
    """Largest t such that pi_w := t for w in free keeps every widths-1..9 pattern dual feasible."""
    vals = [pi[w] for w in WIDTHS if w not in free] + list(mu.values()) + [tab[l][0] for l in range(49)]
    L = 1
    for v in vals:
        L = L * v.denominator // math.gcd(L, v.denominator)
    P = [0 if w in free else int(pi[w] * L) for w in WIDTHS]
    H = [int(tab[l][0] * L) for l in range(49)]
    best = None                                     # (numerator, s, cap, counts) of the minimal bound

    for cap in CAPS:
        M = int(mu[cap] * L)

        def rec(i, rest, acc, s, cur):
            nonlocal best
            if i == len(WIDTHS):
                if s and (best is None or (H[rest] - M - acc) * best[1] < best[0] * s):
                    best = (H[rest] - M - acc, s, cap, tuple(cur))
                return
            w = WIDTHS[i]
            for k in range(rest // w + 1):
                rec(i + 1, rest - k * w, acc + k * P[i], s + (k if w in free else 0), cur + [k])
        rec(0, cap, 0, 0, [])
    return Q(best[0], best[1] * L), (best[2], list(best[3]))


def ranging(inv, basis, d):
    """Largest k >= 0 keeping y(k) = B^-1 (b + k d) >= 0 (d per replica on widths)."""
    ws = used_widths(basis)
    A = [[p[w - 1] for _, p in basis] for w in ws] + [[1 if c == cap else 0 for c, _ in basis] for cap in CAPS]
    y = primal(inv, basis)
    dy = solve(A, [d.get(w, 0) for w in ws] + [0] * len(CAPS))
    ks = [yy / -g for yy, g in zip(y, dy) if g < 0]
    return min(ks) if ks else None


def F_bounds(inv, loc, basis, a):
    """Exact optimal-LP enclosure of F(a): primal (upper) and dual (lower) on one basis."""
    tab = h_table(a)
    y = primal(inv, basis)
    pi, mu = dual(basis, tab)
    ws = sorted(inv)
    rc, worst, n, tight = min_reduced_cost_enum(pi, mu, tab, tuple(ws))
    upper = local_sum(loc, tab, 1) + sum(yy * tab[left(c, p)][1] for yy, (c, p) in zip(y, basis)) - LIVE * tab[LIVE_RANK][0]
    lower = local_sum(loc, tab, 0) + sum(mu[c] * BINS[c] for c in CAPS) + sum(pi[w] * CALLS * inv[w] for w in ws) - LIVE * tab[LIVE_RANK][1]
    return dict(y_min=min(y), dual_min_rc=rc, patterns=n, lower=lower, upper=upper, pi=pi, mu=mu, tab=tab, y=y)


def monotone(pi):
    return all(pi[w - 1] >= pi[w] for w in WIDTHS[1:])


def paid_rank_ok(hist, T):
    """Total paid rank of a T-replica profile equals (896*73 - 320) T."""
    return sum(r * n for r, n in hist.items()) == (LIVE * LIVE_RANK - 320) * T


def dec(x, d=24):
    s = "-" if x < 0 else ""
    x = abs(x)
    q, r = divmod(x.numerator * 10 ** d, x.denominator)
    return f"{s}{q // 10 ** d}.{q % 10 ** d:0{d}d}"


def main():
    out, fails = {}, []

    def need(cond, msg):
        if not cond:
            fails.append(msg)

    a_lo, a_hi = Q(CERT["ceiling"]["a_lo"]), Q(CERT["ceiling"]["a_hi"])
    B = basis_of("staged544")
    inv, loc = INV["staged544"], LOC["staged544"]

    # 1. fixed-inventory ceiling bracket
    lo_side = F_bounds(inv, loc, B, a_lo)
    need(lo_side["y_min"] >= 0, "primal infeasible")
    need(lo_side["upper"] < 0, "F(a_lo) upper bound not negative")
    tab = h_table(a_hi)
    y = primal(inv, B)
    pi, mu = dual(B, tab)

    # 2. free reductions: all patterns of widths 1..9 + monotone prices
    rc_all, worst_all, n_all, tight_all = min_reduced_cost_enum(pi, mu, tab, WIDTHS)
    rc_kn = min_reduced_cost_knapsack(pi, mu, tab, WIDTHS)
    rc_w4, _, n_w4, _ = min_reduced_cost_enum(pi, mu, tab, (4, 5, 6, 7, 8, 9))
    mono = monotone(pi)
    lower = local_sum(loc, tab, 0) + sum(mu[c] * BINS[c] for c in CAPS) \
        + sum(pi[w] * CALLS * inv[w] for w in inv) - LIVE * tab[LIVE_RANK][1]
    need(n_all == 318840 and n_w4 == 2551, "pattern counts")
    need(rc_all >= 0 and rc_kn == rc_all, "dual infeasible over widths 1..9 or knapsack mismatch")
    need(mono, "helper prices not monotone")
    need(lower > 0, "F(a_hi) lower bound not positive")
    out["ceiling"] = dict(a_lo=dec(a_lo), a_hi=dec(a_hi), F_upper_at_a_lo=dec(lo_side["upper"], 30),
                          F_lower_at_a_hi=dec(lower, 30), primal_min_y=str(min(y)))
    need(rc_w4 >= 0 and pi[4] <= -3, "slack-lemma premises")
    out["monotone_price_lemma"] = dict(
        slack_lemma_premises=dict(dual_feasible_widths_4_to_9=rc_w4 >= 0,
                                  margin_minus_pi4_minus_3=dec(-pi[4] - 3)),
        patterns_widths_1_to_9=n_all, patterns_widths_4_to_9=n_w4,
        min_reduced_cost_all=dec(rc_all, 30), min_reduced_cost_knapsack=dec(rc_kn, 30),
        min_reduced_cost_widths_4_to_9=dec(rc_w4, 30), zero_reduced_cost_patterns=tight_all,
        argmin_pattern=[worst_all[0], list(worst_all[1])], monotone=mono,
        holds=rc_all >= 0 and mono and lower > 0,
        note="free reductions keep F(a_hi) > 0; under the per-call conservation (section 5) such a move is not realizable")

    # 3. prices at a_hi (F units per replica; one helper-call = one unit of 9 s_w)
    out["prices_at_a_hi"] = dict(
        helper_pi={w: dec(pi[w]) for w in WIDTHS}, bin_mu={c: dec(mu[c]) for c in CAPS},
        width_unit_price={f"{w}->{w - 1}": dec(pi[w - 1] - pi[w]) for w in range(5, 10)},
        delete_rank1_child=dec(Q(-1)),
        primal_y={f"{c}:{''.join(str(k) for k in p[3:])}": str(v) for (c, p), v in zip(B, y)})
    unit = {w: pi[w - 1] - pi[w] for w in range(5, 10)}
    need(all(0 <= u <= 1 for u in unit.values()), "width-unit price outside [0,1]")

    # 3b. tightest monotone prices for widths 3, 2, 1 (sequential maximisation), re-checked
    pt, limiting = dict(pi), {}
    for free in ((1, 2, 3), (1, 2), (1,)):
        t, limiting[max(free)] = max_uniform_price(pt, mu, tab, free)
        for w in free:
            pt[w] = t
    rc_t = min_reduced_cost_enum(pt, mu, tab, WIDTHS)[0]
    mono_t = all(pt[w - 1] >= pt[w] for w in WIDTHS[1:])
    need(rc_t >= 0 and mono_t and min_reduced_cost_knapsack(pt, mu, tab, WIDTHS) == rc_t, "tight extension")
    ranges = {f"{w}->{w - 1}": ranging(inv, B, {w: -1, w - 1: 1}) for w in range(5, 10)}
    # exact 4->3 price: add column [3,9^5] (48-bin); move k units along
    # +[3,9^5] -[4,9,9,9] +[9,9,9] -[9^5]; all four columns have reduced cost 0 under (pt, mu)
    c3 = (48, (0, 0, 1, 0, 0, 0, 0, 0, 5))
    path = [(c3, 1), ((32, (0, 0, 0, 1, 0, 0, 0, 0, 3)), -1), ((32, (0, 0, 0, 0, 0, 0, 0, 0, 3)), 1),
            ((48, (0, 0, 0, 0, 0, 0, 0, 0, 5)), -1)]
    rc_path = [tab[left(c, q)][0] - mu[c] - sum(pt[w] * q[w - 1] for w in WIDTHS) for (c, q), _ in path]
    need(all(r == 0 for r in rc_path), "4->3 path columns not all tight")
    net = [sum(g * q[i] for (c, q), g in path) for i in range(9)]
    net_bins = {cap: sum(g for (c, q), g in path if c == cap) for cap in CAPS}
    need(net == [0, 0, 1, -1, 0, 0, 0, 0, 0] and not any(net_bins.values()), "4->3 path direction")
    yb = dict(zip(B, y))
    range43 = min(yb[cq] for cq, g in path if g < 0)
    cost43 = sum(g * tab[left(c, q)][0] for (c, q), g in path)
    need(cost43 == pt[3] - pt[4] and range43 == Q(324, 5), "4->3 exact price or range")
    need(abs(cost43 - (tab[5][0] - tab[3][0] - 1)) == 0, "4->3 closed form")
    ranges["4->3"] = range43
    out["prices_at_a_hi"]["tight_small_width_pi"] = {w: dec(pt[w]) for w in (1, 2, 3)}
    out["prices_at_a_hi"]["width_unit_price_lower_bound_4_to_v"] = {f"4->{v}": dec(pt[v] - pt[4]) for v in (3, 2, 1)}
    out["prices_at_a_hi"]["width_unit_price_4_to_3_exact"] = dec(cost43)
    out["prices_at_a_hi"]["exact_range_helper_calls_per_replica"] = {k: str(v) for k, v in ranges.items()}
    out["prices_at_a_hi"]["tight_extension_min_reduced_cost"] = dec(rc_t, 30)
    out["prices_at_a_hi"]["tight_extension_limiting_patterns"] = limiting
    unit[4] = cost43
    need(all(pt[w] <= 0 for w in WIDTHS), "a helper price is positive (unhosting would then be priced)")

    # 3c. staging screens, gain in F per width unit (one helper-call moved one width step)
    sig = {r: LOC["staged544"].get(r, 0) - LOC["pr3682"].get(r, 0) for r in range(1, 9)}
    sig = {r: d for r, d in sig.items() if d}
    need(sig == {1: 3, 2: 1, 3: -2}, "PR3682 -> PR3734 local delta is not the PR3605 signature")
    sig_saving = -sum(d * tab[r][0] for r, d in sig.items())
    out["staging_screen_per_width_unit"] = dict(
        single_child_rank1_deletion_upper_reference={f"{w}->{w - 1}": dec(1 - unit[w]) for w in range(4, 10)},
        documented_signature={str(r): d for r, d in sig.items()},
        documented_signature_saving=dec(sig_saving),
        documented_signature_gain={f"{w}->{w - 1}": dec(sig_saving - unit[w]) for w in range(4, 10)},
        gap_signature_vs_rank1_deletion=dec(1 - sig_saving))
    # first-order conversion of F to the ceiling (float, envelope theorem on the optimal basis)
    dFda = -(CALLS * sum(n * float(tab[r][0]) * math.log(r) for r, n in loc.items())
             + sum(float(yy) * float(tab[left(c, p)][0]) * math.log(left(c, p)) for yy, (c, p) in zip(y, B) if left(c, p) > 1)) \
        + LIVE * float(tab[LIVE_RANK][0]) * math.log(LIVE_RANK)
    out["first_order_float"] = dict(dF_da_at_ceiling=dFda,
                                    ceiling_change_per_unit_F_decrease=1 / dFda)

    # 5. per-call conservation: local paid rank - hosted width = 1856 on both pinned pairs
    cons = {k: sum(r * n for r, n in LOC[k].items()) - sum(w * s for w, s in INV[k].items()) for k in INV}
    need(all(v == 1856 for v in cons.values()), "per-call conservation")
    need(CALLS * 1856 + sum(c * b for c, b in BINS.items()) == LIVE * LIVE_RANK - 320, "deficit 320")
    out["per_call_local_rank_minus_hosted_width"] = cons
    # total paid rank (= (896*73 - 320) T) on three pinned profiles; two share one (inventory, local) pair
    vol = {}
    for k, prof in CERT["profiles"].items():
        T = prof["T"]
        hist = {int(r): n for r, n in prof["histogram"].items()}
        if prof.get("add_local"):
            for r, n in LOC[prof["add_local"]].items():
                hist[r] = hist.get(r, 0) + CALLS * T * n
        vol[k] = dict(T=T, paid_rank_sum=sum(r * n for r, n in hist.items()), identity=paid_rank_ok(hist, T))
        need(vol[k]["identity"], f"volume identity fails for {k}")
    out["paid_rank_total"] = vol

    # 5. 2x2 decomposition at a_hi (each corner: own optimal basis, exact)
    corners = {"pr3682": ("pr3682", "pr3682"), "width_only": ("staged544", "pr3682"),
               "local_only": ("pr3682", "staged544"), "staged544": ("staged544", "staged544")}
    Fc = {}
    for name, (i, l) in corners.items():
        r = F_bounds(INV[i], LOC[l], basis_of(name), a_hi)
        need(r["y_min"] >= 0 and r["dual_min_rc"] >= 0, f"corner {name} basis not optimal")
        need(r["upper"] - r["lower"] < Q(1, 10 ** 70), f"corner {name} gap")
        Fc[name] = r["lower"]
    d_w, d_l = Fc["width_only"] - Fc["pr3682"], Fc["local_only"] - Fc["pr3682"]
    total = Fc["staged544"] - Fc["pr3682"]
    out["decomposition_at_a_hi"] = dict(
        F_lower={k: dec(v, 30) for k, v in Fc.items()},
        width_part=dec(d_w, 30), local_part=dec(d_l, 30), interaction=dec(total - d_w - d_l, 30),
        total=dec(total, 30),
        width_part_per_call=dec(d_w / CALLS, 30), local_saving_per_call=dec(-d_l / CALLS, 30),
        local_part_exact=dec(CALLS * sum((LOC["staged544"].get(r, 0) - LOC["pr3682"].get(r, 0)) * tab[r][0] for r in range(1, 9)), 30))
    need(total < 0 and d_w > 0 and d_l < 0, "decomposition signs")

    # 7. negative controls (each must FAIL the corresponding check)
    ctl = {}
    pi_bad = dict(pi)
    pi_bad[9] += Q(1, 10 ** 30)
    ctl["perturb_pi9_up_1e-30"] = min_reduced_cost_enum(pi_bad, mu, tab, WIDTHS)[0] < 0
    pi_nm = dict(pi)
    for w in (1, 2, 3):
        pi_nm[w] = pi[4] - Q(1, 10 ** 30)
    pg = dict(pt)
    pg[3] += Q(1, 10 ** 30)
    ctl["tight_extension_raised_1e-30_infeasible"] = min_reduced_cost_enum(pg, mu, tab, WIDTHS)[0] < 0
    ctl["non_monotone_extension_rejected_by_monotone_check"] = not monotone(pi_nm)
    lo_tab = h_table(a_lo)
    pl, ml = dual(B, lo_tab)
    lb_lo = local_sum(loc, lo_tab, 0) + sum(ml[c] * BINS[c] for c in CAPS) \
        + sum(pl[w] * CALLS * inv[w] for w in inv) - LIVE * lo_tab[LIVE_RANK][1]
    consistency = {"bound_at_a_lo_not_positive": lb_lo <= 0}    # implied by F_upper(a_lo) < 0 and weak duality
    widened = dict(inv)
    widened[8] -= 1
    widened[9] += 1
    lb_wide = local_sum(loc, tab, 0) + sum(mu[c] * BINS[c] for c in CAPS) \
        + sum(pi[w] * CALLS * widened.get(w, 0) for w in WIDTHS) - LIVE * tab[LIVE_RANK][1]
    ctl["one_8_to_9_widening_per_call_breaks_bound"] = lb_wide <= 0
    hist_bad = {int(r): n for r, n in CERT["profiles"]["pr3734_finite"]["histogram"].items()}
    hist_bad[1] = hist_bad.get(1, 0) + 1
    ctl["paid_rank_check_detects_plus_one"] = not paid_rank_ok(hist_bad, 360)
    for k, v in list(ctl.items()) + list(consistency.items()):
        need(v, f"control {k} did not fail as required")
    out["controls_failed_as_required"] = ctl
    out["consistency_checks"] = consistency

    out["status"] = "PASS" if not fails else "FAIL"
    out["failures"] = fails
    print(json.dumps(out, indent=1))
    print("PASS_STAGED544_WIDTH_LEVER_SCREEN" if not fails else "FAIL_STAGED544_WIDTH_LEVER_SCREEN")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
