#!/usr/bin/env python3
"""Independent audit of the 20-prefix confinement step in the f(7)=24 chain.

Scope.  PR #3058 (research/connector-covering-code) proves f(7)=24 in the
PR943 singleton prefix-walk model.  Its length-22 argument needs three steps
for a 22-step word: |P| >= 20 (covering bound, imported), |P| = 20 impossible,
|P| = 21 impossible (its section 3), |P| = 22 impossible (its sections 4-5).
This verifier re-checks ONE of those steps with its own code: no 22-step word
can have exactly twenty distinct prefixes.

Argument re-derived here.  If |P| = 20 then every position of the walk lies in
the twenty-point set T = P, so the walk is a closed walk spanning T; the graph
G(T, D) induced on T by the walk's seven directions D must then be connected.
Directions come from a basis D of F2^7, and for a basis D the edge set of
G(T, D) is contained in the union of at most seven difference classes
diff(T) = {x XOR y : x, y in T}, one per basis vector.  So

    edges(G(T, D)) <= sum of the seven largest difference multiplicities,

and a graph on twenty vertices with at most two components needs at least
eighteen edges.  When the seven largest multiplicities sum below eighteen,
G(T, D) has at least three components for EVERY basis D, with no enumeration.

Every 20-point cover is an affine image of {0} u S for one of the five
19-point representatives in table6.json (imported classification), and
G(M T + b, D) = G(T, M^-1 D), so the check over all bases covers every cover.

What this verifier does NOT do: it does not re-prove the classification it
imports, it does not exclude |P| = 21 or |P| = 22, and it does not re-prove
f(7) = 24.  For the three representatives where the arithmetic bound is weaker
than eighteen edges it reports a sampled component count and marks the case
open, rather than claiming an exclusion.

Standard library only.  Deterministic: the sampling uses a fixed seed.
"""

import hashlib
import json
import sys
from itertools import combinations, combinations_with_replacement
from pathlib import Path

N = 7
FULL = (1 << N) - 1
ROOT = Path(__file__).resolve().parents[2]
TABLE6 = ROOT / "research/connector-covering-code/table6.json"

# Recorded word-level artifacts from the documented search runs in this
# package's SEARCH.md (stochastic search, positive control included).
W24 = "145164232614626031626540"
W22_B = "1206231531046325014203"
W22_A = "2130240236105010621045"

# Imported constants (credited, not re-proved here).
F5, F6 = 12, 16


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prefix_states(word):
    q = 0
    states = [0]
    for w in word:
        q ^= 1 << w
        states.append(q)
    return states


def pair_sums(points):
    return {a ^ b for a in points for b in points}


def is_universal_word(digits, n=N):
    """A restored word is universal iff its prefix set P satisfies P+P=F2^n."""
    if len(digits) % 2:
        return False, "odd_length"
    if not all(0 <= d < n for d in digits):
        return False, "label_out_of_range"
    states = prefix_states(digits)
    if states[-1] != 0:
        return False, "not_restored"
    counts = [0] * n
    for d in digits:
        counts[d] += 1
    if any(c == 0 or c % 2 for c in counts):
        return False, "usage_not_positive_even"
    return len(pair_sums(set(states))) == (1 << n), "ok"


