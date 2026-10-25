#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact COPY deletion and source-code planning budgets, not supplier admission.

Standard library only. All decisions use rational enclosures. Source and
historical allocation proof attribution are recorded in PROOF.md.
Substantial OpenAI Codex assistance.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from math import prod
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
M, W, CALLS, REPLICAS = 64, 28416, 288, 32
EPSILON = Q(1, 10**16)
SURCHARGE = 32 * M**2 * EPSILON
BIN_COUNTS = {7: 21312, 14: 14208, 28: 14208, 42: 14208}
H = {1: 1322, 2: 1342, 3: 79, 4: 39, 5: 102, 6: 11, 7: 18}
H429 = {1: 1298, 2: 1342, 3: 79, 4: 44, 5: 93, 6: 11, 7: 9}
SELECTED_KAPPA = Q(836330098538459, 500000000000000000)
TARGET_KAPPA = Q(11, 10) * SELECTED_KAPPA
TARGET = TARGET_KAPPA / (1 - TARGET_KAPPA)
PINS = {
    "../inputs/WORD.json.gz":
        "c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c",
    "../inputs/GEOMETRY.json.gz":
        "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
    "../inputs/global_k.py.txt":
        "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8",
    "../inputs/FULL-CALLER-PROOF.md":
        "ebdd9283a7762e01f84ee9dde8885d4ba05cc6c93a4430296ff0a71ea7205832",
    "../inputs/full-check-screens.py.txt":
        "c07d15a1e5edcbbab584fd77b26c2e6787c2baa4ef013de72dbfd52f5d2960e6",
    "../inputs/full-exact-interval.py.txt":
        "d8a78c2a2f87a5cf9fff0367d70f21dcdb712a509ba365879aee134b18c4c25d",
    "../inputs/full-invoices.json":
        "d0877305ca03e88622586fd76622fc9e2e2da0484de3b112577467c82f386a92",
    "inputs/SOURCE-CODE-WORD.json.gz":
        "1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870",
    "inputs/SOURCE-CODE-EXPECTED.json":
        "f078222ab4e99aff085262c00ba77520cc62eb02003d8e0582ab6ad7dab7f402",
    "inputs/SOURCE-CODE-PROOF.md":
        "ebcc91e74938b525b28e46bf03ec09d42d24ab02070dc96f4f0a51cee2cfb83d",
    "inputs/SELECTED-ASSEMBLY.json":
        "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "inputs/SELECTED-RECORD.json":
        "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
    "inputs/DIRECT-FLOOR-PRIOR-README.md":
        "7c833024359891e15766be310c3d1a4579dd0231fe7ffdbf981fd0814bac2dfb",
}


def need(test, message):
    if not test:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Compile these pinned source bytes explicitly, ignoring Python bytecode caches.
_interval_path = HERE / "../inputs/full-exact-interval.py.txt"
need(digest(_interval_path) == PINS["../inputs/full-exact-interval.py.txt"],
     "pinned interval arithmetic source")
_interval = types.ModuleType("_copy_budget_exact")
exec(compile(_interval_path.read_bytes(), str(_interval_path), "exec",
             dont_inherit=True, optimize=0), _interval.__dict__)
add, exact, linear_phi, mul, phi, power, report, sub = (
    getattr(_interval, name) for name in
    ("add", "exact", "linear_phi", "mul", "phi", "power", "report", "sub"))


def combine(*terms):
    result = Counter()
    for factor, coefficients in terms:
        for rank, count in coefficients.items():
            result[rank] += factor * Q(count)
    return {r: Q(n) for r, n in sorted(result.items()) if n}


def validate_histogram(hist):
    need(all(isinstance(r, int) and 0 < r < M and n >= 0
             for r, n in hist.items()), "contracting nonnegative histogram")


