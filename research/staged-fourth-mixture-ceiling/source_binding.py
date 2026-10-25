"""Bind the pooled cost model to the exact PR4088 source subset.

Ross Richardson with substantial OpenAI Codex assistance, Apache-2.0.
The unchanged predecessor binary-frame ledger is re-executed and credited;
this is a local cost extraction, not a native or dirty-state replay.
"""
from collections import Counter
from copy import deepcopy
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import runpy

P = Path(__file__).resolve().parent
SOURCE_HEAD = "76088d49e3ed4142a958659aa996b0ca4da5e88e"
THREE = {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8}
DELTA = {1: 2, 3: 3, 4: -3}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def check_bytes(package=P, overrides=None):
    exports = read(package / "SOURCE-EXPORT.json")
    need(exports["source_head"] == SOURCE_HEAD, "wrong predecessor head")
    rows = exports["files"]
    need(len(rows) == 14, "source subset coverage")
    need(len({row["path"] for row in rows}) == len(rows), "duplicate source path")
    for row in rows:
        need(row["original_head"] == SOURCE_HEAD and row["original_pr"] == 4088,
             "mixed source identity")
        need(row["path"].startswith("source4088/") and ".." not in Path(row["path"]).parts,
             "unsafe source path")
        payload = ((overrides or {}).get(row["path"]) if overrides and row["path"] in overrides
                   else (package / row["path"]).read_bytes())
        need(len(payload) == row["bytes"] and hashlib.sha256(payload).hexdigest() == row["sha256"],
             "source bytes: " + row["path"])
    return exports


def order_context(order, template):
    need(all(isinstance(row, list) and len(row) == 2
             and all(type(v) is int for v in row) for row in order), "call identities")
    need(len(order) == len({tuple(row) for row in order}) == 3240, "call coverage")
    need(set(map(tuple, order)) == {(s, r) for s in range(9) for r in range(360)},
         "current 360-replica order")
    times = {tuple(row): t for t, row in enumerate(order)}
    need(all(times[s, r] < times[s + 1, r] for s in range(8) for r in range(360)),
         "per-replica source order")
    need(template["m"] == 73, "ambient width")
    child_ports = {(row["child"], row["port"]): row["rank"]
                   for row in template["idle_children"]}
    need(len(child_ports) == len(template["idle_children"]) == 18 * 112,
         "duplicate/missing child port")
    need(set(child_ports) == {(c, p) for c in range(18) for p in range(112)},
         "complete child ports")
    need(all(child_ports[c, p] == child_ports[c, 0]
             for c in range(18) for p in range(112)), "port-dependent capacity")
    bins = Counter()
    # The template contains historical 37-replica material. Only its original
    # child-port capacities are used; the current ORDER supplies 360 replicas.
    for capacity in child_ports.values():
        bins[capacity] += 360
    need(dict(bins) == {8: 241920, 16: 161280, 32: 161280, 48: 161280},
         "current complete bin inventory")
    return dict(sorted(bins.items()))


def bind(package=P):
    exports = check_bytes(package)
    source = package / "source4088"
    ledger = runpy.run_path(str(source / "checks/inherited_frames.py"))["ledger"]
    bills = {}
    for tag in ("base", "extra"):
        for variant in ("THREE", "FOUR"):
            word = read(source / f"inputs/{variant}-{tag}.json.gz")
            profile, inventory = ledger(word)
            expected = dict(THREE)
            expected_inventory = {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}
            if variant == "FOUR":
                for rank, count in DELTA.items():
                    expected[rank] += count
                expected_inventory[7] += 1
                expected_inventory[8] -= 1
            need(dict(profile) == expected and dict(inventory) == expected_inventory,
                 "re-extracted local cost/widths")
            bills[f"{variant}-{tag}"] = {"profile": dict(sorted(profile.items())),
                                         "helper_widths": dict(sorted(inventory.items()))}
    bins = order_context(read(source / "owner/ORDER.json"),
                         read(source / "owner/TEMPLATE.json.gz"))
    need(sum(c * n for c, n in bins.items()) == 17418240, "capacity mass")
    demand = {w: 3240 * n for w, n in bills["THREE-base"]["helper_widths"].items()}
    need(sum(w * n for w, n in demand.items()) == 10695240, "hosted width mass")
    need(sum(r * n * 3240 for r, n in THREE.items()) == 16708680, "local rank mass")
    need(16708680 + 17418240 - 10695240 == 65088 * 360, "complete rank mass")
    return {"status": "PASS_BOUND_SOURCE_COSTS", "source_head": SOURCE_HEAD,
            "source_files": len(exports["files"]), "providers": bills,
            "bins": bins, "demands_at_x0": demand, "calls": 3240,
            "stock": 896 * 360, "ambient_width": 73,
            "scope": "Exact source bytes and re-executed predecessor binary-frame cost ledger; "
                     "current order/bin extraction. Stock is the retained stipulated moment "
                     "normalization. No fresh native, dirty-state, owner or outer release."}


def controls(package=P):
    rejected = []

    def reject(name, callback):
        try:
            callback()
        except ValueError:
            rejected.append(name)
            return
        raise ValueError("accepted control: " + name)

    rel = "source4088/inputs/FOUR-base.json.gz"
    raw = (package / rel).read_bytes()
    reject("corrupted_frozen_word", lambda: check_bytes(package, {rel: bytes([raw[0] ^ 1]) + raw[1:]}))
    order = read(package / "source4088/owner/ORDER.json")
    template = read(package / "source4088/owner/TEMPLATE.json.gz")
    reject("historical37_in_place_of_current360", lambda: order_context(
        [row for row in order if row[1] < 37], template))
    bad_template = deepcopy(template)
    bad_template["idle_children"][1] = bad_template["idle_children"][0]
    reject("duplicate_original_child_port", lambda: order_context(order, bad_template))
    return rejected


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = bind()
    result["rejected_controls"] = controls()
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
