"""Check the new arithmetic and unchanged complete replay, not the floor proof."""

from contextlib import redirect_stdout
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations, product, permutations
import io
import json
from pathlib import Path
from random import Random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rational_rank
import replay
from rational_rank import require


def determinant(matrix):
    """Independent Leibniz determinant for orders at most three."""
    size = len(matrix)
    require(size <= 3, "minor oracle capacity")
    answer = Fraction(0)
    for order in permutations(range(size)):
        inversions = sum(order[i] > order[j] for i in range(size) for j in range(i + 1, size))
        term = Fraction((-1) ** inversions)
        for i in range(size):
            term *= matrix[i][order[i]]
        answer += term
    return answer


def minor_rank(matrix):
    height, width = len(matrix), len(matrix[0]) if matrix else 0
    require(max(height, width) <= 3, "small-minor oracle capacity")
    for size in range(min(height, width), 0, -1):
        for rows in combinations(range(height), size):
            for cols in combinations(range(width), size):
                if determinant([[matrix[i][j] for j in cols] for i in rows]):
                    return size
    return 0


def arithmetic_checks():
    count = 0
    alphabet = (Fraction(-1, 2), Fraction(0), Fraction(2, 3))
    shapes = ((0, 0), (2, 0), (1, 1), (1, 3), (3, 1), (2, 2), (2, 3), (3, 2))
    for height, width in shapes:
        for values in product(alphabet, repeat=height * width):
            matrix = [list(values[i * width:(i + 1) * width]) for i in range(height)]
            original = deepcopy(matrix)
            require(rational_rank.rank(matrix) == minor_rank(matrix), "independent minor rank")
            require(matrix == original, "arithmetic input was modified")
            count += 1
    rng = Random(2627)
    for _ in range(200):
        matrix = [[Fraction(rng.randrange(-9, 10), rng.randrange(1, 10)) for _ in range(3)]
                  for _ in range(3)]
        require(rational_rank.rank(matrix) == minor_rank(matrix), "rational 3-by-3 minor rank")
        count += 1
    return count


def rejection_checks():
    invalid = ([[1], [1, 2]], [[0.5]], [[True]], [[1 << 129]], [[0] * 97], [[0]] * 97)
    count = 0
    for matrix in invalid:
        try:
            rational_rank.rank(matrix)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid matrix accepted")
    try:
        rational_rank.primitive([1 << 4097])
    except ValueError:
        count += 1
    else:
        raise ValueError("integer row exhaustion accepted")
    return count


def capture_fixture():
    old, k_engine = replay.load()
    original = old.rank
    calls = dict.fromkeys(replay.EXPECTED_CALLS, 0)
    matrices, ranks = [], []

    def capture(matrix, field="K"):
        calls[field] += 1
        result = k_engine.rank(matrix) if field == "K" else original(matrix, field)
        if field == "Q":
            saved = deepcopy(matrix)
            require(rational_rank.rank(matrix) == result, "actual rational rank differs")
            require(saved == matrix, "actual input was modified")
            matrices.append(saved)
            ranks.append(result)
        return result

    old.rank = capture
    output = io.StringIO()
    with redirect_stdout(output):
        old.main()
    require(calls == replay.EXPECTED_CALLS, "complete actual-call census")
    return matrices, ranks, output.getvalue()


def fixture_digest(matrices, ranks):
    census = [[[[str(value) for value in row] for row in matrix], result]
              for matrix, result in zip(matrices, ranks)]
    raw = json.dumps(census, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()


def full_checks(expected):
    output = io.StringIO()
    with redirect_stdout(output):
        replay.execute()
    require(output.getvalue() == expected, "complete replay stdout differs")
    marker = "PASS_EISENSTEIN_REDUCTION_COPY_FLOOR: sharp abstract scalar cost 40"
    require(expected.endswith(marker + "\n"), "complete source marker missing")
    receipt = json.loads(expected[:expected.rfind(marker)])
    require(len(receipt["negative_controls"]) == 7, "original rejection controls missing")
    previous = replay.rank
    replay.rank = lambda matrix: 0
    try:
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                replay.execute()
        except ValueError:
            return 1
        raise ValueError("wrong rational-rank adapter survived the original checks")
    finally:
        replay.rank = previous


def main():
    arithmetic = arithmetic_checks()
    rejected = rejection_checks()
    matrices, ranks, expected = capture_fixture()
    mutations = full_checks(expected)
    report = {"arithmetic_cases": arithmetic, "invalid_input_controls": rejected,
              "wrong_adapter_controls": mutations, "rank_calls": replay.EXPECTED_CALLS,
              "Q_call_digest": fixture_digest(matrices, ranks),
              "complete_stdout_sha256": hashlib.sha256(expected.encode()).hexdigest(),
              "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(HERE.iterdir()) if p.is_file()}}
    print(json.dumps(report, indent=2, sort_keys=True))
    print("PASS_EISENSTEIN_RATIONAL_RANK")


if __name__ == "__main__":
    main()
