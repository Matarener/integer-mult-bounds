# Independent functional classification of the fixed `L/2` word budget

**Partial result. No new `f(7)` bound, no kappa, no selected-frontier change.**

[PR2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973) (Nicholas Stone)
corrected the word-census engines retained by PR2542, PR2634 and PR2691. They group
prefix states by **coordinate bit 0** but apply a collision budget derived for
**Hamming-weight parity**, whose `s, t` are bounded by `L/2`. This package asks a
narrower and, so far as I can find, unanswered question: **is the bit-0 grouping
special, or is the substitution wrong for every non-parity functional?**

Answer, measured exhaustively on a stated domain: **the substitution is not a
bit-0 artifact.** At `(n, L) = (4, 10)` and `(5, 12)` it falsely prunes a
universal word for **every** nonzero linear functional of Hamming weight `<= n - 2`,
and for **none** of weight `>= n - 1`. At `(4, 8)` the same holds except for one
weight-2 functional (`1010`). Bit 0 is simply the first member of that class.

The regime the old seven-label censuses actually ran is **not** reached here.
See *Scope* below.

## What is established, at the strength proved

### 1. Independent reconstruction of the retained counterexample (measured)

The canonical word `01021323` at `n = 4, L = 8` has prefix states

```
q_0..q_8 = 0, 1, 3, 2, 6, 4, 12, 8, 0
```

All eight nonclosing states are distinct, every label occurs exactly twice, and
`S + S = F2^4` (the sumset has all 16 elements). Grouping by Hamming weight gives
the split `(4, 4)` with collision excess `0`. Grouping by coordinate bit 0 gives
the split `(6, 2)` with collision excess `8`. The substituted budget is
`C(4,2) + C(4,2) - 7 = 5`, so `8 > 5` rejects a universal word; the correct
budget for the actual bit-0 sizes is `C(6,2) + C(2,2) - 7 = 9`, and `8 <= 9`.
These are exactly the numbers in PR2973 section 4, reproduced here from scratch.

### 2. The defect is not specific to bit 0 (finite certificate, exhaustive)

Over **every** restricted-growth word of length `L` over `[0, n)` whose prefix
states `q_0 .. q_{L-1}` are distinct and whose last step returns to `q_0`, the
verifier classifies all `2^n - 1` nonzero linear functionals.

| `n` | `L` | universal words | substituted budget | functionals that falsely prune | false prunes |
|---:|---:|---:|---:|---:|---:|
| 3 | 6 | 4 | 3 | none | 0 |
| 3 | 8 | 2 | 9 | none | 0 |
| 4 | 8 | 22 | 5 | 9 of 15 | 44 |
| 4 | 10 | 110 | 13 | 10 of 15 | 190 |
| 5 | 10 | 0 | 5 | none | 0 |
| 5 | 12 | 828 | 15 | 24 of 31 | 2856 |
| 6 | 12 | 0 | -1 | none | 0 |
| 6 | 14 | 0 | 11 | none | 0 |
| 7 | 14 | 0 | -21 | none | 0 |

The functional weight pattern, measured:

| domain | firing weights | sound weights | exception |
|---|---|---|---|
| `(4, 8)` | 1, 2 | 2, 3, 4 | mask `1010` (weight 2) does not fire |
| `(4, 10)` | 1, 2 | 3, 4 | none |
| `(5, 12)` | 1, 2, 3 | 3, 4, 5 | mask `11010` (weight 3) does not fire |