def idle_primal(full, partial):
    """The prior all-parameter LP theorem, with the resource premises checked."""
    c7, c14, c28, c42 = (BIN_COUNTS[r] for r in (7, 14, 28, 42))
    need(0 <= partial <= c28, "partial helper inventory in LP regime")
    need(c14 + 3*c28 <= full <= c14 + 3*c28 + 5*c42,
         "full helper inventory in LP regime")
    t = Q(full - c14 - 3*c28, 5)
    patterns = {(7, 0, 0): Q(c7), (14, 1, 0): Q(c14),
                (28, 3, 0): Q(c28-partial), (28, 3, 1): Q(partial),
                (42, 5, 0): t, (42, 0, 0): c42-t}
    for r, count in BIN_COUNTS.items():
        need(sum(n for (R, _, _), n in patterns.items() if R == r) == count,
             "all public bins retained")
    need(sum(a*n for (_, a, _), n in patterns.items()) == full,
         "all full helpers retained")
    need(sum(d*n for (_, _, d), n in patterns.items()) == partial,
         "all partial helpers retained")
    idle = Counter()
    for (r, a, d), count in patterns.items():
        remainder = r - 8*a - 4*d
        need(remainder >= 0 and count >= 0, "nonnegative whole pattern")
        if remainder:
            idle[remainder] += count
    need(sum(r*n for r, n in idle.items()) ==
         sum(r*n for r, n in BIN_COUNTS.items()) - 8*full - 4*partial,
         "returned owner rank mass")
    return dict(sorted(idle.items())), [
        {"R": r, "full8": a, "partial4": d, "bins": str(n)}
        for (r, a, d), n in sorted(patterns.items())]


def full_profile(local, full, partial):
    idle, patterns = idle_primal(full, partial)
    hist = combine((CALLS, local), (1, idle))
    validate_histogram(hist)
    return hist, patterns


@lru_cache(None)
def surcharge_per_child(b):
    return mul(power(M, b), SURCHARGE)


def chi(rank, b):
    return add(phi(rank, b), surcharge_per_child(b))


def bill(hist, b, charged=True):
    result = linear_phi(hist, b)
    if charged:
        result = add(result, mul(surcharge_per_child(b), sum(hist.values())))
    return result


def excess(hist, b=TARGET, charged=True):
    return sub(bill(hist, b, charged), exact(M*W))


def quotient(numerator, denominator):
    need(denominator[0] > 0, "positive interval denominator")
    candidates = [x/y for x in numerator for y in denominator]
    return min(candidates), max(candidates)


