# A sharp quadratic-union reduction for the P104 plane question

**Scoped written proof with finite exact corroboration.** Two affine
codimension-two live sets in the full 120-line E8 quadratic model have union
at most **68**. Equality has one exact shape: disjoint sets of sizes 36 and
32, with a shared constraint line carrying inconsistent affine values.
Every other pair has union at most 66; two 36-point sets attain 66.
[PROOF.md](PROOF.md) gives a Gauss-sum proof and explicit attaining sets.

This is a partial step toward Matarener's first open question in
[PR6218](https://github.com/CrocSwap/integer-mult-bounds/pull/6218), at head
`159352d273bd7b9f92c55cee3a9ac9b955de9b86`. The source reports a finite
P104 union bound 66. The new theorem reduces its geometric proof to one
configuration: show that every exceptional full-E8 68-point union contains
at least two of the sixteen removed lines. The full-E8 fixture proves that
puncture information is necessary for this route. That last assertion and
compatible-plane disjointness remain open here. No predecessor census,
word, bound or verifier was audited or replayed.

An older P112 two-flat census already reports 68 in
[PR3253](https://github.com/CrocSwap/integer-mult-bounds/pull/3253).
The new contribution is the full-E8 proof, equality classification and
P104 reduction. The numerical value 68 on P112 is not claimed again.
[PR3269](https://github.com/CrocSwap/integer-mult-bounds/pull/3269) already
uses signed Gauss sums for individual smaller affine supports; it supplies
methodological context rather than this union theorem.

## Exact evidence

The new standard-library checker enumerates 288,072 consistent and 1,368
inconsistent relative quadratic configurations on spans of dimension at
most four. This is a finite corroboration of the proof, not the source's
P104 pair census. It checks the equality shape, parity, and the two-36
branch maxima 36, 52 and 66 at span dimensions two, three and four.

A direct bitset enumeration independently checks the Fourier slice formula
on every one of the 43,180 affine plane systems in the full quadratic model.
Their cardinalities 24, 28, 32 and 36 occur respectively 5,355, 16,320,
16,065 and 5,440 times. Literal eight-bit attaining sets have sizes
(36,32), disjoint union 68, and (36,36), intersection 6, union 66.
Seven mathematical/domain rejection controls remain active with optimization.
An opposite-sign quadratic form has an explicit 72-point union, so the
plus-type hypothesis cannot be dropped.
The emitted JSON receipt binds all package-file hashes and the interpreter.
No receipt is handwritten or stored in the checkout.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -Werror -B research/p104-quadratic-union-reduction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -Werror -B research/p104-quadratic-union-reduction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-quadratic-union-reduction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-quadratic-union-reduction --check-source-history
```

Replace the interpreter prefix on another host. The expected status is
`PASS_P104_QUADRATIC_UNION_REDUCTION`. Each registered command is bounded
at 60 seconds; the first local direct replay took less than one second.
The exact published timings belong in the PR's evidence. Direct replay also
works in a Git-free export with the two declared inputs at their relative
paths. Source pins and historical card/selected-record provenance are in
[SOURCES.json](SOURCES.json); [TASK.json](TASK.json) records the scope change.

## Limits and code bounds

The result does not prove the source's puncture inequality, compatibility
lemma or decoder floor. It does not supply a word, restoration/ownership
contract, native implementation, complete signed invoice, supplier admission,
new kappa or complete multiplication theorem. The five selected assumptions
remain. No predecessor scientific replay, Lean, Docker or full selected replay
is needed or claimed. Independent human and formal proof-kernel review are
unclaimed.

The checker has no recursion, network or subprocess. Its loops are bounded
by dimensions 2..4 for relative forms, at most 64 polar forms, 16 refinements,
35 planes per four-space, and fixed 256/512-point ambient fixtures. The
largest list has 10,795 planes. Each function is below 60 physical lines.
Power-of-Ten rule 3 deviation: CPython allocates integers and collections
during execution. Fixed, non-configurable domains bound live data and the
process releases it on exit. A variable-dimension CLI would require explicit
capacity limits. Warning-strict execution and source compilation are the
available diagnostics; no shared configuration is changed.

## Open next questions

1. Prove the puncture inequality for the single 68-point equality class.
   This would replace the source's finite 66-union bound by a hand argument.
   Start from its symplectic/isotropic shared-line normal form and the two
   removed orthogonal frames. Their relative position is the missing input.
2. After that counting step, prove compatible-plane disjointness with the
   source's hyperplane and at-most-four non-orthogonal exceptions. The
   present theorem does not track which uncovered ports are orthogonal.
   Start with the root-normal case singled out by PR6218.

## Credit

This contribution was produced by Nick Petalas. Credit Matarener for PR6218's
open proof question, B-form reduction, P104 compatibility setting and the
E8/2E8 description, and the retained carrier-code E8 model. DreamingOfClouds
retains the decoder census and P104 word/geometry credit; Ali Romman and the
retained P104/native/caller/compiler contributors retain their work. Credit
Nick Petalas's older PR3253 P112 census and PR3269 signed-support argument
at their stated scopes. Quadratic Fourier inversion, Gauss sums, radicals,
hyperbolic bases and finite quadratic-space classification are classical.
Global literature priority is unclaimed. Apache-2.0.
