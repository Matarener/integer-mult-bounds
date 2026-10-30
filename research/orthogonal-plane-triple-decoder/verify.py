#!/usr/bin/env python3
"""Check the rank-135 alternating-plane fitting construction. Writes nothing."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
FILES = ("CERTIFICATE.json", "README.md", "SOURCES.json", "TASK.json",
         "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() % 2


def planes():
    vectors = [a for a in range(1, 128) if a.bit_count() % 2 == 0]
    result = {tuple(sorted((a, b, a ^ b)))
              for a, b in combinations(vectors, 2) if dot(a, b) == 1}
    require(len(vectors) == 63 and len(result) == 336, "port count")
    return tuple(sorted(result))


def rref_planes():
    """Independent complete two-space enumeration in six even coordinates."""
    result = set()
    total = 0
    for i, j in combinations(range(6), 2):
        slots = [(0, k) for k in range(i + 1, 6) if k != j]
        slots += [(1, k) for k in range(j + 1, 6)]
        for values in product((0, 1), repeat=len(slots)):
            rows = [1 << i, 1 << j]
            for (r, k), value in zip(slots, values, strict=True):
                rows[r] |= value << k
            a, b = [x | ((x.bit_count() % 2) << 6) for x in rows]
            total += 1
            if dot(a, b):
                result.add(tuple(sorted((a, b, a ^ b))))
    require(total == 651, "RREF coverage")
    return tuple(sorted(result))


def orthogonal(e, f):
    return all(dot(a, b) == 0 for a in e for b in f)


def greedy_partition(ports):
    """Replay the finite construction, without a search or optimization."""
    adjacent = [{j for j, f in enumerate(ports) if orthogonal(e, f)}
                for e in ports]
    require(all(len(neighbors) == 20 for neighbors in adjacent), "degree")
    blocks = []
    left = set(range(336))
    triples = 0
    for i in range(336):
        for j in sorted(adjacent[i]):
            if j <= i:
                continue
            for k in sorted(adjacent[i] & adjacent[j]):
                if k > j:
                    triples += 1
                    if {i, j, k} <= left:
                        blocks.append([i, j, k])
                        left.difference_update((i, j, k))
    require(triples == 1120, "triple census")
    for i in sorted(left.copy()):
        if i not in left:
            continue
        options = sorted(left & adjacent[i])
        if options:
            blocks.append([i, options[0]])
            left.difference_update(blocks[-1])
    blocks.extend([i] for i in sorted(left))
    return blocks


def check_partition(ports, blocks):
    require(type(blocks) is list and 1 <= len(blocks) <= 336, "block list")
    seen = []
    for block in blocks:
        require(type(block) is list and 1 <= len(block) <= 3, "block size")
        require(all(type(i) is int and 0 <= i < 336 for i in block), "index")
        require(len(set(block)) == len(block), "repeated index")
        require(all(orthogonal(ports[i], ports[j])
                    for i, j in combinations(block, 2)), "orthogonality")
        seen.extend(block)
    require(sorted(seen) == list(range(336)), "partition coverage")


def binary_rank(rows, width):
    require(0 <= width <= 336 and len(rows) <= 336, "rank dimensions")
    pivots = [0] * width
    rank = 0
    for original in rows:
        require(type(original) is int and 0 <= original < (1 << width), "row")
        row = original
        for bit in range(width - 1, -1, -1):
            if row & (1 << bit):
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    rank += 1
                    break
    return rank


def check_matrix(ports, blocks):
    incidence = [[int(i in block) for block in blocks] for i in range(336)]
    matrix = [[sum(a * b for a, b in zip(u, v, strict=True))
               for v in incidence] for u in incidence]
    owner = {i: b for b, block in enumerate(blocks) for i in block}
    for i in range(336):
        for j in range(336):
            require(matrix[i][j] == int(owner[i] == owner[j]), "factorization")
            if i == j:
                require(matrix[i][j] == 1, "diagonal")
            elif not orthogonal(ports[i], ports[j]):
                require(matrix[i][j] == 0, "forbidden entry")
    anchors = [block[0] for block in blocks]
    for a, i in enumerate(anchors):
        for b, j in enumerate(anchors):
            require(matrix[i][j] == int(a == b), "identity minor")
    packed = [sum(x << j for j, x in enumerate(row)) for row in matrix]
    require(binary_rank(packed, 336) == len(blocks), "independent binary rank")
    return matrix


def check_tariff(ports, blocks):
    tariffs = []
    for block in blocks:
        generators = [a for i in block for a in ports[i][:2]]
        require(binary_rank(generators, 7) == 2 * len(block), "span dimension")
        gram = [sum(dot(a, b) << j for j, b in enumerate(generators))
                for a in generators]
        tariff = binary_rank(gram, len(generators))
        require(tariff == 2 * len(block), "term tariff")
        tariffs.append(tariff)
    require(sum(tariffs) == 672, "total tariff")
    return tariffs


def controls(ports, blocks):
    bad_pair = next([i, j] for i, j in combinations(range(336), 2)
                    if not orthogonal(ports[i], ports[j]))
    cases = [(blocks[:-1], "partition coverage"),
             (blocks + [blocks[0]], "partition coverage"),
             ([bad_pair] + blocks[1:], "orthogonality"),
             ([[True]] + blocks[1:], "index"),
             ([[336]] + blocks[1:], "index"),
             ([[0, 0]] + blocks[1:], "repeated index"),
             ([[0, 1, 2, 3]] + blocks[1:], "block size"),
             ([[]] + blocks[1:], "block size")]
    for candidate, expected in cases:
        try:
            check_partition(ports, candidate)
        except ValueError as exc:
            require(str(exc) == expected, "wrong rejection reason")
        else:
            raise ValueError("accepted invalid partition")
    return len(cases)


def read_small(path):
    with path.open("rb") as stream:
        data = stream.read(1_048_577)
    require(len(data) <= 1_048_576, "file capacity")
    return data


def main():
    ports = planes()
    require(ports == rref_planes(), "independent port enumeration")
    certificate = json.loads(read_small(HERE / "CERTIFICATE.json"))
    require(type(certificate) is dict and set(certificate) == {"blocks"},
            "certificate schema")
    blocks = certificate["blocks"]
    check_partition(ports, blocks)
    require(blocks == greedy_partition(ports), "construction replay")
    require(Counter(map(len, blocks)) == {1: 18, 2: 33, 3: 84}, "block counts")
    require(len(blocks) == 135 < 168, "strict rank improvement")
    matrix = check_matrix(ports, blocks)
    tariffs = check_tariff(ports, blocks)
    rejected = controls(ports, blocks)
    receipt = {
        "status": "PASS_ORTHOGONAL_PLANE_TRIPLE_DECODER",
        "ports": len(ports), "blocks": len(blocks),
        "block_sizes": dict(sorted(Counter(map(len, blocks)).items())),
        "fitting_entries": sum(map(len, matrix)), "exact_rank": len(blocks),
        "identity_minor_entries": len(blocks) ** 2,
        "tariffs": dict(sorted(Counter(tariffs).items())),
        "copy_mass": sum(tariffs), "rejection_controls": rejected,
        "sha256": {name: sha256(read_small(HERE / name)).hexdigest()
                   for name in FILES},
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print("PASS_ORTHOGONAL_PLANE_TRIPLE_DECODER rank=135 copy_mass=672")


if __name__ == "__main__":
    main()
