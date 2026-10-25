# Only the all-ones mask alternates on every step

**Partial. No new exponent.**

A linear functional `l_v` is the mod-2 dot product with a mask `v`. One walk
step replaces the state `q` by `q XOR e_w`. Because

```text
(v AND (q XOR e_w)) XOR (v AND q) = v AND e_w,
```

the functional changes by exactly bit `w` of the mask. The checker confirms
that isolation for every mask, state and label through width 6.

If the mask is all ones, every label flips the value. Starting from zero, the
value after `k` steps is `k mod 2`, for every walk. If some bit is zero, the
step on that label leaves the value unchanged. The all-ones mask is therefore
the only one that alternates on every walk.

## What was executed

The checker tests the step identity. It does not classify words.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the alternation lemma in PR 3699,
head `13db47d8d31603c1391572009e1eb7a22675a219`.

## Scope and evidence

Original card: `census-pruning-audit`, priority revision 6, refined to this
lemma. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/alternation-lemma/verify.py
python3.12 -B research/alternation-lemma/test_verify.py
python3.12 -B scripts/research_package.py --package research/alternation-lemma
```

## Open next questions

This lemma is the comparison. Classifying words would leave it.

## Credit

petalas published the alternation lemma.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
