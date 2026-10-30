#!/usr/bin/env python3
"""Independent audit engine for PR #6129's nearest-even Walsh-stage bound.

Session 51 (JosieElliston fork, Claude Opus 5.5 assistance). Apache-2.0.
Stdlib only. Nothing is imported from PR #6129 or PR #6119.

Engines, all exact (Fraction / int):
  A. residue-tracking tree sets: for every output sign pattern, the complete
     set of (stored value mod 2^(J+1-k), error) after k stages, started from
     every leaf residue mod 2^(J+1). Unlike #6129's parity-only recurrence it
     does not use the "children can be shifted by any even amount" step; it
     uses only R(s + 2t) = R(s) + 2t and the period-2^(J+1) lemma.
  B. literal array exhaustion of the 8-point network (J=3) on the box
     [-3,0]^8, both stage orders, every output coordinate.
  C. a re-implementation of #6119's 12-wire echo surrogate in integer units
     of h/8, exhaustive over one spectator fiber modulo 8h.
  D. controls: ties-to-odd gives the same law (only parity tie-breaking
     matters); floor gives the stagewise J/2 exactly and ties-away-from-zero
     already reaches J/2 at J=2, so the saving needs parity tie-breaking.
"""

from fractions import Fraction
from itertools import product
import json
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def r_even(q):
    """Nearest integer to Fraction q, ties to even (independent of round())."""
    fl = q.numerator // q.denominator
    rem = q - fl
    if rem < Fraction(1, 2):
        return fl
    if rem > Fraction(1, 2):
        return fl + 1
    return fl if fl % 2 == 0 else fl + 1


def r_odd(q):
    fl = q.numerator // q.denominator
    rem = q - fl
    if rem != Fraction(1, 2):
        return r_even(q)
    return fl if fl % 2 else fl + 1


def r_floor(q):
    return q.numerator // q.denominator


def claimed(j):
    return Fraction(j, 3) + (1 - Fraction(-1, 2) ** j) / 9


