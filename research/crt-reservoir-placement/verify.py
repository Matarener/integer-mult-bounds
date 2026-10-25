#!/usr/bin/env python3
"""Bounded placement audit; explicit checks remain active under Python -O.

Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance.
Apache-2.0. See PROOF.md for predecessor credit and the quantified argument.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_bytes(name, data, path):
    """Execute the bytes just read, never a possibly stale bytecode cache."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    checked = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"],
             "source SHA256 mismatch: " + row["path"])
        header = f"blob {len(data)}\0".encode()
        need(hashlib.sha1(header + data).hexdigest() == row["git_blob"],
             "source Git blob mismatch: " + row["path"])
        checked[row["path"]] = data
    return manifest, checked


def overlap(a, b):
    return a[0] < b[1] and b[0] < a[1]


def reference_position(position, swaps):
    for source, destination in swaps:
        if source[0] <= position < source[1]:
            return destination[0] + position - source[0]
        if destination[0] <= position < destination[1]:
            return source[0] + position - destination[0]
    return position


def physical_axes(widths):
    """Independent reverse traversal, not Layout's logical prefix index."""
    axes = [None] * len(widths)
    cursor = 0
    for axis in range(len(widths) - 1, -1, -1):
        axes[axis] = (cursor, cursor + widths[axis])
        cursor += widths[axis]
    return axes


