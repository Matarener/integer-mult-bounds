#!/usr/bin/env python3
"""Independent exact audit of the arithmetic layer of PR3562's ordinary-rate theorem.

Two exact engines (E1 integer-root bisection, E2 rational interval log/exp
series), source binding to the selected bit supplier on main, the arithmetic
of PROOF.md steps (a)-(e) from premises P1-P5, the line-158 witness and a frozen control
sweep. Stdlib only; no floating-point value is accepted as evidence.

Sagar Thakrar (thakrarsagar), with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.
"""
import argparse
import hashlib
import json
import sys
from functools import lru_cache
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# Literals under audit: PR3562 head abb93be8b9ceca07a2b17f3a97db7bb6b074271d,
# research/retuned-ordinary-coupling/PROOF.md (sha256 below; --pr3562-proof checks the bytes).
PR3562_HEAD = "abb93be8b9ceca07a2b17f3a97db7bb6b074271d"
PR3562_PROOF_SHA256 = "3e554832c38b4b801f55b20868679f3283bc90cd5a9d8ce1960f828ed2655f22"
HIST = {1: 381024, 2: 400416, 3: 22752, 4: 26880, 5: 29376, 6: 17376, 7: 26784, 42: 288}
CLAIM = {
    "hist": HIST, "W": 28416, "eps": Fr(1, 10**16), "F": 118606528512,
    "c": Fr(1, 577), "A": 200, "M": 10**6,
    "enclosure": (Fr(999998938581682162866772413602, 10**30), Fr(999998938581682162866772413603, 10**30)),
    "fallback": True, "two_power": "2^c", "coeff": 4283584, "j": 577,
    "C_complex": Fr(1729033982646513517717, 10**24), "excess": 354445191478901059996907,
}
# Endpoints X of the pending complex claims; each PR states kappa = X - 10^-46 - 10^-70
# (modern outer), so X is a primitive complex lower bound and compares like for like with a.
ENDPOINTS = {
    "PR2979 (merged archive, mdumitrean)": Fr(1729033982646513517717, 10**24),
    "PR3633 (hexapode)": Fr(1730096363528623534230, 10**24),
    "PR3642 (roger-sato)": Fr(1730394391813963415120, 10**24),
    "PR3653 (rohanarun)": Fr(1730418899766071163804, 10**24),
}
E1_BRACKET = (Fr(10, 5769), Fr(9, 5192))  # best rationals below/above b with denominator <= 6000


class AuditFailure(Exception):
    pass


def need(ok, msg):
    if not ok:
        raise AuditFailure(msg)


# ---------------- E1: integer-root bisection ----------------
@lru_cache(maxsize=None)
def e1_pow(r, t):
    """Enclose (r/64)^t, t=p/q, by [z/Q,(z+1)/Q], Q=2^bits, with z^q 64^p <= r^p Q^q < (z+1)^q 64^p."""
    p, q = t.numerator, t.denominator
    need(0 < r < 64 and 0 < t <= 1 and q <= 6000, "E1 needs 0<r<64, 0<t<=1, denominator <= 6000")
    bits = 128 if q <= 1000 else 64  # 2^-64 per term still resolves the 10^-8 bracket margins
    Q = 1 << bits
    rhs, den = r**p * Q**q, 64**p
    lo, hi = 0, Q  # invariant lo^q den <= rhs < hi^q den (hi=Q works because r<64)
    while hi - lo > 1:
        mid = (lo + hi) >> 1
        if mid**q * den <= rhs:
            lo = mid
        else:
            hi = mid
    need(lo**q * den <= rhs < hi**q * den, "E1 invariant")
    return Fr(lo, Q), Fr(hi, Q)


# ---------------- E2: rational interval log/exp series ----------------
P = 256  # dyadic outward-rounding precision (bits)


