#!/usr/bin/env python3
"""Replay the saved positive-hint certificate; receipts never replace execution."""
from dataclasses import asdict
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    for row in pins["files"]:
        raw = (HERE / row["path"]).read_bytes()
        require(len(raw) == row["bytes"], "source size: " + row["path"])
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"], "source blob: " + row["path"])
    checker = load("checker", HERE / "checker.py")
    controls = load("lrat_controls", HERE / "test_checker.py")
    result = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(controls))
    require(result.wasSuccessful(), "semantic controls failed: " + repr(result.errors + result.failures))
    actual = asdict(checker.check(HERE / "source/length7.cnf", HERE / "length7.lrat.gz"))
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), "complete typed replay receipt differs")
    require(actual["status"] == "verified_unsat" and actual["final_empty"] is True, "missing actual refutation")
    print("PASS_GL3_INDEPENDENT_LRAT " + json.dumps(dict(receipt=actual, controls=result.testsRun, source_inputs=len(pins["files"]), length8_independent_replay=False), sort_keys=True))


if __name__ == "__main__":
    main()
