"""Independent finite evidence for the new extraction algorithm, not PR2330 replay."""

import hashlib
import importlib.util
import itertools
import json
from dataclasses import replace
from pathlib import Path
import sys
import time


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("split_solver", PACKAGE / "solver.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load package solver")
solver = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = solver
SPEC.loader.exec_module(solver)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def subsets(width: int):
    return (tuple(i for i in range(width) if mask & (1 << i)) for mask in range(1 << width))


def determinant(block, rows, columns) -> int:
    """Literal Leibniz formula over F2, independent of elimination."""
    value = 0
    for permutation in itertools.permutations(columns):
        term = 1
        for row, column in zip(rows, permutation):
            term &= (block[row] >> column) & 1
        value ^= term
    return value


def minor_rank(block, rows, columns) -> int:
    for size in range(min(len(rows), len(columns)), 0, -1):
        for chosen_rows in itertools.combinations(rows, size):
            for chosen_columns in itertools.combinations(columns, size):
                if determinant(block, chosen_rows, chosen_columns):
                    return size
    return 0


def independent_small_check(blocks, certificate) -> int:
    width = len(blocks[0])
    row_list = [i for group in certificate.rows for i in group]
    col_list = [i for group in certificate.columns for i in group]
    check(len(row_list) == len(set(row_list)), "literal row reuse")
    check(len(col_list) == len(set(col_list)), "literal column reuse")
    for block, rows, columns in zip(blocks, certificate.rows, certificate.columns):
        check(len(rows) == len(columns) and determinant(block, rows, columns) == 1,
              "literal determinant certificate")
    returned_cut = 2 * width - len(certificate.cut_rows) - len(certificate.cut_columns)
    returned_cut += sum(minor_rank(block, certificate.cut_rows, certificate.cut_columns)
                        for block in blocks)
    check(returned_cut == len(row_list), "literal returned cut certificate")
    best = 2 * width
    for rows in subsets(width):
        for columns in subsets(width):
            value = 2 * width - len(rows) - len(columns)
            value += sum(minor_rank(block, rows, columns) for block in blocks)
            best = min(best, value)
    check(best == len(row_list), "exhaustive cut optimum")
    return best


