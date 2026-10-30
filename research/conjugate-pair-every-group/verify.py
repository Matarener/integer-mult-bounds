#!/usr/bin/env python3
"""Finite corroboration for the every-group conjugate-pair four-call floor.

The written proof is PROOF.md. This verifier checks, with exact arithmetic:

1. the factor and product expansions used by the proof, on seeded random
   rational and binary instances;
2. the corner-selection identities N1 P_U N3 = P_U or 0 used by Lemma 1;
3. the direct four-call word, for every signature and checked field/width;
4. that no word of length at most three realizes the target, for every
   distinct length-three coincidence signature of a noncommuting pair in
   S3, S4, S5, Q8 and the free group, over F2 at widths 2 and 3 and over F3
   at width 2;
5. failure controls: the four-call word with one call removed, and the
   commuting pair y = x^-1, whose target is the identity.

Standard library only. Prints PASS_CONJUGATE_PAIR_EVERY_GROUP on success.
"""

import itertools
import random
import sys
from fractions import Fraction

MARKER = "PASS_CONJUGATE_PAIR_EVERY_GROUP"
WORDS = tuple(w for k in range(5) for w in itertools.product("xy", repeat=k))


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


# ---------------------------------------------------------------- matrices

def mat_mul(a, b, p):
    n = len(a)
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(n)) % p for j in range(n))
        for i in range(n)
    )


def mat_add(a, b, p):
    return tuple(tuple((x + y) % p for x, y in zip(r, s)) for r, s in zip(a, b))


def mat_sub(a, b, p):
    return tuple(tuple((x - y) % p for x, y in zip(r, s)) for r, s in zip(a, b))


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def zero(n):
    return tuple(tuple(0 for _ in range(n)) for _ in range(n))


def unit(n, i):
    return tuple(tuple(int(a == i and b == i) for b in range(n)) for a in range(n))


def rank_one_idempotents(r, p):
    """All N = u v^T over F_p with v^T u = 1 (each N listed once)."""
    vectors = [v for v in itertools.product(range(p), repeat=r) if any(v)]
    found = set()
    for u in vectors:
        for v in vectors:
            if sum(a * b for a, b in zip(u, v)) % p == 1:
                found.add(tuple(tuple(a * b % p for b in v) for a in u))
    expected = (p ** r - 1) * p ** (r - 1) // (p - 1)
    require(len(found) == expected, "idempotent count at r=%d p=%d" % (r, p))
    return sorted(found)


# ---------------------------------------------------------- group signatures

def compose(a, b):
    """Group product a*b for permutations: apply b first."""
    return tuple(a[i] for i in b)


def signature(x, y, e, mul):
    """Partition of all positive words of length <= 4 by group value."""
    index = {}
    labels = []
    for word in WORDS:
        g = e
        for c in word:
            g = mul(g, x if c == "x" else y)
        labels.append(index.setdefault(g, len(index)))
    return tuple(labels)


def permutation_signatures():
    sigs = {}
    for n in (3, 4, 5):
        elements = list(itertools.permutations(range(n)))
        e = tuple(range(n))
        for x in elements:
            for y in elements:
                if compose(x, y) != compose(y, x):
                    sigs.setdefault(signature(x, y, e, compose), "S%d" % n)
    return sigs


def quaternion_signatures():
    # Q8 as pairs (sign, unit) with units 1,i,j,k.
    table = {
        ("1", u): (1, u) for u in "1ijk"
    }
    table.update({(u, "1"): (1, u) for u in "1ijk"})
    table.update({
        ("i", "i"): (-1, "1"), ("j", "j"): (-1, "1"), ("k", "k"): (-1, "1"),
        ("i", "j"): (1, "k"), ("j", "i"): (-1, "k"),
        ("j", "k"): (1, "i"), ("k", "j"): (-1, "i"),
        ("k", "i"): (1, "j"), ("i", "k"): (-1, "j"),
    })

    def mul(a, b):
        s, u = table[(a[1], b[1])]
        return (a[0] * b[0] * s, u)

    elements = [(s, u) for s in (1, -1) for u in "1ijk"]
    sigs = {}
    for x in elements:
        for y in elements:
            if mul(x, y) != mul(y, x):
                sigs.setdefault(signature(x, y, (1, "1"), mul), "Q8")
    return sigs


