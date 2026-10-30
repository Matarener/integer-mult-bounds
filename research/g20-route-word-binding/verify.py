#!/usr/bin/env python3
"""Bind actual G20 route markers to frozen RIGHT words under a cover plan.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Retains Ali Romman's G20 source credit and the S3 word/ROW lineage in NOTICE.
This checker does not import sibling code or implement physical tape primitives.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json


HERE = Path(__file__).resolve().parent
PINS = {
    "GLOBAL.jsonl.gz": "86e7ce6aff05409410ef4bbc00ff1b29b8c1606383549c7e15242b327e39c235",
    "PORTS.json": "a53a49c938a46c5a9da8c05ffdec4c2ef2dd906dd94c009d6fa451af4ed350e9",
    "CALLS.json": "30dcc37cdade6b2dc05478837eca28b696894d1c4782bac6a1caab5e7f56c9e8",
    "CONTROLLER.json": "39ac84fb848b908f7ba051fae4556d507900c421dc5d23501a9c0cb1d61fd08d",
    "WORDS.json": "c74b8446503425fb4964921e8651b3931f917c62a21565d9569e9f6399ea571b",
}
COLUMNS = ["event_index", "call_index", "stage", "owner", "port", "phase",
           "direction", "word_sha256", "stage_ordinal", "owner_bank"]


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def authenticate(name, raw):
    need(sha256(raw).hexdigest() == PINS[name], "source bytes: " + name)


def right_product(word):
    matrix = [[Q(i == j) for j in range(8)] for i in range(8)]
    for operation in word:
        opcode, i = operation[:2]
        need(type(i) is int and 0 <= i < 8, "program coordinate")
        if opcode == "ADD":
            need(len(operation) == 4, "program ADD arity")
            j, coefficient = operation[2], Q(operation[3])
            need(type(j) is int and 0 <= j < 8 and i != j and coefficient
                 and coefficient.denominator & (coefficient.denominator - 1) == 0,
                 "program dyadic ADD")
            for row in matrix:
                row[j] += coefficient * row[i]
        else:
            need(opcode == "SCALE" and len(operation) == 3, "program SCALE arity")
            coefficient = Q(operation[2])
            numerator, denominator = abs(coefficient.numerator), coefficient.denominator
            need(numerator > 0 and numerator & (numerator - 1) == 0
                 and denominator & (denominator - 1) == 0, "program dyadic-unit SCALE")
            for row in matrix:
                row[i] *= coefficient
    return matrix


def programs(words, ports):
    need([record["port"] for record in words["ports"]] == list(range(111))
         == [record["port"] for record in ports["port_interfaces"]["ports"]],
         "all source program ports")
    references, by_hash, catalogue = {}, {}, []
    for record, source in zip(words["ports"], ports["port_interfaces"]["ports"]):
        need(record["line"] == source["line"] and record["complement"] == source["complement"],
             "source port geometry binding")
        for direction, target in (("forward", "normalizer"), ("inverse", "inverse")):
            word = record[direction + "_word"]
            # These are dependency checks, not a claim to newly construct S3.
            need(right_product(word) == [[Q(value) for value in row] for row in source[target]],
                 "frozen RIGHT word matrix binding")
            word_hash = digest(word)
            references[record["port"], direction] = word_hash
            by_hash[word_hash] = word
            catalogue.append({"port": record["port"], "direction": direction,
                              "word_sha256": word_hash, "operations": len(word)})
    return references, by_hash, catalogue


def expected_routes(events, calls, stages):
    """Independently build every marker's receiver from declared core boundaries."""
    need([call["stage"] for call in calls] == stages
         == [0, 1, *range(3, 32, 2), 32], "source thick-call stages")
    expected = {}
    for ordinal, call in enumerate(calls):
        stage = call["stage"]
        need(call["source_bank"] != call["target_bank"], "distinct call banks")
        if stage == 0:
            continue
        for phase, start in (("ENTRY", call["core_begin"] - 222),
                             ("RETURN", call["core_end"])):
            for bank_position, bank in enumerate((call["source_bank"], call["target_bank"])):
                for port in range(111):
                    index = start + bank_position * 111 + port
                    need(0 <= index < len(events) and index not in expected, "disjoint route intervals")
                    owner = 111 * bank + port
                    expected[index] = (ordinal, stage, owner, port, phase, bank)
                    need(events[index] == ["PAID_PORT_ROUTE", stage, owner, port, phase],
                         "actual source route interval")
    actual = {index for index, event in enumerate(events) if event[0] == "PAID_PORT_ROUTE"}
    need(actual == set(expected), "actual marker interval bijection")
    return expected


