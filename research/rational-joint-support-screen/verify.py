#!/usr/bin/env python3
"""Exact generic-rational support screen for joint bases on two planes."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import itertools
import json
import shutil
from pathlib import Path
import subprocess
import tarfile
import tempfile

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
PLANE_COUNT = 56
BASELINE_COST = 8
PERMUTATIONS = tuple(itertools.permutations(range(4)))


class CheckFailure(ValueError):
    """A source, structural algebra, or receipt check failed."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dot(left: int, right: int) -> int:
    return (left & right).bit_count() & 1


def load_inputs() -> tuple[list[int], tuple[tuple[int, int], ...]]:
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
    need(len(matching) == PLANE_COUNT, "matching edge count")
    flattened = [port for edge in matching for port in edge]
    need(all(len(edge) == 2 and edge[0] != edge[1] for edge in matching),
         "matching edge shape")
    need(sorted(flattened) == list(range(PORTS)), "matching is not a port partition")
    need(all(dot(labels[i], labels[i]) == 1 and dot(labels[j], labels[j]) == 1
             and dot(labels[i], labels[j]) == 0 for i, j in matching),
         "matching edge is not a Gram-I2 plane")
    return labels, matching


def plane_mask(port_support: int) -> int:
    return (1 if port_support & 0b0011 else 0) | (2 if port_support & 0b1100 else 0)


def has_perfect_matching(rows: tuple[int, ...] | list[int],
                         row_indices: tuple[int, ...],
                         column_indices: tuple[int, ...]) -> bool:
    """Whether the indicated bipartite support graph has a perfect matching."""
    for columns in itertools.permutations(column_indices):
        if all((rows[row] >> column) & 1
               for row, column in zip(row_indices, columns)):
            return True
    return False


def has_perfect_matching_dp(rows: tuple[int, ...],
                            row_indices: tuple[int, ...],
                            column_indices: tuple[int, ...]) -> bool:
    """Independent subset-DP check of structural nonsingularity."""
    reachable = {0}
    for row in row_indices:
        next_reachable = set()
        for used in reachable:
            for column in column_indices:
                bit = 1 << column
                if not used & bit and (rows[row] & bit):
                    next_reachable.add(used | bit)
        reachable = next_reachable
    target = sum(1 << column for column in column_indices)
    return target in reachable


def generic_inverse_pattern(rows: tuple[int, ...]) -> tuple[tuple[int, int], ...] | None:
    """Return the generic P/P^-1 plane-support signature, if P is structural full rank."""
    all_rows = (0, 1, 2, 3)
    all_columns = (0, 1, 2, 3)
    if not has_perfect_matching(rows, all_rows, all_columns):
        return None

    pattern = []
    for message in range(4):
        source_ports = sum(((rows[row] >> message) & 1) << row for row in all_rows)
        reader_ports = 0
        for output in all_rows:
            minor_rows = tuple(row for row in all_rows if row != output)
            minor_columns = tuple(column for column in all_columns if column != message)
            if has_perfect_matching(rows, minor_rows, minor_columns):
                reader_ports |= 1 << output
        source = plane_mask(source_ports)
        reader = plane_mask(reader_ports)
        need(source != 0 and reader != 0, "structurally invertible basis has empty message")
        pattern.append((source, reader))
    return tuple(pattern)


def generic_patterns() -> tuple[set[tuple[tuple[int, int], ...]], int]:
    patterns = set()
    full_rank_supports = 0
    for encoded in range(1 << 16):
        rows = tuple((encoded >> (4 * row)) & 0b1111 for row in range(4))
        structural = has_perfect_matching(rows, (0, 1, 2, 3), (0, 1, 2, 3))
        need(structural == has_perfect_matching_dp(rows, (0, 1, 2, 3), (0, 1, 2, 3)),
             "permutation and subset-DP structural-rank disagreement")
        pattern = generic_inverse_pattern(rows)
        if pattern is not None:
            full_rank_supports += 1
            patterns.add(pattern)
    need(full_rank_supports > 0 and len(patterns) > 0, "empty generic support census")
    return patterns, full_rank_supports


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


def actual_inverse_pattern(matrix: list[list[int]],
                           adj: list[list[int]]) -> tuple[tuple[int, int], ...]:
    pattern = []
    for message in range(4):
        source_ports = sum(bool(matrix[row][message]) << row for row in range(4))
        reader_ports = sum(bool(adj[message][output]) << output for output in range(4))
        pattern.append((plane_mask(source_ports), plane_mask(reader_ports)))
    return tuple(pattern)


