#!/usr/bin/env python3
"""Exact finite check for one class-C V2 stabilizer-orbit quotient.

All finite-field and rational calculations use Python integers/Fractions.
The result is conditional on the pinned data88 catalog being complete for
|Off(h)| <= 88, as stated by its source package.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
REAL_MAPS = PKG / "REAL_MAPS.json"
DATA88 = ROOT / "research/k2-class-c-stabilizer-orbit-inputs/data88.txt"
DATA80 = ROOT / "research/one-sided-excess-three/data/data80.txt"
GENS_FILE = ROOT / "research/one-sided-excess-three/data/gens.txt"
EXPECTED_SHA256 = {
    DATA88: "7a207989d901f488120988007dcad3d8edf3b8b1ba79eac7307256925b915667",
    DATA80: "d23ad440471c3afd1a894b3439e29a05f498edfe2af33d7a667ca1d8f1d6b9c5",
    GENS_FILE: "0679ba17f68761c9aea31230df8a7ac4a86533b24ee53d786dd1afa216a4b2c9",
}
N_LABELS = 112
N_BITS = 9
N_DIRECTIONS = 18100
SEED_FLAT = (4, 8, 32, 210, 321)
STABILIZER_GENERATORS = 5
V2_DIM = 6
EXPECTED_RAW_V2 = 788035
EXPECTED_V2_MASKS = 776806
EXPECTED_V2_ORBITS = 47850


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def checked_source_hashes():
    for path, expected in EXPECTED_SHA256.items():
        require(path.is_file(), f"missing pinned input: {path}")
        actual = digest(path)
        require(actual == expected,
                f"source hash mismatch for {path}: {actual} != {expected}")


def rref(vectors):
    """Canonical RREF basis of the GF(2) span, 9-bit integers."""
    rows = [0] * N_BITS
    for raw in vectors:
        value = raw
        for pivot in range(N_BITS - 1, -1, -1):
            if not ((value >> pivot) & 1):
                continue
            if rows[pivot]:
                value ^= rows[pivot]
            else:
                rows[pivot] = value
                break
    for pivot in range(N_BITS):
        if rows[pivot]:
            for lower in range(pivot + 1, N_BITS):
                if rows[lower] & (1 << pivot):
                    rows[lower] ^= rows[pivot]
    return tuple(rows[p] for p in range(N_BITS) if rows[p])


def load_sources():
    data_lines = DATA88.read_text(encoding="ascii").splitlines()
    require(len(data_lines) > 115, "data88 header is incomplete")
    labels = tuple(map(int, data_lines[0].split()))
    require(len(labels) == N_LABELS and len(set(labels)) == N_LABELS,
            "P112 labels must be 112 distinct entries")
    require(labels == tuple(map(int, DATA80.read_text(encoding="ascii").splitlines()[0].split())),
            "data88 label order differs from the pinned main-tree label source")
    directions_expected = int(data_lines[114])
    require(directions_expected == N_DIRECTIONS,
            f"expected {N_DIRECTIONS} directions, found {directions_expected}")

    directions = []
    direction_index = {}
    for line_number, line in enumerate(data_lines[115:], start=116):
        try:
            header, tail = line.split(":", 1)
            fields = list(map(int, header.split()))
            kind = fields[0]
            vector_count = 2 if kind == 2 else 1
            require(kind in (1, 2), f"bad direction type on line {line_number}")
            require(len(fields) == 1 + 8 * vector_count,
                    f"bad coordinate count on line {line_number}")
            vectors = tuple(tuple(fields[1 + 8 * j:1 + 8 * (j + 1)])
                            for j in range(vector_count))
            off = tuple(map(int, tail.split()))
        except (ValueError, IndexError) as exc:
            raise AssertionError(f"malformed data88 line {line_number}: {exc}") from exc
        require(off == tuple(sorted(off)) and len(off) == len(set(off)),
                f"Off support is not a sorted set on line {line_number}")
        require(all(0 <= t < N_LABELS for t in off),
                f"Off support index outside P112 on line {line_number}")
        key = (kind, off)
        require(key not in direction_index,
                f"duplicate typed Off support on line {line_number}")
        require(rank_q(vectors) == vector_count,
                f"dependent real basis vectors on line {line_number}")
        direction_index[key] = len(directions)
        directions.append((kind, vectors, off))
    require(len(directions) == directions_expected,
            f"data88 declares {directions_expected} directions but contains {len(directions)}")

    generators = []
    for line_number, line in enumerate(GENS_FILE.read_text(encoding="ascii").splitlines(), start=1):
        row = tuple(map(int, line.split()))
        validate_permutation(row, f"generator {line_number}")
        generators.append(row)
    require(len(generators) == 12, f"expected 12 generators, found {len(generators)}")
    return labels, directions, direction_index, generators


def validate_permutation(permutation, name="permutation"):
    require(len(permutation) == N_LABELS and set(permutation) == set(range(N_LABELS)),
            f"{name} is not a permutation of 0..111")


def label_action(labels, permutation):
    """Recover and check the full invertible F2^9 action from P112 images."""
    validate_permutation(permutation)
    basis = []
    images = []
    for label, target_index in zip(labels, permutation):
        candidate = rref((*basis, label))
        if len(candidate) > len(basis):
            basis.append(label)
            images.append(labels[target_index])
        if len(basis) == N_BITS:
            break
    require(len(basis) == N_BITS, "P112 labels do not span F2^9")

    coordinates = {0: 0}
    for index, vector in enumerate(basis):
        old = list(coordinates.items())
        coordinates.update({value ^ vector: coeff ^ (1 << index)
                            for value, coeff in old})
    require(len(coordinates) == (1 << N_BITS), "basis coordinate map is not bijective")

    def apply(value):
        coeff = coordinates[value]
        image = 0
        for index, vector in enumerate(images):
            if (coeff >> index) & 1:
                image ^= vector
        return image

    for label, target_index in zip(labels, permutation):
        require(apply(label) == labels[target_index],
                "generator's P112 permutation is not induced by one linear map")
    image_space = {apply(value) for value in range(1 << N_BITS)}
    require(len(image_space) == (1 << N_BITS), "label-space action is singular")
    return tuple(apply(value) for value in range(1 << N_BITS))


def rank_q(vectors):
    """Exact rank over Q of row vectors."""
    if not vectors:
        return 0
    matrix = [[Fraction(value) for value in vector] for vector in vectors]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((row for row in range(rank, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [value / scale for value in matrix[rank]]
        for row in range(len(matrix)):
            if row != rank and matrix[row][column]:
                scale = matrix[row][column]
                matrix[row] = [x - scale * y
                               for x, y in zip(matrix[row], matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def row_times_matrix(vector, matrix):
    return tuple(sum(Fraction(vector[i]) * matrix[i][j] for i in range(8))
                 for j in range(8))


def proportional(left, right):
    ratios = []
    for x, y in zip(left, right):
        if y:
            ratios.append(x / Fraction(y))
        elif x:
            return False
    return bool(ratios) and all(value == ratios[0] for value in ratios)


def in_span(basis, vector):
    return rank_q((*basis, vector)) == rank_q(basis)


def direction_image(directions, direction_index, permutation):
    """The source catalog direction permutation induced by one root permutation."""
    validate_permutation(permutation)
    target = []
    for kind, _vectors, off in directions:
        require(off == tuple(sorted(off)) and len(off) == len(set(off))
                and all(0 <= t < N_LABELS for t in off),
                "malformed Off support in direction catalog")
        image_support = tuple(sorted(permutation[t] for t in off))
        key = (kind, image_support)
        require(key in direction_index,
                "generator does not preserve typed data88 Off supports")
        target.append(direction_index[key])
    require(len(set(target)) == len(directions),
            "generator does not permute the full typed direction catalog")
    return target


def verify_real_matrix(directions, target, matrix):
    """Check one supplied exact Q^8 witness against every listed direction."""
    require(len(matrix) == 8 and all(len(row) == 8 for row in matrix),
            "real-space matrix is not 8 by 8")
    require(rank_q(matrix) == 8, "real-space matrix witness is singular")
    for index, (kind, vectors, _off) in enumerate(directions):
        image_vectors = [row_times_matrix(vector, matrix) for vector in vectors]
        target_vectors = directions[target[index]][1]
        if kind == 1:
            require(proportional(image_vectors[0], target_vectors[0]),
                    f"line direction {index} does not map to its support image")
        else:
            require(all(in_span(target_vectors, vector) for vector in image_vectors),
                    f"plane direction {index} does not map to its support image")


def load_real_matrix_witnesses():
    require(REAL_MAPS.is_file(), "missing exact real-space map witnesses")
    receipt = json.loads(REAL_MAPS.read_text(encoding="ascii"))
    require(receipt.get("schema_version") == 1, "unsupported REAL_MAPS schema")
    require(receipt.get("source_data88_sha256") == digest(DATA88),
            "REAL_MAPS data88 source binding differs")
    require(receipt.get("source_gens_sha256") == digest(GENS_FILE),
            "REAL_MAPS generator source binding differs")
    raw_maps = receipt.get("maps")
    require(isinstance(raw_maps, list) and len(raw_maps) == 12,
            "REAL_MAPS must contain one matrix per generator")
    matrices = []
    for generator_index, raw_matrix in enumerate(raw_maps):
        require(len(raw_matrix) == 8 and all(len(row) == 8 for row in raw_matrix),
                f"bad REAL_MAPS shape for generator {generator_index}")
        try:
            matrix = [[Fraction(entry[0], entry[1]) for entry in row]
                      for row in raw_matrix]
        except (IndexError, TypeError, ZeroDivisionError) as exc:
            raise AssertionError(f"bad rational matrix entry for generator {generator_index}") from exc
        matrices.append(matrix)
    return matrices


def all_rref_bases(dimension):
    """Every subspace once via its unique reduced row-echelon basis."""
    for pivots in combinations(range(N_BITS), dimension):
        pivot_set = set(pivots)
        free_by_row = []
        for pivot in reversed(pivots):
            free_by_row.append((pivot, [bit for bit in range(pivot)
                                        if bit not in pivot_set]))
        choices_by_row = [range(1 << len(free)) for _pivot, free in free_by_row]
        for choices in product(*choices_by_row):
            basis = []
            for (pivot, free), choice in zip(free_by_row, choices):
                value = 1 << pivot
                for index, bit in enumerate(free):
                    if (choice >> index) & 1:
                        value |= 1 << bit
                basis.append(value)
            yield tuple(basis)


def gaussian_binomial_2(n, k):
    numerator = 1
    denominator = 1
    for index in range(k):
        numerator *= (1 << (n - index)) - 1
        denominator *= (1 << (k - index)) - 1
    require(numerator % denominator == 0, "nonintegral Gaussian binomial")
    return numerator // denominator


def flat_mask(basis, label_index):
    span = [0]
    for vector in basis:
        old = span[:]
        span.extend(value ^ vector for value in old)
    require(len(span) == (1 << len(basis)), "flat basis is dependent")
    mask = 0
    for value in span:
        index = label_index.get(value)
        if index is not None:
            mask |= 1 << index
    return mask


def make_mask_lut(permutation):
    return [[sum(1 << permutation[8 * byte + bit]
                 for bit in range(8) if (value >> bit) & 1)
             for value in range(256)] for byte in range(14)]


def apply_mask_lut(mask, lookup):
    result = 0
    for byte, table in enumerate(lookup):
        result |= table[(mask >> (8 * byte)) & 255]
    return result


def compose(left, right):
    """Permutation product left o right."""
    return tuple(left[right[index]] for index in range(N_LABELS))


def inverse_permutation(permutation):
    result = [0] * N_LABELS
    for source, target in enumerate(permutation):
        result[target] = source
    return tuple(result)


def all_five_first_flat_orbit(labels, generators, mask_luts, seed_mask):
    parents = {seed_mask: None}
    queue = [seed_mask]
    for mask in queue:
        for generator_index, lookup in enumerate(mask_luts):
            image = apply_mask_lut(mask, lookup)
            if image not in parents:
                parents[image] = (mask, generator_index)
                queue.append(image)
    canonical_mask = min(parents)
    path = []
    current = canonical_mask
    while current != seed_mask:
        parent, generator_index = parents[current]
        path.append(generator_index)
        current = parent
    path.reverse()
    word = tuple(range(N_LABELS))
    for generator_index in path:
        word = compose(generators[generator_index], word)
    require(apply_mask_lut(seed_mask, make_mask_lut(word)) == canonical_mask,
            "reconstructed orbit word does not reach the canonical first flat")
    return canonical_mask, word, len(parents)


def expected_rejection(function, description):
    try:
        function()
    except (AssertionError, ValueError, KeyError):
        return
    raise AssertionError(f"negative control was accepted: {description}")


def run():
    start = perf_counter()
    checked_source_hashes()
    labels, directions, direction_index, generators = load_sources()
    label_maps = [label_action(labels, generator) for generator in generators]
    real_maps = load_real_matrix_witnesses()
    direction_maps = []
    for index, generator in enumerate(generators):
        target = direction_image(directions, direction_index, generator)
        verify_real_matrix(directions, target, real_maps[index])
        direction_maps.append(target)

    seed = SEED_FLAT
    require(rref(seed) == seed and len(seed) == 5,
            "fixed seed is not the declared 5-flat RREF basis")
    stabilizer_label_generators = generators[:STABILIZER_GENERATORS]
    for index in range(STABILIZER_GENERATORS):
        require(rref(tuple(label_maps[index][value] for value in seed)) == seed,
                f"generator {index} does not fix the seed 5-flat")

    label_index = {label: index for index, label in enumerate(labels)}
    require(len(label_index) == N_LABELS, "P112 labels are not distinct")
    seed_mask = flat_mask(seed, label_index)
    all_mask_luts = [make_mask_lut(generator) for generator in generators]
    for index in range(STABILIZER_GENERATORS):
        require(apply_mask_lut(seed_mask, all_mask_luts[index]) == seed_mask,
                f"generator {index} does not fix the seed root mask")

    canonical_first_mask, word, first_mask_orbit_size = all_five_first_flat_orbit(
        labels, generators, all_mask_luts, seed_mask)
    inverse_word = inverse_permutation(word)
    conjugate_generators = [compose(word, compose(generator, inverse_word))
                            for generator in stabilizer_label_generators]
    conjugate_luts = [make_mask_lut(generator) for generator in conjugate_generators]
    for index, lookup in enumerate(conjugate_luts):
        require(apply_mask_lut(canonical_first_mask, lookup) == canonical_first_mask,
                f"conjugate stabilizer generator {index} does not fix the canonical first mask")

    raw_v2_count = 0
    v2_masks = set()
    for basis in all_rref_bases(V2_DIM):
        raw_v2_count += 1
        v2_masks.add(flat_mask(basis, label_index))
    require(raw_v2_count == gaussian_binomial_2(N_BITS, V2_DIM),
            "RREF enumeration does not match the Gaussian binomial")
    require(raw_v2_count == EXPECTED_RAW_V2,
            f"unexpected raw six-flat count: {raw_v2_count}")
    require(len(v2_masks) == EXPECTED_V2_MASKS,
            f"unexpected number of distinct six-flat root masks: {len(v2_masks)}")

    # Because the full universe remains available, this check rejects any
    # generator action that fails to preserve the deduplicated SUB masks.
    unseen = set(v2_masks)
    orbit_sizes = []
    while unseen:
        root = next(iter(unseen))
        unseen.remove(root)
        stack = [root]
        size = 0
        while stack:
            mask = stack.pop()
            size += 1
            for lookup in conjugate_luts:
                image = apply_mask_lut(mask, lookup)
                require(image in v2_masks,
                        "stabilizer action does not preserve the six-flat mask universe")
                if image in unseen:
                    unseen.remove(image)
                    stack.append(image)
        orbit_sizes.append(size)
    orbit_count = len(orbit_sizes)
    require(orbit_count == EXPECTED_V2_ORBITS,
            f"unexpected stabilizer orbit count: {orbit_count}")
    require(sum(orbit_sizes) == EXPECTED_V2_MASKS,
            "orbit partition does not cover every six-flat root mask")

    # Negative controls: malformed label action, malformed support, and a
    # singular real map must fail closed.
    bad_permutation = list(generators[0])
    bad_permutation[0] = bad_permutation[1]
    expected_rejection(lambda: validate_permutation(bad_permutation),
                       "non-permutation label action")
    bad_directions = list(directions)
    bad_kind, bad_vectors, bad_off = bad_directions[0]
    bad_directions[0] = (bad_kind, bad_vectors, (112, *bad_off))
    expected_rejection(
        lambda: direction_image(bad_directions, direction_index, generators[0]),
        "out-of-range Off support")
    singular = [[Fraction(0) for _ in range(8)] for _ in range(8)]
    expected_rejection(lambda: require(rank_q(singular) == 8,
                                       "singular real-space symmetry map"),
                       "singular real-space symmetry map")

    elapsed = perf_counter() - start
    print("PASS_K2_CLASS_C_STABILIZER_ORBIT_QUOTIENT")
    print(f"directions={len(directions)} generators={len(generators)} exact_Q_maps={len(real_maps)}")
    print(f"seed_flat_basis={seed} seed_root_mask={seed_mask}")
    print(f"first_flat_mask_orbit={first_mask_orbit_size} canonical_mask={canonical_first_mask}")
    print(f"V2_dim={V2_DIM} raw_flats={raw_v2_count} distinct_root_masks={len(v2_masks)}")
    print(f"stabilizer_generators={len(conjugate_generators)} orbits={orbit_count} "
          f"max_orbit={max(orbit_sizes)} min_orbit={min(orbit_sizes)}")
    print(f"candidate_reduction={len(v2_masks)}/{orbit_count}="
          f"{len(v2_masks) / orbit_count:.12f}x")
    print(f"elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    run()
