"""New inverse conformance, exact read accounting, and domain controls."""
from fractions import Fraction as Q
from itertools import product
from physical import fixture, require, run_case


def saved_reads(matrix):
    """A separate rational trace counts nonzero elimination factors."""
    n = len(matrix)
    a = [[Q(v) for v in row] + [Q(int(i == j)) for j in range(n)]
         for i, row in enumerate(matrix)]
    savings = 0
    for k in range(n):
        pivot = a[k][k]
        require(pivot > 0, "positive trace pivot")
        a[k] = [v / pivot for v in a[k]]
        factors = [a[i][k] for i in range(n) if i != k]
        savings += k * (1 + sum(v != 0 for v in factors))
        for i in range(n):
            if i == k:
                continue
            factor = a[i][k]
            a[i] = [x - factor * y for x, y in zip(a[i], a[k])]
        require(all(a[i][j] == int(i == j) for i in range(n) for j in range(k + 1)),
                "completed identity-column invariant")
    return savings, [row[n:] for row in a]


def host_corroboration():
    cases = 0
    for entries in product(range(-1, 2), repeat=4):
        matrix = [[Q(4 + entries[0]), Q(entries[1])],
                  [Q(entries[2]), Q(4 + entries[3])]]
        savings, inverse = saved_reads(matrix)
        require(savings in (1, 2), "two-row exact savings range")
        identity(matrix, inverse)
        cases += 1
    return cases


def identity(matrix, inverse):
    n = len(matrix)
    require(len(inverse) == n and all(len(row) == n for row in inverse), "full output shape")
    for i in range(n):
        for j in range(n):
            require(sum(matrix[i][k] * inverse[k][j] for k in range(n)) == int(i == j),
                    "literal right inverse identity")
            require(sum(inverse[i][k] * matrix[k][j] for k in range(n)) == int(i == j),
                    "literal left inverse identity")


def physical_corroboration():
    matrices = [[[Q(int(i == j)) for j in range(n)] for i in range(n)] for n in range(1, 5)]
    matrices += [fixture(name) for name in ("dense3", "dense4", "rational3")]
    matrices += [[[Q(1, 3), Q(0)], [Q(0), Q(7, 5)]],
                 [[Q(1), Q(0), Q(0)], [Q(-2), Q(1), Q(0)], [Q(3), Q(4), Q(1)]],
                 [[Q(2), Q(3)], [Q(1), Q(2)]]]
    evidence = []
    for matrix in matrices:
        baseline = run_case("baseline", matrix, True)
        candidate = run_case("candidate", matrix, True)
        savings, expected = saved_reads(matrix)
        require(baseline["output"] == candidate["output"], "complete physical output equality")
        actual = [[Q(v) for v in row] for row in candidate["output"]]
        require(actual == expected, "independent rational output")
        identity(matrix, actual)
        require(baseline["counts"]["get"] - candidate["counts"]["get"] == savings,
                "exact matrix-read savings")
        require(baseline["counts"]["set"] == candidate["counts"]["set"], "same matrix writes")
        if matrix == fixture("dense4"):
            require(all(candidate["counts"]["pooled_tape"][key] < baseline["counts"]["pooled_tape"][key]
                        for key in ("reads", "writes", "moves")), "paid pooled-tape improvement")
            require(candidate["counts"]["pool_peak"] == baseline["counts"]["pool_peak"] + 2,
                    "two extra peak scratch leases are charged")
        evidence.append({"matrix": [[str(v) for v in row] for row in matrix],
                         "baseline": baseline, "candidate": candidate, "saved_reads": savings})
    return evidence


def rejecting_controls():
    cases = [([[Q(0)]], "positive exact setup pivot"),
             ([[Q(-1)]], "positive exact setup pivot"),
             ([[Q(1), Q(1)], [Q(1), Q(1)]], "positive exact setup pivot"),
             ([[Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)]], "square exact inverse")]
    for matrix, message in cases:
        for engine in ("baseline", "candidate"):
            try:
                run_case(engine, matrix)
            except ValueError as error:
                require(str(error) == message, "same boundary rejection and cleanup")
            else:
                raise ValueError("missing physical inverse rejection")
    return 2 * len(cases)


def run():
    physical = physical_corroboration()
    return {"physical_fixtures": physical, "host_matrices": host_corroboration(),
            "domain_rejections": rejecting_controls(), "status": "PASS_GAUSSIAN_INVERSE_SETTLED_COLUMNS"}
