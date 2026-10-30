"""Exact finite checks of the new four-subset side spectrum; stdlib only."""

from hashlib import sha256
from itertools import combinations
import json
from math import comb, prod
from pathlib import Path
import platform


MAX_PORTS = 126


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def bareiss(matrix: list[list[int]]) -> tuple[int, int]:
    """Return exact rank and determinant by fraction-free elimination."""
    size = len(matrix)
    require(0 < size <= MAX_PORTS, "matrix size outside finite replay")
    require(all(len(row) == size for row in matrix), "nonsquare matrix")
    work = [row[:] for row in matrix]
    previous, rank, sign = 1, 0, 1
    for column in range(size):
        pivot_row = next(
            (row for row in range(rank, size) if work[row][column]), None
        )
        if pivot_row is None:
            continue
        if pivot_row != rank:
            work[rank], work[pivot_row] = work[pivot_row], work[rank]
            sign = -sign
        pivot = work[rank][column]
        for row in range(rank + 1, size):
            factor = work[row][column]
            for target in range(column + 1, size):
                numerator = pivot * work[row][target] - factor * work[rank][target]
                quotient, remainder = divmod(numerator, previous)
                require(remainder == 0, "nonexact Bareiss division")
                work[row][target] = quotient
            work[row][column] = 0
        previous = pivot
        rank += 1
        if rank == size:
            break
    determinant = sign * previous if rank == size else 0
    return rank, determinant


def shifted(matrix: list[list[int]], scalar: int) -> list[list[int]]:
    return [
        [value - (scalar if row == column else 0)
         for column, value in enumerate(values)]
        for row, values in enumerate(matrix)
    ]


def spectrum(n: int) -> dict[int, int]:
    """Eigenvalues of 8K with their claimed multiplicities."""
    require(5 <= n <= 1001 and n % 2 == 1, "finite odd formula domain required")
    if n == 5:
        return {20: 1, 5: 4}
    a, remainder_a = divmod(2 * (n - 2) * (n - 3) * (10 - n), 3)
    b, remainder_b = divmod((n - 3) * (n - 4) * (20 - n), 6)
    require(remainder_a == remainder_b == 0, "nonintegral scaled eigenvalue")
    rows = [(a, 1), (b, n - 1), ((n - 4) * (n - 5), comb(n, 2) - n),
            (0, comb(n, 4) - comb(n, 2))]
    result: dict[int, int] = {}
    for eigenvalue, multiplicity in rows:
        result[eigenvalue] = result.get(eigenvalue, 0) + multiplicity
    return result


def check_dense(n: int) -> dict[str, object]:
    require(n in (5, 7, 9), "finite dense domain required")
    ports = [frozenset(port) for port in combinations(range(n), 4)]
    size = len(ports)
    require(size <= MAX_PORTS, "port bound exceeded")
    # Literal t(t-2), independently of incidence-space spectral formulas.
    matrix = [[len(s & t) * (len(s & t) - 2) for t in ports] for s in ports]
    expected = spectrum(n)
    require(sum(expected.values()) == size, "wrong total multiplicity")
    for eigenvalue, multiplicity in expected.items():
        rank, _ = bareiss(shifted(matrix, eigenvalue))
        require(size - rank == multiplicity, "wrong dense eigenspace dimension")
    rank, determinant = bareiss(shifted(matrix, 8))
    predicted = prod((eigenvalue - 8) ** count
                     for eigenvalue, count in expected.items())
    require(rank == size, "side response is singular")
    require(determinant == predicted, "wrong side determinant")
    kernel_rank, _ = bareiss(matrix)
    require(kernel_rank == size - expected.get(0, 0), "wrong kernel rank")
    return {"n": n, "ports": size, "scaled_kernel_spectrum": expected,
            "kernel_rank": kernel_rank, "side_rank": rank,
            "det_8K_minus_8I": str(determinant),
            "dense_eigenspaces": len(expected), "literal_entries": size * size}


def check_incidence(n: int) -> int:
    require(n in (7, 9), "finite incidence domain required")
    pairs = [frozenset(pair) for pair in combinations(range(n), 2)]
    ports = [frozenset(port) for port in combinations(range(n), 4)]
    checked = 0
    for left in pairs:
        for right in pairs:
            literal = sum(left <= port and right <= port for port in ports)
            expected = ((n - 4) * (n - 5) // 2 if left == right else 0)
            expected += (n - 4) * len(left & right) + 1
            require(literal == expected, "wrong pair-incidence Gram identity")
            checked += 1
    return checked


def check_controls() -> int:
    # Wrong matrices retain the original spectrum as their rejection target.
    ports = [frozenset(port) for port in combinations(range(5), 4)]
    correct = [[len(s & t) * (len(s & t) - 2) for t in ports] for s in ports]
    mutants = [[row[:] for row in correct] for _ in range(3)]
    mutants[0][0][0] += 1
    mutants[1][0][1] *= -1
    mutants[2] = [[-len(s & t) for t in ports] for s in ports]
    rejected = 0
    for mutant in mutants:
        failed = False
        for eigenvalue, count in spectrum(5).items():
            rank, _ = bareiss(shifted(mutant, eigenvalue))
            failed = failed or len(mutant) - rank != count
        require(failed, "a false spectrum survived")
        rejected += 1
    # An actual smaller intermediate space has rank at most four, not five.
    compressed = [[1 if row == column and row < 4 else 0
                   for column in range(5)] for row in range(5)]
    rank, _ = bareiss(compressed)
    require(rank == 4, "compression control rank")
    return rejected + 1


def main() -> None:
    cases = [check_dense(n) for n in (5, 7, 9)]
    incidence_checks = sum(check_incidence(n) for n in (7, 9))
    formula_cases = 0
    for n in range(5, 1002, 2):
        expected = spectrum(n)
        require(8 not in expected, "eigenvalue one contradicts side theorem")
        require(sum(expected.values()) == comb(n, 4), "formula dimension")
        formula_cases += 1
    controls = check_controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    print(json.dumps({"status": "PASS_FOUR_SUBSET_SIDE_SPECTRUM",
                      "python": platform.python_version(), "cases": cases,
                      "incidence_gram_entries": incidence_checks,
                      "formula_cases": formula_cases, "controls": controls,
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
