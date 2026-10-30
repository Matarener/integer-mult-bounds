#!/usr/bin/env python3
"""Bounded exact corroboration of the all-field Schur rank/dimension law.

Not a proof-kernel verification. No external inputs or dependencies.
apoursh with substantial OpenAI Codex assistance; Apache-2.0.
Predecessor factorization/construction: Krzysztof Wojt PR5128; sector search:
Nick Petalas PR6031. The all-field proof is separate in PROOF.md.
"""
import hashlib
import itertools
import json
from pathlib import Path
import random
import types


def source_module(name):
    path = Path(__file__).with_name(name + ".py")
    module = types.ModuleType(name)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


la = source_module("algebra")
oracle = source_module("oracle")
oracle.install(la)


def closed_rho0(a, b, h, p):
    """Basis-free formula; the order of the three factors is essential."""
    _, f, j, _ = la.compressed(a, b, h, p)
    first = la.mul(la.mul(j, la.inverse(a, p), p), f, p)
    second = la.mul(la.mul(f, la.inverse(b, p), p), j, p)
    return la.rank(first, p) + la.rank(second, p) + 2 * la.rank(h, p) - 2 * len(a)


def invariant(a, b, h, p):
    d = len(a)
    ts = la.compressed(a, b, h, p)
    right = [la.kernel(t, p) for t in ts[1:]]
    left = [la.kernel(la.transpose(t), p) for t in ts[1:]]
    cross = []
    for i, j in ((0, 1), (1, 0)):
        pairing = [[sum(x * y for x, y in zip(w, la.apply(h, z, p))) % p
                    for z in right[j]] for w in left[i]]
        cross.append(la.rank(pairing, p))
    s, r = sum(map(len, right)), sum(cross)
    rho0 = 2 * d - 2 * s + r
    nmax = 3 * d + la.rank(ts[0], p) + s
    law = {rho: nmax - (2 * d - rho) - min(2 * d - rho, r)
           for rho in range(rho0, 2 * d + 1)}
    return rho0, law, cross


def matrices(d, p):
    return [[list(v[i:i + d]) for i in range(0, d * d, d)]
            for v in itertools.product(range(p), repeat=d * d)]


