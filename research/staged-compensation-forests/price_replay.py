"""Independent literal Horner price and three-symbol microcircuit replay."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def primitives(q):
    require(q != 0, "zero coefficient is not emitted")
    n = abs(q.numerator)
    d = q.denominator
    steps = [("clear", "w")]
    for position, bit in enumerate(bin(n)[2:]):
        if position:
            steps.append(("double", "w"))
        if bit == "1":
            steps.append(("add", "w", "s", 1))
    while d > 1:
        require(d % 2 == 0, "non-dyadic coefficient")
        steps.append(("halve", "w"))
        d //= 2
    steps.append(("add", "t", "w", 1 if q > 0 else -1))
    steps.append(("clear", "w"))
    return steps


def check_microcircuit(q):
    steps = primitives(q)
    rows = {"s": [Q(1), Q(0), Q(0)],
            "t": [Q(0), Q(1), Q(0)],
            "w": [Q(0), Q(0), Q(1)]}
    for step in steps:
        op, dst, *rest = step
        if op == "clear":
            rows[dst] = [Q(0)] * 3
        elif op == "double":
            rows[dst] = [2 * a for a in rows[dst]]
        elif op == "halve":
            rows[dst] = [a / 2 for a in rows[dst]]
        elif op == "add":
            src, sign = rest
            rows[dst] = [a + sign * b for a, b in zip(rows[dst], rows[src])]
        else:
            raise ValueError(op)
    require(rows == {"s": [Q(1), Q(0), Q(0)],
                     "t": [q, Q(1), Q(0)],
                     "w": [Q(0), Q(0), Q(0)]}, "coefficient microcircuit")
    return len(steps)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(args.artifacts.resolve() not in args.output.resolve().parents,
            "output must be outside frozen artifact directory")
    files = {
        "original": ("SOURCE-base.json.gz", "compensation"),
        "historical-rank-basis": ("HISTORICAL-SHARED-COMPENSATION.json.gz", None),
        "forest": ("FOREST-COMPENSATION-base.json.gz", None),
        "two-sided": ("TWO-SIDED-COMPENSATION-base.json.gz", None),
    }
    panels, digests = {}, {}
    for name, (path, key) in files.items():
        raw = (args.artifacts / path).read_bytes()
        decoded = gzip.decompress(raw)
        value = json.loads(decoded)
        panels[name] = value[key] if key else value
        digests[name] = {
            "input": path,
            "compressed_sha256": hashlib.sha256(raw).hexdigest(),
            "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
        }
    require(digests["original"]["compressed_sha256"] ==
            "735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653",
            "original source pin")
    require(digests["historical-rank-basis"]["decoded_sha256"] ==
            "9f242abd5d2ed46a2e95dad46449d1d77c6fec330b5e0db6b324ac93fe756e62",
            "historical same-C source pin")
    coefficients = {Q(g[3], g[4]) for panel in panels.values() for g in panel}
    costs = {q: check_microcircuit(q) for q in coefficients}
    bills = {
        name: {"logical_additions": len(panel),
               "component_primitives": sum(costs[Q(g[3], g[4])] for g in panel),
               "histogram": dict(sorted(Counter(str(Q(g[3], g[4])) for g in panel).items()))}
        for name, panel in panels.items()
    }
    require([bills[k]["component_primitives"] for k in files] ==
            [31214, 17334, 13716, 10633], "complete independent literal prices")
    results = {
        "source_bindings": digests,
        "microcircuit_coefficients": {str(q): costs[q] for q in sorted(costs)},
        "arbitrary_microcircuit_input_symbols": ["source", "target", "coefficient-work"],
        "private_work_output": "zero",
        "bills": bills,
        "two_real_component_savings_vs_original": 41162,
        "two_real_component_savings_vs_historical_rank_basis": 13402,
        "two_real_component_savings_vs_target_forest": 6166,
        "scope": "Independent emitted Horner microcircuit count; not a whole-supplier precision or tape invoice.",
    }
    args.output.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n")
    print("PASS_LITERAL_HORNER_PRICES", len(costs), "coefficients")


if __name__ == "__main__":
    main()
