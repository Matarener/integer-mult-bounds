"""Exact finite inputs for the written coupled E8 theorem.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
Root geometry, parabolic bounds and Fourier argument credit PR3166/PR968;
the dimension relaxation is the method of DreamingOfClouds / PR2962.
The retained PR3755 geometry is used explicitly, not called independent evidence.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations

from vendor.pr3755 import geometry as g


SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)


def inverse(rows):
    n = len(rows)
    a = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
         for i, row in enumerate(rows)]
    for j in range(n):
        k = next((k for k in range(j, n) if a[k][j]), None)
        g.require(k is not None, "singular simple-root coordinate matrix")
        a[j], a[k] = a[k], a[j]
        scale = a[j][j]
        a[j] = [x / scale for x in a[j]]
        for k in range(n):
            if k != j:
                scale = a[k][j]
                a[k] = [x - scale * y for x, y in zip(a[k], a[j])]
    return [row[n:] for row in a]


def parabolic_inventory(roots):
    inv = inverse(list(zip(*SIMPLE)))
    supports = []
    for root in roots:
        coefficients = [sum(x * y for x, y in zip(row, root)) for row in inv]
        g.require(all(x.denominator == 1 for x in coefficients), "nonintegral simple coordinates")
        g.require(all(x >= 0 for x in coefficients) or all(x <= 0 for x in coefficients),
                  "root is not positive or negative in declared simple system")
        supports.append(sum(1 << i for i, x in enumerate(coefficients) if x))
    maxima = [0] * 9
    exceptional = 0
    proper_seven_counts = []
    for subset in range(256):
        indices = [i for i, support in enumerate(supports) if support & ~subset == 0]
        rank = subset.bit_count()
        maxima[rank] = max(maxima[rank], len(indices))
        if rank == 7:
            proper_seven_counts.append(len(indices))
            if len(indices) > 42:
                perpendicular = [r for r in roots if all(g.dot(r, roots[i]) == 0 for i in indices)]
                g.require(len(indices) == 63 and len(perpendicular) == 1,
                          "large proper parabolic does not have a root normal")
                exceptional += 1
    g.require(maxima == [0, 1, 3, 6, 12, 20, 36, 63, 120], "parabolic root capacities")
    g.require(exceptional > 0, "missing E7/root-normal positive control")
    return {"subsets": 256, "root_rank_caps": maxima,
            "rank_seven_counts": sorted(proper_seven_counts), "E7_root_normal_cases": exceptional}


def quadratic(value):
    odd_label = value | ((1 ^ g.parity(value)) << 8)
    weight = odd_label.bit_count()
    return (weight * (weight - 1) // 2) % 2


def fourier_capacities(labels):
    # The odd affine hyperplane in F2^9 is identified with F2^8.
    values = [quadratic(x) for x in range(256)]
    expected = {x for x in range(512) if g.parity(x) and (x.bit_count() * (x.bit_count() - 1) // 2) % 2}
    g.require(set(labels) == expected and sum(values) == 120, "quadric/label identification")
    polar = [sum((values[(1 << i) ^ (1 << j)] ^ values[1 << i] ^ values[1 << j]) << j
                 for j in range(8)) for i in range(8)]
    g.require(g.binary_rank(polar) == 8, "degenerate eight-dimensional polar form")
    walsh = []
    for a in range(256):
        value = sum(1 if values[x] == g.parity(a & x) else -1 for x in range(256))
        # B^{-1}=B=I+J in these coordinates.
        dual = a ^ (255 if g.parity(a) else 0)
        g.require(value == 16 * (-1 if values[dual] else 1), "exact quadratic Fourier identity")
        walsh.append(value)
    caps = [0]
    for rank in range(1, 9):
        d = rank - 1
        caps.append(1 if d == 0 else min(1 << d, (1 << (d - 1)) + (4 if d <= 6 else 0)))
    g.require(caps == [0, 1, 2, 4, 8, 12, 20, 36, 64], "Fourier support cap formula")
    # Attainment controls only: the upper bound is the written Gauss-sum lemma.
    state = 3166
    witnesses = []
    for rank in range(1, 9):
        d = rank - 1
        found = None
        for trial in range(20000):
            basis = []
            while len(basis) < d:
                state = (1664525 * state + 1013904223) % (1 << 32)
                value = (state >> 16) & 255
                if g.binary_rank(basis + [value]) > len(basis):
                    basis.append(value)
            state = (1664525 * state + 1013904223) % (1 << 32)
            origin = (state >> 16) & 255
            flat = [origin]
            for value in basis:
                flat += [x ^ value for x in flat]
            chosen = [x | ((1 ^ g.parity(x)) << 8) for x in flat if values[x]]
            if len(chosen) == caps[rank]:
                g.require(g.binary_rank(chosen) == rank, "capacity witness has wrong support rank")
                found = {"rank": rank, "affine_origin": origin, "directions": basis,
                         "root_labels": chosen, "count": len(chosen)}
                break
        g.require(found is not None, "capacity attainment control not found")
        witnesses.append(found)
    return {"walsh_values": dict(sorted(Counter(walsh).items())), "walsh_coefficients": 256,
            "binary_support_caps": caps, "attainment_witnesses": witnesses}


def root_characters(roots, labels):
    off = [sum(1 << j for j, r in enumerate(roots) if g.dot(root, r)) for root in roots]
    spectrum = Counter()
    minimum = 120
    nonself_minimum = 120
    checks = 0
    for z in range(1, 512):
        mask = sum(1 << i for i, label in enumerate(labels) if g.parity(z & label))
        spectrum[mask.bit_count()] += 1
        for i, label in enumerate(labels):
            count = (off[i] & mask).bit_count()
            if z == label:
                g.require(count == 1, "root's own character does not isolate its line")
            else:
                g.require(count >= 24, "root remainder character deletion bound")
                minimum = min(minimum, count)
                nonself_minimum = min(nonself_minimum, (off[i] & mask & ~(1 << i)).bit_count())
            checks += 1
    # The 9-bit model has complementary characters z and z+omega;
    # each such pair contributes sizes56 and64. Omega alone sees all120.
    g.require(dict(sorted(spectrum.items())) == {56: 255, 64: 255, 120: 1}, "character spectrum")
    g.require(minimum == 24, "root remainder bound is not sharp")
    g.require(nonself_minimum == 24, "nonself root remainder bound")
    return {"nonzero_characters": 511, "spectrum": dict(sorted(spectrum.items())),
            "root_character_pairs": checks, "minimum_nonmatching_root_intersection": minimum,
            "minimum_nonmatching_nonself_root_intersection": nonself_minimum}


def budget_feasible(n, budget, caps, root_caps):
    """Forward dominance DP; exact in the necessary size relaxation only.

    Sort basis weights increasingly. After n-8+i columns, uncovered root
    rows lie in a scalar (8-i)-space. Their support union must therefore
    cover at least120-root_caps[8-i] sites. This is PR2962's relaxation,
    implemented forwards with a paid-weight budget rather than max deficit.
    """
    states = {(1, 0): (0, ())}
    visited = 0
    peak = 1
    for placed in range(1, n + 1):
        next_states = {}
        i = placed - (n - 8)
        required = 120 - root_caps[8 - i] if 1 <= i <= 8 else 0
        for (previous, covered), (cost, path) in states.items():
            for weight in range(previous, 10):
                paid = cost + weight
                if paid + (n - placed) * weight > budget:
                    break
                union = min(120, covered + caps[weight])
                if union < required:
                    continue
                key = (weight, union)
                old = next_states.get(key)
                if old is None or paid < old[0]:
                    next_states[key] = (paid, path + (weight,))
                visited += 1
        states = next_states
        peak = max(peak, len(states))
        if not states:
            return None, visited, peak
    best = min(states.values()) if states else None
    return best, visited, peak


def dimension_screen(caps, root_caps):
    caps = list(caps) + [120]
    positive, visited, peak = budget_feasible(23, 72, caps, root_caps)
    g.require(positive is not None and positive[0] == 72, "dimension23 relaxed positive control")
    too_small, _, _ = budget_feasible(23, 71, caps, root_caps)
    g.require(too_small is None, "dimension23 relaxed minimum is not72")
    rows = []
    for n in range(24, 73):
        feasible, count, maximum = budget_feasible(n, 72, caps, root_caps)
        g.require(feasible is None, "unpaid strict dimension screen")
        visited += count
        peak = max(peak, maximum)
        rows.append({"dimension": n, "basis_budget72_feasible_in_relaxation": False})
    return {"strict_dimensions": rows, "dimension23_positive_weights": list(positive[1]),
            "dimension23_positive_cost": positive[0], "transitions": visited,
            "peak_frontier_states": peak, "dimension73_through120": "weight>=dimension>=73"}


def partial_support_budget():
    caps = (0, 1, 2, 4, 8, 12, 20, 36)
    profiles = []
    def visit(remaining, previous, path):
        if remaining == 0:
            if len(path) >= 2:
                profiles.append(path)
            return
        for weight in range(previous, remaining + 1):
            visit(remaining - weight, weight, path + (weight,))
    for bill in range(2, 8):
        visit(bill, 1, ())
    maximum = max(sum(caps[w] for w in path) for path in profiles)
    g.require(len(profiles) == 37 and maximum == 21,
              "low-budget partial-quotient support union bound")
    return {"partitions": len(profiles), "minimum_members": 2,
            "maximum_bill": 7, "maximum_support_union": maximum}


def run(certificate):
    model = g.build_model()
    roots = g.standard_binding(model)
    certificate_result = g.check_certificate(model, certificate)
    transport = g.reflection_transport(model)
    parabolics = parabolic_inventory(roots)
    fourier = fourier_capacities(model["labels"])
    characters = root_characters(roots, model["labels"])
    screen = dimension_screen(fourier["binary_support_caps"], parabolics["root_rank_caps"])
    middle = []
    for size in range(9, 55):
        minimum_weight = next(w for w, cap in enumerate(fourier["binary_support_caps"]) if cap >= 57 - size)
        floor = size + 8 * minimum_weight
        g.require(floor >= 73, "middle coordinate-set slack")
        middle.append({"size": size, "mixed_min_weight": minimum_weight, "basis_floor": floor})
    return model, roots, {"unit_certificate": certificate_result, "reflection_transport": transport,
                          "parabolics": parabolics, "fourier": fourier,
                          "characters": characters, "dimension_screen": screen,
                          "middle_coordinate_sets": middle, "partial_support_budget": partial_support_budget()}
