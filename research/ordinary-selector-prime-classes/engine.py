"""Exact scalar selector certificates; no producer or Count implementation imports.

The archived bit2234-stock-threshold argument already treats the older profile
and its uniform 311311 sufficient bound.  This separate arithmetic addresses
the retuned 1/577 width and all seven prime-dependent scalar cutoffs only.
Prepared by ToikY with substantial OpenAI Codex assistance, Apache-2.0.
"""

import hashlib
import json


R = 269241600
DIMENSION = 64
CHILD = 42
DENOMINATOR = 577
LIMIT = 1 << 20
Q_FLOOR = 1 << 80


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def depth(e):
    require(type(e) is int and e >= 1, "positive scalar width")
    result = 0
    while e >= DIMENSION:
        e = CHILD * (e // DIMENSION)
        result += 1
    return result


def atom_width(e):
    require(type(e) is int and e >= 1, "positive root input")
    low, high = 1, e
    while low < high:
        middle = (low + high) // 2
        if middle ** DENOMINATOR >= e:
            high = middle
        else:
            low = middle + 1
    require((low == 1 or (low - 1) ** DENOMINATOR < e)
            and e <= low ** DENOMINATOR, "exact least reciprocal root")
    return low


def ceil_log(q, value):
    require(type(q) is int and q > 1 and type(value) is int and value >= 1,
            "integer logarithm domain")
    power, exponent = 1, 0
    while power < value:
        power *= q
        exponent += 1
    return exponent


def correction_certificate(q, d):
    """Bound R^d P(q)^d without constructing GL64 or the stock integer.

    P=prod(1-q^-i), i=1..64, obeys 1-1/(q-1)<P<1.
    For positive d, Bernoulli gives
      R^d (q-1-d)/(q-1) < R^d P^d < R^d.
    These strict integer cross-products certify its exact ceiling logarithm.
    An inconclusive sandwich is an error, never an inferred correction.
    """
    require(type(q) is int and q > Q_FLOOR and type(d) is int and 0 <= d <= 23,
            "finite correction certificate domain")
    if d == 0:
        return {"depth": 0, "correction": 0, "R_power": 1,
                "exact_reason": "stock is one at depth zero"}
    a = R ** d
    c = ceil_log(q, a)
    require(c >= 1 and q - 1 > d, "positive correction and lower bound")
    lower_left = a * (q - 1 - d)
    lower_right = q ** (c - 1) * (q - 1)
    upper_right = q ** c
    require(lower_left > lower_right,
            "INCONCLUSIVE lower sandwich: no exact correction admitted")
    require(a <= upper_right, "upper sandwich")
    return {"depth": d, "correction": c, "R_power": a,
            "lower_cross_left": lower_left, "lower_cross_right": lower_right,
            "lower_strict": True, "upper_left": a,
            "upper_right": upper_right, "upper_weak": True,
            "k_formula": "4096*w*depth+correction"}


def selector(q, e, certificates=None, *, strict=True, omit_row_factor=False,
             depth_from_reduced_width=False):
    require(type(e) is int and 1 <= e <= LIMIT, "bounded selector domain")
    w = atom_width(e)
    d = depth(max(1, e // w) if depth_from_reduced_width else e)
    if omit_row_factor:
        # q^-1 < P(q)^d < 1 for 1<=d<=23; hence ceil_log(P^d)=0.
        require(d == 0 or q * (q - 1 - d) > q - 1,
                "omitted-R correction remains exactly zero")
        c = 0
    else:
        cert = (certificates or {}).get(d)
        if cert is None:
            cert = correction_certificate(q, d)
        c = cert["correction"]
    k = 4096 * w * d + c
    first = 2 * k < e if strict else 2 * k <= e
    body = (e - k) // w if first else 0
    remainder = (e - k) % w if first else 0
    return {"e": e, "w": w, "depth": d, "correction": c, "k": k,
            "first_guard": first, "body": body, "remainder": remainder,
            "fits": first and body >= DIMENSION}


def proth_certificate(h, n, a):
    require(type(h) is int and type(n) is int and type(a) is int
            and n >= 1 and 0 < h < 2 ** n and h % 2 == 1,
            "Proth shape")
    q = h * 2 ** n + 1
    residue = pow(a, (q - 1) // 2, q)
    require(residue == q - 1, "Proth half-power must equal minus one")
    require(q > Q_FLOOR and q < (2 ** n + 1) ** 2,
            "prime-divisor size contradiction")
    return {"q": q, "h": h, "n": n, "a": a,
            "half_power_residue": residue,
            "proth_h_less_than_2n": True,
            "prime_divisor_lower_bound": 2 ** n + 1,
            "q_less_than_prime_divisor_bound_squared": True,
            "primality_method": "elementary Proth half-power/order certificate"}


def find_prime(n, fixed_h=None):
    """Deterministic bounded search; preserve every rejected candidate and test."""
    trace = []
    small_primes = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43)
    candidates = [fixed_h] if fixed_h is not None else range(1, 4096, 2)
    for h in candidates:
        q = h * 2 ** n + 1
        divisor = next((p for p in small_primes if q % p == 0), None)
        if divisor is not None:
            trace.append({"h": h, "rejection": "small divisor", "divisor": divisor})
            continue
        tests = []
        for a in range(2, 34):
            residue = pow(a, (q - 1) // 2, q)
            tests.append({"a": a, "residue": residue})
            if residue == q - 1:
                cert = proth_certificate(h, n, a)
                cert["search"] = {"max_h_exclusive": 4096,
                                  "bases_inclusive": [2, 33],
                                  "fixed_h": fixed_h,
                                  "rejected_candidates": trace,
                                  "successful_candidate_tests": tests}
                return cert
        trace.append({"h": h, "rejection": "no bounded half-power witness", "tests": tests})
    raise ValueError("bounded Proth search exhausted: " + str(n))


def cohort_partition():
    # b[d] is the first positive e with depth(e)>=d.  The recurrence inverts
    # 42*floor(e/64)>=b[d] exactly, rather than assuming real-valued depth.
    b = [1, 64]
    while b[-1] <= LIMIT:
        b.append(DIMENSION * ((b[-1] + CHILD - 1) // CHILD))
    rows = []
    for d in range(len(b) - 1):
        lo, hi = b[d], min(LIMIT, b[d + 1] - 1)
        if lo > hi:
            continue
        require(depth(lo) == depth(hi) == d, "cohort endpoint depths")
        require(lo == 1 or depth(lo - 1) == d - 1, "cohort left seam")
        require(depth(b[d + 1]) == d + 1, "cohort right seam")
        correction_upper = (29 * d + 79) // 80
        if d == 0:
            classification = "reject: body is below 64"
            margin = None
        elif d <= 18:
            classification = "reject: strict first guard fails uniformly"
            margin = 16384 * d + 2 - hi
            require(margin >= 0, "uniform precritical rejection margin")
        elif d == 19:
            classification = "fits iff e>=311297+2*m(q)"
            margin = None
        else:
            classification = "fits uniformly"
            upper_k = 8192 * d + correction_upper
            margin = lo - (2 * upper_k + 1)
            require(margin >= 0 and (lo - upper_k) // 2 >= DIMENSION,
                    "uniform postcritical admission")
        rows.append({"depth": d, "first_e": lo, "last_e": hi,
                     "width": "one at e=1; two otherwise" if d == 0 else 2,
                     "correction_lower": 0 if d == 0 else 1,
                     "correction_upper": correction_upper,
                     "classification": classification, "integer_margin": margin})
    require(rows[0]["first_e"] == 1 and rows[-1]["last_e"] == LIMIT
            and all(a["last_e"] + 1 == c["first_e"] for a, c in zip(rows, rows[1:])),
            "disjoint complete bounded cohort cover")
    return b, rows


def run():
    require(R < 2 ** 29 and R ** 19 < Q_FLOOR ** 7,
            "uniform correction upper class seven")
    # At the least allowed integer q, this lower expression already exceeds
    # one, and (q-20)/(q-1) increases with q.
    require(R ** 19 * (Q_FLOOR - 19) > Q_FLOOR,
            "uniform class lower bound one")
    require(LIMIT < 2 ** DENOMINATOR and atom_width(1) == 1
            and atom_width(2) == atom_width(LIMIT) == 2,
            "complete finite width cohort")
    boundaries, cohorts = cohort_partition()
    witnesses = []
    for n, fixed_h in [(540, None), (270, None), (180, None), (135, None),
                       (110, None), (90, None), (80, 213)]:
        prime = find_prime(n, fixed_h)
        q = prime["q"]
        certs = {d: correction_certificate(q, d) for d in range(24)}
        m = certs[19]["correction"]
        cutoff = 311297 + 2 * m
        seams = [selector(q, e, certs) for e in [cutoff - 2, cutoff - 1, cutoff,
                                                cutoff + 1, 311311, LIMIT]]
        require(all(row["fits"] == (row["e"] >= cutoff) for row in seams),
                "exact class threshold seams")
        endpoint_checks = []
        for cohort in cohorts:
            for e in sorted({cohort["first_e"], cohort["last_e"]}):
                actual = selector(q, e, certs)
                require(actual["fits"] == (e >= cutoff), "complete cohort endpoint classification")
                endpoint_checks.append(actual)
        wrong_strict = selector(q, cutoff - 1, certs, strict=False)
        wrong_r = selector(q, 311297, certs, omit_row_factor=True)
        wrong_depth = selector(q, cutoff - 1, certs, depth_from_reduced_width=True)
        require(wrong_strict["fits"] and not seams[1]["fits"], "strictness control discriminates")
        require(wrong_r["fits"] and not selector(q, 311297, certs)["fits"],
                "omitted row-factor control discriminates")
        require(wrong_depth["fits"] and wrong_depth["depth"] != 19,
                "original-width depth control discriminates")
        prime.update({"m": m, "cutoff": cutoff,
                      "correction_certificates": [certs[d] for d in range(24)],
                      "threshold_seams": seams, "cohort_endpoint_checks": endpoint_checks,
                      "semantic_controls": {
                          "nonstrict_first_guard_wrongly_admits": wrong_strict,
                          "omitted_row_factor_wrongly_admits": wrong_r,
                          "depth_on_reduced_width_wrongly_admits": wrong_depth}})
        witnesses.append(prime)
    require([row["m"] for row in witnesses] == list(range(1, 8)),
            "every prime class witnessed in order")
    # Recompute the exact half-power evidence for all seven primes.
    require(all(pow(row["a"], (row["q"] - 1) // 2, row["q"]) == row["q"] - 1
                for row in witnesses), "all exact prime certificates")
    return {"status": "PASS_SCALAR_SELECTOR_PRIME_CLASSES",
            "profile": {"numerator": 1, "denominator": DENOMINATOR,
                        "dimension": DIMENSION, "child_rank": CHILD, "row_factor": R},
            "finite_domain": {"first_e": 1, "last_e": LIMIT,
                              "q_domain": "prime q>2^80"},
            "depth_first_widths": boundaries,
            "cohorts": cohorts, "prime_witnesses": witnesses,
            "prime_class_cutoffs": [row["cutoff"] for row in witnesses],
            "prime_classes": list(range(1, 8)),
            "finite_classification": "fits iff e>=311297+2*m(q), 1<=e<=2^20",
            "symbolic_correction": "m(q)=ceil_log_q(R^19*prod(i=1..64,1-q^-i)^19)",
            "proof_boundary": "All-e extension requires the separately written dyadic proof, not this bounded cohort certificate.",
            "arithmetic": "exact integers; no floating point, GL64 integer, stock integer or producer imports",
            "semantic_controls_rejected": 21,
            "witness_payload_sha256": hashlib.sha256(canonical(witnesses)).hexdigest(),
            "predecessor_credit": "bit2234-stock-threshold already gives the older-profile uniform311311 sufficient bound; not a new result here",
            "scope": "Scalar setup/selector only. No Count primitives, native payload, SOURCE, full supplier, physical/outer theorem, tau/kappa, human or kernel acceptance."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