# ---------------------------------------------------------------- engine A
def tree_states(depth, signs, rnd):
    """States (stored mod M, signed error) for one output tree.

    signs[k] = +1 or -1 is the combination used at stage k+1. Valid for any
    rounding rule with rnd(q + 2t) = rnd(q) + 2t (all three rules here).
    """
    mod = 1 << (depth + 1)
    states = {(r, Fraction(0)) for r in range(mod)}
    for sigma in signs:
        need(mod >= 4, "modulus stays >= 4 before each combination")
        nxt = set()
        lst = sorted(states)
        for (u, eu) in lst:
            for (v, ev) in lst:
                s = (u + sigma * v) % mod
                stored = rnd(Fraction(s, 2))
                local = stored - Fraction(s, 2)
                nxt.add((stored % (mod // 2), local + (eu + sigma * ev) / 2))
        states, mod = nxt, mod // 2
    return states, mod


def engine_a(max_all_signs=4, max_depth=7):
    rows = []
    for depth in range(0, max_depth + 1):
        patterns = (list(product((1, -1), repeat=depth)) if depth <= max_all_signs
                    else [(1,) * depth])
        seen = None
        for signs in patterns:
            states, mod = tree_states(depth, signs, r_even)
            need(mod == 2, "final modulus is two: output parity is determined")
            even = [abs(e) for r, e in states if r == 0]
            odd = [abs(e) for r, e in states if r == 1]
            errs = sorted({e for _, e in states})
            need(max(even) == claimed(depth), "even-output sharp error a_J")
            need(max(odd) == (claimed(depth - 1) if depth else 0), "odd-output sharp a_(J-1)")
            need(errs == sorted({-e for e in errs}), "error set symmetric")
            if seen is None:
                seen = states
            need({(r, abs(e)) for r, e in states} == {(r, abs(e)) for r, e in seen},
                 "all sign patterns give the same parity/|error| set")
        rows.append({"J": depth, "sign_patterns": len(patterns),
                     "sup_error": str(claimed(depth)),
                     "odd_output_sup": str(claimed(depth - 1) if depth else 0),
                     "distinct_errors": len(errs)})
    return rows


def engine_a_period(depth=3, trials=400):
    """Sample the period lemma used by engine A on literal networks.

    The lemma itself is proved in README.md (and #6129 PROOF.md); this is a
    consistency control, not its proof."""
    import random
    rng = random.Random(6129)
    n = 1 << depth
    for _ in range(trials):
        x = [rng.randrange(-50, 50) for _ in range(n)]
        z = [rng.randrange(-5, 6) for _ in range(n)]
        y = [a + (2 * n) * b for a, b in zip(x, z)]
        need(errors(x, list(range(depth))) == errors(y, list(range(depth))),
             "period 2^(J+1) per input")
    return trials


# ---------------------------------------------------------------- engine B
def network(x, order, rnd=r_even):
    vals = [Fraction(v) for v in x]
    n = len(vals)
    for bit in order:
        w = 1 << bit
        out = list(vals)
        for i in range(n):
            if not i & w:
                a, b = vals[i], vals[i | w]
                out[i] = (a + b) / 2
                out[i | w] = (a - b) / 2
                if rnd is not None:
                    out[i], out[i | w] = Fraction(rnd(out[i])), Fraction(rnd(out[i | w]))
        vals = out
    return vals


def errors(x, order, rnd=r_even):
    exact = network(x, order, None)
    got = network(x, order, rnd)
    return [g - e for g, e in zip(got, exact)]


def engine_b():
    depth, n = 3, 8
    best = {}
    for order in ([0, 1, 2], [2, 1, 0], [1, 0, 2]):
        top = Fraction(0)
        for x in product(range(-3, 1), repeat=n):
            e = max(abs(v) for v in errors(x, order))
            need(e <= claimed(depth), "box input exceeds a_3")
            top = max(top, e)
        need(top == claimed(depth), "a_3 attained in [-3,0]^8")
        best[str(order)] = str(top)
    return {"inputs_per_order": 4 ** n, "orders": best}


# ---------------------------------------------------------------- engine C
def surrogate(x8, rule=r_even, strict=True):
    """#6119 surrogate rebuilt from its definition; x8 in units of h, returns
    the normalized error vector in units of h. Units of h/8 internally."""
    unit = 8
    q = [0] * 8
    for old in range(8):  # exposure: original bit 1 becomes bit 0
        q[(old & 4) | ((old & 1) << 1) | ((old & 2) >> 1)] = old

    def rnd(vals):  # nearest-even to the h grid, values in h/8 units
        return [rule(Fraction(v, unit)) * unit for v in vals]

    v = [x8[q[i]] * unit for i in range(8)] + [0] * 4
    m_num, m_den, a = 1, 2, 4
    v = rnd([v[i] if i < 8 else v[i] + Fraction(m_num * v[i - 8], m_den) for i in range(12)])
    v = rnd([v[i] + a * v[i + 8] if i < 4 else v[i] for i in range(12)])
    v = rnd([v[i] - a * v[i + 8] if i < 4 else v[i] for i in range(12)])
    v = rnd([v[i] if i < 8 else v[i] - Fraction(m_num * v[i - 8], m_den) for i in range(12)])
    if not strict:
        return v[8:]
    need(v[8:] == [0] * 4, "echo temporaries return to zero on grid inputs")
    w = list(v)
    for i in range(0, 12, 2):
        w[i], w[i + 1] = Fraction(v[i] + v[i + 1], 2), Fraction(v[i] - v[i + 1], 2)
    v = rnd(w)
    back = [0] * 8
    for i in range(8):
        back[q[i]] = v[i]
    w = list(back)
    for i in range(4):
        w[i], w[i + 4] = Fraction(back[i] + back[i + 4], 2), Fraction(back[i] - back[i + 4], 2)
    out = [Fraction(t, unit) for t in rnd(w)]
    exact = [sum(Fraction((-1) ** bin(i & j & 6).count("1"), 4) * x8[j]
                 for j in range(8) if not (i ^ j) & 1) for i in range(8)]
    return [o - e for o, e in zip(out, exact)]


def engine_c():
    top, count = Fraction(0), 0
    for spectator in (0, 1):
        for vals in product(range(8), repeat=4):
            x = [0] * 8
            for k, idx in enumerate(i for i in range(8) if i & 1 == spectator):
                x[idx] = vals[k]
            e = max(abs(t) for t in surrogate(x))
            top = max(top, e)
            count += 1
    need(top == Fraction(3, 4), "surrogate sharp normalized error 3h/4")
    witness = [0, 0, -1, 0, -2, 0, 0, 0]  # (0,0,-1/4,0,-1/2,0,0,0) at h=1/4
    need(max(abs(t) for t in surrogate(witness)) == Fraction(3, 4), "#6129 witness")
    import random
    rng = random.Random(6119)
    for _ in range(300):
        x = [rng.randrange(-40, 40) for _ in range(8)]
        z = [rng.randrange(-4, 5) for _ in range(8)]
        need(surrogate([a + 8 * b for a, b in zip(x, z)]) == surrogate(x),
             "period 8h per input on the surrogate")
    # Control: with ties-to-odd the lower inverse leaves +/-h on odd inputs,
    # so the echo is not clean; the #6119 application needs ties-to-even.
    dirty = [k for k in range(8) if surrogate([k] + [0] * 7, r_odd, strict=False) != [0] * 4]
    need(dirty == [1, 3, 5, 7], "ties-to-odd leaves the echo temporary dirty exactly on odd k")
    return {"fiber_inputs": count, "sup_over_h": str(top),
            "ties_to_odd_dirty_residues": dirty,
            "at_h_1_4": str(top / 4), "raw_recovery": str(top)}


# ---------------------------------------------------------------- engine D
def r_away(q):
    """Nearest integer, ties away from zero (not 2-periodic near 0)."""
    fl = q.numerator // q.denominator
    if q - fl != Fraction(1, 2):
        return r_even(q)
    return fl + 1 if q > 0 else fl


def engine_d(max_depth=5):
    out = {}
    for name, rule in (("ties_to_odd", r_odd), ("floor", r_floor)):
        vals = []
        for depth in range(max_depth + 1):
            states, _ = tree_states(depth, (1,) * depth, rule)
            vals.append(max(abs(e) for _, e in states))
        out[name] = [str(t) for t in vals]
        if name == "ties_to_odd":
            need(vals == [claimed(d) for d in range(max_depth + 1)],
                 "ties-to-odd has the same sharp law")
        else:
            need(vals == [Fraction(d, 2) for d in range(max_depth + 1)],
                 "floor attains the stagewise J/2")
    away = max(max(abs(t) for t in errors(x, [0, 1], r_away))
               for x in product(range(-8, 8), repeat=4))
    need(away == 1, "ties-away-from-zero attains J/2 at J=2 on [-8,8)^4")
    out["ties_away_J2_box_lower_bound"] = str(away)
    return out


def main():
    result = {
        "engine_A_residue_tree_sets": engine_a(),
        "engine_A_period_lemma_samples": engine_a_period(),
        "engine_B_literal_J3_box": engine_b(),
        "engine_C_pr6119_surrogate": engine_c(),
        "engine_D_controls_sup_error_by_J": engine_d(),
        "conclusion": "PASS: PR6129 formula, parity split and #6119 3h/4 application reproduced",
    }
    json.dump(result, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
