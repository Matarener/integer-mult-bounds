"""Bounded actual-diagonal / arithmetic-H caller join, not a physical layer.

Clear1nsight, with substantial OpenAI Codex assistance, Apache-2.0.
Sagar Thakrar supplies the unchanged PR3617 complete diagonal pass and its
PR3611 packet consumer. Nick Petalas supplies the unchanged PR3593 producer.
"""

from argparse import ArgumentParser
from collections import Counter
from contextlib import ExitStack
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name, path):
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def authenticate():
    manifest_path = HERE / "SOURCE_INVENTORY.json"
    result = {"SOURCE_INVENTORY.json": sha256(manifest_path.read_bytes()).hexdigest()}
    for row in json.loads(manifest_path.read_text())["files"]:
        data = (HERE / "upstream" / row["relative_path"]).read_bytes()
        need(len(data) == row["expected_bytes"], "source length")
        need(sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
             == row["git_blob"], "source Git blob")
        need(sha256(data).hexdigest() == row["sha256"], "source SHA-256")
        result[row["relative_path"]] = row["sha256"]
    return result


def encode(data, width):
    out = ["@"]
    for row in data:
        out.append("^")
        for pair in row:
            for value in pair:
                need(type(value) is int, "p-grid numerator must be a Gaussian integer")
                need(-(1 << (width - 1)) <= value < (1 << (width - 1)), "signed width")
                out.extend((value >> bit) & 1 for bit in range(width - 1, -1, -1))
        out.append("$")
    out.append("!")
    return out


def decode(stream, records, r, width):
    need(stream[0] == "@" and stream[-1] == "!", "whole-stream framing")
    at, rows = 1, []
    for _ in range(records):
        need(stream[at] == "^", "packet start")
        at += 1
        row = []
        for _ in range(r):
            pair = []
            for _ in range(2):
                word = stream[at:at + width]
                need(len(word) == width and all(type(bit) is int and bit in (0, 1)
                                               for bit in word), "signed word")
                value = sum(bit << (width - 1 - j) for j, bit in enumerate(word))
                pair.append(value - ((1 << width) if word[0] else 0))
                at += width
            row.append(tuple(pair))
        need(stream[at] == "$", "packet end")
        at += 1
        rows.append(row)
    need(at == len(stream) - 1, "complete stream extent")
    return rows


def tapes(machine):
    candidates = [*machine.producer.data.values(), machine.producer.descriptor,
                  *(counter.tape for counter in machine.producer.c.values()),
                  *machine.consumer.tapes.values(), *machine.tapes.values()]
    return {id(tape): tape for tape in candidates}


