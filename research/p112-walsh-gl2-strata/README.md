# Every continuous Walsh two-total basis gauge still costs 82

Scoped computer-assisted proof, produced by Nick Petalas. Apache-2.0.

For all 3,136 ordered choices of two distinct Walsh characters on each side
of Cinna Davis's PR2042 P112 ten-term factorization, every invertible real
or rational 2-by-2 basis change `U -> UM, V -> VM^(-T)` has exactly the
pairing-rank profile `{8:8,9:2}` and total tariff 82. The power tariff is
therefore always `8*8^s + 2*9^s`. This replaces a finite five-basis search
with an exact classification of the entire continuous basis orbit.

The new proof is in [PROOF.md](PROOF.md). Every Walsh plane has exactly four
projective support-zero directions; all other real directions share one
support. The verifier checks both label spans on all 280 plane/support cases,
the eight original reader spans, and all 25,088 corrected source-column spans.
The nondegenerate binary pairing then gives every term's exact rank. No
predecessor rank receipt or verifier is replayed as evidence for this result.

This is a decoder side result, with no new kappa or selected-frontier change.
It shows that further basis searches in these fixed Walsh planes cannot lower
their invoice. Arbitrary changed planes, changed rank-two products and physical
supplier realization remain open. The historical P112 packing ceiling is not
an applicable ceiling on the current selected P104 construction.

## Reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p112-walsh-gl2-strata/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/p112-walsh-gl2-strata/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p112-walsh-gl2-strata
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p112-walsh-gl2-strata --check-source-history
```

Other machines can substitute their CPython 3.12 executable. The verifier prints
`PASS_P112_WALSH_GL2_STRATA` in JSON with the complete certificate counts,
support digest and package hashes. It writes no files. Both registered checks
have a 120-second limit. `SOURCES.json` pins the sole executable external input,
Mihir Srivastava's exact P112 geometry constructor, to canonical main
`721c03822c421b7f7fcbb2598993b947c4d88419`. Source hashes are checked before import.

Finite fixtures also check complete 112-by-112 identities under determinant
minus two and determinant one. Singular gauges, a missing total, empty support,
a missing label direction and the wrong inverse are rejected or separated by
explicit controls. The universal claim rests on the written support partition
and complete finite rank certificate, rather than these sample matrices.

## Relation to prior work

- Cinna Davis, [PR2042](https://github.com/CrocSwap/integer-mult-bounds/pull/2042),
  supplies the asymmetric Walsh family and its finite five-basis result.
  This package extends the basis domain to all GL2(R).
- DreamingOfClouds, PR717, and Mihir Srivastava, PR845 and
  `p112-single-lift/geometry.py`, supply the P112 coordinates and pairing tariff.
- Philipp / mightyOil, PR1197, poses the general coupled overlapping-lift case.
  This result closes only the specified Walsh-plane basis orbit.
- Gonzalo Mier, [PR4020](https://github.com/CrocSwap/integer-mult-bounds/pull/4020),
  uses projective support strata for arbitrary rational pair gauges on a
  different 34-channel factorization. The support-stratum method is credited;
  this package's new result concerns the two-added-total Walsh family.
- DreamingOfClouds, PR2338, establishes broader baseline decoder floors under
  its stated format. A floor of 64 does not determine the exact value 82 here.

The source files and predecessor credit remain unchanged. No claim of a new
support-stratification method or independent human review is made.

## Limitations and next decision

Source preparation, adapters, frame transport, dirty restoration, native
execution, hosting, precision, stock, uniform compilation and outer recovery
are unpriced. No full supplier replay, Lean proof or Docker run is claimed.
The result is a scoped exact exclusion, not a search failure or a complete
integer multiplication theorem. Python uses managed allocations, bounded here
by 112 geometry rows, 56 plane records, nine-bit rank workspaces and a fixed
25,088-case loop. No unbounded search, recursion or external solver is used.

## Open next questions

Can changing the rational planes and their product `UV^T`, rather than only
their bases, lower the profile? Start with one explicitly different overlapping
plane pair and its complete support arrangement. This matters because the
arbitrary rank-two branch of PR1197 remains open. A favorable example and
its physical source/frame/restoration bill are still missing. The structured
question is retained in `TASK.json`; this package stops at the classification.
