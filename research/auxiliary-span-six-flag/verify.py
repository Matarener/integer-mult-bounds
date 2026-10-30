#!/usr/bin/env python3
"""Flag census for four-register rank-one idempotents, with sharpness controls.

The written rank bound is in README.md. This program recomputes the finite
classification that bound uses, and it checks the positive and failure controls
named there. It does not replay Lemma 1 of the dirty-auxiliary note.
"""

from __future__ import annotations

from itertools import combinations, permutations
import json

N = 4
EDGE_ORDER = tuple((i, j) for i in range(N) for j in range(N) if i != j)
NORMAL_ROWS = (
    "1100/0000/0000/0000",
    "0100/0100/0000/0000",
    "0000/1010/1010/0000",
)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def rows_to_mat(text):
    rows = text.split("/")
    require(len(rows) == N and all(len(row) == N for row in rows), "bad matrix text")
    mat = 0
    for i, row in enumerate(rows):
        for j, bit in enumerate(row):
            if bit == "1":
                mat |= 1 << (i * N + j)
    return mat


def show(mat):
    return "/".join(
        "".join("1" if (mat >> (i * N + j)) & 1 else "0" for j in range(N))
        for i in range(N)
    )


def matmul(left, right):
    out = 0
    for i in range(N):
        row = (left >> (i * N)) & 15
        acc = 0
        k = 0
        while row:
            if row & 1:
                acc ^= (right >> (k * N)) & 15
            row >>= 1
            k += 1
        out |= acc << (i * N)
    return out


def matvec(mat, vector):
    out = 0
    for i in range(N):
        row = (mat >> (i * N)) & 15
        bit = (row & vector).bit_count() & 1
        out |= bit << i
    return out


def invert(mat):
    rows = [((mat >> (i * N)) & 15) | (1 << (N + i)) for i in range(N)]
    for col in range(N):
        pivot = next((r for r in range(col, N) if (rows[r] >> col) & 1), None)
        require(pivot is not None, "singular matrix in a generator or flag basis")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for r in range(N):
            if r != col and (rows[r] >> col) & 1:
                rows[r] ^= rows[col]
    out = 0
    for i in range(N):
        out |= (rows[i] >> N) << (i * N)
    return out


def rank(mat):
    rows = [(mat >> (i * N)) & 15 for i in range(N)]
    found = 0
    for col in range(N):
        pivot = next((r for r in range(found, N) if (rows[r] >> col) & 1), None)
        if pivot is None:
            continue
        rows[found], rows[pivot] = rows[pivot], rows[found]
        for r in range(N):
            if r != found and (rows[r] >> col) & 1:
                rows[r] ^= rows[found]
        found += 1
    return found


def diagonal_ones(mat):
    return sum((mat >> (i * N + i)) & 1 for i in range(N))


def off_pattern(mat):
    bits = 0
    for bit, (i, j) in enumerate(EDGE_ORDER):
        if (mat >> (i * N + j)) & 1:
            bits |= 1 << bit
    return bits


def is_acyclic(patterns):
    adjacency = [set() for _ in range(N)]
    for pattern in patterns:
        for bit, (i, j) in enumerate(EDGE_ORDER):
            if (pattern >> bit) & 1:
                adjacency[i].add(j)
    indegree = [0] * N
    for i in range(N):
        for j in adjacency[i]:
            indegree[j] += 1
    queue = [i for i, degree in enumerate(indegree) if degree == 0]
    seen = 0
    while queue:
        i = queue.pop()
        seen += 1
        for j in adjacency[i]:
            indegree[j] -= 1
            if indegree[j] == 0:
                queue.append(j)
    return seen == N


def span_mask(basis):
    mask = 1
    for vector in basis:
        addition = 0
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            addition |= 1 << ((bit.bit_length() - 1) ^ vector)
        mask |= addition
    return mask


def preserves(mat, mask):
    remaining = mask
    while remaining:
        bit = remaining & -remaining
        remaining ^= bit
        image = matvec(mat, bit.bit_length() - 1)
        if ((mask >> image) & 1) == 0:
            return False
    return True


def permutation_triangular(mats):
    for order in permutations(range(N)):
        position = [0] * N
        for place, index in enumerate(order):
            position[index] = place
        if all(
            not ((mat >> (i * N + j)) & 1)
            for mat in mats
            for i in range(N)
            for j in range(N)
            if position[i] > position[j]
        ):
            return True
    return False


def outer_projectors():
    found = set()
    for left in range(1, 1 << N):
        for right in range(1, 1 << N):
            if (left & right).bit_count() % 2 == 0:
                continue
            mat = 0
            for i in range(N):
                if (left >> i) & 1 == 0:
                    continue
                for j in range(N):
                    if (right >> j) & 1:
                        mat |= 1 << (i * N + j)
            found.add(mat)
    return found


