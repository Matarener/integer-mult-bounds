# Dense P112 queries keep the actual-reader floor

For two literal PR3370 indicators in groups of sizes m_A,m_B, any finite list
of dense queries q_i=x_i a+y_i b with both coefficients nonzero, realizing
aa^T+bb^T, costs at least 2 max(m_A,m_B) under the actual complete-plane
rectangular source-to-reader Gram tariff. Coefficient fields, query counts,
direction counts, repetitions and readers are unrestricted. Readers may cancel
outside the target. Zero queries may be omitted.

[PROOF.md](PROOF.md) proves the all-field statement. Every target port needs
at least two active dense-query readers. Each reader's binary Gram rank pays
for the complete target-group planes it touches. Summing separately for each
group proves the bound. Two queries attain it for the two halves of one group
over every field with more than two elements. Attainment for different groups
is unclaimed. No such realization exists over F2.

This closes the dense case with arbitrarily many directions left open by PR3429.
That predecessor covers at most three directions, including axes. PR3383 bounds
query self-Gram costs for whole-K spanning lists. It does not bound arbitrary
actual-reader costs; the proof gives the precise comparison and the replay
checks a literal self-cost 8 versus actual-cost 2 example. That one term is not a
factorization or a cheaper construction. No pending predecessor code or theorem
is required by this proof.

Disjoint dense pair replacements cannot lower the literal total 224. This is a
scoped obstruction, with no native execution bill, supplier admission, improved
kappa or selected-frontier change.

## Reproduce

Canonical main 6f100d4bb5083f8c35d96fd95a539811c62f245c, priority revision 6.
Python 3.12 or later, standard library only. From the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p112-dense-query-reader-floor
```

Standalone replay needs neither Git nor network access:

```sh
python3 -I -O -Werror -B research/p112-dense-query-reader-floor/verify.py
python3 -I -O -Werror -B research/p112-dense-query-reader-floor/independent.py
python3 -I -O -Werror -B research/p112-dense-query-reader-floor/test_controls.py
```

Use an existing external TMPDIR for private control copies. Verification writes
no package files. Explicit `verify.py --write` regenerates [RESULT.json](RESULT.json).
The primary and separate elimination implementations check all 496 indicator
pairs and all 80,240 target-reader support subsets. The primary checks 96 exact
rational realizations with 2,4,7 directions, including outside cancellation,
and 16 same-group attaining witnesses. Its 21,504 coefficient checks imply every
entry of each 112-by-112 operator, because a,b are independent. The separate
checker tests 118,285 finite-field coefficient tuples over F2,F3,F5,F7 and 4,854
axis deliveries. Five behavioral test groups include four optimized CLI
corruptions, query-boundary failures, repeat splitting and attaining witnesses.
Universal coverage follows from the proof, not extrapolation from finite tests.

[SOURCES.json](SOURCES.json) pins the live selected labels and unchanged retained
PR3370 certificate, which is included as [RETAINED-RANK32.json](RETAINED-RANK32.json).
Bibliographic predecessor heads and roles are separate from replay inputs.
[VALIDATION.md](VALIDATION.md) records bounds and verification limits.

## Open next questions

A list mixing axis queries and at least four nonaxis directions escapes this
note and PR3429's direction restriction. Start with one exact lower-tariff pair
factorization and its actual readers before pricing native execution. External
query dimensions, changed matrices and changed reader contracts remain open.
[TASK.json](TASK.json) records this handoff and stops further construction work.
Acquisition, coefficient execution, dirty restoration, frames, hosting, stock,
precision, all-size/compiler and both supplier/outer-transfer obligations remain
separate. Independent human and formal proof-kernel review are unclaimed.

## Credit

Tekalign's PR3370 supplies the retained partition. Nick Petalas' PR3429 supplies
the longer-list handoff; PR3398 distinguishes actual-reader and query self-costs.
PR3383 supplies the separate self-Gram spanning-list theorem. Credit remains
with Philippe Van Velzen, PR3345, Matarener/Mark/PR3335, ctoth, ywz65, Sagar
Thakrar, Cinna Davis, Adam Gall, Jeremy Diviney and the retained E8/P112/native,
compiler and supplier lineage. Prepared by Nick Petalas. Apache-2.0.
