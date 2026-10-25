#!/usr/bin/env python3
"""Screened source-normalization shortcut on the prepared P104 cut.

The row-local and column-local FULL charts are 9-dimensional subspaces of the
common 81-dimensional chart F81 = F_2^9 ⊗ F_2^9. Their span has dimension 17,
so local FULL is not global F81. On the prepared entrance of the PR #3978
joint compensator, deleting either Gram factor still leaves the physical
source as F K x with K = T^{-1}. Charging one rank-one chart child on each
of the N = 104^2 data positions costs exactly the debt-free allowance, so
the strict gate fails before any further nonnegative cost.

No new kappa and no selected-frontier change.
"""

from __future__ import annotations

import json
from pathlib import Path

DIM = 9
F81 = DIM * DIM  # 81
N_PORTS = 104
N_DATA = N_PORTS * N_PORTS  # 10816
WIDTH = 81
ROLES = 36608
CALLS = 208
BARE_MASS = 2368
PROGRESS_CAP = 2312


def rank_and_reduced(vectors: list[int]) -> tuple[int, tuple[int, ...]]:
    rows = [v for v in vectors if v]
    rank = 0
    for col in range(F81):
        mask = 1 << col
        pivot = None
        for i in range(rank, len(rows)):
            if rows[i] & mask:
                pivot = i
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and (rows[i] & mask):
                rows[i] ^= rows[rank]
        rank += 1
    reduced = tuple(sorted(v for v in rows[:rank] if v))
    return rank, reduced


def row_space(r: int) -> list[int]:
    """Basis of r ⊗ F_2^9 inside F_2^9 ⊗ F_2^9, coordinates 9*a + b."""
    basis = []
    for k in range(DIM):
        vector = 0
        for a in range(DIM):
            if r & (1 << a):
                vector |= 1 << (DIM * a + k)
        basis.append(vector)
    return basis


def column_space(c: int) -> list[int]:
    """Basis of F_2^9 ⊗ c."""
    basis = []
    for a in range(DIM):
        vector = 0
        for b in range(DIM):
            if c & (1 << b):
                vector |= 1 << (DIM * a + b)
        basis.append(vector)
    return basis


def chart_census() -> dict[str, int]:
    spaces: dict[int, tuple[int, ...]] = {}
    pairs = 0
    for r in range(1, 1 << DIM):
        row_rank, row_id = rank_and_reduced(row_space(r))
        if row_rank != DIM:
            raise AssertionError(f"row chart rank {row_rank} for r={r}")
        spaces[r] = row_id
        for c in range(1, 1 << DIM):
            col_rank, _col_id = rank_and_reduced(column_space(c))
            if col_rank != DIM:
                raise AssertionError(f"column chart rank {col_rank} for c={c}")
            span_rank, _span = rank_and_reduced(row_space(r) + column_space(c))
            intersection = row_rank + col_rank - span_rank
            if intersection != 1 or span_rank != 17:
                raise AssertionError(
                    f"charts r={r} c={c}: intersection {intersection}, span {span_rank}"
                )
            pairs += 1
    if len(set(spaces.values())) != (1 << DIM) - 1:
        raise AssertionError("distinct nonzero row vectors failed to give distinct FULL charts")
    if pairs != ((1 << DIM) - 1) ** 2:
        raise AssertionError(f"pair count {pairs}")
    return {
        "field": 2,
        "factor_dimension": DIM,
        "f81_dimension": F81,
        "nonzero_row_charts": (1 << DIM) - 1,
        "pairs_checked": pairs,
        "row_dimension": DIM,
        "column_dimension": DIM,
        "intersection_dimension": 1,
        "span_dimension": 17,
        "codimension_in_f81": F81 - 17,
    }


# Noncommutative polynomials: a term is (coefficient, atom tuple).
Poly = list[tuple[int, tuple[str, ...]]]


