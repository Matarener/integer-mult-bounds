"""Exact behavior checks. Produced by Nick Petalas. Apache-2.0."""

import gzip
import hashlib
import io
import itertools
import json
import random
import runpy
import statistics
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P = runpy.run_path(str(HERE / "packed.py"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    source = json.loads((HERE / "SOURCES.json").read_bytes())
    pins = {}
    for row in source["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input SHA256")
            pins[row["path"]] = row["sha256"]
    require(len(pins) == 2, "two exact workload inputs")
    return pins


def workload():
    raw = (ROOT / "research/p104-helper-subspace-splits/WORD.json.gz").read_bytes()
    require(len(raw) < 2000000, "compressed workload bound")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        payload = stream.read(8000001)
    require(len(payload) <= 8000000, "expanded workload bound")
    return json.loads(payload)


def dense_forward(n, events):
    """Independent chronological Fraction oracle, then literal transpose."""
    rows = [[Fraction(i == j) for j in range(n)] for i in range(n)]
    for kind, r, s, numerator, shift in events:
        q = Fraction(numerator, 2**shift)
        if kind in ("INIT", "CLEAR"):
            rows[r] = [Fraction(0)] * n
        elif kind == "SCALE":
            rows[r] = [q * x for x in rows[r]]
        elif kind == "COPY":
            rows[r] = [q * x for x in rows[s]]
        else:
            require(kind == "ADD", "oracle opcode")
            rows[r] = [x + q * y for x, y in zip(rows[r], rows[s], strict=False)]
    return [{j: rows[j][i] for j in range(n) if rows[j][i]} for i in range(n)]


def reject(action):
    try:
        action()
    except (ValueError, TypeError, KeyError):
        return 1
    raise ValueError("invalid case accepted")


def check_case(n, events):
    expected = dense_forward(n, events)
    result = P["check_transpose"](n, events, expected)
    require(result["coefficients"] == n * n, "complete coefficient count")
    wrong = [dict(row) for row in expected]
    wrong[-1][0] = wrong[-1].get(0, Fraction(0)) + 1
    reject(lambda: P["check_transpose"](n, events, wrong))
    return n * n


def finite_checks():
    alphabet = [
        ("ADD", 0, 1, 1, 0),
        ("ADD", 1, 0, -1, 1),
        ("SCALE", 0, 0, -1, 1),
        ("SCALE", 1, 1, 3, 0),
        ("COPY", 0, 1, 1, 1),
        ("COPY", 1, 0, -3, 2),
        ("INIT", 0, 0, 1, 0),
        ("CLEAR", 1, 1, 1, 0),
    ]
    cases, coefficients = 0, 0
    for length in range(5):
        for events in itertools.product(alphabet, repeat=length):
            coefficients += check_case(2, events)
            cases += 1
    rng = random.Random(1027)
    for n in range(1, 9):
        for _ in range(20):
            events = []
            for _ in range(40):
                r, s = rng.randrange(n), rng.randrange(n)
                kind = rng.choice(("ADD", "COPY", "SCALE", "INIT", "CLEAR"))
                if r == s and kind in ("ADD", "COPY"):
                    kind = "SCALE"
                events.append(
                    (kind, r, s, rng.choice((-3, -1, 1, 3)), rng.randrange(4))
                )
            coefficients += check_case(n, events)
            cases += 1
    return {
        "words": cases,
        "literal_coefficients": coefficients,
        "wrong_endpoint_rejections": cases,
    }


def controls():
    check = P["check_transpose"]
    identity = [{0: 1}, {1: 1}]
    tests = [
        lambda: check(True, [], [{0: 1}]),
        lambda: check(1025, [], []),
        lambda: check(2, [("BAD", 0, 1, 1, 0)], identity),
        lambda: check(2, [("ADD", 0, 0, 1, 0)], identity),
        lambda: check(2, [("ADD", 0, 2, 1, 0)], identity),
        lambda: check(2, [("SCALE", 0, 0, 1, 33)], identity),
        lambda: check(2, [("ADD", 0, 1, 0, 0)], identity),
        lambda: check(2, [], [{0: Fraction(1, 3)}, {1: 1}]),
        lambda: check(2, [], [{0: True}, {1: 1}]),
        lambda: check(2, [("SCALE", 0, 0, 2**19, 0)] * 216, identity),
        lambda: check(
            1024, [("SCALE", 0, 0, 2**19, 0)] * 10, [{i: 1} for i in range(1024)]
        ),
        lambda: check(1, [("SCALE", 0, 0, 1, 0)] * 60001, [{0: 1}]),
    ]
    # A radix collision without coefficient bounds is not safe equality.
    require(-16 + 1 * 16 == 0, "literal radix collision")
    require(
        reject(lambda: check(2, [], [{0: -15, 1: 1}, {1: 1}])) == 1,
        "false equality rejected after safe radix planning",
    )
    count = sum(reject(action) for action in tests) + 1
    require(check(1, [], [{0: 1}])["columns"] == 1, "one role")
    return count


def benchmark_receipt(pins, expected):
    recorded = json.loads((HERE / "BENCHMARK.json").read_bytes())
    require(recorded["status"] == "PASS_PACKED_TRANSPOSE_BENCHMARK", "benchmark status")
    require(recorded["pairs"] == 5 and recorded["errors"] == 0, "benchmark runs")
    require(recorded["inputs"] == pins, "benchmark input binding")
    for name, digest in recorded["code_sha256"].items():
        require(
            name in ("packed.py", "verify.py", "benchmark.py", "PROOF.md"),
            "benchmark source name",
        )
        require(
            hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest,
            "benchmark source binding",
        )
    require(len(recorded["code_sha256"]) == 4, "complete benchmark sources")
    samples = recorded["samples"]
    require(len(samples) == 10, "ten samples")
    for i, row in enumerate(samples):
        require(row["side"] == ("dense", "packed")[i % 2], "alternating order")
        require(
            row["inputs"] == pins and row["result"] == expected and row["errors"] == 0,
            "every sample completed",
        )
    for side in ("dense", "packed"):
        for key in ("checkpoint_seconds", "process_wall_seconds", "peak_rss_bytes"):
            values = [r[key] for r in samples if r["side"] == side]
            require(
                all(type(v) in (float, int) and v > 0 for v in values),
                "positive measured values",
            )
            require(
                recorded["summary"][side][key]
                == {
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values),
                },
                "derived sample statistics",
            )
    return {"recorded_pairs": 5, "timing_repeated_by_this_check": False}


def run():
    pins = authenticate()
    finite = finite_checks()
    rejected = controls()
    word = workload()
    result = P["reverse_columns"](word)
    n, events, expected = P["source_events"](word)
    width, _ = P["plan"](n, events, expected)
    original = runpy.run_path(
        str(ROOT / "research/p104-helper-subspace-splits/local.py")
    )
    require(result == original["reverse_columns"](word), "unchanged checkpoint summary")
    bad = dict(word)
    bad["program"] = word["program"] + [["ADD", 0, 1, "1", 0]]
    rejected += reject(lambda: P["reverse_columns"](bad))
    receipt = {
        "status": "PASS_PACKED_DYADIC_TRANSPOSE",
        "finite": finite,
        "controls": rejected,
        "workload": result,
        "radix_bits": width,
        "events": len(word["program"]),
        "scalar_events": len(events),
        "inputs": pins,
        "claim_type": "exact backend equivalence, no new kappa",
    }
    receipt["benchmark_receipt"] = benchmark_receipt(pins, result)
    receipt["new_source_sha256"] = {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in ("packed.py", "verify.py", "PROOF.md")
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    run()
