#!/usr/bin/env python3
"""Exact screen of subset-sum basis mixing across pairs of selected planes."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import itertools
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE_PATH = "research/community-frontier1094-audit/selected-replay.tar.gz"
CERT_PATH = "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
MEMBER_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
CERT_SHA256 = "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1"
PORTS = 112
DIMENSION = 9
PAIRS = 56
BASELINE_COST = 8


class CheckFailure(ValueError):
    """A declared source, algebra or receipt check failed."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_inputs() -> tuple[list[int], list[tuple[int, int]]]:
    archive = (ROOT / ARCHIVE_PATH).read_bytes()
    need(digest(archive) == ARCHIVE_SHA256, "selected archive SHA256")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as source:
        member = source.extractfile(MEMBER)
        need(member is not None, "selected data-phase member missing")
        payload = member.read()
    need(digest(payload) == MEMBER_SHA256, "selected data-phase SHA256")

    cert_bytes = (ROOT / CERT_PATH).read_bytes()
    need(digest(cert_bytes) == CERT_SHA256, "paired-plane certificate SHA256")
    certificate = json.loads(cert_bytes)
    need(certificate["selected_archive_sha256"] == ARCHIVE_SHA256,
         "certificate archive binding")
    need(certificate["selected_payload_sha256"] == MEMBER_SHA256,
         "certificate payload binding")
    data = json.loads(payload)
    recipes = sorted(data["recipes"], key=lambda row: row["port"])
    need(data["ports"] == PORTS and len(recipes) == PORTS, "selected port count")
    need([row["port"] for row in recipes] == list(range(PORTS)), "port ordering")
    labels = [row["q"] for row in recipes]
    need(len(set(labels)) == PORTS, "selected labels are not distinct")
    need(all(type(value) is int and 0 < value < (1 << DIMENSION) for value in labels),
         "selected label domain")
    matching = tuple(tuple(edge) for edge in certificate["matching"])
    need(len(matching) == PAIRS, "matching edge count")
    flattened = [port for edge in matching for port in edge]
    need(all(len(edge) == 2 and edge[0] != edge[1] for edge in matching),
         "matching edge shape")
    need(sorted(flattened) == list(range(PORTS)), "matching is not a port partition")
    need(all(dot(labels[i], labels[i]) == 1 and dot(labels[j], labels[j]) == 1
             and dot(labels[i], labels[j]) == 0 for i, j in matching),
         "matching edge is not a Gram-I2 plane")
    return labels, matching


def dot(left: int, right: int) -> int:
    return (left & right).bit_count() & 1


def determinant(matrix: list[list[int]]) -> int:
    size = len(matrix)
    total = 0
    for permutation in itertools.permutations(range(size)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(size) for j in range(i + 1, size))
        product = 1
        for row, column in enumerate(permutation):
            product *= matrix[row][column]
        total += -product if inversions & 1 else product
    return total


def adjugate(matrix: list[list[int]]) -> tuple[int, list[list[int]]]:
    det = determinant(matrix)
    cofactors = []
    for row in range(4):
        cofactor_row = []
        for column in range(4):
            minor = [[matrix[r][c] for c in range(4) if c != column]
                     for r in range(4) if r != row]
            value = determinant(minor)
            cofactor_row.append(-value if (row + column) & 1 else value)
        cofactors.append(cofactor_row)
    return det, [list(row) for row in zip(*cofactors)]


