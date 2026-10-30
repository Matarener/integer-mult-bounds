# Dependent three-query P112 replacements keep the sharp reader floor

For the literal PR3370 fitting matrix, any dependent list of at most three
scalar queries replacing two indicator terms costs at least the original
pair under the actual complete-plane source-to-reader tariff. The new theorem
covers every coefficient field, arbitrary reader values and arbitrary finite
query lists using at most three projective directions in the two-indicator
span. Repeated directions and cancellation outside the target are included.

[PROOF.md](PROOF.md) constructs a support-dominated binary replacement. It
maps the query directions injectively to the three nonzero binary pairs,
fixes any occurring coordinate axes and solves each reader at each port using
only its original active direction classes. Binary rank subadditivity bounds
the replacement's bill by the original bill. The retained expanded-I224
argument then proves the sharp pair floor m_A + m_B.

This closes the dependent-list handoff left open by PR3414. Together with that
predecessor's independent-query written theorem, it completes the tariff floor
for every list of at most three queries. The combined statement inherits
PR3414 at exact head `7b698dc958695d0a788327ddf8866b10a59e4c37`; its separate
independent-query proof is not replayed here. Disjoint replacements of these
kinds cannot lower the literal total of 224.

The result is a scoped obstruction, with no cheaper native implementation,
supplier admission, new kappa or selected-frontier change.

## Reproduce

Canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
Python 3.12 or later, standard library only. From the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/p112-dependent-reader-floor
```

Direct replay needs neither Git history nor network access:

```sh
python3 -I -O -Werror -B research/p112-dependent-reader-floor/verify.py
python3 -I -O -Werror -B research/p112-dependent-reader-floor/independent.py
python3 -I -O -Werror -B research/p112-dependent-reader-floor/test_controls.py
```

Use an existing external `TMPDIR` for control copies. Each control removes its
own temporary copy. Ordinary replay checks the committed receipt without
rewriting it; `verify.py --write` explicitly regenerates [RESULT.json](RESULT.json).

The primary check covers 96 exact rational P112 operators and their binary
replacements, totaling 2,408,448 operator-entry checks. Cases use two or three
directions, two, three, five or seven queries, proportional repetitions, zero
queries, readers cancelling globally, coincident groups and different group sizes.
The separate implementation checks 133 projective direction sets and 23,637
coefficient tuples over F2,F3,F5,F7, reconstructs all 50,176 entries of expanded
I224 and independently recovers the literal tariff 224. Five control groups
include five actual optimized CLI corruptions and a restored positive run.
Universal coverage comes from the written proof, not extrapolation from tests.
[VALIDATION.md](VALIDATION.md) records bounds, checks and limits.

[SOURCES.json](SOURCES.json) pins the live selected labels, the unchanged retained
PR3370 certificate and the exact bibliographic predecessors. No pending source
code is imported. The retained certificate is included so mathematical replay
does not need unmerged Git objects.

## Open next questions

Four or more projective directions, external query dimensions and changed
fitting matrices remain open. A twelve-site abstract example proves that this
binary-map argument cannot handle arbitrary four-direction support data; it
is outside the literal P112 pair fixture and supplies no cheaper tariff witness.
Start any continuation with an exact lower-tariff literal factorization, then
price acquisition, coefficients, restoration, frames and the complete consumer.
[TASK.json](TASK.json) records the questions and a pause after this implication.

## Credit

Tekalign's PR3370 supplies the retained partition and rank-32 fit. Nick Petalas'
PR3414 supplies the independent-three-query theorem and dependent-list handoff;
PR3398 identifies the actual-reader tariff boundary. Philippe Van Velzen and
PR3345 supply the expanded-identity argument. Credit remains with PR3383,
PR3407, Matarener/Mark/PR3335, ctoth, ywz65, Sagar Thakrar, Cinna Davis,
Adam Gall, Jeremy Diviney and the retained E8/P112/native/compiler/supplier
lineage. Prepared by Nick Petalas. Apache-2.0. Independent human and formal
proof-kernel review are unclaimed.
