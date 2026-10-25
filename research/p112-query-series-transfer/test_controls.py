"""Run deliberate corruptions through the actual optimized scientific CLIs."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def owned_copy(source, destination):
    before = source.lstat()
    require(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular source",
    )
    data = source.read_bytes()
    with destination.open("xb") as output:
        require(output.write(data) == len(data), "complete copy")
    after = destination.lstat()
    require(
        stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid(),
        "owned regular destination",
    )
    require(
        (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
        "inode-disjoint copy",
    )
    require(
        destination.read_bytes() == data and source.lstat() == before, "copy identity"
    )


def invoke(directory, script, diagnostic=None):
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(directory / script)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if diagnostic is None:
        require(
            result.returncode == 0 and result.stdout.startswith("PASS_"), result.stderr
        )
    else:
        require(
            result.returncode != 0 and diagnostic in result.stderr,
            "corruption was not rejected: " + result.stderr,
        )
    return {
        "script": script,
        "exit": result.returncode,
        "diagnostic": diagnostic,
        "stderr_sha256": hashlib.sha256(result.stderr.encode()).hexdigest(),
    }


def changed_json(path, key, value):
    data = json.loads(path.read_text())
    data[key] = value
    path.write_text(json.dumps(data))


def mutate(directory, name):
    if name == "operator":
        path = directory / "WITNESS.json"
        data = json.loads(path.read_text())
        data["readers"][0][0] = 0
        path.write_text(json.dumps(data))
        return ("verify.py", "independent.py"), "literal operator"
    if name == "result":
        changed_json(directory / "RESULT.json", "source_premises", -1)
        return ("verify.py", "independent.py"), "frozen result mismatch"
    if name == "template":
        path = directory / "PREDECESSOR-TEMPLATES.json"
        data = json.loads(path.read_text())
        data["points"][0][3] = [1, 1, 0]
        path.write_text(json.dumps(data))
        closure = directory / "SOURCE-CLOSURE.json"
        rows = json.loads(closure.read_text())
        rows[1]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        closure.write_text(json.dumps(rows))
        return ("verify.py", "independent.py"), "transfer"
    if name == "closure":
        path = directory / "SOURCE-CLOSURE.json"
        rows = json.loads(path.read_text())
        rows[0]["sha256"] = "0" * 64
        path.write_text(json.dumps(rows))
        return ("verify.py", "independent.py"), "source closure hash"
    if name == "series-direction":
        path = directory / "verify.py"
        text = path.read_text()
        old = "queries[index] = queries[index][:-1] + (1,)"
        require(text.count(old) == 1, "series mutation target")
        path.write_text(
            text.replace(old, "queries[index] = queries[index][:-1] + (0,)")
        )
        return ("verify.py",), "series witness binding"
    require(name == "collapse", "bounded mutation dispatch")
    path = directory / "independent.py"
    text = path.read_text()
    old = 'active = first and second if kind == "series" else first or second'
    require(text.count(old) == 1, "collapse mutation target")
    path.write_text(text.replace(old, "active = first or second"))
    return ("independent.py",), "transfer"


def main():
    files = sorted(p for p in ROOT.iterdir() if p.is_file())
    require(
        len(files) <= 20
        and all(not p.is_symlink() and p.stat().st_size <= 65536 for p in files),
        "control inventory bound",
    )
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    receipts = []
    with tempfile.TemporaryDirectory(prefix="query-series-controls-") as temporary:
        directory = Path(temporary)
        for source in files:
            owned_copy(source, directory / source.name)
        for script in ("verify.py", "independent.py"):
            receipts.append(invoke(directory, script))
        for name in (
            "operator",
            "result",
            "template",
            "closure",
            "series-direction",
            "collapse",
        ):
            targets, diagnostic = mutate(directory, name)
            for target in targets:
                receipts.append(
                    {"mutation": name, **invoke(directory, target, diagnostic)}
                )
            for source in files:
                (directory / source.name).write_bytes(source.read_bytes())
        for script in ("verify.py", "independent.py"):
            receipts.append(invoke(directory, script))
    require(
        before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "canonical sources unchanged",
    )
    print("PASS_QUERY_SERIES_CONTROLS " + json.dumps(receipts, sort_keys=True))


if __name__ == "__main__":
    main()
