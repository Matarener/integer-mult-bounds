"""Independent exact reconstruction for the P112 six/seven supplement.

Contributed by conorholds. Retains the E8/P112 geometry and label lineage of
PR3161/3162, joaqcoo, and the DreamingOfClouds decoder data. The signed
quadratic-capacity predecessors are PR3269/3300. Apache-2.0.

This engine does not import the primary verifier or execute source helpers.
It reconstructs roots directly, uses a polar-pairing coordinate system of its
own, and enumerates affine sections by ordinary-dot RREF annihilators.
"""

from __future__ import annotations

import ast
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import re


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def insist(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(a, b):
    insist(len(a) == len(b), "dot-product dimension")
    return sum(x * y for x, y in zip(a, b))


def positive_line(vector):
    vector = tuple(vector)
    first = next((x for x in vector if x), None)
    insist(first is not None, "zero root")
    return vector if first > 0 else tuple(-x for x in vector)


def reconstruct_roots():
    roots = []
    for i in range(8):
        for j in range(i + 1, 8):
            for sign in (-1, 1):
                vector = [0] * 8
                vector[i], vector[j] = 2, 2 * sign
                roots.append(tuple(vector))
    # Fix the first sign, rather than generating and deduplicating both lines.
    for code in range(128):
        if code.bit_count() % 2 == 0:
            roots.append((1,) + tuple(-1 if code >> i & 1 else 1 for i in range(7)))
    roots = tuple(sorted(roots))
    frame = set()
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            vector = [0] * 8
            vector[i], vector[i + 1] = 2, 2 * sign
            frame.add(tuple(vector))
    insist(len(roots) == len(set(roots)) == 120, "independent root inventory")
    insist(len(frame) == 8 and frame <= set(roots), "independent paired frame")
    insist(all(scalar(r, r) == 8 for r in roots), "root normalization")
    insist(all(scalar(a, b) == 0 for a, b in combinations(frame, 2)), "frame orthogonality")
    return roots, frame


def binary_rank(vectors):
    pivots = {}
    for original in vectors:
        value = original
        while value:
            column = (value & -value).bit_length() - 1
            if column in pivots:
                value ^= pivots[column]
            else:
                pivots[column] = value
                break
    return len(pivots)


def coordinates_in_span(vectors):
    basis = []
    for value in vectors:
        if binary_rank(basis + [value]) > len(basis):
            basis.append(value)
    coordinates = {0: 0}
    for i, value in enumerate(basis):
        coordinates.update({x ^ value: c | (1 << i) for x, c in tuple(coordinates.items())})
    insist(all(value in coordinates for value in vectors), "span coordinates")
    return basis, coordinates


def rational_rank(rows):
    if not rows:
        return 0
    width = len(rows[0])
    insist(all(len(row) == width for row in rows), "rational matrix shape")
    matrix = [list(map(Fraction, row)) for row in rows]
    rank = 0
    for col in range(width):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][col]
        matrix[rank] = [x / scale for x in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            factor = matrix[i][col]
            if factor:
                matrix[i] = [x - factor * y for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def inverse(matrix):
    size = len(matrix)
    insist(size and all(len(row) == size for row in matrix), "square inverse shape")
    rows = [list(map(Fraction, row)) + [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = next((i for i in range(col, size) if rows[i][col]), None)
        insist(pivot is not None, "singular source simple system")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for i in range(size):
            if i != col and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[col])]
    return [row[size:] for row in rows]


def load_simple_labels(path, roots):
    # Read one frozen numerical declaration; never import or execute geometry.py.
    tree = ast.parse(path.read_text())
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "SIMPLE"
                           for target in node.targets)]
    insist(len(assignments) == 1, "unique source SIMPLE declaration")
    simple = ast.literal_eval(assignments[0].value)
    insist(len(simple) == 8 and all(len(row) == 8 for row in simple), "SIMPLE shape")
    transform = inverse(tuple(zip(*simple)))
    labels = []
    for root in roots:
        coefficients = [scalar(row, root) for row in transform]
        insist(all(c.denominator == 1 for c in coefficients), "integral root coordinates")
        labels.append(1 | sum((int(c) & 1) << (i + 1) for i, c in enumerate(coefficients)))
    return labels


