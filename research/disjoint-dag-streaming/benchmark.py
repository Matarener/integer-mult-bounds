"""Alternate fresh processes on the unchanged h=26 verification workload.

This contribution was produced by Nick Petalas. Apache-2.0.
Generated measurements must be written to an explicit path outside the checkout.
"""
import argparse
import gc
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import accelerator as fast


def require(condition, message):
    if not condition:
        raise ValueError(message)


def baseline_digest(circuit):
    data = json.dumps([[i, circuit.args[i], str(circuit.support[i])]
                       for i in sorted(circuit.active)], separators=(",", ":")).encode()
    return sha256(data).hexdigest()


def worker(mode):
    start = time.perf_counter()
    circuit = fast.DisjointTensor(26)
    built = time.perf_counter()
    verify = circuit.verify if mode == "baseline" else lambda: fast.verify(circuit)
    digest = baseline_digest if mode == "baseline" else fast.stream_digest
    receipt = verify()
    verified = time.perf_counter()
    actual = digest(circuit)
    digested = time.perf_counter()
    require(actual == receipt["dag_sha256"], "Timed digest differs")
    gc.collect()
    tracemalloc.start()
    actual = digest(circuit)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    require(actual == receipt["dag_sha256"], "Memory-run digest differs")
    gc.collect()
    tracemalloc.start()
    memory_receipt = verify()
    verify_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    require(memory_receipt == receipt, "Memory-run verification receipt differs")
    return dict(mode=mode, nodes=len(circuit.active), receipt=receipt,
                construction_seconds=built - start, verify_seconds=verified - built,
                whole_seconds=verified - start, digest_seconds=digested - verified,
                digest_traced_peak_bytes=peak, verify_traced_peak_bytes=verify_peak,
                errors=0)


def run_worker(mode):
    proc = subprocess.run(
        [sys.executable, "-I", "-W", "error", "-B", str(__file__), "--worker", mode],
        capture_output=True, text=True, check=False, timeout=120,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    require(proc.returncode == 0, "Benchmark worker failed: " + proc.stderr[-2000:])
    result = json.loads(proc.stdout)
    require(result["errors"] == 0 and result["nodes"] == 60372, "Wrong workload")
    return result


def summarize(rows):
    fields = ("verify_seconds", "whole_seconds", "digest_seconds",
              "digest_traced_peak_bytes", "verify_traced_peak_bytes")
    return {field: dict(median=statistics.median(row[field] for row in rows),
                        minimum=min(row[field] for row in rows),
                        maximum=max(row[field] for row in rows)) for field in fields}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", choices=("baseline", "streaming"))
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.worker), sort_keys=True))
        return
    require(5 <= args.rounds <= 10, "Use five to ten interleaved pairs")
    require(args.output is not None, "An external output path is required")
    output = args.output.resolve()
    require(not output.is_relative_to(fast.ROOT), "Output must be outside the checkout")
    rows = {"baseline": [], "streaming": []}
    for round_index in range(args.rounds):
        order = ("baseline", "streaming") if round_index % 2 == 0 else ("streaming", "baseline")
        pair = {mode: run_worker(mode) for mode in order}
        require(pair["baseline"]["receipt"] == pair["streaming"]["receipt"],
                "Complete receipts differ")
        for mode in order:
            rows[mode].append(pair[mode])
        print("completed pair", round_index + 1, flush=True)
    report = dict(status="PASS_DISJOINT_DAG_BENCHMARK", rounds=args.rounds,
                  summary={mode: summarize(values) for mode, values in rows.items()},
                  samples=rows, environment=dict(python=sys.version,
                      executable=sys.executable, platform=platform.platform(),
                      logical_cpus=os.cpu_count(), load_average=os.getloadavg()
                      if hasattr(os, "getloadavg") else None),
                  source_sha256={p.name: sha256(p.read_bytes()).hexdigest()
                      for p in (Path(__file__), PACKAGE / "accelerator.py")})
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
