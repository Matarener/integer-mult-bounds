# Independent check of the `f7` functional classification, and the `(5, 14)` domain

**Independent verification (no κ) of a finite certificate, plus new coverage the
checked package itself names as its next question. No new `f(7)` bound, no
supplier, no selected-frontier change.**

## Subject of the check

[`research/f7-bit0-functional-classification`](../f7-bit0-functional-classification/README.md)
(branch `research/w5-b21-todo-20261018`, head `13db47d8d31603c1391572009e1eb7a22675a219`,
PR #3699) reports, on the PR943 singleton prefix walk, that the retained engines'
fixed `L/2` budget substitution is not a coordinate-bit-0 artefact: it falsely
prunes universal words for every functional of low Hamming weight and for none of
high weight, on nine `(n, L)` domains.

This package recomputes that certificate from scratch and extends it to three
domains the published table does not contain, including `(5, 14)`, which the
published package lists as its open next question 2.

The claim under check is fixed at that package's own publication head
`13db47d8d31603c1391572009e1eb7a22675a219`, where its `README.md`,
`RESULT.json` and `verify.py` have SHA-256
`8176c8a889671f67ebcd6f1b9e9efddae55cfbbff4b486442a9b63977e9c4844`,
`5938908a76c497bad4c301eed0f12822fc16b0fbbbff2c0bc5150d82f2052105` and
`a0c93985734fa6855c5561a1b4eb730ef0af6ddd25bfdac1ef8b61d840efbe83` and Git
blob ids `4618c68ffc94be30055537bca4e49696946437dc`,
`84017d1265858fe976bd317c95d287c92fc4cb7e` and
`f554ec10c8ac5e30e067b01adf9b68b2eb80906a`. Those three objects are not
ancestors of this package's publication commit (the checked PR is still open),
so they are recorded here rather than in `SOURCES.json`, whose rows must be
ancestors.

## What is reproduced, and how

`verify.py` is a separate implementation. It imports, executes and copies no
predecessor code. The published numbers are embedded as asserted constants; the
prefix walk, the simplicity/restoration/universality predicates, both collision
excess routes, the enumeration and the classification are written here.

Every number in the published table is reproduced **exactly**, on the first run,
by a different enumerator:

| `n` | `L` | simple closed | universal | substituted budget | false prunes | firing weights |
|---:|---:|---:|---:|---:|---:|---|
| 3 | 6 | 4 | 4 | 3 | 0 | — |
| 3 | 8 | 2 | 2 | 9 | 0 | — |
| 4 | 8 | 29 | 22 | 5 | 44 | 1, 2 |
| 4 | 10 | 110 | 110 | 13 | 190 | 1, 2 |
| 5 | 10 | 358 | 0 | 5 | 0 | — |
| 5 | 12 | 3695 | 828 | 15 | 2856 | 1, 2, 3 |
| 6 | 12 | 6525 | 0 | −1 | 0 | — |
| 6 | 14 | 123704 | 0 | 11 | 0 | — |
| 7 | 14 | 161936 | 0 | −21 | 0 | — |

Beyond the column totals, the check also asserts equality of the **per-functional
false-prune counts** (24 masks at `(5, 12)`, 10 at `(4, 10)`, 9 at `(4, 8)`) and of
the published bit-0 column (`6`, `20`, `248` false prunes for the coordinate-bit-0
functional). The reported `01021323` fixture is reconstructed from the word: the
nine prefix states `0,1,3,2,6,4,12,8,0`, the Hamming-weight split `(4,4)` with
excess `0`, the bit-0 split `(6,2)` with excess `8`, the substituted budget `5`
and the corrected budget `9`.

## New coverage: three further domains

The published table jumps from `(4, 10)` to `(5, 10)` and stops at `L = 14` for
`n = 6, 7`. This package classifies three further domains:

| `n` | `L` | simple closed | universal | substituted budget | false prunes | firing functionals | sound functionals |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 10 | 0 | 0 | 17 | 0 | 0 of 7 | 7 of 7 |
| **4** | **12** | **314** | **314** | **23** | **150** | **13 of 15** | **2 of 15** |
| **5** | **14** | **33922** | **24787** | **27** | **56686** | **25 of 31** | **6 of 31** |

Two measured statements follow.

1. **At `(5, 14)` the substitution falsely prunes for exactly the 25 functionals
   of Hamming weight 1, 2 and 3, and for none of weight 4 or 5.** This is the
   domain the published package names for exactly this test. Its own `(5, 12)`
   reading carried one exception (mask `11010`, weight 3, did not fire); at
   `(5, 14)` there is no exception at all, so the weight threshold `n - 1` with
   "every weight `<= n - 2` fires" is clean there. That is evidence about the
   heuristic, not a proof of it: nothing here bounds the threshold for general
   `(n, L)`.
2. **The `(4, L)` firing set grows with `L` and is monotone on the measured
   range.** `(4, 8)` fires for 9 of 15 functionals, `(4, 10)` for 10, `(4, 12)`
   for 13: at `(4, 12)` three of the four weight-3 functionals fire (`1011`,
   `1101`, `1110`), and only `0111` (weight 3) and `1111` (weight 4) stay sound.
   Compared with `(4, 10)`, where every weight-3 and weight-4 functional is
   sound, the unsound set is strictly larger at the longer length. So the old
   question "is bit 0 special?" is answered with an even wider unsound class at
   this length, and the fix cannot be a per-weight threshold that is independent
   of `L`.

`(3, 10)` has no simple closed word at all: `q_0..q_9` would be ten distinct
states of `F2^3`, which has eight. It is recorded as an empty domain rather than
dropped, so the enumeration's domain check is exercised on a degenerate case.

## Controls, all run on every invocation

- **Fixture.** The published word's prefix states, splits, excesses and both
  budgets are recomputed and asserted, including the identity
  `C(s,2) + C(t,2) - (2^(n-1) - 1) = base + d^2`.
- **Two excess routes.** The collision excess is computed both as a difference
  multiplicity sum and as a direct support-size difference, and the two must
  agree for every universal word and every nonzero functional of every domain.
- **Budget sensitivity.** Shifting the substituted budget by `-2, -1, +1, +2`
  must leave every non-firing domain at zero and must move the count on each of
  the three firing domains. The check therefore depends on the budget's exact
  value, not only on class sizes.
- **Second enumeration route.** On six domains the census is also produced by an
  unconstrained walk (no first-occurrence ordering) whose leaves are canonicalised
  afterwards; the resulting word sets must be equal. This is the check that would
  catch a pruning error in the primary enumerator.
- **Predicates on every enumerated word.** Every emitted word is asserted
  restored and simple; universality is recomputed as `|S + S| = 2^n`.

## What this does not establish

- It is a **finite certificate on ten bounded `(n, L)` domains**, not a theorem
  about the weight threshold, and not a census of the seven-label regime. The
  `(7, 18)` and `(7, 20)` domains that would change a maintained decision are
  not entered.
- It does not re-derive the *necessity* of the exact budget `base + d^2`; that
  implication is inherited from the checked package and from PR2973's `MATH.md`.
  What is checked here is the classification and the counts built on it.
- No `f(7)` value, no pruning repair, no source change, no κ and no supplier is
  claimed. A false prune in this model does not by itself invalidate any reported
  final bound.
- Independent human review and formal proof-kernel acceptance are unclaimed.

## Reproduce

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/f7-functional-independent-check/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B research/f7-functional-independent-check/test_verify.py
```

`verify.py --write` regenerates `RESULT.json`, which is the exact finite receipt.
Standard library only, no Git objects, no network. Runtime is about 30 s on the
recording host; `(5, 14)` alone is a few seconds.

## Credit

The classification question, the model, the nine published domains and the nine
pinned numbers are Nick Petalas's, in
[`research/f7-bit0-functional-classification`](../f7-bit0-functional-classification/README.md)
— including its named open question about `(5, 14)`, which this package answers
for the universal-word domain. Nicholas Stone wrote the word-census correction
(#2973) and its `MATH.md`; James Reed wrote the bit-0 small-domain audit (#3096);
Ross Richardson supplied the PR943 singleton prefix-walk model. This package's
re-implementation, the three added domains and the controls are by Nick Petalas,
produced with AI assistance. Apache-2.0.

## Open next questions

- **Is the firing set monotone in `L` for fixed `n`?** Measured on `(4, 8) <
  (4, 10) < (4, 12)` and `(5, 12) < (5, 14)`, but not proved, and `(5, 10)` has no
  universal word to compare against.
- **Can the weight `>= n - 1` soundness be proved rather than measured?** The
  published alternation lemma explains why only the all-ones functional is
  *justified* by the substitution; it does not explain why high-weight functionals
  do not fire.
- **The `(6, 16)` domain.** `(6, 14)` has 123,704 simple closed words and no
  universal word; the next even length is the first that could change that, and
  it is outside this package's budget.