def binary_rank(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for value in rows:
        row = value
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def binary_rank_columns(rows: list[int], width: int) -> int:
    columns = [sum(((row >> column) & 1) << index
                   for index, row in enumerate(rows)) for column in range(width)]
    pivots: dict[int, int] = {}
    for value in columns:
        column = value
        while column:
            pivot = column.bit_length() - 1
            if pivot in pivots:
                column ^= pivots[pivot]
            else:
                pivots[pivot] = column
                break
    return len(pivots)


def plane_mask(port_support: int) -> int:
    return (1 if port_support & 0b0011 else 0) | (2 if port_support & 0b1100 else 0)


def support_pattern(matrix: list[list[int]], adj: list[list[int]]) -> tuple[tuple[int, int], ...]:
    pattern = []
    for term in range(4):
        source = sum(matrix[row][term] << row for row in range(4))
        reader = sum(bool(adj[term][column]) << column for column in range(4))
        pattern.append((plane_mask(source), plane_mask(reader)))
    need(all(source and reader for source, reader in pattern), "zero factor in invertible basis")
    return tuple(pattern)


def basis_patterns() -> tuple[dict[tuple[tuple[int, int], ...], int], int, int]:
    representatives: dict[tuple[tuple[int, int], ...], int] = {}
    invertible_count = 0
    maximum_determinant = 0
    for encoded in range(1 << 16):
        matrix = [[(encoded >> (4 * row + column)) & 1 for column in range(4)]
                  for row in range(4)]
        det, adj = adjugate(matrix)
        if not det:
            continue
        invertible_count += 1
        maximum_determinant = max(maximum_determinant, abs(det))
        for row in range(4):
            for column in range(4):
                product = sum(matrix[row][k] * adj[k][column] for k in range(4))
                need(product == (det if row == column else 0), "P adj(P) identity")
                product = sum(adj[row][k] * matrix[k][column] for k in range(4))
                need(product == (det if row == column else 0), "adj(P) P identity")
        pattern = support_pattern(matrix, adj)
        representatives.setdefault(pattern, encoded)
    need(invertible_count == 22560, "0/1 rationally invertible matrix count")
    need(len(representatives) == 391, "distinct support-pattern count")
    need(maximum_determinant == 3, "maximum determinant control")
    return representatives, invertible_count, maximum_determinant


def pairing_costs(labels: list[int], planes: tuple[tuple[int, int], ...],
                  first: int, second: int) -> dict[tuple[int, int], int]:
    costs = {}
    for source in (1, 2, 3):
        source_ports = []
        if source & 1:
            source_ports.extend(planes[first])
        if source & 2:
            source_ports.extend(planes[second])
        for reader in (1, 2, 3):
            reader_ports = []
            if reader & 1:
                reader_ports.extend(planes[first])
            if reader & 2:
                reader_ports.extend(planes[second])
            rows = [sum(dot(labels[i], labels[j]) << column
                        for column, j in enumerate(reader_ports)) for i in source_ports]
            rank = binary_rank(rows)
            need(rank == binary_rank_columns(rows, len(reader_ports)),
                 "row/column pairing-rank disagreement")
            costs[(source, reader)] = rank
    need(costs[(1, 1)] == costs[(2, 2)] == 2, "matched-plane diagonal charge")
    return costs


def screen(labels: list[int], planes: tuple[tuple[int, int], ...],
           patterns: dict[tuple[tuple[int, int], ...], int]) -> dict:
    pair_minima = Counter()
    minima_by_pair = []
    best_cost = 1 << 30
    best_example = None
    tested = 0
    for first, second in itertools.combinations(range(len(planes)), 2):
        costs = pairing_costs(labels, planes, first, second)
        baseline = 2 * costs[(1, 1)] + 2 * costs[(2, 2)]
        need(baseline == BASELINE_COST, "separate-decoder baseline")
        local_best = 1 << 30
        local_ties = 0
        for pattern in patterns:
            value = sum(costs[term] for term in pattern)
            tested += 1
            if value < local_best:
                local_best, local_ties = value, 1
            elif value == local_best:
                local_ties += 1
            if value < best_cost:
                best_cost = value
                best_example = {"plane_indices": [first, second],
                                "ports": [list(planes[first]), list(planes[second])],
                                "term_pairing_ranks": [costs[term] for term in pattern],
                                "support_pattern": [list(term) for term in pattern],
                                "representative_matrix_bits": patterns[pattern]}
        pair_minima[str(local_best)] += 1
        minima_by_pair.append(local_best)
        need(local_best >= baseline, "joint basis improved the two-plane baseline")
        need(local_ties > 0, "no minimum support pattern")
    need(len(minima_by_pair) == 1540, "plane-pair census size")
    need(best_cost == BASELINE_COST, "global minimum differs from baseline")
    return {
        "plane_pairs": len(minima_by_pair),
        "support_patterns_per_pair": len(patterns),
        "pair_pattern_cases": tested,
        "minimum_copy_cost_histogram": dict(sorted(pair_minima.items(), key=lambda row: int(row[0]))),
        "minimum_copy_cost": best_cost,
        "baseline_copy_cost": BASELINE_COST,
        "strict_improvements": 0,
        "best_example": best_example,
        "pair_minima_sha256": digest(bytes(minima_by_pair)),
    }


def control_checks(labels: list[int], planes: tuple[tuple[int, int], ...],
                   patterns: dict[tuple[tuple[int, int], ...], int]) -> int:
    identity = ((1, 1), (1, 1), (2, 2), (2, 2))
    need(identity in patterns, "identity basis pattern")
    costs = pairing_costs(labels, planes, 0, 1)
    need(sum(costs[term] for term in identity) == BASELINE_COST, "identity positive control")
    swap = [[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]
    swap_det, swap_adj = adjugate(swap)
    permuted_pattern = support_pattern(swap, swap_adj)
    need(swap_det != 0 and Counter(permuted_pattern) == Counter(identity),
         "permutation basis control")
    need(sum(costs[term] for term in permuted_pattern) == BASELINE_COST,
         "permutation baseline control")
    shear_found = any(pattern != identity and
                      sum(costs[term] for term in pattern) >= BASELINE_COST
                      for pattern in patterns)
    need(shear_found, "nontrivial basis control")
    singular = [[1, 0, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    need(determinant(singular) == 0, "singular matrix rejection control")
    need(len(patterns) == 391 and len(set(patterns)) == 391, "support deduplication control")
    return 5


def compute() -> dict:
    labels, planes = load_inputs()
    patterns, invertible_count, max_det = basis_patterns()
    result = screen(labels, planes, patterns)
    controls = control_checks(labels, planes, patterns)
    return {
        "schema": "joint-plane-binary-basis-screen-v1",
        "source_archive_sha256": ARCHIVE_SHA256,
        "selected_payload_sha256": MEMBER_SHA256,
        "plane_matching_certificate_sha256": CERT_SHA256,
        "port_count": len(labels),
        "matched_planes": len(planes),
        "basis_domain": "all 4x4 {0,1} matrices invertible over Q",
        "invertible_basis_matrices": invertible_count,
        "maximum_absolute_determinant": max_det,
        "distinct_source_reader_support_patterns": len(patterns),
        "controls_rejected_or_passed": controls,
        **result,
        "scope_limits": [
            "arbitrary rational or complex encoder entries",
            "overcomplete factorizations with more than four scalar messages",
            "joint mixing across three or more matched planes",
            "multi-array native primitives and physical routing/restoration"
        ],
        "selected_kappa_changed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = compute()
    output = PACKAGE / "RESULT.json"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        output.write_text(encoded, encoding="utf-8")
    else:
        need(output.exists(), "RESULT.json missing; run with --write")
        need(output.read_text(encoding="utf-8") == encoded, "RESULT.json differs from exact replay")
    print("PASS_JOINT_PLANE_BINARY_BASIS_SCREEN "
          f"matrices={result['invertible_basis_matrices']} "
          f"patterns={result['distinct_source_reader_support_patterns']} "
          f"plane_pairs={result['plane_pairs']} min_copy={result['minimum_copy_cost']} "
          f"strict_improvements={result['strict_improvements']} controls={result['controls_rejected_or_passed']}")


if __name__ == "__main__":
    main()
