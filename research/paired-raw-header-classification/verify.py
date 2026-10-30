#!/usr/bin/env python3
"""Exact corroboration of the paired raw-broadcast header theorem.

No predecessor implementation is imported or executed. Normal execution is
read-only. The optional receipt is generated outside the repository.
"""

import argparse
import hashlib
import json
from math import comb
from pathlib import Path
import sys
import time


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dimensions(n):
    require(type(n) is int and 1 <= n <= 5, "pair count must be in 1..5")
    return 2 * n, 1 << (2 * n)


def full_pair_counts(n):
    """Inclusion-exclusion by the exact number of full parity pairs."""
    dimensions(n)
    return {
        k: comb(n, k) * sum(
            (-1) ** j * comb(n - k, j) * (1 << (1 << (2 * (n - k - j))))
            for j in range(n - k + 1)
        )
        for k in range(1, n + 1)
    }


def template_data(n, pair):
    bits, size = dimensions(n)
    require(type(pair) is int and 0 <= pair < n, "invalid pair")
    raw = tuple(i for i in range(bits) if i // 2 != pair)
    columns = [0] * (1 << len(raw))
    parity = 0
    for x in range(size):
        index = sum(((x >> bit) & 1) << j for j, bit in enumerate(raw))
        columns[index] |= 1 << x
        parity |= (((x >> (2 * pair)) ^ (x >> (2 * pair + 1))) & 1) << x
    require(sum(c.bit_count() for c in columns) == size, "template partition")
    return parity, tuple(columns)


def generate_three_pair_headers():
    """Enumerate each pair family in Gray order, retaining its union."""
    headers = {}
    for pair in range(3):
        current, columns = template_data(3, pair)
        for step in range(1 << len(columns)):
            if step:
                changed = (step & -step).bit_length() - 1
                current ^= columns[changed]
            headers[current] = headers.get(current, 0) | (1 << pair)
    require(len(headers) <= 3 * 65536, "header capacity")
    return headers


def parity_pairs(n, header):
    """Test literal Boolean derivatives, without using template labels."""
    _, size = dimensions(n)
    require(type(header) is int and 0 <= header < (1 << size), "invalid table")
    result = 0
    universe = (1 << size) - 1
    for pair in range(n):
        good = True
        for bit in (2 * pair, 2 * pair + 1):
            distance = 1 << bit
            low = sum(1 << x for x in range(size) if not x & distance)
            flipped = ((header & low) << distance) | ((header >> distance) & low)
            good = good and (header ^ flipped == universe)
        if good:
            result |= 1 << pair
    require(result < (1 << n), "pair-mask range")
    return result


def literal_decoder_check(header, first_pair, second_pair):
    """Actually decode the two omitted demands on every three-pair input."""
    comparisons = 0
    for x in range(64):
        r = (header >> x) & 1
        pair = (first_pair, second_pair)[r]
        a, b = 2 * pair, 2 * pair + 1
        raw_value = x & ~(3 << a)
        g_value = (header >> raw_value) & 1
        for bit, mate in ((a, b), (b, a)):
            decoded = r ^ g_value ^ ((x >> mate) & 1)
            require(decoded == ((x >> bit) & 1), "literal decoder conflict")
            comparisons += 1
    return comparisons


def enumerate_new_domain():
    headers = generate_three_pair_headers()
    histogram = {1: 0, 2: 0, 3: 0}
    digest = hashlib.sha256()
    protocols = comparisons = 0
    for header, declared in sorted(headers.items()):
        actual = parity_pairs(3, header)
        require(actual == declared, "family versus Boolean-derivative mismatch")
        histogram[actual.bit_count()] += 1
        digest.update(header.to_bytes(8, "little") + bytes([actual]))
        choices = tuple(j for j in range(3) if actual & (1 << j))
        for first in choices:
            for second in choices:
                comparisons += literal_decoder_check(header, first, second)
                protocols += 1
    require(histogram == {1: 196518, 2: 42, 3: 2}, "three-pair histogram")
    require(histogram == full_pair_counts(3), "closed-form count mismatch")
    require(protocols == 196704, "optimal payload-set protocol count")
    return {"headers": len(headers), "exact_pair_histogram": histogram,
            "payload_set_protocols": protocols, "omitted_demand_decodes": comparisons,
            "sorted_header_pair_sha256": digest.hexdigest()}


def feasible_raw_payload(fibre, raw, bits):
    """Independent zero-error oracle using each receiver's observation table."""
    for bit in range(bits):
        observed = {}
        for x in fibre:
            key = (x & raw, (x >> (bit ^ 1)) & 1)
            wanted = (x >> bit) & 1
            if key in observed and observed[key] != wanted:
                return False
            observed[key] = wanted
    return True


def oracle_header(header):
    """Exhaust every raw subset separately on both header branches."""
    minima = []
    sizes = []
    feasible = 0
    for r in (0, 1):
        fibre = tuple(x for x in range(64) if (header >> x) & 1 == r)
        best = 6
        for raw in range(64):
            if feasible_raw_payload(fibre, raw, 6):
                touched = sum((raw & (3 << (2 * j))) != (3 << (2 * j))
                              for j in range(3))
                require(len(fibre) <= 1 << (6 - touched), "fibre capacity bound")
                best = min(best, raw.bit_count())
                feasible += 1
        minima.append(best)
        sizes.append(len(fibre))
    numerator = 2 * 64 + sum(a * b for a, b in zip(minima, sizes))
    return numerator, feasible


def sample_headers():
    headers = set()
    for coefficients in range(64):
        for constant in (0, 1):
            headers.add(sum((((x & coefficients).bit_count() & 1) ^ constant) << x
                            for x in range(64)))
    require(len(headers) == 128, "affine sample capacity")
    state = 0xD1B54A32D192ED03
    for _ in range(256):
        state = (6364136223846793005 * state + 1442695040888963407) % (1 << 64)
        headers.add(state)
    headers.add(sum(((((x >> 0) ^ (x >> 1)) & 1)
                     | (((x >> 2) ^ (x >> 3)) & 1)) << x for x in range(64)))
    headers.add(sum((((x ^ (x >> 1)) & 1)
                    ^ (((x >> 2) & (x >> 3) & (x >> 4)) & 1)) << x
                    for x in range(64)))
    require(len(headers) <= 386, "oracle sample capacity")
    return tuple(sorted(headers))


def check_oracles():
    headers = sample_headers()
    optimal = nonoptimal = feasible = 0
    for header in headers:
        numerator, count = oracle_header(header)
        feasible += count
        if parity_pairs(3, header):
            require(numerator == 6 * 64, "optimal-header cost")
            optimal += 1
        else:
            require(numerator >= 7 * 64, "nonclass header one-unit gap")
            nonoptimal += 1
    coordinate = sum(((x >> 0) & 1) << x for x in range(64))
    unbalanced = sum(((((x ^ (x >> 1)) & 1)
                       | (((x >> 2) ^ (x >> 3)) & 1))) << x for x in range(64))
    require(oracle_header(coordinate)[0] == 7 * 64, "balanced sharp gap")
    require(oracle_header(unbalanced)[0] == 7 * 64, "unbalanced sharp gap")
    return {"headers": len(headers), "raw_subsets_examined": 128 * len(headers),
            "feasible_branch_subsets": feasible, "optimal_headers": optimal,
            "nonclass_headers": nonoptimal, "sharp_gap": 1}


def check_controls():
    parity = sum(((x ^ (x >> 1)) & 1) << x for x in range(64))
    zero = tuple(x for x in range(64) if not (parity >> x) & 1)
    one = tuple(x for x in range(64) if (parity >> x) & 1)
    require(feasible_raw_payload(zero, 60, 6), "positive branch zero")
    require(feasible_raw_payload(one, 60, 6), "positive branch one")
    require(not feasible_raw_payload(tuple(range(64)), 60, 6), "constant header")
    require(not feasible_raw_payload(zero, 56, 6), "missing third payload bit")
    damaged = parity ^ 1
    bad_fibre = tuple(x for x in range(64) if (damaged >> x) & 1)
    require(not feasible_raw_payload(bad_fibre, 60, 6), "damaged truth table")
    require(not feasible_raw_payload(zero, 51, 6), "wrong omitted pair")
    require(not feasible_raw_payload(zero, 54, 6), "two different pairs omitted")
    underpriced_charge = 1 + (60).bit_count()
    require(underpriced_charge < 6, "underpriced-header boundary")
    invalid = (0, 6, True, 1.5)
    for n in invalid:
        try:
            dimensions(n)
        except ValueError:
            continue
        raise ValueError("invalid dimension accepted")
    return {"semantic_rejections": 5, "invalid_dimensions": len(invalid),
            "underpriced_header_counterexample_cost": underpriced_charge}


def authenticate_sources(package):
    manifest = json.loads((package / "SOURCES.json").read_text())
    root = package.parent.parent
    rows = manifest["files"]
    require(len(rows) <= 16, "source row bound")
    checked = {}
    for row in rows:
        if row.get("usage") == "input":
            path = root / row["path"]
            require(path.is_file() and path.stat().st_size <= 1048576, "source size")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            require(digest == row["sha256"], "source hash: " + row["path"])
            checked[row["path"]] = digest
    require(len(checked) == 3, "source input count")
    return checked


def write_receipt(path, package, result):
    require(path.expanduser().is_absolute(), "receipt path must be absolute")
    destination = path.expanduser().resolve()
    root = package.parent.parent
    require(destination.is_absolute() and not destination.is_relative_to(root),
            "receipt must be outside the repository")
    files = tuple(sorted(package.iterdir()))
    require(len(files) <= 16, "package file bound")
    hashes = {}
    for file in files:
        require(file.is_file() and file.stat().st_size <= 1048576, "package file size")
        hashes[file.name] = hashlib.sha256(file.read_bytes()).hexdigest()
    payload = {"result": result, "package_sha256": hashes}
    serialized = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    with destination.open("x") as output:
        require(output.write(serialized) == len(serialized), "incomplete receipt write")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    sources = authenticate_sources(package)
    start = time.monotonic()
    result = {"claim_type": "scoped proof with finite corroboration",
              "three_pair_enumeration": enumerate_new_domain(),
              "independent_raw_subset_oracles": check_oracles(),
              "controls": check_controls(), "source_sha256": sources,
              "python": sys.version.split()[0]}
    result["elapsed_seconds"] = round(time.monotonic() - start, 6)
    if args.receipt:
        write_receipt(args.receipt, package, result)
    print(json.dumps(result, sort_keys=True))
    print("PASS_PAIRED_RAW_HEADER_CLASSIFICATION")


if __name__ == "__main__":
    main()
