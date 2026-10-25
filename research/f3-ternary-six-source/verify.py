#!/usr/bin/env python3
"""Verify the exact six-source optimum for full ternary demand over F3.

Interface (unchanged from #4225/#4238): immutable sources x_0..x_{n-1}, one
arbitrarily dirty connector z, outputs y_v for every nonzero v in F3^n, and only
the unsigned complete calls B_j: z += B_j x_j and A_v: y_v += A_v z.

Checks, standard library only, no files written:
  1. the source pin of the interface README;
  2. the 24-event witness path covers every nonzero row of F3^6 by triple sums;
  3. the literal 2208-call word by a generic coefficient ledger and by dense
     random F3 execution with dirty registers;
  4. the source-deletion lemma on the literal word (all six projections are
     valid five-source words with the predicted extra counts);
  5. the extra-triple lower-bound table from the averaging recurrence and the
     counting bound, starting from #4238's cited five-source value e(5) = 1;
  6. rejection controls.
"""

from __future__ import annotations

import hashlib
import itertools
import math
import random
from pathlib import Path

N = 6
Q = 3
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/universal-connector-boundary/README.md"
SOURCE_SHA256 = "23415f7829ab8d80a783142f10f7d31abbce84579362769984680af3df954476"

# Restored 24-event source path: sources 0 and 1 occur six times, 2..5 three times.
PATH = (5, 4, 0, 1, 0, 3, 2, 4, 3, 1, 0, 1, 4, 5, 0, 1, 0, 2, 5, 3, 2, 1, 0, 1)
EXPECTED_CALLS = 2208
FLOOR = 3 * N + 3 * (Q**N - 1)
# Cited from #4238 (head 191a905d7adba6695b079f744140a73e832787a8): the canonical
# five-source census shows the 741-call floor fails, and 744 is attained.
E5_CITED = 1


def fail(message: str) -> None:
    raise SystemExit("FAIL: " + message)


