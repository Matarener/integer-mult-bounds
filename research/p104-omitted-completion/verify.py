#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact normalized endpoint completion of the PR3446 P104 projection.

Nick Petalas. PR3446 supplies the question and projection definition; PR2586
supplies the unchanged word/native archive. No predecessor executable is used.
"""

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/p104-rounded-collector/inputs/WORD.json"
NATIVE = "research/p104-rounded-collector/inputs/NATIVE.json.gz"
HASHES = {
    WORD: "cec1fb3fbd0067b500ad5119a62ba60685be718e769374d7ec8abdd2beaa7e50",
    NATIVE: "ab91c78835c3e10cf3b2cb8a5d4e0b7cfc3df1ae5a811298d27842f2193e1e3d",
}
BASIS = ("X0", "X33", "X101", "X102", "X11", "X12", "X15", "X24")
COLUMNS = ("Y0", "Y10", "Y100", "Y101", "Y102", "Y103", "Y11", "Y12")
ROLES = {f"Y{i}" for i in (*range(22, 33), *range(63, 104))}
ROLES |= {f"{prefix}{i}" for prefix in ("D", "G") for i in range(27, 32)}
ROLES |= {"Q7"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_sources():
    loaded = []
    for name in (WORD, NATIVE):
        path = ROOT / name
        require(
            path.is_file() and not path.is_symlink(), "missing/aliased source " + name
        )
        require(path.stat().st_size <= 1_000_000, "source size limit")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == HASHES[name], "source hash " + name)
        payload = gzip.decompress(raw) if name.endswith(".gz") else raw
        require(len(payload) <= 8_000_000, "source payload limit")
        loaded.append(json.loads(payload, object_pairs_hook=unique))
    return tuple(loaded)


def native_occurrences(word, native):
    """Index the authenticated archive's exact occurrence binding."""
    require(word["chart"] == native["chart"], "native chart")
    require(len(native["transports"]) == 1245, "native classes")
    occurrences = {}
    for record in native["transports"]:
        for event in record["events"]:
            require(type(event) is int and 0 <= event < 5398, "native event range")
            require(event not in occurrences, "duplicate native event")
            occurrences[event] = record
    return occurrences


def bind_frames(word, native):
    """Bind frame chronology and native occurrences, not native matrix semantics."""
    program = word["program"]
    require(len(program) == 5398 and len(word["initial_frames"]) == 358, "word shape")
    occurrences = native_occurrences(word, native)
    frames = deepcopy(word["initial_frames"])
    pairs, active = [], {}
    for event, op in enumerate(program):
        kind, target = op[:2]
        if kind == "zero":
            require(target not in frames, "private alias")
            frames[target] = op[2]
            active[target] = event
            continue
        require(target in frames, "unknown target")
        if kind == "transport":
            require(frames[target] == op[2], "old frame")
            record = occurrences[event]
            require(
                (record["old"], record["new"], record["recipe"]["rank"])
                == (op[2], op[3], op[4]),
                "native occurrence binding",
            )
            frames[target] = op[3]
        elif kind == "add":
            require(
                target != op[2] and frames[target] == frames[op[2]] == op[4],
                "ADD frame",
            )
            require(
                Fraction(op[3])
                in (
                    2,
                    -2,
                    1,
                    -1,
                    Fraction(1, 2),
                    Fraction(-1, 2),
                    Fraction(1, 4),
                    Fraction(-1, 4),
                ),
                "ADD coefficient",
            )
        elif kind == "sign":
            require(Fraction(op[2]) == -1 and frames[target] == op[3], "sign frame")
        elif kind == "erase":
            require(target in active and frames[target] == op[2], "erase frame")
            pairs.append((active.pop(target), event))
            del frames[target]
        else:
            raise ValueError("unknown opcode")
    require(not active and len(pairs) == 8, "private lifetimes")
    require(frames == word["final_frames"], "final frames")
    require(
        set(occurrences) == {i for i, op in enumerate(program) if op[0] == "transport"},
        "complete native occurrence binding",
    )
    return pairs


