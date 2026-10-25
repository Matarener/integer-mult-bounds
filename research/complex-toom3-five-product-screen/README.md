# Exact Toom-3 five-product screen for the selected complex profile

**Exact tensor identity and optimistic profile screen. No selected-provider construction or new κ is claimed.**

## Result

For degree-two polynomials, evaluation at 0, 1, -1, 2 and infinity gives an exact five-product formula for all five output coefficients. The verifier reconstructs the interpolation matrix over the rationals and checks all nine input monomial pairs.

If one such block replaced nine rank-one recursive products by five, it would save four rank-one units. The pinned selected local profile has 2,412 rank-one units. Its exact ceiling calculator gives:

| Hypothetical realized blocks | Rank-one count | Local mass | Complex-side a ceiling |
|---:|---:|---:|---:|
| 0 | 2,412 | 5,586 | 0.001690054109089 |
| 64 | 2,156 | 5,330 | [0.001775054925982, 0.001775054925983] |
| 210 | 1,572 | 4,746 | [0.002005153888714, 0.002005153888715] |
| 254 | 1,396 | 4,570 | [0.002086688163384, 0.002086688163385] |

Sixty-four blocks are the first count whose ideal ceiling clears the task card’s five-percent gate. Two hundred ten are the first count whose complex-side transfer cap exceeds 0.002. The selected forward and backward traces each admit 254 disjoint groups of nine rank-one climbs under the phase-local dependency-window movement model used in PR #1817. This establishes enough candidate event slots under that relaxed model; it does not establish that any group is a Toom-3 tensor.

A straightforward scalar evaluation/interpolation schedule uses 19 additions and 13 rational scales per block. At 210 blocks that is 3,990 additions and 2,730 scales. Copies, scratch allocation, dirty-state restoration, precision, native hosting and the new output map are still unpriced.

The selected bit saving is 0.001733427039589844234749. Under the retained transfer its planning cap is 0.0017304274698236029, below 0.002. Therefore this complex-side idea alone cannot produce an overall κ above 0.002. The selected κ remains 0.001672660197076918.

## Boundary and prior work

The exact Toom-3 identity changes the bilinear tensor, extending the two-coefficient Karatsuba screen in Discussion #1987. It differs from diagonal rank-16 child batching in PR #1779 and its dependency-window audit in PR #1817, and from the two-root E8 rank-16 decoder currently proposed in PR #3895. The fresh overlap snapshot covered 672 open PRs and 2,573 Discussion records; these matches are leads, not a novelty certificate. The PR #1817 event-window rule is reimplemented here and credited to Josie Elliston.

The selected-source event records name frame climbs and register touches. They do not identify a three-by-three coefficient convolution, a five-child output decoder, or a dirty-state memory contract. The 254 groups are eligible event windows only. No selected provider block, complete local profile, supplier admission or kappa improvement is claimed.

The family expansion gate therefore permits only one next source-bound witness: bind one candidate group to its exact paired input forms and outputs, then charge its complete interface. Do not extrapolate the 254 event count into a multi-block construction.

## Reproduction

From the repository root, run:

    python3 scripts/research_package.py --package research/complex-toom3-five-product-screen --check-only
    python3.12 scripts/research_package.py --package research/complex-toom3-five-product-screen

The registered replay checks both orientations, exact rational identities, dependency-window movement, profile ceilings, negative controls and the unchanged bit-side cap. The pinned sources and exact base are recorded in SOURCES.json. No full supplier cold replay, Lean proof, or native compiler replay is claimed.

## Open next questions

TASK.json records the exact first source-binding experiment and the separate bit-side requirement for an overall κ above 0.002. The immediate blocker is the absent mapping from selected child climbs to Toom coefficient inputs and output coefficients.

## Credit

Credit the selected #1094 provider lineage; Josie Elliston / PR #1817 for the dependency-window batching model; the contributors to Discussion #1987 for the two-coefficient Karatsuba screen; Arham Tahir / PR #1779 for diagonal rank-16 batches; and the contributors to PR #3895 for the two-root E8 block decoder. Prepared by Gonzalo Mier with substantial OpenAI Codex assistance. Apache-2.0; no independent human review claimed.
