# H6 commuting dyadic repairs need rank 816

For the H6 kernel K and its complement C=I-K, every dyadic correction B
with BK=KB and C+B invertible over Z[1/2] has rational rank at least
**816**. This is sharp: B=K makes the endpoint the identity. The stronger
conclusion is ker B contained in ker K. Polynomial corrections are included.

Ross Richardson's [PR3655](https://github.com/CrocSwap/integer-mult-bounds/pull/3655)
gives the unrestricted rank-560 dyadic completion. That result and the H6
spectrum are cited premises, not fresh audits. The new obstruction shows
that any rank-560 completion must break commutation with K. Restricting
to commuting corrections costs exactly 256 additional correction rank units.
Correction matrix rank is not a native Gaussian tariff.

This is a scoped written proof with finite exact corroboration. It supplies
no physical source word, paid supplier, new kappa or selected-frontier change.
The rank-816 attainer cancels the useful kernel response and is only an
algebraic witness to sharpness.

## Why the restriction matters

A commuting correction has an invariant kernel. If C+B is a dyadic
automorphism, then its restriction to that kernel is C and must also be a
dyadic automorphism. The nonidentity H6 characteristic factors have odd
nonunit constant terms. None can remain on that kernel. The cited spectrum
therefore forces all 816 responsive dimensions to be changed.

[PROOF.md](PROOF.md) gives the all-dimensional invariant-kernel argument and
the H6 application. It permits arbitrary mixing inside repeated eigenspaces
and does not assume B is symmetric or diagonalizable. A literal two-by-two
noncommuting correction demonstrates that the commutation hypothesis is
essential. Odd denominators and extra directions have separate controls.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/h6-commuting-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/h6-commuting-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/h6-commuting-repair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/h6-commuting-repair --check-source-history
```

Another CPython 3.12 executable may replace the local path. The last command
checks publication bytes after committing. Both registered scientific commands
print `PASS_H6_COMMUTING_REPAIR rank=816 no_new_kappa`.

The verifier enumerates all 390,625 ordered pairs of two-by-two integer
matrices with entries in {-2,-1,0,1,2}. Exactly 12,465 pairs commute, and
6,552 also have a dyadic-unit repaired determinant. Every one satisfies
the invariant-kernel rank bound; 1,856 attain that bound. It checks 36
literal dyadic conjugations of attaining abstract matrices, three altered
factor certificates, four hypothesis controls and ten invalid certificates.
These finite domains corroborate the proof; they do not establish the H6
spectral premise by enumeration.

The program needs no Git, network, predecessor executable or source import.
It emits a generated receipt bound to all six package files and writes no
files. SOURCES.json pins the historical source statements as provenance.
The registered metadata check authenticates those pins separately.

## Limits and execution bounds

The same 30,960-dimensional endpoint and the dyadic coefficient ring are
essential. Noncommuting corrections, rational coefficients with odd
denominators and stable extensions are outside the theorem. The H6 spectrum,
symmetry and unrestricted 560-row completion retain their cited status.
No dense H6 reconstruction, predecessor replay, native circuit, complete
cost/precision/tape/stock calculation or supplier admission is performed.
Independent human and formal proof-kernel review are unclaimed.

The checker has no recursion or shared mutable state. Its largest nested
enumeration has exactly 625 squared iterations. Factor certificates have at
most eight factors of degree at most two, multiplicity at most 40,000,
128-bit coefficient numerators/denominators and total dimension at most
100,000. Matrix helpers consume fixed four-entry internal tuples. Every
function is shorter than 60 lines; exceptions preserve checks under -O.
Registered invocations enable warnings as errors.

Power-of-Ten rule 3 has a managed-runtime deviation. Python allocates its
integers, fractions and collections during the bounded one-shot replay.
The matrix box contains only 625 tuples, and the other finite domains and
factor limits above bound live data. This is not a persistent service or
a fixed-allocation native implementation. No metaprogramming, callback
dispatch or mutable global registry is used.

## Open next questions

- Construct explicit noncommuting coefficients for the predecessor's named
  560-row completion. Identify the spectral components they mix, then price
  legal source frames, scalar work and dirt restoration. Those coefficients
  and a physical word remain missing.
- Consider an enlarged dirty-helper interface only after specifying all
  arbitrary inputs, required outputs and its complete paid/target invoice.
  A stable extension changes the theorem's endpoint and can leave helper
  dirt or restoration costs unpaid.

The structured questions and blockers are in [TASK.json](TASK.json).
The original decoder card is explicitly changed to this algebraic side
obstruction. Selected-baseline metadata orientation passes; it is not a
scientific replay of the selected supplier.

## Credit

This contribution was produced by Nick Petalas. Ross Richardson supplies
PR3655's H6 dyadic repair and its retained spectral premises. Credit Dominik
Scholz's PR606 geometry/factorization, DreamingOfClouds' H6/Walsh proposal
and the retained PR1830 spectral, compensation and encoder lineage.
Saturated kernels over a PID, characteristic polynomials and odd-prime
valuations are classical. The new result is their invariant-kernel use to
prove the exact commuting-repair obstruction for this fixed source.
Apache-2.0.
