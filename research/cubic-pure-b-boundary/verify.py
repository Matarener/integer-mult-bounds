#!/usr/bin/env python3
"""Finite exact certificates for cubic repairs containing an entry-b cube.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
PR6212 supplies the preceding dyadic repair results, retaining Nick Petalas's
PR6200 contract and the Sricharan Vagvala/Adam Gall/Hanson Sun lineage.
No predecessor executable is imported. Universal claims rest on PROOF.md;
this program distinguishes full original-child replays from closed-defect
fixtures and classifies each query in entry-source coordinates.
"""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


SOURCE_HEAD = "9c159482e0495b6a97e17e629debe66a0ceb9466"
THREE_RESIDUES = {0, 1, 2, 5, 8}
ENTRY = ((1, 0, 0, 0, 0), (1, 0), (0, 1))
IDENTITY = ((1, 0), (0, 1))
# Output basis: y_entry,a_entry^3,a_entry^2*b_entry,a_entry*b_entry^2,b_entry^3.
# Source vectors use the ordered basis a_entry,b_entry.


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_sources(package):
    manifest = json.loads((package / "SOURCE-PINS.json").read_text())
    need(manifest["schema_version"] == 1, "source schema")
    need(manifest["predecessor"] == {
        "pr": "https://github.com/CrocSwap/integer-mult-bounds/pull/6212",
        "head": SOURCE_HEAD, "author": "apoursh", "license": "Apache-2.0",
    }, "exact predecessor identity")
    documents = manifest["documents"]
    need(len(documents) == 1 and documents[0]["path"] == "sources/pr6212-PROOF.md",
         "one exact predecessor proof")
    item = documents[0]
    source_path = "research/dyadic-cubic-repair/PROOF.md"
    need(item["source_path"] == source_path, "predecessor source path")
    need(item["source_url"] == "https://raw.githubusercontent.com/"
         f"apoursh/integer-mult-bounds/{SOURCE_HEAD}/{source_path}", "exact-head source URL")
    path = (package / item["path"]).resolve()
    need(path.is_relative_to(package), "source path inside package")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    need(digest == item["sha256"], "source digest: " + item["path"])
    return {item["path"]: digest}


def add(left, right):
    return tuple(a+b for a, b in zip(left, right, strict=True))


def dyadic(value):
    need(isinstance(value, (int, Fraction)), "exact rational scalar")
    denominator = Fraction(value).denominator
    return denominator & (denominator-1) == 0


def determinant(matrix):
    return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]


def frame_inverse(matrix):
    need(len(matrix) == 2 and all(len(row) == 2 for row in matrix), "two-source frame shape")
    need(all(dyadic(value) for row in matrix for value in row), "dyadic frame entries")
    det = determinant(matrix)
    need(det != 0 and dyadic(Fraction(1)/det), "source frame invertible over dyadics")
    a, b = matrix[0]
    c, d = matrix[1]
    return ((Fraction(d)/det, -Fraction(b)/det), (-Fraction(c)/det, Fraction(a)/det))


def frame_apply(matrix, a, b):
    return tuple(add(tuple(row[0]*x for x in a), tuple(row[1]*x for x in b))
                 for row in matrix)


def weighted_cube(weight, form):
    a, b = form
    return (0, weight*a**3, 3*weight*a*a*b, 3*weight*a*b*b, weight*b**3)


def run(events, state=ENTRY):
    output, a, b = state
    queries = []
    for opcode, payload, label in events:
        if opcode == "shear":
            need(dyadic(payload) and payload != 0, "nonzero dyadic shear")
            a = add(a, tuple(payload*x for x in b))
        elif opcode == "frame":
            frame_inverse(payload)
            a, b = frame_apply(payload, a, b)
        elif opcode == "cube":
            source, weight = payload
            need(source in ("a", "b"), "cube reads a source register")
            need(dyadic(weight) and weight != 0, "nonzero dyadic query weight")
            form = a if source == "a" else b
            output = add(output, weighted_cube(weight, form))
            queries.append((weight, form, source, label))
        else:
            raise ValueError("event outside declared source/query alphabet")
    return (output, a, b), queries


