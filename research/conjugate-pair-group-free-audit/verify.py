#!/usr/bin/env python3
"""Group-free independent check of the PR6038 conjugate-pair four-call floor.

Standard library only.  Imports nothing from PR6038 or #4089.

Model (PR6038 / #4089): paid factor D_N(g) = [g] N + (I - N), g in {x, y},
N a rank-one idempotent of M_r(F_q); target T = diag([xy], [yx], [e], ..., [e]).
A word D_{N_1}(g_1) ... D_{N_k}(g_k) expands as sum_U [g_U] P_U.

Relaxation (the point of this check): instead of fixing a group, each subset
word g_U may be put in any class among {e, xy, yx, other} that is *individually*
consistent with xy != yx.  Joint consistency of several coincidences, and the
requirement that every "other" group element gets coefficient zero separately,
are dropped.  Every actual group G and pair x, y with xy != yx therefore gives
one of the allowed labelings, so infeasibility of the relaxation for a field
and width excludes the word for *every* group at once.

Consistency of a single equation g_U = c is decided by exact rules only:
  * consistent    -> an explicit noncommuting witness pair in S3, S4 or S5;
  * inconsistent  -> after cyclic free reduction of g_U c^-1, either one
                     generator occurs exactly once (so it lies in the cyclic
                     group of the other and the pair commutes), or the relator
                     is a cyclic conjugate of the commutator [x, y]^(+-1).
Any equation decided by neither rule makes the verifier fail.

Two tiers are searched.  "full" uses the table above.  "singleton" keeps only
the facts about single letters (x, y not in {e, xy, yx}) and lets every subset
of size >= 2 join any class; this is exactly the relaxed system of Theorem S
in PROOF.md.
"""

from __future__ import annotations

import argparse
import itertools
import sys
import time

MARKER = "PASS_CONJUGATE_PAIR_GROUP_FREE_AUDIT"

def require(cond, msg):
    """Explicit check that also runs under python -O."""
    if not cond:
        raise SystemExit(f"FAIL {msg}")


# ---------------------------------------------------------------- free words
INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}


def free_reduce(word: str) -> str:
    out: list[str] = []
    for ch in word:
        if out and out[-1] == INV[ch]:
            out.pop()
        else:
            out.append(ch)
    return "".join(out)


def cyclic_reduce(word: str) -> str:
    w = free_reduce(word)
    while len(w) >= 2 and w[0] == INV[w[-1]]:
        w = w[1:-1]
    return w


def inverse(word: str) -> str:
    return "".join(INV[ch] for ch in reversed(word))


def forces_commutation(relator: str) -> bool:
    """Sound sufficient test: some generator occurs exactly once cyclically."""
    w = cyclic_reduce(relator)
    if w == "":
        return False  # trivial relation, no information
    commutators = {c[i:] + c[:i] for c in ("xyXY", "yxYX") for i in range(4)}
    if w in commutators:
        return True  # the relation is xy = yx itself
    for gen in "xy":
        if sum(ch in (gen, INV[gen]) for ch in w) == 1:
            return True
    return False


# ------------------------------------------------------- permutation witnesses
def perm_mul(p, q):
    """Composition (p*q)[i] = p[q[i]].  Any fixed associative convention gives a
    group, and only equalities of word values are tested."""
    return tuple(p[i] for i in q)


def perm_inv(p):
    inv = [0] * len(p)
    for i, pi in enumerate(p):
        inv[pi] = i
    return tuple(inv)


def evaluate(word: str, x, y):
    ident = tuple(range(len(x)))
    table = {"x": x, "y": y, "X": perm_inv(x), "Y": perm_inv(y)}
    acc = ident
    for ch in word:
        acc = perm_mul(acc, table[ch])
    return acc


def witness_pairs():
    for n in (3, 4, 5):
        elems = list(itertools.permutations(range(n)))
        for x in elems:
            for y in elems:
                if perm_mul(x, y) != perm_mul(y, x):
                    yield n, x, y


TARGET_WORDS = {"E": "", "XY": "xy", "YX": "yx"}


