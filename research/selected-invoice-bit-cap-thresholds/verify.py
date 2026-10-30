"""Exact local thresholds for the selected P104 invoice to pass at C = 17/5000.

The invoice passes at saving C when its productive target moment exceeds its
paid moment, sum T_r r^(1-C) > sum P_r r^(1-C). Every r^(1-C) is evaluated
with correctly rounded decimal ln/exp at PREC digits; the accumulated error
is far below ERROR_BOUND, and every reported sign clears it.
"""

import hashlib
import json
import math
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

PREC = 80
ERROR_BOUND = Decimal("1e-50")
SIGN_FLOOR = Decimal("1e-30")
BIT_CAP = Fraction(17, 5000)
SELECTED_KAPPA = Fraction(62009, 20000000)
HERE = Path(__file__).resolve().parent
MARKER = "PASS_SELECTED_INVOICE_BIT_CAP_THRESHOLDS"

getcontext().prec = PREC


def dec(q):
    return Decimal(q.numerator) / Decimal(q.denominator)


def power(rank, c):
    if rank == 1:
        return Decimal(1)
    return (dec(1 - c) * Decimal(rank).ln()).exp()


def moment(targets, paid, c):
    total = sum((n * power(r, c) for r, n in targets.items()), Decimal(0))
    return total - sum((n * power(r, c) for r, n in paid.items()), Decimal(0))


def certified_sign(value):
    if abs(value) <= SIGN_FLOOR:
        raise SystemExit(f"FAIL: undecided sign {value}")
    return 1 if value > 0 else -1


def int_keys(table):
    return {int(r): n for r, n in table.items()}


