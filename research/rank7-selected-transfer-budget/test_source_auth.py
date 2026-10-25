"""Reject changed executable inputs before execution in writable private copies."""

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTER = "research/complex-k492-owner-repair/vendor/multicold/engines/outer.py"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def copy_case(root):
    files = sorted(p for p in HERE.rglob("*") if p.is_file())
    need(len(files) <= 64, "bounded package inventory")
    for source in files:
        info = source.lstat()
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "regular private input")
        need(info.st_size <= 2**24, "bounded input")
        dest = root / "research/rank7-selected-transfer-budget" / source.relative_to(HERE)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    need(len(sources["files"]) <= 16, "bounded external inventory")
    for row in sources["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            need(len(raw) <= 2**24, "bounded external input")
            dest = root / row["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)


def check_mutant(root, name):
    copy_case(root)
    package = root / "research/rank7-selected-transfer-budget"
    manifest = package / "SOURCES.json"
    data = json.loads(manifest.read_bytes())
    marker = root / "EXECUTED"
    outer = root / OUTER
    injection = "from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('bad')\n"
    outer.write_text(injection + "raise RuntimeError('UNAUTHENTICATED_OUTER_EXECUTED')\n" +
                     outer.read_text())
    expected = "source hash: " + OUTER
    if name == "usage_reclassification":
        row = next(x for x in data["files"] if x["path"] == OUTER)
        row["usage"] = "provenance"
        manifest.write_text(json.dumps(data))
        expected = "fixed source manifest bytes"
    elif name == "boolean_schema":
        data["schema_version"] = True
        manifest.write_text(json.dumps(data))
        expected = "integer source schema"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPYCACHEPREFIX=str(root / "fresh-bytecode"))
    command = [sys.executable, "-O", "-W", "error", "-B", str(package / "verify.py")]
    result = subprocess.run(command, capture_output=True, env=env, timeout=15)
    need(result.returncode != 0 and expected.encode() in result.stderr, "auth rejection")
    need(not marker.exists() and b"UNAUTHENTICATED_OUTER_EXECUTED" not in result.stderr,
         "mutant executable must not run")
    return {"control": name, "exit_code": result.returncode,
            "rejection": expected, "executed_marker": False,
            "stderr_sha256": hashlib.sha256(result.stderr).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, help="Existing private scratch parent")
    args = parser.parse_args()
    if args.work is not None:
        need(args.work.is_dir() and not args.work.is_symlink(), "private scratch parent")
    records = []
    with tempfile.TemporaryDirectory(prefix="rank7-source-auth-", dir=args.work) as temp:
        for name in ("usage_reclassification", "boolean_schema", "executable_bytes"):
            records.append(check_mutant(Path(temp) / name, name))
    print(json.dumps({"status": "PASS_PREEXECUTION_SOURCE_AUTH_CONTROLS", "controls": records},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
