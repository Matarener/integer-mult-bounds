#!/usr/bin/env python3
"""Exact finite corroboration of the written characteristic-three obstruction."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows, modulus):
    require(modulus in (3, 5), "unsupported modulus")
    require(len(rows) <= 36, "row capacity")
    require(all(len(row) == 6 for row in rows), "six coordinates required")
    work = [[value % modulus for value in row] for row in rows]
    pivot = 0
    for column in range(6):
        candidates = [i for i in range(pivot, len(work)) if work[i][column]]
        if not candidates:
            continue
        chosen = candidates[0]
        work[pivot], work[chosen] = work[chosen], work[pivot]
        inverse = pow(work[pivot][column], -1, modulus)
        work[pivot] = [(value * inverse) % modulus for value in work[pivot]]
        for i in range(len(work)):
            if i != pivot:
                factor = work[i][column]
                work[i] = [(x - factor * y) % modulus
                           for x, y in zip(work[i], work[pivot], strict=True)]
        pivot += 1
    return pivot


def group_data():
    permutations = tuple(itertools.permutations(range(3)))
    table = tuple(tuple(permutations.index(tuple(p[q[i]] for i in range(3)))
                        for q in permutations) for p in permutations)
    signs = tuple((-1) ** sum(p[i] > p[j] for i in range(3)
                             for j in range(i + 1, 3)) for p in permutations)
    basis = tuple(tuple(int(i == j) for j in range(6)) for i in range(6))
    return permutations, table, signs, basis


def multiply(left, right, table):
    output = [0] * 6
    for i in range(6):
        for j in range(6):
            output[table[i][j]] += left[i] * right[j]
    return tuple(output)


def characters(vector, signs, modulus):
    return (sum(vector) % modulus,
            sum(x * sign for x, sign in zip(vector, signs, strict=True)) % modulus)


def radical_basis(signs):
    vectors = []
    for sign in (1, -1):
        indices = [i for i in range(6) if signs[i] == sign]
        for i in indices[1:]:
            vector = [0] * 6
            vector[i], vector[indices[0]] = 1, -1
            vectors.append(tuple(vector))
    return tuple(vectors)


def check_radical(table, signs, basis, radical, modulus):
    require(rank(radical, modulus) == 4, "radical dimension")
    require(all(characters(v, signs, modulus) == (0, 0) for v in radical),
            "radical lies in quotient kernel")
    for u in basis:
        for v in basis:
            image = characters(multiply(u, v, table), signs, modulus)
            a, b = characters(u, signs, modulus), characters(v, signs, modulus)
            require(image == tuple(x * y % modulus for x, y in zip(a, b, strict=True)),
                    "quotient multiplicativity")
    for u in basis:
        for v in radical:
            for product in (multiply(u, v, table), multiply(v, u, table)):
                require(rank((*radical, product), modulus) == 4, "two-sided ideal")
    products = tuple(multiply(u, v, table) for u in radical for v in radical)
    require(rank(products, modulus) == 2, "radical-square dimension")
    for uv in products:
        for w in radical:
            require(all(x % modulus == 0 for x in multiply(uv, w, table)),
                    "radical cube must vanish")
    return {"radical_dimension": 4, "radical_square_dimension": 2,
            "radical_cube_dimension": 0, "quotient_dimension": 2,
            "basis_products": 36, "radical_pair_products": len(products),
            "radical_triple_products": len(products) * len(radical)}


def check_units(table, signs, basis):
    units = 0
    for vector in itertools.product(range(3), repeat=6):
        columns = tuple(multiply(vector, e, table) for e in basis)
        invertible = rank(tuple(zip(*columns, strict=True)), 3) == 6
        predicted = all(characters(vector, signs, 3))
        require(invertible == predicted, "unit criterion")
        units += invertible
    require(units == (3 - 1) ** 2 * 3 ** 4, "unit count")
    return {"elements_enumerated": 3 ** 6, "units": units}


def f9_multiply(x, y):
    a, b = x
    c, d = y
    return ((a * c - b * d) % 3, (a * d + b * c) % 3)


def check_residue_maps(half, imaginary, zeta):
    require(tuple(2 * x % 3 for x in half) == (1, 0), "half relation")
    require(f9_multiply(imaginary, imaginary) == (2, 0), "Gaussian relation")
    square = f9_multiply(zeta, zeta)
    require(f9_multiply(square, square) == (2, 0), "eighth-root relation")
    require(zeta != (0, 0), "unit eighth root")


def check_tensor_count(dimension, quotient_dimension, blocks, products):
    require(dimension == 6 * blocks, "direct-product dimension")
    require(quotient_dimension == 2 * blocks, "split quotient dimension")
    # The inequality itself is the cited Alder--Strassen theorem, not a
    # computer-proved tensor-rank theorem. PROOF.md supplies its hypotheses.
    require(products >= 2 * dimension - quotient_dimension,
            "Alder--Strassen product floor")


def rejected_controls(table, signs, basis, radical):
    controls = 0
    try:
        check_radical(table, signs, basis, radical[:-1], 3)
    except ValueError as error:
        require(str(error) == "radical dimension", "wrong control failure")
        controls += 1
    else:
        raise ValueError("missing radical direction accepted")
    try:
        check_radical(table, signs, basis, radical, 5)
    except ValueError as error:
        require(str(error) in ("radical-square dimension", "radical cube must vanish"),
                "wrong characteristic control failure")
        controls += 1
    else:
        raise ValueError("characteristic-five radical accepted")
    for half, imaginary, zeta in (
            ((1, 0), (0, 1), (1, 1)),
            ((2, 0), (1, 0), (1, 1)),
            ((2, 0), (0, 1), (0, 1))):
        try:
            check_residue_maps(half, imaginary, zeta)
        except ValueError:
            controls += 1
        else:
            raise ValueError("false residue map accepted")
    for blocks, quotient, products in ((1, 2, 9), (8, 16, 79), (1, 3, 9)):
        try:
            check_tensor_count(6 * blocks, quotient, blocks, products)
        except ValueError:
            controls += 1
        else:
            raise ValueError("false product floor accepted")
    return controls


def evidence():
    permutations, table, signs, basis = group_data()
    require(len(set(permutations)) == 6, "group size")
    # An independent normal-form product: a^i s^e a^j s^f.
    a, s = (1, 2, 0), (1, 0, 2)
    normal = []
    for i in range(3):
        power = (0, 1, 2)
        for _ in range(i):
            power = tuple(a[power[k]] for k in range(3))
        for e in range(2):
            normal.append(tuple(power[s[k]] for k in range(3)) if e else power)
    require(len(set(normal)) == 6, "normal-form basis")
    for i, p in enumerate(normal):
        for j, q in enumerate(normal):
            target = 2 * ((i // 2 + (-1) ** (i % 2) * (j // 2)) % 3)
            target += (i % 2 + j % 2) % 2
            require(permutations[table[permutations.index(p)][permutations.index(q)]]
                    == normal[target], "independent group multiplication")
    radical = radical_basis(signs)
    result = check_radical(table, signs, basis, radical, 3)
    result.update(check_units(table, signs, basis))
    # The two quotient images of e and s have determinant -2, a unit mod 3.
    require(characters(basis[0], signs, 3) == (1, 1), "identity character")
    require(characters(basis[permutations.index(s)], signs, 3) == (1, 2),
            "surjective split quotient")
    check_residue_maps((2, 0), (0, 1), (1, 1))
    for blocks in range(1, 9):
        check_tensor_count(6 * blocks, 2 * blocks, blocks, 10 * blocks)
    result["rejected_controls"] = rejected_controls(table, signs, basis, radical)
    result["radical_basis"] = radical
    result["lower_bound_per_block_using_cited_theorem"] = 10
    result["rational_predecessor_products_per_block"] = 9
    result["status"] = "PASS_S3_THREE_LOCAL_OBSTRUCTION"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    if args.receipt is not None:
        receipt = args.receipt.resolve()
        require(args.receipt.is_absolute(), "receipt path must be absolute")
        require(not receipt.is_relative_to(package.parent.parent),
                "receipt must stay outside the checkout")
    result = evidence()
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in files}
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        args.receipt.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
