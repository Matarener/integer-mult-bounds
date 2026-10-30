# A sharp boundary loss in uniform transfer-metric certificates

This scoped written proof with exact finite corroboration was produced by Nick Petalas.
For the standard prefix-product encoder on any finite group G of order q,
every complete physical endpoint is unitary. Its true operator norm is one.
The least uniform operator-norm bound obtainable from Ali Romman's
[PR5451](https://github.com/CrocSwap/integer-mult-bounds/pull/5451) fixed positive
transfer-metric criterion is exactly sqrt(q). Every fixed positive blocking
length and every invertible complex virtual basis change retains that loss.

The new [proof](PROOF.md) characterizes all feasible metrics. The local blocked
operator is a permutation, so its contraction inequality forces c=1 and exact
metric invariance. Physical output separation then forces P=t I. The two
boundary inequalities have product at least q, with an attaining certificate.
This is a sharp limit of that sufficient criterion, not a counterexample to
its theorem. No new kappa or selected-frontier change is claimed.

For the prefix-XOR example in zxv's
[PR5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441), the loss is
sqrt(2). Searching more positive metrics or blocking more columns cannot make
that certificate sharp. A boundary-aware method or a changed representation
is a separate question.

## Evidence and reproduction

The independent local implementation imports no predecessor executable. It
checks complete endpoint entries by literal one-column contraction, complete
blocked local permutations, exact ranks of the metric-invariance equations,
explicit negative quadratic-form witnesses for non-scalar real and complex
metrics, and rational gauge certificates. Six groups include noncommutative S3.
The universal statement rests on the written proof, not extrapolation from
these finite groups or block lengths. Generated stdout receipts bind all seven
package files and both exact source-document inputs by SHA256.

The fixed replay enumerates 21 blocked tables and 787 literal blocked paths,
85,873 metric-commutator entries, 17,792 complete endpoint entries, 45 negative
metric witnesses and 12 gauge certificates. Its 63 controls comprise seven
invalid group/block cases, a changed terminal boundary, an imaginary
off-diagonal metric and 54 strict boundary/rate underclaim witnesses.

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/prefix-encoder-metric-loss/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/prefix-encoder-metric-loss/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/prefix-encoder-metric-loss
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/prefix-encoder-metric-loss --check-source-history
```

Other machines may substitute their CPython 3.12 interpreter. The verifier
prints `PASS_PREFIX_ENCODER_METRIC_LOSS` in its JSON receipt and writes no files.
Both warning-strict modes are registered. The source-history check is a
publication integrity check, separate from the mathematics. A Git-free export
needs this package and the two inputs declared in VERIFY.json.

## Scope and credit

Ali Romman supplies the sufficient metric criterion and its stated limitations.
zxv supplies the concrete fixed-transfer contract and prefix-XOR example, with
the retained weighted-automata, matrix-product, native and phase lineage.
Trace invariance, congruence and weighted operator norms are classical. The
additional result is the sharp optimized loss and its metric rigidity under
blocking and virtual gauges. No predecessor result is audited or replayed.
Source documents, Git blobs and hashes are pinned in [SOURCES.json](SOURCES.json).
New work is Apache-2.0. Independent human and formal proof-kernel review are unclaimed.

The `formal-interface-lemma` card is explicitly changed to this certificate
obstruction. It explains a limitation of one possible route to uniform error
control, without discharging a selected framework assumption. The result
fixes this representation and certificate. Larger or different virtual
representations, position-dependent metrics and boundary-aware certificates
remain open. Physical synthesis, dirty restoration, native costs, the complete
paid invoice, compiler closure, tape/precision and exact recovery are outside
scope. No selected cold replay, native suite, Lean or Docker build was run.

## Open next questions

1. Can a boundary-aware finite certificate attain norm one for this encoder
   while still controlling small complete residuals? Start with the reachable
   boundary subspaces and retain coherent physical input sums. The obstruction
   here only applies to the single fixed positive metric criterion.
2. Does another finite transfer representation of the same endpoint remove
   the loss? Start by allowing a changed virtual dimension and explicit boundary
   maps. An invertible basis change in the present dimension is already covered.

## Verifier constraints

All functions have fewer than sixty physical lines, with structured iterative
control flow and explicit exception checks that remain active under optimization.
Groups have at most six elements; blocked local permutations have at most 216
coordinates; exact constraint elimination has at most 36 variables and 2592
distinct relations. Dense gauge matrices have at most 36 rows. Fixed fixture
loops and these caps bound the complete run. The verifier has no subprocess,
network or input-file argument. Source and package files are capped at one MB.

Power of Ten rule 3 deviation: CPython allocates managed integers, Fractions and
collections during this bounded one-shot check. The fixed domains above bound
live data; no unbounded search or external resource is retained. Both registered
modes exercise those domains. A fixed-allocation implementation would require
a different arithmetic runtime. Rule 8/9 deviation: isolated execution uses one
explicit file-based import of the package-local encoder.py. The only dynamic
target is that fixed sibling file, which is included in the receipt and committed
source. No external plugin or generated code is loaded. Reassess these controls
before adding an external frontend. Warning-strict execution and AST compilation
are the local diagnostics; no external static analyzer is claimed.
