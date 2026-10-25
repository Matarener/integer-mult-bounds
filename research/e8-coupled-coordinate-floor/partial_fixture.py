"""Independent noncoordinate partial-quotient fixture, by conorholds.

Apache-2.0; substantial OpenAI Codex assistance. This file imports only its
separately authored sibling model and stdlib. Explicit scalar identities,
rather than finite-field extrapolation, supply the all-odd-field construction.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json
import runpy


M = runpy.run_path(str(Path(__file__).with_name("independent_model.py")),
                 run_name="independent_model")
require, Field = M["require"], M["Field"]


def inverse_and_determinant(matrix):
    size = len(matrix)
    require(all(len(row) == size for row in matrix), "square scalar basis")
    work = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    determinant = Fraction(1)
    for j in range(size):
        pivot = next((i for i in range(j, size) if work[i][j]), None)
        require(pivot is not None, "invertible scalar basis")
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            determinant = -determinant
        coefficient = work[j][j]
        determinant *= coefficient
        work[j] = [x / coefficient for x in work[j]]
        for i in range(size):
            if i != j and work[i][j]:
                coefficient = work[i][j]
                work[i] = [x - coefficient * y for x, y in zip(work[i], work[j])]
    return [row[size:] for row in work], determinant


def selected_data(rows, labels):
    targets = [tuple(2 if j == 0 else -2 if j == i else 0 for j in range(8))
               for i in range(1, 6)]
    targets += [(0, 0, 0, 0, 0, 0, 2, -2), (2, 0, 0, 0, 0, 0, 2, 0)]
    target_v = (2, 0, 0, 0, 0, 0, 0, 2)
    find = lambda target: next(i for i, row in enumerate(rows)
                               if row == target or row == tuple(-x for x in target))
    selected, v = [find(target) for target in targets], find(target_v)
    h = [tuple(Fraction(x, 2) for x in rows[i]) for i in selected]
    h.append(tuple(Fraction(j == 7) for j in range(8)))
    inverse, determinant = inverse_and_determinant(h)
    require(abs(determinant) == 1, "unimodular scalar-normal basis")
    dual = [tuple(inverse[j][i] for j in range(8)) for i in range(8)]
    require(all(M["dot"](h[i], dual[j]) == int(i == j)
                for i in range(8) for j in range(8)), "exact rational duality")
    require(M["binary_rank"](labels[i] for i in selected) == 6, "A binary rank six")
    require(Field().rank([rows[i] for i in selected]) == 7, "A scalar rank seven")
    relation = 0
    for i in selected[:5]:
        relation ^= labels[i]
    require(relation == labels[selected[5]], "u label is the sum of the five J labels")
    require(M["binary_rank"]([labels[i] for i in selected[:5]]) == 5, "independent J labels")
    require(M["binary_rank"]([labels[i] for i in selected[:5]] + [labels[selected[6]]]) == 6,
            "w label lies outside the J span")
    require(all((labels[v] & labels[i]).bit_count() % 2 == 0 for i in selected),
            "all A roots are binary neighbors of the pivot")
    require(all(M["dot"](rows[v], rows[i]) != 0 for i in selected),
            "all A roots are scalar nonorthogonal to the pivot")
    signs = [1 if rows[i] == target else -1 for i, target in zip(selected, targets)]
    return selected, v, h, dual, int(determinant), signs


def evaluate(rows, normal, field):
    return tuple(field.scalar(sum(Fraction(row[j], 2) * normal[j] for j in range(8)))
                 for row in rows)


def quotient_audit(q, b, units, labels, field):
    require(field.rank([q, b]) == 2, "two-dimensional partial quotient")
    require(all(field.rank([q, b, unit]) == 3 for unit in units),
            "partial quotient has no coordinate unit ray")
    coefficients = list(range(field.prime)) if field.prime else [0, -1, 1]
    rays = [b] + [field.combine((1, q), (t, b)) for t in coefficients]
    require(M["support_weight"](b, labels) == 2, "b weight two")
    for t, vector in zip(coefficients, rays[1:]):
        require(M["support_weight"](vector, labels) == (5 if not t else 6),
                "complete quotient weight strata")
        require(sum(bool(x) for x in vector) >= 2, "no hidden coordinate ray")
    # Over Q, (q+t*b) has coordinates (1,1,1,1,1,1+t,t):
    # t=0,-1 and t outside {0,-1} exhaust support patterns. In finite fields
    # every projective ray is enumerated, including the b ray at infinity.
    minimum = min(M["support_weight"](x, labels) + M["support_weight"](y, labels)
                  for x, y in combinations(rays, 2) if field.rank([x, y]) == 2)
    require(minimum == 7, "minimum partial-quotient basis cost seven")
    return {"dimension": 2, "minimum_basis_cost": minimum,
            "projective_support_strata_over_Q": 4,
            "projective_rays_checked": len(rays), "contains_coordinate_unit": False}


def verify_field(rows, labels, selected, v, h, dual, field):
    units = [tuple(field.scalar(int(i == a)) for i in range(120)) for a in selected]
    pivot = tuple(field.scalar(int(i == v)) for i in range(120))
    q = field.combine(*((1, unit) for unit in units[:6]))
    b = field.combine((1, units[5]), (1, units[6]))
    q_minus_b = field.combine((1, q), (-1, b))
    q_plus_b = field.combine((1, q), (1, b))
    code_h = [evaluate(rows, normal, field) for normal in h]
    t = [field.combine((Fraction(1, 2), evaluate(rows, normal, field))) for normal in dual]
    high_q = [field.combine((1, code_h[j]), (-2, q_minus_b)) for j in range(5)]
    high_q += [field.combine((1, code_h[j]), (-2, b)) for j in (5, 6)] + [code_h[7]]
    low_q = field.combine(*((2, vector) for vector in t[:5]))
    low_b = field.combine(*((-2, vector) for vector in t[:5]), (2, t[5]), (2, t[6]))
    left = [field.combine((1, low_q), (-1, pivot)),
            field.combine((1, low_b), (-1, pivot))] + t + [pivot]
    right = [q, b] + high_q + [q_plus_b]
    require(M["product_equal"](left, right, rows, field), "exact noncoordinate decoder product")
    require(M["normalized"](left, right, field), "active pairwise nonproportional factors")
    require((field.rank(left), field.rank(right)) == (9, 10), "actual factor ranks nine and ten")
    require(field.rank(left + code_h + [pivot]) == 9, "actual singleton P space")
    require(field.rank(right + code_h + [q, b]) == 10, "actual Q equals C plus the partial quotient")
    require(field.rank(code_h + [q, b]) == 10, "direct code/quotient sum")
    require(field.rank([rows[i] for i in selected]) == 7, "selected scalar rank survives field reduction")
    # Eligibility is tested on the actual oriented root at its own coordinate.
    for j, a in enumerate(selected):
        lam = q_minus_b if j < 5 else b
        require(lam[a] == field.scalar(1), "eligibility coefficient is exactly one")
        require(all(not high_q[j][i] for i, label in enumerate(labels)
                    if (label & labels[a]).bit_count() % 2), "actual high column vanishes on its root cut")
    q_normal = tuple(sum(dual[j][i] for j in range(5)) for i in range(8))
    b_normal = tuple(-sum(dual[j][i] for j in range(5)) + dual[5][i] + dual[6][i]
                     for i in range(8))
    require(M["dot"](q_normal, h[7]) == M["dot"](b_normal, h[7]) == 0,
            "low normals have zero eighth dual coordinate")
    require(abs(M["dot"](tuple(Fraction(x, 2) for x in rows[v]), h[7])) == 1,
            "pivot root has nonzero eighth dual coordinate")
    p_weights = [M["support_weight"](vector, labels) for vector in left]
    q_weights = [M["support_weight"](vector, labels) for vector in right]
    costs = [M["term_cost"](p, r, labels) for p, r in zip(left, right)]
    require(p_weights == [9] * 10 + [1], "actual singleton support weights")
    require(q_weights == [5, 2] + [8] * 7 + [9, 6], "actual partial-Q support weights")
    require(costs == [5, 2] + [8] * 7 + [9, 0] and sum(costs) == 72,
            "noncoordinate sharp linear COPY profile")
    merged_p, merged_q = M["merge"](left, right, field)
    require(len(merged_p) == 11 and M["product_equal"](merged_p, merged_q, rows, field),
            "proportional-normalization stability")
    require(not M["product_equal"](left[:-1], right[:-1], rows, field),
            "cannot delete the active zero-cost pivot")
    uncompensated = list(left)
    uncompensated[0] = low_q
    require(not M["product_equal"](uncompensated, right, rows, field),
            "omitting one singleton compensation fails")
    wrong_sign = list(right)
    wrong_sign[2] = field.combine((1, code_h[0]), (-2, q_plus_b))
    require(not M["product_equal"](left, wrong_sign, rows, field),
            "wrong eligible-quotient sign fails exactness")
    return {"terms": 11, "actual_ranks": [9, 10], "costs": costs,
            "p_support_weights": p_weights, "q_support_weights": q_weights,
            "quotient": quotient_audit(q, b, units, labels, field),
            "eligible_roots": 7, "failure_controls": 3}


def verify():
    rows, labels = M["root_model"]()
    M["check_model"](rows, labels)
    selected, v, h, dual, determinant, signs = selected_data(rows, labels)
    result = {"root_coordinates_A": selected, "root_coordinate_v": v,
              "orientation_signs_A": signs, "scalar_normal_basis_determinant": determinant,
              "scalar_rank_A": 7, "binary_rank_A": 6, "gram_pairing_checks": 14400,
              "fields": {}}
    for prime in (0, 3, 5, 7):
        result["fields"][str(prime) if prime else "Q"] = verify_field(
            rows, labels, selected, v, h, dual, Field(prime))
    return result


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
