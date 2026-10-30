#!/usr/bin/env python3
"""Rebuild #4416's p7 target and paid invoice from its literal controller word.

Replays P7-FACTOR.json's 70 physical events as an exact Laurent matrix over Q, D0..D14 under #4416's
stated native contract (forward F_s = D_s S_y(Q^-1), backward B_s = D_s S_x(-Q); IDLE multiplies a pair
by its stage product; ADD and SIGNED_SWAP are scalar row operations). Checks that its left and right
scalar programs give left * M * right = the stated diagonal of monomials, then derives
  main targets: rank 1 + 8 * (number of D exponents) per role, over the 112 port recipes on main;
  paid idles: rank 8 * |stages| per retained window, on both roles of its pair, over the 112 ports;
and adds the THREE-base supplier's helper widths and paid profile over the 15 native calls.
The result must be the invoice #4416's moment inequalities use. No code from #4416.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDORED = {
    "vendor/P7-FACTOR.json": "6f96f6be5d8441f71cbe6ebb1657c69b543eb085b848b92b591b7ac01d6e6598",
    "vendor/RESULT.json": "9b814be97e3b45fcc28eafa8a65694897a7387f71a14d44796c6aadf303d7fab",
    "vendor/SUPPLIER-RESULT.json": "943d5fad2fc529f470df05a35446e07ecaef7344abfce450d2c2eb2c9b3798f6",
}
PHASES = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
PHASES_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def add(a, b, c=1):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + c * v
        if not out[k]:
            del out[k]
    return out


def shift(poly, delta, c=1):
    return {tuple(x + y for x, y in zip(k, delta)): c * v for k, v in poly.items()}


def replay(case, flip_first_reverse=False):
    n, nvar = 2 * case["pairs"], 1 + case["stages"]
    zero = (0,) * nvar
    M = [[{zero: 1} if i == j else {} for j in range(n)] for i in range(n)]
    D = lambda stages: tuple([0] + [int(s in stages) for s in range(case["stages"])])
    flipped = False
    for ev in case["physical_events"]:
        kind = ev[0]
        if kind == "LOCAL":
            _, stage, pair, rev = ev
            if flip_first_reverse and rev and not flipped:
                rev, flipped = False, True
            x, y = (2 * pair + 1, 2 * pair) if rev else (2 * pair, 2 * pair + 1)
            qexp = (1 if rev else -1,) + (0,) * (nvar - 1)
            M[y] = [add(a, shift(b, qexp, -1 if rev else 1)) for a, b in zip(M[y], M[x])]
            for r in (x, y):
                M[r] = [shift(p, D([stage])) for p in M[r]]
        elif kind == "IDLE":
            _, pair, stages = ev
            for r in (2 * pair, 2 * pair + 1):
                M[r] = [shift(p, D(stages)) for p in M[r]]
        elif kind == "ADD":
            _, d, s, c = ev
            M[d] = [add(a, b, c) for a, b in zip(M[d], M[s])]
        elif kind == "SIGNED_SWAP":
            _, a, b = ev
            M[a], M[b] = M[b], [shift(p, zero, -1) for p in M[a]]
        else:
            raise AssertionError(f"unknown event {kind}")
    return M


def scalar(program, n):
    X = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    for op in program:
        if op[0] == "SWAP":
            X[op[1]], X[op[2]] = X[op[2]], X[op[1]]
        elif op[0] == "SCALE":
            X[op[1]] = [Q(op[2]) * v for v in X[op[1]]]
        elif op[0] == "ADD":
            X[op[1]] = [a + Q(op[3]) * b for a, b in zip(X[op[1]], X[op[2]])]
        else:
            raise AssertionError("unknown scalar op")
    return X


def diagonal_identity(M, L, R):
    """left * M * right as a map monomial -> rational matrix"""
    n = len(M)
    keys = {k for row in M for p in row for k in p}
    out = {}
    for k in keys:
        C = [[Q(M[i][j].get(k, 0)) for j in range(n)] for i in range(n)]
        LC = [[sum(L[i][t] * C[t][j] for t in range(n)) for j in range(n)] for i in range(n)]
        out[k] = [[sum(LC[i][t] * R[t][j] for t in range(n)) for j in range(n)] for i in range(n)]
    return out


def main():
    for rel, digest in VENDORED.items():
        need(hashlib.sha256((HERE / rel).read_bytes()).hexdigest() == digest, f"vendored {rel}")
    need(hashlib.sha256((ROOT / PHASES).read_bytes()).hexdigest() == PHASES_SHA, "port recipes on main")
    case = json.loads((HERE / "vendor/P7-FACTOR.json").read_text())
    res = json.loads((HERE / "vendor/RESULT.json").read_text())["strictification"]
    sup = json.loads((HERE / "vendor/SUPPLIER-RESULT.json").read_text())["providers"]["THREE-base"]
    ports = len(json.loads((ROOT / PHASES).read_text())["recipes"])
    need(ports == 112 and case["pairs"] == 7 and case["stages"] == 15 and len(case["physical_events"]) == 70, "p7 shape")
    need(res["native_inventory"]["factor_receipt_sha256"] == VENDORED["vendor/P7-FACTOR.json"], "#4416 binds this P7-FACTOR.json")

    # 1. scalar programs and the exact Laurent identity
    n = 2 * case["pairs"]
    L, R = scalar(case["left_program"], n), scalar(case["right_program"], n)
    need(L == [[Q(x) for x in row] for row in case["left"]] and R == [[Q(x) for x in row] for row in case["right"]], "scalar programs give left and right")
    M = replay(case)
    ident = diagonal_identity(M, L, R)
    mono = [tuple(t) for t in case["exact_diagonal_monomials"]]
    for k, C in ident.items():
        want = [[Q(int(i == j and mono[i] == k)) for j in range(n)] for i in range(n)]
        need(C == want, f"left * M * right at monomial {k}")
    need(set(ident) == set(mono), "every diagonal monomial appears")
    stored = {tuple(c["exponents"]): [[Q(x) for x in row] for row in c["matrix"]] for c in case["coefficient_matrices"]}
    need(stored == {k: [[Q(M[i][j].get(k, 0)) for j in range(n)] for i in range(n)] for k in ident}, "replayed coefficients equal the stored ones")
    # control: one reversed local call flipped breaks the identity
    bad = diagonal_identity(replay(case, flip_first_reverse=True), L, R)
    need(any(C != [[Q(int(i == j and mono[i] == k)) for j in range(n)] for i in range(n)] for k, C in bad.items()) or set(bad) != set(mono),
         "control: a wrong local orientation fails")

    # 2. main targets from the monomials, over every port
    need(all(t[0] in (-1, 1) and set(t[1:]) <= {0, 1} for t in mono), "exponent alphabet")
    main_t = Counter()
    for t in mono:
        main_t[1 + 8 * sum(t[1:])] += ports
    need(dict(main_t) == {25: 448, 41: 448, 57: 448, 121: 224}, "main targets")

    # 3. paid idle windows from the literal IDLE events
    idle_events = Counter((ev[1], tuple(ev[2])) for ev in case["physical_events"] if ev[0] == "IDLE")
    windows = case["retained_idle_windows"]
    need(idle_events == Counter((w["pair"], tuple(w["stages"])) for w in windows), "retained windows are the literal IDLE events")
    keep = case["keep_idle_mask"]
    need(all((keep >> w["index"]) & 1 for w in windows) and not any((keep >> w["index"]) & 1 for w in case["omitted_idle_windows"]), "keep mask selects exactly the retained windows")
    idle = Counter()
    for w in windows:
        need(w["rank"] == 8 * len(w["stages"]), "window rank is 8 per stage")
        idle[w["rank"]] += 2 * ports
    need(dict(idle) == {8: 1344, 16: 448, 32: 448, 48: 448}, "paid idle profile")

    # 4. supplier contributions over the 15 native calls, and the full invoice
    calls = sum(1 for ev in case["physical_events"] if ev[0] == "LOCAL")
    need(calls == case["stages"] == 15, "one native call per stage")
    fw, bw = sup["unsplit_replays"]["forward"]["paid_profile"], sup["unsplit_replays"]["backward"]["paid_profile"]
    need(fw == bw, "supplier forward and backward paid profiles agree")
    T = main_t + Counter({int(k): v * calls for k, v in sup["helper_boundary"]["widths"].items()})
    P = Counter({int(k): v * calls for k, v in fw.items()}) + idle
    need(dict(T) == {int(k): v for k, v in res["targets"].items()}, "rebuilt targets equal #4416's invoice")
    need(dict(P) == {int(k): v for k, v in res["paid"].items()}, "rebuilt paid calls equal #4416's invoice")
    print(json.dumps({
        "status": "PASS_PR4416_INVOICE_REBUILD",
        "laurent_monomials": len(ident),
        "main_targets": dict(sorted(main_t.items())), "paid_idles": dict(sorted(idle.items())),
        "targets": dict(sorted(T.items())), "paid": dict(sorted(P.items())),
        "rank_one": [sum(k * v for k, v in T.items()), sum(k * v for k, v in P.items())],
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
