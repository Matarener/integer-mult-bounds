#!/usr/bin/env python3
"""Bounded exact corroboration; no network, subprocesses, or file writes.

Substantial OpenAI Codex assistance. Apache-2.0.
All scientific checks remain active under python -O.
"""

import copy
import hashlib
import json
from fractions import Fraction
from math import comb, isqrt
from pathlib import Path
import platform
import time
import types

ROOT = Path(__file__).resolve().parent
OPTIMUM_PATH = ROOT / "optimum.py"
OPTIMUM_SOURCE = OPTIMUM_PATH.read_bytes()
opt = types.ModuleType("window_optimum")
opt.__file__ = str(OPTIMUM_PATH)
# Compile the same bytes bound by the receipt, never an adjacent cached .pyc.
exec(compile(OPTIMUM_SOURCE, str(OPTIMUM_PATH), "exec", dont_inherit=True), opt.__dict__)


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def eligible(a, z, c):
    return (a > 0 and z > 0 and c > 0 and z * z > 4 * a * c
            and 2 * a < z < 4 * a and a - z + c > 0
            and 4 * a - 2 * z + c > 0)


def update(record, row):
    a, z, c = row
    score = (z * z - 4 * a * c, z * z)
    if record is None or score[0] * record[0][1] < record[0][0] * score[1]:
        return (score, [list(row)])
    if score[0] * record[0][1] == record[0][0] * score[1]:
        return (record[0], record[1] + [list(row)])
    return record


def compare_certificate(cert, record, label):
    if record is None:
        check(cert["status"] == "infeasible", label + " feasibility")
        return
    check(cert["status"] == "optimal", label + " status")
    num, den = cert["score"]
    check(num * record[0][1] == record[0][0] * den, label + " score")
    check(cert["residuals"] == sorted(record[1]), label + " all minimizers")


def literal_simplex(cap):
    """Every positive triple a+z+c<=cap, no discriminant or trace pruning."""
    buckets = [[] for _ in range(cap + 1)]
    trials = 0
    for a in range(1, cap - 1):
        for z in range(1, cap - a):
            for c in range(1, cap - a - z + 1):
                trials += 1
                if eligible(a, z, c):
                    buckets[a + z + c].append([a, z, c])
    check(trials == comb(cap, 3), "literal domain cardinality")
    record = None
    eligible_count = 0
    predecessor_count = None
    small = []
    for L, rows in enumerate(buckets):
        for row in rows:
            eligible_count += 1
            record = update(record, row)
            if L <= 34:
                small.append(row)
        compare_certificate(opt.solve_normalized(L), record, "literal L=" + str(L))
        if L == 333:
            predecessor_count = eligible_count
    check(small == [[5, 15, 11]], "complete small-budget exception")
    check(predecessor_count == 8158, "PR6139 N=1000 residual count")
    return {"max_L": cap, "triples": trials, "eligible_residuals": eligible_count,
            "budgets_checked": cap + 1, "eligible_through_34": small,
            "eligible_at_L333": predecessor_count}


