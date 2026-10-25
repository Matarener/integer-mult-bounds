#!/usr/bin/env python3
"""Adversarial controls for the exact hypotheses and the public replay."""

from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model
from source import authenticate

HERE = Path(__file__).resolve().parent


def rejected(function, message):
    try:
        function()
    except ValueError as exc:
        model.need(message in str(exc), "wrong rejection: " + str(exc))
        return
    raise ValueError("invalid control accepted: " + message)


def run():
    authenticate()
    t = (1, 1)
    rejected(lambda: model.check_fitting(6, [t], [[0]]), "nonzero")
    # Repeated physical ports cannot be deduplicated: the all-ones matrix has
    # rank one, but the two distinct positions require zero cross coefficients.
    rejected(lambda: model.check_fitting(6, [t, t], [[1, 1], [1, 1]]), "forbidden")
    model.check_fitting(6, [t, t], [[1, 0], [0, 1]])
    rejected(lambda: model.weighted_bound(6, {t: -1}), "nonnegative")
    model.need(model.dot(3, 5) == 1, "even-type control has a valid diagonal pairing")
    rejected(lambda: model.weighted_bound(6, {(3, 5): 1}), "inadmissible")
    chosen = list(model.selector(6)[0])
    bad = next(x for x in model.types(6) if x not in chosen and
               any(not model.dot(w, x[0]) for _, w in chosen[:-1]))
    rejected(lambda: model.check_selector(6, chosen[:-1] + [bad]), "not triangular")
    # Omitting the h5 exceptional type loses its entire orbit. One cannot keep
    # the 1/9 bound merely from the other three orbit fractions.
    truncated = set(model.selector(5)[0][:-1])
    smallest = min(F(len(truncated.intersection(o)), len(o)) for o in model.orbit_partition(5))
    model.need(smallest == 0, "missing exceptional-orbit control")
    # Identity is essential to the trace corollary. Two scalar idempotents
    # sum to D=[2], not I=[1]; normalizing D makes both terms non-idempotent.
    x1 = x2 = F(1)
    diagonal = x1 + x2
    model.need(x1*x1 == x1 and x2*x2 == x2 and diagonal != 1,
               "nonidentity diagonal fixture")
    normalized = x1 / diagonal
    model.need(normalized*normalized != normalized, "normalization lost idempotency")
    # A zero-charge rectangle contributes zero to B .* N and may be removed.
    ports = [(1, 1), (2, 2)]
    with_free = [[1, 7], [0, 1]]
    without_free = [[1, 0], [0, 1]]
    model.check_fitting(6, ports, with_free)
    model.check_fitting(6, ports, without_free)
    model.need(all(model.dot(ports[i][1], ports[j][0]) * with_free[i][j]
                   == without_free[i][j] for i in range(2) for j in range(2)),
               "zero-charge removal changed the endpoint")
    # Exercise the real optimized CLI's source gate, not just an in-memory predicate.
    with tempfile.TemporaryDirectory(prefix="odd-unit-controls-") as folder:
        corrupt = Path(folder) / "source.tar"
        raw = bytearray((HERE / "inputs/small-unit-source.tar").read_bytes())
        raw[len(raw)//2] ^= 1
        corrupt.write_bytes(raw)
        proc = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B",
                               str(HERE / "verify.py"), "--source-archive", str(corrupt)],
                              capture_output=True, text=True, timeout=30)
        model.need(proc.returncode != 0 and "comparison archive SHA256 mismatch" in proc.stderr,
                   "optimized CLI accepted changed comparison source")
    return {"status": "PASS_ODD_UNIT_RANK_CONTROLS", "controls": 9,
            "scope": "Mask, multiplicity, selector, exceptional orbit, trace and source boundaries."}


if __name__ == "__main__":
    model.need(len(sys.argv) == 1, "unknown control arguments")
    print(json.dumps(run(), sort_keys=True))
