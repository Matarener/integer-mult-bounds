#!/usr/bin/env python3
"""Producer for CERTIFICATE.json and CORRECTION-RECIPES.json (not part of replay).

Generates the corrections on #3532's R0 and R1 and the end-cut control on the
published word, lowers every transport edge that is absent from both the
published recipe set and #3532's REPAIR-RECIPES.json with the pinned native
compiler, and writes the receipt computed by verify.py. Refuses to overwrite
existing outputs unless --force is given.
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
    for name in ("CERTIFICATE.json", "CORRECTION-RECIPES.json"):
        V.need(args.force or not (HERE / name).exists(), name + " exists")
    root = V.ROOT
    load("flag1_side_clifford_pin", root / V.NATIVE / "vendor/clifford_exact.py", CLIFFORD_SHA256)
    co = load("flag1_side_native_compile", root / V.NATIVE / "compile.py", COMPILER_SHA256)
    witness, fixture, recipes, _flags, repair, repair_recipes = V.load_inputs(root)
    physical = V.physical_map(recipes)
    program = witness["program"]
    bases = {"published": program}
    for name in ("R0", "R1"):
        bases[name] = V.apply_splices(program, repair["repairs"][name]["splices"])
    spec = V.corrections(program, bases["R0"], bases["R1"], witness["final_frames"], V.ports(fixture))
    known = {(tuple(r["old"]), tuple(r["new"])) for r in recipes["transports"]}
    known |= {(tuple(r["old"]), tuple(r["new"])) for r in repair_recipes}
    new = {}
    for base_name, group in spec.items():
        for name, item in group.items():
            prog = V.apply_splices(bases[base_name], item["splices"])
            for e in prog:
                if e[0] != "transport":
                    continue
                key = (physical(e[2]), physical(e[3]))
                if key in known or key in new:
                    continue
                actual = co.CE.canonical_frame(9, key[0]).adjoint().then(co.CE.canonical_frame(9, key[1]))
                record, _ = co.CE.lower_child(actual)
                V.need(record["rank"] == e[4], "native rank equals frame gap")
                new[key] = {"old": list(key[0]), "new": list(key[1]), "rank": e[4], "recipe": record}
    recs = [new[k] for k in sorted(new)]
    payload = {
        "schema_version": 1,
        "scope": "Native recipes for the transport edges used by the flag-1 corrections (T, S, P, Trow on #3532's R0; E, Erow on R1; Tend on the published word) that are absent from the published p104-native-channel recipe set and from #3532's REPAIR-RECIPES.json. Lowered with the pinned compile.py / vendor/clifford_exact.py; checked by the published check_native.validate() during replay.",
        "compiler_sha256": COMPILER_SHA256,
        "clifford_exact_sha256": CLIFFORD_SHA256,
        "recipes": recs,
    }
    got = V.receipt(root, {"corrections": spec}, recs)
    (HERE / "CORRECTION-RECIPES.json").write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    (HERE / "CERTIFICATE.json").write_text(json.dumps(got, indent=2, sort_keys=True) + "\n")
    print("WROTE", len(recs), "new recipes")


if __name__ == "__main__":
    main()
