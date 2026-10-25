"""Exercise optimized real CLIs on owned, inode-disjoint copies. Apache-2.0."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copy_regular(source, destination):
    info = source.lstat()
    require(
        stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid(),
        "owned regular source",
    )
    data = source.read_bytes()
    fd = os.open(
        destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(fd, "wb") as handle:
        require(handle.write(data) == len(data), "copy write")
    target = destination.lstat()
    require(stat.S_ISREG(target.st_mode) and target.st_uid == info.st_uid, "owned copy")
    require(
        (target.st_dev, target.st_ino) != (info.st_dev, info.st_ino), "distinct copy"
    )


def run(directory, script, diagnostic):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    command = [sys.executable, "-I", "-O", "-Werror", "-B", str(directory / script)]
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=60, env=env, check=False
    )
    if diagnostic is None:
        require(
            result.returncode == 0 and result.stdout.startswith("PASS_"), "positive CLI"
        )
    else:
        require(
            result.returncode != 0 and diagnostic in result.stderr, "intended rejection"
        )


def mutated(original, fault):
    fixtures, results = (
        json.loads(original["FIXTURES.json"]),
        json.loads(original["RESULT.json"]),
    )
    case = fixtures[0]
    if fault == "basis":
        case["blocks"][-1]["bases"]["B"][0] = 0
    elif fault == "gram":
        case["blocks"][-1]["bases"]["B"][0] = 1
    elif fault == "duplicate":
        case["cells"][0]["ports"].append(case["cells"][0]["ports"][0])
    elif fault == "missing":
        case["cells"][0]["ports"].pop()
    elif fault == "boolean":
        case["blocks"][0]["dimension"] = True
    elif fault == "result":
        results["cases"][0]["attaining"] += 1
    elif fault == "stream":
        results["cases"][0]["stream_sha256"] = "0" * 64
    else:
        raise ValueError("unknown fault")
    raw = (json.dumps(fixtures, indent=2) + "\n").encode()
    results["fixtures_sha256"] = hashlib.sha256(raw).hexdigest()
    return {
        "FIXTURES.json": raw,
        "RESULT.json": (json.dumps(results, indent=2) + "\n").encode(),
    }


def main():
    source = Path(__file__).resolve().parent
    names = ("verify.py", "independent.py", "FIXTURES.json", "RESULT.json")
    original = {name: (source / name).read_bytes() for name in names}
    faults = {
        "basis": "label range",
        "gram": "Gram-I basis",
        "duplicate": "cell partition",
        "missing": "cell coverage",
        "boolean": "block dimension",
        "result": "result mismatch",
        "stream": "result mismatch",
    }
    with tempfile.TemporaryDirectory(prefix="mixed-basis-controls-") as temporary:
        target = Path(temporary)
        for name in names:
            copy_regular(source / name, target / name)
        for script in ("verify.py", "independent.py"):
            run(target, script, None)
            for fault, message in faults.items():
                for name, data in mutated(original, fault).items():
                    require(
                        (target / name).write_bytes(data) == len(data), "mutant write"
                    )
                run(target, script, message)
                for name in ("FIXTURES.json", "RESULT.json"):
                    require(
                        (target / name).write_bytes(original[name])
                        == len(original[name]),
                        "restore write",
                    )
                run(target, script, None)
        for name in names:
            require((source / name).read_bytes() == original[name], "unchanged source")
            require((target / name).read_bytes() == original[name], "restored copy")
    print("PASS_MIXED_BASIS_CONTROLS rejected=14 restored=14 initial=2")


if __name__ == "__main__":
    main()
