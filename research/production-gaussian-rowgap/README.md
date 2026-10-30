# Stronger conditioning for the physical Gaussian production matrix

This scoped mathematical proof gives the unchanged original-coordinate rounded
Gaussian matrix H, and every nonempty principal restriction, the bounds

    row gap > u^2/(2(p+u^2)),
    ||H^-1||_infinity < 2 + 2p/u^2.

The production guards imply u*theta>u^2/(4p). Retaining this squared
concentration factor improves the historical inverse estimate 8p. On the
source's p=16384, u=32 metadata example, the new upper bound is 34 instead
of 131072. These are analytic bounds, not measured inverse norms or runtime.
No new kappa is claimed, and the selected frontier is unchanged.

[PROOF.md](PROOF.md) proves the implication from the existing bilateral
row majorant of PR1673 and the retained-band perturbation theorem in
[PR6099](https://github.com/CrocSwap/integer-mult-bounds/pull/6099), at
38ce77a4925c18eb66f94634b1b11a1242af8a87. The latter is conditional on
PR6085's scalar enclosure theorem. Those results are cited premises; their
re-verification is not this contribution. The new theorem answers the
row-gap part of PR6099's Open next questions with a stronger bound.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/production-gaussian-rowgap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/production-gaussian-rowgap --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B research/production-gaussian-rowgap/verify.py
```

The registered normal and optimized checks each enumerate 139850 exact rational
parameter fixtures and 2976 nearest-index geometry pairs, including 12 tie rows
and 120 wrapped pairs. They also check 1024 rounding-budget induction fixtures,
five invalid parameter cases and one exact counterexample after removing the
similarity guard. The parameter fixtures test a relaxation of the production
domain, not 139850 complete production plans. The counterexample refutes the
row-gap estimate in that relaxation, not the inverse estimate separately.

The universal claim rests on the written proof, not these finite checks.
The verifier authenticates five main-branch source files, imports no predecessor
engine and uses no pending PR Git objects. A Git-free source export containing
those declared inputs can run the direct command with any Python 3.12 binary.
[SOURCES.json](SOURCES.json) records exact source identities; [TASK.json](TASK.json)
records the card, changed scope and mathematical dependencies.

## Limitations

The result is conditional on the cited kernel and coefficient estimates. No
independent human or formal proof-kernel review is claimed. Full production
coefficient pages, infinite-periodized ideal comparison, column and spectral
norms, LU growth, physical setup and tape costs, tensor/CRT composition and
the complete multiplication theorem remain outside this result. No selected
cold replay, Lean or Docker run is needed or performed for this scoped theorem.

## Open next questions

Can the retained u^2 factor reduce a complete caller's precision or locality
budget? Start with one explicit inverse-error term and preserve its separate
column, Schur and tape obligations. This package does not reprice that caller.

Can the retained-band matrix be compared to the intended infinite-periodized
ideal with its stated tail bound? Specify that full ideal and its omitted
offsets across the physical seam. Deletion monotonicity suffices here; that
identification and the tail estimate remain separate work from PR6099.

## Credit

This contribution was produced by Nick Petalas. New work is Apache-2.0.
Jose Manuel / jmbarrancoml supplied the physical producer, production guards
and old-H matrix in PR3851. JoyboyBrian supplied the retained-band theorem and
open question in PR6099, building on the scalar theorem in PR6085. The
bilateral row majorant is inherited from the PR1673 capped phase-cell work
and its RaD/hipotures Gaussian sources. The logarithmic-width and rounding
lineage, Chafik Boukhalfa's Gaussian caller work and all source-specific
predecessor credit remain theirs. The new contribution is the stronger
production-parameter gap and inverse implication.
