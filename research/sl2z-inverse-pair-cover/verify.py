#!/usr/bin/env python3
"""Exact paid-call minimum for diag([B],[B^-1]) in the integer-shear alphabet.

Model: PR #3905. G = <X, Y> in SL2(Z), labels X^{+-1}, Y^{+-1}, scalar
ring F2[G], paid factor I + ([g] + [e]) N with N a rank-one idempotent in
M2(F2). Over F2 this is the gate (I - N)[e] + N[g] of the merged
research/group-subproduct-cover package (PR #5394), whose cover theorem
gives the lower bound once the ordered-subproduct cover number is known.

This script checks:
  1. the two gate forms agree for every rank-one idempotent and label;
  2. a complete census of label sequences of length 0..8: none of length
     at most seven has both B and B^-1 among its ordered subproducts;
  3. the eight-call coordinate-projector word equals diag([B],[B^-1]) in
     the formal algebra M2(F2[G]);
  4. deletion, reordering, sharing and support-lemma controls.

Standard library only. Read-only; no network, Git or file writes.
"""

import itertools
import random
import sys

# 2x2 integer matrices as tuples (a, b, c, d) = [[a, b], [c, d]].
IDENTITY = (1, 0, 0, 1)
LABELS = {
    "X": (1, 1, 0, 1),
    "x": (1, -1, 0, 1),  # X^-1
    "Y": (1, 0, 1, 1),
    "y": (1, 0, -1, 1),  # Y^-1
}
LETTERS = "XxYy"
MAX_LENGTH = 8


def mul(p, q):
    a, b, c, d = p
    e, f, g, h = q
    return (a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h)


def evaluate(word):
    m = IDENTITY
    for letter in word:
        m = mul(m, LABELS[letter])
    return m


B = evaluate("XXYY")
B_INV = evaluate("yyxx")


def fail(message):
    print("FAIL_SL2Z_INVERSE_PAIR_COVER " + message)
    sys.exit(1)


def require(condition, message):
    if not condition:
        fail(message)


# ---------------------------------------------------------------------------
# Formal algebra M_n(F2[G]). An entry is a frozenset of group elements: the
# support of an F2 combination, with addition as symmetric difference.

def entry_mul(u, v):
    out = set()
    for g in u:
        for h in v:
            out ^= {mul(g, h)}
    return frozenset(out)


def mat_mul(p, q):
    n, inner, m = len(p), len(q), len(q[0])
    out = []
    for i in range(n):
        row = []
        for j in range(m):
            acc = set()
            for k in range(inner):
                acc ^= entry_mul(p[i][k], q[k][j])
            row.append(frozenset(acc))
        out.append(tuple(row))
    return tuple(out)


def scalar(matrix):
    """Embed an F2 matrix as a formal matrix with coefficient [e]."""
    return tuple(
        tuple(frozenset({IDENTITY}) if x % 2 else frozenset() for x in row)
        for row in matrix
    )


def gate_3905(n_matrix, letter):
    """I + ([g] + [e]) N, the PR #3905 factor."""
    g = LABELS[letter]
    size = len(n_matrix)
    rows = []
    for i in range(size):
        row = []
        for j in range(size):
            acc = {IDENTITY} if i == j else set()
            if n_matrix[i][j] % 2:
                acc ^= {g}
                acc ^= {IDENTITY}
            row.append(frozenset(acc))
        rows.append(tuple(row))
    return tuple(rows)


def gate_5394(n_matrix, letter):
    """(I - N)[e] + N[g], the PR #5394 gate, reduced over F2."""
    g = LABELS[letter]
    size = len(n_matrix)
    rows = []
    for i in range(size):
        row = []
        for j in range(size):
            acc = set()
            if ((1 if i == j else 0) - n_matrix[i][j]) % 2:
                acc ^= {IDENTITY}
            if n_matrix[i][j] % 2:
                acc ^= {g}
            row.append(frozenset(acc))
        rows.append(tuple(row))
    return tuple(rows)


