"""Five alternating complete-command pairs, including startup and validation."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def measure(mode, workload):
    program = "run_replay.py" if workload == "replay" else "run_projection.py"
    command = [sys.executable, "-I", "-W", "error", "-B",
               str(ROOT / program), "--mode", mode]
    start = time.perf_counter()
    result = subprocess.run(command, capture_output=True, check=False, timeout=120)
    elapsed = time.perf_counter() - start
    if result.returncode:
        raise ValueError(result.stderr.decode())
    work = json.loads(result.stderr)
    expected_calls = 82237 if workload == "replay" else 25
    if work["gauss_calls"] != expected_calls or work["maximum_dimension"] != 128:
        raise ValueError("Changed complete-command work count")
    marker = (b"PASS_EXACT_CLIFFORD_CONTRACTIONS\n" if workload == "replay"
              else b"PASS_BITSET_GAUSS_PROJECTION\n")
    if not result.stdout.endswith(marker):
        raise ValueError("Missing complete replay marker")
    return dict(mode=mode, seconds=elapsed, stdout_sha256=sha256(result.stdout).hexdigest(),
                work=work, returncode=result.returncode)


def run(output, workload):
    if output.exists():
        raise ValueError("Refuse overwrite of benchmark evidence")
    samples = []
    for _ in range(5):
        for mode in ("baseline", "bitset"):
            samples.append(measure(mode, workload))
            print(json.dumps(samples[-1], sort_keys=True), flush=True)
    if len({row["stdout_sha256"] for row in samples}) != 1:
        raise ValueError("Different complete outputs")
    summary = {}
    for mode in ("baseline", "bitset"):
        values = [row["seconds"] for row in samples if row["mode"] == mode]
        summary[mode] = dict(median=statistics.median(values), minimum=min(values), maximum=max(values))
    report = dict(python=sys.version, executable=sys.executable, platform=platform.platform(), workload=workload,
                  errors=0, samples=samples, summary=summary,
                  source_hashes={p.name: sha256(p.read_bytes()).hexdigest()
                                 for p in (ROOT / "fast_gauss.py", ROOT / "run_replay.py",
                                           ROOT / "run_projection.py", Path(__file__))})
    with output.open("x") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workload", choices=("replay", "projection"), required=True)
    args = parser.parse_args()
    run(args.output, args.workload)
