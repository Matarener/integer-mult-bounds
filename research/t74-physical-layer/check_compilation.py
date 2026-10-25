# SPDX-License-Identifier: Apache-2.0
"""Check complete source compilation and fail-closed lifetime/phase boundaries."""
from copy import deepcopy
from pathlib import Path

from compile_word import Compiler, check, need, read_native


def run(prepared):
    prepared = Path(prepared)
    result = {pid: check(prepared / "bound/base/providers" / pid) for pid in ("gauge44", "extra")}
    original = read_native(prepared / "bound/base/providers/gauge44")
    rejected = []

    def reject(label, mutate):
        data = deepcopy(original)
        mutate(data)
        try:
            Compiler(data, "forward").run()
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("accepted compiler corruption: " + label)

    def missing_release(data):
        events = data["programs"]["forward"]
        events.pop(next(i for i, e in enumerate(events) if e[:2] == ["zero_buffer", "free"]))

    def premature_release(data):
        events = data["programs"]["forward"]
        event = next(e for e in events if e[:2] == ["zero_buffer", "alloc"])
        event[1] = "free"

    def warp_frame(data):
        event = next(e for e in data["programs"]["forward"] if e[0] == "warp")
        event[3] = -1

    def charged_warp(data):
        event = next(e for e in data["programs"]["forward"] if e[0] == "warp")
        key = (1 if event[2] > 0 else -1, abs(event[2]), event[3], event[4])
        record = next(r for r in data["native"]["warps"] if (r["sign"], r["op"], r["old"], r["new"]) == key)
        record["rank"] = 1

    for label, mutate in (("missing_zero_release", missing_release), ("release_before_allocation", premature_release),
                           ("wrong_warp_source_frame", warp_frame), ("unpaid_positive_warp", charged_warp)):
        reject(label, mutate)
    return dict(status="PASS_T74_COMPLETE_LOCAL_COMPILATION", programs=result, rejected=rejected,
                scope="Complete finite instruction coverage and lifetime/rank failure controls; native identity and physical execution have separate checks.")
