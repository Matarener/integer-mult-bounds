"""Independent operator-level audit of the productive-controller line (#4359 cover, #4440, #4441, #4447).

Sections (each prints one line; RESULT.json stores booleans and exact counts only):

  A  #4359 delayed BIT cover: Q_S D_P Q_S^-1 = D_(SPS^-1) with Q_S = diag(S, CSC), exact over
     Z/q^w, exhaustive on small general linear groups, plus fibre routing g -> gS and controls.
  B  #4440 p17 complex and p16 BIT controller words executed on concrete operators, every
     generator lifted to G^(tensor f), f = 1, 2, 3; literal owned-stream query shears;
     controls, including the stage-zero premise [D0, Q] = 0.
  C  #4447 retimed THREE-base native word (with #4441's 117 entrances, 42 exits, 395 gate
     retimings) executed with every frame realised as a random invertible matrix, both
     orientations, all 632 inputs, f = 1, 2, 3; controls.
  D  #4447's four new transports as dense 512 x 512 matrices built here from the gate list:
     support 2^r per column, modulus 2^(-r/2), and equality with the package lowering
     including absolute phase; the Q^-1 = Gaussian * Pauli identities.
  E  Frame screen: no strictly improving single-gate or whole-component retiming remains
     after #4447; positive control: from #4441's state the screen finds #4447's move.

The native word is synthesised by this file's own code (no predecessor interpreter or
synthesiser is imported).  clifford_exact.canonical_frame defines the frame operators and
its lower_child is used only as the object compared against in D.

Usage: python3.12 -B verify.py [--write]
"""
import gzip
import hashlib
import importlib.util
import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = HERE / "vendor"
NATIVE = ROOT / "research/kappa-rebuild/complex/full-identity-certificates"
CLIFFORD = ROOT / "research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py"
VENDORED = {
    "pr4440-COMPLEX-CONTROLLER.json": "bf1143325d8380fab40cd5a85449f9a5412f0340deba7f4693714c92ae320088",
    "pr4440-BIT-CONTROLLER.json": "39ac84fb848b908f7ba051fae4556d507900c421dc5d23501a9c0cb1d61fd08d",
    "pr4441-CHANGES.json": "cde73b8ff5b3c0d06e69e2293b991b24fd14a16dd4ccab7ff6b3439074a94624",
    "pr4447-PATCH.json": "9ab5328245ff02c9d0be21d39bcc375f50bc5d7909e9f7b9a3a9a6f812f5bd6e",
}
TOL = 1e-6        # numerical endpoint tolerance (observed errors are 1e-15 .. 6e-9)
FAIL = 1e-3       # a control counts as rejected when its error exceeds this


def need(ok, why):
    if not ok:
        raise SystemExit("FAIL: " + why)


def read_json(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith(".gz") else data)


def vendored(name):
    data = (VENDOR / name).read_bytes()
    need(hashlib.sha256(data).hexdigest() == VENDORED[name], "vendored input drift: " + name)
    return json.loads(data)


# ----------------------------------------------------------------------------- A: cover algebra

def mm(A, B, m):
    return tuple(tuple(sum(a * b for a, b in zip(r, c)) % m for c in zip(*B)) for r in A)


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def msub(A, B, m):
    return tuple(tuple((a - b) % m for a, b in zip(r, s)) for r, s in zip(A, B))


def blk(A, B, C, D):
    return tuple(ra + rb for ra, rb in zip(A, B)) + tuple(rc + rd for rc, rd in zip(C, D))


def zero(n):
    return tuple((0,) * n for _ in range(n))


def minv(A, q, m):
    k = len(A)
    A = [list(r) for r in A]
    I = [list(r) for r in eye(k)]
    for col in range(k):
        piv = next((r for r in range(col, k) if A[r][col] % q), None)
        if piv is None:
            return None
        A[col], A[piv] = A[piv], A[col]
        I[col], I[piv] = I[piv], I[col]
        iv = pow(A[col][col], -1, m)
        A[col] = [x * iv % m for x in A[col]]
        I[col] = [x * iv % m for x in I[col]]
        for r in range(k):
            if r != col and A[r][col]:
                f = A[r][col]
                A[r] = [(a - f * b) % m for a, b in zip(A[r], A[col])]
                I[r] = [(a - f * b) % m for a, b in zip(I[r], I[col])]
    return tuple(map(tuple, I))


