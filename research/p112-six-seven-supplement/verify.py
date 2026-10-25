#!/usr/bin/env python3
"""Replay two bounded exact reconstructions; the theorem is in PROOF.md.

conorholds, with substantial OpenAI Codex assistance. Apache-2.0.
Default verification is read-only. --emit deliberately writes RESULT.json.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent


def local_module(name):
    path = PACKAGE / (name + ".py")
    module = ModuleType("six_seven_" + name)
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def run():
    model = local_module("model")
    inputs = model.authenticate()
    primary, primary_engine = model.run()
    other = local_module("independent").run()
    independent_engine = other.pop("independent_engine")
    model.need(model.canonical_json(primary) == model.canonical_json(other),
               "separate exact engines disagree")
    controls = local_module("controls").run(model)
    actual = local_module("actual_controls").run(model)
    actual_d2 = local_module("d2_controls").run(model)
    scientific = {str(path.relative_to(PACKAGE)): sha256(path.read_bytes()).hexdigest()
                  for path in sorted(PACKAGE.rglob("*"))
                  if path.is_file() and path.suffix in (".py", ".md", ".lean")}
    source_hashes = {name: sha256(model.regular_bytes(
        PACKAGE if name in model.RETAINED_INPUTS else model.ROOT, name)).hexdigest()
                     for name in inputs}
    source_hashes["SOURCES.json"] = sha256((PACKAGE / "SOURCES.json").read_bytes()).hexdigest()
    return {"schema_version": 1, "finite_inputs": primary, "consumed_source_sha256": source_hashes,
            "primary_engine": primary_engine, "independent_engine": independent_engine,
            "controls": controls, "actual_factorization_controls": actual,
            "actual_d2_factorization_controls": actual_d2,
            "scientific_sha256": scientific}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    try:
        model = local_module("model")
        if args.sources_only:
            model.authenticate()
            print("PASS_P112_SIX_SEVEN_SOURCES scope=source-integrity-only")
            return 0
        result = run()
        path = PACKAGE / "RESULT.json"
        if args.emit:
            path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        else:
            expected = model.strict_json(path.read_bytes())
            model.need(model.canonical_json(expected) == model.canonical_json(result),
                       "scientific receipt or JSON types differ")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        print("FAIL_P112_SIX_SEVEN_SUPPLEMENT: " + str(error), file=sys.stderr)
        return 1
    print("PASS_P112_SIX_SEVEN_SUPPLEMENT affine6=43180 completions=6216 "
          "orthogonal_pairs=3780 sharp_sparse=5 optimal_covers=7896 frame_cuts=42840 "
          "callers=9 shared_frame_profiles=2 actual_d1_controls=2 actual_d2_controls=2 engines=2 "
          "scope=finite-proof-inputs-and-controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
