#!/usr/bin/env python3
"""Independent bounded corroboration; exact arithmetic, standard library only.

Separate AI reviewer, 2026-10-29; Apache-2.0. No human/formal certification.
Reads the requested package's optimum.py as bytes, executes those exact source
bytes, and prints JSON. Does not write files, use networks, or spawn processes.

Two independently organized domains:
1. Every integer signed quartic with Q(1)=Q(2)=0, positive leading coefficient,
   and positive/negative coefficient mass at most --signed-budget. Feasibility
   uses a generic rational Sturm sequence, not the author's root inequalities.
2. All ordered Farey-neighbor roots m/n < p/q in (1,2) with np-mq=1 and
   (m+n)(p+q)<=--farey-cap. Width comparisons use the exact root ratio pn/qm,
   not the author's discriminant statistic, square tests, or divisor routine.
   This second domain covers Delta=1 only; the reviewed dominance proof remains
   necessary to exclude other discriminants outside the first finite domain.
"""

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path
import platform
import types


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def trim(poly):
    poly = list(poly)
    while poly and poly[-1] == 0:
        poly.pop()
    return poly


def divide(num, den):
    num, den = trim(num), trim(den)
    require(bool(den), "zero polynomial divisor")
    quotient = [Fraction(0)] * max(0, len(num) - len(den) + 1)
    while len(num) >= len(den):
        shift = len(num) - len(den)
        factor = Fraction(num[-1], den[-1])
        quotient[shift] = factor
        for j, coefficient in enumerate(den):
            num[shift + j] -= factor * coefficient
        num = trim(num)
    return trim(quotient), num


def evaluate(poly, x):
    value = 0
    for coefficient in reversed(poly):
        value = value * x + coefficient
    return value


def sturm_count(poly, left, right):
    require(evaluate(poly, left) != 0 and evaluate(poly, right) != 0,
            "Sturm fixture must avoid endpoint roots")
    chain = [trim(poly), trim([i * c for i, c in enumerate(poly)][1:])]
    while chain[-1]:
        _, remainder = divide(chain[-2], chain[-1])
        if not remainder:
            break
        chain.append([-c for c in remainder])

    def variations(x):
        signs = [(v > 0) - (v < 0) for p in chain if (v := evaluate(p, x))]
        return sum(a != b for a, b in zip(signs, signs[1:]))

    return variations(left) - variations(right)


