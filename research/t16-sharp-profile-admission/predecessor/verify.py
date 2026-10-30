"""Reconstruct distinct-call T16 owners from exact pattern flows."""

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PREFIX = "research/complex-t16-rare-pattern-exchanges/data/"
WIDTHS = (4, 5, 7, 8, 9)
INVENTORY = (56, 32, 30, 122, 240)
EXPECTED = {"old": {1: 2431, 17: 1, 48: 4887}, "new": {1: 2429, 5: 1, 14: 1, 48: 4887}}


class Group(NamedTuple):
    capacity: int
    times: tuple
    keys: tuple


class Model(NamedTuple):
    calls: tuple
    widths: tuple
    groups: tuple
    windows: dict
    pairs: tuple
    sides: tuple


def need(ok, message):
    if not ok:
        raise ValueError(message)


def integer(value, low, high):
    need(type(value) is int and low <= value <= high, "integer domain")
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    need(not path.is_symlink() and path.is_file(), "regular JSON input")
    need(path.stat().st_size <= 8_000_000, "JSON size bound")
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def sources(root=ROOT):
    pins = read_json(HERE / "SOURCES.json")
    need(len(pins["files"]) <= 10, "source inventory bound")
    decoded = {}
    for pin in pins["files"]:
        if pin["usage"] != "input":
            continue
        path = root / pin["path"]
        need(not any(p.is_symlink() for p in (path, *path.parents)), "linked source")
        decoded[pin["path"]] = read_json(path)
        need(
            hashlib.sha256(path.read_bytes()).hexdigest() == pin["sha256"],
            "source bytes: " + pin["path"],
        )
    manifest = decoded["research/community-frontier1094-audit/SELECTED-SOURCE.json"]
    for name in ("PLAN.json", "SPEC.json"):
        path = PREFIX + name
        need(
            hashlib.sha256((root / path).read_bytes()).hexdigest()
            == manifest["files"][path],
            "selected source binding",
        )
    spec = decoded[PREFIX + "SPEC.json"]
    need(
        hashlib.sha256((root / (PREFIX + "PLAN.json")).read_bytes()).hexdigest()
        == spec["data"]["plan_sha256"],
        "SPEC plan binding",
    )
    return decoded[PREFIX + "PLAN.json"], spec


def source_model(plan, spec):
    need(
        (plan["T"], plan["M"], plan["L"], plan["live"]) == (16, 73, 9, 14336),
        "selected template",
    )
    ports = plan["provider_registry"]["gauge44"]["ports"]
    need(len(ports) == len(set(ports)) == 112, "port stock")
    calls = tuple(tuple(integer(x, 0, 15) for x in call) for call in plan["order"])
    need(
        len(calls) == 144
        and set(calls) == {(s, r) for s in range(9) for r in range(16)},
        "call set",
    )
    entries = plan["per_call_widths"]
    need(len(entries) == 144, "width list count")
    bycall = {(r["stage"], r["replica"]): tuple(r["widths"]) for r in entries}
    need(set(bycall) == set(calls), "width call set")
    widths = tuple(bycall[c] for c in calls)
    for values in widths:
        need(len(values) == 480 and all(type(w) is int for w in values), "width domain")
        need(Counter(values) == dict(zip(WIDTHS, INVENTORY)), "per-call inventory")
    need(
        {int(w): n for w, n in spec["providers"]["gauge44"]["inventory"].items()}
        == dict(zip(WIDTHS, INVENTORY)),
        "SPEC inventory",
    )
    need(spec["call_order"] == plan["order"], "SPEC chronology")
    pairs = tuple(integer(plan["pairs"][str(c)], 0, 3) for c in range(18))
    sides = tuple(integer(plan["sides"][str(c)], 0, 1) for c in range(18))
    grouped, windows = defaultdict(list), {}
    need(len(plan["windows"]) == 288, "window count")
    for key, (capacity, times) in plan["windows"].items():
        owner, child = map(int, key.split(","))
        need(
            key == f"{owner},{child}" and 0 <= owner < 16 and 0 <= child < 18,
            "window key",
        )
        need(type(capacity) is int and capacity in (8, 16, 32, 48), "capacity")
        need(1 <= len(times) <= 144, "window size")
        times = tuple(integer(t, 0, 143) for t in times)
        need(tuple(sorted(set(times))) == times, "ordered unique window")
        windows[owner, child] = (capacity, frozenset(times))
        grouped[capacity, times].append((owner, child))
    groups = tuple(
        Group(c, t, tuple(sorted(keys))) for (c, t), keys in sorted(grouped.items())
    )
    need(
        len(groups) == 144 and all(len(g.keys) == 2 for g in groups), "group inventory"
    )
    return Model(calls, widths, groups, windows, pairs, sides)


