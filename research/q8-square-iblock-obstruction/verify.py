#!/usr/bin/env python3
"""Corroborate the square i-block obstruction in F2[Q8].

The proof is PROOF.md. This program checks the finite consequences that a
reviewer can recompute without reading that argument as code:

- the Q8 multiplication table and the three-call identity i^3=zi, j^3=zj;
- direct diagonal words for shapes (4,1) and (7,1), including one dirty role;
- Sylvester's inequality on every binary product with dimensions at most 3;
- one non-identity unitriangular middle factor whose active image is exactly
  the seven zi coordinates;
- the dimension collision that forces a vector outside that image to raise
  the rank from 7 to 8;
- the inherited count region on the ray t_i=4 t_j, its unique 11k-split, and
  the square-block rejection of that split through k=32;
- the four 20-call splits at shape (7,1), with (7,13) rejected and the other
  three retained.

Standard library only. No network and no third-party package.
"""

import hashlib
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
RAY_LIMIT = 32


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank_rows(rows, width):
    basis = [0] * width
    found = 0
    for original in rows:
        row = original
        require(0 <= row < (1 << width), "row does not fit the declared width")
        for pivot in range(width - 1, -1, -1):
            if (row >> pivot) & 1:
                if basis[pivot]:
                    row ^= basis[pivot]
                else:
                    basis[pivot] = row
                    found += 1
                    break
    return found


def mat_rows(entries, width):
    return [sum((1 << col) for col, bit in enumerate(row) if bit) for row in entries]


def rank_matrix(entries):
    width = len(entries[0]) if entries else 0
    require(all(len(row) == width for row in entries), "ragged matrix")
    return rank_rows(mat_rows(entries, width), width)


def column_mask(entries, col):
    mask = 0
    for row, values in enumerate(entries):
        if values[col]:
            mask |= 1 << row
    return mask


def rank_columns(entries):
    if not entries:
        return 0
    height = len(entries)
    return rank_rows([column_mask(entries, col) for col in range(len(entries[0]))], height)


def product(left, right):
    """Binary product of row-oriented 0/1 matrices."""
    middle = len(right)
    require(all(len(row) == middle for row in left), "product dimensions")
    width = len(right[0]) if right else 0
    out = []
    for row in left:
        acc = [0] * width
        for index, bit in enumerate(row):
            if bit:
                for col in range(width):
                    acc[col] ^= right[index][col]
        out.append(acc)
    return out


def identity(size):
    return [[1 if row == col else 0 for col in range(size)] for row in range(size)]


def unitriangular(size, lower_bits):
    matrix = identity(size)
    for row, col in lower_bits:
        require(row > col, "unitriangular entries are strictly lower")
        matrix[row][col] ^= 1
    return matrix


def least_admissible(floor, modulus):
    """Least integer >= floor and congruent to modulus modulo 2."""
    if floor % 2 != modulus % 2:
        floor += 1
    return floor


def square_minimum(major, minor):
    """Least legal call count on the minor label when the major block is square."""
    return max(minor, least_admissible(2 * major, minor))


def cubic_ok(ti, tj, ni, nj):
    total_targets = ti + tj
    total_calls = ni + nj
    if ni < ti or nj < tj or (ni - ti) % 2 or (nj - tj) % 2:
        return False
    if 2 * total_calls + ni < 6 * total_targets - ti:
        return False
    if 2 * total_calls + nj < 6 * total_targets - tj:
        return False
    return True


def quadratic_ok(ti, tj, ni, nj):
    return 2 * ni + nj >= 4 * ti - tj and ni + 2 * nj >= 4 * tj - ti


def square_ok(ti, tj, ni, nj):
    if ni == ti and nj < square_minimum(ti, tj):
        return False
    if nj == tj and ni < square_minimum(tj, ti):
        return False
    return True


def splits(ti, tj, calls, predicate):
    found = []
    for ni in range(calls + 1):
        nj = calls - ni
        if predicate(ti, tj, ni, nj):
            found.append((ni, nj))
    return found


def check_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    expected = {
        "research/q8-count-region-rank-floor/PROOF.md",
        "research/q8-homogeneous-mixed-floor/PROOF.md",
        "research/q8-mixed-boundary-rank/PROOF.md",
    }
    seen = set()
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        seen.add(row["path"])
        payload = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == row["sha256"], row["path"])
        text = payload.decode("utf-8")
        if row["path"].endswith("q8-mixed-boundary-rank/PROOF.md"):
            require("5n >= 11t" in text, "inherited 11t/5 bound missing")
            require("XHY=I_t" in text, "mixed tau identity missing")
        if row["path"].endswith("q8-homogeneous-mixed-floor/PROOF.md"):
            require("X_i K_i Y_i" in text, "quadratic block missing")
        if row["path"].endswith("q8-count-region-rank-floor/PROOF.md"):
            require("n_g >= t_g" in text, "block floor missing")
    require(seen == expected, "input inventory changed")
    return len(seen)


