# SPDX-License-Identifier: Apache-2.0
"""Actual optimized CLI corruptions in private, regular-file source exports."""

import json
import os
import stat
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def private_copy(destination):
    from runtime import read_json, require

    sources = read_json(HERE / "SOURCES.json")
    pins = {
        row["path"]: row["sha256"]
        for row in sources["files"]
        if row["usage"] == "input"
    }
    inputs = list(pins)
    package_files = sorted(HERE.rglob("*"))
    require(len(package_files) <= 64, "bounded package export inventory")
    names = [str(p.relative_to(ROOT)) for p in package_files if p.is_file()]
    for name in [*names, *inputs]:
        source = ROOT / name
        before = source.lstat()
        require(
            stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
            "owned regular source copy input",
        )
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            require(
                (opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                "stable authenticated source identity",
            )
            data = stream.read()
        if name in pins:
            require(sha256(data).hexdigest() == pins[name], "authenticated copy input")
        with target.open("xb") as stream:
            created = os.fstat(stream.fileno())
            require(
                created.st_uid == os.getuid()
                and stat.S_ISREG(created.st_mode)
                and (created.st_dev, created.st_ino) != (before.st_dev, before.st_ino),
                "owned distinct private copy",
            )
            require(stream.write(data) == len(data), "complete private source write")
        require(
            sha256(target.read_bytes()).digest() == sha256(data).digest(),
            "byte-exact private source copy",
        )


def mutations():
    return (
        ("square-bit", "selector.py", "if bit == ONE:", "if bit == ZERO:"),
        ("cap-value", "selector.py", "return Count(cap)", "return Count.literal(1)"),
        (
            "final-rows",
            "selector.py",
            'candidate.replace("rows", power(work.get("radix"), work.get(borrowed_name)))',
            "pass  # deliberately leave saturated rows",
        ),
        (
            "compatibility",
            "selector.py",
            "stock.multiply_small(compatibility)",
            "pass  # deliberately omit compatibility",
        ),
        (
            "source-bytes",
            "../physical-ordinary-interchange/encoded.py",
            '"""Unbounded setup integers',
            '"""Changed setup integers',
        ),
        (
            "comparison-bytes",
            "comparison/PR3502-PROOF.md",
            "# Count-tape refinement",
            "# Altered Count-tape refinement",
        ),
    )


def run_rejected(package, expected=None):
    from runtime import require

    result = subprocess.run(
        [sys.executable, "-I", "-O", "-W", "error", "-B", str(package / "verify.py")],
        cwd=package.parents[1],
        capture_output=True,
        text=True,
        timeout=120,
    )
    require(
        result.returncode != 0 and "ValueError:" in result.stderr,
        "optimized public CLI rejects the source/receipt corruption",
    )
    require(
        "PASS_SATURATED_BODY_BORROWING" not in result.stdout,
        "rejected CLI cannot report success",
    )
    if expected is not None:
        require(expected in result.stderr, "expected CLI rejection reason")
    return dict(exit=result.returncode, error=result.stderr.strip().splitlines()[-1])


def main():
    from runtime import read_json, require

    rows = []
    for name, relative, old, new in mutations():
        with TemporaryDirectory(prefix="saturated-control-") as temporary:
            destination = Path(temporary)
            private_copy(destination)
            package = destination / "research/saturated-body-borrowing"
            target = package / relative
            original = target.read_text()
            require(old in original, "mutation reaches actual source: " + name)
            target.write_text(original.replace(old, new, 1))
            rows.append(dict(control=name, **run_rejected(package)))
    with TemporaryDirectory(prefix="saturated-receipt-control-") as temporary:
        destination = Path(temporary)
        private_copy(destination)
        package = destination / "research/saturated-body-borrowing"
        result_path = package / "RESULT.json"
        receipt = read_json(result_path)
        receipt["powers"]["cases"] = True
        result_path.write_text(json.dumps(receipt))
        rows.append(
            dict(
                control="typed-receipt",
                **run_rejected(package, "complete typed science receipt"),
            )
        )
    print("PASS_SATURATED_CLI_CONTROLS " + json.dumps(rows, sort_keys=True))


if __name__ == "__main__":
    main()
