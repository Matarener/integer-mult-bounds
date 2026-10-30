#!/usr/bin/env python3
"""Independent check of #4154's P104 fiber-tag seam, in the orientation of its sources.

#3966 (PROOF.md section 4) defines the row correction z (x) q_j and the column correction r_i (x) z,
with q_j = O p_j for the row label and r_i = O p_i for the column label. #3954's witness lines are
386 (x) 386 (row port) and 405 (x) 386 (donor port), so its pair is row label 386, column label 405,
shared line r_i (x) q_j. Tensors here are sets of (alpha, beta) cells, not packed integers; no code
from #4154. Standard library only.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
GAUGE = ROOT / "research/p104-phase-uniform-gauge"
SEAM = ROOT / "research/p104-fiber-tag-seam"
TWO_AXIS = ROOT / "research/p104-two-axis-compatibility"
PINS = {
    GAUGE / "source/RESULT.json": "ce05a27ebc98677bec4febaa488fa03f5b6fc60216aa43b34298444d12f7ab6c",
    SEAM / "labels.json": "7227a7d6bdb49f36b6e401478034cc542eb887979890c8deda924b8ac0844209",
}
Z, ONES = 420, 511


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def bits(x):
    return [(x >> k) & 1 for k in range(9)]


def dot(x, y):
    return sum(a * b for a, b in zip(bits(x), bits(y))) % 2


def gauge(x):
    """O x = x + (x . z) z"""
    return x ^ Z if dot(x, Z) else x


def cells(u, v):
    """u (x) v as its set of nonzero cells (alpha, beta), with entry u_alpha v_beta"""
    return frozenset((a, b) for a, ua in enumerate(bits(u)) for b, vb in enumerate(bits(v)) if ua and vb)


def add(*tensors):
    out = set()
    for t in tensors:
        out ^= set(t)
    return frozenset(out)


def pair(s, t):
    return len(s & t) % 2


def tags(row_label, col_label):
    q, r = gauge(row_label), gauge(col_label)
    return cells(Z, q), cells(r, Z), cells(r, q)      # row tag, column tag, shared line


def census(labels, tag_fn):
    out = dict(full_equal=0, agree=0, disagree=0, helper_row_match=0, min_ham=99, min_pairs=set())
    a = add(cells(Z, ONES), cells(ONES, Z))
    for j in labels:            # row label
        for i in labels:        # column label
            row, col, line = tag_fn(j, i)
            need(pair(line, line) == 1, "shared line is nondegenerate")
            need(a != row and a != col, "uniform tag is never a fiber tag")
            out["full_equal"] += row == col
            same = pair(row, line) == pair(col, line)
            out["agree" if same else "disagree"] += 1
            out["helper_row_match"] += pair(a, line) == pair(row, line)
            ham = len(row ^ col)
            if ham < out["min_ham"]:
                out["min_ham"], out["min_pairs"] = ham, set()
            if ham == out["min_ham"]:
                out["min_pairs"] |= {j, i}
    return out


def main():
    for path, sha in PINS.items():
        need(hashlib.sha256(path.read_bytes()).hexdigest() == sha, f"pinned {path.name}")
    labels = json.loads((GAUGE / "source/RESULT.json").read_text())["physical_labels"]
    need(json.loads((SEAM / "labels.json").read_text()) == labels, "#4154's labels.json is #3966's source array")
    need(len(set(labels)) == 104 and all(0 < x < 512 for x in labels), "104 distinct labels in F2^9")
    proof = (GAUGE / "PROOF.md").read_text()
    need("The row correction is `z tensor q_j`; the column correction is `r_i tensor z`." in proof, "#3966 row/column corrections")
    need("q_j=Op_j" in proof and "r_i=Op_i" in proof, "#3966 images")

    # #3954's witness lines fix the orientation: row fiber q = p_j = 386, donor column p_i = 405
    w = json.loads((TWO_AXIS / "RESULT.json").read_text())["witness"]
    def as_cells(n):
        return frozenset((k // 9, k % 9) for k in range(81) if (n >> k) & 1)
    need(as_cells(w["u_row"]) == cells(386, 386) and as_cells(w["u_donor"]) == cells(405, 386), "#3954 witness lines are 386(x)386 and 405(x)386")
    need((w["p_row"], w["p_donor"], w["q"]) == (386, 405, 386), "#3954 witness labels")
    ROW, COL = w["q"], w["p_donor"]

    # gauge facts, on all of F2^9
    need(dot(Z, Z) == 0 and bin(Z).count("1") == 4, "z even of weight 4")
    for x in range(512):
        need(gauge(gauge(x)) == x and dot(gauge(x), Z) == dot(x, Z), "O involution, z . Ox = z . x")
        need((bin(gauge(x)).count("1") - bin(x).count("1") - 2 * dot(x, Z)) % 4 == 0, "weight law")
        for y in range(x, 512):
            if dot(gauge(x), gauge(y)) != dot(x, y):
                raise AssertionError("O orthogonal")
    classes = [bin(x).count("1") % 4 for x in labels]
    need(classes.count(1) == 56 and classes.count(3) == 48, "56 class-1 and 48 class-3 labels")
    need(all(bin(gauge(x)).count("1") % 4 == 3 for x in labels), "every image has weight class 3")

    # orientation-free claims of #4154, in the source orientation
    src = census(labels, tags)
    need(src["full_equal"] == 0, "no full-address agreement")
    need((src["agree"], src["disagree"]) == (5440, 5376), "shared-line split 5440 / 5376")
    need(src["min_ham"] == 6 and src["min_pairs"] == {32, 4}, "minimum Hamming 6, only labels 32 and 4")
    need(src["helper_row_match"] == 104 * 48, "helper matches the row tag on 104 * 48 ordered pairs")
    # ... and it is the ROW label's class that decides it: a.line - row.line = z . q_j
    a = add(cells(Z, ONES), cells(ONES, Z))
    for j in labels:
        for i in labels:
            row, _, line = tags(j, i)
            need((pair(a, line) == pair(row, line)) == (bin(j).count("1") % 4 == 3), "helper/row match iff row label class 3")

    # the witness, in the source orientation
    row, col, line = tags(ROW, COL)
    need((gauge(ROW), gauge(COL)) == (386, 49), "witness images 386 and 49")
    flips = (pair(row, line), pair(col, line))
    need(flips == (1, 0), "source orientation: witness shared-line flips are (row 1, column 0)")
    need(pair(a, line) == flips[0], "source orientation: the uniform tag agrees with the witness row tag on the shared line")
    need(len(row ^ col) == 20, "witness Hamming distance 20")
    need((1, 2) not in row ^ col and (2, 1) in row ^ col, "cell (1,2) = bit 11 does not separate; cell (2,1) = bit 19 does")
    need(a != row, "the uniform tag still differs from the row tag on the full address")

    # control: #4154's code builds (z (x) O p_col, O p_row (x) z, O p_row (x) O p_col), the transposes
    def transposed(j, i):
        q, r = gauge(j), gauge(i)
        return cells(Z, r), cells(q, Z), cells(q, r)
    t = census(labels, transposed)
    need({k: t[k] for k in ("full_equal", "agree", "disagree", "min_ham")} == {k: src[k] for k in ("full_equal", "agree", "disagree", "min_ham")}, "control: the census is orientation-free")
    row_t, col_t, line_t = transposed(ROW, COL)
    need((pair(row_t, line_t), pair(col_t, line_t)) == (0, 1) and pair(a, line_t) == 1, "control: transposed orientation reproduces #4154's flips 0/1 and its helper mismatch")
    need((1, 2) in row_t ^ col_t, "control: transposed orientation reproduces #4154's bit 11")
    seam_code = (SEAM / "verify.py").read_text()
    need("return tensor(Z, column_image), tensor(row_image, Z)" in seam_code, "#4154's row tag is z (x) column image")

    print(json.dumps({
        "status": "PASS_P104_FIBER_TAG_ORIENTATION_CHECK",
        "confirmed": {"pairs": 104 * 104, "full_equal": 0, "shared_agree": 5440, "shared_disagree": 5376,
                      "min_hamming": 6, "min_labels": [4, 32], "witness_hamming": 20, "helper_row_matches": 104 * 48},
        "corrected_at_witness_row386_col405": {"shared_flips_row_col": list(flips), "uniform_tag_matches_row_on_shared_line": True,
                                                "separating_cell": [2, 1], "bit": 19},
        "corrected_census_wording": "the uniform tag matches the row tag on the shared line iff the ROW label is class 3",
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
