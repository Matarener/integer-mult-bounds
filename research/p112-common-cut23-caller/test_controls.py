#!/usr/bin/env python3
"""Actual CLI corruption controls and common-cut proof-boundary controls."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_checker():
    spec = importlib.util.spec_from_file_location("cut23_controls_target", HERE / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export_to(root):
    package = root / "research" / HERE.name
    package.mkdir(parents=True)
    for path in HERE.iterdir():
        if path.is_file() and not path.is_symlink():
            shutil.copyfile(path, package / path.name)
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            target = root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row["path"], target)
    return package


def run_cli(script, root):
    result = subprocess.run([sys.executable, "-I", "-O", "-W", "error", "-B", str(script)],
                            cwd=root, text=True, capture_output=True, timeout=60)
    return result


def changed_receipt(package, case):
    path = package / "RESULT.json"
    receipt = json.loads(path.read_text())
    if case == "understated-fourfold":
        receipt["fourfold"]["maximum"] = 13
    elif case == "unproved-direction-bound":
        receipt["theorem"]["projective_direction_bound"] = 2
    elif case == "wrong-caller":
        receipt["caller"]["new_caller"][0] = 3
    elif case == "boolean-budget":
        receipt["theorem"]["cut_budget"] = True
    else:
        raise ValueError("unknown receipt control")
    path.write_text(json.dumps(receipt))


def cli_controls():
    cases = ["source-geometry", "source-frame", "source-inventory", "manifest-usage",
             "understated-fourfold", "unproved-direction-bound", "wrong-caller", "boolean-budget"]
    with tempfile.TemporaryDirectory(prefix="cut23-controls-") as temporary:
        base = Path(temporary)
        positive = export_to(base / "positive")
        result = run_cli(positive / "verify.py", base / "positive")
        require(result.returncode == 0 and "PASS_P112_COMMON_CUT23_CALLER" in result.stdout,
                "positive optimized CLI failed: " + result.stderr)
        for case in cases:
            root = base / case
            package = export_to(root)
            if case.startswith("source-"):
                files = {"source-geometry": "research/p112-common-deletion-slice/geometry.py",
                         "source-frame": "research/p112-common-deletion-slice/FIXTURE.json",
                         "source-inventory": "research/p112-b6-t4-original-covers/RESULT.json"}
                target = root / files[case]
                target.write_bytes(target.read_bytes() + b"\n")
            elif case == "manifest-usage":
                target = package / "SOURCES.json"
                target.write_text(target.read_text().replace('"input"', '"provenance"', 1))
            else:
                changed_receipt(package, case)
            outcome = run_cli(package / "verify.py", root)
            require(outcome.returncode != 0, "CLI accepted corruption: " + case)
            expected = "source" if case.startswith("source-") else (
                "source manifest identity" if case == "manifest-usage" else "result receipt mismatch")
            require(expected in outcome.stderr, "wrong rejection path: " + case + outcome.stderr)
    return len(cases)


def proof_controls():
    checker = load_checker()
    require(checker.theorem_budget(22)["four_cut_intersection_floor"] == 18, "caller boundary")
    failures = [(24, 21, 14), (23, 20, 14), (23, 21, 15), (True, 21, 14)]
    for values in failures:
        try:
            checker.theorem_budget(*values)
        except ValueError:
            continue
        raise ValueError("invalid proof budget accepted")
    # Each direction separately passes with its own 21-site cut. Pooling those
    # cuts for four independent roots violates the one-common-set allowance.
    inputs = checker.authenticate(ROOT)
    g, roots, live, labels = checker.model(inputs)
    flats, off, _ = checker.flat_facts(g, roots, live, labels)
    ids = [2, 13, 17, 44]
    require(len(g["echelon"]([roots[i] for i in ids])) == 4,
            "separate-cut fixture must contain four independent normals")
    cuts = []
    for index in ids:
        cut = min((off[index] & ~mask for _, _, mask in flats), key=int.bit_count)
        require(cut.bit_count() == 21, "individual deletion fixture")
        residual = [labels[i] for i in range(112) if off[index] >> i & 1 and not (cut >> i & 1)]
        require(checker.binary_rank(residual) == 7, "separate-cut positive fixture")
        cuts.append(cut)
    common = cuts[0] | cuts[1] | cuts[2] | cuts[3]
    require(common.bit_count() > 23, "separate cuts silently pooled")
    # Exercise the actual finite-mathematics gate after authentication, rather
    # than counting only receipt/source-hash rejection as semantic coverage.
    shared = off[ids[0]] & off[ids[1]] & off[ids[2]] & off[ids[3]]
    require(shared.bit_count() == 14, "fourfold attainment fixture")
    extra = next(i for i in range(112) if not (shared >> i & 1))
    altered = list(off)
    for index in ids:
        altered[index] |= 1 << extra
    try:
        checker.fourfold_facts(roots, altered)
    except ValueError as error:
        require("fourfold support maximum" in str(error), "wrong semantic rejection")
    else:
        raise ValueError("fourfold gate accepted an explicit15-site intersection")
    return {"rejected_budget_cases": len(failures), "separate_cut_union": common.bit_count(),
            "fourfold_semantic_mutations": 1}


def main():
    count = cli_controls()
    proof = proof_controls()
    print("PASS_COMMON_CUT23_CONTROLS", count, "rejecting optimized CLI runs;", proof)


if __name__ == "__main__":
    main()
