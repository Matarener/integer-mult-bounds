# SPDX-License-Identifier: Apache-2.0
"""Git-free cold replay and failures before source execution, under -O."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    inputs = json.loads((HERE / "VERIFY.json").read_text())["inputs"]
    with tempfile.TemporaryDirectory(prefix="production-low-codes-controls-") as temp:
        root = Path(temp)
        target = root / PACKAGE
        shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in inputs:
            out = root / name
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, out)
        env = dict(os.environ, PATH=str(root / "no-tools"), PYTHONDONTWRITEBYTECODE="1")
        def call(script, succeeds, marker):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(target / script)],
                                    cwd=root, env=env, capture_output=True, text=True, timeout=25)
            need((result.returncode == 0) == succeeds and marker in result.stdout + result.stderr,
                 "CLI control " + marker + ": " + result.stdout + result.stderr)
        # Actual standalone cold replay with no Git or third-party dependency.
        call("verify.py", True, "PASS_PRODUCTION_LOW_CODE_COMPILER")
        probe = target / "import_probe.py"
        probe.write_text("import sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parent))\nimport source_binding\n")
        name = "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/low_codes.py"
        source = root / name
        raw = source.read_bytes()
        source.unlink()
        call("import_probe.py", False, "FileNotFoundError")
        source.write_bytes(raw + b"\n# changed source\n")
        call("import_probe.py", False, "input changed")
        source.write_bytes(raw)
        archive = root / "research/physical-gaussian-leaf/inputs/pr3087.tar"
        raw_archive = archive.read_bytes()
        archive.write_bytes(raw_archive[:-1] + bytes([raw_archive[-1] ^ 1]))
        call("import_probe.py", False, "input changed")
        archive.write_bytes(raw_archive)
        receipt = target / "RESULT.json"
        content = json.loads(receipt.read_text())
        content["schema_version"] = True
        receipt.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n")
        call("verify.py", False, "typed deterministic result equality")
    print("PASS_LOW_CODE_INTEGRITY Git-free replay; missing/changed source; changed archive; typed receipt")

if __name__ == "__main__":
    main()