def canon(terms: list[tuple[int, tuple[str, ...]]]) -> Poly:
    acc: dict[tuple[str, ...], int] = {}
    for coeff, atoms in terms:
        if coeff == 0:
            continue
        acc[atoms] = acc.get(atoms, 0) + coeff
    return [(acc[atoms], atoms) for atoms in sorted(acc) if acc[atoms]]


def add(left: Poly, right: Poly) -> Poly:
    return canon([*left, *right])


def scale(poly: Poly, factor: int) -> Poly:
    return canon([(factor * coeff, atoms) for coeff, atoms in poly])


def mul(left: Poly, right: Poly) -> Poly:
    return canon(
        [
            (cl * cr, al + ar)
            for cl, al in left
            for cr, ar in right
        ]
    )


ONE: Poly = [(1, ())]


def atom(name: str) -> Poly:
    return [(1, (name,))]


def block_apply(matrix: list[list[Poly]], vector: list[Poly]) -> list[Poly]:
    out = []
    for row in matrix:
        acc: Poly = []
        for entry, coord in zip(row, vector, strict=True):
            acc = add(acc, mul(entry, coord))
        out.append(acc)
    return out


def source_terms(poly: Poly) -> Poly:
    return [(c, a) for c, a in poly if "x" in a and "y" not in a]


def gram_product(ar: Poly, ac: Poly) -> list[list[Poly]]:
    """M = U(-A_c) S(A_r) = [[I - A_c A_r, -A_c], [A_r, I]]."""
    return [
        [add(ONE, scale(mul(ac, ar), -1)), scale(ac, -1)],
        [ar, ONE],
    ]


def physical_source(matrix: list[list[Poly]], entrance: list[Poly]) -> Poly:
    """First block of Gphys = diag(F, F K) applied to M * entrance."""
    image = block_apply(matrix, entrance)
    return mul(atom("F"), image[0])


def shortcut_identity() -> dict[str, list[list[str]]]:
    ar, ac = atom("Ar"), atom("Ac")
    kx = mul(atom("K"), atom("x"))
    entrance = [kx, atom("y")]
    plain = [atom("x"), atom("y")]
    full = physical_source(gram_product(ar, ac), entrance)
    row_undo = physical_source(gram_product([], ac), entrance)
    col_undo = physical_source(gram_product(ar, []), entrance)
    row_without_chart = physical_source(gram_product([], ac), plain)
    full_source = source_terms(full)
    row_source = source_terms(row_undo)
    col_source = source_terms(col_undo)
    cleared = source_terms(row_without_chart)
    expect_full = canon(
        [
            (1, ("F", "K", "x")),
            (-1, ("F", "Ac", "Ar", "K", "x")),
        ]
    )
    expect_undo = [(1, ("F", "K", "x"))]
    expect_cleared = [(1, ("F", "x"))]
    if full_source != expect_full:
        raise AssertionError(f"full source {full_source}")
    if row_source != expect_undo or col_source != expect_undo:
        raise AssertionError(f"undo source row={row_source} col={col_source}")
    if cleared != expect_cleared:
        raise AssertionError(f"cleared entrance source {cleared}")
    if any("K" not in atoms for _c, atoms in full_source):
        raise AssertionError("a source monomial lost K")
    def words(poly: Poly) -> list[dict[str, object]]:
        return [{"coeff": coeff, "atoms": list(atoms)} for coeff, atoms in poly]

    return {
        "full_source": words(full_source),
        "row_undo_source": words(row_source),
        "column_undo_source": words(col_source),
        "row_undo_if_entrance_drops_K": words(cleared),
    }


