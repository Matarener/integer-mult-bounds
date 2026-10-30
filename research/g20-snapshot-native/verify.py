"""Rebuild the native word and all proof records in a fresh directory."""
from hashlib import sha256
from pathlib import Path
import gzip
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
OUTPUTS = ["WORD.json.gz", "WINDOWS.json", "LOCAL-RESULT.json", "GLOBAL.jsonl.gz",
           "GLOBAL-RESULT.json", "INVOICE.json", "CALLS.json", "PRIVATE-EPISODES.json",
           "TARGET-OWNERS.json", "SOURCE-DESCRIPTORS.json.gz", "ORDINARY-RESULT.json",
           "INDEPENDENT-RESULT.json", "WINDOW-AUDIT.json"]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def snapshot(root):
    return {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def payload(path):
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    if path.name == "GLOBAL.jsonl.gz":
        return data
    value = json.loads(data)
    if path.name == "GLOBAL-RESULT.json":
        value.pop("CPU_seconds")
    return value


def main():
    before = snapshot(ROOT)
    for row in json.loads((ROOT / "INPUTS.json").read_text()):
        need(before[row["local"]] == row["sha256"], "Frozen input: " + row["local"])
    with tempfile.TemporaryDirectory(prefix="g20-snapshot-") as directory:
        work = Path(directory) / "package"
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns("__pycache__"))
        for name in OUTPUTS:
            (work / name).unlink()
        for name in ["fusion.py", "global_retirement.py", "ordinary.py", "independent.py", "window_audit.py"]:
            command = [sys.executable, "-I", "-B", "-W", "error"]
            if sys.flags.optimize:
                command.append("-O")
            run = subprocess.run(command + [str(work / name)], cwd=work,
                                 text=True, capture_output=True, timeout=300)
            need(run.returncode == 0, name + " failed:\n" + run.stdout + run.stderr)
            print("PASS_REBUILT", name, flush=True)
        for name in OUTPUTS:
            need(payload(work / name) == payload(ROOT / name), "Rebuilt record differs: " + name)
        for row in json.loads((ROOT / "INPUTS.json").read_text()):
            need(sha256((work / row["local"]).read_bytes()).hexdigest() == row["sha256"], "Source changed during replay")
    need(snapshot(ROOT) == before, "Replay changed package files")
    print("PASS_NATIVE_G20_SNAPSHOT_ORDINARY_003487922466")


if __name__ == "__main__":
    main()
