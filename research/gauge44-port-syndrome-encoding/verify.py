#!/usr/bin/env python3
"""Exact source-bound port-basis experiment for the selected gauge44 scatter."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
MEMBER_SHA256 = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
PHASE_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PHASE_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
ANCHOR_ROOTS = (
    (1, -1, 0, 0),
    (0, 1, 0, 1),
    (1, 1, 0, 0),
    (0, 1, -1, 0),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def row_add(matrix, target, source, coefficient):
    require(target != source, "row shear must use distinct rows")
    coefficient = Fraction(coefficient)
    result = list(matrix[target])
    for j, value in enumerate(matrix[source]):
        result[j] += coefficient * value
    matrix[target] = result


def sparse_row_add(matrix, target, source, coefficient):
    require(target != source, "row shear must use distinct rows")
    coefficient = int(coefficient)
    result = dict(matrix[target])
    for j, value in matrix[source].items():
        result[j] = result.get(j, 0) + coefficient * value
        if result[j] == 0:
            del result[j]
    matrix[target] = result


def rref(rows, width=4):
    matrix = [[Fraction(x) for x in row] for row in rows if any(row)]
    pivot_row = 0
    for column in range(width):
        pivot = next((r for r in range(pivot_row, len(matrix))
                      if matrix[r][column]), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        scale = matrix[pivot_row][column]
        matrix[pivot_row] = [x / scale for x in matrix[pivot_row]]
        for r in range(len(matrix)):
            if r != pivot_row and matrix[r][column]:
                scale = matrix[r][column]
                matrix[r] = [matrix[r][j] - scale * matrix[pivot_row][j]
                             for j in range(width)]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return tuple(tuple(row) for row in matrix[:pivot_row])


def solve_columns(columns, target):
    """Return c with sum(c[j] * columns[j]) == target, or None if singular."""
    width = len(target)
    matrix = [[Fraction(columns[j][i]) for j in range(width)] +
              [Fraction(target[i])] for i in range(width)]
    for column in range(width):
        pivot = next((r for r in range(column, width)
                      if matrix[r][column]), None)
        if pivot is None:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [x / scale for x in matrix[column]]
        for r in range(width):
            if r != column and matrix[r][column]:
                scale = matrix[r][column]
                matrix[r] = [matrix[r][j] - scale * matrix[column][j]
                             for j in range(width + 1)]
    return [matrix[i][width] for i in range(width)]


def inverse(matrix):
    n = len(matrix)
    augmented = [[Fraction(x) for x in row] +
                 [Fraction(i == j) for j in range(n)]
                 for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((r for r in range(column, n)
                      if augmented[r][column]), None)
        require(pivot is not None, "anchor matrix is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [x / scale for x in augmented[column]]
        for r in range(n):
            if r != column and augmented[r][column]:
                scale = augmented[r][column]
                augmented[r] = [augmented[r][j] - scale * augmented[column][j]
                                for j in range(2 * n)]
    return [row[n:] for row in augmented]


def support_floor(forms):
    """Enumerate every data-generated proper subspace in one 4D root block."""
    subspaces = {tuple()}
    for size in (1, 2, 3):
        for subset in combinations(forms, size):
            span = rref(subset)
            if len(span) <= 3:
                subspaces.add(span)
    weights_by_rank = defaultdict(list)
    for span in subspaces:
        rank = len(span)
        contained_weight = sum(weight for vector, weight in forms.items()
                              if len(rref((*span, vector))) == rank)
        weights_by_rank[rank].append(contained_weight)
    maximum = max(max(values) for values in weights_by_rank.values())
    return {
        "generated_proper_subspaces": len(subspaces),
        "count_by_dimension": {str(rank): len(values)
                                for rank, values in sorted(weights_by_rank.items())},
        "max_contained_weight_by_dimension": {
            str(rank): max(values) for rank, values in sorted(weights_by_rank.items())
        },
        "max_proper_subspace_weight": maximum,
        "minimum_nonzero_functional_support": sum(forms.values()) - maximum,
    }


def run():
    archive_bytes = ARCHIVE.read_bytes()
    archive_hash = hashlib.sha256(archive_bytes).hexdigest()
    require(archive_hash == ARCHIVE_SHA256, "selected replay archive hash changed")
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        compressed_member = archive.extractfile(MEMBER).read()
    member_hash = hashlib.sha256(compressed_member).hexdigest()
    require(member_hash == MEMBER_SHA256, "selected gauge44 word member hash changed")
    word = json.loads(gzip.decompress(compressed_member))
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        phase_payload = archive.extractfile(PHASE_MEMBER).read()
    require(hashlib.sha256(phase_payload).hexdigest() == PHASE_SHA256,
            "selected DATA-PHASES payload hash changed")
    phases = json.loads(phase_payload)
    recipes = sorted(phases["recipes"], key=lambda row: row["port"])
    ports = [row["q"] for row in recipes]
    require(len(ports) == 112 and [row["port"] for row in recipes] == list(range(112)),
            "unexpected selected DATA-PHASES port order")
    require(word["ports"] == ports, "canonical word and selected port labels disagree")

    centers = word["centers"]
    require(len(centers) == 8 and len(set(centers)) == 8,
            "expected eight distinct selected centre destinations")
    center_index = {register: index for index, register in enumerate(centers)}
    scatter = [[Fraction(0) for _ in centers] for _ in range(112)]
    for instruction in word["cut"]:
        op, src, dst, numerator, denominator, *_ = instruction
        require(op == "add" and 112 <= src < 224 and dst in center_index,
                "unexpected selected centre-cut instruction")
        scatter[src - 112][center_index[dst]] += Fraction(numerator, denominator)
    require(len(scatter) == 112 and all(len(row) == 8 for row in scatter),
            "expected a 112 by 8 selected scatter")
    require(all(not value or value.denominator == 4 for row in scatter for value in row),
            "unexpected scatter coefficient denominator")
    zero_rows = [i for i, row in enumerate(scatter) if not any(row)]
    classes = defaultdict(list)
    for i, row in enumerate(scatter):
        if any(row):
            classes[tuple(row)].append(i)
    require(len(zero_rows) == 24, "expected 24 centre-free ports")
    require(len(classes) == 24, "expected 24 repeated centre signatures")
    require(Counter(map(len, classes.values())) == {3: 8, 4: 16},
            "unexpected multiplicities of repeated signatures")
    for indices in classes.values():
        require(all((ports[i] & ports[j]).bit_count() % 2 == 0
                    for i, j in combinations(indices, 2)),
                "a repeated centre-signature class is not pairwise orthogonal in F2")

    # The current 8D centre basis reaches the exact incidence floor.
    original_support = sum(value != 0 for row in scatter for value in row)
    require(original_support == 176, "expected 176 current centre incidences")
    gram = [[sum((row[i] * row[j] for row in scatter), Fraction(0))
             for j in range(8)] for i in range(8)]
    require(all(gram[i][j] == (Fraction(11, 8) if i == j else 0)
                for i in range(8) for j in range(8)),
            "selected scatter is not the expected tight frame")

    block_forms = []
    floor_results = []
    for offset in (0, 4):
        forms = Counter()
        for signature in classes:
            local = tuple(int(4 * value) for value in signature[offset:offset + 4])
            if any(local):
                forms[local] += len(classes[signature])
        require(len(forms) == 12 and sum(forms.values()) == 44,
                "each centre block must have twelve D4 lines on 44 ports")
        require(Counter(forms.values()) == {3: 4, 4: 8},
                "unexpected D4 line weights")
        floor = support_floor(forms)
        require(floor["generated_proper_subspaces"] == 71,
                "unexpected proper-subspace enumeration")
        require(floor["max_proper_subspace_weight"] == 22 and
                floor["minimum_nonzero_functional_support"] == 22,
                "unexpected basis-independent support floor")
        coordinate_supports = [sum(weight for vector, weight in forms.items()
                                   if vector[j]) for j in range(4)]
        require(coordinate_supports == [22] * 4,
                "current block basis does not attain the support floor")
        block_forms.append(forms)
        floor_results.append(floor)

    # Compose only integer row-add shears: differences within each repeated
    # signature class, then D4-root reductions to four anchors per block.
    transformed = [row[:] for row in scatter]
    transform = [{i: 1} for i in range(112)]
    operations = []

    def add(target, source, coefficient):
        require(coefficient in (-1, 1), "expected only unit row shears")
        row_add(transformed, target, source, coefficient)
        sparse_row_add(transform, target, source, coefficient)
        operations.append((target, source, coefficient))

    representatives = {}
    for signature, indices in sorted(classes.items(), key=lambda item: min(item[1])):
        representative = min(indices)
        representatives[signature] = representative
        for target in sorted(indices):
            if target != representative:
                add(target, representative, -1)
    difference_adds = len(operations)
    require(difference_adds == 64, "expected 64 within-class differences")

    anchor_ids = []
    per_block_cancellations = []
    for offset in (0, 4):
        by_root = {}
        for signature, indices in classes.items():
            root = tuple(int(4 * value) for value in signature[offset:offset + 4])
            if any(root):
                require(not any(signature[:offset]) and
                        not any(signature[offset + 4:]),
                        "a selected scatter row crosses the two D4 blocks")
                by_root[root] = representatives[signature]
        require(len(by_root) == 12, "expected twelve root lines per block")
        anchors = [by_root[root] for root in ANCHOR_ROOTS]
        anchor_ids.extend(anchors)
        cancellations = 0
        for root, representative in sorted(by_root.items()):
            if root in ANCHOR_ROOTS:
                continue
            coefficients = solve_columns(ANCHOR_ROOTS, root)
            require(coefficients is not None and
                    all(value.denominator == 1 and abs(value) <= 1
                        for value in coefficients),
                    "the chosen D4 anchors do not give unit-integral root coordinates")
            nonzeros = 0
            for anchor, coefficient in zip(anchors, coefficients):
                if coefficient:
                    add(representative, anchor, -int(coefficient))
                    nonzeros += 1
            cancellations += nonzeros
        require(cancellations == 20, "expected twenty root reductions per block")
        per_block_cancellations.append(cancellations)

    require(len(operations) == 104, "expected 104 unit row-add shears")
    require(len({target for target, _, _ in operations}) <= 112,
            "invalid row transformation")
    active_rows = [i for i, row in enumerate(transformed) if any(row)]
    require(set(active_rows) == set(anchor_ids),
            "centre signal did not localize exactly to the eight anchors")
    require(sum(value != 0 for row in transformed for value in row) == 16,
            "expected two centre coefficients on each anchor")
    require(all(row == scatter[index] for row, index in
                zip([transformed[i] for i in anchor_ids], anchor_ids)),
            "anchor rows changed unexpectedly")
    require(all(value.denominator == 1 for row in transform for value in row.values()),
            "port transformation is not integral")
    # Every operation is an elementary row-add, so T is unimodular over Z.

    # Recover c from the eight transformed anchors when the input is a pure
    # centre signal S c. This does not cancel arbitrary product residuals.
    readout = [[Fraction(0) for _ in range(112)] for _ in range(8)]
    block_decoder_nonzeros = []
    for block, offset in enumerate((0, 4)):
        ids = anchor_ids[4 * block:4 * block + 4]
        anchor_matrix = [[transformed[row][offset + j] for j in range(4)]
                         for row in ids]
        decoder = inverse(anchor_matrix)
        nonzeros = sum(value != 0 for row in decoder for value in row)
        require(nonzeros == 10, "expected ten decoder coefficients per block")
        require(all(value.denominator == 1 for row in decoder for value in row),
                "anchor decoder unexpectedly needs non-dyadic coefficients")
        block_decoder_nonzeros.append(nonzeros)
        for i in range(4):
            for j in range(4):
                readout[offset + i][ids[j]] = decoder[i][j]

    recovered = [[sum((readout[i][port] * transformed[port][j]
                       for port in range(112)), Fraction(0))
                  for j in range(8)] for i in range(8)]
    require(all(recovered[i][j] == Fraction(i == j)
                for i in range(8) for j in range(8)),
            "anchor readout does not invert the transformed centre signal")
    decoder_nonzeros = sum(value != 0 for row in readout for value in row)
    require(decoder_nonzeros == 20, "expected twenty exact anchor-readout coefficients")

    # A mutation control: the fixed source-bound shears must react to a changed
    # source coefficient rather than silently certifying the old result.
    mutant = [row[:] for row in scatter]
    mutant[0][0] += Fraction(1, 4)
    for target, source, coefficient in operations:
        row_add(mutant, target, source, coefficient)
    require(mutant != transformed, "mutation control failed to detect a changed source")
    require(solve_columns((ANCHOR_ROOTS[0], ANCHOR_ROOTS[0],
                           ANCHOR_ROOTS[2], ANCHOR_ROOTS[3]),
                          ANCHOR_ROOTS[0]) is None,
            "singular-basis control failed")

    return {
        "status": "PASS_GAUGE44_PORT_SYNDROME_ENCODING",
        "archive_sha256": archive_hash,
        "canonical_word_member_sha256": member_hash,
        "data_phases_payload_sha256": PHASE_SHA256,
        "scatter_shape": [112, 8],
        "nonzero_scatter_rows": 88,
        "zero_scatter_rows": 24,
        "signature_classes": len(classes),
        "class_sizes": {str(k): v for k, v in sorted(Counter(map(len, classes.values())).items())},
        "d4_lines_per_block": [12, 12],
        "max_proper_subspace_weight_per_block": [x["max_proper_subspace_weight"]
                                                    for x in floor_results],
        "minimum_nonzero_functional_support_per_block": [
            x["minimum_nonzero_functional_support"] for x in floor_results
        ],
        "basis_invariant_minimum_scatter_support": 176,
        "current_scatter_support": original_support,
        "gram_diagonal": "11/8",
        "gram_off_diagonal": "0",
        "unit_row_add_shears": len(operations),
        "within_class_difference_shears": difference_adds,
        "root_reduction_shears_per_block": per_block_cancellations,
        "transformed_center_rows": len(active_rows),
        "transformed_center_free_rows": 112 - len(active_rows),
        "transformed_scatter_support": 16,
        "exact_anchor_decoder_nonzeros": decoder_nonzeros,
        "decoder_coefficients_integral": True,
        "mutation_control": "PASS",
        "singular_basis_control": "PASS",
        "scope": "Exact local linear algebra only; no native schedule, arbitrary-residual consumer, supplier admission, or kappa gain is proved.",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
