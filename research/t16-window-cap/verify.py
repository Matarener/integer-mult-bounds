#!/usr/bin/env python3
"""Exact temporal realization of two pooled T16 integer inventories.

Standard library only. No optimizer or predecessor checker enters acceptance.
The output is a time/width relaxation, not a legal physical owner map.
"""

import argparse
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import NamedTuple

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
PREFIX = "research/complex-t16-rare-pattern-exchanges/data/"
WIDTHS = (4, 5, 7, 8, 9)
INVENTORY = (56, 32, 30, 122, 240)
EXPECTED = {"old": {1: 2431, 17: 1, 48: 4887},
            "new": {1: 2429, 5: 1, 14: 1, 48: 4887}}


class Group(NamedTuple):
    capacity: int
    times: tuple
    keys: tuple


class Model(NamedTuple):
    helpers: tuple
    groups: tuple
    windows: dict


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    need(type(value) is int and low <= value <= high, "integer domain")
    return value


def read_json(path):
    need(path.stat().st_size <= 8_000_000, "JSON size bound")
    return json.loads(path.read_bytes())


def load_sources(root=ROOT):
    pins = read_json(PACKAGE / "SOURCES.json")
    need(len(pins["files"]) <= 10, "source inventory bound")
    decoded = {}
    for pin in pins["files"]:
        if pin["usage"] == "input":
            path = root / pin["path"]
            need(path.stat().st_size <= 8_000_000, "source size bound")
            data = path.read_bytes()
            need(hashlib.sha256(data).hexdigest() == pin["sha256"],
                 "source bytes: " + pin["path"])
            decoded[pin["path"]] = json.loads(data)
    manifest = decoded["research/community-frontier1094-audit/SELECTED-SOURCE.json"]
    for name in ("PLAN.json", "SPEC.json"):
        path = PREFIX + name
        need(hashlib.sha256((root / path).read_bytes()).hexdigest()
             == manifest["files"][path], "selected source binding")
    spec = decoded[PREFIX + "SPEC.json"]
    need(hashlib.sha256((root / (PREFIX + "PLAN.json")).read_bytes()).hexdigest()
         == spec["data"]["plan_sha256"], "SPEC plan binding")
    return decoded[PREFIX + "PLAN.json"], spec


def source_model(plan, spec):
    need((plan["T"], plan["M"], plan["L"], plan["live"]) == (16, 73, 9, 14336),
         "selected template")
    need(len(plan["provider_registry"]["gauge44"]["ports"]) == 112, "port stock")
    need({int(w): n for w, n in spec["providers"]["gauge44"]["inventory"].items()}
         == dict(zip(WIDTHS, INVENTORY)), "provider inventory")
    order = plan["order"]
    need(len(order) == 144, "call count")
    calls = [tuple(integer(x, 0, 15) for x in call) for call in order]
    need(set(calls) == {(s, r) for s in range(9) for r in range(16)}, "call set")
    need(len(plan["per_call_widths"]) == 144, "width list count")
    widths = {(r["stage"], r["replica"]): r["widths"] for r in plan["per_call_widths"]}
    need(set(widths) == set(calls), "width call set")
    helpers = []
    for call in calls:
        values = widths[call]
        need(len(values) == 480 and all(type(w) is int for w in values), "width domain")
        need(Counter(values) == dict(zip(WIDTHS, INVENTORY)), "per-call inventory")
        helpers.append(tuple(values))
    need(len(plan["windows"]) == 288, "window count")
    grouped, windows = defaultdict(list), {}
    for key, value in plan["windows"].items():
        owner, child = (int(x) for x in key.split(","))
        need(key == f"{owner},{child}" and 0 <= owner < 16 and 0 <= child < 18,
             "window key")
        capacity, times = value
        need(type(capacity) is int and capacity in (8, 16, 32, 48), "capacity")
        need(1 <= len(times) <= 144, "window size")
        times = tuple(integer(t, 0, 143) for t in times)
        need(tuple(sorted(set(times))) == times, "ordered unique window")
        windows[owner, child] = (capacity, frozenset(times))
        grouped[capacity, times].append((owner, child))
    groups = tuple(Group(c, t, tuple(sorted(keys))) for (c, t), keys in sorted(grouped.items()))
    need(len(groups) == 144 and all(len(g.keys) == 2 for g in groups), "group inventory")
    return Model(tuple(helpers), groups, windows)


