#!/usr/bin/env python3
"""Check the finite geometry behind the written arbitrary-multiplicity theorem."""

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (beta_five_floor, certificate, check_fitting,
                   dot, need, types, weighted_bound)
from source import authenticate


def rank(matrix, prime=None):
    rows = [[F(x) if prime is None else x % prime for x in row] for row in matrix]
    pivot = 0
    for col in range(len(rows[0]) if rows else 0):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        inv = 1 / rows[pivot][col] if prime is None else pow(rows[pivot][col], -1, prime)
        rows[pivot] = [x * inv if prime is None else x * inv % prime for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            factor = rows[i][col]
            rows[i] = [x - factor * y if prime is None else (x - factor * y) % prime
                       for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def retained_projector():
    """One source positive control, checked through its exact low-rank factors."""
    odd = [x for x in range(64) if x.bit_count() & 1]
    sinks = [w for w in odd if not dot(1, w)]
    ports = [(q, w) for q in odd for w in sinks if dot(q, w)]
    b = [[dot(w, q) for q in odd] for w in sinks]
    # B L = I16 is an exact integer equality after clearing denominator eight.
    left_inverse = [[(1 - 8 * (q == 62)) * dot(q, w) for w in sinks] for q in odd]
    product = [[sum(b[i][k] * left_inverse[k][j] for k in range(32))
                for j in range(16)] for i in range(16)]
    need(product == [[8 * (i == j) for j in range(16)] for i in range(16)],
         "retained projector factor identity")
    need(rank(b) == 16, "retained rational rank")
    lambdas = [1 - 8 * (q == 62) for q, _ in ports]
    need(len(ports) == 256 and sum(lambdas) == 128, "retained projector trace")
    # A projector is not a complete unit: its rank-one scalar factor fails the mask.
    scalar = [[F(lam, 8) for lam in lambdas] for _ in ports]
    try:
        check_fitting(6, ports, scalar)
    except ValueError as exc:
        need(str(exc) == "forbidden scalar coefficient", "local/complete control reason")
    else:
        raise ValueError("local projector accepted as a complete unit")
    return {"ports": 256, "rank": 16, "trace": 16,
            "complete_unit_rejected": True}


def run(archive=None):
    source = authenticate(archive)
    expected = {
        5: {"cross": (90, 10), "diagonal": (15, 2),
            "one-special": (30, 8), "special": (1, 1)},
        6: {"cross": (480, 45), "diagonal": (32, 3)},
    }
    certificates, fixtures = [], 0
    for dimension in (5, 6):
        cert = certificate(dimension)
        need({r["name"]: (r["size"], r["selected"]) for r in cert["orbits"]}
             == expected[dimension], "orbit certificate changed")
        chosen = list(cert["selector"])
        # Distinct copies remain separate diagonal positions, with arbitrary free entries.
        ports = [t for i, t in enumerate(chosen) for _ in range(1 + (i % 3 == 0))]
        matrix = [[int(i == j) if dot(w, q) else ((7 * i + 11 * j) % 5 - 2)
                   for j, (q, _) in enumerate(ports)] for i, (_, w) in enumerate(ports)]
        check_fitting(dimension, ports, matrix)
        for prime in (None, 2, 3, 5):
            need(rank(matrix, prime) == len(ports), "duplicated triangular minor rank")
            fixtures += 1
        multiplicities = {t: (i * 7 + 3) % 6 for i, t in enumerate(types(dimension))}
        bound = weighted_bound(dimension, multiplicities)
        total = sum(multiplicities.values())
        need(bound >= F(3, 32) * total if dimension == 6 else bound >= F(total, 9),
             "nonuniform multiplicity bound")
        cert["selector_sha256"] = hashlib.sha256(
            json.dumps(cert["selector"], separators=(",", ":")).encode()).hexdigest()
        cert.pop("selector")
        cert["nonuniform_fixture"] = {"ports": total, "bound": str(bound)}
        certificates.append(cert)
    need(F(15, 32) > F(45, 100), "beta-five stop margin")
    need(beta_five_floor(480) == 225 and beta_five_floor(512) == 240,
         "rounded beta-five invoice")
    need(5 * 9 == 45 and (5 * 32) // 3 == 53, "paired window bounds")
    return {"status": "PASS_ODD_UNIT_TRIANGULAR_RANK", "source": source,
            "certificates": certificates, "field_fixtures": fixtures,
            "retained_projector": retained_projector(),
            "scope": "Finite geometry supporting PROOF.md; no supplier or new kappa."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.source_archive), sort_keys=True))
