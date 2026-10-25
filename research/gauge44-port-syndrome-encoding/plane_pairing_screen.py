#!/usr/bin/env python3
"""Bounded screen for pairing repeated centre signatures into E8 planes."""
from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
WORD_MEMBER = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
WORD_SHA256 = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
PHASE_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PHASE_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
PREDECESSOR_CERTIFICATE = ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
PREDECESSOR_CERTIFICATE_SHA256 = "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1"
SEED = 20261018
TRIALS = 500
N = 9


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def edge(a: int, b: int) -> bool:
    return a != b and dot(a, b) == 0


def load_source():
    archive_bytes = ARCHIVE.read_bytes()
    need(hashlib.sha256(archive_bytes).hexdigest() == ARCHIVE_SHA256,
         "selected replay archive hash")
    with tarfile.open(ARCHIVE, "r:gz") as tf:
        word_bytes = tf.extractfile(WORD_MEMBER).read()
        phase_bytes = tf.extractfile(PHASE_MEMBER).read()
    need(hashlib.sha256(word_bytes).hexdigest() == WORD_SHA256,
         "selected canonical-word member hash")
    need(hashlib.sha256(phase_bytes).hexdigest() == PHASE_SHA256,
         "selected DATA-PHASES payload hash")
    word = json.loads(gzip.decompress(word_bytes))
    phases = json.loads(phase_bytes)
    recipes = sorted(phases["recipes"], key=lambda row: row["port"])
    q = [row["q"] for row in recipes]
    need(len(q) == 112 and word["ports"] == q, "selected port labels/order")
    return word, q