def make_manifest(events, calls, stages, references, expected):
    manifest = []
    for index, event in enumerate(events):
        if event[0] != "PAID_PORT_ROUTE":
            continue
        ordinal, stage, owner, port, phase, bank = expected[index]
        direction = "inverse" if phase == "ENTRY" else "forward"
        manifest.append([index, ordinal, stage, owner, port, phase, direction,
                         references[port, direction], ordinal, bank])
    return manifest


def tally(manifest, by_hash):
    """Recompute the coefficient bill from bound words, never an inherited total."""
    histograms = {"ADD": Counter(), "SCALE": Counter()}
    phase_stage, bank_phase, port_direction = Counter(), Counter(), Counter()
    for row in manifest:
        index, call_index, stage, owner, port, phase, direction, word_hash, ordinal, bank = row
        need(word_hash in by_hash, "known concrete program hash")
        phase_stage[stage, phase] += 1
        bank_phase[bank, phase] += 1
        port_direction[port, direction] += 1
        for operation in by_hash[word_hash]:
            histograms[operation[0]][str(Q(operation[-1]))] += 1
    histogram = {kind: dict(sorted(counter.items(), key=lambda item: Q(item[0])))
                 for kind, counter in histograms.items()}
    return {
        "coefficient_histogram": histogram,
        "scalar_word_operations": {kind: sum(counter.values()) for kind, counter in histograms.items()},
        "stage_phase_counts": [[stage, phase, count]
                               for (stage, phase), count in sorted(phase_stage.items())],
        "bank_phase_counts": [[bank, phase, count]
                              for (bank, phase), count in sorted(bank_phase.items())],
        "port_direction_counts": [[port, direction, count]
                                   for (port, direction), count in sorted(port_direction.items())],
        "conditional_named_primitive_counts_times_f_squared": {
            kind: {coefficient: 127 * count for coefficient, count in counter.items()}
            for kind, counter in histogram.items()},
    }


