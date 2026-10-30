#!/usr/bin/env python3
"""Exact two-channel support certificate. Produced by Nick Petalas. Apache-2.0."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path

CLIQUE = (1, 5, 18, 20, 80, 85, 100, 103)
WITNESS = ((0, 0, 0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 1, 1, 1, 0))
SOURCE_FILES = ("PORTS.json", "PROOF.md", "README.md", "SOURCES.json",
                "TASK.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reject(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def checked_ports(payload, expected_hash):
    require(hashlib.sha256(payload).hexdigest() == expected_hash, "port source drift")
    ports = json.loads(payload)
    require(isinstance(ports, list) and len(ports) == 104, "port count")
    require(all(type(q) is int and 0 < q < 512 for q in ports), "port range")
    require(len(set(ports)) == 104, "duplicate ports")
    require(all(q.bit_count() in (3, 7) for q in ports), "port type")
    return ports


def inner(a, b):
    """Integer root inner product in A8 coordinates, before dividing by two."""
    sa = {i for i in range(9) if a >> i & 1}
    sb = {i for i in range(9) if b >> i & 1}
    if len(sa) == 3 and len(sb) == 3:
        return len(sa & sb) - 1
    if len(sa) == 3:
        sa, sb = sb, sa
    i, j = sorted(set(range(9)) - sa)
    if len(sb) == 3:
        return int(i in sb) - int(j in sb)
    k, ell = sorted(set(range(9)) - sb)
    return int(i == k) - int(i == ell) - int(j == k) + int(j == ell)


def root(q):
    """Separate literal nine-coordinate rational root construction."""
    if q.bit_count() == 3:
        return tuple(Fraction(2 if q >> i & 1 else -1, 3) for i in range(9))
    i, j = [i for i in range(9) if not (q >> i & 1)]
    return tuple(Fraction(int(k == i) - int(k == j)) for k in range(9))


def generators(ports):
    roots = [root(q) for q in ports]
    rational = []
    for t in CLIQUE:
        row = []
        for q, vector in zip(ports, roots):
            value = sum(a * b for a, b in zip(roots[t], vector)) / 2
            require(value == Fraction(inner(ports[t], q), 2), "Gram formula")
            require(value.denominator in (1, 2), "non-dyadic Gram entry")
            row.append(value)
        rational.append(tuple(row))
    ternary = tuple(tuple(2 * inner(ports[t], q) % 3 for q in ports) for t in CLIQUE)
    for i in range(8):
        for j in range(8):
            require(rational[i][CLIQUE[j]] == int(i == j), "systematic rational basis")
            require(ternary[i][CLIQUE[j]] == int(i == j), "systematic ternary basis")
    return tuple(rational), ternary


def canonical(vector):
    require(len(vector) == 8 and all(x in (0, 1, 2) for x in vector), "coefficient shape")
    lead = next((x for x in vector if x), None)
    require(lead is not None, "zero projective vector")
    return tuple(x * lead % 3 for x in vector)


def support(coefficients, columns, modulus=None):
    result = 0
    for i, column in enumerate(columns):
        value = sum(a * b for a, b in zip(coefficients, column))
        if modulus is not None:
            value %= modulus
        if value:
            result |= 1 << i
    return result


def plane_key(a, b):
    plus = canonical(tuple((x + y) % 3 for x, y in zip(a, b)))
    minus = canonical(tuple((x + 2 * y) % 3 for x, y in zip(a, b)))
    points = tuple(sorted((a, b, plus, minus)))
    require(len(set(points)) == 4, "dependent pair")
    return points


def pair_census(coefficients, masks):
    histogram = Counter()
    minimum = 105
    minimizers = []
    for i in range(len(masks)):
        for j in range(i):
            weight = (masks[i] | masks[j]).bit_count()
            histogram[weight] += 1
            if weight < minimum:
                minimum = weight
                minimizers = [(j, i)]
            elif weight == minimum:
                minimizers.append((j, i))
    planes = Counter(plane_key(coefficients[i], coefficients[j]) for i, j in minimizers)
    require(all(count == 6 for count in planes.values()), "plane pair multiplicity")
    require(sum(histogram.values()) == 5377560, "incomplete pair census")
    require(minimum == 72, "second support weight")
    return {
        "projective_words": len(coefficients), "independent_projective_pairs": sum(histogram.values()),
        "two_dimensional_subcodes": sum(histogram.values()) // 6,
        "second_support_weight": minimum, "minimizing_pairs": len(minimizers),
        "minimizing_subcodes": len(planes),
        "pair_support_histogram": {str(k): v for k, v in sorted(histogram.items())},
    }


def checks(rational, ternary, ports, payload, port_hash):
    coefficients = [c for c in product(range(3), repeat=8) if any(c) and canonical(c) == c]
    require(len(coefficients) == 3280, "projective coverage")
    columns = tuple(zip(*ternary))
    masks = [support(c, columns, 3) for c in coefficients]
    require(all(mask for mask in masks), "noninjective coefficient map")
    result = pair_census(coefficients, masks)
    rational_columns = tuple(zip(*rational))
    q_masks = [support(c, rational_columns) for c in WITNESS]
    f_masks = [support(c, columns, 3) for c in WITNESS]
    require(q_masks[0] | q_masks[1] == f_masks[0] | f_masks[1], "witness lift support")
    require((q_masks[0] | q_masks[1]).bit_count() == 72, "sharp rational witness")
    require(WITNESS[0][3] * WITNESS[1][4] - WITNESS[0][4] * WITNESS[1][3] == 1,
            "independent rational witness")
    require(len(plane_key(*WITNESS)) == 4, "independent ternary witness")
    require(support(tuple(2 * x % 3 for x in WITNESS[1]), columns, 3) == f_masks[1],
            "projective scaling")
    require(max(mask.bit_count() for mask in f_masks) < 72, "individual support is insufficient")
    require(sum(mask.bit_count() for mask in f_masks) > 72, "support union is not a sum")
    reject(lambda: canonical((0,) * 8), "zero projective word")
    reject(lambda: plane_key(WITNESS[0], WITNESS[0]), "dependent pair")
    reject(lambda: checked_ports(payload + b' ', port_hash), "changed source bytes")
    result["witness"] = {
        "coefficients": WITNESS, "rational_individual_weights": [x.bit_count() for x in q_masks],
        "ternary_individual_weights": [x.bit_count() for x in f_masks],
        "union_ports": [q for i, q in enumerate(ports) if (q_masks[0] | q_masks[1]) >> i & 1],
    }
    return result


def same_receipt(expected, actual):
    require(expected == actual, "receipt differs from full recomputation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    metadata = json.loads((package / "SOURCES.json").read_text())
    external = metadata["external_sources"][0]
    require(external["local_path"] == "PORTS.json", "coordinate fixture path")
    payload = (package / "PORTS.json").read_bytes()
    ports = checked_ports(payload, external["sha256"])
    rational, ternary = generators(ports)
    result = checks(rational, ternary, ports, payload, external["sha256"])
    result["witness"]["coefficients"] = [list(c) for c in WITNESS]
    result["source_hashes"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                               for name in SOURCE_FILES}
    result["claim_type"] = "finite certificate and scoped support/frame proof"
    for value in (71, 73):
        mutant = dict(result, second_support_weight=value)
        reject(lambda: same_receipt(mutant, result), "changed second weight")
    require(result["minimizing_subcodes"] == 704, "minimizer coverage")
    if args.emit_receipt is not None:
        args.emit_receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((package / "RESULT.json").read_text())
        same_receipt(expected, result)
    print("PASS_P104_TWO_CHANNEL_SUPPORT d2=72 pairs=5377560 minimizing_subcodes=704")


if __name__ == "__main__":
    main()
