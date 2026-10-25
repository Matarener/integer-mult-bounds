# Sharper shifted Gaussian conditioning

I prove an explicit conditioning bound for the normalized shifted Gaussian
kernel
\(k(u)=e^{-\gamma u^2+2\gamma su}\), with \(\gamma>0\) and \(|s|<1/2\).
For its Fourier symbol \(\Phi\), write \(m=\Phi(\pi)\). I obtain

\[
m\ge(1-2|s|)\sqrt{\pi/\gamma}\,e^{-\pi^2/(4\gamma)},\qquad
\lim_{N\to\infty}\|T_N(k)^{-1}\|_2
=\sup_{N\ge1}\|T_N(k)^{-1}\|_2=1/m.
\]

I include an explicit convergence bound using alternating vectors.
Using the predecessor's exact finite q-LDU identities, I also prove
\[
\|T_N(s)^{-1}\|_2\le N/P_{N-1}^3\le N e^{\pi^2/(4\gamma)}
\quad (|s|\le1/2),\qquad
P_j=\prod_{r=1}^j(1-e^{-2\gamma r}).
\]
This second estimate includes both half-shift endpoints. I use the actual
block cap instead of losing a factor inverse to the shift gap.
For the actual broad Gaussian caller in PR4100, I account for its
\(\alpha^{-1}\) normalization, positive diagonal gauges and ceiling in
\(\alpha\), and derive \(\|K^{-1}\|_2\le p^{1+\xi+o(1)}\) for
\(N\le B\le p^\xi\), fixed \(0<\xi<1\). This is below \(p^2\) eventually.
The author used a looser \(p^6\) allowance for those capped interiors.

I retain the original product/phase proof and its exact minimum-at-\(\pi\)
corollary. My shifted floor improves the source's simplified \(1/3\)-exponent
floor for \(0<\gamma\le1\). I prove the floor for all positive \(\gamma\),
but do not claim dominance over the old floor at large \(\gamma\).
For small \(\gamma\), I also prove \(L\le m\le8L\), uniformly in the shift,
where \(L\) denotes the displayed floor.

## Scope and source

I start from canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`,
priority revision 7, and pin the retained PR4100 source
`337d04939571a637aeab54a0f58f54fde811663a`.
[SOURCES.json](SOURCES.json) binds the actual source bytes.
[PROOF.md](PROOF.md) contains the universal arguments and caller substitution.
[Discussion4191](https://github.com/CrocSwap/integer-mult-bounds/discussions/4191)
records the claim, live overlap and publication handoff.

I restrict the caller consequence to centered, constant-phase, unit-gap
capped interiors. The source assigns holes and phase/period cuts to the
boundary. I leave the broad Schur complement as an applied factor.
For a raw perturbation of norm \(\varepsilon_p\), the caller must establish
\(\varepsilon_pQ_p^{\rm cap}\le1/2\) before using the rounded inverse bound
\(2Q_p^{\rm cap}\).

The sharp constant \(1/m\) concerns exact normalized sections at fixed
\(\gamma,s\) as \(N\) grows without a cap. Each finite section has a strictly
smaller inverse norm. I make no optimality claim for capped gauged blocks
or selected-frontier change.

## Verification

I use CPython 3.12 and its standard library. The declared two commands have
180-second limits each. From the repository root:

```sh
python3.12 -B scripts/research_package.py \
  --package research/shifted-gaussian-conditioning
```

The verifier checks these finite consequences:

- I enclose 25 minima using both the direct alternating series and the
  positive Jacobi product, with explicit omitted-tail bounds. I compare
  the new floor, the old floor where improvement applies, and a separate
  Poisson leading-term enclosure. Scales range from \(1/16\) to \(8\);
  one shift lies \(2^{-40}\) below \(1/2\).
- I charge the complete \(\ell^1\) truncation and coefficient-rounding error
  for half-width 64 and a 192-bit fractional grid. For 125 matrices of
  sizes 1, 2, 4, 8 and 16, I reconstruct exact rational LDL factorizations
  of the rounded Hermitian part minus half the certified margin.
- I check 150 frequency-circle points and alternating-vector inverse
  bounds. I record analytic size thresholds for reaching \(8/9\) of the
  limiting inverse constant, and mark those large matrices as unexecuted.
- I check 60 exact rational finite-cap cases, including both half shifts,
  against direct Gaussian matrices. I reconstruct the inherited q-LDU
  identities, multiply each shifted inverse on both sides, and check the
  new entry-decay and row/column bounds. I reject reversed shift conjugation.
- I reject altered source bytes, zero scales and an indefinite matrix.
  I reject half shifts for positive symbol-margin admission while admitting
  them in the finite-cap theorem. I check exact cancellation at the half shift, loss
  of accretivity outside the domain, the missing-normalization failure,
  an unpaid truncation tail and JSON scalar-type corruption.

[RESULT.json](RESULT.json) carries the complete typed receipt.
I use directed Decimal arithmetic with explicit transcendental widening,
rational Machin/Taylor bounds and exact rational LDL reconstruction.
I document the arithmetic trust boundary in PROOF.md. These finite
certificates support the formulas and implementation; reviewers must
assess the written universal proof separately.

## Overlap and attribution

I searched 5,236 local records and inspected the retained shifted product
proof, unshifted Poisson estimate, fine-prime audit and accretive-scale
correction. Live checks covered 100 recent PRs and 60/691 hub comments,
then 60 PRs and 40/692 comments before the claim. I found no equivalent
shifted floor or sharp finite-section inverse statement in that coverage.
Before publication I refreshed unchanged canonical main and inspected a
further 100 PR records and 45 hub comments. ToikY's new PR4192 concerns
sequential compiler arena scans, a separate obligation.
During final review I followed the finite-cap question to the retained
`HOLES-AND-Q-LDU.md` and `BILATERAL-LDU.md`. The author already supplies
the exact factors and a different narrow-cell estimate. I derive the
closed-shift finite-cap bound as a corollary and extend this same package.
I did not exhaust older comments, arbitrary diffs, unpublished work or
the mathematical literature.

I credit Jeremy Kothe/IdeaOuter and the PR1758 contributors for the shifted
product/phase argument; Vlado Vojdanovski/PR1673 for the unshifted Poisson
estimate, exact q-LDU identities and capped framework; and Chafik Boukhalfa/PR1786 for the
fine-prime extension. Cinna Davis supplied the later caller I audit.
I checked the original PR1758/1786 credits instead of repeating the later
abbreviated attribution. I preserve the frozen notices and input bytes.
I also retain the classical Jacobi, Poisson, Toeplitz and Gaussian
literature attribution in PROOF.md.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including source-analysis agents. I count those agents within the author
process. I claim no independent human or formal-kernel acceptance.
Apache-2.0.

## Open next questions

In [TASK.json](TASK.json) I specify two remaining questions with first steps
and blockers: sharpness of the finite-cap estimate, and integration into
the complete Gaussian circuit and error ledger.
Reviewers must retain the coefficient-generation, circuit-prefix and
physical execution obligations when using this conditioning estimate.
