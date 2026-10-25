"""Replay a fixed six-width pattern-flow certificate; no solver dependency."""
import argparse
from collections import Counter, defaultdict, deque
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
WIDTHS = (4, 5, 6, 7, 8, 9)
INVENTORY = (26, 2, 18, 50, 99, 213)
AUDITOR = "research/t16-owner-audit-seed67/verify.py"
TEMPLATE = "research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz"
PHASES = "research/community-k492-audit/pr622/replay/baseline558/complex-global/base/work/complex-nine-native/DATA-PHASES.json"
FRAME = "research/rank7-joint-endframes/vendor/preload_move.py"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    need(type(value) is int and low <= value <= high, "integer domain")  # noqa: E721 - reject bool
    return value


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read(path):
    data = Path(path).read_bytes()
    need(len(data) <= 32 * 1024 * 1024, "input byte budget")
    if str(path).endswith(".gz"):
        data = gzip.decompress(data)
    need(len(data) <= 32 * 1024 * 1024, "decoded byte budget")
    return json.loads(data, object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def authenticate(root, package=HERE):
    for manifest, base in [("INPUT-PINS.json", root), ("LOCAL-PINS.json", package)]:
        for relative, digest in read(package / manifest).items():
            path = (base / relative).resolve()
            need(path.is_relative_to(base.resolve()), "input path escape")
            need(
                hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                "source hash: " + relative,
            )


def sources(root, package=HERE):
    authenticate(root, package)
    frames = module("rank7_frames", root / FRAME)
    auditor = module("rank7_owners", root / AUDITOR)
    geometry = auditor.geometry(read(root / TEMPLATE), read(root / PHASES))
    words = [
        read(root / f"research/coupled-carrier-cap740/words/{name}.json.gz")
        for name in ("base", "extra")
    ]
    inventories = []
    for word in words:
        profile, inventory = frames.frame_report(word)
        widths = [
            len(
                frames.basis(
                    word["helper_final"].get(str(r), [1 << i for i in range(9)])
                )
            )
            - len(frames.basis(word["start_extra"].get(str(r), [])))
            for r in range(224, 704)
            if r not in word["removed"]
        ]
        need(Counter(widths) == dict(zip(WIDTHS, INVENTORY)), "actual helper inventory")
        need(profile == word["report"]["local_profile"], "actual local profile")
        need(inventory == word["report"]["width_inventory"], "actual width report")
        inventories.append((widths, {int(k): v for k, v in profile.items()}))
    need(inventories[0] == inventories[1], "provider interface difference")
    return auditor, geometry, inventories[0][0], Counter(inventories[0][1])


def reconstruct(root, package=HERE, certificate=None):
    auditor, geometry, widths, local = sources(root, package)
    plan = read(package / "PLAN-3413.json")
    order = [tuple(x) for x in plan["order"]]
    need(
        len(order) == 144
        and set(order) == {(s, r) for s in range(9) for r in range(16)},
        "call inventory",
    )
    spans, positions = auditor.windows(geometry, order)
    grouped = defaultdict(list)
    for (owner, child), (lo, hi) in spans.items():
        times = tuple(t for t, call in enumerate(order) if lo < positions[call] < hi)
        need(
            plan["windows"][f"{owner},{child}"]
            == [geometry["rank"][child], list(times)],
            "actual chronology window",
        )
        grouped[geometry["rank"][child], times].append((owner, child))
    groups = [
        (capacity, times, tuple(sorted(keys)))
        for (capacity, times), keys in sorted(grouped.items())
    ]
    need(
        len(groups) == 144 and all(len(keys) == 2 for _, _, keys in groups),
        "window groups",
    )
    # Distinct eligible children at one call cannot alias one physical family.
    for t in range(144):
        eligible = [
            (o, geometry["place"][c])
            for _, times, keys in groups
            if t in times
            for o, c in keys
        ]
        need(len(eligible) == len(set(eligible)), "eligible physical-family alias")
    cert = read(package / "CERTIFICATE.json") if certificate is None else certificate
    need(cert["schema"] == "t16-rank7-pattern-flow-v1", "certificate schema")
    patterns, allocation, flow = (cert[k] for k in ("patterns", "allocation", "flow"))
    need(
        1 <= len(patterns) <= 100 and len(allocation) <= 2000 and len(flow) <= 30000,
        "certificate budget",
    )
    for capacity, counts in patterns:
        need(capacity in (8, 16, 32, 48) and type(capacity) is int, "pattern capacity")  # noqa: E721 - reject bool
        need(len(counts) == 6, "pattern dimension")
        for n in counts:
            integer(n, 0, 12)
        need(sum(w * n for w, n in zip(WIDTHS, counts)) <= capacity, "overfull pattern")
    bins, occupied = Counter(), set()
    for g, p, count in allocation:
        integer(g, 0, 143)
        integer(p, 0, len(patterns) - 1)
        integer(count, 1, 224)
        need((g, p) not in occupied, "duplicate pattern allocation")
        occupied.add((g, p))
        need(groups[g][0] == patterns[p][0], "allocation capacity")
        bins[g] += count
    need(all(bins[g] == 224 for g in range(144)), "group bin inventory")
    demands, supplies, degrees, seen = Counter(), Counter(), Counter(), set()
    by_allocation = defaultdict(lambda: defaultdict(lambda: [0] * 6))
    for a, t, k, n in flow:
        integer(a, 0, len(allocation) - 1)
        integer(t, 0, 143)
        integer(k, 0, 5)
        integer(n, 1, 224)
        need((a, t, k) not in seen, "duplicate flow")
        seen.add((a, t, k))
        g, p, count = allocation[a]
        need(t in groups[g][1], "flow outside window")
        demands[t, k] += n
        supplies[a, k] += n
        degrees[a, t] += n
        need(degrees[a, t] <= count, "one call exceeds pattern bin count")
        by_allocation[a][t][k] = n
    need(
        all(demands[t, k] == INVENTORY[k] for t in range(144) for k in range(6)),
        "per-call width demand",
    )
    need(
        all(
            supplies[a, k] == n * patterns[p][1][k]
            for a, (g, p, n) in enumerate(allocation)
            for k in range(6)
        ),
        "pattern width supply",
    )
    coloring = module("rank7_coloring", package / "coloring.py")
    available = {
        (t, k): deque(h for h, width in enumerate(widths) if width == w)
        for t in range(144)
        for k, w in enumerate(WIDTHS)
    }
    rows, used = [], Counter()
    for a, (g, p, count) in enumerate(allocation):
        for values in coloring.colour_pattern(by_allocation[a], patterns[p][1], count):
            owner, child = groups[g][2][used[g] // 112]
            port = used[g] % 112
            used[g] += 1
            offset = 0
            pair, side = geometry["place"][child]
            for t, k in values:
                need(bool(available[t, k]), "literal helper shortage")
                stage, replica = order[t]
                rows.append(
                    dict(
                        time=t,
                        stage=stage,
                        replica=replica,
                        helper=available[t, k].popleft(),
                        owner_replica=owner,
                        child=child,
                        port=port,
                        offset=offset,
                        width=WIDTHS[k],
                        copy=owner * 112 + port,
                        family=owner * 896 + (2 * pair + side) * 112 + port,
                    )
                )
                offset += WIDTHS[k]
    need(all(not queue for queue in available.values()), "unassigned helper")
    rows.sort(key=lambda r: (r["time"], r["helper"]))
    used_width = Counter()
    for row in rows:
        used_width[row["owner_replica"], row["child"], row["port"]] += row["width"]
    idle = Counter(
        geometry["rank"][c] - used_width[o, c, p] for o, c in spans for p in range(112)
    )
    idle.pop(0, None)
    audit = auditor.audit(geometry, widths, local, rows, plan, idle, 16)
    expected = read(package / "EXPECTED.json")
    need(
        hashlib.sha256(canonical(rows)).hexdigest()
        == expected["owner_canonical_sha256"],
        "literal owner digest",
    )
    for key in ("idle", "profile"):
        need(
            audit[key] == {int(k): v for k, v in expected[key].items()},
            "expected " + key,
        )
    for key in ("rank_mass", "deficit", "roles", "calls"):
        need(audit[key] == expected[key], "expected " + key)
    return rows, plan, audit


def modern_inputs(root, rows, plan):
    """Bind reconstructed owners to the actual two-provider rank-seven interface."""
    authenticate(root)
    prefix = "research/rank7-joint-endframes/allocation/vendor/"
    engine = module("rank7_modern_owner", root / (prefix + "independent_owners.py"))
    providers = read(
        root / "research/coupled-carrier-cap740/vendor/PR3133-PROVIDERS.json"
    )
    for provider in providers.values():
        provider["actual_paid_profile"] = {
            int(k): v for k, v in provider["actual_paid_profile"].items()
        }
    sourceplan = read(root / (prefix + "PLAN.json.gz"))
    template = read(root / (prefix + "TEMPLATE.json.gz"))
    order = plan["order"]
    dispatch = {
        tuple(call): ("extra" if index == 0 else "gauge44")
        for index, call in enumerate(order)
    }
    need(
        order[0] == [0, 0] and set(dispatch.values()) == {"extra", "gauge44"},
        "explicit two-provider rule",
    )
    columns = ["time", "helper", "owner_replica", "child", "port", "offset"]
    fill = {
        "columns": columns,
        "dispatch_overrides": [],
        "rows": [[row[k] for k in columns] for row in rows],
    }
    for row in rows:
        need(
            order[row["time"]] == [row["stage"], row["replica"]],
            "semantic call identity",
        )
        provider = providers[dispatch[row["stage"], row["replica"]]]
        need(
            row["width"] == provider["widths"][row["helper"]],
            "actual provider width order",
        )
    result, _, _ = engine.check(
        16, order, fill, dispatch, None, sourceplan, template, providers
    )
    opposite = {
        call: "gauge44" if name == "extra" else "extra"
        for call, name in dispatch.items()
    }
    other, _, _ = engine.check(
        16, order, fill, opposite, None, sourceplan, template, providers
    )
    need(result["profile"] == other["profile"], "both-provider finite profile")
    expected = read(HERE / "EXPECTED.json")
    need(
        {int(k): v for k, v in result["profile"].items()}
        == {int(k): v for k, v in expected["profile"].items()},
        "modern paid profile",
    )
    return fill, order, [[s, r, dispatch[s, r]] for s, r in order], result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=HERE / "source-inputs", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows, plan, audit = reconstruct(args.root.resolve())
    fill, order, dispatch, modern = modern_inputs(args.root.resolve(), rows, plan)
    if args.output is None:
        print("PASS_T16_RANK7_PATTERN_RECONSTRUCTION", audit["roles"])
        return
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "OWNERS.json.gz").write_bytes(
        gzip.compress(canonical(rows), mtime=0)
    )
    (args.output / "PLAN-GEOMETRY.json").write_bytes(canonical(plan))
    (args.output / "OWNER-AUDIT.json").write_bytes(canonical(audit))
    (args.output / "FILL.json.gz").write_bytes(gzip.compress(canonical(fill), mtime=0))
    (args.output / "ORDER.json").write_bytes(canonical(order))
    (args.output / "DISPATCH.json").write_bytes(canonical(dispatch))
    (args.output / "MODERN-OWNER-AUDIT.json").write_bytes(canonical(modern))
    print("PASS_T16_RANK7_PATTERN_RECONSTRUCTION", audit["roles"])


if __name__ == "__main__":
    main()