def classify_equations(words: list[str]):
    """Return {(word, cls): bool consistent} and evidence counts."""
    pending = {(w, c) for w in words for c in TARGET_WORDS}
    result: dict[tuple[str, str], bool] = {}
    evidence = {"witness": 0, "forced_commutation": 0}
    for (w, c) in list(pending):
        if forces_commutation(w + inverse(TARGET_WORDS[c])):
            result[(w, c)] = False
            evidence["forced_commutation"] += 1
            pending.discard((w, c))
    for _n, x, y in witness_pairs():
        if not pending:
            break
        for (w, c) in list(pending):
            if evaluate(w, x, y) == evaluate(TARGET_WORDS[c], x, y):
                result[(w, c)] = True
                evidence["witness"] += 1
                pending.discard((w, c))
    if pending:
        raise SystemExit(f"FAIL undecided equations: {sorted(pending)}")
    return result, evidence


# ------------------------------------------------------------- field algebra
def mat_mul(a, b, q):
    r = len(a)
    return tuple(
        tuple(sum(a[i][t] * b[t][j] for t in range(r)) % q for j in range(r))
        for i in range(r)
    )


def mat_add(a, b, q):
    return tuple(tuple((u + v) % q for u, v in zip(ra, rb)) for ra, rb in zip(a, b))


def identity(r):
    return tuple(tuple(1 if i == j else 0 for j in range(r)) for i in range(r))


def zero(r):
    return tuple(tuple(0 for _ in range(r)) for _ in range(r))


def unit(r, a):
    return tuple(tuple(1 if i == j == a else 0 for j in range(r)) for i in range(r))


def rank_one_idempotents(r, q):
    out = set()
    vecs = [v for v in itertools.product(range(q), repeat=r) if any(v)]
    for u in vecs:
        for v in vecs:
            if sum(a * b for a, b in zip(u, v)) % q == 1:
                out.add(tuple(tuple(ui * vj % q for vj in v) for ui in u))
    return sorted(out)


def subset_products(ns, q, r):
    """P_U for every U (bitmask over positions 0..k-1), chronological order."""
    ident = identity(r)
    bars = [tuple(tuple((ident[i][j] - n[i][j]) % q for j in range(r)) for i in range(r)) for n in ns]
    k = len(ns)
    level = {0: ident}
    for pos in range(k):
        nxt = {}
        for mask, m in level.items():
            nxt[mask | (1 << pos)] = mat_mul(m, ns[pos], q)
            nxt[mask] = mat_mul(m, bars[pos], q)
        level = nxt
    return level


# ------------------------------------------------------------ the relaxation
def label_word(pattern: str, mask: int) -> str:
    return "".join(ch for i, ch in enumerate(pattern) if mask >> i & 1)


def allowed_labels(pattern: str, consistent):
    k = len(pattern)
    allowed = {}
    for mask in range(1 << k):
        w = label_word(pattern, mask)
        if mask == 0:
            allowed[mask] = {"E"}  # the empty subset has value e
        else:
            allowed[mask] = {c for c in TARGET_WORDS if consistent[(w, c)]}
    return allowed


def sub_masks(items):
    for n in range(len(items) + 1):
        for combo in itertools.combinations(items, n):
            yield combo


def relaxed_feasible(prods, allowed, r, q, everything_allowed=False):
    t_xy = unit(r, 0)
    t_yx = unit(r, 1)
    t_e = identity(r)
    t_e = tuple(tuple((t_e[i][j] - t_xy[i][j] - t_yx[i][j]) % q for j in range(r)) for i in range(r))
    masks = list(prods)
    z = zero(r)

    def candidates(cls, target, forced=()):
        pool = [m for m in masks if m not in forced and (everything_allowed and m != 0 or cls in allowed[m])]
        if cls == "E":
            pool = [m for m in pool if m != 0]
        hits = []
        for combo in sub_masks(pool):
            s = z
            for m in forced:
                s = mat_add(s, prods[m], q)
            for m in combo:
                s = mat_add(s, prods[m], q)
            if s == target:
                hits.append(frozenset(combo) | frozenset(forced))
        return hits

    xy_sets = candidates("XY", t_xy)
    if not xy_sets:
        return None
    yx_sets = candidates("YX", t_yx)
    if not yx_sets:
        return None
    e_sets = candidates("E", t_e, forced=(0,))
    for a in xy_sets:
        for b in yx_sets:
            if a & b:
                continue
            for c in e_sets:
                if not (c & a) and not (c & b):
                    return (a, b, c)
    return None


