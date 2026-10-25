#!/usr/bin/env python3
"""Table/Fourier proof audit, importing no predecessor executable.

Chris R / Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
Credit Nick Petalas and the retained E8/P112 source and caller lineage.
"""

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST_SHA = "aaf286296d12499182777926e41e3202baf29ea296050f9135ed3b3872937281"
TABLE = "research/one-sided-six-multisets/data/data.txt"
CUT = "research/p112-common-cut23-caller/"
SIX = "research/p112-six-piece-concentration/"
SIMPLE = ((1,-1,-1,-1,-1,-1,-1,1), (2,2,0,0,0,0,0,0),
          (-2,2,0,0,0,0,0,0), (0,-2,2,0,0,0,0,0),
          (0,0,-2,2,0,0,0,0), (0,0,0,-2,2,0,0,0),
          (0,0,0,0,-2,2,0,0), (0,0,0,0,0,-2,2,0))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    require(len(pairs) == len({key for key, _ in pairs}), "duplicate JSON key")
    return dict(pairs)


def read_json(raw):
    return json.loads(raw, object_pairs_hook=unique)


def authenticate(root=ROOT, directory=HERE):
    raw = (directory / "SOURCES.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, "manifest identity")
    inputs = {}
    for row in read_json(raw)["files"]:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        require(path.resolve().is_relative_to(root.resolve()), "escaped input")
        require(not any(p.is_symlink() for p in [path, *path.parents]), "input symlink")
        data = path.read_bytes()
        require(len(data) <= 2_000_000, "input size")
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "input SHA256")
        require(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == row["git_blob"], "input Git blob")
        inputs[row["path"]] = data
    return inputs


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def coordinates(roots):
    # Solve all columns at once by exact dense Gaussian elimination.
    matrix = [[Fraction(SIMPLE[j][i]) for j in range(8)]
              + [Fraction(r[i]) for r in roots] for i in range(8)]
    for j in range(8):
        pivot = next(i for i in range(j, 8) if matrix[i][j])
        matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
        scale = matrix[j][j]
        matrix[j] = [x / scale for x in matrix[j]]
        for i in range(8):
            if i != j:
                scale = matrix[i][j]
                matrix[i] = [x - scale*y for x,y in zip(matrix[i],matrix[j])]
    result = list(zip(*(row[8:] for row in matrix), strict=True))
    require(all(x.denominator == 1 for c in result for x in c), "integral coordinates")
    require(all(min(c) >= 0 or max(c) <= 0 for c in result), "positive simple system")
    return [tuple(map(int, c)) for c in result]


