# Non-Fano five-query reader floor

For every field of characteristic other than two and every finite even
binary-orthonormal partition, a five-query realization of two disjoint
alternating-half indicators whose seven rays have the non-Fano rank pattern
has actual complete-plane reader tariff at least m_A+m_B. Both actual factors
may have external directions. [The proof](PROOF.md) covers arbitrary port
values and readers, rather than a bounded coefficient search.

PR3489's whole-matroid characteristic-two obstruction remains correct.
Three explicit GF4 configurations preserve only the source-zero and
reader-span implications for two marked targets. This closes that exceptional
five-ray subquestion. It does not prove a general five-term theorem or improve
kappa. It supplies no native program or complete supplier.

The exact finite lemma checks all 21 marked pairs and 2,688 candidate
implications, including 288 source and 672 reader premises. Twenty-one literal
P112 fixtures have factor ranks (3,4). Both operators, both supports and the
actual rectangular tariffs pass. A separate GF16/determinant implementation
checks four original characteristics and the committed sparse literal arrays.
See [RESULT.json](RESULT.json), [FIXTURES.json](FIXTURES.json) and
[validation](VALIDATION.md). Fixture costs are not global search minima.

## Reproduce

Only the Python standard library is needed. From the repository root:

```sh
python3 -I -O -Werror -B research/p112-nonfano-reader-floor/verify.py
python3 -I -O -Werror -B research/p112-nonfano-reader-floor/independent.py
python3 -I -O -Werror -B research/p112-nonfano-reader-floor/test_controls.py
python3 -B scripts/research_package.py --package research/p112-nonfano-reader-floor
python3 -B scripts/check_research_commit.py --package research/p112-nonfano-reader-floor --check-source-history
```

Use an external private TMPDIR for the registered runner and controls. The
registered runner requires Python3.12. Scientific commands support isolated
and optimized mode; repository helper scripts use ordinary import mode.
The package includes the unchanged partition and comparison proof. The data
recipes are the one declared external input. Exact sources and credit are in
[SOURCES.json](SOURCES.json) and [COMPARISON.json](COMPARISON.json).

## Open next questions

Can a five-term pair with another seven-point rank pattern beat the literal
bill, or does a two-marked-target transfer cover it? This would decide whether
the general four-term theorem extends. First name one remaining rank pattern
and test the two source/reader implications, rather than requiring an entire
matroid representation. Classification of the other seven-point rank-three
patterns and a complete five-term theorem have not been supplied here.

An actual cheaper literal factorization remains the useful prerequisite for
native synthesis under a changed contract. No further construction round or
supplier expansion is justified by this scoped negative result.

## Credit

Nick Petalas. Apache-2.0. Credit Tekalign/PR3370 for the retained P112 partition;
Philippe Van Velzen/PR3345 for the expanded identity; PR3398, PR3414,
CubeJerry/PR3459, PR3463, PR3472, PR3475, PR3489 and PR3491 for the related actual-reader and
query-dictionary questions. Retain ctoth, Matarener/Mark, ywz65, Cinna Davis,
Adam Gall, Jeremy Diviney, Sagar Thakrar and the P112/E8/native/compiler/supplier
lineage credited by the frozen sources. PR3491's regular dictionaries and the
concurrent whole-representability criterion concern different hypotheses.
Independent human and formal proof-kernel review are unclaimed.
