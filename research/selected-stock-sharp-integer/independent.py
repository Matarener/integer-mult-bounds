"""Separate no-import integer reconstruction of upper and sharpness claims."""

import hashlib
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def reconstruct():
    # Cross multiplication instead of the primary's Fraction arithmetic.
    require(32**599 > 2**364 * 21**599, "upper contraction")
    require(599 * 327709 < 6741 * 364 * 80, "upper stock coefficient")
    require(6741 * 364 * 80 - 599 * 327709 == 229, "exact upper margin")
    # An independent asymptotic obstruction, separate from the finite witness.
    require(32**6740 < 2**4096 * 21**6740, "6740 asymptotic obstruction")
    # Track inverse thresholds in units of 64, using t -> t+ceil(11t/21).
    units = 1
    for _ in range(262143):
        units += (11 * units + 20) // 21
    width = units << 6
    bits = width.bit_length()
    require(bits == 159307, "large threshold bit length")
    # Reconstruct forward depth with a decreasing quotient in a separate loop.
    remaining = width
    for _count in range(400001):
        if remaining < 64:
            break
        remaining = 21 * (remaining >> 6) * 2
    else:
        raise ValueError("independent contraction capacity")
    require(_count == 262144, "forward large threshold depth")
    gap = 4096 * _count - 6740 * bits
    require(gap == 12644, "strict finite obstruction")
    require(gap - 6740 == 5904, "conventional 1+log width obstruction")
    digest = hashlib.sha256(width.to_bytes((bits + 7) // 8, "big")).hexdigest()
    require(
        digest == "4244143f5dcb47d33ad69a8dcce2e75057f8856543bc923b7ba1c9d6dddf9839",
        "independent width identity",
    )
    return {"depth": _count, "width_bits": bits, "margin": gap, "sha256": digest}


def check_sources():
    package = Path(__file__).resolve().parent
    manifest = package / "SOURCES.json"
    require(manifest.is_file() and manifest.stat().st_size < 1048576, "source metadata capacity")
    source = json.loads(manifest.read_text())
    require(type(source["files"]) is list and len(source["files"]) <= 16, "bounded sources")
    paths = []
    for row in source["files"]:
        if row["usage"] == "input":
            path = package.parents[1] / row["path"]
            require(path.is_file() and not path.is_symlink(), "independent input availability")
            require(path.stat().st_size < 1048576, "independent source capacity")
            require(
                hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "independent source authentication",
            )
            paths.append(row["path"])
    require(len(paths) == 5 and len(set(paths)) == 5, "independent source inventory")


if __name__ == "__main__":
    check_sources()
    result = reconstruct()
    print(
        "PASS_INDEPENDENT_SHARP_STOCK coefficient=6741 "
        f"width_bits={result['width_bits']} margin={result['margin']}"
    )
