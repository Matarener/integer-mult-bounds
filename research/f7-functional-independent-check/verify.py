# SPDX-License-Identifier: Apache-2.0
"""Independent re-derivation of the f7 functional classification, plus two new domains.

Subject of the check
--------------------
`research/f7-bit0-functional-classification` (Nick Petalas) claims a finite
certificate over the PR943 singleton prefix walk: for a word `w` of even length
`L` over `[0, n)`, put `q_0 = 0`, `q_{i+1} = q_i XOR (1 << w_i)`.  A word is

    restored    : every label occurs an even number of times (equivalently q_L = q_0),
    simple      : q_0 .. q_{L-1} are distinct,
    universal   : S + S = F2^n for the set S of prefix states,

and the retained engines substitute the fixed budget

    base = 2 * C(L/2, 2) - (2^(n-1) - 1)

for the exact collision budget `base + d^2` with `d = (s - t)/2`, where `s`, `t`
are the sizes of the even/odd classes of a nonzero linear functional.  The claim
is a table of, per domain, the number of simple closed words, the number of
universal words, the number of words for which the substitution *falsely prunes*
(`base < a + b <= base + d^2`, with `a + b` the collision excess), the firing
mask set and the per-mask counts.

What this module does
---------------------
It recomputes every number in that table from scratch, with its own enumerator
and its own classifier, and asserts exact equality with the published values.
It then extends the census to three domains the published table does not
contain, including `(5, 14)`, which the published package names as its open
next question.

Independence.  No predecessor package code is imported, executed or copied here.
The published numbers are embedded as asserted constants; the enumeration,
the walk, the universality test and the collision excess are separate
implementations.  Two internal routes are compared on every run: a canonical
depth-first enumeration, and an unconstrained enumeration that is canonicalised
afterwards.  No Git objects, no network, no third-party package.
"""

import argparse
import json
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "RESULT.json"

MAX_N = 7
MAX_L = 14

# ---------------------------------------------------------------------------
# Published claim under check (research/f7-bit0-functional-classification)
# ---------------------------------------------------------------------------

# (n, L) -> (simple_closed_words, universal_words, base_budget, false_prunes)
PUBLISHED_TABLE = {
    (3, 6): (4, 4, 3, 0),
    (3, 8): (2, 2, 9, 0),
    (4, 8): (29, 22, 5, 44),
    (4, 10): (110, 110, 13, 190),
    (5, 10): (358, 0, 5, 0),
    (5, 12): (3695, 828, 15, 2856),
    (6, 12): (6525, 0, -1, 0),
    (6, 14): (123704, 0, 11, 0),
    (7, 14): (161936, 0, -21, 0),
}

# (n, L) -> {mask: false prune count} for the three firing domains only.  These
# are the published per-functional counts, transcribed from the published
# receipt; each row sums to that domain's published `false_prunes`.
PUBLISHED_MASK_COUNTS = {
    (4, 8): {1: 6, 2: 6, 3: 5, 4: 4, 5: 1, 6: 5, 8: 8, 9: 4, 12: 5},
    (4, 10): {1: 20, 2: 20, 3: 10, 4: 23, 5: 8, 6: 16, 8: 37, 9: 18,
              10: 10, 12: 28},
    (5, 12): {1: 248, 2: 248, 3: 96, 4: 278, 5: 143, 6: 119, 7: 25,
              8: 221, 9: 41, 10: 105, 11: 15, 12: 175, 13: 10, 14: 26,
              16: 361, 17: 140, 18: 100, 19: 50, 20: 64, 21: 4, 22: 32,
              24: 241, 25: 44, 28: 70},
}

# The published bit-0 column (functional mask 1) of the retained engine.
PUBLISHED_BIT0_FALSE_PRUNES = {(4, 8): 6, (4, 10): 20, (5, 12): 248}

# Fixture published with the table: the canonical word 01021323 at (4, 8).
PUBLISHED_FIXTURE = {
    "word": (0, 1, 0, 2, 1, 3, 2, 3),
    "prefix_states": (0, 1, 3, 2, 6, 4, 12, 8, 0),
    "distinct_nonclosing": 8,
    "restored": True,
    "universal": True,
    "weight_split": (4, 4),
    "weight_excess": 0,
    "bit0_split": (6, 2),
    "bit0_excess": 8,
    "substituted_budget": 5,
    "correct_bit0_budget": 9,
}

