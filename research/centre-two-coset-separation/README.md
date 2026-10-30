# Two translated centre blocks have exactly two hidden directions

For every pair of distinct left cosets of PR3828's 4080-owner subgroup,
the full scalar common-observation kernel is exactly the two known constant
triple directions, one per block. Pairing blocks creates no additional
hidden direction or improvement in information-compression density.

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: **scoped algebraic proof with finite corroboration**. This settles
the two-coset case of Open next question 1 in Clear1nsight's
[PR3828](https://github.com/CrocSwap/integer-mult-bounds/pull/3828).
The exact extra-linear-observation minimum on both full blocks is
`104*8160-2 = 848638`. For any subblock A of their union, the minimum is
`104|A|-j`, where j counts the complete cosets retained in A.

[PROOF.md](PROOF.md) proves the result for every relative translation,
without assuming the subgroup is normal. At a later output, each block
contributes a singleton port or the distinguished triple. Two triple
contributions cannot meet. Distinct singleton columns cannot cancel each
other; a singleton also cannot cancel a vector in the triple plane. All
other ports vanish, leaving the inherited connected triple equations on
each block separately.

The new source check proves that exactly ports `{0,6,85}` lie in that plane.
The single-block coset classification and order, reader rank and pairwise
column independence are cited predecessor premises. Their certificates are
not reverified. The theorem concerns the historical calls-0/4 scalar model,
not an automatically applicable replacement for the selected P104 word.

## Reproduce

From the repository root, CPython 3.12 and its standard library suffice.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/centre-two-coset-separation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/centre-two-coset-separation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/centre-two-coset-separation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/centre-two-coset-separation --check-source-history
```

Any CPython 3.12 executable can replace the local interpreter path.
Expected markers are `PASS_CENTRE_TWO_COSET_SEPARATION`,
`PASS_REGISTERED_RESEARCH_PACKAGE`, and `PASS_RESEARCH_COMMIT_BYTES`.
The direct check writes only stdout. Optional `--receipt /absolute/new/path`
writes a fresh receipt outside the package, binding every package file by
SHA256. No receipt is handwritten or committed.

Exact source-column elimination checks 109 outside-plane columns. A new
small S3 times C2 model checks all six two-coset pairs and all 64 subblocks
of one pair, using literal matrices and kernel witnesses. Four controls
show why column separation and retaining all later outputs are necessary.
The proof supplies the universal result; these finite checks corroborate it.

## Scope and credit

The historical source order gives 8160 owners and a derived observation
minimum of 848638. The large source matrix is not replayed. Source-bound
metadata orientation passed on canonical main
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8. The selected
conditional kappa is `0.003125804` and is unchanged.

Credit Chris R / Clear1nsight PR3828 for the question and full one-block
classification, Ross Richardson PR3797 for the parallel one-block proof
and observation interface, Matarener PR3656 for the subgroup and witness,
Sagar Thakrar PR3291 for the nonparallel-column premises, and Ross
Richardson PR3071 for the reader/model extraction convention. Retain David
Charbonneau PR3147, Sudarsh Chaturvedi PR3168, ywz65, Aaron Wang and the
selected native/geometry/compiler lineage credited by these packages.
No predecessor credit or frozen file is changed.

No physical collector, recursive tariff, native implementation, improved
kappa or complete multiplication theorem is supplied. All five selected
framework assumptions remain. No Lean, Docker, selected cold replay or
independent human/formal-kernel review is claimed.

## Open next questions

Can three distinct left cosets have extra mixed kernel directions? At one
output, three singleton columns can be dependent, so the two-coset proof
ends there. First derive the actual outgoing incidences of one explicit
three-coset block and its coefficient compatibility. A useful physical
extension still needs source access, dirty restoration and a complete
paid/productive invoice; a scalar dimension is not a saved recursive call.

## Implementation constraints

Build the Lever supplies the source-plane checker and exact small-model
elimination. Prove It Works requires literal matrix kernels and controls
that break the stated hypotheses. No predecessor verifier is imported.

Power of Ten review: no recursion, dynamic execution or subprocesses;
source prefix loops have exactly 10851 events times eight rows, and source
rank tests have eight rows and at most three columns. Small-model systems
have at most 72 rows and 30 columns. All functions are under 60 lines.
The source archive is hash-authenticated and bounded before decompression;
it contains no executable dependency. Receipts refuse existing destinations.
Explicit checks remain active under optimized Python.

Rule 3 deviation: Python integers, Fraction and JSON/tar libraries allocate
dynamically. This is a bounded reference verifier, not a fixed-allocation
runtime. Bounds are eight MB for the authenticated archive, eight MB for
the decoded word, 704 live covector entries per row and 80-by-30 maximum
elimination storage. Runtime/library internal allocation is not instrumented.
The exact archive hash fixes decompression input before library allocation.
Warning-strict normal/optimized execution and AST parsing provide diagnostics;
no additional type checker or linter was run.
