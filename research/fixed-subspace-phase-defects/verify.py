#!/usr/bin/env python3
"""Exact finite corroboration of the pointwise-fixed-subspace phase theorem.

Produced by Nick Petalas. Apache-2.0. Standard library only; writes no files.
"""
from collections import Counter
from hashlib import sha256
import json
from math import comb
from pathlib import Path


MAX_WIDTH = 5
MAX_STATES = 4096
PACKAGE_FILES = (
    "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return (x & y).bit_count() & 1


def phase(b, x):
    return (x.bit_count() + 2 * dot(b, x)) % 4


def apply(columns, x):
    result = 0
    for i, column in enumerate(columns):
        if x & (1 << i):
            result ^= column
    return result


def transpose(columns):
    n = len(columns)
    return tuple(sum(((columns[j] >> i) & 1) << j for j in range(n))
                 for i in range(n))


def compose(left, right):
    return tuple(apply(left, column) for column in right)


def transvection(n, e):
    return tuple((1 << i) ^ (e if e & (1 << i) else 0) for i in range(n))


def defect(columns, b):
    result = 0
    for i, row in enumerate(transpose(columns)):
        difference = (phase(b, row) - phase(b, 1 << i)) % 4
        require(difference in (0, 2), "orthogonal defect must be even")
        result |= (difference // 2) << i
    return result


def orthogonal_group(n):
    require(1 <= n <= MAX_WIDTH, "orthogonal enumeration capacity")
    states = [()]
    candidates = tuple(v for v in range(1 << n) if dot(v, v))
    for _ in range(n):
        states = [prefix + (v,) for prefix in states for v in candidates
                  if all(dot(v, w) == 0 for w in prefix)]
        require(len(states) <= MAX_STATES, "partial group capacity")
    require(len(states) == len(set(states)), "duplicate group element")
    return tuple(states)


def all_subspaces(n):
    require(1 <= n <= MAX_WIDTH, "subspace enumeration capacity")
    level = {(0,)}
    spaces = [(0,)]
    for _ in range(n):
        next_level = set()
        for space in level:
            for v in range(1 << n):
                if v not in space:
                    extension = tuple(sorted((*space, *(x ^ v for x in space))))
                    next_level.add(extension)
        require(len(next_level) <= MAX_STATES, "subspace level capacity")
        spaces.extend(sorted(next_level))
        level = next_level
    require(len(spaces) == len(set(spaces)), "duplicate subspace")
    return tuple(spaces)


def basis(space, n):
    generated = {0}
    result = []
    for v in space:
        if v not in generated:
            result.append(v)
            generated.update(tuple(x ^ v for x in generated))
    require(len(result) <= n and generated == set(space), "basis span mismatch")
    return tuple(result)


def phase_table(group, n, counts):
    tables = []
    for b in range(1 << n):
        values = []
        for matrix in group:
            e = defect(matrix, b)
            values.append(e)
            rows = transpose(matrix)
            for x in range(1 << n):
                actual = (phase(b, apply(rows, x)) - phase(b, x)) % 4
                require(actual == 2 * dot(e, x), "literal phase defect mismatch")
                counts["literal_phase_values"] += 1
        tables.append(tuple(values))
    return tuple(tables)


def axis_count(n, w_basis, b):
    if any(w.bit_count() != 1 for w in w_basis):
        return None
    fixed = sum(w_basis)
    free = ((1 << n) - 1) ^ fixed
    m = n - len(w_basis)
    residue = (b & free).bit_count() % 4
    return sum(comb(m, j) for j in range(m + 1) if j % 4 == residue)


def check_context(n, w_basis, b, group, indices, table, allowed, counts):
    predicted = {e for e in range(1 << n)
                 if phase(b, e) == 0 and all(dot(e, w) == 0 for w in w_basis)}
    observed = Counter(table[i] for i in allowed)
    require(set(observed) == predicted, "restricted image mismatch")
    require(len(set(observed.values())) == 1, "unequal restricted fibers")
    require(sum(observed.values()) == len(allowed), "lost group elements")
    counts["subspace_sign_contexts"] += 1
    counts["attainable_defects"] += len(predicted)
    for e in predicted:
        representative = transvection(n, e)
        require(representative in indices, "representative not orthogonal")
        require(all(apply(representative, w) == w for w in w_basis),
                "representative moves required vector")
        require(table[indices[representative]] == e, "representative defect")
        counts["attaining_representatives"] += 1
    for i in allowed:
        representative = transvection(n, table[i])
        h = compose(representative, group[i])
        require(h in indices and table[indices[h]] == 0, "factor not phase exact")
        require(all(apply(h, w) == w for w in w_basis), "factor moves W")
        require(compose(representative, h) == group[i], "factorization mismatch")
        counts["restricted_factorizations"] += 1
    closed = axis_count(n, w_basis, b)
    if closed is not None:
        require(closed == len(predicted), "literal-axis binomial count")
        counts["coordinate_axis_contexts"] += 1


def run_census():
    counts = Counter()
    for n in range(1, MAX_WIDTH + 1):
        group = orthogonal_group(n)
        spaces = all_subspaces(n)
        require(len(group) == (1, 2, 6, 48, 720)[n - 1], "group census size")
        require(len(spaces) == (2, 5, 16, 67, 374)[n - 1], "subspace census size")
        indices = {matrix: i for i, matrix in enumerate(group)}
        tables = phase_table(group, n, counts)
        counts["orthogonal_matrices"] += len(group)
        counts["subspaces"] += len(spaces)
        for space in spaces:
            w_basis = basis(space, n)
            allowed = tuple(i for i, matrix in enumerate(group)
                            if all(apply(matrix, w) == w for w in w_basis))
            require(allowed, "identity missing from pointwise stabilizer")
            for b in range(1 << n):
                check_context(n, w_basis, b, group, indices, tables[b], allowed, counts)
    return dict(sorted(counts.items()))


def controls():
    n = 4
    identity = tuple(1 << i for i in range(n))
    e = 15
    t = transvection(n, e)
    require(phase(0, e) == 0 and apply(t, 1) != 1,
            "unrestricted representative must violate a fixed-axis fixture")
    require(apply(t, 3) == 3 and apply(t, 1) != 1 and apply(t, 2) != 2,
            "fixing a sum is weaker than fixing its summands")
    require(phase(0, 3) == 2, "even weight alone is insufficient")
    require(phase(1, 3) == 0 and defect(transvection(n, 3), 1) == 3,
            "dropping the transported signs must change the fixture")
    swap = (2, 1, 4, 8)
    require(defect(swap, 1) == 3 and apply(swap, 1) != 1,
            "setwise stabilization is not pointwise stabilization")
    require(defect(identity, 15) == 0 and defect(t, 0) == 15,
            "identity and nonzero correction controls")
    try:
        orthogonal_group(6)
    except ValueError:
        pass
    else:
        raise ValueError("group capacity must reject")
    try:
        all_subspaces(0)
    except ValueError:
        pass
    else:
        raise ValueError("subspace capacity must reject")
    return 8


def receipt():
    root = Path(__file__).resolve().parent
    hashes = {name: sha256((root / name).read_bytes()).hexdigest()
              for name in PACKAGE_FILES}
    return {"status": "PASS_FIXED_SUBSPACE_PHASE_DEFECTS",
            "evidence": run_census(), "controls": controls(), "sha256": hashes}


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True))
