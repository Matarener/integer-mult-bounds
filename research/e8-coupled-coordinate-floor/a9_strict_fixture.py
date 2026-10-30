"""Exact strict-basis73 / COPY72 fixture, by conorholds.

Apache-2.0; substantial OpenAI Codex assistance. Uses only the independently
authored root model and exact inverse utility. The actual-basis bill73 is a characteristic-zero minimum; the displayed
construction and its actual bill work over every odd field.
"""

from fractions import Fraction
from pathlib import Path
import json
import runpy


PARTIAL = runpy.run_path(str(Path(__file__).with_name("partial_fixture.py")),
                        run_name="partial_fixture")
M = PARTIAL["M"]
Field, require = M["Field"], M["require"]


def data(rows):
    targets = [(1, -1, -1, -1, -1, -1, -1, 1),
               (2, 2, 0, 0, 0, 0, 0, 0), (-2, 2, 0, 0, 0, 0, 0, 0)]
    targets += [tuple(-2 if j == i else 2 if j == i + 1 else 0 for j in range(8))
                for i in range(1, 6)]
    selected = [next(i for i, row in enumerate(rows)
                     if row == target or row == tuple(-x for x in target))
                for target in targets]
    v = next(i for i in range(120) if i not in selected)
    h = [tuple(Fraction(x, 2) for x in rows[i]) for i in selected]
    inverse, determinant = PARTIAL["inverse_and_determinant"](h)
    require(abs(determinant) == 1, "E8 simple normals give a unit determinant")
    dual = [tuple(inverse[j][i] for j in range(8)) for i in range(8)]
    neighbors = [tuple(j for j in range(8) if i != j and M["dot"](h[i], h[j]))
                 for i in range(8)]
    require(all(neighbors), "no isolated simple root")
    require(len({frozenset((i,) + neighbors[i]) for i in range(8)}) == 8,
            "distinct closed neighborhoods give distinct unit-reader rays")
    reached, pending = {0}, [0]
    while pending:
        for j in neighbors[pending.pop()]:
            if j not in reached:
                reached.add(j)
                pending.append(j)
    require(len(reached) == 8, "connected simple-root graph")
    require(sum(map(len, neighbors)) == 14 and max(map(len, neighbors)) == 3,
            "E8 tree edge and degree counts")
    return selected, v, h, dual, neighbors, int(determinant)


