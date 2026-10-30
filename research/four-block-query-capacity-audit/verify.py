"""Independent finite audit of PR6122's four-query capacity theorem over F2.

Josie Elliston, prepared with Claude Code (Opus 5.5). Apache-2.0.

Standard library only; imports nothing from PR6122 or the repository; writes no
files. Three parts:

1. Exhaustion.  For n = 2..6 and every cap profile c1 >= c2 >= c3 >= c4 with
   0 <= c_j <= n // 2, decide whether I_n = R1 + R2 + R3 + R4 with every R_j a
   square-zero binary matrix of rank <= c_j.  The decision uses conjugation
   invariance (R1 in normal form), a rank filter, and the complete similarity
   invariant rank p(Y)^k, not PR6122's Gram-complement argument.  The answer is
   compared with the rule  n even and sum_j min(c_j, n/2) >= 3n/2.
2. Construction.  For every even n <= 24 and every profile meeting the rule,
   build the omission schedule and replay the literal word
   (I + Q N_1)(I + Q N_2)(I + Q N_3)(I + Q N_4) S in F2[Q]/(Q^2 - 1).
3. Controls.  The decider must reject planted false witnesses, an odd trace
   target and a wrong target; the constructor must refuse profiles that break
   the rule; mutated words must fail the replay.
"""

import itertools
import json
from pathlib import Path
import sys


# ---------- binary matrices as tuples of row bitmasks (bit j = column j) ----------

def eye(n):
    return tuple(1 << i for i in range(n))


def zero(n):
    return (0,) * n


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def mul(a, b):
    out = []
    for row in a:
        v = 0
        j = 0
        while row:
            if row & 1:
                v ^= b[j]
            row >>= 1
            j += 1
        out.append(v)
    return tuple(out)


def rank(rows):
    rows = [r for r in rows if r]
    rk = 0
    while rows:
        p = rows.pop()
        rk += 1
        low = p & -p
        rows = [r ^ p if r & low else r for r in rows]
        rows = [r for r in rows if r]
    return rk


def need(cond, msg):
    if not cond:
        raise SystemExit("FAIL: " + msg)


# ---------- enumeration of square-zero matrices ----------

def subspaces(vectors, t):
    seen = {}
    for combo in itertools.combinations(vectors, t):
        span = {0}
        for v in combo:
            span |= {x ^ v for x in span}
        if len(span) == 1 << t:
            seen.setdefault(frozenset(span), combo)
    return list(seen.values())


def gl(t):
    return [rows for rows in itertools.product(range(1, 1 << t), repeat=t) if rank(rows) == t]


def square_zero(n, t):
    """Every square-zero n x n binary matrix of rank exactly t, each once:
    column space W (basis B), row space Z inside the annihilator of W (basis C),
    R = B M C with M invertible."""
    if t == 0:
        return [zero(n)]
    vecs = list(range(1, 1 << n))
    out = []
    G = gl(t)
    for B in subspaces(vecs, t):
        ann = [v for v in vecs if all(bin(v & w).count("1") % 2 == 0 for w in B)]
        for C in subspaces(ann, t):
            for M in G:
                MC = [0] * t
                for s in range(t):
                    for u in range(t):
                        if M[s] >> u & 1:
                            MC[s] ^= C[u]
                rows = []
                for i in range(n):
                    v = 0
                    for s in range(t):
                        if B[s] >> i & 1:
                            v ^= MC[s]
                    rows.append(v)
                out.append(tuple(rows))
    return out


# ---------- complete similarity invariant over F2 ----------

def irreducibles(maxdeg):
    def pmod(a, b):
        db = b.bit_length() - 1
        while a and a.bit_length() - 1 >= db:
            a ^= b << (a.bit_length() - 1 - db)
        return a
    irr = []
    for p in range(2, 1 << (maxdeg + 1)):
        d = p.bit_length() - 1
        if all(pmod(p, q) for q in irr if 2 * (q.bit_length() - 1) <= d):
            irr.append(p)
    return irr


def poly_eval(p, Y):
    n = len(Y)
    acc = zero(n)
    for i in range(p.bit_length() - 1, -1, -1):
        acc = mul(acc, Y)
        if p >> i & 1:
            acc = add(acc, eye(n))
    return acc


