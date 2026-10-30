#!/usr/bin/env python3
"""Exact regression evidence for the written two-use descent proof.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
No predecessor executable, finite-address quotient, or third-party dependency.
"""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256, sha1
from itertools import product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = "research/bit-fifth-frame-determinant-obstruction/README.md"
SOURCE_SHA256 = "fa3f0f951146caa5b1eb7b7417175eb7a380cae8674e4a470407517dac40f227"
SOURCE_BLOB = "608a24af8bc3d27ee1554c94872601bb3a409f67"
ZERO = (0, 0, 0)
LABELS = {"A": (1, 0, 0), "B": (0, 1, 0), "P": (0, 0, 2),
          "Q": (1, 1, -2), "R": (2, 0, 0), "S": (0, 0, 1)}
PROFILE = {"A": 1, "B": 3, "P": 0, "Q": 1, "R": 1, "S": 2}
TARGETS = [(1, 0, 2), (2, 1, -2), (0, 1, 2), (1, 2, -2)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def unit(w):
    return sum(1 << (i * w + i) for i in range(w))


@lru_cache(maxsize=65536)
def mul_bits(a, b, w):
    """Row-packed binary multiplication, used only by the coefficient engine."""
    out = 0
    mask = (1 << w) - 1
    for i in range(w):
        row = (a >> (i * w)) & mask
        value = 0
        while row:
            bit = row & -row
            value ^= (b >> ((bit.bit_length() - 1) * w)) & mask
            row ^= bit
        out |= value << (i * w)
    return out


def projectors(w):
    return [sum(((v if (u >> i) & 1 else 0) << (i * w)) for i in range(w))
            for u in range(1, 1 << w) for v in range(1, 1 << w)
            if (u & v).bit_count() % 2]


def plus(*matrices):
    out = {}
    for matrix in matrices:
        for exponent, coefficient in matrix.items():
            out[exponent] = out.get(exponent, 0) ^ coefficient
    return {e: c for e, c in out.items() if c}


def times(a, b, w):
    out = {}
    for e, c in a.items():
        for f, d in b.items():
            g = add(e, f)
            out[g] = out.get(g, 0) ^ mul_bits(c, d, w)
    return {e: c for e, c in out.items() if c}


def call(e, n, w):
    return plus({ZERO: unit(w) ^ n}, {e: n})


def word(factors, w):
    out = {ZERO: unit(w)}
    for factor in factors:
        out = times(out, factor, w)
    return out


def endpoint(w):
    out = {}
    for i in range(w):
        e = TARGETS[i] if i < 4 else ZERO
        out[e] = out.get(e, 0) ^ (1 << (i * w + i))
    return out


def entry_engine(factors, w):
    """Independent entry-wise sets of monomials; no packed multiplication."""
    state = [[{ZERO} if i == j else set() for j in range(w)] for i in range(w)]
    for factor in factors:
        right = [[{e for e, c in factor.items() if (c >> (i * w + j)) & 1}
                  for j in range(w)] for i in range(w)]
        nxt = [[set() for _ in range(w)] for _ in range(w)]
        for i in range(w):
            for j in range(w):
                for k in range(w):
                    for a in state[i][k]:
                        for b in right[k][j]:
                            term = (a[0] + b[0], a[1] + b[1], a[2] + b[2])
                            if term in nxt[i][j]:
                                nxt[i][j].remove(term)
                            else:
                                nxt[i][j].add(term)
        state = nxt
    return {e: sum((1 << (i * w + j)) for i in range(w) for j in range(w)
                   if e in state[i][j])
            for row in state for entry in row for e in entry}


def odd_part(matrix):
    return {e: c for e, c in matrix.items() if e[2] % 2}


def authenticate_bytes(data):
    require(sha256(data).hexdigest() == SOURCE_SHA256, "source SHA256 mismatch")
    header = b"blob " + str(len(data)).encode() + b"\0"
    require(sha1(header + data).hexdigest() == SOURCE_BLOB, "source Git blob mismatch")


def check_source():
    authenticate_bytes((ROOT / SOURCE).read_bytes())
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["path"] == SOURCE]
    require(len(rows) == 1 and rows[0]["usage"] == "input"
            and rows[0]["sha256"] == SOURCE_SHA256 and rows[0]["git_blob"] == SOURCE_BLOB,
            "source manifest binding mismatch")


