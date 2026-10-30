#!/usr/bin/env python3
"""Bounded semantic challenges against an actual prepared or completed replay.

SPDX-License-Identifier: Apache-2.0
Prepared for yssite with substantial OpenAI Codex assistance, incorporating
the separate adversarial context's demonstrated cache mutations.
This does not rerun or establish the full release.
"""
import argparse
import gzip
import json
from pathlib import Path
import shutil
import tempfile

from adapt import TAGS, write
from binding import need, read, sha
from native_outputs import REFERENCES, authenticate_native
from replay import check_preflight


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", type=Path, required=True, help="existing replay.py output")
    ap.add_argument("--preflight", type=Path, help="if the run supplied --checked-preflight")
    args = ap.parse_args()
    work = args.work.resolve()
    baseline = (args.preflight or work / "baseline/release-work/preflight").resolve()
    check_preflight(baseline)
    results = [{"name": "actual predecessor preflight", "status": "PASS"}]

    def reject(name, call, reason):
        try:
            call()
        except ValueError as exc:
            need(reason in str(exc), "unexpected rejection: " + str(exc))
            results.append(dict(name=name, status="REJECTED", reason=str(exc)))
        else:
            raise ValueError("accepted semantic mutant: " + name)

    for pid, tag in TAGS.items():
        word_sha = sha(work / f"source/new/borrow/words/BORROW-WORD-43{tag}.json.gz")
        original = work / "native-cache" / word_sha
        # Engine caches add CACHE.json; its transport inventory is checked by
        # the engine. The fixed scientific gate consumes only native products.
        with tempfile.TemporaryDirectory() as td:
            native = Path(td) / "native"
            shutil.copytree(original, native, ignore=shutil.ignore_patterns("CACHE.json"))
            products = authenticate_native(pid, word_sha, native)
            need(len(products) == 11, "all scientific products")
            results.append(dict(name=pid + " actual native products", status="PASS"))

            recipe_path = native / "local/CLIFFORD-RECIPES.json"
            saved = recipe_path.read_bytes()
            recipe = read(recipe_path)
            recipe["warps"][0]["left"]["phase"] = (recipe["warps"][0]["left"]["phase"] + 1) % 4
            write(recipe_path, recipe)
            for name in ("CLIFFORD-REVIEW.json", "WARP-RECIPE-CHECKS.json"):
                path = native / "local" / name
                value = read(path)
                value["recipe_sha256"] = sha(recipe_path)
                write(path, value)
            reject(pid + " wrong phase with all recipe references rebound",
                   lambda: authenticate_native(pid, word_sha, native),
                   "native scientific output commitment")
            recipe_path.write_bytes(saved)
            for name in ("CLIFFORD-REVIEW.json", "WARP-RECIPE-CHECKS.json"):
                shutil.copyfile(original / "local" / name, native / "local" / name)

            steps_path = native / "STEPS.json"
            steps = read(steps_path)
            write(steps_path, steps[:-1])
            reject(pid + " skipped phase stage",
                   lambda: authenticate_native(pid, word_sha, native),
                   "actual native stage products coverage")
            write(steps_path, steps)

            # Positive control: transport and elapsed time may change without
            # changing a mathematical product. Rebind actual serialized refs.
            for path in (native / "local").iterdir():
                value = read(path)
                if path.name in ("CLIFFORD-REVIEW.json", "SCALAR-FRAME-AUDIT.json"):
                    value["seconds"] += 1
                raw = json.dumps(value, sort_keys=True, indent=1).encode()
                path.write_bytes(gzip.compress(raw, mtime=17) if path.suffix == ".gz" else raw)
            for path in (native / "local").iterdir():
                value = read(path)
                changed = False
                for field, target in REFERENCES.items():
                    if field in value:
                        value[field] = sha(native / "local" / target)
                        changed = True
                if changed:
                    write(path, value)
            need(authenticate_native(pid, word_sha, native) == products,
                 "transport-equivalent products")
            results.append(dict(name=pid + " equivalent serialization and timing", status="PASS"))

    with tempfile.TemporaryDirectory() as td:
        mutant = Path(td) / "preflight"
        shutil.copytree(baseline, mutant)
        engine = mutant / "admit_composed.py"
        engine.write_bytes(engine.read_bytes() + b"\n# deliberate source mutation\n")
        receipt_path = mutant / "PREFLIGHT-RESULT.json"
        receipt = read(receipt_path)
        receipt["admission_engine_sha256"] = sha(engine)
        write(receipt_path, receipt)
        reject("changed engine with rebound completion receipt",
               lambda: check_preflight(mutant), "preflight admission engine")

    print(json.dumps(dict(status="PASS_ACTUAL_REPLAY_CHALLENGES", cases=results,
                          scope="Reuse gates only; not full native or ordinary admission."),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
