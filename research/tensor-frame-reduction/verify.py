#!/usr/bin/env python3
"""Check exact finite cases of the tensor frame reduction theorem."""
import argparse
from fractions import Fraction as Q
from itertools import combinations, product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def basis(rows):
    pivots = {}
    for value in rows:
        for bit, row in sorted(pivots.items(), reverse=True):
            if value >> bit & 1:
                value ^= row
        if value:
            bit = value.bit_length() - 1
            for other, row in tuple(pivots.items()):
                if row >> bit & 1:
                    pivots[other] ^= value
            pivots[bit] = value
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def span(rows):
    values = {0}
    for row in rows:
        values |= {value ^ row for value in tuple(values)}
    return values


def spaces(width, dimension=None):
    ranks = range(width + 1) if dimension is None else [dimension]
    for rank in ranks:
        for pivots in combinations(range(width), rank):
            free = [(i, j) for i, p in enumerate(pivots)
                    for j in range(p) if j not in pivots]
            for bits in range(1 << len(free)):
                rows = [1 << p for p in pivots]
                for k, (i, j) in enumerate(free):
                    rows[i] |= ((bits >> k) & 1) << j
                yield tuple(reversed(rows))


def subspace_distance(left, right):
    return 2 * len(basis(left + right)) - len(left) - len(right)


def symplectic(left, right, width):
    mask = (1 << width) - 1
    return (((left & mask) & (right >> width)).bit_count()
            + ((left >> width) & (right & mask)).bit_count()) % 2


def lagrangian(rows, width):
    need(len(basis(rows)) == width, "Lagrangian dimension")
    need(all(not symplectic(a, b, width)
             for a, b in combinations(rows, 2)), "Lagrangian isotropy")


def lagrangians(width):
    return [rows for rows in spaces(2 * width, width)
            if all(not symplectic(a, b, width)
                   for a, b in combinations(rows, 2))]


def canonical(rows, width):
    perpendicular = basis(value for value in range(1 << width)
                          if all((value & row).bit_count() % 2 == 0
                                 for row in rows))
    return basis([row | (row << width) for row in rows]
                 + [row << width for row in perpendicular])


def projection(rows, width):
    return basis(row & ((1 << width) - 1) for row in rows)


def grade(rows, dimension, copies):
    """Use the subspace at each prefix before projection onto one block."""
    mask = (1 << dimension) - 1
    return tuple(basis((row >> (dimension * j)) & mask for row in rows
                       if row >> (dimension * (j + 1)) == 0)
                 for j in range(copies))


def check_grade(rows, dimension, copies):
    actual = grade(rows, dimension, copies)
    values = span(rows)
    mask = (1 << dimension) - 1
    for j, part in enumerate(actual):
        expected = {(value >> (dimension * j)) & mask for value in values
                    if value >> (dimension * (j + 1)) == 0}
        need(span(part) == expected, "Independent prefix-intersection oracle")
    need(sum(map(len, actual)) == len(rows), "Graded dimension")
    return actual


def tensor_space(rows, dimension, copies):
    return basis(row << (dimension * j) for j in range(copies) for row in rows)


def fixed_boundary(rows, target, dimension, copies):
    width = dimension * copies
    need(rows == canonical(tensor_space(target, dimension, copies), width),
         "Fixed tensor boundary")


