"""Exact admissible count region for mixed-negative Q8 endpoints.

Model (inherited unchanged from PR3570/PR3578/PR3589): work in the formal
group algebra F2[Q8].  Every paid factor is

    D_l = I + (1 + [g_l]) u_l v_l^T,    g_l in {i, j},    v_l^T u_l = 1,

with binary u_l, v_l, free binary scalar GL mixing, arbitrary independent
dirty input on every role, and a diagonal endpoint carrying t_i copies of
zi, t_j copies of zj and the identity elsewhere.  Write t = t_i + t_j,
n = n_i + n_j, and let X = [u_1 ... u_n], Y = [v_1^T; ...; v_n^T].

This package recomputes exactly the admissible label splits of the inherited
necessary conditions

    2n + n_i >= 6t - t_i,    2n + n_j >= 6t - t_j,
    n_i = t_i (mod 2),       n_j = t_j (mod 2),

together with the block rank floor

    rank(X_g Y_g) = rank(P_g) = t_g  =>  n_g >= t_g       (g = i, j),

and records the equality structure forced on the boundary.  It is a
necessary-condition refinement: it neither constructs a word nor excludes
one.

Standard library only.  No Git objects, no network, no third-party package.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAP = 64


def require(ok, message):
    if not ok:
        raise ValueError(message)


def splits(t_i, t_j, n, floor=True):
    """Admissible (n_i, n_j) at size n for one endpoint shape."""
    require(t_i >= 0 and t_j >= 0, "shape")
    require(t_i + t_j > 0, "empty shape")
    t = t_i + t_j
    out = []
    for n_i in range(n + 1):
        n_j = n - n_i
        if n_i % 2 != t_i % 2 or n_j % 2 != t_j % 2:
            continue
        if floor and (n_i < t_i or n_j < t_j):
            continue
        if 2 * n + n_i < 6 * t - t_i:
            continue
        if 2 * n + n_j < 6 * t - t_j:
            continue
        out.append((n_i, n_j))
    return out


def region_min(t_i, t_j, floor=True, cap=CAP):
    """Least n with a nonempty admissible region, or None above the cap."""
    for n in range(1, cap + 1):
        if splits(t_i, t_j, n, floor):
            return n
    return None


def parity_rounded(t_i, t_j):
    """PR3589's stated consequence: ceil(11t/5) rounded to the parity of t."""
    t = t_i + t_j
    n = -(-11 * t // 5)
    if n % 2 != t % 2:
        n += 1
    return n


def equality_pairs(t_i, t_j, n):
    """Admissible pairs at size n with equality in a count inequality."""
    t = t_i + t_j
    out = []
    for n_i, n_j in splits(t_i, t_j, n):
        marks = []
        if 2 * n + n_i == 6 * t - t_i:
            marks.append("i")
        if 2 * n + n_j == 6 * t - t_j:
            marks.append("j")
        if marks:
            out.append((n_i, n_j, "".join(marks)))
    return out


# ------------------------------------------------------------- linear algebra

def rank_f2(rows, columns):
    """Rank over F2 of vectors given as integer bit masks of the given width."""
    pivots = {}
    for row in rows:
        require(0 <= row < 1 << columns, "row out of range")
        cur = row
        while cur:
            high = cur.bit_length() - 1
            if high in pivots:
                cur ^= pivots[high]
            else:
                pivots[high] = cur
                break
    return len(pivots)


def fixture_2_8():
    """Explicit rank profile of the (2,8) split at t = 4, balanced shape.

    X_i is 4 x 2 with independent columns, Y_i is 2 x 4, X_i Y_i = P_i, and
    the j-block reproduces P_j with rank two on both sides.  This is rank
    data, not a word.
    """
    x_i = [0b0001, 0b0010]
    y_i = [0b0001, 0b0010]
    x_j = [0b0100, 0b1000] * 4
    y_j = [0b0100, 0b1000, 0, 0, 0, 0, 0, 0]
    return x_i, y_i, x_j, y_j


def block_rank(x_cols, y_rows, roles=4):
    """rank X_g, rank Y_g and rank X_g Y_g for one call block."""
    rx = rank_f2(x_cols, roles)
    ry = rank_f2(y_rows, roles)
    prod_rows = []
    for a in range(roles):
        acc = 0
        for l, col in enumerate(x_cols):
            if col >> a & 1:
                acc ^= y_rows[l]
        prod_rows.append(acc)
    return rx, ry, rank_f2(prod_rows, roles)


def verify():
    receipt = {"region": {}, "shapes": {}}

    # 1. Every endpoint shape through t = 12 has a nonempty region, the rank
    #    floor never weakens it, and the region minimum never beats the
    #    published parity-rounded 11t/5 statement.
    strict = []
    table = {}
    for t in range(1, 13):
        for t_i in range(t + 1):
            t_j = t - t_i
            n_floor = region_min(t_i, t_j, True)
            n_plain = region_min(t_i, t_j, False)
            require(n_floor is not None and n_plain is not None, "empty region")
            require(n_floor >= n_plain, "floor weakened the region")
            require(n_floor >= parity_rounded(t_i, t_j), "region beats PR3589")
            if n_floor > parity_rounded(t_i, t_j):
                strict.append([t_i, t_j, n_floor, parity_rounded(t_i, t_j)])
            table[f"{t_i},{t_j}"] = {
                "t": t,
                "region_min": n_floor,
                "region_min_without_floor": n_plain,
                "parity_rounded_11t_over_5": parity_rounded(t_i, t_j),
                "splits_at_region_min": [list(p) for p in splits(t_i, t_j, n_floor)],
                "equality_at_region_min": [
                    [n_i, n_j, mark] for n_i, n_j, mark in equality_pairs(t_i, t_j, n_floor)
                ],
            }
    receipt["region"]["shapes_checked"] = len(table)
    receipt["region"]["shapes_where_region_beats_parity_rounded"] = len(strict)
    receipt["region"]["strict_shapes"] = strict
    receipt["region"]["table"] = table

    # 2. The floor is not vacuous: it removes splits that the published pair
    #    plus parity admits, at the exact lengths of the open t = 4 shapes.
    effect = {}
    for t_i, t_j in ((4, 0), (0, 4), (3, 1), (1, 3), (2, 2)):
        n = region_min(t_i, t_j, True)
        require(n == region_min(t_i, t_j, False), "floor moved the t=4 minimum")
        effect[f"{t_i},{t_j}"] = {
            "n": n,
            "published_only": [list(p) for p in splits(t_i, t_j, n, False)],
            "admissible": [list(p) for p in splits(t_i, t_j, n, True)],
            "removed_by_floor": [
                list(p) for p in splits(t_i, t_j, n, False)
                if p not in splits(t_i, t_j, n, True)
            ],
        }
    require(effect["4,0"]["removed_by_floor"] == [[0, 10], [2, 8]],
            "(4,0) removal set changed")
    require(effect["3,1"]["removed_by_floor"] == [[1, 9]],
            "(3,1) removal set changed")
    require(effect["2,2"]["removed_by_floor"] == [], "(2,2) removal set changed")
    require(effect["2,2"]["admissible"] == [[2, 8], [4, 6], [6, 4], [8, 2]],
            "(2,2) ten-call splits changed")
    receipt["floor_effect_at_ten"] = effect

    # 3. Equality in a count inequality forces both block ranks to r.
    #    Complete over the integer lattice of rank data at the boundary.
    lattice_pairs = 0
    equality_hits = 0
    forced = {}
    for t_i, t_j in ((2, 1), (3, 0), (3, 1), (2, 2), (4, 0), (0, 4), (1, 1)):
        t = t_i + t_j
        n = region_min(t_i, t_j)
        rows = []
        for n_i, n_j, mark in equality_pairs(t_i, t_j, n):
            r = 3 * t - n
            for g, t_g, n_g in (("i", t_i, n_i), ("j", t_j, n_j)):
                if g not in mark:
                    continue
                require(r > 0, "equality with a vacuous cubic bound")
                require(2 * r == n_g + t_g, "count inequality is not equality")
                require(r <= min(n_g, t), "forced rank outside the allowed range")
                require(r >= t_g, "negative correction dimension")
                hits = 0
                for a in range(0, min(n_g, t) + 1):
                    for b in range(0, min(n_g, t) + 1):
                        if a < r or b < r:
                            continue
                        lattice_pairs += 1
                        if a + b == n_g + t_g:
                            require((a, b) == (r, r), "equality at a non-forced rank pair")
                            hits += 1
                require(hits == 1, "equality not forced to a single rank pair")
                # Realizable rank data must obey the count bound; the box
                # pairs that break it are the ones the bound excludes.
                violating = [
                    (a, b)
                    for a in range(r, min(n_g, t) + 1)
                    for b in range(r, min(n_g, t) + 1)
                    if a + b > n_g + t_g
                ]
                require((r, r) not in violating, "forced pair breaks the count bound")
                equality_hits += hits
                rows.append({
                    "g": g, "n_g": n_g, "t_g": t_g, "r": r,
                    "equality_iff_rank_X_g": r, "equality_iff_rank_Y_g": r,
                    "dim_imY_cap_kerX": r - t_g,
                    "x_g_injective": r == n_g,
                })
        forced[f"{t_i},{t_j}"] = rows
    receipt["equality"] = {
        "boundary_cases": sum(len(v) for v in forced.values()),
        "lattice_pairs_checked": lattice_pairs,
        "forced_equality_hits": equality_hits,
    }
    receipt["forced_boundary_ranks"] = forced

    # 4. The (2,8) ten-call profile is rank-realizable, so the floor does not
    #    already exclude it.
    x_i, y_i, x_j, y_j = fixture_2_8()
    ax, ay, ap = block_rank(x_i, y_i)
    bx, by, bp = block_rank(x_j, y_j)
    require((ax, ay, ap) == (2, 2, 2), "i-block rank profile")
    require((bx, by, bp) == (2, 2, 2), "j-block rank profile")
    receipt["fixture_2_8"] = {
        "rank_X_i": ax, "rank_Y_i": ay, "rank_X_i_Y_i": ap,
        "rank_X_j": bx, "rank_Y_j": by, "rank_X_j_Y_j": bp,
        "n_i": 2, "n_j": 8, "t_i": 2, "t_j": 2, "t": 4, "n": 10,
        "matches_forced_boundary": ax == 2 and ay == 2 and bx == 2 and by == 2,
        "is_a_word": False,
    }

    # 5. The delivered three-target minimum is nine for both shapes, while the
    #    region minimum is seven: the first shape where the region is not
    #    attained.  The value nine is PR3536's corollary, not re-derived here.
    triples = {}
    for t_i, t_j in ((3, 0), (2, 1)):
        n = region_min(t_i, t_j)
        triples[f"{t_i},{t_j}"] = {
            "region_min": n,
            "splits_at_region_min": [list(p) for p in splits(t_i, t_j, n)],
            "delivered_minimum": 9,
            "delivered_by": "PR3536 corollary on the retained PR3471 exclusion",
        }
    require(triples["3,0"]["region_min"] == 7 and triples["2,1"]["region_min"] == 7,
            "three-target region minimum changed")
    receipt["three_targets"] = triples

    return receipt


def main():
    receipt = verify()
    (ROOT / "RESULT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
    r = receipt["region"]
    print(f"endpoint shapes checked: {r['shapes_checked']}")
    print("shapes where the region beats parity-rounded 11t/5: "
          f"{r['shapes_where_region_beats_parity_rounded']}")
    for t_i, t_j in ((2, 2), (3, 1), (4, 0)):
        row = receipt["floor_effect_at_ten"][f"{t_i},{t_j}"]
        print(f"t=4 shape ({t_i},{t_j}) at n={row['n']}: admissible {row['admissible']} "
              f"removed by the rank floor {row['removed_by_floor']}")
    print(f"forced boundary rank rows: {receipt['equality']['boundary_cases']}")
    print(f"rank lattice pairs: {receipt['equality']['lattice_pairs_checked']}")
    print("PASS mixed-negative Q8 admissible count region")
    require((ROOT / "RESULT.json").stat().st_size > 0, "receipt not written")


if __name__ == "__main__":
    main()
