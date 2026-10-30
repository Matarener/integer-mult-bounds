"""Reject malformed contracts and forged records through both optimized CLIs."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = ("verify.py", "independent.py", "FIXTURES.json", "RESULT.json")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def snapshot(root):
    result = {}
    for name in FILES:
        p = root / name
        st = p.lstat()
        need(
            stat.S_ISREG(st.st_mode) and st.st_uid == os.getuid(), "owned regular file"
        )
        result[name] = [
            st.st_dev,
            st.st_ino,
            st.st_mode,
            hashlib.sha256(p.read_bytes()).hexdigest(),
        ]
    return result


def run(root, script):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(root / script)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def mutate(data, record, number):
    f = data[0]
    if number == 0:
        f["lines"][0] = [0, 0]
    elif number == 1:
        f["lines"][0] = [True]
    elif number == 2:
        f["groups"].append(0)
    elif number == 3:
        f["lines"][0] = []
    elif number == 4:
        f["lines"] *= 65
    elif number == 5:
        f["groups"] *= 4
    elif number == 6:
        record["rows"][0]["mmm_min"] += 1
    else:
        record["rows"][0]["stream_sha256"] = "0" * 64


DIAGNOSTICS = (
    "one occurrence per group",
    "cell index",
    "nonempty cells",
    "line arity",
    "line count",
    "cell count",
)


def main():
    before = snapshot(ROOT)
    failures = restores = 0
    with tempfile.TemporaryDirectory(prefix="crossing-controls-") as temp:
        root = Path(temp)
        for name in FILES:
            with (root / name).open("xb") as output:
                payload = (ROOT / name).read_bytes()
                need(output.write(payload) == len(payload), "complete byte copy")
        copied = snapshot(root)
        for name in FILES:
            need(copied[name][:2] != before[name][:2], "inode-disjoint copy")
        for script in FILES[:2]:
            need(run(root, script).returncode == 0, "initial positive")
        for fault in range(8):
            data = json.loads((ROOT / "FIXTURES.json").read_text())
            record = json.loads((ROOT / "RESULT.json").read_text())
            mutate(data, record, fault)
            raw = (json.dumps(data, indent=2) + "\n").encode()
            record["fixtures_sha256"] = hashlib.sha256(raw).hexdigest()
            (root / "FIXTURES.json").write_bytes(raw)
            (root / "RESULT.json").write_text(json.dumps(record) + "\n")
            for script in FILES[:2]:
                process = run(root, script)
                expected = (
                    DIAGNOSTICS[fault]
                    if fault < 6
                    else (
                        "result mismatch"
                        if script == "verify.py"
                        else ("MMM minimum" if fault == 6 else "VVV stream")
                    )
                )
                if fault == 5 and script == "independent.py":
                    expected = "group contract"
                need(
                    process.returncode != 0 and expected in process.stderr,
                    "intended rejection " + str(fault) + " " + script + process.stderr,
                )
                failures += 1
            for name in FILES[2:]:
                (root / name).write_bytes((ROOT / name).read_bytes())
            for script in FILES[:2]:
                need(run(root, script).returncode == 0, "restored positive")
                restores += 1
        need(snapshot(root) == copied, "restored export identity")
    need(snapshot(ROOT) == before, "unchanged source identity")
    print(
        "PASS_CROSSING_CONTROLS",
        failures,
        "rejections",
        restores,
        "restores",
        2,
        "positives",
    )


if __name__ == "__main__":
    main()
