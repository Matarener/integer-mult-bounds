"""Conformance checks for the accelerator, not a new theorem audit."""

from contextlib import redirect_stdout
import argparse
from fractions import Fraction as F
import hashlib
import io
from itertools import product
import json
from pathlib import Path

from fast_support import concrete_splits, require, support_mask
from run import PACKAGE, authenticated_bytes, load_source, replay


def literal_mask(counts, labels, targets):
    sums = {tuple(sum((u[j] * labels[j][axis] for j in range(6)), F(0))
                  for axis in range(3))
            for u in product(*(range(c + 1) for c in counts))}
    return tuple(target in sums for target in targets)


def check_small():
    labels = ((F(1, 3), 0, 0), (0, F(-1, 5), 0), (0, 0, F(1, 7)),
              (F(1, 6), F(1, 10), 0), (F(-1, 3), 0, F(1, 11)),
              (F(1, 3), 0, 0))
    targets = ((0, 0, 0), labels[0], (F(1, 6), F(1, 10), F(1, 7)),
               (F(1, 13), 0, 0))
    checked = 0
    for counts in product(range(4), repeat=6):
        if sum(counts) > 5:
            continue
        require(support_mask(counts, labels, targets)
                == literal_mask(counts, labels, targets), "small conformance")
        checked += 1
    return checked


def check_controls():
    zero = (F(0), F(0), F(0))
    axis = (F(1, 3), F(0), F(0))
    labels = (zero,) * 4 + (axis, tuple(-x for x in axis))
    targets = (axis, tuple(-x for x in axis), zero, (F(1, 6), F(0), F(0)))
    require(support_mask((0, 0, 0, 0, 1, 1), labels, targets)
            == (True, True, True, False), "signed added-label fixture")
    require(support_mask((0,) * 6, labels, targets)
            == (False, False, True, False), "zero-count fixture")
    invalid = [(9, 0, 0, 0, 0, 0), (True, 0, 0, 0, 0, 0),
               (-1, 0, 0, 0, 0, 0), (1, 1)]
    rejected = 0
    for counts in invalid:
        try:
            support_mask(counts, labels, targets)
        except ValueError:
            rejected += 1
    for value in (0.5, F(1, 1 << 257)):
        changed = ((value, 0, 0),) + labels[1:]
        try:
            support_mask((0,) * 6, changed, targets)
        except ValueError:
            rejected += 1
    require(rejected == 6, "invalid input accepted")
    try:
        authenticated_bytes(PACKAGE / "fast_support.py", "0" * 64)
    except ValueError:
        rejected += 1
    require(rejected == 7, "source mutation accepted")
    return rejected


def check_inventory(source):
    digest = hashlib.sha256()
    checked = 0
    for counts, left, right in concrete_splits(source, source.profiles(7)):
        labels = source.OLD + (left, right)
        literal = literal_mask(counts, labels, source.TARGETS)
        require(support_mask(counts, labels, source.TARGETS) == literal,
                "concrete support-mask mismatch")
        digest.update(bytes(literal))
        checked += 1
    return {"split_masks_compared": checked, "mask_sha256": digest.hexdigest()}


def check_benchmark():
    receipt = json.loads((PACKAGE / "BENCHMARK.json").read_text())
    require(receipt["errors"] == 0 and 5 <= receipt["pairs"] <= 9,
            "invalid benchmark completion")
    require(len(receipt["runs"]) == 2 * receipt["pairs"], "missing benchmark runs")
    hashes = set()
    for index, run in enumerate(receipt["runs"]):
        require(run["mode"] == ("baseline", "accelerated")[index % 2],
                "benchmark did not alternate")
        require(type(run["elapsed_ns"]) is int and run["elapsed_ns"] > 0
                and run["returncode"] == 0 and run["stderr_bytes"] == 0,
                "benchmark contains an unsuccessful command")
        hashes.add(run["stdout_sha256"])
    require(len(hashes) == 1, "benchmark outputs differ")
    for name, expected in receipt["implementation_sha256"].items():
        require(name in ("fast_support.py", "run.py", "benchmark.py", "SOURCES.json"),
                "unknown benchmark input")
        authenticated_bytes(PACKAGE / name, expected)
    require(set(receipt["implementation_sha256"])
            == {"fast_support.py", "run.py", "benchmark.py", "SOURCES.json"},
            "incomplete benchmark binding")
    return receipt["pairs"], next(iter(hashes))


def result():
    source = load_source()
    pairs, benchmark_stdout = check_benchmark()
    observed = {"small_cases": check_small(), "rejections": check_controls()}
    observed.update(check_inventory(source))
    capture = io.StringIO()
    with redirect_stdout(capture):
        replay()
    output = capture.getvalue().encode()
    require(output.endswith(b"PASS: no exact word of at most seven calls uses two "
                            b"positive rank-one frames\n"), "incomplete replay")
    observed["complete_stdout_sha256"] = hashlib.sha256(output).hexdigest()
    require(observed["complete_stdout_sha256"] == benchmark_stdout,
            "benchmark did not run this complete output")
    observed["benchmark_pairs"] = pairs
    observed["source_sha256"] = hashlib.sha256(Path(source.__file__).read_bytes()).hexdigest()
    observed["implementation_sha256"] = {
        name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
        for name in ("fast_support.py", "run.py", "verify.py", "SOURCES.json",
                     "BENCHMARK.json")}
    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="generate a receipt at this explicit path")
    args = parser.parse_args()
    observed = result()
    if args.write is not None:
        args.write.write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n")
        print("WROTE", args.write)
        return
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    require(observed == expected, "generated result differs from RESULT.json")
    print(json.dumps(observed, sort_keys=True))
    print("PASS_POSITIVE_FRAME_SUBSET_JOIN_CONFORMANCE no_new_kappa")


if __name__ == "__main__":
    main()