def strict_integer_cap(allowance, cost):
    """Largest integer n with n*cost < allowance; adjacent signs are checked."""
    ratio = quotient(allowance, cost)
    lo, hi = (x.numerator // x.denominator for x in ratio)
    need(lo == hi, "integer cap isolated")
    n = lo
    need(sub(allowance, mul(cost, n))[0] > 0, "integer cap accepted")
    need(sub(allowance, mul(cost, n+1))[1] < 0, "next integer rejected")
    return {"maximum": n, "ratio": report(ratio),
            "accepted_slack": report(sub(allowance, mul(cost, n))),
            "next_slack": report(sub(allowance, mul(cost, n+1)))}


def root_bracket(hist, mode="charged"):
    """Adjacent 10^-15 rational grid points; explicit opposite moment signs."""
    need(mode in ("charged", "raw", "free_bad"), "root tariff mode")
    def evaluate(b):
        if mode == "free_bad":
            return sub(mul(bill(hist, b, False), 1-EPSILON), exact(M*W))
        return excess(hist, b, mode == "charged")
    scale = 10**15
    lo, hi = 0, scale // 50
    need(evaluate(Q(lo, scale))[1] < 0 and
         evaluate(Q(hi, scale))[0] > 0, "initial root bracket")
    while hi-lo > 1:
        mid = (lo+hi)//2
        interval = evaluate(Q(mid, scale))
        if interval[1] < 0:
            lo = mid
        elif interval[0] > 0:
            hi = mid
        else:
            raise ValueError("grid root not separated by exact intervals")
    return {"lower": str(Q(lo, scale)), "upper": str(Q(hi, scale)),
            "mode": mode,
            "lower_excess": report(evaluate(Q(lo, scale))),
            "upper_excess": report(evaluate(Q(hi, scale)))}


def screen(hist, patterns=None, roots=False):
    raw = excess(hist, charged=False)
    charged = excess(hist)
    free_bad = sub(mul(bill(hist, TARGET, False), 1-EPSILON), exact(M*W))
    allowance = mul(charged, -1)
    row = {"H": {str(r): str(n) for r, n in hist.items()},
           "children": str(sum(hist.values())),
           "rank_mass": str(sum(r*n for r, n in hist.items())),
           "deficit": str(M*W-sum(r*n for r, n in hist.items())),
           "raw_excess": report(raw), "charged_excess": report(charged),
           "free_bad_excess": report(free_bad),
           "charged_extra_moment_allowance_global": report(allowance),
           "charged_extra_moment_allowance_per_call":
               report(mul(allowance, Q(1, CALLS))),
           "raw_extra_moment_allowance_per_call":
               report(mul(raw, -Q(1, CALLS)))}
    if patterns is not None:
        row["primal_patterns"] = patterns
        row["integral_pattern_counts"] = all(Q(p["bins"]).denominator == 1
                                            for p in patterns)
    if allowance[0] > 0:
        row["additional_equal_rank_children_per_call"] = {
            str(r): strict_integer_cap(allowance, mul(chi(r, TARGET), CALLS))
            for r in (1, 2, 4, 7, 8, 9, 14, 28, 42, 63)}
        row["arbitrary_extra_rank_mass_per_call"] = (
            row["additional_equal_rank_children_per_call"]["1"])
        row["one_decoder_per_replica_rank1_children"] = strict_integer_cap(
            allowance, mul(chi(1, TARGET), REPLICAS))
    if roots:
        row["charged_root_bracket"] = root_bracket(hist)
    return row


def dual_controls():
    """All 64 feasible whole patterns, plus exact all-parameter endpoint signs."""
    l8 = {2: Q(1, 5), 42: -Q(1, 5)}
    l4 = {4: Q(-1)}
    mus = {7: {7: 1}, 14: combine((1, {6: 1}), (-1, l8)),
           28: combine((1, {4: 1}), (-3, l8)), 42: {42: 1}}
    strict, equal = [], []
    for R in BIN_COUNTS:
        for a in range(R//8+1):
            for d in range((R-8*a)//4+1):
                r = R-8*a-4*d
                coeff = combine((1, {r: 1} if r else {}),
                                (-a, l8), (-d, l4), (-1, mus[R]))
                if coeff:
                    slack = linear_phi(coeff, TARGET)
                    need(slack[0] > 0, "strict LP dual pattern slack")
                    strict.append({"pattern": [R, a, d], "slack": report(slack)})
                else:
                    equal.append([R, a, d])
    need(len(strict)+len(equal) == 64, "all feasible whole patterns")
    endpoint_signs = []
    for terms in ([(14, 5), (2, 1), (6, -5), (42, -1)],
                  [(28, 5), (2, 3), (4, -5), (42, -3)]):
        need(sum(c for _, c in terms) == sum(r*c for r, c in terms) == 0,
             "four-power endpoint zeros")
        def ratio(weights):
            return Q(prod(r**c for r, c in weights if c > 0),
                     prod(r**(-c) for r, c in weights if c < 0))
        q0, q1 = ratio(terms), ratio([(r, r*c) for r, c in terms])
        need(q0 > 1 and q1 < 1, "four-power derivative endpoint signs")
        endpoint_signs.append({"terms": terms, "exp_derivative_at_zero": str(q0),
                               "exp_derivative_at_one": str(q1)})
    return {"patterns": 64, "equalities": equal, "strict": strict,
            "all_parameter_endpoint_products": endpoint_signs,
            "written_all_parameter_proof": "../inputs/FULL-CALLER-PROOF.md"}


def direct_copy_floor(base, patterns, roots):
    """Conditional on the construction audit's N>=9, ranks6..8, mass>=63."""
    optimal = {6: 4, 7: 1, 8: 4}
    need(sum(optimal.values()) == 9 and sum(r*n for r, n in optimal.items()) == 63,
         "direct factorization optimal relaxed COPY profile")
    hist = combine((1, base), (CALLS, {6: 4, 7: -8, 8: 4}))
    row = screen(hist, patterns, roots)
    need(Q(row["free_bad_excess"]["lower"]) > 0,
         "every direct mass63 shape fails target even with free bad packets")
    competitors = []
    for n in (9, 10):
        for n6 in range(n+1):
            for n7 in range(n-n6+1):
                n8 = n-n6-n7
                candidate = {r: c for r, c in ((6, n6), (7, n7), (8, n8)) if c}
                if sum(r*c for r, c in candidate.items()) < 63:
                    continue
                diff = combine((1, candidate), (-1, optimal))
                if not diff:
                    continue
                slack = add(linear_phi(diff, TARGET),
                            mul(surcharge_per_child(TARGET), n-9))
                need(slack[0] > 0, "every nine/ten-child competitor dearer")
                competitors.append({"H": candidate, "charged_slack": report(slack)})
    tail = sub(mul(chi(6, TARGET), 11),
               add(linear_phi(optimal, TARGET), mul(surcharge_per_child(TARGET), 9)))
    need(tail[0] > 0, "all eleven-or-more children dearer")
    row["construction_premise"] = {
        "minimum_child_count": 9, "ranks": [6, 7, 8], "minimum_rank_mass": 63,
        "source": "separate actual source-query/direct-reader factorization audit",
        "prior_63_floor_credit": "Russell Seligmann PR757 and Cody Harris PR761; "
            "see inputs/DIRECT-FLOOR-PRIOR-README.md for the historical model",
        "not_reproved_by_this_cost_checker": True}
    row["optimal_COPY_histogram"] = optimal
    row["all_nine_ten_child_competitors"] = competitors
    row["eleven_or_more_lower_bound_slack"] = report(tail)
    row["raw_saving_per_local_call"] = report(
        linear_phi({6: -4, 7: 8, 8: -4}, TARGET))
    if roots:
        row["free_bad_root_bracket"] = root_bracket(hist, "free_bad")
        ceiling = Q(row["free_bad_root_bracket"]["upper"])
        row["strict_kappa_gain_ceiling_percent"] = str(
            100*(ceiling/(1+ceiling)/SELECTED_KAPPA-1))
    return row


def actual_bins():
    """Reuse the literal source recipe and idle block with active source guards."""
    tree = ast.parse((PKG/"inputs/global_k.py.txt").read_bytes())
    recipe = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == "recipe")
    blocks = [n for n in ast.walk(tree) if isinstance(n, ast.If) and
              ast.unparse(n.test) == "s % 2 == 1 and s <= 2 * K - 3"]
    need(len(blocks) == 1, "unique source idle block")
    class Guards(ast.NodeTransformer):
        def visit_Assert(self, node):
            return ast.copy_location(ast.Expr(value=ast.Call(
                func=ast.Name(id="need", ctx=ast.Load()),
                args=[node.test, ast.Constant(value="source controller guard")],
                keywords=[])), node)
    env = {"__builtins__": {"range": range, "dict": dict, "reversed": reversed}}
    exec(compile(ast.fix_missing_locations(ast.Module(
        body=[recipe], type_ignores=[])), "source-recipe", "exec",
        dont_inherit=True, optimize=0), env)
    block = ast.fix_missing_locations(Guards().visit(ast.Module(
        body=[blocks[0]], type_ignores=[])))
    code = compile(block, "source-idle", "exec", dont_inherit=True, optimize=0)
    levels, schedule, calls = [-1]*4, [], 0
    for event in env["recipe"](4):
        if event["kind"] == "local":
            s, p = event["stage"], event["pair"]
            need(levels[p] == s-1, "source local entrance")
            levels[p] = s
            calls += REPLICAS
            exec(code, {"__builtins__": {"range": range, "dict": dict},
                        "need": need, "K": 4, "s": s, "levels": levels,
                        "schedule": schedule})
        elif event["kind"] == "bridge":
            need(levels[event["dst"]] == levels[event["src"]],
                 "source bridge entrance")
        else:
            need(event["kind"] == "exchange" and levels == [8]*4,
                 "source terminal entrance")
    ranks = [e["rank"] for e in schedule]
    bins = Counter()
    for r in ranks:
        if r:
            bins[r] += 2*111*REPLICAS
    need(dict(bins) == BIN_COUNTS and calls == CALLS, "actual bins and calls")
    need(W == 2*4*111*REPLICAS, "actual public stock, excluding private reserve")
    return {"idle_ranks": ranks, "bins": dict(bins), "calls": calls,
            "W": W, "private_reserve": 9,
            "extraction_only_not_changed_source_admission": True}


def source_controls():
    for name, pin in PINS.items():
        need(digest(HERE/name) == pin, "source SHA-256: "+name)
    geo = json.loads(gzip.decompress((PKG/"inputs/GEOMETRY.json.gz").read_bytes()))
    need((geo["h"], geo["v"], geo["R"]) == (8, 111, 438), "source geometry")
    @lru_cache(None)
    def dim(f):
        pivots = {}
        for label in geo["frames"][f]:
            row = list(map(Q, geo["lines"][label]))
            for p, basis in sorted(pivots.items()):
                a = row[p]
                if a:
                    row = [x-a*y for x, y in zip(row, basis)]
            pivot = next((j for j, x in enumerate(row) if x), None)
            if pivot is not None:
                a = row[pivot]
                pivots[pivot] = [x/a for x in row]
            if len(pivots) == 8:
                break
        return len(pivots)
    out = {}
    for name, path, want_h, widths, copy_ranks in (
            ("five_terminals", PKG/"inputs/WORD.json.gz", H, {4: 5, 8: 433}, [7]*9),
            ("coded429", HERE/"inputs/SOURCE-CODE-WORD.json.gz", H429, {8: 429}, [1]*3)):
        word = json.loads(gzip.decompress(path.read_bytes()))
        need(all(f == 0 for f in word["start"][222:]), "zero-start helper frames")
        got_widths = Counter(dim(f) for f in word["final"][222:])
        need(got_widths == widths, "literal terminal helper width inventory")
        paid, copies, adds = Counter(), [], 0
        for op, dst, src, c, f, z in word["records"]:
            if op == 0:
                need(dim(c)-dim(src) == f >= 0, "actual MOVE rank")
                if f:
                    paid[f] += 1
            elif op == 1:
                adds += 1
            elif op == 2:
                rank = dim(c)-dim(f)
                need(rank > 0 and src == len(word["start"]), "actual COPY rank")
                paid[rank] += 1
                copies.append(rank)
            else:
                need(op == 3, "record opcode")
        need(dict(paid) == want_h and copies == copy_ranks,
             "complete literal local query histogram")
        out[name] = {"H": dict(sorted(paid.items())), "helper_widths": dict(got_widths),
                     "COPY_ranks": copies, "ADDs": adds,
                     "children": sum(paid.values()),
                     "rank_mass": sum(r*n for r, n in paid.items())}
    expected = json.loads((HERE/"inputs/SOURCE-CODE-EXPECTED.json").read_bytes())
    need(expected["dirty_helpers"] == 429 and expected["rank_mass"] == 4989,
         "coded historical expected contract")
    need(expected["deleted_original_families"] == list(range(471, 480)),
         "nine deleted historical helper families")
    return {"pins": PINS, "literal_profiles": out, "controller": actual_bins(),
            "does_not_reprove_arbitrary_input_operator_or_restoration": True}


def rejection(label, action):
    try:
        action()
    except ValueError:
        return {"control": label, "rejected": True}
    raise ValueError("negative control escaped: "+label)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=HERE/"BUDGET.json")
    ap.add_argument("--skip-roots", action="store_true")
    args = ap.parse_args()
    sources = source_controls()
    need(TARGET == Q(9199631083923049, 4990800368916076951),
         "exact necessary 10 percent primitive target")
    base, patterns = full_profile(H, 433*CALLS, 5*CALLS)
    need(sum(r*n for r, n in base.items()) == 1808352, "baseline full mass")
    need(excess(base, charged=False)[0] > 0, "zero deletion rejects 10 percent")
    ideal = {}
    for k in range(10):
        hist = combine((1, base), (-k*CALLS, {7: 1}))
        validate_histogram(hist)
        ideal[str(k)] = screen(hist, patterns, not args.skip_roots and k in (0, 1, 9))
        need((excess(hist)[1] < 0) == (k >= 1), "uniform deletion threshold")
    # Arbitrary deletion locations, before legal sharing/chronology are proved.
    deletion_ratio = quotient(excess(base), chi(7, TARGET))
    minimum = deletion_ratio[1].numerator // deletion_ratio[1].denominator + 1
    need(minimum == 85, "total COPY deletion threshold")
    arbitrary, arbitrary_raw, arbitrary_free_bad = {}, {}, {}
    for count in (minimum-1, minimum):
        hist = combine((1, base), (-count, {7: 1}))
        e = excess(hist)
        need(e[0] > 0 if count == minimum-1 else e[1] < 0,
             "adjacent total COPY deletion signs")
        arbitrary[str(count)] = report(e)
        raw = excess(hist, charged=False)
        free_bad = sub(mul(bill(hist, TARGET, False), 1-EPSILON), exact(M*W))
        arbitrary_raw[str(count)] = report(raw)
        arbitrary_free_bad[str(count)] = report(free_bad)
        if count == minimum-1:
            need(free_bad[0] > 0, "84 deletions fail even the raw LP free-bad lower bound")
    # Existing ordinary chronological invoice, held fixed under ideal deletions.
    invoices = json.loads((PKG/"inputs/full-invoices.json").read_bytes())
    literal = {int(r): Q(n) for r, n in
               invoices["profiles"]["reuse/reference"]["H"].items()}
    need(sum(r*n for r, n in literal.items()) == 1808352, "literal reference mass")
    literal_one = screen(combine((1, literal), (-CALLS, {7: 1})))
    need(excess(combine((1, literal), (-CALLS, {7: 1})))[1] < 0,
         "one deletion on fixed constructed owner invoice")
    # Coded word: 429 full helpers; do not pretend five are already partial.
    coded, coded_patterns = full_profile(H429, 429*CALLS, 0)
    old_allfull, _ = full_profile(combine((1, H), (5, {4: 1})), 438*CALLS, 0)
    old_idle, _ = idle_primal(438*CALLS, 0)
    coded_idle, _ = idle_primal(429*CALLS, 0)
    owner_return = combine((1, coded_idle), (-1, old_idle))
    need(owner_return == {2: -Q(2592, 5), 42: Q(2592, 5)},
         "every removed helper returns its entire owner obligation")
    need(sum(r*n for r, n in owner_return.items()) == 72*CALLS,
         "72 owner rank units returned per call")
    need(sum(r*n for r, n in coded.items()) == 1791072 and
         sum(r*n for r, n in old_allfull.items()) == 1808352,
         "net coded saving exactly 60 per call")
    combined, combined_patterns = full_profile(
        combine((1, H429), (-5, {4: 1})), 424*CALLS, 5*CALLS)
    need(sum(r*n for r, n in combined.items()) == 1791072,
         "hypothetical combined profile retains same complete mass")
    coded_rows = {
        "coded429_full": screen(coded, coded_patterns, not args.skip_roots),
        "coded424_full5_partial_if_terminal_adaptation_proved":
            screen(combined, combined_patterns, not args.skip_roots)}
    improvement = sub(bill(coded, TARGET), bill(combined, TARGET))
    need(improvement[0] > 0, "conditional terminal adaptation favorable")
    # Pure deletions only: mass efficiency ranges from chi(63)/63 to chi(1).
    mass_best = quotient(excess(base), chi(1, TARGET))
    mass_worst = quotient(excess(base), mul(chi(63, TARGET), Q(1, 63)))
    need(mass_best[0] > 586 and mass_best[1] < 587, "best pure mass threshold")
    need(mass_worst[0] > 590 and mass_worst[1] < 591, "uniform pure mass threshold")
    need(excess(combine((1, base), (-587, {1: 1})))[1] < 0,
         "587 rank-one deletions meet the arithmetic screen")
    selected = json.loads((HERE/"inputs/SELECTED-ASSEMBLY.json").read_bytes())
    need(Q(selected["kappa"]) == SELECTED_KAPPA and selected["binding"] == "complex",
         "selected assembly exact binding")
    complex_c = Q(selected["complex_lower"])
    need(complex_c < TARGET and complex_c/(1+complex_c) < TARGET_KAPPA,
         "selected complex endpoint cannot support target")
    controls = [
        rejection("missing_owner_return72", lambda: need(
            sum(r*n for r, n in combine((CALLS, H429), (1, old_idle)).items())
            == 1791072, "owner return required")),
        rejection("429_full_plus5_partial_without_inventory_change",
                  lambda: need(429+5 == expected_helpers(), "physical helper count")),
        rejection("partial_progress_without_removing5_rank4_moves",
                  lambda: need(sum(r*n for r, n in full_profile(
                      H429, 424*CALLS, 5*CALLS)[0].items()) == 1791072,
                      "changed terminal local tariff")),
        rejection("rank_mass_only_substitution",
                  lambda: need(linear_phi({1: 1, 2: -2, 3: 1}, TARGET)[1] >= 0,
                               "equal mass need not have equal moment")),
        rejection("extra_private_reserve_output_credit",
                  lambda: need(W+9 == 2*4*111*REPLICAS, "private reserve is not public stock")),
        rejection("out_of_regime_helper_inventory",
                  lambda: idle_primal(0, 0)),
    ]
    receipt = {
        "status": "PASS_EXACT_COPY_PATH_BUDGETS", "no_new_kappa": True,
        "scientific_scope": "Conditional complete query-moment planning. LP lower "
            "bounds do not assert chronological attainability; adding the inherited "
            "surcharge prices the displayed primal, without claiming charged LP "
            "optimality. Coded source needs a new caller/decoder contract.",
        "sources": sources, "target_primitive": str(TARGET),
        "target_kappa": str(TARGET_KAPPA),
        "selected_kappa": str(SELECTED_KAPPA),
        "inherited_per_child_surcharge_coefficient": str(SURCHARGE),
        "LP_dual": dual_controls(), "ideal_uniform_COPY7_deletions": ideal,
        "direct_query_mass63_lower_bound": direct_copy_floor(
            base, patterns, not args.skip_roots),
        "minimum_uniform_deletions_per_call": 1,
        "minimum_arbitrary_global_COPY7_deletions": minimum,
        "arbitrary_global_deletion_ratio": report(deletion_ratio),
        "adjacent_global_deletion_excess": arbitrary,
        "adjacent_global_deletion_raw_excess": arbitrary_raw,
        "adjacent_global_deletion_free_bad_excess": arbitrary_free_bad,
        "fixed_constructed_owner_invoice_one_deletion": literal_one,
        "pure_deletion_mass": {
            "premise": "Only paid children removed, all ranks 1..63, no added costs",
            "necessary_best_efficiency_mass": report(mass_best),
            "sufficient_all_rank_shapes_mass": report(mass_worst),
            "minimum_attainable_mass_in_relaxation": 587,
            "uniform_sufficient_integer_mass": 591,
            "COPY7_only_integer_mass": minimum*7,
            "warning": "Net mass with both additions and deletions does not determine moment"},
        "coded_owner_return_histogram": {str(r): str(n) for r, n in owner_return.items()},
        "coded_owner_return_mass_per_call": 72,
        "coded_net_complete_mass_saving_per_call": 60,
        "coded_profiles": coded_rows,
        "conditional_five_terminal_charged_improvement_global": report(improvement),
        "selected_complex_still_blocks_10_percent": True,
        "selected_complex_exact_endpoint": str(complex_c),
        "negative_controls": controls,
        "unresolved": [
            "legal sharing/deletion word with arbitrary dirty inputs and literal restoration",
            "coded-source caller and a paid terminal decoder at actual caps",
            "chronological integral whole-helper owners and changed source access",
            "precision, rounded cleanup, physical storage/tape and all-size native compilation",
            "a compatible improved complex supplier and every joint outer inequality"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print("PASS_EXACT_COPY_PATH_BUDGETS no_new_kappa")
    print("Minimum ideal uniform COPY7 deletions: 1; arbitrary total deletions: 85")
    print("Coded owner return: 72 rank units/call; net complete saving: 60/call")


def expected_helpers():
    return 429


if __name__ == "__main__":
    main()
