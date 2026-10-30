# SPDX-License-Identifier: Apache-2.0
"""Complete finite classification over F_2; produced by Nick Petalas."""

from collections import Counter
from itertools import product

PROFILES = ((3, 1, 1, 1, 1), (2, 2, 1, 1, 1), (2, 1, 2, 1, 1))
N = 7
MASK = (1 << N) - 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def layout(widths):
    require(tuple(widths) in PROFILES, "unsupported width profile")
    owners = tuple(i for i, d in enumerate(widths) for _ in range(d))
    positions = tuple(
        N * a + b for a in range(N) for b in range(N)
        if (owners[a] - owners[b]) % 5 in (1, 4)
    )
    generators = tuple(
        (a, b) for a in range(N) for b in range(N)
        if a != b and owners[a] == owners[b]
    )
    identity = sum(1 << (N * a + a) for a in range(N))
    return owners, positions, generators, identity


def rank(word):
    """Row elimination using highest-set-bit pivots."""
    pivots = [0] * N
    answer = 0
    for i in range(N):
        row = (word >> (N * i)) & MASK
        for _ in range(N):
            if not row:
                break
            j = row.bit_length() - 1
            if pivots[j]:
                row ^= pivots[j]
            else:
                pivots[j] = row
                answer += 1
                break
    return answer


def image_rank(word):
    """Independent rank: enumerate the complete column image."""
    image = {0}
    for j in range(N):
        column = sum(((word >> (N * i + j)) & 1) << i for i in range(N))
        image |= {value ^ column for value in image}
    require(len(image) & (len(image) - 1) == 0, "image not a binary space")
    return len(image).bit_length() - 1


def conjugate(word, a, b):
    """Conjugate by I+E_ab, whose inverse is itself in F_2."""
    word ^= ((word >> (N * b)) & MASK) << (N * a)
    column_mask = sum(1 << (N * i + a) for i in range(N))
    column = word & column_mask
    word ^= column << (b - a) if b > a else column >> (a - b)
    return word


def dense_conjugate(word, a, b):
    """Independent entry-array implementation of the same matrix product."""
    entries = [[(word >> (N * i + j)) & 1 for j in range(N)] for i in range(N)]
    entries[a] = [x ^ y for x, y in zip(entries[a], entries[b])]
    for i in range(N):
        entries[i][b] ^= entries[i][a]
    return sum(entries[i][j] << (N * i + j) for i in range(N) for j in range(N))


def orbit(word, generators, group_order):
    reached = {word}
    pending = [word]
    for cursor in range(group_order):
        if cursor == len(pending):
            break
        current = pending[cursor]
        for a, b in generators:
            neighbor = conjugate(current, a, b)
            if neighbor not in reached:
                reached.add(neighbor)
                pending.append(neighbor)
                require(len(reached) <= group_order, "orbit exceeds local group")
    require(len(pending) == len(reached), "orbit worklist mismatch")
    require(all(conjugate(x, a, b) in reached for x in reached for a, b in generators),
            "incomplete orbit")
    return reached


def group_size(widths):
    answer = 1
    for d in widths:
        for j in range(d):
            answer *= (1 << d) - (1 << j)
    return answer


def enumerate_fits(widths):
    _, positions, _, word = layout(widths)
    histogram = [0] * (N + 1)
    optima = set()
    for index in range(1 << len(positions)):
        if index:
            changed = (index & -index).bit_length() - 1
            word ^= 1 << positions[changed]
        r = rank(word)
        histogram[r] += 1
        if r == 4:
            optima.add(word)
    require(sum(histogram) == 1 << len(positions), "enumeration count mismatch")
    require(not any(histogram[:4]), "rank below cited lower bound")
    require(bool(optima), "no rank-four attainer")
    return histogram, optima


def edge_forms(widths):
    _, _, _, identity = layout(widths)
    offsets = [sum(widths[:i]) for i in range(5)]
    forms = {}
    for shared in product(range(4), repeat=5):
        if sum(shared) != 3:
            continue
        private = tuple(widths[i] - shared[i - 1] - shared[i] for i in range(5))
        if min(private) < 0:
            continue
        word = identity
        for i in range(5):
            j = (i + 1) % 5
            for k in range(shared[i]):
                a = offsets[i] + shared[i - 1] + k
                b = offsets[j] + k
                word |= (1 << (N * a + b)) | (1 << (N * b + a))
        require(rank(word) == 4, "edge form has wrong rank")
        forms[word] = {"shared": list(shared), "private": list(private)}
    return forms


def profile_census(widths):
    _, positions, generators, identity = layout(widths)
    histogram, optima = enumerate_fits(widths)
    order = group_size(widths)
    channel_forms = edge_forms(widths)
    unseen = set(optima)
    records = []
    for _ in range(len(optima)):
        if not unseen:
            break
        members = orbit(min(unseen), generators, order)
        require(members <= unseen, "orbit crosses an earlier class or leaves optima")
        representative = min(members)
        require(image_rank(representative) == 4, "independent image rank mismatch")
        require(all(conjugate(representative, a, b) ==
                    dense_conjugate(representative, a, b) for a, b in generators),
                "independent conjugation mismatch")
        forms = [value for key, value in channel_forms.items() if key in members]
        require(len(forms) <= 1, "distinct channel multiplicities in one orbit")
        records.append({
            "representative_rows": [(representative >> (N * i)) & MASK for i in range(N)],
            "orbit_size": len(members), "stabilizer_size": order // len(members),
            "edge_private_form": forms[0] if forms else None,
        })
        unseen.difference_update(members)
    require(not unseen, "unclassified optima")
    require(sum(record["orbit_size"] for record in records) == len(optima),
            "orbit sizes do not partition optima")
    for word in optima:
        require(image_rank(word) == 4, "independent optimum-rank disagreement")
    sizes = Counter(record["orbit_size"] for record in records)
    return {
        "widths": list(widths), "free_entries": len(positions),
        "matrix_count": 1 << len(positions), "rank_histogram": histogram,
        "minimum_rank": 4, "optimal_matrices": len(optima), "local_group_order": order,
        "orbit_count": len(records),
        "orbit_size_histogram": {str(key): value for key, value in sorted(sizes.items())},
        "edge_private_orbits": sum(x["edge_private_form"] is not None for x in records),
        "orbits": records,
    }


def run_census():
    return {"field": "F2", "equivalence": "block-diagonal similarity; labeled vertices",
            "profiles": [profile_census(widths) for widths in PROFILES]}
