#!/usr/bin/env python3
"""Fresh-process complete CLI timing; produced by Nick Petalas, Apache-2.0."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SCRIPT = ROOT / "scripts/choose_current_research_task.py"
ARGS = ["--seed", "0" * 32, "--task", "replay-runtime"]
# Both sides execute the complete CLI in a fresh process with the real __file__.
# Only the source bytes differ. The legacy subprocess and Git queries still run.
LAUNCH = (
    "import pathlib,sys; p=sys.argv.pop(1); "
    "f=sys.argv[0]=str(pathlib.Path.cwd()/'scripts/choose_current_research_task.py'); "
    "exec(compile(pathlib.Path(p).read_bytes(),f,'exec'),"
    "{'__name__':'__main__','__file__':f})"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_pair():
    spec = importlib.util.spec_from_file_location("picker_check", PACKAGE / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.sources()


def invoke(source):
    command = [sys.executable, "-B", "-c", LAUNCH, str(source), *ARGS]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=20)
    require(result.returncode == 0, "complete command failed: " + repr(result.stderr))
    require(len(result.stdout) <= 1024 * 1024, "unexpected output size")
    output = (result.returncode, result.stdout, result.stderr)
    report = json.loads(result.stdout)
    require(report["suggestions"][0]["task_id"] == "replay-runtime", "wrong work")
    return output


def measure(pairs, repetitions, scratch):
    before, after = source_pair()
    samples = {"before": [], "after": []}
    outputs = {}
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        sources = {}
        for side, source in (("before", before), ("after", after)):
            path = Path(directory) / (side + ".py")
            require(path.write_text(source, encoding="utf-8") == len(source), "short source write")
            sources[side] = path
        for pair in range(pairs):
            order = ("before", "after") if pair % 2 == 0 else ("after", "before")
            for side in order:
                started = time.perf_counter()
                for _ in range(repetitions):
                    output = invoke(sources[side])
                    outputs.setdefault(side, output)
                    require(output == outputs[side], "unstable complete output")
                samples[side].append((time.perf_counter() - started) / repetitions)
        require(outputs["before"] == outputs["after"], "changed complete output")
        direct = subprocess.run([sys.executable, "-B", str(SCRIPT), *ARGS], cwd=ROOT,
                                capture_output=True, timeout=20)
        require((direct.returncode, direct.stdout, direct.stderr) == outputs["after"],
                "launcher differs from direct CLI")
    medians = {side: statistics.median(values) for side, values in samples.items()}
    return {
        "schema": "current-picker-complete-timing/1", "pairs": pairs,
        "repetitions_per_batch": repetitions, "successful_timed_commands": 2 * pairs * repetitions,
        "errors": 0, "direct_cli_controls": 1, "argv": ARGS, "launcher": LAUNCH,
        "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
        "cpu_count": os.cpu_count(), "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
        "samples_seconds_per_command": samples, "medians_seconds": medians,
        "ranges_seconds": {side: [min(v), max(v)] for side, v in samples.items()},
        "fraction_less_wall_time": 1 - medians["after"] / medians["before"],
        "stdout_sha256": hashlib.sha256(outputs["after"][1]).hexdigest(),
        "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
        "after_sha256": hashlib.sha256(after.encode()).hexdigest(),
        "benchmark_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "Complete source-executed CLI, fresh interpreter per command; same launcher on both sides. Timing includes JSON decoding and output equality checks. No speed guarantee on other hosts or mapped historical routes.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=9)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    require(5 <= args.pairs <= 31 and 1 <= args.repetitions <= 100, "timing bounds")
    result = measure(args.pairs, args.repetitions, args.scratch)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        with args.write.open("x", encoding="utf-8") as output:
            require(output.write(text) == len(text), "short receipt write")
    print(text, end="")


if __name__ == "__main__":
    main()