def check_sylvester():
    cases = 0
    for out, mid, inn in itertools.product(range(4), repeat=3):
        left_space = list(itertools.product(range(1 << mid), repeat=out))
        right_space = list(itertools.product(range(1 << inn), repeat=mid))
        for left_rows in left_space:
            left_rank = rank_rows(left_rows, mid)
            for right_rows in right_space:
                cases += 1
                right_rank = rank_rows(right_rows, inn)
                product_rows = []
                for left in left_rows:
                    value = 0
                    for index, right in enumerate(right_rows):
                        if (left >> index) & 1:
                            value ^= right
                    product_rows.append(value)
                product_rank = rank_rows(product_rows, inn)
                require(
                    product_rank >= left_rank + right_rank - mid,
                    "Sylvester failed",
                )
    require(cases == sum(2 ** (o * m + m * i) for o, m, i in itertools.product(range(4), repeat=3)), "case count")
    return cases


def check_square_image_fixture():
    """A non-identity invertible K keeps the image on the zi coordinates."""
    size = 7
    lower = [(1, 0), (2, 0), (2, 1), (4, 1), (5, 3), (6, 2), (6, 5)]
    factor = unitriangular(size, lower)
    require(rank_matrix(factor) == size, "fixture middle factor is singular")
    require(factor != identity(size), "fixture did not exercise a dirty-sensitive factor")
    height = 8
    columns = []
    for col in range(size):
        mask = 0
        for row in range(size):
            if factor[row][col]:
                mask |= 1 << row
        columns.append(mask)
    require(rank_rows(columns, height) == size, "active image lost rank")
    span = rank_rows(columns + [1 << 7], height)
    require(span == height, "zj coordinate was already in the square i-image")
    # The false equality rank, 7, cannot contain both target spaces.
    require(rank_rows(columns, height) < height, "collision fixture collapsed")
    return {"middle_rank": size, "image_rank": size, "with_zj_coordinate": span}


def q8_mul(left, right):
    a, b, c = left & 1, (left >> 1) & 1, left >> 2
    d, e, f = right & 1, (right >> 1) & 1, right >> 2
    sign = c ^ f ^ (a & d) ^ (b & e) ^ (b & d)
    return (a ^ d) | ((b ^ e) << 1) | (sign << 2)


def left_action(group, coefficient):
    result = 0
    for basis in range(8):
        if coefficient & (1 << basis):
            result |= 1 << q8_mul(group, basis)
    return result


def apply_call(matrix, group, role):
    require(group in (1, 2), "paid label")
    updated = [row[:] for row in matrix]
    combined = [0] * len(matrix)
    for col, value in enumerate(matrix[role]):
        combined[col] = value
    # v = u = e_role, so v^T M is that one row. (1+[g]) acts on the left.
    increment = [value ^ left_action(group, value) for value in combined]
    for col, value in enumerate(increment):
        updated[role][col] ^= value
    return updated


def algebra_identity(size):
    return [[1 if row == col else 0 for col in range(size)] for row in range(size)]


def target_diagonal(ti, tj, dirty):
    values = [1 << 5] * ti + [1 << 6] * tj + [1] * dirty
    return [[value if row == col else 0 for col in range(len(values))] for row, value in enumerate(values)]


def direct_word(ti, tj, dirty):
    size = ti + tj + dirty
    matrix = algebra_identity(size)
    calls = 0
    for role in range(ti + tj):
        group = 1 if role < ti else 2
        for _ in range(3):
            matrix = apply_call(matrix, group, role)
            calls += 1
    require(matrix == target_diagonal(ti, tj, dirty), "direct word missed the endpoint")
    require(calls == 3 * (ti + tj), "direct word length")
    return calls