def sampled_triples(d, p, count):
    mats = matrices(d, p)
    gl = [a for a in mats if la.rank(a, p) == d]
    rng = random.Random(6031 + 100 * d + p)
    picked = {}
    def take(a, b, h):
        key = tuple(tuple(tuple(row) for row in m) for m in (a, b, h))
        picked[key] = (a, b, h)
    for a in gl[::max(1, len(gl) // 4)][:4]:
        take(a, a, a)
        take(a, a, la.zeros(d, d))
        take(a, la.eye(d), a)
    if (d, p) == (2, 3):
        take([[1, 0], [0, 2]], [[1, 1], [0, 1]], la.eye(2))
    while len(picked) < count:
        take(rng.choice(gl), rng.choice(gl), rng.choice(mats))
    return list(picked.values())


def cases():
    for d, p in ((1, 2), (1, 3), (1, 5), (2, 2)):
        mats = matrices(d, p)
        gl = [a for a in mats if la.rank(a, p) == d]
        yield d, p, "exhaustive", list(itertools.product(gl, gl, mats))
    yield 2, 3, "deterministic sample", sampled_triples(2, 3, 192)
    yield 3, 2, "deterministic sample", sampled_triples(3, 2, 24)


def check_case(a, b, h, p):
    _, actual, witnesses, direct_rho0, pairs = oracle.profile(a, b, h, p)
    rho0, predicted, cross = invariant(a, b, h, p)
    la.require(rho0 == direct_rho0, "cross-block rho0 versus TMT")
    la.require(closed_rho0(a, b, h, p) == direct_rho0, "ordered product rho0 versus TMT")
    la.require(actual == predicted, "exact minimum dimension versus direct search")
    for rho, (iss, ns) in witnesses.items():
        pp, qq = la.build_pair(a, b, h, iss, ns, p)
        la.require(len(pp) == actual[rho], "wrong witness dimension")
        la.require(la.literal_rank(a, b, h, pp, qq, p) == rho, "wrong witness rank")
    row = {"A": a, "B": b, "H": h, "rho0": rho0, "cross_ranks": cross,
           "profile": sorted(actual.items())}
    return row, pairs, len(witnesses)


def rejects(operation):
    try:
        operation()
    except ValueError:
        return True
    return False


def controls():
    a, b, h, p = [[1, 0], [0, 2]], [[1, 1], [0, 1]], la.eye(2), 3
    _, exact, wit, direct, _ = oracle.profile(a, b, h, p)
    rho0, predicted, cross = invariant(a, b, h, p)
    la.require(exact == {1: 5, 2: 6, 3: 7, 4: 9} and cross == [1, 0], "odd fixture")
    tests = {
        "omit_cross_pairing": rejects(lambda: la.require(rho0 - sum(cross) == direct, "omitted cross")),
        "force_equal_cross_ranks": rejects(lambda: la.require(cross[0] == cross[1], "unequal cross")),
        "force_even_rank": rejects(lambda: la.require(direct % 2 == 0, "odd rank")),
        "wrong_minimum": rejects(lambda: la.require({**predicted, 2: 5} == exact, "wrong minimum")),
    }
    iss, ns = wit[1]
    pp, qq = la.build_pair(a, b, h, iss, ns, p)
    changed = [r[:] for r in pp]
    changed[0][0] = (changed[0][0] + 1) % p
    tests["changed_witness"] = rejects(lambda: la.literal_rank(a, b, h, changed, qq, p))
    tests["wrong_product_block"] = rejects(lambda: la.literal_rank(a, b, la.zeros(2, 2), pp, qq, p))
    _, slope, _, start, _ = oracle.profile(h, h, h, p)
    slope_one = {rho: slope[start] + rho - start for rho in slope}
    tests["slope_one_only"] = rejects(lambda: la.require(slope_one == slope, "slope two required"))
    a = b = [[0, 1], [1, 0]]
    h, p = [[0, 1], [1, 1]], 2
    _, f, j, _ = la.compressed(a, b, h, p)
    wrong_first = la.mul(la.mul(la.inverse(a, p), j, p), f, p)
    wrong_second = la.mul(la.mul(la.inverse(b, p), f, p), j, p)
    wrong = la.rank(wrong_first, p) + la.rank(wrong_second, p) + 2 * la.rank(h, p) - 4
    _, _, _, direct, _ = oracle.profile(a, b, h, p)
    la.require(closed_rho0(a, b, h, p) == direct == 0 and wrong == 2, "order fixture")
    tests["commute_inverse_past_factor"] = rejects(lambda: la.require(wrong == direct, "ordered factors"))
    la.require(all(tests.values()), "a mutation survived")
    return tests


def check_subspace_inventory():
    """Gaussian-binomial dimension counts, independent of search results."""
    expected = {(1, 2): [1, 1], (1, 3): [1, 1], (1, 5): [1, 1],
                (2, 2): [1, 3, 1], (2, 3): [1, 4, 1], (3, 2): [1, 7, 7, 1]}
    for (d, p), counts in expected.items():
        actual = [sum(len(s) == k for s in la.subspaces(d, p)) for k in range(d + 1)]
        la.require(actual == counts, "incomplete subspace inventory")
    return {f"d{d}_F{p}": counts for (d, p), counts in expected.items()}


def check_coverage(coverage):
    expected = [(1, 2, 2, 20, 6, 0, 0), (1, 3, 12, 66, 32, 0, 0),
                (1, 5, 80, 260, 168, 0, 0), (2, 2, 576, 21690, 2496, 0, 288),
                (2, 3, 192, 8326, 668, 6, 151), (3, 2, 24, 273516, 146, 6, 11)]
    keys = ("d", "p", "triples", "subspace_pairs", "literal_witnesses",
            "odd_rho0", "noncommuting_pivots")
    la.require([tuple(row[k] for k in keys) for row in coverage] == expected,
               "coverage differs from recorded fixture inventory")


def main():
    subspace_histograms = check_subspace_inventory()
    rows, coverage = [], []
    for d, p, scope, triples in cases():
        pairs = witnesses = odd = noncommuting = 0
        for a, b, h in triples:
            row, count, n = check_case(a, b, h, p)
            pairs += count
            witnesses += n
            odd += row["rho0"] % 2
            noncommuting += la.mul(a, b, p) != la.mul(b, a, p)
            rows.append({"d": d, "p": p, **row})
        coverage.append({"d": d, "p": p, "scope": scope, "triples": len(triples),
                         "subspace_pairs": pairs, "literal_witnesses": witnesses,
                         "odd_rho0": odd, "noncommuting_pivots": noncommuting})
    check_coverage(coverage)
    summary = {"coverage": coverage, "controls": controls(),
               "subspace_histograms": subspace_histograms,
               "rows_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True,
                    separators=(",", ":")).encode()).hexdigest()}
    la.require(summary["rows_sha256"] == "c38f9ced06db3ecf1bc4c7f8802df7f1b3228f3435946700e7340b115d3156db",
               "fixture result digest changed")
    print(json.dumps(summary, sort_keys=True, indent=2))
    print("PASS_SCHUR_RANKS_ALL_FIELDS_BOUNDED_CHECKS")


if __name__ == "__main__":
    main()
