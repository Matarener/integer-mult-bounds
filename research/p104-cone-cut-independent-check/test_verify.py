#!/usr/bin/env python3
"""Behavioural controls for the independent P104 cone-cut checker.

Each control must really reject. No check depends on `assert`, so the module
runs unchanged under `-O`.
"""

import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import verify  # noqa: E402  (the package module under test)


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL_P104_CONE_CUT_INDEPENDENT_CONTROL {message}")


def run_receipt():
    return verify.evaluate()


def control_own_receipt():
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    observed = run_receipt()
    require(observed == stored, "the stored receipt does not match a fresh run")
    require(observed["intersection"] == 0, "the one-step intersection moved")
    require(observed["backward_edges"] == 37, "the one-step cone moved")


def control_trivial_relation():
    """Dropping the rank interval must change the adjacency, not preserve it."""
    word = json.loads(verify.WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(verify.CERTIFICATE.read_text(encoding="utf-8"))
    frames, lines, departures, arrivals, edges = verify.geometry(word, certificate)
    bounds = [(departures[departure], arrivals[arrival]) for departure, arrival in edges]
    pinned, _ = verify.relation(bounds, 1)
    loose = [1 << index for index in range(len(bounds))]
    for index in range(len(bounds)):
        low, _ = bounds[index]
        for other in range(index):
            if low <= bounds[other][1] and bounds[other][0] <= low:
                loose[index] |= 1 << other
                loose[other] |= 1 << index
    require(loose != pinned, "the rank interval is not doing any work")


def control_wrong_target():
    """A different writer label must give a different backward seed set."""
    word = json.loads(verify.WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(verify.CERTIFICATE.read_text(encoding="utf-8"))
    frames, lines, departures, arrivals, edges = verify.geometry(word, certificate)
    true_target = verify.TARGET
    try:
        verify.TARGET = 70
        writers, _, counts, _ = verify.backward_cone(
            edges, departures, arrivals, frames, settle_each=False
        )
    finally:
        verify.TARGET = true_target
    require(len(writers) != 12, "the writer count does not depend on the target")
    require(counts != [12, 22, 37], "the backward growth does not depend on the target")


def control_wrong_source():
    """A different marker label must give a different forward cone."""
    word = json.loads(verify.WITNESS.read_text(encoding="utf-8"))
    certificate = json.loads(verify.CERTIFICATE.read_text(encoding="utf-8"))
    frames, lines, departures, arrivals, edges = verify.geometry(word, certificate)
    true_source = verify.SOURCE
    try:
        verify.SOURCE = 0
        _, counts, _, _, _ = verify.forward_cone(
            edges, lines, departures, arrivals, frames, settle_each=False
        )
    finally:
        verify.SOURCE = true_source
    require(counts[1:] != verify.EXPECTED_MARKER_COUNTS, "the marker counts do not depend on the source")


def main():
    control_own_receipt()
    control_trivial_relation()
    control_wrong_target()
    control_wrong_source()
    print("PASS_P104_CONE_CUT_INDEPENDENT_CONTROLS")


if __name__ == "__main__":
    main()
