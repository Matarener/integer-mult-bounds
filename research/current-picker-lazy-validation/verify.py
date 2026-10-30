#!/usr/bin/env python3
"""Exact current-picker conformance; produced by Nick Petalas, Apache-2.0."""
import copy
import hashlib
import json
from pathlib import Path
import runpy
import statistics
import tempfile
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SCRIPT = "scripts/choose_current_research_task.py"
LEGACY = "scripts/choose_research_task.py"
LOAD = 'check_catalog_files = runpy.run_path(str(LEGACY))["check_catalog_files"]\n'
ANCHOR = 'LEGACY = ROOT / "scripts/choose_research_task.py"\n'
REQUIRED = (
    "scripts/research_selected_baseline.py", "scripts/research_package.py",
    "research/historical-complex-ceiling-replay/VERIFY.json",
    "research/historical-complex-ceiling-replay/verify.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reconstruct(after):
    require(after.count("    " + LOAD) == 1, "missing unique deferred load")
    require(after.count(ANCHOR) == 1, "missing unique legacy path")
    require("\n" + LOAD not in after, "eager legacy load remains")
    return after.replace("    " + LOAD, "").replace(ANCHOR, ANCHOR + LOAD)


def sources():
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    expected = {row["path"]: row["sha256"] for row in pins}
    legacy = (ROOT / LEGACY).read_bytes()
    require(digest(legacy) == expected[LEGACY], "legacy source drift")
    after = (ROOT / SCRIPT).read_text(encoding="utf-8")
    before = reconstruct(after)
    require(digest(before.encode()) == expected[SCRIPT], "baseline source drift")
    return before, after


def namespace(source):
    result = {"__name__": "picker_conformance", "__file__": str(ROOT / SCRIPT)}
    exec(compile(source, str(ROOT / SCRIPT), "exec"), result)
    return result


def rejected(call):
    try:
        call()
    except ValueError as error:
        return str(error)
    raise ValueError("negative control was accepted")


def suggestion(command):
    return {"suggestions": [{"first_step": {"command": command}}]}


def route_controls(old, new):
    controls = 0
    commands = (["python3", "-B", "scripts/research_baseline.py"],
                ["python3", "-B", "research/complex-local-word-ceiling/verify.py"])
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in REQUIRED:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("inert entry reference\n", encoding="utf-8")
        for command in commands:
            left, right = suggestion(command), suggestion(command)
            require(old(left, root) == new(right, root), "route omissions differ")
            require(left == right, "historical route output differs")
        for absent in REQUIRED:
            path = root / absent
            path.unlink()
            original = suggestion(commands[1])
            left, right = copy.deepcopy(original), copy.deepcopy(original)
            a = rejected(lambda: old(left, root))
            b = rejected(lambda: new(right, root))
            require(a == b and left == right == original, "route rejection drift")
            path.write_text("inert entry reference\n", encoding="utf-8")
            controls += 1
    return controls


def timing_receipt(before, after):
    record = json.loads((PACKAGE / "BENCHMARK.json").read_bytes())
    require(record["before_sha256"] == digest(before.encode()) and
            record["after_sha256"] == digest(after.encode()), "timing source mismatch")
    require(record["benchmark_sha256"] == digest((PACKAGE / "benchmark.py").read_bytes()),
            "timing driver mismatch")
    require(type(record["errors"]) is int and record["errors"] == 0, "timing failures")
    require(record["pairs"] == 9 and record["repetitions_per_batch"] == 10 and
            record["successful_timed_commands"] == 180, "timing work count")
    samples = record["samples_seconds_per_command"]
    for side in ("before", "after"):
        values = samples[side]
        require(len(values) == 9 and all(type(x) is float and 0 < x < 20 for x in values),
                "invalid timing samples")
        require(statistics.median(values) == record["medians_seconds"][side] and
                [min(values), max(values)] == record["ranges_seconds"][side],
                "timing summary mismatch")
    medians = record["medians_seconds"]
    require(record["fraction_less_wall_time"] == 1 - medians["after"] / medians["before"],
            "timing ratio mismatch")
    return sum(a > b for a, b in zip(samples["before"], samples["after"]))


def check():
    before, after = sources()
    paired_wins = timing_receipt(before, after)
    with patch("runpy.run_path", wraps=runpy.run_path) as calls:
        old = namespace(before)["resolve_current_first_steps"]
        require(calls.call_count == 1, "baseline did not load eagerly")
        calls.reset_mock()
        new = namespace(after)["resolve_current_first_steps"]
        require(calls.call_count == 0, "candidate loaded legacy eagerly")
        unchanged = suggestion(["python3", "-B", "scripts/research_selected_baseline.py"])
        original = copy.deepcopy(unchanged)
        require(new(unchanged, ROOT) == [] and unchanged == original,
                "current route changed")
        require(calls.call_count == 0, "unused validation loaded legacy")
    catalog = json.loads((ROOT / "docs/research/agent-task-catalog.json").read_bytes())
    cards = [card for track in catalog["tracks"] for card in track["tasks"]]
    require(1 <= len(cards) <= 1000, "catalog size outside verifier bound")
    for card in cards:
        left = {"suggestions": [{"first_step": copy.deepcopy(card["first_step"])}]}
        right = copy.deepcopy(left)
        require(old(left, ROOT) == new(right, ROOT) and left == right,
                "live first-step output differs")
    controls = route_controls(old, new)
    for mutant in (after.replace("    " + LOAD, ""), after + "\n" + LOAD,
                   after.replace(ANCHOR, ANCHOR + "# changed\n")):
        rejected(lambda: require(digest(reconstruct(mutant).encode()) == digest(before.encode()),
                                 "baseline source drift"))
        controls += 1
    return {"status": "PASS_CURRENT_PICKER_LAZY_VALIDATION", "live_cards": len(cards),
            "route_fixtures": 2, "negative_controls": controls, "paired_timing_wins": paired_wins,
            "before_sha256": digest(before.encode()), "after_sha256": digest(after.encode())}


if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True))
