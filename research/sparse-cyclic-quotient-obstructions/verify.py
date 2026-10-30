#!/usr/bin/env python3
"""Read-only exact corroboration of the sparse cyclic quotient proof."""

from hashlib import sha256
from itertools import combinations, product
import json
from math import gcd, lcm
from pathlib import Path
import sys


SUPPORT = ((0, 0), (1, 0), (0, 1), (1, 1), (2, 2))
PACKAGE_FILES = (
    "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def least_nondivisor(value: int) -> int:
    """The finite range includes value+1, which cannot divide positive value."""
    for modulus in range(2, value + 2):
        if value % modulus:
            return modulus
    raise ValueError("positive integer has no nondivisor")


def prime_power(value: int) -> bool:
    for prime in range(2, value + 1):
        if value % prime == 0:
            remainder = value
            for _ in range(value.bit_length()):
                if remainder % prime:
                    break
                remainder //= prime
            return remainder == 1
    raise ValueError("prime-power test requires value >= 2")


def images(support: tuple, weights: tuple, modulus: int) -> tuple:
    return tuple(sum(a * b for a, b in zip(point, weights)) % modulus
                 for point in support)


def require_injection(support: tuple, weights: tuple, modulus: int) -> tuple:
    residues = images(support, weights, modulus)
    need(len(set(residues)) == len(support), "cyclic projection aliases support")
    return residues


def scalar_checks() -> dict:
    largest_minimum = 0
    for height in range(1, 4097):
        minimum = least_nondivisor(height)
        need(prime_power(minimum), "minimum is not a prime power")
        largest_minimum = max(largest_minimum, minimum)
        running_lcm = 1
        for modulus in range(2, height + 2):
            running_lcm = lcm(running_lcm, modulus)
            if running_lcm > height:
                need(modulus == largest_minimum, "minimax LCM formula failed")
                break
        else:
            raise ValueError("LCM never exceeded height")
    realizations = 0
    for minimum in range(2, 65):
        if prime_power(minimum):
            value = lcm(*range(1, minimum))
            need(value % minimum != 0, "prime-power realization aliases")
            need(all(value % q == 0 for q in range(2, minimum)),
                 "realization has smaller faithful modulus")
            realizations += 1
    return {"scalar_heights": 4096, "prime_power_realizations": realizations,
            "largest_minimum_through_4096": largest_minimum}


def vector_checks() -> dict:
    cases = 0
    projections = 0
    for delta in product(range(-6, 7), repeat=2):
        if delta == (0, 0):
            continue
        content = gcd(*delta)
        for modulus in range(2, 9):
            separated = False
            for weights in product(range(modulus), repeat=2):
                projections += 1
                if images(((0, 0), delta), weights, modulus)[1] != 0:
                    separated = True
            need(separated == (content % modulus != 0), "content criterion failed")
            cases += 1
    return {"vector_modulus_cases": cases, "vector_projections": projections}


def polynomial_image(mask: int, residues: tuple) -> int:
    coefficients = 0
    for index, residue in enumerate(residues):
        if mask & (1 << index):
            coefficients ^= 1 << residue
    return coefficients


def literal_column(mask: int, weights: tuple, modulus: int, source: int) -> int:
    """Act directly on an address column using the integer exponents."""
    result = 0
    for index, (x, y) in enumerate(SUPPORT):
        if mask & (1 << index):
            destination = (source + x * weights[0] + y * weights[1]) % modulus
            result ^= 1 << destination
    return result


def rotated_column(coefficients: int, modulus: int, source: int) -> int:
    output = 0
    for address in range(modulus):
        if coefficients & (1 << address):
            output |= 1 << ((address + source) % modulus)
    return output


def fixture_checks() -> dict:
    successes = []
    columns = 0
    projections = 0
    for modulus in range(1, 7):
        successful = 0
        for weights in product(range(modulus), repeat=2):
            projections += 1
            residues = images(SUPPORT, weights, modulus)
            faithful = len(set(residues)) == len(SUPPORT)
            successful += faithful
            coefficient_images = set()
            for mask in range(1 << len(SUPPORT)):
                coefficients = polynomial_image(mask, residues)
                coefficient_images.add(coefficients)
                for source in range(modulus):
                    need(literal_column(mask, weights, modulus, source)
                         == rotated_column(coefficients, modulus, source),
                         "formal coefficients and regular action disagree")
                    columns += 1
            need((len(coefficient_images) == 32) == faithful,
                 "regular representation does not match support injection")
            if not faithful:
                left, right = next((i, j) for i, j in combinations(range(5), 2)
                                   if residues[i] == residues[j])
                need(polynomial_image((1 << left) | (1 << right), residues) == 0,
                     "alias does not give a nonzero formal kernel element")
        successes.append(successful)
    need(successes[:5] == [0] * 5 and successes[5] > 0, "minimum is not six")
    witness = require_injection(SUPPORT, (1, 3), 6)
    need(witness == (0, 1, 3, 4, 2), "wrong six-point residue witness")
    pair_checks = 0
    for left, right in combinations(SUPPORT, 2):
        delta = tuple(a - b for a, b in zip(left, right))
        need(gcd(*delta) % 5 != 0, "pair is unavoidably aliased modulo five")
        need(any(images((left, right), weights, 5)[0]
                 != images((left, right), weights, 5)[1]
                 for weights in product(range(5), repeat=2)),
             "pairwise separation failed")
        pair_checks += 1
    return {"fixture_minimum": 6, "box_modulus": 9,
            "successful_projections_by_modulus_1_to_6": successes,
            "fixture_projections": projections, "regular_action_columns": columns,
            "separable_pairs_modulo_5": pair_checks}


def rejection_controls() -> dict:
    rejected = 0
    for weights, modulus in (((1, 2), 5), ((1, 3), 5), ((1, 2), 6)):
        try:
            require_injection(SUPPORT, weights, modulus)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("unsafe fixture projection was accepted")
    try:
        require_injection(((0,), (2,)), (1,), 2)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("two-point torsion control was accepted")
    require_injection(SUPPORT[:4], (1, 2), 5)
    need(images(SUPPORT, (1, 2), 5)[-1] == 1,
         "omitted-target control did not expose the collision")
    need(least_nondivisor(6) == 4, "prime-only search misses optimum four")
    need(least_nondivisor(lcm(*range(1, 17))) == 17,
         "support-size-only modulus control failed")
    return {"rejected_projections": rejected, "semantic_controls": 3}


def main() -> None:
    need(len(sys.argv) == 1, "this read-only verifier accepts no arguments")
    receipt = {}
    for result in (scalar_checks(), vector_checks(), fixture_checks(),
                   rejection_controls()):
        receipt.update(result)
    root = Path(__file__).resolve().parent
    receipt["files_sha256"] = {
        name: sha256((root / name).read_bytes()).hexdigest() for name in PACKAGE_FILES
    }
    receipt["python"] = sys.version.split()[0]
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print("PASS_SPARSE_CYCLIC_QUOTIENT_OBSTRUCTIONS no_new_kappa")


if __name__ == "__main__":
    main()