def bit_histories(word, pairs):
    """Forward provenance bitsets; initial-bank bits follow the 5398 event bits."""
    names = sorted(word["initial_frames"])
    count = len(word["program"])
    state = {name: 1 << (count + i) for i, name in enumerate(names)}
    history = []
    for event, op in enumerate(word["program"]):
        kind, target = op[:2]
        if kind == "zero":
            state[target] = 1 << event
        elif kind == "add":
            state[target] |= state[op[2]] | (1 << event)
        else:
            state[target] |= 1 << event
        history.append(state[target])
        if kind == "erase":
            del state[target]
    cleanup = [(start, history[end]) for start, end in pairs]
    return names, history, state, cleanup


def projection(word, pairs):
    names, history, final, cleanup = bit_histories(word, pairs)
    program = word["program"]
    ports = [
        i
        for i, op in enumerate(program)
        if i <= 4516
        and op[0] == "add"
        and op[2] in ROLES
        and op[1] not in ROLES | {"C"}
    ]
    require(len(ports) == 675, "outgoing port count")
    require(
        digest(ports)
        == "04b3a0bc022c336c9b177eeed49036f1257ab81ea9d0459b8170075b002a24a4",
        "PR3423 port binding",
    )
    mask = 0
    for event in ports:
        mask |= history[event]
    for name in ROLES | {program[i][1] for i in ports}:
        mask |= final[name]
    for _rounds in range(367):
        previous = mask
        for start, history_mask in cleanup:
            if (mask >> start) & 1:
                mask |= history_mask
        for i, name in enumerate(names):
            if (mask >> (5398 + i)) & 1:
                mask |= final[name]
        if previous == mask:
            break
    else:
        raise ValueError("closure iteration limit")
    selected = {i for i in range(5398) if (mask >> i) & 1}
    inputs = {name for i, name in enumerate(names) if (mask >> (5398 + i)) & 1}
    require(len(selected) == 4027 and len(inputs) == 265, "terminal-history closure")
    require(
        digest(sorted(selected))
        == "66113bcd513a17eac24f43944a8759bdae1bb2a85e2b9900122f281c5c676dc8",
        "PR3446 closure event binding",
    )
    return selected, inputs, ports, _rounds + 1


def add_row(target, source, coefficient):
    result = dict(target)
    for name, value in source.items():
        result[name] = result.get(name, Fraction()) + coefficient * value
        if not result[name]:
            del result[name]
    return result


def linear_map(word, selected):
    state = {name: {name: Fraction(1)} for name in word["initial_frames"]}
    frames = deepcopy(word["initial_frames"])
    for event, op in enumerate(word["program"]):
        if selected is not None and event not in selected:
            continue
        kind, target = op[:2]
        if kind == "zero":
            require(target not in state, "linear private alias")
            state[target], frames[target] = {}, op[2]
        elif kind == "transport":
            require(frames[target] == op[2], "projection transport frame")
            frames[target] = op[3]
        elif kind == "add":
            require(frames[target] == frames[op[2]] == op[4], "projection ADD frame")
            state[target] = add_row(state[target], state[op[2]], Fraction(op[3]))
        elif kind == "sign":
            state[target] = {name: -value for name, value in state[target].items()}
        elif kind == "erase":
            require(not state.pop(target), "nonzero private erasure")
            del frames[target]
        else:
            raise ValueError("linear opcode")
    require(set(state) == set(word["initial_frames"]), "public bank set")
    return state, frames


def reverse_row(word, selected, target):
    """Backward covector propagation, independent of forward state dictionaries."""
    row = {target: Fraction(1)}
    for event in range(5397, -1, -1):
        if selected is not None and event not in selected:
            continue
        op = word["program"][event]
        kind, destination = op[:2]
        if kind == "zero":
            row.pop(destination, None)
        elif kind == "sign" and destination in row:
            row[destination] = -row[destination]
        elif kind == "add" and destination in row:
            source = op[2]
            row[source] = (
                row.get(source, Fraction()) + Fraction(op[3]) * row[destination]
            )
            if not row[source]:
                del row[source]
        else:
            require(kind in ("add", "sign", "transport", "erase"), "reverse opcode")
    require(set(row) <= set(word["initial_frames"]), "reverse private source")
    return row


