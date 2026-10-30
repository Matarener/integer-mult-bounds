#!/usr/bin/env python3
"""Exact integer-height certificate. Produced by Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path


HEIGHT = 12040587444441491
GRID_HEIGHT = 12040700000000000
DENOMINATOR = 700000000000
POWER = 322
TERMS = 80
SCALE = 1 << 220
PACKAGE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def outward(low, high):
    """Round a proved interval outwards onto a fixed dyadic grid."""
    require(low <= high, "reversed interval")
    return Q((low * SCALE).__floor__(), SCALE), Q((high * SCALE).__ceil__(), SCALE)


def log_unit(value):
    """Enclose ln(value), for 1 <= value <= 2, by a positive series."""
    require(Q(1) <= value <= Q(2), "logarithm unit domain")
    z = (value - 1) / (value + 1)
    term = z
    total = Q(0)
    for index in range(TERMS):
        total += 2 * term / (2 * index + 1)
        term *= z * z
    tail = 2 * term / ((2 * TERMS + 1) * (1 - z * z))
    return outward(total, total + tail)


def log2_integer(value):
    require(type(value) is int and 1 <= value <= 1 << 64, "integer log domain")
    shift = value.bit_length() - 1
    low, high = log_unit(Q(value, 1 << shift))
    base_low, base_high = log_unit(Q(2))
    require(base_low > 0, "positive logarithm base")
    return outward(shift + low / base_high, shift + high / base_low)


def margin(height, power=POWER, denominator=DENOMINATOR):
    require(type(height) is int and 1 <= height < 1 << 64, "height domain")
    require(type(power) is int and 1 <= power <= 1024, "power domain")
    require(type(denominator) is int and 1 <= denominator <= 10**15, "gap domain")
    low, high = log2_integer(height + 1)
    return outward(Q(height, denominator) - power * high,
                   Q(height, denominator) - power * low)


def threshold(height=HEIGHT, power=POWER, denominator=DENOMINATOR):
    require(type(height) is int and 2 <= height < 1 << 64, "threshold domain")
    previous = margin(height - 1, power, denominator)
    current = margin(height, power, denominator)
    require(previous[1] < 0, "preceding height must lose strictly")
    require(current[0] > 0, "candidate height must win strictly")
    return {"height": height, "previous_margin": list(map(str, previous)),
            "current_margin": list(map(str, current))}


def authenticate(data, digest, blob):
    require(hashlib.sha256(data).hexdigest() == digest, "changed predecessor bytes")
    header = f"blob {len(data)}\0".encode()
    require(hashlib.sha1(header + data).hexdigest() == blob, "changed predecessor blob")


def sources():
    records = json.loads((PACKAGE / "PREDECESSOR.json").read_text())
    expected = {
        "retained/PROOF.md": "7e6dbcd2937601b107de31c1c2f64be886a4dde6741a30b7cc99bd59cc5528c8",
        "retained/frontier.py": "2d1837eed6e828298f4e02ca9105ed4595b2d305354477e42b97fb3ad20d27fc",
    }
    require(records["commit"] == "08f0e5899254aa82288a91e70789049dc1f29690",
            "changed predecessor head")
    require(len(records["files"]) == 2, "predecessor file inventory")
    require({row["retained_path"] for row in records["files"]} == set(expected),
            "duplicate or missing predecessor file")
    for row in records["files"]:
        path = row["retained_path"]
        require(row["sha256"] == expected[path], "changed predecessor pin")
        authenticate((PACKAGE / path).read_bytes(), expected[path], row["git_blob"])
    text = (PACKAGE / "retained/frontier.py").read_text()
    for literal in ["BASE_K = Q('0.003027288235')", "BASE_S = Q('0.003027288245')",
                    "p=322, H=12040700000000000, j=17201)", "(s-k)/7"]:
        require(literal in text, "missing cited fixed-height parameter")
    require((Q('.003027288245') - Q('.003027288235')) / 7 == Q(1, DENOMINATOR),
            "cited gap does not match the new guard")


def controls():
    rejected = 0
    for bad in [HEIGHT - 1, HEIGHT + 1, 2, 0, -1, True, 1 << 64]:
        try:
            threshold(bad)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("false minimum accepted")
    for bad in [Q(0), Q(3)]:
        try:
            log_unit(bad)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid logarithm domain accepted")
    records = json.loads((PACKAGE / "PREDECESSOR.json").read_text())
    for row in records["files"]:
        data = (PACKAGE / row["retained_path"]).read_bytes()
        for digest, blob, payload in [(row["sha256"], row["git_blob"], data + b"\n"),
                                      (row["sha256"], "0" * 40, data)]:
            try:
                authenticate(payload, digest, blob)
            except ValueError:
                rejected += 1
            else:
                raise ValueError("source mutation accepted")
    return rejected


def small_exact_cases():
    checked = 0
    for height in range(1, 65):
        for power in range(1, 5):
            for denominator in range(1, 5):
                left = (height + 1) ** (power * denominator)
                right = 1 << height
                low, high = margin(height, power, denominator)
                require(not (high < 0) or left > right, "false negative interval")
                require(not (low > 0) or left < right, "false positive interval")
                require(low <= 0 <= high or left != right, "lost exact equality")
                require(left == right or high < 0 or low > 0, "unresolved small sign")
                checked += 1
    return checked


def run():
    sources()
    result = threshold()
    before = tuple(map(Q, result["previous_margin"]))
    after = tuple(map(Q, result["current_margin"]))
    require(Q(-36, 10**15) < before[0] <= before[1] < Q(-35, 10**15), "losing bracket")
    require(Q(1354, 10**15) < after[0] <= after[1] < Q(1355, 10**15), "winning bracket")
    require(HEIGHT > 8 * 1024, "retained side guard")
    result.update(reduction=GRID_HEIGHT - HEIGHT, controls=controls(),
                  small_exact_comparisons=small_exact_cases())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = run()
    if args.receipt:
        destination = args.receipt.resolve()
        require(not destination.is_relative_to(PACKAGE), "receipt must be outside the package")
        files = sorted(path for path in PACKAGE.rglob("*") if path.is_file())
        require(len(files) <= 32, "bounded package inventory")
        result["package_sha256"] = {str(path.relative_to(PACKAGE)):
            hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS_INTEGER_CARRIER_HEIGHT minimum={HEIGHT} reduction={GRID_HEIGHT - HEIGHT} "
          f"small_exact={result['small_exact_comparisons']} controls={result['controls']}")


if __name__ == "__main__":
    main()
