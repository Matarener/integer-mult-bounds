#!/usr/bin/env python3
"""Exact finite certificates for the dyadic cubic-reader repair alphabet.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas's PR6200 supplies the fixed-reader contract and rational theorem;
Sricharan Vagvala, Adam Gall and Hanson Sun retain the preceding lineage.
No predecessor executable is imported. The all-arity localization and
minimality statements are written proofs, not extrapolations from this scan.
"""

import hashlib
import json
from fractions import Fraction
from math import gcd, isqrt
from pathlib import Path


SOURCE_HEAD = "8b705d15869ba12d55adcb9075c68a2c7d44602d"
SOURCE_BASE = "research/cubic-reader-rational-repair/"
ENTRY = ((1, 0, 0, 0, 0), (1, 0), (0, 1))
# Output coordinates are y_entry, a_entry^3, a_entry^2*b_entry,
# a_entry*b_entry^2, b_entry^3. Source coordinates are a_entry,b_entry.


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_sources(package):
    manifest = json.loads((package / "SOURCE-PINS.json").read_text())
    need(manifest["schema_version"] == 1, "source schema")
    predecessor = manifest["predecessor"]
    need(predecessor == {
        "pr": "https://github.com/CrocSwap/integer-mult-bounds/pull/6200",
        "head": SOURCE_HEAD, "author": "Nick Petalas", "license": "Apache-2.0",
    }, "exact predecessor identity")
    documents = manifest["documents"]
    expected = {"sources/pr6200-PROOF.md", "sources/pr6200-README.md"}
    need(len(documents) == 2 and {item["path"] for item in documents} == expected,
         "both exact predecessor documents")
    hashes = {}
    for item in documents:
        filename = item["path"].removeprefix("sources/pr6200-")
        source_path = SOURCE_BASE + filename
        need(item["source_path"] == source_path, "predecessor source path")
        need(item["source_url"] == "https://raw.githubusercontent.com/"
             f"CrocSwap/integer-mult-bounds/{SOURCE_HEAD}/{source_path}",
             "predecessor exact-head URL")
        path = (package / item["path"]).resolve()
        need(path.is_relative_to(package), "source path inside package")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        need(digest == item["sha256"], "source digest: " + item["path"])
        hashes[item["path"]] = digest
    return hashes


def add(left, right):
    return tuple(a + b for a, b in zip(left, right, strict=True))


def weighted_cube(weight, form):
    a, b = form
    return (0, weight * a**3, 3 * weight * a*a*b,
            3 * weight * a*b*b, weight * b**3)


def moments(r):
    need(isinstance(r, int) and r >= 2, "integer arity at least two")
    first = r * (r - 1) // 2
    second = r * (r - 1) * (2*r - 1) // 6
    return first, second


def defect(r):
    first, second = moments(r)
    return (0, 0, 3*first, 3*second, first*first)


def endpoint(r):
    return ((1, r, 0, 0, 0), ENTRY[1], ENTRY[2])


def original_children(r):
    # Event fields are opcode, coefficient, source, provenance label.
    return [event for i in range(r) for event in (
        ("cube", 1, "a", f"child-{i}-read"),
        ("shift", 1, "b", f"child-{i}-shift"))]


def eager_program(r):
    return [event for i in range(r) for event in (
        ("cube", 1, "a", f"child-{i}-read"),
        ("shift", 1, "b", f"child-{i}-shift"),
        ("shift", -1, "b", f"eager-{i}-restore"))]


def run(events, state=ENTRY):
    output, a, b = state
    for opcode, coefficient, source, _ in events:
        need(isinstance(coefficient, (int, Fraction)), "exact scalar coefficient")
        need(coefficient != 0, "zero events must be omitted")
        if opcode == "shift":
            need(source == "b", "source shift reads b only")
            a = add(a, tuple(coefficient * value for value in b))
        elif opcode == "cube":
            need(source in ("a", "b"), "cube reads an actual source stream")
            output = add(output, weighted_cube(coefficient, a if source == "a" else b))
        else:
            raise ValueError("event outside declared alphabet")
    return output, a, b


