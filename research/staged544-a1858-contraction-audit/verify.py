#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent cleanup certificate for the PR #3998 A1858 contraction.

Does not import that package. The four frozen words are authenticated by SHA256,
then the literal triple, its two-ADD image, and the derived cleanup edit are
recomputed here.
"""
import gzip
import hashlib
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
V = 112
N = 704
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
TRIPLE = [
    ["add", 457, 475, -1, 1, [82, 42]],
    ["add", 456, 457, 1, 1, [82, 42]],
    ["add", 456, 475, 1, 1, [82, 42]],
]
PAIR = [
    ["add", 456, 457, 1, 1, [82, 42]],
    ["add", 457, 475, -1, 1, [82, 42]],
]
WORDS = (
    ("BORROW-WORD-43base.json.gz",
     "5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699"),
    ("BORROW-WORD-43extra.json.gz",
     "965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e"),
    ("PR3945-WORD-base.json.gz",
     "08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0"),
    ("PR3945-WORD-extra.json.gz",
     "d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299"),
)


class AuditFailure(Exception):
    """Explicit failure. python -O does not disable it."""


def need(ok, *why):
    if not ok:
        raise AuditFailure(" ".join(map(str, why)))


def is_target(register):
    return V <= register < 2 * V


def ratio(gate):
    return Fraction(gate[3], gate[4])


def ordinary_forward(word):
    """Non-wrapper actions whose literal inverse is the cleanup section."""
    out = [gate for gate in word["A"][word["prelude_events"]:]]
    placed = {}
    for index, record in enumerate(word["warps"], 1):
        placed.setdefault(record[0], []).append(["warp", record[1], index])
    for position in range(len(word["B"]) + 1):
        out.extend(placed.get(position, []))
        if position < len(word["B"]):
            out.append(word["B"][position])
    return out + list(word["restore"])


def derive_cleanup(word):
    restored = set(map(int, word["helper_final"]))

    def renamed(register):
        return register + N if register in restored else register

    out = []
    for gate in reversed(ordinary_forward(word)):
        if gate[0] == "warp":
            out.append(["warp", renamed(gate[1]), -gate[2], FULL])
        elif is_target(gate[1]):
            continue
        elif gate[0] == "add":
            out.append(["add", renamed(gate[1]), renamed(gate[2]),
                        -gate[3], gate[4], FULL])
        else:
            need(gate[0] == "scale", "unknown primitive", gate)
            out.append(["scale", renamed(gate[1]), gate[3], gate[2], FULL])
    return out


def matrix(gates):
    registers = sorted({register for gate in gates for register in gate[1:3]})
    index = {register: place for place, register in enumerate(registers)}
    rows = [[Fraction(int(i == j)) for j in range(len(registers))]
            for i in range(len(registers))]
    for gate in gates:
        need(gate[0] == "add", "matrix domain", gate)
        target, source = index[gate[1]], index[gate[2]]
        need(target != source, "self ADD", gate)
        coefficient = ratio(gate)
        rows[target] = [left + coefficient * right
                        for left, right in zip(rows[target], rows[source])]
    return rows


def chain(first, second):
    return (first[0] == second[0] == "add"
            and len(set(first[1:3] + second[1:3])) == 3
            and (first[1] == second[2] or first[2] == second[1]))


def expand(first, second, position):
    need(chain(first, second), "not an A2 chain")
    left, right = ratio(first), ratio(second)
    if first[2] == second[1]:
        target, source, coefficient = first[1], second[2], -left * right
    else:
        target, source, coefficient = second[1], first[2], left * right
    central = ["add", target, source, coefficient.numerator,
               coefficient.denominator, []]
    out = [deepcopy(second), deepcopy(first)]
    out.insert(position, central)
    return out


def inverse_sites(word):
    """Consecutive inverse A2 triples outside the A prelude."""
    spans = {
        "A": range(word["prelude_events"], len(word["A"]) - 2),
        "B": range(0, max(0, len(word["B"]) - 2)),
        "restore": range(0, max(0, len(word["restore"]) - 2)),
    }
    found = []
    for section, indices in spans.items():
        for index in indices:
            block = word[section][index:index + 3]
            if not all(isinstance(gate, list) and gate and gate[0] == "add"
                       for gate in block):
                continue
            for position in (0, 1, 2):
                remaining = [gate for place, gate in enumerate(block)
                             if place != position]
                later, earlier = remaining[::-1]
                if not chain(later, earlier):
                    continue
                expected = expand(later, earlier, position)
                if all(actual[:3] == want[:3] and ratio(actual) == ratio(want)
                       for actual, want in zip(block, expected)):
                    found.append((section, index, position))
    return found


def inverses(gates):
    return [["add", gate[1], gate[2], -gate[3], gate[4], FULL]
            for gate in reversed(gates)]


def replace_once(haystack, old, new):
    width = len(old)
    hits = [index for index in range(len(haystack) - width + 1)
            if haystack[index:index + width] == old]
    need(len(hits) == 1, "inverse block occurrences", len(hits))
    index = hits[0]
    return haystack[:index] + new + haystack[index + width:], index


def tiny_cleanup_length(destination):
    word = {
        "A": [["add", destination, 3, 1, 1, [1]]],
        "prelude_events": 0,
        "warps": [],
        "B": [],
        "restore": [],
        "helper_final": [],
    }
    return len(derive_cleanup(word))


def controls():
    wrong = deepcopy(TRIPLE)
    wrong[2] = ["add", 456, 475, -1, 1, [82, 42]]
    need(matrix(TRIPLE) == matrix(PAIR), "A1858 matrices differ")
    need(matrix(wrong) != matrix(PAIR), "wrong central sign was accepted")
    swapped = inverses([PAIR[1], PAIR[0]])
    need(matrix(swapped) != matrix(inverses(PAIR)),
         "cleanup order does not matter")
    need(tiny_cleanup_length(456) == 1, "helper ADD omitted from cleanup")
    need(tiny_cleanup_length(112) == 0, "target ADD entered cleanup")
    general_left = ["add", 1, 2, 3, 1, []]
    general_right = ["add", 2, 4, 5, 1, []]
    need(matrix([general_left, general_right])
         == matrix(expand(general_left, general_right, 1)),
         "general A2 identity failed")


def audit_word(name, digest):
    raw = (PACKAGE / "inputs" / name).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == digest, "sha256", name)
    word = json.loads(gzip.decompress(raw))
    need(word["A"][1858:1861] == TRIPLE, "A1858 triple", name)
    need(all(not is_target(gate[1]) for gate in TRIPLE), "target destination")
    need(all(register not in set(map(int, word["helper_final"]))
             for register in (456, 457, 475)), "restored rename", name)
    stored = word["cleanup"]
    need(stored == derive_cleanup(word), "stored cleanup", name)
    sites = inverse_sites(word)
    need(sites == [("A", 1858, 2)], "inverse sites", name, sites)
    edited = deepcopy(word)
    edited["A"][1858:1861] = deepcopy(PAIR)
    for key, value in word.items():
        if key not in ("A", "cleanup"):
            need(edited[key] == value, "frozen field", name, key)
    derived = derive_cleanup(edited)
    predicted, index = replace_once(stored, inverses(TRIPLE), inverses(PAIR))
    need(derived == predicted, "cleanup edit", name)
    need(len(edited["A"]) == len(word["A"]) - 1, "forward count", name)
    need(len(derived) == len(stored) - 1, "cleanup count", name)
    need(inverse_sites(edited) == [], "post sites", name, inverse_sites(edited))
    return {
        "word": name,
        "forward_events": len(word["A"]),
        "cleanup_events": len(stored),
        "cleanup_edit_index": index,
        "deleted_cleanup_gate": inverses(TRIPLE)[0],
        "forward_add_delta": -1,
        "cleanup_add_delta": -1,
    }


def main():
    controls()
    rows = [audit_word(name, digest) for name, digest in WORDS]
    need(len({row["cleanup_edit_index"] for row in rows[:2]}) == 1,
         "PR3734 cleanup index split")
    need(len({row["cleanup_edit_index"] for row in rows[2:]}) == 1,
         "PR3945 cleanup index split")
    need(rows[2]["cleanup_events"] == rows[0]["cleanup_events"] + 1,
         "PR3945 cleanup offset")
    print("PASS_A1858_CLEANUP_CONTRACTION",
          "words=4",
          "sites_before=1",
          "sites_after=0",
          "forward_add_delta=-1",
          "cleanup_add_delta=-1",
          "pr3734_cleanup_index=" + str(rows[0]["cleanup_edit_index"]),
          "pr3945_cleanup_index=" + str(rows[2]["cleanup_edit_index"]))


if __name__ == "__main__":
    main()