def table_model(raw):
    lines = raw.decode().splitlines()
    labels = list(map(int, lines[0].split()))
    live = [tuple(map(int, row.split())) for row in lines[2:114]]
    frame = [tuple(2*(i==a) + s*2*(i==a+1) for i in range(8))
             for a in (0,2,4,6) for s in (-1,1)]
    roots = sorted(live + frame)
    shell = {tuple(2*(k==i) + s*(k==j) for k in range(8))
             for i,j in combinations(range(8),2) for s in (-2,2)}
    shell.update((1,*tail) for tail in product((-1,1),repeat=7) if sum(tail)%4 == 3)
    require(len(shell) == 120 and roots == sorted(shell), "complete E8 root patterns")
    coord = coordinates(roots)
    full = [1+sum((x%2) << (j+1) for j,x in enumerate(c)) for c in coord]
    require(labels == [x for r,x in zip(roots,full) if r not in frame], "caller labels")
    require(len(live) == len(set(labels)) == 112 and all(x&1 for x in labels),
            "distinct affine labels")
    require(all(sum(r[i]*r[j] for r in live) == 112*(i==j)
                for i in range(8) for j in range(8)), "evaluation Gram")
    for alpha in SIMPLE:
        for r in roots:
            require(dot(alpha,r)%4 == 0, "reflection integrality")
            image = tuple(x-dot(alpha,r)//4*y for x,y in zip(r,alpha))
            if next(x for x in image if x) < 0:
                image = tuple(-x for x in image)
            require(image in shell, "reflection closure")
    return roots, live, labels, coord


def character_section(size, spectrum, a, b):
    numerator = size+spectrum[a]+spectrum[b]+spectrum[a^b]
    require(numerator%4 == 0, "nonintegral Fourier section")
    return numerator//4


def character_caps(labels, supports):
    pairs = [(a,b) for a in range(1,512) for b in range(a+1,512) if a^b > b]
    require(len(pairs) == 43_435, "dual-space coverage")
    spectra = [[sum(1 if (a&x).bit_count()%2 == 0 else -1 for x in selected)
                for a in range(512)] for selected in [labels,*supports]]
    hist = Counter(character_section(112,spectra[0],a,b) for a,b in pairs)
    caps = [max(character_section(len(s),f,a,b) for a,b in pairs)
            for s,f in zip(supports,spectra[1:],strict=True)]
    require(max(hist) == 36 and set(caps) == {32}, "Fourier capacities")
    return {str(k):hist[k] for k in sorted(hist)}


def quadruples(off):
    hist = Counter((off[a]&off[b]&off[c]&off[d]).bit_count()
                   for a,b,c,d in combinations(range(len(off)),4))
    require(sum(hist.values()) == 8_214_570 and max(hist) == 14,
            "four-direction domain and maximum")
    return {str(k):hist[k] for k in sorted(hist)}


def audit(inputs):
    roots,live,labels,coord = table_model(inputs[TABLE])
    stored = read_json(inputs[CUT+"RESULT.json"])
    faces = [sum(all(c[j] == 0 for j in range(8) if not mask>>j&1) for c in coord)
             for mask in range(256)]
    require(max(faces[m] for m in range(256) if m.bit_count()<=6) == 36,
            "low-rank parabolic cap")
    require([faces[255^(1<<j)] for j in range(8)] == [42,28,22,14,16,23,37,63],
            "seven-node faces")
    face = [r for r,c in zip(roots,coord) if c[7] == 0]
    require(len(face) == 63 and sum(all(dot(r,h) == 0 for r in face) for h in roots) == 1,
            "E7 root normal")
    off = [sum(1<<i for i,r in enumerate(live) if dot(r,h)) for h in roots]
    supports = [[x for r,x in zip(live,labels) if dot(r,h)] for h in roots]
    flats = character_caps(labels,supports)
    four = quadruples(off)
    require(flats == stored["flat_facts"]["flat_size_histogram"], "full flat histogram")
    require(four == stored["fourfold"]["histogram"], "full fourfold histogram")
    require(Counter(map(int.bit_count,off)) == {53:112,56:8}, "root distances")
    prior = read_json(inputs["research/p112-b6-t4-original-covers/RESULT.json"])
    outstanding = {tuple(r["weights"]) for r in prior["rows"] if not r["covered"]}
    contracts = {tuple([2]*3+[7]*7), tuple([2,3,4,4]+[7]*6),
                 tuple([2,5]+[6]*8), tuple([4,5,5,5]+[6]*6)}
    require(outstanding == contracts and sum(r["covered"] for r in prior["rows"]) == 65,
            "conditional historical partition")
    six = read_json(inputs[SIX+"RESULT.json"])["incidence"]
    require(six["excluded_profile"] == [4,5,5,5]+[6]*6, "PR3295 actual caller")
    require(six["support_budget"] == 84 and six["singleton_lower_bounds"] == [6,10,10,10,18,18]
            and six["E6_joint_allowance"] == 146 < 156, "PR3295 incidence binding")
    require(4*21-3*23 == 15 > 14 and 2+4+8+8 == 22 < 53, "caller arithmetic")
    return {"schema":"p112-c5-followup-audit/v1", "flats":43_435,
            "root_flat_tests":5_212_200, "quadruples":8_214_570,
            "flat_size_histogram":flats, "fourfold_histogram":four,
            "common_cut_bound":3, "common_cut_budget":23,
            "fixed_inventory_conditional_coverage":69, "fixed_inventory_rows":69,
            "existing_last_caller_source":"PR3295 / 4cff8128f0f9ea1e61515b95ddbb884366e9362c",
            "scope":"Conditional contract composition; no full C5 or human/kernel review."}


def main():
    require(not sys.argv[1:], "no arguments")
    result = audit(authenticate())
    expected = read_json((HERE/"RESULT.json").read_bytes())
    require(json.dumps(result,sort_keys=True) == json.dumps(expected,sort_keys=True),
            "audit receipt mismatch")
    print("PASS_C5_FOLLOWUP_AUDIT Fourier43435x120 quadruples8214570 conditional_inventory69/69")


if __name__ == "__main__":
    main()
