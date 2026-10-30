#!/usr/bin/env python3
"""Check the source bill, sign-cut capacity and exact finite controls."""
import hashlib
import itertools
import json
import math
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parent


def require(test, message):
    if not test:
        raise ValueError(message)


def rank(rows, modulus=None):
    a = [[F(x) if modulus is None else x % modulus for x in row] for row in rows]
    pivot = 0
    for col in range(len(a[0]) if a else 0):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        inverse = 1 / a[pivot][col] if modulus is None else pow(a[pivot][col], -1, modulus)
        a[pivot] = [x * inverse for x in a[pivot]]
        if modulus:
            a[pivot] = [x % modulus for x in a[pivot]]
        for i in range(pivot + 1, len(a)):
            factor = a[i][col]
            a[i] = [x - factor * y for x, y in zip(a[i], a[pivot])]
            if modulus:
                a[i] = [x % modulus for x in a[i]]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def transpose(a):
    return [list(row) for row in zip(*a)]


def inverse2(a):
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    require(det != 0, "singular source pair")
    return [[a[1][1] / det, -a[0][1] / det], [-a[1][0] / det, a[0][0] / det]]


def pair(kind, q, d):
    if kind == "A":
        a = [[F(1), F(0)], [1 / q, F(1)]]
    elif kind == "B":
        a = [[F(1), F(0)], [F(1), q]]
    else:
        require(kind == "C", "unknown pair")
        a = [[q, F(0)], [F(1), F(1)]]
    return [[d * x for x in row] for row in a]


def orient(a, inverse, dual):
    if inverse:
        a = inverse2(a)
    return transpose(a) if dual else a


def difference_rank(a, b, modulus=None):
    return rank([[x - y for x, y in zip(u, v)] for u, v in zip(a, b)], modulus)


def cut_rank(kind, central_flip, transverse_flip):
    if not transverse_flip:
        return int(central_flip)
    return 1 if central_flip and kind != "A" else 2


def check_pairs():
    count = 0
    for kind, q, d, inv, dual, c, e in itertools.product(
        "ABC", [F(1), F(-1), F(2), F(-2), F(1, 2), F(2, 3)],
        [F(1), F(-1), F(2, 3)], [False, True], [False, True], range(2), range(2)
    ):
        a = orient(pair(kind, q, d), inv, dual)
        b = orient(pair(kind, (-1) ** c * q, (-1) ** e * d), inv, dual)
        require(difference_rank(a, b) == cut_rank(kind, c, e), "pair sign rank")
        count += 1
    return count


def odd_poly(r, size):
    return [F(0)] + [F(-math.comb(r, j) * (-2) ** j, 2) for j in range(1, r + 1)] + [F(0)] * (size - r - 1)


def capacity_poly(d, exceptional=True):
    """Enumerate every mask, then collect its Bernoulli probability."""
    result = [F(0)] * (d + 2)
    for mask in range(1 << (d + 1)):
        c = mask & 1
        e = (mask >> 1).bit_count() & 1
        value = 56 * (cut_rank("A", c, e) + cut_rank("B" if exceptional else "A", c, e))
        weight = mask.bit_count()
        for j in range(d + 2 - weight):
            result[weight + j] += value * math.comb(d + 1 - weight, j) * (-1) ** j
    return result


def check_cut_polynomials():
    for d in range(1, 11):
        actual = capacity_poly(d)
        expected = [F(0)] * (d + 2)
        for r, n in [(1, 28), (d, 140), (d + 1, 84)]:
            expected = [x + n * y for x, y in zip(expected, odd_poly(r, d + 2))]
        require(actual == expected, "whole-call cut polynomial")
        require(actual[1] == 112 * (2 * d + 1), "linear capacity")
    require(capacity_poly(8, False)[1] == 1904, "eight-axis positive control")
    return [str(x) for x in capacity_poly(7)]