def binary_controls(generic: set[tuple[tuple[int, int], ...]]) -> tuple[int, set]:
    binary_count = 0
    binary_patterns = set()
    for encoded in range(1 << 16):
        matrix = [[(encoded >> (4 * row + column)) & 1 for column in range(4)]
                  for row in range(4)]
        det, adj = adjugate(matrix)
        if not det:
            continue
        binary_count += 1
        binary_patterns.add(actual_inverse_pattern(matrix, adj))
        # Every nonzero evaluated minor must be structurally permitted.
        rows = tuple(sum(matrix[row][column] << column for column in range(4))
                     for row in range(4))
        structural = generic_inverse_pattern(rows)
        need(structural is not None, "numeric invertibility without structural matching")
    need(binary_count == 22560, "invertible 0/1 matrix control")
    need(len(binary_patterns) == 391, "binary actual support-pattern control")
    identity = ((1, 1), (1, 1), (2, 2), (2, 2))
    need(identity in generic and identity in binary_patterns, "identity basis control")
    full_rows = (0b1111, 0b1111, 0b1111, 0b1111)
    need(generic_inverse_pattern(full_rows) == ((3, 3),) * 4,
         "generic dense-matrix control")
    singular_rows = (0b0001, 0b0001, 0b0100, 0b1000)
    need(generic_inverse_pattern(singular_rows) is None, "structural singularity control")
    return binary_count, binary_patterns


def encode_pattern(pattern: tuple[tuple[int, int], ...]) -> int:
    return sum((source * 4 + reader) << (4 * term)
               for term, (source, reader) in enumerate(pattern))


def ternary_artifact(generic: set[tuple[tuple[int, int], ...]]) -> dict:
    """Validate every signed-ternary witness in the optional exhaustive C receipt."""
    artifact = PACKAGE / "TERNARY-SCREEN.txt"
    source = PACKAGE / "ternary_screen.c"
    data = artifact.read_bytes()
    source_bytes = source.read_bytes()
    lines = data.decode("ascii").splitlines()
    need(lines, "ternary screen receipt is empty")
    header = lines[0].split()
    need(header[0] == "TERNARY_SCREEN_V1", "ternary screen receipt schema")
    fields = dict(item.split("=", 1) for item in header[1:])
    expected = {"total": "43046721", "invertible": "27947520", "signatures": "439",
                "binary_invertible": "22560", "binary_signatures": "391"}
    need(fields == expected, "ternary screen receipt counts")

    signatures = set()
    for line in lines[1:]:
        fields = line.split()
        need(len(fields) == 17, "ternary witness row shape")
        signature = int(fields[0], 16)
        need(signature not in signatures, "duplicate ternary signature")
        values = [int(value) for value in fields[1:]]
        need(all(value in (-1, 0, 1) for value in values), "non-ternary witness value")
        matrix = [values[4 * row:4 * row + 4] for row in range(4)]
        determinant_value, adj = adjugate(matrix)
        need(determinant_value != 0, "singular ternary witness")
        actual = actual_inverse_pattern(matrix, adj)
        need(encode_pattern(actual) == signature, "ternary witness signature mismatch")
        signatures.add(signature)
    need(len(signatures) == 439, "ternary signature witness count")
    need(signatures == {encode_pattern(pattern) for pattern in generic},
         "ternary and generic rational signature sets differ")

    compiler = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    replayed = False
    if compiler:
        with tempfile.TemporaryDirectory(prefix="joint-plane-ternary-") as temporary:
            executable = Path(temporary) / "ternary-screen"
            compiled = subprocess.run(
                [compiler, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror",
                 str(source), "-o", str(executable)],
                capture_output=True, check=False, timeout=30)
            need(compiled.returncode == 0,
                 "C11 ternary screen compilation failed: "
                 + compiled.stderr.decode("utf-8", errors="replace"))
            run = subprocess.run([str(executable)], capture_output=True,
                                 check=False, timeout=60)
            need(run.returncode == 0, "C11 ternary screen failed")
            need(run.stdout == data, "C11 ternary screen differs from receipt")
            replayed = True
    return {
        "total_matrices": 43046721,
        "invertible_matrices": 27947520,
        "unique_signatures": len(signatures),
        "binary_invertible_matrices": 22560,
        "binary_signatures": 391,
        "signature_set_sha256": digest(b"".join(
            signature.to_bytes(2, "big") for signature in sorted(signatures))),
        "source_sha256": digest(source_bytes),
        "receipt_sha256": digest(data),
        "matches_generic_support_family": True,
        "c_replay_if_available": "required when a C11 compiler is available",
    }, replayed


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


