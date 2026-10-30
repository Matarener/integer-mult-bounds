"""Certificate integrity and necessary-hypothesis controls.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
Controls are classified separately from factorization mutations in fixtures.py.
"""

from copy import deepcopy
from functools import reduce
from itertools import combinations
from operator import xor


def run(g, model, certificate):
    g.check_certificate(model, certificate)
    # The two ranks in the theorem belong to different fields. This standard
    # three-vector example separates them, as well as testing zero/full rank.
    g.require(g.binary_rank([0, 0]) == 0
              and g.binary_rank([1 << i for i in range(9)]) == 9
              and g.binary_rank([3, 5, 6]) == 2, "binary rank field controls")
    g.require(g.rational_rank([[1, 1, 0], [1, 0, 1], [0, 1, 1]]) == 3,
              "scalar rank field control")
    cases = []

    def case(name, change, expected):
        value = deepcopy(certificate)
        change(value)
        cases.append((name, value, expected))

    case("missing_single", lambda d: d["single_types"].pop(), "single inventory count")
    case("missing_forbidden_profile", lambda d: d["forbidden_pairs"].pop(), "forbidden inventory count")
    case("duplicate_single", lambda d: d["single_types"].__setitem__(1, deepcopy(d["single_types"][0])),
         "duplicate single type")
    case("duplicate_profile", lambda d: d["forbidden_pairs"].__setitem__(1, deepcopy(d["forbidden_pairs"][0])),
         "unknown/duplicate forbidden profile")

    def wrong_binding(data):
        counts = data["forbidden_pairs"][1]["counts"]
        data["forbidden_pairs"][1] = deepcopy(data["forbidden_pairs"][0])
        data["forbidden_pairs"][1]["counts"] = counts

    case("valid_minor_bound_to_wrong_profile", wrong_binding, "normal/profile binding")
    case("duplicate_minor_row", lambda d: d["single_types"][0]["rows"].__setitem__(
        -1, d["single_types"][0]["rows"][0]), "minor root indices")
    case("negative_root_index", lambda d: d["single_types"][0]["rows"].__setitem__(0, -1),
         "minor root indices")
    case("incorrect_determinant", lambda d: d["single_types"][0].__setitem__(
        "determinant", d["single_types"][0]["determinant"] + 1), "integer minor determinant")
    case("boolean_determinant", lambda d: d["single_types"][0].__setitem__("determinant", True),
         "minor determinant type/value")
    case("boolean_normal", lambda d: d["single_types"][0].__setitem__("normal", True),
         "single normal binding")
    case("float_profile_count", lambda d: d["forbidden_pairs"][0]["counts"].__setitem__(
        0, float(d["forbidden_pairs"][0]["counts"][0])), "profile counts")
    outside = next(i for i, label in enumerate(model["labels"]) if not g.parity(label & 1))
    case("witness_outside_character", lambda d: d["single_types"][0]["rows"].__setitem__(0, outside),
         "witness support membership")

    # A full-rank minor can still fail in odd characteristic. These eight
    # valid star rows have determinant +/-768, so specifically exercise the
    # unit gate after the membership and exact determinant checks pass.
    star_indices = [7, 14, 20, 25, 29, 32, 34, 35]
    scalar_rows = g.standard_binding(model)
    star_determinant = g.determinant([scalar_rows[i] for i in star_indices])
    g.require(abs(star_determinant) == 768, "nonunit full-rank control")

    def nonunit(data):
        data["single_types"][7]["rows"] = star_indices
        data["single_types"][7]["determinant"] = star_determinant

    case("full_rank_minor_not_unit_over_Z_half", nonunit, "minor is not a unit over Z[1/2]")

    # Eight distinct valid single-character rows whose shared second character
    # forces rank seven: this must reach the determinant gate, not a shape gate.
    dependent = [i for i, label in enumerate(model["labels"])
                 if g.parity(label & 1) and g.parity(label & 2)][:8]
    g.require(len(dependent) == 8 and g.determinant([scalar_rows[i] for i in dependent]) == 0,
              "singular distinct-row control is not singular")

    def singular(data):
        data["single_types"][0]["rows"] = dependent
        data["single_types"][0]["determinant"] = 1

    case("distinct_valid_rows_with_singular_minor", singular, "integer minor determinant")
    rejected = {}
    for name, value, expected in cases:
        try:
            g.check_certificate(model, value)
        except ValueError as error:
            g.require(expected in str(error), "control failed at wrong gate: " + name)
            rejected[name] = expected
        else:
            raise ValueError("accepted corrupted certificate: " + name)

    alternate = deepcopy(certificate)
    witness = alternate["single_types"][0]
    witness["rows"][0], witness["rows"][1] = witness["rows"][1], witness["rows"][0]
    witness["determinant"] = -witness["determinant"]
    g.check_certificate(model, alternate)

    def intersection_rank(a, b):
        return g.rational_rank([row for row, label in zip(model["roots"], model["labels"])
                                if g.parity(label & a) and g.parity(label & b)])

    # Omitting either binary condition admits a dependent fake clique. At
    # least one of its edges has actual scalar intersection rank eight.
    even = [3, 12, 15]
    odd = [1, 2, 4, 7]
    g.require(reduce(xor, even, 0) == reduce(xor, odd, 0) == 0, "dependent clique controls")
    g.require(all(not g.parity(a & b) for a, b in combinations(even, 2)), "even weakened clique")
    g.require(all(g.parity(a) for a in odd), "odd weakened clique")
    even_rank = intersection_rank(3, 12)
    odd_rank = intersection_rank(1, 7)
    g.require(even_rank == odd_rank == 8, "weakened binary edge rules escaped geometry")
    return {"certificate_corruptions_rejected": rejected,
            "binary_vs_scalar_rank_control": {"binary": 2, "rational": 3},
            "alternative_valid_minor_accepted": True,
            "weakened_edge_rule_counterexamples": {
                "omit_even_colour": {"normals": even, "xor": 0, "forbidden_pair_rank": even_rank},
                "omit_orthogonality": {"normals": odd, "xor": 0, "forbidden_pair_rank": odd_rank}}}
