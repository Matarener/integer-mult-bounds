# Higher-order rank exchanges beyond concave dominance

**A new sufficient family of power-moment improvements with explicit paid budgets.
No physical supplier or new κ.**

The previous capped-mass test accepts changes that lower every concave cost.
It misses some changes that lower every relevant rank power. For example,

```text
3 rank-2 children + 1 rank-4 child → 1 rank-1 child + 3 rank-3 children
4 rank-2 children + 4 rank-4 children → 1 rank-1 + 6 rank-3 + 1 rank-5 child
```

Both strictly lower `Σ r^(1−a)` for **every real 0 < a < 1**, while preserving
count and rank mass. Their capped sums have both signs: an explicit concave
cost actually increases. Thus they supply useful sufficient search targets
outside the earlier test's domain, rather than repricing already accepted moves.
These are profile transformations; a compatible circuit implementation remains
separate. Child ranks cannot be changed by relabelling existing operations.

[PROOF.md](PROOF.md) proves the arbitrary-order binomial-stencil theorem by an
iterated derivative integral. It also proves a uniform rational lower credit,
using an aggregated cube partition with only `n(B−1)+1` coefficient buckets.
The credit can pay any complete positive-rank overhead bill with smaller rank
mass. Grid refinement improves the bound without re-evaluating an entire root.
The finite-difference identity is classical; no broad novelty claim is made.

On the actual current PR3815/3857 complete histogram, for saving a between
0.0017 and 0.0018 and a 16-part grid:

| profile exchange | copies that pay one added rank-1 child | aggregate inventory available |
| --- | ---: | ---: |
| order 3 | 3,502 | 330,480 copies |
| order 4 | 7,099 | 82,620 copies |

These are separate sufficient implementation targets, each with one additional
rank-1 cost explicitly paid. They do not prove grouping, source/consumer
compatibility, stock, chronology, dirty restoration or any new multiplication
exponent. No current frontier change or actual speedup is claimed.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B research/higher-order-rank-exchanges/verify.py
python3.12 -B research/higher-order-rank-exchanges/test_certificate.py
python3.12 -O -B research/higher-order-rank-exchanges/test_certificate.py
python3.12 -B scripts/research_package.py --package research/higher-order-rank-exchanges
```

Ordinary replay is read-only and works without Git. It checks the immutable
current histogram hash, reconstructs the full proposed paid profiles, and
compares every rational receipt field. Controls use exact independent radical
bounds in 42 cases, 168 grid bounds, six separately enclosed full-profile power
gaps and rejecting inventory, overhead, domain and actual CLI corruptions.
The all-real statement follows from the written proof, not those finite samples.
No Lean formalization, full native replay or independent human review is claimed.

`certificate.stencil` constructs the signed profile; `certificate.credit` gives
a rational uniform saving; `certificate.certify` checks aggregate availability,
legal ranks and the proposed paid histogram. The implementation bounds order
at 12 and grid subdivisions at 128; the proof has no such finite-order cap.
A failed quantitative test is inconclusive, since its credit is only sufficient.

## Open next questions

1. Can one actual source-level program implement an order-3 or order-4 exchange
   with a complete physical bill below the certificate? Start with a compatible
   set of rank-2/rank-4 operands, freeze the exact caller ABI and check an explicit
   matrix identity before searching hosting. Counts alone cannot answer this.
2. Can a different stencil family improve the power bill on an intended saving
   interval without satisfying all-exponent improvement? Start with an exact
   signed profile and a separately proved derivative-sign domain; do not infer
   a theorem from a sampled root or impose this certificate as a universal barrier.

## Credit and comparison

PR3863 (`635fe84596c19016f3d0316a5cf7abbe48285490`) supplies the immediate paid
concave-profile framework and the retained separate exact-power test oracle.
The earlier ranked-pair package supplies the min-basis order certificate and its
formal finite identity. The new higher-order family goes beyond that order;
it does not claim the finite-difference identity as newly invented mathematics.
MathProof's `IntegerKappaMomentTransfer20261015` provides the sufficient
replacement-with-reserve and normalized-admission precedent; no local Lean file
is imported or counted as a new kernel result.

Current-profile credit stays with ChaloupeMusic/PR3815, hexapode/PR3802,
dataisfire/PR3734 and the retained native/owner/hosting lineage; PR3857 retained
that exact histogram and its finite analytic certificate. Preceding rank-pair
credit includes Avi Eisenberg/PR62, eumemic/PR57, Chafik Boukhalfa/PR60 and
Dominik Scholz/PR63, with the full inherited notices retained in NOTICE.
SOURCES.json pins the live scientific provenance. OVERLAP.md states search limits.

Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
