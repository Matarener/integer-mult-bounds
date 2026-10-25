# SPDX-License-Identifier: Apache-2.0
"""Check the complete PR2979 source/native boundary without accepting its invoice."""

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boundary
import controls
import io_support as io


def case(
    modules, data, previous, old_pair, helper_names, orientation, checked, progress
):
    backward = orientation == "backward"
    events, metadata = modules["source"].bind(
        data["word"], data["canonical_word"], data["programs"][orientation], backward
    )
    normalized = boundary.normalized(
        events, metadata["start"], helper_names, backward, modules["algebra"]
    )
    profile = boundary.paid_profile(events)
    io.require(
        profile == {1: 2445, 2: 706, 3: 232, 4: 108, 5: 18, 8: 8},
        "unchanged complete local paid profile",
    )
    delta = boundary.prior_delta(
        modules["native"],
        events,
        data["canonical_word"],
        previous,
        old_pair,
        orientation,
    )
    faults = controls.run(
        modules, data, events, metadata, helper_names, previous, orientation, delta
    )
    native = modules["audit"].native_case(
        modules["native"],
        modules["kernel"],
        events,
        [i for i, e in enumerate(events) if e[0] != "phase"],
        data["canonical_word"],
        data["recipes"],
        data["adapters"],
        backward,
        checked,
        progress,
    )
    return {
        "source_bound_events": len(events),
        "normalized": normalized,
        "prior_delta": delta,
        "paid_profile": profile,
        "native": native,
        "semantic_controls": faults,
    }


def audit(blobs, modules, provider, run, progress=None):
    data = modules["support"].artifacts(blobs, provider, run)
    previous = io.decode(blobs[io.PEER + "RESULT-" + provider + ".json"])
    old_pair = io.decode(blobs[io.PRIOR + "RESULT-" + provider + ".json"])
    checked, cases = {}, {}
    helpers = {
        "L" + str(h) for h in range(224, 704) if h not in data["word"]["removed"]
    }
    io.require(len(helpers) == 408, "all 408 dirty helpers")
    source_rows = boundary.source_rows(modules["endpoints"], data["word"], helpers)
    for orientation in ("forward", "backward"):
        cases[orientation] = case(
            modules, data, previous, old_pair, helpers, orientation, checked, progress
        )
        cases[orientation]["source_covector_rows"] = source_rows[orientation]
    return {
        "status": "PASS_COMPLETE_SOURCE_NATIVE_BOUNDARY",
        "provider": provider,
        "scientific_head": "be191346391661f4d35fc0d1508d0a6029572576",
        "orientations": cases,
        "distinct_native_identities": len(checked),
        "native_identity_receipts": sorted(
            checked.values(), key=lambda r: r["receipt_id"]
        ),
        "input_sha256": {p: io.sha(b) for p, b in sorted(blobs.items())},
        "new_supplier": False,
        "new_kappa": False,
    }


def compute(provider, artifacts=None, progress=None):
    blobs = io.inputs()
    own = {p.name: io.sha(io.read(p)) for p in io.PACKAGE.glob("*.py")}
    modules = io.modules(blobs)
    if artifacts is None:
        with tempfile.TemporaryDirectory(prefix="complete-native-") as name:
            run = modules["support"].generate(blobs, provider, Path(name), progress)
            result = audit(blobs, modules, provider, run, progress)
    else:
        result = audit(blobs, modules, provider, artifacts, progress)
    io.require(io.inputs() == blobs, "all source inputs unchanged during replay")
    io.require(
        own == {p.name: io.sha(io.read(p)) for p in io.PACKAGE.glob("*.py")},
        "checking code unchanged during replay",
    )
    result["checker_sha256"] = own
    return io.decode(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=("base", "extra"))
    parser.add_argument("--artifacts", type=Path)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()

    def progress(value):
        print(json.dumps(value, sort_keys=True), file=sys.stderr, flush=True)

    result = compute(args.provider, args.artifacts, progress if args.progress else None)
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        expected = io.result(args.provider)
        io.require(result == expected, "complete deterministic receipt equality")
        print(result["status"] + " provider=" + args.provider)


if __name__ == "__main__":
    main()
