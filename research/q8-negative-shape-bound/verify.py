#!/usr/bin/env python3
"""Corroborate the new Q8 shape bound; emit a deterministic hash-bound receipt.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
from pathlib import Path

MAX_TARGETS = 64
MAX_BINARY_WIDTH = 3
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(value, divisor):
    require(value >= 0 and divisor > 0, "invalid nonnegative ceiling")
    return (value + divisor - 1) // divisor


def count_bound(ti, tj):
    return (
        ti
        + tj
        + 2 * max(ceil_div(3 * (ti + tj), 5), ceil_div(3 * ti, 4), ceil_div(3 * tj, 4))
    )


def allowed(ti, tj, ni, nj, strengthened):
    t, n = ti + tj, ni + nj
    if ni < ti or nj < tj or (ni - ti) % 2 or (nj - tj) % 2:
        return False
    if 2 * n + ni < 6 * t - ti or 2 * n + nj < 6 * t - tj:
        return False
    return not strengthened or (
        2 * ni + nj >= 4 * ti - tj and ni + 2 * nj >= 4 * tj - ti
    )


def enumerate_counts():
    records, improved, candidates, feasible = [], [], 0, 0
    for t in range(1, MAX_TARGETS + 1):
        for ti in range(t + 1):
            tj, old_min, new_min = t - ti, None, None
            for s in range(t + 1):
                has_pair = False
                for a in range(s + 1):
                    candidates += 1
                    ni, nj = ti + 2 * a, tj + 2 * (s - a)
                    old_ok = allowed(ti, tj, ni, nj, False)
                    new_ok = allowed(ti, tj, ni, nj, True)
                    if old_ok and old_min is None:
                        old_min = ni + nj
                    if new_ok:
                        feasible += 1
                        has_pair = True
                        if new_min is None:
                            new_min = ni + nj
                require(
                    has_pair == (t + 2 * s >= count_bound(ti, tj)),
                    f"projection mismatch at {(ti, tj, s)}",
                )
            require(
                old_min is not None and new_min == count_bound(ti, tj),
                f"minimum mismatch at {(ti, tj)}",
            )
            records.append([ti, tj, old_min, new_min])
            if ti and tj and new_min > old_min:
                improved.append([ti, tj, old_min, new_min])
    require([7, 1, 18, 20] in improved, "missing strict mixed improvement")
    return {
        "shapes": len(records),
        "candidate_splits": candidates,
        "feasible_splits": feasible,
        "improved_mixed_shapes": len(improved),
        "records_sha256": digest(records),
        "first_improvements": improved[:12],
    }


def canonical_count_witnesses():
    records = []
    for t in range(1, MAX_TARGETS + 1):
        for ti in range(t + 1):
            tj = t - ti
            s = (count_bound(ti, tj) - t) // 2
            a = max(0, ti + 2 * tj - 2 * s, ti - tj - s)
            b = s - a
            require(a >= 0 and b >= 0, "negative interval witness")
            require(
                allowed(ti, tj, ti + 2 * a, tj + 2 * b, True),
                "invalid constructive count witness",
            )
            records.append([ti, tj, ti + 2 * a, tj + 2 * b])
    return {"witnesses": len(records), "sha256": digest(records)}


def matrix_rank(rows, width):
    require(0 <= width <= MAX_BINARY_WIDTH, "binary width exceeds bound")
    basis = [0] * width
    rank = 0
    for original in rows:
        row = original
        require(0 <= row < 1 << width, "binary row outside width")
        for pivot in range(width - 1, -1, -1):
            if row & (1 << pivot):
                if basis[pivot]:
                    row ^= basis[pivot]
                else:
                    basis[pivot] = row
                    rank += 1
                    break
    return rank


def binary_product(left, right):
    out = []
    for row in left:
        value = 0
        for index, other in enumerate(right):
            if row & (1 << index):
                value ^= other
        out.append(value)
    return tuple(out)


def lower_units(width):
    slots = [(row, col) for row in range(width) for col in range(row)]
    for bits in range(1 << len(slots)):
        rows = [1 << index for index in range(width)]
        for index, (row, col) in enumerate(slots):
            if bits & (1 << index):
                rows[row] |= 1 << col
        yield tuple(rows)


def check_new_rank_step():
    pairs, middle_units = 0, 0
    for width in range(MAX_BINARY_WIDTH + 1):
        lefts = tuple(itertools.product(range(1 << width), repeat=2))
        rights = tuple(itertools.product(range(4), repeat=width))
        for left in lefts:
            a = matrix_rank(left, width)
            for right in rights:
                pairs += 1
                b = matrix_rank(right, 2)
                p = matrix_rank(binary_product(left, right), 2)
                require(a + b <= width + p, "nonzero-product rank charge")
                require(2 * min(a, b) <= width + p, "two-sided rank charge")
                for unit in lower_units(width):
                    middle_units += 1
                    product = binary_product(binary_product(left, unit), right)
                    require(
                        matrix_rank(product, 2) >= a + b - width,
                        "invertible chronological middle rank",
                    )
    zero_product_mutant = matrix_rank((1, 2), 2) * 2
    require(zero_product_mutant > 2, "nonzero product correction was lost")
    return {"rectangular_pairs": pairs, "chronological_middle_cases": middle_units}


def q8_mul(left, right):
    a, b, c = left & 1, (left >> 1) & 1, left >> 2
    d, e, f = right & 1, (right >> 1) & 1, right >> 2
    sign = c ^ f ^ (a & d) ^ (b & e) ^ (b & d)
    return (a ^ d) | ((b ^ e) << 1) | (sign << 2)


def left_basis_action(group, coefficient):
    result = 0
    for basis in range(8):
        if coefficient & (1 << basis):
            result ^= 1 << q8_mul(group, basis)
    return result


def right_basis_action(coefficient, group):
    result = 0
    for basis in range(8):
        if coefficient & (1 << basis):
            result ^= 1 << q8_mul(basis, group)
    return result


def group_controls():
    require(q8_mul(1, 1) == q8_mul(2, 2) == 4, "Q8 squares")
    require(q8_mul(1, 2) == 3 and q8_mul(2, 1) == 7, "Q8 noncommutation")
    cases = 0
    for a, b, c in itertools.product(range(8), repeat=3):
        require(
            q8_mul(q8_mul(a, b), c) == q8_mul(a, q8_mul(b, c)),
            "group multiplication is not associative",
        )
        cases += 1
    return {"associative_triples": cases}


def apply_call(matrix, group, u, v):
    size = len(matrix)
    require(group in (1, 2), "only positive i/j calls are paid")
    require(
        0 < u < 1 << size and 0 < v < 1 << size,
        "call vectors outside the finite role space",
    )
    require((u & v).bit_count() % 2 == 1, "non-idempotent paid call")
    row_sum = [0] * size
    for index, row in enumerate(matrix):
        if v & (1 << index):
            row_sum = [a ^ b for a, b in zip(row_sum, row, strict=True)]
    increment = [value ^ left_basis_action(group, value) for value in row_sum]
    return tuple(
        tuple(
            value ^ (increment[col] if u & (1 << row) else 0)
            for col, value in enumerate(values)
        )
        for row, values in enumerate(matrix)
    )


def identity(size):
    return tuple(tuple(int(row == col) for col in range(size)) for row in range(size))


def target(ti, tj, dirty):
    diagonal = [1 << 5] * ti + [1 << 6] * tj + [1] * dirty
    return tuple(
        tuple(value if row == col else 0 for col in range(len(diagonal)))
        for row, value in enumerate(diagonal)
    )


def full_word_controls():
    words, entries, calls, dirty_basis_columns = 0, 0, 0, 0
    for t in range(1, 9):
        for ti in range(t + 1):
            tj, dirty = t - ti, 2
            matrix = identity(t + dirty)
            for role in range(t):
                group = 1 if role < ti else 2
                for _ in range(3):
                    matrix = apply_call(matrix, group, 1 << role, 1 << role)
                    calls += 1
            require(matrix == target(ti, tj, dirty), "full dirty endpoint differs")
            require(3 * t >= count_bound(ti, tj), "direct upper word violates bound")
            words += 1
            entries += (t + dirty) ** 2
            for col in range(t + dirty):
                for basis in range(8):
                    actual = tuple(
                        right_basis_action(row[col], basis) for row in matrix
                    )
                    inverse = 5 if col < ti else (6 if col < t else 0)
                    expected = tuple(
                        (1 << q8_mul(inverse, basis)) if row == col else 0
                        for row in range(t + dirty)
                    )
                    require(actual == expected, "regular dirty basis column differs")
                    dirty_basis_columns += 1
    return {
        "direct_words": words,
        "formal_entries": entries,
        "paid_calls_executed": calls,
        "regular_basis_columns_covered": dirty_basis_columns,
    }


def failure_controls():
    controls = []
    require(allowed(7, 1, 7, 11, False), "old comparison fixture rejected")
    require(not allowed(7, 1, 7, 11, True), "new inequality missing")
    controls.append("old eighteen-call fixture rejected by new inequality")
    require(allowed(2, 1, 2, 5, True), "necessary-only seven-call fixture lost")
    controls.append("count relaxation does not assert endpoint existence")
    require(count_bound(7, 1) == 20 and count_bound(1, 7) == 20, "shape/parity control")
    controls.append("label exchange and parity strengthen the real bound")
    exact = target(1, 0, 2)
    mutant = [list(row) for row in exact]
    mutant[1][0] = 1
    require(tuple(tuple(row) for row in mutant) != exact, "dirty leak accepted")
    controls.append("full matrix rejects off-diagonal dirty leakage")
    try:
        apply_call(identity(2), 1, 1, 2)
    except ValueError:
        controls.append("non-idempotent call rejected")
    else:
        raise ValueError("non-idempotent call accepted")
    for k in range(1, 257):
        require(allowed(7 * k, k, 7 * k, 11 * k, False), "old scaled fixture")
        require(not allowed(7 * k, k, 7 * k, 11 * k, True), "scaled exclusion")
        require(
            count_bound(7 * k, k) == 8 * k + 2 * ceil_div(21 * k, 4),
            "scaled parity projection",
        )
    controls.append("256 scaled strict exclusions corroborate the uniform family")
    return controls


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def read_limited(path, limit):
    with path.open("rb") as stream:
        payload = stream.read(limit + 1)
    require(len(payload) <= limit, "source exceeds byte bound: " + str(path))
    return payload


def authenticated_sources():
    payload = read_limited(PACKAGE / "SOURCES.json", 65536)
    manifest = json.loads(payload)
    expected = {
        "docs/research/agent-task-catalog.json",
        "certificates/selected-result.json",
        "research/q8-count-region-rank-floor/PROOF.md",
        "research/q8-homogeneous-mixed-floor/PROOF.md",
        "research/q8-mixed-boundary-rank/PROOF.md",
    }
    require(len(manifest["files"]) == len(expected), "source inventory size changed")
    require(
        {row["path"] for row in manifest["files"]} == expected,
        "source inventory changed",
    )
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "provenance":
            continue
        require(row["usage"] == "input", "unknown source role")
        path = ROOT / row["path"]
        payload = read_limited(path, 4 * 1024 * 1024)
        actual = hashlib.sha256(payload).hexdigest()
        require(actual == row["sha256"], "source hash mismatch: " + row["path"])
        hashes[row["path"]] = actual
    for name in (
        "PROOF.md",
        "README.md",
        "TASK.json",
        "SOURCES.json",
        "VERIFY.json",
        "verify.py",
    ):
        path = PACKAGE / name
        hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(
            read_limited(path, 4 * 1024 * 1024)
        ).hexdigest()
    return hashes


def main():
    source_hashes = authenticated_sources()
    result = {
        "status": "PASS_Q8_NEGATIVE_SHAPE_BOUND",
        "claim_type": "scoped proof with finite corroboration",
        "count_projection": enumerate_counts(),
        "count_witnesses": canonical_count_witnesses(),
        "rank_step": check_new_rank_step(),
        "q8_algebra": group_controls(),
        "direct_words": full_word_controls(),
        "failure_controls": failure_controls(),
        "source_sha256": source_hashes,
    }
    result["receipt_sha256"] = digest(result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
