# SPDX-License-Identifier: Apache-2.0
"""Scope A: an own fixed-inventory LP ceiling for the staged 644/660 supplier and its attainment by PR3633 (see the
provenance note below).

Model (PR3633 ceiling/PROOF.md and owners/UPSTREAM-PROOF.md; PR3630's check_budget.py literal constants are parsed
and compared below and state the same model with T = 740, live 896 T).  Helper widths W = (4,5,6,7,8,9) with per-call
inventory I = (26,2,18,52,97,213) and per-call local paid bill L = 2439H1+726H2+224H3+102H4+20H5+8H8; nine calls per
replica; per replica n = (672,448,448,448) bins of capacities (8,16,32,48) (18 source children x 112 ports); live
stock 896 per replica; dimension 73; H_r(a) = r^(1-a).  Over its lifetime a bin holds a multiset of helper roles (a
pattern p, p_w roles of width w) with |p| = sum_w w p_w <= cap and is charged one idle child H_{cap-|p|} (nothing
when |p| = cap).  The complete profile of T replicas is 9T copies of L plus the idle children; its moment is
M_T(a) = sum_r n_r r (73/r)^a / (73 * 896 T) (audit_kappa.moment with live = 896T) and its 24-digit endpoint C is
the largest 24-digit decimal with M_T(C) < 1.

Per-replica LP.  Variables x_{c,p} >= 0 for every pattern of every capacity (the empty pattern included);
sum_p x_{c,p} = n_c (4 rows) and sum_{c,p} p_w x_{c,p} = 9 I_w (6 rows); cost sum x_{c,p} H_{c-|p|}(a) + 9 L.
Patterns are generated as multisets of roles (each multiset extended only by widths >= its largest member) and
cross-validated against an independent generating-function count.  Search: an own two-phase revised simplex
(Bland's rule, exact Fractions, integer costs round(10^60 * mid of the audit_kappa enclosure of 73^a H_r(a)) at
a_hi = 0.001730096363528623534231; the common factor 73^a does not change the optimal basis).  Certificate, checked
by check() without trusting the search: the patterns are complete and valid; the basic solution is exact, rational,
>= 0 and meets all ten equalities; the dual y is a vector of exact rational combinations of the symbols H_r; the
reduced cost of EVERY column is a rational combination of H_r that is either identically zero or has a rigorous
interval lower bound > 0 at a_hi AND uniformly on the decimal bracket [a_lo, a_hi] (audit_kappa.H encloses
r (73/r)^a = 73^a H_r(a), a common positive factor, increasing in a for r < 73); b.y = c.x symbolically.

Ceiling theorem (finite certificate + this written argument).  Hypotheses: the widths, capacities, per-replica bin
counts n, per-call inventory I, local bill L and nine-call normalization are exactly as above; T is any positive
integer; every one of the 9T I_w width-w roles lies in exactly one bin; every one of the n_c T capacity-c bins carries
one pattern with |p| <= c and is charged exactly H_{c-|p|}; the complete profile is 9T L plus those idle children;
the moment uses live stock 896T and m = 73.  Claim: every such allocation has M_T(a_hi) > 1, so its root is < a_hi
and its 24-digit endpoint is <= a_lo = a_hi - 1e-24.  Proof: x = (bin counts)/T is LP-feasible; weak duality with
reduced costs >= 0 at a_hi gives idle cost(a_hi) >= T b.y(a_hi) = T c.x*(a_hi); hence sum_r n_r H_r(a_hi) >=
T sum_r P_r H_r(a_hi) for the LP-minimum per-replica profile P, i.e. M_T(a_hi) >= M_P(a_hi) (live 896) > 1 by the
enclosure.  All ranks are in [1, 48] < 73, so every term r (73/r)^a increases with a and M_T(a) > 1 for all a >= a_hi;
any 24-digit C with M_T(C) < 1 is < a_hi, i.e. C <= a_lo.  Adding further paid children of rank in [1,72] only
raises M_T, so the bound persists.  Relaxed (dropped): source windows, physical families, chronology, call-copy
decomposition, slot limits and integrality.  NOT covered: any other width vector, inventory, local bill,
capacity/bin-count model, live-stock scaling or call normalization.  The dual is certified at a_hi and uniformly on
[a_lo, a_hi] only; no all-exponent dual claim.  Every LP-optimal solution is supported on the symbolically tight
columns (strictly positive reduced costs elsewhere), so its profile 9L + b.y is unique.

Attainment.  PR3633's T = 488 aggregate (owners/CANDIDATE.json: groups [cap, lo, hi, n_g] per base T = 61, x
[group, pattern, count], z [group, macro-time t, width, count], S = 8) uses only tight patterns, has 488 n_c bins of
each capacity, S n_g bins per group, 4392 I_w roles of each width, z inside lo < t <= hi with width balance, call
inventory and group degree, and its idle profile + 4392 L equals the claimed profile = 488 P.  Its endpoint is
therefore exactly a_lo (accepted at a_lo, rejected at a_hi): no allocation in this fixed model has a larger 24-digit
endpoint.

Cross-checks.  PR3633 ceiling/CEILING.json: model, hashed candidate field list (must be the 11 scientific fields)
and candidate sha256 binding, basis, value, dual feasibility on the own columns at their exponent (a rational with
denominator 2^60 10^6, below a_hi) and at a_hi, b.y, the root polynomial (= lcm-scaled P minus scale * 896 at rank
73, i.e. live 896 per replica) and the root interval bracketing.  PR3633 CLAIM.json: profile, root interval, kappa,
candidate_endpoint, calls and roles.  PR3630: the literal constants of check_budget.py (ast.literal_eval of literal
right-hand sides) equal this model with W = 896 T; its parsed basis is optimal with the same value; its dual,
re-derived by the own symbolic solver, is positive uniformly on its [LO, HI] with its stated (12, 2539) counts, and
its reduced-cost coefficient digest (own reduced costs, PR3630's documented serialisation) equals VALIDATION.json
dual.coefficient_sha256; its README bound C < a_hi.

Rejections raise audit_common.AuditFail('ceiling.<rule>: detail'); the vendored audit_kappa engine can also raise
AuditFail('kappa.<rule>: ...') (e.g. kappa.profile for a nonpositive count, kappa.rank for rank >= 73); a missing
key, wrong shape or unparsable literal raises AuditFail('ceiling.input_format: ...').  Every negative control runs
through check() on a deep copy and counts only on its expected rule id; they include three crafted duals whose
reduced cost is undecidable inside the enclosure at a_hi or changes sign inside (a_lo, a_hi), so the interval-endpoint
choices of lower_at/lower_uniform and the evaluation exponent are exercised.

Independence: own code from the stated mathematics; PR3633/PR3630/PR3605 files are read as data only (PR3630's
check_budget.py is parsed by regular expressions and ast.literal_eval, never executed).  Provenance note: a first
draft of this module mirrored the shape of PR3633's ceiling/verify_ceiling.py pattern walk and column builder and
of owners/verify_candidate.py's z loop; after review those parts were rewritten (multiset-extension enumeration,
sparse columns, tally-based aggregate checks).

Credits: the capacity model and the finite-pattern primal/dual approach descend from the retained coupled-carrier-
cap740 certificate lineage on main (research/coupled-carrier-cap740); Ross Richardson's PR3630 (independent 2,551-
pattern dual and all-T ceiling) and PR3605 (staged 644/660 width 8->7 supplier); hexapode's PR3633 (T488 aggregate,
ceiling certificate).  Standard library only.
"""
import ast
import copy
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