def linear_transfer(old, new):
    insist(len(old) == len(new), "label transfer length")
    equations = {}
    for left, right in zip(old, new):
        while left:
            pivot = left.bit_length() - 1
            if pivot not in equations:
                equations[pivot] = (left, right)
                break
            a, b = equations[pivot]
            left, right = left ^ a, right ^ b
        else:
            insist(right == 0, "source label relations do not transfer")
    insist(len(equations) == binary_rank(new) == 9, "invertible nine-bit transfer")
    images = []
    for column in range(9):
        left, right = 1 << column, 0
        while left:
            a, b = equations[left.bit_length() - 1]
            left, right = left ^ a, right ^ b
        images.append(right)
    insist(binary_rank(images) == 9, "singular label transfer")
    insist([value & 1 for value in images] == [1] + [0] * 8,
            "label transfer preserves the declared leading coordinate")
    for left, right in zip(old, new):
        image = 0
        for column in range(9):
            if left >> column & 1:
                image ^= images[column]
        insist(image == right, "literal label transfer")
    return images


def independent_model():
    roots, frame = reconstruct_roots()
    ordinary = [[scalar(a, b) for b in roots] for a in roots]
    insist(all(value % 4 == 0 for row in ordinary for value in row), "integral polar pairing")
    pairing_rows = [sum(((value // 4) & 1) << j for j, value in enumerate(row))
                    for row in ordinary]
    basis_ids, selected = [], []
    for i, row in enumerate(pairing_rows):
        if binary_rank(selected + [row]) > len(selected):
            selected.append(row)
            basis_ids.append(i)
    insist(len(basis_ids) == 8, "independent polar rank")
    residues = [sum(((ordinary[i][j] // 4) & 1) << k for k, j in enumerate(basis_ids))
                for i in range(120)]
    insist(len(set(residues)) == 120, "injective independent residues")
    basis_roots = [roots[i] for i in basis_ids]
    q = {}
    for code in range(256):
        lift = tuple(sum(root[j] for i, root in enumerate(basis_roots) if code >> i & 1)
                     for j in range(8))
        residue = 0
        for i, root_id in enumerate(basis_ids):
            if code >> i & 1:
                residue ^= residues[root_id]
        norm = scalar(lift, lift)
        insist(norm % 8 == 0 and residue not in q, "independent lattice lift")
        q[residue] = (norm // 8) & 1
    insist(len(q) == 256 and {x for x, value in q.items() if value} == set(residues),
            "roots are exactly the quadratic ones")
    insist(sum(1 - 2 * q[x] for x in range(256)) == 16, "positive ambient Gauss sign")
    bilinear = [[q[x ^ y] ^ q[x] ^ q[y] for y in range(256)] for x in range(256)]
    for x in range(256):
        row = sum(bilinear[x][1 << j] << j for j in range(8))
        insist(all(bilinear[x][y] == ((row & y).bit_count() & 1) for y in range(256)),
                "quadratic polarization is bilinear")
    for i in range(120):
        for j in range(120):
            insist(bilinear[residues[i]][residues[j]] == ((ordinary[i][j] // 4) & 1),
                    "root/polar binding")
    labels = [1 | residue << 1 for residue in residues]
    source_geometry = ROOT / "research/p112-root-simplex-exclusion/geometry.py"
    source_labels = load_simple_labels(source_geometry, roots)
    simple_transfer = linear_transfer(source_labels, labels)
    old_path = ROOT / "research/one-sided-decoders-all-m/data/data.json"
    old = json.loads(old_path.read_text(), parse_float=Fraction)
    insist(len(old["LAB"]) == 112 and all(type(x) is int and 0 < x < 512 and x & 1
                                        for x in old["LAB"]), "old declared labels")
    old_roots = [positive_line(tuple(2 * Fraction(x) for x in row)) for row in old["L"]]
    insist(len(old_roots) == len(set(old_roots)) == 112, "old live-root inventory")
    insist(set(old_roots) == set(roots) - frame, "old live roots match paired-frame model")
    old_frame = {positive_line(tuple(2 * Fraction(x) for x in row)) for row in old["F0"]}
    insist(old_frame == frame, "old frame binding")
    old_full = [positive_line(tuple(2 * Fraction(x) for x in row)) for row in old["E8"]]
    insist(len(old_full) == len(set(old_full)) == 120 and set(old_full) == set(roots),
            "old full-root binding")
    root_id = {root: i for i, root in enumerate(roots)}
    old_ids = [root_id[root] for root in old_roots]
    old_transfer = linear_transfer(old["LAB"], [labels[i] for i in old_ids])
    insist(len(old["FC"]) == 112 and all(len(row) == 8 for row in old["FC"]), "FC shape")
    code_rows = [tuple(row[j] for row in old["FC"]) for j in range(8)]
    root_rows = [tuple(roots[i][j] for i in old_ids) for j in range(8)]
    insist(rational_rank(code_rows) == rational_rank(root_rows) == 8, "source code ranks")
    insist(rational_rank(code_rows + root_rows) == 8, "source FC/root-code equality")
    return {"roots": roots, "frame": frame, "ordinary": ordinary, "residues": residues,
            "labels": labels, "q": q, "bilinear": bilinear, "old_ids": old_ids,
            "code_rows": code_rows, "simple_transfer": simple_transfer,
            "old_transfer": old_transfer,
            "source_hashes": {"geometry": sha256(source_geometry.read_bytes()).hexdigest(),
                              "data": sha256(old_path.read_bytes()).hexdigest()}}


def annihilators():
    """All ordinary-dot two-row RREF spaces, using leftmost pivots."""
    for p, q in combinations(range(8), 2):
        free_a = [j for j in range(p + 1, 8) if j != q]
        free_b = list(range(q + 1, 8))
        for code_a in range(1 << len(free_a)):
            a = 1 << p
            for i, column in enumerate(free_a):
                a |= ((code_a >> i) & 1) << column
            for code_b in range(1 << len(free_b)):
                b = 1 << q
                for i, column in enumerate(free_b):
                    b |= ((code_b >> i) & 1) << column
                yield a, b


def section_census(model):
    residues, ordinary = model["residues"], model["ordinary"]
    bilinear, q = model["bilinear"], model["q"]
    all_roots = (1 << 120) - 1
    live = sum(1 << i for i, root in enumerate(model["roots"]) if root not in model["frame"])
    off = [sum(1 << j for j, value in enumerate(row) if value) for row in ordinary]
    masks = [(sum(1 << i for i, x in enumerate(residues) if not ((a & x).bit_count() & 1)))
             for a in range(256)]
    polar_to_normal = {sum(bilinear[x][1 << j] << j for j in range(8)): x for x in range(256)}
    insist(len(polar_to_normal) == 256, "nonsingular independent polarity")
    root_by_residue = {x: i for i, x in enumerate(residues)}
    histogram, completions, qualifying = Counter(), {}, []
    directions = 0
    for a, b in annihilators():
        directions += 1
        perpendicular = (0, polar_to_normal[a], polar_to_normal[b],
                         polar_to_normal[a] ^ polar_to_normal[b])
        radical = tuple(x for x in perpendicular if not ((a & x).bit_count() & 1)
                        and not ((b & x).bit_count() & 1))
        for ca in range(2):
            for cb in range(2):
                section = (masks[a] if ca == 0 else all_roots ^ masks[a])
                section &= masks[b] if cb == 0 else all_roots ^ masks[b]
                histogram[section.bit_count()] += 1
                insist(section.bit_count() <= 36, "independent rank-seven capacity")
                for v in range(120):
                    count = (section & off[v]).bit_count()
                    insist(count <= 32, "root32 capacity")
                    if count < 29:
                        continue
                    insist(count == section.bit_count() == 32, "completion32 rigidity")
                    rv = residues[v]
                    insist(len(radical) == 4 and rv in radical, "completion radical")
                    isotropic = [x for x in radical if x and not q[x]]
                    insist(len(isotropic) == 1, "completion isotropic partner")
                    u = isotropic[0]
                    w = root_by_residue[rv ^ u]
                    insist(ordinary[v][w] == 0, "completion mate orthogonality")
                    for x in range(256):
                        in_section = ((a & x).bit_count() & 1) == ca
                        in_section &= ((b & x).bit_count() & 1) == cb
                        insist(in_section == (bilinear[rv][x] == bilinear[u][x] == 1),
                                "completion affine equations")
                    defect = off[v] & ~section
                    core = off[v] & off[w]
                    insist(defect == (core | (1 << v)) and core.bit_count() == 24,
                            "closed own-root defect")
                    insist((v, w) not in completions, "duplicate classified completion")
                    completions[v, w] = (a, b, ca, cb)
                    if (section & off[v] & live).bit_count() >= 29:
                        qualifying.append((v, w))
    expected = {(v, w) for v in range(120) for w in range(120) if ordinary[v][w] == 0}
    insist(set(completions) == expected, "all orthogonal-mate completions classified")
    insist(directions == 10795 and sum(histogram.values()) == 43180,
            "complete ordinary-annihilator census")
    return {"count": sum(histogram.values()),
            "cardinality_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "qualifying29": len(qualifying),
            "completion_digest": sha256(json.dumps(sorted(qualifying), separators=(",", ":")).encode()).hexdigest()}, \
        {"annihilator_directions": directions, "full_completions": len(completions)}


def core_census(model):
    ordinary, labels = model["ordinary"], model["labels"]
    root_by_label = {label: i for i, label in enumerate(labels)}
    histogram = Counter()
    live = set(model["old_ids"])
    frame = set(range(120)) - live
    optimal, per_word = [], Counter()
    pair_count, small_flat_count = 0, 0
    for v, w in combinations(range(120), 2):
        if ordinary[v][w] != 0:
            continue
        pair_count += 1
        core = [i for i in range(120) if ordinary[v][i] and ordinary[w][i]]
        insist(len(core) == 24, "ordinary common-off core24")
        basis, coordinates = coordinates_in_span([labels[i] for i in core])
        insist(len(basis) == 7, "core span has rank seven")
        for functional in range(1, 1 << len(basis)):
            low = {i for i in core if not ((coordinates[labels[i]] & functional).bit_count() & 1)}
            size = len(low)
            insist(size <= 16, "core six-space cap16")
            histogram[size] += 1
            if size != 16 or low & frame:
                continue
            for normal, mate in ((v, w), (w, v)):
                high = {i for i in live if i != normal and ordinary[normal][i]
                        and not ordinary[mate][i]}
                target = {i for i in live if ordinary[normal][i]}
                sparse = target - high - low
                floor = 5 if normal in live else 8
                if len(sparse) != floor:
                    continue
                insist(len(high) == 32 and high.isdisjoint(low), "uniform disjoint cover")
                insist([binary_rank(labels[i] for i in part) for part in (high, low, sparse)]
                       == [7, 6, 4], "uniform sharp cover ranks")
                if floor == 5:
                    insist(normal in sparse
                           and binary_rank(labels[i] for i in sparse - {normal}) == 3,
                           "uniform split-four rank")
                    four = sparse - {normal}
                    anchor = min(four)
                    closure_labels = {labels[i] for i in four} | {
                        labels[normal] ^ labels[anchor] ^ labels[i] for i in four}
                    insist(len(closure_labels) == 8
                           and all(label & 1 and label in root_by_label
                                   for label in closure_labels),
                           "independent small-flat closure has eight root labels")
                    closure = {root_by_label[label] for label in closure_labels}
                    insist(closure <= live, "independent small-flat roots are live")
                    insist({i for i in closure if ordinary[normal][i]} == sparse,
                           "independent small-flat nonzero evaluations are exactly sparse5")
                    extra_orthogonal = closure - sparse
                    insist(len(extra_orthogonal) == 3
                           and all(ordinary[normal][i] == 0 for i in extra_orthogonal),
                           "independent small-flat three extra roots are orthogonal")
                    small_flat_count += 1
                if per_word[normal] == 0:
                    for i in live:
                        actual = sum(ordinary[normal][i] if i in part else 0
                                     for part in (high, low, sparse))
                        insist(actual == ordinary[normal][i], "uniform actual coefficient identity")
                optimal.append((normal, mate, sum(1 << i for i in low)))
                per_word[normal] += 1
    insist(pair_count == 3780 and sum(histogram.values()) == pair_count * 127,
            "complete core hyperplane census")
    insist(all(per_word[i] == (3 if i in live else 945) for i in range(120)),
            "all root normals have the classified optimum multiplicity")
    insist(small_flat_count == 336, "independent nonframe small-flat inventory")
    return {"pairs": pair_count, "forms_per_pair": 127,
            "aggregate_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "uniform_sharpness": {"nonframe_words": 112, "frame_words": 8,
                                  "five_site_covers": sum(per_word[i] for i in live),
                                  "eight_site_covers": sum(per_word[i] for i in frame),
                                  "covers_per_nonframe_word": 3, "covers_per_frame_word": 945,
                                  "partition_ranks": [7, 6, 4],
                                  "nonframe_small_flats": small_flat_count,
                                  "nonframe_small_flat_roots": 8,
                                  "extra_orthogonal_roots": 3,
                                  "cover_digest": sha256(json.dumps(sorted(optimal),
                                      sort_keys=True, separators=(",", ":")).encode()).hexdigest()}}


def sharp_witness(model):
    roots, labels, ordinary = model["roots"], model["labels"], model["ordinary"]
    by_root = {root: i for i, root in enumerate(roots)}
    v = by_root[(2, 0, 2, 0, 0, 0, 0, 0)]
    w = by_root[(2, 0, -2, 0, 0, 0, 0, 0)]
    live = set(model["old_ids"])
    x = {i for i in live if i != v and ordinary[v][i] and not ordinary[w][i]}
    y = set()
    for i in (0, 2):
        for j in range(4, 8):
            for sign in (-1, 1):
                row = [0] * 8
                row[i], row[j] = 2, 2 * sign
                y.add(by_root[positive_line(row)])
    small = set()
    for i, j in ((1, 2), (0, 3)):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            small.add(by_root[positive_line(row)])
    sparse = small | {v}
    target = {i for i in live if ordinary[v][i]}
    insist(not (x & y or x & sparse or y & sparse), "witness supports overlap")
    insist(x | y | sparse == target, "witness exact support partition")
    sizes = [len(sparse), len(y), len(x)]
    ranks = [binary_rank(labels[i] for i in part) for part in (sparse, y, x)]
    insist(sizes == [5, 16, 32] and ranks == [4, 6, 7], "sharp witness boundary")
    four = (x, y, small, {v})
    split_sizes = [len(part) for part in four]
    split_ranks = [binary_rank(labels[i] for i in part) for part in four]
    insist(split_sizes == [32, 16, 4, 1] and split_ranks == [7, 6, 3, 1], "slack9 ranks")
    pieces = [tuple(ordinary[v][i] if i in part else 0 for i in model["old_ids"]) for part in four]
    for column, i in enumerate(model["old_ids"]):
        insist(sum(piece[column] for piece in pieces) == ordinary[v][i], "scalar codeword identity")
    code_rank = rational_rank(model["code_rows"])
    pieces_rank = rational_rank(pieces)
    joint_rank = rational_rank(model["code_rows"] + pieces)
    insist((code_rank, pieces_rank, joint_rank) == (8, 4, 11), "slack9 exact code intersection")
    # For disjoint supports, a determinant matching between any new basis and
    # these four pieces makes each new rank dominate a distinct old rank.
    # Thus their rank sum is the actual minimum basis cost, without a search.
    old_index = {root_id: i for i, root_id in enumerate(model["old_ids"])}
    return {"sizes": sizes, "ranks": ranks,
            "sparse_indices": sorted(old_index[i] for i in sparse),
            "slack9": {"sizes": split_sizes, "ranks": split_ranks,
                       "code_rank": code_rank, "pieces_rank": pieces_rank,
                       "joint_rank": joint_rank, "cost": sum(split_ranks)}}


def source_callers():
    callers = []
    pattern = re.compile(r"^d (\d+) slack (\d+) .*?(\[\[.*\]\])$", re.MULTILINE)
    for t in (2, 3):
        path = PACKAGE / f"inputs/pr3154/land_e{t}_k8.out"
        matches = list(pattern.finditer(path.read_text()))
        insist(matches, "empty CONJG2 source list")
        for match in matches:
            d, slack = map(int, match.group(1, 2))
            for weights in ast.literal_eval(match.group(3)):
                insist(all(type(w) is int and 1 <= w <= 7 for w in weights),
                        "source caller weights")
                insist(len(weights) == d + t and sum(weights) - 8 * d == slack,
                        "source caller dimension/slack")
                remaining = sorted(weights, reverse=True)
                for _ in range(d - 1):
                    if 7 not in remaining:
                        break
                    remaining.remove(7)
                else:
                    capacities = {1: 1, 2: 2, 3: 4}
                    if remaining[:2] == [7, 6] and all(w in capacities for w in remaining[2:]):
                        if sum(capacities[w] for w in remaining[2:]) <= 4:
                            callers.append({"t": t, "d": d, "slack": slack,
                                            "weights": sorted(weights, reverse=True)})
    callers.sort(key=lambda row: (row["t"], row["d"], row["slack"], row["weights"]))
    expected = {(2, 1, (7, 6, 2)), (2, 1, (7, 6, 3)),
                (2, 2, (7, 7, 6, 2)), (2, 2, (7, 7, 6, 3)),
                (3, 1, (7, 6, 1, 1)), (3, 1, (7, 6, 2, 1)),
                (3, 2, (7, 7, 6, 1, 1)), (3, 2, (7, 7, 6, 2, 1)),
                (3, 2, (7, 7, 6, 2, 2))}
    insist(len(callers) == len(expected)
            and {(row["t"], row["d"], tuple(row["weights"])) for row in callers} == expected,
            "exact nine source caller implications")
    return callers


def no_coloops(rows):
    """Rank and coverage by fundamental dependencies, without a dual census."""
    pivots, dependent = {}, 0
    for position, original in enumerate(rows):
        value, support = original, 1 << position
        while value:
            column = (value & -value).bit_length() - 1
            if column not in pivots:
                pivots[column] = value, support
                break
            row, witness = pivots[column]
            value ^= row
            support ^= witness
        else:
            dependent |= support
    return len(pivots), dependent == (1 << len(rows)) - 1


def frame_plane_census(model):
    labels, ordinary = model["labels"], model["ordinary"]
    live = set(model["old_ids"])
    frame = sorted(set(range(120)) - live)
    phases = [(normal, {i for i in live if (normal & labels[i]).bit_count() & 1})
              for normal in range(1, 512)]
    records, minimum = [], 112
    for i in frame:
        matched = [outside for normal, outside in phases
                   if not ((normal & labels[i]).bit_count() & 1)]
        insist(len(matched) == 255, "all matched independent hyperplanes")
        for j in frame:
            if i == j:
                continue
            for coefficient in (1, -1, 2):
                off = {k for k in live if ordinary[i][k] + coefficient * ordinary[j][k]}
                for outside in matched:
                    deleted = sorted(off & outside)
                    insist(no_coloops([labels[k] for k in deleted]) == (8, True),
                            "independent frame-plane rank/no-coloop criterion")
                    minimum = min(minimum, len(deleted))
                    records.append((i, j, coefficient, sum(1 << k for k in deleted)))
    insist(len(records) == 42840, "independent frame-plane census inventory")
    return {"cases": len(records), "minimum_deleted": minimum,
            "rank": 8, "all_one_point_deletions_preserve_rank": True,
            "case_digest": sha256(json.dumps(sorted(records), sort_keys=True,
                                  separators=(",", ":")).encode()).hexdigest()}


def invoice_profiles():
    sizes = (0, 1, 2, 4, 8, 12, 20, 36)
    answer = {}
    for count, total in ((3, 16), (4, 16), (4, 17)):
        rows = [row for row in product(range(1, 8), repeat=count)
                if all(row[i] >= row[i + 1] for i in range(count - 1)) and sum(row) <= total]
        survivors = []
        for row in rows:
            crude = sum(sizes[w] for w in row)
            if crude < 53:
                continue
            if crude < 70 and sum(min(sizes[w], 32) for w in row) < 53:
                continue
            eliminated = False
            for i, wi in enumerate(row):
                for j, wj in enumerate(row):
                    other = [w for k, w in enumerate(row) if k not in (i, j)]
                    if i != j and wi == 7 and wj == 6 and all(w <= 3 for w in other):
                        eliminated |= sum(sizes[w] for w in other) <= 4
            if not eliminated:
                survivors.append(list(row))
        answer[str(count) + ":" + str(total)] = {"examined": len(rows), "survivors": sorted(survivors)}
    return answer


def root_plane_inventory(model):
    roots = model["roots"]
    planes = set()
    for i, j in combinations(range(120), 2):
        a, b = roots[i], roots[j]
        ab = scalar(a, b)
        denominator = 64 - ab * ab
        members = []
        for k, c in enumerate(roots):
            ac, bc = scalar(a, c), scalar(b, c)
            left, right = 8 * ac - ab * bc, 8 * bc - ab * ac
            if all(denominator * z == left * x + right * y for x, y, z in zip(a, b, c)):
                members.append(k)
        insist(2 <= len(members) <= 3, "independent rational root-plane cap")
        planes.add(sum(1 << k for k in members))
    counts = Counter(mask.bit_count() for mask in planes)
    frame = sorted(set(range(120)) - set(model["old_ids"]))
    active_counts = Counter()
    for plane in planes:
        if plane.bit_count() != 3:
            continue
        members = [roots[k] for k in range(120) if plane >> k & 1]
        active = sum(any(scalar(a, roots[f]) for a in members) for f in frame)
        contained_frame = sum((plane >> f) & 1 for f in frame)
        insist((active, contained_frame) in ((4, 1), (6, 0)), "independent A2 active axes")
        active_counts[active] += 1
    insist(active_counts == {4: 224, 6: 896}, "independent A2 frame-support inventory")
    return {"root_pairs": 7140, "distinct_planes": len(planes),
            "root_line_histogram": {str(k): v for k, v in sorted(counts.items())},
            "a2_active_axes": {str(k): v for k, v in sorted(active_counts.items())},
            "plane_digest": sha256(json.dumps(sorted(planes), separators=(",", ":")).encode()).hexdigest()}


def four_axis_inventory(model):
    frame = sorted(set(range(120)) - set(model["old_ids"]))
    counts = Counter()
    for axes in combinations(frame, 4):
        forms = Counter()
        for site in model["old_ids"]:
            row = tuple(scalar(model["roots"][site], model["roots"][a]) // 4 for a in axes)
            lead = next((x for x in row if x), 1)
            forms[tuple(lead * x for x in row)] += 1
        inventory = Counter((sum(x != 0 for x in row), multiplicity)
                            for row, multiplicity in forms.items())
        if inventory == {(0, 8): 1, (2, 8): 12, (4, 1): 8}:
            counts['block'] += 1
        else:
            insist(inventory == {(1, 8): 4, (2, 4): 12, (3, 2): 16},
                   "independent nonblock restricted forms")
            counts['nonblock'] += 1
    insist(counts == {'block': 14, 'nonblock': 56}, "independent four-axis set count")
    return {'sets': 70, 'block_sets': counts['block'], 'nonblock_sets': counts['nonblock'],
            'block_multiplicities': {'zero': 8, 'pair': 8, 'four': 1},
            'nonblock_multiplicities': {'singleton': 8, 'pair': 4, 'triple': 2}}


def pencil_applications():
    sizes = (0, 1, 2, 4, 8, 12, 20, 36)
    rows, shared = [], []
    pattern = re.compile(r"^d (\d+) slack (\d+) .*?(\[\[.*\]\])$", re.MULTILINE)
    for t in (2, 3):
        text = (PACKAGE / f"inputs/pr3154/land_e{t}_k8.out").read_text()
        for match in pattern.finditer(text):
            d, slack = map(int, match.group(1, 2))
            if d < 2:
                continue
            for weights in ast.literal_eval(match.group(3)):
                if t == 2 and any(all(w <= cap for w, cap in zip(sorted(
                        [w for i, w in enumerate(weights) if i not in killed], reverse=True),
                        (7, 7, 5, 5))) for killed in combinations(range(len(weights)), d - 2)):
                    shared.append((t, d, slack, weights))
                found = False
                for killed in combinations(range(len(weights)), d - 2):
                    remaining = [w for i, w in enumerate(weights) if i not in killed]
                    for main in combinations(range(len(remaining)), 4):
                        if all(remaining[i] <= 6 for i in main) and sum(
                                sizes[w] for i, w in enumerate(remaining) if i not in main) <= 9:
                            found = True
                            break
                    if found:
                        break
                if found:
                    rows.append((t, d, slack, weights))
    counts = Counter(row[0] for row in rows)
    return {"t2": counts[2], "t3": counts[3], "total": len(rows),
            "application_digest": sha256(json.dumps(sorted(rows), sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest(),
            "shared_frame_7755": shared}


def frame_sign_inventory(model):
    labels, dots, residues = model["labels"], model["ordinary"], model["residues"]
    frame = sorted(set(range(120)) - set(model["old_ids"]))
    records = []
    for a, b in combinations(frame, 2):
        common = [i for i in range(120) if i not in (a, b) and dots[a][i] and dots[b][i]]
        same = {i for i in common if (dots[a][i] > 0) == (dots[b][i] > 0)}
        opposite = set(common) - same
        insist(len(common) == 24 and len(same) == len(opposite) == 12,
                "independent frame sign-half cardinalities")
        insist(binary_rank(labels[i] for i in same) == binary_rank(labels[i] for i in opposite) == 7,
                "independent sign-half binary rank")
        classes = {}
        for i in common:
            key = min(residues[i], residues[i] ^ residues[a], residues[i] ^ residues[b],
                      residues[i] ^ residues[a] ^ residues[b])
            classes.setdefault(key, []).append(i)
        insist(len(classes) == 6 and all(len(v) == 4 and len(set(v) & same) == 2
                                         for v in classes.values()),
                "independent sign-half quotient-fiber multiplicities")
        records.append((a, b, sum(1 << i for i in same), sum(1 << i for i in opposite)))
    return {"frame_pairs": 28, "sign_halves": 56, "half_size": 12,
            "binary_rank": 7, "radical_fibers_per_pair": 6, "half_points_per_fiber": 2,
            "case_digest": sha256(json.dumps(records, sort_keys=True,
                                  separators=(",", ":")).encode()).hexdigest()}


def root764_inventory(model):
    labels, residues = model["labels"], model["residues"]
    bilinear = model["bilinear"]
    all_roots = (1 << len(labels)) - 1
    polar_one = [sum(1 << i for i, residue in enumerate(residues)
                     if bilinear[normal][residue]) for normal in range(256)]
    sections, root_high_pairs = set(), 0
    for root in residues:
        root_sections, generated = set(), 0
        for second in range(256):
            if not bilinear[root][second]:
                continue
            for offset in range(2):
                second_slice = polar_one[second] if offset else all_roots ^ polar_one[second]
                section = polar_one[root] & second_slice
                insist(section.bit_count() == 28, "independent root764 complementary section28")
                root_sections.add(section)
                generated += 1
        insist(generated == 256 and len(root_sections) == 128,
               "independent root764 second-form duplicate multiplicity")
        root_high_pairs += len(root_sections)
        sections.update(root_sections)
    insist(root_high_pairs == 15360, "independent root764 root/high inventory")
    expected_histogram = Counter({0: 1, 12: 63, 16: 63})
    for section in sorted(sections):
        section_labels = [labels[i] for i in range(len(labels)) if section >> i & 1]
        basis, coordinates = coordinates_in_span(section_labels)
        insist(len(basis) == 7, "independent root764 complementary label rank7")
        points = [coordinates[label] for label in section_labels]
        histogram = Counter(sum(not ((point & functional).bit_count() & 1)
                                for point in points)
                            for functional in range(1, 1 << len(basis)))
        insist(histogram == expected_histogram,
               "independent root764 complementary hyperplane histogram")
    return {"root_high_pairs": root_high_pairs, "c28_sections": len(sections),
            "c28_section_histogram": {str(k): v for k, v in sorted(expected_histogram.items())},
            "c28_digest": sha256(json.dumps(sorted(sections),
                                           separators=(",", ":")).encode()).hexdigest()}


def quotient6_inventory():
    # Deduplicate actual point sets, rather than selecting annihilator bases.
    roots = {x for x in range(64) if ((x & (x >> 1) & 21).bit_count() & 1)}
    hyperplanes = [frozenset(x for x in range(64) if (x & a).bit_count() % 2 == offset)
                   for a in range(1, 64) for offset in range(2)]
    four = {left & right for left, right in combinations(hyperplanes, 2)
            if len(left & right) == 16}
    insist(len(roots) == 28 and len(hyperplanes) == 126 and len(four) == 2604,
           "independent six-quadric affine inventory")
    histograms = {4: Counter(len(flat & roots) for flat in four),
                  5: Counter(len(flat & roots) for flat in hyperplanes)}
    insist(max(histograms[4]) == 10 and max(histograms[5]) == 16,
           "independent six-quadric affine capacities")
    return {str(d): {str(k): v for k, v in sorted(counts.items())}
            for d, counts in histograms.items()}


def d2_profile_inventory():
    capacities = {1: 1, 2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
    answer = {}
    for length, budget in ((4, 24), (5, 25)):
        # Build ordered positive partitions recursively, not combinations-with-replacement.
        def partitions(size, ceiling, remaining):
            if size == 0:
                yield []
                return
            for first in range(1, min(ceiling, remaining - size + 1) + 1):
                for tail in partitions(size - 1, first, remaining - first):
                    yield [first] + tail
        rows = list(partitions(length, 7, budget))
        kept = []
        for row in rows:
            if max(row) < 7:
                continue  # The written four-six lemma, or 55555 and distance53.
            others = row[1:]
            capacity = sum(capacities[x] for x in others)
            root_capacity = sum(min(32, capacities[x]) for x in others)
            if capacity < 53 or (capacity < 70 and root_capacity < 53):
                continue
            tails = others.copy()
            if 6 in tails and 7 in tails:
                tails.remove(6)
                tails.remove(7)
                if sum(capacities[x] for x in tails) < 5:
                    continue
            kept.append(row)
        forbidden = [[7, 7, 5, 5], [7, 7, 6, 4]] if length == 4 else [[7, 6, 6, 5, 1]]
        insist(all(row in kept for row in forbidden), "independent intrinsic d2 profiles")
        answer[str(length) + ':' + str(budget)] = {
            'examined': len(rows), 'intrinsic_exclusions': forbidden,
            'actual_profiles': sorted(row for row in kept if row not in forbidden)}
    return answer


def run():
    model = independent_model()
    affine, extra = section_census(model)
    extra.update({"coordinate_method": "independent root polar-pairing basis",
                  "section_method": "ordinary-dot left-pivot RREF annihilators",
                  "source_hashes": model["source_hashes"],
                  "simple_label_transfer": model["simple_transfer"],
                  "old_label_transfer": model["old_transfer"]})
    return {"root_inventory": {"full": len(model["roots"]), "live": len(model["old_ids"]),
                               "frame": len(model["frame"])},
            "affine6_sections": affine, "core_sections": core_census(model),
            "witness": sharp_witness(model), "callers": source_callers(),
            "frame_plane": frame_plane_census(model),
            "invoice_profiles": invoice_profiles(),
            "root_planes": root_plane_inventory(model), "pencil_callers": pencil_applications(),
            "frame_sign_halves": frame_sign_inventory(model),
            "root764": root764_inventory(model),
            "quotient6": quotient6_inventory(),
            "d2_profiles": d2_profile_inventory(),
            "four_axes": four_axis_inventory(model),
            "independent_engine": extra}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
