# SPDX-License-Identifier: Apache-2.0
"""Check every data output at the original PR2979 emitted macro boundary."""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_BYTES = 16 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read(path):
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "input byte capacity")
    return raw


def authenticate():
    manifest = json.loads(read(PACKAGE / "SOURCES.json"))
    pins = [r for r in manifest["files"] if r["usage"] == "input"]
    require(0 < len(pins) <= 32, "input inventory capacity")
    blobs = {}
    for pin in pins:
        path = ROOT / pin["path"]
        require(path.resolve().is_relative_to(ROOT), "input stays under root")
        raw = read(path)
        require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source hash: " + pin["path"])
        blobs[pin["path"]] = raw
    require(len(blobs) == len(pins), "unique input inventory")
    return blobs


def load(blobs, relative, name):
    path = ROOT / relative
    require(read(path) == blobs[relative], "authenticated module before import")
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, "source module loader")
    module = importlib.util.module_from_spec(spec)
    previous = sys.pycache_prefix
    with tempfile.TemporaryDirectory(prefix="data-import-") as cache:
        sys.pycache_prefix = cache
        try:
            spec.loader.exec_module(module)
        finally:
            sys.pycache_prefix = previous
    require(read(path) == blobs[relative], "authenticated module after import")
    return module


def modules(blobs):
    prefix = "research/rank7-v45-native-cone-seed78/"
    result = {name: load(blobs, prefix + name + ".py", "data_boundary_" + name)
              for name in ("support", "source", "cone")}
    result["source_covectors"] = load(blobs, "research/rank7-v45-native-endpoint/endpoints.py", "data_source_covectors")
    result["values"] = load(blobs, "research/rank7-peer-private-free-audit/lifetimes.py", "data_boundary_values")
    return result


def expected(output, backward):
    require(type(output) is int and 0 <= output < 224, "data output domain")
    row = [["L" + str(output), [], "1"]]
    if backward and output < 112:
        row.append(["L" + str(112 + output), [], "-1"])
    if not backward and output >= 112:
        row.append(["L" + str(output - 112), [], "1"])
    return sorted(row)


def data_rows(mod, word, events, backward):
    source = mod["source_covectors"]
    live = set(range(704)) - set(word["removed"])
    buffers = {704 + int(r) for r in word["helper_final"]}
    gates = source.program(word)
    rows, private_terms = [], []
    for output in range(224):
        emitted = mod["cone"].endpoint(events, "L" + str(output), len(events) - 1, backward)
        pulled = source.endpoint(gates, output, backward, live, buffers)
        original = sorted([["L" + str(r), list(w), q] for r, w, q in pulled if r in live])
        private = [[r, list(w), q] for r, w, q in pulled if r in buffers]
        require(emitted == original == expected(output, backward), "data output " + str(output))
        rows.append({"output": output, "emitted_and_source_original_terms": emitted})
        if private:
            private_terms.append({"output": output, "zero_entrance_terms": private})
    return {"outputs": rows, "source_private_entrance_terms": private_terms,
            "original_inputs": len(live), "private_zero_entrances": len(buffers),
            "source_gates": len(gates), "emitted_events": len(events)}


def restored_rows(mod, events, original, backward):
    # Reuse PR3238's exact row arithmetic, observing every final helper at once.
    arithmetic = mod["values"]
    require(len(events) <= 100000 and len(original) == 632, "forward state capacity")
    rows = {r: {(r, ()): Fraction(1)} for r in original}
    active, allocated, frees = set(), set(), []
    for index, event in enumerate(events):
        tag = event[0]
        if tag == "zero_buffer":
            action, r = event[1:]
            if action == "alloc":
                require(r not in rows and r not in allocated, "fresh zero buffer")
                rows[r] = {}
                active.add(r)
                allocated.add(r)
            else:
                require(action == "free" and r in active, "live private free")
                require(not rows[r], "zero at actual private free")
                frees.append({"role": r, "event": index, "value": []})
                active.remove(r)
                del rows[r]
        elif tag == "scalar":
            op, r = event[1], event[1][1]
            used = op[1:3] if op[0] in ("add", "copy") else op[1:2]
            require(all(not x.startswith("Z") or x in active for x in used), "live private scalar")
            if op[0] == "clear":
                rows[r] = {}
            elif op[0] == "copy":
                rows[r] = dict(rows[op[2]])
            elif op[0] == "scale":
                q = Fraction(op[2], op[3])
                require(q != 0, "nonzero scale")
                rows[r] = {key: q * value for key, value in rows[r].items()}
            else:
                require(op[0] == "add" and r != op[2], "distinct ADD")
                rows[r] = arithmetic.merge(rows[r], rows[op[2]], Fraction(op[3], op[4]))
        elif tag == "warp":
            r, operator = event[1:3]
            require(r in rows, "live warp role")
            if backward:
                operator = (1 if operator > 0 else -1) * (1000000 + abs(operator))
            rows[r] = arithmetic.warp(rows[r], operator)
        else:
            require(tag in ("phase", "climb", "center", "adapter", "residual_adapter"), "known frame event")
        require(len(rows) <= 731, "632 original, 91 private, eight center rows")
    require(not active and len(frees) == len(allocated) == 91, "all 91 private frees")
    helpers = [r for r in original if int(r[1:]) >= 224]
    for role in helpers:
        require(rows[role] == {(role, ()): Fraction(1)}, "forward helper " + role)
    return {"helper_outputs": len(helpers), "frees": frees,
            "helper249": arithmetic.encode(rows["L249"])}


