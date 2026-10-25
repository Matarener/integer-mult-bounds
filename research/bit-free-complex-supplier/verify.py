#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bit-free complex supplier: exact pricing of the selected local word.

Replays every number in README.md from the pinned repository inputs:

  A. control: the kappa01-outer-repair 'relative' adapter compiler (232198 /
     239648 rank mass) is reproduced exactly;
  B. lazy-direction compiler: a child F_r only needs its Walsh directions to be
     coordinates of the stored layout (identity F_r P_M = P_M prod C_{M^-1 e_j},
     checked on the native Clifford tableau);
  C. children alone force ~no layout changes (exact per-register greedy);
  D. ADD gates force >= ceil(conflicts/2) layout changes under ANY schedule;
     a greedy shared-layout schedule gives an upper bound;
  E. skew kernels (no address map at all): minimum-weight residual bases;
  F. pass-model lemmas (LDS of XOR permutations, prefix-reversal basis,
     bit-reordering invariance, controlled block reversal = shear);
  G. savings: moment sum n_r (r/73)^(1-a) = 896/9 per call, base = selected
     local profile + all idle mass in rank-51 children (the optimistic
     relaxation of research/complex-local-word-ceiling), extra children added.

Standard library only.  Prints PASS_BIT_FREE_COMPLEX_SUPPLIER and writes RESULT.json.
"""
import gzip, hashlib, itertools, json, random, subprocess, sys
from bisect import bisect_left
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from math import ceil, log, exp
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/kappa01-outer-repair"))
sys.path.insert(0, str(ROOT / "research/involutive-walsh-lift"))
import adapter_fusion as af  # noqa: E402
import native as nt  # noqa: E402
import sources as walsh_sources  # noqa: E402

N, I = af.N, af.I
NATIVE_GZ = ROOT / "research/involutive-walsh-lift/evidence/WALSH-RETARGET-NATIVE.json.gz"
NATIVE_SHA = "5bfd2c228533e0d20d62b867ef9c1b57c235399478232e1beee875d6838051db"
M73, W_CALL = 73, Q(896, 9)
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def require(ok, what):
    if not ok:
        raise SystemExit("FAIL: " + what)


def par(x):
    return bin(x).count("1") & 1


def wt(x):
    return bin(x).count("1")


# ----------------------------------------------------------------- inputs
def load():
    raw = NATIVE_GZ.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == NATIVE_SHA, "native retarget pin")
    data = json.loads(gzip.decompress(raw))
    recipes = {(c["old"], c["new"], c["rank"]): c for c in data["children"]}
    require(len(recipes) == len(data["children"]) == 2896, "unique recipes")
    word = walsh_sources.load_local(ROOT)["CANONICAL-WORD.json.gz"]
    require(len(word["frames"]) == 1004 and len(word["ports"]) == 112, "canonical word")
    ceil_res = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json").read_text())
    require(ceil_res["model"]["m"] == 73 and ceil_res["model"]["idle_rank_cap"] == 51, "ceiling model")
    return data, recipes, word


def interior(program):
    s = program.index(["phase", "A"]) + 1
    e = program.index(["phase", "exit_adapters"])
    return program[s:e]


def child_of(ev):
    if ev[0] == "climb":
        r, old, new, rank = ev[2:]
        return r, old, new, rank
    if ev[0] == "center":
        r, old, new, rank = ev[1:]
        return r + 704, old, new, rank
    return None


def reg(arg):
    return arg[1] + (704 if arg[0] == "C" else 0)


# --------------------------------------------------- B. lazy directions
def tableau_identity(trials=200):
    rnd = random.Random(1)
    ok = 0
    for _ in range(trials):
        while True:
            Mx = tuple(rnd.randrange(512) for _ in range(9))
            try:
                Mi = af.inv(Mx); break
            except (RuntimeError, StopIteration):
                pass
        r = rnd.randint(1, 8)
        u = [af.mv(Mi, 1 << j) for j in range(r)]
        ok += nt.tableau((("P", Mx),) + nt.fourier(r)) == \
            nt.tableau(tuple(("C", v, 1) for v in u) + (("P", Mx),))
    return ok


def is_aligned(vecs):
    return all(v and v & (v - 1) == 0 for v in vecs) and len(set(vecs)) == len(vecs)


def apply_ops_to_vectors(ops, vecs):
    rows = [0] * N
    for j, u in enumerate(vecs):
        for i in range(N):
            if u >> i & 1:
                rows[i] |= 1 << j
    for op in ops:
        af.apply_op(rows, op)
    return [sum(((rows[i] >> j) & 1) << i for i in range(N)) for j in range(len(vecs))]


def eliminate_square(rowsK):
    r = len(rowsK); rows = list(rowsK); ops = []; used = set()
    for j in range(r):
        p = next((i for i in range(r) if i not in used and rows[i] >> j & 1), None)
        if p is None:
            p = next(i for i in range(r) if rows[i] >> j & 1)
        used.add(p)
        targets = tuple(i for i in range(r) if i != p and rows[i] >> j & 1)
        if targets:
            ops.append(("shear", tuple((t, 1 << p) for t in targets)))
            for t in targets:
                rows[t] ^= rows[p]
    return ops


@lru_cache(maxsize=None)
def align_directions(vecs):
    if is_aligned(vecs):
        return ()
    r = len(vecs)
    U = [sum(((vecs[j] >> i) & 1) << j for j in range(r)) for i in range(N)]
    best = None
    for K in itertools.combinations([i for i in range(N) if U[i]], r):
        work, rank = [U[i] for i in K], 0
        for j in range(r):
            p = next((i for i in range(rank, r) if work[i] >> j & 1), None)
            if p is None:
                continue
            work[rank], work[p] = work[p], work[rank]
            for i in range(r):
                if i != rank and work[i] >> j & 1:
                    work[i] ^= work[rank]
            rank += 1
        if rank < r:
            continue
        for order in ("clear", "square"):
            rows, ops = list(U), []

            def do(op):
                af.apply_op(rows, op); ops.append(op)

            def clear():
                targets = []
                for t in range(N):
                    if t in K or not rows[t]:
                        continue
                    ech = []
                    for k in K:
                        v, c = rows[k], 1 << k
                        for ev, ec, piv in ech:
                            if v >> piv & 1:
                                v ^= ev; c ^= ec
                        if v:
                            ech.append((v, c, (v & -v).bit_length() - 1))
                    val, comb = rows[t], 0
                    for ev, ec, piv in ech:
                        if val >> piv & 1:
                            val ^= ev; comb ^= ec
                    require(val == 0, "row in span")
                    targets.append((t, comb))
                if targets:
                    do(("shear", tuple(targets)))

            def square():
                for op in eliminate_square([rows[k] for k in K]):
                    do(("shear", tuple((K[t], 1 << K[(c & -c).bit_length() - 1]) for t, c in op[1])))
            (clear(), square()) if order == "clear" else (square(), clear())
            ops = af.fuse_ops(tuple(ops))
            require(is_aligned(apply_ops_to_vectors(ops, vecs)), "alignment program")
            key = (af.score(af.profile(ops)), len(ops))
            if best is None or key < best[0]:
                best = (key, ops)
    require(best is not None, "independent directions")
    return best[1]


def as_matrix(ops):
    rows = list(I)
    for op in ops:
        af.apply_op(rows, op)
    return tuple(rows)


def compile_word(program, recipes, policy):
    pending = [(I, 0) for _ in range(712)]
    native, extra, mass_by, nonid = Counter(), Counter(), Counter(), Counter()

    def charge(ph, why, nontrivial):
        extra.update(ph); mass_by[why] += sum(r * n for r, n in ph.items())
        if nontrivial:
            nonid[why] += 1

    def charge_affine(A, why):
        word = af.synthesize(A[0]); ph = af.profile(word)
        if A[1]:
            ph[wt(A[1])] += 2
        charge(ph, why, bool(word) or bool(A[1]))

    for ev in interior(program):
        ch = child_of(ev)
        if ch:
            r, old, new, rank = ch
            rec = recipes[(old, new, rank)]
            left, right = af.perm(rec["left"]), af.perm(rec["right"])
            native[rank] += 1
            Q_ = af.affine_mul(right, pending[r])
            if policy == "relative":
                charge_affine((Q_[0], 0), "child_entrance")
                pending[r] = af.affine_mul(left, (I, Q_[1]))
            else:
                Minv = af.inv(Q_[0])
                dirs = tuple(af.mv(Minv, 1 << j) for j in range(rank))
                ops = align_directions(dirs)
                charge(af.profile(ops), "child_alignment", bool(ops))
                G = as_matrix(ops)
                require(is_aligned([af.mv(G, u) for u in dirs]), "aligned child")
                pending[r] = af.affine_mul(left, af.affine_mul(Q_, (af.inv(G), 0)))
        elif ev[0] == "scalar":
            g = ev[1]; tag, t = g[0], reg(g[1])
            if tag == "scale":
                continue
            if tag == "clear":
                pending[t] = (I, 0); continue
            s = reg(g[2])
            if tag == "copy":
                pending[t] = pending[s]; continue
            if pending[t] == pending[s]:
                continue
            to_t = af.affine_mul(af.affine_inv(pending[t]), pending[s])
            to_s = af.affine_mul(af.affine_inv(pending[s]), pending[t])

            def c(A):
                ph = af.profile(af.synthesize(A[0]))
                if A[1]:
                    ph[wt(A[1])] += 2
                return af.score(ph)
            if (c(to_t), repr(to_t)) <= (c(to_s), repr(to_s)):
                charge_affine(to_t, "add_alignment"); pending[s] = pending[t]
            else:
                charge_affine(to_s, "add_alignment"); pending[t] = pending[s]
    for A in pending:
        if A != (I, 0):
            charge_affine(A, "returned_layout")
    require(native == Counter(LOCAL), "native inventory")
    return dict(adapter_mass=sum(r * n for r, n in extra.items()),
                total_mass=sum(r * n for r, n in (native + extra).items()),
                mass_by_reason=dict(sorted(mass_by.items())),
                nonidentity_maps=sum(nonid.values()),
                adapter_profile={str(k): v for k, v in sorted(extra.items())})


# ---------------------------------------------- C/D. layout-change bounds
class Seg:
    def __init__(self, fixed=False):
        self.fixed, self.vecs, self.ech, self.members = fixed, set(), {}, set()

    def fits(self, vs):
        ech, new = dict(self.ech), set(self.vecs)
        for v in vs:
            if v in new:
                continue
            if self.fixed and v & (v - 1):
                return None
            x = v
            for p in sorted(ech, reverse=True):
                if x >> p & 1:
                    x ^= ech[p]
            if x == 0:
                return None
            ech[x.bit_length() - 1] = x; new.add(v)
        return ech, new

    def add(self, vs):
        res = self.fits(vs)
        if res is None:
            return False
        self.ech, self.vecs = res
        return True


def child_needs(rec, rank):
    L, R = af.perm(rec["left"])[0], af.perm(rec["right"])[0]
    Rinv = af.inv(R)
    return [af.mv(Rinv, 1 << j) for j in range(rank)], af.mm(L, R)


def child_only_changes(program, recipes):
    segs, phi, changes = [Seg() for _ in range(712)], [I] * 712, 0
    for ev in interior(program):
        ch = child_of(ev)
        if ch:
            r, old, new, rank = ch
            need, LR = child_needs(recipes[(old, new, rank)], rank)
            if not segs[r].add([af.mv(phi[r], w) for w in need]):
                changes += 1; segs[r], phi[r] = Seg(), I
                require(segs[r].add(need), "fresh")
            phi[r] = af.mm(phi[r], af.inv(LR))
        elif ev[0] == "scalar":
            g = ev[1]
            if g[0] == "clear":
                segs[reg(g[1])], phi[reg(g[1])] = Seg(), I
            elif g[0] == "copy":
                s = segs[reg(g[2])]; c = Seg(); c.vecs, c.ech = set(s.vecs), dict(s.ech)
                segs[reg(g[1])], phi[reg(g[1])] = c, phi[reg(g[2])]
    return changes


def independent(vs):
    ech = {}
    for v in set(vs):
        x = v
        for p in sorted(ech, reverse=True):
            if x >> p & 1:
                x ^= ech[p]
        if x == 0:
            return False
        ech[x.bit_length() - 1] = x
    return True


def gate_conflicts(program, recipes):
    ev = interior(program)
    tl, gates = {r: [] for r in range(712)}, []
    for i, e in enumerate(ev):
        ch = child_of(e)
        if ch:
            r, old, new, rank = ch
            need, LR = child_needs(recipes[(old, new, rank)], rank)
            tl[r].append(("child", i, need, LR))
        elif e[0] == "scalar":
            g = e[1]
            if g[0] == "scale":
                continue
            t = reg(g[1])
            if g[0] == "clear":
                tl[t].append(("cut", i)); continue
            s = reg(g[2]); tl[t].append(("gate", i)); tl[s].append(("gate", i))
            if g[0] == "add":
                gates.append((i, t, s))
    pos = {r: {it[1]: j for j, it in enumerate(tl[r]) if it[0] != "child"} for r in tl}

    def window(r, i):
        j, out, Mx = pos[r][i], [], I
        for it in reversed(tl[r][:j]):
            if it[0] != "child":
                break
            Mx = af.mm(Mx, it[3]); out += [af.mv(Mx, w) for w in it[2]]
        Mi = I
        for it in tl[r][j + 1:]:
            if it[0] != "child":
                break
            out += [af.mv(Mi, w) for w in it[2]]; Mi = af.mm(Mi, af.inv(it[3]))
        return out
    conflicts = sum(1 for i, t, s in gates if not independent(window(t, i) + window(s, i)))
    return len(gates), conflicts


def greedy_schedule(program, recipes):
    comp, phi = {}, {}
    for r in range(712):
        c = Seg(); c.members.add(r); comp[r] = c; phi[r] = I
    changes = 0

    def leave(r, c, p):
        comp[r].members.discard(r); comp[r] = c; c.members.add(r); phi[r] = p
    for ev in interior(program):
        ch = child_of(ev)
        if ch:
            r, old, new, rank = ch
            need, LR = child_needs(recipes[(old, new, rank)], rank)
            if not comp[r].add([af.mv(phi[r], w) for w in need]):
                changes += 1; c = Seg(); leave(r, c, I); require(c.add(need), "fresh")
            phi[r] = af.mm(phi[r], af.inv(LR))
        elif ev[0] == "scalar":
            g = ev[1]; t = reg(g[1])
            if g[0] == "scale":
                continue
            if g[0] == "clear":
                leave(t, Seg(), I); continue
            s = reg(g[2])
            if g[0] == "copy":
                leave(t, comp[s], phi[s]); continue
            ct, cs = comp[t], comp[s]
            if ct is cs:
                if phi[t] != phi[s]:
                    changes += 1; phi[s] = phi[t]
                continue
            psi = af.mm(phi[t], af.inv(phi[s]))
            if ct.add([af.mv(psi, v) for v in cs.vecs]):
                for r in list(cs.members):
                    comp[r] = ct; ct.members.add(r); phi[r] = af.mm(psi, phi[r])
                cs.members.clear()
            else:
                changes += 1; leave(s, ct, phi[t])
    return changes


# ------------------------------------------------------- E. skew kernels
def span(basis):
    out = {0}
    for b in basis:
        out |= {x ^ b for x in out}
    return out


def basis_of(S):
    basis = []
    for x in sorted(S):
        if x and x not in span(basis):
            basis.append(x)
    return basis


@lru_cache(maxsize=None)
def skew_basis(a, b, rank):
    S, B = span(a), span(b)
    if not S <= B:
        S, B = B, S
    sb = basis_of(S)
    res = sorted(x for x in B if x and all(not par(x & s) for s in sb))
    if len(res) + 1 == 2 ** rank:
        cand = sorted((v for v in res if par(v)), key=lambda v: (wt(v), v))
        best = [None, 10 ** 9]

        def bt(chosen, pool, total):
            need = rank - len(chosen)
            if need == 0:
                if total < best[1]:
                    best[:] = [tuple(chosen), total]
                return
            if len(pool) < need or total + sum(wt(cand[i]) for i in pool[:need]) >= best[1]:
                return
            for k, i in enumerate(pool):
                if total + wt(cand[i]) * need >= best[1]:
                    break
                v = cand[i]
                bt(chosen + [v], [j for j in pool[k + 1:] if not par(cand[j] & v)], total + wt(v))
        bt([], list(range(len(cand))), 0)
        if best[0] is not None:
            return best[0], "onb"
        pool, kind, cur = res, "non-onb", {0}
    else:
        pool, kind, cur = sorted(B - S), "degenerate", set(S)
    basis = []
    for v in sorted(pool, key=lambda v: (wt(v), v)):
        if v not in cur:
            basis.append(v); cur |= {x ^ v for x in cur}
        if len(basis) == rank:
            break
    return tuple(basis), kind


def skew_children(program, word):
    F = [tuple(v) for v in word["frames"]]
    out, kinds = [], Counter()
    for ev in interior(program):
        ch = child_of(ev)
        if ch:
            _, old, new, rank = ch
            b, kind = skew_basis(F[old], F[new], rank)
            require(len(b) == rank, "skew basis")
            kinds[kind] += 1
            out.append((rank, b))
    return out, kinds


# ------------------------------------------------- F. pass-model lemmas
def lds(p):
    tails = []
    for x in p:
        i = bisect_left(tails, -x)
        if i == len(tails):
            tails.append(-x)
        else:
            tails[i] = -x
    return len(tails)


def pass_lemmas():
    rnd = random.Random(3)
    n = 8
    xor_lds = all(lds([i ^ c for i in range(1 << n)]) == 1 << wt(c) for c in range(1 << n))
    sub = True
    for _ in range(3000):
        m = rnd.randint(2, 40)
        p, q = rnd.sample(range(m), m), rnd.sample(range(m), m)
        sub &= lds([p[q[i]] for i in range(m)]) <= lds(p) * lds(q)
    n = 10
    masks = [(1 << (t + 1)) - 1 for t in range(n)]
    minimum = {}
    for k in range(n + 1):
        for comb in itertools.combinations(masks, k):
            x = 0
            for mk in comb:
                x ^= mk
            minimum.setdefault(x, k)
    bnd = lambda c: sum(1 for t in range(n) if (c >> t & 1) != (c >> (t + 1) & 1))
    prefix = all(minimum[c] == bnd(c) for c in range(1 << n))
    n = 8
    reorder = True
    for _ in range(300):
        c = rnd.randrange(1, 1 << n); pi = rnd.sample(range(n), n)
        cp = sum(((c >> i) & 1) << pi[i] for i in range(n))
        reorder &= lds([i ^ cp for i in range(1 << n)]) == 1 << wt(c)
    kron = all(wt(sum(1 << (i * 9 + j) for i in range(9) if v >> i & 1 for j in range(9) if w >> j & 1))
               == wt(v) * wt(w) for v in range(1, 512, 7) for w in range(1, 512, 11))
    rev = True
    for t in range(n - 1):
        for ctrl in range(t + 1, n):
            size, data, res = 1 << (t + 1), list(range(1 << n)), []
            for start in range(0, len(data), size):
                block = data[start:start + size]
                res += block[::-1] if (start >> ctrl) & 1 else block
            rev &= res == [i ^ ((size - 1) if (i >> ctrl) & 1 else 0) for i in range(1 << n)]
    return dict(xor_lds_is_2_pow_weight=xor_lds, lds_submultiplicative=sub,
                min_prefix_reversals_equal_run_boundaries=prefix,
                bit_reordering_keeps_lds=reorder, kronecker_weight_multiplies=kron,
                controlled_block_reversal_is_shear=rev)


# --------------------------------------------------------- G. savings
def moment(h, a):
    return sum(float(n) * (r / M73) ** (1 - a) for r, n in h.items()) / float(W_CALL)


def base_histogram():
    # coverage law of research/complex-local-word-ceiling: paid mass 72 W + 64 N,
    # 1646 idle units per call, relaxed into rank-51 children (optimistic).
    idle = 72 * W_CALL + 64 - sum(r * n for r, n in LOCAL.items())
    require(idle == 1646, "idle mass per call")
    h = dict(LOCAL); h[51] = idle / 51
    return h


def solve(h):
    lo, hi = -5.0, 0.5
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if moment(h, mid) > 1 else (mid, hi)
    return lo


def with_extra(base, extra):
    h = dict(base)
    for r, n in extra.items():
        h[int(r)] = h.get(int(r), 0) + n
    return h


def main():
    data, recipes, word = load()
    out = dict(status="EXACT SCOPED PRICING; NO NEW KAPPA; NEGATIVE RESULT FOR A BIT-FREE COMPLEX SUPPLIER")
    out["tableau_identity_F_P_equals_P_prod_C"] = tableau_identity()
    require(out["tableau_identity_F_P_equals_P_prod_C"] == 200, "tableau identity")
    base = base_histogram()
    a0 = solve(base)
    out["base_saving_relaxation"] = a0
    require(abs(a0 - 0.0016900541) < 2e-8, "base reproduces the packing ceiling")
    out["rank1_children_allowed_for_a_ge_0"] = (1 - moment(base, 0)) * float(W_CALL) * M73
    per = {}
    for o in ("backward", "forward"):
        prog = data["programs"][o]
        rel = compile_word(prog, recipes, "relative")
        lazy = compile_word(prog, recipes, "direction")
        require(rel["total_mass"] == {"backward": 232198, "forward": 239648}[o], "control reproduction")
        child_only = child_only_changes(prog, recipes)
        gates, conflicts = gate_conflicts(prog, recipes)
        greedy = greedy_schedule(prog, recipes)
        per[o] = dict(relative_control=rel, lazy_directions=lazy,
                      saving_relative=solve(with_extra(base, rel["adapter_profile"])),
                      saving_lazy=solve(with_extra(base, lazy["adapter_profile"])),
                      child_only_forced_changes=child_only, add_gates=gates,
                      conflicting_gates=conflicts, changes_lower_bound=-(-conflicts // 2),
                      greedy_schedule_changes=greedy,
                      saving_at_lower_bound=solve(with_extra(base, {1: 2 * (-(-conflicts // 2))})))
    out["orientations"] = per
    kids, kinds = skew_children(data["programs"]["forward"], word)
    hist = Counter(wt(v) for _, b in kids for v in b)
    out["skew_kernel"] = dict(basis_kinds=dict(kinds), direction_weight_histogram=dict(sorted(hist.items())),
                              mean_direction_weight=sum(k * n for k, n in hist.items()) / sum(hist.values()))

    def skew_saving(cost):
        extra = Counter()
        for rank, b in kids:
            extra[rank] += sum(cost(v) for v in b) / rank - 1
        return solve(with_extra(base, extra))
    out["skew_kernel"]["saving_per_bit_flips"] = skew_saving(wt)
    out["skew_kernel"]["saving_multiway_j3"] = skew_saving(lambda v: 1 + ceil((wt(v) - 1) / 3))
    out["skew_kernel"]["saving_multiway_j8_one_level"] = skew_saving(lambda v: 1 + ceil((wt(v) - 1) / 8))
    out["pass_model_lemmas"] = pass_lemmas()
    require(all(out["pass_model_lemmas"].values()), "pass-model lemmas")
    for o in per:
        require(per[o]["lazy_directions"]["total_mass"] < per[o]["relative_control"]["total_mass"] / 1.8,
                "lazy compiler halves the mass")
        require(per[o]["changes_lower_bound"] * 2 > out["rank1_children_allowed_for_a_ge_0"],
                "forced changes exceed the whole budget")
        require(per[o]["saving_lazy"] < 0 and per[o]["saving_at_lower_bound"] < 0, "negative savings")
    require(out["skew_kernel"]["saving_multiway_j8_one_level"] < 0, "skew kernels negative")
    (HERE / "RESULT.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({o: {k: per[o][k] for k in ("saving_relative", "saving_lazy", "child_only_forced_changes",
                                                   "changes_lower_bound", "greedy_schedule_changes",
                                                   "saving_at_lower_bound")} for o in per}, indent=1))
    print(json.dumps(out["skew_kernel"], indent=1))
    print("PASS_BIT_FREE_COMPLEX_SUPPLIER")


if __name__ == "__main__":
    main()
