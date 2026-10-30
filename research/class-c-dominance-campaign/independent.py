#!/usr/bin/env python3
"""Independent dimension-dominance and threshold audit for the Class-C tables.

This checker reads the two pinned CSV inputs directly. It does not import the
package's primary verifier or reproduce the underlying E8/P112 geometry.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any


PACKAGE = Path(__file__).resolve().parent
EXPECTED_HASHES = {
    "rows70.csv": "c0eb6bb88498bf39a8b2020b1d0d600181f6e13eb9dd6a6e5f90794f0895754a",
    "rows17.csv": "9ebe7fc1ecd74148e7bdefa1f6bb2ed00551884b1a4a6558d7f129f7eef4efd5",
}
EXPECTED_TABLE_COVERABLE = {"rows70.csv": 64, "rows17.csv": 16}
EXPECTED_HARD_T8_FAILURES = {7, 8, 13}


class CheckFailure(Exception):
    """A failed data, consistency, or expected-result check."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


@dataclass(frozen=True)
class Row:
    row_idx: int | str
    depth: int
    configs: tuple[str, ...]


def normalized_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def choose_column(headers: list[str], aliases: tuple[str, ...], pattern: str) -> str:
    by_normalized = {normalized_header(name): name for name in headers}
    for alias in aliases:
        if alias in by_normalized:
            return by_normalized[alias]
    candidates = [name for name in headers if re.search(pattern, normalized_header(name))]
    if len(candidates) == 1:
        return candidates[0]
    raise CheckFailure(
        "cannot identify CSV column; headers=" + repr(headers) + "; candidates=" + repr(candidates)
    )


def parse_row_id(value: str) -> int | str:
    cleaned = value.strip()
    if re.fullmatch(r"-?\d+", cleaned):
        return int(cleaned)
    if not cleaned:
        raise CheckFailure("empty row index in CSV")
    return cleaned


def row_id_sort_key(value: int | str) -> tuple[int, int | str]:
    if isinstance(value, int):
        return (0, value)
    return (1, value)


def parse_configs(value: str) -> tuple[str, ...]:
    text = value.strip()
    if not text or text.lower() in {"none", "null", "n/a", "-", "[]"}:
        return ()

    found = re.findall(r"(?<!\d)([1-7]{4})(?!\d)", text)
    if not found:
        separated = re.findall(
            r"(?<!\d)([1-7])\s*[,;:/]\s*([1-7])\s*[,;:/]\s*([1-7])\s*[,;:/]\s*([1-7])(?!\d)",
            text,
        )
        found = ["".join(parts) for parts in separated]
    if not found:
        raise CheckFailure("nonempty config cell has no four-dimension config: " + repr(text))
    return tuple(sorted(set(found)))


def read_rows(path: Path, raw: bytes) -> list[Row]:
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise CheckFailure(f"{path.name} is not UTF-8: {error}") from error
    reader = csv.DictReader(StringIO(content))
    headers = reader.fieldnames
    require(headers is not None and len(headers) > 0, f"{path.name} has no CSV header")

    id_column = choose_column(
        headers,
        ("row_idx", "row_id", "row", "id", "index"),
        r"(^|_)(row|idx|index|id)($|_)",
    )
    depth_column = choose_column(headers, ("d", "dimension_d", "d_value"), r"(^|_)d($|_)|dimension")
    config_column = choose_column(
        headers,
        ("configs", "covering_configs", "covering_4flat_configs", "configurations"),
        r"config",
    )

    rows: list[Row] = []
    for line_number, record in enumerate(reader, start=2):
        if not record or all(value is None or not value.strip() for value in record.values()):
            continue
        try:
            depth = int((record.get(depth_column) or "").strip())
        except ValueError as error:
            raise CheckFailure(f"{path.name}:{line_number}: invalid d value") from error
        rows.append(
            Row(
                row_idx=parse_row_id(record.get(id_column) or ""),
                depth=depth,
                configs=parse_configs(record.get(config_column) or ""),
            )
        )

    ids = [row.row_idx for row in rows]
    require(len(ids) == len(set(ids)), f"{path.name} contains duplicate row indices")
    return rows


def config_dimensions(config: str) -> tuple[int, ...]:
    require(bool(re.fullmatch(r"[1-7]{4}", config)), f"invalid config label {config!r}")
    return tuple(int(value) for value in config)