def brute_projectors():
    found = set()
    for mat in range(1 << (N * N)):
        if matmul(mat, mat) == mat and rank(mat) == 1:
            found.add(mat)
    return found


def subspaces():
    lines = [span_mask([vector]) for vector in range(1, 16)]
    planes = []
    seen = set()
    for first, second in combinations(range(1, 16), 2):
        mask = span_mask([first, second])
        if mask.bit_count() == 4 and mask not in seen:
            seen.add(mask)
            planes.append(mask)
    hyperplanes = []
    seen = set()
    for triple in combinations(range(1, 16), 3):
        mask = span_mask(triple)
        if mask.bit_count() == 8 and mask not in seen:
            seen.add(mask)
            hyperplanes.append(mask)
    flags = [
        (line, plane, hyper)
        for line in lines
        for plane in planes
        if (line & plane) == line
        for hyper in hyperplanes
        if (plane & hyper) == plane
    ]
    line_planes = [
        (line, plane) for line in lines for plane in planes if (line & plane) == line
    ]
    return lines, planes, hyperplanes, flags, line_planes


def flag_bitmasks(projectors, flags):
    masks = []
    for mat in projectors:
        bits = 0
        for index, (line, plane, hyper) in enumerate(flags):
            if preserves(mat, line) and preserves(mat, plane) and preserves(mat, hyper):
                bits |= 1 << index
        masks.append(bits)
    return masks


def generators():
    generated = []
    for order in permutations(range(N)):
        mat = 0
        for column, row in enumerate(order):
            mat |= 1 << (row * N + column)
        generated.append(mat)
    identity = sum(1 << (i * N + i) for i in range(N))
    for i in range(N):
        for j in range(N):
            if i != j:
                generated.append(identity | (1 << (i * N + j)))
    return generated


def group_order(gens):
    identity = sum(1 << (i * N + i) for i in range(N))
    seen = {identity}
    queue = [identity]
    while queue:
        current = queue.pop()
        for gen in gens:
            nxt = matmul(current, gen)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return len(seen)


def contained(mask, vector):
    return ((mask >> vector) & 1) == 1


def adapted_bases(flags):
    bases = []
    for line, plane, hyper in flags:
        v1 = next(v for v in range(1, 16) if contained(line, v))
        v2 = next(v for v in range(1, 16) if contained(plane, v) and not contained(line, v))
        v3 = next(v for v in range(1, 16) if contained(hyper, v) and not contained(plane, v))
        v4 = next(v for v in range(1, 16) if not contained(hyper, v))
        change = 0
        for column, vector in enumerate((v1, v2, v3, v4)):
            for row in range(N):
                if (vector >> row) & 1:
                    change |= 1 << (row * N + column)
        bases.append((change, invert(change)))
    return bases


