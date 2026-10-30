#!/usr/bin/env python3
"""Independent unit-axis review of the new zero-port phase/geometry bridge.

This does not re-run the local producer or price the unresolved residual inverse.
Apache-2.0. Substantial OpenAI Codex assistance, October2026.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def gaussian_add(a, b):
    return a[0]+b[0], a[1]+b[1]


def gaussian_mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def matmul(a, b):
    return [[gaussian_add(gaussian_mul(a[i][0], b[0][j]),
                          gaussian_mul(a[i][1], b[1][j])) for j in range(2)]
            for i in range(2)]


def native_line(recipes):
    """Direct Gaussian 2x2 identities, including the exact phase factor."""
    zero, one = (F(0), F(0)), (F(1), F(0))
    eye, translation = [[one, zero], [zero, one]], [[zero, one], [one, zero]]
    a, b = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    positive, negative = [[a, b], [b, a]], [[b, a], [a, b]]
    need(matmul(positive, positive) == translation, "C_r squared is exactly translation_r")
    need(matmul(translation, positive) == negative, "inverse line is translation_r C_r")
    need(matmul(positive, negative) == eye, "positive and negative lines exactly cancel")
    for sign in (1, -1):
        r = recipes[str(sign)]
        need(r["rank"] == 1, "one paid recursive rank")
        for side in ("left", "right"):
            m = r[side]
            need(m["matrix_rows"] == [1 << j for j in range(9)] and
                 m["quadratic_rows"] == [0]*9 and m["linear_Z4"] == [0]*9 and m["phase"] == 0,
                 "actual unit-axis monomial adapter")
            need(m["offset"] == (1 if side == "left" and sign == -1 else 0),
                 "literal nonidentity inverse left translation")
    return {"checked_exact_2x2_identities": 3,
            "inverse_line_price": "1H1 plus one native left payload translation",
            "tensor_extension": "The other72 unit axes are untouched; products of the unit-axis convolutions commute with exact phase1."}


def route_permutations(routes):
    expected = list(range(73))
    permutations = {}
    for stage in range(9):
        perm = expected.copy()
        if stage:
            for i in range(8):
                lo, hi = 1+i, 9+8*(stage-1)+i
                perm[lo], perm[hi] = perm[hi], perm[lo]
        need(sorted(perm) == expected and all(perm[perm[i]] == i for i in expected),
             "exact involutory unit-axis permutation")
        for port in range(112, 128):
            row = routes[f"{stage}:{port}"]
            need(row["owner_right_matrix_columns"] == [1 << j for j in perm],
                 "actual zero-port map equals the specified axis transpositions")
            need(row["local_label"] == 0 and row["virtual_normal"] == 1,
                 "virtual normal is not a new nonzero local port label")
            need(row["logical_payload_translation"] == row["entry_payload_translation"] ==
                 row["exit_payload_translation"] == 0, "zero-port affine route has no translation")
        permutations[stage] = perm
    return permutations


def permute(frame, permutation):
    result = [0]*73
    for old, exponent in enumerate(frame):
        result[permutation[old]] = exponent
    return result


def walk(geometry, permutations):
    # Each entry represents the exact Fourier multiplier i^(sum e_j omega_j).
    # It is an operator equality for arbitrary field functions on all73 bits.
    current = {(bank, p): [0]*73 for bank in range(8) for p in range(112, 128)}
    lines, idle, local_stages = [], [], []
    for event in geometry["ordered_recipe"]:
        kind = event["kind"]
        if kind == "native_line":
            bank, port, stage = event["bank"], event["port"], event["before_stage"]
            need(event["label"] == 1 and event["sign"] == -1 and event["rank"] == 1,
                 "exact signed unit line")
            need(event["family"] == 128*bank+port and 1 <= stage <= 8, "line physical role")
            current[bank, port][0] = (current[bank, port][0]-1) % 4
            lines.append((stage, bank, port))
        elif kind == "local":
            stage, pair = event["stage"], event["pair"]
            expected_in = [int(9 <= j < 9+8*stage) for j in range(73)]
            expected_out = [int(j < 9+8*stage) for j in range(73)]
            for bank in (2*pair, 2*pair+1):
                for port in range(112, 128):
                    need(permute(current[bank, port], permutations[stage]) == expected_in,
                         "actual incoming zero field is exactly the common local exterior")
                    current[bank, port] = permute(expected_out, permutations[stage])
            local_stages.append(stage)
        elif kind == "zero_port_idle_interval":
            bank, axes = event["bank"], event["axis_indices"]
            need(len(axes) == event["rank"] and len(set(axes)) == len(axes), "paid idle axis count")
            for port in event["zero_ports"]:
                for axis in axes:
                    need(current[bank, port][axis] == 0, "idle work adds previously absent axes")
                    current[bank, port][axis] = 1
            idle.append(event["rank"])
        elif kind == "bridge":
            d, s = event["dst"], event["src"]
            for port in range(112, 128):
                need(current[2*d, port] == current[2*s, port] ==
                     current[2*d+1, port] == current[2*s+1, port],
                     "both literal bridge additions have identical gauges")
        elif kind == "terminal_Y_translations":
            need(event["zero_port_translation"] == 0, "zero-port terminal translation")
        else:
            need(kind == "signed_exchange", "known zero-port data operation")
            for pair in range(4):
                for port in range(112, 128):
                    current[2*pair, port], current[2*pair+1, port] = \
                        current[2*pair+1, port], current[2*pair, port]
    need(local_stages == list(range(9)), "all nine literal local calls")
    need(all(frame == [1]*73 for frame in current.values()), "every added data field ends in exact FULL73")
    need(len(lines) == len(set(lines)) == 256, "every extra line charged exactly once")
    need(Counter(idle) == {8: 6, 16: 2, 17: 2, 32: 2, 33: 2, 48: 2, 49: 2},
         "independently rebuilt idle interval histogram")
    need(sum(idle) == 438, "six additional initial virtual-axis covers are charged")
    return {"all73_axis_operator_equalities": True, "productive_gauges_checked": len(current),
            "extra_H1": len(lines), "inverse_line_native_left_translations": len(lines),
            "idle_rank_histogram_per_zero_port": dict(sorted(Counter(idle).items())),
            "idle_rank_mass_per_zero_port": sum(idle),
            "scope": "Correct native gauges and equal bridge gauges. No claim that the D-encoded contents have been decoded."}


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("--transition-evidence", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    result = read(a.transition_evidence/"RESULT.json")
    routes = read(a.transition_evidence/"ROUTES.json.gz")
    geometry = read(a.transition_evidence/"NINE-STAGE-DATA-GEOMETRY.json.gz")
    for name, key in (("ROUTES.json.gz", "routes_payload_sha256"),
                      ("NINE-STAGE-DATA-GEOMETRY.json.gz", "geometry_payload_sha256")):
        raw = gzip.decompress((a.transition_evidence/name).read_bytes())
        need(hashlib.sha256(raw).hexdigest() == result[key], "decompressed transition source binding")
    permutations = route_permutations(routes)
    checked = walk(geometry, permutations)
    bad = deepcopy(geometry)
    first = next(i for i, e in enumerate(bad["ordered_recipe"]) if e["kind"] == "native_line")
    del bad["ordered_recipe"][first]
    try:
        walk(bad, permutations)
    except ValueError as error:
        need("incoming zero field" in str(error), "missing inverse line rejected for the right reason")
    else:
        raise ValueError("missing inverse line accepted")
    out = {"status": "PASS_INDEPENDENT_UNIT_AXIS_PHASE_AND_GEOMETRY_REVIEW",
           "native_line": native_line(result["native_virtual_line"]["recipes"]),
           "nine_call_geometry": checked,
           "negative_control": "Omitting one of the256 inverse lines fails the actual next-call common exterior gauge.",
           "reviewed_source_sha256": {name: hashlib.sha256((a.transition_evidence/name).read_bytes()).hexdigest()
               for name in ("RESULT.json", "ROUTES.json.gz", "NINE-STAGE-DATA-GEOMETRY.json.gz")},
           "scope": "Independently checks the new unit-normal native lines, all9x16 actual zero-port routes and every zero-port field through the emitted nine-call recipe. The old112-port recipe and local symmetric producer are inherited and verified elsewhere; no decoder, complete theorem, or new kappa is claimed."}
    a.out.write_text(json.dumps(out, indent=2)+"\n")
    print(out["status"])


if __name__ == "__main__":
    main()
