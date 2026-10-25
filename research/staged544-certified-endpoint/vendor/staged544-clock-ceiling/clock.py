# SPDX-License-Identifier: Apache-2.0
"""The changed T360 source clock: one deterministic rule applied to PR3734's ORDER.json.

Greedy merge of the predecessor call list. At tick t the next call is the first listed
call whose replica has already placed every earlier stage, except that a stage-1 call
is skipped while it would raise the number of placed stage-1 calls above 53/224 (t + 1).

Why 53/224: a stage-1 call closes its owner's two rank-16 children (-1, tau1]. In the
fixed-inventory ideal every rank-16 slot holds (7, 9), so each closing pair of children
needs 224 width-7 helpers, while every call supplies 53. Integer arithmetic only.
"""


def throttle(order, stage=1, num=53, den=224):
    pending = [tuple(x) for x in order]
    replicas = 1 + max(r for _, r in pending)
    nxt = [0] * replicas                       # next stage expected per replica
    out, placed = [], 0
    while pending:
        t = len(out)
        for i, (s, r) in enumerate(pending):
            if nxt[r] != s:
                continue
            if s == stage and den * (placed + 1) > num * (t + 1):
                continue
            break
        else:
            raise ValueError('no admissible call')
        s, r = pending.pop(i)
        out.append([s, r])
        nxt[r] += 1
        placed += s == stage
    return out


def check_order(order, replicas=360, stages=9):
    if len(order) != stages * replicas or {tuple(x) for x in order} != {(s, r) for s in range(stages) for r in range(replicas)}:
        raise ValueError('call coverage')
    seen = [0] * replicas
    for s, r in order:
        if s != seen[r]:
            raise ValueError('per-replica stage order')
        seen[r] += 1
