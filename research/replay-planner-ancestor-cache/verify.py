"""Behavioral controls for one-plan ancestor reuse. Standard library only."""
import hashlib
import json
from pathlib import Path
import stat
import statistics
import tempfile
import types
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
namespace = {"__file__": str(PACKAGE / "planner.py"), "__name__": "planner_checks"}
exec(compile((PACKAGE / "planner.py").read_bytes(), "planner.py", "exec"), namespace)
load_runner = namespace["load_runner"]
PathChecks = namespace["PathChecks"]
install = namespace["install"]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def outcome(function, root, name):
    try:
        return ("return", str(function(root, name)))
    except (OSError, ValueError, TypeError) as error:
        return (type(error).__name__, str(error))


def write(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def check_guard(root, runner):
    write(root, "shared/branch/a.txt", "a")
    write(root, "shared/branch/b.txt", "b")
    write(root, "plain", "a regular file")
    names = ["shared/branch/a.txt", "shared/branch/b.txt", "absent/child/a",
             "absent/child/b", "plain/child/a", "plain/child/b", "shared",
             "./shared", "shared//branch", "../outside", "/absolute", "",
             "shared/../plain", "shared\\branch", None, 3, [], {}]
    cache = PathChecks(root, runner.canonical_relative_path, runner.require)
    for name in names:
        expected = outcome(runner.symlink_free_relative_path, root, name)
        require(outcome(cache, root, name) == expected, "guard behavior changed")
    require(cache.hits > 0 and cache.lookups == len(cache.checked),
            "successful prefixes were not reused")
    require(cache.checked["absent"] is False and cache.checked["plain"] is False,
            "terminal component status changed")
    return len(names)


def check_aliases(root, runner):
    aliases = [("alias", "shared"), ("dangling", "missing"),
               ("leaf", "shared/branch/a.txt")]
    for name, target in aliases:
        (root / name).symlink_to(target)
    cache = PathChecks(root, runner.canonical_relative_path, runner.require)
    for name in ["alias/branch/a.txt", "dangling/child", "leaf"]:
        expected = outcome(runner.symlink_free_relative_path, root, name)
        require(expected[0] == "ValueError" and outcome(cache, root, name) == expected,
                "symlink was not rejected identically")
    original = Path.lstat

    def junction(path, *args, **kwargs):
        if path == root / "junction":
            return types.SimpleNamespace(st_mode=stat.S_IFDIR, st_reparse_tag=0xA0000003)
        return original(path, *args, **kwargs)

    with patch.object(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003, create=True), \
            patch.object(Path, "lstat", junction):
        expected = outcome(runner.symlink_free_relative_path, root, "junction/child")
        require(expected[0] == "ValueError"
                and outcome(cache, root, "junction/child") == expected,
                "junction was not rejected identically")
    return 4


def check_plan(root, baseline, candidate):
    names = ["shared/branch/a.txt", "shared/branch/b.txt"]
    for package in ("alpha", "alpha-extra", "beta"):
        write(root, "research/" + package + "/VERIFY.json",
              json.dumps({"inputs": names + names[:1]}))
    tracked = frozenset(path.relative_to(root).as_posix()
                        for path in root.rglob("*") if path.is_file() and not path.is_symlink())
    changes = [[], names[:1], names + ["research/alpha/check.py"],
               ["scripts/research_package.py"], ["shared/branch/removed.txt"]]
    original = candidate.symlink_free_relative_path
    with patch.object(baseline, "tracked_input_paths", return_value=tracked), \
            patch.object(candidate, "tracked_input_paths", return_value=tracked):
        for changed in changes:
            expected = baseline.plan_details(root, changed)
            require(candidate.plan_details(root, changed) == expected,
                    "complete plan causes or manifest hashes changed")
            require(candidate.symlink_free_relative_path is original,
                    "successful plan leaked its cache")
        write(root, "research/beta/VERIFY.json", json.dumps({"inputs": ["shared/BRANCH/a.txt"]}))
        expected = outcome(baseline.plan_details, root, names)
        require(expected[0] == "ValueError"
                and outcome(candidate.plan_details, root, names) == expected,
                "exact HEAD spelling was not retained")
        require(candidate.symlink_free_relative_path is original,
                "failing plan leaked its cache")
        write(root, "research/beta/VERIFY.json", json.dumps({"inputs": names}))
        # Same checked input becomes an alias between plans. A new plan must
        # inspect it again rather than retaining the previous plan's success.
        leaf = root / names[0]
        leaf.unlink()
        leaf.symlink_to("b.txt")
        expected = outcome(baseline.plan_details, root, names)
        require(expected[0] == "ValueError"
                and outcome(candidate.plan_details, root, names) == expected,
                "next plan reused stale filesystem validation")
        leaf.unlink()
        leaf.write_text("restored", encoding="utf-8")
        require(candidate.plan_details(root, names) == baseline.plan_details(root, names),
                "next plan failed to recover after a rejected alias")
    return len(changes) + 3


def check_failure(root, runner):
    original = Path.lstat

    def denied(path, *args, **kwargs):
        if path == root / "shared/branch":
            raise PermissionError("fixture ancestor lookup denied")
        return original(path, *args, **kwargs)

    cache = PathChecks(root, runner.canonical_relative_path, runner.require)
    with patch.object(Path, "lstat", denied):
        expected = outcome(runner.symlink_free_relative_path, root, "shared/branch/a.txt")
        require(expected[0] == "PermissionError"
                and outcome(cache, root, "shared/branch/a.txt") == expected,
                "ancestor lookup failure was swallowed")
        require("shared/branch" not in cache.checked, "a failed lookup was cached")
    require(outcome(cache, root, "shared/branch/a.txt")[0] == "return",
            "failed lookup poisoned a later retry")
    return 2


def check_source(root):
    write(root, "scripts/research_package.py", "raise RuntimeError('unauthenticated source ran')")
    try:
        load_runner(root)
    except ValueError as error:
        require(str(error) == "runner source SHA256 mismatch", "wrong source rejection")
        return 1
    raise ValueError("changed runner source was executed")


def check_benchmark():
    receipt = json.loads((PACKAGE / "BENCHMARK.json").read_text(encoding="utf-8"))
    expected = {"scripts/research_package.py"} | {
        "research/replay-planner-ancestor-cache/" + name
        for name in ("planner.py", "benchmark.py", "VERIFY.json")}
    require(set(receipt["source_sha256"]) == expected, "benchmark source coverage changed")
    for name, digest in receipt["source_sha256"].items():
        require(hashlib.sha256((PACKAGE.parents[1] / name).read_bytes()).hexdigest() == digest,
                "benchmark source hash mismatch: " + name)
    measured = receipt["measurement"]
    samples = measured["samples_seconds"]
    require(len(samples) == 2 and measured["pairs"] == 9
            and all(len(side) == 9 and all(type(x) is float and x > 0 for x in side)
                    for side in samples), "benchmark samples are incomplete")
    medians = [statistics.median(side) for side in samples]
    require(medians == measured["median_seconds"]
            and [[min(side), max(side)] for side in samples] == measured["range_seconds"]
            and 1 - medians[1] / medians[0] == measured["fraction_less_time"],
            "benchmark summary does not match samples")
    require(measured["errors"] == 0 and measured["complete_outputs_equal"] is True
            and measured["selected_packages"] == 3788 and min(samples[0]) > max(samples[1]),
            "benchmark acceptance predicate failed")
    return 1


def main():
    baseline, candidate = load_runner(), install(load_runner())
    with tempfile.TemporaryDirectory(prefix="planner-ancestor-controls-") as directory:
        root = Path(directory)
        counts = {"guard_cases": check_guard(root, baseline),
                  "alias_cases": check_aliases(root, baseline),
                  "lookup_failure_cases": check_failure(root, baseline),
                  "plan_cases": check_plan(root, baseline, candidate),
                  "source_corruption_cases": check_source(root),
                  "benchmark_receipt_cases": check_benchmark()}
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(PACKAGE.iterdir()) if path.is_file()}
    print(json.dumps({"marker": "PASS_REPLAY_PLANNER_ANCESTOR_CACHE", "cases": counts,
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