def inverse(events):
    result = []
    for opcode, payload, label in reversed(events):
        if opcode == "frame":
            result.append((opcode, frame_inverse(payload), label))
        elif opcode == "shear":
            result.append((opcode, -payload, label))
        elif opcode == "cube":
            result.append((opcode, (payload[0], -payload[1]), label))
        else:
            raise ValueError("event outside declared source/query alphabet")
    return result


def pure_entry_b(queries):
    return [query for query in queries if query[0] != 0 and query[1][0] == 0
            and query[1][1] != 0]


def moments(r):
    need(isinstance(r, int) and r >= 3, "arity at least three")
    return r*(r-1)//2, r*(r-1)*(2*r-1)//6


def endpoint(r):
    return ((1, r, 0, 0, 0), ENTRY[1], ENTRY[2])


def drifting_endpoint(r):
    first, second = moments(r)
    return ((1, r, 3*first, 3*second, first*first), (1, r), (0, 1))


def original_children(r):
    return [event for i in range(r) for event in (
        ("cube", ("a", 1), f"child-{i}-read"),
        ("shear", 1, f"child-{i}-shift"))]


def eager_program(r):
    return [event for i in range(r) for event in (
        ("cube", ("a", 1), f"child-{i}-read"),
        ("shear", 1, f"child-{i}-shift"),
        ("shear", -1, f"eager-{i}-restore"))]


def high_class_repair(r):
    need(r % 9 in (0, 1), "high-class residue")
    first, _ = moments(r)
    epsilon = -1 if r % 9 == 0 else 1
    q = (r if epsilon == -1 else r-1)//3
    need(first % 9 == 0, "integer nonmonic query weight")
    weight, pure_weight = first//9, first*(3*first-1)//9
    matrix = ((3, epsilon), (1, 0))
    undo = ((0, 1), (epsilon, -3*epsilon))
    need(frame_inverse(matrix) == undo, "literal unimodular inverse")
    return [
        ("shear", q-r, "repair-first-source"),
        ("cube", ("a", epsilon*3*first), "repair-monic-query"),
        ("frame", matrix, "repair-nonmonic-frame"),
        ("cube", ("a", -epsilon*weight), "repair-nonmonic-query"),
        ("frame", undo, "repair-undo-frame"),
        ("shear", -q, "repair-final-source"),
        ("cube", ("b", -pure_weight), "repair-entry-b-query"),
    ]


