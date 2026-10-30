#!/usr/bin/env python3
"""Exact unit-fee target-partition threshold. Produced by Nick Petalas."""
import argparse
import hashlib
import json
from pathlib import Path

BITS = 128
SCALE = 1 << BITS
ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer_root(value, degree):
    """Return floor(value**(1/degree)), with integer endpoint certificates."""
    require(type(value) is int and 0 <= value < 1 << 15000, "radicand limit")
    require(type(degree) is int and 1 <= degree <= 100, "degree limit")
    if value == 0:
        return 0
    estimate = 1 << ((value.bit_length() + degree - 1) // degree)
    for _ in range(512):
        next_estimate = ((degree - 1) * estimate
                         + value // estimate ** (degree - 1)) // degree
        if next_estimate >= estimate:
            require(estimate ** degree <= value < (estimate + 1) ** degree,
                    "root endpoint certificate")
            return estimate
        estimate = next_estimate
    raise ValueError("root iteration limit")


def power_bounds(rank, numerator):
    require(type(rank) is int and 1 <= rank <= 288, "rank limit")
    require(numerator in (1, 99), "exponent limit")
    radicand = rank ** numerator << (100 * BITS)
    lower = integer_root(radicand, 100)
    upper = lower if lower ** 100 == radicand else lower + 1
    return lower, upper


def balanced_parts(rank, count):
    require(type(rank) is int and type(count) is int
            and 2 <= count <= rank <= 288, "partition domain")
    quotient, remainder = divmod(rank, count)
    result = (quotient,) * (count - remainder) + (quotient + 1,) * remainder
    require(sum(result) == rank and len(result) == count, "balanced mass")
    return result


def profit_bounds(parts, table):
    require(isinstance(parts, tuple) and 2 <= len(parts) <= 288,
            "proper partition required")
    require(all(type(r) is int and r >= 1 for r in parts), "positive ranks")
    rank = sum(parts)
    require(rank <= 288, "partition rank limit")
    debit_lower, debit_upper = table[rank]
    fee = len(parts) * SCALE
    lower = sum(table[r][0] for r in parts) - debit_upper - fee
    upper = sum(table[r][1] for r in parts) - debit_lower - fee
    return lower, upper


def threshold_certificate(table):
    """Jensen rejects all smaller ranks; a balanced partition attains 288."""
    debit_lower, debit_upper = table[287]
    rows = []
    for count in range(2, 288):
        root_lower, root_upper = power_bounds(count, 1)
        lower = debit_lower * (root_lower - SCALE) - count * SCALE ** 2
        upper = debit_upper * (root_upper - SCALE) - count * SCALE ** 2
        require(upper < 0, "Jensen rejection failed")
        balanced_lower, balanced_upper = profit_bounds(balanced_parts(287, count), table)
        rows.append({"pieces": count, "lower": lower, "upper": upper,
                     "balanced_lower": balanced_lower, "balanced_upper": balanced_upper})
    best = max(rows, key=lambda row: row["upper"])
    require(best["pieces"] == 3, "critical rejected count")
    integer_best = max(rows, key=lambda row: row["balanced_upper"])
    require(integer_best["pieces"] == 3, "critical integer count")
    require(integer_best["balanced_upper"] * 1000000 < -4077 * SCALE,
            "uniform integer negative margin")
    parts = balanced_parts(288, 3)
    lower, upper = profit_bounds(parts, table)
    require(lower * 1000000 > 6289 * SCALE, "positive witness lower margin")
    require(upper * 1000000 < 6290 * SCALE, "positive witness upper margin")
    return {"exponent": "99/100", "fee_per_piece": 1,
            "first_profitable_rank": 288, "rejected_rank": 287,
            "jensen_denominator": SCALE ** 2, "jensen_rows": rows,
            "critical_rejected_pieces": 3, "witness": list(parts),
            "profit_denominator": SCALE, "profit_lower": lower,
            "profit_upper": upper}


def binary_root_oracle(value, degree):
    """Independent bisection, used only on the decisive endpoint powers."""
    low, high = 0, 1 << ((value.bit_length() + degree - 1) // degree)
    for _ in range(high.bit_length() + 1):
        if high - low <= 1:
            require(low ** degree <= value < high ** degree, "oracle endpoints")
            return low
        middle = (low + high) // 2
        if middle ** degree <= value:
            low = middle
        else:
            high = middle
    raise ValueError("oracle iteration limit")


def check_power_oracle(table):
    cases = [(rank, 99) for rank in (1, 2, 3, 4, 96, 287, 288)]
    cases += [(rank, 1) for rank in (2, 3, 4, 287)]
    for rank, numerator in cases:
        radicand = rank ** numerator << (100 * BITS)
        actual = table[rank][0] if numerator == 99 else power_bounds(rank, 1)[0]
        require(actual == binary_root_oracle(radicand, 100), "oracle mismatch")
    return len(cases)


def check_all_small_partitions(table):
    """Enumerate each sorted partition once; test the fixed-count maximizer."""
    checked = 0
    for rank in range(2, 25):
        stack = [(rank, 1, ())]
        for _ in range(100000):
            if not stack:
                break
            remaining, minimum, prefix = stack.pop()
            if remaining == 0:
                if len(prefix) < 2:
                    continue
                lower, upper = profit_bounds(prefix, table)
                require(upper < 0, "small partition passed")
                balanced = balanced_parts(rank, len(prefix))
                if prefix != balanced:
                    balanced_lower, _ = profit_bounds(balanced, table)
                    require(upper < balanced_lower, "strict balancing failed")
                require(lower <= upper, "reversed profit interval")
                checked += 1
                continue
            for part in range(minimum, remaining + 1):
                stack.append((remaining - part, part, prefix + (part,)))
        else:
            raise ValueError("partition enumeration limit")
    return checked


def verify_certificate(certificate, table):
    require(type(certificate) is dict, "certificate object")
    expected = threshold_certificate(table)
    require(json.dumps(certificate, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "threshold certificate mismatch")


def check_controls(certificate, table):
    controls = []
    for key, wrong in (("first_profitable_rank", 287), ("fee_per_piece", 0),
                       ("exponent", "1/2"), ("witness", [95, 96, 96]),
                       ("profit_lower", -1), ("critical_rejected_pieces", 2),
                       ("fee_per_piece", True)):
        altered = dict(certificate)
        altered[key] = wrong
        controls.append(altered)
    altered = json.loads(json.dumps(certificate))
    altered["jensen_rows"][0]["upper"] = 1
    controls.append(altered)
    for altered in controls:
        try:
            verify_certificate(altered, table)
        except ValueError:
            continue
        raise ValueError("forged certificate accepted")
    return len(controls)


def check_domain_controls(table):
    bad_parts = ((288,), (0, 288), (-1, 2), (True, 2), (144, 145))
    for parts in bad_parts:
        try:
            profit_bounds(parts, table)
        except ValueError:
            continue
        raise ValueError("invalid partition accepted")
    return len(bad_parts)


def source_hashes():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "verify.py")
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-receipt", type=Path)
    args = parser.parse_args()
    table = {rank: power_bounds(rank, 99) for rank in range(1, 289)}
    certificate = threshold_certificate(table)
    report = {"marker": "PASS_UNIT_FEE_TARGET_THRESHOLD", "certificate": certificate,
              "small_partitions": check_all_small_partitions(table),
              "independent_power_checks": check_power_oracle(table),
              "forged_certificates_rejected": check_controls(certificate, table),
              "invalid_partitions_rejected": check_domain_controls(table),
              "source_sha256": source_hashes()}
    if args.check_receipt:
        require(args.check_receipt.stat().st_size <= 1000000, "receipt size limit")
        supplied = json.loads(args.check_receipt.read_text(encoding="utf-8"))
        require(type(supplied) is dict
                and json.dumps(supplied, sort_keys=True) == json.dumps(report, sort_keys=True),
                "receipt or source mismatch")
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