def rank_q(A, q):
    rows = [[v % q for v in r] for r in A]
    rk = 0
    for col in range(len(rows[0])):
        piv = next((r for r in range(rk, len(rows)) if rows[r][col]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        iv = pow(rows[rk][col], -1, q)
        rows[rk] = [v * iv % q for v in rows[rk]]
        for r in range(len(rows)):
            if r != rk and rows[r][col]:
                f = rows[r][col]
                rows[r] = [(a - f * b) % q for a, b in zip(rows[r], rows[rk])]
        rk += 1
    return rk


def DP(P, C, m):
    I = eye(len(P))
    return blk(msub(I, P, m), mm(P, C, m), mm(C, P, m), msub(I, mm(mm(C, P, m), C, m), m))


def QS(S, C, m):
    return blk(S, zero(len(S)), zero(len(S)), mm(mm(C, S, m), C, m))


def cover_exhaustive(q, w, n, sample_S, rng):
    m = q ** w
    mats = [tuple(tuple(f[i * n:(i + 1) * n]) for i in range(n)) for f in itertools.product(range(m), repeat=n * n)]
    group = [(S, minv(S, q, m)) for S in mats]
    group = [(S, Si) for S, Si in group if Si is not None]
    gset = {S for S, _ in group}
    idem = [P for P in mats if mm(P, P, m) == P]
    invol = [C for C, _ in group if mm(C, C, m) == eye(n)]
    bad_C = [C for C, _ in group if mm(C, C, m) != eye(n)]
    Ss = group if sample_S is None else rng.sample(group, sample_S)
    t = dict(group=len(group), idempotents=len(idem), involutions=len(invol), checks=0, covariance=0,
             rank_kept=0, wrong_lower_block_tested=0, wrong_lower_block_rejected=0)
    for C in invol:
        for P in idem:
            D = DP(P, C, m)
            for S, Si in Ss:
                P2 = mm(mm(S, P, m), Si, m)
                t["checks"] += 1
                t["covariance"] += mm(mm(QS(S, C, m), D, m), QS(Si, C, m), m) == DP(P2, C, m)
                t["rank_kept"] += rank_q(P2, q) == rank_q(P, q)
                if mm(mm(C, S, m), C, m) != S:
                    t["wrong_lower_block_tested"] += 1
                    W = blk(S, zero(n), zero(n), S)
                    Wi = blk(Si, zero(n), zero(n), Si)
                    t["wrong_lower_block_rejected"] += mm(mm(W, D, m), Wi, m) != DP(P2, C, m)
    fib = 0
    for S, Si in rng.sample(group, min(len(group), 24)):
        ok = {mm(g, S, m) for g, _ in group} == gset
        for P in rng.sample(idem, min(len(idem), 4)):
            P2 = mm(mm(S, P, m), Si, m)
            for g, gi in group:
                gS = mm(g, S, m)
                ok &= mm(mm(gS, P, m), minv(gS, q, m), m) == mm(mm(g, P2, m), gi, m)
        fib += ok
    t["fibre_routing_ok"] = fib
    rej = 0
    for C in rng.sample(bad_C, min(len(bad_C), 20)):
        Ci = minv(C, q, m)
        broke = False
        for P in rng.sample(idem, min(len(idem), 6)):
            for S, Si in rng.sample(group, min(len(group), 8)):
                Qi = blk(Si, zero(n), zero(n), mm(mm(Ci, Si, m), Ci, m))
                broke |= mm(mm(QS(S, C, m), DP(P, C, m), m), Qi, m) != DP(mm(mm(S, P, m), Si, m), C, m)
        rej += broke
    t["non_involution_C_tested"] = min(len(bad_C), 20)
    t["non_involution_C_rejected"] = rej
    return t


def section_A():
    rng = random.Random(4359)
    out = {}
    for q, w, n, sample in [(2, 1, 2, None), (2, 2, 2, None), (3, 1, 2, None), (2, 1, 3, 30)]:
        t = cover_exhaustive(q, w, n, sample, rng)
        need(t["covariance"] == t["checks"] == t["rank_kept"], f"cover covariance q={q} w={w} n={n}")
        need(t["wrong_lower_block_rejected"] > 0.8 * t["wrong_lower_block_tested"], "wrong lower block control")
        need(t["non_involution_C_rejected"] == t["non_involution_C_tested"], "C^2 != I control")
        need(t["fibre_routing_ok"] == min(t["group"], 24), "fibre routing")
        out[f"q{q}_w{w}_n{n}" + ("" if sample is None else f"_S{sample}")] = t
    C = None
    for q, w, n, trials in [(2, 8, 6, 200), (2, 16, 8, 100), (2, 30, 12, 30), (3, 5, 7, 100)]:
        m = q ** w
        C = tuple(tuple(int(i + j == n - 1) for j in range(n)) for i in range(n))
        ok = 0
        for _ in range(trials):
            while True:
                S = tuple(tuple(rng.randrange(m) for _ in range(n)) for _ in range(n))
                Si = minv(S, q, m)
                if Si:
                    break
            while True:
                T = tuple(tuple(rng.randrange(m) for _ in range(n)) for _ in range(n))
                Ti = minv(T, q, m)
                if Ti:
                    break
            k = rng.randrange(0, n + 1)
            P = mm(mm(T, tuple(tuple(int(i == j and i < k) for j in range(n)) for i in range(n)), m), Ti, m)
            P2 = mm(mm(S, P, m), Si, m)
            ok += (mm(mm(QS(S, C, m), DP(P, C, m), m), QS(Si, C, m), m) == DP(P2, C, m)
                   and rank_q(P2, q) == k)
        need(ok == trials, f"random cover q={q} w={w}")
        out[f"random_q{q}_w{w}_n{n}"] = dict(checks=trials, passed=ok)
    print("A  cover covariance: all exhaustive and random cases hold; controls rejected", flush=True)
    return out


# ----------------------------------------------------------------------------- B: controllers

def kpow(M, f):
    out = np.eye(1, dtype=M.dtype)
    for _ in range(f):
        out = np.kron(out, M)
    return out


def replay_controller(word, G, binary, p, drop_query=None, query_with_Q=False):
    red = (lambda a: np.mod(a, 2)) if binary else (lambda a: a)
    Q, Qi, Ds = G["Q"], G["Qi"], G["D"]
    d = Q.shape[0]
    A = [[np.eye(d, dtype=Q.dtype) if i == j else np.zeros((d, d), dtype=Q.dtype) for j in range(2 * p)]
         for i in range(2 * p)]
    qn = 0
    for ev in word:
        op = ev[0]
        if op in ("LOCAL", "QUERY_SHEAR"):
            _, stage, pair, backward = ev
            x, y = 2 * pair, 2 * pair + 1
            if op == "QUERY_SHEAR":
                qn += 1
                if drop_query == qn:
                    continue
            if backward:
                x, y, T = y, x, -Q
            else:
                T = Q if (query_with_Q and op == "QUERY_SHEAR") else Qi
            A[y] = [red(a + T @ b) for a, b in zip(A[y], A[x])]
            if op == "LOCAL":
                for r in (x, y):
                    A[r] = [red(Ds[stage] @ a) for a in A[r]]
        elif op == "IDLE":
            M = np.eye(d, dtype=Q.dtype)
            for s in ev[2]:
                M = red(Ds[s] @ M)
            for r in (2 * ev[1], 2 * ev[1] + 1):
                A[r] = [red(M @ a) for a in A[r]]
        elif op == "ADD":
            c = ev[3] if len(ev) > 3 else 1
            A[ev[1]] = [red(a + c * b) for a, b in zip(A[ev[1]], A[ev[2]])]
        elif op in ("SWAP", "SIGNED_SWAP"):
            s = -1 if op == "SIGNED_SWAP" else 1
            A[ev[1]], A[ev[2]] = A[ev[2]], [red(s * a) for a in A[ev[1]]]
        else:
            need(False, "unknown controller event " + op)
    return A


def monomial(term, G, binary):
    M = np.eye(G["Q"].shape[0], dtype=G["Q"].dtype)
    if binary:
        e0, ex = term & 1, [(term >> (s + 1)) & 1 for s in range(len(G["D"]))]
    else:
        e0, ex = term[0], term[1:]
    for s, e in enumerate(ex):
        for _ in range(e):
            M = G["D"][s] @ M
    for _ in range(abs(e0)):
        M = (G["Q"] if e0 > 0 else G["Qi"]) @ M
    return np.mod(M, 2) if binary else M


def endpoint(A, L, R, diag, G, binary):
    n, d = len(A), G["Q"].shape[0]
    if binary:   # float64 BLAS is exact here: every entry stays far below 2^53 before reduction
        M = np.mod(np.kron(L, np.eye(d)) @ np.block(A).astype(float), 2)
        M = np.mod(M @ np.kron(R, np.eye(d)), 2)
    else:
        M = np.kron(L, np.eye(d)) @ np.block(A) @ np.kron(R, np.eye(d))
    off = on = 0.0
    for i in range(n):
        for j in range(n):
            b = M[i * d:(i + 1) * d, j * d:(j + 1) * d]
            if i == j:
                on = max(on, float(np.max(np.abs(b - monomial(diag[i], G, binary)))))
            else:
                off = max(off, float(np.max(np.abs(b))))
    return max(off, on), off


def complex_gens(stages, d, f, rng, noncommuting=None):
    P = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))
    Pi = np.linalg.inv(P)
    mk = lambda: P @ np.diag(np.exp(2j * np.pi * rng.random(d)) * (0.5 + rng.random(d))) @ Pi
    Q, D = mk(), [mk() for _ in range(stages)]
    if noncommuting is not None:
        D[noncommuting] = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))
    G = {"Q": kpow(Q, f), "D": [kpow(x, f) for x in D]}
    G["Qi"] = np.linalg.inv(G["Q"])
    return G