def classify():
    by_outer = outer_projectors()
    by_brute = brute_projectors()
    require(by_outer == by_brute, "outer-product and brute-force projector lists differ")
    projectors = tuple(sorted(by_outer))
    for mat in projectors:
        require(diagonal_ones(mat) in (1, 3), "projector diagonal count is not 1 or 3: " + show(mat))
        require(diagonal_ones(mat) % 2 == 1, "projector trace is even")

    pools = {}
    for mat in projectors:
        pools.setdefault(off_pattern(mat), []).append(mat)
    nonzero = sorted(pattern for pattern in pools if pattern)
    cyclic = [pattern for pattern in nonzero if not is_acyclic([pattern])]
    acyclic = [pattern for pattern in nonzero if is_acyclic([pattern])]

    lines, planes, hypers, flags, line_planes = subspaces()
    require(len(lines) == 15 and len(planes) == 35 and len(hypers) == 15, "subspace census drifted")
    require(len(flags) == 315, "complete-flag count drifted: " + str(len(flags)))
    masks = flag_bitmasks(projectors, flags)
    index = {mat: i for i, mat in enumerate(projectors)}

    line_plane_masks = []
    for mat in projectors:
        bits = 0
        for number, (line, plane) in enumerate(line_planes):
            if preserves(mat, line) and preserves(mat, plane):
                bits |= 1 << number
        line_plane_masks.append(bits)

    spans = {}
    for first, second in combinations(nonzero, 2):
        third = first ^ second
        if third in (0, first, second):
            continue
        spans.setdefault(tuple(sorted((first, second, third))), None)

    flagged = []
    flagless = []
    line_plane_flagless = []
    full_planes = []
    for key in spans:
        realized = [pattern for pattern in key if pattern in pools]
        mats = [mat for pattern in realized for mat in pools[pattern]]
        bits = masks[index[mats[0]]]
        weak = line_plane_masks[index[mats[0]]]
        for mat in mats[1:]:
            bits &= masks[index[mat]]
            weak &= line_plane_masks[index[mat]]
        record = (key, tuple(mats), realized)
        if bits:
            flagged.append(record)
        else:
            flagless.append(record)
        if weak == 0:
            line_plane_flagless.append(frozenset(mats))
        if len(realized) == 3:
            full_planes.append(record)

    bases = adapted_bases(flags)
    pivot_checks = 0
    for mat, bits in zip(projectors, masks):
        require(bits != 0, "rank-one idempotent preserves no complete flag: " + show(mat))
        remaining = bits
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            change, change_inv = bases[bit.bit_length() - 1]
            conjugated = matmul(matmul(change_inv, mat), change)
            below = any(
                (conjugated >> (i * N + j)) & 1 for i in range(N) for j in range(i)
            )
            require(not below and diagonal_ones(conjugated) == 1,
                    "flag basis is not a one-pivot triangular form: " + show(mat))
            pivot_checks += 1

    gens = generators()
    identity = sum(1 << (i * N + i) for i in range(N))
    for gen in gens:
        require(matmul(gen, invert(gen)) == identity, "generator is not invertible")
    require(group_order(gens) == 20160, "permutation and transvection generators do not give GL(4,2)")
    conj = {}
    for mat in projectors:
        for number, gen in enumerate(gens):
            image = matmul(matmul(invert(gen), mat), gen)
            require(image in index, "conjugation left the rank-one idempotents")
            conj[mat, number] = image

    def weight_key(mats):
        return (sum(mat.bit_count() for mat in mats), tuple(sorted(mats)))

    normal = min((mats for _, mats, _ in flagless), key=weight_key)
    start = frozenset(normal)
    orbit = {start}
    queue = [start]
    exceptions = {frozenset(mats) for _, mats, _ in flagless}
    hit = set()
    while queue:
        current = queue.pop()
        if current in exceptions:
            hit.add(current)
        for number in range(len(gens)):
            image = frozenset(conj[mat, number] for mat in current)
            if image not in orbit:
                orbit.add(image)
                queue.append(image)

    return {
        "projectors": projectors,
        "pools": pools,
        "masks": masks,
        "index": index,
        "nonzero": nonzero,
        "cyclic": cyclic,
        "acyclic": acyclic,
        "flagged": flagged,
        "flagless": flagless,
        "line_plane_flagless": line_plane_flagless,
        "full_planes": full_planes,
        "normal": normal,
        "orbit": len(orbit),
        "hit": len(hit),
        "pivot_checks": pivot_checks,
        "flags": len(flags),
    }


def assignment_successes(calls):
    successes = 0
    total = 1
    for _ in range(calls):
        total *= N
    for code in range(total):
        hits = [0, 0, 0, 0]
        for _ in range(calls):
            hits[code % N] += 1
            code //= N
        if hits[0] >= 3 and hits[1] >= 3 and hits[2] >= 3:
            successes += 1
    return successes


