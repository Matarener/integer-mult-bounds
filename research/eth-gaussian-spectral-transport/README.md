# Gaussian tensor precision and shared-response transport from the ETH preprint

This package gives explicit informal Gaussian constructions extracted from OpenAI's October 25, 2026 ETH preprint, including a spectral replacement for the project's existing Gaussian tensor engine and a smaller precision bill for its ordinary bulk. It does not establish a new numerical κ. Every theorem below is proved directly, without assuming the preprint's headline ETH conclusion.

## Main concrete result

The existing raw Gaussian axis is C=[[i,1],[1,i]], with π=1+i. Its normalized n-fold tensor A_n=(C/π)^(tensor n) has eigenvalue i^j on Walsh-weight j. For any integer interval [a,a+R] in [0,n], the explicit Newton polynomial

    g(X)=i^a sum_(h=0)^R (i-1)^h binom(X-a,h)

agrees with A_n on those weight spaces. The residual has an explicit rank-one expansion on at most

    2^n-sum_(j=a)^(a+R) binom(n,j)

exceptional Walsh directions. The ordinary numerator π^R g(W), W=sum_j(I-X_j)/2, has a literal Gaussian-integer dynamic-program word. Its denominator debt is R rather than n. Its bulk response modulo π^p needs its numerator only modulo π^(p+R), whereas the full common numerator and correction need π^(p+n). This is an actual precision saving of n-R Gaussian units for the stated bulk computation.

The exceptional correction and physical word are charged, not inferred cheap from rank. The full construction may cost more than existing fast transforms on an unrestricted dense input. A κ improvement requires a named shared-response consumer in which the explicit correction has a favorable complete bill.

## What to read

| Document | Positive result and exact scope |
|---|---|
| [Gaussian spectral bridge](gaussian-spectral-bridge.md) | B1-B4: actual source matrix; exact central-weight replacement; Gaussian-integer numerator word, coefficient/norm bounds, exceptional-rank tradeoff and lower-precision bulk |
| [Tapered recovery and preprint assessment](preprint-assessment.md) | G1-G8: complete Gaussian-DVR Hermite constructor, precision dividend, concrete integral Cauchy deformation, weighted mode count and exact entrywise recovery |
| [Integral kernels and actual response packets](algebraic-application.md) | Fraction-free partial-swap synthesis; joint valuation/Taylor filtering; explicit Cauchy factorization; affine parameter dependence of six real P104 updates |
| [Communication and uniform descriptions](constructive-transport.md) | Ten constructive results for actual query delivery, dyadic module certificates, chronological shared summaries, creation-time semantics and fully charged uniform interpretation |
| [Exact endpoint and κ interface](endpoint-lowering.md) | E1-E5: denominator-sensitive pruning, exact ordinary recovery, observable-dependent precision retirement, explicit modular query deletion and sufficient full-invoice assembly |
| [Sources and frontier](SOURCES.md) | Pinned paper, main and relevant pending source heads; inspected linked-tree precedents; evidence and overlap limits |
| [Notices](NOTICES.md) | License, assistance and predecessor attribution |

## A useful new combination

The paper's taper is transported into the ramified Gaussian ring, rather than treating i as a harmless addition to its unramified coefficient ring. Its measurement idea is turned into a literal source-preserving query program over the caller's scalar ring. The spectral construction is specialized from the paper's alternating sequence (-1)^j to the actual Gaussian tensor's four-phase sequence i^j. Integer numerator synthesis, net valuation weights and exact decoding then share one common precision bill.

The source-specific packet is also concrete. In the PR 5786 common word, the six updates at indices 13104, 13110, 13287, 13293, 13475 and 13481 have an exact total parameter degree at most one. Their full endpoint is determined by a constant and six linear coefficients rather than 64 formal subset coefficients. This gives an exact symbolic-construction saving. PR 5802 already credits its three pending-sum acquisitions; they are not subtracted again here.

## Frontier and evidence

Canonical main was pinned to de5ec2e7a6074068452f45b1a191b5c72832df4a, priority revision 8. The selected conditional κ is 0.00310045; admitted BIT is .0034. The previous pure-math PR 5806 claims conditional κ>=.0031234. The final refresh found PR 5811 claiming conditional κ=.00312418633064, realizing the fourth role-92 accumulation and crediting the concurrent PR 5806 baseline join. Both are distinct from selected admission. This package changes none of these records and does not resubmit their query gains. A large complex gain above .0034 would also need a compatible admitted BIT improvement.

Four workers developed and independently cross-reviewed the informal proofs. Work performed was source reading and pure mathematics. No solver, mathematical search, operator replay, benchmark or Lean run was executed. Publication byte/hash checks are separate from mathematical verification. The paper's whole ETH claim has not been independently established by this package. Its local algebraic mechanisms are reconstructed and proved here.

## Open next questions

1. **A real exceptional-summary consumer.** Identify an actual Gaussian provider interval whose consumed response is literally the B1 matrix, with the exceptional Walsh measurements already available or cheaply shareable. First step: give that response equality and the source versions, then emit its delivery words. Rank similarity alone is insufficient.
2. **Positive net crossing weights.** For that same interval, write the Cauchy/local deformation and debit every π denominator from source scaling, native normalization and final decoding. First step: a literal termwise net-weight table and full final modulus. A crossing term disappears only at that modulus.
3. **A funded whole replacement.** Price all retained modes, group contractions, jets, interpolation, ordinary passes, dirty restoration and target changes in the complete actual caller. First step: its explicit new paid/target lists, compared under E5 and every selected strict guard. No favorable unknown gadget is assumed by the results already proved.

Start with B1-B4 and G4-G6. They are the two main mathematical transfers; the other notes make their endpoint, scalar-ring and cost interfaces reviewable.

Prepared by Dugongue with substantial OpenAI Codex assistance, one coordinator and three workers. New text is Apache-2.0. Existing source and classical mathematical credit are retained in SOURCES.md and NOTICES.md.

