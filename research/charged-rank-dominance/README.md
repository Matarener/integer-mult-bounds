# Pay for overhead from a certified concave-profile improvement

This package turns the existing all-power rank-profile improvement into an
explicit **sufficient positive-cost allowance**. It answers a concrete next
question left by a sign-only comparison: how much additional routing or cleanup
can be charged while the entire moment still improves?

For the source-bound historical rank-first pairs, the rational certificate pays
**one additional rank-1 child on h = 23 and three on h = 25**, uniformly for
saving a between 0.0017 and 0.0018. The universal theorem also prices arbitrary
positive-rank overhead by its full rank mass and composes across batches.
These are cost allowances, not newly constructed routing/cleanup operations.
On the actual current PR3815/3857 histogram, the theorem also supplies a concrete
implementation target: **1,775** mass-preserving `2+2 → 1+3` exchanges would pay
one extra rank-1 child and strictly improve its moment, if a legal implementation
preserves the other costs and interfaces. The histogram has enough children;
this package supplies no such circuit transformation.
No new κ, complete supplier, selected-frontier update or practical runtime
improvement is claimed. The old source is a calibration, not the present best
supplier; PR3857's staged supplier is a different construction.

[PROOF.md](PROOF.md) gives the complete theorem and proof. [RESULT.json](RESULT.json)
contains exact fractions and all capped sums. `certificate.budget` computes the
uniform credit; `certificate.admissible` verifies a proposed overhead histogram.
A rejection is inconclusive: the bound is sufficient and intentionally coarse.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B research/charged-rank-dominance/verify.py
python3.12 -B research/charged-rank-dominance/test_certificate.py
python3.12 -O -B research/charged-rank-dominance/test_certificate.py
python3.12 -B scripts/research_package.py --package research/charged-rank-dominance
```

Ordinary replay is read-only and accepts a Git-free export. It authenticates
four exact source receipts and the pinned current full histogram, rebuilds every capped sum from their actual full
rank histograms and compares the complete result. Controls independently use
rational atanh/alternating-exp enclosures at nine source points and exact
square-root intervals on an exhaustive small histogram domain, plus malformed,
reversed, changed-mass and unaffordable-overhead cases. These finite checks
support the implementation; the proof supplies the all-real-interval statement.
The physical words and native compiler are not replayed in this package.

## What is reused and what is added

`research/ranked-pair-verification/concave_dominance.py` and its PROOF.md already
prove the capped-mass identity and a strict sign for all exponents. That result
is explicitly credited, not rediscovered. The new step bounds the discrete
power curvature from below using only rational interval endpoints, creating a
uniform, positive paid-cost budget and a sound charged-admission rule.
The MathProof `IntegerKappaMomentTransfer20261015` source supplies the prior
sufficient replacement-with-reserve and normalized-admission framework;
this package discharges a concrete quantitative saving hypothesis. The local
Lean source is not a runtime dependency or new formal certificate.

## Open next questions

1. Bind an actual current source-level exchange to its capped-mass vector and
   the full added physical ledger. First freeze the before/after histograms,
   unchanged normalizers and actual added children. Chronology, dirty recovery
   and the all-size compiler remain separate requirements.
2. Tighten the rational curvature envelope for a candidate that fails this
   inexpensive first pass. First isolate the largest contributing k values;
   use certified logarithm bounds there instead of recomputing an entire root.
   An unsuccessful coarse test is not a barrier theorem.

## Credit and scope

Retains the ranked-pair verification package and its already proved concave
order, including Avi Eisenberg / ikeboy (PR62 pair graph), eumemic (PR57 joint
frame compiler), Chafik Boukhalfa (PR60 rank-first reclamation), and Dominik
Scholz (PR63 concurrent identical composition). Its historical PR64 checkpoint
and subsequent verification retain priority for the sign theorem. Full retained
predecessor attribution is in [NOTICE](NOTICE), copied from the pinned source.
The majorization/discrete-curvature technique is standard. No claim that nobody
has applied it before is made. See OVERLAP.md for bounded search coverage.

Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
