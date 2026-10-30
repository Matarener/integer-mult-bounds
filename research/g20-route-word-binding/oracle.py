#!/usr/bin/env python3
"""Independent join and paired-address oracle for the actual G20 route markers.

ToikY with substantial OpenAI Codex assistance in a separate implementation
context. Ali Romman supplied the frozen global caller and port witnesses;
the frozen ToikY dyadic words are predecessor data. Apache-2.0. Retain NOTICE.
No primary verifier, predecessor implementation or mutable result is imported.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PINS = {
    "GLOBAL.jsonl.gz": (1895549,
        "86e7ce6aff05409410ef4bbc00ff1b29b8c1606383549c7e15242b327e39c235",
        "2290f206fe550af3738ab1219bb127bc09c65bbb"),
    "PORTS.json": (311085,
        "a53a49c938a46c5a9da8c05ffdec4c2ef2dd906dd94c009d6fa451af4ed350e9",
        "aeffcdb444f564d247aff2265f9aebc424bce14f"),
    "CALLS.json": (18903,
        "30dcc37cdade6b2dc05478837eca28b696894d1c4782bac6a1caab5e7f56c9e8",
        "9ee8c26f321ee3d420976fab69075c0c05db12ce"),
    "CONTROLLER.json": (23753,
        "39ac84fb848b908f7ba051fae4556d507900c421dc5d23501a9c0cb1d61fd08d",
        "89c400d5970024b3debe870c36ce43889beed001"),
    "WORDS.json": (640895,
        "c74b8446503425fb4964921e8651b3931f917c62a21565d9569e9f6399ea571b",
        "c3466c486097794afcdaba7ad3b3a26f517fb09c"),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def source(name):
    raw = (HERE / "source" / name).read_bytes()
    size, checksum, blob = PINS[name]
    need(len(raw) == size and sha256(raw).hexdigest() == checksum,
         "Oracle exact raw source: " + name)
    need(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
         "Oracle exact source Git blob: " + name)
    if name.endswith(".gz"):
        return [json.loads(line) for line in gzip.decompress(raw).splitlines()]
    return json.loads(raw)


def eye(n=8):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    n = len(a)
    return [[sum((a[i][k] * b[k][j] for k in range(n)
                  if a[i][k] and b[k][j]), F(0))
             for j in range(n)] for i in range(n)]


def apply(matrix, vector):
    return [sum((a * x for a, x in zip(row, vector)), F(0)) for row in matrix]


def p2_event(event):
    need(type(event) is list and event and event[0] in ("ADD", "SCALE"),
         "Oracle explicit P2 factor opcode")
    kind = event[0]
    need(len(event) == (4 if kind == "ADD" else 3), "Oracle factor arity")
    positions = event[1:3] if kind == "ADD" else event[1:2]
    need(all(type(i) is int and 0 <= i < 8 for i in positions),
         "Oracle factor coordinate")
    need(type(event[-1]) is str, "Oracle exact rational coefficient")
    q = F(event[-1])
    need(q and str(q) == event[-1] and q.denominator & (q.denominator - 1) == 0,
         "Oracle dyadic factor coefficient")
    if kind == "ADD":
        need(positions[0] != positions[1], "Oracle distinct ADD coordinates")
        return kind, positions[0], positions[1], q
    n = abs(q.numerator)
    need(n & (n - 1) == 0, "Oracle dyadic unit scale")
    return kind, positions[0], positions[0], q


def word_matrix(word):
    result = eye()
    for event in word:
        kind, i, j, q = p2_event(event)
        elementary = eye()
        elementary[i][j] = q
        result = multiply(result, elementary)
    return result


def paired_basis(matrix, vector, mode="reflected"):
    first = apply(matrix, vector[:8])
    if mode == "omit_second":
        return first + vector[8:]
    if mode == "unreflected":
        return first + apply(matrix, vector[8:])
    return first + list(reversed(apply(matrix, list(reversed(vector[8:])))))


def native(projector, vector):
    differences = [vector[i] - vector[15 - i] for i in range(8)]
    correction = apply(projector, differences)
    output = vector[:]
    for i in range(8):
        output[i] -= correction[i]
        output[15 - i] += correction[i]
    return output


def compact(vector):
    return {str(i): str(x) for i, x in enumerate(vector) if x}


def algebra(ports, words):
    q = [[F(i == j == 0) for j in range(8)] for i in range(8)]
    failures = {}
    histograms = {}
    word_hashes = {}
    need([p["port"] for p in ports] == [p["port"] for p in words] == list(range(111)),
         "Oracle exact port inventory")
    for port, witness in zip(ports, words):
        w = [[F(x) for x in row] for row in port["normalizer"]]
        wi = [[F(x) for x in row] for row in port["inverse"]]
        need(word_matrix(witness["forward_word"]) == w
             and word_matrix(witness["inverse_word"]) == wi,
             "Oracle frozen word to actual port matrix")
        need(multiply(w, wi) == eye() == multiply(wi, w), "Oracle both port inverses")
        # Reconstruct the orthogonal line projector directly from the literal
        # first source column, independently of W Q W^-1.
        line = [row[0] for row in w]
        norm = sum((x * x for x in line), F(0))
        need(norm > 0, "Oracle nonzero actual source line")
        projector = [[x * y / norm for y in line] for x in line]
        need(all(sum((line[i] * w[i][j] for i in range(8)), F(0)) == 0
                 for j in range(1, 8)), "Oracle literal source complement orthogonality")
        need(multiply(projector, w) == multiply(w, q),
             "Oracle actual line/complement normalizer")
        need(multiply(multiply(wi, projector), w) == q,
             "Oracle cover ENTRY inverse, RETURN forward")
        if "wrong_cover_direction" not in failures:
            changed = multiply(multiply(w, projector), wi)
            if changed != q:
                axis = next(j for j in range(8)
                            if any(changed[i][j] != q[i][j] for i in range(8)))
                failures["wrong_cover_direction"] = {
                    "port": port["port"], "axis": axis,
                    "expected": compact([q[i][axis] for i in range(8)]),
                    "actual": compact([changed[i][axis] for i in range(8)])}
        for direction in ("forward", "inverse"):
            word = witness[direction + "_word"]
            word_hashes[(port["port"], direction)] = digest(word)
            histograms[(port["port"], direction)] = Counter(
                (p2_event(event)[0], str(p2_event(event)[3])) for event in word)
        for axis in range(16):
            x = [F(i == axis) for i in range(16)]
            expected = native(q, x)
            actual = paired_basis(wi, native(projector, paired_basis(w, x)))
            need(actual == expected, "Oracle every literal paired address basis column")
            for bad in ("unreflected", "omit_second"):
                if bad not in failures:
                    changed = paired_basis(wi, native(projector,
                        paired_basis(w, x, bad)), bad)
                    if changed != expected:
                        failures[bad] = {"port": port["port"], "axis": axis,
                                         "expected": compact(expected),
                                         "actual": compact(changed)}
    need(set(failures) == {"unreflected", "omit_second", "wrong_cover_direction"},
         "Oracle discriminating actual-port direction/reflection/half controls")
    return histograms, word_hashes, failures


def layouts_for(stages, words):
    layouts = []
    for ordinal, stage in enumerate(stages):
        active = [0] + list(range(1 + 7 * ordinal, 8 + 7 * ordinal))
        actual = words["placements"][ordinal]
        need(actual == {"active_indices": active, "ordinal": ordinal, "stage": stage},
             "Oracle chosen layout binds stage ordinal, not raw stage ID")
        spectators = set(range(127)) - set(active)
        need(len(set(active)) == 8 and len(spectators) == 119,
             "Oracle all inactive stage coordinates")
        for f in (1, 2):
            lifted = {c * f + lane for c in active for lane in range(f)}
            need(len(lifted) == 8 * f
                 and len(set(range(127 * f)) - lifted) == 119 * f,
                 "Oracle tensor lanes and spectator completeness")
        layouts.append({"stage": stage, "ordinal": ordinal, "active": active,
                        "spectator_count": len(spectators)})
    need(len(words["placements"]) == len(stages), "Oracle no additional layout")
    return layouts


def cover_controls(join, calls, ports, words):
    # Choose the two distinct actual owner banks for stage1/port0. Reassign one
    # ENTRY to the other bank while retaining all four words and every count.
    call_index = 1
    banks = [calls[call_index]["source_bank"], calls[call_index]["target_bank"]]
    need(len(set(banks)) == 2, "Oracle distinct actual owner banks")
    rows = [row for row in join if row[1] == call_index and row[4] == 0]
    need(len(rows) == 4, "Oracle concrete four-marker control scope")
    w = [[F(x) for x in row] for row in ports[0]["normalizer"]]
    wi = [[F(x) for x in row] for row in ports[0]["inverse"]]
    matrices = {"forward": w, "inverse": wi}

    def endpoint(reassign=False, wrong_return=False):
        covers = {bank: eye() for bank in banks}
        assignments = []
        for row in rows:
            bank, direction = row[3] // 111, row[6]
            if reassign and row[5] == "ENTRY" and bank == banks[1]:
                bank = banks[0]
            if wrong_return and row[5] == "RETURN" and bank == banks[1]:
                direction = "inverse"
            covers[bank] = multiply(covers[bank], matrices[direction])
            assignments.append((bank, direction))
        return covers, assignments

    good, good_assignments = endpoint()
    bad, bad_assignments = endpoint(reassign=True)
    phase, phase_assignments = endpoint(wrong_return=True)
    need(all(matrix == eye() for matrix in good.values()),
         "Oracle actual two-bank cover restoration")
    need(Counter(direction for bank, direction in good_assignments)
         == Counter(direction for bank, direction in bad_assignments),
         "Oracle owner control retains every word/coefficient multiplicity")
    need(any(matrix != eye() for matrix in bad.values()),
         "Oracle duplicate-bank control fails actual cover restoration")
    lengths = {direction: len(words[0][direction + "_word"])
               for direction in ("forward", "inverse")}
    need(sum(lengths[d] for b, d in good_assignments)
         == sum(lengths[d] for b, d in phase_assignments),
         "Oracle phase control retains total elementary call count")
    need(any(matrix != eye() for matrix in phase.values()),
         "Oracle wrong RETURN control fails actual cover restoration")
    return {
        "duplicate_bank_same_coefficient_counts": {
            "call_index": call_index, "stage": calls[call_index]["stage"],
            "port": 0, "source_events": [row[0] for row in rows],
            "banks": banks, "marker_count": 4,
            "same_word_and_coefficient_histogram": True,
            "actual_cover_diagonals": {str(bank): [str(bad[bank][i][i])
                                                   for i in range(8)] for bank in banks}},
        "wrong_return_same_factor_count": {
            "call_index": call_index, "port": 0, "marker_count": 4,
            "elementary_call_count": sum(lengths[d] for b, d in good_assignments),
            "actual_cover_diagonals": {str(bank): [str(phase[bank][i][i])
                                                   for i in range(8)] for bank in banks}},
    }


def run():
    events, ports, calls, controller, words = (source(name) for name in PINS)
    need(len(events) == 317004 and len(calls) == 18, "Oracle exact stream and calls")
    stages = controller["invoice"]["thick_stages"]
    need(controller["ambient_rank"] == 127
         and [call["stage"] for call in calls] == stages
         and len(set(stages)) == 18 and stages[0] == 0,
         "Oracle actual thick-stage order")
    layouts = layouts_for(stages, words)
    histograms, word_hashes, controls = algebra(ports["port_interfaces"]["ports"],
                                              words["ports"])
    by_stage = {call["stage"]: (i, call) for i, call in enumerate(calls)}
    join, seen, counts = [], set(), Counter()
    stage_phase, bank_phase = Counter(), Counter()
    for event_index, event in enumerate(events):
        if event[0] != "PAID_PORT_ROUTE":
            continue
        need(len(event) == 5, "Oracle actual route arity")
        _, stage, owner, port, phase = event
        need(type(stage) is int and stage in by_stage and stage != 0
             and phase in ("ENTRY", "RETURN"),
             "Oracle actual route stage and phase")
        call_index, call = by_stage[stage]
        need(type(owner) is int and type(port) is int and 0 <= port < 111,
             "Oracle actual route owner and port")
        bank, residue = divmod(owner, 111)
        need(residue == port and bank in (call["source_bank"], call["target_bank"]),
             "Oracle source-call owner/port join")
        start = call["core_begin"] - 222 if phase == "ENTRY" else call["core_end"]
        need(start <= event_index < start + 222, "Oracle route call-boundary interval")
        key = (call_index, bank, port, phase)
        need(key not in seen, "Oracle unique actual route incidence")
        seen.add(key)
        direction = "inverse" if phase == "ENTRY" else "forward"
        word_hash = word_hashes[(port, direction)]
        join.append([event_index, call_index, stage, owner, port, phase,
                     direction, word_hash])
        counts.update(histograms[(port, direction)])
        stage_phase[(stage, phase)] += 1
        bank_phase[(bank, phase)] += 1
    wanted = {(i, bank, port, phase)
              for i, call in enumerate(calls) if call["stage"] != 0
              for bank in (call["source_bank"], call["target_bank"])
              for port in range(111) for phase in ("ENTRY", "RETURN")}
    need(seen == wanted and len(join) == 7548, "Oracle every actual route exactly once")
    controls.update(cover_controls(join, calls, ports["port_interfaces"]["ports"],
                                   words["ports"]))
    named = []
    for f in (1, 2):
        n = 127 * f
        named.append({"f": f, "N": n,
            "coefficient_counts": [{"primitive": "ordered_shift" if kind == "ADD"
                                     else "unit_scale", "coefficient": value,
                                     "count": count * n * f}
                                    for (kind, value), count in sorted(counts.items())]})
    return {
        "status": "PASS_G20_ROUTE_WORD_BINDING_ORACLE",
        "source_sha256": {name: row[1] for name, row in PINS.items()},
        "event_count": len(events), "route_count": len(join),
        "event_join_columns": ["event_index", "call_index", "stage", "owner", "port",
                               "phase", "direction", "word_sha256"],
        "event_join_sha256": digest(join),
        "stage_phase_counts": [{"stage": stage, "phase": phase, "count": count}
                               for (stage, phase), count in sorted(stage_phase.items())],
        "bank_phase_counts": [{"bank": bank, "phase": phase, "count": count}
                              for (bank, phase), count in sorted(bank_phase.items())],
        "word_products": 222, "cover_conjugations": 111, "paired_basis_columns": 1776,
        "stage_layouts": layouts,
        "paired_basis_order": "x0..x7; x15..x8; physical D=diag(W,J W J)",
        "cover_recipe": "One retained cover route g->g W^-1 at ENTRY and g->g W "
                        "at RETURN. (g W^-1)P(g W^-1)^-1=g Q g^-1.",
        "cover_word_instances": len(join), "cover_words_per_marker": 1,
        "native_address_halves": 2,
        "half_count_scope": "Both native halves are normalized by the same changed "
                            "cover matrix. They do not duplicate this cover-route word.",
        "named_P2_kernel_counts": named, "negative_controls": controls,
        "scope": "Conditional finite cover-route word binding and coefficient counts. "
                 "The source marker does not implement a full physical route. Low "
                 "cache/carry/permutation, ROW borrow/pad/return, coefficient preparation, "
                 "head motion, tape tariffs and full compiler admission remain open.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true",
                        help="Print a candidate receipt without writing files")
    args = parser.parse_args()
    value = run()
    if args.emit:
        print(json.dumps(value, indent=2, sort_keys=True))
    else:
        need(canonical(json.loads((HERE / "ORACLE.json").read_bytes())) == canonical(value),
             "Oracle complete retained receipt")
        print(json.dumps({"status": value["status"], "routes": value["route_count"],
                          "event_join_sha256": value["event_join_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
