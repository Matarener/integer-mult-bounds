#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Complex decoder copy budgets for u = 1..6 unpaid coordinates per family, with large local children.

Engine: research/complex-local-word-ceiling/ceiling.py, imported unchanged (sha256 checked).
Premises generalise research/plane-port-copy-budgets (complex side, favourable 'shrink' bracket):
  * u unpaid coordinates per live family;
  * every one of the 224 data incidences per call climbs u-1 coordinates less, so (u-1)*224 units of
    local mass are removed; 'selected' removes them as rank-1 children of the shipped word, and
    'rankL' places all remaining non-copy local mass fractionally at one rank L in {8, 16, 32};
  * the 8 rank-8 centre copies are replaced by k decoder copies of one rank r in {2, 8}; charge C = r*k
    enters both as local children and as the coverage-law centre term;
  * remaining mass goes to idle children at the halving-guard cap R = 51, fractional counts allowed.
A budget is the largest charge C = r*k whose relaxed moment is certified < 1 at the target saving,
with k+1 certified > 1 (moments increase with k). A missing budget means k = 0 already fails, which
rules out every construction under these premises; a budget is only a necessary target.
usage: verify.py [--write]
"""
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(ok, why):
    if not ok:
        raise SystemExit("FAIL: " + why)


PINS = {f["path"]: f["sha256"] for f in json.loads((HERE / "SOURCES.json").read_text())["files"]}
ENGINE = "research/complex-local-word-ceiling/ceiling.py"
need(hashlib.sha256((ROOT / ENGINE).read_bytes()).hexdigest() == PINS[ENGINE], "engine pin")
_spec = importlib.util.spec_from_file_location("cx_ceiling", ROOT / ENGINE)
CX = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CX)

CM, CFAM, CST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
DATA_INCIDENCES = 224
UNPAID = (1, 2, 3, 4, 5, 6)
DELIVERY = ("selected", 8, 16, 32)
COPY_RANKS = (2, 8)


def a_of(kappa):
    return kappa / (1 - kappa)


def targets(kappa):
    return {"selected_endpoint": a_of(kappa), "kappa_plus_10pct": a_of(kappa * Q(11, 10)),
            "kappa_x2": a_of(2 * kappa), "kappa_x4": a_of(4 * kappa), "a_1_over_99": Q(1, 99),
            "kappa_0p05": a_of(Q(1, 20)), "a_1_over_9": Q(1, 9)}


def base_local(u, delivery):
    word = {r: n for r, n in WORD.items() if r != 8}
    drop = (u - 1) * DATA_INCIDENCES
    if delivery == "selected":
        need(word[1] >= drop, "enough rank-1 children to shrink")
        word[1] -= drop
        return word
    mass = sum(r * n for r, n in word.items()) - drop
    return {delivery: Q(mass, delivery)}


def verdict(local, centre, a, u):
    try:
        lo, hi = CX.relax(local, CM, CFAM, CST, centre, a, unpaid=u)
    except ValueError:
        return "fail"  # local mass exceeds the coverage law
    return "pass" if hi < 1 else "fail" if lo > 1 else "undecided"


def budget(u, delivery, r, a, limit=3000):
    base = base_local(u, delivery)

    def v(k):
        loc = dict(base)
        if k:
            loc[r] = loc.get(r, 0) + k
        out = verdict(loc, r * k, a, u)
        need(out != "undecided", "undecided verdict")
        return out

    if v(0) == "fail":
        return None
    need(v(limit) == "fail", "search limit")
    lo, hi = 0, limit
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if v(mid) == "pass" else (lo, mid)
    need(v(lo) == "pass" and v(lo + 1) == "fail", "sharp budget")
    return r * lo


def compute():
    sel = json.loads((ROOT / "certificates/selected-result.json").read_text())
    kappa = Q(sel["kappa"])
    need(kappa == Q(836330098538459, 500000000000000000), "selected kappa")
    tg = targets(kappa)
    table = {}
    for u in UNPAID:
        for d in DELIVERY:
            for r in COPY_RANKS:
                table["u%d/%s/rank%d" % (u, d, r)] = {name: budget(u, d, r, a) for name, a in tg.items()}
    # control 1: u = 2 'selected' reproduces plane-port-copy-budgets' complex 'shrink' budgets
    pred = json.loads((ROOT / "research/plane-port-copy-budgets/RESULT.json").read_text())["complex"]["shrink"]
    for r in COPY_RANKS:
        for name in ("selected_endpoint", "kappa_plus_10pct", "a_1_over_99"):
            p = pred["rank%d/%s" % (r, name)]
            need(table["u2/selected/rank%d" % r][name] == (None if p is None else p["charge"]),
                 "u=2 reproduces plane-port-copy-budgets rank%d %s" % (r, name))
    # control 2: today's 64 centre charge is within the u = 1 budget at the selected endpoint
    need(table["u1/selected/rank8"]["selected_endpoint"] == 64, "u=1 selected word: budget equals today's 64")
    # control 3: kappa010-complex-lever-floor's rank-32 boundary (first passing u = 6 with the centre free)
    need(table["u5/32/rank2"]["a_1_over_9"] is None and table["u6/32/rank2"]["a_1_over_9"] is not None,
         "a = 1/9 first opens at u = 6 for rank-32 delivery")
    return {"status": "PASS_COMPLEX_MULTI_UNPAID_COPY_BUDGETS", "targets": {k: str(v) for k, v in tg.items()},
            "budgets_charge_per_call": table,
            "controls": ["u=2 equals plane-port-copy-budgets (6 cells)", "u=1 selected budget is 64",
                         "a=1/9 opens at u=6 for rank-32 delivery (kappa010-complex-lever-floor)"]}


def main():
    if not __debug__:
        raise SystemExit("refusing python -O")
    out = compute()
    path = HERE / "RESULT.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return
    need(json.loads(path.read_text(encoding="utf-8")) == json.loads(json.dumps(out)), "RESULT.json differs")
    print("PASS_COMPLEX_MULTI_UNPAID_COPY_BUDGETS cells=%d controls=3 no_new_kappa" % (len(out["budgets_charge_per_call"]) * 7))


if __name__ == "__main__":
    main()