def run(layer):
    initial_sources = authenticate()
    component_hash = sha256(Path(layer.__file__).read_bytes()).hexdigest()
    own_hash = sha256(Path(__file__).read_bytes()).hexdigest()
    adapter = load("retained_3617_pass", HERE / "upstream" / "pass.py")
    producer = load("retained_3593_producer", HERE / "upstream" / "inputs" / "controller.py")
    consumer = load("retained_3611_consumer", HERE / "upstream" / "inputs" / "consumer.py")
    passes = []

    def physical_diagonal(data, ell, flags, k, h, opposite, width):
        descriptor = ("1" * ell + "#" + "1" * k + "#" + "1" * h + "#"
                      + "".join("L" if flag else "S" for flag in flags)
                      + "#" + ("+" if opposite else "-") + "#")
        source = encode(data, width)
        machine = adapter.DiagonalPass(producer, consumer, descriptor, width, source)
        initial = tapes(machine)
        need(len(initial) == 38 and len({id(t.cells) for t in initial.values()}) == 38,
             "38 distinct admitted roles")
        capacities = {key: len(tape.cells) for key, tape in initial.items()}
        borrowed = [machine.tapes[role] for role in ("fullinput", "width", "descriptor")]
        snapshots = [list(t.cells) for t in borrowed]

        def no_allocation(*_args, **_kwargs):
            raise ValueError("runtime tape replacement")

        with ExitStack() as stack:
            for cls in (producer.Tape, consumer.Tape):
                stack.enter_context(patch.object(cls, "__init__", no_allocation))
            output = machine.run()
        final = tapes(machine)
        need(set(final) == set(initial), "stable within-pass roles")
        need(all(len(t.cells) == capacities[key] for key, t in final.items()), "fixed capacities")
        need(all(t.head == 0 for t in final.values()), "all heads returned")
        need(all(t.cells == old for t, old in zip(borrowed, snapshots)), "borrowed bytes returned")
        retained = {id(output), *(id(t) for t in borrowed)}
        need(all(not any(t.cells) for key, t in final.items() if key not in retained),
             "all other roles blank")
        returned = list(output.cells)
        try:
            machine.run()
        except ValueError as error:
            need(str(error) == "one-shot full pass", "one-shot rejection reason")
        else:
            raise ValueError("missing full-pass one-shot rejection")
        need(output.cells == returned and all(t.head == 0 for t in final.values()),
             "one-shot control leaves returned state")
        actions = Counter()
        for tape in final.values():
            actions.update(tape.counts)
        gates = sum(machine.gates.values()) + sum(machine.producer.gates.values()) + sum(machine.consumer.gates.values())
        passes.append({"ell": ell, "flags": list(flags), "K": k, "h": h,
                       "opposite": opposite, "width": width, "records": len(data),
                       "physical_roles_this_stage": 38, "cells": sum(capacities.values()),
                       "tape_actions": dict(sorted(actions.items())), "explicit_gates": gates,
                       "source_tariff_this_diagonal": sum(actions.values()) + gates,
                       "input_sha256": digest(data), "output_stream_sha256": digest(returned)})
        return decode(returned, len(data), 1 << ell, width)

    cases = []
    for ell, flags, k in ((3, (False, False, False), 1), (4, (True,), 2)):
        original, physical = layer.slots_for(ell, flags, k)
        records, r, precision, width = 1 << len(original), 1 << ell, 4, 6
        cube = [[((17 * x + 5 * j + 3) % 17 - 8, (11 * x + 7 * j + 2) % 17 - 8)
                 for j in range(r)] for x in range(records)]
        levels = list(range(ell - 2, -1, -1))
        if any(flags):
            levels.insert(0, ell - 1)
        rounds = []
        for opposite in (False, True):
            actual, reference = layer.reorder(cube, original, physical), cube
            for h in reversed(levels) if opposite else levels:
                reference = layer.reference_round(reference, original, ell, flags, h, opposite)
                if opposite:
                    actual = physical_diagonal(actual, ell, flags, k, h, True, width)
                b, q = (ell - 1) % k, (ell - 1) // k
                g, a = len(flags), sum(flags)
                if b <= h < ell - 1:
                    j, rho = (ell - 2 - h) // k, (h - b) % k
                    left, right = a + g*b + j*g*k, (q-j-1)*g*k
                    need(left + g*k + right == len(physical), "matched active-root extent")
                    bits = tuple(right + rho + t*k for t in range(g))
                    need(set(bits) == set(layer.selected(physical, h)), "matched active-root slots")
                    descriptor = {"g": g, "K": k, "left_bits": left,
                                  "right_bits": right, "offset": rho}
                else:
                    bits = layer.selected(physical, h)
                    descriptor = {"elementary_selected_bits": list(bits)}
                # This is an arithmetic H oracle, not a physical active-root call.
                raw, denominator = layer.h_fast(actual, bits)
                actual = layer.truncate(raw, denominator)
                if not opposite:
                    actual = physical_diagonal(actual, ell, flags, k, h, False, width)
                need(actual == layer.reorder(reference, original, physical), "complete joined round")
                need(all(a*a + b*b <= (1 << (2 * precision)) for row in actual for a, b in row),
                     "whole returned p-grid unit disk")
                rounds.append({"h": h, "opposite": opposite,
                               "arithmetic_H_descriptor": descriptor,
                               "all_coefficients_compared": records * r,
                               "endpoint_sha256": digest(actual)})
        cases.append({"ell": ell, "flags": list(flags), "K": k, "records": records,
                      "precision": precision, "width": width, "rounds": rounds})

    ell, flags, k = 3, (False, False, False), 1
    _, physical = layer.slots_for(ell, flags, k)
    signal = [[(int(x == 0 and j == 0) * 8, 0) for j in range(8)] for x in range(64)]
    raw, divisor = layer.h_fast(signal, layer.selected(physical, 1))
    rounded = layer.truncate(raw, divisor)
    correct = layer.diagonal(rounded, physical, ell, flags, 1)
    wrong = physical_diagonal(rounded, ell, flags, 2, 1, False, 6)
    differences = [(x, j) for x in range(64) for j in range(8) if correct[x][j] != wrong[x][j]]
    need(differences, "wrong-K full-round endpoint control")
    try:
        encode([[(Fraction(1, 2), 0)]], 6)
    except ValueError as error:
        need(str(error) == "p-grid numerator must be a Gaussian integer", "off-grid rejection reason")
    else:
        raise ValueError("missing off-grid encoding rejection")
    need(authenticate() == initial_sources, "all retained source bytes unchanged")
    need(sha256(Path(layer.__file__).read_bytes()).hexdigest() == component_hash,
         "frozen arithmetic component unchanged")
    need(sha256(Path(__file__).read_bytes()).hexdigest() == own_hash, "join implementation unchanged")
    return {"schema": "actual-fixed-diagonal-arithmetic-layer-join-v1",
            "source_head": "4bf091f415d6470b60a5062a08b0a47e5b12dbd7",
            "source_hashes": initial_sources, "arithmetic_component_sha256": component_hash,
            "implementation_sha256": own_hash, "cases": cases, "diagonal_passes": passes,
            "controls": {"wrong_K_endpoint": differences, "off_grid_encoding": True,
                         "one_shot_after_each_pass": True, "no_runtime_tape_replacement": True},
            "scope": {"actual_full_diagonal": True, "H_is_arithmetic_oracle": True,
                      "Q_is_arithmetic_oracle": True, "layout_is_arithmetic_oracle": True,
                      "fresh_stage_instances": True, "all_round_38_role_reuse_proved": False,
                      "production_width_execution": False, "complete_physical_layer": False}}


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--layer-component", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(load("frozen_layer_arithmetic", args.layer_component.resolve())), indent=2, sort_keys=True))
