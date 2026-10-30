"""Actual optimized Git-free CLI rejection controls on exclusive byte copies."""

import json
import os
import stat
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent))
from binding_source import HERE, ROOT, require


def identity(path):
    info = path.lstat()
    require(
        stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid(),
        "owned regular source",
    )
    return dict(
        bytes=info.st_size,
        sha256=sha256(path.read_bytes()).hexdigest(),
        device=str(info.st_dev),
        inode=str(info.st_ino),
        mode=stat.S_IMODE(info.st_mode),
    )


def copy_file(source, destination):
    old = identity(source)
    require(old["bytes"] <= 500000, "bounded source copy")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output:
        raw = source.read_bytes()
        require(output.write(raw) == len(raw), "complete exclusive copy")
    new = identity(destination)
    require(
        (old["device"], old["inode"]) != (new["device"], new["inode"]),
        "disjoint copy inode",
    )
    require(
        old["sha256"] == new["sha256"] and identity(source) == old, "source unchanged"
    )
    return dict(source=str(source), destination=str(destination), before=old, copy=new)


def rejected(argv, message):
    result = subprocess.run(
        argv, capture_output=True, text=True, timeout=30, check=False
    )
    require(
        result.returncode != 0 and message in result.stderr, "specific CLI rejection"
    )
    return dict(
        argv=argv, exit=result.returncode, stdout=result.stdout, stderr=result.stderr
    )


def main():
    require(len(sys.argv) == 1, "no control arguments")
    inputs = json.loads((HERE / "VERIFY.json").read_text())["inputs"]
    files = list(HERE.iterdir())
    require(len(files) <= 24 and len(inputs) <= 16, "bounded copy inventory")
    sources = {path.relative_to(ROOT) for path in files}
    sources.update(Path(path) for path in inputs)
    with TemporaryDirectory(prefix="strict-cli-") as temporary:
        root = Path(temporary)
        copies = [copy_file(ROOT / path, root / path) for path in sorted(sources)]
        package = root / HERE.relative_to(ROOT)
        verify = str(package / "verify.py")
        prefix = [sys.executable, "-I", "-O", "-W", "error", "-B"]
        rows = [rejected([*prefix, verify, "unknown"], "no verifier arguments")]
        code = "import runpy,sys,types;sys.modules['selector']=types.ModuleType('selector');sys.argv=[sys.argv[1]];runpy.run_path(sys.argv[0],run_name='__main__')"
        rows.append(rejected([*prefix, "-c", code, verify], "cold composed namespace"))
        changed = root / "research/encoded-strict-borrowing/strict_selector.py"
        with changed.open("ab") as output:
            require(output.write(b"\n") == 1, "one-byte input mutation")
        rows.append(rejected([*prefix, verify], "input hash"))
        for row in copies:
            require(
                identity(Path(row["source"])) == row["before"],
                "all original sources unchanged",
            )
    print(
        json.dumps(
            dict(
                status="PASS_STRICT_CALLER_CLI_CONTROLS", controls=rows, copies=copies
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
