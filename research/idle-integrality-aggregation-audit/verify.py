#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Audit normalization before imposing integer idle counts; no physical admission.

New audit: OpenAI Codex at Arham Tahir's direction. Exact interval pricing is
Douglas Colkitt / Claude's unchanged ceiling.py. The aggregate optimum theorem
is Penguin (OpenAI) / Maximus Putnam's PR1685, not a new theorem here.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from math import gcd
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = "research/complex-local-word-ceiling/ceiling.py"
GRID = 10**15


def require(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    """Authenticate all live bytes before executing the credited price engine."""
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for row in pins["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row["sha256"],
                    "live source mismatch: " + row["path"])
    subject = json.loads((HERE / "AUDITED-SOURCE.json").read_text())
    for row in subject["files"]:
        data = (HERE / row["retained_path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "audited source mismatch: " + row["retained_path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == row["git_blob"], "audited Git blob mismatch")
    # Compile authenticated bytes directly: a neighboring .pyc is never read.
    engine = ModuleType("credited_ceiling")
    engine.__file__ = str(ROOT / ENGINE)
    exec(compile((ROOT / ENGINE).read_bytes(), engine.__file__, "exec"), engine.__dict__)
    return engine, subject


def histogram(raw):
    return {int(rank): count for rank, count in raw.items()}


def validate(hist, mass, cap):
    require(type(mass) is int and mass >= 0, "integer nonnegative mass required")
    require(type(cap) is int and cap >= 1, "positive integer cap required")
    require(all(type(r) is int and 1 <= r <= cap and type(n) is int and n >= 0
                for r, n in hist.items()), "integer histogram / rank cap required")
    require(sum(r*n for r, n in hist.items()) == mass, "idle mass mismatch")


def concentrated(mass, cap):
    """PR1685's strict-concavity optimum, at the stated aggregation unit."""
    validate({}, 0, cap)
    require(type(mass) is int and mass >= 0, "integer nonnegative mass required")
    count, residual = divmod(mass, cap)
    answer = {cap: count} if count else {}
    if residual:
        answer[residual] = 1
    validate(answer, mass, cap)
    return answer


def outward_decimal(x, upper=False, places=30):
    scale = 10**places
    scaled = x * scale
    value = -((-scaled.numerator)//scaled.denominator) if upper else scaled.numerator//scaled.denominator
    sign = "-" if value < 0 else ""
    value = abs(value)
    return f"{sign}{value//scale}.{value%scale:0{places}d}"


def enclosure(bounds):
    return {"exact": [str(v) for v in bounds],
            "outward_decimal": [outward_decimal(bounds[0]), outward_decimal(bounds[1], True)]}


@lru_cache(None)
def binomial_price(rank, m, a):
    """Independent positive-binomial bounds; no logarithms or exponentials.

    x^(1-a) = x * sum_k (a)_k/k! * (1-x)^k. For 0<a<1 the
    positive term ratio is <= z=1-x, so a geometric tail bounds all
    uncomputed terms. Integer floor/ceil propagation encloses each term.
    """
    require(0 < rank < m and 0 < a < 1, "binomial domain")
    scale = 1 << 192
    term_lo = term_hi = sum_lo = sum_hi = scale
    for k in range(20000):
        numerator = (a.numerator + k*a.denominator)*(m-rank)
        denominator = a.denominator*(k+1)*m
        term_lo = term_lo*numerator//denominator
        term_hi = -((-term_hi*numerator)//denominator)
        sum_lo += term_lo
        sum_hi += term_hi
        tail_hi = -((-term_hi*(m-rank))//rank)
        if tail_hi <= 1 << 52:  # Absolute series tail <= 2^-140.
            return Q(rank*sum_lo, m*scale), Q(rank*(sum_hi+tail_hi), m*scale)
    raise ValueError("binomial tail did not converge within the stated cap")


def run():
    C, subject = authenticate()
    asm = json.loads((ROOT / "research/community-frontier1094-audit/ASSEMBLY.json").read_text())
    ind = json.loads((ROOT / "research/community-frontier1094-audit/INDEPENDENT1094.json").read_text())
    audited = json.loads((HERE / "audited-pr3729/RESULT.json").read_text())
    full, actual = histogram(asm["complex_profile"]), histogram(ind["owner"]["idle"])
    N, W, m = ind["price"]["calls"], ind["price"]["live"], 73
    require((N, W) == (144, 14336), "selected aggregation unit changed")
    require(full == histogram(ind["owner"]["profile"]), "selected invoice mismatch")
    require(sum(r*n for r, n in full.items()) == 72*W + 64*N, "coverage identity mismatch")
    require(set(actual) <= set(full), "idle ranks missing from full invoice")
    residual = {r: n-actual.get(r, 0) for r, n in full.items()}
    require(all(n >= 0 and n % N == 0 for n in residual.values()), "local invoice not uniform")
    local = {r: n//N for r, n in residual.items() if n}
    require(local == histogram(audited["selected"]["local_profile_per_call"]), "audited local profile mismatch")
    require(actual == histogram(audited["selected"]["selected_idle_histogram"]), "audited selected idle mismatch")
    cap = C.max_idle_rank(m)
    require(cap == 51, "halving guard changed")
    idle_mass = sum(r*n for r, n in actual.items())
    validate(actual, idle_mass, cap)
    require(idle_mass == 237024 and idle_mass == 1646*N, "idle mass changed")
    w = Q(W, N)
    require(w == Q(896, 9), "family normalization changed")

    @lru_cache(None)
    def price(rank, a):
        return C.child_cost(rank, m, a)

    def moment(calls, idle, a, cost=price):
        whole = Counter({r: n*calls for r, n in local.items()})
        whole.update(idle)
        return tuple(sum(n*cost(r, a)[j] for r, n in whole.items())/(w*calls)
                     for j in (0, 1))

    def bracket(calls, idle):
        # Strict monotonicity: 0 < r/m < 1 and all counts are positive.
        lo, hi = 0, GRID//20
        require(moment(calls, idle, Q(lo, GRID))[1] < 1, "no positive saving")
        require(moment(calls, idle, Q(hi, GRID))[0] > 1, "search interval too short")
        while hi-lo > 1:
            mid = (lo+hi)//2
            bounds = moment(calls, idle, Q(mid, GRID))
            if bounds[1] < 1:
                lo = mid
            elif bounds[0] > 1:
                hi = mid
            else:
                raise ValueError("interval does not separate grid point")
        low, high = Q(lo, GRID), Q(hi, GRID)
        require(moment(calls, idle, low)[1] < 1 < moment(calls, idle, high)[0], "bracket sign failure")
        return {"a_lower": str(low), "a_upper": str(high),
                "decimal": [outward_decimal(low), outward_decimal(high, True)],
                "at_lower": enclosure(moment(calls, idle, low)),
                "at_upper": enclosure(moment(calls, idle, high))}

    endpoint = Q(audited["integer_ceiling"]["a_ceiling"])
    claimed_hist = histogram(audited["integer_ceiling"]["optimal_idle_histogram"])
    require(endpoint == Q("0.001688603446527"), "audited claim changed")
    require(claimed_hist == concentrated(1646, cap), "audited per-call optimum mismatch")
    per_call = {r: n*N for r, n in claimed_hist.items()}
    pooled = concentrated(idle_mass, cap)
    require(pooled == {51: 4647, 27: 1}, "pooled optimum changed")
    validate(per_call, idle_mass, cap)
    pooled_at_endpoint = moment(N, pooled, endpoint)
    per_call_at_endpoint = moment(N, per_call, endpoint)
    require(pooled_at_endpoint[1] < 1 < per_call_at_endpoint[0], "aggregation counterexample missing")
    require(pooled_at_endpoint[1] < Q("0.999995816"), "counterexample margin too small")
    nonintegral_actual_averages = {r: str(Q(n, N)) for r, n in actual.items() if n % N}
    require(len(nonintegral_actual_averages) == len(actual), "selected average fixture changed")

    # Integer children can belong to calls without giving every call mass 1646.
    # This is an arithmetic decomposition, not a physical hosting witness.
    allocation = [(39, {51: 33}), (1, {51: 32, 27: 1}), (104, {51: 32})]
    combined = Counter()
    for count, hist in allocation:
        combined.update({r: count*n for r, n in hist.items()})
    require(sum(count for count, _ in allocation) == N and dict(combined) == pooled,
            "integer per-call decomposition failure")

    pooled_bracket = bracket(N, pooled)
    restricted_bracket = bracket(1, claimed_hist)
    require(Q(restricted_bracket["a_upper"]) == endpoint, "published restricted bracket not reproduced")
    require(endpoint < Q(pooled_bracket["a_lower"]), "ceilings not strictly separated")

    # Independently certify the decisive signs and corrected bracket. This
    # engine shares neither log/exp code nor the subject PR's dynamic program.
    def independent_cost(rank, a):
        return binomial_price(rank, m, a)
    independent_rows = []
    for label, hist, a, want_below in [
        ("pooled_at_audited_endpoint", pooled, endpoint, True),
        ("restricted_at_audited_endpoint", per_call, endpoint, False),
        ("pooled_at_corrected_lower", pooled, Q(pooled_bracket["a_lower"]), True),
        ("pooled_at_corrected_upper", pooled, Q(pooled_bracket["a_upper"]), False),
    ]:
        bounds = moment(N, hist, a, independent_cost)
        reference = moment(N, hist, a)
        require(bounds[1] < 1 if want_below else bounds[0] > 1,
                "independent sign failure: " + label)
        require(bounds[0] <= reference[1] and reference[0] <= bounds[1],
                "price engines disagree: " + label)
        independent_rows.append({"check": label, "a": str(a), "moment": enclosure(bounds)})
    # At a=1/2 the answer is sqrt(r/m); squaring calibrates the new
    # engine against an exact rational identity without using either series.
    square_root_controls = [1, 14, 27, 51]
    for rank in square_root_controls:
        low, high = binomial_price(rank, m, Q(1, 2))
        require(0 < low <= high and low*low <= Q(rank, m) <= high*high,
                "independent square-root calibration failure")

    # Diagnostic only for a model permitting replication and unrestricted pooling.
    factor = cap//gcd(idle_mass, cap)
    require(factor == 17, "replication period changed")
    replicated = concentrated(idle_mass*factor, cap)
    require(replicated == {51: 79008}, "replicated histogram changed")
    a_control = Q("0.00169")
    fractional = C.relax(local, m, 896, 9, 64, a_control)
    replicated_value = moment(N*factor, replicated, a_control)
    require(replicated_value[0] <= fractional[1] and fractional[0] <= replicated_value[1],
            "replicated fractional identity not enclosed")
    require(Q(idle_mass*factor, cap)/factor == Q(idle_mass, cap), "fractional coefficient identity")

    # The two-unpaid law is hypothetical. Test only the asserted arithmetic
    # impossibility from a fractional average, not that law's realizability.
    two_average = C.model(local, m, 896, 9, 64, unpaid=2)["idle_mass"]
    two_total = two_average*N
    require(two_average == Q(13918, 9) and two_total.denominator == 1,
            "two-unpaid averaging fixture changed")
    two_hist = concentrated(int(two_total), cap)
    require(two_hist == {51: 4366, 22: 1}, "two-unpaid aggregate witness changed")

    rejected = []
    controls = [
        ("rank_above_guard", lambda: validate({52: 1}, 52, cap)),
        ("wrong_mass", lambda: validate({51: 4647, 27: 1}, idle_mass+1, cap)),
        ("fractional_child_count", lambda: validate({51: Q(idle_mass, 51)}, idle_mass, cap)),
        ("normalized_count_is_not_integer", lambda: validate({r: Q(n, N) for r, n in pooled.items()}, 1646, cap)),
        ("wrong_normalization", lambda: require(sum(n*price(r, endpoint)[0] for r, n in
            (Counter({r: n*N for r, n in local.items()}) + Counter(pooled)).items())/w < 1,
            "aggregate moment must be divided by total W")),
    ]
    for name, operation in controls:
        try:
            operation()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("failure control accepted: " + name)

    return {"status": "PASS_IDLE_INTEGRALITY_AGGREGATION_AUDIT",
            "scope": "source-bound aggregate-model counterexample; not physical packing or supplier admission",
            "audited_head": subject["head"], "calls": N, "live_families": W,
            "local_per_call": local, "idle_mass_total": idle_mass, "idle_mass_average": "1646",
            "actual_idle": actual, "nonintegral_actual_counts_per_call": nonintegral_actual_averages,
            "claimed_endpoint": str(endpoint), "pooled_histogram": pooled,
            "pooled_moment_at_claimed_endpoint": enclosure(pooled_at_endpoint),
            "restricted_moment_at_claimed_endpoint": enclosure(per_call_at_endpoint),
            "pooled_ceiling": pooled_bracket, "restricted_ceiling": restricted_bracket,
            "independent_binomial_checks": independent_rows,
            "binomial_square_root_calibration_ranks": square_root_controls,
            "integer_call_allocation": [{"calls": n, "idle": h, "mass": sum(r*k for r, k in h.items())}
                                        for n, h in allocation],
            "replication_diagnostic": {"factor": factor, "calls": N*factor, "idle": replicated,
                                       "fractional_coefficient_identity": True},
            "two_unpaid_arithmetic_only": {"average_idle_mass": str(two_average),
                                           "total_idle_mass": int(two_total), "integer_histogram": two_hist},
            "rejection_controls": rejected}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate this package's RESULT.json")
    args = parser.parse_args()
    result = run()
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        (HERE / "RESULT.json").write_text(serialized)
    else:
        require(json.loads((HERE / "RESULT.json").read_text()) == json.loads(serialized),
                "committed result mismatch; do not silently rewrite evidence")
    print(result["status"])
    print("pooled ceiling:", result["pooled_ceiling"]["decimal"])
    print("moment at audited endpoint:", result["pooled_moment_at_claimed_endpoint"]["outward_decimal"])
