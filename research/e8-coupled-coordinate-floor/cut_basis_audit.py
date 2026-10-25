"""Independent actual-equality-basis cut audit, prepared by conorholds.

Apache-2.0; substantial OpenAI Codex assistance. Uses only the separately
authored independent_model.py and stdlib, never the primary implementation.
Finite examples supplement, rather than prove, the universal cut lemma.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import json
import runpy


MODEL = runpy.run_path(str(Path(__file__).with_name("independent_model.py")),
                       run_name="independent_model")
Field = MODEL["Field"]
require = MODEL["require"]
binary_rank = MODEL["binary_rank"]
support_weight = MODEL["support_weight"]
term_cost = MODEL["term_cost"]


def rational_rank(vectors):
    """Fraction-free Q elimination, clearing denominators row by row."""
    basis = {}
    for vector in vectors:
        values = [Fraction(x) for x in vector]
        denominator = lcm(*(x.denominator for x in values))
        row = [int(x * denominator) for x in values]
        for pivot, old in sorted(basis.items()):
            if row[pivot]:
                divisor = gcd(row[pivot], old[pivot])
                left, right = old[pivot] // divisor, row[pivot] // divisor
                row = [left * x - right * y for x, y in zip(row, old)]
                common = gcd(*row)
                if common:
                    row = [x // common for x in row]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            common = gcd(*row)
            if row[pivot] < 0:
                common = -common
            basis[pivot] = [x // common for x in row]
    return len(basis)


def scalar_rank(vectors, field):
    return field.rank(vectors) if field.prime else rational_rank(vectors)


def root_index(rows, target):
    opposite = tuple(-x for x in target)
    return next(i for i, row in enumerate(rows) if row in (target, opposite))


def geometries(rows):
    def pair(i, j, sign=-1):
        return tuple(2 if t == i else 2 * sign if t == j else 0 for t in range(8))
    orthogonal = [root_index(rows, pair(i, i + 1, sign))
                  for i in range(0, 8, 2) for sign in (-1, 1)]
    star = [root_index(rows, pair(0, i)) for i in range(1, 8)]
    star.append(root_index(rows, (1,) * 8))
    simple = [root_index(rows, (1, -1, -1, -1, -1, -1, -1, 1)),
              root_index(rows, pair(0, 1, 1)), root_index(rows, pair(0, 1))]
    simple += [root_index(rows, pair(i, i + 1)) for i in range(1, 6)]
    return {"orthogonal": orthogonal, "star": star, "simple": simple}


def evaluation(rows, normal, field):
    return tuple(field.scalar(Fraction(MODEL["dot"](row, normal), 4)) for row in rows)


def make_basis(rows, labels, selected, variant, field):
    """Actual coordinate units, actual holes, and actual code completions."""
    k = len(selected)
    normals = [rows[i] for i in selected]
    require(scalar_rank(normals, field) == k, "independent selected root normals")
    for row in rows:
        if len(normals) == 8:
            break
        if scalar_rank(normals + [row], field) > len(normals):
            normals.append(row)
    require(len(normals) == 8, "scalar completion")
    code = [evaluation(rows, normal, field) for normal in normals]
    units = [tuple(field.scalar(int(i == a)) for i in range(120)) for a in selected]
    holes = [field.combine((1, code[j]), (-2, units[j])) for j in range(k)]
    completion = code[k:]
    if variant:
        coefficients = (Fraction(1, 2), -1, 2, -2)
        scaled_units, sheared_holes = [], []
        for j, (a, hole) in enumerate(zip(selected, holes)):
            terms = [(1, hole)]
            for b, unit in zip(selected, units):
                if (labels[a] & labels[b]).bit_count() % 2 == 0:
                    # Some allowed shears cancel the coordinate exactly.
                    coefficient = -hole[b] if (a + b) % 2 == 0 else Fraction(1, 2)
                    terms.append((coefficient, unit))
            sheared_holes.append(field.combine((coefficients[j % 4], field.combine(*terms))))
            scaled_units.append(field.combine((coefficients[(j + 1) % 4], units[j])))
        completion = [field.combine(
            (coefficients[j % 4], vector),
            *((coefficients[(j + a) % 4], unit) for a, unit in enumerate(units)))
            for j, vector in enumerate(completion)]
        units, holes = scaled_units, sheared_holes
    basis = units + holes + completion
    weights = [support_weight(vector, labels) for vector in basis]
    require(weights == [1] * k + [8] * k + [9] * (8 - k), "actual equality-basis weights")
    require(sum(weights) == 72, "actual equality-basis cost")
    require(scalar_rank(basis, field) == 8 + k, "actual equality-basis independence")
    require(scalar_rank(basis + code + units, field) == 8 + k, "actual space C+D_A")
    return basis, weights


def cut_audit(basis, weights, rows, labels, characters, field):
    checks, vanishing_checks, dimensions = 0, 0, {}
    for v, coordinates in enumerate(characters):
        restriction = [tuple(vector[i] for i in coordinates) for vector in basis]
        vanishing = [j for j, vector in enumerate(restriction) if not any(vector)]
        rank = scalar_rank(restriction, field)
        dimension = len(basis) - rank
        require(dimension == len(vanishing), f"actual-column cut generation at v={v}")
        dimensions[dimension] = dimensions.get(dimension, 0) + 1
        if vanishing:
            hole = list(evaluation(rows, rows[v], field))
            hole[v] = field.clean(hole[v] - field.scalar(2))
            for j in vanishing:
                supported_labels = [label for value, label in zip(basis[j], labels) if value]
                require(binary_rank(supported_labels + [labels[v]]) == weights[j] + 1,
                        "vanishing column excludes u_v from its support span")
                require(term_cost(hole, basis[j], labels) == weights[j],
                        "vanishing actual column has no singleton-hole rebate")
                vanishing_checks += 1
        checks += 1
    return {"cuts": checks, "vanishing_membership_and_copy_checks": vanishing_checks,
            "cut_dimension_histogram": dimensions}


def minimum_basis_countercontrol(rows, labels, field):
    # Four mutually nonorthogonal star roots. The scalar space here is only
    # two-dimensional; the minimum-basis cut statement is false in general.
    indices = [root_index(rows, tuple(2 if t == 0 else -2 if t == j else 0
                                    for t in range(8))) for j in range(1, 5)]
    v, a, b, c = indices
    require(all((labels[i] & labels[j]).bit_count() % 2 == int(i == j)
                for i in indices for j in indices), "four-star binary labels")
    units = [tuple(field.scalar(int(i == j)) for i in range(120)) for j in indices]
    f1 = field.combine((1, units[0]), (1, units[1]))
    f2 = field.combine((-1, units[0]), (1, units[2]), (1, units[3]))
    basis = [f1, f2]
    require([support_weight(vector, labels) for vector in basis] == [2, 3], "bad-cut basis cost five")
    # For x*f1+y*f2 the four coordinates are (x-y,x,y,y).
    # Over Q the four support strata are y=0, x=0, x=y, and the generic
    # x*y*(x-y)!=0 stratum. Their representatives below exhaust support costs.
    coefficients = ([(1, t) for t in range(field.prime)] + [(0, 1)]
                    if field.prime else [(1, 0), (0, 1), (1, 1), (1, 2)])
    rays = [field.combine((x, f1), (y, f2)) for x, y in coefficients]
    minimum = min(support_weight(x, labels) + support_weight(y, labels)
                  for x, y in combinations(rays, 2) if scalar_rank([x, y], field) == 2)
    require(minimum == 5, "genuine minimum-cost basis countercontrol")
    coordinates = [i for i, label in enumerate(labels)
                   if (label & labels[v]).bit_count() % 2]
    restriction = [tuple(vector[i] for i in coordinates) for vector in basis]
    rank = scalar_rank(restriction, field)
    vanishing = sum(not any(vector) for vector in restriction)
    require(rank == 1 and vanishing == 0, "countercontrol violates strong cut condition")
    g = field.combine((1, f1), (1, f2))
    require(any(g) and all(not g[i] for i in coordinates), "nontrivial cut-kernel vector")
    require(g == field.combine((1, units[1]), (1, units[2]), (1, units[3])), "explicit cut-kernel identity")
    return {"root_coordinates": indices, "minimum_basis_cost": minimum,
            "cut_dimension": 2 - rank, "vanishing_actual_columns": vanishing,
            "universal_minimum_basis_claim_rejected": True}


def verify():
    rows, labels = MODEL["root_model"]()
    MODEL["check_model"](rows, labels)
    geometry = geometries(rows)
    require(all(rational_rank([rows[i] for i in selected]) == 8 for selected in geometry.values()),
            "three independent scalar-root geometries")
    require(MODEL["dot"](rows[geometry["orthogonal"][0]], rows[geometry["orthogonal"][1]]) == 0,
            "orthogonal pair type")
    require(MODEL["dot"](rows[geometry["star"][0]], rows[geometry["star"][1]]) != 0,
            "nonorthogonal pair type")
    characters = [tuple(i for i, label in enumerate(labels)
                        if (normal & label).bit_count() % 2) for normal in labels]
    require(all(len(coordinates) == 64 for coordinates in characters), "root-character sizes")
    result = {"root_lines": 120, "gram_pairing_checks": 14400, "fields": {}}
    for prime in (0, 3, 5, 7):
        field = Field(prime)
        cases = []
        for name, selected in geometry.items():
            if prime and name == "simple":
                continue
            sizes = range(1, 9) if not prime else (2,)
            for k in sizes:
                for variant in (0, 1):
                    try:
                        basis, weights = make_basis(rows, labels, selected[:k], variant, field)
                        cut = cut_audit(basis, weights, rows, labels, characters, field)
                    except ValueError as error:
                        raise ValueError(f"field={prime or 'Q'}, geometry={name}, k={k}, "
                                         f"variant={variant}: {error}") from error
                    cases.append({"geometry": name, "k": k, "sheared": bool(variant),
                                  "basis_dimension": len(basis), "basis_cost": sum(weights), **cut})
        result["fields"][str(prime) if prime else "Q"] = {
            "actual_equality_bases": cases,
            "minimum_basis_countercontrol": minimum_basis_countercontrol(rows, labels, field)}
    result["basis_count"] = sum(len(value["actual_equality_bases"]) for value in result["fields"].values())
    result["root_cut_count"] = 120 * result["basis_count"]
    result["vanishing_membership_and_copy_checks"] = sum(
        row["vanishing_membership_and_copy_checks"]
        for field in result["fields"].values() for row in field["actual_equality_bases"])
    return result


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