def family(model, owner, child, port):
    return owner * 896 + (2 * model.pairs[child] + model.sides[child]) * 112 + port


def check_geometry(model):
    for t, (stage, replica) in enumerate(model.calls):
        eligible = [
            family(model, owner, child, 0)
            for (owner, child), (_, times) in model.windows.items()
            if t in times
        ]
        need(len(eligible) == len(set(eligible)), "two eligible children on one family")
        active = max(0, (stage - 1) // 2)
        need(
            all(
                owner != replica or model.pairs[child] != active
                for (owner, child), (_, times) in model.windows.items()
                if t in times
            ),
            "active data pair eligible",
        )


def pattern_inventory(cert, model):
    patterns, allocation = (cert[k] for k in ("patterns", "allocation"))
    need(1 <= len(patterns) <= 12 and 1 <= len(allocation) <= 1728, "inventory bound")
    residuals = []
    for capacity, counts, multiplicity in patterns:
        need(type(capacity) is int and capacity in (8, 16, 32, 48), "pattern capacity")
        need(len(counts) == 5, "pattern dimension")
        for n in counts:
            integer(n, 0, 12)
        integer(multiplicity, 1, 32256)
        residuals.append(capacity - sum(w * n for w, n in zip(WIDTHS, counts)))
        need(residuals[-1] >= 0, "overfull pattern")
    totals, bins, idle, seen = Counter(), Counter(), Counter(), set()
    for g, p, n in allocation:
        integer(g, 0, 143)
        integer(p, 0, len(patterns) - 1)
        integer(n, 1, 224)
        need((g, p) not in seen, "duplicate allocation")
        seen.add((g, p))
        need(model.groups[g].capacity == patterns[p][0], "allocation capacity")
        totals[p] += n
        bins[g] += n
        if residuals[p]:
            idle[residuals[p]] += n
    need(all(bins[g] == 224 for g in range(144)), "all bins allocated")
    need(
        [totals[p] for p in range(len(patterns))] == [p[2] for p in patterns],
        "pattern inventory",
    )
    return dict(idle)


def check_certificate(cert, model, expected):
    need(pattern_inventory(cert, model) == expected, "attaining idle profile")
    patterns, allocation, flow = (cert[k] for k in ("patterns", "allocation", "flow"))
    need(len(flow) <= 30000, "flow bound")
    demands, supplies, degrees, seen = Counter(), Counter(), Counter(), set()
    for a, t, k, n in flow:
        integer(a, 0, len(allocation) - 1)
        integer(t, 0, 143)
        integer(k, 0, 4)
        integer(n, 1, 240)
        need((a, t, k) not in seen, "duplicate flow")
        seen.add((a, t, k))
        g, _p, count = allocation[a]
        need(t in model.groups[g].times, "flow outside window")
        demands[t, k] += n
        supplies[a, k] += n
        degrees[a, t] += n
        need(degrees[a, t] <= count, "one call exceeds pattern bin count")
    need(
        all(demands[t, k] == INVENTORY[k] for t in range(144) for k in range(5)),
        "per-call demand",
    )
    need(
        all(
            supplies[a, k] == n * patterns[p][1][k]
            for a, (_, p, n) in enumerate(allocation)
            for k in range(5)
        ),
        "pattern width balance",
    )


def regular_graph(demands, counts, multiplicity):
    """Make the time-to-slot multigraph regular using dummy slots and times."""
    times = sorted(demands)
    slots = [k for k, n in enumerate(counts) for _ in range(n)]
    size = max(len(times), len(slots))
    need(size <= 144, "graph vertex bound")
    matrix = [[0] * size for _ in range(size)]
    for k in range(5):
        columns = [j for j, width in enumerate(slots) if width == k]
        remaining = {j: multiplicity for j in columns}
        for i, t in enumerate(times):
            count = demands[t][k]
            for j in columns:
                amount = min(count, remaining[j])
                matrix[i][j] += amount
                remaining[j] -= amount
                count -= amount
            need(count == 0, "slot supply exhausted")
        need(not any(remaining.values()), "unfilled real slot")
    row_defect = [multiplicity - sum(row) for row in matrix]
    col_defect = [multiplicity - sum(row[j] for row in matrix) for j in range(size)]
    for i in range(size):
        for j in range(len(slots), size):
            amount = min(row_defect[i], col_defect[j])
            matrix[i][j] += amount
            row_defect[i] -= amount
            col_defect[j] -= amount
    need(not any(row_defect) and not any(col_defect), "regularization")
    return matrix, times, slots


def perfect_matching(matrix):
    """Bounded alternating-path matching on positive support, without recursion."""
    size = len(matrix)
    left, right = [-1] * size, [-1] * size
    for start in range(size):
        queue, previous, endpoint = deque([start]), {}, None
        for _ in range(size):
            if not queue or endpoint is not None:
                break
            i = queue.popleft()
            for j in range(size):
                if matrix[i][j] <= 0 or j in previous:
                    continue
                previous[j] = i
                if right[j] == -1:
                    endpoint = j
                    break
                queue.append(right[j])
        need(endpoint is not None, "regular graph has no perfect matching")
        for _ in range(size):
            i = previous[endpoint]
            old = left[i]
            left[i], right[endpoint] = endpoint, i
            if old == -1:
                break
            endpoint = old
        else:
            raise ValueError("alternating path exceeded vertex bound")
    return left


def colour_pattern(demands, counts, multiplicity):
    if not any(counts):
        return [[] for _ in range(multiplicity)]
    matrix, times, slots = regular_graph(demands, counts, multiplicity)
    bins = []
    for _ in range(multiplicity):
        if len(bins) == multiplicity:
            break
        match = perfect_matching(matrix)
        amount = min(matrix[i][j] for i, j in enumerate(match))
        values = sorted(
            (times[i], slots[j]) for i, j in enumerate(match) if j < len(slots)
        )
        need(len({t for t, _ in values}) == len(values), "repeated time in colour")
        bins.extend([values] * amount)
        for i, j in enumerate(match):
            matrix[i][j] -= amount
    need(
        len(bins) == multiplicity and not any(any(row) for row in matrix),
        "colour exhaustion",
    )
    return bins


def expand(cert, model):
    demands = defaultdict(lambda: defaultdict(lambda: [0] * 5))
    for a, t, k, n in cert["flow"]:
        demands[a][t][k] = n
    available = {
        (t, k): deque(h for h, w in enumerate(values) if w == width)
        for t, values in enumerate(model.widths)
        for k, width in enumerate(WIDTHS)
    }
    rows, used = [], Counter()
    for a, (g, p, n) in enumerate(cert["allocation"]):
        coloured = colour_pattern(demands[a], cert["patterns"][p][1], n)
        for values in coloured:
            owner, child = model.groups[g].keys[used[g] // 112]
            port = used[g] % 112
            used[g] += 1
            offset = 0
            for t, k in values:
                need(bool(available[t, k]), "literal helper shortage")
                rows.append(
                    (
                        t,
                        available[t, k].popleft(),
                        owner,
                        child,
                        port,
                        offset,
                        WIDTHS[k],
                    )
                )
                offset += WIDTHS[k]
    need(all(not q for q in available.values()), "unassigned helper")
    return sorted(rows)


def check_rows(rows, model):
    need(len(rows) == 69120, "literal helper count")
    seen, families, bins = set(), set(), defaultdict(list)
    for t, h, owner, child, port, offset, width in rows:
        integer(t, 0, 143)
        integer(h, 0, 479)
        integer(owner, 0, 15)
        integer(child, 0, 17)
        integer(port, 0, 111)
        integer(offset, 0, 48)
        need((t, h) not in seen, "duplicate literal helper")
        seen.add((t, h))
        need(type(width) is int and width == model.widths[t][h], "literal width")
        need((owner, child) in model.windows, "literal owner")
        need(t in model.windows[owner, child][1], "literal window")
        f = family(model, owner, child, port)
        need((t, f) not in families, "two helpers on one family in one call")
        families.add((t, f))
        stage, replica = model.calls[t]
        need(
            owner != replica or model.pairs[child] != max(0, (stage - 1) // 2),
            "literal active data pair",
        )
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


def verify(root=ROOT, certificate=None):
    model = source_model(*sources(root))
    check_geometry(model)
    cert = read_json(HERE / "CERTIFICATE.json") if certificate is None else certificate
    need(
        cert["schema_version"] == 1 and set(cert["profiles"]) == set(EXPECTED), "schema"
    )
    result = {}
    for name, expected in EXPECTED.items():
        profile = cert["profiles"][name]
        check_certificate(profile, model, expected)
        rows = expand(profile, model)
        idle = check_rows(rows, model)
        need(idle == expected, "literal profile")
        digest = hashlib.sha256(
            json.dumps(rows, separators=(",", ":")).encode()
        ).hexdigest()
        result[name] = {
            "idle": {str(r): n for r, n in idle.items()},
            "helpers": len(rows),
            "assignment_sha256": digest,
            "pattern_flow_rows": len(profile["flow"]),
        }
    return {
        "schema_version": 1,
        "calls": 144,
        "bins": 32256,
        "profiles": result,
        "one_helper_per_family_per_call": True,
        "active_data_pairs_excluded": True,
        "scope": "Finite hosting on supplied selected windows; no complete physical admission.",
    }


def export_owners(output, model, certificate):
    output = output.resolve()
    need(not output.is_relative_to(ROOT), "owner output must be outside the checkout")
    output.mkdir(parents=True, exist_ok=False)
    for name, profile in certificate["profiles"].items():
        rows = expand(profile, model)
        need(check_rows(rows, model) == EXPECTED[name], "exported owner profile")
        owners = []
        for t, h, owner, child, port, offset, width in rows:
            stage, replica = model.calls[t]
            owners.append(
                {
                    "time": t,
                    "helper": h,
                    "stage": stage,
                    "replica": replica,
                    "owner_replica": owner,
                    "child": child,
                    "port": port,
                    "offset": offset,
                    "width": width,
                    "copy": owner * 112 + port,
                    "family": family(model, owner, child, port),
                }
            )
        data = json.dumps(owners, sort_keys=True, separators=(",", ":")).encode()
        (output / f"OWNERS-{name}.json.gz").write_bytes(gzip.compress(data, mtime=0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument(
        "--owners-dir", type=Path, help="New external directory for literal owner maps"
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    certificate = read_json(args.certificate)
    result = verify(args.root, certificate)
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == read_json(HERE / "RESULT.json"), "complete receipt equality")
    if args.owners_dir is not None:
        export_owners(args.owners_dir, source_model(*sources(args.root)), certificate)
    print("PASS_T16_DISTINCT_CALL_ATTAINMENT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
