"""Finite corroboration of the synchronized-envelope proof; no files written.

New work produced by Nick Petalas. Apache-2.0.
"""

import copy
from fractions import Fraction
import hashlib
import itertools
import json
from math import prod
from pathlib import Path
import subprocess
import sys

import envelope


ROOT = Path(__file__).resolve().parent


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def subset_expansion(bases, p, q, scale, offset):
    """Independent literal subset formula, not repeated sparse multiplication."""
    result = {1: offset}
    for mask in range(1 << len(bases)):
        chosen = [base for i, base in enumerate(bases) if mask & (1 << i)]
        absent = [base for i, base in enumerate(bases) if not mask & (1 << i)]
        rank = prod(chosen)**q
        coefficient = scale * (-1)**len(absent) * prod(absent)**p
        result[rank] = result.get(rank, 0) + coefficient
    return {rank: count for rank, count in result.items() if count}


def document(bases, p, q, scale, offset, use_targets):
    values = subset_expansion(bases, p, q, scale, offset)
    old = {"schema": "integer-mult-recursive-invoice/v1",
           "contract": {"model": "finite synthetic power-invoice control"},
           "paid": {"13": 17}, "targets": {"11": 19}}
    new = copy.deepcopy(old)
    for rank, count in values.items():
        if use_targets:
            owner, kind = (old, "targets") if count > 0 else (new, "targets")
        else:
            owner, kind = (new, "paid") if count > 0 else (old, "paid")
        key = str(rank)
        owner[kind][key] = owner[kind].get(key, 0) + abs(count)
    return {"schema": "synchronized-invoice-envelope/v1", "old": old, "new": new,
            "certificate": {"bases": list(bases), "p": p, "q": q,
                            "scale": scale, "offset": offset}}


def integer_root(value, q):
    low, high = 1, value
    for _ in range(31):
        if low >= high:
            break
        middle = (low + high) // 2
        if middle**q < value:
            low = middle + 1
        else:
            high = middle
    ensure(low == high and low**q == value, "rank is not an exact q-th power")
    return low


def exact_points(doc, coefficients):
    cert = doc["certificate"]
    p, q = cert["p"], cert["q"]
    roots = {rank: integer_root(rank, q) for rank in coefficients}
    count = 0
    for numerator in sorted({-1, 0, p - 1, p, p + 1, q, q + 1}):
        value = sum(Fraction(coefficient) * Fraction(roots[rank])**numerator
                    for rank, coefficient in coefficients.items())
        factor = Fraction(cert["scale"]) * prod(
            Fraction(base)**numerator - base**p for base in cert["bases"])
        ensure(value == factor + cert["offset"], "rational-power evaluation disagrees")
        ensure(value >= cert["offset"], "claimed envelope fails at exact point")
        ensure((value == cert["offset"]) == (numerator == p), "wrong equality point")
        count += 1
    return count


def positive_cases():
    contexts = [(bases, p, q) for bases in itertools.product(range(2, 8), repeat=2)
                for q in range(2, 6) for p in range(1, q)]
    for length in (4, 6, 8):
        contexts.extend((bases, 1, 2) for bases in itertools.product((2, 3), repeat=length))
    cases = points = terms = 0
    for bases, p, q in contexts:
        for scale, offset in itertools.product((1, 3), (0, 1, 7)):
            doc = document(bases, p, q, scale, offset, bool(cases % 2))
            coefficients = subset_expansion(bases, p, q, scale, offset)
            result = envelope.check(doc)
            ensure(envelope.expand(doc["certificate"]) == coefficients, "expansions differ")
            ensure(result["minimum"] == offset, "wrong minimum")
            ensure(result["root_multiplicity"] == (len(bases) if offset == 0 else 0),
                   "wrong multiplicity")
            points += exact_points(doc, coefficients)
            terms += len(coefficients)
            cases += 1
    return {"contexts": len(contexts), "certificates": cases,
            "exact_rational_points": points, "expanded_support_entries": terms}


def rejected(call):
    try:
        call()
    except (ValueError, TypeError):
        return
    raise ValueError("invalid certificate was accepted")


def negative_cases(example):
    mutations = []
    for key, value in (("bases", [2, 3, 5]), ("bases", [True, 3]),
                       ("bases", [1, 3]), ("bases", [2] * 10),
                       ("bases", [64, 64]), ("p", 0), ("p", 2),
                       ("q", 17), ("scale", 0), ("scale", True),
                       ("offset", -1), ("offset", 1)):
        candidate = copy.deepcopy(example)
        candidate["certificate"][key] = value
        if value == [64, 64]:
            candidate["certificate"]["q"] = 16
        mutations.append(candidate)
    for side, kind, key, value in (("new", "targets", "5", 12),
                                    ("old", "targets", "5", 12),
                                    ("new", "paid", "36", 2),
                                    ("old", "paid", "4", True),
                                    ("old", "paid", "04", 3),
                                    ("new", "paid", "1000000001", 1),
                                    ("new", "paid", "2", 10**60 + 1)):
        candidate = copy.deepcopy(example)
        candidate[side][kind][key] = value
        mutations.append(candidate)
    candidate = copy.deepcopy(example)
    candidate["new"]["contract"]["model"] = "changed model"
    mutations.append(candidate)
    candidate = copy.deepcopy(example)
    candidate["certificate"]["untrusted_claim"] = "positive"
    mutations.append(candidate)
    for candidate in mutations:
        rejected(lambda: envelope.check(candidate))
    for raw in (b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}', b' ' * (1024**2 + 1)):
        rejected(lambda: envelope.decode(raw))
    ensure(prod(Fraction(a)**0 - a for a in (2, 3, 5)) < 0, "odd-factor control fails")
    return len(mutations) + 5


def cli_case():
    path = ROOT / "EXAMPLE.json"
    result = subprocess.run([sys.executable, "-I", "-W", "error", "-B",
                             str(ROOT / "envelope.py"), str(path)],
                            check=True, capture_output=True, text=True, timeout=15)
    parsed = json.loads(result.stdout)
    ensure(parsed["input_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(),
           "CLI input hash differs")
    ensure(parsed["minimum"] == 0 and parsed["root_multiplicity"] == 2, "wrong CLI envelope")
    return parsed


def main():
    example, digest = envelope.load(ROOT / "EXAMPLE.json")
    ensure(envelope.check(example)["support_size"] == 4, "example support differs")
    stats = positive_cases()
    stats["rejection_controls"] = negative_cases(example)
    stats["example_input_sha256"] = digest
    stats["cli"] = cli_case()
    names = ("envelope.py", "verify.py", "PROOF.md", "README.md", "TASK.json",
             "SOURCES.json", "VERIFY.json", "EXAMPLE.json")
    stats["package_sha256"] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                               for name in names}
    print(json.dumps(stats, indent=2, sort_keys=True))
    print("PASS_MIXED_RANK_TOUCHING_ENVELOPE")


if __name__ == "__main__":
    main()
