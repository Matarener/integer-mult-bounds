#!/usr/bin/env python3
"""Rejection controls. Imports both checkers and does not change their proofs."""
import independent
import verify


def require(condition, message):
    if not condition:
        raise SystemExit("CONTROL_FAILED " + message)


def test_programs_agree():
    for hubs in (1, 2, 3):
        left = verify.summarize(hubs)
        right = independent.summarize(hubs)
        for key in ("rows", "charge", "excess", "forced_rows", "readers_per_mark", "sources_per_mark"):
            require(left[key] == right[key], f"h={hubs} {key}")
    require(verify.k32_charge() == 54, "fraction K3,2")
    require(independent.k32_charge() == 54, "integer K3,2")


def test_rank_methods_agree_on_two_hubs():
    names, vecs, _E, _F, dim = verify.star(2)
    for mask in range(1 << len(names)):
        rows = [vecs[i] for i in verify.bits(mask)]
        require(verify.rank(rows, dim) == independent.rank(rows, dim), f"rank mask {mask}")


def test_triple_is_minimal_and_costs_two():
    _names, vecs, E, F, dim = verify.star(1)
    triple = [1, 4, 5]  # d, x0, y0
    require(verify.spans(vecs, triple, E, dim), "triple spans E")
    require(verify.reader_cost(vecs, (1 << 1) | (1 << 4) | (1 << 5), E, F, dim) == 2, "triple cost")
    for omitted in range(3):
        proper = [triple[i] for i in range(3) if i != omitted]
        require(not verify.spans(vecs, proper, E, dim), "proper subset spans E")


def test_crossed_row_is_not_the_k32_certificate():
    full = verify.summarize(2)
    require(full["charge"] == 128 and full["excess"] == 24, "full two-hub charge")
    require(verify.k32_charge() == 54, "21-premise charge stays 54")
    require(full["charge"] != verify.k32_charge(), "certificates differ")


def determinant(rows):
    size = len(rows)
    if size == 1:
        return rows[0][0]
    total = 0
    for column in range(size):
        minor = [
            [rows[i][k] for k in range(size) if k != column]
            for i in range(1, size)
        ]
        total += (-1) ** column * rows[0][column] * determinant(minor)
    return total


def test_written_determinants():
    # PROOF.md: family A minor on E,F,G and family C minor on E,F,G,Vi,Vj.
    family_a = ((1, 1, 0), (1, 0, 1), (0, 1, 1))
    family_c = (
        (1, 1, 0, 0, 0),
        (0, 0, 0, 1, 0),
        (0, 1, 1, -1, 0),
        (0, 0, 0, 0, 1),
        (1, 0, 1, 0, -1),
    )
    require(determinant(family_a) == -2, "family A minor")
    require(determinant(family_c) == -2, "family C minor")


def test_dropping_a_third_hub_row_breaks_the_census():
    _names, _vecs, _E, _F, _dim, readers, sources = verify.census(3)
    expect = verify.predicted(3)
    require(readers[0] == expect[0], "census matches before the mutation")
    forced = verify.cost_two_masks(3)
    require(forced[0] in readers[0], "forced row present")
    mutated = [mask for mask in readers[0] if mask != forced[0]]
    require(mutated != expect[0], "dropped row still matched")


def main():
    test_programs_agree()
    test_rank_methods_agree_on_two_hubs()
    test_triple_is_minimal_and_costs_two()
    test_crossed_row_is_not_the_k32_certificate()
    test_dropping_a_third_hub_row_breaks_the_census()
    test_written_determinants()
    print("PASS_THIRD_HUB_EXTREMAL_CONTROLS mutations=6 no_new_kappa")


if __name__ == "__main__":
    main()