def inverse(events):
    return [(op, -coefficient, source, label)
            for op, coefficient, source, label in reversed(events)]


def dyadic(value):
    denominator = Fraction(value).denominator
    return denominator & (denominator - 1) == 0


def decomposition_value(terms, b_weight):
    result = weighted_cube(b_weight, (0, 1))
    for slope, weight in terms:
        result = add(result, weighted_cube(weight, (1, slope)))
    return result


def four_decomposition(r):
    first, second = moments(r)
    need((first - second) % 2 == 0, "integer universal cube weights")
    terms = [(1, (first + second)//2), (-1, (second - first)//2), (0, -second)]
    return terms, first*first - first


def three_decomposition(r):
    need(r % 3 == 2, "integer three-query subclass")
    first, _ = moments(r)
    numerator = first * (r - 2) * (r + 1)
    need(numerator % 6 == 0, "integer pure-b weight")
    return [((r + 1)//3, first), ((r - 2)//3, -first)], numerator//6


def repair_events(r, terms, b_weight):
    events, position = [], r
    for slope, weight in terms:
        if weight == 0:
            continue
        if slope != position:
            events.append(("shift", slope-position, "b", "repair-source"))
        events.append(("cube", -weight, "a", "repair-query"))
        position = slope
    if position != 0:
        events.append(("shift", -position, "b", "repair-restore"))
    if b_weight != 0:
        events.append(("cube", -b_weight, "b", "repair-query"))
    return events


def check_program(r, terms, b_weight, require_dyadic=True):
    need(decomposition_value(terms, b_weight) == defect(r), "exact cubic decomposition")
    children = original_children(r)
    actual_drift = run(children)
    need(actual_drift == (add(endpoint(r)[0], defect(r)), (1, r), (0, 1)),
         "retained chronological defect and actual drifting source")
    repair = repair_events(r, terms, b_weight)
    program = children + repair
    need(program[:2*r] == children, "all original children retained unchanged")
    if require_dyadic:
        need(all(dyadic(event[1]) for event in program), "every physical coefficient dyadic")
    final = run(program)
    need(final == endpoint(r), "arbitrary-input repaired endpoint")
    need(run(inverse(program), final) == ENTRY, "literal full-program inverse")
    need(run(inverse(repair), final) == actual_drift, "literal repair inverse")
    need(run(eager_program(r)) == final, "same arbitrary-input eager endpoint")
    return {"queries": sum(event[0] == "cube" for event in repair),
            "shifts": sum(event[0] == "shift" for event in repair),
            "original_children": r}


def square_root(value):
    value = Fraction(value)
    numerator, denominator = isqrt(value.numerator), isqrt(value.denominator)
    if numerator*numerator == value.numerator and denominator*denominator == value.denominator:
        return Fraction(numerator, denominator)
    return None


def prime_factors(number):
    factors, divisor = set(), 2
    while divisor*divisor <= number:
        if number % divisor == 0:
            factors.add(divisor)
            while number % divisor == 0:
                number //= divisor
        divisor += 1
    if number > 1:
        factors.add(number)
    return factors


def localized(value, allowed_primes):
    return prime_factors(Fraction(value).denominator) <= allowed_primes


def pell_data(r):
    first, _ = moments(r)
    n = 2*r - 1
    root = square_root(Fraction(2*r*r - 2*r - 1, 12))
    quotient, remainder = divmod(n*n - 3, 6)
    k = isqrt(quotient)
    integer_solution = remainder == 0 and k*k == quotient
    need((root is not None) == integer_solution, "rational-square and integer-Pell equivalence")
    if root is None:
        return None
    need(root == Fraction(k, 2) and k > 0, "half-integral square root")
    need(n*n - 6*k*k == 3 and n % 3 == 0, "Pell identity and divisible numerator")
    need(k % 2 == 1 and (n//3) % 2 == 1, "odd k and odd one-third numerator")
    need(4*first == 3*k*k + 1 and gcd(first, k) == 1, "coprime forced weight numerator")
    t, s = (n//3 + k)//2, (n//3 - k)//2
    weight = Fraction(first, k)
    need(t-s == k and t+s == n//3, "integer normalized slopes")
    need(weight.denominator == k, "forced weight has exact reduced denominator k")
    need(decomposition_value([(t, weight), (s, -weight)], 0) == defect(r),
         "forced rational two-cube identity")
    need(dyadic(weight) == (r == 2), "only arity two has dyadic Pell weight")
    return {"r": r, "n": n, "k": k, "t": t, "s": s, "weight": weight}


def localization_checks(data):
    k, weight = data["k"], data["weight"]
    factors = prime_factors(k)
    rings = [set(), {2}, factors, factors | {2}]
    rings.extend(factors - {prime} for prime in sorted(factors))
    # This finite corroboration is distinct from the universal nonmonic
    # normalization argument in the written proof.
    scales = sorted({Fraction(1), Fraction(2), Fraction(1, 2), Fraction(3),
                     Fraction(1, 3), Fraction(k), Fraction(1, k), Fraction(2, k)})
    normalization_count = 0
    for primes in rings:
        permitted = factors <= primes
        need(localized(weight, primes) == permitted, "exact localization criterion")
        need(localized(-weight, primes) == permitted, "opposite normalized weight")
        for slope, normalized_weight in ((data["t"], weight), (data["s"], -weight)):
            admissible = []
            for alpha in scales:
                beta = alpha*slope
                gamma = normalized_weight/(alpha**3)
                need(gamma*alpha**3 == normalized_weight and beta/alpha == slope,
                     "nonmonic normalization")
                need(weighted_cube(gamma, (alpha, beta)) ==
                     weighted_cube(normalized_weight, (1, slope)),
                     "all four nonmonic cubic coefficients")
                accepted = all(localized(value, primes) for value in (alpha, beta, gamma))
                need(not accepted or permitted, "no forbidden prime hidden by rescaling")
                admissible.append(accepted)
                normalization_count += 1
            need(any(admissible) == permitted, "monic attainment and sampled nonmonic obstruction")
    return normalization_count, len(rings)


def expect_rejected(function, diagnostic):
    try:
        function()
    except ValueError as error:
        need(str(error) == diagnostic, "specific rejection diagnostic")
    else:
        raise ValueError("mutation unexpectedly accepted: " + diagnostic)


def mutation_controls():
    r = 14
    terms, b_weight = three_decomposition(r)
    children = original_children(r)
    repair = repair_events(r, terms, b_weight)
    need(repair == [("shift", -9, "b", "repair-source"),
                    ("cube", -91, "a", "repair-query"),
                    ("shift", -1, "b", "repair-source"),
                    ("cube", 91, "a", "repair-query"),
                    ("shift", -4, "b", "repair-restore"),
                    ("cube", -2730, "b", "repair-query")], "literal r14 schedule")
    changed = repair[:]
    op, coefficient, source, label = changed[1]
    changed[1] = (op, coefficient+1, source, label)
    need(run(children+changed) != endpoint(r), "wrong query coefficient rejected")
    missing_restore = [event for event in repair if event[3] != "repair-restore"]
    result = run(children+missing_restore)
    need(result[0] == endpoint(r)[0] and result[1] != ENTRY[1], "source restoration independently necessary")
    need(run(children+repair[:-1]) != endpoint(r), "pure-b correction cannot be omitted")
    omitted_child = children[1:]
    need(omitted_child != children and run(omitted_child+repair) != endpoint(r),
         "original reader cannot be omitted")
    reversed_first = [children[1], children[0], *children[2:]]
    need(run(reversed_first+repair) != endpoint(r), "read-before-shift chronology necessary")
    # Shift as if an entry snapshot existed, then restore the real source.
    # The source endpoint is correct but its sampled cube arguments are wrong.
    snapshot_schedule = repair[:]
    snapshot_schedule[0] = ("shift", repair[0][1]+r, "b", "repair-source")
    snapshot_schedule[4] = ("shift", repair[4][1]-r, "b", "repair-restore")
    result = run(children+snapshot_schedule)
    need(result[1:] == ENTRY[1:] and result[0] != endpoint(r)[0], "actual source semantics necessary")
    data = pell_data(r)
    need(data is not None, "r14 rational two-query fixture")
    rational = [(data["t"], data["weight"]), (data["s"], -data["weight"])]
    expect_rejected(lambda: check_program(r, rational, 0), "every physical coefficient dyadic")
    alpha = Fraction(1, 11)
    gamma = data["weight"] / alpha**3
    need(dyadic(gamma) and not dyadic(alpha) and not dyadic(alpha*data["t"]),
         "integral query weight cannot hide non-dyadic source")
    need(gamma == 11011 and gamma*alpha**3 == Fraction(91, 11), "hidden denominator exact values")
    alpha = Fraction(11)
    gamma = data["weight"] / alpha**3
    need(dyadic(alpha) and dyadic(alpha*data["t"]) and not dyadic(gamma),
         "integral source cannot hide non-dyadic query weight")
    expect_rejected(lambda: run([("shift", 1, "y", "forbidden-feedback")]),
                    "source shift reads b only")
    return ["query-coefficient", "final-source-restoration", "pure-b-correction",
            "retained-original-reader", "read-before-shift-chronology", "actual-drifting-source",
            "rational-square-is-not-dyadic", "denominator-in-source", "denominator-in-query",
            "output-feedback-excluded"]


def main():
    package = Path(__file__).resolve().parent
    hashes = authenticate_sources(package)
    four_count, three_count, retained_total = 0, 0, 0
    pell_scan = []
    for r in range(2, 257):
        result = check_program(r, *four_decomposition(r))
        need(result["queries"] == (2 if r == 2 else 4), "universal nonzero query count")
        need(result["shifts"] <= 3, "universal source-shift count")
        four_count += 1
        retained_total += r
        if r % 3 == 2:
            result = check_program(r, *three_decomposition(r))
            need(result["queries"] == (2 if r == 2 else 3), "subclass nonzero query count")
            need(result["shifts"] <= 3, "subclass source-shift count")
            three_count += 1
        data = pell_data(r)
        if data is not None:
            pell_scan.append(r)
    need(pell_scan == [2, 14, 134], "bounded rational two-query arities")
    pell_fixtures, normalizations, ring_cases = [], 0, 0
    n, k = 3, 1
    for _ in range(7):
        r = (n+1)//2
        data = pell_data(r)
        need(data is not None and data["k"] == k, "fixed Pell recurrence fixture")
        count, rings = localization_checks(data)
        normalizations += count
        ring_cases += rings
        pell_fixtures.append({**data, "weight": str(data["weight"]),
                              "denominator_primes": sorted(prime_factors(k))})
        n, k = 5*n+12*k, 2*n+5*k
    rational_program_arities = [2, 14, 134, 1322]
    for r in rational_program_arities:
        data = pell_data(r)
        result = check_program(r, [(data["t"], data["weight"]),
                                  (data["s"], -data["weight"])], 0, require_dyadic=False)
        need(result["queries"] == 2, "rational comparison uses two queries")
    controls = mutation_controls()
    print("PASS_DYADIC_CUBIC_REPAIR " + json.dumps({
        "source_head": SOURCE_HEAD, "source_sha256": hashes,
        "scope": "exact finite corroboration; universal claims require PROOF.md",
        "arity_scan": {"first": 2, "last": 256, "count": 255},
        "universal_integer_programs": four_count,
        "subclass_integer_programs": three_count,
        "original_children_in_universal_programs": retained_total,
        "rational_two_query_arities_in_scan": pell_scan,
        "rational_two_query_programs": rational_program_arities,
        "pell_fixtures": pell_fixtures,
        "localization_ring_cases": ring_cases,
        "nonmonic_normalizations": normalizations,
        "mutations_rejected": controls,
        "r14_dyadic_repair": {"queries": 3, "source_shifts": 3,
                               "retained_children": 14, "eager_restore_shifts": 14},
        "no_backend_saving_or_kappa_claim": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
