"""Independent bounded checks for the compressed theta constructor."""

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from constructor import EDGES, compile_templates, construct, covers, need, validate


def authenticate_sources() -> int:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    count = 0
    for row in manifest["files"]:
        if row["usage"] == "input":
            payload = (ROOT / row["path"]).read_bytes()
            need(hashlib.sha256(payload).hexdigest() == row["sha256"], "source drift")
            count += 1
    need(count == 2, "source inventory")
    return count


def copy_matching_table() -> dict:
    """Independent one-copy deletion recurrence on all widths in {0,1,2}^7."""
    table = {}
    for widths in sorted(product(range(3), repeat=7), key=sum):
        if not any(widths):
            table[widths] = 0
            continue
        vertex = next(i for i in range(7) if widths[i])
        remainder = list(widths)
        remainder[vertex] -= 1
        best = table[tuple(remainder)]
        for u, v in EDGES:
            if vertex not in (u, v):
                continue
            neighbor = v if vertex == u else u
            if remainder[neighbor]:
                paired = remainder.copy()
                paired[neighbor] -= 1
                best = max(best, 1 + table[tuple(paired)])
        table[widths] = best
    return table


def matrix_for(widths: tuple, certificate: dict) -> list:
    offsets = [sum(widths[:i]) for i in range(7)]
    used = [0] * 7
    n = sum(widths)
    need(n <= 14, "bounded matrix fixture")
    matrix = [[int(i == j) for j in range(n)] for i in range(n)]
    for edge, (u, v) in enumerate(EDGES):
        for _ in range(certificate["shared"][edge]):
            a, b = offsets[u] + used[u], offsets[v] + used[v]
            matrix[a][b] = matrix[b][a] = 1
            used[u] += 1
            used[v] += 1
    for i in range(7):
        need(used[i] + certificate["private"][i] == widths[i], "matrix coverage")
    return matrix


def rank_mod(matrix: list, prime: int) -> int:
    n = len(matrix)
    work = [[x % prime for x in row] for row in matrix]
    rank = 0
    for column in range(n):
        pivot = next((i for i in range(rank, n) if work[i][column]), None)
        if pivot is None:
            continue
        work[pivot], work[rank] = work[rank], work[pivot]
        scale = pow(work[rank][column], -1, prime)
        work[rank] = [x * scale % prime for x in work[rank]]
        for i in range(rank + 1, n):
            scale = work[i][column]
            work[i] = [(x - scale * y) % prime for x, y in zip(work[i], work[rank])]
        rank += 1
    return rank


def fitting_entries(widths: tuple, matrix: list) -> int:
    labels = tuple(i for i in range(7) for _ in range(widths[i]))
    edges = {frozenset(edge) for edge in EDGES}
    count = 0
    for i, u in enumerate(labels):
        for j, v in enumerate(labels):
            if i == j:
                need(matrix[i][j] == 1, "missing diagonal")
            elif u == v or frozenset((u, v)) not in edges:
                need(matrix[i][j] == 0, "forbidden ordered entry")
            count += 1
    return count


def check_small(templates: tuple) -> dict:
    table = copy_matching_table()
    digest = hashlib.sha256()
    matrix_count = entry_count = fractional_count = 0
    for widths, optimum in table.items():
        certificate = construct(widths, templates)
        need(sum(certificate["shared"]) == optimum, "copy-matching disagreement")
        dual_cost = sum(a * b for a, b in zip(widths, certificate["dual"]))
        fractional_count += dual_cost % 2
        digest.update(json.dumps([widths, certificate], sort_keys=True).encode())
        if max(widths) <= 1 or widths in ((2,) * 7, (2, 1, 2, 1, 2, 1, 2)):
            matrix = matrix_for(widths, certificate)
            entry_count += fitting_entries(widths, matrix)
            for prime in (2, 3, 101):
                need(rank_mod(matrix, prime) == certificate["rank"], "attaining rank")
                matrix_count += 1
    return {"width_vectors": len(table), "matrix_ranks": matrix_count,
            "fitting_entries": entry_count, "half_integer_optima": fractional_count,
            "recipe_sha256": digest.hexdigest()}


def check_large(templates: tuple) -> dict:
    fixtures = []
    for bits in (64, 257, 4096):
        n = 1 << bits
        fixtures.extend(((n,) * 7, (n + 1,) * 7,
                         (n, 1, n + 3, 0, 5 * n, 7, 2 * n + 1)))
    ranks = []
    largest = 0
    for widths in fixtures:
        certificate = construct(widths, templates)
        validate(widths, certificate)
        largest = max(largest, max(widths).bit_length())
        if len(set(widths)) == 1:
            need(certificate["rank"] == (sum(widths) + 1) // 2, "uniform large rank")
        ranks.append(certificate["rank"].bit_length())
    return {"large_fixtures": len(fixtures), "largest_width_bits": largest,
            "rank_bit_lengths": ranks}


def rejects(function, *arguments) -> None:
    try:
        function(*arguments)
    except ValueError:
        return
    raise ValueError("negative control accepted")


def check_controls(templates: tuple) -> int:
    controls = 0
    for widths in ((1,) * 6, (-1,) + (1,) * 6, (True,) + (1,) * 6,
                   (1.0,) + (1,) * 6, [1] * 7):
        rejects(construct, widths, templates)
        controls += 1
    widths = (1,) * 7
    certificate = construct(widths, templates)
    changes = (("private", (2,) * 7), ("shared", (1,) * 8),
               ("dual", (0,) * 7), ("dual", (True,) * 7),
               ("rank", certificate["rank"] + 1), ("rank", True))
    for key, value in changes:
        damaged = dict(certificate)
        damaged[key] = value
        rejects(validate, widths, damaged)
        controls += 1
    damaged = dict(certificate)
    damaged.update(shared=(0,) * 8, private=widths, rank=7)
    rejects(validate, widths, damaged)
    rejects(validate, widths, {})
    rejects(construct, widths, ())
    return controls + 3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    sources = authenticate_sources()
    templates = compile_templates()
    need(len(templates) == 1583 and len(covers()) == 267, "fixed enumeration inventory")
    result = {"sources": sources, "templates": len(templates), "covers": len(covers())}
    result.update(check_small(templates))
    result.update(check_large(templates))
    result["rejection_controls"] = check_controls(templates)
    result["file_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt:
        destination = args.receipt.resolve()
        need(not destination.is_relative_to(ROOT), "receipt must be outside checkout")
        destination.write_text(payload)
    print(payload, end="")
    print("PASS_THETA_COMPRESSED_CONSTRUCTOR")


if __name__ == "__main__":
    main()
