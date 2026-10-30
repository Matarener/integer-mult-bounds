"""Run both modes without Git and reject changed live sources before import."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = "research/eisenstein-rational-rank"
sys.path.insert(0, str(HERE))
from rational_rank import require


def execute(root, original=False):
    command = [sys.executable, "-W", "error", "-I", "-O", "-B", str(root / PACKAGE / "replay.py")]
    if original:
        command.append("--original")
    return subprocess.run(command, cwd=root, capture_output=True, timeout=30, check=False)


def hashes(root, paths):
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths}


def main():
    manifest = json.loads((HERE / "VERIFY.json").read_text())
    inputs = manifest["inputs"]
    require(len(inputs) == 3, "complete three-file executable dependency set")
    local = [PACKAGE + "/" + p.name for p in HERE.iterdir() if p.is_file()]
    paths = sorted(local + inputs)
    with tempfile.TemporaryDirectory(prefix="eisenstein-rational-integrity-") as directory:
        root = Path(directory)
        for name in paths:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        before = hashes(root, paths)
        baseline, changed = execute(root, True), execute(root)
        require(baseline.returncode == changed.returncode == 0, "Git-free replay failed")
        require(not baseline.stderr and not changed.stderr, "Git-free replay warning")
        require(baseline.stdout == changed.stdout, "Git-free complete output differs")
        require(hashes(root, paths) == before, "Git-free replay changed input files")
        for name in inputs:
            source = root / name
            raw = source.read_bytes()
            source.write_bytes(raw + b"\n# changed source\n")
            failed = execute(root)
            require(failed.returncode != 0, "changed source accepted")
            require(("source SHA: " + name).encode() in failed.stderr,
                    "changed source was not rejected before import")
            source.write_bytes(raw)
        require(hashes(root, paths) == before, "source control did not restore private copy")
    print("PASS_EISENSTEIN_RATIONAL_INTEGRITY git_free_modes=2 source_controls=3")


if __name__ == "__main__":
    main()
