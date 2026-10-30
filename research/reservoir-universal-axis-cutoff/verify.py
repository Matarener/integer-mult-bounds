#!/usr/bin/env python3
"""Exact axis capacity of the inherited conservative reservoir envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ALLOCATOR = "research/crt-reservoir-placement/allocator.py"
MAX_FILE_BYTES = 1 << 20


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_bytes(path: Path) -> bytes:
    with path.open("rb") as handle:
        data = handle.read(MAX_FILE_BYTES + 1)
    need(len(data) <= MAX_FILE_BYTES, "File exceeds the replay read bound")
    return data


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def parameters(p: int, d: int) -> int:
    need(type(p) is int and p >= 1, "p must be a positive integer")
    need(type(d) is int and d >= 65536 and d & (d - 1) == 0,
         "d must be a power of two at least 65536")
    return (p + 1).bit_length()


def batch(p: int, d: int, ell: int, wide: int) -> int:
    c = parameters(p, d)
    need(type(ell) is int and ell >= max(2, c), "Invalid precision")
    need(type(wide) is int and 0 <= wide <= d, "Invalid width count")
    return (d * (ell - 1) + wide) // (6400 * (ell + c))


def attaining_precision(p: int, d: int) -> int:
    c = parameters(p, d)
    k, delta = divmod(d, 6400)
    need(delta > 0, "A dyadic count has a nonzero remainder modulo 6400")
    return max(2, c, (6400 * k * c + delta - 1) // delta)


def capacity(p: int) -> tuple[int, int]:
    c = parameters(p, 65536)
    m = (p << (64 * c)) // (19200 * (p + 2) ** 64)
    return m, 6400 * (m + 1) - 1


def envelope_fits(p: int, r: int) -> bool:
    c = parameters(p, 65536)
    need(type(r) is int and r >= 0, "Invalid batch size")
    return 19200 * r * (p + 2) ** 64 <= p << (64 * c)


def check_maximum_grid() -> dict[str, int]:
    precision_rows = 0
    seams = 0
    for p in range(1, 129):
        for exponent in range(16, 25):
            d = 1 << exponent
            c = parameters(p, d)
            k = d // 6400
            ell_star = attaining_precision(p, d)
            need(batch(p, d, ell_star, d) == k, "Maximum is not attained")
            need(batch(p, d, ell_star + 1, d) == k, "Attained tail changes")
            if ell_star > c:
                need(batch(p, d, ell_star - 1, d) < k, "Attainment seam")
            seams += 1
            for ell in range(c, c + 65):
                low = batch(p, d, ell, 0)
                high = batch(p, d, ell, d)
                need(1 <= low <= high <= k, "Finite precision bound")
                length = d * ell
                denom = 6400 * (ell + c)
                need(high * denom <= length < (high + 1) * denom,
                     "Integer quotient bounds")
                precision_rows += 1
    return dict(precision_rows=precision_rows, attaining_seams=seams)


def check_width_counts() -> dict[str, int]:
    rows = 0
    d = 65536
    cases = ((1, 2), (1, 100), (2, 2), (2, 84),
             (131070, 36), (131070, 37))
    for p, ell in cases:
        previous = -1
        k = d // 6400
        for wide in range(d + 1):
            r = batch(p, d, ell, wide)
            need(previous <= r <= k, "Width-count monotonicity or maximum")
            need(r - previous <= 1 or previous == -1, "Unexpected batch jump")
            previous = r
            rows += 1
        need(previous == batch(p, d, ell, d), "Missing final width count")
    return dict(layouts=6, complete_width_count_patterns=rows)


def check_capacities() -> dict[str, object]:
    values = set(range(1, 513))
    values.update((1 << exponent) + offset
                  for exponent in range(2, 65) for offset in (-3, -2, -1, 0))
    neighbors = 0
    no_cutoff = 0
    for p in sorted(values):
        m, limit = capacity(p)
        need(envelope_fits(p, m) and not envelope_fits(p, m + 1),
             "Allowance floor seam")
        first_failure = max(65536, 1 << limit.bit_length())
        for d in (first_failure, max(65536, first_failure // 2)):
            ell_star = attaining_precision(p, d)
            r = batch(p, d, ell_star, d)
            expected = d <= limit
            need(envelope_fits(p, r) == expected, "Sharp axis-capacity boundary")
            need((r <= m) == expected, "Batch-capacity equivalence")
            neighbors += 1
        ell_star = attaining_precision(p, first_failure)
        need(not envelope_fits(p, batch(p, first_failure, ell_star, first_failure)),
             "No-p-cutoff witness did not fail")
        no_cutoff += 1
    examples = {}
    for p in (1, 2, 131070, 16777214, 9240576):
        m, limit = capacity(p)
        largest = None if limit < 65536 else 1 << (limit.bit_length() - 1)
        examples[str(p)] = dict(batch_capacity=m, axis_limit=limit,
                                largest_accepted_dyadic_count=largest)
    need(examples["16777214"]["largest_accepted_dyadic_count"] == 4194304,
         "Explicit large capacity")
    return dict(ambient_parameters=len(values), dyadic_neighbors=neighbors,
                no_p_cutoff_witnesses=no_cutoff, examples=examples)


def source_hashes() -> dict[str, str]:
    sources = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    need(len(rows) == 1 and rows[0]["path"] == ALLOCATOR, "Unexpected live input")
    source = read_bytes(ROOT / ALLOCATOR)
    digest = hashlib.sha256(source).hexdigest()
    need(digest == rows[0]["sha256"], "Changed allocator source")
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256(read_bytes(PACKAGE / name)).hexdigest()
              for name in names}
    hashes[ALLOCATOR] = digest
    return hashes


def actual_layouts() -> list[dict[str, int]]:
    constructor = runpy.run_path(str(ROOT / ALLOCATOR))["Layout"]
    rows = []
    d, p = 65536, 131070
    for ell, wide in ((17, d), (36, d), (37, 0), (37, d)):
        widths = (ell,) * wide + (ell - 1,) * (d - wide)
        layout = constructor(p, ell, widths)
        expected = batch(p, d, ell, wide)
        need(layout.r_max == expected, "Actual Layout batch differs")
        need(layout.L == d * (ell - 1) + wide, "Actual Layout length differs")
        need(layout.G == 64 * (ell + 17), "Actual Layout guard differs")
        rows.append(dict(p=p, d=d, ell=ell, wide=wide,
                         L=layout.L, G=layout.G, r_max=layout.r_max))
        del layout, widths
    need([row["r_max"] for row in rows] == [5, 6, 6, 7], "Boundary fixtures")
    need(envelope_fits(p, 6) and not envelope_fits(p, 7), "First failure")
    return rows


def controls(hashes: dict[str, str]) -> list[str]:
    names = []
    bad = ((0, 65536, 2, 0), (True, 65536, 2, 0), (1, 32768, 2, 0),
           (1, 102400, 2, 0), (1, 65536, 1, 0), (131070, 65536, 16, 0),
           (1, 65536, 2, -1), (1, 65536, 2, 65537), (1, 65536, 2, True))
    for index, args in enumerate(bad):
        try:
            batch(*args)
        except ValueError:
            names.append("invalid_domain_" + str(index))
        else:
            raise ValueError("An invalid domain fixture was accepted")
    p = 131070
    need(envelope_fits(p, 6) and not envelope_fits(p, 7), "Rounded cutoff mutant")
    names.append("allow_one_excess_batch")
    need(batch(p, 65536, 17, 65536) < 10, "Minimum precision is not maximum")
    names.append("check_only_minimum_precision")
    need(batch(p, 65536, 37, 0) == 6 < batch(p, 65536, 37, 65536),
         "Narrow widths cannot replace the maximum-width pattern")
    names.append("check_only_narrow_widths")
    changed = hashlib.sha256(read_bytes(ROOT / ALLOCATOR) + b"\n").hexdigest()
    need(changed != hashes[ALLOCATOR], "Source corruption was invisible")
    names.append("changed_source_byte")
    need(canonical({"count": 1}) != canonical({"count": True}),
         "Boolean-valued receipt mutation was invisible")
    names.append("boolean_receipt_count")
    return names


def result() -> dict[str, object]:
    hashes = source_hashes()
    return dict(schema_version=1, claim_type="scoped proof with finite corroboration",
                maximum_batch="floor(d/6400), attained",
                capacity="d <= 6400*(floor(p*2^(64*c)/(19200*(p+2)^64))+1)-1",
                source_sha256=hashes, maximum_grid=check_maximum_grid(),
                width_counts=check_width_counts(), capacities=check_capacities(),
                actual_layouts=actual_layouts(), controls=controls(hashes),
                no_new_kappa=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Write a new generated receipt")
    args = parser.parse_args()
    report = result()
    if args.write is not None:
        with args.write.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        saved = json.loads(read_bytes(PACKAGE / "RESULT.json"))
        need(canonical(saved) == canonical(report), "Receipt mismatch")
    print("PASS_RESERVOIR_UNIVERSAL_AXIS_CUTOFF "
          + hashlib.sha256(canonical(report).encode()).hexdigest())


if __name__ == "__main__":
    main()
