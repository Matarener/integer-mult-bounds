#!/usr/bin/env python3
"""Exact common-cut23 certificate and one historical C5 caller application.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
Geometry definitions retain Nick Petalas's PR3163 and E8/P112 lineage.
"""

import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SOURCE_MANIFEST_SHA = "9312885bb9c46b31a199283937b4cf0aec74252f6cd6877f6ef6e27f84f979fb"
MODEL = "research/p112-common-deletion-slice/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    raw = path.read_bytes()
    require(len(raw) <= 2_000_000, "input size bound")
    return json.loads(raw, object_pairs_hook=no_duplicates)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate(root):
    manifest_raw = (PACKAGE / "SOURCES.json").read_bytes()
    require(hashlib.sha256(manifest_raw).hexdigest() == SOURCE_MANIFEST_SHA,
            "source manifest identity")
    manifest = read_json(PACKAGE / "SOURCES.json")
    payloads = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        require(path.resolve().is_relative_to(root.resolve()), "input escaped root")
        require(all(not parent.is_symlink() for parent in (path, *path.parents)
                    if parent != root.parent), "source symlink")
        raw = path.read_bytes()
        require(len(raw) <= 2_000_000, "source size bound")
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob")
        payloads[row["path"]] = raw
    return payloads


def model(payloads):
    # Compile the exact authenticated source: no imports or cached bytecode.
    namespace = {"__name__": "p112_pinned_geometry"}
    raw = payloads[MODEL + "geometry.py"]
    exec(compile(raw, MODEL + "geometry.py", "exec"), namespace)
    roots = namespace["roots"]()
    fixture = json.loads(payloads[MODEL + "FIXTURE.json"])
    frame = {tuple(row) for row in fixture["omitted_frame"]}
    live = tuple(row for row in roots if row not in frame)
    labels = tuple(namespace["label"](row) for row in live)
    require(len(roots) == 120 and len(frame) == 8 and len(live) == 112, "root model")
    require(len(set(labels)) == 112 and all(x & 256 for x in labels), "affine labels")
    table = payloads["research/one-sided-six-multisets/data/data.txt"].decode().splitlines()
    original_labels = tuple(map(int, table[0].split()))
    original_roots = tuple(tuple(map(int, row.split())) for row in table[2:114])
    require(original_roots == live, "original caller root coordinates")
    require(original_labels == tuple(((x & 255) << 1) | (x >> 8) for x in labels),
            "original caller binary-label rotation")
    require(all(sum(r[i] * r[j] for r in live) == 112 * (i == j)
                for i in range(8) for j in range(8)), "injective evaluation Gram")
    namespace["reflection_permutations"](roots)
    return namespace, roots, live, labels


def chamber_facts(g, roots):
    coordinates = [g["coordinates"](r) for r in roots]
    supports = [sum(1 << j for j, x in enumerate(c) if x) for c in coordinates]
    faces = [sum(s & ~mask == 0 for s in supports) for mask in range(256)]
    lower = max(faces[mask] for mask in range(256) if mask.bit_count() <= 6)
    seven = [faces[255 ^ (1 << j)] for j in range(8)]
    require(lower == 36 and seven == [42, 28, 22, 14, 16, 23, 37, 63], "chamber caps")
    mask = sum(1 << i for i, s in enumerate(supports) if s & ~(255 ^ 128) == 0)
    normal = g["normals"](roots, mask)
    require(len(normal) == 1 and normal[0] in {g["canonical"](r) for r in roots},
            "63-root face must have a root normal")
    return {"rank_at_most_six_max": lower, "seven_face_counts": seven,
            "root_face_normal": list(normal[0])}


def flat_facts(g, roots, live, labels):
    all_live = (1 << 112) - 1
    characters = [sum(1 << i for i, label in enumerate(labels)
                      if (a & label).bit_count() % 2) for a in range(512)]
    flats = [(a, b, all_live ^ (characters[a] | characters[b]))
             for a in range(1, 512) for b in range(a + 1, 512) if b < (a ^ b)]
    require(len(flats) == 43_435, "seven-flat coverage")
    histogram = Counter(mask.bit_count() for _, _, mask in flats)
    require(max(histogram) == 36, "global rank-seven support cap")
    off = [sum(1 << i for i, r in enumerate(live) if g["dot"](r, h)) for h in roots]
    maxima = [max((o & mask).bit_count() for _, _, mask in flats) for o in off]
    require(set(maxima) == {32}, "root-restricted seven-flat cap")
    cuts = Counter((o.bit_count(), m, o.bit_count() - m) for o, m in zip(off, maxima))
    require(dict(cuts) == {(56, 32, 24): 8, (53, 32, 21): 112}, "root cut minima")
    return flats, off, {
        "seven_flats": len(flats), "global_seven_flat_cap": max(histogram),
        "flat_size_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "root_flat_tests": len(roots) * len(flats),
        "root_cut_minima": {",".join(map(str, k)): cuts[k] for k in sorted(cuts)},
    }


