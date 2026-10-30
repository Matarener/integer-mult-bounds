#!/usr/bin/env python3
"""Independent E8 row-module certificates checked by integer multiplication.

@CubeJerry, with OpenAI Codex assistance. Apache-2.0.
Imports neither the certificate builder nor any predecessor executable.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import dot, fixed_geometry, matrices, projection, transport_numerator

PACKAGE = Path(__file__).resolve().parent
EXPECTED_COUNTS = {"S1": 1, "A2": 119, "S2": 119, "A3": 1540, "S3": 1540, "W2": 3276}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper, name):
    require(type(value) is int and lower <= value <= upper, "invalid " + name)
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def dense_dyadic(row, width):
    """Decode to integer numerators and a common power-of-two denominator."""
    require(isinstance(row, list) and len(row) == width, "dyadic row shape")
    decoded = []
    for pair in row:
        require(isinstance(pair, list) and len(pair) == 2, "dyadic pair shape")
        n = integer(pair[0], -(1 << 32), 1 << 32, "numerator")
        e = integer(pair[1], 0, 16, "denominator exponent")
        require(e == 0 or n % 2 != 0, "noncanonical dyadic pair")
        decoded.append((n, e))
    exponent = max((e for _, e in decoded), default=0)
    return [n << (exponent-e) for n, e in decoded], 1 << exponent


def sparse_dyadic(row, width):
    require(isinstance(row, list) and len(row) <= width, "sparse row shape")
    dense = [[0, 0] for _ in range(width)]
    previous = -1
    for entry in row:
        require(isinstance(entry, list) and len(entry) == 3, "sparse entry shape")
        index = integer(entry[0], 0, width-1, "source index")
        require(index > previous, "unordered or duplicate source index")
        require(entry[1] != 0, "zero sparse coefficient")
        dense[index] = entry[1:]
        previous = index
    return dense_dyadic(dense, width)


def check_splitting(matrix, witness):
    """Check E=C A, E[:,J]=I, A=A[:,J] E over Z[1/2].

    All equalities use integer products after clearing powers of two.
    There is no elimination, determinant or modular arithmetic in this checker.
    """
    m = len(matrix)
    require(0 < m <= 63, "matrix row bound")
    n = len(matrix[0])
    require(0 < n <= 8 and all(len(row) == n for row in matrix), "matrix shape")
    require(all(type(x) is int for row in matrix for x in row), "integer input required")
    require(isinstance(witness, dict) and set(witness) == {"pivots", "basis", "coefficients"},
            "splitting keys")
    pivots, basis, coefficients = (witness[k] for k in ("pivots", "basis", "coefficients"))
    require(isinstance(pivots, list), "pivot list")
    rank = len(pivots)
    require(rank <= min(m, n), "rank bound")
    require(all(type(p) is int and 0 <= p < n for p in pivots), "pivot range")
    require(pivots == sorted(set(pivots)), "pivot uniqueness")
    require(isinstance(basis, list) and isinstance(coefficients, list)
            and len(basis) == len(coefficients) == rank, "splitting shape")
    eb = [dense_dyadic(row, n) for row in basis]
    cb = [sparse_dyadic(row, m) for row in coefficients]
    for i, ((erow, eden), (crow, cden)) in enumerate(zip(eb, cb)):
        for j, pivot in enumerate(pivots):
            require(erow[pivot] == eden*(i == j), "basis pivot identity")
        for j in range(n):
            product = sum(crow[k]*matrix[k][j] for k in range(m))
            require(product*eden == erow[j]*cden, "E=C A identity")
    common = max((den for _, den in eb), default=1)
    scaled = [[x*(common//den) for x in row] for row, den in eb]
    for row in matrix:
        for j in range(n):
            require(sum(row[pivots[k]]*scaled[k][j] for k in range(rank)) == common*row[j],
                    "A=A[:,J] E identity")
    return rank


def check_case_inventory(certificate):
    require(isinstance(certificate, dict) and set(certificate) == {"schema", "witnesses"},
            "certificate schema keys")
    require(certificate["schema"] == "e8-dyadic-row-splittings-v1", "certificate schema")
    witnesses = certificate["witnesses"]
    require(isinstance(witnesses, list) and len(witnesses) == 6595, "case count")
    counts, ranks, anchor_ranks = Counter(), Counter(), {}
    observed = 0
    for (key, matrix), item in zip(matrices(), witnesses, strict=True):
        require(isinstance(item, dict) and set(item) == {"case", "pivots", "basis", "coefficients"},
                "case record shape")
        require(item["case"] == list(key), "case domain/order mismatch")
        rank = check_splitting(matrix, {k: v for k, v in item.items() if k != "case"})
        name = key[0]
        if name == "A3":
            require(rank in (2, 3), "triple anchor rank")
            anchor_ranks[key[1:]] = rank
        elif name == "S3":
            require(rank == 8-anchor_ranks[key[1:]], "triple complement rank")
        else:
            require(rank == {"S1": 7, "A2": 2, "S2": 6, "W2": 3}[name], "claimed rank")
        counts[name] += 1
        ranks[(name, rank)] += 1
        observed += 1
    require(dict(counts) == EXPECTED_COUNTS, "family inventory")
    require(Counter(anchor_ranks.values()) == {2: 28, 3: 1512}, "dependent triple coverage")
    return {"cases": observed, "family_counts": dict(counts),
            "rank_counts": {f"{k[0]}:{k[1]}": v for k, v in sorted(ranks.items())}}


def check_geometry():
    signed, lines, f, orthogonal, neighbors, directions = fixed_geometry()
    require(len(signed) == len(set(signed)) == 240 and len(lines) == 120, "lattice inventory")
    require(set(signed) == set(lines) | {tuple(-x for x in r) for r in lines}, "signed partition")
    require(all(dot(r, r) == 8 for r in signed), "root norms")
    require(all(dot(a, b) in (-8, -4, 0, 4, 8) for a in signed for b in signed), "root pairings")
    require(len(orthogonal[f]) == 63 and len(neighbors) == 56 and len(directions) == 28,
            "anchor incidence inventory")
    fibers = Counter(projection(lines[i], lines[f]) for i in neighbors)
    require(set(fibers) == set(directions) and set(fibers.values()) == {2}, "projection fibers")
    require(all(dot(row, lines[f]) == 0 for row in directions), "projection orthogonality")
    return {"signed_roots": len(signed), "lines": len(lines), "neighbors": len(neighbors),
            "projected_directions": len(directions)}


def check_transport(matrix, anchor, target, signed_set):
    require(len(matrix) == 8 and all(len(row) == 8 for row in matrix), "transport shape")
    require(all(type(x) is int for row in matrix for x in row), "integer transport")
    for i in range(8):
        for j in range(8):
            require(sum(matrix[k][i]*matrix[k][j] for k in range(8)) == 16*(i == j),
                    "transport isometry")
    require(tuple(dot(row, anchor) for row in matrix) == tuple(4*x for x in target),
            "anchor transport")
    images = set()
    for root in signed_set:
        image = tuple(dot(row, root) for row in matrix)
        require(all(x % 4 == 0 for x in image), "transport integrality")
        quotient = tuple(x//4 for x in image)
        require(quotient in signed_set, "transport root membership")
        images.add(quotient)
    require(images == signed_set, "transport permutation")


def check_all_transports():
    signed, lines, f, _, _, _ = fixed_geometry()
    for target in lines:
        check_transport(transport_numerator(target), lines[f], target, set(signed))
    return {"explicit_anchor_transports": len(lines), "signed_root_images": len(lines)*len(signed)}


def characteristic_three_boundary():
    """A singular anchor Gram matrix is not a failure of the complement claim."""
    f = (2, 2, 0, 0, 0, 0, 0, 0)
    u = (2, 0, 2, 0, 0, 0, 0, 0)
    # Columns 1 and 2 give a unit minor, but the Gram determinant is 48.
    require(f[1]*u[2]-f[2]*u[1] == 4, "characteristic-three independent anchors")
    gram = [[dot(f, f), dot(f, u)], [dot(u, f), dot(u, u)]]
    require(gram == [[8, 4], [4, 8]], "characteristic-three Gram fixture")
    require((gram[0][0]*gram[1][1]-gram[0][1]*gram[1][0]) % 3 == 0,
            "characteristic-three Gram degeneracy")
    radical = tuple((a+b) % 3 for a, b in zip(f, u))
    require(any(radical) and dot(radical, f) % 3 == dot(radical, u) % 3 == 0,
            "characteristic-three radical")
    return {"anchor_gram_determinant": 48, "anchor_unit_minor": 4,
            "nonzero_radical_mod3": list(radical),
            "scope": "The ambient-complement proof must not invert the anchor Gram matrix."}


def expect_rejection(action, label):
    try:
        action()
    except (ValueError, TypeError, KeyError):
        return label
    raise ValueError("negative control accepted: " + label)


def controls(certificate):
    rejected = []
    positive = {"pivots": [0], "basis": [[[1, 0], [0, 0]]], "coefficients": [[[0, 1, 1]]]}
    require(check_splitting(((2, 0),), positive) == 1, "dyadic positive control")
    for odd in (3, 5):
        rejected.append(expect_rejection(lambda odd=odd: check_splitting(((odd, 0),), positive),
                                         f"odd_torsion_{odd}"))
    one = deepcopy(positive)
    one["coefficients"][0][0][1] = -1
    rejected.append(expect_rejection(lambda: check_splitting(((2, 0),), one), "wrong_left_inverse"))
    one = deepcopy(positive)
    one["basis"][0][0][0] = -1
    rejected.append(expect_rejection(lambda: check_splitting(((2, 0),), one), "wrong_pivot_identity"))
    rejected.append(expect_rejection(lambda: check_splitting(((2, 1),), positive), "missed_row_component"))
    rejected.append(expect_rejection(lambda: check_splitting(((0, 0),), positive), "singular_input"))
    rejected.append(expect_rejection(lambda: dense_dyadic([[True, 0]], 1), "boolean_coefficient"))
    rejected.append(expect_rejection(lambda: dense_dyadic([[2, 1]], 1), "unreduced_dyadic"))
    rejected.append(expect_rejection(lambda: sparse_dyadic([[0, 1, 0], [0, 1, 0]], 1),
                                     "duplicate_source_index"))
    rejected.append(expect_rejection(lambda: parse('{"a":0,"a":1}'), "duplicate_json_key"))
    missing = {**certificate, "witnesses": certificate["witnesses"][:-1]}
    rejected.append(expect_rejection(lambda: check_case_inventory(missing), "missing_case"))
    reordered = {**certificate, "witnesses": list(certificate["witnesses"])}
    reordered["witnesses"][0], reordered["witnesses"][1] = reordered["witnesses"][1], reordered["witnesses"][0]
    rejected.append(expect_rejection(lambda: check_case_inventory(reordered), "wrong_case_binding"))
    signed, lines, f, _, _, _ = fixed_geometry()
    bad_transport = transport_numerator(lines[0])
    bad_transport[0][0] += 1
    rejected.append(expect_rejection(lambda: check_transport(bad_transport, lines[f], lines[0], set(signed)),
                                     "damaged_transport"))
    require(all(x % 2 == 0 for x in lines[f]), "characteristic-two exclusion control")
    return {"rejected": rejected, "positive_controls": ["dyadic_left_inverse", "characteristic_two_excluded"]}


def source_bindings():
    source = parse((PACKAGE / "SOURCES.json").read_bytes())
    root, result = PACKAGE.parents[1], {}
    for item in source["files"]:
        if item["usage"] == "input":
            raw = (root / item["path"]).read_bytes()
            require(sha256(raw).hexdigest() == item["sha256"], "source bytes changed: " + item["path"])
            result[item["path"]] = item["sha256"]
    reference = parse((PACKAGE / "predecessor" / "SOURCE.json").read_bytes())
    raw = (PACKAGE / "predecessor" / "PR6198-PROOF.md").read_bytes()
    require(sha256(raw).hexdigest() == reference["sha256"], "predecessor proof bytes changed")
    require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == reference["git_blob"],
            "predecessor Git blob mismatch")
    result["PR6198-PROOF.md"] = reference["sha256"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=PACKAGE / "CERTIFICATE.json.gz")
    args = parser.parse_args()
    sources = source_bindings()
    with gzip.open(args.certificate, "rb") as handle:
        payload = handle.read(8_000_001)
    require(len(payload) <= 8_000_000, "certificate payload bound")
    certificate = parse(payload)
    result = {"status": "PASS_E8_DYADIC_SPAN_AUDIT", "certificate_payload_sha256": sha256(payload).hexdigest(),
              "geometry": check_geometry(), "splittings": check_case_inventory(certificate),
              "transports": check_all_transports(), "controls": controls(certificate), "source_sha256": sources,
              "characteristic_three_boundary": characteristic_three_boundary(),
              "scope": "Independent finite dyadic certificates plus the written all-odd-field argument; no new kappa."}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
