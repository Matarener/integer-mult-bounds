"""Audit one scalar word by individual rows and columns over the rationals.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The basis formulas and split schedule are from PR5751/5599/5609.
This checker imports no source constructor, matrix checker or price engine.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json

from evidence import need


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def vector(record):
    return {int(i): Q(x) for i, x in record.items() if Q(x)}


def encoded(value):
    return {str(i): str(x) for i, x in sorted(value.items()) if x}


def set_value(value, index, item):
    if item:
        value[index] = item
    else:
        value.pop(index, None)


def operations(program):
    result = []
    for event in program:
        op, target = event[:2]
        if op == "MOVE":
            continue
        need(op in ("INIT", "CLEAR", "ADD", "COPY", "SCALE"), "Known scalar operation")
        result.append((op, target, event[2] if op in ("ADD", "COPY") else None,
                       Q(event[-2]) if op not in ("INIT", "CLEAR") else None))
    return result


def push(column, program, check_copy=False):
    """Apply a chronological scalar program to one input column."""
    value = dict(column)
    for op, target, source, coefficient in program:
        if op in ("INIT", "CLEAR"):
            value.pop(target, None)
        elif op == "SCALE":
            set_value(value, target, coefficient * value.get(target, 0))
        else:
            old = value.get(target, 0)
            if op == "COPY":
                need(not check_copy or not old, "COPY destination is zero for every input")
                old = 0
            set_value(value, target, old + coefficient * value.get(source, 0))
    return value


def pull(row, program):
    """Apply the transpose in reverse chronology to one output functional."""
    value = dict(row)
    for op, target, source, coefficient in reversed(program):
        if op in ("INIT", "CLEAR"):
            value.pop(target, None)
        elif op == "SCALE":
            set_value(value, target, coefficient * value.get(target, 0))
        else:
            contribution = coefficient * value.get(target, 0)
            if op == "COPY":
                value.pop(target, None)
            set_value(value, source, value.get(source, 0) + contribution)
    return value


def dot(row, column):
    return sum(x * column.get(i, 0) for i, x in row.items())


def unit(value):
    n, d = abs(value.numerator), value.denominator
    return n > 0 and n & (n - 1) == 0 and d & (d - 1) == 0


def spans(word):
    result = []
    for basis in word["frames"]:
        span = {0}
        for row in basis:
            need(type(row) is int and 0 < row < 512 and row not in span,
                 "Independent binary frame basis")
            span |= {x ^ row for x in tuple(span)}
        result.append(frozenset(span))
    return result


def chronology(word, stop=None):
    """Recount actual fields and charges; no scalar endpoint is assumed here."""
    public, owned = word["public"], word["owned_fields"]
    current = list(word["initial"]) + [None] * owned
    frame = spans(word)
    active, paid, scalar, lifetimes, peak = set(), Counter(), 0, 0, 0
    events = word["program"] if stop is None else word["program"][:stop]
    for event in events:
        op, target = event[:2]
        need(type(target) is int and 0 <= target < public + owned, "Valid target role")
        if op == "MOVE":
            _, _, start, end, private = event
            need(type(private) is bool and private == (target in active)
                 and current[target] == start, "Actual transport source and ownership")
            need(frame[end] < frame[start] if private else frame[start] < frame[end],
                 "Strict nested transport")
            paid[abs(len(word["frames"][end]) - len(word["frames"][start]))] += 1
            current[target] = end
        elif op == "INIT":
            need(target >= public and target not in active, "Owned initialization")
            active.add(target)
            current[target] = event[2]
            lifetimes += 1
            peak = max(peak, len(active))
            scalar += 2
        elif op == "CLEAR":
            need(target in active and current[target] == event[2], "Owned erasure")
            active.remove(target)
            current[target] = None
            scalar += 2
        else:
            need(op in ("ADD", "COPY", "SCALE"), "Known physical operation")
            coefficient, basis = Q(event[-2]), event[-1]
            n, d = abs(coefficient.numerator), coefficient.denominator
            need(coefficient and not d & (d - 1) and abs(coefficient) + 1 < 2**16,
                 "Nonzero bounded dyadic scalar")
            need(current[target] == basis, "Scalar target has the stated frame")
            if op == "SCALE":
                need(unit(coefficient), "Invertible dyadic scale")
                scalar += 2 * (abs(n.bit_length() - d.bit_length()) + int(coefficient < 0))
            else:
                source = event[2]
                need(type(source) is int and 0 <= source < public + owned and source != target
                     and current[source] == basis, "Actual common scalar frame")
                need(op != "COPY" or target in active, "COPY target is owned")
                scalar += 2 * (n.bit_length() + n.bit_count() + d.bit_length() + 1)
    if stop is not None:
        return current
    need(not active and current[:public] == word["final"], "Complete physical exits")
    main = set(word["live"]) | {i + 112 for i in word["live"]}
    helpers = Counter(len(word["frames"][word["final"][i]])
                      - len(word["frames"][word["initial"][i]])
                      for i in range(public) if i not in main)
    need(min(helpers) > 0, "Positive helper ranks")
    return {"paid": paid, "helpers": helpers, "scalar": scalar,
            "owned_lifetimes": lifetimes, "peak_owned": peak}


def inverse(events):
    result = []
    for event in reversed(events):
        item = list(event)
        q = Q(item[-2])
        item[-2] = str(1 / q if item[0] == "SCALE" else -q)
        result.append(item)
    return result


def bases(pivot, frame, a, b, c, d):
    boundary = [["ADD", pivot, i, str(-x), 3] for i, x in sorted(c.items()) if i != pivot]
    if d[pivot] != 1:
        boundary.append(["SCALE", pivot, str(d[pivot]), 3])
    boundary += [["ADD", i, pivot, str(x / d[pivot]), 3]
                 for i, x in sorted(d.items()) if i != pivot]
    cut = [] if a[pivot] == 1 else [["SCALE", pivot, str(a[pivot]), frame]]
    cut += [["ADD", pivot, i, str(x), frame] for i, x in sorted(a.items()) if i != pivot]
    cut += [["ADD", i, pivot, str(-x), frame] for i, x in sorted(b.items()) if i != pivot]
    return boundary, cut


def check_cut(word, cut, frame, plan):
    a, b = vector(plan["retirement"]), vector(plan["injection"])
    prefix = operations(word["program"][:cut])
    suffix = operations(word["program"][cut:])
    c, d = pull(a, prefix), push(b, suffix)
    need(encoded(c) == plan["input"] and encoded(d) == plan["output"],
         "Exact independent boundary functionals")
    need(dot(a, b) == 1 and dot(c, d) == 1, "Both unit pairings")
    need(push(d, prefix) == b, "Prefix column transport")
    complete = prefix + suffix
    need(pull(c, complete) == c and push(d, complete) == d, "Identity boundary modes")
    pivot = plan["pivot"]
    e = {pivot: Q(1)}
    need(pull(e, complete) == e and push(e, complete) == e, "Identity pivot row and column")
    current = chronology(word, cut)
    need(all(current[i] == frame for i in set(a) | set(b)), "Cut support is physically present")
    main = set(word["live"]) | {i + 112 for i in word["live"]}
    need(all(0 <= i < word["public"] and i not in main and word["initial"][i] == 3
             and word["final"][i] == 127 for i in set(c) | set(d)),
         "Full independent boundary helpers")
    need(unit(a.get(pivot, Q(0))) and unit(d.get(pivot, Q(0))), "Dyadic basis pivots")
    boundary, middle = bases(pivot, frame, a, b, c, d)
    q, s = operations(boundary), operations(middle)
    need(push(e, q) == d and pull(c, q) == e, "Both input-basis identities")
    need(push(b, s) == e and pull(e, s) == a, "Both cut-basis identities")
    return boundary, middle, {
        "cut": cut, "frame": frame, "pivot": pivot, "fresh": word["public"],
        "input": encoded(c), "output": encoded(d),
        "retirement": encoded(a), "injection": encoded(b),
        "basis_operations": 2 * (len(boundary) + len(middle)),
    }


def rebuild(source, plan):
    need(digest(source) == plan["source_word_sha256"], "Exact starting word")
    word = deepcopy(source)
    meetings, snapshots = [], []
    frame_spaces = spans(source)
    for meeting in plan["meetings"]:
        cut, frame = meeting["cut"], meeting["frame"]
        word["program"] = [list(e) for e in word["program"]]
        added = []
        for move in meeting["moves"]:
            at, old = move["event"], move["event_value"]
            need(at >= cut and word["program"][at] == old and old[0] == "MOVE"
                 and old[4] is False, "Exact public future query")
            need(frame_spaces[old[2]] < frame_spaces[frame] < frame_spaces[old[3]],
                 "Proper intermediate frame")
            role = old[1]
            need(all(role not in (e[1:3] if e[0] in ("ADD", "COPY") else e[1:2])
                     for e in word["program"][cut:at]), "No intervening field access")
            added.append(["MOVE", role, old[2], frame, False])
            word["program"][at][2] = frame
        word["program"][cut:cut] = added
        cut += len(added)
        steps = []
        for step in meeting["splits"]:
            if frame == 105:
                snapshots.append((deepcopy(word), cut, frame, deepcopy(step)))
            boundary, middle, receipt = check_cut(word, cut, frame, step)
            public, pivot = word["public"], step["pivot"]
            def renamed(events, continuing):
                answer = []
                for old in events:
                    event = list(old)
                    for i in (1, 2) if old[0] in ("ADD", "COPY") else (1,):
                        role = old[i]
                        event[i] = (public if continuing and role == pivot
                                    else role + 1 if role >= public else role)
                    answer.append(event)
                return answer
            before = renamed(boundary + word["program"][:cut] + middle, False)
            undo_cut = renamed(inverse(middle), True)
            after = inverse(boundary)
            for event in after:
                event[-1] = 127
            next_cut = len(before) + len(undo_cut)
            program = before + undo_cut + renamed(word["program"][cut:] + after, True)
            result = dict(word)
            result.update(public=public + 1, program=program, schema="p104-paid-meeting-splits/1")
            result["initial"] = word["initial"] + [frame]
            result["final"] = list(word["final"]) + [127]
            result["final"][pivot] = frame
            receipt["next_cut"] = next_cut
            steps.append(receipt)
            word, cut = result, next_cut
        meetings.append({"frame": frame, "added_queries": len(added), "steps": steps})
    return word, {"source_word_sha256": digest(source), "word_sha256": digest(word),
                  "meetings": meetings}, snapshots


def check_column(word, source, program=None):
    actual = push({source: Q(1)}, operations(word["program"]) if program is None else program,
                  check_copy=True)
    expected = {source: Q(1)} if source < word["public"] else {}
    if source in word["live"]:
        expected[source + 112] = Q(1)
    need(actual == expected, "Complete scalar input column: " + str(source))


def all_columns(word):
    program = operations(word["program"])
    size = word["public"] + word["owned_fields"]
    for source in range(size):
        check_column(word, source, program)
    return {"columns": size, "coefficients": size * size,
            "dirty_owned_columns": word["owned_fields"], "copy_zero_checked": True}


def invoice(local, controller):
    paid, targets, counts = Counter(), Counter(), Counter()
    for event in controller["physical_events"]:
        op = event[0]
        need(op in ("LOCAL", "QUERY_SHEAR", "IDLE", "ADD", "SIGNED_SWAP", "Q_POWER"),
             "Known complete-controller operation")
        counts[op] += 1
        if op == "LOCAL":
            need(event[3] is False, "Forward local invocation")
            paid.update(local["paid"])
            targets.update(local["helpers"])
        elif op == "QUERY_SHEAR":
            paid[1] += 104
        elif op == "IDLE":
            paid[8 * len(event[2])] += 208
    for diagonal in controller["diagonal"]:
        targets[1 + 8 * sum(diagonal[1:])] += 104
    need(counts["LOCAL"] == 18 and counts["QUERY_SHEAR"] == counts["IDLE"] == 15,
         "Complete retained controller multiplicities")
    return {"paid": dict(sorted(paid.items())), "targets": dict(sorted(targets.items())),
            "paid_calls": sum(paid.values()), "productive_fields": sum(targets.values()),
            "rank_mass_surplus": sum(r * n for r, n in targets.items())
            - sum(r * n for r, n in paid.items())}
