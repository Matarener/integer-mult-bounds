# SPDX-License-Identifier: Apache-2.0
"""Reject corrupted scientific certificates; produced by Nick Petalas."""

from copy import deepcopy
import json
from pathlib import Path

from census import PROFILES, conjugate, dense_conjugate, layout, orbit, rank, require
from independent import full_group, transform, verify_certificate


def expect_rejection(certificate, label):
    try:
        verify_certificate(certificate)
    except (ValueError, KeyError, TypeError):
        return
    raise ValueError("accepted corrupted certificate: " + label)


def controls():
    saved = json.loads((Path(__file__).parent / "RESULT.json").read_text())
    mutations = []
    changed = deepcopy(saved)
    changed["profiles"][0]["rank_histogram"][4] -= 1
    changed["profiles"][0]["rank_histogram"][5] += 1
    mutations.append((changed, "rank histogram with unchanged total"))
    changed = deepcopy(saved)
    changed["profiles"][1]["orbits"].pop()
    mutations.append((changed, "missing orbit"))
    changed = deepcopy(saved)
    changed["profiles"][2]["orbits"].append(changed["profiles"][2]["orbits"][0])
    mutations.append((changed, "duplicate orbit"))
    changed = deepcopy(saved)
    changed["profiles"][0]["orbits"][0]["representative_rows"][0] = 0
    mutations.append((changed, "invalid representative"))
    changed = deepcopy(saved)
    changed["profiles"][1]["orbits"][0]["orbit_size"] += 1
    mutations.append((changed, "wrong orbit size"))
    changed = deepcopy(saved)
    changed["profiles"][0]["orbits"][0]["edge_private_form"] = None
    mutations.append((changed, "incorrect channel classification"))
    changed = deepcopy(saved)
    changed["profiles"][2]["local_group_order"] += 1
    mutations.append((changed, "wrong full local group"))
    changed = deepcopy(saved)
    changed["profiles"].pop()
    mutations.append((changed, "omitted width profile"))
    for changed, label in mutations:
        expect_rejection(changed, label)
    return len(mutations)


def action_controls():
    saved = json.loads((Path(__file__).parent / "RESULT.json").read_text())
    checked = 0
    require(rank(0) == 0 and rank((1 << 49) - 1) == 1, "rank boundary controls")
    for widths, record in zip(PROFILES, saved["profiles"]):
        _, _, generators, identity = layout(widths)
        require(rank(identity) == 7, "identity rank")
        group = full_group(widths)
        for item in record["orbits"]:
            word = sum(row << (7 * i) for i, row in enumerate(item["representative_rows"]))
            generated = orbit(word, generators, len(group))
            require(generated == {transform(word, element) for element in group},
                    "generators do not cover complete group orbit")
            for member in generated:
                for a, b in generators:
                    result = conjugate(member, a, b)
                    require(result == dense_conjugate(member, a, b), "dense action mismatch")
                    require(conjugate(result, a, b) == member, "transvection not involutive")
                    checked += 1
    return checked


if __name__ == "__main__":
    print("PASS_BINARY_C5_CONTROLS", {"rejected_certificates": controls(),
                                      "dense_action_checks": action_controls()})
