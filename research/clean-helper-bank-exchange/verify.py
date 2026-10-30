#!/usr/bin/env python3
"""Check all short words by literal truth tables, independently of generation."""

import hashlib
import itertools
import json
from pathlib import Path
import platform


PACKAGE = Path(__file__).resolve().parent
MASK = (1 << 16) - 1
GATES = tuple((destination, source) for source in range(5)
              for destination in range(5) if source != destination)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pack(rows):
    """Evaluate each row on all sixteen assignments, without parity arithmetic."""
    require(len(rows) == 5 and all(type(row) is int and 0 <= row < 16 for row in rows),
            "invalid five-wire coefficient state")
    tables = []
    for row in rows:
        table = 0
        for assignment in itertools.product((0, 1), repeat=4):
            data = sum(bit << i for i, bit in enumerate(assignment))
            value = 0
            for bit in range(4):
                if row & (1 << bit):
                    value ^= assignment[bit]
            table |= value << data
        tables.append(table)
    return sum(table << (16 * wire) for wire, table in enumerate(tables))


def apply(state, gate):
    if gate is None:
        return state
    destination, source = gate
    require(0 <= destination < 5 and 0 <= source < 5 and destination != source,
            "invalid directed ADD")
    return state ^ (((state >> (16 * source)) & MASK) << (16 * destination))


def short_words(start, depth):
    """Enumerate all (20+1)^depth words; None pads shorter words only."""
    reached = set()
    for word in itertools.product((None, *GATES), repeat=depth):
        state = start
        for gate in word:
            state = apply(state, gate)
        reached.add(state)
    return reached


def digest(states):
    payload = json.dumps(sorted(states), separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def check_record(record, states, shorter):
    require(record["states"] == len(states), "wrong state count")
    require(record["sha256"] == digest(states), "wrong state digest")
    require(record["layers"] == shorter + [len(states) - sum(shorter)], "wrong layers")


def check_certificate(cert):
    require(cert["schema_version"] == 1 and cert["data_wires"] == 4
            and cert["clean_helpers"] == 1 and cert["gate_count"] == 20
            and cert["excluded_maximum_length"] == 5, "wrong model")
    start = pack((1, 2, 4, 8, 0))
    prefix = short_words(start, 2)
    check_record(cert["prefix"], prefix, [1, len(short_words(start, 1)) - 1])
    nonzero = (1, 2, 3)
    bases = tuple((a, b) for a, b in itertools.permutations(nonzero, 2))
    expected = {(a << 2, b << 2, c, d, 0) for a, b in bases for c, d in bases}
    rows = [tuple(record["rows"]) for record in cert["endpoints"]]
    require(len(rows) == 36 and set(rows) == expected, "wrong endpoint inventory")
    suffix_total = 0
    for record in cert["endpoints"]:
        target = pack(record["rows"])
        one = short_words(target, 1)
        two = short_words(target, 2)
        suffix = short_words(target, 3)
        check_record(record, suffix, [1, len(one) - 1, len(two) - len(one)])
        require(prefix.isdisjoint(suffix), "short exchange word found")
        suffix_total += len(suffix)
        del one, two, suffix
    witnesses = cert["six_add_attainments"]
    require(len(witnesses) == 2, "missing attainments")
    targets = set()
    for witness in witnesses:
        require(len(witness["gates"]) == 6, "wrong attainment length")
        state = start
        for gate in witness["gates"]:
            state = apply(state, gate)
        target_rows = tuple(witness["rows"])
        require(target_rows in expected and state == pack(target_rows), "false attainment")
        targets.add(target_rows)
    require(len(targets) == 2, "duplicate attainments")
    return {"endpoints": len(rows), "prefix_states": len(prefix),
            "suffix_states_summed_over_endpoints": suffix_total,
            "padded_suffix_words": 36 * 21**3, "attainments": len(targets)}


def controls(cert):
    names = ("model", "count", "digest", "inventory", "helper return", "attainment", "gate")
    mutations = [json.loads(json.dumps(cert)) for _ in names]
    mutations[0]["clean_helpers"] = 0
    mutations[1]["prefix"]["states"] = 1
    mutations[2]["prefix"]["sha256"] = "0" * 64
    mutations[3]["endpoints"].pop()
    mutations[4]["endpoints"][0]["rows"][4] = 1
    mutations[5]["six_add_attainments"][0]["gates"].pop()
    mutations[6]["six_add_attainments"][0]["gates"][0] = [0, 0]
    rejected = []
    for name, copy in zip(names, mutations):
        try:
            check_certificate(copy)
        except ValueError:
            rejected.append(name)
    require(len(rejected) == len(names), "mutation accepted")
    start = pack((1, 2, 4, 8, 0))
    require(start in short_words(start, 3), "padding lost a short word")
    for gate in GATES:
        state = apply(start, gate)
        require(state in short_words(start, 2), "positive one-gate meet missing")
        require(apply(state, gate) == start, "ADD is not involutive")
    target = start
    for gate in ((4, 0), (1, 4), (4, 0), (2, 1), (3, 2)):
        target = apply(target, gate)
    require((target >> 64) == 0, "positive helper word failed restoration")
    require(not short_words(start, 2).isdisjoint(short_words(target, 3)),
            "positive five-ADD meet missing")
    return rejected


def main():
    source = PACKAGE / "CERTIFICATE.json"
    require(source.stat().st_size < 64 * 1024, "certificate size limit")
    cert = json.loads(source.read_text())
    counts = check_certificate(cert)
    rejected = controls(cert)
    names = ("CERTIFICATE.json", "PROOF.md", "README.md", "SOURCES.json", "TASK.json",
             "VERIFY.json", "generate.py", "verify.py")
    hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"counts": counts, "rejected_controls": rejected,
                      "python": platform.python_version(), "source_sha256": hashes}, sort_keys=True))
    print("PASS_CLEAN_HELPER_BANK_EXCHANGE")


if __name__ == "__main__":
    main()
