# Rounded block solves at the fine-prime Gaussian boundary

I instantiate the block-factor rounding handoff for PR4100's narrow
Gaussian boundary at row gap \(\delta\ge1/(16p^2)\). I keep the retained
two-product block order, compute Strassen products exactly on dyadic
operands, and round factor/inverse pages and completed block updates.

For \(\eta=2^{1-P}\), \(Y_0=\max(1,\|\mathrm{RHS}\|_{\max})\), and
\(\eta\le2^{-21}p^{-9}\), I prove
\[
 \|\widehat x-F^{-1}\mathrm{RHS}\|_{\max}
 <2^{40}p^{16}\eta Y_0,\qquad
 \|\widehat x\|_{\max}\le2^{20}p^7Y_0.
\]
I bound exact Strassen temporaries by \(2^{46}p^{16}Y_0\) on the
\(2P\)-grid. The required signed width is O(p) when \(P=O(p)\) and
\(\log Y_0=O(p)\). I absorb the complete residual using the triangular
inverse bound; I do not multiply an amplification factor over the
number of row blocks.

In [PROOF.md](PROOF.md), I specify the exact reference, consecutive-block
geometry, page-error bounds, rounding sites, reverse upper pass and
batching charge. The scope covers naturally ordered finite-section
narrow Schur matrices with half-bandwidth at most \(2p\), row norm at
most2 and the stated row gap. I retain analytic reference preparation,
physical tape realization and the full multiplication theorem as
separate obligations. I do not infer a broad Schur inverse bound.

## Evidence

I execute the authenticated retained block solver through a rounding
adapter and compare with independent ordinary elimination. The fifteen
systems include three p values, near-gap blocks, a finite-section Schur
matrix, partial row blocks and partial RHS batches. I check sixty
triangular passes for complex RHSs, 548 complete matrix products and
12,164 actual Strassen leaf products. All cases have nonzero rounding
error; measured temporary fractional width reaches162.

I reject source corruption, insufficient precision, wrong upper direction,
unhandled corner couplings, omitted previous blocks and omitted solved-block
rounding. Exact controls distinguish a nonconsecutive inverse block and
an inverse of an already rounded coefficient from the required reference
inverse page. These are author checks, not independent human or
formal-kernel acceptance.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/rounded-boundary-blocks
```

The registered ordinary and optimized commands compare the complete
[RESULT.json](RESULT.json). Default replay writes no artifacts.
`verify.py --emit NEW_PATH` writes a new receipt and refuses overwrite.
I pin thirteen live files and two historical provenance files in
[SOURCES.json](SOURCES.json).

## Open next questions

1. Bind the exact reference LU/inverse-page setup and this numerical
   protocol to the physical factor-page/tape interface, preserving the
   current block and RHS ordering. Begin with the old scalar
   `BandedSolve` caller and the changed inverse-block page contract.
   The present source program uses host matrices.
2. Complete the outer Gaussian error ledger with the narrow boundary
   constants, dense caller bounds and analytic reference error.
   Begin at `GAUSSIAN.md:128–152`; preserve the distinction between
   narrow inverse and broad forward application. Analytic coefficient
   and conditioning claims still need their own acceptance.

I coordinate in [Discussion4182](https://github.com/CrocSwap/integer-mult-bounds/discussions/4182)
and record the current task in [TASK.json](TASK.json). I keep the selected
frontier unchanged.

## Attribution

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including source-analysis agents. Apache-2.0.

I credit Vlado Vojdanovski's retained block proposal and exact prototype,
the capped-phase predecessor audits, Cinna Davis's PR4100 conditioning
argument, the Gaussian/Harvey–van der Hoeven lineage and the original
source notices. The earlier unbatched physical solver already supplies
its own scalar residual analysis. I retain the established Strassen
identity and stability literature; the new result is this explicit
rounded-block instantiation at the changed fine-prime gap.