def injectively_dominates(larger: str, smaller: str) -> bool:
    """Test role matching by trying every injection of smaller roles into larger."""
    large_roles = config_dimensions(larger)
    small_roles = config_dimensions(smaller)
    if len(small_roles) > len(large_roles):
        return False
    for assigned_positions in itertools.permutations(range(len(large_roles)), len(small_roles)):
        if all(small_roles[index] <= large_roles[position] for index, position in enumerate(assigned_positions)):
            return True
    return False


def check_rows_are_consistent(rows70: list[Row], rows17: list[Row]) -> None:
    all_by_id = {row.row_idx: row for row in rows70}
    for row in rows17:
        require(row.row_idx in all_by_id, f"hard row {row.row_idx!r} is absent from rows70.csv")
        full = all_by_id[row.row_idx]
        require(
            (row.depth, row.configs) == (full.depth, full.configs),
            f"hard row {row.row_idx!r} differs between the two input tables",
        )


def make_coverage(rows70: list[Row], rows17: list[Row]) -> tuple[dict[str, Any], list[str]]:
    configs = sorted({config for row in rows70 for config in row.configs})
    require(len(configs) == 13, f"expected 13 distinct configs, found {len(configs)}: {configs}")
    require(all(config in configs for row in rows17 for config in row.configs), "rows17 has a config absent from rows70")

    # Ordered target/source comparisons. A target includes itself through the
    # non-strict, injective role relation.
    dominance: dict[str, list[str]] = {}
    for target in configs:
        dominance[target] = sorted(
            source for source in configs if injectively_dominates(target, source)
        )

    def rows_covered(rows: list[Row], target: str) -> list[int | str]:
        dominated_sources = set(dominance[target])
        return sorted(
            (row.row_idx for row in rows if dominated_sources.intersection(row.configs)),
            key=row_id_sort_key,
        )

    coverage: dict[str, Any] = {
        "dominance": dominance,
        "cover_all": {target: rows_covered(rows70, target) for target in configs},
        "cover_hard": {target: rows_covered(rows17, target) for target in configs},
    }
    return coverage, configs


def literal_coverage(rows: list[Row], configs: list[str]) -> dict[str, set[int | str]]:
    return {config: {row.row_idx for row in rows if config in row.configs} for config in configs}


def exhaustive_min_covers(
    rows: list[Row], configs: list[str], cover_map: dict[str, set[int | str]]
) -> tuple[int, list[tuple[str, ...]], int]:
    targets = {row.row_idx for row in rows if row.configs}
    require(bool(targets), "no table-coverable rows in minimum-cover calculation")
    for size in range(1, len(configs) + 1):
        winners: list[tuple[str, ...]] = []
        for selection in itertools.combinations(configs, size):
            covered: set[int | str] = set()
            for config in selection:
                covered.update(cover_map[config])
            if targets <= covered:
                winners.append(selection)
        if winners:
            return size, winners, len(targets)
    raise CheckFailure("no cover found from the complete config alphabet")


def threshold_coverage(
    rows: list[Row], target: str, threshold: int, dominance: dict[str, list[str]]
) -> set[int | str]:
    # A pass at T yields span <= T-1; to kill a row with dimension d one needs
    # T-1 <= d-1, hence T <= d. Using T >= d reverses the implication.
    dominated_sources = set(dominance[target])
    return {
        row.row_idx
        for row in rows
        if threshold <= row.depth and dominated_sources.intersection(row.configs)
    }


def compare_result(actual: dict[str, Any], result_path: Path) -> None:
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise CheckFailure(f"missing expected result file: {result_path}") from error
    except json.JSONDecodeError as error:
        raise CheckFailure(f"invalid JSON in {result_path}: {error}") from error
    expected = result.get("coverage")
    require(isinstance(expected, dict), "RESULT.json must contain an object at ['coverage']")
    if actual != expected:
        mismatch = {
            key: {"expected": expected.get(key), "actual": actual.get(key)}
            for key in sorted(set(expected) | set(actual))
            if expected.get(key) != actual.get(key)
        }
        raise CheckFailure("independent coverage differs from RESULT.json: " + json.dumps(mismatch, sort_keys=True))