def stage0_gens(stages, rng, commuting):
    """V = A (old nine axes, incl. the central one) x B (fresh blocks); D0 = (F q^-1) x I."""
    a, b = 2, 3
    q = rng.standard_normal((a, a)) + 1j * rng.standard_normal((a, a))
    F = q @ q if commuting else rng.standard_normal((a, a)) + 1j * rng.standard_normal((a, a))
    P = rng.standard_normal((b, b)) + 1j * rng.standard_normal((b, b))
    Pi = np.linalg.inv(P)
    G = {"Q": np.kron(q, np.eye(b)), "Qi": np.kron(np.linalg.inv(q), np.eye(b)),
         "D": [np.kron(F @ np.linalg.inv(q), np.eye(b))]}
    for _ in range(1, stages):
        G["D"].append(np.kron(np.eye(a), P @ np.diag(rng.standard_normal(b) + 1j * rng.standard_normal(b)) @ Pi))
    return G


def translation(v, k):
    M = np.zeros((1 << k, 1 << k), dtype=np.int64)
    for x in range(1 << k):
        M[x ^ v, x] = 1
    return M


def bit_gens(stages, k, f, rng, bad=None):
    N = 1 << k
    Q = translation(int(rng.integers(1, N)), k)
    D = [translation(int(rng.integers(0, N)), k) for _ in range(stages)]
    if bad == "Q_not_involution":
        perm = list(range(N))
        perm[0], perm[1], perm[2] = 1, 2, 0
        Q = np.eye(N, dtype=np.int64)[perm]
    if bad == "D_noncommuting":
        D[3] = np.eye(N, dtype=np.int64)[list(rng.permutation(N))]
    G = {"Q": kpow(Q, f), "D": [kpow(x, f) for x in D]}
    G["Qi"] = np.mod(np.round(np.linalg.inv(G["Q"])).astype(np.int64), 2)
    return G


