# Preliminary mechanism review — not frontier admission

PR5599 at `09dd0965711ca7eeb169057a420abab1c9052137` claims κ = 0.00310045. The source was archived on main; the stronger claim remains under review. The primary execution stopped at its 600-second wall limit, after the helper-cut and complete endpoint checkpoint. See VALIDATION.json for the exact coverage. Native/caller completion and funding checkpoints were not reached. No complete validation or mathematical rejection follows.

## Mechanism inspected

For a helper-only boundary pair (c,d) and a common-chart cut pair (a,b), the conditions aP=c, Sb=d and ab=cd=1 permit two invertible scalar changes of basis. With Gd=e_p and e_p^T G=c, and Jb=e_p and e_p^T J=a, the input basis G^-1 makes the cut coordinate an original independent input. Retaining that coordinate and replacing its subsequent role by a fresh input changes the final helper state by d(z-ch). The final G returns all other helper coordinates and places the new independent input in the successor coordinate. Main outputs are unaffected because the suffix direction is helper-only. This is a change in the independent input inventory, not duplicate credit for an old output.

The source emits common-chart ADDs and dyadic-unit SCALEs and their inverses. The full exact replay checks all sources and outputs, strict nested transports, helper supports, ownership, and every sequential split; the dense reverse replay independently checks the scalar endpoint matrix. Those checkpoints passed in this maintainer run. Written chart/tensor induction retains scalar coefficients outside tensor powers. The full implementation check remains unfinished.

The thirteen splits change the local target histogram by 2H1+5H2+6H4+6H5+5H7+2H8−13H9 and leave the local paid histogram unchanged. Rank mass is unchanged. Strict concavity predicts a positive target-moment change. All 748 local public fields, including the 13 new inputs, must survive the actual caller join: 540 helpers per forward call and 13,048 productive fields globally. This obligation cannot be discharged just by the scalar split identity.

## Interfaces inspected; remaining checks

The retained P104 caller implements backward main interfaces using an all-forward local call surrounded by signed swaps and Q^2 translations; it does not transpose COPY/CLEAR instructions. General helper endpoint normalizers conjugate a nested chart difference into its native Gaussian job, with both monomial normalizers charged. This differs from the more restrictive canonical-start convention of the selected neutral caller. The PR5550 checker was adapted to recount the new input inventory, normalizers and scalar/route allowance; its exact diff is retained. The adapter has not yet passed its positive control or candidate execution and must not be treated as validated tooling.

The new pricing source uses the larger target count in completion tails, decay 39/40, product power 1024, cutoff 17, floor 18, and compiler logarithm power 1024. An independent decimal arithmetic screen agreed with the advertised raw crossing and positive tested margin, but that screen is not a directed interval certificate or complete compiler replay. The primary source's exact funding stage remains uncompleted in this run.

The earlier cut-stability package applies to its own word; its numerical maxima must not be copied to this changed word. A new conservative scalar-operation majorant and paid-rank mass are provided by PR5599. Their complete use in the retained precision/storage application still belongs in the final conjunction review. The five selected assumptions remain explicit: native all-width implementation, ownership/erasure, uniform compiler closure, precision/tape implementation, and analytic recovery.

No full uniform word, rounded multiplier, Lean theorem or tape execution was verified. No new κ is selected here. Credit is retained in README.md and every original source package.