def check_plan(plan, axes, boundaries):
    layout = plan.layout
    length, h, d = layout.L, layout.H, layout.d
    need(1 <= len(plan.active_axes) <= layout.r_max, "batch capacity")
    need(len(plan.dependencies) == len(plan.active_axes), "dependency count")
    if plan.level == layout.levels:
        expected_reservoir = ((3 * d // 4, d) if plan.partition == 0
                              else (d // 2, 3 * d // 4))
    else:
        expected_reservoir = ((d // 2, d) if plan.partition == 0 else (0, d // 2))
    need(plan.reservoir_axes == expected_reservoir, "root/nonroot reservoir")
    lo, hi = expected_reservoir
    reservoir = (axes[hi - 1][0], axes[lo][1])
    need(plan.reservoir_interval == reservoir, "physical reservoir orientation")
    need(8 * (reservoir[1] - reservoir[0]) >= length, "mixed-width L/8 budget")
    destinations = ((0, h), (h, 2 * h), (length - h, length))
    need(plan.destination_blocks == destinations, "three literal destinations")
    blocks = plan.source_blocks + destinations
    need(all(not overlap(a, b) for i, a in enumerate(blocks) for b in blocks[i + 1:]),
         "six disjoint fields")
    for block in plan.source_blocks:
        need(reservoir[0] <= block[0] < block[1] <= reservoir[1]
             and block[1] - block[0] == h, "source contained in reservoir")
    width = 1 << plan.level
    for axis, dependency in zip(plan.active_axes, plan.dependencies):
        node = axis // width * width
        left_axes = (node, node + width // 2)
        left = (axes[left_axes[1] - 1][0], axes[left_axes[0]][1])
        need(axis >= left_axes[1], "right-child axis")
        need(dependency.axis == axis and dependency.left_axes == left_axes
             and dependency.own_interval == axes[axis]
             and dependency.left_interval == left, "dense source dependencies")
        need(not overlap(reservoir, axes[axis]) and not overlap(reservoir, left),
             "reservoir omits entire source dependencies")
        for v in (axes[axis][0], axes[axis][1] - 1):
            image = reference_position(v, plan.swaps)
            need(plan.map_position(v) == image and 2 * h <= image < length - h,
                 "target in the new middle field")
            j = length - h - 1 - image
            need(0 <= j < length - 3 * h, "local arithmetic target index")
    pieces = plan.map_interval(0, length)
    original = 0
    for piece in pieces:
        a, b = piece.original_interval
        c, e = piece.image_interval
        need(a == original and b - a == e - c, "ordered translation fragments")
        for v in (a, b - 1):
            mapped = reference_position(v, plan.swaps)
            need(mapped == v + c - a and plan.map_position(mapped) == v,
                 "complete coordinate involution")
        original = b
    need(original == length, "complete original coordinate cover")
    cursor = 0
    for lo, hi in sorted(piece.image_interval for piece in pieces):
        need(lo == cursor, "image cover without collision")
        cursor = hi
    need(cursor == length, "complete image coordinate cover")
    cuts = {v for block in blocks for v in block}
    fragments = d + len(cuts - boundaries)
    need(plan.descriptor_fragment_count == fragments <= d + 12,
         "split-axis descriptor budget")
    return fragments - d


def production_census(allocator):
    d, ell = 65536, 24
    widths = tuple(ell - (i % 2) for i in range(d))
    length = sum(widths)
    layout = allocator.Layout(6 * length, ell, widths)
    axes = physical_axes(widths)
    boundaries = {point for interval in axes for point in interval}
    need(layout.L == length and layout.G == 3072 and layout.r_max == 5
         and layout.H == 15360, "unchanged production constants")
    digest = hashlib.sha256()
    counts = []
    total_axes = max_extra = 0
    for level in range(1, layout.levels + 1):
        seen = bytearray(d)
        batches = 0
        for plan in allocator.iter_plans(layout, level):
            max_extra = max(max_extra, check_plan(plan, axes, boundaries))
            for axis in plan.active_axes:
                need(not seen[axis], "axis scheduled once per level")
                seen[axis] = 1
                total_axes += 1
            digest.update(json.dumps(
                [level, plan.partition, plan.batch_index, plan.active_axes,
                 plan.reservoir_axes, plan.source_blocks],
                separators=(",", ":")).encode() + b"\n")
            batches += 1
        half_node = 1 << (level - 1)
        need(all(bool(seen[i]) == bool((i // half_node) % 2) for i in range(d)),
             "exact complete right-child schedule")
        need(batches <= 25600, "quantified per-layer batch bound")
        counts.append(batches)
    return {
        "domain": "descriptor census, not a payload execution or time certificate",
        "d": d, "ell": ell, "p": layout.p, "L": length,
        "width_pattern": "24,23 repeated", "G": layout.G,
        "r_max": layout.r_max, "H": layout.H,
        "tree_levels": layout.levels, "batches_per_level": counts,
        "total_batches": sum(counts), "active_axis_visits": total_axes,
        "max_extra_descriptor_fragments": max_extra,
        "schedule_sha256": digest.hexdigest(),
    }


def permute_word(value, placement):
    """Independent bit-mask exchange of an address's literal fields."""
    result = value
    for source, destination in placement.swaps:
        width = source[1] - source[0]
        mask = (1 << width) - 1
        a = placement.length - source[1]
        b = placement.length - destination[1]
        different = ((result >> a) ^ (result >> b)) & mask
        result ^= (different << a) | (different << b)
    return result


def read_descriptor(word, fragments, length):
    result = 0
    for fragment in fragments:
        lo, hi = fragment.image_interval
        size = hi - lo
        result = (result << size) | ((word >> (length - hi)) & ((1 << size) - 1))
    return result


def must_reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)


def tiny_caller(allocator, crt):
    """Actual root-axis CRT controls on every dirty address of a small grid."""
    placement = allocator.Placement(12, 1, ((4, 5), (5, 6), (6, 7)))
    widths, moduli = (2, 3, 3, 4), (3, 5, 7, 11)
    axes = physical_axes(widths)
    descriptors = [placement.map_interval(*interval) for interval in axes]
    shifts = (0, 2, 5, 8)
    masks = (3, 7, 7, 15)
    networks = {offset: crt.benes(crt.rotation(16, 11, offset)) for offset in range(11)}
    need(all(len(layers) == 7 for layers in networks.values()), "actual Beneš depth")
    schedule = [bit for bit, table in networks[0]]
    for layers in networks.values():
        need([bit for bit, table in layers] == schedule, "common control schedule")
        for bit, table in layers:
            need(all(table[x] == table[x ^ (1 << bit)] for x in range(16)),
                 "source omits active target")
    # k_A is the locally scaled CRT inverse of the complete left child.
    # For this root target, (S_A * P_B,i)^-1 = (15*7)^-1 mod 11 = 2.
    offset_factor = pow(3 * 5 * 7, -1, 11)
    need(offset_factor == 2, "actual root caller offset")

    def original_coordinates(word):
        return [(word >> shift) & mask for shift, mask in zip(shifts, masks)]

    def moved_coordinates(word):
        return [read_descriptor(word, parts, 12) for parts in descriptors]

    def offset(values):
        if values[0] >= 3 or values[1] >= 5:
            return 0
        return crt.decode_group(values[:2], moduli[:2]) * offset_factor % 11

    def control(word, layer, stale=False):
        values = original_coordinates(word) if stale else moved_coordinates(word)
        return networks[offset(values)][layer][1][values[3]]

    def ideal_step(word, layer):
        values = original_coordinates(word)
        bit, table = networks[offset(values)][layer]
        return word ^ (table[values[3]] << (8 + bit))

    def placed_step(word, layer):
        # Ideal all-address endpoint of a completed repaired macro; this
        # deliberately does not reimplement or test the raw compact word.
        placed = permute_word(word, placement)
        original_v = 3 - schedule[layer]
        current_v = placement.map_position(original_v)
        local_j = 12 - placement.H - 1 - current_v
        placed ^= control(placed, layer) << (local_j + placement.H)
        return permute_word(placed, placement)

    omission_checks = forward_steps = inverse_steps = 0
    stale_witness = wrong_index_witness = contiguous_witness = None
    permutation = []
    for word in range(4096):
        placed = permute_word(word, placement)
        need(permute_word(placed, placement) == word, "dirty placement inverse")
        need(moved_coordinates(placed) == original_coordinates(word),
             "all original axes reconstructed from split descriptors")
        for v in range(12):
            need(((word >> (11 - v)) & 1)
                 == ((placed >> (11 - placement.map_position(v))) & 1),
                 "implementation agrees with independent word permutation")
        for layer in range(7):
            f = control(placed, layer)
            for destination in placement.destination_blocks:
                toggled = placed ^ (1 << (11 - destination[0]))
                need(control(toggled, layer) == f, "transported control omits dirty fields")
                omission_checks += 1
                if stale_witness is None and control(toggled, layer, True) != control(placed, layer, True):
                    stale_witness = {"placed_address": placed, "layer": layer,
                                     "toggled_physical_position": destination[0]}
            need(placed_step(word, layer) == ideal_step(word, layer),
                 "all-address single-layer conjugation")
            # Wrongly using the GLOBAL arithmetic bit as a Y-local bit adds H.
            current_v = placement.map_position(3 - schedule[layer])
            wrong = placed ^ (f << ((11 - current_v) + placement.H))
            if wrong_index_witness is None and permute_word(wrong, placement) != ideal_step(word, layer):
                wrong_index_witness = {"address": word, "layer": layer}
        values = original_coordinates(word)
        # Axis 3 becomes split; one slice from its first moved position loses
        # its original significance even when that slice remains in range.
        start = placement.map_position(0)
        contiguous = (placed >> (12 - start - 4)) & 15
        if contiguous_witness is None and contiguous != values[3]:
            contiguous_witness = {"address": word, "axis": 3}
        state = word
        for layer in range(7):
            state = placed_step(state, layer)
            forward_steps += 1
        expected_target = ((values[3] + offset(values)) % 11
                           if values[3] < 11 else values[3])
        expected = (word & 255) | (expected_target << 8)
        need(state == expected, "complete padded root-axis modular rotation")
        permutation.append(state)
        for layer in reversed(range(7)):
            state = placed_step(state, layer)
            inverse_steps += 1
        need(state == word, "complete dirty inverse")
    need(len(set(permutation)) == 4096, "all distinct labeled address payloads")
    wrong_root = (axes[1][0], axes[0][1])
    need(not overlap(wrong_root, axes[3]) and overlap(wrong_root, (7, 12)),
         "root opposite-half dependency counterexample")
    need(stale_witness is not None and wrong_index_witness is not None
         and contiguous_witness is not None, "all semantic mutants detected")
    dirty = 1 << (11 - placement.source_blocks[2][0])
    placed = permute_word(dirty, placement)
    # Restore only the first two swaps; the third dirty bit remains at B.
    partial = placed
    for source, destination in placement.swaps[:2]:
        a, b = 11 - source[0], 11 - destination[0]
        different = ((partial >> a) ^ (partial >> b)) & 1
        partial ^= (different << a) | (different << b)
    need(partial != dirty, "omitted inverse exchange detected")
    controls = [
        {"name": "root reservoir intersects full left-child dependency",
         "reservoir": wrong_root, "target": axes[3]},
        {"name": must_reject(lambda: allocator.Placement(
            12, 1, ((0, 1), (5, 6), (6, 7))), "overlapping source/destination rejected")},
        {"name": "stale coordinate descriptors", "witness": stale_witness},
        {"name": "global bit used as middle-field bit", "witness": wrong_index_witness},
        {"name": "split axis read as one contiguous slice", "witness": contiguous_witness},
        {"name": "third inverse exchange omitted", "input": dirty, "output": partial},
    ]
    return {
        "domain": "small geometry and caller fixture, below the large-family cutoff",
        "moduli": moduli, "widths": widths, "L": 12, "H": 1,
        "root_target_axis": 3, "reservoir_axis": 2, "layers": 7,
        "all_dirty_addresses": 4096, "single_layer_conjugations": 4096 * 7,
        "borrowed_field_omission_checks": omission_checks,
        "forward_steps": forward_steps, "inverse_steps": inverse_steps,
        "payload_permutation_sha256": hashlib.sha256(
            b"".join(value.to_bytes(2, "big") for value in permutation)).hexdigest(),
        "semantic_failure_controls": controls,
    }


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    manifest, checked = sources()
    allocator_path = PACKAGE / "allocator.py"
    allocator = load_bytes("_crt_placement_allocator", allocator_path.read_bytes(), allocator_path)
    caller_path = "research/unconditional-batched-crt/check_batched_crt.py"
    crt = load_bytes("_pinned_crt_caller", checked[caller_path], ROOT / caller_path)
    receipt = {
        "schema_version": 1,
        "result": "PASS_CRT_RESERVOIR_PLACEMENT",
        "base_commit": manifest["base_commit"],
        "source_inputs_checked": len(checked),
        "production": production_census(allocator),
        "finite_caller": tiny_caller(allocator, crt),
        "input_rejections": [
            must_reject(lambda: allocator.Layout(24, 5, (5,) * 4),
                        "small geometry cannot pass as actual-family Layout"),
            must_reject(lambda: allocator.Layout(1, 2, (1,) * 65535),
                        "non-power-of-two axis count"),
            must_reject(lambda: allocator.Layout(1, 2, (3,) * 65536),
                        "width outside ell-1 or ell"),
            must_reject(lambda: allocator.Layout(64, 2, (2,) * 65536),
                        "ell below ceil(log2(p+2))"),
        ],
        "limitations": [
            "Quantified claim is the written proof; finite census is corroboration.",
            "All-address restoration assumes a completed repaired switch macro.",
            "No ordinary exchange implementation, control evaluator or tape-cost certificate.",
            "No last-K tail, full CRT construction, multiplication theorem or new kappa.",
        ],
    }
    result_path = PACKAGE / "RESULT.json"
    if args.write_result:
        result_path.write_text(json.dumps(receipt, indent=2) + "\n")
    else:
        need(json.loads(result_path.read_text()) == json.loads(json.dumps(receipt)),
             "stored RESULT.json differs from reproduced receipt")
    print(json.dumps({"result": receipt["result"],
                      "production_batches": receipt["production"]["total_batches"],
                      "dirty_addresses": receipt["finite_caller"]["all_dirty_addresses"],
                      "semantic_controls": len(receipt["finite_caller"]["semantic_failure_controls"])},
                     sort_keys=True))


if __name__ == "__main__":
    run()
