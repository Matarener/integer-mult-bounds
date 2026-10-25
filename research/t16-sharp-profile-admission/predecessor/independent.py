"""Independent sufficient-condition audit. Imports no other project code."""

import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    require(path.is_file() and not path.is_symlink(), "regular source")
    require(path.stat().st_size <= 8_000_000, "input bound")
    return json.loads(path.read_bytes())


def source():
    pins = read(HERE / "SOURCES.json")
    require(len(pins["files"]) <= 10, "source count")
    for pin in pins["files"]:
        if pin["usage"] == "input":
            p = ROOT / pin["path"]
            require(not any(x.is_symlink() for x in (p, *p.parents)), "linked input")
            read(p)
            require(
                hashlib.sha256(p.read_bytes()).hexdigest() == pin["sha256"],
                "source hash",
            )
    plan = read(ROOT / "research/complex-t16-rare-pattern-exchanges/data/PLAN.json")
    groups = {}
    for key, (cap, times) in plan["windows"].items():
        groups.setdefault((cap, tuple(times)), []).append(
            tuple(map(int, key.split(",")))
        )
    groups = [
        (cap, times, sorted(keys)) for (cap, times), keys in sorted(groups.items())
    ]
    require(
        len(groups) == 144 and all(len(keys) == 2 for _, _, keys in groups), "groups"
    )
    for t, (stage, replica) in enumerate(plan["order"]):
        families = []
        for _, times, keys in groups:
            if t not in times:
                continue
            for owner, child in keys:
                pair, side = plan["pairs"][str(child)], plan["sides"][str(child)]
                require(
                    owner != replica or pair != max(0, (stage - 1) // 2), "active pair"
                )
                families.extend((owner, pair, side, port) for port in range(112))
        require(len(families) == len(set(families)), "eligible family collision")
    widths = {
        (r["stage"], r["replica"]): Counter(r["widths"])
        for r in plan["per_call_widths"]
    }
    return groups, [widths[tuple(c)] for c in plan["order"]]


def profile(data, groups, widths, expected):
    patterns, allocations = data["patterns"], data["allocation"]
    require(len(patterns) <= 12 and len(allocations) <= 1728, "inventory limits")
    require(len(data["flow"]) <= 30000, "flow limit")
    stock, patterns_used, residuals = Counter(), Counter(), Counter()
    for group, pattern, number in allocations:
        cap, counts, _ = patterns[pattern]
        require(cap == groups[group][0] and number > 0, "capacity")
        stock[group] += number
        patterns_used[pattern] += number
        residual = cap - sum(w * n for w, n in zip((4, 5, 7, 8, 9), counts))
        require(residual >= 0, "overfull pattern")
        if residual:
            residuals[residual] += number
    require(all(stock[g] == 224 for g in range(144)), "stock")
    require(
        all(patterns_used[p] == value[2] for p, value in enumerate(patterns)),
        "patterns",
    )
    require(residuals == expected, "idle")
    seen, demand, delivered, degree = set(), Counter(), Counter(), Counter()
    for allocation, time, kind, number in data["flow"]:
        require(
            all(type(x) is int for x in (allocation, time, kind, number)), "integers"
        )
        group, _pattern, _multiplicity = allocations[allocation]
        require(0 <= kind < 5 and 0 < number <= 240, "flow domain")
        require(time in groups[group][1], "time eligibility")
        require((allocation, time, kind) not in seen, "duplicate flow")
        seen.add((allocation, time, kind))
        demand[time, (4, 5, 7, 8, 9)[kind]] += number
        delivered[allocation, kind] += number
        degree[allocation, time] += number
    require(
        all(
            demand[t, w] == counts[w]
            for t, counts in enumerate(widths)
            for w in (4, 5, 7, 8, 9)
        ),
        "literal demand",
    )
    for a, (_, p, n) in enumerate(allocations):
        require(
            all(delivered[a, k] == n * patterns[p][1][k] for k in range(5)), "slots"
        )
        require(all(degree[a, t] <= n for t in range(144)), "distinct-call degree")
    return len(data["flow"])


def main():
    groups, widths = source()
    cert = read(HERE / "CERTIFICATE.json")
    require(set(cert["profiles"]) == {"old", "new"}, "profile names")
    counts = [
        profile(cert["profiles"][name], groups, widths, expected)
        for name, expected in (
            ("old", {1: 2431, 17: 1, 48: 4887}),
            ("new", {1: 2429, 5: 1, 14: 1, 48: 4887}),
        )
    ]
    print("PASS_INDEPENDENT_PATTERN_DEGREES", counts)


if __name__ == "__main__":
    main()
