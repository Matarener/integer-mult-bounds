# A census-free pair-reader floor for even orthonormal partitions

For any finite even orthonormal partition of binary labels, choose two
alternating-half indicators a,b from groups of sizes m_A,m_B. Every finite
factorization

    aa^T + bb^T = sum_i u_i q_i^T,   q_i in span_F(a,b)

costs at least **m_A+m_B** under the actual complete-plane rectangular binary
reader tariff, over every coefficient field F. Readers are arbitrary and may
cancel outside the target. Axes, repetitions, zero queries and arbitrarily
many projective directions are included. The original two terms attain the
floor. Disjoint pair replacements cannot lower whole-K total 2n for n ports.
Groups must have positive even size and binary Gram I. Planes are consecutive
pairs and halves alternate within each group. Cross-group pairings are arbitrary.

The concrete replay binds the selected 112 P112 labels and Tekalign's PR3370
partition, giving whole-K total 224. Concurrent
[PR3459](https://github.com/CrocSwap/integer-mult-bounds/pull/3459) by CubeJerry
reports the same literal P112 conclusion through submodular support layers and
a complete rank census. This contribution supplies a different proof and the
general partition theorem; the literal mixed-list result has concurrent credit.

[PROOF.md](PROOF.md) gives the universal argument. Inject each finite set of
projective query classes into the characteristic-two field F2(t), fixing the
axes. At each target port, select active classes to obtain the same coordinate
axis with new reader supports contained in the old class unions. Binary
rectangular rank cannot increase under that replacement. The retained expanded
I224 argument works over F2(t), because extending F2 preserves binary matrix
rank. No homomorphism from the original coefficient field is required.

This independently answers [PR3447](https://github.com/CrocSwap/integer-mult-bounds/pull/3447)'s
mixed-axis handoff. PR3447's stronger dense-only bound 2 max(m_A,m_B) remains
valid. [PR3429](https://github.com/CrocSwap/integer-mult-bounds/pull/3429) covers
at most three projective directions. Its four-direction binary-map obstruction
is respected: the new map takes values in an extension of F2. PR3383's query
self-cost theorem concerns a different tariff.

## Evidence and replay

The labels come from the pinned selected DATA-PHASES input. Tekalign's PR3370
certificate is retained unchanged as RETAINED-RANK32.json. SOURCES.json records
both byte and Git-blob hashes. No pending predecessor code or Git object is
needed to replay this package.

- The primary checker authenticates sources and expanded I224, then checks
  992 exact rational-to-GF64 transfers across all 496 literal pairs, including
  proportional repetitions, zero queries and outside cancellation. It checks
  8,432 grouped actual-reader tariff comparisons and 444,416 operator coordinates.
- The separate implementation uses explicit nine-coordinate labels and GF16
  logarithm arithmetic. It rejects all 256 binary images of the old abstract
  four-direction example and solves its twelve requests over GF16. It checks
  133,363 prime-field tuples, 6,074 support transfers, 1,984 rectangular rank
  comparisons and every P112 expanded-identity entry. Three non-P112 fixtures
  on 2, 8 and 6 ports add 416 expanded entries; odd/nonorthonormal controls are
  rejected. A wrong-characteristic rank example distinguishes field extension
  from a characteristic change.
- Seven actual optimized CLI corruptions reject altered input bytes, fixture,
  source blob, receipt, operator coefficients, direction collisions and a
  reducible field modulus. The restored positive and separate checks pass.

Use Python 3.12 for the registered replay, with an existing private external
TMPDIR for disposable test copies:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/p112-extension-field-reader-floor
python3 -I -O -Werror -B research/p112-extension-field-reader-floor/verify.py
python3 -I -O -Werror -B research/p112-extension-field-reader-floor/independent.py
python3 -I -O -Werror -B research/p112-extension-field-reader-floor/test_controls.py
```

RESULT.json preserves exact primary receipts. VERIFY.json registers all three
commands without dependencies. [VALIDATION.md](VALIDATION.md) records the
verification boundary and code constraints. Finite fields in the replay only
corroborate the universal written F2(t) proof.

## Limits

This is a scoped negative theorem for one additive support tariff. It supplies
no native program, improved kappa or selected-frontier change. Native source
acquisition, coefficient execution, frames, dirty restoration, ownership,
hosting, stock, precision, all-size/compiler, both supplier admissions and the
outer multiplication theorem remain separate obligations. Human and formal
proof-kernel review are unclaimed.

## Open next questions

The structured questions are recorded in TASK.json:

- Can an external query dimension give one exact pair factorization below
  m_A+m_B? Begin with explicit queries, actual readers and literal rectangular
  ranks. No lower-cost witness is supplied here.
- Can a larger jointly recoded block escape support transfer to characteristic
  two? Begin with an explicit incidence pattern and bind it to the literal
  labels. An abstract incidence obstruction alone does not give a cheaper decoder.

The session stops with this theorem. Another construction round needs a changed
hypothesis and a complete paid boundary.

## Sources and credit

Nick Petalas. Apache-2.0. Tekalign's PR3370 supplies the retained group fixture.
Philippe Van Velzen and PR3345 supply the expanded-identity tariff argument.
Nick Petalas's PR3429, PR3447, PR3398 and PR3383 supply the immediate scope
comparisons. Matarener/Mark's PR3335, ctoth, ywz65, Sagar Thakrar, Cinna Davis,
Adam Gall, Jeremy Diviney and the retained P112/E8/native/compiler/supplier
lineage keep their predecessor credit. Exact comparison heads are in PROOF.md;
frozen source bytes and original attribution are preserved.