def rejection(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control was accepted: " + message)


def frame(e):
    # Independent rational-matrix realization in the basis A, B, S=P/2.
    a, b, s = e
    return (F(a) + F(s, 4), F(s, 4), F(s, 4), F(b) + F(s, 4))


def sum_frames(frames):
    frames = list(frames)
    return tuple(sum(row[i] for row in frames) for i in range(4))


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def candidate_checks():
    for e in LABELS.values():
        a, b, c, d = frame(e)
        require(a * d == b * c and a + d > 0 and a >= 0 and d >= 0,
                "paid frame is not positive rank one")
    labels = [LABELS[name] for name, count in PROFILE.items() for _ in range(count)]
    require(len(labels) == 8, "wrong candidate length")
    require(sum_frames(map(frame, labels)) == sum_frames(map(frame, TARGETS))
            == (F(4), F(0), F(0), F(4)), "determinant sum mismatch")
    require(tuple(sum(e[j] for e in labels) for j in range(3))
            == tuple(sum(t[j] for t in TARGETS) for j in range(3)) == (4, 4, 0),
            "integer-lattice determinant sum mismatch")
    # Compare literal 2^8 rational-matrix subset expansion with bounded lattice counts.
    literal = []
    for mask in range(1 << len(labels)):
        literal.append(sum_frames([frame(e) for i, e in enumerate(labels) if (mask >> i) & 1]))
    support_counts = [literal.count(frame(t)) for t in TARGETS]
    require(all(support_counts), "candidate does not pass the support condition")
    lattice_sums = set()
    for counts in product(*(range(n + 1) for n in PROFILE.values())):
        lattice_sums.add(tuple(sum(c * LABELS[name][j] for name, c in zip(PROFILE, counts))
                               for j in range(3)))
    require(all(t in lattice_sums for t in TARGETS), "lattice support disagrees")
    characters = []
    for chi in product(range(2), repeat=3):
        value = lambda e: sum(x * y for x, y in zip(chi, e)) % 2
        paid = sum(map(value, labels))
        target = sum(map(value, TARGETS))
        require(paid >= target, "raw lattice character already excludes candidate")
        characters.append({"chi": list(chi), "calls": paid, "target_rank": target})
    # A single projector assignment satisfies ALL raw first-order matrix
    # equations jointly, not just their separate rank inequalities.
    linear_witness = [("A", 0), ("B", 1), ("B", 2), ("B", 3),
                      ("Q", 3), ("R", 0), ("S", 0), ("S", 0)]
    for chi in product(range(2), repeat=3):
        derivative = 0
        for name, role in linear_witness:
            if sum(x * y for x, y in zip(chi, LABELS[name])) % 2:
                derivative ^= 1 << (role * 4 + role)
        target = sum((sum(x * y for x, y in zip(chi, e)) % 2) << (i * 4 + i)
                     for i, e in enumerate(TARGETS))
        require(derivative == target, "joint first-order witness failed")
    linear_factors = [call(LABELS[name], 1 << (role * 4 + role), 4)
                      for name, role in linear_witness]
    require(word(linear_factors, 4) == entry_engine(linear_factors, 4) != endpoint(4),
            "first-order witness must not be an exact construction")
    # Descent removes the two S factors and adds one P. H uses A,B,P as its basis.
    contracted = dict(PROFILE, P=1, S=0)
    contracted_labels = [LABELS[name] for name, count in contracted.items() for _ in range(count)]
    require(all(e[2] % 2 == 0 for e in contracted_labels + TARGETS), "descent not in H")
    detected = sum((e[2] // 2) % 2 for e in contracted_labels)
    target_derivative = [((t[2] // 2) % 2) << i for i, t in enumerate(TARGETS)]
    require(detected == 2 and rank(target_derivative) == 4, "descent rank gap lost")
    require(all(e[2] % 2 == 0 for name, e in LABELS.items() if name != "S")
            and all(t[2] % 2 == 0 for t in TARGETS), "index-two premise fails")
    return {"profile": PROFILE, "lattice_basis": ["A", "B", "S=P/2"],
            "literal_subset_count": len(literal), "target_support_multiplicities": support_counts,
            "joint_first_order_witness_label_role": linear_witness,
            "raw_characters": characters, "contracted_profile": contracted,
            "contracted_detected_calls": detected, "contracted_target_rank": 4}


def descent_regressions():
    census = []
    for w in (2, 3):
        ps = projectors(w)
        require(len(set(ps)) == ((1 << w) - 1) * (1 << (w - 1)), "projector count")
        for n in ps:
            require(mul_bits(n, n, w) == n, "projector not idempotent")
        even_endpoints = checked = 0
        for first, middle, last in product(ps, repeat=3):
            factors = [call((0, 0, 1), first, w), call((0, 0, 2), middle, w),
                       call((0, 0, 1), last, w)]
            result = word(factors, w)
            if w == 2:
                require(result == entry_engine(factors, w), "independent engine mismatch")
            expected = first == last and mul_bits(first, middle, w) == mul_bits(middle, first, w)
            require((not odd_part(result)) == expected, "two-use criterion mismatch")
            if expected:
                fused = word([factors[1], call((0, 0, 2), first, w)], w)
                require(result == fused, "contraction changed endpoint")
                even_endpoints += 1
            checked += 1
        census.append({"width": w, "projectors": len(ps), "triples": checked,
                       "even_endpoints": even_endpoints})
    # Arbitrary middle matrix: test the stronger P M = M Q intertwiner lemma.
    # These finite matrix-unit regressions are not a proof for arbitrary width.
    block_cases = 0
    for w in (2, 3, 4):
        ps = projectors(w)
        pairs = product(ps, repeat=2) if w < 4 else ((n, n) for n in ps)
        for p, q in pairs:
            c, d = unit(w) ^ p, unit(w) ^ q
            for ij in range(w * w):
                m = 1 << ij
                middle = {(0, 0, 2): m}
                actual = word([call((0, 0, -3), p, w), middle,
                               call((0, 0, 5), q, w)], w)
                cmq = mul_bits(mul_bits(c, m, w), q, w)
                pmd = mul_bits(mul_bits(p, m, w), d, w)
                expanded = plus({(0, 0, 2): mul_bits(mul_bits(c, m, w), d, w)},
                                {(0, 0, 7): cmq}, {(0, 0, -1): pmd},
                                {(0, 0, 4): mul_bits(mul_bits(p, m, w), q, w)})
                require(actual == expanded, "Peirce block expansion mismatch")
                require((not odd_part(actual)) == (cmq == 0 and pmd == 0),
                        "cross blocks failed to isolate")
                if not odd_part(actual):
                    require(mul_bits(p, m, w) == mul_bits(m, q, w), "intertwiner failed")
                    require(actual == word([middle, call((0, 0, 2), q, w)], w),
                            "general contraction failed")
                block_cases += 1
    return {"complete_three_factor_censuses": census, "matrix_unit_block_cases": block_cases,
            "independent_entry_engine_triples": 216}


def construction_controls():
    direct = [("A", 0), ("P", 0), ("A", 1), ("Q", 1),
              ("B", 2), ("P", 2), ("B", 3), ("Q", 3)]
    divided = [("A", 0), ("S", 0), ("B", 2), ("S", 0), ("A", 1),
               ("Q", 1), ("P", 2), ("B", 3), ("Q", 3)]
    positives = 0
    for w in (4, 5, 7):
        for pattern in (direct, divided):
            factors = [call(LABELS[label], 1 << (role * w + role), w) for label, role in pattern]
            expected = endpoint(w)
            require(word(factors, w) == expected == entry_engine(factors, w), "positive endpoint")
            positives += 1
            # At w>4, the temporary scalar mixing uses dirty role w-1.
            mixed = []
            for label, role in pattern:
                other = w - 1 if w > 4 else (role + 1) % w
                g = unit(w) ^ (1 << (other * w + role))
                n = mul_bits(mul_bits(g, 1 << (role * w + role), w), g, w)
                mixed.extend([{ZERO: g}, call(LABELS[label], n, w), {ZERO: g}])
            require(word(mixed, w) == expected == entry_engine(mixed, w), "free-mixing endpoint")
            positives += 1
    w = 2
    n, k = 1, 3
    bad = [call((0, 0, 1), n, w), call((0, 0, 2), k, w), call((0, 0, 1), n, w)]
    require(bool(odd_part(word(bad, w))), "noncommuting middle escaped detection")
    require(word(bad, w) != word([bad[1], call((0, 0, 2), n, w)], w), "bad contraction accepted")
    require(bool(odd_part(word([bad[0]], w))), "single odd call escaped detection")
    unequal = [call((0, 0, 1), 1, w), call((0, 0, 1), 8, w)]
    require(bool(odd_part(word(unequal, w))), "unequal projectors escaped detection")
    require(word([call((0, 0, -1), n, w), call((0, 0, 1), n, w)], w)
            == {ZERO: unit(w)}, "inverse pair failed")
    nonprojector = 2
    require(word([call((0, 0, 1), nonprojector, w)] * 2, w)
            != call((0, 0, 2), nonprojector, w), "idempotence negative control")
    # Equal projectors are required only after normalization: a free middle
    # map can intertwine different projectors while preserving contraction.
    g = unit(w) ^ 4
    p = mul_bits(mul_bits(g, n, w), g, w)
    require(p != n, "free-middle fixture is trivial")
    free_middle = [call((0, 0, 1), p, w), {ZERO: g}, call((0, 0, 1), n, w)]
    require(not odd_part(word(free_middle, w)), "free-middle parity")
    require(word(free_middle, w) == word([{ZERO: g}, call((0, 0, 2), n, w)], w)
            == entry_engine(free_middle, w), "free-middle contraction")
    w = 5
    factors = [call(LABELS[label], 1 << (role * w + role), w) for label, role in divided]
    for i in range(len(factors)):
        require(word(factors[:i] + factors[i+1:], w) != endpoint(w), "deleted call accepted")
    for i, (label, role) in enumerate(divided):
        if label == "S":
            altered = factors[:]
            altered[i] = call(LABELS["P"], 1 << (role * w + role), w)
            require(word(altered, w) != endpoint(w), "half-frame mutation accepted")
    rejection(lambda: authenticate_bytes((ROOT / SOURCE).read_bytes() + b"\n"), "source mutation")
    return {"positive_endpoints_two_engines": positives, "widths": [4, 5, 7],
            "single_call_deletions_rejected": 9, "half_frame_replacements_rejected": 2,
            "other_controls": ["noncommuting middle", "single odd call", "unequal projectors",
                               "inverse-pair identity", "non-idempotent", "free-middle intertwiner",
                               "source mutation"]}


def compute():
    check_source()
    return {"schema": "bit-two-use-lattice-descent/1", "source_sha256": SOURCE_SHA256,
            "candidate": candidate_checks(), "descent_regressions": descent_regressions(),
            "controls": construction_controls(),
            "scope": "Finite exact regression evidence for README's all-finite-width proof; no new kappa."}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main():
    require(len(sys.argv) == 1, "no arguments accepted; verification never regenerates evidence")
    actual = compute()
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    require(canonical(actual) == canonical(expected), "RESULT.json differs from recomputed evidence")
    print("PASS_BIT_TWO_USE_LATTICE_DESCENT profile=1,3,0,1,1,2 raw_characters=8 descent_rank=2<4")


if __name__ == "__main__":
    main()
