"""Build the G20 scalar conjugations and all required native routes.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retain the source geometry, caller and author notices in prior/.
"""
from collections import Counter
from copy import deepcopy


def need(ok, message):
    if not ok:
        raise ValueError(message)


def scalar_records(word):
    return [e[:] for e in word["records"] if e[0] not in ["Q", "ZERO_Q"]]


def scalar_endpoint(records, width, owned):
    rows = [1 << i for i in range(width)]
    for e in records:
        op, d = e[:2]
        if op == "ADD":
            rows[d] ^= rows[e[2]]
        elif op == "ERASE":
            need(d in owned, "Only owned erasure")
            rows[d] = 0
        elif op == "INIT":
            need(d in owned and not rows[d], "Only whole zero INIT")
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
                for i in range(width)]
    need(rows == expected, "All scalar input and dirty columns")


def cancel(word, receipts):
    out = deepcopy(word)
    width, owned = len(word["start"]), set(word["owned"])
    for receipt in receipts:
        records = out["records"]
        rows = [1 << i for i in range(width)]
        zeros = set()
        for ix, e in enumerate(records):
            if e[0] == "ADD":
                if not rows[e[2]]:
                    zeros.add(ix)
                rows[e[1]] ^= rows[e[2]]
            elif e[0] == "ERASE":
                rows[e[1]] = 0
        need(zeros == set(receipt["zero_source_contacts"]), "Exact zero source contacts")
        drop = set(zeros)
        for i, j, a, b in receipt["pairs"]:
            need(0 <= i < j < len(records), "Ordered cancellation indices")
            need(records[i][:3] == records[j][:3] == ["ADD", a, b], "Equal transvections")
            need(i not in drop and j not in drop, "Disjoint cancellation pairs")
            for e in records[i + 1:j]:
                if e[0] == "ADD":
                    need(e[1] != b and e[2] != a, "Every intervening scalar map commutes")
                elif e[0] in ["ERASE", "INIT"]:
                    need(e[1] not in [a, b], "No erased cancellation operand")
            drop.update([i, j])
        need(len(drop) == receipt["removed"], "Exact removed contact count")
        out["records"] = [e for i, e in enumerate(records) if i not in drop]
        scalar_endpoint(out["records"], width, owned)
    return out


def conjugate(word, witness):
    records = scalar_records(word)
    c = witness["candidate"]
    first, last = c["first"], c["last"]
    a, b = c["gate"]
    need(0 <= first < last < len(records), "Ordered conjugation indices")
    need(records[first][:3] == records[last][:3] == ["ADD", a, b], "Equal outer transvections")
    changes = []
    for i in range(first + 1, last):
        e = records[i]
        if e[0] in ["ERASE", "INIT"]:
            need(e[1] not in [a, b], "No erased conjugation operand")
        elif e[0] == "ADD" and (e[1] == b or e[2] == a):
            d, s = e[1:3]
            if d == b and s != a:
                extra = ["ADD", a, s, e[3]]
            else:
                need(s == a and d != b, "A2 transvection relation")
                extra = ["ADD", d, b, e[3]]
            changes.append((i, extra))
    need(changes == [(x["index"], x["extra"]) for x in c["changes"]],
         "Every noncommuting contact has its correction")
    need(len(changes) == len(witness["frames"]), "One actual coframe per correction")
    replacements = {i: (extra, f) for (i, extra), f in zip(changes, witness["frames"])}
    out = []
    for i, e in enumerate(records):
        if i in [first, last]:
            continue
        if i in replacements:
            extra, f = replacements[i]
            out.extend([e[:3] + [f], extra[:3] + [f]])
        else:
            out.append(e)
    scalar_endpoint(out, len(word["start"]), set(word["owned"]))
    return out


def emit(word, scalars, paths, geometry):
    width, owned = len(word["start"]), set(word["owned"])
    rows, state = [1 << i for i in range(width)], word["start"][:]
    records = []

    def route(d, target):
        source = state[d]
        if source == target:
            return
        if source is None:
            need(d in owned and not rows[d], "Only zero owned header")
            records.append(["INIT", d, target])
            state[d] = target
            return
        path = paths[str(source) + ":" + str(target)]
        need(path and path[0][0] == source and path[-1][1] == target, "Route endpoints")
        for a, b, rank in path:
            need(state[d] == a, "Route continuity")
            geometry.nested(a, b, rank)
            records.append(["Q" if rows[d] else "ZERO_Q", d, a, b, rank])
            state[d] = b

    for e in scalars:
        op, d = e[:2]
        if op in ["ERASE", "INIT"]:
            need(d in owned and (op == "ERASE" or not rows[d]), "Owned clear or whole zero INIT")
            rows[d], state[d] = 0, e[2]
            records.append(e[:])
        else:
            need(op == "ADD", "Scalar opcode")
            s, frame = e[2:]
            if not rows[s]:
                continue
            route(d, frame)
            route(s, frame)
            records.append(e[:])
            rows[d] ^= rows[s]
    for d, frame in enumerate(word["final"]):
        if d in owned:
            need(not rows[d], "Whole owned return")
            if state[d] != frame:
                records.append(["ERASE", d, frame])
                state[d] = frame
        else:
            route(d, frame)
    need(state == word["final"], "Every final frame")
    scalar_endpoint(records, width, owned)
    return dict(word, records=records)


def paid(word):
    return Counter(e[4] for e in word["records"] if e[0] == "Q")