def section_B():
    rng = np.random.default_rng(4440)
    out = {}
    w = vendored("pr4440-COMPLEX-CONTROLLER.json")
    p, word = w["pairs"], w["physical_events"]
    st = 2 * p + 1
    L = np.array([[complex(Fraction(x)) for x in r] for r in w["boundaries"]["left"]])
    R = np.array([[complex(Fraction(x)) for x in r] for r in w["boundaries"]["right"]])
    diag = [tuple(t) for t in w["diagonal"]]
    cx = dict(pairs=p, full_native_calls=sum(e[0] == "LOCAL" for e in word),
              query_shears=sum(e[0] == "QUERY_SHEAR" for e in word))
    need(cx["full_native_calls"] == 19 and cx["query_shears"] == 16, "complex p17 call counts")
    for f, d in [(1, 4), (2, 3), (3, 3)]:
        G = complex_gens(st, d, f, rng)
        err, _ = endpoint(replay_controller(word, G, False, p), L, R, diag, G, False)
        need(err < TOL, f"complex controller endpoint f={f}: {err}")
        cx[f"commuting_lift_f{f}_holds"] = True
    # literal owned-stream query shears
    G = complex_gens(st, 3, 2, rng)
    dd = G["Q"].shape[0]
    worst = 0.0
    for ev in word:
        if ev[0] != "QUERY_SHEAR":
            continue
        X = rng.standard_normal(dd) + 1j * rng.standard_normal(dd)
        Y = rng.standard_normal(dd) + 1j * rng.standard_normal(dd)
        X0, Y0 = X.copy(), Y.copy()
        src, dst, Gm, sg = (Y, X, G["Q"], -1) if ev[3] else (X, Y, G["Qi"], 1)
        Z = np.zeros(dd, dtype=complex) + src
        Z = Gm @ Z
        dst += sg * Z
        Z = Z - Gm @ src
        want = (X0 - G["Q"] @ Y0) if ev[3] else (Y0 + G["Qi"] @ X0)
        worst = max(worst, float(np.max(np.abs(Z))), float(np.max(np.abs(dst - want))),
                    float(np.max(np.abs((Y if ev[3] else X) - (Y0 if ev[3] else X0)))))
    need(worst < TOL, "literal query shear")
    cx["literal_owned_stream_query_shears_hold"] = True
    G = complex_gens(st, 3, 1, rng)
    ctl = {
        "query_uses_Q_not_Qinv": endpoint(replay_controller(word, G, False, p, query_with_Q=True), L, R, diag, G, False)[0],
        "one_query_shear_deleted": endpoint(replay_controller(word, G, False, p, drop_query=5), L, R, diag, G, False)[0],
    }
    G2 = complex_gens(st, 3, 1, rng, noncommuting=5)
    ctl["D5_not_commuting"] = endpoint(replay_controller(word, G2, False, p), L, R, diag, G2, False)[0]
    G3 = stage0_gens(st, rng, commuting=False)
    ctl["stage0_D0_not_commuting_with_Q"] = endpoint(replay_controller(word, G3, False, p), L, R, diag, G3, False)[1]
    for k, v in ctl.items():
        need(v > FAIL, "complex control accepted: " + k)
    cx["controls_rejected"] = sorted(ctl)
    G4 = stage0_gens(st, rng, commuting=True)
    e4, _ = endpoint(replay_controller(word, G4, False, p), L, R, diag, G4, False)
    need(e4 < TOL, "stage-zero D0 = F q^-1 with [F, q] = 0 must pass")
    cx["stage0_D0_commuting_with_Q_holds"] = True
    out["complex_p17"] = cx

    w = vendored("pr4440-BIT-CONTROLLER.json")
    p, word = w["pairs"], w["physical_events"]
    st, n = 2 * p + 1, 2 * p
    bits = lambda rows: np.array([[(rows[i] >> j) & 1 for j in range(n)] for i in range(n)], dtype=np.int64)
    L, R = bits(w["boundaries"]["left_rows"]), bits(w["boundaries"]["right_rows"])
    diag = w["boundaries"]["diagonal_monomials"]
    bt = dict(pairs=p, full_native_calls=sum(e[0] == "LOCAL" for e in word),
              query_shears=sum(e[0] == "QUERY_SHEAR" for e in word))
    need(bt["full_native_calls"] == 18 and bt["query_shears"] == 15, "BIT p16 call counts")
    for f, k in [(1, 5), (2, 3), (3, 2)]:
        for trial in range(2):
            G = bit_gens(st, k, f, rng)
            err, _ = endpoint(replay_controller(word, G, True, p), L, R, diag, G, True)
            need(err == 0, f"BIT controller endpoint f={f}")
        bt[f"commuting_involution_lift_f{f}_holds"] = True
    G = bit_gens(st, 4, 1, rng)
    ctl = {"one_query_shear_deleted": endpoint(replay_controller(word, G, True, p, drop_query=4), L, R, diag, G, True)[0]}
    for bad in ("Q_not_involution", "D_noncommuting"):
        Gb = bit_gens(st, 4, 1, rng, bad=bad)
        ctl[bad] = endpoint(replay_controller(word, Gb, True, p), L, R, diag, Gb, True)[0]
    for k, v in ctl.items():
        need(v > 0, "BIT control accepted: " + k)
    bt["controls_rejected"] = sorted(ctl)
    out["bit_p16"] = bt
    print("B  #4440 controllers: endpoints hold at f = 1, 2, 3; controls rejected; "
          "the identity needs [D0, Q] = 0", flush=True)
    return out