def product(factors):
    out = factors[0]
    for f in factors[1:]:
        out = mat_mul(out, f)
    return out


def rank_one_idempotents():
    found = []
    for bits in itertools.product((0, 1), repeat=4):
        n_matrix = ((bits[0], bits[1]), (bits[2], bits[3]))
        square = tuple(
            tuple(sum(n_matrix[i][k] * n_matrix[k][j] for k in range(2)) % 2 for j in range(2))
            for i in range(2)
        )
        det = (bits[0] * bits[3] - bits[1] * bits[2]) % 2
        if square == n_matrix and any(bits) and det == 0:
            found.append(n_matrix)
    return found


# ---------------------------------------------------------------------------
# Census of ordered-subproduct sets S(w) for every word w of length <= 8.

def census():
    """Return per-length counts and the length-8 words covering both targets."""
    covers_b = [0] * (MAX_LENGTH + 1)
    covers_inv = [0] * (MAX_LENGTH + 1)
    covers_both = [0] * (MAX_LENGTH + 1)
    words = [0] * (MAX_LENGTH + 1)
    both_words = []
    stack = [("", frozenset({IDENTITY}))]
    while stack:
        word, subproducts = stack.pop()
        k = len(word)
        words[k] += 1
        has_b = B in subproducts
        has_inv = B_INV in subproducts
        covers_b[k] += has_b
        covers_inv[k] += has_inv
        if has_b and has_inv:
            covers_both[k] += 1
            if k == MAX_LENGTH:
                both_words.append(word)
        if k == MAX_LENGTH:
            continue
        for letter in LETTERS:
            g = LABELS[letter]
            extended = subproducts | {mul(s, g) for s in subproducts}
            stack.append((word + letter, frozenset(extended)))
    return words, covers_b, covers_inv, covers_both, sorted(both_words)


def masks_for(word, target):
    k = len(word)
    out = []
    for mask in range(1 << k):
        if evaluate(word[i] for i in range(k) if mask >> i & 1) == target:
            out.append(mask)
    return out


def cover_number(targets, limit):
    """Least k <= limit with every target in one S(w); None if absent."""
    level = {frozenset({IDENTITY})}
    for k in range(limit + 1):
        if any(all(t in s for t in targets) for s in level):
            return k
        level = {
            frozenset(s | {mul(x, LABELS[letter]) for x in s})
            for s in level
            for letter in LETTERS
        }
    return None


