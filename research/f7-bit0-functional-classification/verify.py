"""Independent functional classification of the fixed L/2 bit-0 word budget.

Model (PR943 singleton prefix walk): q_0 = 0, q_{i+1} = q_i XOR (1 << w_i).
  restoration : every label occurs a positive even number of times
  universal   : the set S of distinct prefix states satisfies S + S = F2^n
  simple      : q_0 .. q_{L-1} are distinct (the closing q_L = q_0 adds no point)

For a nonzero linear functional with indicator mask `m`, write
  E = {p in S : parity(p & m) == 0},  O = S - E,  s = |E|,  t = |O|,
  a = C(s,2) - |{x XOR y : x != y, x,y in E}|,  b = analogously for O.
Universality forces a + b <= C(s,2) + C(t,2) - (Q - 1) with Q = 2^(n-1).
The old engine groups by coordinate bit 0 but substitutes the time-parity sizes
L/2, L/2.  Write base = C(L/2,2)*2 - (Q-1) and d = |s - t| / 2; then the
correct budget is exactly base + d*d.  The substitution is *false* for one word
when base < a + b <= base + d*d.

Nick Petalas, with substantial automated assistance.  Apache-2.0.
Independent implementation: no predecessor package code is imported.
"""

import argparse
import json
import sys
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent

DOMAINS = [
    (3, 6),
    (3, 8),
    (4, 8),
    (4, 10),
    (5, 10),
    (5, 12),
    (6, 12),
    (6, 14),
    (7, 14),
]
CROSS_CHECK = [(3, 6), (3, 8), (4, 8)]
MAX_N = 8
MAX_L = 16
MAX_EXAMPLES = 2
# Bound for the unpruned cross-check enumerator only; the primary enumerator
# prunes on prefix-state distinctness and is bounded by MAX_N and MAX_L.
MAX_BRUTE_WORDS = 6_553_600


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(v):
    return bin(v).count("1") & 1


def binom2(k):
    return k * (k - 1) // 2


def prefix_states(word):
    q = 0
    states = [0]
    for lab in word:
        q ^= 1 << lab
        states.append(q)
    return states


def restored(word):
    counts = {}
    for lab in word:
        counts[lab] = counts.get(lab, 0) + 1
    return all(c % 2 == 0 for c in counts.values())


def is_universal(states, n):
    S = set(states)
    return {x ^ y for x in S for y in S} == set(range(1 << n))


def split_stats(states, mask):
    """Class sizes and collision excess for the functional with indicator mask.

    Inputs are deduplicated first: the closing state q_L equals q_0 and must not
    be counted as a second point of the prefix set.
    """
    states = sorted(set(states))
    E = [p for p in states if parity(p & mask) == 0]
    O = [p for p in states if parity(p & mask) == 1]
    supp_e = {x ^ y for x, y in combinations(E, 2)}
    supp_o = {x ^ y for x, y in combinations(O, 2)}
    a = binom2(len(E)) - len(supp_e)
    b = binom2(len(O)) - len(supp_o)
    return len(E), len(O), a + b


def budget_terms(n, L):
    """(base, d) for the fixed L/2 substitution at (n, L)."""
    require(L % 2 == 0, "even length")
    half = L // 2
    base = 2 * binom2(half) - ((1 << (n - 1)) - 1)
    return base


def is_false_prune(n, L, states, mask):
    s, t, exc = split_stats(states, mask)
    base = budget_terms(n, L)
    d = (s - t) // 2
    return base < exc <= base + d * d, (s, t, exc, base, base + d * d)


def enumerate_words(n, L):
    """Restricted-growth words of length L over [0, n) with distinct prefix states.

    The closing step is forced to land back on q_0, so every emitted word is
    self-avoiding up to q_{L-1}.  Leaf words are additionally checked for
    restoration and universality by the caller.
    """
    require(1 <= n <= MAX_N and 2 <= L <= MAX_L, "bounded domain")
    seen = {0}
    word = []

    def walk(i, q, maxlab):
        """Place label w_i; `q` is the prefix state q_i before the placement."""
        if i == L:
            yield tuple(word), tuple(sorted(seen))
            return
        for lab in range(min(maxlab + 2, n)):
            nq = q ^ (1 << lab)
            if i == L - 1:
                if nq == 0:
                    word.append(lab)
                    yield from walk(i + 1, 0, max(maxlab, lab))
                    word.pop()
                continue
            if nq in seen:
                continue
            seen.add(nq)
            word.append(lab)
            yield from walk(i + 1, nq, max(maxlab, lab))
            word.pop()
            seen.discard(nq)

    yield from walk(0, 0, -1)


