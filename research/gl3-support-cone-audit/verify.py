#!/usr/bin/env python3
"""Authenticated source integration, not an independent group implementation.

Calls the unchanged PR4211 implementations and compares their literal outputs
to an oracle frozen before its author saw predecessor code. No SAT or RUP run.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

SOURCE_HEAD = "ca0002008b497428f0b651501c4a220a9d2785e7"
PINS = {
    "model.py": "38945ee5997b0b985d3fa461a06451ae91f6a0ac5757e42b74c5e175967a785c",
    "cnf_model.py": "12a02756ee757e5b70507e30fc6b8657f802000945742db5726335e83c56793f",
    "exact_checker.py": "92d7b726d3776012743fbc7713193a8b338ce6ae0d868f3805b9160ebd93efe1",
    "DIRECT_NINE.json": "adc28b1cf52b848875062e9df0abdb2bc4d7b4aa4caa809480c723b571de845a",
    "CERTIFICATES.json": "f5bc7526ca29724a89ea3126cdf4b3780774c3f15a0328f3f91b227c7ad16042",
}
ORACLE_SHA = "a053d73b1ce58a193209efe3f1735b82ffd51756dea2756fad5ea8b22fe89663"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def literal(rows):
    return "(" + ",".join(map(str, rows)) + ")"


def unpack(x):
    return tuple((x >> (3 * r)) & 7 for r in range(3))


def find_source(directory, name):
    for local in (name, "PR4211-" + name + ".txt", "PR4211-" + name):
        candidate = directory / local
        if candidate.is_file():
            require(digest(candidate.read_bytes()) == PINS[name], "source hash: " + name)
            return candidate
    raise ValueError("missing source: " + name)


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def run(source, reference):
    paths = {name: find_source(source, name) for name in PINS}
    require(digest(reference.read_bytes()) == ORACLE_SHA, "frozen oracle hash")
    oracle = json.loads(reference.read_bytes())
    old_exact = sys.modules.get("exact_checker")
    exact = load_module("exact_checker", paths["exact_checker.py"])
    sys.modules["exact_checker"] = exact
    try:
        cnfm = load_module("pr4211_cnf_model", paths["cnf_model.py"])
    finally:
        if old_exact is None:
            sys.modules.pop("exact_checker", None)
        else:
            sys.modules["exact_checker"] = old_exact
    packed = load_module("pr4211_model", paths["model.py"])
    algebra = packed.Algebra()
    reference_rows = {
        (r["length"], r["cut"], r["row"], r["column"]): set(r["allowed_support"])
        for r in oracle["support_rows"]
    }
    require(len(reference_rows) == 153, "153 oracle rows")
    source_group = {literal(unpack(x)): len(algebra.paths[x]) for x in algebra.group}
    require(source_group == {x: y["distance"] for x, y in oracle["group"].items()},
            "actual packed group distances vs independent oracle")
    elements, _, distance, _, permutations = cnfm.address_data()
    require({literal(x): distance[x] for x in elements} == source_group,
            "actual direct-CNF group distances")
    translations = 0
    for label, permutation in enumerate(permutations):
        for k, row in enumerate(elements):
            bit = algebra.translate(1 << algebra.index[sum(x << (3*r) for r, x in enumerate(row))], label)
            require(bit.bit_count() == 1, "monomial translation")
            translated = unpack(algebra.group[bit.bit_length() - 1])
            require(translated == elements[permutation[k]], "actual translation agreement")
            translations += 1
    identity = algebra.endpoint((packed.ID,) * 3)
    for gate in algebra.generators:
        require(algebra.step(algebra.step(identity, gate), gate) == identity,
                "actual factor involution")
    certificates = {x["length"]: x for x in json.loads(paths["CERTIFICATES.json"].read_bytes())["certificates"]}
    regenerated = []
    packed_rows = []
    allocated_rows = 0
    allocated_bits = 0
    with tempfile.TemporaryDirectory(prefix="gl3-support-cnf-") as work:
        for n in (7, 8):
            masks = packed.support_masks(algebra, n)
            cnf, _, allocated, cnf_elements, metadata = cnfm.build(n)
            require(cnf_elements == elements, "CNF group order stable")
            actual_allocated = {}
            for (t, r, c, k), variable in allocated.items():
                require(type(variable) is int and variable >= 2, "allocated coefficient variable")
                actual_allocated.setdefault((t, r, c), set()).add(literal(elements[k]))
            for t in range(n + 1):
                for r in range(3):
                    for c in range(3):
                        values = {literal(unpack(x)) for k, x in enumerate(algebra.group)
                                  if masks[t][c] & (1 << k)}
                        require(values == reference_rows[n, t, r, c], "packed support vs oracle")
                        require(metadata["support_counts"][t][c] == len(values), "CNF support count")
                        packed_rows.append({"length": n, "cut": t, "row": r, "column": c,
                                            "allowed": sorted(values)})
                        if 0 < t < n:
                            require(actual_allocated.get((t, r, c), set()) == values,
                                    "actual CNF allocated coefficient mask vs oracle")
                            allocated_rows += 1
                            allocated_bits += len(values)
            require(not any(t in (0, n) for t, _, _, _ in allocated), "endpoint coefficients are constants")
            path = Path(work) / (str(n) + ".cnf")
            cnf.write(path)
            data = path.read_bytes()
            cert = certificates[n]
            require(digest(data) == cert["cnf_sha256"] and len(data) == cert["cnf_bytes"],
                    "regenerated CNF bytes vs published certificate")
            require(cnf.variables == cert["variables"] and len(cnf.clauses) == cert["clauses"],
                    "regenerated CNF counts")
            regenerated.append({"length": n, "variables": cnf.variables, "clauses": len(cnf.clauses),
                                "bytes": len(data), "sha256": digest(data),
                                "allocated_state_variables": len(allocated)})
    word = json.loads(paths["DIRECT_NINE.json"].read_bytes())["word_uvij"]
    direct = exact.check(word)
    require(direct["accepted"] and direct["basis_columns_checked"] == 504, "source direct-nine full replay")
    masks9 = packed.support_masks(algebra, 9)
    prefixes = []
    for t in range(10):
        state = [[sorted(literal(x) for x in exact.column(word[:t], c)[r])
                  for c in range(3)] for r in range(3)]
        for r in range(3):
            for c in range(3):
                allowed = {literal(unpack(x)) for k, x in enumerate(algebra.group)
                           if masks9[t][c] & (1 << k)}
                require(set(state[r][c]) <= allowed, "actual direct-nine prefix lies in support cone")
        prefixes.append(state)
    require(prefixes == oracle["positive_examples"][-1]["prefix_algebra"],
            "actual direct-nine prefixes vs independent formal replay")
    require(oracle["positive_examples"][-1]["length"] == len(word) == 9,
            "direct-nine receipt records integer length")
    # Deliberate semantic errors, not corrupted-file hashes.
    witness = [[1, 1, 0, 1], [1, 1, 1, 2]]
    target = ((3, 6, 4), exact.IDENTITY, exact.IDENTITY)
    require(exact.check(witness, target)["accepted"], "two-call orientation witness")
    prefix = next(iter(exact.column(witness[:1], 0)[0]))
    ball1 = {x for x in elements if distance[x] <= 1}
    right = {exact.product(x, target[0]) for x in ball1}
    wrong_left = {exact.product(target[0], x) for x in ball1}
    require(prefix in right and prefix not in wrong_left, "left-translation mutant rejected")
    correct = packed.support_masks(algebra, 2, tuple(sum(v << (3*r) for r, v in enumerate(x)) for x in target))
    needed_bit = 1 << algebra.index[sum(v << (3*r) for r, v in enumerate(prefix))]
    require(correct[1][0] & needed_bit, "positive prefix bit admitted")
    require(not ((correct[1][0] ^ needed_bit) & needed_bit), "one-hole mutant excludes actual valid prefix")
    wrong_target_mask = packed.support_masks(algebra, 2, (packed.ID,) * 3)[2][0]
    actual_target_bit = 1 << algebra.index[sum(v << (3*r) for r, v in enumerate(target[0]))]
    require(not (wrong_target_mask & actual_target_bit), "wrong-target mutant excludes actual endpoint")
    order3 = (2, 4, 1)
    require(exact.product(order3, order3) != exact.IDENTITY, "noninvolutory-address premise control")
    return {
        "status": "PASS_SOURCE_SUPPORT_INTEGRATION",
        "role": "source reuse and integration; independent oracle frozen before source access",
        "source_head": SOURCE_HEAD, "source_sha256": PINS, "oracle_sha256": ORACLE_SHA,
        "group_elements": len(elements), "generator_monomial_translations_checked": translations,
        "actual_factor_involutions_checked": len(algebra.generators),
        "support_rows_compared": len(packed_rows), "support_rows_sha256": digest(canonical(packed_rows)),
        "allocated_interior_rows_compared": allocated_rows, "allocated_state_bits_compared": allocated_bits,
        "cnf_regeneration": regenerated, "source_direct_nine": direct,
        "source_direct_nine_prefix_matrices": len(prefixes),
        "source_direct_nine_prefix_sha256": digest(canonical(prefixes)),
        "controls": {"wrong_left_translate": "rejected by legal two-call word",
                     "one_missing_allowed_bit": "rejects actual valid prefix",
                     "wrong_target": "rejects actual endpoint",
                     "noninvolutory_address": "order-three square differs from identity"},
        "orientation_witness": {"word_uvij": witness, "endpoint": target,
                                "prefix": prefix, "correct_right_support": sorted(right),
                                "incorrect_left_support": sorted(wrong_left)},
        "noninvolution_witness": {"address": order3,
                                  "address_squared": exact.product(order3, order3),
                                  "projector": "e0 e0^T, so the first diagonal factor is [address]"},
        "limits": ["no SAT solve or RUP replay", "no complete Boolean compiler equivalence audit",
                   "no independent proof of free-mixing normalization", "no minimum-nine certification",
                   "not human review or proof-assistant verification", "no new kappa"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument("--source", type=Path, default=here / "source")
    parser.add_argument("--reference", type=Path, default=here / "ORACLE-RESULT.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.source, args.reference)
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
