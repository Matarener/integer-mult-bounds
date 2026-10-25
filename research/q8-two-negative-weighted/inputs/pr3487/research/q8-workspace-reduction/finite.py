"""Replay the retained finite exclusions; do not enlarge their search domain."""

import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

from model import alphabet, diagonal, factor, identity, matmul, require

PACKAGE = Path(__file__).resolve().parent
FLAGS = (
    "-std=c++20",
    "-O3",
    "-Wall",
    "-Wextra",
    "-Wconversion",
    "-Wsign-conversion",
    "-Wshadow",
    "-Wpedantic",
    "-Werror",
)


def source_pins():
    receipt = json.loads((PACKAGE / "inputs/RETENTION.json").read_text())
    require(len(receipt) == 3, "retained source inventory")
    expected_names = {"pr3471-search.cpp", "pr3471-RESULT.json", "pr3471-README.md"}
    require(
        {row["retained_path"] for row in receipt} == expected_names, "retained paths"
    )
    for row in receipt:
        path = PACKAGE / "inputs" / row["retained_path"]
        require(path.is_file() and not path.is_symlink(), "missing retained source")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "retained source drift",
        )
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(
                row["path"] == "research/q8-mixed-uniform-tariff/PROOF.md",
                "live input path",
            )
            path = PACKAGE.parents[1] / row["path"]
            require(path.is_file(), "missing live input")
            require(
                hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "live input drift",
            )


def run(argv, timeout=120):
    return subprocess.run(
        argv, check=True, capture_output=True, text=True, timeout=timeout
    ).stdout


def packed(matrix, r):
    return b"".join(
        bytes(matrix[a * r : (a + 1) * r]) + b"\0" * (4 - r) for a in range(r)
    ) + b"\0" * (16 - 4 * r)


def unpacked(data, r):
    require(len(data) == 16, "native state size")
    require(not any(data[4 * r :]), "native row padding")
    require(
        all(not any(data[4 * a + r : 4 * a + 4]) for a in range(r)),
        "native column padding",
    )
    return tuple(data[4 * a + b] for a in range(r) for b in range(r))


def independent_ball(depth, inverse):
    seen = {identity(4)}
    letters = [factor((u, v, g + int(inverse)), 4) for u, v, g in alphabet(4)]
    frontier = seen
    for _ in range(depth):
        following = {matmul(a, b, 4) for a in frontier for b in letters}
        frontier = following - seen
        seen |= following
    return seen


def check_balls(directory, receipt):
    for key, expected in receipt["balls"].items():
        data = (directory / (key + ".bin")).read_bytes()
        require(len(data) == 16 * expected["states"], "native ball length")
        require(
            hashlib.sha256(data).hexdigest() == expected["sha256"], "native ball drift"
        )
        order = [
            struct.unpack("<4I", data[a : a + 16]) for a in range(0, len(data), 16)
        ]
        require(order == sorted(set(order)), "native ball order/duplicates")
    inverse = independent_ball(2, True)
    positive = independent_ball(2, False)
    for name, expected in (("r4-two-inverse", inverse), ("r4-two-prefix", positive)):
        data = (directory / (name + ".bin")).read_bytes()
        actual = {unpacked(data[a : a + 16], 4) for a in range(0, len(data), 16)}
        require(actual == expected, "independent depth-two ball")
    for target in ((3, 3, 0, 0), (3, 5, 0, 0)):
        wanted = {matmul(a, diagonal(target), 4) for a in inverse}
        require(not (wanted & positive), "independent negative-pair meet")
    return {"positive": len(positive), "inverse": len(inverse), "pair_meets": 2}


def check_probes(directory, receipt):
    from model import GROUP

    expected = bytearray(x for row in GROUP for x in row)
    for r in range(1, 5):
        letters = alphabet(r)
        for call in letters:
            expected.extend(packed(factor(call, r), r))
        seed = 117
        for _ in range(1024):
            word = []
            for _ in range(5):
                seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
                word.append(letters[seed % len(letters)])
            a = identity(r)
            for call in word:
                a = matmul(a, factor(call, r), r)
            expected.extend(packed(a, r))
            expected.extend(packed(matmul(a, diagonal((3,) * r), r), r))
    data = (directory / "probes.bin").read_bytes()
    require(data == expected, "independent Hamilton native probes")
    require(
        hashlib.sha256(data).hexdigest() == receipt["probes"]["sha256"], "probe receipt"
    )
    return receipt["probes"]


def replay(directory):
    source_pins()
    compiler = shutil.which("clang++") or shutil.which("g++")
    require(compiler is not None, "C++20 compiler required")
    executable = directory / "search"
    run(
        [
            compiler,
            *FLAGS,
            str(PACKAGE / "inputs/pr3471-search.cpp"),
            "-o",
            str(executable),
        ]
    )
    run([str(executable), "probes", str(directory)])
    output = run([str(executable), "search", str(directory)], 300)
    rows = [json.loads(line) for line in output.splitlines()]
    retained = json.loads((PACKAGE / "inputs/pr3471-RESULT.json").read_text())
    require(
        json.dumps(rows, sort_keys=True)
        == json.dumps(retained["search"], sort_keys=True),
        "retained exact finite searches",
    )
    probes = check_probes(directory, retained)
    balls = check_balls(directory, retained)
    relevant = [row for row in rows if row["tag"] in ("r4-pair", "r4-two")]
    require(len(relevant) == 2, "missing finite dependency")
    return {
        "search": relevant,
        "independent_balls": balls,
        "probes": probes,
        "other_unchanged_native_cases": len(rows) - len(relevant),
    }
