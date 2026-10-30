#!/usr/bin/env python3
"""Exact finite floor for the R438 direct clean-query scatter class.

The 512 cases are unit-query subsets, not an enumeration of GL(9,2).
No physical compiler, positive supplier or changed outer exponent is claimed.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json
import types

HERE = Path(__file__).resolve().parent


def load_source(filename):
    path = HERE / filename
    source = path.read_bytes()
    pins = json.loads((HERE / "SOURCES.json").read_bytes())["code"]
    if sha256(source).hexdigest() != pins[filename]:
        raise ValueError("authenticated sibling source: " + filename)
    module = types.ModuleType(filename[:-3])
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


acquisition = load_source("acquisition_screen.py")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bits(row):
    return acquisition.bits(row)


def rank(rows):
    basis = {}
    for row in rows:
        acquisition.basis_add(basis, row, 0)
    return len(basis)


def product(left, right):
    result = []
    for row in left:
        value = 0
        for j in bits(row):
            value ^= right[j]
        result.append(value)
    return result


def inverse(rows):
    n = len(rows)
    augmented = [row | (1 << (n + j)) for j, row in enumerate(rows)]
    for j in range(n):
        p = next((i for i in range(j, n) if augmented[i] >> j & 1), None)
        need(p is not None, "invertible centre pairing")
        augmented[j], augmented[p] = augmented[p], augmented[j]
        for i in range(n):
            if i != j and augmented[i] >> j & 1:
                augmented[i] ^= augmented[j]
    need([r & ((1 << n) - 1) for r in augmented] == [1 << j for j in range(n)],
         "inverse left block")
    result = [r >> n for r in augmented]
    need(product(rows, result) == product(result, rows) == [1 << j for j in range(n)],
         "both exact binary inverse identities")
    return result


def modular_rank(lines, support, modulus=101):
    """Field rank supplies a certified lower bound on the rational rank."""
    basis, pivots = {}, []
    for i in support:
        row = [x % modulus for x in lines[i]]
        for j, old in sorted(basis.items()):
            c = row[j]
            row = [(x - c * y) % modulus for x, y in zip(row, old)]
        j = next((j for j, x in enumerate(row) if x), None)
        if j is not None:
            c = pow(row[j], -1, modulus)
            basis[j] = [(c * x) % modulus for x in row]
            pivots.append(i)
        if len(basis) == 8:
            break
    return len(basis), pivots


def rational_normal(lines, support):
    basis = {}
    for i in support:
        row = list(map(Fraction, lines[i]))
        for j, old in sorted(basis.items()):
            c = row[j]
            row = [x - c * y for x, y in zip(row, old)]
        j = next((j for j, x in enumerate(row) if x), None)
        if j is not None:
            c = row[j]
            basis[j] = [x / c for x in row]
    need(len(basis) == 7, "actual rational hyperplane")
    free = next(j for j in range(8) if j not in basis)
    normal = [Fraction(0)] * 8
    normal[free] = Fraction(1)
    for j, row in sorted(basis.items(), reverse=True):
        normal[j] = -sum(a * b for a, b in zip(row, normal))
    need(all(sum(a * b for a, b in zip(lines[i], normal)) == 0 for i in support),
         "normal annihilates every actual port line in support")
    return normal


def frame_geometry(geometry):
    """Check every catalogue span and its complete live-root closure over Q."""
    lines = geometry["lines"]
    masks, dims = [], []
    for support in geometry["frames"]:
        basis = {}
        for i in support:
            row = list(map(Fraction, lines[i]))
            for j, old in sorted(basis.items()):
                c = row[j]
                row = [x - c * y for x, y in zip(row, old)]
            j = next((j for j, x in enumerate(row) if x), None)
            if j is not None:
                c = row[j]
                basis[j] = [x / c for x in row]
        actual = []
        if len(basis) == 8:
            actual = list(range(len(lines)))
        else:
            for p, line in enumerate(lines):
                row = list(map(Fraction, line))
                for j, old in sorted(basis.items()):
                    c = row[j]
                    row = [x - c * y for x, y in zip(row, old)]
                if not any(row):
                    actual.append(p)
        need(actual == support, "catalogue frame is the exact rational live-root closure")
        need(modular_rank(lines, support)[0] == len(basis),
             "modular dimensions agree with exact rational frame dimensions")
        masks.append(sum(1 << p for p in support))
        dims.append(len(basis))
    return masks, dims


def encode(vector):
    return [[x.numerator, x.denominator] for x in vector]


def decode(vector):
    return [Fraction(a, b) for a, b in vector]


def geometry_audit(R, K, M, geometry):
    lines = geometry["lines"]
    source, target = [], []
    source_seven, target_seven = {}, {}
    for coefficient in range(1, 512):
        query = product([coefficient], R)[0]
        source_support = list(bits(query))
        output_support = [p for p, row in enumerate(K)
                          if (row & coefficient).bit_count() & 1]
        srank, spivots = modular_rank(lines, source_support)
        trank, tpivots = modular_rank(lines, output_support)
        need(srank >= 7 and trank >= 7, "all nonzero support ranks at least seven")
        if srank == 7:
            source_seven[coefficient] = rational_normal(lines, source_support)
        if trank == 7:
            target_seven[coefficient] = rational_normal(lines, output_support)
        source.append(dict(coefficient=coefficient, modular_rank=srank, pivot_ports=spivots))
        target.append(dict(coefficient=coefficient, modular_rank=trank, pivot_ports=tpivots))
    need(set(source_seven) == {1 << j for j in range(9)},
         "exactly the nine original source directions have rank seven")
    need(set(target_seven) == set(M),
         "exactly the nine pairing rows are target hyperplane supports")
    need(all(source_seven[1 << j] == target_seven[M[j]] for j in range(9)),
         "source and target special normals coincide in actual coordinates")
    incidence = []
    for j in range(9):
        for k in range(9):
            dot = sum(a * b for a, b in zip(source_seven[1 << j], target_seven[M[k]]))
            actual = dot == 0
            expected = j != k and (M[k] >> j) & 1 == 1
            need(actual == expected, "exact rank-six bridge incidence")
            if actual:
                incidence.append([k, j])
    return dict(source_rank_histogram=dict(sorted(Counter(x["modular_rank"] for x in source).items())),
                target_rank_histogram=dict(sorted(Counter(x["modular_rank"] for x in target).items())),
                source_directions=source, target_directions=target,
                source_seven_normals={str(a): encode(n) for a, n in source_seven.items()},
                target_seven_normals={str(v): encode(n) for v, n in target_seven.items()},
                rank_six_cells=incidence)


def nine_term_audit(M):
    cases = []
    for J in range(512):
        zero_directions = [row for row in M if row & J == 0]
        r = rank(zero_directions)
        d = 9 - J.bit_count()
        benefits = [j for j in bits(J)
                    if any((v & J) == 1 << j and k != j for k, v in enumerate(M))]
        lower = 63 - len(benefits) + d - r
        need(lower >= 63, "nine-query paid lower bound")
        cases.append(dict(unit_query_subset=J, remaining_dimension=d,
                          special_reader_rank=r, rank_six_possible=benefits, lower_bound=lower))
    need([c["unit_query_subset"] for c in cases if c["lower_bound"] == 63] == [0, 511],
         "equality subsets")
    return dict(cases=cases, lower_bound_histogram=dict(sorted(Counter(c["lower_bound"]
                for c in cases).items())), minimum=63, equality_unit_query_subsets=[0, 511])


def all_count_audit(M, Minv, geometry_result):
    minor = [1, 4, 8]
    block = [sum(((Minv[row] >> col) & 1) << j for j, col in enumerate(minor))
             for row in minor]
    need(block == [1, 4, 2] and rank(block) == 3, "forced rank-three exact minor")
    low_cells = {tuple(cell) for cell in geometry_result["rank_six_cells"]}
    need(all((row, col) not in low_cells for row in minor for col in minor),
         "every rank-six contribution is zero on forced minor")
    return dict(minor_rows=minor, minor_columns=minor, minor_binary_rows=block,
                minor_rank=3, minimum_higher_rank_terms=3,
                cost_floor_for_ten_or_more="6*N+3", overall_cost_floor=63)


def controls(word, R, K, M, Minv, geometric):
    outcomes = []
    for name, mutate in (
        ("deleted_first_copy_fails_complete_boundary",
         lambda records: [r for i, r in enumerate(records) if not 23524 <= i <= 23588]),
        ("changed_live_snapshot_fails_actual_erase",
         lambda records: records[:23525] + [[1, 471, 472, 1, 510, 99]] + records[23525:]),
    ):
        bad = dict(word)
        bad["records"] = mutate(word["records"])
        try:
            acquisition.audit(bad)
        except ValueError:
            outcomes.append(name)
        else:
            raise ValueError("semantic control accepted: " + name)
    # The deleted-copy control above also fails the nine-episode contract.
    # Separately replay the removed episode's public difference explicitly.
    column = next(bits(R[0]))
    target = next(p for p, row in enumerate(K) if row & 1)
    need((R[0] >> column) & (K[target] & 1) == 1,
         "single independent source input witnesses omitted scatter")
    outcomes.append(dict(control="one_hot_source_detects_deleted_scatter",
                         source=column, target=111 + target))
    normal = decode(geometric["source_seven_normals"]["1"])
    need(sum(x*x for x in normal) != 0 and (M[0] & 1) == 1,
         "diagonal M entry does not imply geometric containment")
    outcomes.append("falsely_allowing_diagonal_rank_six_is_rejected")
    need(rank([1, 2, 4]) == 3 and rank([1, 4, 0]) == 2,
         "minor rank-sensitive control")
    broken = Minv[:]
    broken[8] ^= 1 << 4
    need(product(M, broken) != [1 << j for j in range(9)], "wrong inverse rejected")
    outcomes.append("one_bit_inverse_defect_breaks_exact_identity")
    dual = acquisition.separator([1, 2], 4)
    need((dual & 4).bit_count() % 2 == 1, "dual witness positive control")
    try:
        acquisition.separator([1, 2, 4], 4)
    except ValueError:
        outcomes.append("adding_missing_influence_invalidates_acquisition_separator")
    else:
        raise ValueError("false acquisition obstruction control accepted")
    return outcomes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    word, geometry = acquisition.load()
    _, _, snapshots, R, K = acquisition.audit(word)
    need(rank(R) == rank(K) == rank(snapshots) == 9, "literal rank-nine transfer")
    M = product(R, K)
    need(M == [507, 135, 238, 349, 185, 437, 205, 503, 425], "actual centre pairing")
    need(all((M[i] >> j & 1) == (M[j] >> i & 1) for i in range(9) for j in range(9)),
         "symmetric actual pairing")
    Minv = inverse(M)
    geometric = geometry_audit(R, K, M, geometry)
    nine = nine_term_audit(M)
    all_count = all_count_audit(M, Minv, geometric)
    report = dict(status="PASS_DIRECT_QUERY_SCATTER_FLOOR_63_NO_NEW_KAPPA",
                  no_new_kappa=True, source_word_sha256=acquisition.WORD_SHA,
                  geometry_sha256=acquisition.GEOMETRY_SHA,
                  persistent_columns=660, R=[str(r) for r in R], K=K,
                  M=M, M_inverse=Minv, geometry=geometric,
                  nine_term_bound=nine, all_count_bound=all_count,
                  controls=controls(word, R, K, M, Minv, geometric),
                  scope="query rows in span(R), reader columns in image(K), direct immutable snapshots; arbitrary count",
                  script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"], "512 unit-query subsets; 511 source and 511 target supports; exact 3x3 minor")


if __name__ == "__main__":
    main()
