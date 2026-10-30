#!/usr/bin/env python3
"""Actual private-copy faults; CubeJerry with OpenAI Codex, Apache-2.0."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]


def main():
    pins = json.loads((PKG / "SOURCES.json").read_text())
    inputs = [x["path"] for x in pins["files"] if x["usage"] == "input"]
    with tempfile.TemporaryDirectory(prefix="row-rounding-faults-") as scratch:
        root = Path(scratch)
        for name in inputs:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        copied = root / PKG.relative_to(ROOT)
        copied.mkdir(parents=True, exist_ok=True)
        for name in ("verify.py", "SOURCES.json", "EXPECTED.json"):
            shutil.copyfile(PKG / name, copied / name)
        argv = [sys.executable, "-I", "-B"]
        if sys.flags.optimize:
            argv.append("-O")
        argv.append(str(copied / "verify.py"))

        def run(label, error=None):
            result = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=30)
            if error is None:
                if result.returncode or "PASS_DEFERRED_ROW_ROUNDING_AUDIT" not in result.stdout:
                    raise ValueError("positive copy failed: " + label + result.stderr)
            elif not result.returncode or error not in result.stderr:
                raise ValueError("wrong rejection: " + label + result.stderr)

        run("unchanged")
        rejected = []
        for name in inputs:
            if name.endswith(("SUPPLIER-SUPPORT-AUDIT.md", "FINITE-TEMPLATE-CLOSURE.md",
                              "frontier6030/CLAIM.json")):
                target = root / name
                original = target.read_bytes()
                target.write_bytes(original + b"\nchanged-source\n")
                run(name, "source bytes:")
                target.write_bytes(original)
                rejected.append("source:" + name)

        script = copied / "verify.py"
        original = script.read_text(encoding="utf-8")
        mutations = (
            ("omit inverse shear", "lower_inverse[i+8][i] = -m",
             "lower_inverse[i+8][i] = F(0)", "full padded phase endpoint"),
            ("discard original rows", "project_rows = [[F(i == j) for j in range(12)]",
             "project_rows = [[F(i+4 == j) for j in range(12)]", "full deferred endpoint"),
            ("premature clear", '("upper", upper, True),',
             '("upper", upper, True), ("early_clear", [[F(i==j and i<8) for j in range(12)] for i in range(12)], False),',
             "full padded phase endpoint"),
            ("ignore internal padded defects", "sum(abs(v) for v in matrix[i])",
             "sum(abs(v) for v in matrix[i][:8])", "attaining defects"),
            ("omit recovery scale", "raw_error = 4 * max(map(abs, output))",
             "raw_error = max(map(abs, output))", "raw recovery needs factor four"),
            ("wrong rounding rule", "return q + (q % 2 if r else 0)",
             "return q", "independent nonlinear execution"),
        )
        for label, before, after, error in mutations:
            if original.count(before) != 1:
                raise ValueError("mutation target is not unique: " + label)
            script.write_text(original.replace(before, after), encoding="utf-8")
            run(label, error)
            script.write_text(original, encoding="utf-8")
            rejected.append(label)
        expected = copied / "EXPECTED.json"
        saved = expected.read_bytes()
        expected.unlink()
        run("missing certificate", "FileNotFoundError")
        expected.write_bytes(saved)
        rejected.append("missing certificate")
        run("restored")
    print(json.dumps({"positive_private_copies": 2, "rejected_private_mutations": rejected}, indent=2))
    print("PASS_ROW_ROUNDING_MUTATIONS")


if __name__ == "__main__":
    main()
