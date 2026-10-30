"""Source-bound obstruction to neutral equal-capacity T16 buffer transport.

Nick Petalas. Apache-2.0. Retained reconstruction credit is in source3388/.
"""

import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_BYTES = 32 * 1024 * 1024
OWNER_HASH = "8e5940efdf9026ec41200e6dc7132e3736f2d63f84d5e4e24d82d8db03967f4e"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    need(path.is_file() and not path.is_symlink(), "regular input file required")
    need(path.stat().st_size <= MAX_BYTES, "compressed input byte limit")
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
    else:
        raw = path.read_bytes()
    need(len(raw) <= MAX_BYTES, "input byte limit")
    return json.loads(raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Python source loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(package, root):
    retained = read(package / "RETAINED.json")
    need(
        retained["source_head"] == "684d347c0e6e578b8ab600d2e680ad6701cf7fa0",
        "PR3388 source head",
    )
    need(retained["owner_canonical_sha256"] == OWNER_HASH, "source payload pin")
    need(len(retained["files"]) == 20, "retained source inventory")
    for item in retained["files"]:
        relative = Path(item["path"])
        need(
            not relative.is_absolute() and ".." not in relative.parts,
            "retained source path",
        )
        path = package / relative
        need(
            path.is_file() and path.stat().st_size <= MAX_BYTES,
            "retained source byte limit",
        )
        need(
            hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"],
            "changed retained source: " + item["path"],
        )
    need(
        set(retained["fixtures"]) == {"OWNERS.json.gz", "PLAN.json"},
        "fixture inventory",
    )
    for name, expected in retained["fixtures"].items():
        need((package / name).stat().st_size <= MAX_BYTES, "fixture byte limit")
        need(
            hashlib.sha256((package / name).read_bytes()).hexdigest() == expected,
            "changed fixture: " + name,
        )
    sources = read(package / "SOURCES.json")["files"]
    need(len(sources) <= 100, "live source count")
    for item in sources:
        if item["usage"] == "input":
            path = root / item["path"]
            need(
                path.is_file() and path.stat().st_size <= MAX_BYTES,
                "live source byte limit",
            )
            need(
                hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"],
                "changed live source: " + item["path"],
            )


def reconstruct(package, root):
    # This import path contains only authenticated, retained PR3388 modules.
    sys.path.insert(0, str(package / "source3388"))
    prior = load("retained_pr3388", package / "source3388/verify.py")
    prior.ROOT = root
    export = prior.check_sources(root)
    old, plan = prior.predecessor(root, export)
    context = (*prior.context(root)[:4], plan)
    rows, _before, audit, plan = prior.construct(old, context)
    need(digest(rows) == OWNER_HASH, "exact PR3388 final payload")
    need(rows == read(package / "OWNERS.json.gz"), "retained owner fixture")
    need(plan == read(package / "PLAN.json"), "retained chronology fixture")
    need(
        audit["idle"] == {1: 2382, 3: 118, 16: 1, 32: 1, 48: 4880},
        "PR3388 baseline idle profile",
    )
    return rows, plan, context[1], audit


def inventory(rows, plan, geometry):
    bins = defaultdict(list)
    eligible = {}
    for index, row in enumerate(rows):
        key = row["owner_replica"], row["child"], row["port"]
        bins[key].append(index)
    for owner in range(16):
        for child, capacity in geometry["rank"].items():
            times = plan["windows"][f"{owner},{child}"][1]
            pair = geometry["place"][child][0]
            eligible[owner, child] = sum(
                1 << time
                for time in times
                if not (
                    plan["order"][time][1] == owner
                    and geometry["stage_pair"][plan["order"][time][0]] == pair
                )
            )
            for port in range(112):
                bins[owner, child, port]
                need(capacity <= 48, "bin capacity bound")
    masks = {
        key: sum(1 << rows[i]["time"] for i in members) for key, members in bins.items()
    }
    used = {
        key: sum(rows[i]["width"] for i in members) for key, members in bins.items()
    }
    return bins, masks, used, eligible


def closure(candidates, masks, eligible, initial):
    """Least fixed point. A first visit retains its original whole bundle."""
    need(len(candidates) <= 7168 and len(initial) == 1, "rank16 domain bound")
    reached = set(initial)
    additions = []
    for _round in range(len(candidates) + 1):
        windows = {eligible[key[:2]] for key in reached}
        new = {
            key
            for key in candidates
            if key not in reached
            and any(not masks[key] & ~window for window in windows)
        }
        additions.append(len(new))
        if not new:
            return reached, additions
        reached.update(new)
    raise ValueError("closure iteration bound exhausted")


def available_widths(rows, bundles, windows):
    histogram = Counter()
    witness = None
    for key, members in bundles.items():
        maximum = max(
            sum(rows[i]["width"] for i in members if window >> rows[i]["time"] & 1)
            for window in windows
        )
        histogram[maximum] += 1
        if witness is None or maximum > witness["available_width"]:
            witness = {"bin": list(key), "available_width": maximum}
    need(witness is not None, "nonempty full48 bundle domain")
    return dict(sorted(histogram.items())), witness


def analyze(rows, plan, geometry, audit):
    bins, masks, used, eligible = inventory(rows, plan, geometry)
    rank16 = [key for key in bins if geometry["rank"][key[1]] == 16]
    initial = {key for key in rank16 if used[key] == 0}
    candidates = [key for key in rank16 if used[key] > 0]
    reached, additions = closure(candidates, masks, eligible, initial)
    windows = {eligible[key[:2]] for key in reached}
    full48 = {
        key: members
        for key, members in bins.items()
        if geometry["rank"][key[1]] == used[key] == 48
    }
    histogram, witness = available_widths(rows, full48, windows)
    need(max(histogram) < 16, "a full48 bundle can supply the rank16 buffer")
    return {
        "status": "PASS_T16_BUFFER_TRANSPORT_CUT",
        "source_head": "684d347c0e6e578b8ab600d2e680ad6701cf7fa0",
        "owner_canonical_sha256": digest(rows),
        "roles": len(rows),
        "rank_mass": audit["rank_mass"],
        "initial_rank16_buffer": [list(key) for key in sorted(initial)],
        "rank16_bins": len(rank16),
        "nonempty_rank16_bundles": len(candidates),
        "closure_additions": additions,
        "reachable_rank16_bins": len(reached),
        "reachable_owner_children": [
            list(key) for key in sorted({b[:2] for b in reached})
        ],
        "eligibility_classes": [
            list(t for t in range(144) if window >> t & 1) for window in sorted(windows)
        ],
        "full48_bundles": len(full48),
        "available_width_histogram": histogram,
        "maximum_available_width": max(histogram),
        "maximum_witness": witness,
        "required_width": 16,
        "scope": (
            "Neutral equal-capacity whole-bin transport at fixed PR3388 chronology, "
            "then one full48 split. Family conflicts are ignored. Nonneutral, "
            "partial-bin and chronology changes are outside."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=PACKAGE)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    package, root = args.package.resolve(), args.root.resolve()
    authenticate(package, root)
    result = analyze(*reconstruct(package, root))
    if args.write:
        (package / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(
            canonical(result) == canonical(read(package / "RESULT.json")),
            "committed result differs",
        )
    print(result["status"], "reachable=896 max_width=9 required=16 no_new_kappa")


if __name__ == "__main__":
    main()
