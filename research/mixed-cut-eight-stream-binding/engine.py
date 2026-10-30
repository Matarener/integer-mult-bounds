#!/usr/bin/env python3
"""Exact identity-cover chronological eight-stream audit of PR4268 half cuts.

Retains Nick Petalas' PR3187 Gaussian-integer phase/shear/data-event code
unchanged, and binds it to Marius-Paul Dumitrean's actual PR2979 T74 fill.
Jacob Sussman's PR4268 supplies the mixed-job question and original head
counts. The physical-stream/E8 predecessor credit remains in the package.
Prepared by ToikY with substantial OpenAI Codex assistance. This is not a
native, all-cover, rounded, supplier, outer-transfer or proof-kernel audit.
"""

from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def loader():
    path = Path(__file__).with_name("source_context.py")
    spec = importlib.util.spec_from_file_location("_mixed_cut_source_context", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load()


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def stream_for(data, child):
    plan = data["plan"]
    return 2 * plan["pairs"][str(child)] + plan["sides"][str(child)]


def allocations(data):
    """Check every literal row and compact prefix; group without dropping calls."""
    loads = defaultdict(int)
    grouped = defaultdict(list)
    for index, row in enumerate(data["rows"]):
        require(len(row) == 6 and all(type(value) is int for value in row), "FILL row types")
        time, helper, owner, child, port, offset = row
        require(time == index // 408 and helper == index % 408, "literal time/helper order")
        require(0 <= owner < 74 and 0 <= port < 112 and 0 <= child < 20, "destination domain")
        stage, caller = data["order"][time]
        tag = data["dispatch"][stage, caller]
        width = data["providers"][tag]["widths"][helper]
        require(type(width) is int and width > 0, "positive literal helper width")
        key = owner, port, child
        require(offset == loads[key], "literal compact prefix or overlap failure")
        loads[key] += width
        rank = data["recipes"][port]["idle_children"][child]["rank"]
        require(loads[key] <= rank, "hosted range exceeds actual child")
        grouped[owner, port].append((time, helper, child, offset, width, caller))
    return loads, grouped


def event_streams(data, recipe, loads, owner, port, event):
    kind = event["kind"]
    if kind == "local_cover_sweep":
        local = next(row for row in data["template"]["recipe"]
                     if row["kind"] == "local" and row["stage"] == event["stage"])
        return (2 * local["pair"], 2 * local["pair"] + 1)
    if kind == "idle_cover_sweep":
        return tuple(stream_for(data, child) for child in event["child_indices"]
                     if recipe["idle_children"][child]["rank"] > loads[owner, port, child]
                     or recipe["idle_children"][child]["translation_after"] != 0)
    if kind == "bridge":
        return (2 * event["dst"], 2 * event["src"],
                2 * event["dst"] + 1, 2 * event["src"] + 1)
    if kind == "terminal_Y_translations":
        return tuple(2 * pair + 1 for pair in event["pairs"] if recipe["q"] != 0)
    if kind == "terminal":
        return tuple(range(8))
    raise ValueError("unknown event in first-touch classifier")


def classify(data, loads, grouped):
    blocks = data["algebra"].stage_blocks(data["template"])
    positions = {(stage, replica): time for time, (stage, replica) in enumerate(data["order"])}
    cut_events = {}
    for stage, events in blocks.items():
        for index, event in enumerate(events):
            if event["kind"] == "idle_cover_sweep":
                for child in event["child_indices"]:
                    require(child not in cut_events, "duplicate child event")
                    cut_events[child] = (stage, index)
    classes = []
    for owner in range(74):
        for port, recipe in enumerate(data["recipes"]):
            first = {}
            for time, helper, child, offset, width, caller in grouped[owner, port]:
                stream = stream_for(data, child)
                position = (time, -1)
                first[stream] = min(first.get(stream, position), position)
            for stage, events in blocks.items():
                for index, event in enumerate(events):
                    position = (positions[stage, owner], index)
                    for stream in event_streams(data, recipe, loads, owner, port, event):
                        first[stream] = min(first.get(stream, position), position)
            for child in (8, 10, 12, 13):
                rank = recipe["idle_children"][child]["rank"] - loads[owner, port, child]
                if rank != 48:
                    continue
                stage, index = cut_events[child]
                stream = stream_for(data, child)
                position = positions[stage, owner], index
                classes.append({"owner": owner, "port": port, "child": child, "stream": stream,
                                "replica_class": owner // 37, "residual_rank": rank,
                                "cut_position": list(position), "first_touch": list(first[stream]),
                                "is_first_touch_head": first[stream] == position})
    return classes, blocks


def fixture_context(data, loads, grouped, item):
    owner, port = item["owner"], item["port"]
    recipe = data["recipes"][port]
    hosts = defaultdict(list)
    host_receipt = []
    for time, helper, child, offset, width, caller in grouped[owner, port]:
        axes = list(map(int, recipe["idle_children"][child]["orthogonal_axes"][offset:offset + width]))
        require(len(axes) == width, "projected hosted width")
        stream = stream_for(data, child)
        hosts[time].append((stream, axes))
        host_receipt.append({"time": time, "helper": helper, "caller_replica": caller,
                             "child": child, "stream": stream, "offset": offset,
                             "width": width, "axes": axes})
    residual = {}
    for child, entry in enumerate(recipe["idle_children"]):
        axes = list(map(int, entry["orthogonal_axes"]))
        require(len(axes) == entry["rank"], "actual geometry rank")
        residual[child] = axes[loads[owner, port, child]:]
    return {"recipe": recipe, "template": data["template"], "hosts": hosts,
            "residual": residual, "owner": owner, "port": port,
            "host_receipt": host_receipt}


def replay(data, fixture, blocks, character, residual):
    require(type(character) is int and 0 <= character < (1 << 73), "73-axis Fourier character")
    algebra = data["algebra"]
    matrix = algebra.identity()
    for time, (stage, caller) in enumerate(data["order"]):
        # All selected-owner hosted phases are retained, including foreign callers.
        for stream, axes in fixture["hosts"].get(time, ()):
            algebra.phase(matrix, stream, sum(algebra.dot(character, axis) for axis in axes))
        if caller == fixture["owner"]:
            for event in blocks[stage]:
                algebra.data_event(matrix, event, fixture, residual, character)
    return matrix


def primitive_events(data, fixture, blocks):
    """Inspectable shared extraction; the root oracle supplies separate arithmetic.

    phase.terms denotes sum(coefficient * dot(character, axis)); signed_swap
    maps (left,right) to (right,-left).  This expansion is not itself a
    second implementation of the source binding.
    """
    result = []
    recipe = fixture["recipe"]

    def emit(kind, provenance, **values):
        result.append({"kind": kind, "provenance": provenance, **values})

    for time, (stage, caller) in enumerate(data["order"]):
        for host_index, (stream, axes) in enumerate(fixture["hosts"].get(time, ())):
            provenance = {"time": time, "caller_replica": caller, "owner": fixture["owner"],
                          "port": fixture["port"], "source_kind": "hosted_helper_return",
                          "host_index_at_time": host_index}
            emit("phase", provenance, stream=stream, terms=[[1, axis] for axis in axes])
        if caller != fixture["owner"]:
            continue
        for event_index, event in enumerate(blocks[stage]):
            kind = event["kind"]
            provenance = {"time": time, "stage": stage, "caller_replica": caller,
                          "owner": fixture["owner"], "port": fixture["port"],
                          "source_kind": kind, "event_index_in_stage": event_index}
            if kind == "local_cover_sweep":
                local = next(row for row in data["template"]["recipe"]
                             if row["kind"] == "local" and row["stage"] == stage)
                x, y = 2 * local["pair"], 2 * local["pair"] + 1
                for side, stream in enumerate((x, y)):
                    terms = ([[-(1 - side), recipe["q"]]] if stage == 0 else
                             [[-1, 1 << index] for index in range(9 + 8 * (stage - 1))]
                             + [[side, recipe["q"]]])
                    emit("phase", provenance, stream=stream,
                         terms=[term for term in terms if term[0] != 0])
                if local["reverse"]:
                    emit("shear", provenance, dst=x, src=y, coefficient=-1)
                else:
                    emit("shear", provenance, dst=y, src=x, coefficient=1)
                for side, stream in enumerate((x, y)):
                    terms = [[1, 1 << index] for index in range(9 + 8 * stage)]
                    if side:
                        terms.append([-1, recipe["q"]])
                    emit("phase", provenance, stream=stream, terms=terms)
            elif kind == "idle_cover_sweep":
                for side, child in enumerate(event["child_indices"]):
                    terms = [[1, axis] for axis in fixture["residual"][child]]
                    translation = recipe["idle_children"][child]["translation_after"]
                    if translation:
                        terms.append([2, translation])
                    emit("phase", {**provenance, "child": child},
                         stream=2 * event["pair"] + side, terms=terms)
            elif kind == "bridge":
                emit("shear", provenance, dst=2 * event["dst"], src=2 * event["src"],
                     coefficient=event["coefficient"])
                emit("shear", provenance, dst=2 * event["src"] + 1, src=2 * event["dst"] + 1,
                     coefficient=-event["coefficient"])
            elif kind == "terminal_Y_translations":
                for pair in event["pairs"]:
                    emit("phase", provenance, stream=2 * pair + 1, terms=[[2, recipe["q"]]])
            elif kind == "terminal":
                for pair in range(event["pairs"]):
                    emit("signed_swap", provenance, left=2 * pair, right=2 * pair + 1)
            else:
                raise ValueError("unknown primitive expansion event")
    return result


def input_corrected(data, baseline, stream, exponent):
    corrected = [list(row) for row in baseline]
    for row in corrected:
        row[stream] = data["algebra"].rotate(row[stream], exponent)
    return corrected


def scalar_fourier(data, character):
    phase = data["algebra"].rotate((1, 0), character.bit_count())
    return [[phase if row == col else (0, 0) for col in range(8)] for row in range(8)]


def characters(fixture, removed):
    return sorted({0, (1 << 73) - 1, fixture["recipe"]["q"], *removed,
                   *(1 << index for index in range(73))})


def columns(matrix):
    return [[list(matrix[row][col]) for row in range(8)] for col in range(8)]


def evaluate_fixture(data, loads, grouped, blocks, item, require_head):
    fixture = fixture_context(data, loads, grouped, item)
    child, stream = item["child"], item["stream"]
    original = fixture["residual"]
    require(len(original[child]) == 48, "chosen full rank48 block")
    removed = original[child][:24]
    changed = dict(original)
    changed[child] = original[child][24:]
    receipt = {**item, "removed_axes": removed, "retained_axes": changed[child],
               "all_hosted_occurrences": fixture["host_receipt"],
               "hosted_occurrences": len(fixture["host_receipt"]),
               "foreign_caller_occurrences": sum(row["caller_replica"] != item["owner"]
                                                 for row in fixture["host_receipt"]),
               "primitive_events": primitive_events(data, fixture, blocks),
               "primitive_extraction_status": "shared source extraction; separate oracle arithmetic required",
               "checks": []}
    baselines = {}
    # Baseline must pass before any altered word is executed.
    for character in characters(fixture, removed):
        baseline = replay(data, fixture, blocks, character, original)
        expected = scalar_fourier(data, character)
        require(baseline == expected, "unaltered base2979 identity-cover baseline failed")
        baselines[character] = baseline
    for character, baseline in baselines.items():
        exponent = -sum(data["algebra"].dot(character, axis) for axis in removed)
        expected = input_corrected(data, baseline, stream, exponent)
        actual = replay(data, fixture, blocks, character, changed)
        passed = actual == expected
        row = {"character": character, "omitted_phase_mod4": exponent % 4,
               "matches_input_correction": passed, "actual_columns": columns(actual),
               "expected_columns": columns(expected)}
        receipt["checks"].append(row)
        if not passed:
            receipt["witness_character"] = character
            receipt["outcome"] = "cut_counterexample" if require_head else "wrong_nonhead_cut_rejected"
            return receipt
    receipt["outcome"] = "head_cut_passed" if require_head else "nonhead_control_not_discriminating"
    return receipt


def run():
    data = loader()
    loads, grouped = allocations(data)
    classes, blocks = classify(data, loads, grouped)
    heads = [item for item in classes if item["is_first_touch_head"] and item["child"] in (8, 10)]
    chosen = []
    for child in (8, 10):
        for replica_class in (0, 1):
            matches = [item for item in heads if item["child"] == child
                       and item["replica_class"] == replica_class]
            require(matches, "missing child/replica-class head fixture")
            chosen.append(min(matches, key=lambda item: (item["owner"], item["port"])))
    base_receipt = {"schema_version": 1, "cover": "identity only", "matrix_domain": "8x8 Gaussian integers",
                    "source_main": "12fa8c5c844be21bfefb38a19503fbd867a11244",
                    "original_rows": 271728, "original_calls": 666, "original_replicas": 74,
                    "source_pins": data["pins"],
                    "replica_classes": [[0, 36], [37, 73]],
                    "template_plan_T_metadata": data["plan"]["T"],
                    "zero_padding_families_replayed": False,
                    "full_rank48_block_count": len(classes),
                    "classification_summary": [
                        {"child": child, "replica_class": replica_class,
                         "is_first_touch_head": is_head, "count": count}
                        for (child, replica_class, is_head), count in sorted(Counter(
                            (item["child"], item["replica_class"], item["is_first_touch_head"])
                            for item in classes).items())],
                    "classification_sha256": canonical_hash(classes),
                    "head_counts": dict(sorted(Counter(item["child"] for item in heads).items())),
                    "fixtures": [], "negative_control": None,
                    "scope": "No all-cover/native/compiler/supplier/outer/precision/physical-cost admission."}
    for item in chosen:
        result = evaluate_fixture(data, loads, grouped, blocks, item, True)
        base_receipt["fixtures"].append(result)
        if result["outcome"] == "cut_counterexample":
            base_receipt["outcome"] = "authenticated_head_cut_counterexample"
            return base_receipt
    nonheads = [item for item in classes if not item["is_first_touch_head"] and item["child"] in (12, 13)]
    require(nonheads, "missing nonhead control domain")
    for item in nonheads[:8]:
        result = evaluate_fixture(data, loads, grouped, blocks, item, False)
        if result["outcome"] == "wrong_nonhead_cut_rejected":
            base_receipt["negative_control"] = result
            break
    require(base_receipt["negative_control"] is not None, "nonhead cuts did not discriminate")
    base_receipt["outcome"] = "four_source_bound_head_fixtures_passed_with_nonhead_rejection"
    base_receipt["checked_head_characters"] = sum(len(item["checks"]) for item in base_receipt["fixtures"])
    base_receipt["all_arbitrary_input_columns_per_character"] = 8
    return base_receipt


if __name__ == "__main__":
    require(len(sys.argv) == 1, "engine CLI takes no arguments")
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
