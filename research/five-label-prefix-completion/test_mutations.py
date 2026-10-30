#!/usr/bin/env python3
"""Actual optimized-Python mutants with receipt comparison disabled.
Prepared for SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
MUTATIONS = (
    ("independent_future_pairs", "if not joint:", "if True:"),
    ("drop_old_pairs", "possible = pair_support(points)", "possible = 0"),
    ("drop_old_new_pairs", "possible |= 1 << (old ^ new)", "possible |= 0"),
    ("strict_vertex_boundary", "+ x.bit_count() <= remaining)", "+ x.bit_count() < remaining)"),
    ("omit_closing_edge", "remaining = length - len(points) + 1", "remaining = length - len(points)"),
    ("omit_return_distance", "and (last ^ x).bit_count() + x.bit_count() <= remaining)", "and (last ^ x).bit_count() <= remaining)"),
    ("disable_geometric_traversal_filter",
     "return len(future) < 12 - len(points) or possible != (1 << 32) - 2", "return False"),
)


def run(directory, emit=False):
    args = [sys.executable, "-I", "-O", "-B", str(directory / "verify.py")]
    if emit:
        args.append("--emit-receipt")
    return subprocess.run(args, cwd=directory, capture_output=True, timeout=60)


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="five-label-prefix-") as temp:
        root = Path(temp)
        for source in HERE.iterdir():
            if source.is_file():
                shutil.copyfile(source, root / source.name)
        positive = run(root)
        if positive.returncode != 0 or b"PASS_FIVE_LABEL_PREFIX_COMPLETION" not in positive.stdout:
            raise ValueError("source-only optimized positive control: " + positive.stderr.decode(errors="replace"))
        original = (root / "bounds.py").read_text(encoding="utf-8")
        for name, before, after in MUTATIONS:
            if original.count(before) != 1:
                raise ValueError("mutation target not unique: " + name)
            (root / "bounds.py").write_text(original.replace(before, after), encoding="utf-8", newline="\n")
            result = run(root, emit=True)
            if result.returncode == 0:
                raise ValueError("surviving semantic/claim mutant: " + name)
            results.append({"name": name, "rejected": True,
                            "last_error": result.stderr.decode(errors="replace").splitlines()[-1]})
            (root / "bounds.py").write_text(original, encoding="utf-8", newline="\n")
        receipt = (root / "RESULT.json").read_bytes()
        altered = json.loads(receipt)
        altered["oracle"]["simple_universal"] = True
        (root / "RESULT.json").write_text(json.dumps(altered), encoding="utf-8")
        result = run(root)
        if result.returncode == 0 or b"complete deterministic receipt equality" not in result.stderr:
            raise ValueError("typed receipt mutation not rejected by equality")
        results.append({"name": "typed_receipt_boolean", "rejected": True})
        (root / "RESULT.json").write_bytes(receipt)
        proof = root / "PROOF.md"
        proof.write_bytes(proof.read_bytes() + b"\n")
        result = run(root)
        if result.returncode == 0 or b"complete deterministic receipt equality" not in result.stderr:
            raise ValueError("proof-byte mutation not rejected by binding")
        results.append({"name": "proof_byte_binding", "rejected": True})
    print(json.dumps({"positive_source_only_optimized": "PASS", "controls": results}, indent=2))


if __name__ == "__main__":
    main()

