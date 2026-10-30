"""Conformance for the bitset substitution; produced by Nick Petalas, Apache-2.0."""
import ast
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from incidence import capacities, require, zero_masks
from replay import PACKAGE, PREDECESSOR, ROOT, authenticate, checked_bytes


def normalized(output):
    return re.sub(r"(?m)^\[\s*\d+\.\d+s\] ", "", output)


def captured(scope, engine):
    with tempfile.TemporaryDirectory(prefix="span-bytecode-") as temporary:
        env = dict(os.environ, PYTHONPYCACHEPREFIX=temporary,
                   PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
        env.pop("PYTHONOPTIMIZE", None)
        env.pop("FULL", None)
        argv = [sys.executable, "-B", str(PACKAGE / "replay.py"),
                "--scope", scope, "--engine", engine]
        start = time.perf_counter()
        result = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True,
                                text=True, timeout=180, check=False)
        elapsed = time.perf_counter() - start
    require(result.returncode == 0, f"{scope}/{engine} failed: {result.stderr[-2000:]}")
    require(len(result.stdout) <= 1024 * 1024, "bounded replay output")
    marker = "PASS_P104_BFORM_NINE_TERM_FLOOR" if scope == "complete" else "PASS\nDONE"
    output = normalized(result.stdout)
    require(marker in output, "completed scientific command")
    return elapsed, output


def literal_section(ports, z, width):
    bits = []
    for q in ports:
        parity = sum(((q >> bit) & 1) * ((z >> bit) & 1)
                     for bit in range(width)) % 2
        bits.append(parity == 0)
    return tuple(bits)


def check_case(ports, width, sections=zero_masks):
    masks = sections(ports, width)
    require(len(masks) == (1 << width) - 1, "all nonzero sections retained")
    literal = tuple(literal_section(ports, z, width) for z in range(1, 1 << width))
    for mask, expected in zip(masks, literal):
        require(tuple(bool(mask >> i & 1) for i in range(len(ports))) == expected,
                "literal section equality")
    best = 0
    pairs = 0
    for i, first in enumerate(literal):
        for j in range(i + 1, len(literal)):
            scalar = sum(a and b for a, b in zip(first, literal[j]))
            require((masks[i] & masks[j]).bit_count() == scalar, "pair incidence equality")
            best = max(best, scalar)
            pairs += 1
    actual = capacities(ports, width)
    require(actual == {width - 2: best, width - 1: max(map(sum, literal))},
            "complete capacity equality")
    return pairs


def finite_cases():
    cases = pairs = 0
    for width in (2, 3):
        for subset in range(1 << (1 << width)):
            ports = tuple(q for q in range(1 << width) if subset >> q & 1)
            pairs += check_case(ports, width)
            cases += 1
    for subset in (0, 1, 65535, 21845, 43690, 32769, 3855, 61680):
        ports = tuple(q for q in range(16) if subset >> q & 1)
        pairs += check_case(ports, 4)
        cases += 1
    source = (PREDECESSOR / "checks/spanlemma.py").read_text()
    assignments = (node for node in ast.parse("r" + source).body if isinstance(node, ast.Assign))
    ports = next(ast.literal_eval(node.value) for node in assignments
                 if any(isinstance(t, ast.Name) and t.id == "P" for t in node.targets))
    pairs += check_case(tuple(ports), 9)
    return {"fixtures": cases + 1, "section_pairs": pairs, "actual_port_count": len(ports)}


def rejected(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError(message)


def controls():
    for ports, width in (((0,), 1), ((0,), 10), ((0,), True), ((0, 0), 2),
                         ((-1,), 2), ((4,), 2), ([0], 2), ((0.0,), 2)):
        rejected(lambda: zero_masks(ports, width), "invalid input accepted")
    rejected(lambda: check_case((0, 1, 2, 3), 2,
                               lambda p, w: (0, 0, 0)), "zero section mutation")
    rejected(lambda: check_case((0, 1, 2, 3), 2,
                               lambda p, w: zero_masks(p, w)[:-1]), "missing section mutation")
    with tempfile.TemporaryDirectory(prefix="span-source-control-") as directory:
        original = (PREDECESSOR / "checks/spanlemma.py").read_bytes()
        path = Path(directory) / "changed.py"
        path.write_bytes(original + b"\n# changed\n")
        rejected(lambda: checked_bytes(path, hashlib.sha256(original).hexdigest()),
                 "changed actual source accepted")
    require(normalized("[  2.4s] count 36\n") == "count 36\n", "timestamp normalization")
    require(normalized("[  2.4s] count 36\n") != normalized("[  1.0s] count 35\n"),
            "scientific value remains visible")
    return 13


def check_record(record, transcripts, source_hashes):
    require(record["implementation_sha256"] == source_hashes, "benchmark implementation binding")
    digest = hashlib.sha256((PACKAGE / "SOURCES.json").read_bytes()).hexdigest()
    require(record["source_manifest_sha256"] == digest, "benchmark input binding")
    for scope in ("span", "complete"):
        result = record[scope]
        require(result["completed_commands"] == 10 and result["errors"] == 0,
                "complete error-free timing domain")
        require(result["transcript_sha256"] == [transcripts[scope]] * 10,
                "benchmark transcript binding")
        for engine in ("scalar", "bitset"):
            values = result["seconds"][engine]
            require(len(values) == 5 and all(type(x) is float and 0 < x < 180 for x in values),
                    "five bounded timing samples")
            require(statistics.median(values) == result["median_seconds"][engine],
                    "generated timing median")
            require([min(values), max(values)] == result["range_seconds"][engine],
                    "generated timing range")
        expected = 1 - result["median_seconds"]["bitset"] / result["median_seconds"]["scalar"]
        require(result["reduction"] == expected and expected > 0, "generated improvement")


def record_controls(record, transcripts, source_hashes):
    for kind in ("source", "median", "transcript"):
        changed = json.loads(json.dumps(record))
        if kind == "source":
            changed["source_manifest_sha256"] = "0" * 64
        elif kind == "median":
            changed["complete"]["median_seconds"]["bitset"] += 1
        else:
            changed["complete"]["transcript_sha256"][0] = "0" * 64
        rejected(lambda: check_record(changed, transcripts, source_hashes),
                 "changed benchmark record accepted")


def main():
    require(len(sys.argv) == 1, "verifier takes no arguments")
    authenticate()
    finite = finite_cases()
    finite["controls"] = controls()
    transcripts = {}
    for scope in ("span", "complete"):
        _, scalar = captured(scope, "scalar")
        _, bitset = captured(scope, "bitset")
        require(scalar == bitset, "complete normalized output equality")
        transcripts[scope] = hashlib.sha256(scalar.encode()).hexdigest()
    source_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in sorted(PACKAGE.glob("*.py"))}
    path = PACKAGE / "BENCHMARK.json"
    require(path.stat().st_size <= 65536, "bounded generated timing record")
    record = json.loads(path.read_text())
    check_record(record, transcripts, source_hashes)
    record_controls(record, transcripts, source_hashes)
    finite["controls"] += 3
    print(json.dumps({"finite": finite, "transcripts": transcripts,
                      "implementation_sha256": source_hashes}, sort_keys=True))
    print("PASS_P104_SPAN_BITSET")


if __name__ == "__main__":
    main()