def residual_map(full, sliced, inputs):
    residual = {}
    for target in sorted(full):
        row = add_row(full[target], sliced[target], Fraction(-1))
        if row:
            require(target not in inputs and target.startswith("X"), "residual target")
            require(all(source.startswith("Y") for source in row), "residual source")
            residual[target] = row
        if target in inputs:
            require(not row, "retained terminal mismatch")
    require(len(residual) == 52, "residual row count")
    for target, row in full.items():
        require(row.get(target) == 1, "dirty identity coefficient")
        require(
            all(
                name == target or target.startswith("X") and name.startswith("Y")
                for name in row
            ),
            "full dirty restoration",
        )
    return residual


def inverse_minor(matrix):
    require(len(matrix) == 8 and all(len(row) == 8 for row in matrix), "minor shape")
    aug = [
        list(row) + [Fraction(i == j) for j in range(8)] for i, row in enumerate(matrix)
    ]
    determinant = Fraction(1)
    for col in range(8):
        pivot = next((i for i in range(col, 8) if aug[i][col]), None)
        require(pivot is not None, "singular minor")
        if pivot != col:
            aug[pivot], aug[col] = aug[col], aug[pivot]
            determinant = -determinant
        scale = aug[col][col]
        determinant *= scale
        aug[col] = [value / scale for value in aug[col]]
        for i in range(8):
            if i != col:
                scale = aug[i][col]
                aug[i] = [a - scale * b for a, b in zip(aug[i], aug[col], strict=True)]
    return determinant, [row[8:] for row in aug]


def check_factor(residual, gather, scatter):
    for target, row in residual.items():
        for source in (f"Y{i}" for i in range(104)):
            value = (
                sum(
                    (scatter[target][k] * gather[k].get(source, 0) for k in range(8)),
                    Fraction(),
                )
                / 2
            )
            require(value == row.get(source, 0), "factor identity")


def factor(residual):
    gather = [
        {source: int(2 * value) for source, value in residual[target].items()}
        for target in BASIS
    ]
    require(
        all(
            Fraction(gather[i][source]) == 2 * value
            for i, target in enumerate(BASIS)
            for source, value in residual[target].items()
        ),
        "integral gather",
    )
    square = [
        [Fraction(gather[i].get(source, 0)) for source in COLUMNS] for i in range(8)
    ]
    determinant, inverse = inverse_minor(square)
    require(determinant == -2, "rank-eight 2R minor determinant")
    scatter = {}
    for target, row in residual.items():
        coordinates = [
            sum(
                (2 * row.get(COLUMNS[k], 0) * inverse[k][j] for k in range(8)),
                Fraction(),
            )
            for j in range(8)
        ]
        require(
            all(value.denominator == 1 for value in coordinates), "integral scatter"
        )
        scatter[target] = [int(value) for value in coordinates]
    check_factor(residual, gather, scatter)
    return gather, scatter


def mat_read(row, values):
    return sum(
        (coefficient * values[source] for source, coefficient in row.items()),
        Fraction(),
    )


def completion(values, helpers, gather, scatter, cancel_dirty=True):
    """Abstract weighted transvections in a common normalized module."""
    result, scratch = dict(values), list(helpers)
    if cancel_dirty:
        for target, row in scatter.items():
            result[target] -= sum((row[k] * scratch[k] for k in range(8)), Fraction())
    for k, row in enumerate(gather):
        scratch[k] += mat_read(row, values) / 2
    for target, row in scatter.items():
        result[target] += sum((row[k] * scratch[k] for k in range(8)), Fraction())
    for k, row in enumerate(gather):
        scratch[k] -= mat_read(row, values) / 2
    require(scratch == list(helpers), "dirty summary restoration")
    return result, scratch