def old_three_repair(r):
    need(r % 3 == 2, "old three-query residue")
    first, _ = moments(r)
    t, s = (r+1)//3, (r-2)//3
    numerator = first*(r-2)*(r+1)
    need(numerator % 6 == 0, "integer old pure-b weight")
    return [
        ("shear", t-r, "repair-first-source"),
        ("cube", ("a", -first), "repair-first-query"),
        ("shear", s-t, "repair-second-source"),
        ("cube", ("a", first), "repair-second-query"),
        ("shear", -s, "repair-final-source"),
        ("cube", ("b", -numerator//6), "repair-entry-b-query"),
    ]


def four_repair(r):
    first, second = moments(r)
    need((first-second) % 2 == 0, "integer universal weights")
    return [
        ("shear", 1-r, "repair-first-source"),
        ("cube", ("a", -(first+second)//2), "repair-first-query"),
        ("shear", -2, "repair-second-source"),
        ("cube", ("a", -(second-first)//2), "repair-second-query"),
        ("shear", 1, "repair-final-source"),
        ("cube", ("a", second), "repair-third-query"),
        ("cube", ("b", -(first*first-first)), "repair-entry-b-query"),
    ]


def selected_repair(r):
    moments(r)
    if r % 9 in (0, 1):
        return high_class_repair(r), "new-three"
    if r % 3 == 2:
        return old_three_repair(r), "old-three"
    return four_repair(r), "four"


def check_program(r, expand_children):
    repair, kind = selected_repair(r)
    drift = drifting_endpoint(r)
    final, queries = run(repair, drift)
    need(final == endpoint(r), "arbitrary-input repaired endpoint")
    need(run(inverse(repair), final)[0] == drift, "exact repair inverse")
    need(len(pure_entry_b(queries)) == 1, "one nonzero cube of entry b")
    expected = 3 if r % 9 in THREE_RESIDUES else 4
    need(len(queries) == expected, "predicted nonzero query count")
    shears = sum(event[0] == "shear" for event in repair)
    frames = sum(event[0] == "frame" for event in repair)
    need((shears, frames) == ((2, 2) if kind == "new-three" else (3, 0)),
         "complete logical source-event count")
    need(all(Fraction(query[0]).denominator == 1 for query in queries), "integer query attainment")
    if kind == "new-three":
        after_frame = run(repair[:3], drift)[0]
        need(after_frame[2] != ENTRY[2], "nonmonic frame really changes b temporarily")
        need(run(repair[:5], drift)[0][2] == ENTRY[2], "inverse frame restores entry b")
    if expand_children:
        children = original_children(r)
        need(run(children)[0] == drift, "literal retained-child chronology")
        program = children+repair
        need(program[:2*r] == children, "all original children retained unchanged")
        need(run(program)[0] == final, "full retained-child program")
        need(run(eager_program(r))[0] == final, "exact eager comparison")
        need(run(inverse(program), final)[0] == ENTRY, "literal full-program inverse")
    return {"kind": kind, "queries": len(queries), "shears": shears, "frames": frames}


def divided_moments(values):
    gamma, alpha, beta, delta, eta, theta = values
    return ((gamma*alpha**3 + delta*eta**3) % 3,
            (gamma*alpha*alpha*beta + delta*eta*eta*theta) % 3,
            (gamma*alpha*beta*beta + delta*eta*theta*theta) % 3)


def modular_certificate():
    tested, antecedents = 0, 0
    for values in itertools.product(range(3), repeat=6):
        zeroth, first, second = divided_moments(values)
        tested += 1
        if zeroth == first == 0:
            antecedents += 1
            need(second == 0, "two forms: M0=M1=0 implies M2=0 modulo three")
    need(tested == 729, "complete six-variable residue census")
    targets = []
    for r in range(3, 257):
        first, second = moments(r)
        blocked = first % 3 == 0 and second % 3 != 0
        need(blocked == (r % 9 not in THREE_RESIDUES), "exact obstruction residue pattern")
        if blocked:
            targets.append(r)
    return {"residue_assignments": tested, "antecedent_assignments": antecedents,
            "excluded_arities_in_scan": len(targets), "excluded_residues": [3, 4, 6, 7]}


def expect_rejected(function, diagnostic):
    try:
        function()
    except ValueError as error:
        need(str(error) == diagnostic, "specific mutation diagnostic")
    else:
        raise ValueError("mutation unexpectedly accepted: " + diagnostic)


def mutation_controls():
    r, drift = 10, drifting_endpoint(10)
    repair = high_class_repair(r)
    expect_rejected(lambda: run([("frame", ((3, 1), (6, 2)), "singular")], drift),
                    "source frame invertible over dyadics")
    expect_rejected(lambda: run([("frame", ((3, 0), (0, 1)), "nonunit")], drift),
                    "source frame invertible over dyadics")
    wrong_inverse = repair[:]
    wrong_inverse[4] = ("frame", ((0, 1), (1, -2)), "wrong-inverse")
    need(run(wrong_inverse, drift)[0] != endpoint(r), "wrong inverse rejected")
    need(run(repair[:2]+repair[3:], drift)[0] != endpoint(r), "dropped forward frame rejected")
    no_inverse, queries = run(repair[:4]+repair[5:], drift)
    need(no_inverse[2] != ENTRY[2] and not pure_entry_b(queries), "temporary b must be restored")
    no_shear = run(repair[:5]+repair[6:], drift)[0]
    need(no_shear[0] == endpoint(r)[0] and no_shear[1] != ENTRY[1], "final source shear necessary")
    no_b, queries = run(repair[:-1], drift)
    need(no_b[1:] == ENTRY[1:] and no_b[0] != endpoint(r)[0] and not pure_entry_b(queries),
         "nonzero entry-b correction necessary")
    moved_b = repair[:3]+[repair[-1]]+repair[3:-1]
    wrong_output, queries = run(moved_b, drift)
    need(wrong_output[1:] == ENTRY[1:] and wrong_output[0] != endpoint(r)[0],
         "current-b query is not necessarily an entry-b query")
    need(any(query[2] == "b" for query in queries) and not pure_entry_b(queries),
         "entry-coordinate pure-b classification")
    _, swapped = run([("frame", ((0, 1), (1, 0)), "swap"),
                      ("cube", ("a", 1), "entry-b-via-a")])
    need(len(pure_entry_b(swapped)) == 1, "entry-b can be held in current a")
    changed_weight = repair[:]
    changed_weight[3] = ("cube", ("a", repair[3][1][1]+1), "wrong-weight")
    need(run(changed_weight, drift)[0] != endpoint(r), "nonmonic weight mutation")
    children = original_children(r)
    need(run(children[1:]+repair)[0] != endpoint(r), "all original cube calls necessary")
    need(run([children[1], children[0], *children[2:], *repair])[0] != endpoint(r),
         "read-then-shear chronology necessary")
    need(divided_moments((1, 1, 0, 2, 1, 1)) == (0, 2, 2), "first moment cannot be omitted")
    need(divided_moments((1, 1, 1, 1, 1, 2)) == (2, 0, 2), "zeroth moment cannot be omitted")
    first, second = moments(3)
    need((3*first) % 3 == (3*second) % 3 == (first*first) % 3 == 0 and second % 3 != 0,
         "raw coefficient reduction loses the divided-moment obstruction")
    unrestricted = [("shear", -2, "outside-class"), ("cube", ("a", -1), "outside-class"),
                    ("shear", 1, "outside-class"), ("cube", ("a", -1), "outside-class"),
                    ("shear", -2, "outside-class"), ("cube", ("a", 2), "outside-class")]
    result, queries = run(unrestricted, drifting_endpoint(3))
    need(result == endpoint(3) and len(queries) == 3 and not pure_entry_b(queries),
         "unrestricted r3 three-query repair is outside the pure-b class")
    expect_rejected(lambda: moments(2), "arity at least three")
    return ["singular-frame", "nonunit-determinant", "wrong-frame-inverse",
            "dropped-forward-frame", "unrestored-temporary-b", "omitted-final-source-shear",
            "omitted-entry-b-correction", "current-b-versus-entry-b", "entry-b-in-current-a",
            "nonmonic-query-weight", "omitted-original-reader", "reversed-child-chronology",
            "missing-first-moment", "missing-zeroth-moment", "raw-versus-divided-moments",
            "unrestricted-r3-outside-class", "arity-two-outside-domain"]


def main():
    package = Path(__file__).resolve().parent
    hashes = authenticate_sources(package)
    counts = {"new-three": 0, "old-three": 0, "four": 0}
    original_count = 0
    for r in range(3, 257):
        receipt = check_program(r, expand_children=True)
        counts[receipt["kind"]] += 1
        original_count += r
    large = []
    for r in range(1_000_000, 1_000_009):
        large.append({"r": r, **check_program(r, expand_children=False)})
    modular = modular_certificate()
    controls = mutation_controls()
    print("PASS_CUBIC_PURE_B_BOUNDARY " + json.dumps({
        "source_head": SOURCE_HEAD, "source_sha256": hashes,
        "full_program_scan": {"first": 3, "last": 256, "count": 254},
        "programs_by_construction": counts, "retained_original_children": original_count,
        "large_closed_defect_only": large, "modular_divided_moment_certificate": modular,
        "controls": controls, "nonzero_entry_b_queries_per_repair": 1,
        "new_three_event_bill": {"cube_queries": 3, "shears": 2, "frames": 2},
        "scope": "finite certificates; universal restricted-class proof is in PROOF.md",
        "no_unrestricted_rank_or_backend_saving_claim": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
