#!/usr/bin/env python3
"""Check the source-bound PR3359 direct-cycle obstruction using integer hinges."""

import argparse
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "research/complex-t16-two-stage-cycles/data/OWNERS.json.gz"
PLAN = "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
AUDITOR = "research/t16-owner-audit-seed67/verify.py"
ROLE_KEYS = ("stage", "replica", "time", "helper", "width")
ROWS = 69120
CALLS = 144
MAX_RANK = 48
MAX_BYTES = 32 * 1024 * 1024


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    path = Path(path)
    need(path.stat().st_size <= MAX_BYTES, "input byte bound")
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
    else:
        raw = path.read_bytes()
    need(len(raw) <= MAX_BYTES, "decompressed byte bound")
    return json.loads(raw)


def sources(main):
    manifest = read(PACKAGE / "SOURCES.json")
    need(len(manifest["files"]) <= 20, "source count bound")
    for item in manifest["files"]:
        if item["usage"] == "input":
            need((main / item["path"]).stat().st_size <= MAX_BYTES, "source byte bound")
            raw = (main / item["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source pin")
    export = read(PACKAGE / "SOURCE-EXPORT.json")
    need(len(export["retained_files"]) == 3, "retained inventory")
    for name, item in export["retained_files"].items():
        raw = (PACKAGE / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "retained pin")
    raw = (PACKAGE / "predecessor.patch.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == export["patch_sha256"], "patch pin")
    return export


def predecessor(main, export):
    rows = read(main / BASE)
    patch = read(PACKAGE / "predecessor.patch.json")
    need(len(rows) == ROWS and len(patch) == export["patch_rows"] <= 300, "map size")
    indices = [item["index"] for item in patch]
    need(indices == sorted(set(indices)), "ordered distinct patch indices")
    for item in patch:
        index = item["index"]
        need(type(index) is int and 0 <= index < ROWS, "patch index")
        need(rows[index] == item["before"], "patch preimage")
        need(
            all(rows[index][key] == item["after"][key] for key in ROLE_KEYS),
            "changed logical role",
        )
        rows[index] = item["after"]
    expected = read(PACKAGE / "predecessor/RESULT.json")["owner_canonical_sha256"]
    need(digest(rows) == expected == export["owner_canonical_sha256"], "PR3359 map")
    return rows


def context(main):
    spec = importlib.util.spec_from_file_location("direct_cycle_owner", main / AUDITOR)
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    word = read(auditor.WORD)
    geometry = auditor.geometry(
        read(main / auditor.TEMPLATE), read(main / auditor.PHASES)
    )
    widths = auditor.word_widths(word)
    local = auditor.as_profile(word["report"]["local_profile"])
    plan = read(main / PLAN)
    need(
        len(plan["order"]) == CALLS and max(geometry["rank"].values()) == MAX_RANK,
        "fixed call and rank inventory",
    )
    return auditor, geometry, widths, local, plan


def bin_key(row):
    return row["owner_replica"], row["child"], row["port"]


def audit(rows, ctx):
    auditor, geometry, widths, local, plan = ctx
    used = Counter()
    for row in rows:
        used[bin_key(row)] += row["width"]
    spans, _ = auditor.windows(geometry, [tuple(item) for item in plan["order"]])
    idle = Counter()
    for owner, child in spans:
        for port in range(112):
            free = geometry["rank"][child] - used[owner, child, port]
            need(free >= 0, "overfilled source bin")
            if free:
                idle[free] += 1
    return auditor.audit(geometry, widths, local, rows, plan, idle, 16)


def relaxed_graph(rows, ctx):
    """Complete window/capacity graph; drop all family and active-pair conflicts.

    For a fixed source/target state, every convex hinge has its largest
    increment at the same extreme residual. Keep that extreme only.
    """
    auditor, geometry, widths, _, plan = ctx
    order = [tuple(item) for item in plan["order"]]
    spans, positions = auditor.windows(geometry, order)
    width_set = sorted(set(widths))
    need(len(width_set) == 5, "source width inventory")
    states = [(time, width) for time in range(CALLS) for width in width_set]
    index = {state: i for i, state in enumerate(states)}
    used = Counter()
    for row in rows:
        used[bin_key(row)] += row["width"]
    free = {key: geometry["rank"][key[1]] - value for key, value in used.items()}
    allowed = {
        key: [
            time
            for time, call in enumerate(order)
            if spans[key[:2]][0] < positions[call] < spans[key[:2]][1]
        ]
        for key in used
    }
    count = len(states)
    edges = {}
    for row in rows:
        key = bin_key(row)
        residual = free[key]
        target = index[row["time"], row["width"]]
        for time in allowed[key]:
            for incoming in width_set:
                delta = row["width"] - incoming
                if residual + delta < 0:
                    continue
                edge = index[time, incoming] * count + target
                old = edges.get(edge)
                if (
                    old is None
                    or (delta > 0 and residual > old)
                    or (delta < 0 and residual < old)
                ):
                    edges[edge] = residual
    need(len(edges) <= count * count, "finite graph bound")
    return states, edges


def check_potentials(states, edges, certificate):
    count = len(states)
    need(certificate["states"] == [list(state) for state in states], "potential states")
    hinges = certificate["hinges"]
    need(set(hinges) == {str(k) for k in range(1, MAX_RANK)}, "all hinge indices")
    for k in range(1, MAX_RANK):
        potential = hinges[str(k)]
        need(len(potential) == count, "potential size")
        need(
            all(type(x) is int and 0 <= x <= 64 for x in potential),
            "integer potentials",
        )
        for edge, residual in edges.items():
            source, target = divmod(edge, count)
            delta = states[target][1] - states[source][1]
            gain = max(residual + delta - k, 0) - max(residual - k, 0)
            need(gain <= potential[target] - potential[source], "hinge edge inequality")
    return (MAX_RANK - 1) * len(edges)


def run(main):
    rows = predecessor(main, sources(main))
    ctx = context(main)
    owner = audit(rows, ctx)
    states, edges = relaxed_graph(rows, ctx)
    certificate = read(PACKAGE / "POTENTIALS.json")
    inequalities = check_potentials(states, edges, certificate)
    return {
        "status": "PASS_T16_DIRECT_CYCLE_OBSTRUCTION",
        "source_pr": 3359,
        "owner_canonical_sha256": digest(rows),
        "owner_audit": owner,
        "states": len(states),
        "relaxed_edges": len(edges),
        "graph_sha256": digest(sorted(edges.items())),
        "integer_hinge_inequalities": inequalities,
        "hinges": MAX_RANK - 1,
        "potential_sha256": digest(certificate),
        "claim": "No direct four-bin rotation lowers any concave idle-rank cost; the certificate covers any one-out/one-in-per-bin permutation.",
        "scope": "Exact PR3359, original whole-helper widths and chronology. No multiple changes per bin, changed word, supplier admission or new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(run(args.main.resolve())))
    if args.write:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(
            canonical(result) == canonical(read(PACKAGE / "RESULT.json")),
            "typed result",
        )
    print(
        result["status"],
        "edges=" + str(result["relaxed_edges"]),
        "inequalities=" + str(result["integer_hinge_inequalities"]),
        flush=True,
    )


if __name__ == "__main__":
    main()