def fault_control(mod, events, original, backward):
    # At this cut all ordinary sources have FULL charts and no later data read.
    # Insert one legal same-chart data shear, outside every helper/private root.
    cut = next(i for i, event in enumerate(events) if event == ["zero_buffer", "free", "Z249"])
    require(all(e[0] in ("zero_buffer", "residual_adapter", "phase") for e in events[cut:]), "terminal data isolation")
    full = list(mod["source"].FULL)
    for role in ("L0", "L1"):
        require(any(e[:3] == ["adapter", "new_to_old", role] and tuple(e[3]) == tuple(full) for e in events[:cut]), "data exits in FULL frame")
    require(all(e[0] != "residual_adapter" or int(e[2][1:]) >= 224 for e in events[cut:]), "suffix only wraps helpers")
    gate = ["scalar", ["add", "L0", "L1", 1, 1], full]
    mutant = events[:cut] + [gate] + events[cut:]
    before = restored_rows(mod, events, original, backward)
    after = restored_rows(mod, mutant, original, backward)
    # Inserting the gate shifts free indices by one; compare values, not positions.
    free_values = lambda r: [[f["role"], f["value"]] for f in r["frees"]]
    require(free_values(before) == free_values(after), "all private roots preserved")
    require(before["helper_outputs"] == after["helper_outputs"] == 408, "all helper roots preserved")
    row = mod["cone"].endpoint(mutant, "L0", len(mutant) - 1, backward)
    require(row != expected(0, backward), "data fault rejected")
    return {"insert_before_event": cut, "inserted_event": gate,
            "helper_outputs_preserved": 408, "private_frees_preserved": len(after["frees"]),
            "corrupted_L0": row, "expected_L0": expected(0, backward)}


def provider(mod, blobs, tag, run):
    data = mod["support"].artifacts(blobs, tag, run)
    cases = {}
    for orientation in ("forward", "backward"):
        backward = orientation == "backward"
        events, meta = mod["source"].bind(data["word"], data["canonical_word"], data["programs"][orientation], backward)
        print("CHECK_DATA_BOUNDARY " + tag + " " + orientation, file=sys.stderr, flush=True)
        result = data_rows(mod, data["word"], events, backward)
        result["data_fault"] = fault_control(mod, events, meta["start"], backward)
        result["events_sha256"] = digest(events)
        cases[orientation] = result
    return {"status": "PASS_PR2979_ALL_DATA_BOUNDARY", "provider": tag,
            "orientations": cases, "scientific_head": "be191346391661f4d35fc0d1508d0a6029572576",
            "native_realization_reused_premise": True, "new_supplier": False, "new_kappa": False}


def compute(tag, artifacts=None):
    blobs = authenticate()
    mod = modules(blobs)
    if artifacts is None:
        with tempfile.TemporaryDirectory(prefix="rank7-data-") as directory:
            run = mod["support"].generate(blobs, tag, Path(directory))
            result = provider(mod, blobs, tag, run)
    else:
        result = provider(mod, blobs, tag, artifacts)
    require(authenticate() == blobs, "inputs unchanged during replay")
    result["input_sha256"] = {p: hashlib.sha256(raw).hexdigest() for p, raw in sorted(blobs.items())}
    require(len(canonical(result)) <= MAX_BYTES, "receipt capacity")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=("base", "extra"))
    parser.add_argument("--artifacts", type=Path)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute(args.provider, args.artifacts)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        with gzip.GzipFile(fileobj=io.BytesIO(read(PACKAGE / ("RESULT-" + args.provider + ".json.gz")))) as stream:
            raw = stream.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, "decoded receipt capacity")
        retained = json.loads(raw)
        require(result == retained, "deterministic result equality")
        print(result["status"] + " provider=" + args.provider)


if __name__ == "__main__":
    main()
