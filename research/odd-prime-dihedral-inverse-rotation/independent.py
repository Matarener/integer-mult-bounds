#!/usr/bin/env python3
"""Independent permutation-built D_{2p} replay; imports no primary engine."""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent

CERTIFIED_PRIMES = (5, 7, 11, 13, 17, 19, 23, 29, 31)
EXPECTED_COUNTS = {0: 1, 1: 56, 2: 3136, 3: 175616}
ZERO_M = (0, 0, 0)
ID_M = (1, 2, 4)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def load_json_reject_duplicates(path: Path):
    def hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def build_perms(p: int):
    need(is_prime(p) and p % 2 == 1, f"odd prime required: {p}")

    def as_perm(k: int, e: int) -> tuple[int, ...]:
        return tuple((k + (-j if e else j)) % p for j in range(p))

    perms = [as_perm(k, e) for k in range(p) for e in range(2)]
    index = {perm: i for i, perm in enumerate(perms)}
    need(len(perms) == 2 * p and len(index) == 2 * p, f"p={p}: perm count")

    def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(a[b[i]] for i in range(p))

    table = [[index[compose(a, b)] for b in perms] for a in perms]
    e = index[tuple(range(p))]
    s = index[tuple((-j) % p for j in range(p))]
    t = index[tuple((-j - 1) % p for j in range(p))]
    r = table[s][t]
    r_inv = table[t][s]
    need(table[s][s] == e and table[t][t] == e, f"p={p}: involutions")
    acc = e
    for _ in range(p):
        acc = table[acc][r]
    need(acc == e, f"p={p}: rotation order")
    need(all(table[table[a][b]][c] == table[a][table[b][c]]
             for a, b, c in product(range(2 * p), repeat=3)),
         f"p={p}: associativity")
    return {
        "p": p,
        "table": table,
        "e": e,
        "s": s,
        "t": t,
        "r": r,
        "r_inv": r_inv,
        "ngroup": 2 * p,
    }


PROJECTORS = [(x, y) for x in range(1, 8) for y in range(1, 8)
              if (x & y).bit_count() & 1]
need(len(PROJECTORS) == 28, "projector count")


def add_rows(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return (a[0] ^ b[0], a[1] ^ b[1], a[2] ^ b[2])


def right_call(table, state, label: int, projector: tuple[int, int]):
    x, y = projector
    out = [ZERO_M for _ in range(len(state))]
    for g, rows in enumerate(state):
        if rows == ZERO_M:
            continue
        image = tuple(y if (row & x).bit_count() & 1 else 0 for row in rows)
        unchanged = add_rows(rows, image)
        h = table[g][label]
        out[g] = add_rows(out[g], unchanged)
        out[h] = add_rows(out[h], image)
    return tuple(out)


def word_state(group, labels, projectors):
    unit = tuple(ID_M if g == group["e"] else ZERO_M for g in range(group["ngroup"]))
    state = unit
    for label, projector in zip(labels, projectors):
        state = right_call(group["table"], state, label, projector)
    return state


def target_for(group):
    return tuple(
        (1, 0, 0) if g == group["r"] else
        (0, 2, 0) if g == group["r_inv"] else
        (0, 0, 4) if g == group["e"] else ZERO_M
        for g in range(group["ngroup"])
    )


def search_prime(p: int) -> dict:
    group = build_perms(p)
    target = target_for(group)
    counts = {}
    hits = {}
    digests = {}
    for k in range(4):
        digest = hashlib.sha256()
        count = hit = 0
        for labels in product((group["s"], group["t"]), repeat=k):
            for projectors in product(PROJECTORS, repeat=k):
                state = word_state(group, labels, projectors)
                record = bytes(labels)
                record += b"".join(bytes(pr) for pr in projectors)
                record += bytes(row for coeff in state for row in coeff)
                digest.update(record)
                count += 1
                hit += state == target
        counts[k] = count
        hits[k] = hit
        digests[k] = digest.hexdigest()
    need(counts == EXPECTED_COUNTS, f"p={p}: counts {counts}")
    need(hits == {0: 0, 1: 0, 2: 0, 3: 0}, f"p={p}: hits {hits}")
    e00 = (1, 1)
    e11 = (2, 2)
    direct = word_state(
        group,
        (group["s"], group["t"], group["t"], group["s"]),
        (e00, e00, e11, e11),
    )
    need(direct == target, f"p={p}: direct fails")
    return {
        "p": p,
        "exact_endpoint_hits": {str(k): hits[k] for k in range(4)},
        "independent_state_sha256": {str(k): digests[k] for k in range(4)},
        "direct_exact": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="merge independent digests into CERTIFICATE.json",
    )
    args = parser.parse_args()
    cert_path = HERE / "CERTIFICATE.json"
    need(cert_path.is_file(), "missing CERTIFICATE.json; run verify.py --write first")
    cert = load_json_reject_duplicates(cert_path)
    need(tuple(cert["certified_primes"]) == CERTIFIED_PRIMES, "prime list")
    rows = [search_prime(p) for p in CERTIFIED_PRIMES]
    if args.write:
        for row, committed in zip(rows, cert["primes"]):
            need(row["p"] == committed["p"], "prime match on write")
            committed["independent_state_sha256"] = row["independent_state_sha256"]
        cert_path.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
        print("WROTE_INDEPENDENT_DIGESTS", cert_path)
        cert = load_json_reject_duplicates(cert_path)
    for row, committed in zip(rows, cert["primes"]):
        need(row["p"] == committed["p"], "prime match")
        need(row["exact_endpoint_hits"] == committed["exact_endpoint_hits"],
             f"p={row['p']} hits")
        need("independent_state_sha256" in committed,
             f"p={row['p']}: missing independent digests")
        need(row["independent_state_sha256"] == committed["independent_state_sha256"],
             f"p={row['p']}: independent digest mismatch")
    print(
        "PASS_INDEPENDENT_ODD_PRIME_DIHEDRAL_INVERSE_ROTATION",
        f"primes={list(CERTIFIED_PRIMES)}",
        "min_calls=4",
        "hits=0",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
