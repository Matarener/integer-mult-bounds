# Codimension-one soundness of the fixed `L/2` substitution

**Proof for double transversals, plus two finite ledgers. No new κ.**

On simple restored universal words with `n ∈ {3, 4}` and `L = 2n`, every
label-basis linear functional of Hamming weight at least `n - 1` is sound for
the substituted budget `base(n, L)`. It does not falsely prune. The argument
is in [PROOF.md](PROOF.md). The same weight pattern is not a law: at `(4, 12)`
three of the four weight-3 masks do falsely prune.

Selected conditional κ stays `0.001672660197076918`. This does not change the
frontier, does not decide `f(7)`, and does not run `survey(7, 18)`.

## Scope

Catalogue card: `census-pruning-audit` (priority revision 6). Scope status:
**refined**.

The fourteenth session slot fell on a 12-item handoff list by
`(14 - 1) mod 12 = 1`. That item is [Discussion #1166 comment
19021170](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19021170),
question 1: the `(7, 18)` / `(7, 20)` functional census. This package answers
question 2 of the same comment instead. #3699 measured that weight at least
`n - 1` does not fire on its small domains and wrote that the regularity was
not a theorem. #3733 then showed it is not a weight-threshold law.

The card's premise is unchanged in this narrower sense: the object is still
the word-census parity substitution, and the bit-0 witness `01021323` is
retained as the control that the predicate still detects a false prune.
Launching the seven-label census is a scope-change trigger on the card, so
that census stays an open question.

Base commit: `bb4bccbf42844d2801487450727c2f63e10d1d0f`. Provenance pins are in
[SOURCES.json](SOURCES.json). No live inputs. The predecessor enumerators are
not imported.

## Result

The walk is `q_0 = 0`, `q_{i+1} = q_i XOR e_{w_i}`. A word is simple when the
`L` prefix states are distinct, restored when every label occurs a positive
even number of times, and universal when those states sum to `F_2^n`. False
pruning means `base < a + b ≤ base + d²`, with `d = (s - t) / 2` and

```
base(n, L) = 2 C(L/2, 2) - (2^{n-1} - 1).
```

For `L = 2n` every label occurs twice. The all-ones functional alternates, so
`d = 0`. A weight-`(n - 1)` functional has exactly two preserving steps, hence
`|s - t| ≤ 2`. The unbalanced classes have sizes `n + 1` and `n - 1`. Their
excess is exactly 3. That equals `base(3, 6) = 3` and is strictly below
`base(4, 8) = 5`. Equality is not a false prune.

The weight pattern stops as soon as a label may occur four times. An
independent enumeration of the 314 restricted-growth universal words at
`(4, 12)` gives:

| mask | omitted label | false prunes |
|---:|---:|---:|
| `0111` | 3 | 0 |
| `1011` | 2 | 4 |
| `1101` | 1 | 4 |
| `1110` | 0 | 4 |

Two further statements are finite ledgers, not theorems. Mask `1010` has
excess at most 3 on all 22 words at `(4, 8)`, and `3 ≤ base = 5`. Mask
`11010` has excess at most 14 on all 828 words at `(5, 12)`, and
`14 ≤ base = 15`.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 scripts/research_package.py --package research/f7-codim-one-substitution-soundness --check-only
python3.12 scripts/research_package.py --package research/f7-codim-one-substitution-soundness
```

Direct commands:

```sh
python3 -B research/f7-codim-one-substitution-soundness/verify.py
python3 -B research/f7-codim-one-substitution-soundness/test_verify.py
```

The first prints `PASS_F7_CODIM_ONE_SUBSTITUTION_SOUNDNESS` and a JSON receipt.
The second prints `PASS_F7_CODIM_ONE_SUBSTITUTION_TESTS groups=4`. A local run
finished in well under a second. That runtime is not a portability claim.

The restricted-growth enumerator is a cross-check. The inequality for
`n ≤ 4` and `L = 2n` is proved for every word, not only for the normal form.
Rows with no universal word would not support a prune conclusion; both theorem
domains are nonempty. Nothing here was run under a proof assistant.

## Open next questions

1. **Which functionals fire at `(7, 18)` and `(7, 20)`?** Comment 19021170
   names this as the census that can change a maintained exclusion. The
   enumerator in #3699 has `survey(7, 18)` wired and not run. This package
   does not run it. Blocker: seven-label state count and a separate resource
   budget.

2. **Why are masks `1010` at `(4, 8)` and `11010` at `(5, 12)` the only
   weight-`(n - 2)` exceptions?** The second ledger is tight by one unit
   (excess 14 against base 15). A first step is to list the words that meet
   excess 14 and compare them with a firing neighbor such as mask `10101`.
   Blocker: no structural classification; the ledgers are enumerations.

3. **For which lengths above `2n` does weight at least `n - 1` stay sound?**
   `(4, 12)` is already a counterexample to a general law. `(4, 10)` and the
   weight-at-least-4 masks at `(5, 12)` were measured sound by #3699 and #3733
   and are not proved here. The obstruction is that four preserving steps can
   change the class sizes by 4, and `n + 1 > 2^{n-2}` only for `n ≤ 4`, so the
   pair-sum closure used above stops there.

## Credit

The singleton prefix walk is the PR943 model used by #2542, #2634 and #2691.
Nicholas Stone wrote the word-census correction and its `MATH.md` (#2973).
The false-prune predicate and the measured weight table, including the two
exceptions and the statement that they were not a theorem, are from #3699
(`research/f7-bit0-functional-classification`). #3733
(`research/f7-functional-independent-check`) first recorded that `(4, 12)`
breaks a weight threshold; the counts in this package were recomputed and not
imported. James Reed's bit-0 audit is #3096. Douglas Colkitt supplied the
selected frontier this package does not change.

Prepared by unpaidmoon. Substantial Cursor Grok assistance for selection,
proof writing, implementation and execution. No independent human or
formal-kernel review is claimed. New work is Apache-2.0.
