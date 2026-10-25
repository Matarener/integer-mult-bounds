"""Actual optimized CLI faults on private, inode-disjoint regular copies."""

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


def copy_package(destination):
    paths = sorted(ROOT.rglob("*"))
    require(len(paths) <= 64, "package file bound")
    for source in paths:
        info = source.lstat()
        require(not stat.S_ISLNK(info.st_mode), "source link")
        target = destination / source.relative_to(ROOT)
        if stat.S_ISDIR(info.st_mode):
            target.mkdir(exist_ok=True)
        else:
            require(
                stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid(),
                "owned regular source",
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                require(stream.write(source.read_bytes()) == info.st_size, "short copy")
            after = target.lstat()
            require(
                (after.st_dev, after.st_ino) != (info.st_dev, info.st_ino),
                "inode alias",
            )


def run_cli(directory, expected=None):
    process = subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(directory / "verify.py")],
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
        env=dict(os.environ, PYTHONPYCACHEPREFIX=str(directory / "private-bytecode")),
    )
    if expected is None:
        require(
            process.returncode == 0 and "PASS_ROOTED_MINOR_TRANSFER" in process.stdout,
            "positive CLI failed: " + process.stderr,
        )
    else:
        require(
            process.returncode != 0 and expected in process.stderr,
            "fault did not reject at intended boundary "
            + str(expected)
            + ": "
            + process.stderr,
        )


def change_json(path, mutate):
    value = json.loads(path.read_text())
    mutate(value)
    path.write_text(json.dumps(value))


def main():
    with tempfile.TemporaryDirectory(prefix="rooted-minor-controls-") as temporary:
        directory = Path(temporary) / "package"
        directory.mkdir()
        copy_package(directory)
        run_cli(directory)
        cases_path = directory / "CASES.json"
        original = cases_path.read_bytes()
        faults = [
            (lambda c: c[0]["branch_sets"][0].append("a"), "disjoint branch sets"),
            (
                lambda c: c[0]["branch_sets"].__setitem__(
                    slice(0, 2), c[0]["branch_sets"][1::-1]
                ),
                "root placement",
            ),
            (
                lambda c: c[-1]["branch_sets"][0].append("unused"),
                "disconnected branch set",
            ),
            (lambda c: c[0]["links"].__setitem__(1, 0), "six distinct links"),
            (lambda c: c[-1]["links"].__setitem__(0, 10), "link does not join"),
            (lambda c: c[0]["vertices"].append("h"), "duplicate vertex"),
        ]
        for mutate, diagnostic in faults:
            change_json(cases_path, mutate)
            run_cli(directory, diagnostic)
            cases_path.write_bytes(original)
        program = directory / "verify.py"
        original_program = program.read_bytes()
        program.write_bytes(
            original_program.replace(b"images = [e, f, g]", b"images = [f, e, g]")
        )
        run_cli(directory, "projected K3,2 queries")
        program.write_bytes(original_program)
        source = directory / "predecessor/PROOF.md"
        source.write_bytes(source.read_bytes() + b"corrupt\n")
        run_cli(directory, "retained source hash")
        source.write_bytes((ROOT / "predecessor/PROOF.md").read_bytes())
        result = directory / "RESULT.json"
        raw = result.read_bytes()
        change_json(result, lambda v: v["cases"][0].__setitem__("contraction_rank", 1))
        run_cli(directory, "result receipt mismatch")
        result.write_bytes(raw)
        run_cli(directory)
    print("PASS_ROOTED_MINOR_CONTROLS rejecting_clis=9 positive_clis=2")


if __name__ == "__main__":
    main()
