"""Source-closed sign invariant and retained finite premise. Apache-2.0."""

import argparse
import hashlib
import json
import random
import subprocess
import tempfile
from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import invariant as inv
import oracle

ROOT = Path(__file__).resolve().parent


def quotient_contract():
    images = inv.group_images()
    group = oracle.group_permutations()
    for g in range(8):
        for h in range(8):
            inv.require(inv.quotient_product(images[g], images[h]) == images[group[g][h]],
                        "Q8 quotient homomorphism")
    for a, b, c in product((1, 2, 4, 8, 16), repeat=3):
        inv.require(inv.quotient_product(inv.quotient_product(a, b), c)
                    == inv.quotient_product(a, inv.quotient_product(b, c)), "associativity")
    inv.require(images[5] == 11 and images[6] == 13, "negative central coefficient")
    return {"group_products": 64, "basis_associativity": 125}


def check_word(rows, labels):
    endpoint = oracle.endpoint(rows, labels)
    images = inv.group_images()
    central = []
    for row in endpoint:
        output = 0
        for c, packet in enumerate(row):
            q = 0
            for g in range(8):
                if packet >> g & 1:
                    q ^= images[g]
            output |= ((q >> 3) & 1) << c
        central.append(output)
    h = inv.chronological(rows, labels)
    expected = inv.multiply(inv.multiply(rows, h), rows)
    inv.require(tuple(central) == expected, "chronological central coefficient")
    inv.require(inv.multiply(rows, rows) == oracle.binary_product(rows, rows), "binary product")
    inv.require(inv.rank(rows) == oracle.span_rank(rows), "independent rank")
    if not any(inv.obstruction(rows, labels)):
        inv.require(2 * inv.rank(rows) <= len(rows), "half-call rank bound")


def generic_words():
    count = 0
    for n in range(1, 4):
        for rows in oracle.grams(n):
            for labels in product((1, 2), repeat=n):
                check_word(rows, labels)
                count += 1
    rng = random.Random(15253471)
    for n in range(4, 10):
        for _ in range(80):
            rows = tuple(rng.randrange(1 << n) | (1 << k) for k in range(n))
            labels = tuple(rng.choice((1, 2)) for _ in range(n))
            check_word(rows, labels)
            count += 1
    return count


def direct_words():
    checked = 0
    for target in product((1, 2), repeat=3):
        rows = tuple(sum(1 << j for j in range(9) if j // 3 == k // 3) for k in range(9))
        labels = tuple(g for g in target for _ in range(3))
        check_word(rows, labels)
        inv.require(not any(inv.obstruction(rows, labels)) and inv.rank(rows) == 3,
                    "attaining nine-call core")
        endpoint = oracle.endpoint(rows, labels)
        expected = tuple(tuple(((rows[r] >> c) & 1) << (target[r // 3] + 4)
                               for c in range(9)) for r in range(9))
        inv.require(endpoint == expected, "direct negative endpoint")
        checked += 1
    inv.require(any(inv.obstruction((1, 2, 4), (1, 1, 1))), "positive scope control")
    return checked


def retained_sources():
    rows = json.loads((ROOT / "inputs/RETENTION.json").read_text())
    for row in rows:
        raw = (ROOT / row["path"]).read_bytes()
        inv.require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained source hash")
    return len(rows)


def dirty_controls():
    omissions = 0
    faithful_columns = 0
    group = oracle.group_permutations()
    for target in product((1, 2), repeat=3):
        word = tuple((1 << k, 1 << k, g) for k, g in enumerate(target) for _ in range(3))
        expected = tuple(tuple((1 << (target[r] + 4) if r < 3 else 1) if r == c else 0
                               for c in range(5)) for r in range(5))
        endpoint = oracle.physical_endpoint(word, 5)
        inv.require(endpoint == expected, "restored dirty spectators")
        for remove in range(9):
            inv.require(oracle.physical_endpoint(word[:remove] + word[remove + 1:], 5)
                        != expected, "one-call deletion")
            omissions += 1
        for c in range(5):
            for h in range(8):
                output = tuple(sum((1 << group[g][h]) for g in range(8)
                                   if endpoint[r][c] >> g & 1) for r in range(5))
                wanted = tuple((1 << group[target[c] + 4][h] if c < 3 else 1 << h)
                               if r == c else 0 for r in range(5))
                inv.require(output == wanted, "faithful dirty input column")
                faithful_columns += 1
    return {"omissions": omissions, "faithful_columns": faithful_columns}


def native_check(directory):
    binary = directory / "finite"
    command = ["c++", "-std=c++20", "-O3", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               "-Wconversion", "-Wshadow", str(ROOT / "finite.cpp"), "-o", str(binary)]
    subprocess.run(command, check=True, capture_output=True, timeout=120)
    completed = subprocess.run([str(binary), str(directory)], check=True,
                               capture_output=True, text=True, timeout=180)
    actual = [json.loads(line) for line in completed.stdout.splitlines()]
    retained = json.loads((ROOT / "inputs/pr3471-RESULT.json").read_text())
    expected = [row for row in retained["search"]
                if row["tag"] in ("r3-three", "positive-control")]
    inv.require(actual == expected, "retained finite search changed")
    for tag in ("r3-three", "positive-control"):
        for side in ("inverse", "prefix"):
            name = tag + "-" + side
            raw = (directory / (name + ".bin")).read_bytes()
            inv.require(hashlib.sha256(raw).hexdigest() == retained["balls"][name]["sha256"],
                        "retained ball changed")
    return actual


def independent_meet(directory):
    result = oracle.complete_meet()
    inv.require(result["hits"] == [0, 0], "independent finite exclusion")
    for side in ("inverse", "prefix"):
        raw = oracle.native_bytes(result[side])
        inv.require(raw == (directory / ("r3-three-" + side + ".bin")).read_bytes(),
                    "independent complete ball disagreement")
    return {"hits": result["hits"], "candidates": result["candidates"],
            "inverse_states": len(result["inverse"]), "prefix_states": len(result["prefix"])}


def source_hashes():
    paths = sorted(p for p in ROOT.rglob("*") if p.is_file()
                   and (p.suffix in (".py", ".cpp", ".md") or p.parent == ROOT / "inputs")
                   and "__pycache__" not in p.parts)
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def produce():
    retained = retained_sources()
    quotient = quotient_contract()
    words = generic_words()
    direct = direct_words()
    dirty = dirty_controls()
    with tempfile.TemporaryDirectory(prefix="q8-negative-core-") as temporary:
        directory = Path(temporary)
        native = native_check(directory)
        independent = independent_meet(directory)
    inv.require(independent["candidates"] == native[0]["candidates"], "complete query count")
    return {"status": "PASS_NEGATIVE_CORE_BOUND", "retained_sources": retained,
            "quotient": quotient, "generic_words": words, "direct_nine_call_targets": direct,
            "dirty": dirty,
            "native": native, "independent": independent, "source_sha256": source_hashes()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if args.write is not None:
        inv.require(not args.write.exists(), "refuse to overwrite receipt")
    result = produce()
    if args.write is None:
        inv.require(result == json.loads((ROOT / "RESULT.json").read_text()), "receipt mismatch")
    else:
        with args.write.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "source_sha256"}, sort_keys=True))


if __name__ == "__main__":
    main()
