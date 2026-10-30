# SPDX-License-Identifier: Apache-2.0
"""Complete normalized helper observations and exact coverage comparisons."""

from collections import Counter
from fractions import Fraction


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def scalar(rows, active, event, algebra):
    op, target = event[1], event[1][1]
    used = op[1:3] if op[0] in ("add", "copy") else op[1:2]
    require(
        all(not r.startswith("Z") or r in active for r in used),
        "private use outside lifetime",
    )
    if op[0] == "clear":
        require(target in rows or target.startswith("C"), "CLEAR target")
        rows[target] = {}
    elif op[0] == "copy":
        require(target != op[2], "distinct COPY operands")
        rows[target] = dict(rows[op[2]])
    elif op[0] == "scale":
        q = Fraction(op[2], op[3])
        require(q != 0, "nonzero scale")
        rows[target] = {k: q * v for k, v in rows[target].items()}
    else:
        require(op[0] == "add" and target != op[2], "distinct ADD operands")
        rows[target] = algebra.merge(rows[target], rows[op[2]], Fraction(op[3], op[4]))


def normalized(events, original, helpers, backward, algebra):
    """All original inputs are formal variables; allocated private inputs are zero."""
    require(len(events) <= 100000 and len(original) == 632, "finite stream domain")
    rows = {r: {(r, ()): Fraction(1)} for r in original}
    active, allocated, frees, post = set(), set(), [], {}
    for index, event in enumerate(events):
        tag = event[0]
        if tag == "zero_buffer":
            action, role = event[1:]
            if action == "alloc":
                require(role not in allocated and role not in rows, "fresh private")
                active.add(role)
                allocated.add(role)
                rows[role] = {}
            else:
                require(action == "free" and role in active, "matched private free")
                require(not rows[role], "nonzero private at actual free")
                frees.append([role, index])
                active.remove(role)
                del rows[role]
        elif tag == "scalar":
            scalar(rows, active, event, algebra)
        elif tag == "warp":
            role, op = event[1:3]
            if backward:
                op = (1 if op > 0 else -1) * (1000000 + abs(op))
            rows[role] = algebra.warp(rows[role], op)
        else:
            require(
                tag in ("phase", "climb", "center", "adapter", "residual_adapter"),
                "known event kind",
            )
            if tag == "residual_adapter" and event[1] == "post":
                require(event[2] not in post, "unique helper post wrapper")
                post[event[2]] = [index, algebra.encode(rows[event[2]])]
    require(not active and len(frees) == len(allocated) == 91, "all 91 actual frees")
    result = {r: algebra.encode(rows[r]) for r in sorted(helpers)}
    bad = next(((r, v) for r, v in result.items() if v != [[r, [], "1"]]), None)
    require(bad is None, "all dirty helper outputs restored: " + repr(bad))
    return {"helper_outputs": result, "post_wrappers": post, "private_frees": frees}


def source_rows(engine, word, helpers):
    """A distinct retained backward algorithm checks the original source word."""
    live = set(range(704)) - set(word["removed"])
    buffers = {704 + int(h) for h in word["helper_final"]}
    gates, result = engine.program(word), {}
    for dual in (False, True):
        rows = {}
        for role in sorted(helpers):
            index = int(role[1:])
            pulled = engine.endpoint(gates, index, dual, live, buffers)
            projected = [r for r in pulled if r[0] in live]
            require(projected == [(index, (), "1")], "source helper restoration")
            rows[role] = [[r, list(w), q] for r, w, q in pulled]
        result["backward" if dual else "forward"] = rows
    return result


def prior_delta(native, events, canonical, previous, old_pair, orientation):
    full = native.classes(
        events, [i for i, e in enumerate(events) if e[0] != "phase"], canonical
    )
    old = previous["orientations"][orientation]["native"]
    earlier = old_pair["orientations"][orientation]["native"]["associations"]
    old_classes = {tuple(row["class"]) for row in earlier}
    old_classes.update(tuple(row["class"]) for row in old["new_class_associations"])
    require(len(old_classes) == old["expanded_classes"], "prior union class count")
    require(old_classes <= set(full), "prior classes belong to complete stream")
    new = sorted(set(full) - old_classes, key=native.stable_key)
    return {
        "prior_classes": len(old_classes),
        "complete_classes": len(full),
        "new_classes": [list(k) for k in new],
        "new_native_events": sum(len(full[k]) for k in new),
        "complete_native_events": sum(len(v) for v in full.values()),
    }


def paid_profile(events):
    return dict(
        sorted(
            Counter(
                e[5] if e[0] == "climb" else e[4]
                for e in events
                if e[0] in ("climb", "center")
            ).items()
        )
    )
