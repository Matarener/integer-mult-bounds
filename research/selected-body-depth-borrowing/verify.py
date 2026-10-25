"""Source-bound exact borrowing receipt. Nick Petalas. Apache-2.0."""

import hashlib
import json
import sys
from dataclasses import astuple
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from borrowing import ceil_log, depth, need, select, selected_digits  # noqa: E402

PROFILES = (
    (2, 1, 2, 6, 2),
    (3, 2, 3, 12, 5),
    (4, 3, 2, 1, 1),
    (5, 2, 5, 7, 5),
    (6, 5, 3, 8, 2),
    (7, 3, 5, 11, 1),
    (8, 7, 2, 12, 5),
    (64, 42, 3, 6, 2),
)
INPUTS = (
    "research/ordinary-one-factor-stock/PROOF.md",
    "research/ordinary-one-factor-stock/selector.py",
    "research/physical-ordinary-interchange/encoded.py",
    "research/physical-ordinary-interchange/ordinary.py",
    "research/selected-bit-recursive-caller/PROOF.md",
    "research/selected-bit-recursive-caller/node.py",
    "research/selected-runtime-guard-stock/README.md",
)


def unique(pairs):
    need(len(pairs) <= 256, "object capacity")
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path):
    need(path.is_file() and not path.is_symlink(), "regular required JSON")
    need(path.stat().st_size <= 262144, "JSON capacity")
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def sources():
    manifest = load(PACKAGE / "SOURCES.json")
    need(
        type(manifest["files"]) is list and len(manifest["files"]) <= 16,
        "source inventory capacity",
    )
    entries = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(sorted(row["path"] for row in entries)) == INPUTS, "exact source closure")
    for row in entries:
        path = PACKAGE.parent.parent / row["path"]
        need(path.is_file() and not path.is_symlink(), "regular required source")
        need(path.stat().st_size <= 1048576, "source capacity")
        need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "source SHA256")


def census():
    digest = hashlib.sha256()
    admitted = 0
    for index, (m, r, q, b, compatibility) in enumerate(PROFILES):
        for e in range(1, 257):
            for w in range(1, 5):
                maximum = depth(e // w, m, r)
                digits = (
                    0,
                    *(ceil_log(q, compatibility * b**d) for d in range(1, maximum + 1)),
                )
                plan = select(e, w, m, r, digits)
                admitted += plan is not None
                row = [index, e, w, None if plan is None else list(astuple(plan))]
                digest.update((json.dumps(row, separators=(",", ":")) + "\n").encode())
    return {"cases": 8192, "admitted": admitted, "sha256": digest.hexdigest()}


def prime_certificate():
    q = (1 << 127) - 1
    need(all(127 % p for p in (2, 3, 5, 7, 11)), "prime Mersenne exponent")
    residue = 4
    for _ in range(125):
        residue = (residue * residue - 2) % q
    need(residue == 0 and q > 1 << 80, "Lucas-Lehmer selected prime")
    return {"q": str(q), "exponent": 127, "iterations": 125, "residue": residue}


def selected_case(e):
    w = 2
    need(1 < e**17 <= 2**10000, "exact selected atom width is two")
    table = selected_digits(w, depth(e, 64, 42))
    plan = select(e, w, 64, 42, table[: depth(e // w, 64, 42) + 1])
    need(plan is not None, "selected witness fits")
    return {
        "e": e,
        "w": w,
        "root_depth": depth(e, 64, 42),
        "root_depth_borrowed": table[-1],
        "unborrowed_body_depth": depth(e // w, 64, 42),
        "unborrowed_body_borrowed": table[depth(e // w, 64, 42)],
        "plan": list(astuple(plan)),
    }


def cycle():
    e, w = 970370, 2
    table = selected_digits(w, depth(e // w, 64, 42))
    low, high = 155651, 163843
    values = [table[depth((e - k) // w, 64, 42)] for k in (low, high, 159747)]
    need(values == [high, low, low], "actual selected two-cycle")
    need(all(2 * k < e and (e - k) // w >= 64 for k in (low, high)), "cycle fits")
    threshold = 64
    for _ in range(19):
        threshold = 64 * ((threshold + 41) // 42)
    need(threshold == 405312, "exact inverse-depth threshold")
    boundary = [table[depth((e - k) // w, 64, 42)] for k in (159746, 159747)]
    need(boundary == [high, low], "selected optimum boundary")
    return {
        "e": e,
        "w": w,
        "cycle": [low, high],
        "images": values,
        "depth20_threshold": threshold,
        "boundary_required": boundary,
    }


def report():
    return {
        "schema_version": 1,
        "scope": "least fitted borrowing for prescribed NODE-guard stocks",
        "census": census(),
        "prime": prime_certificate(),
        "selected": [selected_case(e) for e in (250000, 262144, 524288, 1048576, 970370)],
        "cycle": cycle(),
    }


def main():
    need(len(sys.argv) == 1, "no arguments; verifier never writes")
    sources()
    observed = report()
    expected = load(PACKAGE / "RESULT.json")
    need(
        json.dumps(observed, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "complete typed receipt",
    )
    print("PASS_BODY_DEPTH_BORROWING " + json.dumps(observed, sort_keys=True))


if __name__ == "__main__":
    main()
