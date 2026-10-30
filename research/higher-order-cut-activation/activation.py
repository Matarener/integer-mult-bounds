"""Exact scalar fixtures for parallel helper-cut activation.

Produced by Nick Petalas. Apache-2.0.
"""

from math import gcd, prod

MAX_BANKS = 8
MAX_ENTRY = 10**9
MAX_SCALAR = 49


def checked_entries(values):
    """Bound the executable domain; the written theorem is not bounded by it."""
    entries = tuple(values)
    if not 1 <= len(entries) <= MAX_BANKS:
        raise ValueError("require between one and eight diagonal entries")
    if any(type(value) is not int or not 1 <= value <= MAX_ENTRY for value in entries):
        raise ValueError("require positive integer entries at most 10^9")
    return entries


def extended_gcd(a, b):
    if not 1 <= a <= MAX_ENTRY or not 1 <= b <= MAX_ENTRY:
        raise ValueError("extended gcd operands outside executable bounds")
    old_r, r, old_s, s, old_t, t = a, b, 1, 0, 0, 1
    for _ in range(64):
        if r == 0:
            assert old_s * a + old_t * b == old_r
            return old_r, old_s, old_t
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    raise ArithmeticError("Euclidean iteration guard exhausted")


def unit_witness(values):
    entries = checked_entries(values)
    coefficients = [1]
    divisor = entries[0]
    for value in entries[1:]:
        divisor, left, right = extended_gcd(divisor, value)
        coefficients = [left * entry for entry in coefficients] + [right]
    if divisor & (divisor - 1):
        raise ValueError("diagonal entries have a common odd divisor")
    assert sum(a * b for a, b in zip(coefficients, entries)) == divisor
    return tuple(coefficients), divisor


def omitted_prime_entries(primes):
    """The caller supplies distinct primes; the verifier tests that premise."""
    primes = checked_entries(primes)
    if len(primes) < 2 or len(set(primes)) != len(primes):
        raise ValueError("require at least two distinct primes")
    if any(value < 3 or value % 2 == 0 for value in primes):
        raise ValueError("require odd primes")
    total = prod(primes)
    entries = checked_entries(tuple(total // prime for prime in primes))
    assert all(gcd(entry, prime) == 1 for entry, prime in zip(entries, primes))
    return entries


def prefix(d):
    """Emit ordinary unit-coefficient ADDs, including coefficient repetition."""
    if type(d) is not int or not 1 <= d <= MAX_SCALAR:
        raise ValueError("scalar fixture requires 1 <= d <= 49")
    gates = [(0, 2, 1), (1, 2, 1), (2, 0, 1)]
    gates.extend((2, 1, 1) for _ in range(d - 1))
    assert len(gates) == d + 2
    return tuple(gates)


def inverse(gates):
    if len(gates) > MAX_BANKS * (MAX_SCALAR + 2):
        raise ValueError("gate list exceeds fixture bound")
    return tuple((target, source, -sign) for target, source, sign in reversed(gates))


def replay(gates, values):
    state = list(values)
    if not 1 <= len(state) <= 3 * MAX_BANKS or len(gates) > 2 * MAX_BANKS * (MAX_SCALAR + 2):
        raise ValueError("replay dimensions exceed fixture bounds")
    for target, source, sign in gates:
        if not (0 <= target < len(state) and 0 <= source < len(state)):
            raise ValueError("gate coordinate outside state")
        if target == source or sign not in (-1, 1):
            raise ValueError("require a signed ADD between distinct coordinates")
        state[target] += sign * state[source]
    return tuple(state)