def serial_completion(values, dirty, gather, scatter):
    """Eight summaries in sequence through one restored dirty module element."""
    result = dict(values)
    initial_dirty = dirty
    for k, row in enumerate(gather):
        for target, coefficients in scatter.items():
            result[target] -= coefficients[k] * dirty
        dirty += mat_read(row, values) / 2
        for target, coefficients in scatter.items():
            result[target] += coefficients[k] * dirty
        dirty -= mat_read(row, values) / 2
        require(dirty == initial_dirty, "serial dirty summary restoration")
    return result, dirty


def evaluate(word, selected, values):
    state = dict(values)
    for event, op in enumerate(word["program"]):
        if selected is not None and event not in selected:
            continue
        kind, target = op[:2]
        if kind == "zero":
            state[target] = Fraction()
        elif kind == "add":
            state[target] += Fraction(op[3]) * state[op[2]]
        elif kind == "sign":
            state[target] = -state[target]
        elif kind == "erase":
            require(state.pop(target) == 0, "fixture private dirt")
        else:
            require(kind == "transport", "fixture opcode")
    return state


def fixtures(word, selected, residual, gather, scatter):
    for seed in range(6):
        values = {
            name: Fraction(
                ((j * 37 + seed * 11) % 43 - 21)
                * (4 if name.startswith(("Y", "N")) else 1)
            )
            for j, name in enumerate(sorted(word["initial_frames"]))
        }
        dirty = [Fraction((k * 19 + seed * 13) % 31 - 15) for k in range(8)]
        sliced = evaluate(word, selected, values)
        patched, _ = completion(sliced, dirty, gather, scatter)
        serial, restored = serial_completion(sliced, dirty[0], gather, scatter)
        require(restored == dirty[0] and serial == patched, "serial completion fixture")
        require(
            patched == evaluate(word, None, values), "whole-word fixture completion"
        )
        require(
            all(value.denominator == 1 for value in patched.values()),
            "module output fixture",
        )
        for row in gather:
            require(
                (mat_read(row, sliced) / 2).denominator == 1, "module gather fixture"
            )
    # This half-integral coefficient prevents inferring arbitrary-M admission.
    target = next(
        name
        for name, row in residual.items()
        if any(v.denominator == 2 for v in row.values())
    )
    source = next(
        name for name, value in residual[target].items() if value.denominator == 2
    )
    require(residual[target][source].denominator == 2, "unit-input residual control")
    return {
        "scalar_fixtures": 6,
        "parallel_helpers": 8,
        "serial_helpers": 1,
        "nonintegral_unit_input": [target, source, str(residual[target][source])],
    }


def controls(word, native, residual, gather, scatter):
    rejected = []

    def rejects(label, operation):
        try:
            operation()
        except (ValueError, KeyError):
            rejected.append(label)
        else:
            raise ValueError("accepted negative control " + label)

    bad = deepcopy(gather)
    source = next(iter(bad[0]))
    bad[0][source] += 1
    rejects("wrong_gather_coefficient", lambda: check_factor(residual, bad, scatter))
    bad_scatter = deepcopy(scatter)
    bad_scatter[next(iter(bad_scatter))][0] += 1
    rejects(
        "wrong_scatter_coefficient", lambda: check_factor(residual, gather, bad_scatter)
    )
    rank_seven = [dict(row) if i < 7 else {} for i, row in enumerate(gather)]
    rejects(
        "seven_summary_truncation", lambda: check_factor(residual, rank_seven, scatter)
    )
    changed = deepcopy(word)
    changed["program"][2038][3] = "1"
    rejects("dirty_private_erasure", lambda: linear_map(changed, None))
    changed_native = deepcopy(native)
    changed_native["transports"][0]["recipe"]["rank"] += 1
    rejects("native_rank_binding", lambda: bind_frames(word, changed_native))
    values = {name: Fraction() for name in word["initial_frames"]}
    dirty = [Fraction(i + 1) for i in range(8)]
    wrong, _ = completion(values, dirty, gather, scatter, cancel_dirty=False)
    require(any(wrong.values()), "uncancelled dirty summary control")
    return rejected + ["uncancelled_dirty_summaries"]