def divisor_census(cap):
    """All Delta=1 triples through cap using a divisibility census."""
    buckets = [[] for _ in range(cap + 1)]
    trials = 0
    for t in range(1, ((cap - 1) // 2 - 1) // 2 + 1):
        z = 2 * t + 1
        for a in range((t + 1) // 2 + 1, t):
            trials += 1
            c, rem = divmod(t * (t + 1), a)
            if not rem and a + z + c <= cap:
                check(eligible(a, z, c), "divisor root condition")
                buckets[a + z + c].append([a, z, c])
    record = None
    residual_count = 0
    multi = 0
    for L, rows in enumerate(buckets):
        for row in rows:
            residual_count += 1
            record = update(record, row)
        if L >= 35:
            cert = opt.solve_normalized(L)
            compare_certificate(cert, record, "divisor L=" + str(L))
            check(opt.verify_certificate(cert), "certificate rejected")
            multi += len(cert["residuals"]) > 1
    return {"max_L": cap, "divisor_trials": trials, "residuals": residual_count,
            "budgets_checked": cap - 34, "budgets_with_multiple_optimizers": multi}


def largest_c_oracle(L):
    """All discriminants, selecting the best c for each fixed a,z."""
    record = None
    pairs = eligible_pairs = 0
    for z in range(1, (L - 1) // 2 + 1):
        for a in range(z // 4 + 1, (z - 1) // 2 + 1):
            pairs += 1
            c = min(L - a - z, (z * z - 1) // (4 * a))
            if c > max(0, z - a, 2 * z - 4 * a):
                eligible_pairs += 1
                check(eligible(a, z, c), "largest-c root predicate")
                record = update(record, [a, z, c])
    cert = opt.solve_normalized(L)
    compare_certificate(cert, record, "largest-c L=" + str(L))
    return {"L": L, "pairs": pairs, "eligible_pairs": eligible_pairs,
            "certificate": cert}


def multiply(P, Q):
    result = [0] * (len(P) + len(Q) - 1)
    for i, p in enumerate(P):
        for j, q in enumerate(Q):
            result[i + j] += p * q
    return result


def evaluate(P, x):
    result = 0
    for p in reversed(P):
        result = result * x + p
    return result


def derivative(P):
    return [i * P[i] for i in range(1, len(P))]


def profiles_and_padding():
    count = padding_count = 0
    for L in (31, 34, 35, 37, 40, 62, 63, 144, 333, 1000):
        cert = opt.solve_normalized(L)
        for a, z, c in cert["residuals"]:
            delta = z * z - 4 * a * c
            for h in range(1, 7):
                Q = [c, -z, a]
                for _ in range(h):
                    Q = multiply(Q, [2, -3, 1])
                Q = [(-1) ** (h + 1) * q for q in Q]
                A = [max(-q, 0) for q in Q]
                B = [max(q, 0) for q in Q]
                S = 6 ** h // 2
                W = S * (a + z + c)
                check(len(Q) == 2 * h + 3, "support size")
                check(sum(A) == sum(B) == W, "per-side count")
                check(sum(q * (2 ** j) for j, q in enumerate(Q)) == 0, "rank mass")
                derivative_Q = Q
                for _ in range(h):
                    check(evaluate(derivative_Q, 1) == evaluate(derivative_Q, 2) == 0,
                          "endpoint multiplicity")
                    derivative_Q = derivative(derivative_Q)
                check(evaluate(derivative_Q, 1) != 0 and evaluate(derivative_Q, 2) != 0,
                      "multiplicity is exact")
                midpoint = Fraction(z, 2 * a)
                check(1 < midpoint < 2 and evaluate(Q, midpoint) > 0, "window sign")
                if delta == 1:
                    r, s = Fraction(z - 1, 2 * a), Fraction(z + 1, 2 * a)
                    check(1 < r < s < 2, "strict rational roots")
                    check(evaluate(Q, r) == evaluate(Q, s) == 0, "interior roots")
                    check(evaluate(Q, (1 + r) / 2) < 0 and evaluate(Q, (s + 2) / 2) < 0,
                          "outside window signs")
                count += 1
                for rho in (0, S - 1):
                    N = S * L + rho
                    allowance = N - W
                    check(allowance >= 0, "budget")
                    padded_A, padded_B = A[:], B[:]
                    padded_A[0] += allowance
                    padded_B[0] += allowance
                    check(sum(padded_A) == sum(padded_B) == N, "full common padding")
                    check([b - a0 for a0, b in zip(padded_A, padded_B)] == Q,
                          "padding leaves polynomial unchanged")
                    check(sum(padded_A) + 1 > N, "overbudget padding rejected")
                    actual = opt.solve_budget(h, N)
                    check(actual["normalized_certificate"] == cert, "h and remainder scaling")
                    padding_count += 1
    return {"signed_profiles": count, "padding_and_scaling_cases": padding_count}


def rejection_controls():
    controls = []

    def rejected(label, call):
        try:
            call()
        except (ValueError, ArithmeticError):
            controls.append(label)
        else:
            raise RuntimeError("control was accepted: " + label)

    for x in (-1, True, 3.5, "35", opt.MAX_L + 1):
        rejected("invalid L " + repr(x), lambda x=x: opt.solve_normalized(x))
    for h, N in ((0, 100), (17, 100), (True, 100), (1, 0), (1, True), (1, 300003)):
        rejected("invalid h,N " + repr((h, N)), lambda h=h, N=N: opt.solve_budget(h, N))
    for label, source_L, edit in (
        ("missing tied optimizer", 144, lambda c: c["residuals"].pop()),
        ("wrong discriminant", 333, lambda c: c.update(discriminant=4)),
        ("missing excluded trace", 333, lambda c: c["excluded_odd_traces"].pop()),
        ("wrong coefficient", 333, lambda c: c["residuals"][0].__setitem__(0, 61)),
        ("wrong exact score", 333, lambda c: c.update(score=[1, 25920])),
        ("boolean masquerading as discriminant", 333, lambda c: c.update(discriminant=True)),
        ("extra unverified metadata", 333, lambda c: c.update(unchecked=True)),
        ("false small-budget feasibility", 30, lambda c: c.update(status="optimal")),
        ("false rational small-budget claim", 31, lambda c: c.update(discriminant=1)),
        ("looser budget with better optimizer", 35, lambda c: c.update(normalized_budget=40)),
    ):
        cert = copy.deepcopy(opt.solve_normalized(source_L))
        edit(cert)
        rejected(label, lambda cert=cert: opt.verify_certificate(cert))
    # Valid algebraic discriminant-one triples at the excluded boundary roots.
    for row in ([2, 7, 6], [3, 11, 10]):
        check(row[1] ** 2 - 4 * row[0] * row[2] == 1, "boundary fixture Delta")
        check(not eligible(*row), "root at x=2 must be excluded")
    # The seed family alone does not solve the intermediate budgets.
    check(opt.solve_normalized(40)["z_star"] == 19 > 17, "seed-only false conclusion")
    return {"rejected_inputs_and_certificates": len(controls), "labels": controls,
            "boundary_fixtures": 2, "seed_only_counterexample": 40}


def dominance_fixtures():
    count = 0
    for n in list(range(3, 1001)) + [10 ** 10, 10 ** 50, 10 ** 100]:
        for L in (4 * n * n - 1, 4 * (n + 1) ** 2 - 2):
            z0 = 2 * n * n - 1
            Z = (L - 1) // 2
            check(isqrt((L + 1) // 4) == n, "integer seed selection")
            check(2 * z0 > Z and 4 * z0 * z0 > Z * Z, "strict domination")
            check(2 * n * n - 4 * n - 2 > 0, "uniform polynomial sign")
            count += 1
    return {"endpoint_and_large_integer_fixtures": count,
            "uniformity_depends_on_written_proof": True}


def main():
    started = time.perf_counter()
    report = {"claim_type": "proposed proof with exact finite corroboration",
              "python": platform.python_version(),
              "literal_simplex": literal_simplex(400),
              "divisor_census": divisor_census(4096),
              "all_discriminant_oracles": [largest_c_oracle(L) for L in
                                           (31, 34, 35, 40, 144, 333, 401, 512,
                                            777, 1000, 2048, 4096, 8192)],
              "profiles": profiles_and_padding(),
              "controls": rejection_controls(),
              "dominance": dominance_fixtures()}
    report["large_reference_cases"] = []
    for L in (9999, 10000, 99999, 100000):
        cert = opt.solve_normalized(L)
        check(opt.verify_certificate(cert), "large certificate")
        report["large_reference_cases"].append(cert)
    report["source_sha256"] = {p.name: hashlib.sha256(
                                   OPTIMUM_SOURCE if p == OPTIMUM_PATH else p.read_bytes()
                               ).hexdigest()
                               for p in sorted(ROOT.iterdir())
                               if p.suffix in (".py", ".md", ".json")}
    report["elapsed_seconds"] = round(time.perf_counter() - started, 6)
    report["marker"] = "PASS_EXACT_HIDDEN_WINDOW_OPTIMA"
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
