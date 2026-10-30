"""Independent finite corroboration of the written all-pair theorem."""

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

from optimize import Completion, optimal_completions, power_two


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def determinant(matrix: tuple) -> F:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def gram(matrix: tuple) -> tuple:
    return tuple(tuple(sum(matrix[k][i] * matrix[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def unit(value: F) -> bool:
    numerator = abs(value.numerator)
    denominator = value.denominator
    return (numerator > 0 and numerator & (numerator - 1) == 0
            and denominator & (denominator - 1) == 0)


def inspect_completion(a: tuple, b: tuple, item: Completion) -> F:
    matrix = item.matrix
    det = determinant(matrix)
    require(unit(det), "nonunit completion determinant")
    require(abs(det) == power_two(item.exponent), "wrong determinant exponent")
    require(tuple(matrix[i][0] for i in range(2)) == b, "wrong first column")
    require(tuple(sum(a[i] * matrix[i][j] for i in range(2))
                  for j in range(2)) == (1, 0), "wrong prescribed row")
    inverse = ((matrix[1][1] / det, -matrix[0][1] / det),
               (-matrix[1][0] / det, matrix[0][0] / det))
    require(inverse[0] == a, "wrong inverse row")
    for i, j in itertools.product(range(2), repeat=2):
        product = sum(matrix[i][k] * inverse[k][j] for k in range(2))
        require(product == int(i == j), "inverse product")
    gg = gram(matrix)
    require(determinant(gg) == det * det, "Gram determinant")
    q = (gg[0][0] + gg[1][1]) / abs(det)
    require(q == item.q and q >= 2, "wrong spectral proxy")
    return q


def integer_pairs(bound: int) -> tuple:
    require(bound in (2, 5), "unsupported census bound")
    pairs = []
    for values in itertools.product(range(-bound, bound + 1), repeat=4):
        a, b = values[:2], values[2:]
        if sum(a[i] * b[i] for i in range(2)) == 1:
            pairs.append((tuple(map(F, a)), tuple(map(F, b))))
    return tuple(pairs)


def exhaustive_exponents(a: tuple, b: tuple, exponents: range) -> tuple:
    scores = []
    for k in exponents:
        t = F(2) ** k
        matrix = ((b[0], -t * a[1]), (b[1], t * a[0]))
        gg = gram(matrix)
        scores.append(((gg[0][0] + gg[1][1]) / abs(determinant(matrix)), k))
    minimum = min(q for q, _ in scores)
    return tuple(k for q, k in scores if q == minimum)


def check_pairs() -> dict:
    counts = {"integer_dual_pairs": 0, "scaled_pairs": 0,
              "exponent_matrices": 0, "optimal_representatives": 0,
              "tied_pairs": 0}
    pairs = integer_pairs(5)
    counts["integer_dual_pairs"] = len(pairs)
    for original_a, original_b in pairs:
        for scale in range(-3, 4):
            a = tuple(x * F(2) ** scale for x in original_a)
            b = tuple(x / F(2) ** scale for x in original_b)
            result = optimal_completions(a, b)
            oracle = exhaustive_exponents(a, b, range(-16, 17))
            require(tuple(item.exponent for item in result) == oracle,
                    "exhaustive determinant comparison")
            aa, bb = sum(x*x for x in a), sum(x*x for x in b)
            for item in result:
                inspect_completion(a, b, item)
                require(F(2)**(2*item.exponent-1) <= bb/aa
                        <= F(2)**(2*item.exponent+1), "global optimality window")
                opposite = tuple((row[0], -row[1]) for row in item.matrix)
                inspect_completion(a, b, Completion(item.exponent, item.q, opposite))
            counts["scaled_pairs"] += 1
            counts["exponent_matrices"] += 33
            counts["optimal_representatives"] += 2 * len(result)
            counts["tied_pairs"] += int(len(result) == 2)
    return counts


def check_grid() -> dict:
    pairs = integer_pairs(2)
    columns = tuple(itertools.product((F(i, 4) for i in range(-16, 17)), repeat=2))
    examined, compatible = 0, 0
    for a, b in pairs:
        scores = []
        for z in columns:
            examined += 1
            matrix = ((b[0], z[0]), (b[1], z[1]))
            det = determinant(matrix)
            if sum(a[i] * z[i] for i in range(2)) != 0 or not unit(det):
                continue
            compatible += 1
            gg = gram(matrix)
            scores.append((gg[0][0] + gg[1][1]) / abs(det))
        require(scores, "empty direct column oracle")
        expected = optimal_completions(a, b)
        require(min(scores) == expected[0].q, "direct second-column minimum")
        for item in expected:
            require(tuple(row[1] for row in item.matrix) in columns,
                    "optimal column absent from oracle grid")
    return {"grid_pairs": len(pairs), "grid_matrices": examined,
            "compatible_grid_matrices": compatible}


def check_fixtures() -> dict:
    a, b = (F(3), F(5)), (F(2), F(-1))
    result = optimal_completions(a, b)
    require(len(result) == 1, "source optimum multiplicity")
    item = result[0]
    require((item.exponent, item.q) == (-1, 27), "source optimum")
    require(item.matrix == ((2, F(-5, 2)), (-1, F(3, 2))), "source matrix")
    require(gram(item.matrix) == ((5, F(-13, 2)), (F(-13, 2), F(17, 2))),
            "literal source Gram")
    require(27*27 > 4*170 and 27 < 39, "strict arithmetic and baseline gaps")
    tie = optimal_completions((1, 0), (1, 1))
    require(tuple(x.exponent for x in tie) == (0, 1), "exact tie")
    require(all(x.q == 3 for x in tie), "tie proxy")
    extremes = (((2**63, 1), (0, 1)), ((0, 1), (2**63, 1)),
                ((F(1, 2**64), 1), (0, 1)), ((1, 0), (1, F(1, 2**64))))
    for row, column in extremes:
        aa, bb = tuple(map(F, row)), tuple(map(F, column))
        found = optimal_completions(aa, bb)
        require(tuple(x.exponent for x in found)
                == exhaustive_exponents(aa, bb, range(-130, 131)), "size boundary")
        for candidate in found:
            inspect_completion(aa, bb, candidate)
    return {"source_q": 27, "cited_completion_q": 39,
            "tie_exponents": [0, 1], "size_boundary_pairs": len(extremes)}


def check_controls() -> int:
    invalid = (((1,), (1, 0)), ((0, 0), (0, 0)), ((1, 0), (0, 1)),
               ((F(1, 3), 1), (0, 1)), ((1, 0), (1, F(1, 3))),
               ((2**64, 1), (0, 1)), ((1, 0), (1, F(1, 2**65))),
               ((True, 0), (1, 0)), ((1.0, 0), (1, 0)), (None, (1, 0)))
    count = 0
    for a, b in invalid:
        try:
            optimal_completions(a, b)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid dual pair accepted")
    a, b = (F(3), F(5)), (F(2), F(-1))
    corrupt = (Completion(-1, F(26), ((2, F(-5, 2)), (-1, F(3, 2)))),
               Completion(0, F(27), ((2, F(-5, 2)), (-1, F(3, 2)))),
               Completion(0, F(39), ((2, 5), (1, -3))),
               Completion(0, F(1), ((2, -15), (-1, 9))))
    for item in corrupt:
        try:
            inspect_completion(a, b, item)
        except ValueError:
            count += 1
        else:
            raise ValueError("corrupted completion accepted")
    return count


def main() -> None:
    counts = check_pairs() | check_grid() | check_fixtures()
    counts["rejected_controls"] = check_controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "optimize.py", "verify.py")
    hashes = {}
    for name in names:
        require((package / name).stat().st_size <= 262144, "source file too large")
        data = (package / name).read_bytes()
        require(len(data) <= 262144, "package source exceeds hash bound")
        hashes[name] = hashlib.sha256(data).hexdigest()
    print(json.dumps({"counts": counts, "sha256": hashes}, sort_keys=True))
    print("PASS_DYADIC_BASIS_CONDITIONING")


if __name__ == "__main__":
    main()
