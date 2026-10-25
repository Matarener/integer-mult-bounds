#!/usr/bin/env python3
"""Producer for CERTIFICATE.json and REPAIR-RECIPES.json (not part of replay).

Defines the two changed schedules as splices of the published witness,
lowers each transport edge absent from the published recipe set with the
pinned native compiler, and writes the receipt computed by verify.py.
Refuses to overwrite existing outputs unless --force is given.
"""

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402

COMPILER_SHA256 = "9d2fc2d81962ddb0b4dd7d6482d9918a87a6b05759690317dea79939ca5656a3"
CLIFFORD_SHA256 = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"

W4 = [95, 447, 6, 32]
W4P = [95, 447, 32, 20]
W5 = [95, 447, 6, 32, 20]
W6 = W5 + [15]
V5 = [95, 447, 6, 32, 192]
V6 = [95, 447, 6, 32, 20, 192]
W7 = V6 + [15]
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]


def splices(program, final):
    def one(i, event):
        return {"published_range": [i, i + 1], "published": [program[i]], "events": [event]}
    r0 = [
        one(3362, ["transport", "D17", W4, W6, 2]),
        one(3363, ["transport", "Y59", W4P, W6, 2]),
        one(3364, ["add", "Y59", "D17", "1/4", W6]),
        one(3365, ["transport", "Y103", W4P, W6, 2]),
        one(3366, ["add", "Y103", "D17", "1/4", W6]),
        one(3460, ["transport", "D28", V5, W7, 2]),
        one(3461, ["transport", "Y103", W6, W7, 1]),
        one(3462, ["add", "Y103", "D28", "1/4", W7]),
        one(3525, ["transport", "Y59", W6, final["Y59"], 2]),
        one(3569, ["transport", "Y103", W7, final["Y103"], 1]),
        one(3612, ["transport", "D17", W6, FULL, 3]),
        one(3634, ["transport", "D28", W7, FULL, 2]),
    ]
    r1 = [
        {"published_range": [3363, 3367], "published": program[3363:3367],
         "events": [program[3365], program[3366],
                    ["transport", "D17", W5, W6, 1],
                    ["transport", "Y59", W4P, W6, 2],
                    ["add", "Y59", "D17", "1/4", W6]]},
        one(3525, ["transport", "Y59", W6, final["Y59"], 2]),
        one(3612, ["transport", "D17", W6, FULL, 3]),
    ]
    return {
        "R0": {
            "class": "event-preserving retarget: same events in the same order, same ADD registers and coefficients, only transport frames and ranks and the matching ADD chart fields change",
            "rule": "from the forced event on, each changed register's frame is its published frame plus the basis head, until a frame that already spans the head",
            "splices": r0,
        },
        "R1": {
            "class": "two-register comparison: Y103's transport and update at 3365-3366 move before Y59's, and D17 gets one added rank-1 transport",
            "rule": "D17 serves Y103 in the published rank-5 chart, then lifts to the rank-6 head chart for Y59",
            "splices": r1,
        },
    }


def load(name, path, digest):
    raw = path.read_bytes()
    V.need(hashlib.sha256(raw).hexdigest() == digest, "pinned compiler module: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    for name in ("CERTIFICATE.json", "REPAIR-RECIPES.json"):
        V.need(args.force or not (HERE / name).exists(), name + " exists")
    root = V.ROOT
    load("flag43_clifford_pin", root / V.NATIVE / "vendor/clifford_exact.py", CLIFFORD_SHA256)
    co = load("flag43_native_compile", root / V.NATIVE / "compile.py", COMPILER_SHA256)
    witness, _fixture, recipes, _flags = V.load_inputs(root)
    cert = {"repairs": splices(witness["program"], witness["final_frames"])}
    physical = V.physical_map(recipes)
    pub = {(tuple(r["old"]), tuple(r["new"])) for r in recipes["transports"]}
    new = {}
    for name in ("R0", "R1"):
        prog = V.apply_splices(witness["program"], cert["repairs"][name]["splices"])
        for e in prog:
            if e[0] != "transport":
                continue
            key = (physical(e[2]), physical(e[3]))
            if key in pub or key in new:
                continue
            actual = co.CE.canonical_frame(9, key[0]).adjoint().then(co.CE.canonical_frame(9, key[1]))
            record, _ = co.CE.lower_child(actual)
            V.need(record["rank"] == e[4], "native rank equals frame gap")
            new[key] = {"old": list(key[0]), "new": list(key[1]), "rank": e[4], "recipe": record}
    recs = [new[k] for k in sorted(new)]
    payload = {
        "schema_version": 1,
        "scope": "Native recipes for the transport edges used by repairs R0 and R1 that are absent from the published p104-native-channel recipe set. Lowered with the pinned compile.py / vendor/clifford_exact.py; checked by the published check_native.validate() during replay.",
        "compiler_sha256": COMPILER_SHA256,
        "clifford_exact_sha256": CLIFFORD_SHA256,
        "recipes": recs,
    }
    got = V.receipt(root, cert, recs)
    (HERE / "REPAIR-RECIPES.json").write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    (HERE / "CERTIFICATE.json").write_text(json.dumps(got, indent=2, sort_keys=True) + "\n")
    print("WROTE", len(recs), "new recipes")


if __name__ == "__main__":
    main()
