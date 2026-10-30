# Sharp spectral conditioning for signed rank transport

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof, with exact finite corroboration.** In
Jeremy Diviney's [PR #836](https://github.com/CrocSwap/integer-mult-bounds/pull/836)
formal register model over a finite group, a paid row call of price c has

    |Delta Phi| <= c (K+1/K)/2,

where K is the spectral condition number of the faithful regular prefix.
The constant is sharp for every K>=1, already on two roles over C2.
The new step applies the classical Kantorovich inequality to the actual
coefficient row and inverse column, then constructs a legal equality family.

For the complete rank-nine endpoint with eight unit-price calls, at least
one paid prefix must consequently have

    K >= (9+sqrt(17))/8 > 1.64,

strengthening the predecessor's stated necessary 9/8 spectral bound.
The complete weighted price condition is in [PROOF.md](PROOF.md).
Neither local equality nor this necessary condition constructs the cheaper
endpoint. No new kappa, physical supplier or selected-frontier change follows.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sharp-rank-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sharp-rank-conditioning
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sharp-rank-conditioning --check-source-history
```

Other machines can substitute their CPython 3.12 executable. Both normal and
optimized commands are registered. The direct check prints
`PASS_SHARP_RANK_CONDITIONING` in a generated JSON receipt binding every
package file and the cited source proof by SHA256. It writes no files and
works in the official Git-free export with its declared proof input.
No receipt is handwritten.

The finite check covers all 80 distinct rational parameters v=p/q with
1<=q<=p<=16. Each equality witness has its full four-dimensional regular
inverse checked by rational elimination and both two-dimensional Fourier
blocks checked separately. A complete orthogonal eigenbasis certifies its
exact spectral condition number. Literal row permutation and inversion
give the new increment, including its negative starting potential. The
unitary boundary v=1 is also checked separately.

Another 64 rational matrices in dimensions one through eight have prescribed
singular values and independent rational inverses. All 288 row/inverse-column
inequalities pass; eight scalar-dimension rows attain equality. Nine rejection
controls cover invalid bounds, parameters, capacity, singularity and replacing
the inverse by the transpose. Four semantic checks separate a false unitary
bound, a squared-condition substitution, the old threshold and the strict
rational comparison. These are finite real-rational fixtures; the complex,
all-dimension theorem rests on the written spectral argument.

## Scope and credit

Credit Jeremy Diviney #836 for the signed rank potential, exact transport,
endpoint law and nonunitary search question; Nir Ailon for the retained
forward/inverse-potential context; eumemic #288, Swapnil Jain and the retained
register/frame lineage; littleBro #680/#705 for the predecessor's finite
Clifford context. The Kantorovich inequality and spectral theorem are
classical. The contribution is this sharp application and its attaining
formal family, without a claim of general literature priority.

The predecessor proof is cited and source-bound; no predecessor executable,
example or count is replayed. The original `bit-new-register-model` card is
explicitly changed to this complex conditioning side result in
[TASK.json](TASK.json). Base main is
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19220081)
records the scope before substantial work. Published PRs, recent account
submissions, claims and distinctive main/merged searches were inspected.
The cached card scan reported 324 open PRs and 5,489 Discussion records,
with complete remote pagination, but only 224 of 8,136 main note paths
materialized locally. Searches do not prove novelty or cover unpublished work.

The theorem requires finite groups and the full invertible independent-input
boundary. Infinite groups, clean restricted inputs, nonfaithful concrete
representations and a complete eight-call construction are outside scope.
Physical costs, native realization, compiler, stock, precision/tape, analytic
recovery and the multiplication theorem remain unrun obligations. No selected
cold replay, Lean, Docker, independent human or formal proof-kernel review is
claimed. All five selected framework assumptions retain their status.

## Open next questions

Can a complete rank-nine endpoint with eight unit calls attain this necessary
conditioning floor? Start with one fixed formal word and track exact endpoint
equations together with every signed gain. The local equality family does not
supply the full endpoint; this is the main blocker to an attainment claim.
The structured question and its relevance are in TASK.json.

## Implementation bounds

The verifier has no recursion, subprocesses, network, dynamic code evaluation
or shared mutable state. Numerical loops have fixed finite domains: dimensions
at most eight, 80 witness parameters, 64 matrices, at most 24 rotations per
matrix and nine invalid-input cases. All functions fit within 60 physical
lines. Explicit exceptions keep every invariant active under optimization.
Six package files and one proof input are each capped at 256 KiB.

Power of Ten rule 3 deviation: CPython and Fraction allocate during the bounded
offline calculation. Live matrices have at most 8-by-8 entries; rational
rotations have denominators 5 or 13 and at most 24 factors, singular values
are integers 1..4, and witness numerators/denominators are at most 16.
These fixed capacities bound live storage and coefficient heights; runtime
allocation itself is not instrumented. A native implementation would need
fixed storage before claiming that property. Rule 9 deviation: eight local
zero-argument callbacks encode the bounded invalid-input controls; production
mathematical paths use direct calls. Rule 10 diagnostics are warning-strict
normal/optimized replay and AST inspection; no separate static type analyzer
is configured or run for this isolated package.
