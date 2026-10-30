"""Check complete draft equivalence, source binding, recorded timing arithmetic and rejection controls."""
import hashlib
import json
from pathlib import Path
import runpy
import statistics
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timing_receipt():
    receipt = json.loads((PACKAGE / "MEASUREMENTS.json").read_bytes())
    paths = {"baseline": PACKAGE / "baseline.py", "candidate": ROOT / "scripts/new_research_package.py"}
    for side, path in paths.items():
        require(receipt["hashes"][side] == digest(path), "recorded generator source changed: " + side)
    require(receipt["benchmark_sha256"] == digest(PACKAGE / "benchmark.py"), "benchmark source changed")
    require(receipt["shared_reader_sha256"] == digest(ROOT / "scripts/research_package.py"), "shared reader changed")
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    old = next(row for row in pins if row["path"] == "scripts/new_research_package.py")
    require(old["sha256"] == receipt["hashes"]["baseline"], "baseline provenance differs")
    savings = {}
    require(set(receipt["workloads"]) == {"default", "eight_sources"}, "workload inventory differs")
    for name, workload in receipt["workloads"].items():
        require(type(workload["errors"]) is int and workload["errors"] == 0, "recorded creation errors")
        require(type(workload["mismatches"]) is int and workload["mismatches"] == 0, "recorded output mismatches")
        rows = workload["samples"]
        require(len(rows) == 31, "expected 31 measured pairs")
        for side in paths:
            values = [row[side] for row in rows]
            require(all(type(v) is int and v > 0 for v in values), "invalid elapsed nanoseconds")
            summary = {"median_ns": statistics.median(values), "min_ns": min(values), "max_ns": max(values)}
            require(workload["summary"][side] == summary, "recorded timing summary differs")
        a = workload["summary"]["baseline"]["median_ns"]
        b = workload["summary"]["candidate"]["median_ns"]
        savings[name] = {"saved_ns": a - b, "baseline_ns": a}
    return savings


def fixture(root):
    data = {
        "docs/research/agent-task-catalog.json": json.dumps({"priority_revision": 8,
            "tracks": [{"tasks": [{"id": "fixture", "question": "Preserve exact output bytes"}]}]}).encode(),
        "certificates/selected-result.json": b"{}\n",
        "input/empty": b"", "input/binary": bytes(range(256)), "input/unicode-\u03ba": b"literal input\n",
    }
    for name, contents in data.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
    commands = [["init", "-q"], ["add", "."], ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "fixture"]]
    for args in commands:
        subprocess.run(["git", *args], cwd=root, capture_output=True, check=True, timeout=30)


def compare_drafts():
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        baseline = runpy.run_path(str(PACKAGE / "baseline.py"))["create"]
        candidate = runpy.run_path(str(ROOT / "scripts/new_research_package.py"))["create"]
    finally:
        sys.path.pop(0)
    cases = [[], ["input/empty", "input/binary", "input/unicode-\u03ba"],
             ["docs/research/agent-task-catalog.json"] * 2 + ["certificates/selected-result.json"]]
    with tempfile.TemporaryDirectory(prefix="draft-equivalence-") as temporary:
        root = Path(temporary)
        fixture(root)
        for index, sources in enumerate(cases):
            outputs = []
            for side, create in (("baseline", baseline), ("candidate", candidate)):
                target = create(root, "fixture", "fixture", "Nick Petalas", sources)
                files = {p.name: (p.read_bytes(), p.stat().st_mode & 0o777) for p in target.iterdir()}
                require(len(files) == 5, "expected exactly five generated files")
                outputs.append(files)
                target.rename(root / f"saved-{index}-{side}")
            require(outputs[0] == outputs[1], "draft bytes or modes differ")
    return len(cases)


def main():
    savings = timing_receipt()
    cases = compare_drafts()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_research_scaffold*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    require(result.wasSuccessful(), "draft rejection/conformance suite failed")
    print(json.dumps({"status": "PASS_DRAFT_CATALOGUE_SINGLE_READ", "differential_cases": cases,
        "generated_files_compared": cases * 5, "guard_tests": result.testsRun,
        "recorded_savings": savings, "candidate_sha256": digest(ROOT / "scripts/new_research_package.py"),
        "claim_type": "empirical tooling improvement with scoped output-equivalence evidence"}, sort_keys=True))


if __name__ == "__main__":
    main()
