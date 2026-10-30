"""Time complete offline commands against the pinned predecessor; write only stdout."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = "721c03822c421b7f7fcbb2598993b947c4d88419"
SCRIPT = ROOT / "scripts/find_overlap.py"
WRAPPER = """import pathlib,sys
source = pathlib.Path(sys.argv.pop(1)).read_bytes()
script = sys.argv.pop(1)
sys.argv[0] = script
exec(compile(source, script, 'exec'), {'__name__':'__main__', '__file__':script})
"""


def command(source, cache):
    return [sys.executable, "-I", "-W", "error", "-B", "-c", WRAPPER,
            str(source), str(SCRIPT), "--task", "joint-query-controller",
            "--offline", "--json", "--limit", "3", "--cache", str(cache)]


def run(source, cache):
    started = time.perf_counter()
    result = subprocess.run(command(source, cache), cwd=ROOT, capture_output=True,
                            check=True, timeout=60)
    elapsed = time.perf_counter() - started
    report = json.loads(result.stdout)
    del report["searched_at"]
    if result.stderr:
        raise ValueError("unexpected stderr: " + result.stderr.decode())
    if report["status"] != "POSSIBLE_OVERLAP_NOT_A_NOVELTY_CERTIFICATE":
        raise ValueError("wrong command status")
    return elapsed, report


def measure(cache, samples):
    if cache.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("cache exceeds the 64 MiB benchmark limit")
    before = hashlib.sha256(cache.read_bytes()).hexdigest()
    baseline = subprocess.run(
        ["git", "--no-replace-objects", "show", BASE + ":scripts/find_overlap.py"],
        cwd=ROOT, capture_output=True, check=True, timeout=30).stdout
    times = {"baseline": [], "candidate": []}
    expected = None
    with tempfile.TemporaryDirectory(prefix="overlap-benchmark-", dir=cache.parent) as tmp:
        source = Path(tmp) / "baseline.py"
        source.write_bytes(baseline)
        for _ in range(samples):
            for label, path in (("baseline", source), ("candidate", SCRIPT)):
                elapsed, report = run(path, cache)
                if expected is None:
                    expected = report
                if report != expected:
                    raise ValueError("complete reports differ beyond searched_at")
                times[label].append(elapsed)
    if hashlib.sha256(cache.read_bytes()).hexdigest() != before:
        raise ValueError("workload cache changed")
    summary = {label: {"seconds": rows, "median": statistics.median(rows),
                       "minimum": min(rows), "maximum": max(rows)}
               for label, rows in times.items()}
    coverage = dict(expected["coverage"])
    local = dict(coverage["local"])
    missing = local.pop("unsearched_head_paths")
    local["unsearched_head_paths_count"] = None if missing is None else len(missing)
    coverage["local"] = local
    return {"base": BASE, "python": sys.version, "platform": platform.platform(),
            "cache_sha256": before, "cache_bytes": cache.stat().st_size,
            "baseline_source_sha256": hashlib.sha256(baseline).hexdigest(),
            "candidate_source_sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
            "samples_per_side": samples, "errors": 0,
            "compared_complete_reports": samples * 2,
            "coverage": coverage, "matches_total": expected["matches_total"],
            "normalized_report_sha256": hashlib.sha256(json.dumps(
                expected, sort_keys=True, ensure_ascii=True).encode()).hexdigest(),
            "timing": summary,
            "reduction": 1 - summary["candidate"]["median"] / summary["baseline"]["median"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--samples", type=int, default=7, choices=range(5, 16))
    args = parser.parse_args()
    cache = args.cache.resolve(strict=True)
    if cache.is_relative_to(ROOT):
        parser.error("keep the cache outside the checkout")
    print(json.dumps(measure(cache, args.samples), indent=2))


if __name__ == "__main__":
    main()
