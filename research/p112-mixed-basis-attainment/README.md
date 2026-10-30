# Floor attainment for different orthonormal block bases

This package closes PR3579's different-basis attainment handoff for the fixed
VVV residual queries. Groups may use different full Gram-I bases in each
orthogonal binary block, and cells may cross blocks. Over every coefficient
field of characteristic different from two, arbitrary ambient readers attain

    n_1+3n_2+3n_3

exactly when a pinned cell graph has an independent negative-cell set satisfying
one weighted count equation per triply shared block. [PROOF.md](PROOF.md) states
the contract and proves both directions, including explicit attaining readers.
The criterion uses binary pairings and integer counts after graph construction.
No general efficient decision algorithm is claimed.

The same proof shows MMM always attains `2n_1+3n_2+3n_3` in this broader geometry.
The original three-term bill is `n_1+2n_2+3n_3`. These are support tariffs, with no
cheaper physical decoder, new supplier, kappa gain or selected-frontier change.

A five-cell matched example keeps dimensions and cell membership fixed while
changing one common four-dimensional basis. The coordinate case attains 15;
the changed basis cannot attain that floor. Exact finite replay measures minima
15 and 17, and MMM minimum 18 in both. This separates basis compatibility from
dimension/count data.

## Evidence and reproduction

[FIXTURES.json](FIXTURES.json) and [RESULT.json](RESULT.json) contain 35 bounded
cases, including twelve matched mixed/coordinate pairs, dimensions four through
six, two-group blocks, crossing cells and the explicit five-cell example.
The column-span checker compares the graph/count criterion with every VVV
assignment, and checks that unpinned components can be zeroed. The separate
checker constructs actual scalar factors and rectangular binary Gram matrices.
Only their byte/geometry input boundary is shared; their scientific calculations
are separate. Both compare all four charges, complete ordered stream hashes,
histograms, minima and first attaining witnesses.

From any directory containing this exported package, with CPython3.12:

```sh
python3.12 -I -O -Werror -B research/p112-mixed-basis-attainment/verify.py
python3.12 -I -O -Werror -B research/p112-mixed-basis-attainment/independent.py
python3.12 -I -O -Werror -B research/p112-mixed-basis-attainment/test_controls.py
```

The commands resolve inputs beside their scripts and need no Git or network.
Set `TMPDIR` to an existing private directory for control copies. The registered
repository replay and source-history check are:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/p112-mixed-basis-attainment
python3.12 -Werror -B scripts/check_research_commit.py --package research/p112-mixed-basis-attainment --check-source-history
```

[VALIDATION.md](VALIDATION.md) states exact coverage, controls and limitations.
The written proof supplies all-size quantifiers; finite fixtures corroborate
implementations and examples. Independent human and formal proof-kernel review
are unclaimed. Physical acquisition, coefficients, frames, dirty restoration,
hosting, precision, stock, compiler/all-size admission, full suppliers/consumers
and outer transfer remain open. Different nonreducing spans, partial bases,
characteristic two and arbitrary queries are outside this theorem.

## Open next questions

Does graph/count feasibility admit a useful efficient algorithm, or a hardness
classification, with its three-group orthogonal-basis restrictions? Start with
one triply shared block and explicit full Gram-I transition matrices. No such
complexity result is proved here.

Can the rank-floor method handle one actual nonreducing block or partial basis?
Start with an exact rectangular rank inequality or counterexample for a pinned
literal target. The full-basis projection and nondegeneracy arguments used here
would need replacement. Neither question authorizes a downstream physical
construction campaign without its full cost ledger.

## Credit and source closure

Credit retains Nick Petalas/PR3579/3569/3560/3549/3538, Philippe Van Velzen and
Arham Tahir's expanded-identity method, Tekalign/PR3370 and the retained
P112/E8/native/compiler lineage. COMPARISONS retains exact predecessor proof
bytes with origin commit, path, Git blob and SHA256 solely as handoff context.
Every used mathematical statement is proved locally, and no predecessor runtime
or foreign Git object is needed for scientific replay. SOURCES.json pins only
catalogue and selected-record provenance. New work is Apache-2.0.
