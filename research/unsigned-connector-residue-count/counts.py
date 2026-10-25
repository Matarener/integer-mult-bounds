"""Exact finite corroboration of the all-characteristic counting theorem.

The theorem has no upper characteristic limit. Executable checks deliberately
accept only 2 <= m <= 32, bounding every loop and the dynamic-programming table.
"""

from math import comb, gcd

MAX_MODULUS = 32


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_modulus(modulus: int) -> None:
    require(type(modulus) is int and 2 <= modulus <= MAX_MODULUS,
            "characteristic must be an integer between 2 and 32")


def divisors(number: int) -> tuple[int, ...]:
    require(type(number) is int and 1 <= number <= MAX_MODULUS,
            "divisor input outside finite verification domain")
    return tuple(d for d in range(1, number + 1) if number % d == 0)


def mobius(number: int) -> int:
    require(type(number) is int and 1 <= number <= MAX_MODULUS,
            "Mobius input outside finite verification domain")
    remaining, sign = number, 1
    for prime in range(2, number + 1):
        if remaining % prime == 0:
            remaining //= prime
            sign = -sign
            if remaining % prime == 0:
                return 0
    require(remaining == 1, "factorization did not finish")
    return sign


def ramanujan(order: int, coefficient: int) -> int:
    require(type(order) is int and 1 <= order <= MAX_MODULUS,
            "root order outside finite verification domain")
    require(type(coefficient) is int and 0 <= coefficient < MAX_MODULUS,
            "coefficient outside finite verification domain")
    return sum(e * mobius(order // e) for e in divisors(gcd(order, coefficient)))


def formula_counts(modulus: int) -> tuple[int, ...]:
    check_modulus(modulus)
    counts = []
    for coefficient in range(modulus):
        numerator = sum(ramanujan(d, coefficient) * comb(2 * modulus // d, modulus // d)
                        for d in divisors(modulus))
        require(numerator >= 0 and numerator % modulus == 0,
                "divisor formula did not produce a nonnegative integer")
        counts.append(numerator // modulus)
    require(sum(counts) == comb(2 * modulus, modulus), "formula mass mismatch")
    return tuple(counts)


def chronological_counts(modulus: int) -> tuple[int, ...]:
    """Append actual A/B events, retaining source count and AB coefficient."""
    check_modulus(modulus)
    table = [[[0] * modulus for _ in range(modulus + 1)]
             for _ in range(modulus + 1)]
    table[0][0][0] = 1
    for sources in range(modulus + 1):
        for readouts in range(modulus + 1):
            for residue in range(modulus):
                count = table[sources][readouts][residue]
                if sources < modulus:
                    table[sources + 1][readouts][residue] += count
                if readouts < modulus:
                    new_residue = (residue + sources) % modulus
                    table[sources][readouts + 1][new_residue] += count
    result = tuple(table[modulus][modulus])
    require(sum(result) == comb(2 * modulus, modulus), "chronological mass mismatch")
    return result


def signature(word: str, modulus: int) -> tuple[int, int, int]:
    """Return Bx in z, Az_initial in y, and ABx in y, modulo m."""
    check_modulus(modulus)
    require(type(word) is str and len(word) <= 2 * MAX_MODULUS,
            "word exceeds the finite replay bound")
    source, dirt, product = 0, 0, 0
    for event in word:
        require(event in "AB", "unknown connector event")
        if event == "B":
            source = (source + 1) % modulus
        else:
            dirt = (dirt + 1) % modulus
            product = (product + source) % modulus
    return source, dirt, product


def witness(modulus: int, coefficient: int) -> str:
    check_modulus(modulus)
    require(type(coefficient) is int and 0 < coefficient < modulus,
            "nonzero coefficient required")
    word = "B" * coefficient + "A" + "B" * (modulus - coefficient)
    word += "A" * (modulus - 1)
    require(signature(word, modulus) == (0, 0, coefficient), "witness action mismatch")
    return word
