"""Optimized real-CLI faults on owned byte copies, with restored positives.

Nick Petalas. Apache-2.0.
"""

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = ("verify.py", "independent.py", "FIXTURES.json", "RESULT.json")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_regular(source, destination):
    before = source.lstat()
    need(
        stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(),
        "owned regular source",
    )
    data = source.read_bytes()
    with destination.open("xb") as stream:
        need(stream.write(data) == len(data), "complete byte copy")
    after = destination.lstat()
    need(
        stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid(),
        "owned regular destination",
    )
    need(
        (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino),
        "inode-disjoint copy",
    )
    need(digest(source) == digest(destination), "copy byte equality")


def mutate(fixtures, expected, name):
    if name == "overlapping-cells":
        fixtures["fixtures"][0]["groups"][0]["cells"] = [[0, 1], [1]]
    elif name == "nonorthogonal-blocks":
        fixtures["fixtures"][0]["blocks"][1] = [1]
    elif name == "partial-block-basis":
        fixtures["fixtures"][1]["groups"][0]["parts"][0]["basis"].pop()
    elif name == "wrong-block-span":
        fixtures["fixtures"][1]["groups"][0]["parts"][0]["basis"] = [4, 8]
    elif name == "oversized-ambient":
        fixtures["fixtures"][0]["ambient_dimension"] = 17
    elif name == "missing-target-group":
        fixtures["fixtures"][0]["groups"].pop()
    elif name == "false-crossing-equality":
        expected["results"]["crossing-forces-strict-vvv"]["VVV"]["minimum"] = 6
    elif name == "altered-charge-stream":
        expected["results"]["odd-block-crossing"]["MMM"]["charge_stream_sha256"] = (
            "0" * 64
        )
    else:
        raise ValueError("unknown bounded control")


def run(checker, directory):
    command = [sys.executable, "-I", "-O", "-Werror", "-B", str(directory / checker)]
    return subprocess.run(
        command, cwd=directory, capture_output=True, timeout=30, check=False
    )


def check_fault(checker, directory, fault, changes_fixture):
    fixtures = json.loads((HERE / "FIXTURES.json").read_bytes())
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    mutate(fixtures, expected, fault)
    if changes_fixture:
        fixture_bytes = json.dumps(fixtures).encode()
        expected["fixtures_sha256"] = hashlib.sha256(fixture_bytes).hexdigest()
    else:
        fixture_bytes = (HERE / "FIXTURES.json").read_bytes()
    (directory / "FIXTURES.json").write_bytes(fixture_bytes)
    (directory / "RESULT.json").write_text(json.dumps(expected))
    negative = run(checker, directory)
    messages = {
        "overlapping-cells": ("cells partition target group", "cell partition"),
        "nonorthogonal-blocks": (
            "orthogonal Gram-I block decomposition",
            "block orthonormality",
        ),
        "partial-block-basis": ("complete group block basis", "complete basis"),
        "wrong-block-span": ("group block span", "block span"),
        "oversized-ambient": ("ambient dimension capacity", "ambient capacity"),
        "missing-target-group": ("three target groups", "three groups"),
        "false-crossing-equality": (
            "recorded exact result mismatch",
            "independent recorded result mismatch",
        ),
        "altered-charge-stream": (
            "recorded exact result mismatch",
            "independent recorded result mismatch",
        ),
    }
    message = messages[fault][int(checker == "independent.py")]
    need(
        negative.returncode != 0 and message.encode() in negative.stderr,
        "wrong CLI fault outcome: " + fault + negative.stderr.decode(),
    )
    print(
        checker, fault, negative.returncode, negative.stderr.decode().splitlines()[-1]
    )
    for name in NAMES[2:]:
        (directory / name).write_bytes((HERE / name).read_bytes())
    restored = run(checker, directory)
    need(restored.returncode == 0, "restored CLI failed: " + restored.stderr.decode())


def main():
    before = {name: digest(HERE / name) for name in NAMES}
    faults = (
        "overlapping-cells",
        "nonorthogonal-blocks",
        "partial-block-basis",
        "wrong-block-span",
        "oversized-ambient",
        "missing-target-group",
        "false-crossing-equality",
        "altered-charge-stream",
    )
    need(len(faults) == 8, "bounded fault inventory")
    with tempfile.TemporaryDirectory(prefix="cell-crossing-controls-") as temporary:
        directory = Path(temporary)
        need(
            directory.lstat().st_uid == os.getuid() and not directory.is_symlink(),
            "owned directory",
        )
        for name in NAMES:
            copy_regular(HERE / name, directory / name)
        for checker in NAMES[:2]:
            positive = run(checker, directory)
            need(
                positive.returncode == 0,
                "positive CLI failed: " + positive.stderr.decode(),
            )
            for i, fault in enumerate(faults):
                check_fault(checker, directory, fault, i < 6)
        need(
            all(digest(directory / n) == before[n] for n in NAMES), "control copy drift"
        )
    need(all(digest(HERE / n) == before[n] for n in NAMES), "source drift")
    print(
        "PASS_CELL_CROSSING_CONTROLS optimized_faults=16 "
        "restored=16 initial_positives=2"
    )


if __name__ == "__main__":
    main()
