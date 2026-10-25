"""Actual optimized CLI corruption controls. Nick Petalas. Apache-2.0."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"


def need(value, message):
    if not value:
        raise ValueError(message)


def execute(root, script, cache, expected=None):
    command = [
        sys.executable,
        "-I",
        "-O",
        "-Werror",
        "-B",
        "-X",
        f"pycache_prefix={cache}",
        str(root / "research" / HERE.name / script),
    ]
    result = subprocess.run(
        command, cwd=root, capture_output=True, text=True, timeout=45, check=False
    )
    output = result.stdout + result.stderr
    if expected is None:
        need(result.returncode == 0, output)
    else:
        need(
            result.returncode != 0 and expected in output,
            f"control did not reject {expected}: {output}",
        )
    return result.returncode


def replace_once(path, old, new):
    raw = path.read_text()
    need(raw.count(old) == 1, "one mutation target")
    path.write_text(raw.replace(old, new))


def controls(root, package):
    mutations = (
        ("RESULT.json", '"pairs": 496', '"pairs": 495', "receipt"),
        (
            "SOURCES.json",
            '"git_blob": "d9a4f84211182ca200c081ea061d724c8a2cfb70"',
            '"git_blob": "0000000000000000000000000000000000000000"',
            "source blob",
        ),
        (
            "verify.py",
            "readers[2] = [value / 2 for value in old]",
            "readers[2] = [value / 3 for value in old]",
            "pair operator",
        ),
        ("verify.py", "(1, len(images) + 1)", "(1, 1)", "injective images"),
        ("verify.py", "a ^= 67", "a ^= 65", "field inverse"),
    )
    count = 0
    for index, (name, old, new, message) in enumerate(mutations):
        path = package / name
        original = path.read_bytes()
        try:
            replace_once(path, old, new)
            execute(root, "verify.py", root / f"cache-{index}", message)
        finally:
            path.write_bytes(original)
        count += 1
    for index, path in enumerate((root / INPUT, package / "RETAINED-RANK32.json")):
        original = path.read_bytes()
        try:
            path.write_bytes(original + b" ")
            execute(root, "verify.py", root / f"cache-source-{index}", "source SHA256")
        finally:
            path.write_bytes(original)
        count += 1
    return count


def main():
    # TMPDIR lets callers keep all disposable copies in their private run directory.
    with tempfile.TemporaryDirectory(
        prefix="p112-extension-", dir=os.environ.get("TMPDIR")
    ) as temp:
        root = Path(temp)
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package)
        destination = root / INPUT
        destination.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / INPUT, destination)
        execute(root, "verify.py", root / "positive-cache")
        rejected = controls(root, package)
        execute(root, "verify.py", root / "restored-cache")
        execute(root, "independent.py", root / "separate-cache")
        print(
            "PASS_EXTENSION_CONTROLS",
            json.dumps(
                {
                    "optimized_cli_rejections": rejected,
                    "restored_positive_and_separate": True,
                }
            ),
        )


if __name__ == "__main__":
    main()