def rdn(x):
    return Fr((x.numerator << P) // x.denominator, 1 << P)


def rup(x):
    return Fr(-((-x.numerator << P) // x.denominator), 1 << P)


def atanh_inv(m, terms=140):
    """Enclose atanh(1/m)=sum z^(2k+1)/(2k+1), z=1/m; tail <= z^(2K+1)/((2K+1)(1-z^2))."""
    z2, t, s = Fr(1, m * m), Fr(1, m), Fr(0)
    for k in range(terms):
        s += t / (2 * k + 1)
        t *= z2
    return s, s + t / ((2 * terms + 1) * (1 - z2))


def _iadd(*xs):
    return sum(x[0] for x in xs), sum(x[1] for x in xs)


def _iscale(k, x):
    return (k * x[0], k * x[1]) if k >= 0 else (k * x[1], k * x[0])


def ln_table():
    a3, a5, a9, a15 = (atanh_inv(m) for m in (3, 5, 9, 15))
    ln2 = _iscale(2, a3)
    ln3 = _iadd(ln2, _iscale(2, a5))              # 3/2 -> atanh(1/5)
    ln5 = _iadd(_iscale(2, ln2), _iscale(2, a9))  # 5/4 -> atanh(1/9)
    ln7 = _iadd(_iscale(3, ln2), _iscale(-2, a15))  # 7/8 -> -atanh(1/15)
    ln = {1: (Fr(0), Fr(0)), 2: ln2, 3: ln3, 4: _iscale(2, ln2), 5: ln5,
          6: _iadd(ln2, ln3), 7: ln7, 42: _iadd(ln2, ln3, ln7)}
    # L_r = ln(64/r) = 6 ln2 - ln r > 0
    return {r: _iadd(_iscale(6, ln2), _iscale(-1, v)) for r, v in ln.items()}


LN64 = None


def exp_bounds(u, terms=120):
    """For rational u>=0 return (lo, hi) with lo <= exp(u) <= hi (Horner, outward rounding, Lagrange tail)."""
    need(u >= 0 and terms + 2 > u, "exp_bounds domain")
    ul, uh = rdn(u), rup(u)
    sl = sh = Fr(1)
    for k in range(terms, 0, -1):
        sl = rdn(1 + ul * sl / k)
        sh = rup(1 + uh * sh / k)
    tail = Fr(1)
    for k in range(1, terms + 2):
        tail *= uh / k
    tail = rup(tail / (1 - uh / (terms + 2)))
    return sl, sh + tail


@lru_cache(maxsize=None)
def e2_pow(r, t):
    """Enclose (r/64)^t = exp(-t ln(64/r)) for rational t in (0,1]."""
    global LN64
    if LN64 is None:
        LN64 = ln_table()
    lo_L, hi_L = LN64[r]
    return 1 / exp_bounds(t * hi_L)[1], 1 / exp_bounds(t * lo_L)[0]


def moment(params, t, engine):
    """Enclose mu_t = (sum_r H_r (r/64)^t + eps F (1/64)^t)/W."""
    W, lo, hi = params["W"], Fr(0), Fr(0)
    terms = [(h, r) for r, h in params["hist"].items()]
    if params["fallback"]:
        terms.append((params["eps"] * params["F"], 1))
    for weight, r in terms:
        a, b = engine(r, t)
        lo += weight * a
        hi += weight * b
    return lo / W, hi / W


def mu1(params):
    v = sum(Fr(h * r, 64) for r, h in params["hist"].items())
    if params["fallback"]:
        v += params["eps"] * params["F"] / 64
    return v / params["W"]


# ---------------- source binding ----------------
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_sources(params):
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row.get("usage") == "input":
            need(sha(ROOT / row["path"]) == row["sha256"], "source pin mismatch: " + row["path"])
    record = json.loads((ROOT / "certificates/selected-result.json").read_text())
    need(sha(ROOT / record["certificate"]) == record["certificate_sha256"], "selected certificate hash")
    assembly = json.loads((ROOT / record["certificate"]).read_text())
    nine = json.loads((ROOT / "research/e8-bit-p111-tuned/tune/EXPECTED.json").read_text())["nine"]
    need(nine["bit_lower"] == assembly["bit_lower"], "supplier/assembly bit endpoint differ")
    supplier = {int(k): v for k, v in nine["profile"].items()}
    need(params["hist"] == supplier, "histogram differs from the selected bit supplier")
    need(params["W"] == nine["bit"]["live"], "W differs from the selected bit supplier")
    need(params["F"] == 32 * 64**2 * sum(params["hist"].values()), "F != 32*64^2*sum H")
    lean = (ROOT / "research/lean-bit-moment-discharge/lean/Selected.lean").read_text()
    need("%d / (%d * %d)" % (params["F"], 1 / params["eps"], params["W"]) in lean,
         "fallback weight eps*F/W is not the main-side Selected.lean literal")
    return Fr(assembly["bit_lower"])


# ---------------- the audit ----------------
@lru_cache(maxsize=None)
def selector_D(N):
    D = [0] * (N + 1)
    for e in range(64, N + 1):
        D[e] = 1 + D[42 * (e >> 6)]
    return tuple(D)


def depth_ratio_max(N):
    """Side computation: max of D(e)/floor(log2 e) over 2 <= e <= N, as (ratio, first e attaining it)."""
    D, best, arg = selector_D(N), Fr(0), None
    for e in range(2, N + 1):
        if D[e] * best.denominator > best.numerator * (e.bit_length() - 1):
            best, arg = Fr(D[e], e.bit_length() - 1), e
    return best, arg


@lru_cache(maxsize=None)
def depth_bound_ok(N):
    D = selector_D(N)
    return all(2**D[e] <= e * e for e in range(2, N + 1))  # D(e) <= 2 log2 e


def fit_and_composition(c, M, two_power="2^c", claimed=None):
    """Steps (c)-(d) for rational c in (17/10000, 1/512) and majorant coefficient M (histogram-free)."""
    need(Fr(17, 10000) < c < Fr(1, 512), "c outside (17/10000, 1/512)")
    # (c) selector fit for e >= 2^20 (analytic proof in PROOF.md; exact boundary arithmetic here)
    need(17**128 > 32 * 16**128, "(c) 2^(5/128) < 17/16")
    need(20 * c < Fr(5, 128), "(c) 20c < 5/128")
    need(2 * 8195 * 2 == 32780 and 32780 * 20 * 17 == 696575 * 16 and 696575 < 2**20, "(c) 2k/e boundary")
    D = selector_D(2**20)
    need(depth_bound_ok(2**20), "(c) D(e) <= 2 log2 e fails")
    e0 = 2**20
    need(c.denominator <= 10**30, "c must be an explicit rational")
    w0 = 2  # ceil(e0^c): 1 < 2^(20c) < 2^(5/128) < 2 for 0 < c < 1/512
    k0 = (4096 * w0 + 1) * D[e0]  # k <= (4096 w + 1) D(e) from |GL_64|<q^4096, 269241600<q
    need(2 * k0 < e0 and (e0 - k0) // w0 >= 64, "(c) fit predicates at e = 2^20")
    need(Fr(e0, 4 * w0) - 1 > 64, "(c) e^(1-c)/4 - 1 > 64 at e = 2^20")
    # (d) composition: coefficient, the 2^c factor and the line-156 gap witness
    p, q = c.numerator, c.denominator
    need(2 * 16**512 < 17**512, "(d) 2^c < 2^(1/512) < 17/16")
    if LN64 is None:
        e2_pow(1, Fr(1))
    ln2_lo = LN64[1][0] / 6
    # log2 x <= 2 x^s for x >= 1, s=(1-c)^2: max of log2(x)/x^s is 1/(s e ln2), so need s*e*ln2 >= 1/2
    need((1 - c)**2 * exp_bounds(Fr(1))[0] * ln2_lo >= Fr(1, 2), "(d) log2 e <= 2 e^((1-c)^2)")
    # setup absorption (1+log2 V)^4 <= 512 V: with y=2 ln V, (1+y)^4 e^(-y/2) <= 8^4 e^(-7/2) < 4096/33
    need(exp_bounds(Fr(7))[0] > 33**2 and Fr(4096, 33) <= 512, "(d) setup absorption")
    factor = Fr(17, 16) if two_power == "2^c" else Fr(2)
    coeff = 801 + 4 * M * factor + 2 * 8195 * 2 + 2 + 1
    if claimed is not None:
        need(coeff == claimed, "(d) coefficient %s != claimed %s" % (coeff, claimed))
    a = c * (1 - c)
    # premise-extremal witness at e=2^q: n=e^(1-c)=2^(q-p), w=2e^c=2^(p+1); exponents of 2:
    lhs = (q - p) * (1 - c) + p + 1          # log2(n^(1-c) w)
    rhs = c + q * (1 - a)                     # log2(2^c e^(1-a))
    need(lhs - rhs == 1 - c, "(d) witness identity")
    need(2**511 * 16**512 > 17**512, "(d) witness ratio 2^(1-c) > 2^(511/512) > 17/16")
    need((q - p) + (p + 1) > q, "(d) witness violates n <= e/w (excluded by n=floor((e-k)/w))")
    return {"a": a, "coeff": coeff, "coeff_cited_premises_only": 801 + 4 * M * 2 + 32780 + 3}


def audit(params, full=True):
    out = {}
    bit_lower = bind_sources(params)
    c, A, M = params["c"], params["A"], params["M"]
    t = 1 - c
    need(Fr(17, 10000) < c < Fr(1, 512), "c outside (17/10000, 1/512)")
    # P5 composition: two C0 calls x padded volume < 2V x majorant (A, M), plus wrapper bill (n+k+w+1)
    need(2 * 2 * A + 1 == 801, "P5: 801 != 2*2*A + 1")

    # (a) moment certificates, two engines
    m1 = mu1(params)
    need(A * (1 - m1) > 1, "(a) A(1-mu_1) <= 1")
    encs = {"E1": moment(params, t, e1_pow), "E2": moment(params, t, e2_pow)}
    for name, (lo, hi) in encs.items():
        need(lo <= hi, name + " empty")
        need(hi < 1, "(a) %s: mu_(1-c) not certified below 1" % name)
        need(M * (1 - hi) > 1, "(a)/(b) %s: M(1-mu_(1-c)) <= 1, majorant coefficient too small" % name)
        if params.get("enclosure"):
            L, U = params["enclosure"]
            need(L <= lo and hi <= U, "(a) %s enclosure not inside PR3562's stated enclosure" % name)
    out["mu_1"] = m1
    out["mu_t"] = encs

    out.update(fit_and_composition(c, M, params["two_power"], params["coeff"]))
    a = out["a"]

    # (e) consequence arithmetic and reciprocal restriction
    C = params["C_complex"]
    need(a - C == Fr(params["excess"], 332929 * 10**24), "(e) stated excess")
    need(a > C, "(e) a <= C_complex")
    j = params["j"]
    need(Fr(1, j) < bit_lower and Fr(j - 1, j * j) > C, "(e) reciprocal 1/%d fails" % j)
    out["reciprocal"] = {jj: (Fr(1, jj) < bit_lower, Fr(jj - 1, jj * jj) > C) for jj in (576, 577, 578)}

    if not full:
        return out
    # root binding and ceiling: E2 at the selected endpoint, E1 on a small-denominator bracket
    blo, bhi = bit_lower, bit_lower + Fr(1, 10**24)
    need(moment(params, 1 - blo, e2_pow)[1] < 1 < moment(params, 1 - bhi, e2_pow)[0],
         "root: selected bit_saving does not bracket the fallback-inclusive root")
    nofb = dict(params, fallback=False)
    need(moment(nofb, 1 - bhi, e2_pow)[1] < 1, "root: fallback-free root not separated")
    lo1, hi1 = E1_BRACKET
    need(moment(params, 1 - lo1, e1_pow)[1] < 1 < moment(params, 1 - hi1, e1_pow)[0], "root: E1 bracket")
    need(lo1 < blo and bhi < hi1, "root: E1 bracket does not contain the E2 bracket")
    need(Fr(1, 577) < blo and bhi < Fr(1, 576), "root: 1/577 < b < 1/576")
    out["root"] = (blo, bhi)
    # informational (E2 only): one non-reciprocal c' inside the window where c'(1-c') exceeds PR3653's X
    cw = blo - Fr(1, 10**9)
    mw = moment(params, 1 - cw, e2_pow)[1]
    Mw = int(1 / (1 - mw)) + 1
    need(mw < 1 and Mw * (1 - mw) > 1, "window example")
    out["window"] = (cw, cw * (1 - cw), Mw, fit_and_composition(cw, Mw)["coeff"])
    out["ceiling"] = (blo * (1 - blo), bhi * (1 - bhi))
    return out


def controls():
    base = dict(CLAIM)
    altered = dict(HIST)
    altered[7] += 1
    return {
        "c just above b (c = 9/5192 = b + 9.0e-9)": dict(base, c=E1_BRACKET[1], enclosure=None),
        "M = 10^6 too small (c = 10/5769 = b - 2.4e-8)": dict(base, c=E1_BRACKET[0], enclosure=None),
        "altered histogram (H_7 + 1)": dict(base, hist=altered),
        "fallback dropped": dict(base, fallback=False),
        "reciprocal j = 576": dict(base, j=576),
        "reciprocal j = 578": dict(base, j=578),
        "factor 2 instead of 2^c": dict(base, two_power="2"),
    }


def check_pr3562_bytes(path):
    data = Path(path).read_bytes()
    need(hashlib.sha256(data).hexdigest() == PR3562_PROOF_SHA256, "PR3562 PROOF.md sha256")
    text = data.decode()
    for lit in ("{1:381024,2:400416,3:22752,4:26880,", "5:29376,6:17376,7:26784,42:288}",
                "W=28416", "epsilon=10^-16", "F=32*64^2*sum H_r=118606528512",
                "999998938581682162866772413602", "999998938581682162866772413603",
                "c=1/577,  w=ceil(e^c),  a=c(1-c)=576/332929", "T(n,w)<=200C n+1000000C n^(576/577)w.",
                "k<=8195w log2(e)<=16390e^c log2(e).", "4283584 C V e^(1-a)",
                "I use n<=e^(1-c), w<=2e^c and", "n^(1-c)w<=2^c e^(1-c+c^2)<(17/16)e^(1-a).",
                "C_complex=1729033982646513517717/10^24", "354445191478901059996907/(332929*10^24)>0."):
        need(lit in text, "PR3562 literal not found: " + lit)


def dec(x, digits=28):
    s = "-" if x < 0 else ""
    x = abs(x)
    i = x.numerator * 10**digits // x.denominator
    return s + str(i // 10**digits) + "." + str(i % 10**digits).zfill(digits)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pr3562-proof", help="optional path to PR3562's PROOF.md at head " + PR3562_HEAD)
    args = ap.parse_args()
    if args.pr3562_proof:
        check_pr3562_bytes(args.pr3562_proof)
        print("PR3562 PROOF.md bytes and audited literals: match")
    r = audit(CLAIM)
    (l1, h1), (l2, h2) = r["mu_t"]["E1"], r["mu_t"]["E2"]
    print("(a) mu_1 =", r["mu_1"], "<", Fr(199, 200))
    print("(a) mu_(576/577) E1 in [%s, %s], width %.3e" % (dec(l1, 33), dec(h1, 33), h1 - l1))
    print("(a) mu_(576/577) E2 in [%s, %s], width %.3e" % (dec(l2, 33), dec(h2, 33), h2 - l2))
    print("(a) both inside PR3562's 10^-30 enclosure and below 999999/10^6")
    print("(b) 200(1-mu_1) > 1 and 10^6(1-mu_(576/577)) > 1 under both engines")
    print("(c) 17^128 > 32*16^128; 2k/e <= 696575/2^20 < 1; 2^D(e) <= e^2 on [2, 2^20]; fit holds at e = 2^20")
    rmax, emax = depth_ratio_max(2**20)
    print("(c) side computation: max D(e)/floor(log2 e) on [2, 2^20] =", rmax, "first at e =", emax)
    print("(d) P5 = 2 calls x 2V x (200n + 10^6 n^(1-c) w) + (n+k+w+1): 801 = 2*2*200+1, 4000000 = 2*2*10^6")
    print("(d) 2^c < 17/16; log2 e <= 2e^((1-c)^2); (1+log2 V)^4 <= 512V; line-158 witness: the line-156 bounds alone allow n^(1-c)w = 2^(1-c) * 2^c e^(1-a)")
    print("(d) coefficient 801 + 4250000 + 32780 + 2 + 1 = %d (uses n <= e/w from line 117);" % CLAIM["coeff"],
          "the line-156 bounds n<=e^(1-c), w<=2e^c alone give factor 2: coefficient", r["coeff_cited_premises_only"])
    print("(e) a - C_complex = %s; reciprocal (1/j<b, (j-1)/j^2>C): %s" % (dec(r["a"] - CLAIM["C_complex"]), r["reciprocal"]))
    tpl = fit_and_composition(Fr(1, 576), 10**6)
    print("(c)-(d) parametric template at c = 1/576, M = 10^6 (PR3690's c; assumes the same D, K, P5 composition and A = 200; R437 moments not checked here): coefficient",
          tpl["coeff"], "a =", tpl["a"])
    blo, bhi = r["root"]
    print("root: fallback-inclusive root in (%s, %s] (selected bit_saving + 10^-24); E1 bracket (10/5769, 9/5192)" % (dec(blo, 24), dec(bhi, 24)))
    cl, ch = r["ceiling"]
    print("ceiling b(1-b) in [%s, %s]" % (dec(cl, 24), dec(ch, 24)))
    for name, X in ENDPOINTS.items():
        print("  %s X=%s: a-X=%s, b(1-b)-X in [%s, %s], 575/331776-X=%s" % (
            name, dec(X, 24), dec(r["a"] - X, 24), dec(cl - X, 24), dec(ch - X, 24), dec(tpl["a"] - X, 24)))
    cw, aw, Mw, kw = r["window"]
    print("window (E2 only, informational): c' = b_sel - 10^-9 gives c'(1-c') - X(PR3653) = %s with M = %d, coefficient %s"
          % (dec(aw - ENDPOINTS["PR3653 (rohanarun)"], 24), Mw, kw))
    failures = 0
    for name, params in controls().items():
        try:
            audit(params)
        except AuditFailure as exc:
            print("control rejected as required:", name, "->", exc)
            continue
        failures += 1
        print("CONTROL ACCEPTED (bad):", name)
    need(failures == 0, "%d control(s) accepted" % failures)
    print("PASS_PR3562_REPROOF_AUDIT: audited arithmetic steps (a)-(e) hold from P1-P5; line-156 bounds alone give factor 2, "
          "n <= e/w from line 117 gives 2^c; coefficient 4283584 justified")


if __name__ == "__main__":
    try:
        main()
    except AuditFailure as exc:
        print("FAIL:", exc)
        sys.exit(1)
