# SPDX-License-Identifier: Apache-2.0
"""Closed-form fixed-field compiler, retaining the exact source GL ordering.

JoyboyBrian with OpenAI Codex assistance. Constraints and mixed-radix methods
are executed unchanged from Jose Manuel's retained PR2501/PR2569 lineage.
This is offline finite compilation, not a new physical tape tariff.
"""
from dataclasses import dataclass
from math import gcd, prod, isqrt
from source_binding import OLD, need

PRIME = 213 * (1 << 80) + 1


@dataclass(frozen=True)
class PowerTwoCertificate:
    q: int
    exponent: int
    witness: int

    def check(self):
        q, k, a = self.q, self.exponent, self.witness
        need(type(q) is type(k) is type(a) is int and q >= 3 and 1 <= k < q.bit_length(),
             "typed odd-prime certificate")
        factor = 1 << k
        need((q - 1) % factor == 0 and ((q - 1) // factor) % 2 == 1 and factor * factor > q,
             "complete large power-of-two factor")
        need(1 < a < q and pow(a, q - 1, q) == 1 and
             gcd(pow(a, (q - 1) // 2, q) - 1, q) == 1, "prime order witness")
        return q


SELECTED_CERTIFICATE = PowerTwoCertificate(PRIME, 80, 7)


def admit_prime(q, certificate=None):
    need(type(q) is int and q >= 3, "odd prime")
    if certificate is not None:
        need(type(certificate) is PowerTwoCertificate and certificate.check() == q,
             "typed certificate binds requested q")
    elif q == PRIME:
        SELECTED_CERTIFICATE.check()
    else:
        # Bounded reference-domain admission, never a selected-field trial loop.
        need(q <= 257 and all(q % a for a in range(2, isqrt(q) + 1)),
             "larger primes require a power-two certificate")


def prefix_count(constraints, reduced, total, value):
    """Number of admissible completions with next symbol strictly below value."""
    if constraints.inconsistent:
        return value * total
    _row, rhs, pivot = reduced
    exponent = len(constraints.rows) - len(constraints.basis)
    if pivot is not None:
        return value * (total - constraints.q ** (exponent - 1))
    return value * total - (constraints.q ** exponent if value > rhs else 0)


def select_symbol(constraints, reduced, total, rank):
    """Inverse prefix selection; at most one exceptional symbol, no q-loop."""
    if constraints.inconsistent:
        return divmod(rank, total)
    _row, rhs, pivot = reduced
    exponent = len(constraints.rows) - len(constraints.basis)
    if pivot is not None:
        count = total - constraints.q ** (exponent - 1)
        need(count > 0, "nonempty independent completion")
        return divmod(rank, count)
    excluded = constraints.q ** exponent
    need(excluded <= total, "source independent-row completion bound")
    # The exceptional interval ends here, including its possible zero length.
    if rank >= (rhs + 1) * total - excluded:
        rank += excluded
    return divmod(rank, total)


class LowCodes(OLD.LowCodes):
    """Same GL labels and inherited public methods; direct row rank/select."""
    def __init__(self, q, dimension, requests=1, certificate=None):
        admit_prime(q, certificate)
        need(type(dimension) is int and 1 <= dimension <= 64 and
             type(requests) is int and requests > 0, "fixed source vocabulary")
        self.q, self.dimension, self.requests = q, dimension, requests
        self.radices = tuple(q ** dimension - q ** k for k in range(dimension))
        self.size = prod(self.radices)
        self.limit = 2 * requests * self.size
        self.bits = max(1, (self.limit - 1).bit_length())

    def vector_rank(self, rows, vector):
        constraints, rank = OLD.Constraints(rows, self.q), 0
        for column, value in enumerate(vector):
            reduced = constraints.next(column)
            total = self.q ** (self.dimension - column - 1)
            rank += prefix_count(constraints, reduced, total, value)
            constraints.choose(reduced, value)
        need(constraints.inconsistent, "independent low row")
        return rank

    def vector_unrank(self, rows, rank):
        constraints, vector = OLD.Constraints(rows, self.q), []
        for column in range(self.dimension):
            reduced = constraints.next(column)
            total = self.q ** (self.dimension - column - 1)
            value, rank = select_symbol(constraints, reduced, total, rank)
            need(0 <= value < self.q, "low-row rank range")
            vector.append(value)
            constraints.choose(reduced, value)
        need(rank == 0 and constraints.inconsistent, "complete independent low row")
        return tuple(vector)