def run_case(k, r, q, consistent, everything_allowed=False, stop_at_first=True):
    idem = rank_one_idempotents(r, q)
    patterns = ["".join(p) for p in itertools.product("xy", repeat=k)]
    allowed = {p: allowed_labels(p, consistent) for p in patterns}
    found = []
    tuples = 0
    for ns in itertools.product(idem, repeat=k):
        tuples += 1
        prods = subset_products(ns, q, r)
        for p in patterns:
            hit = relaxed_feasible(prods, allowed[p], r, q, everything_allowed)
            if hit is not None:
                found.append((p, ns, hit))
                if stop_at_first:
                    return len(idem), tuples, found
    return len(idem), tuples, found


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="2:2,2:3,2:5,3:2",
                    help="comma list r:q of width:prime for the length<=3 exclusion")
    args = ap.parse_args(argv)
    t0 = time.time()

    # all positive subwords of words of length <= 4 over {x, y}
    words = sorted({label_word("".join(p), m)
                    for k in range(5) for p in itertools.product("xy", repeat=k)
                    for m in range(1, 1 << k)})
    consistent, evidence = classify_equations(words)

    # spot-check the rules against facts that are known independently
    must_be_false = [("x", "E"), ("x", "XY"), ("xx", "XY"), ("yy", "YX"), ("xxx", "XY"),
                     ("xxy", "XY"), ("xyx", "XY"), ("xyx", "YX"), ("xy", "YX")]
    must_be_true = [("xx", "E"), ("xxy", "YX"), ("yyx", "XY"), ("xyy", "YX"), ("yxx", "XY"),
                    ("xxx", "E"), ("xy", "XY")]
    for key in must_be_false:
        require(consistent[key] is False, f"expected inconsistent {key}")
    for key in must_be_true:
        require(consistent[key] is True, f"expected consistent {key}")
    # x^3 can equal neither xy nor yx (y would be x^2); PR6038's (F3) states a weaker form
    require(not consistent[("xxx", "XY")] and not consistent[("xxx", "YX")], "x^3 rule")

    # singleton-only table: keep only the facts that a single label x or y
    # is not e, xy or yx; every subset of size >= 2 may join any class.
    singleton_only = {key: (val if len(key[0]) <= 1 else True) for key, val in consistent.items()}

    summary = []
    for spec in args.cases.split(","):
        r, q = (int(s) for s in spec.split(":"))
        for k in range(0, 4):
            for name, table in (("full", consistent), ("singleton", singleton_only)):
                n_idem, tuples, found = run_case(k, r, q, table)
                if found:
                    raise SystemExit(f"FAIL length {k} {name} relaxed solution at r={r} q={q}: {found[0]}")
            summary.append(f"r{r}q{q}k{k}:{tuples}")

    # positive control 1: the direct four-call word satisfies the relaxation
    r, q = 2, 2
    e00, e11 = unit(r, 0), unit(r, 1)
    pattern = "xyyx"
    prods = subset_products((e00, e00, e11, e11), q, r)
    require(relaxed_feasible(prods, allowed_labels(pattern, consistent), r, q) is not None, "direct word")
    # and the search finds length-4 solutions on its own
    _, _, found4 = run_case(4, 2, 2, consistent)
    require(found4, "length-4 search found nothing")

    # control 2: without the group-theoretic labels (pure linear algebra,
    # every nonempty subset may join any class) some length <= 3 word fits,
    # so the exclusion above really uses the support facts.
    control_k = None
    for k in range(1, 4):
        _, _, f = run_case(k, 2, 2, consistent, everything_allowed=True)
        if f:
            control_k = k
            break
    require(control_k is not None, "unrestricted control found no short solution")

    # control 3: one wrong consistency bit (allow y = xy, which forces x = e)
    # must reopen a length <= 3 word at r=2, q=2.
    bad = dict(consistent)
    bad[("y", "XY")] = True
    reopened = None
    for k in range(1, 4):
        _, _, f = run_case(k, 2, 2, bad)
        if f:
            reopened = (k, f[0][0])
            break
    require(reopened is not None, "mutated consistency table did not reopen")

    n_true = sum(consistent.values())
    print(f"{MARKER} equations={len(consistent)} consistent={n_true} "
          f"witnessed={evidence['witness']} forced={evidence['forced_commutation']} "
          f"cases={' '.join(summary)} length4_found=1 unrestricted_control_k={control_k} "
          f"mutated_reopens={reopened[0]}:{reopened[1]} seconds={time.time() - t0:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
