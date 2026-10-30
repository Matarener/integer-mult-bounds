# SPDX-License-Identifier: Apache-2.0
"""Semantic faults outside the old private-free/native coverage."""

from copy import deepcopy

import boundary


def rejected(action, text):
    try:
        action()
    except ValueError as error:
        boundary.require(text in str(error), "wrong semantic rejection: " + str(error))
        return str(error)
    raise ValueError("semantic fault accepted: " + text)


def phase(native, kernel, canonical, recipes, adapters, backward, delta):
    key = next(tuple(k) for k in delta["new_classes"] if k[0] == "child")
    changed = dict(recipes)
    changed["children"] = list(recipes["children"])
    index = next(
        i
        for i, row in enumerate(recipes["children"])
        if (row["old"], row["new"]) == key[1:]
    )
    row = deepcopy(recipes["children"][index])
    row["left"]["phase"] = (row["left"]["phase"] + 1) % 4
    changed["children"][index] = row
    reason = rejected(
        lambda: native.check(kernel, key, canonical, changed, adapters, backward),
        "exact native class mismatch",
    )
    return {"class_outside_prior_native_cones": list(key), "rejection": reason}


def helper(events, original, helpers, backward, algebra, previous, orientation):
    ranges = previous["orientations"][orientation]["expanded"]["event_ranges_half_open"]
    covered = {i for lo, hi in ranges for i in range(lo, hi)}
    candidates = [
        i
        for i, e in enumerate(events)
        if i not in covered
        and e[0] == "scalar"
        and e[1][0] == "add"
        and e[1][1] in helpers
        and e[1][1] != "L249"
        and e[1][2].startswith("L")
    ]
    boundary.require(candidates, "uncovered actual helper ADD exists")
    # A single actual last uncovered helper write has no path to the old roots.
    index = candidates[-1]
    changed = list(events)
    changed[index] = deepcopy(events[index])
    changed[index][1][3] *= -1
    old = algebra.values(changed, original, backward)
    boundary.require(
        old["helper249"] == [["L249", [], "1"]], "old helper root still passes"
    )
    boundary.require(
        all(not r["value"] for r in old["frees"]), "all old private roots still pass"
    )
    reason = rejected(
        lambda: boundary.normalized(changed, original, helpers, backward, algebra),
        "all dirty helper outputs restored",
    )
    return {
        "event_outside_prior_expanded_cone": index,
        "original_event": events[index],
        "mutant_event": changed[index],
        "old_helper_and_91_frees_pass": True,
        "rejection": reason,
    }


def run(modules, data, events, metadata, helpers, previous, orientation, delta):
    backward = orientation == "backward"
    return {
        "helper": helper(
            events,
            metadata["start"],
            helpers,
            backward,
            modules["algebra"],
            previous,
            orientation,
        ),
        "phase": phase(
            modules["native"],
            modules["kernel"],
            data["canonical_word"],
            data["recipes"],
            data["adapters"],
            backward,
            delta,
        ),
    }
