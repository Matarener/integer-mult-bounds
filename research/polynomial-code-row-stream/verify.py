"""Exact stream conformance and complete source-bound scientific replay."""

import hashlib
import itertools
import json
from pathlib import Path
import statistics
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))

from replay import authenticate, cached_engine, complete  # noqa: E402
from stream import MAX_BITS, PermutationStream, require  # noqa: E402


def literal(bits, index, n):
    return sum(((bits >> j) & 1) << (j ^ index) for j in range(n))


def small_streams():
    stream = PermutationStream()
    checked = 0
    for n in (1, 2, 4, 8):
        for bits in range(1 << n):
            for index in range(n):
                require(stream(bits, index, n) == literal(bits, index, n),
                        "Exhaustive literal row mismatch")
                checked += 1
    wide = 0
    for n in (16, 32, 64, 128):
        for coordinate, index in itertools.product(range(n), repeat=2):
            require(stream(1 << coordinate, index, n) == 1 << (coordinate ^ index),
                    "Wide one-coordinate permutation mismatch")
            wide += 1
    for n in (32, 8, 128, 16, 64, 1, 32):
        for bits in (0, (1 << n) - 1, ((1 << n) - 1) // 3):
            for index in (n - 1, 0, n // 2, n - 1, n - 1):
                require(stream(bits, index, n) == literal(bits, index, n),
                        "Interleaved width/base/repeated-index mismatch")
                wide += 1
    require(stream(1, MAX_BITS - 1, MAX_BITS) == 1 << (MAX_BITS - 1),
            "Largest admitted width failed")
    return {"exhaustive_small_rows": checked, "wide_and_history_rows": wide,
            "maximum_width_rows": 1}


def controls():
    stream = PermutationStream()
    invalid = [(False, 0, 8), (-1, 0, 8), (256, 0, 8), (1.0, 0, 8),
               (1, False, 8), (1, -1, 8), (1, 8, 8), (1, 0.0, 8),
               (1, 0, False), (1, 0, 0), (1, 0, 3), (1, 0, MAX_BITS * 2)]
    for args in invalid:
        stream(37, 3, 8)
        before = (stream.requests, stream.swaps, stream.base, stream.previous_row)
        try:
            stream(*args)
        except ValueError:
            pass
        else:
            raise ValueError("Invalid stream input accepted")
        require(before == (stream.requests, stream.swaps, stream.base, stream.previous_row),
                "Invalid call changed stream state")
        require(stream(37, 2, 8) == literal(37, 2, 8), "Warm rejection poisoned state")
    stream = PermutationStream()
    stream(37, 1, 8)
    stream.previous_row ^= 1
    require(stream(37, 3, 8) != literal(37, 3, 8), "Wrong preceding row undetected")
    stream = PermutationStream()
    stream(37, 2, 8)
    stream.masks[0] = 0
    require(stream(37, 3, 8) != literal(37, 3, 8), "Wrong cached mask undetected")
    return len(invalid) + 2


def production_rows():
    from experiments import affine_vector_screens as source
    fixtures = json.loads((PACKAGE.parents[1] /
                          "scripts/experiments/affine_vector_witnesses.json").read_text())
    stream, cached = PermutationStream(), cached_engine()
    digest = hashlib.sha256()
    for fixture in fixtures["cubic_codes"]:
        data = source.polynomial_code_base(fixture["extra"])
        for index in fixture["independent_rows"]:
            original = source.xor_permute(data["base"], index, data["n"])
            row = stream(data["base"], index, data["n"])
            require(row == original == cached(data["base"], index, data["n"]),
                    "Complete polynomial witness row changed")
            digest.update(row.to_bytes((data["n"] + 7) // 8, "little"))
    require(stream.requests == 3074, "Production row coverage changed")
    require(stream.swaps < stream.direct_swaps, "No production work reduction")
    return {"production_rows": stream.requests, "direct_swaps": stream.direct_swaps,
            "stream_swaps": stream.swaps, "incremental_requests": stream.incremental_requests,
            "row_stream_sha256": digest.hexdigest()}


def check_benchmark(output):
    record = json.loads((PACKAGE / "BENCHMARK.json").read_text())
    engines = ("original", "cached", "incremental")
    require(record["sample_order"] == list(engines) * 5, "Timing order changed")
    require(record["complete_replays"] == 15 and record["errors"] == 0,
            "Incomplete or failing timing run")
    for engine in engines:
        values = record["samples_seconds"][engine]
        require(len(values) == 5 and all(type(x) is float and 0 < x < 60 for x in values),
                "Invalid timing samples")
        require(record["summary_seconds"][engine] ==
                {"median": statistics.median(values), "min": min(values), "max": max(values)},
                "Timing summary mismatch")
    for name in ("stream.py", "replay.py", "benchmark.py"):
        require(record["script_sha256"][name] ==
                hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest(),
                "Timing implementation hash mismatch")
    require(record["source_manifest_sha256"] ==
            hashlib.sha256((PACKAGE / "SOURCES.json").read_bytes()).hexdigest(),
            "Timing source manifest mismatch")
    serialized = (json.dumps(output, sort_keys=True) + "\n").encode()
    require(record["stdout_sha256"] == hashlib.sha256(serialized).hexdigest(),
            "Timing complete-output hash mismatch")


def main():
    inputs = authenticate()
    result = small_streams()
    result["controls"] = controls()
    outputs = [complete(engine)[0] for engine in ("original", "cached", "incremental")]
    require(outputs[0] == outputs[1] == outputs[2], "Full certificate discrepancy")
    check_benchmark(outputs[0])
    result.update(production_rows())
    result.update(status="PASS_POLYNOMIAL_CODE_ROW_STREAM", inputs=inputs,
                  complete_nine_screen_replays=len(outputs))
    files = sorted(path for path in PACKAGE.iterdir() if path.is_file())
    require(len(files) <= 16, "Package receipt file cap exceeded")
    result["package_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in files}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
