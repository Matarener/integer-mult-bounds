"""Reject actual optimized-CLI source mutations before loading the backend."""

from pathlib import Path
import subprocess
import sys
import tempfile

from predecessor import HERE, require


def run():
    valid = HERE / "inputs/pr2899-export.tar.gz"
    with tempfile.TemporaryDirectory(prefix="retuned-controls-") as directory:
        root = Path(directory)
        changed = root / "changed.tar"
        raw = valid.read_bytes()
        changed.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
        linked = root / "linked.tar"
        linked.symlink_to(valid)
        missing = root / "missing.tar"
        cases = [(valid, None), (changed, "pinned backend archive bytes"),
                 (linked, "regular backend archive"), (missing, "regular backend archive")]
        for archive, expected in cases:
            argv = [sys.executable, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py"),
                    "--suite", "source-check", "--archive", str(archive)]
            result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            if expected is None:
                require(result.returncode == 0 and "PASS_RETUNED_SOURCE_BYTES" in result.stdout,
                        "actual optimized source positive control")
            else:
                require(result.returncode != 0 and expected in result.stderr
                        and "PASS_RETUNED_SOURCE_BYTES" not in result.stdout,
                        "actual optimized source rejection")
    return {"status": "PASS_RETUNED_SOURCE_CONTROLS", "positive_cli": 1, "rejected_cli": 3}