def check_graphs():
    """Check all character pairs for mixed circuits over the field of size 5."""
    rng = Random(5628)
    axes, fields, circuits, steps = 5, 8, 12, 36
    comparisons = 0
    for _ in range(circuits):
        roots = [rng.choice([1, 2]) for _ in range(axes)]
        values = [[q * (-1 if mask >> j & 1 else 1) % 5 for j, q in enumerate(roots)] for mask in range(1 << axes)]
        states = [[[int(i == j) for j in range(fields)] for i in range(fields)] for _ in values]
        budget = [0] * len(values)
        for _ in range(steps):
            event = rng.randrange(4)
            x, y = rng.sample(range(fields), 2)
            if event == 0:
                scalar = rng.choice([1, 2, 3, 4])
                for a in states:
                    a[x] = [(u + scalar * v) % 5 for u, v in zip(a[x], a[y])]
            elif event == 1:
                for a in states:
                    a[x] = a[y][:]
            elif event == 2:
                subset = rng.randrange(1, 1 << axes)
                for mask, a in enumerate(states):
                    scalar = math.prod(q for j, q in enumerate(values[mask]) if subset >> j & 1) % 5
                    a[x] = [scalar * u % 5 for u in a[x]]
                for cut in range(len(budget)):
                    budget[cut] += (subset & cut).bit_count() & 1
            else:
                kind = rng.choice("ABC")
                central = rng.randrange(axes)
                subset = rng.randrange(1 << axes) & ~(1 << central)
                inv, dual = rng.choice([False, True]), rng.choice([False, True])
                for mask, a in enumerate(states):
                    q = F(values[mask][central])
                    d = F(math.prod(v for j, v in enumerate(values[mask]) if subset >> j & 1))
                    block = orient(pair(kind, q, d), inv, dual)
                    block = [[v.numerator * pow(v.denominator, -1, 5) % 5 for v in row] for row in block]
                    u, v = a[x], a[y]
                    a[x] = [(block[0][0] * k + block[0][1] * l) % 5 for k, l in zip(u, v)]
                    a[y] = [(block[1][0] * k + block[1][1] * l) % 5 for k, l in zip(u, v)]
                for cut in range(len(budget)):
                    budget[cut] += cut_rank(kind, cut >> central & 1, (cut & subset).bit_count() & 1)
        for x in range(len(values)):
            for y in range(x):
                require(difference_rank(states[x], states[y], 5) <= budget[x ^ y], "whole-graph cut bound")
                comparisons += 1
    for r in [1, 2, 7, 8, 11]:
        require(sum(mask.bit_count() & 1 for mask in range(1 << r)) == 1 << (r - 1), "query-only positive control")
    return {"circuits": circuits, "steps_each": steps, "character_pair_checks": comparisons}


def check_faithfulness():
    # These integer pairs are twice the one-bit Gaussian matrix.
    numerator = [[(1, 1), (1, -1)], [(1, -1), (1, 1)]]
    for vector, eigenvalue in [([1, 1], (1, 0)), ([1, -1], (0, 1))]:
        output = [tuple(sum(entry[k] * scalar for entry, scalar in zip(row, vector)) for k in range(2)) for row in numerator]
        require(output == [tuple(2 * scalar * v for v in eigenvalue) for scalar in vector], "base Gaussian eigenvector")
    multiplicities = {}
    for width in range(1, 17):
        counts = [sum(math.comb(width, k) for k in range(width + 1) if k % 4 == j) for j in range(4)]
        require(all(counts) == (width >= 3), "faithful width")
        multiplicities[str(width)] = counts
    return multiplicities