try:
    _HERE = Path(__file__).resolve().parent
    if str(_HERE / 'vendor' / 'pr3053') not in sys.path:
        sys.path.insert(0, str(_HERE / 'vendor' / 'pr3053'))
except NameError:          # loaded by exec: the integration supplies the vendored modules
    _HERE = None

import audit_common as AC
import audit_kappa as AK

need = AC.need
E24 = Q(1, 10 ** 24)
A_LO = Q('0.001730096363528623534230')
A_HI = Q('0.001730096363528623534231')
T488 = 488
MODEL = dict(widths=(4, 5, 6, 7, 8, 9), caps=(8, 16, 32, 48), n=(672, 448, 448, 448), inv=(26, 2, 18, 52, 97, 213),
             local={1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}, calls=9, live=896)
FIELDS3633 = ['baseT', 'S', 'order', 'dispatch', 'groups', 'widths', 'inventory', 'local_profile', 'x', 'z', 'profile']
PR3633 = '72c268f113368ea0387d188225e3f81ba6d6ef73'
PR3630 = 'bcac7fe04b9b7f7f5d3c27d620561f96c4ae5608'
PINS = {  # key: (commit, path, sha256)
    'candidate': (PR3633, 'research/staged-width-t488/owners/CANDIDATE.json',
                  'fbdda845beac5bba9baa4b1b8c8f596e98f70b59e1d60ebf4f4d3e8758631bfd'),
    'expected': (PR3633, 'research/staged-width-t488/owners/EXPECTED.json',
                 '924493b6bbeade055af4916ac7bd6d7d7ec0600719f5c39636dc3f16d7ec14ea'),
    'ceiling3633': (PR3633, 'research/staged-width-t488/ceiling/CEILING.json',
                    'a26bf26118222a5bcb6bf9f698d6b8b86003ff7b1479fd68b31f67c74945e460'),
    'claim': (PR3633, 'research/staged-width-t488/CLAIM.json',
              '3332fb6f6d5ae81da8ead667973491ebefa1803d6d96a06790386ac16243f332'),
    'budget3630': (PR3630, 'research/staged-644-660-owner-successor/check_budget.py',
                   '639820c9ccf72b88ae16768055ec5500a66004784f57a2fa5f218bf4d2e4ee05'),
    'readme3630': (PR3630, 'research/staged-644-660-owner-successor/README.md',
                   '79cf49cd2274364888830d63a664f514c7b1a51d3ac54e57dc4117d432078e31'),
    'validation3630': (PR3630, 'research/staged-644-660-owner-successor/VALIDATION.json',
                       '1d85df49a5e4b9d1262cfaffa9725e03bfe660f395bc6c08d594a0b0551fc24e'),
}


