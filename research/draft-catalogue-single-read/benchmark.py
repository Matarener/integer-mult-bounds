"""Measure complete draft-creation commands; move every draft to the supplied scratch directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "a5bff3bf133e482541c09eba4e773884bdb2b1b7"
SOURCES = [
    "AGENTS.md", "CONTRIBUTING.md", "autoresearch.md",
    "docs/research/current-priorities.md", "docs/research/agent-procedure.md",
    "docs/research/research-package-guide.md", "certificates/frontier6030-source.json",
    "docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(directory):
    files = sorted(directory.iterdir())
    if {p.name for p in files} != {"README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"}:
        raise ValueError("the command did not produce exactly the five draft files")
    return {p.name: {"sha256": digest(p), "mode": p.stat().st_mode & 0o777} for p in files}


def run_command(script, scratch, label, sources, slug):
    target = ROOT / "research" / slug
    if target.exists() or target.is_symlink():
        raise ValueError("benchmark output already exists: " + str(target))
    env = dict(os.environ, PYTHONPATH=str(ROOT / "scripts"), TMPDIR=str(scratch))
    env.pop("PYTHONOPTIMIZE", None)
    argv = [sys.executable, "-W", "error", "-B", str(script), slug,
            "--task", "replay-runtime", "--author", "Nick Petalas", "--base", BASE]
    for name in sources:
        argv.extend(["--source", name])
    start = time.perf_counter_ns()
    try:
        result = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, timeout=30)
        elapsed = time.perf_counter_ns() - start
    finally:
        # The name was absent above and is owned by this invocation only.
        # Move even a partial draft out of the checkout on failure/interruption.
        if target.exists():
            target.rename(scratch / label)
    if result.returncode != 0 or result.stderr:
        raise ValueError("creation failed: " + result.stderr.decode(errors="replace"))
    expected = (str(target) + "\nDRAFT ONLY: complete scope, evidence, open questions and verifier; "
                "the stub deliberately fails.\n").encode()
    if result.stdout != expected:
        raise ValueError("unexpected complete-command stdout")
    return elapsed, snapshot(scratch / label)


def measure(scratch, samples):
    scripts = {"baseline": scratch / "baseline.py", "candidate": scratch / "candidate.py"}
    originals = {"baseline": PACKAGE / "baseline.py", "candidate": ROOT / "scripts/new_research_package.py"}
    for side, source in originals.items():
        scripts[side].write_bytes(source.read_bytes())
    slug = "draft-runtime-probe-" + scratch.name.lower().replace("_", "-")[-30:]
    # Explicitly cap the generated slug independently of the caller's path spelling.
    slug = "draft-runtime-probe-" + hashlib.sha256(slug.encode()).hexdigest()[:16]
    results = {}
    for workload, sources in (("default", []), ("eight_sources", SOURCES)):
        reference = None
        rows = []
        for index in range(samples + 1):
            # One unreported warm-up pair, followed by alternating A/B and B/A pairs.
            order = ("baseline", "candidate") if index % 2 == 0 else ("candidate", "baseline")
            row = {}
            for side in order:
                label = f"{workload}-{index:03}-{side}"
                elapsed, outputs = run_command(scripts[side], scratch, label, sources, slug)
                if reference is None:
                    reference = outputs
                if outputs != reference:
                    raise ValueError("five-file output/mode mismatch: " + label)
                row[side] = elapsed
            if index:
                rows.append(row)
        summaries = {}
        for side in scripts:
            values = [row[side] for row in rows]
            summaries[side] = {"median_ns": statistics.median(values), "min_ns": min(values), "max_ns": max(values)}
        results[workload] = {"sources": sources, "samples": rows, "summary": summaries,
                             "output_files": reference, "errors": 0, "mismatches": 0}
    return {"schema_version": 1, "base": BASE, "python": sys.version,
            "platform": platform.platform(), "processor": platform.processor(), "cpu_count": os.cpu_count(),
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            "hashes": {side: digest(path) for side, path in originals.items()},
            "benchmark_sha256": digest(Path(__file__)), "shared_reader_sha256": digest(ROOT / "scripts/research_package.py"),
            "workloads": results, "scope": "Whole fresh Python CLI process through all five file writes; validation outside timer."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=31)
    args = parser.parse_args()
    if not 5 <= args.samples <= 101:
        parser.error("samples must be between 5 and 101")
    scratch = args.scratch.resolve()
    scratch.mkdir(parents=True, exist_ok=False)
    print(json.dumps(measure(scratch, args.samples), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
