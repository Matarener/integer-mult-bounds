# Independent audit of the cross-cell rounding and inverse bounds in PR #4462

**Result: the two conditional lemmas hold.** This answers the explicit request
for a different contributor to check [#4462](https://github.com/CrocSwap/integer-mult-bounds/pull/4462)
at `89548dc186c9c90d459085b6d1be4834977705b9`. It supplies an independent written
derivation of the inverse approximation and locality steps, an explicit combined
within/across-cell rounding budget, and a separately written rational matrix
verifier with six failure controls. **No new kappa or selected-frontier change.**

The original paper claims, ideal Gaussian gaps and production page generator
remain hypotheses. This is a conditional matrix proof with exact finite checks,
not a formal-kernel proof or an independent human review. It does not certify the
full multiplication theorem or the Schur/tensor extensions.

## 1. Contract and relation to the caller

Let integer `p >= 2`, `0 <= W <= p-1`, and let `H` be a finite square complex
matrix with diagonal exactly one and half-bandwidth `W`. Both the absolute row
and column off-sums of an ideal nonnegative matrix `N` are at most `1-g`, where

```
g = 1/(8p^2),  delta = 2^(2-32760p),  eta = 2^(-32768p).
```

Within each cell assume `|H_ij| <= N_ij/(1-delta)`. Across cells either use
`0 <= H_ij <= N_ij` (Lemma A), or permit an absolute rounding error `e` from
`N_ij` (the mixed application of Lemma B). These are off-diagonal conditions;
the diagonal stays exactly one, including at cuts. Principal sections inherit
the hypotheses. The locality argument also applies on a cycle using the
inherited graph distance, provided the section really agrees with the full
matrix on all retained entries.

The three live input notes in [SOURCES.json](SOURCES.json) establish the source
context, not these hypotheses independently: LOG-A specifies downward entries
across cells and a unit diagonal; FINE-PRIME uses rounded entries and states an
eventual row/column perturbation `poly(p) 2^(-(C-o(1))p)`; the downstream report
sets `P=32768p`. The selected #4359 review continues to retain analytic/native
assumptions. The #4100 claim is not the selected theorem.

Exact snapshots of #4462's README and verifier, including their original credit,
are in `reviewed/`; [REVIEWED.json](REVIEWED.json) records their original commit,
Git blobs and SHA256 hashes. The new verifier authenticates but never imports or
executes them. Its rational matrix implementation was written separately after
reading the audited claim and code; this is not a blind replication.

## 2. Downward transfer and the mixed rounding ledger

For any fixed row or column split the ideal off-sum as `T_in + T_out <= 1-g`.
Under Lemma A,

```
off(H) <= T_in/(1-delta) + T_out <= (1-g)/(1-delta).
```

The second inequality follows by subtracting `T_in+T_out` after multiplying by
`1-delta`: the difference is `-delta*T_out <= 0`. Thus its gap is at least
`(g-delta)/(1-delta)`, giving the same ceiling as #4462:

```
U = (1-delta)/(g-delta) = 8p^2 (D-4)/(D-32p^2),  D=2^(32760p).
```

Here `||H^-1||_1, ||H^-1||_infinity, ||H^-1||_2 <= U`; the bound on `U` need
not be strict when the premises are non-strict. The stronger comparison with
`10p^2` below is strict.

The per-entry statement needs its reference specified. If **every** entry is
within `e=1/(64p^4)` of `N`, there are at most `2W` errors in each off-sum, so
the excess is at most `2(p-1)e < 1/(32p^3)`. If instead that error bound only
applies **across cells**, the within-cell ratio error must also be charged:

```
off(H) <= (1-g) + delta*T_in/(1-delta) + 2W e
       <= (1-g) + 2delta + 2(p-1)e.
```

The constants still suffice. For every integer `p>=2`, `p<=2^(p-1)` (induction
from `p=1`, since `p+1<=2p`). Consequently

```
128p^4 <= 2^(4p+3) < 2^(32760p-2),
delta < 1/(128p^4) < 1/2,
2delta + 2(p-1)e < (2p-1)/(64p^4) < 1/(32p^3).
```

This supplies the combined budget that #4462 leaves implicit when moving
between its two readings. It also handles a raw oracle with `|z-N_ij|<2eta`:
`64p^4 <= 2^(4p+2) < 2^(32768p-1)` implies `2eta<e`, for all `p>=2`.
Negative rounded outputs cause no problem: `|z|<=N_ij+|z-N_ij|`.
No source change or actual page-generator implementation is asserted here.

## 3. Robust inverse and spectral bounds

Assume directly, as in Lemma B, that **both** absolute row and column off-sums
of `H` are at most `1-g+rho`, with `rho<=1/(32p^3)`. Put

```
q = g - 1/(32p^3) = (4p-1)/(32p^3).
```

Writing `H=I+E`, both induced norms of `E` are at most `1-q<1`. The Neumann
series gives the two inverse norm bounds `<=1/q`; the inequality
`||A||_2 <= sqrt(||A||_1 ||A||_infinity)` gives the same 2-norm bound. Since

```
q >= 7/(64p^2) > 1/(10p^2),
100 < 2^7 <= p^7,   10 < 2^4 <= p^4,
```

we obtain `||H^-1||_2<10p^2<p^6` and `||H^-1||_2^2<p^11`.
Also `||H||_1, ||H||_infinity <= 2-q<2`, hence `||H||_2<2`.
Thus every eigenvalue of `H*H` is strictly between `p^-11` and `p^11`:
the lower bound follows from the inverse norm, and the upper bound follows
from `4<p^11`. This proves the spectral endpoint 11 and normalizer 6.

The downward route satisfies this same robust premise: its excess is at most
`delta*(1-g)/(1-delta) <= 2delta < 1/(32p^3)`. This also justifies positivity
of `g-delta` and all inverses used in section 2.

## 4. Polynomial approximation and the exact locality condition

Set `c=p^-11`, `L=p^24`, and

```
Q = I-c H*H,       P_L = c sum_{j=0}^{L-1} Q^j H*.
```

By section 3 the Hermitian matrix `Q` has eigenvalues strictly between zero
and `1-p^-22`. The finite geometric-series identity gives, in this order,

```
H^-1 - P_L = Q^L H^-1.
```

For a nonnormal `H`, moving `Q^L` to the right of `H^-1` is not valid in general.
Using `log(1-x)<-x` for `0<x<1` (integrate `1/(1-t)>1` from zero to `x`),

```
||H^-1-P_L||_2 < (1-p^-22)^(p^24) ||H^-1||_2
               < p^6 exp(-p^2).
```

This is an all-p argument, not a numerical evaluation of an enormous matrix
power. Since each `H` or `H*` step changes index by at most `W`, a monomial in
`Q^j H*` has at most `2j+1` such steps. Thus `P_L` has half-bandwidth at most
`(2L-1)W`. A row at distance **greater than** `(2L-1)W` from omitted section
indices has identical restricted and full polynomial rows: every path in the
matrix product stays in the section. This does not assert equality of the
two exact inverse rows. Their difference can subsequently be bounded using
both approximation errors.

The predecessor's more conservative agreement distance `(2L+1)W` also fits
under `p^26`. Indeed

```
p^26 - (2p^24+1)(p-1) = p^24((p-1)^2+1) - p + 1 > 0
```

for `p>=2`, since `p^24>=p` and the bracket is at least two. This verifies
length 24 and both bandwidth/agreement exponents 26. It does not transfer
them to a Schur complement or certify a core/halo geometry.

## 5. Discriminating exact fixtures

The new standard-library verifier uses rational Gauss-Jordan elimination and
matrix multiplication, not the predecessor's scalar-only replay. It checks:

- scalar identities and conservative bounds at every integer `p=2..512`, with
  the universal justification in sections 2-4;
- 24 four-by-four mixed-cell matrices: every contiguous partition and three
  signed cross-cell error patterns, including nonnormal cases, using the
  deliberately larger delta envelope `1/(128p^4)` at `p=3`;
- all 16 sign vectors per mixed matrix, both exact inverse identities, and
  both induced inverse norms;
- exact nonnormal polynomial residuals at lengths 1-4, an interior row
  agreement fixture, and failure of that agreement near a cut;
- six controls: omit row control, omit column control, increase excess beyond
  the spectral tolerance, omit the unit diagonal, reverse the residual order,
  or claim near-face polynomial agreement.

The one-sided controls are substantive. At `p=2`, let `r=249/256` and take the
six-by-six unit-diagonal matrix with `H[0,1]=-r` and `H[i,i-1]=-r` for
`i=1..5`. It has bandwidth one and every row off-sum equals the allowed `r`,
but one column off-sum is `2r`. Its inverse on `e_0` is

```
x_i = r^i/(1-r^2), i=0..5,
||x||_2^2 = 6342978758591946527831281/3517374640846117273600 > 1600.
```

Therefore `||H^-1||_2>40=10p^2`: the row hypothesis alone is insufficient.
Transposition gives the column-only counterexample. These are generic contract
controls, not examples satisfying the ideal Gaussian hypotheses of Lemma A.

The reported `p=2` threshold is also corroborated. A symmetric two-by-two
matrix with diagonal one and off-diagonal `-(31/32+rho)` has the eigenvector
`(1,1)` with eigenvalue `1/32-rho`. For `0<=rho<1/32`, spectral endpoint 11
holds exactly when

```
rho < 1/32 - 2^(-11/2).
```

Exact rational squaring puts this threshold strictly between `91/10000` and
`92/10000`. The budget `1/256` is safely below it. This demonstrates sharpness
of the generic off-sum implication, not an optimum for Gaussian matrices or
for the sufficient ceiling `10p^2`.

## Reproduce and evidence

```sh
python3.12 -B scripts/research_package.py --package research/delta-cross-cell-independent-audit --check-only
python3.12 -B scripts/research_package.py --package research/delta-cross-cell-independent-audit
python3.12 -O -I -B research/delta-cross-cell-independent-audit/verify.py
```

The direct verifier also runs from a committed package export with the three
declared input files and no Git or third-party libraries. It prints
`PASS_DELTA_CROSS_CELL_INDEPENDENT_AUDIT`. Checks use explicit exceptions and
remain active under `-O`. [RESULT.json](RESULT.json) records the finite receipt;
passing checks support, but do not formally prove, the written universal steps.

Environment: Windows, CPython 3.12.0. Linux execution and a formal proof-kernel
replay were not run. The generic source-binding baseline was attempted but
stopped at the sparse omission `research/kappa-0023-productive-jobs`; this audit
does not report it or the selected cold replay as passed. The exact selected
record, review, source manifest and certificate were read.

Local validation passed: registered metadata and replay, direct optimized
replay, committed-byte preflight (12 package/input files), export integrity,
and optimized replay of that export with an identical RESULT.json. The optional
full source-history preflight was not run in this shallow clone. All replay
inputs are either on the base commit or retained inside this package; the
unmerged predecessor commit is not needed to run the standalone verifier.

## Coordination, coverage and limits

Base: canonical main `2a13eb1827784206202db90e5dc8327cf8a250db`, priority
revision 7, selected conditional kappa `23/10000`.
[Discussion #4498](https://github.com/CrocSwap/integer-mult-bounds/discussions/4498)
is the canonical investigation, answering [the #1166 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19111508).

The initial overlap refresh covered 351 open PRs (including drafts) and 3,375
discussion records with complete pagination. Local notes were sparse: 5,730
of 5,731 tracked note paths were initially absent. No novelty claim follows.
Live search and the relevant package inspection identified #4462 (audited),
#4473 (its independent-check request), #4472 (rounding-contract audit), and
#4481 (distinct Schur follow-up). The card was retrieved explicitly after the
handoff selection, not rerolled. Final freshness is recorded in TASK.json.

No ideal Gaussian row/column gap, analytic truncation estimate, raw exponential
oracle implementation, physical page generator, Schur transfer, tensor/core
error, native/stock budget or integer multiplication theorem is verified here.
FINE-PRIME's stated exponentially small perturbation eventually meets the
budget for a fixed positive C, but no effective threshold is computed and no
uniformity of hidden constants is supplied by this audit.

## Open next questions

Does the actual page generator meet the **combined** within/across-cell error
ledger for both rows and columns? This matters because the matrix implication
alone does not supply its caller hypotheses. Pin one emitted reference block
and reconstruct all diagonals, band entries and certified perturbations. An
all-size conclusion still needs a certified ideal gap and a uniform generator
argument; small matrices alone cannot provide them. #4481's Schur follow-up is
already separate work and is not proposed here as a new assignment.

## Credit

Ryanson Jonathan / pinterbanget supplied #4462's conditional transfer and
robustness lemmas and requested another contributor's check; its snapshots
retain his Claude Code / Claude Opus 5.5 disclosure. James Reed / jwr404 supplied
the column split and exponent chain (#4442, #4451, #4452). The #4449 across-cell
rounding contract is credited to mihir-s-05 with OpenAI assistance; this audit
does not independently reprove that predecessor. Cinna Davis and the retained
LOG-A, FINE-PRIME and rad20 authors retain their source attribution.

Prepared by mihir-s-05 with substantial OpenAI Codex assistance. The matrix
Neumann series, norm inequalities and finite geometric-series identity are
classical; no priority claim is made. New work and retained snapshots are
Apache-2.0. No independent human or formal-kernel verification is claimed.
