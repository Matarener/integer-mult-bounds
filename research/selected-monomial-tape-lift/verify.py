#!/usr/bin/env python3
"""Record-level f-column lift of the selected caller's monomials and J routes.

Standard library only.  Exit status 0 means every check passed; a JSON summary is printed
and compared with RESULT.json (regenerate with --write-result).  See README.md / PROOF.md.
"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import lift as L  # noqa: E402

BINDINGS = {
    "research/final4610-independent-admission/SPECIALIZATION.md": [
        "96+9+27+36+3 = 171",
        "A row addition is precisely the selected compact-control addition with its full dirty-control restoration and repair.",
        "The ideal algebraic lift holds for every positive f. Its physical tariff applies only in the selected source domain: f<=p, A=O(p), K/log p tending to infinity, and a superpolynomial record fiber. In the actual layer f<=e<=floor(b_in^epsilon) and p=6*b_in eventually.",
        "It uses one fixed list of primitive **types/operations**, rather than f separately allocated tapes.",
    ],
    "notes/compact-control-movement.tex": [
        r"\begin{proposition}[Compact-control selected-bit addition]",
        r" G=4\lceil\log_2 p\rceil+6,\quad f\le p,\quad A=O(p),",
        r" O\bigl(V((f\log p)^\tau+1)\bigr)",
    ],
    "notes/compact-control-layout.tex": [
        "Both front fields precede all active",
        "slots and the back field follows them, so the compact-control proposition",
        "applies to every ordered pair of slots.",
    ],
    "research/kappa-function-composition/complex/prune_native.py": [
        "result = ce.diag(n, tuple(recipe['quadratic_rows']), tuple(recipe['linear_Z4']))",
        "result = result.then(ce.perm(n, tuple(recipe['matrix_rows']))).then(ce.xgate(n, recipe['offset']))",
    ],
}


def need(ok, msg):
    if not ok:
        raise SystemExit("FAIL: " + msg)


def engine_agreement(ce, m, name):
    """The monomial's one-column action equals the exact Clifford engine on every basis state."""
    op = ce.diag(L.N9, m.Q, m.alpha).then(ce.perm(L.N9, m.G)).then(ce.xgate(L.N9, m.b)).then(ce.Op(L.N9, ce.identity(L.N9), [("phase", m.a)]))
    for x in range(1 << L.N9):
        vec, den = op.zero_state(x)
        need(den == 0, f"{name}: monomial is dyadic-free")
        y, ph = m.one_column(x)
        want = [(1, 0), (0, 1), (-1, 0), (0, -1)][(ph + m.a) % 4]
        need(vec[y] == want and all(v == (0, 0) for i, v in enumerate(vec) if i != y), f"{name}: engine agreement at x={x}")