def load():
    meta = json.loads((HERE / "INPUT.json").read_text())
    raw = (HERE / meta["invoice_file"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != meta["invoice_sha256"]:
        raise SystemExit("FAIL: invoice bytes differ from the exporter hash")
    invoice = json.loads(raw)
    parts = {k: int_keys(v) for k, v in meta["components"].items()}
    return meta, int_keys(invoice["paid"]), int_keys(invoice["targets"]), parts


def check_replication(paid, targets, parts, full):
    """Paid = full*local + query + idle; targets = full*helpers + main."""
    want_paid, want_targets = {}, {}
    for r, n in parts["local_paid"].items():
        want_paid[r] = want_paid.get(r, 0) + full * n
    for name in ("query_paid", "idle_paid"):
        for r, n in parts[name].items():
            want_paid[r] = want_paid.get(r, 0) + n
    for r, n in parts["local_helpers"].items():
        want_targets[r] = want_targets.get(r, 0) + full * n
    for r, n in parts["main_targets"].items():
        want_targets[r] = want_targets.get(r, 0) + n
    if want_paid != paid or want_targets != targets:
        raise SystemExit("FAIL: invoice is not the declared 18-fold local replication")


def bisect_root(targets, paid, lo, hi, width):
    if certified_sign(moment(targets, paid, lo)) != 1:
        raise SystemExit("FAIL: lower root bracket does not pass")
    if certified_sign(moment(targets, paid, hi)) != -1:
        raise SystemExit("FAIL: upper root bracket does not fail")
    while hi - lo > width:
        mid = (lo + hi) / 2
        if certified_sign(moment(targets, paid, mid)) == 1:
            lo = mid
        else:
            hi = mid
    return lo, hi


def min_deletions(local_paid, max_rank, need):
    """Fewest local paid deletions of rank <= max_rank whose per-FULL mass exceeds need."""
    total, count = Decimal(0), 0
    for r in sorted((r for r in local_paid if r <= max_rank), reverse=True):
        for _ in range(local_paid[r]):
            total += power(r, BIT_CAP)
            count += 1
            if total > need + SIGN_FLOOR:
                return count, total
    return None, total


def split_gain(rank, parts):
    return sum(power(p, BIT_CAP) for p in parts) - power(rank, BIT_CAP)


def min_splits(helpers, need, gain_of):
    """Fewest local helper targets split (each once, by gain_of) to exceed need."""
    gains = sorted(((gain_of(r), r) for r, n in helpers.items() for _ in range(n)), reverse=True)
    total = Decimal(0)
    for count, (gain, _) in enumerate(gains, start=1):
        total += gain
        if total > need + SIGN_FLOOR:
            return count, total
    return None, total


def main():
    meta, paid, targets, parts = load()
    full = meta["full_calls"]
    check_replication(paid, targets, parts, full)
    if meta["selected_kappa"] != f"{SELECTED_KAPPA.numerator}/{SELECTED_KAPPA.denominator}":
        raise SystemExit("FAIL: selected kappa changed")

    root = bisect_root(targets, paid, Fraction(31, 10000), Fraction(311, 100000), Fraction(1, 10**13))
    deficit = -moment(targets, paid, BIT_CAP)
    if certified_sign(deficit) != 1:
        raise SystemExit("FAIL: selected invoice already passes at 17/5000")
    need = deficit / full

    single = {r: certified_sign(power(r, BIT_CAP) - need) == 1 for r in range(1, 8)}
    deletions = {}
    for s in range(1, 8):
        deletions[s], _ = min_deletions(parts["local_paid"], s, need)

    refine = {r: split_gain(r, [1] * r) for r in parts["local_helpers"]}
    binary = {r: split_gain(r, [r // 2, r - r // 2]) if r > 1 else Decimal(0) for r in parts["local_helpers"]}
    full_count, full_mass = min_splits(parts["local_helpers"], need, lambda r: refine[r])
    bin_count, bin_mass = min_splits(parts["local_helpers"], need, lambda r: binary[r])

    refined_targets = dict(parts["main_targets"])
    rank_mass = sum(r * n for r, n in parts["local_helpers"].items())
    refined_targets[1] = refined_targets.get(1, 0) + full * rank_mass
    ceiling = bisect_root(refined_targets, paid, Fraction(1, 1000), Fraction(1, 10), Fraction(1, 10**13))

    controls = run_controls(paid, targets, parts, full, need)
    controls["all_helpers_refined_at_1_100"] = certified_sign(moment(refined_targets, paid, Fraction(1, 100)))
    if controls["all_helpers_refined_at_1_100"] != -1:
        raise SystemExit("FAIL: refined invoice passes at 1/100")
    controls["h9_refinements"] = h9_split_control(paid, targets, full, full_count, [1] * 9)
    controls["h9_binary_splits"] = h9_split_control(paid, targets, full, bin_count, [4, 5])
    result = {
        "marker": MARKER,
        "selected_root_bracket": [str(x) for x in root],
        "selected_root_decimal": [f"{float(x):.13f}" for x in root],
        "deficit_at_17_5000": f"{deficit:.12f}",
        "deficit_per_full": f"{need:.12f}",
        "full_calls": full,
        "single_local_paid_deletion_passes": single,
        "min_local_paid_deletions_with_rank_at_most": deletions,
        "full_refinement_gain_per_helper": {r: f"{g:.12f}" for r, g in sorted(refine.items())},
        "balanced_binary_gain_per_helper": {r: f"{g:.12f}" for r, g in sorted(binary.items())},
        "min_full_helper_refinements": full_count,
        "min_balanced_binary_splits": bin_count,
        "all_helpers_refined_root_bracket": [f"{float(x):.13f}" for x in ceiling],
        "controls": controls,
        "float_corroboration": float_corroboration(paid, targets, need),
    }
    print(json.dumps(result, indent=1, sort_keys=True))
    print(MARKER)


def float_corroboration(paid, targets, need):
    a = 1 - float(BIT_CAP)
    m = sum(n * r**a for r, n in targets.items()) - sum(n * r**a for r, n in paid.items())
    if not math.isclose(-m / 18, float(need), rel_tol=1e-9):
        raise SystemExit("FAIL: float and decimal deficits disagree")
    return f"{-m:.9f}"


def h9_split_control(paid, targets, full, count, pieces):
    """Split count local H9 targets into pieces; count passes and count-1 fails."""
    signs = []
    for k in (count - 1, count):
        t = dict(targets)
        t[9] -= full * k
        for piece in pieces:
            t[piece] = t.get(piece, 0) + full * k
        signs.append(certified_sign(moment(t, paid, BIT_CAP)))
    if signs != [-1, 1]:
        raise SystemExit(f"FAIL: H9 split control {pieces} {signs}")
    return {str(count - 1): signs[0], str(count): signs[1]}


def run_controls(paid, targets, parts, full, need):
    """Rerun the actual changed invoices for the boundary cases."""
    out = {}
    for rank, expect in ((4, -1), (5, 1)):
        p = dict(paid)
        p[rank] -= full
        out[f"delete_one_local_rank_{rank}"] = certified_sign(moment(targets, p, BIT_CAP))
        if out[f"delete_one_local_rank_{rank}"] != expect:
            raise SystemExit(f"FAIL: control rank {rank}")
    for k, expect in ((4, -1), (5, 1)):
        p = dict(paid)
        p[1] -= full * k
        out[f"delete_{k}_local_rank_1"] = certified_sign(moment(targets, p, BIT_CAP))
        if out[f"delete_{k}_local_rank_1"] != expect:
            raise SystemExit(f"FAIL: control {k} rank-one deletions")
    out["selected_passes_at_selected_kappa"] = certified_sign(moment(targets, paid, SELECTED_KAPPA))
    if out["selected_passes_at_selected_kappa"] != 1:
        raise SystemExit("FAIL: selected invoice does not pass at selected kappa")
    return out


if __name__ == "__main__":
    sys.exit(main())
