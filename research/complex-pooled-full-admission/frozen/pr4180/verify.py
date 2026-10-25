#!/usr/bin/env python3
"""Bounded binding regression; full inherited release uses replay.py separately.

SPDX-License-Identifier: Apache-2.0
Prepared for yssite with substantial OpenAI Codex assistance.
"""
import json
import sys
import unittest

from adapt import MIXED, TAGS
from binding import account, need, read
from sources import authenticate_sources


def real_call_binding():
    # Reuse PR4088's declared source-window interpretation, not its walk().
    # The separate campaign scanner also challenged this interpretation from
    # exact event positions and actual phase-axis lists.
    sys.path.insert(0, str(MIXED))
    from owner_verify import context
    order, selected, windows, family, widths, profiles = context()
    original = read(MIXED / "owner/PLAN.json.gz")
    registry = {}
    for pid, tag in TAGS.items():
        kind = "NATIVE" if tag.endswith("-four") else "THREE"
        checks = read(MIXED / f"evidence/{kind}-LOCAL-{tag.split('-')[0]}.json")
        registry[pid] = dict(widths=widths[pid], actual_paid_profile=profiles[pid],
                             orientation_program_sha256={o: checks[o]["sha256"]
                                                         for o in ("forward", "backward")})
    calls, per_call = [], []
    for time, (stage, replica) in enumerate(order):
        pid = selected[stage, replica]
        orientation = "forward" if stage % 2 == 0 else "backward"
        calls.append(dict(stage=stage, replica=replica, time=time, provider=pid, orientation=orientation,
                          local_program_sha256=registry[pid]["orientation_program_sha256"][orientation]))
        per_call.append(dict(stage=stage, replica=replica, time=time, widths=widths[pid]))
    plan = dict(order=order, provider_registry=registry, provider_calls=calls, per_call_widths=per_call,
                pairs=original["pairs"], sides=original["sides"],
                windows={f"{o},{c}": (cap, range(lo + 1, hi + 1))
                         for (o, c), (cap, lo, hi) in windows.items()})
    rows = read(MIXED / "owner/FILL.json.gz")["rows"]

    class Roles:
        def __len__(self):
            return len(rows)

        def __iter__(self):
            for time, helper, owner, child, port, offset in rows:
                stage, replica = order[time]
                yield dict(time=time, helper=helper, stage=stage, replica=replica,
                           owner_replica=owner, child=child, port=port, offset=offset,
                           family=896 * owner + 112 * family[child] + port,
                           copy=112 * owner + port, width=widths[selected[stage, replica]][helper])

    idle, total = account(plan, Roles(), read(MIXED / "owner/MIXED-DISPATCH.json"))
    expected = read(MIXED / "RESULT.json")
    need(idle == {int(k): v for k, v in expected["idle"].items()}, "actual idle")
    need(total == {int(k): v for k, v in expected["profile"].items()}, "actual complete profile")
    return dict(rows=len(rows), calls=len(order), providers=len(registry), idle=idle, profile=total)


def main():
    inputs = authenticate_sources()
    suite = unittest.defaultTestLoader.loadTestsFromName("test_binding")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    need(result.wasSuccessful(), "binding controls")
    finite = real_call_binding()
    print(json.dumps(dict(status="PASS_FOUR_PROVIDER_BINDING_REGRESSION", live_inputs=inputs,
                          tests=result.testsRun, finite=finite,
                          scope="Binding and negative controls only; full release is a separate command."),
                     sort_keys=True))


if __name__ == "__main__":
    main()