def dense_rank(matrix) -> int:
    """Dense row operations, separate from the solver's bit-vector rank."""
    work = [list(row) for row in matrix]
    width = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(width):
        pivot = next((i for i in range(pivot_row, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        for row in range(len(work)):
            if row != pivot_row and work[row][column]:
                work[row] = [a ^ b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
    return pivot_row


def independent_large_check(blocks, certificate) -> int:
    width = len(blocks[0])
    all_rows = [i for group in certificate.rows for i in group]
    all_cols = [i for group in certificate.columns for i in group]
    check(len(all_rows) == len(set(all_rows)), "dense row reuse")
    check(len(all_cols) == len(set(all_cols)), "dense column reuse")
    for block, rows, columns in zip(blocks, certificate.rows, certificate.columns):
        matrix = [[(block[i] >> j) & 1 for j in columns] for i in rows]
        check(len(rows) == len(columns) == dense_rank(matrix), "dense minor rank")
    cut = 2 * width - len(certificate.cut_rows) - len(certificate.cut_columns)
    for block in blocks:
        matrix = [[(block[i] >> j) & 1 for j in certificate.cut_columns]
                  for i in certificate.cut_rows]
        cut += dense_rank(matrix)
    check(cut == len(all_rows), "dense primal/cut gap")
    return cut


def exhaustive_cases() -> dict:
    counts = {}
    histogram = [0, 0, 0]
    for colors in (1, 2, 3):
        count = 0
        for encoding in range(1 << (4 * colors)):
            blocks = tuple(tuple((encoding >> (4 * c + 2 * i)) & 3 for i in range(2))
                           for c in range(colors))
            certificate = solver.solve(blocks)
            value = independent_small_check(blocks, certificate)
            if colors == 3:
                histogram[value] += 1
            count += 1
        counts[str(colors)] = count
    return {"width_two_cases_by_colors": counts, "three_color_optimum_histogram": histogram}


def larger_cases() -> list:
    records = []
    for width in (3, 4, 6, 8, 12):
        for index in range(6):
            blocks = []
            for color in range(3):
                rows = []
                for row in range(width):
                    payload = f"binary-split:{width}:{index}:{color}:{row}".encode()
                    rows.append(int.from_bytes(hashlib.sha256(payload).digest(), "big")
                                & ((1 << width) - 1))
                blocks.append(tuple(rows))
            blocks = tuple(blocks)
            certificate = solver.solve(blocks)
            optimum = independent_large_check(blocks, certificate)
            if width == 3:
                check(independent_small_check(blocks, certificate) == optimum, "sampled cuts")
            records.append({"width": width, "index": index, "optimum": optimum})
    return records


def fixtures() -> list:
    records = []
    for width in (8, 16, 32):
        identity = tuple(1 << i for i in range(width))
        constant = tuple((1 << width) - 1 for _ in range(width))
        zero = tuple(0 for _ in range(width))
        for name, blocks, expected in (
                ("perfect", (identity, zero), width),
                ("constant_rank_two", (constant, constant), 2),
                ("zero", (zero, zero), 0)):
            certificate = solver.solve(blocks)
            optimum = independent_large_check(blocks, certificate)
            check(optimum == expected, "explicit large fixture")
            records.append({"name": name, "width": width, "optimum": optimum,
                            "certificate": certificate.__dict__})
    exchange = ((3, 3), (1, 0))
    check(independent_small_check(exchange, solver.solve(exchange)) == 2,
          "greedy-trap fixture")
    return records


def rejection_controls() -> int:
    cases = [(), ((0,),) * 9, ((),), ((4, 0),), ((True,),), ((-1,),),
             ((1, 0), (0,)), ([1],), ((0,) * 33,), ((0,) * 13,) * 8]
    count = 0
    for blocks in cases:
        try:
            solver.solve(blocks)
        except ValueError:
            count += 1
        else:
            raise RuntimeError("accepted invalid input")
    blocks = ((1, 2), (0, 0))
    good = solver.solve(blocks)
    wrong = [replace(good, rows=((0, 0), ())),
             replace(good, columns=((0, 0), ())),
             replace(good, rows=((0,), (0,)), columns=((0,), (0,))),
             replace(good, rows=((0,), ()), columns=((1,), ())),
             replace(good, cut_rows=(2,)), replace(good, cut_rows=(0, 0)),
             replace(good, cut_columns=(-1,)), replace(good, rows=()),
             replace(good, cut_rows=(), cut_columns=()),
             replace(good, rows=((0,), ()), columns=((0,), ()))]
    for certificate in wrong:
        try:
            solver.certify(blocks, certificate)
        except ValueError:
            count += 1
        else:
            raise RuntimeError("accepted invalid certificate")
    return count


def main() -> None:
    check(len(sys.argv) <= 2, "expected at most one phase argument")
    phase = sys.argv[1] if len(sys.argv) == 2 else "all"
    check(phase in ("all", "exhaustive", "sampled", "fixtures"), "unknown phase")
    result = {"claim_type": "constructive scoped algorithm with finite certificates",
              "phase": phase}
    for name, action in (("exhaustive", exhaustive_cases), ("sampled", larger_cases),
                         ("fixtures", fixtures)):
        if phase in ("all", name):
            start = time.perf_counter()
            result[name] = action()
            print(f"{name}: {time.perf_counter() - start:.3f}s", file=sys.stderr, flush=True)
    result["rejection_controls"] = rejection_controls()
    hashes = {}
    for path in sorted(PACKAGE.iterdir()):
        if path.is_file():
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result["package_sha256"] = hashes
    result["status"] = "PASS_POLYNOMIAL_DECODER_SPLIT"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