def check_profile(profile, model, expected):
    patterns, allocation, flow = (profile[k] for k in ("patterns", "allocation", "flow"))
    need(1 <= len(patterns) <= 12, "pattern count")
    residuals = []
    for capacity, counts, multiplicity in patterns:
        need(type(capacity) is int and capacity in (8, 16, 32, 48), "pattern capacity")
        need(len(counts) == 5, "pattern width dimension")
        counts = [integer(n, 0, 12) for n in counts]
        integer(multiplicity, 1, 32256)
        residuals.append(capacity - sum(w * n for w, n in zip(WIDTHS, counts)))
        need(residuals[-1] >= 0, "overfull pattern")
    need(len(allocation) <= 1728 and len(flow) <= 30000, "certificate row bound")
    pattern_totals, bin_totals, supplies, idle = Counter(), Counter(), Counter(), Counter()
    seen = set()
    for group, pattern, count in allocation:
        integer(group, 0, 143)
        integer(pattern, 0, len(patterns) - 1)
        integer(count, 1, 224)
        need((group, pattern) not in seen, "duplicate allocation")
        seen.add((group, pattern))
        cap, widths, _ = patterns[pattern]
        need(cap == model.groups[group].capacity, "allocation capacity")
        pattern_totals[pattern] += count
        bin_totals[group] += count
        for k, n in enumerate(widths):
            supplies[group, k] += n * count
        if residuals[pattern]:
            idle[residuals[pattern]] += count
    need([pattern_totals[j] for j in range(len(patterns))] == [r[2] for r in patterns],
         "global pattern inventory")
    need(all(bin_totals[g] == 224 for g in range(144)), "group bin inventory")
    demands, used, seen = Counter(), Counter(), set()
    for group, time, k, count in flow:
        integer(group, 0, 143)
        integer(time, 0, 143)
        integer(k, 0, 4)
        integer(count, 1, 240)
        need((group, time, k) not in seen, "duplicate flow")
        seen.add((group, time, k))
        need(time in model.groups[group].times, "flow outside window")
        demands[time, k] += count
        used[group, k] += count
    need(used == +supplies, "group width balance")
    need(all(demands[t, k] == INVENTORY[k] for t in range(144) for k in range(5)),
         "per-call demand")
    need(dict(idle) == expected, "attaining idle profile")
    return dict(idle)


def expand(profile, model):
    """Match equal-width tokens. Every bin of a group has the same allowed times."""
    available = {(t, k): deque(h for h, w in enumerate(values) if w == width)
                 for t, values in enumerate(model.helpers) for k, width in enumerate(WIDTHS)}
    tokens = defaultdict(deque)
    for g, t, k, n in sorted(profile["flow"]):
        for _ in range(n):
            tokens[g, k].append((t, available[t, k].popleft()))
    rows = []
    bins_used = Counter()
    for g, j, n in sorted(profile["allocation"]):
        group = model.groups[g]
        for _ in range(n):
            owner, child = group.keys[bins_used[g] // 112]
            port = bins_used[g] % 112
            bins_used[g] += 1
            offset = 0
            for k, count in enumerate(profile["patterns"][j][1]):
                for _ in range(count):
                    time, helper = tokens[g, k].popleft()
                    rows.append((time, helper, owner, child, port, offset, WIDTHS[k]))
                    offset += WIDTHS[k]
    need(all(not q for q in available.values()) and all(not q for q in tokens.values()),
         "token exhaustion")
    return sorted(rows)


def check_rows(rows, model):
    """Check the literal rows independently of the aggregate flow equations."""
    need(len(rows) == 69120, "literal helper count")
    seen, bins = set(), defaultdict(list)
    for time, helper, owner, child, port, offset, width in rows:
        need(type(time) is int and 0 <= time < 144, "literal time")
        need(type(helper) is int and 0 <= helper < 480, "literal helper")
        need((time, helper) not in seen, "duplicate literal helper")
        seen.add((time, helper))
        need(width == model.helpers[time][helper], "literal width")
        need((owner, child) in model.windows, "literal owner")
        need(time in model.windows[owner, child][1], "literal window")
        need(type(port) is int and 0 <= port < 112, "literal port")
        need(type(offset) is int and offset >= 0, "literal offset")
        bins[owner, child, port].append((offset, width))
    idle = Counter()
    for (owner, child), (capacity, _) in model.windows.items():
        for port in range(112):
            used = 0
            for offset, width in sorted(bins[owner, child, port]):
                need(offset == used, "literal overlap or prefix gap")
                used += width
            need(used <= capacity, "literal overfull bin")
            if used < capacity:
                idle[capacity - used] += 1
    return dict(sorted(idle.items()))


def verify():
    plan, spec = load_sources()
    model = source_model(plan, spec)
    certificate = read_json(PACKAGE / "CERTIFICATE.json")
    need(certificate["schema_version"] == 1 and set(certificate["profiles"]) == set(EXPECTED),
         "certificate schema")
    results = {}
    for name, expected in EXPECTED.items():
        profile = certificate["profiles"][name]
        idle = check_profile(profile, model, expected)
        rows = expand(profile, model)
        need(check_rows(rows, model) == idle, "aggregate/literal reconciliation")
        digest = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
        results[name] = {"idle": {str(r): n for r, n in sorted(idle.items())},
                         "helpers": len(rows), "bins": 32256, "assignment_sha256": digest,
                         "allocation_rows": len(profile["allocation"]), "flow_rows": len(profile["flow"])}
    return {"schema_version": 1, "calls": 144, "source_windows": 288, "window_groups": 144,
            "ports_per_window": 112, "profiles": results,
            "scope": "Temporal width/capacity relaxation only; no family/pair or physical admission."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate this package's RESULT.json")
    args = parser.parse_args()
    result = verify()
    if args.write:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == read_json(PACKAGE / "RESULT.json"), "complete receipt equality")
    print("PASS_T16_TEMPORAL_ATTAINMENT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
