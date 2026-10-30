"""Optimized CLI corruptions and finite-field identities. Apache-2.0."""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def regular_bytes(path):
    info = path.lstat()
    need(
        stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid(),
        "owned regular source",
    )
    need(info.st_size <= 1048576, "control source size")
    return path.read_bytes(), info


def create_export(destination):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    paths = [p.relative_to(ROOT) for p in HERE.iterdir() if p.is_file()]
    paths += [Path(r["path"]) for r in manifest["files"] if r["usage"] == "input"]
    need(len(paths) <= 32 and len(set(paths)) == len(paths), "export capacity")
    records = []
    for relative in paths:
        source = ROOT / relative
        raw, before = regular_bytes(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            need(stream.write(raw) == len(raw), "complete export write")
        after = target.lstat()
        need(
            stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid(),
            "owned regular export",
        )
        need(
            (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
            "export inode alias",
        )
        digest = hashlib.sha256(raw).hexdigest()
        need(
            hashlib.sha256(target.read_bytes()).hexdigest() == digest,
            "export byte equality",
        )
        records.append({"path": relative.as_posix(), "sha256": digest})
    return records


def run(export, ok, reason):
    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = str(export / "private-pycache")
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-O",
            "-Werror",
            "-B",
            str(export / PACKAGE / "verify.py"),
        ],
        cwd=export,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    need(
        (result.returncode == 0) == ok, "unexpected CLI exit: " + reason + result.stderr
    )
    need(
        "PASS_P112_FOUR_TERM_TRIPLE" in result.stdout
        if ok
        else reason in result.stderr,
        "missing CLI outcome",
    )


def field_identities():
    checked = 0
    for prime in (3, 5, 7, 11):
        inverse2 = pow(2, -1, prime)
        axes = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0))
        for a, b, c in axes:
            for w in range(prime):
                u = (
                    ((a + b) * inverse2 - w) % prime,
                    ((a + c) * inverse2 - w) % prime,
                    ((b + c) * inverse2 - w) % prime,
                    w,
                )
                if a + b + c == 1 and w not in (0, inverse2):
                    need(all(u), "generic support reduction")
                for x, y, z in axes:
                    q = (x + y - z, x - y + z, -x + y + z, x + y + z)
                    need(
                        sum(s * t for s, t in zip(u, q, strict=True)) % prime
                        == (a * x + b * y + c * z) % prime,
                        "finite-field affine identity",
                    )
                    checked += 1
    return checked


def cleanup_owned(root):
    paths = list(root.rglob("*"))
    need(len(paths) <= 100, "cleanup capacity")
    for path in sorted(paths, key=lambda p: len(p.parts), reverse=True):
        info = path.lstat()
        need(info.st_uid == os.getuid(), "cleanup owner")
        if stat.S_ISLNK(info.st_mode) or stat.S_ISREG(info.st_mode):
            path.unlink()
        else:
            need(stat.S_ISDIR(info.st_mode), "unexpected cleanup file type")
            path.rmdir()
    root.rmdir()


def main():
    scratch = Path(tempfile.mkdtemp(prefix="four-term-controls-"))
    try:
        records = create_export(scratch)
        result_path = scratch / PACKAGE / "RESULT.json"
        original = result_path.read_bytes()
        corrupt = json.loads(original)
        corrupt["MMM"]["classes"][0]["minimum"] -= 1
        result_path.write_text(json.dumps(corrupt))
        run(scratch, False, "result mismatch")
        result_path.write_bytes(original)
        source = scratch / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
        original = source.read_bytes()
        source.write_bytes(original + b" ")
        run(scratch, False, "source drift")
        source.write_bytes(original)
        source.unlink()
        source.symlink_to(
            ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
        )
        run(scratch, False, "source alias")
        source.unlink()
        with source.open("xb") as stream:
            need(stream.write(original) == len(original), "restored source write")
        program = scratch / PACKAGE / "verify.py"
        original = program.read_bytes()
        broken = original.replace(
            b"((1, 0, 1), (1, 1, 0), (1, 1, 1), (0, 1, 1))",
            b"((0, 0, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1))",
            1,
        )
        need(broken != original, "mutation applied")
        program.write_bytes(broken)
        run(scratch, False, "reader span implication")
        program.write_bytes(original)
        run(scratch, True, "restored positive")
        for row in records:
            for root in (ROOT, scratch):
                raw, _ = regular_bytes(root / row["path"])
                need(
                    hashlib.sha256(raw).hexdigest() == row["sha256"],
                    "source/export changed",
                )
        print(
            "PASS_FOUR_TERM_CONTROLS",
            json.dumps(
                {
                    "negative_cli_cases": 4,
                    "restored_cli": True,
                    "finite_field_entries": field_identities(),
                    "owned_regular_inode_disjoint_copies": len(records),
                    "source_and_export_hashes_unchanged": True,
                },
                sort_keys=True,
            ),
        )
    finally:
        cleanup_owned(scratch)


if __name__ == "__main__":
    main()
