#!/usr/bin/env python3
"""Exercise the real CLI on private copies, including scientific mutants.

conorholds, with OpenAI Codex assistance. Apache-2.0.
No predecessor or original package file is modified.
"""

from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def snapshot():
    return {str(p.relative_to(PACKAGE)): sha256(p.read_bytes()).hexdigest()
            for p in PACKAGE.rglob("*") if p.is_file()}


def main():
    before = snapshot()
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    checked = []
    with tempfile.TemporaryDirectory(prefix="p112-six-seven-controls-") as temp:
        root = Path(temp) / "tree"
        package = root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.olean"))
        for row in sources["files"]:
            if row["usage"] == "input":
                target = root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / row["path"]).read_bytes())

        def cli(expected, message=None, sources_only=False):
            args = [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")]
            if sources_only:
                args.append("--sources-only")
            result = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=90)
            output = result.stdout + result.stderr
            need(result.returncode == expected,
                 "actual CLI returned an unexpected exit status: " + output)
            if message:
                need(message in output, "actual CLI rejected for the wrong reason: " + output)

        cli(0, "PASS_P112_SIX_SEVEN_SUPPLEMENT")
        checked.append("complete optimized Git-free positive")
        cli(0, "source-integrity-only", sources_only=True)
        manifest_path = package / "SOURCES.json"
        manifest_bytes = manifest_path.read_bytes()
        for relabel in (False, True):
            broken = json.loads(manifest_bytes)
            index = next(i for i, row in enumerate(broken["files"]) if row["usage"] == "input")
            if relabel:
                broken["files"][index]["usage"] = "provenance"
            else:
                broken["files"].pop(index)
            manifest_path.write_text(json.dumps(broken))
            cli(1, "source inventory differs from consumed inputs", sources_only=True)
            manifest_path.write_bytes(manifest_bytes)
        checked.append("missing or relabeled consumed source pin rejected")
        for relative, message in (
            ("research/p112-root-simplex-exclusion/geometry.py", "live source hash differs"),
            ("research/one-sided-decoders-all-m/data/data.json", "live source hash differs"),
            (str((package / "inputs/pr3154/land_e2_k8.out").relative_to(root)),
             "retained PR source hash differs"),
        ):
            path = root / relative
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            cli(1, message, sources_only=True)
            path.write_bytes(original)
        checked.append("two changed live sources and changed retained caller rejected")

        caller = package / "inputs/pr3154/land_e2_k8.out"
        original = caller.read_bytes()
        respaced = original.replace(b"'LP': 0", b"'LP':  0", 1)
        need(respaced != original, "retained caller spacing anchor changed")
        caller.write_bytes(respaced)
        repinned = json.loads(manifest_bytes)
        row = next(row for row in repinned["retained_pr_sources"]
                   if row["retained_path"] == "inputs/pr3154/land_e2_k8.out")
        row["sha256"] = sha256(caller.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(repinned))
        cli(0, "source-integrity-only", sources_only=True)
        cli(1, "scientific receipt or JSON types differ")
        caller.write_bytes(original)
        manifest_path.write_bytes(manifest_bytes)
        checked.append("repinned caller bytes invalidate the frozen receipt")

        linked = root / "research/p112-root-simplex-exclusion/geometry.py"
        original = linked.read_bytes()
        saved = linked.with_suffix(".saved")
        saved.write_bytes(original)
        linked.unlink()
        linked.symlink_to(saved.name)
        cli(1, "linked source input", sources_only=True)
        linked.unlink()
        linked.write_bytes(original)
        saved.unlink()
        checked.append("linked source rejected")

        path = package / "model.py"
        source = path.read_text()
        mutations = [
            ("self.neighbors[i] | (1 << i)", "self.neighbors[i]",
             "root off-support convention", "omit actual root self"),
            ("section == g.neighbors[v] & ~g.neighbors[w]",
             "section == g.neighbors[v] & g.neighbors[w]",
             "wrong orthogonal completion orientation", "reverse completion half"),
            ("for a in range(1, 256):", "for a in range(2, 256):",
             "incomplete affine/root domain or wrong cap", "omit affine annihilator family"),
            ("target = g.off[v] & g.live", "target = g.neighbors[v] & g.live",
             "sharp witness changed", "drop self only in claimed sharp witness"),
            ("if low.bit_count() != 16 or low & g.frame:",
             "if low.bit_count() != 16 or low & g.live:",
             "uniform optimal-cover count", "confuse frame and live sites in the uniform construction"),
            ("for coefficient in (1, -1, 2):", "for coefficient in (1, -1, 0):",
             "frame-plane rank or one-point deletion failed", "replace generic two-axis stratum by an axis"),
            ("if g.dots[a][site] * g.dots[b][site] > 0",
             "if g.dots[a][site] * g.dots[a][site] > 0",
             "frame sign-half partition", "erase the second frame axis from coefficient-sign partition"),
        ]
        for old, new, message, name in mutations:
            need(source.count(old) == 1, "mutation anchor changed")
            path.write_text(source.replace(old, new))
            cli(1, message)
            path.write_text(source)
            checked.append(name)

        actual_path = package / "actual_controls.py"
        actual_source = actual_path.read_text()
        anchor = "scale * value / 2 - coefficient * pivot_unit[i]"
        need(actual_source.count(anchor) == 1, "actual factorization mutation anchor changed")
        actual_path.write_text(actual_source.replace(anchor, anchor.replace(" - ", " + ")))
        cli(1, "actual d1 consumer is not the exact Gram factorization")
        actual_path.write_text(actual_source)
        checked.append("wrong actual singleton compensation sign rejected by Gram entries")

        d2_path = package / "d2_controls.py"
        d2_source = d2_path.read_text()
        anchor = "high[j] = [x - scalar*y for x, y in zip(high[j], high[chosen])]"
        need(d2_source.count(anchor) == 1, "actual d2 marked shear mutation anchor changed")
        d2_path.write_text(d2_source.replace(anchor, anchor.replace(" - ", " + ")))
        cli(1, "actual d2 restricted dual expansion")
        d2_path.write_text(d2_source)
        checked.append("wrong actual d2 marked shear rejected by restricted dual expansion")

        independent_path = package / "independent.py"
        independent_source = independent_path.read_text()
        anchor = '"qualifying29": len(qualifying)'
        need(independent_source.count(anchor) == 1, "independent mutation anchor changed")
        independent_path.write_text(independent_source.replace(anchor, anchor + " + 1"))
        cli(1, "separate exact engines disagree")
        independent_path.write_text(independent_source)
        checked.append("actual independent-engine disagreement rejected")

        receipt_path = package / "RESULT.json"
        receipt = receipt_path.read_bytes()
        wrong = json.loads(receipt)
        wrong["finite_inputs"]["affine6_sections"]["count"] = True
        receipt_path.write_text(json.dumps(wrong))
        cli(1, "scientific receipt or JSON types differ")
        receipt_path.write_bytes(receipt)
        checked.append("Boolean masquerading as an integer receipt rejected")

    need(snapshot() == before, "original package bytes changed during controls")
    print("PASS_P112_SIX_SEVEN_CLI_CONTROLS groups=" + str(len(checked))
          + " scientific_mutants=" + str(len(mutations) + 2)
          + " engine_disagreement=1 original_bytes=unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
