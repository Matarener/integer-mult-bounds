"""Separate event-level and explicit-set check. Imports no project Python code."""

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEMPLATE = (
    "research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/"
    "vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz"
)
PHASES = (
    "research/community-k492-audit/pr622/replay/baseline558/complex-global/"
    "base/work/complex-nine-native/DATA-PHASES.json"
)
OWNER_HASH = "8e5940efdf9026ec41200e6dc7132e3736f2d63f84d5e4e24d82d8db03967f4e"
PLAN_HASH = "782e237299af262c1564e75138809a1d75f2f4dea99f1eca374895ef4f4bd6d3"
LIMIT = 32 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def document(path):
    require(path.is_file() and path.stat().st_size <= LIMIT, "input byte limit")
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as stream:
            raw = stream.read(LIMIT + 1)
    else:
        raw = path.read_bytes()
    require(len(raw) <= LIMIT, "expanded input byte limit")
    return json.loads(raw)


def source_data():
    sources = document(HERE / "SOURCES.json")["files"]
    require(len(sources) <= 100, "source count")
    for row in sources:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            require(path.stat().st_size <= LIMIT, "source byte bound")
            require(
                hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "changed selected source",
            )
    rows = document(HERE / "OWNERS.json.gz")
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    require(hashlib.sha256(raw).hexdigest() == OWNER_HASH, "exact PR3388 owners")
    require(len(rows) == 69120, "role count")
    plan = document(HERE / "PLAN.json")
    encoded_plan = json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
    require(hashlib.sha256(encoded_plan).hexdigest() == PLAN_HASH, "exact PR3388 plan")
    return rows, plan


def events(order):
    template = document(ROOT / TEMPLATE)
    phases = document(ROOT / PHASES)
    capacities = {}
    for recipe in phases["recipes"]:
        children = recipe["idle_children"]
        items = enumerate(children) if isinstance(children, list) else children.items()
        for child, info in items:
            rank = len(info["orthogonal_axes"])
            require(capacities.setdefault(int(child), rank) == rank, "uniform rank")
    blocks = defaultdict(list)
    stage = None
    for event in template["execution_schedule"][:30]:
        if event["kind"] == "local_cover_sweep":
            stage = event["stage"]
        require(stage is not None, "source event before sweep")
        blocks[stage].append(event)
    active = {
        item["stage"]: item["pair"]
        for item in template["recipe"]
        if item["kind"] == "local"
    }
    require(len(order) == 144 and len({tuple(x) for x in order}) == 144, "call order")
    last, spans, positions, child_pairs = {}, {}, {}, {}
    cursor = 0
    for stage, replica in order:
        for event in blocks[stage]:
            kind = event["kind"]
            if kind == "local_cover_sweep":
                positions[stage, replica] = cursor
                last[replica, active[stage]] = cursor
            elif kind == "bridge":
                for pair in (event["src"], event["dst"]):
                    last[replica, pair] = cursor
            elif kind == "idle_cover_sweep":
                for child in event["child_indices"]:
                    child_pairs[child] = event["pair"]
                    spans[replica, child] = (
                        last.get((replica, event["pair"]), -1),
                        cursor,
                    )
            cursor += 1
    return capacities, active, spans, positions, child_pairs


def independent_closure(bundle_times, windows, start):
    require(len(bundle_times) <= 7168, "finite rank16 bin domain")
    pending = [windows[start]]
    visited_windows = set()
    for _step in range(len(windows) + 1):
        if not pending:
            reached = {start} | {
                key
                for key, times in bundle_times.items()
                if any(times <= window for window in visited_windows)
            }
            return reached, visited_windows
        window = pending.pop()
        if window in visited_windows:
            continue
        visited_windows.add(window)
        for key, times in bundle_times.items():
            target = windows[key]
            if (
                times <= window
                and target not in visited_windows
                and target not in pending
            ):
                pending.append(target)
    raise ValueError("independent closure bound exhausted")


def bin_inventory(rows, plan):
    capacity, active, spans, positions, pairs = events(plan["order"])
    bins = defaultdict(list)
    for row in rows:
        require(
            plan["order"][row["time"]] == [row["stage"], row["replica"]], "role time"
        )
        bins[row["owner_replica"], row["child"], row["port"]].append(row)
    windows, rank16, full48, empty16 = {}, {}, {}, []
    for owner in range(16):
        for child, cap in capacity.items():
            if cap == 0:
                continue
            low, high = spans[owner, child]
            permitted = frozenset(
                t
                for t, call in enumerate(plan["order"])
                if low < positions[tuple(call)] < high
                and not (call[1] == owner and active[call[0]] == pairs[child])
            )
            for port in range(112):
                key = owner, child, port
                members = bins[key]
                used = sum(row["width"] for row in members)
                require(used <= cap, "physical capacity")
                if cap == 16:
                    windows[key] = permitted
                    if members:
                        rank16[key] = frozenset(row["time"] for row in members)
                    else:
                        empty16.append(key)
                if cap == used == 48:
                    full48[key] = members
    require(len(empty16) == 1, "one empty16 buffer")
    return rank16, windows, empty16[0], full48


def run():
    rows, plan = source_data()
    rank16, windows, start, full48 = bin_inventory(rows, plan)
    reached, window_classes = independent_closure(rank16, windows, start)
    counts = Counter(
        max(
            sum(row["width"] for row in members if row["time"] in window)
            for window in window_classes
        )
        for members in full48.values()
    )
    expected = document(HERE / "RESULT.json")
    require(
        len(reached) == expected["reachable_rank16_bins"] == 896, "reachable bin count"
    )
    require(len(window_classes) == 4, "eligibility class count")
    require(
        sorted({key[:2] for key in reached})
        == [tuple(key) for key in expected["reachable_owner_children"]],
        "reachable types",
    )
    require(
        dict(counts)
        == {int(k): v for k, v in expected["available_width_histogram"].items()}
        == {0: 2185, 4: 12, 9: 91},
        "full48 width histogram",
    )
    require(max(counts) == 9 < 16 and len(full48) == 2288, "split obstruction")
    print("PASS_INDEPENDENT_T16_TRANSPORT_CUT reachable=896 max_width=9 full48=2288")


if __name__ == "__main__":
    run()