def main() -> int:
    input_dir = PACKAGE / "inputs"
    raw_inputs: dict[str, bytes] = {}
    for name, expected_hash in EXPECTED_HASHES.items():
        path = input_dir / name
        try:
            raw = path.read_bytes()
        except FileNotFoundError as error:
            raise CheckFailure(f"missing pinned input: {path}") from error
        actual_hash = hashlib.sha256(raw).hexdigest()
        require(actual_hash == expected_hash, f"{name} SHA256 mismatch: {actual_hash}")
        raw_inputs[name] = raw

    rows70 = read_rows(input_dir / "rows70.csv", raw_inputs["rows70.csv"])
    rows17 = read_rows(input_dir / "rows17.csv", raw_inputs["rows17.csv"])
    require(len(rows70) == 70, f"expected 70 rows in rows70.csv, found {len(rows70)}")
    require(len(rows17) == 17, f"expected 17 rows in rows17.csv, found {len(rows17)}")
    check_rows_are_consistent(rows70, rows17)

    coverage, configs = make_coverage(rows70, rows17)
    compare_result(coverage, PACKAGE / "RESULT.json")

    hard_coverable = [row for row in rows17 if row.configs]
    all_coverable = [row for row in rows70 if row.configs]
    require(
        len(hard_coverable) == EXPECTED_TABLE_COVERABLE["rows17.csv"],
        f"expected 16 table-coverable hard rows, found {len(hard_coverable)}",
    )
    require(
        len(all_coverable) == EXPECTED_TABLE_COVERABLE["rows70.csv"],
        f"expected 64 table-coverable rows, found {len(all_coverable)}",
    )

    expected_minima = {"rows70": (4, 2), "rows17": (3, 2)}
    for label, rows in (("rows70", rows70), ("rows17", rows17)):
        literal_min, literal_solutions, count = exhaustive_min_covers(
            rows, configs, literal_coverage(rows, configs)
        )
        dominance_cover_map = {
            config: set(coverage["cover_all" if label == "rows70" else "cover_hard"][config])
            for config in configs
        }
        dominance_min, dominance_solutions, dominance_count = exhaustive_min_covers(
            rows, configs, dominance_cover_map
        )
        require(count == dominance_count, f"coverable-row count differs for {label}")
        require(
            (literal_min, dominance_min) == expected_minima[label],
            f"expected literal/dominance minima {expected_minima[label]} for {label}, "
            f"got {literal_min}/{dominance_min}",
        )
        print(
            f"{label}: coverable={count}, literal_min={literal_min}, "
            f"dominance_min={dominance_min}, example_dominance_cover={dominance_solutions[0]}"
        )
        if not literal_solutions or not dominance_solutions:
            raise CheckFailure(f"missing exhaustive minimum-cover witness for {label}")

    hard_ids = {row.row_idx for row in hard_coverable}
    all_ids = {row.row_idx for row in all_coverable}
    hard_plan = threshold_coverage(rows17, "6554", 7, coverage["dominance"]) | threshold_coverage(
        rows17, "5555", 8, coverage["dominance"]
    )
    all_plan = threshold_coverage(rows70, "6554", 6, coverage["dominance"]) | threshold_coverage(
        rows70, "5555", 8, coverage["dominance"]
    )
    require(hard_plan == hard_ids, f"6554@T7 + 5555@T8 misses/adds hard rows: {sorted(hard_ids ^ hard_plan, key=row_id_sort_key)}")
    require(all_plan == all_ids, f"6554@T6 + 5555@T8 misses/adds rows: {sorted(all_ids ^ all_plan, key=row_id_sort_key)}")

    t8_only = threshold_coverage(rows17, "6554", 8, coverage["dominance"]) | threshold_coverage(
        rows17, "5555", 8, coverage["dominance"]
    )
    missing_at_t8 = hard_ids - t8_only
    require(not hard_ids <= t8_only, "T8-only plan unexpectedly covers all table-coverable hard rows")
    require(
        EXPECTED_HARD_T8_FAILURES <= missing_at_t8,
        f"T8-only plan did not fail rows 7, 8, 13: missing={sorted(missing_at_t8, key=row_id_sort_key)}",
    )

    print(f"configs={len(configs)}, ordered_config_pairs={len(configs) ** 2}")
    print(f"6554@T7 + 5555@T8: covers {len(hard_plan)} hard/table-coverable rows")
    print(f"6554@T6 + 5555@T8: covers {len(all_plan)} all/table-coverable rows")
    print("T8-only hard rows missed:", sorted(missing_at_t8, key=row_id_sort_key))
    print("SCOPE: independent table/matching audit; shared CSV and config premise, no geometry proof")
    print("PASS_INDEPENDENT_CLASS_C_DOMINANCE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CheckFailure as error:
        print(f"FAIL_INDEPENDENT_CLASS_C_DOMINANCE: {error}", file=sys.stderr)
        raise SystemExit(1)
