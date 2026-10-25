#!/usr/bin/env python3
"""Intermediate scalar magnitudes of one literal F0 dirty-helper ray.

The reviewed F0 word is projected onto its common-chart scalar operations.
No predecessor executable is imported. This is not a physical Hilbert-norm
certificate and not a new exponent.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 712
FAULT = 24438
DIRTY = 359
DATA = 112
SCALAR_SHA = "4c17e407bca2520b85cdfb1cc90b301aa4aad36902b95d7e967d3082259630e2"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def reg(token):
    need(isinstance(token, list) and len(token) == 2, "register token")
    kind, index = token
    need(type(index) is int and kind in ("L", "C"), "register kind")
    need(0 <= index < (704 if kind == "L" else 8), "register range")
    return index + (704 if kind == "C" else 0)


def classify(index):
    if index < 224:
        return "data"
    if index < 704:
        return "helper"
    return "private"


def expand(packet):
    need(packet["schema"] == "conserved-qq16-full-cover-native-words-v1", "schema")
    word = []
    for event in packet["programs"]["F_0"]:
        op = event[0]
        if op == "retained_core":
            need(event[1:3] == ["forward", 0], "F0 core")
            word.extend(packet["core_words"]["forward"])
        elif op in ("cover_sweep", "private_sweep"):
            word.extend(event[2])
        else:
            word.append(event)
    need(len(word) == 26099, "expanded event count")
    need(Counter(event[0] for event in word) == {
        "scalar": 21025, "climb": 3486, "adapter": 1090,
        "residual_adapter": 480, "phase": 10, "native_line": 8,
    }, "F0 event inventory")
    need(word[FAULT] == ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1],
         "published fault event")
    return word


def apply_dense(state, gate):
    op, dst = gate[0], reg(gate[1])
    if op == "add":
        src = reg(gate[2])
        need(src != dst and len(gate) == 5 and gate[3] != 0, "ADD operands")
        state[dst] += Q(gate[3], gate[4]) * state[src]
    elif op == "scale":
        need(len(gate) == 4 and gate[2] != 0, "SCALE operands")
        state[dst] *= Q(gate[2], gate[3])
    elif op == "clear":
        need(dst >= 704 and len(gate) == 2, "owned CLEAR")
        state[dst] = Q(0)
    else:
        raise ValueError("unknown scalar operation")


def apply_sparse(state, gate):
    op, dst = gate[0], reg(gate[1])
    if op == "add":
        src = reg(gate[2])
        need(src != dst and len(gate) == 5 and gate[3] != 0, "ADD operands")
        value = state.get(dst, Q(0)) + Q(gate[3], gate[4]) * state.get(src, Q(0))
        if value:
            state[dst] = value
        else:
            state.pop(dst, None)
    elif op == "scale":
        need(len(gate) == 4 and gate[2] != 0, "SCALE operands")
        value = Q(gate[2], gate[3]) * state.get(dst, Q(0))
        if value:
            state[dst] = value
        else:
            state.pop(dst, None)
    elif op == "clear":
        need(dst >= 704 and len(gate) == 2, "owned CLEAR")
        state.pop(dst, None)
    else:
        raise ValueError("unknown scalar operation")


def blank(seed, sparse):
    if sparse:
        return {seed: Q(1)}
    state = [Q(0)] * WIDTH
    state[seed] = Q(1)
    return state


def items(state, sparse):
    if sparse:
        return state.items()
    return ((index, value) for index, value in enumerate(state) if value)


def project(word, seed, sparse=False):
    """Exact forward image of one initial basis register.

    Magnitudes are recorded before and after every scalar operation. Non-scalar
    events do not change this projection's state.
    """
    state = blank(seed, sparse)
    peaks = {kind: Q(0) for kind in ("data", "helper", "private")}
    first = {}
    seen = set()
    data_peak_states = 0
    data_peak_registers = set()
    cut = None
    for index, event in enumerate(word):
        if index == FAULT:
            cut = (state[39] if not sparse else state.get(39, Q(0)),
                   state[359] if not sparse else state.get(359, Q(0)))
        if event[0] != "scalar":
            continue
        need(len(event) == 3, "scalar frame annotation")
        for register, value in items(state, sparse):
            magnitude = abs(value)
            seen.add(magnitude)
            kind = classify(register)
            if magnitude > peaks[kind] or (magnitude == peaks[kind] and kind not in first):
                if magnitude > peaks[kind]:
                    peaks[kind] = magnitude
                    first[kind] = {
                        "event": index,
                        "phase": "before",
                        "register": register,
                        "value": value,
                        "frame": event[2],
                        "gate": event[1],
                    }
        before = dict(state) if sparse else list(state)
        (apply_sparse if sparse else apply_dense)(state, event[1])
        hit_registers = []
        for register, value in items(state, sparse):
            magnitude = abs(value)
            seen.add(magnitude)
            kind = classify(register)
            if magnitude > peaks[kind]:
                source = None
                if event[1][0] == "add":
                    source_register = reg(event[1][2])
                    source = before[source_register] if not sparse else before.get(source_register, Q(0))
                peaks[kind] = magnitude
                first[kind] = {
                    "event": index,
                    "phase": "after",
                    "register": register,
                    "value": value,
                    "frame": event[2],
                    "gate": event[1],
                    "before": (before[register] if not sparse else before.get(register, Q(0))),
                    "source": source,
                }
            if kind == "data" and magnitude == 128:
                hit_registers.append(register)
        if hit_registers:
            data_peak_states += 1
            data_peak_registers.update(hit_registers)
            need(event[2] == 1, "data-peak frame annotation")
    final = {index: value for index, value in items(state, sparse)}
    return {"peaks": peaks, "first": first, "absolute_values": seen,
            "data_peak_states": data_peak_states,
            "data_peak_registers": data_peak_registers,
            "cut": cut, "final": final}


def load(root):
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        if item["usage"] == "input":
            raw = (root / item["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source pin " + item["path"])
    certificate = root / "research/joint-query/certificate.json.gz"
    raw = certificate.read_bytes()
    need(len(raw) < 1024 * 1024, "compressed certificate cap")
    payload = gzip.decompress(raw)
    need(len(payload) < 16 * 1024 * 1024, "certificate payload cap")
    receipt = json.loads((root / "research/qq16-producer-dirty-fault/RESULT.json").read_text(encoding="utf-8"))
    contract = (root / "research/qq16-producer-defect-transfer/README.md").read_text(encoding="utf-8")
    need("||F|| <= 58" in contract, "pinned completed-output norm statement")
    return json.loads(payload), receipt


def response(word, event_index, increment):
    """Zero input, with one constant added to the scalar destination after event_index."""
    state = [Q(0)] * WIDTH
    for index, event in enumerate(word):
        if event[0] == "scalar":
            apply_dense(state, event[1])
            if index == event_index:
                state[reg(event[1][1])] += increment
    return state


def audit(root):
    packet, receipt = load(root)
    word = expand(packet)
    scalars = [event[1] for event in word if event[0] == "scalar"]
    need(hashlib.sha256(canonical(scalars)).hexdigest() == SCALAR_SHA, "scalar projection digest")
    need(receipt["scalar_projection_sha256"] == SCALAR_SHA, "published scalar projection")
    need(receipt["prefix_dirty_target_coefficient"] == "-4", "published cut coefficient")
    dense = project(word, DIRTY, sparse=False)
    sparse = project(word, DIRTY, sparse=True)
    need(dense["peaks"] == sparse["peaks"], "dense/sparse peak agreement")
    need(dense["final"] == sparse["final"], "dense/sparse final agreement")
    need(dense["cut"] == sparse["cut"] == (Q(-4), Q(1)), "dirty cut coefficients")
    need(dense["absolute_values"] == sparse["absolute_values"], "dense/sparse magnitude set")
    need(dense["peaks"] == {"data": Q(128), "helper": Q(68), "private": Q(0)}, "dirty peaks")
    need(len(dense["absolute_values"]) == 37, "distinct dirty magnitudes")
    need(max(dense["absolute_values"]) == 128, "no larger dirty coefficient")
    data_hit = dense["first"]["data"]
    need(data_hit["phase"] == "after" and data_hit["event"] == 24280, "first data peak event")
    need(data_hit["register"] == 103 and data_hit["value"] == Q(-128), "data peak register")
    need(data_hit["frame"] == 1 and data_hit["gate"] == ["add", ["L", 103], ["L", 354], 64, 1],
         "data peak gate")
    need(data_hit["before"] == Q(-64) and data_hit["source"] == Q(-1), "pre-peak operands")
    helper_hit = dense["first"]["helper"]
    need(helper_hit["phase"] == "after" and helper_hit["event"] == 24338, "first helper peak event")
    need(helper_hit["register"] == 609 and helper_hit["value"] == Q(68), "helper peak register")
    need(helper_hit["gate"] == ["add", ["L", 609], ["L", 354], -34, 1], "helper peak gate")
    need(helper_hit["before"] == Q(34) and helper_hit["source"] == Q(-1), "helper peak operands")
    need(helper_hit["frame"] == 1, "helper peak frame")
    need(dense["data_peak_states"] == 154 and dense["data_peak_registers"] == {103},
         "data peak support")
    need(dense["final"] == {DIRTY: Q(1)}, "exact dirty restoration")
    # |destination| + |coefficient| |source| at the creating ADD.
    need(abs(data_hit["before"]) + 64 * abs(data_hit["source"]) == 128, "local allowance units")
    data_dense = project(word, DATA, sparse=False)
    data_sparse = project(word, DATA, sparse=True)
    need(data_dense["peaks"] == data_sparse["peaks"] == {
        "data": Q(1), "helper": Q(0), "private": Q(0)}, "data-ray peaks")
    need(data_dense["final"] == data_sparse["final"] == {DATA: Q(1)}, "exact data restoration")
    need(data_dense["cut"] == (Q(0), Q(0)), "data ray misses the dirty cut")
    # A unit injection at the data-peak ADD is not the published restoration-preserving fault.
    injected = response(word, 24280, Q(1))
    data_terms = [(index, value) for index, value in enumerate(injected[:224]) if value]
    helper_terms = [(index, value) for index, value in enumerate(injected[224:704]) if value]
    need(len(data_terms) == 78 and max(abs(value) for _, value in data_terms) == Q(1, 16),
         "peak-site data response")
    need(len(helper_terms) == 71 and max(abs(value) for _, value in helper_terms) == Q(17, 32),
         "peak-site helper response")
    need(not any(injected[704:]), "peak-site private response")
    return {
        "schema_version": 1,
        "status": "PASS_QQ16_F0_DIRTY_RAY_MAGNITUDE",
        "scope": "common-chart scalar projection of literal F0; one dirty ray and one data ray",
        "scalar_projection_sha256": SCALAR_SHA,
        "dirty_input": DIRTY,
        "data_input": DATA,
        "dirty_peaks": {kind: str(value) for kind, value in dense["peaks"].items()},
        "dirty_distinct_absolute_coefficients": len(dense["absolute_values"]),
        "data_peak_event": 24280,
        "data_peak_register": 103,
        "data_peak_value": "-128",
        "data_peak_gate": ["add", ["L", 103], ["L", 354], 64, 1],
        "data_peak_states": 154,
        "helper_peak_event": 24338,
        "helper_peak_register": 609,
        "helper_peak_value": "68",
        "fault_cut": ["-4", "1"],
        "local_allowance_at_data_peak": "128*u*T",
        "data_ray_peaks": {kind: str(value) for kind, value in data_dense["peaks"].items()},
        "restores_both_rays": True,
        "peak_site_unit_injection": {
            "event": 24280,
            "data_support": 78,
            "data_max": "1/16",
            "helper_support": 71,
            "helper_max": "17/32",
            "private_support": 0,
        },
        "completed_output_norm_statement": "||F|| <= 58 is a completed-output bound, not this intermediate ledger",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = audit(args.root.resolve())
    print(result["status"])
    print("dirty peaks data=128 helper=68 private=0; data ray peak=1; both rays restore")


if __name__ == "__main__":
    main()
