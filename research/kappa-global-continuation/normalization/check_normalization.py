#!/usr/bin/env python3
"""Exact obstruction and rational alternative for symmetric helper normalization.

Apache-2.0. Substantial OpenAI assistance under the user's direction.
This is a local algebraic certificate, not a native consumer or a new kappa.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


def mul(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def tr(a):
    return list(map(list, zip(*a)))


def eye(n, scale=1):
    return [[scale*int(i == j) for j in range(n)] for i in range(n)]


def determinant(a):
    a = [[F(x) for x in row] for row in a]
    out = F(1)
    for j in range(len(a)):
        p = next((i for i in range(j, len(a)) if a[i][j]), None)
        if p is None:
            return F(0)
        if p != j:
            a[p], a[j] = a[j], a[p]
            out = -out
        v = a[j][j]
        out *= v
        for i in range(j+1, len(a)):
            t = a[i][j]/v
            a[i] = [x-t*y for x, y in zip(a[i], a[j])]
    return out


# F9 = F3[i], i^2 = -1. The transpose in the proof is bilinear.
def fadd(a, b):
    return ((a[0]+b[0]) % 3, (a[1]+b[1]) % 3)


def fmul(a, b):
    return ((a[0]*b[0]-a[1]*b[1]) % 3,
            (a[0]*b[1]+a[1]*b[0]) % 3)


def finv(a):
    norm = (a[0]*a[0]+a[1]*a[1]) % 3
    need(norm != 0, "nonzero F9 element")
    inv = pow(norm, -1, 3)
    return (a[0]*inv % 3, -a[1]*inv % 3)


def frank(a):
    a = [[tuple(x) for x in row] for row in a]
    r = 0
    for j in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][j] != (0, 0)), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        u = finv(a[r][j])
        a[r] = [fmul(u, x) for x in a[r]]
        for i in range(len(a)):
            if i != r:
                q = a[i][j]
                a[i] = [fadd(x, fmul((-q[0] % 3, -q[1] % 3), y))
                        for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def fgram(a):
    rows = []
    for row in a:
        out = []
        for other in a:
            x = (0, 0)
            for u, v in zip(row, other):
                x = fadd(x, fmul(u, v))
            out.append(x)
        rows.append(out)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--followup", required=True, type=Path,
                        help="Authenticated kappa-consumer-followup package directory")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("RESULT.json"))
    args = parser.parse_args()
    package = args.followup.resolve()
    artifact = package / "artifact"
    base = artifact / "recovered-involutory"
    component_path = base / "modern_native_component.py"
    c = module(component_path, "normalization_source_component")
    inp = base / "modern-source/inputs"
    receipt_path = inp / "NATIVE-RECEIPT.json"
    need(c.digest(receipt_path) == c.NATIVE_RECEIPT_SHA, "native receipt source pin")
    sources = {"component": c.digest(component_path), "receipt": c.digest(receipt_path)}
    provider_checks = {}
    pivots = (224, 225, 227, 229, 240, 241, 256, 257)
    for name, item in c.read(receipt_path)["providers"].items():
        local = inp / "native-cache" / item["word_sha256"] / "local"
        for filename in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            need(c.digest(local/filename) == item["complete_native_files"]["local/"+filename],
                 "native payload pin")
        word = c.read(local/"CANONICAL-WORD.json.gz")
        programs = c.read(local/"LOCAL-PROGRAMS.json.gz")
        R, K, P, J, _, _ = c.clean_reconstruction(word, programs)
        rt = [{k: R[k][p] for k in range(8) if p in R[k]} for p in range(112)]
        need(c.matmul(R, rt) == [{i: F(56)} for i in range(8)], "actual RR^T=56I")
        need(K == [{k: x/4 for k, x in row.items()} for row in rt], "actual K=R^T/4")
        before = c.replay(programs["forward"][:programs["forward"].index(["phase", "centers"])])
        H = [{j: x for (j, w), x in before["L", p].items() if j >= 224 and not w}
             for p in word["centers"]]
        hminor = [[H[i].get(p, F(0)) for p in pivots] for i in range(8)]
        det = determinant(hminor)
        need(det and abs(det.numerator) & (abs(det.numerator)-1) == 0
             and det.denominator & (det.denominator-1) == 0,
             "actual H has a Gaussian-dyadic unit minor")
        reduced = [[(int(x.numerator*pow(x.denominator, -1, 3)) % 3, 0) for x in row]
                   for row in hminor]
        need(frank(reduced) == 8, "H retains row rank8 modulo3")
        provider_checks[name] = {"word_sha256": item["word_sha256"],
            "RR_transpose": "56 I8", "H_pivots": list(pivots),
            "H_minor_determinant": str(det), "H_mod3_rank": 8}

    # Existing 16-column solution [4I,8iI] has full row rank even modulo3.
    a16 = [[((1 if j == i else 0), 0) if j < 8
            else (0, (2 if j-8 == i else 0)) for j in range(16)] for i in range(8)]
    need(frank(a16) == 8, "16-column witness independent rows")
    need(fgram(a16) == [[(0, 0)]*8 for _ in range(8)], "16-column witness isotropic")
    # The counting bound uses rank(A)=8 and row(A) subset row(A)^perp.
    excluded_sizes = [k for k in range(16) if 8 > k-8]
    need(excluded_sizes == list(range(16)), "all fewer-than16 column sizes excluded")

    # A smaller *rational*, not Gaussian-dyadic-unimodular, factor is possible.
    # B is left multiplication by quaternion 1+i+j, as a real 4x4 matrix.
    b4 = [[1, -1, -1, 0], [1, 1, 0, 1], [1, 0, 1, -1], [0, -1, 1, 1]]
    need(mul(b4, tr(b4)) == eye(4, 3), "quaternion norm3")
    b8 = [[b4[i % 4][j % 4] if i//4 == j//4 else 0 for j in range(8)] for i in range(8)]
    a8_imag = [[4*x for x in row] for row in b8]
    need(mul(a8_imag, tr(a8_imag)) == eye(8, 48), "A8 A8^T=−48I with imaginary factor")
    # A8 = 4i B8, A8^-1 = -i B8^T/12. Every nonzero inverse entry requires3.
    inv_imag = [[-F(x, 12) for x in row] for row in tr(b8)]
    need(mul(a8_imag, inv_imag) == eye(8, -1), "Gaussian rational inverse")
    det_a8 = determinant(a8_imag)  # i^8=1.
    need(det_a8 == 2**16*3**4, "rational alternative determinant")
    a8_mod3 = [[(0, x % 3) for x in row] for row in a8_imag]
    need(frank(a8_mod3) == 4 and fgram(a8_mod3) == [[(0, 0)]*8 for _ in range(8)],
         "8-column alternative loses rank modulo3")
    # Effective controls: replacing i by1 destroys isotropy; claiming inverse
    # dyadic destroys denominator admission; dropping a witness column destroys Gram zero.
    real_mutant = [[(x[0] if x[0] else x[1], 0) for x in row] for row in a16]
    need(fgram(real_mutant) != [[(0, 0)]*8 for _ in range(8)], "phase replacement control")
    need(any(x.denominator % 3 == 0 for row in inv_imag for x in row if x),
         "odd denominator control")
    need(fgram([row[:-1] for row in a16]) != [[(0, 0)]*8 for _ in range(8)],
         "missing column control")
    out = {"status": "PASS_SYMMETRIC_NORMALIZATION_SIZE_OBSTRUCTION",
        "scope": "Helper-only invertible Gaussian-dyadic normalization HB=[A,0], symmetric reflection D=I−Q^TQ/4, and required112-data block J. This is not a bound on arbitrary changed contracts.",
        "sources": sources, "providers": provider_checks,
        "theorem": {"coefficient_ring": "Z[1/2,i]", "residue_field": "F9=F3[i]",
            "required_extra_Gram": "A A^T=−48 I8", "required_extra_row_rank_mod3": 8,
            "argument": "Invertible helper normalization preserves row rank of H modulo3; AA^T=0 makes row(A) an8-dimensional totally isotropic subspace of the nondegenerate k-dimensional bilinear dot space, so8≤k−8.",
            "minimum_extra_source_ports": 16, "minimum_symmetric_source_ports": 128,
            "16_column_witness_mod3_rank": frank(a16), "excluded_extra_counts": excluded_sizes},
        "rational_eight_port_alternative": {"A_imaginary_integer_matrix": a8_imag,
            "A_inverse_imaginary_matrix": [[str(x) for x in row] for row in inv_imag],
            "AA_transpose": "−48 I8", "determinant": str(det_a8), "mod3_rank": frank(a8_mod3),
            "arithmetic_change": "Requires division by3. The reflection matrix itself is Gaussian dyadic, but invertible helper normalization/denormalization is not.",
            "construction_scope": "Exact matrix factor and normalization feasibility over Q(i); no literal120-port native program or global consumer emitted."},
        "rejection_controls": ["replace_imaginary_factor", "pretend_inverse_dyadic", "omit_last_witness_column"]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2)+"\n")
    print(out["status"], "minimum_extra_ports=16", "rational8_requires_division3", flush=True)


if __name__ == "__main__":
    main()