def scatter_classes(word):
    centers = word["centers"]
    center_index = {register: index for index, register in enumerate(centers)}
    scatter = [[0] * 8 for _ in range(112)]
    for op, src, dst, numerator, denominator, *_ in word["cut"]:
        need(op == "add" and 112 <= src < 224 and dst in center_index,
             "unexpected selected centre-cut instruction")
        need(denominator > 0 and 4 % denominator == 0,
             "unexpected selected centre coefficient denominator")
        scatter[src - 112][center_index[dst]] += numerator * (4 // denominator)
    groups = defaultdict(list)
    for index, row in enumerate(scatter):
        if any(row):
            groups[tuple(row)].append(index)
    classes = [indices for _, indices in sorted(groups.items(), key=lambda item: min(item[1]))]
    zeros = [index for index, row in enumerate(scatter) if not any(row)]
    need(Counter(map(len, classes)) == {3: 8, 4: 16} and len(zeros) == 24,
         "selected repeated-signature class profile")
    return classes, zeros


def random_completion(remaining, adjacency, rng):
    dead = set()

    def visit(mask):
        if not mask:
            return ()
        if mask in dead:
            return None
        vertices = [i for i in remaining if (mask >> i) & 1]
        first = min(vertices, key=lambda i: (
            sum((mask >> j) & 1 for j in adjacency[i]), rng.random()))
        partners = [j for j in adjacency[first] if (mask >> j) & 1]
        rng.shuffle(partners)
        for partner in partners:
            suffix = visit(mask ^ (1 << first) ^ (1 << partner))
            if suffix is not None:
                return ((first, partner),) + suffix
        dead.add(mask)
        return None

    return visit(sum(1 << i for i in remaining))


def solve_identity_system(q, pairs):
    """Return one solution to sum A_k M_k A_k^T = I over F2, if any."""
    columns = []
    for i, j in pairs:
        for a in (q[i], q[j]):
            for b in (q[i], q[j]):
                column = 0
                for row in range(N):
                    if not ((a >> row) & 1):
                        continue
                    for col in range(N):
                        if (b >> col) & 1:
                            column |= 1 << (row * N + col)
                columns.append(column)

    variable_count = len(columns)
    rhs_bit = 1 << variable_count
    variable_mask = rhs_bit - 1
    pivots = {}
    for output in range(N * N):
        equation = 0
        for variable, column in enumerate(columns):
            if (column >> output) & 1:
                equation |= 1 << variable
        if output // N == output % N:
            equation |= rhs_bit
        while equation & variable_mask:
            pivot = (equation & variable_mask).bit_length() - 1
            if pivot in pivots:
                equation ^= pivots[pivot]
            else:
                pivots[pivot] = equation
                break
        if not equation & variable_mask and equation & rhs_bit:
            return None

    solution = 0
    for pivot in sorted(pivots):
        equation = pivots[pivot]
        value = (equation >> variable_count) & 1
        lower = equation & ((1 << pivot) - 1)
        value ^= (lower & solution).bit_count() & 1
        if value:
            solution |= 1 << pivot
    matrices = [sum(((solution >> (4 * k + bit)) & 1) << bit for bit in range(4))
                for k in range(len(pairs))]

    # Independent direct replay of all 81 entries of the claimed identity.
    for row in range(N):
        for col in range(N):
            value = 0
            for (i, j), matrix in zip(pairs, matrices):
                basis = (q[i], q[j])
                for a in range(2):
                    for b in range(2):
                        value ^= (((matrix >> (2 * a + b)) & 1) &
                                  ((basis[a] >> row) & 1) &
                                  ((basis[b] >> col) & 1))
            need(value == int(row == col), "solver output fails direct identity replay")
    return matrices


def matrix_rank(matrix):
    if matrix == 0:
        return 0
    a, b, c, d = ((matrix >> bit) & 1 for bit in range(4))
    return 2 if (a * d ^ b * c) else 1


def port_vector(q, vector):
    return sum(dot(label, vector) << index for index, label in enumerate(q))


def binary_rank(rows):
    basis = {}
    for value in rows:
        row = value
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def support_pairing_rank(q, row_mask, column_mask):
    row_indices = [i for i in range(len(q)) if (row_mask >> i) & 1]
    column_indices = [j for j in range(len(q)) if (column_mask >> j) & 1]
    rows = [sum(dot(q[i], q[j]) << col for col, j in enumerate(column_indices))
            for i in row_indices]
    return binary_rank(rows)


def complete_plane_closure(mask, pairs):
    """Include the whole matched plane whenever either port is touched."""
    closed = mask
    for i, j in pairs:
        if ((mask >> i) & 1) or ((mask >> j) & 1):
            closed |= (1 << i) | (1 << j)
    return closed


def verify_decoder(q, pairs, matrices):
    decoder_columns = []
    rank_counts = Counter()
    copy_ranks = Counter()
    reader_ranks = Counter()
    for (i, j), matrix in zip(pairs, matrices):
        rank = matrix_rank(matrix)
        rank_counts[rank] += 1
        if rank == 0:
            continue
        qi, qj = q[i], q[j]
        if rank == 1:
            x = y = None
            for candidate_x in range(1, 4):
                for candidate_y in range(1, 4):
                    candidate = sum((((candidate_x >> a) & 1) *
                                     ((candidate_y >> b) & 1)) << (2 * a + b)
                                    for a in range(2) for b in range(2))
                    if candidate == matrix:
                        x, y = candidate_x, candidate_y
                        break
                if x is not None:
                    break
            need(x is not None, "rank-one matrix does not factor")
            left = (qi if x & 1 else 0) ^ (qj if x & 2 else 0)
            right = (qi if y & 1 else 0) ^ (qj if y & 2 else 0)
            support_l, support_r = port_vector(q, left), port_vector(q, right)
            decoder_columns.append((support_l, support_r))
            expected_support_rank = 7
        else:
            left0, left1 = port_vector(q, qi), port_vector(q, qj)
            row0 = (matrix & 1, (matrix >> 1) & 1)
            row1 = ((matrix >> 2) & 1, (matrix >> 3) & 1)
            right0 = (qi if row0[0] else 0) ^ (qj if row0[1] else 0)
            right1 = (qi if row1[0] else 0) ^ (qj if row1[1] else 0)
            support_l = left0 | left1
            support_r = port_vector(q, right0) | port_vector(q, right1)
            need(support_l == support_r, "rank-two decoder changed its support")
            decoder_columns.extend(((left0, port_vector(q, right0)),
                                    (left1, port_vector(q, right1))))
            expected_support_rank = 9
        actual_copy_rank = support_pairing_rank(q, support_l, support_r)
        copy_ranks[(rank, actual_copy_rank)] += 1
        actual_reader_rank = support_pairing_rank(
            q, complete_plane_closure(support_l, pairs),
            complete_plane_closure(support_r, pairs))
        reader_ranks[(rank, actual_reader_rank)] += 1

    actual = [0] * len(q)
    for left, right in decoder_columns:
        for port in range(len(q)):
            if (left >> port) & 1:
                actual[port] ^= right
    expected = [sum(dot(q[port], q[other]) << other for other in range(len(q)))
                for port in range(len(q))]
    need(actual == expected, "full decoder identity D T^T = U U^T failed")
    return rank_counts, copy_ranks, reader_ranks, decoder_columns


def apply_c_sequence(start, sequence):
    state = {start: (1, 0)}
    for label in sequence:
        next_state = {}
        for address, (real, imag) in state.items():
            a = next_state.get(address, (0, 0))
            next_state[address] = (a[0] + real - imag, a[1] + real + imag)
            moved = address ^ label
            b = next_state.get(moved, (0, 0))
            next_state[moved] = (b[0] + real + imag, b[1] + imag - real)
        state = {address: value for address, value in next_state.items() if value != (0, 0)}
    return state


def verify_exact_plane_endpoints(q, pairs):
    checked = 0
    for i, j in pairs:
        qi, qj = q[i], q[j]
        need(edge(qi, qj), "plane endpoint received a non-edge")
        for start in range(1 << N):
            state = apply_c_sequence(start, [qi, qj, qi, qj])
            need(state == {start ^ qi ^ qj: (16, 0)},
                 f"exact plane endpoint failed at {(i, j)}, input {start}")
            checked += 1
    return checked


def run():
    word, q = load_source()
    classes, zeros = scatter_classes(word)
    adjacency = [[j for j, other in enumerate(q) if edge(value, other)]
                 for i, value in enumerate(q)]
    need({len(row) for row in adjacency} == {52}, "selected orthogonality graph degree")
    need(all(all(edge(q[i], q[j]) for i, j in combinations(indices, 2))
              for indices in classes),
         "a repeated-signature class is not pairwise orthogonal")

    rng = random.Random(SEED)
    solutions = []
    completed = 0
    for trial in range(TRIALS):
        fixed = []
        remaining = []
        for original in classes:
            indices = original[:]
            rng.shuffle(indices)
            while len(indices) >= 2:
                fixed.append((indices.pop(), indices.pop()))
            remaining.extend(indices)
        remaining.extend(zeros)
        need(len(fixed) == 40 and len(remaining) == 32,
             "within-class pair counts")
        completion = random_completion(remaining, adjacency, rng)
        need(completion is not None and len(completion) == 16,
             "could not complete residual ports to an orthogonal matching")
        pairs = tuple(fixed) + tuple(completion)
        need(len(pairs) == 56 and all(edge(q[i], q[j]) for i, j in pairs),
             "candidate is not a 56-plane orthogonal matching")
        completed += 1
        matrices = solve_identity_system(q, pairs)
        if matrices is not None:
            ranks, copy_ranks, reader_ranks, _ = verify_decoder(q, pairs, matrices)
            raw_cost = sum(rank * count for (_, rank), count in copy_ranks.items())
            reader_cost = sum(rank * count for (_, rank), count in reader_ranks.items())
            solutions.append((trial, reader_cost, raw_cost, ranks, copy_ranks,
                              reader_ranks, tuple(pairs), tuple(matrices)))

    need(completed == TRIALS, "not all sampled pairings completed")
    need(bool(solutions), "no sampled same-class pairing admits an identity factorization")
    best = min(solutions, key=lambda row: (row[1], row[2], sum(row[3].values())))
    best_pairs, best_matrices = best[6], best[7]
    checked_ranks, checked_copy_ranks, checked_reader_ranks = best[3], best[4], best[5]
    endpoint_cases = verify_exact_plane_endpoints(q, best_pairs)

    predecessor_bytes = PREDECESSOR_CERTIFICATE.read_bytes()
    need(hashlib.sha256(predecessor_bytes).hexdigest() == PREDECESSOR_CERTIFICATE_SHA256,
         "paired-plane predecessor certificate hash changed")
    predecessor = json.loads(predecessor_bytes)
    predecessor_pairs = tuple(tuple(pair) for pair in predecessor["matching"])
    predecessor_matrices = tuple(predecessor["plane_matrices_2bit_rows"])
    _, predecessor_raw, predecessor_reader, _ = verify_decoder(
        q, predecessor_pairs, predecessor_matrices)
    predecessor_raw_cost = sum(rank * count for (_, rank), count in
                                predecessor_raw.items())
    predecessor_reader_cost = sum(rank * count for (_, rank), count in
                                   predecessor_reader.items())
    need(predecessor_raw_cost == 126 and predecessor_reader_cost == 144,
         "predecessor raw/complete-plane reader controls changed")
    return {
        "status": "PASS_BOUNDED_SAME_CLASS_PLANE_SCREEN",
        "seed": SEED,
        "trials": TRIALS,
        "completed_orthogonal_matchings": completed,
        "same_signature_planes_per_trial": 40,
        "residual_planes_per_trial": 16,
        "identity_factorizations_found": len(solutions),
        "first_solution_trial": solutions[0][0],
        "best_sampled_solution_trial": best[0],
        "best_sampled_complete_plane_reader_cost": best[1],
        "best_sampled_raw_support_rank_sum": best[2],
        "predecessor_raw_support_rank_sum": predecessor_raw_cost,
        "predecessor_complete_plane_reader_cost": predecessor_reader_cost,
        "complete_plane_reader_cost_reduction": predecessor_reader_cost - best[1],
        "complete_plane_reader_cost_reduction_fraction": "7/16",
        "predecessor_certificate_sha256": PREDECESSOR_CERTIFICATE_SHA256,
        "best_sampled_rank1_planes": best[3][1],
        "best_sampled_rank2_planes": best[3][2],
        "best_sampled_zero_planes": best[3][0],
        "best_sampled_pairs": [list(pair) for pair in best_pairs],
        "best_sampled_matrix_bits": list(best_matrices),
        "full_decoder_identity": "PASS",
        "raw_support_ranks_by_matrix_rank": {
            f"{matrix_rank}:{copy_rank}": count
            for (matrix_rank, copy_rank), count in sorted(checked_copy_ranks.items())
        },
        "complete_plane_reader_ranks_by_matrix_rank": {
            f"{matrix_rank}:{reader_rank}": count
            for (matrix_rank, reader_rank), count in sorted(checked_reader_ranks.items())
        },
        "total_complete_plane_reader_cost": sum(rank * count for (_, rank), count in
                                                 checked_reader_ranks.items()),
        "exact_plane_endpoint_input_cases": endpoint_cases,
        "scope": "Seeded 500-candidate screen with the free-zero F2 solution; sampled cost is not an optimum or supplier-admitted result.",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