def survey(n, L):
    """Exhaustive record for one (n, L) domain."""
    require(1 <= n <= MAX_N and 2 <= L <= MAX_L, "bounded domain")
    masks = list(range(1, 1 << n))
    words = 0
    universal = 0
    firing = {}
    for word, states in enumerate_words(n, L):
        words += 1
        if not restored(word):
            continue
        if not is_universal(states, n):
            continue
        universal += 1
        for mask in masks:
            hit, detail = is_false_prune(n, L, states, mask)
            if not hit:
                continue
            entry = firing.setdefault(mask, {"count": 0, "examples": []})
            entry["count"] += 1
            if len(entry["examples"]) < MAX_EXAMPLES:
                entry["examples"].append(
                    {
                        "word": "".join(map(str, word)),
                        "s": detail[0],
                        "t": detail[1],
                        "excess": detail[2],
                        "substituted_budget": detail[3],
                        "correct_budget": detail[4],
                    }
                )
    return {
        "n": n,
        "L": L,
        "simple_closed_words": words,
        "universal_words": universal,
        "base_budget": budget_terms(n, L),
        "firing_masks": sorted(firing),
        "sound_masks": [m for m in masks if m not in firing],
        "firing_weight_max": max((bin(m).count("1") for m in firing), default=0),
        "false_prunes": sum(v["count"] for v in firing.values()),
        "records": firing,
    }


def canonical(word):
    """Restricted-growth form: first label 0, each later label at most max+1."""
    if word[0] != 0:
        return False
    high = 0
    for lab in word[1:]:
        if lab > high + 1:
            return False
        high = max(high, lab)
    return True


def brute_survey(n, L):
    """Separately written enumerator: every label sequence, filtered, no pruning."""
    require(1 <= n <= MAX_N and 2 <= L <= MAX_L, "bounded domain")
    require(n ** L <= MAX_BRUTE_WORDS, "bounded brute-force search space")
    words = 0
    universal = 0
    for word in product(range(n), repeat=L):
        if not canonical(word) or not restored(word):
            continue
        states = prefix_states(word)
        if len(set(states[:-1])) != L or states[-1] != states[0]:
            continue
        words += 1
        if is_universal(states, n):
            universal += 1
    return words, universal


def alternation_holds(n, L):
    """Machine check of the lemma: l(q_{i+1}) XOR l(q_i) == v_{w_i}."""
    require(1 <= n <= MAX_N and 2 <= L <= MAX_L, "bounded domain")
    checked = 0
    for word, _states in enumerate_words(n, L):
        for mask in range(1, 1 << n):
            states = prefix_states(word)
            for i in range(1, L + 1):
                step = parity(states[i] & mask) ^ parity(states[i - 1] & mask)
                require(
                    step == ((mask >> word[i - 1]) & 1),
                    f"alternation identity: word={word} mask={mask} i={i}",
                )
                checked += 1
    return checked


def fixture_01021323():
    """Exact independent reconstruction of the retained n=4 counterexample."""
    word = (0, 1, 0, 2, 1, 3, 2, 3)
    states = prefix_states(word)
    record = {
        "word": "".join(map(str, word)),
        "prefix_states": states,
        "distinct_nonclosing": len(set(states[:-1])),
        "restored": restored(word),
        "universal": is_universal(states, 4),
    }
    weight = split_stats(states, 0b1111)
    bit0 = split_stats(states, 0b0001)
    bit0_high = split_stats(states, 0b1000)
    base = budget_terms(4, 8)
    record["weight_split"] = [weight[0], weight[1]]
    record["weight_excess"] = weight[2]
    record["bit0_split"] = [bit0[0], bit0[1]]
    record["bit0_excess"] = bit0[2]
    record["bit3_split"] = [bit0_high[0], bit0_high[1]]
    record["bit3_excess"] = bit0_high[2]
    record["substituted_budget"] = base
    record["correct_bit0_budget"] = base + ((bit0[0] - bit0[1]) // 2) ** 2
    return record


def run(refresh=False):
    receipt = {
        "schema": 1,
        "model": "PR943 singleton prefix walk",
        "domains": [],
        "cross_check": [],
        "fixture": fixture_01021323(),
        "alternation_checks": 0,
    }
    for n, L in DOMAINS:
        receipt["domains"].append(survey(n, L))
        print(f"n={n} L={L} done", file=sys.stderr)
    for n, L in CROSS_CHECK:
        words, universal = brute_survey(n, L)
        fast = survey(n, L)
        require(
            (words, universal) == (fast["simple_closed_words"], fast["universal_words"]),
            f"cross-check mismatch at ({n},{L})",
        )
        receipt["cross_check"].append({"n": n, "L": L, "words": words, "universal": universal})
    receipt["alternation_checks"] = alternation_holds(4, 8)
    path = PACKAGE / "RESULT.json"
    if refresh or not path.exists():
        path.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n")
        print(f"wrote {path}", file=sys.stderr)
    stored = json.loads(path.read_bytes())
    canonical = json.loads(json.dumps(receipt, sort_keys=True))
    require(canonical == stored, "receipt mismatch: stored RESULT.json differs from a fresh run")
    return canonical


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true", help="rewrite RESULT.json")
    args = ap.parse_args()
    receipt = run(refresh=args.emit)
    hits = [
        (d["n"], d["L"], d["false_prunes"])
        for d in receipt["domains"]
        if d["false_prunes"]
    ]
    print("domains_with_false_prunes", hits)
    print("PASS_F7_BIT0_FUNCTIONAL_CLASSIFICATION")


if __name__ == "__main__":
    main()