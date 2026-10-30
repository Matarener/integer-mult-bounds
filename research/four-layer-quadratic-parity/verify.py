"""Exact corroboration of the four-layer quadratic comparison; standard library."""

from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path


class VerificationError(RuntimeError):
    """An explicit mathematical or resource contract failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def coefficients(center: int) -> tuple[int, int, int]:
    """Coefficients of 3P after Boolean multilinearization, by support size."""
    if type(center) is not int or not 1 <= center <= 128:
        raise ValueError("center must be an integer from 1 through 128")
    sign = (-1) ** center
    return sign * (2 * center * center - 5), sign * (2 - 4 * center), sign * 4


def numerator(weight: int, center: int) -> int:
    return (-1) ** center * (2 * (weight - center) ** 2 - 5)


def layer_weights(dimension: int) -> tuple[int, ...]:
    if type(dimension) is not int or not 1 <= dimension <= 512:
        raise ValueError("dimension must be an integer from 1 through 512")
    return tuple(comb(dimension, t) * 3 ** (dimension - t)
                 for t in range(dimension + 1))


def check_agreement(center: int, offset: int = 5, divisor: int = 3) -> None:
    actual = tuple(t for t in range(4 * center + 1)
                   if (-1) ** center * (2 * (t - center) ** 2 - offset)
                   == divisor * (-1) ** t)
    expected = (center - 2, center - 1, center + 1, center + 2)
    require(actual == expected, "four-layer equality set changed")


def row_distribution(dimension: int) -> tuple[int, ...]:
    """Count by row weight and overlap, independently of the four-symbol formula."""
    counts = [0] * (dimension + 1)
    for row_weight in range(dimension + 1):
        rows = comb(dimension, row_weight)
        for overlap in range(row_weight + 1):
            counts[overlap] += rows * comb(row_weight, overlap) * 2 ** (
                dimension - row_weight)
    return tuple(counts)


def check_comparison() -> dict[str, object]:
    for center in range(4, 129):
        dimension = 4 * center
        weights = layer_weights(dimension)
        check_agreement(center)
        require(sum(weights) == 4 ** dimension, "pair count does not close")
        triples = tuple(sum(weights[s:s + 3]) for s in range(dimension - 1))
        best = sum(weights[center - 1:center + 2])
        require(triples.index(max(triples)) == center - 1, "wrong best triple")
        require(triples.count(best) == 1, "best triple is not unique")
        four = sum(weights[t] for t in (center - 2, center - 1, center + 1, center + 2))
        delta = four - best
        polynomial = (27 * center ** 4 - 36 * center ** 3 - 171 * center ** 2
                      - 128 * center - 12)
        denominator = 3 * (center + 1) * (center + 2) * (3 * center + 1) * (3 * center + 2)
        require(delta * denominator == weights[center] * polynomial,
                "closed gain formula changed")
        shift = center - 4
        positive = 27 * shift ** 4 + 396 * shift ** 3 + 1989 * shift ** 2 + 3688 * shift + 1348
        require(polynomial == positive and positive > 0, "positive shift failed")
    weights = layer_weights(16)
    four = sum(weights[t] for t in (2, 3, 5, 6))
    best = sum(weights[3:6])
    require((four, best, four - best) == (2713419648, 2633821596, 79598052),
            "dimension-16 instance changed")
    return {"dimensions": 125, "n16_rank": 137, "n16_four": four,
            "n16_best_consecutive": best, "n16_gain": four - best}


def check_counts() -> int:
    cases = 0
    for dimension in (4, 8, 12, 16, 20, 32, 40, 64):
        require(row_distribution(dimension) == layer_weights(dimension),
                "row enumeration disagrees with pair-layer formula")
        cases += 1
    for dimension in (4, 8):
        counts = [0] * (dimension + 1)
        for x in range(1 << dimension):
            for y in range(1 << dimension):
                counts[(x & y).bit_count()] += 1
        require(tuple(counts) == layer_weights(dimension), "dense pair count failed")
        cases += 1
    return cases


def features(dimension: int) -> tuple[int, ...]:
    singles = tuple(1 << i for i in range(dimension))
    return (0,) + singles + tuple(a | b for a, b in combinations(singles, 2))


def factor_value(x: int, y: int, masks: tuple[int, ...], coeff: tuple[int, int, int]) -> int:
    return sum(coeff[mask.bit_count()] for mask in masks if (x & y) & mask == mask)


def check_factorization(coeff: tuple[int, int, int], center: int) -> int:
    entries = 0
    for dimension in range(1, 7):
        masks = features(dimension)
        for x in range(1 << dimension):
            for y in range(1 << dimension):
                require(factor_value(x, y, masks, coeff) == numerator((x & y).bit_count(), center),
                        "rank factorization disagrees with the literal polynomial")
                entries += 1
    return entries


def check_feature_rank() -> int:
    cases = 0
    for dimension in range(1, 9):
        masks = features(dimension)
        require(len(masks) == 1 + dimension + comb(dimension, 2), "feature count failed")
        for row, source in enumerate(masks):
            for column, target in enumerate(masks):
                zeta = int(source & target == target)
                require(not zeta or column <= row, "feature minor is not triangular")
                inverse_product = sum(
                    (-1) ** (middle.bit_count() - target.bit_count())
                    for middle in masks
                    if source & middle == middle and middle & target == target)
                require(inverse_product == int(row == column), "feature inverse failed")
        for center in (4, 5):
            require(all(coefficients(center)), "a feature coefficient vanished")
        cases += 1
    return cases


def expect_rejection(function, *arguments) -> None:
    try:
        function(*arguments)
    except (VerificationError, ValueError):
        return
    raise VerificationError("a deliberate mutation was accepted")


def check_controls() -> int:
    for offset, divisor in ((4, 3), (6, 3), (5, 2), (5, 4)):
        expect_rejection(check_agreement, 4, offset, divisor)
    for coeff in ((26, -14, 4), (28, -13, 4), (27, -14, 2)):
        expect_rejection(check_factorization, coeff, 4)
    for invalid in (0, -1, 129, True):
        expect_rejection(coefficients, invalid)
    for invalid in (0, -1, 513, True):
        expect_rejection(layer_weights, invalid)
    for center in (2, 3):
        weights = layer_weights(4 * center)
        four = sum(weights[t] for t in (center - 2, center - 1, center + 1, center + 2))
        require(four < max(sum(weights[s:s + 3]) for s in range(4 * center - 1)),
                "excluded small-dimension comparison changed")
    weights = layer_weights(40)
    four = sum(weights[t] for t in (8, 9, 11, 12))
    require(four < sum(weights[::2]), "constant-rank limitation control failed")
    return 18


def main() -> None:
    result = check_comparison()
    result["count_cases"] = check_counts()
    result["factor_entries"] = sum(check_factorization(coefficients(m), m) for m in (4, 5))
    result["feature_rank_cases"] = check_feature_rank()
    result["controls"] = check_controls()
    package = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {name: sha256((package / name).read_bytes()).hexdigest()
                               for name in names}
    result["claim_type"] = "scoped proof with exact finite corroboration"
    print(json.dumps(result, sort_keys=True))
    print("PASS_FOUR_LAYER_QUADRATIC_PARITY")


if __name__ == "__main__":
    main()