# ----------------------------------------------------------------------------- C: native word

def gate_index(program):
    """(phase, ordinal) -> index of every persistent scalar gate whose roles are all L."""
    phase, count, out = None, {}, {}
    for i, e in enumerate(program):
        if e[0] == "phase":
            phase = e[1]
        if e[0] == "scalar":
            g = e[1]
            roles = g[1:3] if g[0] in ("add", "copy") else g[1:2]
            if all(r[0] == "L" for r in roles):
                k = count.get(phase, 0)
                out[phase, k] = i
                count[phase] = k + 1
    return out


def subspace(basis):
    pts = {0}
    for x in basis:
        pts |= {v ^ x for v in tuple(pts)}
    return frozenset(pts)


def synthesize(c, program):
    """Own synthesis: drop recorded climbs; climb each L role to every gate/warp entry frame."""
    spaces = [subspace(b) for b in c["frames"]]
    cur = list(c["start"])
    out = []

    def climb(r, f):
        if cur[r] != f:
            need(spaces[cur[r]] < spaces[f], "nested positive climb")
            out.append(["climb", r, cur[r], f, len(c["frames"][f]) - len(c["frames"][cur[r]])])
            cur[r] = f
    for e in program:
        if e[0] == "climb":
            continue
        if e[0] == "scalar":
            g = e[1]
            for r in (g[1:3] if g[0] in ("add", "copy") else g[1:2]):
                if r[0] == "L":
                    climb(r[1], e[2])
        elif e[0] == "warp":
            climb(e[1][1], e[3])
            cur[e[1][1]] = e[4]
        out.append(e)
    for r, f in enumerate(c["final"]):
        climb(r, f)
    return out


def native_state(apply_patch=True):
    c = read_json(NATIVE / "THREE-base-FULL-IDENTITY-CANONICAL.json.gz")
    prog = read_json(NATIVE / "THREE-base-FULL-IDENTITY-NATIVE.json.gz")
    ch = vendored("pr4441-CHANGES.json")
    for key, field in (("entrances", "start"), ("exits", "final")):
        for role, old, new in ch[key]:
            need(c[field][role] == old, "pinned helper boundary")
            c[field][role] = new
    for d, p in prog.items():
        idx = gate_index(p)
        for phase, k, old, new in ch["gates"]:
            need(p[idx[phase, k]][2] == old, "pinned retimed gate")
            p[idx[phase, k]][2] = new
    patch = vendored("pr4447-PATCH.json")
    new_frame = None
    if apply_patch:
        need(c["frames"][patch["old_frame"]] == patch["old_basis"], "pinned old frame")
        new_frame = len(c["frames"])
        c["frames"].append(patch["new_basis"])
        for d, p in prog.items():
            i = gate_index(p)[patch["phase"], patch["ordinal"]]
            need(p[i][2] == patch["old_frame"], "pinned changed contact")
            p[i][2] = new_frame
    return c, prog, new_frame, patch


