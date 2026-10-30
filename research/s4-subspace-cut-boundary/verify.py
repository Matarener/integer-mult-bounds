#!/usr/bin/env python3
"""Exact binary subspace-cut inventory for the fixed S4 tuple. Apache-2.0."""

import itertools
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GENERATORS = ((1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2))
TARGETS = ((1, 0, 3, 2), (2, 0, 3, 1), (3, 1, 2, 0), (1, 0, 3, 2))
SOURCES = (
    "research/s4-two-premium-cut-envelope/PROOF.md",
    "research/s4-two-premium-cut-envelope/README.md",
    "research/symmetric-adjacent-cut-bound/PROOF.md",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, limit=131072):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "input capacity")
    return raw


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def reject_number(value):
    raise ValueError("noninteger JSON number: " + value)


def load_json(path):
    return json.loads(
        read(path),
        object_pairs_hook=unique_object,
        parse_float=reject_number,
        parse_constant=reject_number,
    )


def authenticate():
    pins = load_json(HERE / "SOURCES.json")["files"]
    live = {row["path"]: row for row in pins if row["usage"] == "input"}
    require(set(live) == set(SOURCES), "source inventory")
    for name, row in live.items():
        raw = read(ROOT / name)
        require(sha256(raw).hexdigest() == row["sha256"], "source SHA256")


def action(permutation, vector):
    return sum(((vector >> j) & 1) << permutation[j] for j in range(len(permutation)))


def coordinate_action(permutation, edges):
    if not edges:
        return permutation
    pairs = tuple(itertools.combinations(range(4), 2))
    return tuple(pairs.index(tuple(sorted(permutation[i] for i in e))) for e in pairs)


def subspaces(width):
    require(width in (4, 6), "module width")
    layers = [{frozenset((0,))}]
    for dimension in range(width):
        following = set()
        for space in layers[dimension]:
            for vector in range(1 << width):
                if vector not in space:
                    following.add(space | frozenset(x ^ vector for x in space))
        require(all(len(s) == 1 << (dimension + 1) for s in following), "span size")
        layers.append(following)
    return layers


def crossing(space, images):
    image = {images[x] for x in space}
    intersection = space.intersection(image)
    require(len(image) == len(space) and len(intersection) > 0, "invertible action")
    require(len(intersection).bit_count() == 1, "intersection is a subspace")
    return len(space).bit_length() - len(intersection).bit_length()


def inventory(edges):
    width = 6 if edges else 4
    actions = [coordinate_action(p, edges) for p in GENERATORS + TARGETS]
    maps = [[action(p, x) for x in range(1 << width)] for p in actions]
    layers = subspaces(width)
    histogram, slacks, encoded = Counter(), Counter(), []
    for layer in layers:
        for space in layer:
            profile = tuple(crossing(space, m) for m in maps)
            module_slack = sum(
                a * b for a, b in zip((4, 2, 4), profile[:3], strict=True)
            ) - sum(profile[3:])
            require(module_slack >= 0, "strong module cut inequality")
            slack = 4 * sum(profile[:3]) - sum(profile[3:])
            require(slack >= 0, "shared cut inequality")
            require(all(c <= width // 2 for c in profile), "cut dimension cap")
            histogram[profile] += 1
            slacks[slack] += 1
            encoded.append(sum(1 << x for x in space))
    counts = [len(layer) for layer in layers]
    expected = [1, 63, 651, 1395, 651, 63, 1] if edges else [1, 15, 35, 15, 1]
    require(counts == expected, "Gaussian binomial completeness")
    require(len(set(encoded)) == sum(counts), "unique complete subspaces")
    payload = b"".join(x.to_bytes((1 << width) // 8, "little") for x in sorted(encoded))
    return {
        "dimension_counts": counts,
        "spaces": sum(counts),
        "membership_sha256": sha256(payload).hexdigest(),
        "profiles": [
            {"cuts": list(p), "count": n} for p, n in sorted(histogram.items())
        ],
        "slack_histogram": {str(k): v for k, v in sorted(slacks.items())},
    }


def inversions(p):
    return sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4))


def natural_cases():
    cases = []
    for a, b, c in itertools.product((0, 1), repeat=3):
        # Three actual words for (14), and the ambient four-space cap.
        far = min(2, 2 * a + 2 * b + c, a + 2 * b + 2 * c, 2 * a + b + 2 * c)
        bound = 2 * min(2, a + c) + min(2, a + b + c) + far
        require(bound <= 4 * a + 2 * b + 4 * c, "all-field natural case")
        cases.append([a, b, c, bound])
    return cases


def certificate():
    ordered = [inversions(p) for p in GENERATORS + TARGETS]
    natural = []
    for prefix in (1, 3):
        natural.append(
            [sum(p[i] >= prefix for i in range(prefix)) for p in GENERATORS + TARGETS]
        )
    require(ordered == [1, 1, 1, 2, 3, 5, 2], "ordered-pair profile")
    require(
        natural == [[1, 0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1, 1]], "prefix profiles"
    )
    charges = [sum(row[j] for row in [ordered, *natural]) for j in range(3)]
    bound = sum(sum(row[3:]) for row in [ordered, *natural])
    require(charges == [2, 1, 2] and bound == 20, "attaining cut certificate")
    middle = [sum(p[i] >= 2 for i in range(2)) for p in GENERATORS + TARGETS]
    require(middle == [0, 1, 0, 0, 1, 1, 0], "middle prefix profile")
    module_bound = 2 * sum(natural[0][3:]) + sum(middle[3:]) + 2 * sum(natural[1][3:])
    require(module_bound == 18, "module-only attainment")
    return {
        "generator_charges": charges,
        "tuple_bound": bound,
        "dual": [4, 4, 4],
        "module_only_bound": module_bound,
        "module_only_dual": [4, 2, 4],
    }


def run():
    authenticate()
    return {
        "status": "PASS_S4_SUBSPACE_CUT_BOUNDARY",
        "natural_binary": inventory(False),
        "edge_binary": inventory(True),
        "attainment": certificate(),
        "natural_all_field_cases": natural_cases(),
        "module_only_price_bound": "4*p1+2*p2+4*p3 for all nonnegative prices",
        "price_cone_bound": "8*beta+4*alpha for 0<=alpha<=beta",
        "direct_bill": "9*beta+3*alpha",
        "actual_circuit_optimum_unsettled": True,
    }


if __name__ == "__main__":
    actual = run()
    expected = load_json(HERE / "RESULT.json")
    require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "result receipt",
    )
    print(
        json.dumps(
            {"status": actual["status"], "binary_spaces": 2892, **actual["attainment"]}
        )
    )