def read_pinned(repo, key):
    commit, path, sha = PINS[key]
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    p = subprocess.run(['git', '--no-replace-objects', '-C', str(repo), 'show', '%s:%s' % (commit, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    need(p.returncode == 0, 'ceiling.input: git show %s:%s failed: %s' % (commit[:12], path, p.stderr.decode()[:200]))
    need(hashlib.sha256(p.stdout).hexdigest() == sha, 'ceiling.input: %s sha256 mismatch' % key)
    return p.stdout


# ---------------------------------------------------------------- patterns, columns, symbols, intervals

def enumerate_patterns(widths, caps):
    """Every (cap, p): p a nonnegative count vector over widths with sum_w w p_w <= cap (empty pattern included).

    Roles are added one at a time in nondecreasing width order, so each multiset of roles is produced once; the
    result is sorted by (cap, counts), the lexicographic order PR3630 serialises its coefficients in."""
    top, layer, multisets = max(caps), [((), 0)], [((), 0)]
    while layer:
        layer = [(ms + (w,), s + w) for ms, s in layer for w in widths if (not ms or w >= ms[-1]) and s + w <= top]
        multisets += layer
    vectors = [(tuple(ms.count(w) for w in widths), s) for ms, s in multisets]
    return sorted((c, v) for c in caps for v, s in vectors if s <= c)


def dp_count(widths, cap):
    """Number of nonnegative vectors with sum w p_w <= cap: prefix sum of the coefficients of prod 1/(1 - x^w)."""
    f = [1] + [0] * cap
    for w in widths:
        for s in range(w, cap + 1):
            f[s] += f[s - w]
    return sum(f)


def used(widths, q):
    return sum(w * k for w, k in zip(widths, q))


def column(model, cap, q):
    """Sparse LP column {row: coefficient}: the capacity row of cap, then one row per width carrying its count."""
    col = {model['caps'].index(cap): 1}
    col.update((len(model['caps']) + i, k) for i, k in enumerate(q) if k)
    return col


def times(model, pats, amounts):
    """A x for the given columns and amounts, as a dense list of the ten row sums."""
    out = [Q(0)] * (len(model['caps']) + len(model['widths']))
    for (c, q), v in zip(pats, amounts):
        for i, a in column(model, c, q).items():
            out[i] += a * v
    return out


def rhs(model):
    return [Q(v) for v in model['n']] + [Q(model['calls'] * v) for v in model['inv']]


def tally(items, key):
    """Sum the counts of (k, n) items grouped by key(k)."""
    out = {}
    for k, n in items:
        out[key(k)] = out.get(key(k), 0) + n
    return out


def sym_add(acc, d, coef=1):
    for r, v in d.items():
        acc[r] = acc.get(r, 0) + coef * v
        if acc[r] == 0:
            del acc[r]
    return acc


def idle_sym(model, cap, q):
    i = cap - used(model['widths'], q)
    return {i: Q(1)} if i else {}


def reduced_cost(model, cap, q, y):
    acc = dict(idle_sym(model, cap, q))
    for i, a in column(model, cap, q).items():
        sym_add(acc, y[i], -a)
    return acc


def b_dot(b, y):
    acc = {}
    for bi, yi in zip(b, y):
        sym_add(acc, yi, bi)
    return acc


_H = {}


def h_iv(r, a):
    """Rigorous enclosure of r (73/r)^a = 73^a H_r(a) from the vendored audit_kappa engine (cached)."""
    if (r, a) not in _H:
        _H[r, a] = AK.H(r, a)
    return _H[r, a]


def lower_at(sym, a):
    """Lower bound of 73^a * sum_r c_r H_r(a)."""
    return sum((c * h_iv(r, a)[0 if c > 0 else 1] for r, c in sym.items()), Q(0))


def lower_uniform(sym, a0, a1):
    """Lower bound of 73^a * sum_r c_r H_r(a) over a0 <= a <= a1 (each r (73/r)^a increases in a since r < 73)."""
    return sum((c * (h_iv(r, a0)[0] if c > 0 else h_iv(r, a1)[1]) for r, c in sym.items()), Q(0))


def inverse(B):
    m = len(B)
    z = [[Q(v) for v in row] + [Q(int(i == j)) for j in range(m)] for i, row in enumerate(B)]
    for j in range(m):
        k = next((k for k in range(j, m) if z[k][j]), None)
        need(k is not None, 'ceiling.basis_singular: basis matrix is singular')
        z[j], z[k] = z[k], z[j]
        p = z[j][j]
        z[j] = [v / p for v in z[j]]
        for i in range(m):
            if i != j and z[i][j]:
                f = z[i][j]
                z[i] = [u - f * v for u, v in zip(z[i], z[j])]
    return [row[m:] for row in z]


def symbolic_dual(model, basis):
    """y with B^T y = c_B, each y_i an exact rational combination {rank: coefficient} of the symbols H_r."""
    m = len(basis)
    cols = [column(model, cap, q) for cap, q in basis]
    Binv = inverse([[col.get(i, 0) for col in cols] for i in range(m)])
    y = []
    for i in range(m):
        acc = {}
        for k, (cap, q) in enumerate(basis):
            if Binv[k][i]:
                sym_add(acc, idle_sym(model, cap, q), Binv[k][i])
        y.append(acc)
    return y


def profile_of(model, basis, x):
    prof = {r: model['calls'] * Q(v) for r, v in model['local'].items()}
    for (cap, q), v in zip(basis, x):
        sym_add(prof, idle_sym(model, cap, q), v)
    return prof


# ---------------------------------------------------------------- search (own simplex; not trusted by check)

def simplex(model, patterns, a):
    m, b = 10, rhs(model)
    cols = [column(model, cap, q) for cap, q in patterns]
    real = len(cols)
    cols += [{i: 1} for i in range(m)]
    costs = []
    for cap, q in patterns:
        i = cap - used(model['widths'], q)
        lo, hi = h_iv(i, a) if i else (0, 0)
        costs.append(round((lo + hi) / 2 * 10 ** 60))
    basis, iters = list(range(real, real + m)), [0, 0]

    def phase(cost, ph):
        while True:
            Binv = inverse([[cols[j].get(i, 0) for j in basis] for i in range(m)])
            xB = [sum(Binv[i][k] * b[k] for k in range(m)) for i in range(m)]
            y = [sum(cost[basis[k]] * Binv[k][i] for k in range(m)) for i in range(m)]
            inb = set(basis)
            enter = next((j for j in range(real) if j not in inb
                          and cost[j] - sum(y[i] * v for i, v in cols[j].items()) < 0), None)
            if enter is None:
                return Binv, xB
            d = [sum(Binv[i][k] * v for k, v in cols[enter].items()) for i in range(m)]
            cand = [(xB[i] / d[i], basis[i], i) for i in range(m) if d[i] > 0]
            need(cand, 'ceiling.search: unbounded LP')
            basis[min(cand)[2]] = enter
            iters[ph] += 1
    Binv, xB = phase([0] * real + [1] * m, 0)
    need(sum(v for v, j in zip(xB, basis) if j >= real) == 0, 'ceiling.search: LP infeasible')
    for r in range(m):        # drive zero-level artificials out (the 10 rows have full rank)
        if basis[r] >= real:
            j = next(j for j in range(real) if j not in basis
                     and sum(Binv[r][k] * v for k, v in cols[j].items()) != 0)
            basis[r] = j
            Binv = inverse([[cols[jj].get(i, 0) for jj in basis] for i in range(m)])
    Binv, xB = phase(costs + [0] * m, 1)
    order = sorted(range(m), key=lambda i: basis[i])
    B = [patterns[basis[i]] for i in order]
    return dict(basis=B, x=[xB[i] for i in order], y=symbolic_dual(model, B), iterations=iters)


# ---------------------------------------------------------------- parsing of PR3630 literals (data only)

def parse_pr3630(src, readme):
    def lit(pattern, what):
        m = re.search(pattern, src, re.M)
        need(m, 'ceiling.x3630_parse: %s literal not found' % what)
        try:
            return ast.literal_eval(m.group(1))
        except (ValueError, SyntaxError) as e:
            need(False, 'ceiling.x3630_parse: %s is not a literal (%s)' % (what, e))
    consts = {k: lit(r'^%s = (.+)$' % k, k) for k in ('CAPS', 'WIDTHS', 'CAP_TOTAL', 'INVENTORY', 'L')}
    consts['M'], consts['T'], consts['W'] = lit(r'^M, T, W = (.+)$', 'M, T, W')
    consts['calls'] = 9 if re.search(r'^rhs = list\(map\(Q, CAP_TOTAL\)\) \+ \[Q\(9 \* n\) for n in INVENTORY\]$',
                                     src, re.M) else None
    m = re.search(r'^specs = \[(.*)\]$', src, re.M)
    need(m, 'ceiling.x3630_parse: specs literal not found')
    specs = [(int(c), tuple(int(v) for v in ws.replace(' ', '').split(',') if v), Q(int(p), int(d or 1)))
             for c, ws, p, d in re.findall(r'\((\d+), \(([\d, ]*)\), Q\((\d+)(?:, (\d+))?\)\)', m.group(1))]
    lo = re.search(r"^LO = Q\('([0-9.]+)'\)$", src, re.M)
    hi = re.search(r'^HI = LO \+ Q\(1, 10 \*\* 24\)$', src, re.M)
    cnt = re.search(r'\(len\(tight\), len\(strict\)\) == \((\d+), (\d+)\)', src)
    bound = re.search(r'C < (0\.\d{24})', readme)
    need(len(specs) == 10 and lo and hi and cnt and bound, 'ceiling.x3630_parse: basis/endpoints/counts/bound')
    return dict(consts=consts, specs=specs, LO=lo.group(1), HI='LO + 1e-24',
                counts=[int(cnt.group(1)), int(cnt.group(2))], bound=bound.group(1))


def digest3630(model, pats, rcs):
    """PR3630's coefficient digest: per pattern in (cap, counts) order, json [[cap, counts, idle], sorted (r, str)]."""
    h = hashlib.sha256()
    for c, q in sorted(pats):
        h.update(json.dumps([[c, list(q), c - used(model['widths'], q)], sorted((r, str(v)) for r, v in
                                                                              rcs[c, q].items())],
                            separators=(',', ':')).encode())
    return h.hexdigest()


def projection_sha(cand, fields):
    return hashlib.sha256(json.dumps({k: cand[k] for k in fields}, sort_keys=True, separators=(',', ':')).encode()
                          ).hexdigest()


# ---------------------------------------------------------------- the main check

def rule_of(e):
    return str(e).split(':', 1)[0]


def check(D):
    """Main check; the positive run and every negative control go through here."""
    try:
        return _check(D)
    except (KeyError, IndexError, TypeError, ValueError, ZeroDivisionError, AttributeError) as e:
        raise AC.AuditFail('ceiling.input_format: malformed input (%s: %s)' % (type(e).__name__, e)) from e


def _check(D):
    model, a_hi, rec = D['model'], D['a_hi'], {}
    W, caps, calls = model['widths'], model['caps'], model['calls']
    b = rhs(model)
    # 1. enumeration: every pattern fits, no duplicates, and the per-capacity count equals the DP count
    pats = D['patterns']
    need(all(c in caps and len(q) == len(W) and all(type(k) is int and k >= 0 for k in q) and used(W, q) <= c
             for c, q in pats), 'ceiling.enum_valid: a listed pattern does not fit its capacity')
    need(len(set(pats)) == len(pats), 'ceiling.enum_distinct: duplicate pattern')
    split = {c: sum(1 for cc, _ in pats if cc == c) for c in caps}
    dp = {c: dp_count(W, c) for c in caps}
    need(split == dp, 'ceiling.enum_complete: per-capacity counts %s != independent counts %s' % (split, dp))
    rec['patterns'] = dict(per_capacity={str(c): split[c] for c in caps}, total=len(pats))
    pset = set(pats)
    # 2. primal: exact basic solution, >= 0, all ten equalities
    cert = D['cert']
    basis, x, y = [(c, tuple(q)) for c, q in cert['basis']], cert['x'], cert['y']
    need(len(basis) == len(x) == 10 and all(p in pset for p in basis), 'ceiling.primal_column: basis not in enumeration')
    need(all(v >= 0 for v in x), 'ceiling.primal_sign: negative basic amount')
    Ax = times(model, basis, x)
    need(Ax == b, 'ceiling.primal_rows: A x = %s != b = %s' % (Ax, b))
    # 3. dual feasibility of every column: symbolic zero, or rigorous positive lower bound at a_hi and on [a_lo, a_hi]
    need(len(y) == 10, 'ceiling.dual_shape: ten dual entries required')
    tight, strict, rcs = [], [], {}
    for c, q in pats:
        rc = reduced_cost(model, c, q, y)
        rcs[c, q] = rc
        if not rc:
            tight.append((c, q))
            continue
        lo = lower_at(rc, a_hi)
        need(lo > 0, 'ceiling.dual_feasible: reduced cost of (%d, %s) = %s has lower bound %.3e at a_hi'
             % (c, q, rc, float(lo)))
        need(lower_uniform(rc, A_LO, A_HI) > 0, 'ceiling.dual_uniform: reduced cost of (%d, %s) not positive on '
             '[a_lo, a_hi]' % (c, q))
        strict.append(lo)
    tset = set(tight)
    # 4. strong duality: b.y == c.x symbolically
    by = b_dot(b, y)
    cx = {}
    for (c, q), v in zip(basis, x):
        sym_add(cx, idle_sym(model, c, q), v)
    need(by == cx, 'ceiling.strong_duality: b.y %s != c.x %s' % (by, cx))
    P = profile_of(model, basis, x)
    rec['lp'] = dict(a_hi=str(a_hi), basis=[dict(capacity=c, pattern=list(q), idle=c - used(W, q), x=str(v))
                                            for (c, q), v in zip(basis, x)],
                     dual=[{str(r): str(v) for r, v in sorted(yi.items())} for yi in y],
                     symbolically_zero=len(tight), strictly_positive=len(strict),
                     min_strict_lower_scaled_by_73a='%.6e' % float(min(strict)),
                     dual_uniform_on_bracket=[str(A_LO), str(A_HI)],
                     tight_patterns=[[c, list(q)] for c, q in tight],
                     minimum_profile_per_replica={str(r): str(v) for r, v in sorted(P.items())},
                     idle_per_replica={str(r): str(v) for r, v in sorted(cx.items())})
    # 5. claimed profile (EXPECTED and CLAIM, T = 488) / 488 == LP minimum
    cand = D['candidate']
    S, G, base = cand['S'], cand['groups'], cand['baseT']
    T = base * S
    need(T == D['expected']['replicas'] == D['claim']['replicas'] == T488, 'ceiling.claimed_profile: T != 488')
    for name in ('expected', 'claim'):
        cp = {int(r): Q(v, T) for r, v in D[name]['profile'].items()}
        need(cp == P, 'ceiling.claimed_profile: %s profile / 488 != LP minimum' % name)
    # 6. attainment by the PR3633 aggregate
    need(all(type(row) is list and len(row) == 4 and all(type(v) is int for v in row) and row[3] > 0 for row in G)
         and all(type(e) is list and len(e) == 3 and type(e[0]) is int and type(e[2]) is int and type(e[1]) is list
                 and len(e[1]) == len(W) and all(type(k) is int for k in e[1]) for e in cand['x'])
         and all(type(e) is list and len(e) == 4 and all(type(v) is int for v in e) for e in cand['z']),
         'ceiling.input_format: candidate groups/x/z must be integer lists [cap,lo,hi,n>0]/[g,[6],n]/[g,t,w,n]')
    need(cand['widths'] == list(W) and {int(k): v for k, v in cand['inventory'].items()} == dict(zip(W, model['inv']))
         and {int(k): v for k, v in cand['local_profile'].items()} == model['local']
         and len(cand['order']) == calls * base and D['expected']['calls'] == calls * T,
         'ceiling.attain_model: candidate widths/inventory/local bill/nine-call normalization')
    bins = {(g, tuple(q)): n for g, q, n in cand['x']}
    need(len(bins) == len(cand['x']) and all(0 <= g < len(G) and n > 0 for (g, q), n in bins.items()),
         'ceiling.attain_format: x has a repeated (group, pattern), a group index out of range or a count <= 0')
    kinds = {(G[g][0], q) for g, q in bins}
    need(kinds <= pset, 'ceiling.attain_pattern: %s not enumerated' % sorted(kinds - pset)[:3])
    loose = sorted(kinds - tset)
    need(not loose, 'ceiling.attain_tight: %d aggregate bin pattern(s) have positive reduced cost, e.g. %s'
         % (len(loose), loose[:3]))
    need(tally(bins.items(), lambda k: k[0]) == {g: S * row[3] for g, row in enumerate(G)},
         'ceiling.attain_bins: bins per group != S n_g')
    per_cap = tally(bins.items(), lambda k: G[k[0]][0])
    need(per_cap == {c: T * nc for c, nc in zip(caps, model['n'])}
         and tally(((row[0], row[3]) for row in G), lambda c: c) == {c: base * nc for c, nc in zip(caps, model['n'])},
         'ceiling.attain_bins: bins per capacity %s != 488 n' % per_cap)
    roles = [sum(n * k[1][i] for k, n in bins.items()) for i in range(len(W))]
    need(roles == [calls * T * v for v in model['inv']], 'ceiling.attain_roles: roles per width %s != 4392 I' % roles)
    flow = {(g, t, w): n for g, t, w, n in cand['z']}
    need(len(flow) == len(cand['z']) and all(0 <= g < len(G) and w in W and n > 0 for (g, t, w), n in flow.items()),
         'ceiling.attain_format: z has a repeated (group, time, width), a bad group/width or a count <= 0')
    outside = sorted(k for k in flow if not G[k[0]][1] < k[1] <= G[k[0]][2])
    need(not outside, 'ceiling.attain_window: %d z entries outside their group window (lo, hi], e.g. %s'
         % (len(outside), outside[:3]))
    supply = tally((((g, w), n * k) for (g, q), n in bins.items() for w, k in zip(W, q) if k), lambda k: k)
    need(tally(flow.items(), lambda k: (k[0], k[2])) == supply,
         'ceiling.attain_zbalance: per (group, width) z total != roles carried by that group\'s bins')
    need(tally(flow.items(), lambda k: (k[1], k[2])) == {(t, w): S * v for t in range(len(cand['order']))
                                                         for w, v in zip(W, model['inv'])},
         'ceiling.attain_zcalls: per (macro-call, width) z total != S I_w')
    over = sorted(k for k, v in tally(flow.items(), lambda k: (k[0], k[1])).items() if v > S * G[k[0]][3])
    need(not over, 'ceiling.attain_zdegree: %d (group, time) loads exceed S n_g, e.g. %s' % (len(over), over[:3]))
    idle = tally(bins.items(), lambda k: G[k[0]][0] - used(W, k[1]))
    idle.pop(0, None)
    full = sym_add({r: calls * T * v for r, v in model['local'].items()}, idle)
    for name, prof in (('candidate', cand['profile']), ('expected', D['expected']['profile']),
                       ('claim', D['claim']['profile'])):
        need({int(r): v for r, v in prof.items()} == full, 'ceiling.attain_profile: idle + 4392 L != %s profile' % name)
    used_kinds = sorted([c, list(q)] for c, q in kinds)
    rec['attainment'] = dict(T=T, S=S, base_T=base, groups=len(G), x_entries=len(bins), z_entries=len(flow),
                             bins_per_capacity={str(c): v for c, v in sorted(per_cap.items())},
                             roles_per_width={str(w): v for w, v in zip(W, roles)},
                             idle_profile={str(r): v for r, v in sorted(idle.items())},
                             full_profile={str(r): v for r, v in sorted(full.items())},
                             tight_patterns_used=len(kinds),
                             nonbasic_tight_used=[k for k in used_kinds if (k[0], tuple(k[1])) not in set(basis)],
                             equals_488_times_LP_minimum=True)
    # 7. root: claimed endpoint C accepted, C + 1e-24 rejected (live 896 T), for the LP minimum and the claimed profile
    live = model['live'] * T
    cl = D['claim']
    C = Q(cl['root_interval'][0])
    need(C > 0 and (C * 10 ** 24).denominator == 1, 'ceiling.endpoint_format: claimed C %s is not a 24-digit decimal' % C)
    mom = lambda p, a: AK.moment(p, a, live=live)
    profiles = {'lp_minimum_x488': {r: v * T for r, v in P.items()},
                'pr3633_claimed': {int(r): v for r, v in D['expected']['profile'].items()}}
    rec['root'] = {}
    for name, prof in profiles.items():
        need(AK.accepts(mom(prof, C)), 'ceiling.root_accept: %s not accepted at claimed endpoint %s' % (name, C))
        need(AK.rejects(mom(prof, C + E24)), 'ceiling.root_reject: %s not rejected at %s' % (name, C + E24))
        rec['root'][name] = AK.endpoint_check(prof, C, mom=mom)
    need(AK.rejects(AK.moment(P, a_hi, live=model['live'])), 'ceiling.root_ceiling: LP minimum not rejected at a_hi')
    need(Q(cl['root_interval'][1]) == C + E24 and C + E24 == a_hi,
         'ceiling.claim_interval: claimed root interval is not [C, C + 1e-24] with C + 1e-24 = a_hi')
    kappa = Q(cl['kappa'])
    need(kappa == C - AK.KAPPA_TERMS[0] - AK.KAPPA_TERMS[1], 'ceiling.kappa: kappa != C - 1e-46 - 1e-70')
    need(Q(cl['candidate_endpoint']) == kappa and cl['calls'] == calls * T and cl['roles'] == calls * T * sum(model['inv']),
         'ceiling.claim_fields: CLAIM candidate_endpoint/calls/roles differ from kappa/4392/4392 sum(I)')
    rec['root'].update(endpoint=AK.dec(C, 24), kappa=cl['kappa'], candidate_endpoint_equals_kappa=True, live=live,
                       lp_minimum_per_replica_rejected_at_a_hi=True,
                       ceiling='for every positive integer T every complete allocation of this fixed model has '
                               'M_T(a_hi) > 1, so its 24-digit endpoint is <= %s; PR3633 attains it' % AK.dec(C, 24))
    # 8a. cross-check PR3633 ceiling/CEILING.json
    cj = D['ceiling3633']
    need(cj['widths'] == list(W) and cj['capacities'] == list(caps)
         and {int(k): v for k, v in cj['inventory'].items()} == dict(zip(W, model['inv']))
         and {int(k): v for k, v in cj['local_profile'].items()} == model['local']
         and [Q(v) for v in cj['rhs_per_replica']] == b, 'ceiling.x3633_model: CEILING.json model differs')
    need(cj['candidate_scientific_fields'] == FIELDS3633,
         'ceiling.x3633_fields: hashed candidate field list %s != the 11 scientific fields' % cj['candidate_scientific_fields'])
    need(projection_sha(cand, FIELDS3633) == cj['candidate_scientific_sha256'],
         'ceiling.x3633_binding: candidate projection sha256')
    cb = [(e['capacity'], tuple(e['counts'])) for e in cj['basis']]
    cx3633 = [Q(e['amount_per_replica']) for e in cj['basis']]
    need(all(p in pset for p in cb) and all(e['idle'] == e['capacity'] - used(W, e['counts']) for e in cj['basis'])
         and times(model, cb, cx3633) == b and all(v >= 0 for v in cx3633),
         'ceiling.x3633_basis: CEILING.json primal basis infeasible')
    need(profile_of(model, cb, cx3633) == P and {int(r): Q(v) for r, v in cj['full_profile_per_replica'].items()} == P,
         'ceiling.x3633_value: CEILING.json optimal value differs from the LP minimum')
    y3633 = [{int(r): Q(v) for r, v in row.items()} for row in cj['dual_by_constraint']]
    need(len(y3633) == 10, 'ceiling.x3633_dual: ten dual entries required')
    e3633 = Q(cj['exponent'])
    xs = {}
    for label, a in (('at_their_exponent', e3633), ('at_a_hi', a_hi)):
        z = s = 0
        for c, q in pats:
            rc = reduced_cost(model, c, q, y3633)
            if not rc:
                z += 1
            else:
                need(lower_at(rc, a) > 0, 'ceiling.x3633_dual: CEILING.json dual infeasible at %s for (%d, %s)'
                     % (label, c, q))
                s += 1
        xs[label] = [z, s]
    need(b_dot(b, y3633) == cx, 'ceiling.x3633_dual_value: CEILING.json dual value b.y differs from the LP minimum')
    scale = math.lcm(*(v.denominator for v in P.values()))
    poly = {int(r): v for r, v in cj['scaled_root_profile'].items()}
    need(poly == {**{r: int(v * scale) for r, v in P.items()}, 73: -scale * model['live']},
         'ceiling.x3633_rootpoly: CEILING.json root polynomial != %d P - %d H73 (live 896 per replica)'
         % (scale, scale * model['live']))
    rl, rh = (Q(v) for v in cj['root_interval'])
    need(e3633 == rh and rl < rh and AK.accepts(AK.moment(P, rl, live=model['live']))
         and AK.rejects(AK.moment(P, rh, live=model['live'])) and A_LO < rh <= a_hi,
         'ceiling.x3633_root: CEILING.json root interval does not bracket the LP-minimum root below a_hi')
    rec['x3633'] = dict(basis_equal=sorted(cb) == sorted(basis), amounts_equal=dict(zip(cb, cx3633)) == dict(zip(basis, x)),
                        dual_equal=y3633 == y, zero_strict=xs, value_equal=True, field_list_pinned=True,
                        root_polynomial_scale=scale, exponent=cj['exponent'],
                        exponent_denominator_is_2p60_10p6=e3633.denominator == 2 ** 60 * 10 ** 6,
                        exponent_minus_a_hi='%.6e' % float(e3633 - a_hi), root_interval=cj['root_interval'],
                        root_lower_minus_a_lo='%.6e' % float(rl - A_LO),
                        note='their dual is certified at a rational exponent e = their root-interval upper end, with '
                             'a_lo < e <= a_hi; by monotonicity rejection at e implies rejection at a_hi; their root '
                             'interval is not the decimal bracket but brackets the same unique root')
    # 8b. cross-check PR3630 (constants and basis parsed from check_budget.py; dual re-derived by the own solver)
    r30 = D['pr3630']
    k30 = r30['consts']
    need(tuple(k30['CAPS']) == caps and tuple(k30['WIDTHS']) == W and tuple(k30['CAP_TOTAL']) == model['n']
         and tuple(k30['INVENTORY']) == model['inv'] and k30['L'] == model['local'] and k30['calls'] == calls
         and k30['M'] == 73 and type(k30['T']) is int and k30['T'] > 0 and k30['W'] == model['live'] * k30['T'],
         'ceiling.x3630_model: PR3630 constants %s differ from this model' % k30)
    b30 = [(c, tuple(ws.count(w) for w in W)) for c, ws, _ in r30['specs']]
    x30 = [v for _, _, v in r30['specs']]
    need(all(p in pset for p in b30) and all(v > 0 for v in x30) and times(model, b30, x30) == b,
         'ceiling.x3630_basis: PR3630 basis infeasible')
    need(profile_of(model, b30, x30) == P, 'ceiling.x3630_value: PR3630 optimal value differs from the LP minimum')
    y30 = symbolic_dual(model, b30)
    lo30 = Q(r30['LO'])
    z = s = 0
    rc30 = {}
    for c, q in pats:
        rc = rc30[c, q] = reduced_cost(model, c, q, y30)
        if not rc:
            z += 1
            continue
        need(lower_at(rc, a_hi) > 0 and lower_uniform(rc, lo30, lo30 + E24) > 0,
             'ceiling.x3630_dual: PR3630 dual not positive for (%d, %s)' % (c, q))
        s += 1
    need([z, s] == r30['counts'], 'ceiling.x3630_dual: zero/strict counts %s != stated %s' % ([z, s], r30['counts']))
    v30 = D['validation3630']['dual']
    dig = digest3630(model, pats, rc30)
    need(dig == v30['coefficient_sha256'] and [v30['patterns'], v30['symbolically_zero'], v30['strict']]
         == [len(pats), z, s], 'ceiling.x3630_digest: own reduced-cost digest %s or counts != VALIDATION.json dual %s'
         % (dig, v30))
    need(lo30 == A_LO and lo30 + E24 == a_hi and Q(r30['bound']) == a_hi,
         'ceiling.x3630_bound: PR3630 stated bracket/bound differ from [a_lo, a_hi]')
    rec['x3630'] = dict(model_equal=True, model_T=k30['T'], model_live=k30['W'],
                        basis_equal=sorted(b30) == sorted(basis), amounts_equal=dict(zip(b30, x30)) == dict(zip(basis, x)),
                        dual_equal_to_own=y30 == y, zero_strict=[z, s], uniform_on_bracket=True, value_equal=True,
                        coefficient_sha256=dig, digest_matches_validation=True,
                        stated_bound=r30['bound'], bound_confirmed=True)
    return rec


# ---------------------------------------------------------------- driver and negative controls

def load(repo):
    raw = {k: read_pinned(repo, k) for k in PINS}
    D = dict(model=MODEL, a_hi=A_HI, patterns=enumerate_patterns(MODEL['widths'], MODEL['caps']),
             candidate=json.loads(raw['candidate']), expected=json.loads(raw['expected']),
             ceiling3633=json.loads(raw['ceiling3633']), claim=json.loads(raw['claim']),
             validation3630=json.loads(raw['validation3630']),
             pr3630=parse_pr3630(raw['budget3630'].decode(), raw['readme3630'].decode()))
    return D, {k: dict(commit=PINS[k][0], path=PINS[k][1], sha256=PINS[k][2]) for k in PINS}


def controls(D, rec):
    """Negative controls: each mutates a deep copy of D and runs it through check(); killed only on its rule id."""
    tight = {(c, tuple(q)) for c, q in rec['lp']['tight_patterns']}
    basis = [(c, tuple(q)) for c, q in D['cert']['basis']]
    W, G0 = D['model']['widths'], D['candidate']['groups']
    inc = lambda v: v + 1
    out = []

    def edit(*path, f):            # replace the value at a nested path by f(value)
        def mut(d):
            o = d
            for k in path[:-1]:
                o = o[k]
            o[path[-1]] = f(o[path[-1]])
        return mut

    def qstr(delta):
        return lambda v: str(Q(v) + delta)

    def dual_row0(g):              # capacity-8 row dual + g (a {rank: coefficient} combination)
        return edit('cert', 'y', 0, f=lambda yi: sym_add(dict(yi), g))

    def h1_over_h3(a, pick3):      # q with q H3 ~ H1 at exponent a (from the cached enclosures)
        (l1, h1), (l3, h3) = h_iv(1, a), h_iv(3, a)
        return (l1 + h1) / 2 / (l3 if pick3 == 'lo' else (l3 + h3) / 2)
    q_hi = h1_over_h3(A_HI, 'lo')                # q lo(H3) = mid(H1) at a_hi: sign undecidable inside the enclosure
    q_mid = h1_over_h3((A_LO + A_HI) / 2, 'mid')  # H1 - q H3 crosses zero inside (a_lo, a_hi), increasing in a

    def dup_tight(d):              # a tight basic column replaced by a duplicate of another column of its capacity
        i = next(i for i, p in enumerate(d['patterns']) if p in tight and p in basis)
        d['patterns'][i] = next(p for p in d['patterns'] if p[0] == d['patterns'][i][0] and p != d['patterns'][i])

    def x_add(c, g, q, n):         # n more bins of pattern q in group g (merging, dropping emptied entries)
        e = next((e for e in c['x'] if e[0] == g and e[1] == q), None)
        if e is None:
            c['x'].append([g, list(q), n])
        else:
            e[2] += n
        c['x'] = [e for e in c['x'] if e[2]]

    def swap_pattern(pick):        # one x entry's pattern replaced by another of its capacity chosen by pick
        def mut(d):
            c = d['candidate']
            have = {(g, tuple(q)) for g, q, n in c['x']}
            for e in c['x']:
                q2 = next((p for cc, p in d['patterns'] if cc == G0[e[0]][0] and p != tuple(e[1]) and pick((cc, p))
                           and (e[0], p) not in have), None)
                if q2 is not None:
                    e[1] = list(q2)
                    return
            need(False, 'ceiling.controls: no pattern swap available')
        return mut

    def x_move(d):                 # one bin moved to another group of the same capacity: per-group counts broken
        c = d['candidate']
        g1, q = c['x'][0][0], c['x'][0][1]
        g2 = next(g for g, row in enumerate(G0) if g != g1 and row[0] == G0[g1][0])
        x_add(c, g1, q, -1)
        x_add(c, g2, q, 1)

    def group_grow(d):             # a capacity-48 group gets n_g + 1 and S more empty bins: per-capacity counts broken
        c = d['candidate']
        g = next(g for g, row in enumerate(G0) if row[0] == 48)
        c['groups'][g][3] += 1
        x_add(c, g, [0] * len(W), c['S'])

    def split(key):                # an entry with count >= 2 split into two entries with the same key
        def mut(d):
            rows = d['candidate'][key]
            e = next(e for e in rows if e[-1] >= 2)
            e[-1] -= 1
            rows.append(copy.deepcopy(e[:-1]) + [1])
        return mut

    def z_time(which):
        def mut(d):
            c = d['candidate']
            e = c['z'][0]
            if which == 'lo':
                e[1] = G0[e[0]][1]
            elif which == 'hi+1':
                e[1] = G0[e[0]][2] + 1
            else:                  # another in-window macro-time: width balance kept, call inventory broken
                have = {(g, t, w) for g, t, w, n in c['z']}
                for e in c['z']:
                    t2 = next((t for t in range(G0[e[0]][1] + 1, G0[e[0]][2] + 1) if (e[0], t, e[2]) not in have),
                              None)
                    if t2 is not None:
                        e[1] = t2
                        return
                need(False, 'ceiling.controls: no free in-window macro-time')
        return mut

    def z_group(d):                # a z entry moved to another group whose window contains t: width balance broken
        c = d['candidate']
        have = {(g, t, w) for g, t, w, n in c['z']}
        for e in c['z']:
            g2 = next((g for g, row in enumerate(G0) if g != e[0] and row[1] < e[1] <= row[2]
                       and (g, e[1], e[2]) not in have), None)
            if g2 is not None:
                e[0] = g2
                return
        need(False, 'ceiling.controls: no other group for a z entry')

    def z_degree(d):               # 1-unit 4-cycle move: balance and call totals kept, a saturated (g, t) overloaded
        c, S = d['candidate'], d['candidate']['S']
        flow = {(g, t, w): n for g, t, w, n in c['z']}
        load_ = tally(flow.items(), lambda k: (k[0], k[1]))
        for g2, t1 in sorted(k for k, v in load_.items() if v == S * G0[k[0]][3]):
            for (g1, t, w) in [k for k in flow if k[1] == t1 and k[0] != g2]:
                t2 = next((k[1] for k in flow if k[0] == g2 and k[2] == w and k[1] != t1
                           and G0[g1][1] < k[1] <= G0[g1][2]), None)
                if t2 is not None:
                    for k, v in (((g1, t1, w), -1), ((g2, t1, w), 1), ((g2, t2, w), -1), ((g1, t2, w), 1)):
                        flow[k] = flow.get(k, 0) + v
                    c['z'] = [[*k, v] for k, v in flow.items() if v]
                    return
        need(False, 'ceiling.controls: no degree move available')

    def c3633_fields(d):           # shorter field list with its projection hash recomputed: only the list pin catches it
        cj = d['ceiling3633']
        cj['candidate_scientific_fields'] = [f for f in FIELDS3633 if f != 'z']
        cj['candidate_scientific_sha256'] = projection_sha(d['candidate'], cj['candidate_scientific_fields'])

    def c3633_row0(delta):
        return edit('ceiling3633', 'dual_by_constraint', 0, f=lambda row: {**row, '1': str(Q(row.get('1', '0')) + delta)})

    def p30_pivot(d):              # PR3630 basis -> adjacent feasible basis: a non-tight column pivoted in, unique ratio
        specs, model = d['pr3630']['specs'], d['model']
        B = [(c, tuple(ws.count(w) for w in W)) for c, ws, _ in specs]
        cols = [column(model, c, q) for c, q in B]
        Binv = inverse([[col.get(i, 0) for col in cols] for i in range(len(B))])
        for c, q in d['patterns']:
            if (c, q) in tight:
                continue
            dj = [sum(Binv[i][k] * v for k, v in column(model, c, q).items()) for i in range(len(B))]
            ratios = sorted((specs[i][2] / dj[i], i) for i in range(len(B)) if dj[i] > 0)
            if ratios and (len(ratios) == 1 or ratios[0][0] < ratios[1][0]):
                th, leave = ratios[0]
                specs[:] = [(s[0], s[1], s[2] - th * dj[i]) for i, s in enumerate(specs) if i != leave] + [
                    (c, tuple(w for w, k in zip(W, q) for _ in range(k)), th)]
                return
        need(False, 'ceiling.controls: no non-degenerate pivot available')

    overfull = lambda cap: [0] * (len(W) - 1) + [cap // W[-1] + 1]
    for name, mut, rule in (
            # enumeration and primal
            ('drop_tight_pattern_column', edit('patterns', f=lambda ps: [p for p in ps if p != next(
                b for b in basis if b in tight)]), 'ceiling.enum_complete'),
            ('pattern_overfull', edit('patterns', 0, f=lambda p: (p[0], tuple(overfull(p[0])))), 'ceiling.enum_valid'),
            ('duplicate_replaces_tight_column', dup_tight, 'ceiling.enum_distinct'),
            ('primal_amount_negated', edit('cert', 'x', 0, f=lambda v: -v), 'ceiling.primal_sign'),
            ('primal_amount_plus_1', edit('cert', 'x', 0, f=inc), 'ceiling.primal_rows'),
            # dual: coarse and sharp perturbations, and three crafted near-zero reduced costs
            ('dual_plus_1e-40_H1', dual_row0({1: Q(1, 10 ** 40)}), 'ceiling.dual_feasible'),
            ('dual_undecidable_within_enclosure', dual_row0({1: Q(1), 3: -q_hi}), 'ceiling.dual_feasible'),
            ('dual_negative_at_a_hi_positive_at_a_lo', dual_row0({1: Q(1), 3: -q_mid}), 'ceiling.dual_feasible'),
            ('dual_positive_at_a_hi_negative_at_a_lo', dual_row0({1: Q(-1), 3: q_mid}), 'ceiling.dual_uniform'),
            ('weak_feasible_dual_minus_1e-3_H1', dual_row0({1: -Q(1, 1000)}), 'ceiling.strong_duality'),
            # claimed profiles
            ('expected_profile_plus_H1', edit('expected', 'profile', '1', f=inc), 'ceiling.claimed_profile'),
            ('claim_profile_plus_H1', edit('claim', 'profile', '1', f=inc), 'ceiling.claimed_profile'),
            # aggregate
            ('x_entry_malformed', edit('candidate', 'x', 0, f=lambda e: e[:2]), 'ceiling.input_format'),
            ('x_count_float', edit('candidate', 'x', 0, 2, f=float), 'ceiling.input_format'),
            ('candidate_inventory_edit', edit('candidate', 'inventory', '4', f=inc), 'ceiling.attain_model'),
            ('x_entry_split_duplicate', split('x'), 'ceiling.attain_format'),
            ('aggregate_overfull_pattern', edit('candidate', 'x', 0, f=lambda e: [e[0], overfull(G0[e[0]][0]), e[2]]),
             'ceiling.attain_pattern'),
            ('aggregate_nontight_pattern', swap_pattern(lambda p: p not in tight), 'ceiling.attain_tight'),
            ('x_count_plus_1', edit('candidate', 'x', 0, 2, f=inc), 'ceiling.attain_bins'),
            ('x_bin_moved_between_groups', x_move, 'ceiling.attain_bins'),
            ('group_plus_1_with_S_empty_bins', group_grow, 'ceiling.attain_bins'),
            ('aggregate_other_tight_pattern', swap_pattern(lambda p: p in tight), 'ceiling.attain_roles'),
            ('z_entry_split_duplicate', split('z'), 'ceiling.attain_format'),
            ('z_at_window_lo', z_time('lo'), 'ceiling.attain_window'),
            ('z_at_window_hi_plus_1', z_time('hi+1'), 'ceiling.attain_window'),
            ('z_moved_to_other_group', z_group, 'ceiling.attain_zbalance'),
            ('z_moved_to_other_call', z_time('move'), 'ceiling.attain_zcalls'),
            ('z_degree_overload', z_degree, 'ceiling.attain_zdegree'),
            ('candidate_profile_plus_H1', edit('candidate', 'profile', '1', f=inc), 'ceiling.attain_profile'),
            # root and claim
            ('claimed_endpoint_not_24_digit', edit('claim', 'root_interval', 0, f=qstr(Q(1, 10 ** 30))),
             'ceiling.endpoint_format'),
            ('claimed_endpoint_plus_1e-24', edit('claim', 'root_interval', 0, f=qstr(E24)), 'ceiling.root_accept'),
            ('claimed_endpoint_minus_1e-24', edit('claim', 'root_interval', 0, f=qstr(-E24)), 'ceiling.root_reject'),
            ('certify_at_a_lo', edit('a_hi', f=lambda v: A_LO), 'ceiling.root_ceiling'),
            ('claim_interval_upper_plus_1e-24', edit('claim', 'root_interval', 1, f=qstr(E24)), 'ceiling.claim_interval'),
            ('kappa_plus_1e-70', edit('claim', 'kappa', f=qstr(Q(1, 10 ** 70))), 'ceiling.kappa'),
            ('candidate_endpoint_changed', edit('claim', 'candidate_endpoint', f=lambda v: '1/1000'),
             'ceiling.claim_fields'),
            # PR3633 CEILING.json
            ('ceiling3633_inventory_edit', edit('ceiling3633', 'inventory', '4', f=inc), 'ceiling.x3633_model'),
            ('ceiling3633_short_field_list', c3633_fields, 'ceiling.x3633_fields'),
            ('candidate_dispatch_edit', edit('candidate', 'dispatch', 0, -1, f=lambda v: -7), 'ceiling.x3633_binding'),
            ('ceiling3633_amount_edit', edit('ceiling3633', 'basis', 2, 'amount_per_replica', f=qstr(1)),
             'ceiling.x3633_basis'),
            ('ceiling3633_full_profile_edit', edit('ceiling3633', 'full_profile_per_replica', '1', f=qstr(1)),
             'ceiling.x3633_value'),
            ('ceiling3633_dual_perturb', c3633_row0(Q(1, 1000)), 'ceiling.x3633_dual'),
            ('ceiling3633_weak_dual', c3633_row0(-Q(1, 1000)), 'ceiling.x3633_dual_value'),
            ('ceiling3633_rootpoly_live', edit('ceiling3633', 'scaled_root_profile', '73', f=inc),
             'ceiling.x3633_rootpoly'),
            ('ceiling3633_root_lower_at_upper', edit('ceiling3633', 'root_interval', f=lambda r: [r[1], r[1]]),
             'ceiling.x3633_root'),
            # PR3630
            ('pr3630_live_plus_1', edit('pr3630', 'consts', 'W', f=inc), 'ceiling.x3630_model'),
            ('pr3630_amount', edit('pr3630', 'specs', 2, f=lambda s: (s[0], s[1], s[2] + 1)), 'ceiling.x3630_basis'),
            ('pr3630_adjacent_suboptimal_basis', p30_pivot, 'ceiling.x3630_value'),
            ('pr3630_bracket_moved_to_0', edit('pr3630', 'LO', f=lambda v: '0'), 'ceiling.x3630_dual'),
            ('pr3630_counts', edit('pr3630', 'counts', f=lambda v: [13, 2538]), 'ceiling.x3630_dual'),
            ('pr3630_digest', edit('validation3630', 'dual', 'coefficient_sha256', f=lambda v: '0' * 64),
             'ceiling.x3630_digest'),
            ('pr3630_bound', edit('pr3630', 'bound', f=lambda v: '0.001730096363528623534232'), 'ceiling.x3630_bound')):
        AC.attempt(name)
        d = copy.deepcopy(D)
        mut(d)
        try:
            check(d)
            got = None
        except AC.AuditFail as e:
            got = rule_of(e)
        out.append(dict(name=name, expected=rule, raised=got, killed=got == rule))
    return out


def run(repo=None):
    t0 = time.time()
    repo = repo or (_HERE.parents[1] if _HERE else Path.cwd())
    D, pins = load(repo)
    t1 = time.time()
    found = simplex(D['model'], D['patterns'], D['a_hi'])
    D['cert'] = dict(basis=found['basis'], x=found['x'], y=found['y'])
    t2 = time.time()
    rec = check(D)
    t3 = time.time()
    ctl = controls(D, rec)
    need(all(c['killed'] for c in ctl), 'ceiling.controls: a negative control survived or raised another rule: %s'
         % [c for c in ctl if not c['killed']])
    rec.update(status='PASS_FIXED_MODEL_LP_CEILING_ATTAINED_BY_PR3633', simplex_iterations=found['iterations'],
               controls=ctl, inputs=pins,
               seconds=dict(load=round(t1 - t0, 2), search=round(t2 - t1, 2), check=round(t3 - t2, 2),
                            controls=round(time.time() - t3, 2), total=round(time.time() - t0, 2)),
               scope='Fixed staged 644/660 supplier (widths, inventory, local bill), capacities/bin counts, nine-call '
                     'normalization and live 896T; windows, families, chronology and integrality relaxed. Dual '
                     'certified at a_hi and uniformly on [a_lo, a_hi] only. No literal-owner, native, outer or '
                     'multiplication-theorem claim.')
    return rec


if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1] if len(sys.argv) > 1 else None), indent=1))