def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def add(u: tuple[int, ...], v: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((a + b) % Q for a, b in zip(u, v))


def boundaries(path: tuple[int, ...], n: int) -> list[tuple[int, ...]]:
    """Prefix count vectors q_0..q_{L-1} modulo three (q_L = q_0 = 0)."""
    q = [0] * n
    out = [tuple(q)]
    for j in path[:-1]:
        q[j] = (q[j] + 1) % Q
        out.append(tuple(q))
    return out


def triple_readouts(path: tuple[int, ...], n: int) -> dict[tuple[int, ...], tuple[int, int, int]]:
    """Lexicographically first boundary triple a <= b <= c for each covered row."""
    qs = boundaries(path, n)
    first: dict[tuple[int, ...], tuple[int, int, int]] = {}
    for a, b, c in itertools.combinations_with_replacement(range(len(qs)), 3):
        first.setdefault(add(add(qs[a], qs[b]), qs[c]), (a, b, c))
    return first


def nonzero_rows(n: int) -> list[tuple[int, ...]]:
    return [v for v in itertools.product(range(Q), repeat=n) if any(v)]


def build_word(path: tuple[int, ...], n: int) -> list[tuple[str, object]]:
    """Interleave source calls and three readouts per row into one literal word."""
    first = triple_readouts(path, n)
    at: dict[int, list[tuple[int, ...]]] = {}
    for v in nonzero_rows(n):
        if v not in first:
            fail(f"row {v} is not a triple sum")
        for t in first[v]:
            at.setdefault(t, []).append(v)
    word: list[tuple[str, object]] = []
    for t, j in enumerate(path):
        word.extend(("A", v) for v in at.get(t, []))
        word.append(("B", j))
    return word


def ledger(word: list[tuple[str, object]], n: int) -> dict[tuple[int, ...], tuple[int, ...]]:
    """Generic coefficients: y_v = c_z A_v z0 + sum_j c_j A_v B_j x_j (+ y_v0)."""
    z = [1] + [0] * n  # coefficient of z0, then of each B_j x_j
    y: dict[tuple[int, ...], list[int]] = {}
    for kind, arg in word:
        if kind == "B":
            z[1 + arg] = (z[1 + arg] + 1) % Q
        else:
            acc = y.setdefault(arg, [0] * (n + 1))
            for k in range(n + 1):
                acc[k] = (acc[k] + z[k]) % Q
    check(z == [1] + [0] * n, "connector is not restored")
    return {v: tuple(c) for v, c in y.items()}


def word_valid(word: list[tuple[str, object]], n: int) -> bool:
    try:
        coeff = ledger(word, n)
    except SystemExit:
        return False
    rows = nonzero_rows(n)
    return set(coeff) == set(rows) and all(coeff[v] == (0,) + v for v in rows)


def counts(word: list[tuple[str, object]]) -> tuple[dict[object, int], dict[object, int]]:
    b: dict[object, int] = {}
    a: dict[object, int] = {}
    for kind, arg in word:
        target = b if kind == "B" else a
        target[arg] = target.get(arg, 0) + 1
    return b, a


def extra_triples(word: list[tuple[str, object]], n: int) -> int:
    b, a = counts(word)
    total = sum(b.values()) + sum(a.values())
    floor = 3 * n + 3 * (Q**n - 1)
    check((total - floor) % 3 == 0, "extra calls are not whole triples")
    return (total - floor) // 3


def matmul(m: list[list[int]], x: list[int]) -> list[int]:
    return [sum(r * c for r, c in zip(row, x)) % Q for row in m]


def dense_run(word: list[tuple[str, object]], n: int, dim: int, rng: random.Random) -> bool:
    def rmat() -> list[list[int]]:
        return [[rng.randrange(Q) for _ in range(dim)] for _ in range(dim)]

    def rvec() -> list[int]:
        return [rng.randrange(Q) for _ in range(dim)]

    bmaps = [rmat() for _ in range(n)]
    amaps = {v: rmat() for v in nonzero_rows(n)}
    xs = [rvec() for _ in range(n)]
    z0 = rvec()
    y0 = {v: rvec() for v in amaps}
    z = list(z0)
    y = {v: list(w) for v, w in y0.items()}
    for kind, arg in word:
        if kind == "B":
            z = [(p + r) % Q for p, r in zip(z, matmul(bmaps[arg], xs[arg]))]
        else:
            y[arg] = [(p + r) % Q for p, r in zip(y[arg], matmul(amaps[arg], z))]
    if z != z0:
        return False
    for v, a in amaps.items():
        want = list(y0[v])
        for j in range(n):
            if v[j]:
                term = matmul(a, matmul(bmaps[j], xs[j]))
                want = [(p + v[j] * r) % Q for p, r in zip(want, term)]
        if y[v] != want:
            return False
    return True


def delete_source(word: list[tuple[str, object]], j: int) -> list[tuple[str, object]]:
    """Remove B_j and every A_v with v_j != 0; relabel the remaining coordinates."""
    out: list[tuple[str, object]] = []
    for kind, arg in word:
        if kind == "B":
            if arg != j:
                out.append(("B", arg - (arg > j)))
        elif arg[j] == 0:
            out.append(("A", arg[:j] + arg[j + 1 :]))
    return out


def counting_bound(n: int) -> int:
    """Least extra triples forced by the number of distinct nonzero triple sums."""
    rows = Q**n - 1
    best = None
    for s in range(0, 10**6):
        length = 3 * n + 3 * s
        cap = math.comb(length + 2, 3) - length
        value = s + max(0, rows - cap)
        best = value if best is None else min(best, value)
        if s >= best:
            return best
    fail("counting bound did not terminate")
    return -1


def lower_bound_table(n_max: int) -> dict[int, tuple[int, int, int]]:
    """n -> (recurrence bound, counting bound, combined), from e(5) = 1."""
    table = {5: (E5_CITED, counting_bound(5), max(E5_CITED, counting_bound(5)))}
    for n in range(6, n_max + 1):
        rec = -(-n * table[n - 1][2] // (n - 1))
        cnt = counting_bound(n)
        table[n] = (rec, cnt, max(rec, cnt))
    return table


def main() -> None:
    check(hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256, "interface source pin")

    # 2. witness coverage
    check(len(PATH) == 24, "path length")
    check([PATH.count(j) for j in range(N)] == [6, 6, 3, 3, 3, 3], "source counts")
    rows = nonzero_rows(N)
    first = triple_readouts(PATH, N)
    covered = sum(1 for v in rows if v in first)
    check(covered == 728 == len(rows), f"coverage {covered}")

    # 3. literal word
    word = build_word(PATH, N)
    b, a = counts(word)
    check(len(word) == EXPECTED_CALLS, f"word length {len(word)}")
    check(all(c % 3 == 0 and c >= 3 for c in b.values()), "source counts")
    check(all(c == 3 for c in a.values()) and len(a) == 728, "readout counts")
    check(word_valid(word, N), "generic ledger")
    check(extra_triples(word, N) == 2, "extra triples of witness")
    rng = random.Random(20261020)
    for dim in (2, 3):
        check(dense_run(word, N, dim, rng), f"dense F3 execution at dimension {dim}")

    # 4. deletion lemma on the literal word
    projected_extras = []
    for j in range(N):
        sub = delete_source(word, j)
        check(word_valid(sub, N - 1), f"projection deleting source {j}")
        check(dense_run(sub, N - 1, 2, rng), f"dense projection deleting source {j}")
        projected_extras.append(extra_triples(sub, N - 1))
    # Sources 0, 1 carry one extra triple each; deleting one keeps the other.
    check(projected_extras == [1, 1, 2, 2, 2, 2], f"projected extras {projected_extras}")
    check(sum(projected_extras) <= (N - 1) * extra_triples(word, N), "averaging inequality")
    check(min(projected_extras) >= E5_CITED, "five-source projections respect e(5)")

    # 5. lower-bound table
    table = lower_bound_table(12)
    check(table[6][2] == 2, "e(6) lower bound")
    check(table[7][2] == 3 and table[8][2] == 4, "e(7), e(8) lower bounds")
    check(FLOOR + 3 * table[6][2] == EXPECTED_CALLS, "optimum equals bound")
    print("n  recurrence  counting  combined  lower_bound_calls")
    for n, (rec, cnt, comb) in table.items():
        floor = 3 * n + 3 * (Q**n - 1)
        print(f"{n:<2} {rec:>10} {cnt:>9} {comb:>9} {floor + 3 * comb:>18}")

    # 6. rejection controls
    controls = 0
    broken = list(word)
    del broken[next(i for i, w in enumerate(broken) if w[0] == "A")]
    check(not word_valid(broken, N), "dropped readout accepted")
    controls += 1
    broken = [w for w in word if w != ("B", 2)] + [("B", 2)] * 2
    check(not word_valid(broken, N), "two-call source accepted")
    controls += 1
    broken = list(word)
    i = next(k for k, w in enumerate(broken) if w[0] == "A")
    v = broken[i][1]
    broken[i] = ("A", tuple((c + 1) % Q for c in v) if v != (2,) * N else (1,) * N)
    check(not word_valid(broken, N), "misrouted readout accepted")
    controls += 1
    first_n5_path = (0, 1, 0, 2, 1, 0, 3, 2, 1, 4, 3, 2, 4, 3, 4)  # #4238 gap path
    check(len(triple_readouts(first_n5_path, 5)) - 1 == 241, "#4238 gap-path control")
    controls += 1
    swapped = list(PATH)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    check(len([v for v in rows if v in triple_readouts(tuple(swapped), N)]) < 728, "swap control")
    controls += 1

    print(f"controls={controls} projected_extras={projected_extras}")
    print(f"PASS_F3_TERNARY_SIX_SOURCE calls={len(word)} floor={FLOOR} rows={len(rows)}")


if __name__ == "__main__":
    main()
