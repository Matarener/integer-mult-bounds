# Verification evidence

I ran the direct checks on macOS arm64 with CPython 3.12 using `-I -O -B`.
At 01:30 UTC on 2026-10-18, I also completed the registered replay with
`-I -O -Werror -B` and the runner's private bytecode namespace. Its metadata
and source-pin checks passed, followed by all three verification commands and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
I retain the following exact results, which the three registered commands
recompute without writing files:

| Check | Observed result |
|---|---|
| Original pooled receipt | SHA256 `462227d245f3932d56aafc5ba5a81aedc0d26fcef8b3c2a4b1ed673c7c5e329a` |
| Changed correction | 4,991 nonzeros pass the older pooled one-hop test |
| Literal preconditioned channel | 280 input columns, 49 changed target rows |
| Native bridge | Physical masks 121/296; 512 basis columns; depth 1,2,3 checks |
| Bridge column receipt | SHA256 `8da3ef1356610f21673afd364583c317c0c156c59c5b26403dc7079898ff67d2` |
| Boundary corruption controls | Old correction, wrong shear sign, missing restoration and raw compressed physical labels reject |
| Direct versus full-memory support | All 416 entries agree; peak two memories under the retained cap of 16 |
| Forbidden block | Rows (4,6,8,39), columns (0,1,2,3); determinant 1/16 by two calculations |
| Support receipt | SHA256 `4dd6dd2aa941e26b821f85ce7463821be479413c75f33da19cfef0b3f3f65033` |
| Four separate H2 charges | Moment in [1.000088868784313991, 1.000088868784313992] |

I check the full conditional identity only after assuming a complete correction
oracle. I have not constructed that oracle. I use the support certificate and
written proof to exclude it for preconditioners of rank below four under the
stated contract. I have not run a complete supplier, formal proof checker or
selected-frontier replay, and I claim no independent human review.
