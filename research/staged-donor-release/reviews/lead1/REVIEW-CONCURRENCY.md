# Scoped concurrency reconciliation review

CONCLUDE: YES
OUTCOME: SUCCESS_KAPPA — conditional gain over the old pinned PR3638/PR3633 baseline; matches the currently reported concurrent endpoint, with smaller T360 stock. No additional frontier gain or priority claim.
PRESENTATION ARTIFACT: 2b0c3deffe4ff261e7f36826299b264b81b2c39c
ORIGINAL SCIENTIFIC ARTIFACT: a3bdc591920a4b9003d8442d1fcca24218153661

This is a factual upstream-reconciliation follow-up to my independent scientific review, not a new scientific approval of either concurrent PR. No external posts or PRs were created and no heavy replay was launched.

## Findings

Reviewed all six paths changed by the presentation commit: CONCURRENT-WORK.md, README.md, PR-DRAFT.md, TASK.json, evidence/concurrent/3642.json and evidence/concurrent/3653.json. Live GitHub API reads independently confirmed the retained heads: PR3642 at 044d24f12e74f228dd462c07ae2d7f3ea35e2be9 and PR3653 at 607a09ff441c79b215a8127a81f4cc70021d0d9b. Their retained bodies support the reported mechanism, endpoints, T values and finite stock counts. The public claims remain provisional external evidence; their full scientific releases were not independently replayed here.

A fresh exact integer/Fraction check extracted PR3653's stated profile and checked every rank cross-product:

h488[r]*360 = h360[r]*488, for ranks 1,2,3,4,5,8,48.

Thus the normalized profiles agree exactly; there is no exponent gain from this T360 composition over that reported T488 construction. The common conditional endpoint is .001730418899766071163804−10^-46−10^-70. The exact common-grid gain over the old pinned .001730096363528623534230 predecessor is .000000322536237447629574. PR3642's reported .001730394391813963415120 endpoint is lower by .000000024507952107748684.

The smaller finite constants are correctly stated: physical stock 896*360+408+8+91+2 = 323069 versus 896*488+408+8+91+2 = 437757; calls 3240 versus 4392; roles 1321920 versus 1791936. Stock reduction is not a further normalized exponent improvement. Evidence: CONCURRENCY-CHECK.json.

The presentation explicitly credits the concurrent retiming mechanism and T488 endpoint, identifies the result as matching that endpoint with smaller stock, and limits its strict-gain comparison to the old pinned baseline. This is an appropriate revision of the claim. I do not treat the broader overlap search's pagination counts as a novelty certificate or as independently verified source-diff coverage.

I also compared the package to the original approved scientific commit. Subsequent changes are presentation, validation/review records, the new concurrent metadata and reviewer artifacts; no scientific source, source archive, candidate word, native/complete receipt, mathematical price, or execution engine changed. The PROOF edits since original approval merely record that approval. The original scientific conclusion and its explicit reuse/cold-run limitations therefore remain applicable.

## Critical gaps

None blocking the revised scoped conclusion. This approval does not establish that PR3653 has itself met every admission obligation; it establishes exact agreement with its reported normalized profile and endpoint, with that qualification preserved in the package.

## Remaining open domain

All inherited theorem assumptions and unexecuted portable/no-reuse cold tails remain as recorded in REVIEW-TERMINAL.md. No selected-frontier update, global optimum, priority, novel retiming discovery, or improvement beyond PR3653's reported endpoint is approved. Publication and any subsequent upstream changes remain outside this exact-commit review.