def execute_native(c, program, backward, d, f, rng, skip_climb=None, mismatch=None, alias=None):
    D = d ** f
    lift = lambda M: kpow(M, f)
    Cf = [lift(rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))) for _ in c["frames"]]
    if alias:
        Cf[alias[0]] = Cf[alias[1]]
    Ci = [np.linalg.inv(M) for M in Cf]
    gens = {}

    def G(op):
        k = abs(op)
        if k not in gens:
            M = lift(rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d)))
            M = np.linalg.inv(M).T if backward else M
            gens[k] = (M, np.linalg.inv(M))
        return gens[k][0] if op > 0 else gens[k][1]
    x = {("L", i): rng.standard_normal(D) + 1j * rng.standard_normal(D) for i in range(632)}
    fr = {("L", i): f0 for i, f0 in enumerate(c["start"])}
    v = {r: Cf[fr[r]] @ u for r, u in x.items()}
    climbs = 0
    for e in program:
        k = e[0]
        if k == "climb":
            _, r, a, b, _rank = e
            climbs += 1
            role = ("L", r)
            need(fr[role] == a, "climb source frame")
            fr[role] = b
            if skip_climb == climbs:
                continue
            Cb = Cf[b] if mismatch != (r, a, b) else Cf[b - 1]
            v[role] = Cb @ (Ci[a] @ v[role])
        elif k == "center":
            role = ("C", e[1])
            if role in v:
                v[role] = Cf[e[3]] @ (Ci[e[2]] @ v[role])
        elif k == "warp":
            role = tuple(e[1])
            need(fr[role] == e[3], "warp entry frame")
            v[role] = Cf[e[4]] @ (G(e[2]) @ (Ci[e[3]] @ v[role]))
            fr[role] = e[4]
        elif k == "scalar":
            op = e[1]
            t = tuple(op[1])
            if op[0] == "clear":
                v[t] = np.zeros(D, dtype=complex)
            elif op[0] == "copy":
                v[t] = v[tuple(op[2])].copy()
            elif op[0] == "add":
                v[t] = v[t] + complex(Fraction(op[3], op[4])) * v[tuple(op[2])]
            else:
                v[t] = complex(Fraction(op[2], op[3])) * v[t]
        elif k not in ("phase", "adapter", "residual_adapter"):
            need(False, "unknown native event " + k)
    scale = max(float(np.max(np.abs(u))) for u in x.values())
    err = 0.0
    for i in range(632):
        role = ("L", i)
        need(fr[role] == c["final"][i], "final frame")
        want = x[role].copy()
        if backward and i < 112:
            want = want - x[("L", 112 + i)]
        if not backward and 112 <= i < 224:
            want = want + x[("L", i - 112)]
        err = max(err, float(np.max(np.abs(Ci[fr[role]] @ v[role] - want))))
    cz = max([float(np.max(np.abs(v[r]))) for r in v if r[0] == "C"] or [0.0])
    return err / scale, cz / scale, climbs


def section_C():
    c, prog, new_frame, patch = native_state()
    rng = np.random.default_rng(4447)
    out = dict(frames=len(c["frames"]), new_frame=new_frame)
    for direction in ("forward", "backward"):
        program = synthesize(c, prog[direction])
        bw = direction == "backward"
        prof = {}
        for e in program:
            if e[0] == "climb":
                prof[e[4]] = prof.get(e[4], 0) + 1
        need(prof == {1: 2254, 2: 514, 3: 444, 4: 103, 5: 40}, "own synthesis reproduces #4447's L-role bill")
        row = dict(events=len(program), climbs=sum(e[0] == "climb" for e in program),
                   scalar_gates=sum(e[0] == "scalar" for e in program), warps=sum(e[0] == "warp" for e in program),
                   L_role_paid_profile={str(k): prof[k] for k in sorted(prof)})
        for f, d in [(1, 3), (2, 3), (3, 2)]:
            err, cz, _ = execute_native(c, program, bw, d, f, rng)
            need(err < TOL and cz < TOL, f"native endpoint {direction} f={f}: {err}")
            row[f"physical_frames_f{f}_holds"] = True
        climbs = [e for e in program if e[0] == "climb"]
        first = next(k for k, e in enumerate(climbs, 1) if e[3] == new_frame)
        into = next(e for e in climbs if e[3] == new_frame)
        ctl = {"skip_climb_into_new_frame": execute_native(c, program, bw, 3, 1, rng, skip_climb=first)[0],
               "new_frame_realised_differently_on_one_transport":
                   execute_native(c, program, bw, 3, 1, rng, mismatch=(into[1], into[2], into[3]))[0]}
        for k, v in ctl.items():
            need(v > FAIL, "native control accepted: " + k)
        row["controls_rejected"] = sorted(ctl)
        e_alias = execute_native(c, program, bw, 3, 1, rng, alias=(new_frame, patch["old_frame"]))[0]
        need(e_alias < TOL, "any common frame operator must work")
        row["new_frame_realised_as_old_frame_everywhere_holds"] = True
        out[direction] = row
    print("C  #4447 native word with physical frames: both orientations hold at f = 1, 2, 3; controls rejected",
          flush=True)
    return out, c, prog, new_frame


# ----------------------------------------------------------------------------- D: transports

def _par(x):
    return x.bit_count() & 1


