#!/usr/bin/env python3
"""Independent replay: full GL(3,F2) enumeration and uv^T idempotents."""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

from algebra import (  # noqa: E402
    GROUP_ORDER,
    IDENTITY,
    X,
    Y,
    all_gl3_matrices,
    build_group,
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
    return sorted(set(out))


def main() -> int:
    gl3 = all_gl3_matrices()
    need(len(gl3) == GROUP_ORDER, "GL(3,F2) order")
    gl3_set = set(gl3)
    need(X in gl3_set and Y in gl3_set and IDENTITY in gl3_set, "generators in GL3")
    for a in gl3:
        for b in gl3:
            need(compose(a, b) in gl3_set, "GL3 closed")

    xy = compose(X, Y)
    yx = compose(Y, X)
    need(xy in gl3_set and yx in gl3_set, "7-cycles in GL3")
    need(xy != yx, "distinct conjugates")

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

    elements, index, table = build_group()
    need(set(elements) == gl3_set, "generated group equals full GL(3,F2)")
    for roles in (2, 3, 4, 5):
        got = direct_word(roles, index[X], index[Y], index[IDENTITY], table)
        want = target_state(roles, index[xy], index[yx], index[IDENTITY])
        need(got == want, f"independent direct word r={roles}")

    print(
        "PASS_INDEPENDENT_PSL27_CONJUGATE_ANY_REGISTERS "
        "gl3_order=168 "
        "support_patterns=['xyx','yxy'] "
        "forced_B_outside_rank_one "
        "direct_roles=[2, 3, 4, 5] "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