def json_rows(rows):
    return {
        target: {source: str(value) for source, value in sorted(row.items())}
        for target, row in sorted(rows.items())
    }


def residual_receipt(residual, inputs, full_frames, slice_frames):
    omitted = sorted(set(full_frames) - inputs)
    zero_rows = sorted(set(omitted) - set(residual))
    gaps = {name: [slice_frames[name], full_frames[name]] for name in omitted}
    require(all(old != new for old, new in gaps.values()), "93 omitted frame gaps")
    require(
        all(slice_frames[name] == full_frames[name] for name in inputs),
        "retained final frames",
    )
    require(len(zero_rows) == 41, "zero residual rows")
    return {
        "rows": sorted(residual),
        "zero_omitted_rows": zero_rows,
        "nonzero_entries": sum(map(len, residual.values())),
        "matrix_sha256": digest(json_rows(residual)),
        "rank": 8,
        "minor_rows": BASIS,
        "minor_columns": COLUMNS,
        "minor_determinant": "-1/128",
    }, gaps


def audit(word, native):
    pairs = bind_frames(word, native)
    selected, inputs, ports, rounds = projection(word, pairs)
    full, full_frames = linear_map(word, None)
    sliced, slice_frames = linear_map(word, selected)
    residual = residual_map(full, sliced, inputs)
    for name in sorted(full):
        require(reverse_row(word, None, name) == full[name], "reverse full-row oracle")
        require(
            reverse_row(word, selected, name) == sliced[name],
            "reverse slice-row oracle",
        )
    gather, scatter = factor(residual)
    residual_record, gaps = residual_receipt(
        residual, inputs, full_frames, slice_frames
    )
    outside = [
        i
        for i, op in enumerate(word["program"])
        if i not in selected
        and op[0] == "add"
        and op[2] in inputs
        and op[1] not in inputs
    ]
    require(len(outside) == 696, "omitted outgoing effects")
    result = {
        "schema_version": 1,
        "scope": "Chart-normalized endpoints; physical adapters unclaimed.",
        "source_sha256": HASHES,
        "reverse_oracle_rows": 716,
        "closure": {
            "ports": len(ports),
            "events": len(selected),
            "inputs": len(inputs),
            "rounds": rounds,
            "events_sha256": digest(sorted(selected)),
            "inputs_sha256": digest(sorted(inputs)),
        },
        "omitted_outgoing_adds": outside,
        "omitted_opcode_counts": dict(
            Counter(op[0] for i, op in enumerate(word["program"]) if i not in selected)
        ),
        "residual": residual_record,
        "factor": {
            "identity": "R = C A / 2",
            "A": gather,
            "C": scatter,
            "A_nonzeros": sum(map(len, gather)),
            "C_nonzeros": sum(bool(v) for row in scatter.values() for v in row),
            "abstract_weighted_updates": 2
            * (
                sum(map(len, gather))
                + sum(bool(v) for row in scatter.values() for v in row)
            ),
        },
        "unfilled_physical_frame_gaps": gaps,
        "fixtures": fixtures(word, selected, residual, gather, scatter),
        "controls": controls(word, native, residual, gather, scatter),
    }
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, help="Write a fresh receipt; refuse overwrite."
    )
    args = parser.parse_args()
    result = audit(*read_sources())
    if args.out is not None:
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(
            (HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=unique
        )
        require(canonical(result) == canonical(expected), "certificate drift")
    print(
        "PASS_P104_OMITTED_COMPLETION events=4027 inputs=265 residual_rows=52 rank=8 frame_gaps=93 no_new_kappa"
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError) as error:
        print("FAIL_P104_OMITTED_COMPLETION: " + str(error), file=sys.stderr)
        sys.exit(1)
