#!/usr/bin/env python3
"""Exact private-frame transport and restricted coded-wrapper controls.

Only the standard library is used. Default operation compares a saved receipt;
--output explicitly writes a receipt. No compiler or supplier admission.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import argparse
import ast
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PINS = {
    "inputs/GEOMETRY.json.gz":
        "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
    "inputs/global_k.py.txt":
        "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8",
    "composition/inputs/CODED-WORD.json.gz":
        "1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870",
    "composition/PRIVATE-MOVE-control.py.txt":
        "d3a93e54bb7d333b73917586407d11674d38b5c3fda4fbdc436fb5293ae7786a",
    "composition/PRIVATE-MOVE-episode.py.txt":
        "38f79cb2a370548471063952d5f7c74bd795a2a8496fdcf3ce0996d79e3adaff",
    "composition/PRIVATE-MOVE-volume.md":
        "19683df4394de299cbd7e1cce39bf9434ad260b1a37006587cf9aed84c9c0a03",
    "composition/PRIVATE-MOVE-native-closure.md":
        "74cc8de20f21acb5123fe2d20996fe0925ea6e51b3dec633bd5221fb719b3344",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(relative):
    raw = (ROOT / relative).read_bytes()
    need(sha256(raw).hexdigest() == PINS[relative], "Source pin: " + relative)
    return json.loads(gzip.decompress(raw)) if relative.endswith(".gz") else raw.decode()


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def add(a, b, coefficient=1):
    return [[x + coefficient*y for x, y in zip(r, s)] for r, s in zip(a, b)]


def mm(a, b):
    return [[sum(x*y for x, y in zip(r, c)) for c in zip(*b)] for r in a]


def rref(rows):
    basis = {}
    for row in rows:
        row = list(map(Q, row))
        for p, old in sorted(basis.items()):
            c = row[p]
            row = [x-c*y for x, y in zip(row, old)]
        p = next((p for p, x in enumerate(row) if x), None)
        if p is not None:
            c = row[p]
            basis[p] = [x/c for x in row]
    return basis


def normal(lines):
    basis = rref(lines)
    if len(basis) != 7:
        return None
    p = next(p for p in range(8) if p not in basis)
    result = [Q(0)]*8
    result[p] = Q(1)
    for p, row in sorted(basis.items(), reverse=True):
        result[p] = -sum(x*y for x, y in zip(row, result))
    need(all(sum(x*y for x, y in zip(row, result)) == 0 for row in lines),
         "Exact hyperplane normal")
    return result


def outer(x, y):
    return [[a*b for b in y] for a in x]


def dot(x, y):
    return sum(a*b for a, b in zip(x, y))


def scale(a, c):
    return [[x*c for x in row] for row in a]


def cap(n):
    return add(eye(8), scale(outer(n, n), -1/dot(n, n)))


def intersection(n, m):
    nn, nm, mm_ = dot(n, n), dot(n, m), dot(m, m)
    determinant = nn*mm_-nm*nm
    need(determinant > 0, "Distinct rational hyperplanes")
    complement = add(scale(outer(n, n), mm_), scale(outer(m, m), nn))
    complement = add(complement, scale(add(outer(n, m), outer(m, n)), -nm))
    return add(eye(8), scale(complement, -1/determinant))


def swap(p):
    rest = add(eye(len(p)), p, -1)
    return [a+b for a, b in zip(rest, p)] + [a+b for a, b in zip(p, rest)]


def serial(a):
    return [[str(x) for x in row] for row in a]


def frame_checks(geometry):
    normals = {}
    for i, support in enumerate(geometry["frames"]):
        n = normal([geometry["lines"][p] for p in support])
        if n is not None:
            normals[i] = n
    need(len(normals) == 120, "Actual 120 rank-seven frame closures")
    examples = []
    for other in (511, 512):
        n, m = normals[510], normals[other]
        f, h, g = cap(n), cap(m), intersection(n, m)
        r, s = add(f, g, -1), add(h, g, -1)
        for name, p, dimension in (("F", f, 7), ("H", h, 7), ("G", g, 6),
                                    ("COPY", r, 1), ("MOVE", s, 1)):
            need(mm(p, p) == p and p == list(map(list, zip(*p))),
                 name + " exact orthogonal idempotent")
            need(sum(p[i][i] for i in range(8)) == dimension,
                 name + " exact rational rank")
        df, dg, dh, dr, ds = map(swap, (f, g, h, r, s))
        need(mm(dr, df) == dg, "COPY transports the whole arbitrary source")
        need(mm(ds, dg) == dh, "Private promotion preserves logical payload")
        need(mm(ds, dh) == dg, "Private inverse restores the exact copied frame")
        need(mm(ds, mm(ds, mm(dr, df))) == dg, "Complete private return")
        need(dh != dg, "Omitting return is detected on an address basis column")
        examples.append({
            "centre_frame": 510, "receiver_frame": other,
            "centre_normal": [str(x) for x in n],
            "receiver_normal": [str(x) for x in m],
            "normal_gram_determinant": str(dot(n, n)*dot(m, m)-dot(n, m)**2),
            "intersection_projector": serial(g),
            "copy_projector": serial(r), "move_projector": serial(s),
            "denominators": sorted({x.denominator for p in (g, r, s)
                                    for row in p for x in row}),
            "rank_invoice": [1, 1, 1],
            "checked_address_columns_per_identity": 16,
        })
    need(3 not in examples[0]["denominators"] and
         any(d % 3 == 0 for d in examples[1]["denominators"]),
         "Actual non-dyadic intersection control")
    f = cap(normals[510])
    full = eye(8)
    s = add(full, f, -1)
    need(mm(swap(s), swap(f)) == swap(full), "Zero-rank COPY then FULL promotion")
    need(mm(swap(s), swap(full)) == swap(f), "Paid FULL return")
    return {"rank_seven_catalogue_frames": len(normals), "examples": examples,
            "zero_copy_full_visit_invoice": [0, 1, 1]}


def original_controller_rejection(source):
    tree = ast.parse(source)
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    need(len(classes) == 1 and classes[0].name == "LocalState", "Frozen controller class")
    namespace = {"need": need}
    exec(compile(ast.Module(body=classes, type_ignores=[]), "<frozen controller>", "exec",
                 dont_inherit=True, optimize=0),
         namespace)
    call = SimpleNamespace(owners=(0, 1), start=(510, 512), reverse=False,
                           events=((2, 0, 2, 510, 636, 1, 0),
                                   (0, 2, 636, 512, 1, 0)),
                           requests=(object(), object()))
    state = namespace["LocalState"](call)
    state.accept(0)
    try:
        state.accept(1)
    except ValueError as error:
        need(str(error) == "live local destination/source role",
             "Existing ABI fails at the private destination gate")
        return str(error)
    raise ValueError("Old ABI unexpectedly admitted a private MOVE")


# A group-ring control over F2. N is involutive; C and c are mutual inverses.
# No commutation of N with C is introduced. F is factored off the active pair.
def reduce_word(word):
    out = []
    inverse = {"N": "N", "C": "c", "c": "C"}
    for letter in word:
        if out and inverse[letter] == out[-1]:
            out.pop()
        else:
            out.append(letter)
    return tuple(out)


def poly(word=""):
    return {reduce_word(word)}


ZERO = set()
ONE = poly()
NN = poly("N")
CC = poly("C")
CI = poly("c")


def pmul(a, b):
    result = set()
    for x in a:
        for y in b:
            result.symmetric_difference_update({reduce_word(x+y)})
    return result


def matmul(a, b):
    result = []
    for row in a:
        line = []
        for col in zip(*b):
            entry = set()
            for x, y in zip(row, col):
                entry.symmetric_difference_update(pmul(x, y))
            line.append(entry)
        result.append(line)
    return result


def diag(a, b):
    return [[a, ZERO], [ZERO, b]]


def wrapper_checks(word, recipe_source):
    rows = [1 << i for i in range(word["public_registers"])] + [0]
    for op, dst, src, coefficient, _frame, _phase in word["records"]:
        if op == 1 and coefficient % 2:
            rows[dst] ^= rows[src]
        elif op == 2:
            rows[-1] = rows[dst]
        elif op == 3:
            need(rows[-1] == rows[dst], "Actual copied code source retained")
            rows[-1] = 0
    need(rows[3] & 1, "Actual A[3,0] coefficient for noncommutation")
    # Geometry pins port0=2e0, port3=2e3 separately in the main checker.
    # On a port0 HEAD=e0 impulse, (NA)[3] stays HEAD=e0 while
    # (AN)[3] is TAIL=e0; the two induced VALUE permutation entries differ.
    b = [[poly("CN"), ZERO], [poly("NCN"), NN]]
    reverse = [[NN, ONE], [ZERO, poly("Nc")]]
    clean_b = [[NN, ZERO], [ONE, NN]]
    clean_reverse = [[NN, ONE], [ZERO, NN]]
    need(matmul(b, diag(poly("NcN"), ONE)) == clean_b,
         "Exact forward paid source wrapper")
    need(matmul(diag(ONE, poly("NCN")), reverse) == clean_reverse,
         "Exact inverse paid source wrapper")
    source_restored = [[NN, ZERO], [poly("NCN"), NN]]
    wrong = matmul(diag(ONE, CI), matmul(source_restored, diag(ONE, CC)))
    need(wrong != clean_b and wrong[1][1] == poly("cNC"),
         "False current-cap commutation rejected")
    z = NN ^ ONE
    allowed_forward, allowed_reverse = [], []
    for mask in range(16):
        p = [[(mask >> (2*i+j)) & 1 for j in range(2)] for i in range(2)]
        q = [[((ONE if i == j else ZERO) ^ (z if p[i][j] else ZERO))
              for j in range(2)] for i in range(2)]
        if matmul(q, b) == matmul(b, q):
            allowed_forward.append(mask)
            need(p[0][0] == 0, "No active forward-source sweep commutes through the call")
        if matmul(q, reverse) == matmul(reverse, q):
            allowed_reverse.append(mask)
            need(p[1][1] == 0, "No active inverse-source sweep commutes through the call")
    tree = ast.parse(recipe_source)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "recipe"]
    need(len(nodes) == 1, "Frozen recipe")
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<frozen recipe>", "exec",
                 dont_inherit=True, optimize=0), namespace)
    events = namespace["recipe"](4)
    tight = [{"stage": e["stage"], "pair": e["pair"],
              "bank": 2*e["pair"]+int(e["reverse"]),
              "interval": "after inverse call, before C" if e["reverse"]
                          else "after inverse C, before forward call"}
             for e in events if e["kind"] == "local"]
    need(len(tight) == 9, "Nine disjoint coded-wrapper intervals")
    return {
        "literal_code_A_3_0": 1,
        "wrong_free_wrapper_bottom_right": "C^-1 N C, not N (F factored off)",
        "paid_forward_wrapper": "diag(N C_s^-1 N,I) before B_s",
        "paid_inverse_wrapper": "diag(I,N C_s N) after R_s",
        "two_by_two_commuting_bank_masks_forward": allowed_forward,
        "two_by_two_commuting_bank_masks_inverse": allowed_reverse,
        "actual_recipe_tight_intervals": tight,
        "restricted_bank_sweep_lower_bound": 9,
        "rank_one_requests_per_whole_port_sweep": 111,
        "restricted_rank_mass_lower_bound": 999,
        "scope": "Fixed ordered barriers: retain the chronological order of both "
                 "coded calls and individual C_s or inverse-C_s factors; move, "
                 "combine and cancel only N sweeps. Scalar bank changes transport "
                 "P and the boundary functional. No reordering code factors or "
                 "commuting across composite barrier products. Not a minimum for "
                 "changed calls, partial-port queries, or general routed repairs.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sources = {name: read(name) for name in PINS}
    geometry = sources["inputs/GEOMETRY.json.gz"]
    need(geometry["lines"][0] == [2, 0, 0, 0, 0, 0, 0, 0] and
         geometry["lines"][3] == [0, 0, 0, 2, 0, 0, 0, 0],
         "Actual noncommuting port roots")
    a = lambda r: 0 if r == 0 else 2*(r*(127-r)+4096)
    output = {
        "status": "PASS_PRIVATE_FRAME_TRANSPORT_AND_RESTRICTED_WRAPPER_CONTROLS",
        "no_new_kappa": True,
        "source_pins": PINS,
        "private_operator_checks": frame_checks(geometry),
        "existing_controller_rejection": original_controller_rejection(
            sources["composition/PRIVATE-MOVE-control.py.txt"]),
        "rank_three_invoice": {"rank_histogram": {"1": 3}, "positive_requests": 3,
                               "good_adapter_slots_per_f": 3*a(1),
                               "reference_rank7_adapter_slots_per_f": a(7),
                               "additional_adapter_slots_per_f": 3*a(1)-a(7),
                               "additional_bad_allowance": "2 * 10^-16 * 131072"},
        "zero_copy_full_invoice": {"rank_histogram": {"1": 2}, "positive_requests": 2,
                                  "good_adapter_slots_per_f": 2*a(1),
                                  "additional_adapter_slots_per_f": 2*a(1)-a(7)},
        "wrapper_controls": wrapper_checks(
            sources["composition/inputs/CODED-WORD.json.gz"],
            sources["inputs/global_k.py.txt"]),
        "limits": [
            "Fresh private workspace; arbitrary ordinary source/helper payloads.",
            "No emitted extended controller, request provider or physical supplier.",
            "Non-dyadic G=F intersect H can exclude q=3; fixed q>2^80 is sufficient "
            "for the displayed rational examples.",
            "The same-query receiver floor is proved in construction/PROOF.md.",
            "No rounded precision, whole-storage or outer-recurrence admission.",
        ],
    }
    receipt = json.dumps(output, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(receipt)
    else:
        need((HERE / "PRIVATE-MOVE-RESULT.json").read_text() == receipt,
             "Saved private-MOVE receipt differs from exact recomputation")
    print(json.dumps({"status": output["status"], "no_new_kappa": True,
                      "restricted_wrapper_rank_mass": 999}, sort_keys=True))


if __name__ == "__main__":
    main()