def main():
    require(B == (5, 2, 2, 1), "B is not [[5,2],[2,1]]")
    require(mul(B, B_INV) == IDENTITY, "B_INV is not the inverse of B")

    # 1. Gate identity and the 24 legal factors of PR #3905.
    idempotents = rank_one_idempotents()
    require(len(idempotents) == 6, "expected six rank-one idempotents in M2(F2)")
    for n_matrix in idempotents:
        for letter in LETTERS:
            require(
                gate_3905(n_matrix, letter) == gate_5394(n_matrix, letter),
                "gate forms differ",
            )
    legal_factors = len(idempotents) * len(LETTERS)

    # 2. Complete census.
    words, covers_b, covers_inv, covers_both, both_words = census()
    require(words == [4 ** k for k in range(MAX_LENGTH + 1)], "census word counts")
    require(all(c == 0 for c in covers_both[: MAX_LENGTH]), "a word of length <= 7 covers both targets")
    require(covers_both[MAX_LENGTH] == 124, "expected 124 covering words of length 8")
    require(covers_b[3] == 0 and covers_inv[3] == 0, "a single target is covered below length 4")
    require(covers_b[4] == 1 and covers_inv[4] == 1, "single-target covers at length 4")
    geodesics_b = ["".join(w) for w in itertools.product(LETTERS, repeat=4) if evaluate(w) == B]
    geodesics_inv = ["".join(w) for w in itertools.product(LETTERS, repeat=4) if evaluate(w) == B_INV]
    require(geodesics_b == ["XXYY"] and geodesics_inv == ["yyxx"], "geodesic words")
    overlapping = 0
    for word in both_words:
        mb = masks_for(word, B)
        mi = masks_for(word, B_INV)
        require(mb and mi, "census cover lacks a mask")
        if any(p & q for p in mb for q in mi):
            overlapping += 1
    require(overlapping == 54, "expected 54 length-8 covers with an overlapping mask pair")
    require("XXYYyyxx" in both_words, "coordinate-projector word missing from census")

    # 3. Eight-call construction in M2(F2[G]).
    e11 = ((1, 0), (0, 0))
    e22 = ((0, 0), (0, 1))
    schedule = [(e11, "X"), (e11, "X"), (e11, "Y"), (e11, "Y"),
                (e22, "y"), (e22, "y"), (e22, "x"), (e22, "x")]
    target = (
        (frozenset({B}), frozenset()),
        (frozenset(), frozenset({B_INV})),
    )
    require(product([gate_3905(n, g) for n, g in schedule]) == target, "eight-call word")
    # Dirty inputs: the endpoint is an operator identity, so (u, v) -> (Bu, B^-1 v)
    # for every u, v in F2[G]. Check a few explicit dirty columns.
    rng = random.Random(3905)
    pool = [evaluate(w) for k in range(4) for w in itertools.product(LETTERS, repeat=k)]
    for _ in range(16):
        u = frozenset(rng.sample(pool, 3))
        v = frozenset(rng.sample(pool, 3))
        column = ((u,), (v,))
        out = mat_mul(product([gate_3905(n, g) for n, g in schedule]), column)
        require(out == ((entry_mul(frozenset({B}), u),), (entry_mul(frozenset({B_INV}), v),)),
                "dirty column")

    # 4. Controls.
    controls = 0
    for drop in range(len(schedule)):
        shorter = schedule[:drop] + schedule[drop + 1:]
        require(product([gate_3905(n, g) for n, g in shorter]) != target, "deletion control")
        controls += 1
    swapped = [(e11, "X"), (e11, "Y"), (e11, "X"), (e11, "Y")] + schedule[4:]
    require(product([gate_3905(n, g) for n, g in swapped]) != target, "reorder control")
    controls += 1
    # Sharing is detectable: B and X^2 share one four-letter cover.
    require(cover_number([B, evaluate("XX")], 6) == 4, "sharing control")
    require(cover_number([B, B_INV], 7) is None, "cover-number cross-check")
    require(cover_number([B, B_INV], 8) == 8, "cover-number cross-check at 8")
    controls += 1
    # Support lemma sanity: arbitrary F2 frames and interleaved scalar matrices
    # never produce a group element outside S(w).
    for _ in range(40):
        word = "".join(rng.choice(LETTERS) for _ in range(5))
        factors = []
        for letter in word:
            frame = tuple(tuple(rng.randrange(2) for _ in range(2)) for _ in range(2))
            mixer = tuple(tuple(rng.randrange(2) for _ in range(2)) for _ in range(2))
            factors.append(scalar(mixer))
            factors.append(gate_3905(frame, letter))
        result = product(factors)
        allowed = {evaluate(word[i] for i in range(5) if m >> i & 1) for m in range(32)}
        for row in result:
            for entry in row:
                require(entry <= allowed, "support lemma violated")
    controls += 1

    print(
        "PASS_SL2Z_INVERSE_PAIR_COVER "
        f"legal_factors={legal_factors} census_words={sum(words)} "
        f"max_both_cover_below_8={max(covers_both[:MAX_LENGTH])} "
        f"length8_both_covers={covers_both[MAX_LENGTH]} overlapping_mask_covers={overlapping} "
        f"geodesics=1+1 minimum_calls=8 controls={controls} no_new_kappa"
    )


if __name__ == "__main__":
    main()
