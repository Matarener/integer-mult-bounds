# SPDX-License-Identifier: Apache-2.0
"""Complete selected instruction and child inventory with boundary controls."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cover import act, is_orthogonal, multiply, transpose
from native_program import check
from scalar_program import compile_catalogue
from selected_binding import SelectedBinding, require
from selected_source import load


def run():
    data = load()
    binding = SelectedBinding(data)
    catalogue, _ = compile_catalogue(data["programs"])
    local = check(data)
    histogram = Counter()
    for call in binding.calls.values():
        for op in binding.codes[call["orientation"]]:
            if op[0] == "child":
                histogram[op[3]] += 1
    histogram.update(row["rank"] for row in binding.template["idle_children"])
    expected = {1: 349604, 2: 60192, 3: 62585, 4: 20448, 5: 11808, 7: 7, 8: 1152, 48: 4866}
    require(dict(histogram) == expected and max(histogram) == binding.maximum_rank, "complete selected child histogram")
    require(binding.inventory()["subgroups_per_cover"] == 70032 and len(binding.events) == 482,
            "complete selected global schedule")
    identity = tuple(1 << i for i in range(73))
    identity_index = binding.cover.rank(identity)
    # One full owner group checks all 704 physical selectors and both directions.
    groups = []
    for direction in ("forward", "backward"):
        index = next(i for i, event in enumerate(binding.events) if event["kind"] == "local_cover_sweep"
                     and binding.calls[event["time"]]["orientation"] == direction)
        group = binding.group(index, 0, identity_index)
        call = binding.calls[binding.events[index]["time"]]
        owners = binding.owner_specs[call["time"]]
        require(len(group.keys) == 704, "all local owner keys")
        for key, owner in zip(group.keys, owners):
            require(key[0] == owner.family and binding.cover.unrank(key[1]) == owner.sigma_columns,
                    "physical owner g=d sigma inverse")
        groups.append((index, len(group.code), sha256(json.dumps(group.code).encode()).hexdigest()))
    stage2 = next(owners for time, owners in binding.owner_specs.items() if binding.calls[time]["stage"] == 2)
    require((stage2[0].entry, stage2[0].exit) == (917515, 917508), "data Pauli pullback boundary")
    # Cover defect uses output-coordinate row weights. A second multiplication
    # by g would apply a different translation for this fixed orthogonal g.
    vectors = (15, 30)
    factors = [tuple((1 << i) ^ (vector if vector >> i & 1 else 0) for i in range(73)) for vector in vectors]
    transvection = multiply(*factors)
    require(is_orthogonal(transvection), "nontrivial orthogonal control")
    label = binding.cover.rank(transvection)
    correction = binding.group(481, 0, label)
    mask = sum((((row.bit_count() - 1) // 2) & 1) << i for i, row in enumerate(transvection))
    require(act(transvection, mask) != mask, "extra chart multiplication changes the correction control")
    require(len(correction.code) == 1 and correction.recipes[correction.code[0][3]]["offset"] == mask,
            "final output-coordinate correction")
    # Retain translations even after hosting consumed the positive rank.
    zero_rank_translations = positive = 0
    for index, event in enumerate(binding.events):
        if event["kind"] != "idle_cover_sweep":
            continue
        for subgroup in range(224):
            side, port = divmod(subgroup, 112)
            child = event["child_indices"][side]
            original = data["phases"]["recipes"][port]["idle_children"][child]
            remainder = binding.remainders.get((event["replica"], child, port))
            if remainder:
                positive += 1
            elif original["translation_after"]:
                zero_rank_translations += 1
    require((positive, zero_rank_translations) == (7526, 6822), "idle positive and translation-only coverage")
    literal_passes = {}
    for direction, code in binding.codes.items():
        literal_passes[direction] = sum(len(catalogue[op[4]].program) for op in code if op[0] == "scalar")
    require(literal_passes == {"forward": 80397, "backward": 80421}, "complete expanded scalar bill")
    result = dict(selected=binding.inventory(), local=local, child_histogram=dict(sorted(histogram.items())),
                  literal_passes=literal_passes, complete_owner_groups=groups,
                  positive_idles=positive, translation_only_idles=zero_rank_translations,
                  scope="Selected source compilation and control binding; no complete O73 numerical payload.")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
