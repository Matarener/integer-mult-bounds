"""Actual optimized CLI and cross-cohort source rejection controls."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from active_sources import HERE, PINS, compare_backend, opened, require


def run():
    cases = []
    with tempfile.TemporaryDirectory(prefix="active-t74-controls-") as directory:
        root = Path(directory)
        for index, name in enumerate(PINS):
            original = HERE / "inputs" / name
            changed = root / (str(index) + ".tar")
            changed.write_bytes(b"changed frozen export")
            cases.extend(((name, original, None), (name, changed, "pinned source export: " + name)))
        name = "t74-export.tar"
        link = root / "linked.tar"
        link.symlink_to(HERE / "inputs" / name)
        cases.extend(((name, link, "regular source export"), (name, root / "missing.tar", "regular source export")))
        for name, path, expected in cases:
            result = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py"),
                                     "--suite", "source-check", "--archive-name", name, "--archive", str(path)],
                                    capture_output=True, text=True, timeout=30)
            if expected is None:
                require(result.returncode == 0 and "PASS_ACTIVE_T74_SOURCE_BYTES" in result.stdout,
                        "actual optimized source acceptance")
            else:
                require(result.returncode != 0 and expected in result.stderr
                        and "PASS_ACTIVE_T74_SOURCE_BYTES" not in result.stdout, "actual optimized source rejection")
        with opened() as state:
            copy = root / "cohort-copy"
            shutil.copytree(state.backend, copy)
            path = copy / "ordinary.py"
            raw = path.read_bytes()
            path.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
            try:
                compare_backend(state.rate, copy)
            except ValueError as exc:
                require(str(exc) == "ordinary cohort bytes: ordinary.py", "specific cohort mismatch")
            else:
                raise ValueError("changed ordinary cohort accepted")
    return {"status": "PASS_ACTIVE_T74_SOURCE_CONTROLS", "positive_cli": 2,
            "negative_cli": 4, "cohort_mismatch_rejected": True}
