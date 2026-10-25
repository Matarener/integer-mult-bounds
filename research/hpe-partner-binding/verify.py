#!/usr/bin/env python3
"""The selected HPE binding accepts a tail gate whose helper is its own partner.

The Lean label statement requires those two registers to differ. This check
uses one synthetic 38-gate tail. It does not read an emitted word and it does
not run Lean.
"""

import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BINDING = ROOT / "scripts/verify_hpe_lean_binding.py"
EXACT = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"
PAIRS = ROOT / "research/hyperplane-end-lean/code/check_hpe_pairs.py"
PROOF = ROOT / "research/hyperplane-end-lean/PROOF.md"
MARKER = "PASS_HPE_PARTNER_BINDING self_partner_accepted=true no_new_kappa"
FIELDS = ("quadratic_rows", "linear_Z4", "matrix_rows", "offset", "phase")


def fail(message):
    raise SystemExit("FAIL_HPE_PARTNER_BINDING " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "scripts/verify_hpe_lean_binding.py",
        "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean",
        "research/hyperplane-end-lean/code/check_hpe_pairs.py",
        "research/hyperplane-end-lean/PROOF.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def parse_pairs(text):
    pairs = {}
    for number in (1, 2, 3):
        match = re.search(r"def pair%d : Pair := (.*?)\n\n" % number, text, re.S)
        require(match is not None, "missing pair " + str(number))
        entrance, terminal, left, right = ast.literal_eval(match[1].replace("⟨", "[").replace("⟩", "]"))
        pairs[(tuple(entrance), tuple(terminal))] = {
            "left": dict(zip(FIELDS, left, strict=True)),
            "right": dict(zip(FIELDS, right, strict=True)),
        }
    require(len(pairs) == 3, "pair keys collided")
    return pairs


def binding_accepts(word, adapters, pairs):
    found = set()
    for gate in word["tail"]:
        if not (gate[0] == "add" and gate[3:5] == [-1, 1]):
            return False
        helper, terminal = gate[1], gate[-1]
        entrance = word["start"][helper]
        if word["final"][helper] != terminal:
            return False
        key = (tuple(word["frames"][entrance]), tuple(word["frames"][terminal]))
        if key not in pairs:
            return False
        recipe = adapters["recipes"]["%s:%s" % (entrance, terminal)]
        if recipe["rank"] != 7:
            return False
        for side in ("left", "right"):
            if recipe[side] != pairs[key][side]:
                return False
        found.add(key)
    return len(word["tail"]) == 38 and len(found) == 3


def partners_differ(word):
    return all(gate[1] != gate[2] for gate in word["tail"])


def synthetic(pairs, self_partner):
    frames = []
    recipes = {}
    order = list(pairs)
    for index, key in enumerate(order):
        frames.extend([list(key[0]), list(key[1])])
        recipes["%d:%d" % (2 * index, 2 * index + 1)] = {"rank": 7, **pairs[key]}
    tail = []
    start = []
    final = []
    for helper in range(38):
        pair_index = 0 if helper < 16 else 1 if helper < 32 else 2
        entrance, terminal = 2 * pair_index, 2 * pair_index + 1
        partner = helper if self_partner and helper == 0 else helper + 100
        tail.append(["add", helper, partner, -1, 1, terminal])
        start.append(entrance)
        final.append(terminal)
    return {"frames": frames, "start": start, "final": final, "tail": tail}, {"recipes": recipes}


def evaluate():
    authenticate()
    binding = BINDING.read_text(encoding="utf-8")
    exact = EXACT.read_text(encoding="utf-8")
    pairs_source = PAIRS.read_text(encoding="utf-8")
    proof = PROOF.read_text(encoding="utf-8")
    require("gate[3:5] == [-1, 1]" in binding, "the coefficient test moved")
    require("gate[2]" not in binding, "the binding now reads the partner index")
    require("h == p" in pairs_source, "the instance partner test moved")
    require("h ≠ p" in proof, "the label hypothesis moved")
    pairs = parse_pairs(exact)
    word, adapters = synthetic(pairs, True)
    distinct, _ = synthetic(pairs, False)
    plus = json.loads(json.dumps(word))
    plus["tail"][0][3] = 1
    require(binding_accepts(word, adapters, pairs), "the self-partner tail was rejected")
    require(partners_differ(word) is False, "the self-partner registers differed")
    require(binding_accepts(distinct, adapters, pairs), "the distinct-partner tail was rejected")
    require(partners_differ(distinct), "the distinct-partner control collided")
    require(binding_accepts(plus, adapters, pairs) is False, "a plus coefficient was accepted")
    return {
        "tail_gates": 38,
        "pairs": 3,
        "self_partner_binding_accepts": True,
        "self_partner_registers_differ": False,
        "distinct_partner_binding_accepts": True,
        "plus_coefficient_binding_accepts": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
