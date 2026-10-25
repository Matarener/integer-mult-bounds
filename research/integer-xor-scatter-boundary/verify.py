"""Composed integer-label and XOR boundary evidence. Apache-2.0."""

import argparse
import copy
import gzip
import hashlib
import json
import sys
import tempfile
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import boundary  # noqa: E402

WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
XOR = "research/xor-scatter-boundary/boundary.py"
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sources(root):
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    for row in pins:
        if row["usage"] == "input":
            body = (root / row["path"]).read_bytes()
            require(hashlib.sha256(body).hexdigest() == row["sha256"], "input pin")
    word = json.loads(gzip.decompress((root / WORD).read_bytes()))
    module = types.ModuleType("authenticated_xor_predecessor")
    module.__file__ = str(root / XOR)
    exec(compile((root / XOR).read_bytes(), XOR, "exec", optimize=0), module.__dict__)
    return word, module


def fixture(word, fractional=False, paired=False):
    result = copy.deepcopy(word)
    if fractional:
        result["lines"][0][1] = 0.5
    if paired:
        result["scatter"][0].extend([0, 0])
    return result


def artifacts(path):
    return {
        name: hashlib.sha256((path / name).read_bytes()).hexdigest()
        for name in ARTIFACTS
    }


def reject(word, name, directory, root):
    path, output = directory / (name + ".json"), directory / name
    path.write_text(json.dumps(word), encoding="utf-8")
    before = path.read_bytes()
    try:
        boundary.execute("export", path, output, root, directory)
    except ValueError:
        pass
    else:
        raise ValueError("invalid word accepted: " + name)
    require(not output.exists(), "rejection published output")
    require(path.read_bytes() == before, "rejection changed input")
    return True


def audit(root, directory):
    word, old = sources(root)
    require(word["lines"][0] == [2, 0, 0, 0, 0, 0, 0, 0], "label fixture")
    require(word["scatter"][0] == [4, 5, 6, 7, 8], "scatter fixture")
    accepted, rejected = {}, {}
    for name, paired in (("baseline", False), ("paired", True)):
        value = fixture(word, paired=paired)
        path, output = directory / (name + ".json"), directory / name
        path.write_text(json.dumps(value), encoding="utf-8")
        before = path.read_bytes()
        boundary.execute("export", path, output, root, directory)
        require(path.read_bytes() == before, "export changed input")
        accepted[name] = artifacts(output)
    require(accepted["baseline"] == accepted["paired"], "paired repair byte identity")
    baseline_path = directory / "baseline.json"
    old.execute("export", baseline_path, directory / "old-baseline", root, directory)
    require(
        artifacts(directory / "old-baseline") == accepted["baseline"],
        "predecessor baseline byte identity",
    )
    old.delegate(
        old.scripts(root)[old.EXPORTER],
        baseline_path,
        directory,
        "raw-exporter.py",
        directory / "raw-baseline",
    )
    require(
        artifacts(directory / "raw-baseline") == accepted["baseline"],
        "raw selected artifact byte identity",
    )
    for paired in (False, True):
        name = "fractional_paired" if paired else "fractional"
        value = fixture(word, fractional=True, paired=paired)
        rejected[name] = reject(value, name, directory, root)
        old_output = directory / ("old-" + name)
        old.execute("export", directory / (name + ".json"), old_output, root, directory)
        require(
            artifacts(old_output)["frames.json"] != accepted["baseline"]["frames.json"],
            "known predecessor geometry discrepancy not reproduced",
        )
    bad = fixture(word, paired=True)
    bad["lines"][0][1] = 1
    rejected["integer_wrong_geometry"] = reject(
        bad, "integer_wrong_geometry", directory, root
    )
    bad = fixture(word)
    bad["scatter"][0].append(0)
    rejected["wrong_endpoint"] = reject(bad, "wrong_endpoint", directory, root)
    return {
        "status": "PASS_INTEGER_XOR_SCATTER_BOUNDARY",
        "accepted": accepted,
        "rejected": rejected,
        "predecessor_fractional_exports": 2,
        "selected_artifacts_unchanged": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="integer-xor-audit-") as temporary:
        result = audit(boundary.ROOT, Path(temporary))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
        require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "typed deterministic evidence differs",
        )
        print(result["status"], "no_new_kappa")


if __name__ == "__main__":
    main()