def _mv(rows, x):
    return sum(_par(r & x) << i for i, r in enumerate(rows))


def _qv(Q, alpha, x, n):
    return (sum(alpha[i] for i in range(n) if x >> i & 1)
            + 2 * sum(_par((Q[i] >> (i + 1)) & (x >> (i + 1))) for i in range(n) if x >> i & 1)) % 4


def dense(n, circuit):
    N = 1 << n
    U = np.eye(N, dtype=complex)
    for e in circuit:
        if e[0] in ("P", "X"):
            M = np.zeros((N, N))
            for x in range(N):
                M[_mv(e[1], x) if e[0] == "P" else x ^ e[1], x] = 1
        elif e[0] == "D":
            M = np.diag([1j ** _qv(e[1], e[2], x, n) for x in range(N)])
        elif e[0] == "phase":
            M = (1j ** e[1]) * np.eye(N)
        elif e[0] == "C":
            Xq = np.zeros((N, N))
            for x in range(N):
                Xq[x ^ e[1], x] = 1
            a = (1 + 1j) / 2 if e[2] > 0 else (1 - 1j) / 2
            M = a * np.eye(N) + np.conj(a) * Xq
        else:
            need(False, "unknown gate")
        U = M @ U
    return U


def section_D(c, prog, new_frame):
    spec = importlib.util.spec_from_file_location("imb_clifford_exact", CLIFFORD)
    ce = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ce)
    program = synthesize(c, prog["forward"])
    edges = sorted({(e[2], e[3]) for e in program if e[0] == "climb" and new_frame in (e[2], e[3])})
    need(len(edges) == 4, "four new transports")
    rows = []
    for a, b in edges:
        r = len(c["frames"][b]) - len(c["frames"][a])
        op = ce.canonical_frame(9, c["frames"][a]).adjoint().then(ce.canonical_frame(9, c["frames"][b]))
        for orient, actual in (("forward", op), ("backward", op.adjoint())):
            U = dense(9, actual.circuit)
            need(np.max(np.abs(U.conj().T @ U - np.eye(512))) < 1e-12, "unitary")
            nz = np.abs(U) > 1e-12
            need(set(nz.sum(axis=0).tolist()) == {1 << r}, f"support 2^{r} per column")
            need(np.allclose(np.abs(U[nz]), 2 ** (-r / 2)), "equal moduli")
            rec, compiled = ce.lower_child(actual)
            need(rec["rank"] == r, "package lowering rank")
            need(np.max(np.abs(dense(9, compiled.circuit) - U)) < 1e-12, "lowering equals transport with phase")
        rows.append(dict(source=a, target=b, rank=r, support_per_column=1 << r,
                         lowering_matches_with_absolute_phase=True))
    need(sorted(x["rank"] for x in rows) == [1, 1, 2, 4], "#4447's new ranks [1,1,2,4]")
    rng = np.random.default_rng(1159)
    for n in (1, 2, 3, 4):
        N = 1 << n
        for _ in range(20):
            q = int(rng.integers(1, N))
            need(np.max(np.abs(dense(n, [("C", q, -1)]) - dense(n, [("C", q, 1), ("X", q)]))) < 1e-14,
                 "C(q,-1) = X^q C(q,+1)")
            A = np.triu(rng.integers(0, 2, (n, n)), 1)
            A = A + A.T
            Qm = tuple(sum(int(A[i, j]) << j for j in range(n)) for i in range(n))
            al = tuple(int(x) for x in rng.integers(0, 4, n))
            Dp = dense(n, [("D", Qm, al)])
            Z = np.diag([(-1) ** sum(al[i] for i in range(n) if x >> i & 1) for x in range(N)])
            need(np.max(np.abs(np.conj(Dp) - Z @ Dp)) < 1e-14, "D^-1 = Z^alpha D")
    print("D  #4447 transports: ranks 1, 1, 2, 4 with exact phases; Q^-1 = Gaussian * Pauli holds", flush=True)
    return dict(transports=rows, inverse_gaussian_identities_hold=True)


# ----------------------------------------------------------------------------- E: frame screen

def rref(vs):
    piv = {}
    for x in vs:
        for b, v in piv.items():
            if x >> b & 1:
                x ^= v
        if x:
            b = x.bit_length() - 1
            for k in list(piv):
                if piv[k] >> b & 1:
                    piv[k] ^= x
            piv[b] = x
    return tuple(sorted(piv.values()))


def chains(c, program):
    ch = {r: [("start", -1, f, f)] for r, f in enumerate(c["start"])}
    for i, e in enumerate(program):
        if e[0] == "scalar":
            g = e[1]
            for r in (g[1:3] if g[0] in ("add", "copy") else g[1:2]):
                if r[0] == "L":
                    ch[r[1]].append(("gate", i, e[2], e[2]))
        elif e[0] == "warp":
            ch[e[1][1]].append(("warp", i, e[3], e[4]))
    for r, f in enumerate(c["final"]):
        ch[r].append(("final", -1, f, f))
    return ch