def load_profiles():
    for item in json.loads((ROOT / "INPUTS.json").read_text()):
        data = (ROOT / item["local"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == item["git_blob"], "source Git blob")
    profiles = {}
    expected = {
        "B": ({1: 1956, 2: 450, 3: 403, 4: 127, 5: 28, 8: 8}, {3: 2, 4: 26, 6: 7, 7: 47, 8: 326}, 1688),
        "C": ({1: 2011, 2: 445, 3: 427, 4: 112, 5: 12, 7: 8}, {3: 26, 4: 2, 6: 6, 7: 48, 8: 326}, 1680),
    }
    for kind in "BC":
        source = json.loads((ROOT / "inputs" / (kind + "-PROFILE.json")).read_text())
        paid, helpers = ({int(r): n for r, n in source[key].items()} for key in ["paid", "helpers"])
        net = sum(r * n for r, n in paid.items()) - sum(r * n for r, n in helpers.items())
        require((paid, helpers, net) == expected[kind], "source profile")
        require(sum(helpers.values()) == 408 and source["local_deficit"] == net, "source helper census")
        profiles[kind] = (paid, helpers)
    return profiles


def power_intervals():
    # Decimal proposes endpoints. Integer powers prove both strict bounds.
    scale, numerator, denominator = 10 ** 15, 9, 2500
    bounds = {}
    with localcontext() as ctx:
        ctx.prec = 60
        for r in range(1, 9):
            w = int(Decimal(scale) * Decimal(r) ** (-Decimal(numerator) / denominator))
            target = scale ** denominator
            require(w ** denominator * r ** numerator <= target < (w + 1) ** denominator * r ** numerator, "power interval")
            bounds[r] = (F(r * w, scale), F(r * (w + 1), scale))
    return bounds


def check_bills(profiles):
    results = {}
    bounds = power_intervals()
    for kind, (paid, helpers) in profiles.items():
        cap = {1: 28, 7: 140, 8: 84}
        coefficients = {r: paid.get(r, 0) - helpers.get(r, 0) - cap.get(r, 0) for r in range(1, 9)}
        extra = 8 if kind == "B" else 0
        low = {r: n for r, n in coefficients.items() if n > 0}
        low[1] -= extra
        high = {r: -n for r, n in coefficients.items() if n < 0}
        mass = sum(r * n for r, n in low.items())
        require(mass == sum(r * n for r, n in high.items()) == (4567 if kind == "B" else 4576), "separated mass")
        require(max(low) == 5 and min(high) == 6, "separated support")
        hinge_margins = []
        for k in range(1, 17):
            g = lambda r: F(min(r, k))
            actual = sum(n * g(r) for r, n in coefficients.items())
            lower = extra * g(1) + mass * (g(5) / 5 - g(6) / 6)
            require(actual >= lower >= 0, "concave hinge tariff")
            hinge_margins.append(str(actual))
        lower = sum(n * bounds[r][0 if n >= 0 else 1] for r, n in coefficients.items())
        upper = sum(n * bounds[r][1 if n >= 0 else 0] for r, n in coefficients.items())
        require(lower > (F(3158147, 100000) if kind == "B" else F(2398603, 100000)), "strict exact moment gap")
        results[kind] = {"bill_minus_capacity": coefficients, "linear_gap": extra, "separated_mass": mass,
                         "hinge_margins_1_to_16": hinge_margins,
                         "gap_at_C_9_over_2500": {"lower": str(lower), "upper": str(upper)}}
    return results


def controls(profiles):
    failures = 0
    paid, helpers = profiles["B"]
    changed = {"B": (dict(paid), dict(helpers))}
    changed["B"][0][1] -= 8
    tests = [
        (lambda: require(capacity_poly(7)[1] == 1904, "wrong transverse dimension")),
        (lambda: require(difference_rank(pair("B", F(1), F(1)), pair("B", F(1), F(-1))) == cut_rank("B", 1, 1), "omitted central flip")),
        (lambda: check_bills(changed)),
        (lambda: require(all(sum(math.comb(2, k) for k in range(3) if k % 4 == j) for j in range(4)), "unfaithful width")),
    ]
    for test in tests:
        try:
            test()
        except ValueError:
            failures += 1
    require(failures == len(tests), "corruption controls")
    return failures


def main():
    profiles = load_profiles()
    result = {
        "status": "PASS_COMPLEMENTARY_CALLER_CAPACITY_GATE",
        "pair_rank_cases": check_pairs(), "capacity_polynomial_in_p": check_cut_polynomials(),
        "graph_checks": check_graphs(), "Gaussian_eigenvalue_multiplicities": check_faithfulness(),
        "bills": check_bills(profiles), "rejected_controls": controls(profiles),
        "main_capacity": {"1": 28, "7": 140, "8": 84},
        "scope": "Coordinate Gaussian callers; ordinary even-power algebra; separate fresh helpers; every f>=3 and 0<C<1. No new kappa.",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    expected = ROOT / "RESULT.json"
    require(expected.read_text() == encoded, "frozen result")
    print(result["status"])
    print("RESULT_SHA256", hashlib.sha256(encoded.encode()).hexdigest())


if __name__ == "__main__":
    main()
