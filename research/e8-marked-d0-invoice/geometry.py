"""New finite inputs in Cartan/lattice coordinates; prepared by conorholds.

Substantial OpenAI Codex assistance; Apache-2.0. The authenticated PR3166
model supplies roots and lattice labels. No independent.py data are imported.
Universal coefficient arguments remain written proofs.
"""

from collections import Counter
from itertools import combinations, product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(model, rank):
    labels, frame, gram = model.labels, model.frame, model.gram
    p = [i for i in range(120) if model.p112_mask >> i & 1]
    pset = set(p)
    lookup = {labels[i]: i for i in range(120)}
    z = [labels[i] for i in frame]
    outside = model.hyperplane_outside
    matched = [[cut & model.p112_mask for normal, cut in enumerate(outside, 1)
                if not (normal & label).bit_count() % 2] for label in z]
    require(all(len(cuts) == 255 for cuts in matched), "matched hyperplane count")
    incidences = {r: sum(bool(gram[r][axis]) << j for j, axis in enumerate(frame)) for r in p}
    blocks = Counter(incidences.values())
    require(len(blocks) == 14 and set(blocks.values()) == {8}, "frame incidence design")

    def mask(values):
        return sum(1 << i for i in values)

    def support(axes, coefficients):
        return mask(r for r in p if sum(c * gram[frame[j]][r]
                                       for j, c in zip(axes, coefficients)))

    def projective(values):
        first = next(value for value in values if value)
        return tuple(values if first > 0 else (-x for x in values))

    expected = {1: (56, Counter({(1, 56): 1})),
                2: (24, Counter({(1, 32): 2, (2, 12): 2})),
                3: (8, Counter({(1, 16): 3, (2, 8): 6, (3, 2): 4}))}
    cuts, forms = {}, {}
    for size in (1, 2, 3):
        cut_values, case_count = [], 0
        for axes in combinations(range(8), size):
            counts, zeros = Counter(), 0
            for r in p:
                values = tuple(gram[r][frame[j]] for j in axes)
                if any(values):
                    counts[projective(values)] += 1
                else:
                    zeros += 1
            signature = Counter((sum(bool(x) for x in form), count)
                                for form, count in counts.items())
            require((zeros, signature) == expected[size], "restricted frame-form inventory")
            for signs in product((-1, 1), repeat=size - 1):
                off = support(axes, (1,) + signs)
                require(off.bit_count() == {1: 56, 2: 76, 3: 80}[size], "signed-axis support")
                for j in axes:
                    deletion = min((off & cut).bit_count() for cut in matched[j])
                    require(deletion >= 24, "matched carrying cut below twenty-four")
                    cut_values.append(deletion)
                    case_count += 1
        cuts[str(size)] = {"normal_index_pairs": case_count, "minimum_deletion": min(cut_values)}
        forms[str(size)] = {"zero": expected[size][0],
                            "shapes": [list(key) + [value] for key, value in sorted(expected[size][1].items())]}
    require([cuts[str(i)]["minimum_deletion"] for i in (1, 2, 3)] == [24, 34, 28],
            "exact matched cut minima")
    require(support((0, 1), (1, 2)).bit_count() == 88, "generic two-axis boundary")
    require(support((0, 1, 2), (1, 1, 2)).bit_count() == 94, "unequal three-axis boundary")

    triples = pure_swaps = unit_cases = 0
    for i, label in enumerate(z):
        for a, b in combinations(p, 2):
            c = lookup.get(label ^ labels[a] ^ labels[b])
            if c not in pset or c <= b:
                continue
            triples += 1
            require(rank([labels[a], labels[b], labels[c]]) == 3, "carrier triple rank")
            for r, s, t in ((a, b, c), (b, a, c), (c, a, b)):
                if gram[r][s] and gram[r][t]:
                    pure_swaps += 1
                    require(gram[r][frame[i]] == 0, "pure-carrier actual coefficient gate")
                require(not (gram[s][t] and gram[s][frame[i]] and gram[t][frame[i]]),
                        "carrier3 plus unit permits both nonunit swaps")
                unit_cases += 1
    require(triples == 7168 and pure_swaps == 5376, "carrier domain coverage")

    # Private columns certify every product of the four eight-element sign
    # groups. This is not a sampled quartet enumeration.
    complements = products = 0
    full_axes = (1 << 8) - 1
    for unmatched in combinations(range(8), 4):
        k = mask(unmatched)
        j = full_axes ^ k
        if k in blocks:
            continue
        private = [i for i in range(8) if j >> i & 1]
        groups = [[r for r in p if incidences[r] & j == 1 << i] for i in private]
        require(all(len(group) == 8 for group in groups), "private quartet sign groups")
        incidence_blocks = [incidences[group[0]] for group in groups]
        require(all(sum(bool(block >> axis & 1) for block in incidence_blocks)
                    == (1 if axis in private else 3) for axis in range(8)),
                "private quartet frame-pairing counts")
        for own, group in enumerate(groups):
            for r in group:
                require(all((1 + gram[r][frame[axis]]) % 2 == int(own != other)
                            for other, axis in enumerate(private)), "binary private coordinates")
                require(labels[r] >> 8 == 1, "private root leading bit")
        require(all((1 + gram[a][b]) % 2 == 1 for a in frame for b in frame),
                "frame labels do not pair to one")
        complements += 1
        products += 8 ** 4
    require((complements, products) == (56, 229376), "private product completeness")
    own_frame, own_two = support((0,), (1,)), support((0, 1), (1, 1))
    unrestricted_frame = min((own_frame & cut).bit_count() for cut in outside)
    unrestricted_two = min((own_two & cut).bit_count() for cut in outside)
    require(unrestricted_frame == 0 and unrestricted_two == 12,
            "dropping matched-frame premise has no counterexample")
    return {"restricted_forms": forms, "matched_cuts": cuts,
            "carrier_triples": triples, "pure_carrier_swap_roots": pure_swaps,
            "carrier_plus_unit_cases": unit_cases,
            "private_complements": complements, "private_sign_products": products,
            "countercontrols": {"without_matched_frame_cut": unrestricted_frame,
                                "without_matched_frame_two_axis_cut": unrestricted_two,
                                "generic_two_axis_support": 88,
                                "unequal_three_axis_support": 94}}
