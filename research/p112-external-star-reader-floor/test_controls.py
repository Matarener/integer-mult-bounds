"""Actual optimized CLI fault controls. Nick Petalas. Apache-2.0."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
INPUT = Path("research/adaptive-kernel-demotion/inputs/DATA-PHASES.json")


def invoke(package, script="verify.py"):
    return subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(package / script)],
                          capture_output=True, text=True, timeout=120, check=False)


def main():
    with tempfile.TemporaryDirectory(prefix="external-star-", dir=os.environ.get("TMPDIR")) as temporary:
        root = Path(temporary)
        package = root / "research" / HERE.name
        package.mkdir(parents=True)
        for source in sorted(HERE.iterdir()):
            if source.is_symlink() or not source.is_file():
                raise ValueError("unexpected package entry")
            shutil.copyfile(source, package / source.name)
        target = root / INPUT
        target.parent.mkdir(parents=True)
        shutil.copyfile(HERE.parents[1] / INPUT, target)
        faults = [
            (target, lambda raw: raw + b" ", "source SHA256"),
            (package / "RETAINED-RANK32.json", lambda raw: raw + b" ", "source SHA256"),
            (package / "verify.py", lambda raw: raw.replace(b"return 2\n", b"return 1\n"),
             "rational query support"),
            (package / "verify.py", lambda raw: raw.replace(b"a ^= 7", b"a ^= 5"),
             "GF4 defining polynomial"),
            (package / "RESULT.json", lambda raw: raw.replace(b'"errors": 0', b'"errors": 1'),
             "RESULT mismatch"),
        ]
        for path, mutate, message in faults:
            original = path.read_bytes()
            changed = mutate(original)
            if changed == original:
                raise ValueError("control did not change its fixture")
            path.write_bytes(changed)
            result = invoke(package)
            path.write_bytes(original)
            if result.returncode == 0 or message not in result.stderr:
                raise ValueError("fault was not rejected: " + message + result.stderr[-1000:])
        for script in ("verify.py", "independent.py"):
            result = invoke(package, script)
            if result.returncode != 0:
                raise ValueError("restored positive failed: " + result.stderr)
    print(json.dumps({"status": "PASS_EXTERNAL_STAR_CLI_CONTROLS", "errors": 0,
                      "optimized_faults_rejected": len(faults), "restored_positives": 2}, sort_keys=True))


if __name__ == "__main__":
    main()