def free_signature():
    return {signature("x", "y", "", lambda a, b: a + b): "free"}


def word_value(sig, word):
    return sig[WORDS.index(word)]


# ------------------------------------------------------------ word products

def corner_products(ns, p):
    """P_U for every subset U (bitmask over call positions)."""
    r = len(ns[0])
    comps = [mat_sub(identity(r), n, p) for n in ns]
    out = {}
    for mask in range(1 << len(ns)):
        prod = identity(r)
        for i, n in enumerate(ns):
            prod = mat_mul(prod, n if mask >> i & 1 else comps[i], p)
        out[mask] = prod
    return out


def coefficients(sig, labels, ns, p):
    """Group-algebra coefficients of a chronological product of paid factors."""
    r = len(ns[0])
    acc = {}
    for mask, prod in corner_products(ns, p).items():
        word = tuple(labels[i] for i in range(len(labels)) if mask >> i & 1)
        g = word_value(sig, word)
        acc[g] = mat_add(acc.get(g, zero(r)), prod, p)
    return acc


def target(sig, r):
    rest = tuple(tuple(int(i == j and i >= 2) for j in range(r)) for i in range(r))
    out = {word_value(sig, ()): rest}
    for word, role in ((("x", "y"), 0), (("y", "x"), 1)):
        g = word_value(sig, word)
        out[g] = mat_add(out.get(g, zero(r)), unit(r, role), 2 ** 31)
    return out


def realizes(sig, labels, ns, p):
    r = len(ns[0])
    got = coefficients(sig, labels, ns, p)
    want = {g: tuple(tuple(v % p for v in row) for row in m)
            for g, m in target(sig, r).items()}
    for g in set(got) | set(want):
        if got.get(g, zero(r)) != want.get(g, zero(r)):
            return False
    return True


def class_key(sig, labels):
    """Canonical map from call subsets to coefficient classes.

    Realizability of the target depends only on this key: which subsets share
    a group value, and which classes are e, xy and yx.
    """
    special = {word_value(sig, ()): "e", word_value(sig, ("x", "y")): "xy",
               word_value(sig, ("y", "x")): "yx"}
    names = {}
    key = []
    for mask in range(1 << len(labels)):
        word = tuple(labels[i] for i in range(len(labels)) if mask >> i & 1)
        g = word_value(sig, word)
        key.append(special.get(g) or names.setdefault(g, len(names)))
    return tuple(key)


def key_realizable(key, products, r, p):
    want = {"e": tuple(tuple(int(i == j and i >= 2) for j in range(r))
                       for i in range(r)),
            "xy": unit(r, 0), "yx": unit(r, 1)}
    if "xy" not in key or "yx" not in key:
        return False
    for cls in ("xy", "yx", "e") + tuple(sorted(c for c in set(key)
                                                 if isinstance(c, int))):
        acc = zero(r)
        for mask, c in enumerate(key):
            if c == cls:
                acc = mat_add(acc, products[mask], p)
        if acc != want.get(cls, zero(r)):
            return False
    return True


def short_word_keys(sigs):
    keys = set()
    for sig in sigs:
        for k in (1, 2, 3):
            for labels in itertools.product("xy", repeat=k):
                keys.add(class_key(sig, labels))
    return keys


def no_short_word(keys, idems, p):
    """Exhaustive search over every word of length 1..3 for every key."""
    r = len(idems[0])
    by_len = {}
    for key in keys:
        by_len.setdefault(len(key), []).append(key)
    for size, group in by_len.items():
        k = size.bit_length() - 1
        for ns in itertools.product(idems, repeat=k):
            products = corner_products(ns, p)
            for key in group:
                if key_realizable(key, products, r, p):
                    return False
    return True


# ----------------------------------------------------------------- checks