def check_group_and_words():
    require(q8_mul(1, 1) == 4 and q8_mul(2, 2) == 4, "squares")
    require(q8_mul(1, 2) == 3 and q8_mul(2, 1) == 7, "ij and ji")
    require(q8_mul(4, 3) == 7, "ji = z ij")
    require(q8_mul(q8_mul(1, 1), 1) == 5, "i^3 = zi")
    require(q8_mul(q8_mul(2, 2), 2) == 6, "j^3 = zj")
    triples = 0
    for left, mid, right in itertools.product(range(8), repeat=3):
        require(q8_mul(q8_mul(left, mid), right) == q8_mul(left, q8_mul(mid, right)), "associativity")
        triples += 1
    words = {
        "(4,1)+dirty": direct_word(4, 1, 1),
        "(7,1)+dirty": direct_word(7, 1, 1),
        "(4,1)": direct_word(4, 1, 0),
    }
    try:
        apply_call(algebra_identity(1), 3, 0)
    except ValueError:
        rejected = True
    else:
        rejected = False
    require(rejected, "a label outside {i,j} was accepted")
    return {"associative_triples": triples, "direct_calls": words}


def check_ray(limit):
    excluded = []
    survivors_at_next = []
    for k in range(1, limit + 1):
        ti, tj = 4 * k, k
        bound = 11 * k
        legal = splits(ti, tj, bound, cubic_ok)
        require(legal == [(ti, 7 * k)], f"ray split changed at k={k}: {legal}")
        require(not square_ok(ti, tj, ti, 7 * k), "square lemma missed the equality split")
        require(7 * k < 2 * ti, "the numerical gap disappeared")
        # The exchanged ray is the same arithmetic with the labels swapped.
        exchanged = splits(tj, ti, bound, cubic_ok)
        require(exchanged == [(7 * k, ti)], f"exchanged ray split changed at k={k}")
        require(not square_ok(tj, ti, 7 * k, ti), "swapped square lemma missed")
        later = [
            pair for pair in splits(ti, tj, bound + 2, cubic_ok) if square_ok(ti, tj, *pair)
        ]
        require(later, f"no count split survives at 11k+2 for k={k}")
        require(all(cubic_ok(ti, tj, *pair) and square_ok(ti, tj, *pair) for pair in later), "survivor")
        excluded.append(k)
        survivors_at_next.append(later[0])
    # Shape (4,1) still has admissible count splits at 13. Do not claim 15.
    thirteen = [pair for pair in splits(4, 1, 13, cubic_ok) if square_ok(4, 1, *pair) and quadratic_ok(4, 1, *pair)]
    require(thirteen == [(4, 9), (6, 7), (8, 5), (10, 3)], thirteen)
    return {
        "k_checked": excluded[-1],
        "first_survivor_after_the_gap": survivors_at_next[0],
        "shape_4_1_at_13": thirteen,
    }


def check_seven_one():
    ti, tj = 7, 1
    require(square_minimum(ti, tj) == 15, "parity lift")
    cubic_20 = splits(ti, tj, 20, cubic_ok)
    quadratic_20 = [pair for pair in cubic_20 if quadratic_ok(ti, tj, *pair)]
    surviving = [pair for pair in quadratic_20 if square_ok(ti, tj, *pair)]
    require(quadratic_20 == [(7, 13), (9, 11), (11, 9), (13, 7)], quadratic_20)
    require(surviving == [(9, 11), (11, 9), (13, 7)], surviving)
    require(not square_ok(ti, tj, 7, 13), "(7,13) survived")
    # The older cubic region really does allow the split the quadratic forbids.
    require(cubic_ok(ti, tj, 7, 11) and not quadratic_ok(ti, tj, 7, 11), "old 18-call fixture")
    require(not square_ok(ti, tj, 7, 11), "square lemma should also reject (7,11)")
    # Homogeneous recovery: a square i-block on four zi targets needs eight j-calls.
    require(square_minimum(4, 0) == 8, "homogeneous square floor")
    require(not square_ok(4, 0, 4, 6), "homogeneous (4,6) should fail")
    # The obstruction is not a 22-call theorem at (7,1): three splits remain.
    require(len(surviving) == 3, "over-claimed the 20-call exclusion")
    return {"rejected": (7, 13), "still_open": surviving}


def main():
    result = {
        "status": "PASS_Q8_SQUARE_IBLOCK_OBSTRUCTION",
        "claim_type": "scoped obstruction; 20-call existence at (7,1) remains open",
        "pinned_inputs": check_sources(),
        "sylvester_products": check_sylvester(),
        "square_image": check_square_image_fixture(),
        "group_and_direct_words": check_group_and_words(),
        "ray": check_ray(RAY_LIMIT),
        "seven_one": check_seven_one(),
    }
    print("PASS_Q8_SQUARE_IBLOCK_OBSTRUCTION")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
