"""Check explicit F2 shadow matrices for the E6 and E7 root-line patterns.

A shadow on a root-line set L is an F2 matrix N indexed by L with N_tt = 1 and
N_ts = 0 whenever t != s are orthogonal; entries on non-orthogonal pairs are free
(PR #2277, SAT-2).  WITNESSES.json stores N = U V^T for E6 (rank 8) and E7
(rank 11).  This script rebuilds the line sets from E8, checks every pattern
entry, computes the exact F2 rank of N and runs mutation controls.
Standard library only.  Prepared by Nick Petalas.  Apache-2.0.
"""
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPECTED = {"E6": (36, 8), "E7": (63, 11)}


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def e8_roots_doubled():
    """All 240 E8 roots with doubled coordinates (norm 8)."""
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                r = [0] * 8
                r[i], r[j] = si, sj
                roots.append(tuple(r))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(signs)
    assert len(roots) == 240
    return roots


def canonical(v):
    """Representative of the line {v, -v}: first nonzero coordinate positive."""
    first = next(x for x in v if x != 0)
    return tuple(v) if first > 0 else tuple(-x for x in v)


def line_set(anchors):
    """Lines of E8 roots orthogonal to every anchor root."""
    return {canonical(r) for r in e8_roots_doubled() if all(dot(r, a) == 0 for a in anchors)}


def rank_f2(rows):
    """Exact rank over F2 of integer bitmask rows."""
    pivots = {}
    for row in rows:
        while row:
            top = row.bit_length() - 1
            if top not in pivots:
                pivots[top] = row
                break
            row ^= pivots[top]
    return len(pivots)


def shadow_rows(U, V):
    """Rows of N = U V^T over F2 as bitmasks."""
    n = len(U)
    return [sum(1 << s for s in range(n) if sum(a & b for a, b in zip(U[t], V[s])) & 1) for t in range(n)]


def pattern_violations(lines, rows):
    """Entries breaking N_tt = 1 or N_ts = 0 on orthogonal pairs."""
    bad = []
    n = len(lines)
    for t in range(n):
        for s in range(n):
            bit = rows[t] >> s & 1
            if t == s and bit != 1:
                bad.append((t, s))
            elif t != s and dot(lines[t], lines[s]) == 0 and bit != 0:
                bad.append((t, s))
    return bad


def check_unit(name, item):
    size, rank_cap = EXPECTED[name]
    anchors = [tuple(a) for a in item["anchors"]]
    roots = set(e8_roots_doubled())
    assert all(a in roots for a in anchors), f"{name}: anchor is not an E8 root"
    if name == "E6":
        assert abs(dot(anchors[0], anchors[1])) == 4, "E6 anchors must span an A2"
    lines = [tuple(v) for v in item["lines"]]
    assert len(set(lines)) == len(lines) == size, f"{name}: expected {size} distinct lines"
    assert {canonical(v) for v in lines} == line_set(anchors), f"{name}: stored lines are not the {name} line set"
    U, V = item["U"], item["V"]
    assert item["rank_cap"] == rank_cap and len(U) == len(V) == size
    assert all(len(row) == rank_cap and set(row) <= {0, 1} for row in U + V), f"{name}: factor shape"
    rows = shadow_rows(U, V)
    bad = pattern_violations(lines, rows)
    assert not bad, f"{name}: {len(bad)} pattern violations, first {bad[0]}"
    exact = rank_f2(rows)
    assert exact <= rank_cap, f"{name}: rank {exact} > {rank_cap}"
    orth_pairs = sum(1 for t in range(size) for s in range(t + 1, size) if dot(lines[t], lines[s]) == 0)
    free = size * (size - 1) - 2 * orth_pairs
    ones_free = sum(bin(r).count("1") for r in rows) - size
    print(f"PASS {name}: {size} lines, {orth_pairs} orthogonal pairs forced zero, "
          f"{size} unit diagonal entries, {ones_free}/{free} free entries set; exact F2 rank {exact} <= {rank_cap}")
    return lines, rows


def controls(lines, rows, name):
    """The checker must reject a diagonal zero and a nonzero orthogonal entry."""
    t = 0
    s = next(s for s in range(len(lines)) if s != t and dot(lines[t], lines[s]) == 0)
    flipped_diag = list(rows)
    flipped_diag[t] ^= 1 << t
    flipped_orth = list(rows)
    flipped_orth[t] ^= 1 << s
    assert pattern_violations(lines, flipped_diag) == [(t, t)]
    assert pattern_violations(lines, flipped_orth) == [(t, s)]
    assert rank_f2([1, 2, 3]) == 2 and rank_f2([1 << k for k in range(9)]) == 9
    print(f"PASS {name} controls: diagonal and orthogonal-entry mutations rejected; rank helper calibrated")


def nonorthogonal_cliques(lines, size):
    """Every set of `size` pairwise non-orthogonal lines, as bitmasks."""
    n = len(lines)
    adj = [sum(1 << s for s in range(n) if s != t and dot(lines[t], lines[s]) != 0) for t in range(n)]
    found = []

    def grow(members, mask, cand):
        if len(members) == size:
            found.append(mask)
            return
        while cand:
            t = cand.bit_length() - 1
            cand &= ~(1 << t)
            grow(members + [t], mask | 1 << t, cand & adj[t] & ((1 << t) - 1))

    grow([], 0, (1 << n) - 1)
    return adj, found


def e7_seven_clique_partitions(lines):
    """Exhaustive exact cover of the 63 E7 lines by pairwise non-orthogonal 7-sets."""
    adj, sevens = nonorthogonal_cliques(lines, 7)
    assert not nonorthogonal_cliques(lines, 8)[1], "an 8-set of pairwise non-orthogonal E7 lines exists"
    by_low = {}
    for c in sevens:
        by_low.setdefault((c & -c).bit_length() - 1, []).append(c)

    def cover(rem):
        if rem == 0:
            return 1
        low = (rem & -rem).bit_length() - 1
        return sum(cover(rem & ~c) for c in by_low.get(low, []) if c & rem == c)

    return len(sevens), cover((1 << len(lines)) - 1)


def main():
    data = json.loads((HERE / "WITNESSES.json").read_text())
    assert sorted(data["units"]) == ["E6", "E7"]
    for name in ("E6", "E7"):
        lines, rows = check_unit(name, data["units"][name])
        controls(lines, rows, name)
    sevens, partitions = e7_seven_clique_partitions([tuple(v) for v in data["units"]["E7"]["lines"]])
    assert (sevens, partitions) == (288, 0), (sevens, partitions)
    print(f"PASS E7 clique cover: no 8-set of pairwise non-orthogonal lines; {sevens} 7-sets; "
          f"{partitions} partitions of the 63 lines into nine 7-sets")
    print("PASS e6-e7-shadow-minrank-upper: mr2(Gamma_E6) <= 8 and mr2(Gamma_E7) <= 11")


if __name__ == "__main__":
    sys.exit(main())
