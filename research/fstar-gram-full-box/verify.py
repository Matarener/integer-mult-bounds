#!/usr/bin/env python3
"""Exact rational witnesses and a complete three-coordinate mod-four check.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar, with substantial OpenAI Codex assistance.
The retained definition oracle is credited in SOURCES.json and README.md.
"""
from collections import Counter
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
ORACLE_SHA = "6792f0c92943e418d93ae6bc8b616447efc2a505612c87c011a36025d98f814d"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     default=str).encode()).hexdigest()


def load_oracle(corrupt=False):
    path = HERE / "inputs/independent_box.py"
    raw = path.read_bytes() + (b"\n# altered\n" if corrupt else b"")
    require(hashlib.sha256(raw).hexdigest() == ORACLE_SHA, "definition source changed")
    module = ModuleType("retained_box_definition")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def nu(value):
    value = F(value)
    require(value != 0, "zero has no finite valuation")
    a, b, result = abs(value.numerator), value.denominator, 0
    while a % 2 == 0:
        a //= 2
        result += 1
    while b % 2 == 0:
        b //= 2
        result -= 1
    return result


def two(power):
    return F(2**power) if power >= 0 else F(1, 2**(-power))


def residue(value):
    value = F(value)
    require(value.denominator % 2 == 1, "nonintegral two-adic residue")
    return value.numerator * pow(value.denominator, -1, 4) % 4


def parity_dot(a, b):
    return sum(((a >> k) & 1) * ((b >> k) & 1) for k in range(3)) % 2


def normalize(P, Q):
    P, Q = [tuple(map(F, row)) for row in P], [tuple(map(F, row)) for row in Q]
    require(P and len(P) == len(Q) and all(len(row) == 3 for row in P+Q), "three-column factors")
    M = [[sum(P[i][k]*Q[j][k] for k in range(3)) for j in range(len(P))]
         for i in range(len(P))]
    require(all(M[i][i] for i in range(len(P))), "nonzero diagonal")
    active, alpha, beta = [], {}, {}
    for k in range(3):
        left, right = [nu(row[k]) for row in P if row[k]], [nu(row[k]) for row in Q if row[k]]
        if left and right:
            active.append(k)
            alpha[k], beta[k] = min(left), min(right)
    gamma = min(alpha[k]+beta[k] for k in active)
    p = [[two(-alpha[k])*row[k] if k in active else F(0) for k in range(3)] for row in P]
    q = [[two(alpha[k]-gamma)*row[k] if k in active else F(0) for k in range(3)] for row in Q]
    A = [sum(1 << k for k in active if row[k] and nu(row[k]) == alpha[k]) for row in P]
    B = [sum(1 << k for k in active if row[k] and nu(row[k]) == gamma-alpha[k]) for row in Q]
    require(A == [sum(1 << k for k in range(3) if residue(row[k]) % 2) for row in p], "left normalization")
    require(B == [sum(1 << k for k in range(3) if residue(row[k]) % 2) for row in q], "right normalization")
    for i in range(len(P)):
        for j in range(len(P)):
            require(sum(p[i][k]*q[j][k] for k in range(3)) == two(-gamma)*M[i][j], "normalized product")
            require(parity_dot(A[i], B[j]) == residue(two(-gamma)*M[i][j]) % 2, "scope parity identity")
    return dict(P=P, Q=Q, M=M, p=p, q=q, A=A, B=B, gamma=gamma,
                tau=[(a & b).bit_count() for a, b in zip(A, B)])


def color(row, support):
    coordinates = [k for k in range(3) if support & (1 << k)]
    require(len(coordinates) == 2, "color needs two coordinates")
    value = residue(row[coordinates[0]]) * residue(row[coordinates[1]]) % 4
    require(value in (1, 3), "color needs odd coordinates")
    return 0 if value == 1 else 1


def construct(data, first, middle, last):
    A, B = data["A"], data["B"]
    a, b = A[:], B[:]
    for i in first:
        tied = A[i] & B[i]
        b[i] = tied & -tied
    for i in last:
        tied = A[i] & B[i]
        a[i] = tied & -tied
    order = first+middle+last
    return dict(a=a, b=b, kept=sorted(order), order=order)


def literal_check(data, witness):
    A, B, M = data["A"], data["B"], data["M"]
    a, b, order, kept = (witness[key] for key in ("a", "b", "order", "kept"))
    if len(a) != len(A) or len(b) != len(B) or sorted(order) != sorted(kept) or len(set(kept)) != len(kept):
        return False
    if any(a[i] & ~A[i] or b[i] & ~B[i] or parity_dot(a[i], b[i]) != 1 for i in kept):
        return False
    return all(M[i][j] != 0 or parity_dot(a[i], b[j]) == 0
               for position, i in enumerate(order) for j in order[position+1:])


def secondary(data):
    first, middle, last = [], [], []
    for i, tau in enumerate(data["tau"]):
        if tau % 2:
            middle.append(i)
        elif tau == 2 and data["A"][i] == data["B"][i] and nu(data["M"][i][i]) == data["gamma"]+1:
            (first if color(data["p"][i], data["A"][i]) == 0 else last).append(i)
    return construct(data, first, middle, last), (first, middle, last)


