#!/usr/bin/env python3
"""Exact eight-field ADD-resynthesis obstruction; standard library only.

The optimistic linear information-flow network permits arbitrary scalar mixing
at every shared frame. Its unit-capacity wires give necessary rank conditions,
never sufficient implementability claims.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Source construction credit: Cao Yifan, Dillon Amburgey, Ali Romman,
Chris R/Clear1nsight, GamingPuzzled and the retained native/compiler lineage.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import itertools
import json
from pathlib import Path

CANONICAL = "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
PROVIDER = ("research/coupled-helper-neutral-completion/capsule/workspace/"
            "swarm-provider-audit-sol-high-20261024/repository/research/"
            "native-rank8-helper-provider/WORD.json.gz")
PINS = {
    CANONICAL: "7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05",
    PROVIDER: "7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc",
}
START, STOP = 9044, 9116
FIELDS = [19, 40, 288, 289, 295, 299, 300, 301]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reject(operation, label):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("negative control unexpectedly accepted: " + label)


def span(vectors):
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in result}
    return frozenset(result)


def dimension(space):
    need(len(space) and len(space) & (len(space) - 1) == 0, "power-of-two subspace size")
    return len(space).bit_length() - 1


def frame_state(program, canonical, stop):
    current = {("L", i): f for i, f in enumerate(canonical["start"])}
    current[("C", 0)] = None
    for event in program[:stop]:
        if event[0] == "climb":
            _, _, i, a, b, _ = event
            need(current[("L", i)] == a, "chronological climb entrance")
            current[("L", i)] = b
        elif event[0] == "warp":
            _, field, _, a, b = event
            need(current[tuple(field)] == a, "chronological warp entrance")
            current[tuple(field)] = b
        elif event[0] == "center":
            _, i, a, b, _ = event
            need(current[("C", i)] == a, "chronological centre entrance")
            current[("C", i)] = b
        elif event[0] == "scalar":
            operation, f = event[1:]
            if operation[0] == "clear":
                current[tuple(operation[1])] = f
    return current


def participants(event):
    if event[0] == "scalar":
        return {tuple(x) for x in event[1][1:] if isinstance(x, list)}
    if event[0] == "climb":
        return {("L", event[2])}
    if event[0] == "warp":
        return {tuple(event[1])}
    if event[0] == "center":
        return {("C", event[1])}
    return set()


def closed_fields(program, stop=STOP):
    selected = {("L", i) for i in (19, 300, 301)}
    while True:
        enlarged = selected | set().union(*(participants(e) for e in program[START:stop]
                                            if selected & participants(e)))
        if enlarged == selected:
            break
        selected = enlarged
    need(all(kind == "L" for kind, _ in selected), "no owned centre/scratch inside closure")
    return sorted(i for _, i in selected)


def invertible_prefix(program):
    """Audit the prefix grammar; native climb/warp invertibility is inherited."""
    for event in program[:START]:
        need(event[0] in ("scalar", "warp", "climb", "phase", "adapter", "residual_adapter"),
             "prefix has only invertible persistent operations and annotations")
        if event[0] == "scalar":
            op = event[1]
            need(op[0] in ("add", "scale") and op[1][0] == "L",
                 "prefix has no destructive scalar operation")
            if op[0] == "add":
                need(op[2][0] == "L" and op[1] != op[2] and op[4] != 0,
                     "prefix has only invertible ADDs")
            else:
                need(op[2] != 0 and op[3] != 0, "prefix has only nonzero SCALEs")
        elif event[0] == "warp":
            need(event[1][0] == "L", "prefix has only persistent warp targets")


def extract(program, canonical):
    fields = closed_fields(program)
    need(fields == FIELDS, "exact eight-field dependency closure")
    at_start = frame_state(program, canonical, START)
    current = {i: at_start[("L", i)] for i in fields}
    entry = dict(current)
    rows = {i: [Q(int(i == j)) for j in fields] for i in fields}
    paid, events = Counter(), []
    paths = {i: [current[i]] for i in fields}
    spaces = [span(x) for x in canonical["frames"]]
    for index in range(START, STOP):
        event = program[index]
        touched = participants(event)
        if not touched.intersection({("L", i) for i in fields}):
            continue
        need(touched <= {("L", i) for i in fields}, "closed input/output fields")
        events.append([index, event])
        if event[0] == "climb":
            _, _, i, a, b, r = event
            need(current[i] == a and spaces[a] < spaces[b], "strict nested local climb")
            need(r == dimension(spaces[b]) - dimension(spaces[a]), "exact paid climb rank")
            current[i] = b
            paths[i].append(b)
            paid[r] += 1
        elif event[0] == "scalar":
            operation, f = event[1:]
            need(operation[0] in ("add", "scale"), "only reversible ADD/scale in local block")
            target = operation[1][1]
            need(current[target] == f, "receiver is at scalar frame")
            if operation[0] == "add":
                source = operation[2][1]
                need(current[source] == f and source != target, "co-framed distinct ADD fields")
                q = Q(operation[3], operation[4])
                rows[target] = [a + q * b for a, b in zip(rows[target], rows[source])]
            else:
                q = Q(operation[2], operation[3])
                need(q != 0, "invertible scale")
                rows[target] = [q * a for a in rows[target]]
        else:
            raise ValueError("no warp/centre/retag admitted inside local block")
    need(paid == {1: 10}, "retained local ten-H1 invoice")
    return {"fields": fields, "entry": entry, "exit": current, "matrix": [rows[i] for i in fields],
            "paths": paths, "events": events, "paid": paid}


def rank(matrix):
    rows = [list(row) for row in matrix]
    count = 0
    for j in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(count, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        value = rows[count][j]
        rows[count] = [a / value for a in rows[count]]
        for i in range(len(rows)):
            if i != count:
                value = rows[i][j]
                rows[i] = [a - value * b for a, b in zip(rows[i], rows[count])]
        count += 1
    return count


def interval_spaces(a, b):
    need(a <= b and dimension(b) <= 2, "bounded rank-two frame interval")
    found, todo = {a}, [a]
    while todo:
        current = todo.pop()
        for x in sorted(b - current):
            nxt = span([*current, x])
            if nxt not in found:
                found.add(nxt)
                todo.append(nxt)
    need(b in found and all(a <= u <= b for u in found), "complete subspace interval endpoints")
    return sorted(found, key=lambda u: (len(u), tuple(sorted(u))))


def all_paths(a, b):
    choices = interval_spaces(a, b)

    def descend(u):
        if u == b:
            return [(u,)]
        return [(u,) + path for v in choices if u < v for path in descend(v)]
    return descend(a)


def label(space):
    return ",".join(map(str, sorted(space)))


def rank_cut(paths, inputs, outputs):
    """Exact max-flow bound for unrestricted linear mixing at frame stations.

    Each ascending field edge transports one arbitrary data column. Co-framed
    fields may mix without restrictions, including time order and invertibility;
    relaxing these constraints can only increase the possible transfer rank.
    """
    source, sink = "SOURCE", "SINK"
    capacities = Counter()
    for path in paths.values():
        for a, b in zip(path, path[1:]):
            need(a < b, "acyclic strictly ascending station edge")
            capacities[(label(a), label(b))] += 1
    for field in inputs:
        capacities[(source, label(paths[field][0]))] += 1
    for field in outputs:
        capacities[(label(paths[field][-1]), sink)] += 1
    residual = Counter(capacities)
    neighbors = {}
    for a, b in capacities:
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
    flow = 0
    while True:
        previous = {source: None}
        todo = deque([source])
        while todo and sink not in previous:
            a = todo.popleft()
            for b in sorted(neighbors.get(a, set())):
                if b not in previous and residual[(a, b)] > 0:
                    previous[b] = a
                    todo.append(b)
        if sink not in previous:
            reachable = set(previous)
            break
        path, b = [], sink
        while b != source:
            a = previous[b]
            path.append((a, b))
            b = a
        amount = min(residual[e] for e in path)
        for a, b in path:
            residual[(a, b)] -= amount
            residual[(b, a)] += amount
        flow += amount
    cut = [(a, b, c) for (a, b), c in sorted(capacities.items()) if a in reachable and b not in reachable]
    need(sum(c for _, _, c in cut) == flow, "independently summed exact min-cut capacity")
    return {"capacity": flow, "source_side": sorted(reachable), "cut_edges": cut}


def minor(block, inputs, outputs):
    indices = {field: k for k, field in enumerate(block["fields"])}
    return [[block["matrix"][indices[o]][indices[i]] for i in inputs] for o in outputs]


def evaluate(block, direction, spaces):
    options = {i: all_paths(spaces[block["entry"][i]], spaces[block["exit"][i]]) for i in FIELDS}
    need({i: len(p) for i, p in options.items()} == {i: (4 if i in (300, 301) else 1) for i in FIELDS},
         "exhaustive sixteen trajectory assignments")
    rejected, neutral = [], []
    for selections in itertools.product(*(options[i] for i in FIELDS)):
        paths = dict(zip(FIELDS, selections))
        profile = Counter(dimension(b) - dimension(a) for path in paths.values() for a, b in zip(path, path[1:]))
        need(sum(r * c for r, c in profile.items()) == 10, "fixed boundary rank mass")
        collapsed = [i for i in (300, 301) if len(paths[i]) == 2]
        if not collapsed:
            neutral.append(paths)
            continue
        # These two-column minors survive arbitrary pre-basis changes at frame0.
        chosen = collapsed[0]
        inputs = [300, 301] if direction == "backward" else [19]
        outputs = ([19, 301] if chosen == 300 else [19, 300]) if direction == "backward" else [chosen]
        desired = minor(block, inputs, outputs)
        desired_rank = rank(desired)
        cut = rank_cut(paths, inputs, outputs)
        need(desired_rank > cut["capacity"], "every saving assignment violates necessary transfer-rank cut")
        rejected.append({"collapsed_helpers": collapsed,
                         "helper_paths": {str(i): [sorted(u) for u in paths[i]] for i in (300, 301)},
                         "paid_profile": dict(profile), "input_fields": inputs, "output_fields": outputs,
                         "required_minor": [[str(x) for x in row] for row in desired],
                         "required_rank": desired_rank, "rank_cut": cut})
    need(len(rejected) == 7 and len(neutral) == 9, "seven improving and nine neutral trajectories")
    return rejected, neutral


def run(root):
    raw = {}
    for path, expected in PINS.items():
        raw[path] = (root / path).read_bytes()
        need(sha256(raw[path]).hexdigest() == expected, "exact source hash: " + path)
    canonical_payload, provider_payload = (gzip.decompress(raw[p]) for p in (CANONICAL, PROVIDER))
    word, provider = json.loads(canonical_payload), json.loads(provider_payload)
    need(provider["source_sha256"] == sha256(canonical_payload).hexdigest(), "provider source binds canonical decompressed payload")
    need(provider["direction"] == "backward", "selected provider direction")
    invertible_prefix(provider["word"])
    need(provider["word"][START:STOP] == word["programs"]["backward"][START:STOP],
         "selected provider local tape equals inherited backward local tape")
    canonical = word["canonical"]
    spaces = [span(b) for b in canonical["frames"]]
    backward = extract(provider["word"], canonical)
    forward = extract(word["programs"]["forward"], canonical)
    need(backward["entry"] == forward["entry"] and backward["exit"] == forward["exit"],
         "same eight-field endpoint frame contract in both orientations")
    need(rank(backward["matrix"]) == rank(forward["matrix"]) == 8, "invertible exact eight-field transfer")
    back_rejected, _ = evaluate(backward, "backward", spaces)
    forward_rejected, _ = evaluate(forward, "forward", spaces)
    original_paths = {i: tuple(spaces[f] for f in backward["paths"][i]) for i in FIELDS}
    controls = []
    controls.append(reject(lambda: invertible_prefix([["scalar", ["scale", ["L", 0], 0, 1], 0]]),
                           "zero-prefix-scale-rejected"))
    for helper, outputs in ((300, [19, 301]), (301, [19, 300])):
        broken_paths = dict(original_paths)
        broken_paths[helper] = (original_paths[helper][0], original_paths[helper][-1])
        need(rank_cut(broken_paths, [300, 301], outputs)["capacity"] == 1,
             "deleting the line21 visit loses a transfer channel")
        repaired_paths = dict(broken_paths)
        repaired_paths[helper] = original_paths[helper]
        cut = rank_cut(repaired_paths, [300, 301], outputs)
        need(cut["capacity"] == rank(minor(backward, [300, 301], outputs)) == 2,
             "restored original line21 path admits necessary rank-two flow")
        controls.append("restore-helper-" + str(helper) + "-line21-rank-flow-admitted")
    changed = [list(row) for row in minor(backward, [300, 301], [19, 301])]
    need(changed == [[Q(0), Q(1)], [Q(-1), Q(-1)]], "named determinant-one target minor")
    changed[0][1] = Q(0)
    broken_paths = dict(original_paths)
    broken_paths[300] = (original_paths[300][0], original_paths[300][-1])
    need(rank(changed) == rank_cut(broken_paths, [300, 301], [19, 301])["capacity"] == 1,
         "deleted target coefficient removes this necessary-rank contradiction")
    controls.append(reject(lambda: need(rank(changed) == 2, "required minor rank changed"), "delete-required-b-coefficient-destroys-obstruction"))
    controls.append(reject(lambda: need(sha256(raw[PROVIDER] + b"x").hexdigest() == PINS[PROVIDER], "changed source"), "changed-provider-source-rejected"))
    # Full closure restoration occurs well before the first protected cache copy.
    cache = [(i, e) for i, e in enumerate(provider["word"]) if e[0] == "scalar" and e[1][0] == "copy" and e[1][1][0] == "C"]
    first_later = next(i for i, _ in cache if i >= STOP)
    need(first_later == 11207 and not any(START <= i < STOP for i, _ in cache), "protected cache checkpoint untouched")
    protected_copies = [[i, e] for i, e in cache if e[1][1][1] in range(1, 9)]
    zero_retags = [[i, e] for i, e in enumerate(provider["word"]) if e[0] == "zero_retag"]
    need(len(protected_copies) == 8 and sorted(e[1][1][1] for _, e in protected_copies) == list(range(1, 9)),
         "eight protected cached centres")
    need(len(zero_retags) == 8 and all(i >= STOP for i, _ in zero_retags), "eight later zero-retags outside block")
    next_fields = closed_fields(provider["word"], 9137)
    need(len(next_fields) == 20, "larger next closure has twenty fields")
    def record(block):
        return {"entry_frames": block["entry"], "exit_frames": block["exit"],
                "matrix": [[str(x) for x in row] for row in block["matrix"]],
                "paid_profile": dict(block["paid"]), "retained_paths": block["paths"],
                "local_events": block["events"]}
    return {"status": "PASS_EIGHT_FIELD_MONOTONE_ADD_FLOOR_NO_NEW_KAPPA", "schema_version": 1,
            "block": {"start": START, "stop": STOP, "indexing": "zero-based half-open", "fields": FIELDS},
            "source_inputs": [{"path": p, "sha256": h, "decompressed_sha256": sha256(gzip.decompress(raw[p])).hexdigest()} for p, h in PINS.items()],
            "selected_backward": record(backward), "inherited_forward": record(forward),
            "prefix_events_checked_for_invertible_grammar": START,
            "frame_bases": {str(f): canonical["frames"][f]
                            for f in sorted(set(backward["entry"].values()) | set(backward["exit"].values()))},
            "next_closure_not_optimized": {"interval": [START, 9137], "fields": next_fields},
            "complete_trajectory_assignments_per_orientation": 16,
            "cost_saving_trajectories_rejected_per_orientation": 7,
            "neutral_trajectories_not_claimed_feasible": 9,
            "backward_obstructions": back_rejected, "forward_obstructions": forward_rejected,
            "moment_exponent_interval": "0<s<1", "local_minimum_invoice": {"H1": 10},
            "attainment": "the exact retained local tape", "first_later_protected_cache_copy": first_later,
            "protected_cache_copies": protected_copies, "later_zero_retags": zero_retags,
            "controls": controls,
            "scope": "Fixed eight arbitrary fields and fixed boundary frames; arbitrary scalar ADD/scale factorizations, arbitrary order, and all strictly nested intermediate subspaces; no extra fields, warps, erasure, zero-retags, changed boundary interfaces, or whole-word impossibility claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write-result", action="store_true", help="regenerate the package-local RESULT.json")
    args = parser.parse_args()
    report = run(args.repo.resolve())
    serialized = json.dumps(report, sort_keys=True, indent=2) + "\n"
    expected = Path(__file__).with_name("RESULT.json")
    if args.write_result:
        expected.write_text(serialized, encoding="utf-8")
    else:
        need(json.loads(expected.read_text(encoding="utf-8")) == json.loads(serialized),
             "recomputed certificate differs from committed RESULT.json")
    print(report["status"] + " minimum=10H1 rejected_saving_paths=7/7 controls=" + str(len(report["controls"])))


if __name__ == "__main__":
    main()
