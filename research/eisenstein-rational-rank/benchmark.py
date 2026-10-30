"""Measure one complete, authenticated fixture; write only a new external file."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import replay
from rational_rank import rank, require
from verify import capture_fixture, fixture_digest


def full_sample(mode, expected):
    command = [sys.executable, "-W", "error", "-I", "-O", "-B", str(HERE / "replay.py")]
    if mode == "baseline":
        command.append("--original")
    start = time.perf_counter()
    done = subprocess.run(command, capture_output=True, timeout=30, check=False)
    elapsed = time.perf_counter() - start
    require(done.returncode == 0 and not done.stderr, "timed replay failed")
    require(done.stdout == expected, "timed complete output differs")
    return elapsed


def kernel_sample(mode, matrices, expected, original):
    start = time.perf_counter()
    if mode == "baseline":
        results = [original(matrix, "Q") for matrix in matrices]
    else:
        results = [rank(matrix) for matrix in matrices]
    elapsed = time.perf_counter() - start
    require(results == expected, "timed Q results differ")
    return elapsed


def summarize(samples):
    return {mode: {"median": statistics.median(values), "min": min(values), "max": max(values)}
            for mode, values in samples.items()}


def measurements(pairs):
    matrices, expected_ranks, output = capture_fixture()
    original, _ = replay.load()
    full = {"baseline": [], "integer": []}
    kernels = {"baseline": [], "integer": []}
    order = []
    for pair in range(pairs + 1):
        modes = ("baseline", "integer") if pair % 2 == 0 else ("integer", "baseline")
        for mode in modes:
            elapsed = full_sample(mode, output.encode())
            kernel = kernel_sample(mode, matrices, expected_ranks, original.rank)
            if pair:
                full[mode].append(elapsed)
                kernels[mode].append(kernel)
                order.append([pair, mode])
    full_summary, kernel_summary = summarize(full), summarize(kernels)
    ratio = full_summary["baseline"]["median"] / full_summary["integer"]["median"]
    return {"full_seconds": full, "Q_seconds": kernels, "order": order,
            "full_summary": full_summary, "Q_summary": kernel_summary, "full_speed_ratio": ratio,
            "Q_call_digest": fixture_digest(matrices, expected_ranks),
            "complete_stdout_sha256": hashlib.sha256(output.encode()).hexdigest(),
            "rank_calls_per_complete_run": replay.EXPECTED_CALLS, "errors": 0,
            "pairs": pairs, "discarded_warmup_pairs": 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs", type=int, default=6)
    args = parser.parse_args()
    require(5 <= args.pairs <= 12, "use five through twelve timing pairs")
    destination = args.output.resolve()
    require(not destination.is_relative_to(replay.ROOT), "timing output must be outside checkout")
    require(not destination.exists(), "timing output must be new")
    result = measurements(args.pairs)
    result.update({"python": platform.python_version(), "platform": platform.platform(),
                   "machine": platform.machine(), "interpreter": sys.executable,
                   "adapter_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                      for name in ("rational_rank.py", "replay.py", "benchmark.py", "verify.py")},
                   "scope": "Same complete fixture and K adapter; only Q-rank changes. Fresh-process wall time includes imports and source authentication. Kernel samples execute all 209 actual matrices. Shared-host load is uncontrolled; no universal speed guarantee."})
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"full": result["full_summary"], "Q": result["Q_summary"],
                      "ratio": result["full_speed_ratio"], "errors": result["errors"]}, indent=2))


if __name__ == "__main__":
    main()
