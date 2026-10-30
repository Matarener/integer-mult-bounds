"""Reject scientific and source faults through both optimized checker CLIs."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def byte_copy(source, destination):
    before = source.lstat()
    require(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular source",
    )
    require(before.st_size <= 65536, "copy size capacity")
    value = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as handle:
        require(handle.write(value) == len(value), "complete copy")
    after = destination.lstat()
    require(
        after.st_uid == os.getuid() and stat.S_ISREG(after.st_mode),
        "owned regular copy",
    )
    require(
        (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
        "distinct copy inode",
    )
    require(destination.read_bytes() == value, "copy byte equality")
    unchanged = source.lstat()
    require(
        (before.st_dev, before.st_ino, before.st_mode, before.st_size)
        == (unchanged.st_dev, unchanged.st_ino, unchanged.st_mode, unchanged.st_size),
        "source identity stable",
    )
    require(source.read_bytes() == value, "source bytes stable")


def cli(script, root, accepted):
    command = [sys.executable, "-W", "error", "-O", "-B", str(script)]
    run = subprocess.run(
        command, cwd=root, capture_output=True, text=True, timeout=60, check=False
    )
    if accepted:
        require(
            run.returncode == 0 and "PASS_" in run.stdout, "positive CLI: " + run.stderr
        )
    else:
        require(
            run.returncode != 0
            and "ValueError" in run.stderr
            and "PASS_" not in run.stdout,
            "fault was not rejected",
        )


def mutations(data, result):
    records = []
    bad = json.loads(json.dumps(data))
    bad["cases"][0]["coherent_points"][3] = [0, 0, 0]
    records.append(("coherent-query", "MAPS.json", bad))
    bad = json.loads(json.dumps(data))
    bad["cases"][7]["star_queries"][2][3] = 0
    records.append(("hub-dependence", "MAPS.json", bad))
    bad = json.loads(json.dumps(data))
    bad["cases"].pop()
    records.append(("missing-case", "MAPS.json", bad))
    bad = json.loads(json.dumps(data))
    bad["polynomial"] = 11
    records.append(("field-polynomial", "MAPS.json", bad))
    bad = json.loads(json.dumps(result))
    bad["reader_premises"] += 1
    records.append(("result-count", "RESULT.json", bad))
    return records


def main():
    inputs = json.loads((HERE / "SOURCES.json").read_text())["files"]
    live = [v["path"] for v in inputs if v["usage"] == "input"]
    require(len(live) == 2, "exact live source closure")
    local = ["verify.py", "independent.py", "MAPS.json", "RESULT.json", "SOURCES.json"]
    sources = [HERE / name for name in local] + [
        HERE.parents[1] / path for path in live
    ]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    with tempfile.TemporaryDirectory(prefix="two-port-controls-") as tmp:
        root = Path(tmp)
        require(
            root.lstat().st_uid == os.getuid() and not root.is_symlink(),
            "owned temporary root",
        )
        package = root / "research" / HERE.name
        for source in sources:
            byte_copy(source, root / source.relative_to(HERE.parents[1]))
        scripts = [package / "verify.py", package / "independent.py"]
        for script in scripts:
            cli(script, root, True)
        data = json.loads((package / "MAPS.json").read_text())
        result = json.loads((package / "RESULT.json").read_text())
        records = mutations(data, result)
        for _name, target, value in records:
            path = package / target
            original = path.read_bytes()
            path.write_text(json.dumps(value))
            for script in scripts:
                cli(script, root, False)
            path.write_bytes(original)
            for script in scripts:
                cli(script, root, True)
        source = root / live[0]
        original = source.read_bytes()
        source.write_bytes(original + b"\nsource mutation\n")
        for script in scripts:
            cli(script, root, False)
        source.write_bytes(original)
        for script in scripts:
            cli(script, root, True)
    require(
        before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "original source files unchanged",
    )
    print(
        "PASS_TWO_PORT_CONTROLS",
        json.dumps(
            {
                "faults": [r[0] for r in records] + ["source-bytes"],
                "rejections": 12,
                "positive_runs": 14,
            },
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
