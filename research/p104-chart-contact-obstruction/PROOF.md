# Why this one chart retag fails

The authenticated emitted word of Ali Romman's [PR #5660](https://github.com/CrocSwap/integer-mult-bounds/pull/5660), head `3b0b4f37d5005f381ed9cfcccebfbe1ab35c71aa`, has exactly one final four-gate block matching the published replacement. Its zero-based program indices are 14187, 14189, 14192 and 14194. The nominated edit changes only the common chart of `ADD(586,733,"-4",597)` at event 14189 to 652, retaining scalar chronology, coefficients, roles and endpoints.

Donor 733's immediately preceding required contact is event 13554, `ADD(695,733,"1",597)`. Its immediately succeeding required contact is event 14397, `ADD(132,733,"2",597)`. Both are source reads and must be included in its contact chain. Thus the changed donor chain contains

$$597\longrightarrow652\longrightarrow597.$$

The ordered bases of these frames are `[82]` and `[82,268]`, respectively. Over the source binary ambient space, 82 and 268 are nonzero and distinct, so they are independent. The first span has dimension 1 and the second dimension 2. In particular, 268 does not belong to the one-dimensional span of 82.

The published `construct.rebuild` permits a nontrivial public MOVE only when its old space is a strict subset of its new space. Hence the return from 652 to 597 is forbidden. Identical-frame coalescing does not remove the intervening required contact at 652. No alternative chart, inserted intermediate route, scalar retiming, basis change or private-return protocol is part of this object.

This is a completed physical obstruction to the exact direct-route retag. The conditional donor tariff formula presupposes that the next required chart contains frame 652; the measured next chart is 597, so that premise fails. No new paid histogram, signed saving or two-point price was calculated after the stop. The recipient-only expression $H_2-2H_1$ is not an earned saving.

The evidence checks the full old required-contact routes against all actual published MOVEs for both 586 and 733, including COPY source uses and final endpoints. Owned chronology is checked at descriptor level. It does not independently replay endpoint matrices, owned erasure, native phases, ordinary costs, the full caller/compiler or funded $\kappa$. The public grammar text is pinned independently; equality to an archive member was not checked. The standalone checker directly reads the committed descriptor and imports no source module or archive.

No conclusion transfers to [PR #5678](https://github.com/CrocSwap/integer-mult-bounds/pull/5678), head `af814f6f3c477fdd13b8f04380a33cf32004966b`, which changes paid bases and reports conditional $\kappa=0.00310815849$. This historical obstruction is neither a global no-go nor a claim stronger than a successor construction.