def exact_calibration():
    counts = {}
    grade_pairs = 0
    strict_grade = 0
    for dimension, copies in [(1, 2), (1, 3), (1, 4), (2, 2)]:
        width = dimension * copies
        all_spaces = list(spaces(width))
        need(len(set(all_spaces)) == len(all_spaces), "Unique subspaces")
        parts = [check_grade(rows, dimension, copies) for rows in all_spaces]
        for i, left in enumerate(all_spaces):
            for j, right in enumerate(all_spaces):
                old = subspace_distance(left, right)
                common = len(span(left) & span(right)).bit_length() - 1
                need(old == len(left) + len(right) - 2 * common,
                     "Independent subspace distance")
                new = sum(subspace_distance(a, b)
                          for a, b in zip(parts[i], parts[j]))
                need(new <= old, "Graded distance contraction")
                grade_pairs += 1
                strict_grade += new < old
        for target in spaces(dimension):
            repeated = tensor_space(target, dimension, copies)
            need(grade(repeated, dimension, copies) == (target,) * copies,
                 "Fixed boundary in every copy")
        counts[f"{dimension}x{copies}"] = len(all_spaces)

    native_pairs = 0
    strict_native = 0
    native_counts = {}
    for width in range(1, 5):
        all_lags = lagrangians(width)
        expected = 1
        for k in range(1, width + 1):
            expected *= 2 ** k + 1
        need(len(all_lags) == expected, "Complete Lagrangian census")
        native_counts[str(width)] = len(all_lags)
        projected = [projection(rows, width) for rows in all_lags]
        dimension, copies = (2, 2) if width == 4 else (1, width)
        parts = [check_grade(rows, dimension, copies) for rows in projected]
        pairs = (product(range(len(all_lags)), repeat=2) if width <= 3 else
                 ((i, (i + offset) % len(all_lags))
                  for i in range(len(all_lags)) for offset in (137, 593, 1009)))
        for i, j in pairs:
            rank = len(basis(all_lags[i] + all_lags[j])) - width
            middle = subspace_distance(projected[i], projected[j])
            ranks = [subspace_distance(a, b)
                     for a, b in zip(parts[i], parts[j])]
            need(sum(ranks) <= middle <= rank, "Composed native rank bound")
            native_pairs += 1
            strict_native += sum(ranks) < rank
        for rows in spaces(width):
            need(projection(canonical(rows, width), width) == rows,
                 "Canonical chart is fixed by projection")

    # The hinges span the cone of increasing concave values on this grid.
    hinge_checks = 0
    for dimension in range(1, 5):
        for copies in range(1, 5):
            for ranks in product(range(dimension + 1), repeat=copies):
                for knot in range(1, dimension * copies + 1):
                    need(sum(min(copies * rank, knot) for rank in ranks)
                         <= copies * min(sum(ranks), knot), "Concave averaging")
                    hinge_checks += 1

    # Use one copy for the whole graph, with fixed zero and full boundaries.
    all_lags = lagrangians(2)
    edges = [(0, 2, 1), (2, 3, 2), (3, 1, 3), (0, 3, 1), (2, 1, 2)]
    zero, full = canonical((), 2), canonical((2, 1), 2)
    graph_checks = 0
    for left, right in product(all_lags, repeat=2):
        labels = [zero, full, left, right]
        fixed_boundary(zero, (), 1, 2)
        fixed_boundary(full, (1,), 1, 2)
        parts = [grade(projection(rows, 2), 1, 2) for rows in labels]
        for knot in [Q(1, 2), Q(1), Q(3, 2)]:
            tariff = lambda value: value + 2 * min(value, knot)
            old = sum(weight * tariff(Q(len(basis(labels[a] + labels[b])) - 2, 2))
                      for a, b, weight in edges)
            costs = [sum(weight * tariff(subspace_distance(parts[a][j], parts[b][j]))
                         for a, b, weight in edges) for j in range(2)]
            need(min(costs) <= sum(costs, Q(0)) / 2 <= old,
                 "One common copy for the complete graph")
            graph_checks += 1

    controls = []
    try:
        lagrangian((1, 4), 2)
    except ValueError:
        controls.append("nonisotropic_frame")
    try:
        fixed_boundary(canonical((1,), 2), (1,), 1, 2)
    except ValueError:
        controls.append("nonproduct_boundary")
    diagonal = (3,)
    naive = tuple(basis((row >> j) & 1 for row in diagonal) for j in range(2))
    need(sum(map(len, naive)) == 2 and len(diagonal) == 1,
         "Naive projection must fail the dimension identity")
    controls.append("projection_without_prefix_intersection")
    ranks = [(1, 0), (0, 1)]
    local_min = sum(min(row) for row in ranks)
    shared_min = min(sum(row[j] for row in ranks) for j in range(2))
    need((local_min, shared_min) == (0, 1), "Per-edge choices must not be combined")
    controls.append("different_copy_for_each_edge")
    need(sum(Q(sum(row), 2) ** 2 for row in ranks) == Q(1, 2)
         < Q(1), "Convex tariff reverses the averaging step")
    controls.append("convex_tariff")
    need(-sum(min(Q(sum(row), 2), Q(1, 2)) for row in ranks) == -1
         < -Q(1, 2), "Variable negative credits reverse the required comparison")
    controls.append("unfixed_productive_credit")
    coupled_rank = len(basis(zero + full)) - 2
    single_rank = subspace_distance((), (1,))
    need(Q(coupled_rank, 2) == single_rank and coupled_rank != single_rank,
         "Tensor rank normalization on fixed native boundaries")
    controls.append("missing_tensor_normalization")
    need(len(controls) == 7 and strict_grade and strict_native, "All controls")
    return dict(schema_version=1, claim="fixed-boundary recursive rank-moment reduction",
                kappa_improvement=False, subspace_counts=counts,
                graded_ordered_pairs=grade_pairs, strict_graded_pairs=strict_grade,
                lagrangian_counts=native_counts, composed_native_pairs=native_pairs,
                native_pair_coverage="all pairs at widths 1..3; three fixed offsets at width 4",
                strict_native_pairs=strict_native, exact_hinge_checks=hinge_checks,
                complete_graph_checks=graph_checks, controls=controls,
                proof_scope="The written proof gives all finite dimensions and positive tensor widths.",
                excluded="Changed scalar words, variable productive boundaries, native phase or compiler admission.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = exact_calibration()
    path = Path(__file__).with_name("RESULT.json")
    if args.write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == json.loads(path.read_text()), "Committed exact receipt")
    print("PASS_TENSOR_FRAME_REDUCTION", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