def fourfold_facts(roots, off):
    histogram = Counter()
    witness = None
    for a, b, c, d in combinations(range(120), 4):
        size = (off[a] & off[b] & off[c] & off[d]).bit_count()
        histogram[size] += 1
        if size == 14 and witness is None:
            witness = [a, b, c, d]
    require(sum(histogram.values()) == comb(120, 4) == 8_214_570, "fourfold coverage")
    require(max(histogram) == 14 and witness is not None, "fourfold support maximum")
    return {"quadruples": sum(histogram.values()), "maximum": max(histogram),
            "histogram": {str(k): histogram[k] for k in sorted(histogram)},
            "witness_indices": witness, "witness_roots": [list(roots[i]) for i in witness]}


def binary_rank(values):
    basis = {}
    for value in values:
        while value:
            pivot = value.bit_length()
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def positive_fixture(g, roots, live, labels, flats, off):
    directions = [(0, 0, 0, 0, 0, 2, -2, 0), (0, 0, 0, 0, 0, 2, 2, 0)]
    annihilators = [(65, 257), (64, 257)]
    lookup = {(a, b): mask for a, b, mask in flats}
    cuts = [off[roots.index(h)] & ~lookup[ab] for h, ab in zip(directions, annihilators)]
    common = cuts[0] | cuts[1]
    ranks = [binary_rank([labels[i] for i, r in enumerate(live)
                          if g["dot"](r, h) and not (common >> i & 1)]) for h in directions]
    require(common.bit_count() == 22 and ranks == [7, 7], "two-direction positive fixture")
    require(len(g["echelon"](directions)) == 2, "positive fixture independence")
    return {"directions": [list(h) for h in directions],
            "annihilators": [list(ab) for ab in annihilators],
            "common_cut_indices": [i for i in range(112) if common >> i & 1],
            "residual_ranks": ranks}


def theorem_budget(cut_budget, live_cut_minimum=21, fourfold_maximum=14):
    require(type(cut_budget) is int and 0 <= cut_budget <= 23, "uncertified cut budget")
    intersection_floor = 4 * live_cut_minimum - 3 * cut_budget
    require(intersection_floor > fourfold_maximum, "no four-direction contradiction")
    return {"cut_budget": cut_budget, "four_cut_intersection_floor": intersection_floor,
            "fourfold_maximum": fourfold_maximum, "projective_direction_bound": 3}


def caller_audit(payloads):
    prior = json.loads(payloads["research/p112-b6-t4-original-covers/RESULT.json"])
    require(prior["historical"] == len(prior["rows"]) == 69 and prior["combined"] == 65,
            "historical inventory identity")
    inherited = [row["weights"] for row in prior["rows"] if row["covered"]]
    require(len(inherited) == 65, "inherited covered flags")
    successors = [[2, 2, 2] + [7] * 7, [2, 5] + [6] * 8]
    target = [2, 3, 4, 4] + [7] * 6
    remaining = [4, 5, 5, 5] + [6] * 6
    require(prior["inventory_uncertified"] == [successors[0], target, successors[1], remaining],
            "named caller binding")
    cap = sum(2 ** (w - 1) for w in target[:4])
    require(cap == 22 < 53 and len(target) - 6 == 4, "caller quotient budget")
    return {"historical_rows": 69, "inherited_contract_coverage": len(inherited),
            "successor_contract_rows": successors, "coverage_before_new_lemma": 67,
            "new_caller": target, "small_support_cap": cap, "required_directions": 6,
            "direction_bound": 3, "conditional_inventory_coverage": 68,
            "inventory_uncertified": [remaining],
            "scope": "Fixed named contract inventory, not a global unresolved count."}


def compute(root):
    payloads = authenticate(root)
    g, roots, live, labels = model(payloads)
    chamber = chamber_facts(g, roots)
    flats, off, flat_summary = flat_facts(g, roots, live, labels)
    return {"schema": "p112-common-cut23-caller/v1", "chamber": chamber,
            "flat_facts": flat_summary, "fourfold": fourfold_facts(roots, off),
            "positive_fixture": positive_fixture(g, roots, live, labels, flats, off),
            "theorem": theorem_budget(23), "caller": caller_audit(payloads)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=PACKAGE.parents[1])
    parser.add_argument("--write-result", type=Path, help="Explicit receipt generation only")
    args = parser.parse_args()
    result = compute(args.repository)
    if args.write_result is not None:
        require(not args.write_result.exists(), "refuse to overwrite a receipt")
        args.write_result.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(canonical(result) == canonical(read_json(PACKAGE / "RESULT.json")),
                "result receipt mismatch")
    print("PASS_P112_COMMON_CUT23_CALLER flats=43435 root_flat_tests=5212200 "
          "quadruples=8214570 bound=3 caller_excluded=true conditional_inventory=68/69")


if __name__ == "__main__":
    main()