At `(4, 8)` the verifier also finds **6** false prunes under bit 0 specifically,
and 22 universal simple words. Both figures agree with the independent
[PR3096 audit](../f7-bit0-false-prune/README.md) ("leaves 6", "22 simple canonical
universal words"), which I did not consult while writing this enumerator.

### 3. Why the substitution has a justification for exactly one functional

**Lemma (machine-checked on every word at `(4, 8)`, 3480 checks).** For a
nonzero linear functional with indicator vector `v`,

```
l(q_{i+1}) XOR l(q_i) = v_{w_i}.
```

So the class value flips at step `i` exactly when the label placed at step `i`
lies in the support of `v`. For `v = 1^n` every step flips, so `l(q_i) = i mod 2`
and the two classes *are* the weight-parity classes, whose sizes are bounded by
`L/2`. The `L/2` substitution therefore rests on an identity that holds for the
all-ones functional and for **no** other. For every other functional the class
sizes are whatever the word happens to produce, which is what the `d*d` slack
term measures.

The measured `weight >= n - 1` safety in the table above is *not* proved by this
lemma. It is an empirical regularity of these two domains. See open questions.

## Scope, and what is deliberately not claimed

- This is a **finite certificate on a stated small domain plus one scoped
  lemma**. It is not a new `f(7)` bound, not a corrected seven-label census, and
  not a proof that any old exclusion is wrong or right.
- **The seven-label decision regime is not reached.** PR2542's decisive call is
  `cyclic_census(7, 18, budget=9, simple=True)` and PR2634/PR2691 extend to
  `L = 20`. The only seven-label domain here is `(7, 14)`, which has **zero**
  universal simple words, so it is vacuous. A `(7, 18)` or `(7, 20)` functional
  census is a separate resource budget and a separate named decision; this
  package does not decide whether the old exclusion would have changed there.
- Rows `(5, 10)`, `(6, 12)`, `(6, 14)` and `(7, 14)` have zero universal simple
  words, so "no false prune" there is a statement about an empty set.
- `substituted budget = -1` at `(6, 12)` and `-21` at `(7, 14)` is a measured
  observation: at those parameters the old substitution is negative, so it would
  reject every candidate immediately. This is not offered as a correction.
- Nothing here revives or refutes PR2542's counting bound, pair identity,
  restoration parity or the verified Gray constructions, and nothing here revives
  the later set-level work (#2773, #2870, #2911, #2933, #2961) on its own
  hypotheses.
- Universality is `S + S = F2^n` over the **distinct** prefix states. The closing
  state `q_L = q_0` is not counted as a second point; that deduplication is
  explicit in `split_stats`.

## Reproduce

Python 3.12 standard library only, from the repository root:

```sh
python3 -I -B research/f7-bit0-functional-classification/verify.py
python3 -I -O -Werror -B research/f7-bit0-functional-classification/test_verify.py
```

The first command re-runs all nine domains, the separately written brute-force
cross-check at `(3,6)`, `(3,8)` and `(4,8)`, the `01021323` fixture and the
alternation lemma, then requires the freshly computed receipt to equal the
committed `RESULT.json` byte-for-byte after JSON canonicalisation. Its marker is
`PASS_F7_BIT0_FUNCTIONAL_CLASSIFICATION`. `--emit` rewrites `RESULT.json`.

`test_verify.py` adds 18 behavioural tests, including negative controls for the
domain bounds, the restoration predicate, the closing-state deduplication and
the receipt's internal consistency.

Runtime on the recorded host (Apple arm64) is about 1.5 s for the tests and
about 5 s for the verifier. Host and interpreter affect timing, not the counts.

**Executed interpreter.** These two commands were run locally under CPython
**3.15.0**, not 3.12: `python3.12` is not installed on this host. The code is
standard library only and uses no version-specific syntax, but the repository's
registered replay hook requires 3.12, so
`python3 -B scripts/research_package.py --package research/f7-bit0-functional-classification`
was **not** executed here. `scripts/research_package.py --package
research/f7-bit0-functional-classification --check-only` was executed and returns
`PASS_PACKAGE_METADATA_AND_PINS`.

## Implementation notes

`verify.py` is an independent implementation. No predecessor package code is
imported or executed; `SOURCES.json` pins the reference documents by hash and
marks them `usage: reference`.

The primary enumerator prunes on prefix-state distinctness and forces the final
step to land on `q_0`. The cross-check enumerator walks `product(range(n),
repeat=L)` with no pruning and filters afterwards. Agreement of
`simple_closed_words` and `universal_words` on three domains is asserted on every
run; it is the check that caught an off-by-one in the walk's starting step during
development.

## Open next questions

1. **The `(7, 18)` and `(7, 20)` functional census.** This is the only domain that
   changes a maintained decision. It needs its own budget; the enumerator is
   reusable but the state count at seven labels is large.
2. **Why weight `>= n - 1` is safe in these domains.** The alternation lemma
   explains why the `L/2` substitution is *justified* only for the all-ones
   functional. It does not explain why high-weight functionals happen not to
   *fire*. A proof or a counterexample at `(5, 14)` would settle it.
3. **The two exceptions**, masks `1010` at `(4, 8)` and `11010` at `(5, 12)`.
   If a weight-2 functional can be safe at one length and unsafe at another, the
   weight threshold is a heuristic, not a rule, and should not be generalised.
4. **Whether a repair can keep the bit-0 grouping.** Using the actual class sizes
   is sound for any functional, so the old traversal code could be repaired by
   one substitution instead of being rewritten. That is a source-change question
   for the maintainers, not a claim here.

## Credit and scope

Nicholas Stone wrote the word-census correction (#2973) and its `MATH.md`;
James Reed wrote the bit-0 small-domain audit (#3096); Ross Richardson supplied
the PR943 singleton prefix-walk model; Douglas Colkitt supplied the selected
source bindings and review. This package independently re-derives the retained
numbers and adds the functional classification and the alternation lemma. It does
not replace any of them.

Nick Petalas. Apache-2.0. Substantial automated assistance in research,
implementation, checking and writing. Separate internal source inspection and
review do not constitute independent human or proof-assistant review. Full
selected replay, all-size transfer and hosted CI are not claimed.