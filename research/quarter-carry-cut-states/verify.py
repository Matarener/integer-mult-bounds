#!/usr/bin/env python3
"""Exact rational-carry cut classes, produced by Nick Petalas. Apache-2.0."""

from dataclasses import dataclass
import hashlib
import json
from math import gcd
from pathlib import Path


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Problem:
    q: int
    high: int
    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        values = (self.q, self.high, self.numerator, self.denominator)
        need(all(type(v) is int for v in values), "integer parameters required")
        need(all(v.bit_length() <= 4096 for v in values), "parameter bit limit")
        need(self.q >= 2 and self.high >= 1, "invalid modulus")
        need(self.denominator >= 1, "positive denominator required")
        need(gcd(self.denominator, self.q * self.high) == 1, "denominator not a unit")


def parameters(p: Problem) -> tuple[int, int, int, int]:
    g = gcd(p.numerator, p.q)
    d = p.q // g
    e = p.high // gcd(p.numerator // g, p.high)
    return g, d, e, min(g, e)


def count(p: Problem) -> int:
    if p.high == 1:
        return 1
    _, d, _, m = parameters(p)
    return d * m


def encode(p: Problem, x: int) -> int:
    need(type(x) is int and 0 <= x < p.q, "source digit out of range")
    if p.high == 1:
        return 0
    _, d, e, m = parameters(p)
    return (x % d) * m + (x // d) % e


def representative(p: Problem, label: int) -> int:
    need(type(label) is int and 0 <= label < count(p), "label out of range")
    if p.high == 1:
        return 0
    _, d, _, m = parameters(p)
    return label // m + (label % m) * d


def integer_packet(p: Problem, x: int, y: int) -> int:
    need(0 <= x < p.q and 0 <= y < p.q, "digit out of range")
    t = (y + p.numerator * pow(p.denominator, -1, p.q) * x) % p.q
    n = p.numerator * x + p.denominator * (y - t)
    need(n % p.q == 0, "nonintegral carry")
    return n // p.q


def step_response(p: Problem, x: int, y: int) -> int:
    packet = integer_packet(p, x, y)
    return packet * pow(p.denominator, -1, p.high) % p.high


def full_modulus_response(p: Problem, x: int, y: int) -> int:
    modulus = p.q * p.high
    output = (y + p.numerator * x * pow(p.denominator, -1, modulus)) % modulus
    return output // p.q


def distinguish(p: Problem, x: int, other: int) -> int:
    need(p.high > 1 and encode(p, x) != encode(p, other), "equivalent sources")
    if full_modulus_response(p, x, 0) != full_modulus_response(p, other, 0):
        return 0
    inverse = pow(p.denominator, -1, p.q)
    r = p.numerator * x * inverse % p.q
    other_r = p.numerator * other * inverse % p.q
    need(r != other_r, "equal thresholds must have unequal constants")
    y = p.q - max(r, other_r)
    need(0 < y < p.q, "invalid threshold witness")
    need(full_modulus_response(p, x, y) != full_modulus_response(p, other, y),
         "threshold witness did not separate responses")
    return y


def check_problem(p: Problem, stats: dict[str, int], digest) -> None:
    need(p.q <= 257, "enumeration radix limit")
    signatures = []
    packets = set()
    labels = set()
    for x in range(p.q):
        label = encode(p, x)
        labels.add(label)
        rep = representative(p, label)
        need(0 <= rep < p.q, "invalid representative")
        row = []
        packet_row = []
        for y in range(p.q):
            value = full_modulus_response(p, x, y)
            need(value == step_response(p, x, y), "full-width oracle disagrees")
            need(value == full_modulus_response(p, rep, y), "encoding loses information")
            row.append(value)
            packet_row.append(integer_packet(p, x, y))
            stats["digit_pairs"] += 1
        signatures.append(tuple(row))
        packets.add(tuple(packet_row))
    need(len(set(signatures)) == count(p), "incorrect class count")
    need(labels == set(range(count(p))), "encoding is not onto")
    need(len(packets) == (1 if p.numerator == 0 else p.q), "packet count")
    digest.update(str((p, tuple(sorted(labels)), len(packets))).encode())
    stats["systems"] += 1


def complete_small_domain(stats: dict[str, int], digest) -> None:
    for q in range(2, 26):
        for high in range(1, 17):
            for numerator in range(-24, 25):
                for denominator in range(1, 9):
                    if gcd(denominator, q * high) != 1:
                        continue
                    check_problem(Problem(q, high, numerator, denominator), stats, digest)


def quarter_family(stats: dict[str, int], digest) -> None:
    for q in range(3, 66, 2):
        for width in range(1, 7):
            p = Problem(q, q ** (width - 1), 1, 4)
            need(count(p) == (1 if width == 1 else q), "quarter corollary")
            check_problem(p, stats, digest)
            stats["quarter_systems"] += 1
    p = Problem(257, 257, 1, 4)
    check_problem(p, stats, digest)
    codes = {integer_packet(p, x, y) for x in range(p.q) for y in range(p.q)}
    need(codes == set(range(-3, 5)), "quarter packet alphabet")
    need((count(p) - 1).bit_length() == 9, "quarter bit count")
    for x in range(p.q):
        for other in range(x):
            y = distinguish(p, x, other)
            need(full_modulus_response(p, x, y) != full_modulus_response(p, other, y),
                 "bad pair separator")
            stats["quarter_separators"] += 1


def nonunit_and_collapse_controls(stats: dict[str, int]) -> None:
    fixtures = [(9, 3, 9, 1, 3), (9, 9, 27, 4, 3), (12, 4, 24, 5, 2),
                (15, 3, 5, 2, 9), (8, 2, 8, 3, 2), (8, 1, 1, 3, 1),
                (9, 9, 0, 4, 1), (6, 5, -12, 7, 5)]
    for q, high, a, d, expected in fixtures:
        p = Problem(q, high, a, d)
        actual = len({tuple(full_modulus_response(p, x, y) for y in range(q))
                      for x in range(q)})
        need(actual == expected == count(p), "collapse fixture")
        stats["collapse_controls"] += 1


def rejection_controls(stats: dict[str, int]) -> None:
    invalid = [(1, 3, 1, 4), (3, 0, 1, 4), (3, 3, 1, 0),
               (3, 3, 1, 3), (3, 2, 1, 4), (True, 3, 1, 4),
               (3, 3, 1.0, 4), (3, 3, 1 << 4096, 4)]
    for args in invalid:
        try:
            Problem(*args)
        except ValueError:
            stats["invalid_inputs_rejected"] += 1
        else:
            raise ValueError("invalid input accepted")
    p = Problem(17, 17, 1, 4)
    for bad in (-1, p.q, True):
        try:
            encode(p, bad)
        except ValueError:
            stats["invalid_inputs_rejected"] += 1
        else:
            raise ValueError("invalid source accepted")
    for bad in (-1, count(p), True):
        try:
            representative(p, bad)
        except ValueError:
            stats["invalid_inputs_rejected"] += 1
        else:
            raise ValueError("invalid label accepted")


def semantic_controls(stats: dict[str, int]) -> None:
    p = Problem(17, 17, 1, 4)
    need(full_modulus_response(p, 0, 0) != full_modulus_response(p, 1, 0),
         "constant-code mutant survived")
    need(count(p) > 8, "final packet alphabet mistaken for cut states")
    need(full_modulus_response(p, 1, 16) != full_modulus_response(p, 0, 16),
         "stale-source mutant survived")
    collapsed = Problem(9, 3, 9, 1)
    need(count(collapsed) != collapsed.q, "nonunit no-collapse mutant survived")
    trivial = Problem(17, 1, 1, 4)
    need(count(trivial) != trivial.q, "Q=1 mutant survived")
    need(integer_packet(trivial, 1, 0) != integer_packet(trivial, 0, 0),
         "integer packet conflated with high correction")
    stats["semantic_controls"] += 6


def main() -> None:
    stats = dict.fromkeys(("systems", "digit_pairs", "quarter_systems",
                          "quarter_separators", "collapse_controls",
                          "invalid_inputs_rejected", "semantic_controls"), 0)
    digest = hashlib.sha256()
    complete_small_domain(stats, digest)
    quarter_family(stats, digest)
    nonunit_and_collapse_controls(stats)
    rejection_controls(stats)
    semantic_controls(stats)
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_QUARTER_CARRY_CUT_STATES", "coverage": stats,
                      "census_sha256": digest.hexdigest(), "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
