"""Exact checks for the new rank-two primitive stream. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
ROLES = 5


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_word():
    path = PACKAGE / "WORD.json"
    need(path.stat().st_size <= 4096, "word size limit")
    word = json.loads(path.read_text())
    need(type(word) is list and len(word) == 13, "expected thirteen primitives")
    for gate in word:
        need(type(gate) is list and gate, "invalid primitive")
        need(gate[0] in ("xor", "g"), "unknown primitive")
        need(len(gate) == (3 if gate[0] == "xor" else 2), "invalid arity")
        need(all(type(i) is int and 0 <= i < ROLES for i in gate[1:]),
             "invalid role")
        if gate[0] == "xor":
            need(gate[1] != gate[2], "self XOR is not invertible")
    need(sum(g[0] == "xor" for g in word) == 10, "CNOT invoice")
    need(sum(g[0] == "g" for g in word) == 3, "reflection invoice")
    return word


def formal(word):
    # An (identity coefficient, g coefficient) pair of binary input masks.
    rows = [(1 << i, 0) for i in range(ROLES)]
    for gate in word:
        i = gate[1]
        a, b = rows[i]
        if gate[0] == "g":
            rows[i] = (b, a)
        else:
            c, d = rows[gate[2]]
            rows[i] = (a ^ c, b ^ d)
    return tuple(rows)


def move(value, permutation):
    return sum(((value >> i) & 1) << j for i, j in enumerate(permutation))


def literal(word, state, permutation):
    # Independent bit-array execution; no formal coefficient operations.
    data = [list((row >> j) & 1 for j in range(len(permutation))) for row in state]
    for gate in word:
        target = gate[1]
        if gate[0] == "xor":
            source = data[gate[2]]
            data[target] = [x ^ y for x, y in zip(data[target], source)]
        else:
            old = data[target][:]
            for i, j in enumerate(permutation):
                data[target][j] = old[i]
    return tuple(sum(bit << j for j, bit in enumerate(row)) for row in data)


def target(state, permutation):
    a, b, c, d, h = state
    return (a ^ c ^ move(c, permutation), b ^ d ^ move(d, permutation),
            c, d, move(h, permutation))


def finite_actions(word):
    dense = 0
    for state in itertools.product(range(4), repeat=ROLES):
        need(literal(word, state, (1, 0)) == target(state, (1, 0)),
             "complete two-address state mismatch")
        dense += 1
    involutions, columns = 0, 0
    for size in range(1, 7):
        for permutation in itertools.permutations(range(size)):
            if any(permutation[permutation[i]] != i for i in range(size)):
                continue
            involutions += 1
            for role in range(ROLES):
                for bit in range(size):
                    state = tuple((1 << bit) if i == role else 0 for i in range(ROLES))
                    need(literal(word, state, permutation) == target(state, permutation),
                         "involutory-address full basis mismatch")
                    columns += 1
    return {"dense_two_address_states": dense, "involutions": involutions,
            "literal_basis_columns": columns}


def controls(word, expected):
    omissions = 0
    for i in range(len(word)):
        need(formal(word[:i] + word[i + 1:]) != expected,
             "primitive omission invisible")
        omissions += 1
    need(literal(word, (0, 0, 0, 0, 1), (1, 0)) != (0, 0, 0, 0, 1),
         "dirty helper incorrectly restored")
    need(any(literal(word, tuple(1 if i == j else 0 for i in range(ROLES)),
                     (1, 2, 0)) != target(tuple(1 if i == j else 0 for i in range(ROLES)),
                                           (1, 2, 0)) for j in range(ROLES)),
         "noninvolutory substitution incorrectly accepted")
    wrong_order = word[:]
    wrong_order[1], wrong_order[2] = wrong_order[2], wrong_order[1]
    need(formal(wrong_order) != expected, "noncommuting order control")
    return {"primitive_omissions_rejected": omissions, "boundary_controls": 3}


def authenticate():
    path = PACKAGE / "SOURCES.json"
    need(path.stat().st_size <= 65536, "source manifest size limit")
    sources = json.loads(path.read_text())
    need(type(sources["files"]) is list and len(sources["files"]) <= 16,
         "source manifest count limit")
    hashes = {}
    for source in sources["files"]:
        if source["usage"] != "input":
            continue
        name = source["path"]
        path = ROOT / name
        need(path.stat().st_size <= 1048576, "source file size limit")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(digest == source["sha256"] and blob == source["git_blob"],
             "changed cited source: " + name)
        hashes[name] = digest
    for name in ("README.md", "PROOF.md", "WORD.json", "verify.py", "TASK.json",
                 "SOURCES.json", "VERIFY.json"):
        path = PACKAGE / name
        need(path.stat().st_size <= 1048576, "package file size limit")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    need(len(sys.argv) == 1, "verifier takes no arguments")
    hashes = authenticate()
    word = read_word()
    expected = ((5, 4), (10, 8), (4, 0), (8, 0), (0, 16))
    need(formal(word) == expected, "full formal F2[C2] endpoint")
    report = finite_actions(word)
    report.update(controls(word, expected))
    need(report == {"dense_two_address_states": 1024, "involutions": 119,
                    "literal_basis_columns": 3215, "primitive_omissions_rejected": 13,
                    "boundary_controls": 3}, "finite coverage changed")
    print(json.dumps({"claim_type": "scoped construction", "scalar_CNOTs": 10,
                      "coordinate_reflections": 3, "checks": report,
                      "sha256": hashes}, sort_keys=True))
    print("PASS_CLEAN_RANK_TWO_CONJUGATORS reflections=3 CNOTs=10 no_new_kappa")


if __name__ == "__main__":
    main()
