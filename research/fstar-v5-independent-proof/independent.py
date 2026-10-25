#!/usr/bin/env python3
"""Independent target-first linear-algebra check of the raw-mask certificate.

No predecessor executable or primary checker is imported.  Each ordered triple
is tested by enumerating its target labels and solving three independent binary
linear systems for the source labels.  Forbidden triples are then extended by
backtracking, rather than scanning all five-line multisets.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW_TYPES = tuple((a, b) for a in range(8) for b in range(8) if a & b)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def authenticate() -> None:
    """Authenticate declared source inputs without executing any of them."""
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    entries = manifest["files"]
    require(isinstance(entries, list) and bool(entries), "empty source manifest")
    seen = set()
    for entry in entries:
        name = entry["path"]
        require(name not in seen, "duplicate source input")
        seen.add(name)
        if entry["usage"] != "input":
            continue
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        require(digest == entry["sha256"], "source digest mismatch: " + name)
    frozen = manifest["frozen_sources"]
    require(isinstance(frozen, list) and bool(frozen), "empty frozen source manifest")
    frozen_paths = set()
    for entry in frozen:
        name = entry["path"]
        require(name not in frozen_paths, "duplicate frozen source")
        frozen_paths.add(name)
        digest = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        require(digest == entry["sha256"], "frozen source digest mismatch: " + name)


def submasks(mask: int) -> tuple[int, ...]:
    return tuple(x for x in range(1, 8) if x & ~mask == 0)


@lru_cache(maxsize=None)
def row_consistent(allowed: int, equations: tuple[tuple[int, int], ...]) -> bool:
    """Decide A·coefficient=rhs with A supported inside ``allowed`` over F2."""
    pivots = [0, 0, 0]
    for coefficient, rhs in equations:
        row = (coefficient & allowed) | (rhs << 3)
        for column in (2, 1, 0):
            if not row & (1 << column):
                continue
            if pivots[column]:
                row ^= pivots[column]
            else:
                pivots[column] = row
                break
        else:
            if row & 8:
                return False
    return True


def ordered_feasible(types: tuple[tuple[int, int], ...]) -> bool:
    """Exactly test all three kept lines in this fixed order and even envelope."""
    require(len(types) == 3, "ordered oracle requires exactly three lines")
    # A target mask must permit its own diagonal equation.  The source row is
    # solved below, so no preferred singleton or diagonal pair is assumed.
    choices = [tuple(b for b in submasks(b0) if a0 & b) for a0, b0 in types]
    constrained = [tuple(j for j in range(i + 1, 3)
                         if (types[i][0] & types[j][1]).bit_count() % 2 == 0)
                   for i in range(3)]
    for targets in itertools.product(*choices):
        works = True
        for i in range(3):
            equations = ((targets[i], 1),) + tuple((targets[j], 0)
                                                  for j in constrained[i])
            if not row_consistent(types[i][0], equations):
                works = False
                break
        if works:
            return True
    return False


def triple_feasible(indices: tuple[int, int, int]) -> bool:
    """Test every order; indices retain the shared three total coordinates."""
    return any(ordered_feasible(tuple(RAW_TYPES[i] for i in order))
               for order in sorted(set(itertools.permutations(indices))))


def coherent_families(size: int) -> set[tuple[int, ...]]:
    """The proposed complete description, independent of oracle output."""
    families = set()
    for tied in (3, 5, 6):
        ordinary = RAW_TYPES.index((tied, tied))
        for special_type in ((tied, 7), (7, tied)):
            special = RAW_TYPES.index(special_type)
            for multiplicity in range(size + 1):
                family = (ordinary,) * (size - multiplicity) + (special,) * multiplicity
                families.add(tuple(sorted(family)))
    return families


def extend_forbidden(forbidden: set[tuple[int, int, int]], size: int) -> list[tuple[int, ...]]:
    """Extend only prefixes whose every positional triple is forbidden."""
    result = []

    def visit(prefix: tuple[int, ...], lower: int) -> None:
        if len(prefix) == size:
            result.append(prefix)
            return
        for value in range(lower, len(RAW_TYPES)):
            if all((prefix[i], prefix[j], value) in forbidden
                   for i, j in itertools.combinations(range(len(prefix)), 2)):
                visit(prefix + (value,), value)

    visit((), 0)
    return result


def build() -> dict:
    authenticate()
    triples = tuple(itertools.combinations_with_replacement(range(len(RAW_TYPES)), 3))
    require(len(triples) == math.comb(39, 3), "incomplete triple universe")
    forbidden = {triple for triple in triples if not triple_feasible(triple)}
    require(forbidden == coherent_families(3), "forbidden triples differ from formula")
    families = extend_forbidden(forbidden, 5)
    require(len(families) == len(set(families)), "duplicate backtracking result")
    expected = coherent_families(5)
    require(set(families) == expected, "five-line classification differs from formula")
    return {
        "raw_type_count": len(RAW_TYPES),
        "triple_count": len(triples),
        "forbidden_triples": [list(t) for t in sorted(forbidden)],
        "family_count": len(families),
        "families": [list(t) for t in sorted(families)],
        "exact_formula_match": set(families) == expected,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the independently derived receipt")
    args = parser.parse_args()
    actual = build()
    if args.emit:
        print(json.dumps(actual, sort_keys=True, indent=2))
        return
    retained = json.loads((HERE / "RESULT.json").read_text())
    for key, value in actual.items():
        require(retained.get(key) == value, "independent receipt mismatch: " + key)
    print("PASS independent target-first systems: 9139 triples, 21 forbidden, 33 five-line families")


if __name__ == "__main__":
    main()
