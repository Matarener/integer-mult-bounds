# Nine-product S3 convolution needs a characteristic-three denominator

**Scoped proof; no new kappa.** A bilinear formula for b independent,
unrestricted S3 convolutions needs at least **10b scalar products** whenever
its coefficient ring admits a map to a characteristic-three field. This
includes dyadic, dyadic-Gaussian and eighth-root dyadic coefficients. Joint
formulas may mix all blocks; the lower bound still applies.

Consequently every rational formula using fewer than 10b products has a
coefficient whose reduced denominator is divisible by three. Cinna Davis's
[nine-product construction (#2224)](https://github.com/CrocSwap/integer-mult-bounds/pull/2224)
therefore cannot keep its product count through a denominator-free or purely
dyadic bilinear replacement. Its rational identity is cited, not audited.
This answers one branch of its exact-division implementation question.

The [proof](PROOF.md) computes a four-dimensional nilpotent ideal in K[S3],
with quotient K x K, in characteristic three. The classical
[Alder--Strassen bound](https://doi.org/10.1016/0304-3975(81)90070-0)
then gives 2(6b)-2b=10b. The new contribution is this source-specific
denominator obstruction and its implication for jointly batched S3 blocks.
The lower-bound theorem, modular specialization and group-algebra structure
are classical; no mathematical priority for those ingredients is claimed.

## Evidence and reproduction

The standard-library verifier constructs the new modular certificate and
enumerates every one of the 729 elements of F3[S3]. It finds 324 units,
checks radical dimensions (4,2,0), all 36 basis products, all 64 radical
triple products, and eight rejection controls. It imports no predecessor
verifier and does not replay the rational nine-product formula or its ceiling.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/s3-three-local-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/s3-three-local-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/s3-three-local-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/s3-three-local-obstruction --check-source-history
```

Direct replay prints `PASS_S3_THREE_LOCAL_OBSTRUCTION` in its JSON output;
the registered runner prints `PASS_REGISTERED_RESEARCH_PACKAGE`. An optional
`--receipt /absolute/path/outside/the/checkout.json` writes generated evidence
bound to all six package files by SHA256. No receipt is hand-written.

The written proof applies for every b and every characteristic-three field.
The finite checks corroborate its algebraic certificate; they do not prove
the cited general tensor-rank theorem or constitute proof-kernel verification.

## Scope and sources

The formula model is a sum of products of a linear form in the left inputs
and a linear form in the right inputs, followed by arbitrary linear output
maps. All blocks may share these forms and products. Linear scratch and
arbitrary dirty inputs cannot remove the lower bound: set auxiliary inputs
and initial accumulated outputs to zero and retain the required data outputs.
Invertible input/output basis changes over the coefficient ring are included.

Ten is a lower bound; no ten-product dyadic construction is claimed. Exact
division by three on restricted intermediate values, nonlinear algorithms,
approximation and arbitrary complex coefficients remain outside this model.
No provider placement, complete signed bill, precision/tape schedule, supplier
admission, selected-frontier change or complete multiplication theorem is claimed.

The base is canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`,
priority revision 8. The selected source-binding baseline passed before work.
The current coframe card is changed to the arithmetic boundary of #2224;
this is a scoped mechanism obstruction, not a current supplier optimization.
See [TASK.json](TASK.json) and [SOURCES.json](SOURCES.json) for the exact card,
scope and source pins. The advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228557)
records the question. The live overlap search covered 393 open PRs and 5,638
Discussion records; sparse local-note coverage was incomplete. Whole-main
README searches and separate merged-PR searches supplied additional coverage.
No novelty claim rests on a lack of search matches.

Credit Cinna Davis / 1337isnot1337's #2224 at
`b767ef166b6871c6965dce9b463432c665130024` for the rational S3 mechanism,
its division question and retained Strassen/representation-theory lineage.
Nick Petalas's older [#3336](https://github.com/CrocSwap/integer-mult-bounds/pull/3336)
excludes a literal affine-data placement; it is a separate obstruction and
is not extended or rechecked here. Credit Alder, Strassen and Bläser for
the cited algebra-complexity results. Predecessor files and credits remain intact.

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. New work is Apache-2.0.

## Verification bounds

The verifier has no recursion, dynamic code execution or mutable shared state.
Matrices have at most 36 rows and exactly six columns; the largest
enumeration has 729 elements. Each function is under 60 physical lines.
Checks use explicit exceptions and survive optimization. Receipt I/O failures
propagate. Managed Python allocation is the rule-3 deviation: small fixed
dimensions bound live data, while Python integers and temporary collections
allocate during replay. No Python static analyzer is configured; registered
commands enable warning errors. There are no callback control dispatchers.

## Open next questions

1. What is the exact bilinear rank over Z[1/2] of this six-coordinate tensor?
   Start by constructing a ten-product formula or proving a stronger floor
   in characteristic three. The present argument does not prove attainability.
2. Can a known-exact division-by-three implementation retain nine rational
   products within a fully charged physical invoice? Start with #2224's
   numerator schedule and its intermediate divisibility invariant. Actual
   source placement, quotient cost, storage, precision and restoration are open.

Structured questions are in TASK.json. Neither follow-on is reserved here.