def check_expansion_identities():
    """D_N(g) = [g]N + (I-N) and the corner selection identities."""
    rng = random.Random(20261028)
    for _ in range(200):
        r = rng.choice((2, 3, 4))
        ns = []
        for _ in range(3):
            while True:
                u = [Fraction(rng.randint(-3, 3)) for _ in range(r)]
                v = [Fraction(rng.randint(-3, 3)) for _ in range(r)]
                s = sum(a * b for a, b in zip(u, v))
                if s != 0:
                    break
            ns.append(tuple(tuple(a * b / s for b in v) for a in u))
        eye = tuple(tuple(Fraction(int(i == j)) for j in range(r)) for i in range(r))

        def mm(a, b):
            return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(r))
                               for j in range(r)) for i in range(r))

        def ms(a, b):
            return tuple(tuple(x - y for x, y in zip(c, d)) for c, d in zip(a, b))

        for n in ns:
            require(mm(n, n) == n, "rational idempotent")
            require(mm(n, ms(eye, n)) == mm(ms(eye, n), n) == ms(eye, eye),
                    "complementary idempotents annihilate")
        comps = [ms(eye, n) for n in ns]
        zero_r = ms(eye, eye)
        for mask in range(8):
            prod = eye
            for i in range(3):
                prod = mm(prod, ns[i] if mask >> i & 1 else comps[i])
            left = mm(ns[0], prod)
            right = mm(prod, ns[2])
            require(left == (prod if mask & 1 else zero_r),
                    "left corner selection")
            require(right == (prod if mask & 4 else zero_r),
                    "right corner selection")
            bar_left = mm(comps[0], prod)
            require(bar_left == (prod if not mask & 1 else zero_r),
                    "left complement selection")
        # Sum over subsets of P_U equals I: the product of (N_i + (I - N_i)).
        total = tuple(tuple(Fraction(0) for _ in range(r)) for _ in range(r))
        for mask in range(8):
            prod = eye
            for i in range(3):
                prod = mm(prod, ns[i] if mask >> i & 1 else comps[i])
            total = tuple(tuple(a + b for a, b in zip(c, d))
                          for c, d in zip(total, prod))
        require(total == eye, "subset expansion sums to identity")
    return 200


def check_direct_word(sig, r, p):
    labels = ("x", "y", "y", "x")
    ns = (unit(r, 0), unit(r, 0), unit(r, 1), unit(r, 1))
    require(realizes(sig, labels, ns, p), "direct four-call word")
    for drop in range(4):
        sub_l = labels[:drop] + labels[drop + 1:]
        sub_n = ns[:drop] + ns[drop + 1:]
        require(not realizes(sig, sub_l, sub_n, p), "mutated direct word rejected")


def check_commuting_control():
    """The noncommuting hypothesis is needed: y = x^-1 gives target I."""
    e = (0, 1, 2)
    x = (1, 2, 0)
    y = (2, 0, 1)
    require(compose(x, y) == e == compose(y, x), "inverse control pair")
    sig = signature(x, y, e, compose)
    r = 2
    got = target(sig, r)
    require(got == {word_value(sig, ()): identity(r)},
            "inverse pair target is the identity, met by the empty word")
    return r


def main():
    checked = check_expansion_identities()
    print("expansion and corner identities: %d random rational triples" % checked)
    sigs = {}
    sigs.update(permutation_signatures())
    sigs.update(quaternion_signatures())
    sigs.update(free_signature())
    print("distinct noncommuting length-4 signatures: %d" % len(sigs))
    keys = short_word_keys(sigs)
    print("distinct subset-class keys for words of length 1..3: %d" % len(keys))
    for sig in sigs:
        require(word_value(sig, ()) not in
                (word_value(sig, ("x", "y")), word_value(sig, ("y", "x"))),
                "the empty word cannot realize the target")
    for (r, p) in ((2, 2), (3, 2), (2, 3)):
        idems = rank_one_idempotents(r, p)
        for sig in sigs:
            check_direct_word(sig, r, p)
        require(no_short_word(keys, idems, p),
                "a word of length <= 3 realizes the target (r=%d p=%d)" % (r, p))
        print("F%d width %d: %d idempotents, no word of length <= 3 for any "
              "key; direct word passes" % (p, r, len(idems)))
    control = check_commuting_control()
    print("control y = x^-1: target is I at width %d, met by zero calls" % control)
    print(MARKER)


if __name__ == "__main__":
    main()