def gram(data):
    require(data["P"] == data["Q"], "Gram theorem requires identical factors")
    require(all(data["tau"]), "Gram theorem requires nonempty canonical ties")
    m = min(nu(x) for row in data["P"] for x in row if x)
    R = [[two(-m)*x for x in row] for row in data["P"]]
    supports = [sum(1 << k for k in range(3) if residue(row[k]) % 2) for row in R]
    require(data["gamma"] == 2*m, "Gram gamma")
    require(supports == [a & b for a, b in zip(data["A"], data["B"])], "global odd supports equal ties")
    require(supports == data["B"], "Gram right anchors equal global odd supports")
    first, middle, last = [], [], []
    for i, support in enumerate(supports):
        if support.bit_count() % 2:
            middle.append(i)
        else:
            require(nu(data["M"][i][i]) == 2*m+1, "two-odd-squares valuation")
            (first if color(R[i], support) == 0 else last).append(i)
    return construct(data, first, middle, last), (first, middle, last)


def crosscheck(oracle, data, witness):
    inherited = oracle.rational_data(data["P"], data["Q"])
    require((data["M"], data["gamma"], data["A"], data["B"], data["tau"]) ==
            (inherited["M"], inherited["gamma"], inherited["a0"], inherited["b0"], inherited["tau"]),
            "independent rational normalization disagrees")
    require(literal_check(data, witness), "literal witness rejected")
    require(oracle.check_witness(data["A"], data["B"], inherited["arcs"], witness), "definition witness rejected")
    return dict(rows=len(data["P"]), kept=len(witness["kept"]), gamma=data["gamma"],
                tau_histogram=dict(sorted(Counter(map(str, data["tau"])).items())),
                asymmetric_anchor_rows=sum(a != b for a, b in zip(data["A"], data["B"])),
                zero_arcs=len(inherited["arcs"]), matrix_sha256=digest(data["M"]),
                witness_sha256=digest(witness))


def mod_four():
    rows = []
    for p in product(range(4), repeat=3):
        support = sum(1 << k for k in range(3) if p[k] % 2)
        if support.bit_count() != 2:
            continue
        for q in product(range(4), repeat=3):
            if support != sum(1 << k for k in range(3) if q[k] % 2):
                continue
            if sum(x*y for x, y in zip(p, q)) % 4 == 2:
                rows.append((p, q, support, color(p, support)))
    histogram, same_color = Counter(), 0
    for p, _q, support, c in rows:
        for _p2, q2, support2, c2 in rows:
            value = sum(x*y for x, y in zip(p, q2)) % 4
            histogram[value] += 1
            if c == c2:
                same_color += 1
                require(value != 0, "same-color modular zero")
                require(value == 2 if support == support2 else value % 2 == 1, "mod-four pair type")
    require(len(rows) == 96 and same_color == 4608, "complete mod-four census")
    return rows, dict(rows=len(rows), ordered_pairs=len(rows)**2, same_color_pairs=same_color,
                      color_sizes=dict(Counter(str(x[3]) for x in rows)),
                      cross_dot_residues={str(k): v for k, v in sorted(histogram.items())},
                      rows_sha256=digest(rows))


def reject(call, fragment):
    try:
        call()
    except ValueError as error:
        require(fragment in str(error), "unexpected negative control: "+str(error))
        return
    raise ValueError("accepted negative control: "+fragment)


