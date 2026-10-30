#!/usr/bin/env python3
"""Finite corroboration, exact causal words and SHA256-bound stdout receipt.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
from math import gcd, prod
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import activation


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = json.loads((package / "SOURCES.json").read_text())
    hashes = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((root / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source hash mismatch: " + row["path"])
            hashes[row["path"]] = digest
    for path in sorted(package.iterdir()):
        if path.is_file():
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def minor_capacity(entries):
    """Independent determinantal-divisor oracle, with no Smith implementation."""
    require(1 <= len(entries) <= 8, "minor dimension guard")
    answer = 0
    for size in range(1, len(entries) + 1):
        divisor = 0
        for chosen in itertools.combinations(entries, size):
            divisor = gcd(divisor, prod(chosen))
        if divisor & (divisor - 1):
            break
        answer = size
    return answer


def verify_families():
    prime_menu = (3, 5, 7, 11, 13, 17)
    for prime in prime_menu:
        require(all(prime % d for d in range(2, prime)), "nonprime menu member")
    families = proper_pools = witnesses = 0
    for size in range(2, 7):
        for primes in itertools.combinations(prime_menu, size):
            entries = activation.omitted_prime_entries(primes)
            require(minor_capacity(entries) == 1, "full pool capacity")
            coefficients, divisor = activation.unit_witness(entries)
            require(sum(a * b for a, b in zip(coefficients, entries)) == divisor == 1,
                    "unit witness identity")
            families += 1
            witnesses += 1
            for mask in range(1, (1 << size) - 1):
                selected = tuple(entries[i] for i in range(size) if mask >> i & 1)
                missing = next(i for i in range(size) if not mask >> i & 1)
                prime = primes[missing]
                require(all(value % prime == 0 for value in selected), "missing-prime obstruction")
                require(minor_capacity(selected) == 0, "proper pool capacity")
                proper_pools += 1
    return {"families": families, "proper_nonempty_pools": proper_pools,
            "attaining_unit_witnesses": witnesses}


def columns(gates, dimension):
    return tuple(activation.replay(gates, tuple(int(j == i) for j in range(dimension)))
                 for i in range(dimension))


def verify_scalar(d):
    gates = activation.prefix(d)
    backward = activation.inverse(gates)
    forward_columns = columns(gates, 3)
    expected = ((1, 0, 1), (0, 1, d - 1), (1, 1, d + 1))
    require(forward_columns == expected, "literal prefix differs from formula")
    require(columns(backward, 3) == ((2, 1, -1), (d - 1, d, 1 - d), (-1, -1, 1)),
            "literal suffix differs from inverse formula")
    for word in (gates + backward, backward + gates):
        require(columns(word, 3) == ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "dirty restoration")
    left, right = (1, -1, 0), (d - 1, -1, 0)
    require(tuple(sum(left[j] * col[j] for j in range(3)) for col in forward_columns) == left,
            "prefix-eligible row")
    require(activation.replay(backward, right) == right, "suffix-eligible column")
    require(sum(a * b for a, b in zip(left, right)) == d, "cut pairing")
    require(gcd(*left) == gcd(*right) == 1, "saturated rank-one basis")


def verify_nine_coordinate_word():
    entries = (15, 21, 35)
    gates = tuple((target + 3 * bank, source + 3 * bank, sign)
                  for bank, d in enumerate(entries)
                  for target, source, sign in activation.prefix(d))
    backward = activation.inverse(gates)
    require(len(gates + backward) == 154, "complete scalar ADD invoice")
    for word in (gates + backward, backward + gates):
        require(columns(word, 9) == tuple(tuple(int(i == j) for i in range(9)) for j in range(9)),
                "nine-coordinate dirty restoration")
    left = tuple(coefficient * entry for coefficient in (1, 1, -1) for entry in (1, -1, 0))
    right = tuple(entry for d in entries for entry in (d - 1, -1, 0))
    require(sum(a * b for a, b in zip(left, right)) == 1, "literal unit channel")
    prefix_columns = columns(gates, 9)
    require(tuple(sum(left[j] * col[j] for j in range(9)) for col in prefix_columns) == left,
            "pooled prefix support")
    require(activation.replay(backward, right) == right, "pooled suffix support")
    dirty = (7, -11, 13, -17, 19, -23, 29, -31, 37)
    require(activation.replay(gates + backward, dirty) == dirty, "signed dirty-input fixture")
    return {"coordinates": 9, "complete_scalar_adds": len(gates + backward),
            "forward_inverse_basis_columns": 18, "pairing": list(entries),
            "unit_row": [1, 1, -1], "unit_column": [1, 1, 1]}


def rejects(call):
    try:
        call()
    except ValueError:
        return 1
    raise ValueError("a rejecting control was accepted")


def verify_controls():
    controls = 0
    for entries in ((15,), (15, 21), (15, 35), (21, 35)):
        controls += rejects(lambda entries=entries: activation.unit_witness(entries))
    for entries in ((), (True,), (-1,), (10**9 + 1,), (1,) * 9):
        controls += rejects(lambda entries=entries: activation.checked_entries(entries))
    controls += rejects(lambda: activation.omitted_prime_entries((3, 3)))
    controls += rejects(lambda: activation.omitted_prime_entries((2, 3)))
    controls += rejects(lambda: activation.prefix(50))
    controls += rejects(lambda: activation.replay(((0, 0, 1),), (1, 2, 3)))
    controls += rejects(lambda: require(15 + 21 + 35 == 1, "wrong channel sign"))
    controls += rejects(lambda: require(minor_capacity((15, 21)) == 1, "false pair activation"))
    gates = activation.prefix(15)
    controls += rejects(lambda: require(columns(gates + activation.inverse(gates)[:-1], 3)
                                        == ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "omitted cleanup"))
    require(activation.unit_witness((2, 6))[1] == 2, "dyadic unit positive control")
    require(minor_capacity((1, 3, 5)) == 2, "two-channel positive control")
    return controls


def main():
    hashes = authenticate()
    families = verify_families()
    scalar_cases = tuple(range(1, 50, 2))
    for d in scalar_cases:
        verify_scalar(d)
    result = {"family_checks": families, "scalar_cut_cases": len(scalar_cases),
              "concrete_word": verify_nine_coordinate_word(),
              "rejecting_controls": verify_controls()}
    print(json.dumps({"result": result, "sha256": hashes}, sort_keys=True))
    print("PASS_HIGHER_ORDER_CUT_ACTIVATION")


if __name__ == "__main__":
    main()