# Domains in the published table, and the new domains this package adds.
PUBLISHED_DOMAINS = sorted(PUBLISHED_TABLE)
NEW_DOMAINS = [(3, 10), (4, 12), (5, 14)]
# Unconstrained-enumeration cross-check domains (canonical forms must agree).
CANONICAL_CROSS_CHECK = [(3, 6), (3, 8), (4, 8), (4, 10), (5, 10), (5, 12)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


# ---------------------------------------------------------------------------
# Walk, predicates and collision excess
# ---------------------------------------------------------------------------


def prefix_states(word):
    """q_0 .. q_L for the singleton prefix walk, as a tuple."""
    q = 0
    out = [q]
    for lab in word:
        q ^= 1 << lab
        out.append(q)
    return tuple(out)


def is_simple(word):
    states = prefix_states(word)
    return len(set(states[:-1])) == len(word)


def is_restored(word):
    counts = Counter(word)
    return all(value % 2 == 0 for value in counts.values())


def is_universal(word, n):
    states = set(prefix_states(word)[:-1])
    reach = {x ^ y for x in states for y in states}
    return len(reach) == (1 << n)


def sumset_size(word, n):
    states = set(prefix_states(word)[:-1])
    return len({x ^ y for x in states for y in states})


def excess_by_counter(states, mask):
    """Collision excess a + b, computed from a difference multiplicity table.

    For a class C of size k the excess is C(k, 2) - |{x XOR y : x != y, in C}|.
    Counting unordered pairs per difference gives the same number through
    `sum(u_d - 1 over appearing d)` because the appearing differences partition
    the unordered pairs.
    """
    even, odd = [], []
    for point in states:
        (even if bin(point & mask).count("1") % 2 == 0 else odd).append(point)
    excess = 0
    for side in (even, odd):
        diff = Counter()
        for x, y in combinations(side, 2):
            diff[x ^ y] += 1
        for value in diff.values():
            excess += value - 1
    return excess, len(even), len(odd)


def excess_by_set(states, mask):
    """The same excess by the direct support-size difference."""
    even, odd = [], []
    for point in states:
        (even if bin(point & mask).count("1") % 2 == 0 else odd).append(point)
    excess = 0
    for side in (even, odd):
        support = {x ^ y for x, y in combinations(side, 2)}
        excess += len(side) * (len(side) - 1) // 2 - len(support)
    return excess, len(even), len(odd)


def base_budget(n, L):
    require(L % 2 == 0, "even length required")
    half = L // 2
    return 2 * (half * (half - 1) // 2) - ((1 << (n - 1)) - 1)


def false_prune(n, L, states, mask, extra=0):
    """Does the fixed `base` budget wrongly reject this word for this functional?

    `extra` widens the right-hand endpoint, which is how the sensitivity control
    perturbs the rule under check.
    """
    excess, s, t = excess_by_counter(states, mask)
    require((s - t) % 2 == 0, "class-size parity")
    d = (s - t) // 2
    base = base_budget(n, L)
    return base < excess <= base + extra + d * d, (excess, s, t, base, d)


# ---------------------------------------------------------------------------
# Two independent enumerators
# ---------------------------------------------------------------------------


def enumerate_canonical(n, L):
    """First-occurrence words of length L: q_0..q_{L-1} distinct, q_L = q_0.

    `maxlab` enforces first-occurrence label order, so each relabelling class
    contributes exactly one word.  The last step is forced (it must close).
    """
    require(1 <= n <= MAX_N and 2 <= L <= MAX_L and L % 2 == 0, "domain bounds")
    words, nodes = [], 0
    stack = [(0, 1, -1, 0, ())]  # state, visited states, max label, depth, word
    while stack:
        q, visited, maxlab, depth, word = stack.pop()
        nodes += 1
        if depth == L:
            if q == 0:
                words.append(word)
            continue
        top = min(maxlab + 1, n - 1)
        if depth == L - 1:
            for lab in range(top + 1):
                if q ^ (1 << lab) == 0:
                    stack.append((0, visited, max(maxlab, lab), depth + 1, word + (lab,)))
        else:
            for lab in range(top + 1):
                nq = q ^ (1 << lab)
                if not (visited >> nq) & 1:
                    stack.append((nq, visited | (1 << nq), max(maxlab, lab),
                                  depth + 1, word + (lab,)))
    return words, nodes


def enumerate_unconstrained(n, L):
    """Every word of length L (canonical order dropped), filtered afterwards.

    Returns the set of first-occurrence canonical forms, so its cardinality is
    comparable with `enumerate_canonical`.
    """
    require(1 <= n <= MAX_N and 2 <= L <= MAX_L and L % 2 == 0, "domain bounds")
    forms, nodes = set(), 0
    stack = [(0, frozenset([0]), 0, ())]  # state, visited states, depth, word
    while stack:
        q, visited, depth, word = stack.pop()
        nodes += 1
        if depth == L:
            if q == 0:
                forms.add(canonical_form(word))
            continue
        last = depth == L - 1
        for lab in range(n):
            nq = q ^ (1 << lab)
            if last:
                if nq == 0:
                    stack.append((0, visited, depth + 1, word + (lab,)))
            elif nq not in visited:
                stack.append((nq, visited | {nq}, depth + 1, word + (lab,)))
    return forms, nodes


def canonical_form(word):
    """Relabel by first occurrence: 0, 1, 2, ..."""
    seen, out = {}, []
    for lab in word:
        if lab not in seen:
            seen[lab] = len(seen)
        out.append(seen[lab])
    return tuple(out)


# ---------------------------------------------------------------------------
# Domain census
# ---------------------------------------------------------------------------


def classify_domain(n, L):
    """Complete functional classification of one (n, L) domain."""
    words, nodes = enumerate_canonical(n, L)
    simple_closed = len(words)
    universal = [w for w in words if is_universal(w, n)]
    masks = range(1, 1 << n)
    per_mask = {}
    per_mask_bit0 = {}
    for mask in masks:
        hits = 0
        for word in universal:
            states = prefix_states(word)[:-1]
            fired, _ = false_prune(n, L, states, mask)
            if fired:
                hits += 1
        if hits:
            per_mask[mask] = hits
    for word in universal:
        states = prefix_states(word)[:-1]
        if false_prune(n, L, states, 1)[0]:
            per_mask_bit0[word] = 1
    weight_of = {m: bin(m).count("1") for m in masks}
    firing = sorted(per_mask)
    return {
        "n": n,
        "L": L,
        "base_budget": base_budget(n, L),
        "nodes": nodes,
        "simple_closed_words": simple_closed,
        "universal_words": len(universal),
        "false_prunes": sum(per_mask.values()),
        "bit0_false_prunes": len(per_mask_bit0),
        "per_mask_counts": {str(m): per_mask[m] for m in firing},
        "firing_masks": firing,
        "firing_weights": sorted({weight_of[m] for m in firing}),
        "sound_masks": sorted(set(masks) - set(firing)),
        "masks_total": (1 << n) - 1,
    }


def verify_fixture():
    word = PUBLISHED_FIXTURE["word"]
    states = prefix_states(word)
    require(states == PUBLISHED_FIXTURE["prefix_states"], "fixture prefix states")
    require(len(set(states[:-1])) == PUBLISHED_FIXTURE["distinct_nonclosing"],
            "fixture distinct states")
    require(is_restored(word) is True, "fixture restoration")
    require(is_universal(word, 4) is True, "fixture universality")
    weight_excess, s_w, t_w = excess_by_counter(states[:-1], 0b1111)
    require((s_w, t_w) == PUBLISHED_FIXTURE["weight_split"], "fixture weight split")
    require(weight_excess == PUBLISHED_FIXTURE["weight_excess"], "fixture weight excess")
    bit0_excess, s_0, t_0 = excess_by_counter(states[:-1], 0b0001)
    require((s_0, t_0) == PUBLISHED_FIXTURE["bit0_split"], "fixture bit0 split")
    require(bit0_excess == PUBLISHED_FIXTURE["bit0_excess"], "fixture bit0 excess")
    require(base_budget(4, 8) == PUBLISHED_FIXTURE["substituted_budget"], "fixture budget")
    s_f, t_f = PUBLISHED_FIXTURE["bit0_split"]
    exact = s_f * (s_f - 1) // 2 + t_f * (t_f - 1) // 2 - ((1 << 3) - 1)
    require(exact == PUBLISHED_FIXTURE["correct_bit0_budget"], "fixture corrected budget")
    require(exact == base_budget(4, 8) + ((s_f - t_f) // 2) ** 2,
            "fixture corrected budget equals base + d^2")
    return {"word": "".join(str(d) for d in word),
            "prefix_states": list(states),
            "bit0_excess": bit0_excess,
            "substituted_budget": base_budget(4, 8),
            "correct_bit0_budget": PUBLISHED_FIXTURE["correct_bit0_budget"]}


def run(selected_new=NEW_DOMAINS):
    receipt = {"schema": 1, "fixture": verify_fixture(),
               "published_domains": [], "new_domains": [], "controls": {},
               "cross_check": []}

    for (n, L) in PUBLISHED_DOMAINS:
        record = classify_domain(n, L)
        claim_simple, claim_universal, claim_base, claim_prunes = PUBLISHED_TABLE[(n, L)]
        require(record["simple_closed_words"] == claim_simple,
                f"simple closed count {(n, L)}")
        require(record["universal_words"] == claim_universal,
                f"universal count {(n, L)}")
        require(record["base_budget"] == claim_base, f"base budget {(n, L)}")
        require(record["false_prunes"] == claim_prunes, f"false prune count {(n, L)}")
        expected = PUBLISHED_MASK_COUNTS.get((n, L), {})
        require(record["per_mask_counts"] == {str(k): v for k, v in expected.items()},
                f"per-mask counts {(n, L)}")
        if (n, L) in PUBLISHED_BIT0_FALSE_PRUNES:
            require(record["bit0_false_prunes"] == PUBLISHED_BIT0_FALSE_PRUNES[(n, L)],
                    f"bit-0 false prune count {(n, L)}")
        receipt["published_domains"].append(record)

    for (n, L) in selected_new:
        receipt["new_domains"].append(classify_domain(n, L))

    # Control 1: every enumerated word is restored and simple by construction,
    # and the two independent excess routes agree everywhere.
    pairs = 0
    for (n, L) in PUBLISHED_DOMAINS + list(selected_new):
        words, _ = enumerate_canonical(n, L)
        for word in words:
            require(is_restored(word), f"enumerated word not restored at {(n, L)}")
            require(is_simple(word), f"enumerated word not simple at {(n, L)}")
            if not is_universal(word, n):
                continue
            states = prefix_states(word)[:-1]
            for mask in range(1, 1 << n):
                if excess_by_counter(states, mask) != excess_by_set(states, mask):
                    raise ValueError(f"excess routes disagree at {(n, L)} mask {mask}")
                pairs += 1
    receipt["controls"]["excess_route_pairs"] = pairs

    # Control 2: shifting the substituted budget must change the firing pattern,
    # which shows the check depends on the exact budget value and not only on the
    # class sizes.  Every domain with no universal word must stay at zero.
    shifted = {}
    for shift in (-2, -1, 1, 2):
        row = {}
        for (n, L) in PUBLISHED_DOMAINS:
            words, _ = enumerate_canonical(n, L)
            hits = 0
            for word in words:
                if not is_universal(word, n):
                    continue
                states = prefix_states(word)[:-1]
                for mask in range(1, 1 << n):
                    if false_prune(n, L, states, mask, extra=shift)[0]:
                        hits += 1
            row[f"{n},{L}"] = hits
        shifted[str(shift)] = row
    changed = []
    for (n, L) in PUBLISHED_DOMAINS:
        key = f"{n},{L}"
        claim = PUBLISHED_TABLE[(n, L)][3]
        vals = {shifted[str(shift)][key] for shift in (-2, -1, 1, 2)}
        if claim == 0:
            require(vals == {0}, f"a budget shift invented prunes at {(n, L)}: {vals}")
        elif vals != {claim}:
            changed.append(key)
    require(sorted(changed) == ["4,10", "4,8", "5,12"],
            f"a budget shift must move exactly the firing domains, got {changed}")
    receipt["controls"]["budget_shift_prunes"] = shifted

    # Control 3: unconstrained enumeration must reproduce the canonical census.
    for (n, L) in CANONICAL_CROSS_CHECK:
        canonical, _ = enumerate_canonical(n, L)
        unconstrained, _ = enumerate_unconstrained(n, L)
        require(set(canonical) == unconstrained,
                f"enumerators disagree at {(n, L)}: "
                f"{len(set(canonical) ^ unconstrained)} symmetric difference")
        receipt["cross_check"].append(
            {"n": n, "L": L, "words": len(unconstrained)})

    return receipt


def write_receipt(receipt):
    RESULT_PATH.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="regenerate RESULT.json beside this file")
    args = parser.parse_args(argv)
    receipt = run()
    if args.write:
        write_receipt(receipt)
    else:
        require(RESULT_PATH.exists(), "committed RESULT.json is missing")
        committed = json.loads(RESULT_PATH.read_text())
        require(committed == receipt, "fresh receipt differs from committed RESULT.json")
    for record in receipt["published_domains"]:
        print(f"published n={record['n']} L={record['L']}: "
              f"closed={record['simple_closed_words']} "
              f"universal={record['universal_words']} "
              f"false_prunes={record['false_prunes']} "
              f"weights={record['firing_weights']}")
    for record in receipt["new_domains"]:
        print(f"new       n={record['n']} L={record['L']}: "
              f"closed={record['simple_closed_words']} "
              f"universal={record['universal_words']} "
              f"false_prunes={record['false_prunes']} "
              f"weights={record['firing_weights']}")
    print("PASS_F7_FUNCTIONAL_INDEPENDENT_CHECK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
