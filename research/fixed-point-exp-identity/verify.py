#!/usr/bin/env python3
"""Compare the opt-in fixed-point exponential with the pinned Taylor series.

Both engines are loaded unchanged from their pinned paths. The checks are:

1. three explicit rational witnesses in [0, 1/2] where the engines differ by
   one 2^-256 step, one for each possible difference allowed by PROOF.md;
2. a deterministic sweep (small denominators, dyadic grids, pseudo-random
   2^-400 rationals and every stopping-threshold neighbourhood) that checks
   the comparison theorem, the stopping-index relations and outward soundness
   against an independent 2^-420 enclosure of exp(y);
3. faithful integer replicas of both loops, matched against the engines on
   every swept argument, which expose the stopping indices K, J and J';
4. negative controls: a truncated fast series, a replica with a shifted stop
   rule, altered witnesses and out-of-range arguments.

Standard library only. Writes no files. Prints a receipt bound to every
package file and both live inputs.
"""
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PINNED = ROOT / "research/complex-local-word-ceiling/ceiling.py"
FAST = ROOT / "research/ceiling-exp-fixed-point/fast_exp.py"
PINS = {
    PINNED: "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
    FAST: "2310ed44a378a4312da8597afbaca7b9afb9ecf8444f30649379ab2ea0eaa2c4",
}
LEMMA = (
    "For every rational y in [0, 1/2], both fixed-point bounds enclose exp(y); "
    "the fixed-point lower bound equals the pinned one or is one 2^-256 step "
    "below it; the fixed-point upper bound is within one 2^-256 step of the "
    "pinned one in either direction. All three differences occur."
)
P = 256
ULP = Q(1, 1 << P)
THRESHOLD = Q(1, 1 << (P + 8))
HALF = Q(1, 2)
# (name, numerator, log2 denominator, lower step difference, upper step difference)
WITNESSES = (
    ("lower_below", 112820218673535760887793545904259590797381065892570661424580061060165255037665752986083267877235245850711931879344953535701995, 417, -1, 0),
    ("upper_above", 451280874694143043551174183617038363189524263570282645698320244240661020150663011662191663705856790611080739247516933954367195, 419, 0, 1),
    ("upper_below", 78399356583641526323813352267101195722476550890209629673398400468040250926551770777747114730408459053066364815584736195, 400, 0, -1),
)


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def load(path, name):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINS[path], f"{path.name} bytes changed")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def down(x):
    return Q((x.numerator << P) // x.denominator, 1 << P)


def up(x):
    return -down(-x)


def pinned_replica(y):
    """Exact pinned loop: stopping index K, lower and upper bounds."""
    s, t, k = Q(1), Q(1), 0
    while k < 200:
        k += 1
        t = t * y / k
        s += t
        if t * y < THRESHOLD:
            return k, down(s), up(s + 2 * t * y / (k + 1))
    raise SystemExit("FAIL: pinned replica did not stop")


def fast_replica(y, upper, stop_shift=0):
    """Integer fast loop: stopping index and bound. stop_shift is a control."""
    scale = P + 48
    unit = 1 << scale
    if upper:
        c = -((-y.numerator << scale) // y.denominator)
    else:
        c = (y.numerator << scale) // y.denominator
    total, term, step = unit, unit, 0
    stop = 2 * scale - (P + 8) + stop_shift
    while step < 200:
        step += 1
        num, den = term * c, step << scale
        term = -((-num) // den) if upper else num // den
        total += term
        if c == 0 or term * c < 1 << stop:
            if upper:
                tail = 2 * term * c
                total += -((-tail) // ((step + 1) << scale))
                return step, up(Q(total, unit))
            return step, down(Q(total, unit))
    raise SystemExit("FAIL: fast replica did not stop")


def exp_enclosure(y):
    """Independent enclosure of exp(y) with width below 2^-420, 0 <= y <= 1/2."""
    s, t = Q(1), Q(1)
    for k in range(1, 200):
        t = t * y / k
        s += t
        tail = t * y / (k + 1) * 2
        if tail < Q(1, 1 << 420):
            return s, s + tail
    raise SystemExit("FAIL: independent enclosure did not stop")


def classify(y, pinned, fast, stats):
    """Check every claim of the comparison theorem at one argument."""
    lo_p, hi_p = pinned.exp(y, y)
    lo_f, hi_f = fast.bounds(y, y, P, pinned.require)
    K, rlo_p, rhi_p = pinned_replica(y)
    J, rlo_f = fast_replica(y, False)
    J2, rhi_f = fast_replica(y, True)
    require((rlo_p, rhi_p, rlo_f, rhi_f) == (lo_p, hi_p, lo_f, hi_f), f"replica mismatch at {y}")
    e_lo, e_hi = exp_enclosure(y)
    require(lo_f <= e_lo and e_hi <= hi_f, f"fast enclosure unsound at {y}")
    require(lo_p <= e_lo and e_hi <= hi_p, f"pinned enclosure unsound at {y}")
    d_lo, d_hi = (lo_f - lo_p) / ULP, (hi_f - hi_p) / ULP
    require(d_lo in (-1, 0), f"lower difference {d_lo} at {y}")
    require(d_hi in (-1, 0, 1), f"upper difference {d_hi} at {y}")
    require(J <= K, f"fast lower loop stopped after pinned at {y}")
    require(J2 in (K, K + 1) or y == 0, f"fast upper loop index {J2} vs {K} at {y}")
    require(d_hi != -1 or J2 == K + 1, f"tighter upper bound without an extra term at {y}")
    key = (int(d_lo), int(d_hi), J - K, J2 - K)
    stats[key] = stats.get(key, 0) + 1
    return key


def sweep_arguments():
    """Deterministic argument list; every entry lies in [0, 1/2]."""
    args = {Q(0), HALF}
    for b in range(1, 61):
        for a in range(0, b // 2 + 1):
            args.add(Q(a, b))
    for e in (64, 128, 256, 300, 304, 305, 400):
        for a in (1, 3, 5, 7, (1 << (e - 1)) - 1):
            args.add(Q(a, 1 << e))
    state = 0x9E3779B97F4A7C15
    for _ in range(400):
        state = (state * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        numerator = (state << 336) | (state * 0xD1B54A32D192ED03 % (1 << 336))
        args.add(Q(numerator % (1 << 399), 1 << 400))
    return sorted(args)


def threshold_arguments():
    """Arguments straddling every stopping threshold t_k y = 2^-264 in (0, 1/2]."""
    out = []
    denominator = 1 << 400
    for k in range(1, 60):
        def gap(m):
            t = Q(1)
            for j in range(1, k + 1):
                t = t * Q(m, denominator) / j
            return t * Q(m, denominator) - THRESHOLD
        lo, hi = 0, denominator // 2
        if gap(hi) < 0:
            continue
        for _ in range(400):
            mid = (lo + hi) // 2
            lo, hi = (mid, hi) if gap(mid) < 0 else (lo, mid)
        require(hi - lo == 1, "threshold bisection did not converge")
        for offset in (-(1 << 300), -(1 << 120), -2, -1, 0, 1, 2, 1 << 120):
            m = lo + offset
            if 0 < m <= denominator // 2:
                out.append(Q(m, denominator))
    return out


def witnesses(pinned, fast):
    rows = []
    for name, numerator, log_den, want_lo, want_hi in WITNESSES:
        y = Q(numerator, 1 << log_den)
        require(0 < y <= HALF, f"{name} outside [0, 1/2]")
        key = classify(y, pinned, fast, {})
        require(key[:2] == (want_lo, want_hi), f"{name} differences {key[:2]}")
        rows.append({"name": name, "log2_denominator": log_den, "lower_steps": key[0],
                     "upper_steps": key[1], "J_minus_K": key[2], "J_upper_minus_K": key[3]})
    return rows


def controls(pinned, fast, near):
    """Each control must be rejected by the same checks used above."""
    rejected = 0
    y = Q(1, 3)
    e_lo, e_hi = exp_enclosure(y)
    lo_p, hi_p = pinned.exp(y, y)
    truncated = fast.series(y, True, P, max_terms=1)
    require(abs(truncated - hi_p) > ULP, "one-term series passed the one-step comparison")
    require(not e_hi <= fast.series(y, False, P), "lower series accepted as an upper enclosure")
    rejected += 2
    for name, numerator, log_den, want_lo, want_hi in WITNESSES:
        key = classify(Q(numerator, 1 << log_den), pinned, fast, {})
        for altered in ((want_lo + 1, want_hi), (want_lo, -want_hi or 1)):
            require(key[:2] != altered, f"{name} accepted altered differences {altered}")
            rejected += 1
    moved = 0
    for y in near:
        if fast_replica(y, True, stop_shift=-40) != fast_replica(y, True):
            moved += 1
    require(moved > 0, "a replica with a shifted stop rule was not detected")
    rejected += 1
    for bad in (HALF + Q(1, 1 << 400), Q(-1, 1 << 400)):
        for call in (lambda: pinned.exp(bad, bad), lambda: fast.bounds(bad, bad, P, pinned.require)):
            try:
                call()
            except ValueError:
                rejected += 1
                continue
            raise SystemExit(f"FAIL: accepted out-of-range argument {bad}")
    return rejected


def receipt():
    files = sorted(p for p in PACKAGE.iterdir() if p.is_file())
    out = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    for path in PINS:
        out[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def main():
    require(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    pinned = load(PINNED, "pinned_ceiling")
    fast = load(FAST, "fixed_point_exp")
    rows = witnesses(pinned, fast)
    stats = {}
    general = sweep_arguments()
    near = threshold_arguments()
    for y in general + near:
        classify(y, pinned, fast, stats)
    seen = {(k[0], k[1]) for k in stats}
    require({(-1, 0), (0, 1), (0, -1)} <= {(r["lower_steps"], r["upper_steps"]) for r in rows}, "witness set")
    rejected = controls(pinned, fast, near)
    summary = {
        "witnesses": rows,
        "general_arguments": len(general),
        "threshold_arguments": len(near),
        "outcomes": {f"lo{k[0]:+d}_hi{k[1]:+d}_J{k[2]:+d}_Jup{k[3]:+d}": v for k, v in sorted(stats.items())},
        "sweep_differences_seen": sorted(seen),
        "controls_rejected": rejected,
        "receipt_sha256": receipt(),
    }
    print(json.dumps(summary, indent=1, sort_keys=True))
    print(f"PASS_FIXED_POINT_EXP_IDENTITY witnesses=3 general={len(general)} "
          f"threshold={len(near)} controls={rejected} no_new_kappa")


if __name__ == "__main__":
    sys.exit(main())