def validate_manifest(manifest, expected, references, placements):
    indices = [row[0] for row in manifest]
    need(len(indices) == len(set(indices)) and set(indices) == set(expected),
         "route-event coverage")
    for row in manifest:
        index, call_index, stage, owner, port, phase, direction, word_hash, ordinal, bank = row
        source_call, source_stage, source_owner, source_port, source_phase, source_bank = expected[index]
        need(call_index == source_call and stage == source_stage, "source call/stage binding")
        need(owner == source_owner and port == source_port and bank == source_bank
             and owner == 111 * bank + port, "owner bank/port binding")
        need(phase == source_phase, "source route phase")
        need(direction == ("inverse" if source_phase == "ENTRY" else "forward"),
             "single-cover route direction")
        need(word_hash == references[port, direction], "bound concrete port program")
        need(ordinal == source_call and placements[ordinal]["stage"] == stage,
             "stage ordinal binding")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit candidate only; never write files")
    args = parser.parse_args()
    raw = {name: (HERE / "source" / name).read_bytes() for name in PINS}
    for name, content in raw.items():
        authenticate(name, content)
    decoded = gzip.decompress(raw["GLOBAL.jsonl.gz"])
    events = [json.loads(line) for line in decoded.splitlines()]
    ports, calls, controller, words = (json.loads(raw[name]) for name in
                                      ("PORTS.json", "CALLS.json", "CONTROLLER.json", "WORDS.json"))
    need(len(events) == ports["events"] == 317004
         and sha256(decoded).hexdigest() == ports["stream_sha256"], "retained stream receipt")
    stages = controller["invoice"]["thick_stages"]
    placements = words["placements"]
    need([record["stage"] for record in placements] == stages, "S3 placement stages")
    for ordinal, record in enumerate(placements):
        need(record["ordinal"] == ordinal and record["active_indices"]
             == [0] + list(range(1 + 7 * ordinal, 8 + 7 * ordinal)), "S3 compatible placement")
    references, by_hash, catalogue = programs(words, ports)
    expected = expected_routes(events, calls, stages)
    manifest = make_manifest(events, calls, stages, references, expected)
    bill = tally(manifest, by_hash)
    validate_manifest(manifest, expected, references, placements)
    need(len(manifest) == 7548, "source-specific marker count")
    need(all(count == 34 for _, _, count in bill["port_direction_counts"])
         and len(bill["port_direction_counts"]) == 222, "observed per-port direction multiplicity")
    need(all(bill["coefficient_histogram"][kind]
             == {coefficient: 34 * count for coefficient, count in counts.items()}
             for kind, counts in words["operation_histogram_both_directions"].items()),
         "actual marker histogram versus S3 words")
    controls = []

    def reject(name, reason, mutate):
        changed = deepcopy(manifest)
        mutate(changed)
        # Recompute a coherent bill before testing the source join. A stale
        # aggregate receipt/hash is not the rejection mechanism.
        rebuilt = tally(changed, by_hash)
        try:
            validate_manifest(changed, expected, references, placements)
        except ValueError as error:
            need(str(error) == reason, "control rejected for unintended reason: " + name)
            controls.append({"name": name, "reason": str(error), "rejected": True,
                             "recomputed_bill_sha256": digest(rebuilt)})
        else:
            raise ValueError("semantic control accepted: " + name)

    reject("omitted_marker", "route-event coverage", lambda rows: rows.pop(0))
    reject("wrong_owner", "owner bank/port binding", lambda rows: rows[0].__setitem__(3, rows[0][3] + 1))

    def wrong_phase(rows):
        rows[0][5:8] = ["RETURN", "forward", references[rows[0][4], "forward"]]

    def wrong_direction(rows):
        rows[0][6:8] = ["forward", references[rows[0][4], "forward"]]

    reject("coherently_rebound_wrong_phase", "source route phase", wrong_phase)
    reject("coherently_rebound_wrong_direction", "single-cover route direction", wrong_direction)
    reject("foreign_port_program", "bound concrete port program",
           lambda rows: rows[0].__setitem__(7, references[1, "inverse"]))
    wrong_ordinal = next(index for index, row in enumerate(manifest) if row[2] == 3)
    reject("raw_stage_as_ordinal", "stage ordinal binding",
           lambda rows: rows[wrong_ordinal].__setitem__(8, 3))
    try:
        authenticate("GLOBAL.jsonl.gz", raw["GLOBAL.jsonl.gz"] + b" ")
    except ValueError as error:
        need(str(error) == "source bytes: GLOBAL.jsonl.gz", "source control reason")
        controls.append({"name": "source_corruption", "reason": str(error), "rejected": True})
    else:
        raise ValueError("source corruption accepted")
    result = {
        "schema": "g20-route-word-binding/1", "source_raw_sha256": PINS,
        "source_stream_sha256": ports["stream_sha256"], "source_events": len(events),
        "marker_count": len(manifest), "single_cover_word_instances": len(manifest),
        "manifest_columns": COLUMNS, "manifest": manifest,
        "manifest_sha256": digest(manifest),
        "event_join_sha256": digest([row[:8] for row in manifest]),
        "program_catalogue": catalogue, "placements": placements,
        "cover_convention": "Declared single ROW cover g->gS: P=WQW^-1, ENTRY S=W^-1, RETURN S=W; one word per marker",
        "RIGHT_word_convention": words["word_convention"],
        "multiplicity": "Observed 17 nonzero stages * 2 owner banks * 111 ports * 2 phases; no extra paired-half multiplier",
        "conditional_coefficient_bill": "For each observed word coefficient a, count[a]*(127*f)*f*C_kind(a); no physical leaf tariff is asserted",
        "source_dependency_scope": "5798 endpoint/native/marker audit and S3 factor construction are retained dependencies, not new whole-caller acceptance",
        "physical_scope": "Exact source-event to program manifest under the declared single-cover plan; physical ROW schedule, tape/cache/carry/type/borrow/padding and full bill remain open",
        **bill, "failure_controls": controls,
    }
    if not args.emit:
        need(canonical(result) == canonical(json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))),
             "frozen canonical RESULT.json comparison")
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_G20_ROUTE_WORD_BINDING")


if __name__ == "__main__":
    main()