def verify_field(rows, labels, selected, v, h, dual, neighbors, field):
    evaluate = PARTIAL["evaluate"]
    dv = tuple(field.scalar(int(i == v)) for i in range(120))
    units = [tuple(field.scalar(int(i == a)) for i in range(120)) for a in selected]
    rv = tuple(Fraction(x, 2) for x in rows[v])
    ev = evaluate(rows, rv, field)
    code = [evaluate(rows, normal, field) for normal in h]
    c = [M["dot"](rv, normal) for normal in h]
    beta = [M["dot"](rv, normal) for normal in dual]
    t = [field.combine((Fraction(1, 2), evaluate(rows, normal, field))) for normal in dual]
    high_p = [field.combine((1, t[i]), (-beta[i] / 4, dv)) for i in range(8)]
    unit_p = [field.combine((2, high_p[i]), *((-1, high_p[j]) for j in neighbors[i]))
              for i in range(8)]
    holes = [field.combine((1, code[i]), (-2, units[i]), (c[i], dv),
                           *((1, units[j]) for j in neighbors[i])) for i in range(8)]
    jv = field.combine((1, dv), (Fraction(-1, 2), ev))
    q0 = field.combine((Fraction(1, 4), ev), (Fraction(-1, 2), dv))
    alpha = [2 * beta[i] - sum(beta[j] for j in neighbors[i]) for i in range(8)]
    expansion = field.combine((-1, dv),
                              *((alpha[i] / 4, units[i]) for i in range(8)),
                              *((beta[i] / 4, holes[i]) for i in range(8)))
    require(expansion == q0, "free pivot has actual unit-v coordinate minus one")
    left = [jv] + unit_p + high_p + [dv]
    right = [dv] + units + holes + [q0]
    require(M["product_equal"](left, right, rows, field), "exact strict-basis compensation product")
    require(M["normalized"](left, right, field), "both full factor families are normalized")
    require((field.rank(left), field.rank(right)) == (9, 17), "actual ranks nine and seventeen")
    require(field.rank(left + code + [dv]) == 9, "actual singleton P space")
    require(field.rank(right + code + [dv] + units) == 17, "actual full nine-coordinate Q space")
    require(field.rank(right[:-1]) == 17, "nonpivot Q is the actual seventeen-column basis")
    basis_weights = [M["support_weight"](vector, labels) for vector in right[:-1]]
    require(basis_weights == [1] * 9 + [8] * 8 and sum(basis_weights) == 73,
            "actual nonpivot basis attains the strict73 floor")
    costs = [M["term_cost"](p, q, labels) for p, q in zip(left, right)]
    require(costs == [0] + [1] * 8 + [8] * 8 + [0] and sum(costs) == 72,
            "strict73 minus one rebate attains COPY72")
    require([M["support_weight"](vector, labels) for vector in left]
            == [8] + [9] * 16 + [1], "only the two exceptional P rays are deficient")
    for i, a in enumerate(selected):
        require(all(not holes[i][x] for x, label in enumerate(labels)
                    if (label & labels[a]).bit_count() % 2), "actual allowed root-hole cut")
        require(not c[i] or (labels[a] & labels[v]).bit_count() % 2 == 0,
                "v correction is allowed only at a neighbor")
    merged_p, merged_q = M["merge"](left, right, field)
    require((len(merged_p), field.rank(merged_p), field.rank(merged_q)) == (18, 9, 17),
            "both-side proportional merging preserves the large actual Q space")
    require(M["product_equal"](merged_p, merged_q, rows, field), "normalized product exactness")
    require(not M["product_equal"](left[1:], right[1:], rows, field),
            "cannot delete the active free J atom")
    require(not M["product_equal"](left[:-1], right[:-1], rows, field),
            "cannot delete the active free pivot")
    # Removing all cross shears keeps exactness but creates eight repeated
    # P rays, which collapse the actual Q space under proportional merging.
    plain_holes = [field.combine((1, code[i]), (-2, units[i]), (c[i], dv)) for i in range(8)]
    plain_p = [jv] + [field.combine((2, vector)) for vector in high_p] + high_p + [dv]
    plain_q = [dv] + units + plain_holes + [q0]
    require(M["product_equal"](plain_p, plain_q, rows, field), "unsheared positive exact-product control")
    require(not M["normalized"](plain_p, plain_q, field), "unsheared repeated P rays are detected")
    plain_merged_p, plain_merged_q = M["merge"](plain_p, plain_q, field)
    require((len(plain_merged_p), field.rank(plain_merged_p), field.rank(plain_merged_q)) == (10, 9, 9),
            "unsheared fixture cannot retain full A9 after normalization")
    return {"terms": 18, "actual_ranks": [9, 17], "coordinate_count": 9,
            "actual_nonpivot_basis_weights": basis_weights, "actual_basis_bill": 73,
            "copy_costs": costs, "copy": 72, "both_normalizations_stable": True,
            "unsheared_after_merge": {"terms": 10, "ranks": [9, 9]},
            "failed_product_controls": 2}


def outside_frame(rows, excluded):
    def visit(chosen, candidates):
        if len(chosen) == 8:
            return chosen
        for j, index in enumerate(candidates):
            future = [x for x in candidates[j + 1:] if M["dot"](rows[index], rows[x]) == 0]
            if len(future) + len(chosen) + 1 >= 8:
                result = visit(chosen + [index], future)
                if result is not None:
                    return result
        return None
    frame = visit([], [i for i in range(120) if i not in excluded])
    require(frame is not None and len(frame) == 8, "orthogonal frame outside A9")
    require(all(M["dot"](rows[i], rows[j]) == 8 * int(i == j)
                for i in frame for j in frame), "outside frame norm-two Gram")
    return frame


def verify():
    rows, labels = M["root_model"]()
    M["check_model"](rows, labels)
    selected, v, h, dual, neighbors, determinant = data(rows)
    frame = outside_frame(rows, set(selected) | {v})
    result = {"coordinate_roots": [v] + selected, "outside_orthogonal_frame": frame, "pivot_root": v,
              "simple_normal_basis_determinant": determinant,
              "simple_graph_adjacency": neighbors, "gram_pairing_checks": 14400,
              "fields": {}}
    for prime in (0, 3, 5, 7):
        result["fields"][str(prime) if prime else "Q"] = verify_field(
            rows, labels, selected, v, h, dual, neighbors, Field(prime))
    return result


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