def main():
    oracle = load_oracle()
    reject(lambda: load_oracle(True), "definition source changed")
    rows, modular = mod_four()
    fixtures = {}
    corpus = [row for row in product(range(-2, 3), repeat=3) if any(x % 2 for x in row)]
    gram_cases = {"signed98": corpus,
                  "odd_denominators98": [[F(x, (3, 5, 7)[i % 3]) for x in row] for i, row in enumerate(corpus)],
                  "column_scaled": [[F(row[k])*(1, 1, 2)[k] for k in range(3)]
                                    for row in ((1,1,1), (1,-1,2), (1,0,3), (0,1,1))],
                  "mismatched_anchors": [(1,1,2), (1,-1,0)],
                  "inactive_columns": [(1,1,0), (1,-1,0), (-3,1,0)]}
    for scale in (F(1, 8), F(-4, 15), F(6, 7)):
        gram_cases["global_scale_"+str(scale)] = [[scale*x for x in row] for row in corpus]
    for name, P in gram_cases.items():
        data = normalize(P, P)
        witness, blocks = gram(data)
        fixtures[name] = {**crosscheck(oracle, data, witness), "blocks": list(map(len, blocks))}
        require(len(witness["kept"]) == len(P), "Gram witness is not full")
    centered = lambda x: -1 if x == 3 else x
    P = [[centered(x) for x in row[0]] for row in rows]
    Q = [[centered(x) for x in row[1]] for row in rows]
    odd = [(1,0,0), (0,1,0), (0,0,1), (1,1,1)]
    P += odd
    Q += odd
    for name, left, right in (
        ("matched100", P, Q),
        ("contravariant_columns100", [[F(x)*s for x, s in zip(row, (F(1,4), 2, 8))] for row in P],
         [[F(x)/s for x, s in zip(row, (F(1,4), 2, 8))] for row in Q]),
        ("asymmetric_global_scales100", [[F(5,12)*x for x in row] for row in P],
         [[F(-9,10)*x for x in row] for row in Q])):
        data = normalize(left, right)
        witness, blocks = secondary(data)
        fixtures[name] = {**crosscheck(oracle, data, witness), "blocks": list(map(len, blocks))}
        require(len(witness["kept"]) == 100, "matched corpus retention")

    # Higher cancellation defeats a full-box conclusion even with matched anchors.
    P = [(1,1,0), (1,5,2), (1,17,4), (1,0,1)]
    Q = [(-7,-1,6), (1,-1,4), (1,-1,2), (1,0,1)]
    high = normalize(P, Q)
    require(high["A"] == high["B"] == [3,3,3,5] and high["gamma"] == 0, "higher-cancellation anchors")
    hdata = oracle.rational_data(P, Q)
    maximum, h_witness = oracle.maximum_box(hdata["a0"], hdata["b0"], hdata["arcs"])
    require(maximum == 3, "higher-cancellation maximum")
    require(literal_check(high, h_witness), "independent higher-cancellation maximum witness")
    rejected_full = construct(high, [0,1,2,3], [], [])
    require(not literal_check(high, rejected_full), "missing valuation assumption accepted")
    retained, blocks = secondary(high)
    require(retained["kept"] == [3], "higher-cancellation filtering")
    fixtures["higher_cancellation"] = {**crosscheck(oracle, high, retained), "exact_maximum": maximum,
                                       "maximum_witness": h_witness, "diagonal": [str(high["M"][i][i]) for i in range(4)]}
    mixed = normalize(P+[(0,0,1)], Q+[(0,0,1)])
    retained, blocks = secondary(mixed)
    require(retained["kept"] == [3,4], "good-plus-odd partial retention")
    fixtures["good_odd_and_excluded"] = {**crosscheck(oracle, mixed, retained), "blocks": list(map(len, blocks))}

    # Existing asymmetric core: symmetry/positive definiteness of M is insufficient.
    P = [(-1,-3,0), (1,-1,-2), (3,3,3)]
    Q = [(1,-3,2), (3,-1,-2), (3,-1,2)]
    spd = normalize(P, Q)
    reject(lambda: gram(spd), "identical factors")
    old = oracle.rational_data(P, Q)
    maximum, old_witness = oracle.maximum_box(old["a0"], old["b0"], old["arcs"])
    require(maximum == 2 and spd["M"] == [[F(8),F(0),F(0)], [F(0),F(8),F(0)], [F(0),F(0),F(12)]], "retained SPD core")
    require(literal_check(spd, old_witness), "independent retained SPD maximum witness")
    fixtures["symmetric_matrix_not_Gram_factors"] = {"exact_maximum": maximum, "witness": old_witness,
                                                    "matrix_sha256": digest(spd["M"])}
    empty = normalize([(1,0,0), (2,0,0)], [(1,0,0), (2,0,0)])
    reject(lambda: gram(empty), "nonempty canonical ties")
    e = oracle.rational_data(empty["P"], empty["Q"])
    require(oracle.maximum_box(e["a0"], e["b0"], e["arcs"])[0] == 1, "empty tie maximum")
    fixtures["empty_tie"] = {"tau": empty["tau"], "exact_maximum": 1}

    # Semantic mutations on actual orthogonal Gram rows, not fabricated hashes.
    control = normalize([(1,1,2), (1,-1,0)], [(1,1,2), (1,-1,0)])
    witness, blocks = gram(control)
    wrong_color = construct(control, [0,1], [], [])
    wrong_labels = dict(witness, a=control["A"][:], b=control["B"][:])
    wrong_order = dict(witness, order=list(reversed(witness["order"])))
    for mutant in (wrong_color, wrong_labels, wrong_order):
        require(not literal_check(control, mutant), "semantic witness mutation accepted")
    reject(lambda: residue(F(1,2)), "nonintegral two-adic residue")
    # A global half-scale must be removed before taking residues; using raw P fails.
    reject(lambda: color((F(1,2), F(1,2), 0), 3), "nonintegral two-adic residue")
    result = dict(schema_version=1, oracle_sha256=ORACLE_SHA, modular=modular, fixtures=fixtures,
                  controls=["source-byte corruption", "missing valuation condition", "symmetric M is not P=Q",
                            "empty canonical tie", "wrong color", "full even labels", "reversed block order",
                            "nonintegral residue", "omitted global scaling"],
                  limitations=["finite arithmetic corroboration plus explicit witnesses; universal result is in PROOF.md",
                               "no Gram restriction imposed on general frontier", "no selected frontier or kappa change"])
    if "--emit" in sys.argv:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "retained receipt mismatch")
        print("PASS: 96 modular types, 9216 ordered pairs, rational Gram/partial witnesses and semantic controls")


if __name__ == "__main__":
    main()
