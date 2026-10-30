"""Generate complete-command timing evidence; never run by the generic replay."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def run(argv, cwd):
    started = time.perf_counter_ns()
    result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=60, check=True)
    return result, (time.perf_counter_ns() - started) / 1_000_000_000


def benchmark(pairs):
    common = [sys.executable, "-I", "-W", "error", "-B"]
    suffix = ["--changed-since", "0" * 40]
    commands = [common + [str(ROOT / "scripts/research_package.py")] + suffix,
                common + [str(PACKAGE / "planner.py")] + suffix]
    samples, reference = [[], []], None
    for pair in range(pairs):
        for side in ((0, 1) if pair % 2 == 0 else (1, 0)):
            result, seconds = run(commands[side], ROOT)
            observed = (result.stdout, result.stderr)
            if reference is None:
                reference = observed
            if observed != reference:
                raise ValueError("complete planner output or warning changed")
            samples[side].append(seconds)
    assert reference is not None
    include = json.loads(reference[0])["include"]
    medians = [statistics.median(side) for side in samples]
    return {"commands": commands, "pairs": pairs, "samples_seconds": samples,
            "median_seconds": medians,
            "range_seconds": [[min(side), max(side)] for side in samples],
            "fraction_less_time": 1 - medians[1] / medians[0], "errors": 0,
            "complete_outputs_equal": True, "selected_packages": len(include),
            "stdout_sha256": sha256(reference[0]), "stderr_sha256": sha256(reference[1]),
            "stderr": reference[1].decode("utf-8")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs", type=int, default=9, choices=range(5, 21))
    args = parser.parse_args()
    head, _ = run(["git", "rev-parse", "HEAD"], ROOT)
    tracked, _ = run(["git", "ls-tree", "-r", "--name-only", "-z", "HEAD"], ROOT)
    sparse, _ = run(["git", "sparse-checkout", "list"], ROOT)
    result = {"schema_version": 1, "claim_type": "empirical tooling improvement",
              "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "head": head.stdout.decode().strip(), "python": sys.version,
              "platform": platform.platform(), "tracked_paths_sha256": sha256(tracked.stdout),
              "sparse_checkout_sha256": sha256(sparse.stdout),
              "source_sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes())
                                for path in [ROOT / "scripts/research_package.py", PACKAGE / "planner.py",
                                             PACKAGE / "benchmark.py", PACKAGE / "VERIFY.json"]},
              "measurement": benchmark(args.pairs)}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["measurement"], sort_keys=True))


if __name__ == "__main__":
    main()
