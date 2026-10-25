"""Independent-oracle and hypothesis-boundary controls for the supplement.

conorholds, with OpenAI Codex assistance. Apache-2.0.
These are mathematical/endpoint controls, not a machine-execution claim.
"""

from fractions import Fraction
from itertools import product


def run(model):
    g = model.Geometry()
    v = g.index[(2, 0, 2, 0, 0, 0, 0, 0)]
    w = g.index[(2, 0, -2, 0, 0, 0, 0, 0)]
    high = g.neighbors[v] & ~g.neighbors[w] & g.live
    low_roots = {tuple(2 if j == center else sign * 2 if j == other else 0 for j in range(8))
                 for center in (0, 2) for other in range(4, 8) for sign in (-1, 1)}
    low = sum(1 << g.index[r] for r in low_roots)
    target = g.off[v] & g.live
    sparse = target & ~(low | high)

    def endpoint(parts, all_sites=False):
        errors = []
        domain = range(120) if all_sites else model.indices(g.live)
        for i in domain:
            actual = sum(Fraction(g.dots[v][i], 4) * coefficient
                         for support, coefficient in parts if support >> i & 1)
            if actual != Fraction(g.dots[v][i], 4):
                errors.append(i)
        return errors

    valid = [(sparse, 1), (low, 1), (high, 1)]
    model.need(not endpoint(valid), "five-site positive oracle")
    no_self = [(sparse ^ (1 << v), 1), (low, 1), (high, 1)]
    model.need(endpoint(no_self) == [v], "self omission must change the real codeword")
    model.need((g.neighbors[v] & g.live) & ~(low | high) == sparse ^ (1 << v),
               "open-neighbor false four-site cover")
    model.need((sparse ^ (1 << v)).bit_count() == 4,
               "the self control must hit the exact four-site boundary")
    wrong_orientation = g.neighbors[v] & g.neighbors[w] & g.live
    model.need(endpoint([(sparse, 1), (low, 1), (wrong_orientation, 1)]),
               "wrong completion orientation accepted")
    model.need(endpoint([(sparse, 1), (low, -1), (high, 1)]),
               "wrong coefficient sign accepted")
    shifted_low = low ^ (1 << next(model.indices(low)))
    model.need(len(endpoint([(sparse, 1), (shifted_low, 1), (high, 1)])) == 1,
               "omitted live root not detected")
    full_errors = endpoint(valid, all_sites=True)
    model.need(len(full_errors) == 4 and all(g.frame >> i & 1 for i in full_errors),
               "puncturing convention not essential to the witness")

    # Both affine offsets are tested. A minus-type four-dimensional form
    # has a six-point hyperplane section, so nonsingularity alone is insufficient.
    values = list(product((0, 1), repeat=4))
    plus = lambda x: (x[0] * x[1] + x[2] * x[3]) % 2
    minus = lambda x: (plus(x) + x[0] + x[1]) % 2
    maximum = {}
    for name, q in (("plus", plus), ("minus", minus)):
        maximum[name] = max(sum(q(x) == 1 and sum(a * b for a, b in zip(normal, x)) % 2 == theta
                                for x in values)
                            for normal in values if any(normal) for theta in (0, 1))
    model.need(maximum == {"plus": 4, "minus": 6}, "Gauss-sign countermodel")

    # The demonstrated slack-nine space is not excluded: its two small
    # supports use five sites. Raising the four-site gate would be false.
    capacities = {1: 1, 2: 2, 3: 4}
    model.need(capacities[3] + capacities[1] == 5 > 4,
               "slack-nine witness erroneously covered by the caller rule")
    witness = model.witness_checks(g)
    model.need(witness["slack9"]["code_rank"] + witness["slack9"]["pieces_rank"]
               - witness["slack9"]["joint_rank"] == 1,
               "slack-nine control lacks its actual code intersection")
    need_failure = []
    for wrong in (True, 1.0, "1", 2):
        need_failure.append(model.canonical_json({"n": wrong}) != model.canonical_json({"n": 1}))
    model.need(all(need_failure), "scientific receipt weakened JSON number types")
    for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
        try:
            model.strict_json(raw)
        except ValueError:
            continue
        raise ValueError("ambiguous/nonfinite JSON accepted")

    return {"five_site_positive": True, "self_omission_exact_defect": 1,
            "wrong_completion_orientation_rejected": True, "wrong_coefficient_rejected": True,
            "omitted_live_root_rejected": True, "full_E8_missing_frame_sites": 4,
            "quadric_hyperplane_maxima": maximum, "slack9_outside_four_site_gate": True,
            "typed_receipt_and_strict_json": True}