def screen(c, prog, ts=(0.997, 0.9999)):
    """Best strictly improving single-gate and whole-component retimings (dimension screen)."""
    sp = [rref(b) for b in c["frames"]]
    pts = {}

    def points(s):
        if s not in pts:
            pts[s] = subspace(s)
        return pts[s]
    keys = {d: gate_index(p) for d, p in prog.items()}
    inv = {d: {i: k for k, i in keys[d].items()} for d in prog}
    chs = {d: chains(c, p) for d, p in prog.items()}
    parent = {k: k for k in keys["forward"]}

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k
    for d, ch in chs.items():
        for r, seq in ch.items():
            for a, b in zip(seq, seq[1:]):
                if a[0] == b[0] == "gate" and a[2] == b[2] and a[1] in inv[d] and b[1] in inv[d]:
                    x, y = find(inv[d][a[1]]), find(inv[d][b[1]])
                    if x != y:
                        parent[x] = y
    comps = {}
    for k in keys["forward"]:
        comps.setdefault(find(k), []).append(k)
    groups = [[k] for k in keys["forward"]] + [v for v in comps.values() if len(v) > 1]

    where = {d: {} for d in chs}            # event index -> [(role, position in chain)]
    for d, ch in chs.items():
        for r, seq in ch.items():
            for k, item in enumerate(seq):
                if item[0] == "gate":
                    where[d].setdefault(item[1], []).append((r, k))

    def best_move(group):
        bnd = []
        for d, ch in chs.items():
            per_role = {}
            for key in group:
                for r, k in where[d][keys[d][key]]:
                    per_role.setdefault(r, []).append(k)
            for r, ks in per_role.items():
                seq = ch[r]
                ks = sorted(set(ks))
                start = prev = ks[0]
                for k in ks[1:] + [None]:
                    if k is not None and k == prev + 1:
                        prev = k
                        continue
                    bnd.append((seq[start - 1][3], seq[prev + 1][2]))
                    if k is not None:
                        start = prev = k
        low = rref([x for p_, _ in bnd for x in sp[p_]])
        up = None
        for _, n_ in bnd:
            up = points(sp[n_]) if up is None else up & points(sp[n_])
        up = rref(up)
        if len(rref(up + low)) != len(up):
            return None
        cur = len(sp[prog["forward"][keys["forward"][group[0]]][2]])
        dims = [(len(sp[p_]), len(sp[n_])) for p_, n_ in bnd]
        cost = lambda g, t: sum((0 if a == g else (g - a) ** t) + (0 if b == g else (b - g) ** t) for a, b in dims)
        best = None
        for g in range(len(low), len(up) + 1):
            gain = [cost(cur, t) - cost(g, t) for t in ts]
            if min(gain) > 1e-9 and (best is None or gain[0] > best[0][0]):
                best = (gain, g, low)
        return best
    found = []
    for grp in groups:
        b = best_move(grp)
        if b:
            found.append((b[0][0], grp, b))
    return len(keys["forward"]), len(comps), sorted(found, reverse=True)


def section_E():
    c, prog, _, patch = native_state(apply_patch=False)
    gates, comps, found = screen(c, prog)
    need(found, "control: the screen must find a move on #4441's state")
    _, grp, (gain, g, low) = found[0]
    need(grp == [(patch["phase"], patch["ordinal"])] and g == 3 and
         set(subspace(low)) == set(subspace(patch["new_basis"])), "control rediscovers #4447's span move")
    c, prog, _, _ = native_state(apply_patch=True)
    gates2, comps2, found2 = screen(c, prog)
    need(not found2, "no further strictly improving retiming expected")
    print(f"E  frame screen: control finds #4447's move on #4441's state; after #4447 none of {gates2} gates "
          f"or {comps2} constant-frame components improves", flush=True)
    return dict(control_on_pr4441_state=dict(gate=list(grp[0]), dimension=g, span_matches_pr4447=True),
                after_pr4447=dict(retimeable_gates=gates2, constant_frame_components=comps2, improving_moves=0))


def main():
    result = {"schema_version": 1, "base_commit": "2a13eb1827784206202db90e5dc8327cf8a250db",
              "pr_heads": {"4440": "40e22a83ed660d3d6074c4f2dbf14bfb621eee51",
                           "4441": "5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39",
                           "4447": "322e0ec764aa7ef7801383feb1f656e460dd8bed"}}
    result["A_cover_covariance"] = section_A()
    result["B_controllers"] = section_B()
    native, c, prog, new_frame = section_C()
    result["C_native_word"] = native
    result["D_transports"] = section_D(c, prog, new_frame)
    result["E_frame_screen"] = section_E()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = HERE / "RESULT.json"
    if "--write" in sys.argv:
        path.write_text(text, encoding="utf-8", newline="\n")
    else:
        need(path.read_text(encoding="utf-8") == text, "RESULT.json differs from this replay")
    print("PASS_PRODUCTIVE_CONTROLLER_LIFT_AUDIT", flush=True)


if __name__ == "__main__":
    main()
