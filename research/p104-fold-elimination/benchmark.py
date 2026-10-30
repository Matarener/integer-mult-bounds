"""Time alternating complete first-step folds, checking every output word."""

import argparse
import gzip
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

from runtime import PACKAGE, authenticate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_word(path):
    word = json.loads(gzip.decompress(path.read_bytes()))
    data = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest(), len(word["program"])


def measure(mode, toolkit, scratch, index):
    output = scratch / f"{index}-{mode}.json.gz"
    command = [sys.executable, "-B", str(PACKAGE / "run.py"), mode,
               str(toolkit), str(output), "--whole-fold"]
    started = time.perf_counter()
    result = subprocess.run(command, capture_output=True, text=True, timeout=570)
    elapsed = time.perf_counter() - started
    (scratch / f"{index}-{mode}.stdout").write_text(result.stdout)
    (scratch / f"{index}-{mode}.stderr").write_text(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"fold failed: {mode}, exit {result.returncode}")
    report = json.loads(result.stdout.strip().splitlines()[-1])
    if len(report["steps"]) != 1 or report["steps"][0]["status"] != "FOLDED":
        raise RuntimeError("complete fold did not accept its site")
    fingerprint, events = canonical_word(output)
    return {"mode": mode, "seconds": elapsed, "word_sha256": fingerprint,
            "events": events, "step": report["steps"][0], "exit_code": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("toolkit", type=Path)
    parser.add_argument("scratch", type=Path)
    parser.add_argument("--pairs", type=int, default=5)
    args = parser.parse_args()
    if not 5 <= args.pairs <= 10:
        parser.error("use five to ten alternating pairs")
    args.scratch.mkdir(parents=True, exist_ok=False)
    manifest = authenticate(args.toolkit)
    runs = []
    for index in range(args.pairs):
        for mode in ("baseline", "candidate"):
            run = measure(mode, args.toolkit, args.scratch, index)
            if runs and any(run[key] != runs[0][key]
                            for key in ("word_sha256", "events", "step")):
                raise RuntimeError("complete fold outputs differ")
            runs.append(run)
            print(mode, index, f"{run['seconds']:.6f}", flush=True)
    summary = {}
    for mode in ("baseline", "candidate"):
        samples = [run["seconds"] for run in runs if run["mode"] == mode]
        summary[mode] = {"median_seconds": statistics.median(samples),
                         "range_seconds": [min(samples), max(samples)]}
    receipt = {"schema": "p104-fold-benchmark/1", "runs": runs,
               "summary": summary, "errors": 0, "python": sys.version,
               "executable": sys.executable, "platform": platform.platform(),
               "source_head": manifest["source_head"],
               "hashes": {path.name: digest(path) for path in
                          sorted(PACKAGE.glob("*.py"))},
               "retained_manifest_sha256": digest(PACKAGE / "RETAINED.json"),
               "timed_region": "Fresh process through completed first fold, including source authentication, both attempted variants, legality and output serialization."}
    (args.scratch / "BENCHMARK.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