def main():
    write = "--write-result" in sys.argv
    t0 = time.time()
    for path, needles in BINDINGS.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for s in needles:
            need(s in text, f"binding in {path}: {s!r}")
    ce = L.load_clifford()
    # 1. the 896 port wrappers of NORMALIZERS.json
    W = L.wrappers()
    need(len(W) == 896, "896 compiled wrappers (112 ports x 8)")
    mx, tot = Counter(), Counter()
    per_wrapper = {}
    for i, (name, m) in enumerate(W):
        if i % 112 == 0:
            engine_agreement(ce, m, name)
        ok, info = L.check_monomial(m, 1, L.all_addresses(L.N9, 1))
        need(ok, f"{name}: f=1 exhaustive, {info}")
        need(info["total"] <= 171 and info["XROW"] <= 96, f"{name}: within the s2 grammar bound")
        for f in (2, 3, 4):
            ok, _ = L.check_monomial(m, f, L.random_addresses(L.N9, f, 48, 1000 * f + i))
            need(ok, f"{name}: f={f} sampled")
        for k, v in info.items():
            mx[k] = max(mx[k], v)
            tot[k] += v
        per_wrapper[name] = info["total"]
    for name, m in W[:2]:
        ok, _ = L.check_monomial(m, 2, L.all_addresses(L.N9, 2))
        need(ok, f"{name}: f=2 exhaustive")
    # 2. the central translation X0 (C0 and D are positive-rank children, not monomials)
    (xname, x0), = L.central_elements(ce)
    ok, xinfo = L.check_monomial(x0, 3, L.random_addresses(L.N9, 3, 200, 5))
    need(ok and xinfo["total"] == 1 and xinfo["NOT"] == 1, "X0 is one translation record")
    # 3. the literal 145-axis J routes of the plan
    words = L.plan_words()
    need(len(words) == 32 + 72 + 15, "32 main, 72 helper, 15 idle targets")
    route_counts, conventions, swaps = Counter(), Counter(), Counter()
    central = 0
    for j, w in enumerate(words):
        for key in ("pre", "post"):
            ok, conv, info = L.check_word(w[key], w["perm"], w["inv"], 2, 12, 100 + j)
            need(ok, f"{w['name']} {key}: literal SWAP_BITS word realizes a declared permutation")
            conventions[(key, tuple(conv))] += 1
            route_counts[w["kind"]] += info["XROW"]
            swaps[w["kind"]] += len(w[key])
        central += w["central_X"]
    need(central == 16, "16 central X corrections (negative Q powers)")
    # 4. the body's own monomials and the provider's mode words (not port wrappers; #5442's mode-output certificate
    #    binds output_N, and the body applies whole-job helper normalizers, Z-map block maps, C8 routes and aliases)
    B = L.body_monomials(ce)
    need(sum(n for _, _, n in B) == 1072 + 16 and len(B) == 283, "1,088 body and mode words, 283 distinct")
    bmx, btot, bocc = Counter(), Counter(), Counter()
    for i, (kind, m, n) in enumerate(B):
        ok, info = L.check_monomial(m, 1, L.all_addresses(L.N9, 1))
        need(ok, f"body word {i} ({kind}): f=1 exhaustive, {info}")
        need(info["total"] <= 171 and info["XROW"] <= 96, f"body word {i}: within the s2 grammar bound")
        for f in (2, 3, 4):
            ok, _ = L.check_monomial(m, f, L.random_addresses(L.N9, f, 48, 7000 + 1000 * f + i))
            need(ok, f"body word {i} ({kind}): f={f} sampled")
        for k, v in info.items():
            bmx[k] = max(bmx[k], v)
            btot[k] += v * n
        bocc[kind] += n
    out = {"status": "PASS", "bindings": sum(map(len, BINDINGS.values())),
           "wrappers": {"count": len(W), "max_records": dict(mx), "sum_records": dict(tot),
                        "bound_s2": 171, "histogram_total": dict(sorted(Counter(per_wrapper.values()).items()))},
           "central": {"X0_records": xinfo, "C0_and_D": "positive-rank children (cgate, fourier), not monomials"},
           "routes": {"targets": len(words), "swap_bits_events": dict(swaps), "xrow_records": dict(route_counts),
                      "central_X_records": central,
                      "conventions": {f"{k[0]}:{'|'.join(k[1])}": v for k, v in conventions.items()}},
           "body_words": {"occurrences": 1088, "distinct": len(B), "occurrences_by_first_kind": dict(sorted(bocc.items())),
                          "max_records": dict(bmx), "sum_records_over_occurrences": dict(btot)},
           "checks": {"f1_exhaustive_body_words": len(B), "f1_exhaustive_wrappers": 896, "f2_exhaustive_wrappers": 2, "sampled_f": [2, 3, 4],
                      "engine_agreement_wrappers": 8, "route_f": 2, "route_addresses": 12}}
    path = HERE / "RESULT.json"
    out = json.loads(json.dumps(out))      # JSON-normal form: tuples become lists, keys become strings
    if write:
        path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    else:
        need(json.loads(path.read_text(encoding="utf-8")) == out, "RESULT.json differs from the fresh computation")
    print(json.dumps({**out, "seconds": round(time.time() - t0, 1)}, indent=1))


if __name__ == "__main__":
    main()