def components(points, dirs):
    pts = sorted(points)
    idx = {p: i for i, p in enumerate(pts)}
    parent = list(range(len(pts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for d in dirs:
        for p in pts:
            j = idx.get(p ^ d)
            if j is not None and idx[p] < j:
                a, b = find(idx[p]), find(j)
                if a != b:
                    parent[a] = b
    return len({find(i) for i in range(len(pts))})


def difference_histogram(points):
    hist = {}
    for a, b in combinations(sorted(points), 2):
        hist[a ^ b] = hist.get(a ^ b, 0) + 1
    hist.pop(0, None)
    return hist


class Lcg:
    """Small deterministic generator: no dependence on CPython's RNG stream."""

    def __init__(self, seed):
        self.s = seed & ((1 << 64) - 1)

    def next(self):
        self.s = (self.s * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return self.s >> 16

    def randrange(self, n):
        return self.next() % n

    def basis(self):
        cols, span = [], {0}
        while len(cols) < N:
            v = 1 + self.randrange(FULL)
            if v not in span:
                span |= {s ^ v for s in span}
                cols.append(v)
        return cols


def main():
    failures = []
    notes = []

    def check(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail else ""))
        if not ok:
            failures.append(name)

    check("input_table6_present", TABLE6.is_file(), sha256_file(TABLE6) if TABLE6.is_file() else "missing")
    data = json.loads(TABLE6.read_text())
    reps = data["representatives"]
    check("five_representatives", len(reps) == 5, str([r["id"] for r in reps]))

    # ---- coverage oracle controls -------------------------------------------
    d24 = [int(c) for c in W24]
    ok, why = is_universal_word(d24)
    check("positive_control_w24_universal", ok, why)
    check("positive_control_w24_length", len(d24) == 24, str(len(d24)))
    d22b = [int(c) for c in W22_B]
    okb, whyb = is_universal_word(d22b)
    check("non_vacuity_w22_not_universal", (not okb) and whyb == "ok", whyb)
    covered = len(pair_sums(set(prefix_states(d22b))))
    check("non_vacuity_w22_coverage", covered == 126, f"covered={covered}/128")
    d22a = [int(c) for c in W22_A]
    oka, whya = is_universal_word(d22a)
    covered_a = len(pair_sums(set(prefix_states(d22a))))
    check("non_vacuity_w22_pattern_a", (not oka) and covered_a == 125, f"covered={covered_a}/128")
    check("mutant_w24_breaks", not is_universal_word([0] + d24[1:])[0], "prepended label")
    check("small_connected_control", components({0, 1, 2, 3, 4, 5, 6, 7},
                                                [1 << i for i in range(N)]) <= 2,
          "routine can see near-connectivity")

    # ---- confinement arithmetic --------------------------------------------
    open_reps, excluded_reps = [], []
    lcg = Lcg(20261018)
    results = {}
    for r in reps:
        T = sorted({0} | set(r["columns"]))
        check(f"rep{r['id']}_twenty_points", len(T) == 20, str(len(T)))
        check(f"rep{r['id']}_covers", len(pair_sums(T)) == 1 << N, "P+P=F2^7")
        hist = difference_histogram(T)
        top7 = sorted(hist.values(), reverse=True)[:7]
        need = len(T) - 2  # edges needed for at most two components
        bound_excludes = sum(top7) < need
        std = components(T, [1 << i for i in range(N)])
        samples = []
        for _ in range(200):
            samples.append(components(T, lcg.basis()))
        results[str(r["id"])] = {
            "distinct_differences": len(hist),
            "top7_multiplicity_sum": sum(top7),
            "edges_needed_for_two_components": need,
            "arithmetic_excludes_two_components": bound_excludes,
            "components_standard_basis": std,
            "components_min_over_200_sampled_bases": min(samples),
        }
        check(f"rep{r['id']}_standard_basis_ge3", std >= 3, f"components={std}")
        check(f"rep{r['id']}_sampled_bases_ge3", min(samples) >= 3,
              f"min over 200 bases={min(samples)}")
        if bound_excludes:
            excluded_reps.append(r["id"])
        else:
            open_reps.append(r["id"])

    complete = all(results[str(i)]["arithmetic_excludes_two_components"] for i in excluded_reps)
    notes.append(f"arithmetic exclusion complete for representatives {excluded_reps}")
    notes.append(f"remaining representatives {open_reps} carry sampled evidence only")

    # ---- simple-cycle multiplicity arithmetic ------------------------------
    patterns = []
    for counts in combinations_with_replacement(range(2, 23, 2), 7):
        if sum(counts) != 22:
            continue
        if max(counts) > 22 - F6:
            continue
        if any(a + b > 22 - F5 for a, b in combinations(counts, 2)):
            continue
        patterns.append(tuple(sorted(counts, reverse=True)))
    check("l22_simple_cycle_patterns", patterns == [(6, 4, 4, 2, 2, 2, 2), (4, 4, 4, 4, 2, 2, 2)],
          str(patterns))

    report = {
        "checked": "20-prefix confinement arithmetic for 20-point covers",
        "representatives": results,
        "arithmetic_excluded_representatives": excluded_reps,
        "sampled_only_representatives": open_reps,
        "l22_simple_cycle_multiplicity_patterns": patterns,
        "word_artifacts": {"universal_24_word": W24, "best_22_pattern_a": W22_A,
                           "best_22_pattern_b": W22_B},
    }
    print(json.dumps(report, indent=1, sort_keys=True))
    if failures:
        print("FAILED_CHECKS " + ",".join(failures))
        return 1
    print("PASS_F7_L22_CONFINEMENT_AUDIT "
          f"arithmetic_complete={len(excluded_reps)}/5 sampled_only={len(open_reps)} "
          f"f7_untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