def signed_quartic_census(opt, cap):
    """Full signed-coefficient domain, before any alternating-sign assumption."""
    buckets = [[] for _ in range(cap + 1)]
    trials = bounded = endpoint_rejected = root_count_rejected = eligible = 0
    for q4 in range(1, cap + 1):
        for q3 in range(-cap, cap + 1):
            for q2 in range(-cap, cap + 1):
                trials += 1
                # Solve the two linear equalities Q(1)=Q(2)=0 exactly.
                q1 = -3 * q2 - 7 * q3 - 15 * q4
                q0 = 2 * q2 + 6 * q3 + 14 * q4
                if abs(q1) > cap or abs(q0) > cap:
                    continue
                Q = [q0, q1, q2, q3, q4]
                mass = sum(max(c, 0) for c in Q)
                if mass > cap:
                    continue
                bounded += 1
                require(sum(Q) == 0 and evaluate(Q, 2) == 0, "linear constraints")
                require(sum(max(-c, 0) for c in Q) == mass, "signed masses")
                # Generic exact polynomial division checks the endpoint factors.
                residual, rem1 = divide(Q, [-1, 1])
                residual, rem2 = divide(residual, [-2, 1])
                require(not rem1 and not rem2 and len(residual) == 3, "deflation")
                if evaluate(residual, 1) == 0 or evaluate(residual, 2) == 0:
                    endpoint_rejected += 1
                    continue
                if sturm_count(residual, 1, 2) != 2:
                    root_count_rejected += 1
                    continue
                require(all(c.denominator == 1 for c in residual), "integer quotient")
                c, b, a = map(int, residual)
                z = -b
                require(a > 0 and z > 0 and c > 0, "positive-root coefficient signs")
                require(Q[0] > 0 > Q[1] and Q[2] > 0 > Q[3] and Q[4] > 0,
                        "alternating full polynomial")
                require(mass == 3 * (a + z + c), "normalization from full coefficients")
                require(evaluate(Q, Fraction(z, 2 * a)) > 0, "oriented positive window")
                eligible += 1
                score = Fraction(z * z - 4 * a * c, z * z)
                buckets[mass].append((score, [a, z, c]))
    require(trials == cap * (2 * cap + 1) ** 2, "signed domain count")
    best, winners = None, []
    changes = []
    for N, rows in enumerate(buckets):
        for score, row in rows:
            if best is None or score < best:
                best, winners = score, [row]
            elif score == best:
                winners.append(row)
        cert = opt.solve_normalized(N // 3)
        if best is None:
            require(cert["status"] == "infeasible", "signed feasibility at N=" + str(N))
        else:
            require(cert["status"] == "optimal", "signed status at N=" + str(N))
            require(Fraction(*cert["score"]) == best, "signed score at N=" + str(N))
            require(cert["residuals"] == sorted(winners), "signed all ties at N=" + str(N))
        if rows:
            changes.append({"per_profile_N": N, "new_eligible": len(rows),
                            "optimum_residuals": sorted(winners)})
    return {"per_profile_N_cap": cap, "normalized_L_cap": cap // 3,
            "signed_coefficient_trials": trials, "bounded_endpoint_polynomials": bounded,
            "endpoint_root_rejections": endpoint_rejected,
            "Sturm_root_count_rejections": root_count_rejected,
            "eligible_polynomials": eligible, "budget_prefixes": cap + 1,
            "eligible_mass_events": changes}


def farey_census(opt, cap):
    buckets = [[] for _ in range(cap + 1)]
    root_pairs, numerator_trials, congruence_trials = set(), 0, 0
    # q>=2 and p>=3 imply p+q>=5, hence 2n+1 <= floor(cap/5).
    for n in range(2, (cap // 5 - 1) // 2 + 1):
        for m in range(n + 1, 2 * n):
            numerator_trials += 1
            if gcd(m, n) != 1:
                continue
            # np-mq=1, so q == -inverse(m) modulo n.
            q0 = (-pow(m, -1, n)) % n
            if q0 < 2:
                q0 += n
            max_q = (cap // (m + n) - 1) // 2
            for q in range(q0, max_q + 1, n):
                congruence_trials += 1
                p, rem = divmod(m * q + 1, n)
                require(rem == 0, "Farey congruence")
                if not q < p < 2 * q:
                    continue
                cost = (m + n) * (p + q)
                if cost > cap:
                    continue
                require(n * p - m * q == 1, "strict adjacent roots")
                row = [n * q, m * q + n * p, m * p]
                require(sum(row) == cost, "root-product budget")
                require(tuple(row) not in root_pairs, "duplicate Farey parametrization")
                root_pairs.add(tuple(row))
                buckets[cost].append((Fraction(p * n, q * m), row))
    best, winners, multi, checked = None, [], 0, 0
    tie_examples = []
    for L, rows in enumerate(buckets):
        for ratio, row in rows:
            if best is None or ratio < best:
                best, winners = ratio, [row]
            elif ratio == best:
                winners.append(row)
        if L < 35:
            require(best is None, "unexpected Delta=1 small case")
            continue
        cert = opt.solve_normalized(L)
        require(cert["residuals"] == sorted(winners), "Farey all optimizers at L=" + str(L))
        require(best == Fraction(cert["z_star"] + 1, cert["z_star"] - 1),
                "independent root ratio at L=" + str(L))
        require(opt.verify_certificate(cert), "valid certificate")
        checked += 1
        if len(winners) > 1:
            multi += 1
            if len(tie_examples) < 5:
                tie_examples.append({"L": L, "residuals": sorted(winners)})
    return {"normalized_L_cap": cap, "numerator_trials": numerator_trials,
            "congruence_trials": congruence_trials, "unique_Delta1_residuals": len(root_pairs),
            "budget_prefixes_checked": checked, "budgets_with_ties": multi,
            "first_tie_budgets": tie_examples}


def certificate_mutations(opt):
    tested = 0
    exception_counts = {}

    def rejects(cert, label):
        nonlocal tested
        try:
            opt.verify_certificate(cert)
        except (ValueError, TypeError, OverflowError) as exc:
            tested += 1
            name = type(exc).__name__
            exception_counts[name] = exception_counts.get(name, 0) + 1
        else:
            raise RuntimeError("malformed certificate accepted: " + label)

    for value in (None, [], True, 1, "{}"):
        rejects(value, "top-level type")

    def leaves(value, path=()):
        if isinstance(value, dict):
            for key, item in value.items():
                yield from leaves(item, path + (key,))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                yield from leaves(item, path + (i,))
        else:
            yield path, value

    for L in (0, 30, 31, 34, 35, 40, 144, 333, 4096, 100000):
        valid = opt.solve_normalized(L)
        require(opt.verify_certificate(valid), "unmutated control")
        for key in valid:
            cert = copy.deepcopy(valid)
            del cert[key]
            rejects(cert, "missing " + key)
        cert = copy.deepcopy(valid)
        cert["unverified"] = "extra"
        rejects(cert, "extra field")
        for path, leaf in leaves(valid):
            if path == ("normalized_budget",):
                choices = [str(L), float(L), True, -1, 100001]
            elif type(leaf) is int:
                choices = [leaf + 1, float(leaf), True, str(leaf), None]
            elif type(leaf) is str:
                choices = [leaf + "!", None, 0]
            elif leaf is None:
                choices = [0, False, "null"]
            else:
                raise RuntimeError("unexpected valid leaf type")
            for replacement in choices:
                cert = copy.deepcopy(valid)
                target = cert
                for component in path[:-1]:
                    target = target[component]
                target[path[-1]] = replacement
                rejects(cert, repr(path))
        for key in ("residuals", "excluded_odd_traces"):
            items = valid.get(key)
            if not items:
                continue
            for variant in (items[:-1], items + items[:1]):
                cert = copy.deepcopy(valid)
                cert[key] = variant
                rejects(cert, key + " omitted/duplicate")
            if len(items) > 1:
                cert = copy.deepcopy(valid)
                cert[key] = list(reversed(items))
                rejects(cert, key + " reversed canonical order")
    return {"malformed_cases_rejected": tested, "exception_counts": exception_counts,
            "valid_controls": 10}


def boundary_checks():
    fixtures = [([3, -5, 2], "root at 1"), ([6, -7, 2], "root at 2"),
                ([2, -3, 1], "both endpoints"), ([9, -12, 4], "double interior root"),
                ([11, -15, 5], "irrational interior pair"),
                ([12, -17, 6], "rational interior pair")]
    results = []
    for poly, name in fixtures:
        boundary = evaluate(poly, 1) == 0 or evaluate(poly, 2) == 0
        count = None if boundary else sturm_count(poly, 1, 2)
        accepted = not boundary and count == 2
        require(accepted == ("interior pair" in name), "boundary fixture " + name)
        results.append({"fixture": name, "accepted": accepted, "interior_root_count": count})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--signed-budget", default=150, type=int)
    parser.add_argument("--farey-cap", default=4096, type=int)
    args = parser.parse_args()
    require(1 <= args.signed_budget <= 600, "bounded signed-budget range 1..600")
    require(35 <= args.farey_cap <= 10000, "bounded farey-cap range 35..10000")
    source_path = args.package / "optimum.py"
    source = source_path.read_bytes()
    opt = types.ModuleType("independent_review_subject")
    opt.__file__ = str(source_path)
    exec(compile(source, str(source_path), "exec", dont_inherit=True), opt.__dict__)
    report = {
        "claim_type": "independent AI review with bounded exact corroboration",
        "python": platform.python_version(),
        "boundary_fixtures": boundary_checks(),
        "signed_quartics": signed_quartic_census(opt, args.signed_budget),
        "Farey_root_pair_census": farey_census(opt, args.farey_cap),
        "certificate_mutations": certificate_mutations(opt),
        "source_sha256": {name: hashlib.sha256((args.package / name).read_bytes()).hexdigest()
                          for name in ("PROOF.md", "README.md", "SOURCES.json", "optimum.py", "verify.py")},
        "executed_optimum_sha256": hashlib.sha256(source).hexdigest(),
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "marker": "PASS_INDEPENDENT_EXACT_REVIEW",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