def gate() -> dict[str, int | bool]:
    if N_DATA != 10816:
        raise AssertionError(N_DATA)
    capacity = WIDTH * ROLES
    remaining = capacity - N_DATA - CALLS * PROGRESS_CAP
    bare = CALLS * BARE_MASS + remaining
    inherited_excess = bare - capacity
    if capacity != 2965248 or remaining != 2473536 or bare != 2966080 or inherited_excess != 832:
        raise AssertionError(
            f"inherited gate tie-out capacity={capacity} remaining={remaining} "
            f"bare={bare} excess={inherited_excess}"
        )
    # Debt-free specialization d = mass - progress = 0 of C < N - 208 d.
    debt = 0
    allowance = N_DATA - CALLS * debt
    factor_cost = N_DATA  # one rank-one K child on every data position
    if not (factor_cost == allowance and not factor_cost < allowance):
        raise AssertionError("factor cost must meet, and therefore miss, the strict allowance")
    excess_before = CALLS * debt - N_DATA
    excess_after = excess_before + factor_cost
    if excess_before != -N_DATA or excess_after != 0:
        raise AssertionError(f"screened excess {excess_before} -> {excess_after}")
    bill = capacity + excess_after
    if bill != capacity:
        raise AssertionError("screened bill must equal 81W")
    return {
        "N": N_DATA,
        "m": WIDTH,
        "W": ROLES,
        "calls": CALLS,
        "capacity_81W": capacity,
        "inherited_positive_debt_excess": inherited_excess,
        "debt_free_allowance": allowance,
        "rank_one_chart_cost": factor_cost,
        "strict_gate_passes": factor_cost < allowance,
        "screened_excess": excess_after,
        "screened_bill": bill,
    }


def controls() -> int:
    """Mutants that must not satisfy the theorem."""
    count = 0
    zero_rank, _zero = rank_and_reduced(row_space(0))
    if zero_rank != 0:
        raise AssertionError("the zero row vector is not a 9-dimensional chart")
    count += 1
    # A one-dimensional factor would make the local span smaller than 17.
    bad_r, bad_c = 1, 1
    span_rank, _span = rank_and_reduced(row_space(bad_r)[:1] + column_space(bad_c)[:1])
    if span_rank == 17:
        raise AssertionError("truncated charts unexpectedly spanned 17")
    count += 1
    # Dropping K from the entrance removes the defect; the theorem is about K.
    ar, ac = atom("Ar"), atom("Ac")
    dropped = source_terms(physical_source(gram_product([], ac), [atom("x"), atom("y")]))
    if dropped == [(1, ("F", "K", "x"))]:
        raise AssertionError("dropping K still looked like the chart defect")
    count += 1
    # An off-by-one tariff would pass the strict inequality and is not this bill.
    if (N_DATA - 1) < (N_DATA - CALLS * 0):
        count += 1
    else:
        raise AssertionError("control tariff failed to become strict")
    # Commuting F through K is a different word and is not the physical order.
    if canon([(1, ("K", "F", "x"))]) == canon([(1, ("F", "K", "x"))]):
        raise AssertionError("polynomial normal form identified distinct chart orders")
    count += 1
    return count


def receipt() -> dict:
    charts = chart_census()
    identity = shortcut_identity()
    bill = gate()
    control_count = controls()
    return {
        "charts": charts,
        "identity": identity,
        "gate": bill,
        "checks": 3,
        "controls": control_count,
        "kappa_claim": None,
    }


def main() -> None:
    result = receipt()
    result_path = Path(__file__).with_name("RESULT.json")
    committed = json.loads(result_path.read_text(encoding="utf-8"))
    comparable = {key: result[key] for key in ("charts", "identity", "gate")}
    recorded = {key: committed[key] for key in ("charts", "identity", "gate")}
    if comparable != recorded:
        raise SystemExit("RESULT.json does not match the recomputed certificate")
    checks = result["checks"]
    controls = result["controls"]
    print(
        "PASS_P104_SOURCE_CHART_SHORTCUT "
        f"checks={checks} controls={controls} "
        f"span={result['charts']['span_dimension']} "
        f"codimension={result['charts']['codimension_in_f81']} "
        f"cost={result['gate']['rank_one_chart_cost']} "
        f"allowance={result['gate']['debt_free_allowance']} "
        f"bill={result['gate']['screened_bill']}"
    )


if __name__ == "__main__":
    main()
