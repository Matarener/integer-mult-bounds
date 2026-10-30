"""Independent Gaussian-Fraction checks for the all-size Schur closure proof.

Finite evidence uses mu(z)=|Re z|+|Im z|, hence is rational throughout.
No producer module or receipt is imported. The universal complex theorem
is the separate written proof, not an extrapolation of this enumeration.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def z(a=0, b=0):
    return Q(a), Q(b)


ZERO, ONE = z(), z(1)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def neg(a):
    return -a[0], -a[1]


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def div(a, b):
    norm = b[0]*b[0]+b[1]*b[1]
    need(norm > 0, "nonzero Gaussian divisor")
    value = mul(a, (b[0], -b[1]))
    return value[0]/norm, value[1]/norm


def mu(a):
    return abs(a[0])+abs(a[1])


def identity(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def block(matrix, rows, columns):
    return [[matrix[i][j] for j in columns] for i in rows]


def minus(left, right):
    return [[sub(a, b) for a, b in zip(x, y)] for x, y in zip(left, right)]


def times(left, right):
    columns = len(right[0]) if right else 0
    return [[sumz(mul(left[i][k], right[k][j]) for k in range(len(right)))
             for j in range(columns)] for i in range(len(left))]


def sumz(values):
    value = ZERO
    for entry in values:
        value = add(value, entry)
    return value


def inverse(matrix):
    n = len(matrix)
    rows = [row[:] + unit for row, unit in zip(matrix, identity(n))]
    for pivot in range(n):
        selected = next((i for i in range(pivot, n) if rows[i][pivot] != ZERO), None)
        need(selected is not None, "singular principal pivot")
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        divisor = rows[pivot][pivot]
        rows[pivot] = [div(x, divisor) for x in rows[pivot]]
        for i in range(n):
            if i != pivot:
                factor = rows[i][pivot]
                rows[i] = [sub(a, mul(factor, b)) for a, b in zip(rows[i], rows[pivot])]
    result = [row[n:] for row in rows]
    need(times(matrix, result) == times(result, matrix) == identity(n), "two-sided exact inverse")
    return result


def norms(matrix):
    if not matrix:
        return Q(0), Q(0)
    row = max(sum((mu(x) for x in entries), Q(0)) for entries in matrix)
    column = max(sum((mu(entries[j]) for entries in matrix), Q(0)) for j in range(len(matrix[0])))
    return column, row


def schur(matrix, eliminated, retained):
    result = block(matrix, retained, retained)
    if not eliminated:
        return result
    correction = times(times(block(matrix, retained, eliminated),
                             inverse(block(matrix, eliminated, eliminated))),
                       block(matrix, eliminated, retained))
    return minus(result, correction)


def positive_matrix(matrix):
    return [[z(mu(value)) for value in row] for row in matrix]


def check_one(matrix, rho, eliminated, retained):
    n = len(matrix)
    defect = minus(matrix, identity(n))
    need(max(norms(defect)) <= rho < 1, "two-sided component envelope admission")
    current = schur(matrix, eliminated, retained)
    delta = minus(current, identity(len(retained)))
    need(max(norms(delta)) <= rho, "sharp rho closure")
    need(max(norms(current)) <= 1+rho, "descendant direct norm")
    need(max(norms(inverse(current))) <= 1/(1-rho), "descendant inverse norm")
    if eliminated:
        positive = positive_matrix(defect)
        pee = block(positive, eliminated, eliminated)
        neumann = inverse(minus(identity(len(eliminated)), pee))
        need(all(value[1] == 0 and value[0] >= 0 for row in neumann for value in row), "positive resolvent")
        bound = block(positive, retained, retained)
        extra = times(times(block(positive, retained, eliminated), neumann),
                      block(positive, eliminated, retained))
        bound = [[add(a, b) for a, b in zip(x, y)] for x, y in zip(bound, extra)]
        for i, row in enumerate(delta):
            for j, value in enumerate(row):
                need(mu(value) <= bound[i][j][0] and bound[i][j][1] == 0, "entrywise Schur majorant")
        for i in range(len(retained)):
            escape = sum((positive[retained[i]][j][0] for j in eliminated), Q(0))
            rowbound = sum((x[0] for x in bound[i]), Q(0))
            need(rowbound <= rho-(1-rho)*escape, "strong row budget slack")
        for j in range(len(retained)):
            escape = sum((positive[i][retained[j]][0] for i in eliminated), Q(0))
            columnbound = sum((row[j][0] for row in bound), Q(0))
            need(columnbound <= rho-(1-rho)*escape, "strong column budget slack")
    return current


def generated(n, seed, rho):
    raw = [[z((3*i+5*j+seed) % 7-3, (5*i+2*j+2*seed) % 5-2)
            for j in range(n)] for i in range(n)]
    maximum = max(norms(raw))
    factor = rho/maximum if maximum else Q(0)
    defect = [[mul(z(factor), entry) for entry in row] for row in raw]
    return [[add(entry, identity(n)[i][j]) for j, entry in enumerate(row)]
            for i, row in enumerate(defect)]


def general_census():
    matrices = comparisons = quotients = restrictions = 0
    digest = sha256()
    for n in (1, 2, 3, 4):
        for seed in (0, 1, 2, 3):
            for rho in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4)):
                matrix = generated(n, seed, rho)
                matrices += 1
                # 0 discarded, 1 eliminated, 2 retained: all principal
                # restrictions and elimination subsets with nonempty output.
                for labels in product((0, 1, 2), repeat=n):
                    eliminated = [i for i, flag in enumerate(labels) if flag == 1]
                    retained = [i for i, flag in enumerate(labels) if flag == 2]
                    if not retained:
                        continue
                    current = check_one(matrix, rho, eliminated, retained)
                    comparisons += 1
                    digest.update(repr(current).encode())
                    # Restricting a current Schur complement retains the
                    # previously eliminated set in its original description.
                    reduced = retained[::2]
                    restricted = block(current, list(range(0, len(retained), 2)),
                                       list(range(0, len(retained), 2)))
                    need(restricted == schur(matrix, eliminated, reduced), "restriction/elimination closure")
                    restrictions += 1
                    if len(retained) >= 2:
                        next_eliminate = retained[::2]
                        next_retain = retained[1::2]
                        nested = schur(current, list(range(0, len(retained), 2)),
                                       list(range(1, len(retained), 2)))
                        need(nested == schur(matrix, eliminated+next_eliminate, next_retain),
                             "principal Schur quotient identity")
                        quotients += 1
                    reversed_matrix = block(matrix, list(reversed(range(n))), list(reversed(range(n))))
                    need(max(norms(minus(reversed_matrix, identity(n)))) <= rho,
                         "simultaneous permutation preserves hypotheses")
    return {"matrices": matrices, "principal_restriction_schur_cases": comparisons,
            "restriction_identities": restrictions, "nested_quotient_identities": quotients,
            "sizes": [1, 2, 3, 4], "rhos": ["0", "1/4", "1/2", "3/4"],
            "component_envelope": True, "result_digest": digest.hexdigest()}


def toeplitz(symbol):
    return [[symbol[i-j] if i >= j else ZERO for j in range(len(symbol))]
            for i in range(len(symbol))]


def parity_census():
    nodes = shear_checks = 0
    roots = []

    def walk(matrix, rho):
        nonlocal nodes, shear_checks
        nodes += 1
        n = len(matrix)
        need(max(norms(minus(matrix, identity(n)))) <= rho, "recursive component envelope")
        need(matrix == toeplitz([row[0] for row in matrix]), "lower Toeplitz descendant")
        if n == 1:
            return
        evens, odds = list(range(0, n, 2)), list(range(1, n, 2))
        E, O = block(matrix, evens, evens), block(matrix, odds, evens)
        upper = block(matrix, evens, odds)
        m = n//2
        shift = [[ONE if i == j+1 else ZERO for j in range(m)] for i in range(m)]
        K = times(O, inverse(E))
        need(upper == times(shift, O), "parity upper block is ZO")
        need(block(matrix, odds, odds) == E, "parity diagonal blocks agree")
        S = schur(matrix, evens, odds)
        need(S == minus(E, times(times(shift, O), K)), "source Schur coefficient formula")
        need(times(O, inverse(E)) == times(inverse(E), O), "Toeplitz commuting K")
        need(max(norms(O)) <= rho, "off-diagonal rho bound")
        bound = rho/(1-rho)
        need(max(norms(K)) <= bound and max(norms(times(shift, K))) <= bound, "local compensated shear bound")
        lower = [[ONE if i == j else (K[i-m][j] if i >= m and j < m else ZERO)
                  for j in range(2*m)] for i in range(2*m)]
        need(max(norms(lower)) <= 1+bound and max(norms(inverse(lower))) <= 1+bound,
             "completed shear and inverse bound")
        shear_checks += 1
        walk(E, rho)
        walk(S, rho)

    for n in (1, 2, 4, 8):
        for seed in (0, 1, 2):
            rho = Q(1, 2)
            raw = [z((i+seed) % 3-1, (2*i+seed) % 3-1) for i in range(n)]
            total = sum((mu(x) for x in raw), Q(0))
            factor = rho/total if total else Q(0)
            symbol = [add(ONE if i == 0 else ZERO, mul(z(factor), value))
                      for i, value in enumerate(raw)]
            matrix = toeplitz(symbol)
            walk(matrix, rho)
            roots.append({"n": n, "seed": seed, "source_component_defect": str(sum((mu(sub(value, ONE if i == 0 else ZERO)) for i, value in enumerate(symbol)), Q(0)))})
    return {"root_cases": len(roots), "recursive_nodes": nodes, "nonleaf_shear_checks": shear_checks,
            "roots": roots, "physical_compiler_executed": False}


def controls():
    rho = Q(1, 2)
    sharp = [[z(1-rho), ZERO, ZERO], [ZERO, z(1+rho), ZERO], [ZERO, ZERO, ONE]]
    result = schur(sharp, [2], [0, 1])
    need(max(norms(minus(result, identity(2)))) == rho, "rho constant is sharp")
    need(max(norms(result)) == 1+rho and max(norms(inverse(result))) == 1/(1-rho),
         "direct and inverse constants are sharp")
    # At rho=1 an admitted principal pivot may be singular.
    rejected = False
    try:
        schur([[ZERO, ZERO], [ZERO, ONE]], [0], [1])
    except ValueError as exc:
        rejected = "singular principal pivot" in str(exc)
    need(rejected, "rho<1 pivot margin control")
    # For rho>1 even an invertible principal pivot can exceed the bound.
    beyond = [[z(Q(1, 4)), z(Q(3, 4))], [z(Q(3, 4)), z(Q(1, 4))]]
    need(max(norms(minus(beyond, identity(2)))) == Q(3, 2), "beyond-one premise")
    bad = schur(beyond, [0], [1])
    need(max(norms(minus(bad, identity(1)))) == 3 > Q(3, 2), "beyond-one failure witness")
    # Row-only input bound does not imply a column conclusion.
    r = Q(3, 4)
    row_only = [[ONE, z(r), ZERO], [z(r), ONE, ZERO], [z(r), ZERO, ONE]]
    need(norms(minus(row_only, identity(3)))[1] == r, "row-only admission")
    row_descendant = schur(row_only, [0], [1, 2])
    need(norms(minus(row_descendant, identity(2)))[0] == Q(9, 8) > r,
         "column conclusion needs its own column hypothesis")
    # Nonprincipal restrictions and arbitrary similarity are not granted.
    need(block(identity(2), [0], [1]) == [[ZERO]], "nonprincipal identity block is zero")
    similarity = [[ZERO, z(2*r)], [ZERO, ZERO]]
    need(max(norms(similarity)) > r, "nonisometric basis may amplify defect")
    # A usual-modulus hypothesis cannot silently become a component one.
    phase = z(Q(3, 10), Q(3, 10))
    need(phase[0]**2+phase[1]**2 == Q(9, 50) < Q(1, 4), "usual modulus rho-half admission")
    component_boundary = [[add(ONE, phase), ZERO], [ZERO, ONE]]
    component_result = schur(component_boundary, [1], [0])
    need(mu(sub(component_result[0][0], ONE)) == Q(3, 5) > rho,
         "component conclusion requires component admission")
    return {"sharp_rho_defect": "1/2", "sharp_direct": "3/2", "sharp_inverse": "2",
            "rho_one_singular_pivot_rejected": True,
            "rho_three_halves_counterexample_defect": "3",
            "row_only_column_counterexample": "9/8 > 3/4",
            "modulus_only_component_boundary": "|z|^2=9/50<1/4 but mu(z)=3/5>1/2 for z=(3+3i)/10",
            "nonprincipal_and_nonisometric_extensions_rejected": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {"status": "PASS_EXACT_COMPONENT_SCHUR_CLOSURE_NO_NEW_KAPPA",
              "general_cases": general_census(), "parity_cases": parity_census(),
              "controls": controls(),
              "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "finite_scope": "Gaussian-rational component envelopes only; universal modulus/component theorem is written separately; no predecessor module imports or physical compiler execution"}
    if args.output is not None:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
