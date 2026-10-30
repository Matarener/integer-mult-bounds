#!/usr/bin/env python3
"""Exact certificate, independent set replay and failure controls.

Jerry Chen (@CubeJerry), with OpenAI Codex assistance. Apache-2.0.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random

# Explicit sibling load works under -I and in an exported, Git-free package.
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g20_flag_model", HERE / "model.py")
model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)
require = model.require


def set_replay(word):
    """Separate representation: literal sets, not integer row arithmetic."""
    rows = [{i} for i in range(len(word["start"]))]
    queries = []
    for index, event in enumerate(word["records"]):
        op, dest = event[:2]
        if op == "ADD":
            rows[dest] = rows[dest].symmetric_difference(rows[event[2]])
        elif op == "ERASE":
            rows[dest] = set()
        elif op == "Q":
            queries.append((index, dest, event[-1], frozenset(rows[dest])))
        elif op == "ZERO_Q":
            require(not rows[dest], "set replay nonzero free query")
    return queries


def apply_map(row, mapping):
    out = 0
    while row:
        bit = row & -row
        out ^= mapping[bit.bit_length() - 1]
        row ^= bit
    return out


def substitution_fixture(data, captured, payloads):
    """Direct held-zero replay versus one triangular entry substitution.

    These finite fixtures exercise the lemma; PROOF.md gives its argument
    for every subset and every native-linear payload.
    """
    width = len(data["word"]["start"])
    owned = set(data["word"]["owned"])
    base = [0 if i in owned else 1 << i for i in range(width)]
    mapping = [0 if i in captured or i in owned else 1 << i for i in range(width)]
    dynamic = list(mapping)
    pending = set(captured)
    for index, event in enumerate(data["word"]["records"]):
        op, dest = event[:2]
        if op == "ADD" and event[2] in pending:
            h = event[2]
            require(index == data["first"][h], "capture epoch")
            require(base[h] & (1 << h), "unit unread diagonal")
            require(not base[h] & sum(1 << j for j in pending - {h}),
                    "unread triangularity")
            mapping[h] = payloads[h] ^ apply_map(base[h] ^ (1 << h), mapping)
            dynamic[h] = payloads[h]
            pending.remove(h)
        if op == "ADD":
            base[dest] ^= base[event[2]]
            if dest not in pending:
                dynamic[dest] ^= dynamic[event[2]]
        elif op == "ERASE":
            base[dest] = dynamic[dest] = 0
        if dest not in pending:
            require(dynamic[dest] == apply_map(base[dest], mapping),
                    "first-read substitution identity")
    require(not pending, "all captures executed")
    mask = sum(1 << h for h in captured)
    require(all(not mapping[h] & mask for h in captured), "graph-kernel projection")


def rejected(label, operation, expected):
    try:
        operation()
    except ValueError as error:
        require(expected in str(error), "wrong rejection for " + label)
        return label
    raise ValueError("negative control accepted: " + label)


def controls(data, certificate, frames, local):
    names = []
    bad = copy.deepcopy(certificate)
    bad["groups"][0].pop()
    names.append(rejected("omitted token", lambda: model.check_partition(data, bad),
                          "complete token coverage"))
    bad = copy.deepcopy(certificate)
    bad["groups"][0].append(bad["groups"][0][0])
    names.append(rejected("duplicate token in color", lambda: model.check_partition(data, bad),
                          "duplicate in color"))
    bad = copy.deepcopy(certificate)
    absent = next(i for i in range(len(data["vectors"])) if i not in bad["groups"][0])
    bad["groups"][0].append(absent)
    names.append(rejected("distinct dependent row", lambda: model.check_partition(data, bad),
                          "dependent color"))
    for name, index, mask, reason in (
        ("partial helper in restricted color", 64,
         sum(1 << h for h in data["partial"]), "partial flag"),
        ("rank-two helper in restricted color", 92,
         sum(1 << h for h in data["free_two"]), "rank-two flag"),
    ):
        bad = copy.deepcopy(certificate)
        row_id = next(i for i, v in enumerate(data["vectors"]) if v & mask and
                      (index == 64 or not v & sum(1 << h for h in data["partial"])))
        bad["groups"][index].append(row_id)
        names.append(rejected(name, lambda: model.check_partition(data, bad), reason))
    bad_data = dict(data)
    bad_data["multiplicities"] = data["multiplicities"].copy()
    _, _, rank, row = next(q for q in data["eligible"] if q[0] == 6291)
    bad_data["multiplicities"][data["vectors"].index(row)] -= model.TOKENS[rank]
    names.append(rejected("omit cross-helper early query 6291",
                          lambda: model.check_partition(bad_data, certificate),
                          "complete token coverage"))
    bad_word = copy.deepcopy(data["word"])
    first_q = next(e for e in bad_word["records"] if e[0] == "Q")
    first_q[-1] += 1
    names.append(rejected("forged query rank", lambda: model.census(bad_word, frames, local),
                          "query rank"))
    source = (model.ROOT / model.WORD).read_bytes()
    damaged = bytes([source[0] ^ 1]) + source[1:]
    names.append(rejected("changed source bytes", lambda: model.authenticate(
        damaged, hashlib.sha256(source).hexdigest(), model.WORD), "source hash"))
    return names


def verify():
    word, frames, local = model.inputs()
    data = model.census(word, frames, local)
    expected_sets = [(i, h, r, frozenset(j for j in range(len(word["start"]))
                                      if row & (1 << j)))
                     for i, h, r, row in data["queries"]]
    require(set_replay(word) == expected_sets, "independent set replay")
    certificate = model.read_certificate()
    sizes = model.check_partition(data, certificate)
    model.power_bounds()
    rng = random.Random(8)
    helpers = sorted(data["helpers"])
    cases = [set(), {684}, {465, 684}, {274, 297, 467}, set(data["free_two"]),
             set(helpers), set(rng.sample(helpers, 32))]
    for captured in cases:
        retained = set(range(len(word["start"]))) - captured - set(word["owned"])
        mask = sum(1 << h for h in retained)
        payloads = {h: rng.getrandbits(len(word["start"])) & mask for h in sorted(captured)}
        substitution_fixture(data, captured, payloads)
    names = controls(data, certificate, frames, local)
    query_bytes = json.dumps([(i, h, r, hex(v)) for i, h, r, v in data["queries"]],
                            separators=(",", ":")).encode()
    result = {
        "status": "PASS_G20_ALL_SUBSET_FIRST_READ_FLAG_BOUND",
        "wire_count": len(word["start"]), "event_count": len(word["records"]),
        "helper_count": len(helpers), "full_helpers": 413, "partial_helpers": [465, 684],
        "rank_two_early_helpers": len(data["free_two"]),
        "paid_profile": {str(k): v for k, v in sorted(data["paid"].items())},
        "query_count": len(data["queries"]), "eligible_queries": len(data["eligible"]),
        "distinct_rows": len(data["vectors"]), "tokens": sum(sizes),
        "color_limits": certificate["limits"], "color_sizes": sizes,
        "cross_helper_early_queries": data["early_cross"],
        "query_rows_sha256": hashlib.sha256(query_bytes).hexdigest(),
        "t_interval": ["99/100", "1"], "full_helper_loss_lower_bound": "(5/128)*4^t",
        "substitution_fixtures": len(cases), "negative_controls": names,
        "kappa_change": False,
    }
    return result


def main():
    result = verify()
    expected = json.loads((HERE / "RESULT.json").read_text())
    require(result == expected, "recorded result mismatch")
    print(result["status"])
    print("415 helpers; 2216 queries; 64274 tokens; 108 colors; 8 rejected controls")


if __name__ == "__main__":
    main()
