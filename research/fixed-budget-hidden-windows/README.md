# Fixed call budgets limit PR6049's hidden power windows

This is a scoped follow-up to [PR6049](https://github.com/CrocSwap/integer-mult-bounds/pull/6049)
and its [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/6052).
It addresses the fixed-budget question for the minimal power-of-two alphabet.
It supplies arithmetic profiles, not a native supplier or a new kappa.

## Claim

Let h>=1 and N>=1 be integers. Let A_j,B_j be nonnegative integer call counts
on ranks 2^j, 0<=j<=2h+2, with at most N calls **per profile**. Put
F(p)=sum_j(B_j-A_j)2^(jp). Assume zeros of multiplicity at least h at p=0,1,
and two distinct interior zeros alpha<beta, with F>0 on (alpha,beta).
The endpoint conditions include equal call count and rank mass. Then

    beta-alpha > 2*6^h / (N*ln(2)).

The constant is asymptotically sharp. Irrational quadratic interior roots and
common paid padding are included. Define S=6^h/2 and
Z=floor((floor(N/S)-1)/2). Every eligible pair also satisfies

    beta-alpha >= log_2((Z+1)/(Z-1)),
    beta-alpha > 2*6^h / ((N-S)*ln(2)).

Eligible inputs have Z>=2 and N>S. The discrete bound is attained at every
N=S*(4*n^2-1), n>=3, by residual
(n*x-n-1)*((n-1)*x-n). This proves exact finite-budget optima on that infinite
sequence, not attainment at every budget.

[PROOF.md](PROOF.md) gives the degree reduction, integer discriminant,
half-L1 normalization, trace bound, equality cases and rational mesh consequence.
For h=1,N=1000, all 8,158 eligible integer quadratics are enumerated exactly.
The minimum width is log_2(81/80), attained by 60x^2-161x+108 (987 calls)
and 72x^2-161x+90 (969 calls). The independent shifted-coordinate census agrees.

## Scope boundaries

[SCOPE-COUNTEREXAMPLES.md](SCOPE-COUNTEREXAMPLES.md) and the independent checker
give exact controls against extending the result without its hypotheses:

- Seven ranks with simple endpoint zeros (h=1, larger support) admit a
  two-crossing family of width Theta(N^(-3/2)); no positive universal
  constant/N lower bound holds there. This is not a counterexample to the
  h=2 seven-rank theorem, which requires double endpoint zeros.
- One interior crossing can produce an edge loss missed by the stated mesh.
- The same numerical constant does not transfer unchanged to a different
  five-rank alphabet.

The theorem is specific to integer multiplicities, the specified power-of-two
alphabet and endpoint/interior-zero pattern. It does not resolve arbitrary
rank alphabets, legal supplier realizability, the selected compiler, or any
of the five retained framework assumptions. It does not alter the selected
conditional kappa 781451/250000000. Finite checks corroborate the written
proof and are not a formal verification of its uniform mathematical statements.

## Reproduce

From the repository root, using Python 3.10+ standard-library features:

```sh
python3 -I -B research/fixed-budget-hidden-windows/replay.py
```

The replay runs the main and independent verifiers and unit tests in normal
and optimized modes, serially, with a 30-second timeout per command. It checks
both JSON outputs against the saved receipts and writes no package files.
Individual entry points are:

```sh
python3 -I -B research/fixed-budget-hidden-windows/verify.py
python3 -I -B research/fixed-budget-hidden-windows/independent_check.py
```

The main verifier uses exact integer/Fraction arithmetic, directed square-root
enclosures and a positive logarithm series with a rigorous tail bound. The
independent verifier uses shifted coefficients and exact Sturm root counting.
Acceptance does not depend on floating-point arithmetic. The interval helper
is conservatively incomplete at extreme inputs: a valid n=10^20 profile passes
the integer certificate but its tiny strict margin is lost at the fixed printed
precision. The built-in fixtures, through n=10^9, pass. The proof is uniform.

Runs used CPython 3.14.7. Python 3.10 syntax/API compatibility was inspected,
not tested on a 3.10 runtime. No dependencies, network, Git, upstream Python
execution or selected-supplier replay are needed by these direct commands.
No shared CI or selected-record files are changed. This standalone package
does not opt into the repository's generic research-package metadata workflow.

## Sources, credit and review

Base main: 721c03822c421b7f7fcbb2598993b947c4d88419.
PR6049 head: 2646b6d67ceb74b9868e632f3a27312d8be62a0e.
[SOURCES.json](SOURCES.json) records the exact paths, commit, Git blob IDs,
SHA256 hashes and public URLs for two unmodified inert source exports.
The verifier pins that manifest and checks the exported byte hashes and Git
blob hashes. Commit/path attribution is recorded; the full offline commit-tree
chain is not included in this compact package. No publication ancestry claim
is inferred from a matching blob hash.

zxv's PR6049 supplies the hidden-window construction, endpoint-multiplicity
framework and minimal support result. Its credited predecessors include
[Nick Petalas's PR5174](https://github.com/CrocSwap/integer-mult-bounds/pull/5174)
and Ali Romman's root-budget work. The new scope is the budget-width bounds,
attained cases, finite census and explicit boundary counterexamples. The proof
uses classical polynomial/discriminant and logarithmic inequalities; no global
novelty claim is made. Repository license and upstream notices are retained.

Prepared with substantial OpenAI Codex assistance, including GPT-6 Astra,
and separate AI proof/implementation review. AI reviewers contributed the
stronger discrete argument and scope counterexamples. No independent human
review, proof-assistant acceptance or maintainer approval is claimed.

Human review is requested for the degree and endpoint hypotheses, per-profile
normalization, discrete inequality and equality case, census completeness,
and seven-rank counterexample family. An archival merge alone would not
establish scientific acceptance.

## Open next questions

1. Characterize the budgets at which the discrete lower bound is attainable.
   This would distinguish a general lower bound from an exact optimum. A first
   step is to classify integer quadratics with Delta=1, -b=Z and both roots in
   (1,2). The unresolved part is the arithmetic feasibility classification.
2. Determine sharp budget-width bounds for the seven-rank class. The included
   family rules out constant/N but does not identify the optimal rate. A first
   step is a coefficient-height separation bound for the quartic residual.
   A matching lower bound is not established in this package.