def controls(data):
    pools = data["pools"]
    index = data["index"]
    masks = data["masks"]
    require(len(data["projectors"]) == 120, "projector count")
    require(len(pools) == 105, "pattern count including zero")
    require(len(data["nonzero"]) == 104, "nonzero pattern count")
    require(len(data["acyclic"]) + 1 == 93, "acyclic pattern count including zero")
    require(len(data["cyclic"]) == 12, "cyclic pattern count")
    require(sorted(len(pools[p]) for p in data["nonzero"]) == [1] * 92 + [2] * 12,
            "nonzero fiber histogram drifted")
    require(len(pools[0]) == 4, "zero pattern is not the four coordinate projectors")
    require(all(len(pools[p]) == 1 for p in data["cyclic"]), "cyclic pattern has several lifts")
    require(
        {mat for p in data["cyclic"] for mat in pools[p]}
        == {mat for mat in data["projectors"] if diagonal_ones(mat) == 3},
        "cyclic projectors are not exactly the three-diagonal idempotents",
    )
    require(len(data["flagged"]) + len(data["flagless"]) == 4964, "two-dimensional span count")
    require(len(data["flagged"]) == 4892 and len(data["flagless"]) == 72, "flag split drifted")
    require(len(data["full_planes"]) == 196, "full-plane count drifted")
    topological = [record for record in data["full_planes"] if is_acyclic(record[0])]
    cyclic_union = [record for record in data["full_planes"] if not is_acyclic(record[0])]
    require(len(topological) == 176 and len(cyclic_union) == 20, "full-plane acyclicity split drifted")
    require(all(permutation_triangular(record[1]) for record in topological),
            "an acyclic full plane is not permutation-triangular")
    require(all(not permutation_triangular(record[1]) for record in cyclic_union),
            "a cyclic-union full plane is permutation-triangular")
    require(all(len(realized) == 3 for _, _, realized in data["full_planes"]), "full plane marker")
    flagged_full = sum(len(realized) == 3 for _, _, realized in data["flagged"])
    require(flagged_full == 196, "a realizable full plane has no complete flag")
    require(all(len(realized) == 2 and len(mats) == 3 for _, mats, realized in data["flagless"]),
            "a flagless pool is not a partial triple")
    require({frozenset(mats) for _, mats, _ in data["flagless"]} == set(data["line_plane_flagless"]),
            "line-plane exceptions differ from complete-flag exceptions")
    for _, mats, _ in data["flagless"]:
        require(not permutation_triangular(mats), "flagless triple is permutation-triangular")
        for left, right in combinations(mats, 2):
            require(masks[index[left]] & masks[index[right]] != 0,
                    "a pair inside a flagless triple has no complete flag")
        fibers = sorted(len(pools[off_pattern(mat)]) for mat in mats)
        require(fibers == [1, 2, 2], "flagless triple does not have fibers 1 and 2")

    perm_flagged = sum(permutation_triangular(mats) for _, mats, _ in data["flagged"])
    require(perm_flagged == 1748, "permutation-triangular flagged span count drifted: " + str(perm_flagged))
    require(data["orbit"] == 10080 and data["hit"] == 72, "GL(4,2) orbit does not cover the flagless triples")
    require(data["pivot_checks"] == 10080, "pivot-check count drifted")
    require(tuple(show(mat) for mat in data["normal"]) == NORMAL_ROWS
            or tuple(sorted(show(mat) for mat in data["normal"])) == tuple(sorted(NORMAL_ROWS)),
            "minimum-weight flagless triple changed: " + " ".join(show(mat) for mat in data["normal"]))
    normal_set = frozenset(rows_to_mat(text) for text in NORMAL_ROWS)
    require(normal_set == frozenset(data["normal"]), "normal-form encoding drifted")
    joint = masks[index[data["normal"][0]]]
    for mat in data["normal"][1:]:
        joint &= masks[index[mat]]
    require(joint == 0, "published normal form preserves a complete flag")
    tampered = data["normal"][0] ^ 1
    require(matmul(tampered, tampered) != tampered or rank(tampered) != 1,
            "flipping the normal-form corner still produced a rank-one idempotent")

    coordinates = [1 << (i * N + i) for i in range(N)]
    require(set(coordinates) <= set(data["projectors"]), "a coordinate projector is missing")
    coordinate_flags = masks[index[coordinates[0]]]
    for mat in coordinates[1:]:
        coordinate_flags &= masks[index[mat]]
    require(coordinate_flags != 0, "coordinate projectors share no complete flag")
    for pattern in data["cyclic"]:
        mat = pools[pattern][0]
        require(masks[index[mat]] & coordinate_flags == 0,
                "a cyclic projector shares a coordinate flag with all E_ii")
    for pattern in data["acyclic"]:
        require(permutation_triangular(pools[pattern] + coordinates),
                "an acyclic pattern is not permutation-triangular with the coordinates")

    require(assignment_successes(8) == 0, "eight coordinate calls can cover three rank-3 targets")
    require(assignment_successes(9) > 0, "nine coordinate calls cannot cover three rank-3 targets")
    identity = tuple(1 if i == j else 0 for i in range(3) for j in range(3))
    units = []
    for basis in range(3):
        units.append(tuple(1 if (i, j) == (basis, basis) else 0 for i in range(3) for j in range(3)))
    summed = tuple(sum(unit[k] for unit in units) for k in range(9))
    require(summed == identity, "three coordinate frames do not sum to I_3")

    summary = {
        "projectors": 120,
        "patterns_including_zero": 105,
        "nonzero_patterns": 104,
        "acyclic_patterns_including_zero": 93,
        "cyclic_patterns": 12,
        "two_dimensional_spans": 4964,
        "full_planes": 196,
        "topological_full_planes": 176,
        "cyclic_union_full_planes": 20,
        "flagged_spans": 4892,
        "flagless_spans": 72,
        "permutation_triangular_flagged_spans": 1748,
        "gl4_order": 20160,
        "normal_form_orbit": 10080,
        "pivot_checks": data["pivot_checks"],
        "coordinate_assignments_of_length_8_covering_three_targets": 0,
        "normal_form": list(NORMAL_ROWS),
    }
    return summary


def main():
    summary = controls(classify())
    print(json.dumps(summary, sort_keys=True))
    print("PASS_AUXILIARY_SPAN_SIX_FLAG")


if __name__ == "__main__":
    main()