def pair_costs(labels: list[int], planes: tuple[tuple[int, int], ...],
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
           patterns: set[tuple[tuple[int, int], ...]]) -> dict:
    histogram = Counter()
    minima = []
    best_cost = 1 << 30
    best_example = None
    cases = 0
    strict_improvements = 0
    for first, second in itertools.combinations(range(len(planes)), 2):
        costs = pair_costs(labels, planes, first, second)
        local_best = 1 << 30
        local_pattern = None
        for pattern in sorted(patterns):
            charge = sum(costs[term] for term in pattern)
            cases += 1
            if charge < local_best:
                local_best = charge
                local_pattern = pattern
        need(local_best <= BASELINE_COST, "identity baseline absent from generic family")
        need(local_pattern is not None, "no generic support pattern priced")
        strict_improvements += local_best < BASELINE_COST
        histogram[str(local_best)] += 1
        minima.append(local_best)
        if local_best < best_cost:
            best_cost = local_best
            best_example = {"plane_indices": [first, second],
                            "ports": [list(planes[first]), list(planes[second])],
                            "support_pattern": [list(term) for term in local_pattern]}
    need(len(minima) == 1540, "plane-pair census size")
    need(strict_improvements == 0, "joint support strictly improves the baseline")
    need(best_cost == BASELINE_COST, "global minimum differs from baseline")
    return {
        "plane_pairs": len(minima),
        "support_patterns_per_pair": len(patterns),
        "pair_pattern_cases": cases,
        "minimum_copy_cost_histogram": dict(sorted(histogram.items(), key=lambda row: int(row[0]))),
        "minimum_copy_cost": best_cost,
        "baseline_copy_cost": BASELINE_COST,
        "strict_improvements": strict_improvements,
        "best_example": best_example,
        "pair_minima_sha256": digest(bytes(minima)),
    }


def compute() -> dict:
    labels, planes = load_inputs()
    patterns, support_count = generic_patterns()
    binary_count, binary_patterns = binary_controls(patterns)
    ternary, _ = ternary_artifact(patterns)
    combined_patterns = patterns | binary_patterns
    result = screen(labels, planes, patterns)
    combined_result = screen(labels, planes, combined_patterns)
    need(result["minimum_copy_cost"] == combined_result["minimum_copy_cost"],
         "binary cancellation family changes the minimum")
    return {
        "schema": "generic-rational-joint-support-screen-v1",
        "source_archive_sha256": ARCHIVE_SHA256,
        "selected_payload_sha256": MEMBER_SHA256,
        "plane_matching_certificate_sha256": CERT_SHA256,
        "port_count": len(labels),
        "matched_planes": len(planes),
        "coefficient_domain": "generic rational nonzero coefficients on each {0,1} support",
        "structurally_invertible_support_matrices": support_count,
        "generic_source_reader_support_patterns": len(patterns),
        "binary_invertible_matrices": binary_count,
        "binary_actual_support_patterns": len(binary_patterns),
        "generic_binary_intersection_patterns": len(patterns & binary_patterns),
        "generic_only_patterns": len(patterns - binary_patterns),
        "binary_cancellation_only_patterns": len(binary_patterns - patterns),
        "generic_or_binary_pattern_union": len(combined_patterns),
        "controls_passed": 6,
        "signed_ternary_screen": ternary,
        **result,
        "generic_union_binary_screen": combined_result,
        "scope_limits": [
            "special rational assignments outside {-1,0,1} that create additional cofactor cancellations",
            "overcomplete factorizations with more than four scalar messages",
            "joint mixing across three or more matched planes",
            "coefficient arithmetic and scaling overhead in a native implementation",
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
        need(output.read_text(encoding="utf-8") == encoded,
             "RESULT.json differs from exact replay")
    has_c_compiler = any(shutil.which(name) for name in ("cc", "gcc", "clang"))
    ternary_status = "REPLAYED" if has_c_compiler else "RECEIPT_CHECKED_NO_C_COMPILER"
    print("PASS_GENERIC_RATIONAL_JOINT_SUPPORT_SCREEN "
          f"structural_supports={result['structurally_invertible_support_matrices']} "
          f"patterns={result['generic_source_reader_support_patterns']} "
          f"plane_pairs={result['plane_pairs']} min_copy={result['minimum_copy_cost']} "
          f"strict_improvements={result['strict_improvements']} ternary_c={ternary_status}")


if __name__ == "__main__":
    main()