def sim_key(Y, irr):
    """(p, rank p(Y), rank p(Y)^2, ...) for each irreducible p with p(Y) singular.
    These ranks determine every elementary divisor, so equal keys <=> similar."""
    n = len(Y)
    key = []
    for p in irr:
        d = p.bit_length() - 1
        P = poly_eval(p, Y)
        rk = rank(P)
        if rk == n:
            continue
        ranks = [rk]
        Pk = P
        for _ in range(n // d - 1):
            Pk = mul(Pk, P)
            ranks.append(rank(Pk))
        key.append((p, tuple(ranks)))
    return tuple(key)


def normal_form(n, t):
    return tuple((1 << (i + 1)) if i % 2 == 0 and i // 2 < t else 0 for i in range(n))


def decide(n, caps, sz, irr, target=None):
    """Exact decision of target = R1+R2+R3+R4 (default I_n) with caps c1..c4.
    Returns (witness or None, number of similarity classes tested)."""
    c1, c2, c3, c4 = caps
    T = eye(n) if target is None else target
    by_rank_desc = lambda c: [R for t in range(c, -1, -1) for R in sz[t]]
    R2s, R3s = by_rank_desc(c2), by_rank_desc(c3)
    classes = set()
    if T == eye(n):
        # conjugation fixes I_n, so R1 may be taken in normal form
        firsts = [normal_form(n, t) for t in range(c1, -1, -1)]
        need(all(mul(R, R) == zero(n) and rank(R) == t
                 for R, t in zip(firsts, range(c1, -1, -1))), "normal form")
    else:
        # a non-scalar target is not conjugation invariant: enumerate every R1
        firsts = by_rank_desc(c1)
    for R1 in firsts:
        for R2 in R2s:
            Y = add(add(T, R1), R2)
            if rank(Y) > c3 + c4:          # Y = R3 + R4 forces rank Y <= c3 + c4
                continue
            k = sim_key(Y, irr)
            if k in classes:               # membership in {R3+R4} is a class function
                continue
            classes.add(k)
            for R3 in R3s:
                Z = add(Y, R3)
                if rank(Z) <= c4 and mul(Z, Z) == zero(n):
                    return (R1, R2, R3, Z), len(classes)
    return None, len(classes)


def check_witness(w, caps, target):
    n = len(target)
    ok = all(mul(R, R) == zero(n) and rank(R) <= c for R, c in zip(w, caps, strict=True))
    total = zero(n)
    for R in w:
        total = add(total, R)
    return ok and total == target


def rule(n, caps):
    p = n // 2
    return n % 2 == 0 and sum(min(c, p) for c in caps) >= 3 * p


# ---------- omission-schedule construction and literal word replay ----------

def construct(n, caps):
    """Return paid layers N_1..N_4 and final constant S, or None if the rule fails.
    Pair k omits one position; position j is omitted by o_j >= p - c_j pairs."""
    if not rule(n, caps):
        return None
    p = n // 2
    omit = [max(0, p - min(c, p)) for c in caps]
    spare = p - sum(omit)
    for j in range(4):                      # top up to exactly p omissions
        extra = min(spare, p - omit[j])
        omit[j] += extra
        spare -= extra
    need(spare == 0 and sum(omit) == p, "omission counts")
    order = [j for j in range(4) for _ in range(omit[j])]
    layers = [[0] * n for _ in range(4)]
    for k, skipped in enumerate(order):
        a, b = 2 * k, 2 * k + 1
        active = [j for j in range(4) if j != skipped]
        layers[active[0]][a] |= 1 << b      # E_ab
        layers[active[1]][b] |= 1 << a      # E_ba
        layers[active[2]][a] |= 1 << b      # E_ab
    swap = tuple(1 << (i ^ 1) for i in range(n))
    return [tuple(x) for x in layers], swap


def replay(layers, final, caps):
    """Literal product in F2[Q]/(Q^2-1): an element is (E, O) meaning E + Q O."""
    n = len(final)
    E, O = eye(n), zero(n)
    for N, c in zip(layers, caps, strict=True):
        if mul(N, N) != zero(n) or rank(N) > c:
            return False
        # (E + Q O)(I + Q N) = (E + O N) + Q (O + E N), using Q^2 = 1
        E, O = add(E, mul(O, N)), add(O, mul(E, N))
    E, O = mul(E, final), mul(O, final)
    return E == zero(n) and O == eye(n)


# ---------- k calls: simplex blocks and wrap-around packing ----------

def m_k(k):
    """Largest even block dimension usable with k calls (a 2q-block needs 2q+1 calls)."""
    return 2 * ((k - 1) // 2)


def k_rule(n, k, r):
    """Claimed exact k-call capacity: n even, n >= 2 and n + ceil(n / m_k) <= k r."""
    m = m_k(k)
    return m > 0 and n >= 2 and n % 2 == 0 and n + -(-n // m) <= k * r


def simplex(d):
    """I_d = sum of d+1 rank-one square-zero binary matrices (d even):
    R_i = e_i (1 - e_i)^T for i < d, and R_d = J (all ones)."""
    full = (1 << d) - 1
    blocks = [tuple((full ^ (1 << i)) if row == i else 0 for row in range(d)) for i in range(d)]
    blocks.append(tuple(full for _ in range(d)))
    return blocks


def construct_k(n, k, r):
    """Paid matrices N_1..N_k (square-zero, rank <= r) with sum I_n, or None.
    Blocks of dimension m_k (and one smaller even block) are laid out on
    consecutive call positions, wrapping around (McNaughton)."""
    if not k_rule(n, k, r):
        return None
    m = m_k(k)
    dims = [m] * (n // m) + ([n % m] if n % m else [])
    layers = [[0] * n for _ in range(k)]
    slot = offset = 0
    for d in dims:
        for R in simplex(d):
            pos = slot % k
            for i, row in enumerate(R):
                layers[pos][offset + i] |= row << offset
            slot += 1
        offset += d
    out = [tuple(x) for x in layers]
    return out if all(rank(N) <= r for N in out) else "cap"


def replay_k(layers, r):
    """Literal word prod_j (I + N_j)(I + Q N_j) in F2[Q]/(Q^2-1); (I + N_j) is the free constant."""
    n = len(layers[0])
    E, O = eye(n), zero(n)
    for N in layers:
        if mul(N, N) != zero(n) or rank(N) > r:
            return False
        C = add(eye(n), N)
        E, O = mul(E, C), mul(O, C)
        E, O = add(E, mul(O, N)), add(O, mul(E, N))
    return E == zero(n) and O == eye(n)


# ---------- main ----------

def main(compare=True):
    need(sys.version_info >= (3, 10), "Python 3.10 or newer required")
    result = {"exhaustion": {}, "construction": {}, "k_calls": {}, "controls": {}}

    # 1. exhaustion
    store = {}
    for n in range(2, 7):
        sz = [square_zero(n, t) for t in range(n // 2 + 1)]
        irr = irreducibles(n)
        store[n] = (sz, irr)
        rows = []
        for caps in itertools.combinations_with_replacement(range(n // 2, -1, -1), 4):
            w, ncls = decide(n, caps, sz, irr)
            if w is not None:
                need(check_witness(w, caps, eye(n)), f"witness n={n} {caps}")
            need((w is not None) == rule(n, caps), f"exhaustion disagrees with rule at n={n} {caps}")
            rows.append([list(caps), w is not None, ncls])
        result["exhaustion"][str(n)] = {
            "square_zero_counts_by_rank": [len(x) for x in sz],
            "profiles": len(rows),
            "feasible": sum(1 for r in rows if r[1]),
            "uniform_cap_feasible": {str(r[0][0]): r[1] for r in rows if len(set(r[0])) == 1},
            "classes_tested_uniform_cap": {str(r[0][0]): r[2] for r in rows if len(set(r[0])) == 1},
        }
    six = result["exhaustion"]["6"]
    need(six["uniform_cap_feasible"]["2"] is False and six["uniform_cap_feasible"]["3"] is True,
         "headline n=6 cap-2 exclusion")

    # 2. construction (every even n <= 24, every sorted profile with c_j <= n/2 + 1)
    built = refused = 0
    for n in range(2, 25, 2):
        top = n // 2 + 1
        for caps in itertools.combinations_with_replacement(range(top, -1, -1), 4):
            for perm in sorted(set(itertools.permutations(caps))):
                out = construct(n, perm)
                if out is None:
                    need(not rule(n, perm), "constructor refused a rule-feasible profile")
                    refused += 1
                    continue
                need(replay(out[0], out[1], perm), f"replay n={n} {perm}")
                need(sum(rank(N) for N in out[0]) == 3 * n // 2, "total rank 3n/2")
                built += 1
    result["construction"] = {"words_replayed": built, "profiles_refused": refused,
                              "max_dimension": 24}

    # 2b. k calls, k = 3..9, caps r = 1..6: every claimed-feasible n is built and replayed
    words_k = 0
    for k in range(3, 10):
        for r in range(1, 7):
            for n in range(2, k * r + 1, 2):
                out = construct_k(n, k, r)
                if not k_rule(n, k, r):
                    need(out is None, "k constructor accepted an excluded n")
                    continue
                need(out not in (None, "cap"), f"k construction failed n={n} k={k} r={r}")
                need(replay_k(out, r), f"k replay n={n} k={k} r={r}")
                need(sum(rank(N) for N in out) == n + -(-n // m_k(k)), "k total rank")
                words_k += 1
    for r in range(1, 200):   # the k = 4 rule is PR6122's 2 floor(4r/3)
        need(max(n for n in range(2, 4 * r + 1, 2) if k_rule(n, 4, r)) == 2 * (4 * r // 3), "k=4 agreement")
    for n in range(2, 40, 2):  # rank-one caps reproduce the n+1 minimum-query simplex
        need(min(k for k in range(3, 50) if k_rule(n, k, 1)) == n + 1, "rank-one minimum")
    result["k_calls"] = {"k_range": [3, 9], "cap_range": [1, 6], "words_replayed": words_k,
                         "five_call_capacity_r1_to_6": [max(n for n in range(2, 5 * r + 1, 2) if k_rule(n, 5, r)) for r in range(1, 7)],
                         "six_call_capacity_r1_to_6": [max(n for n in range(2, 6 * r + 1, 2) if k_rule(n, 6, r)) for r in range(1, 7)]}

    # 3. controls
    ctl = {}
    # (a) decider finds a witness for a reachable non-scalar target (E_21 at n=2,
    # caps (1,0,0,0): the normal form E_12 alone would miss it)
    sz2, irr2 = store[2]
    target = (0, 1)
    w, _ = decide(2, (1, 0, 0, 0), sz2, irr2, target)
    ctl["reachable_nonidentity_target_found"] = w is not None and check_witness(w, (1, 0, 0, 0), target)
    # (b) an invertible non-identity target with odd trace is unreachable at any caps
    odd = tuple((1 << i) | ((1 << (i + 1)) if i < 2 else 0) for i in range(3))
    sz3, irr3 = store[3]
    w, _ = decide(3, (1, 1, 1, 1), sz3, irr3, odd)
    ctl["odd_trace_target_rejected"] = w is None
    # (c) planted false witnesses fail the check
    good = construct(6, (3, 3, 3, 0))
    need(good is not None and replay(*good, (3, 3, 3, 0)), "positive fixture")
    bad_rank = check_witness((eye(6), zero(6), zero(6), zero(6)), (3, 3, 3, 3), eye(6))
    ctl["non_square_zero_witness_rejected"] = not bad_rank
    # (d) mutated words fail the replay
    layers, final = construct(8, (3, 3, 3, 3))
    m1 = [zero(8)] + layers[1:]
    m2 = [layers[1], layers[0]] + layers[2:]
    ctl["dropped_layer_rejected"] = not replay(m1, final, (3, 3, 3, 3))
    ctl["swapped_layers_rejected"] = not replay(m2, final, (3, 3, 3, 3))
    ctl["rank_cap_violation_rejected"] = not replay(layers, final, (2, 3, 3, 3))
    ctl["constructor_refuses_6_at_cap_2"] = construct(6, (2, 2, 2, 2)) is None
    ctl["constructor_refuses_10_at_cap_3"] = construct(10, (3, 3, 3, 3)) is None
    five = construct_k(8, 5, 2)
    ctl["five_calls_rank_two_twist_eight"] = five not in (None, "cap") and replay_k(five, 2)
    ctl["five_call_word_needs_its_constants"] = not replay(five, eye(8), (2,) * 5)
    ctl["five_call_word_order_free"] = replay_k(list(reversed(five)), 2)
    ctl["five_calls_rank_two_refuse_ten"] = construct_k(10, 5, 2) is None
    need(all(ctl.values()), f"controls {ctl}")
    result["controls"] = ctl

    if not compare:
        print(json.dumps(result, sort_keys=True, indent=2))
        return
    expected = json.loads((Path(__file__).resolve().parent / "RESULT.json").read_text())
    need(expected == result, "RESULT.json differs from the recomputed result")
    print(json.dumps(result, sort_keys=True))
    print("PASS_FOUR_BLOCK_QUERY_CAPACITY_AUDIT")


if __name__ == "__main__":
    need(sys.argv[1:] in ([], ["--print-result"]), "usage: verify.py [--print-result]")
    main(compare=not sys.argv[1:])
