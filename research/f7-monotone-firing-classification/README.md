# The fixed `L/2` firing set is not monotone in length

**Negative answer for monotonicity, with a proof at `n = 4` and a finite census at `n = 5`. No new κ.** Selected conditional κ stays `0.001672660197076918`.

## Scope and evidence

Card `census-pruning-audit`, scope **refined**. Discussion #1166 comment 19022438 asks whether the firing set of the fixed `L/2` substitution is monotone in `L` for fixed `n`, and names `(4, 14)` and `(5, 16)` as the first classification. Handoff 2 of that comment, high-weight soundness on double transversals, is already #4148. This package does not run the `(7, 18)` / `(7, 20)` census from comment 19021170.

The argument is in [PROOF.md](PROOF.md). `verify.py` checks the flat-excess maxima, reproduces the published per-mask tables, classifies the two new domains, and compares the firing sets.

On `F_2^4`, every level set is an affine 3-flat. Every 6-point, 7-point and 8-point subset has collision excess at most 8, 14 and 21. A 14-point set therefore has excess at most `21 + 8 = 29`, and `base(4, 14) = 35`. The full space has excess `42 < base(4, 16) = 49`. No functional fires on any 14-point or 16-point set.

The canonical walk census shows this silence is not an empty domain:

| `n` | `L` | closed | universal | false prunes | firing masks |
|---:|---:|---:|---:|---:|---:|
| 4 | 8 | 29 | 22 | 44 | 9 |
| 4 | 10 | 110 | 110 | 190 | 10 |
| 4 | 12 | 314 | 314 | 150 | 13 |
| 4 | 14 | 392 | 392 | 0 | 0 |
| 4 | 16 | 112 | 112 | 0 | 0 |
| 5 | 12 | 3695 | 828 | 2856 | 24 |
| 5 | 14 | 33922 | 24787 | 56686 | 25 |
| 5 | 16 | 267890 | 263140 | 447912 | 25 |

For `n = 4` the firing sets at lengths 8, 10 and 12 are strictly nested, and the sets at 14 and 16 are empty. Monotonicity fails. The canonical word `010201031213` is one of the 16 length-12 words on which mask `1` fires (excess 24, split `(8, 4)`, `d = 2`, base 23). The same mask fires on no 14-point set.

For `n = 5` the firing set is still monotone through length 16. Length 12 omits only the weight-3 mask `11010` from the 25 masks of weight at most 3. Lengths 14 and 16 fire on exactly those 25 masks. Mask `11010` fires 170 times at length 14 and 1728 times at length 16. No weight-4 or weight-5 mask fires.

The `(4, 8)`, `(4, 10)` and `(5, 12)` per-mask counts match #3699. The `(4, 12)` and `(5, 14)` counts match #3733. Both excess routes agree on every classified word, and an unconstrained enumerator reproduces the canonical `n = 4` forms.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/f7-monotone-firing-classification --check-only
python3.12 -B scripts/research_package.py --package research/f7-monotone-firing-classification
```

Direct commands:

```sh
python3 -B research/f7-monotone-firing-classification/verify.py
python3 -B research/f7-monotone-firing-classification/test_verify.py
```

The first prints `PASS_F7_MONOTONE_FIRING_CLASSIFICATION` and the firing-set sizes `9,10,13,0,0` and `24,25,25`. The second prints `PASS_F7_MONOTONE_FIRING_TESTS groups=3`. A local CPython 3.12 run of `verify.py` finished in about one minute. That runtime is not a portability claim.

Not run: `survey(7, 18)`, `survey(7, 20)`, length 18 at `n = 5`, Lean, Docker, and the selected cold replay.

## Open next questions

1. **For `n = 5`, which even length first makes every functional sound?** The 16-point level sets have not yet capped a length-16 word. A first step is `(5, 18)`, with the same canonical enumerator and the flat-excess cap as the stopping test. Blocker: the length-16 census is already 267,890 closed words, and length 18 was outside this session.

2. **Which functionals fire at `(7, 18)` and `(7, 20)`?** Comment 19021170 names that census as the one that can change a maintained exclusion. Blocker: the seven-label state count, and the card's separate-budget rule. This package does not run it.

3. **Does any `n > 5` repeat the `n = 4` collapse one step after the firing set has filled every low-weight mask?** The mechanism here is the quadratic base overtaking a dimension-capped excess. Blocker: no general threshold is proved, and `(6, 16)` already has 2,262,380 canonical closed words before universality is tested.

## Credit

The prefix walk is the PR943 model used by #2542, #2634 and #2691. Nicholas Stone wrote the word-census correction (#2973). Nick Petalas classified the functionals in #3699 and extended them through `(5, 14)` in #3733; the monotone question is handoff 1 of discussion comment 19022438. #4148 proved the separate double-transversal soundness statement and left this classification open. James Reed's bit-0 audit is #3096. Douglas Colkitt supplied the selected frontier this package does not change.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0. No independent human or formal-kernel review is claimed.
