"""Run one complete frozen mixed-point construction in a fresh interpreter.

The caller chooses the opt-in compact interner or the retained baseline.
All timing excludes the structural digest, and reports its separate cost.
Produced by Nick Petalas. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent


def signature(circuit):
    digest = hashlib.sha256()
    for support in circuit.support:
        raw = support.to_bytes((support.bit_length() + 7) // 8, "little")
        digest.update(len(raw).to_bytes(4, "little"))
        digest.update(raw)
    for field in (circuit.inputs, circuit.targets, circuit.args,
                  circuit.outputs, circuit.active, circuit.additions):
        raw = json.dumps(field, separators=(",", ":")).encode()
        digest.update(len(raw).to_bytes(8, "little"))
        digest.update(raw)
    return digest.hexdigest()


def full_structure(circuit):
    return dict(inputs=circuit.inputs, targets=circuit.targets,
                support=[hex(value) for value in circuit.support],
                args=circuit.args, outputs=circuit.outputs,
                active=circuit.active, additions=circuit.additions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=("baseline", "candidate"))
    parser.add_argument("--case", nargs=5, type=int, default=(50, 3, 3, 1, 1))
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--factored", action="store_true")
    args = parser.parse_args()
    n, k, l, r, common = args.case
    if not (1 <= n <= 50 and 0 <= k <= 3 and 0 <= l <= 3 and
            0 <= r <= min(k, l) and k + l - r <= n and common in (0, 1)):
        parser.error("case outside the bounded construction domain")
    if args.full and n > 14:
        parser.error("full JSON output is limited to n <= 14")
    sys.path[:0] = [str(HERE / args.variant), str(HERE / "baseline")]
    from mixed_point_circuit import build, factored_transpose
    start = time.perf_counter()
    circuit = build(n, k, l, r, common=bool(common))
    if args.factored:
        circuit, _ = factored_transpose(circuit)
    built = time.perf_counter()
    if circuit.verify() is not True:
        raise ValueError("complete output-support check failed")
    verified = time.perf_counter()
    result = dict(variant=args.variant, case=args.case,
                  factored=args.factored, build_seconds=built - start,
                  verify_seconds=verified - built,
                  nodes=len(circuit.support), active=len(circuit.active),
                  additions=circuit.additions, errors=0,
                  signature=signature(circuit))
    result["digest_seconds"] = time.perf_counter() - verified
    result["peak_rss_native_units"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if args.full:
        result["structure"] = full_structure(circuit)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
