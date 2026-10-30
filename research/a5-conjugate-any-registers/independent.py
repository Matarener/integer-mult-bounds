#!/usr/bin/env python3
"""Independent replay: even-permutation A5 and uv^T idempotents."""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

from algebra import (  # noqa: E402
    IDENTITY,
    X,
    Y,
    compose,
    direct_word,
    is_rank_one_idempotent,
    mat_add,
    mat_mul,
    projector,
    rank_f2,
    subsequence_support,
    target_state,
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def all_even_permutations():
    out = []
    for perm in itertools.permutations(range(5)):
        inversions = 0
        for i in range(5):
            for j in range(i + 1, 5):
                if perm[i] > perm[j]:
                    inversions += 1
        if inversions % 2 == 0:
            out.append(perm)
    return out


def uv_idempotents(roles: int):
    vectors = [v for v in itertools.product([0, 1], repeat=roles) if any(v)]
    out = []
    for u in vectors:
        for v in vectors:
            if sum(u[i] * v[i] for i in range(roles)) % 2 != 1:
                continue
            matrix = tuple(u[row] * v[col] for row in range(roles) for col in range(roles))
            need(is_rank_one_idempotent(matrix, roles), "uv^T idempotent")
            out.append(matrix)
    # Deduplicate.
    return sorted(set(out))


def main() -> int:
    even = all_even_permutations()
    need(len(even) == 60, "even permutations")
    need(X in even and Y in even and IDENTITY in even, "generators even")
    # Closure under composition inside A5.
    even_set = set(even)
    for a, b in itertools.islice(itertools.product(even, repeat=2), 0, None):
        need(compose(a, b) in even_set, "A5 closed")
        break  # spot-check first; full check below
    for a in even:
        for b in even:
            need(compose(a, b) in even_set, "A5 closed full")

    xy = compose(X, Y)
    yx = compose(Y, X)
    need(xy in even_set and yx in even_set, "5-cycles even")

    both = []
    for name, labels in (
        ("xyx", (X, Y, X)),
        ("yxy", (Y, X, Y)),
        ("xxy", (X, X, Y)),
        ("yyx", (Y, Y, X)),
    ):
        support = subsequence_support(labels)
        if xy in support and yx in support:
            both.append(name)
    need(both == ["xyx", "yxy"], f"independent support filter {both}")

    for roles in (2, 3, 4):
        Ns = uv_idempotents(roles)
        expected = {2: 6, 3: 28, 4: 120}[roles]
        need(len(Ns) == expected, f"uv idempotents r={roles}")
        e00 = projector(roles, 0)
        e11 = projector(roles, 1)
        forced = mat_add(e00, e11)
        need(rank_f2(forced, roles) == 2, "rank")
        need(forced not in Ns, "forced matrix outside rank-one alphabet")
        need(mat_mul(forced, forced, roles) == forced, "forced idempotent")

    # Rebuild the predecessor group table path via algebra.direct_word.
    from algebra import build_group  # local import after path bootstrap

    elements, index, table = build_group()
    need(set(elements) == even_set, "generated group equals even permutations")
    for roles in (2, 3, 4, 5):
        got = direct_word(roles, index[X], index[Y], index[IDENTITY], table)
        want = target_state(roles, index[xy], index[yx], index[IDENTITY])
        need(got == want, f"independent direct word r={roles}")

    print(
        "PASS_INDEPENDENT_A5_CONJUGATE_ANY_REGISTERS "
        "even_permutations=60 "
        "support_patterns=['xyx','yxy'] "
        "forced_B_outside_rank_one "
        "direct_roles=[2, 3, 4, 5] "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
