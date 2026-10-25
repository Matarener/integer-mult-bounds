# Matched P104 source-return adapters

**Independent comparative audit of two existing constructions; no new kappa.**
This closes the first bounded request in [PR3943's handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19032700): match its 960-ADD return with PR3940's 1152-ADD return before comparing their costs. Both constructions belong to Chris R / Clear1nsight with substantial OpenAI assistance. The new contribution is the matched contract, source-bound comparison and separate checking, not the 960-ADD schedule.

## Result and common contract

The adapters are directly comparable under their stated **formal canonical-chart** semantics. They have the same entrance, same physical output locations and charts, same unit arithmetic alphabet, and return all 72 arbitrary dirty helpers. PR3943 saves exactly **192 unit Gaussian array additions** relative to PR3940's separately closed return adapter. Both require 104 halves, 104 restoring doubles and 192 rank-one frame transports. The scalar saving does not reduce their recursive rank mass or repair the failed supplier screen.

| Pinned adapter | Unit ADD/SUB | Halves | Doubles | Frame transports | Formal events |
| --- | ---: | ---: | ---: | ---: | ---: |
| PR3940 `51ba88c007cfbcc3d9cf22dd321f5224be3a5bb1` | 1152 | 104 | 104 | 192 | 1552 |
| PR3943 `2cba526a4ebe0ef6c3c0143498adcf67dca97941` | 960 | 104 | 104 | 192 | 1360 |

At 512 complex words per array, the difference is `192*512*2=196608` real-component additions. This is an operation count, not a measured runtime advantage, scalar optimality proof or native admission. In particular, PR3940's **fused** source-preserving suffix is a different entrance and comparison: its 208-H1/mass-2576 invoice is not invalidated by this closed-adapter audit.

Write `J=[0,1,3,6,22,31,93,103]`, `|N|=96`, `B=A[J,N]`, and `w=x+y`. The common encoded entrance is

```
X_J = q = x_J + B x_N       FULL
X_N = w_N                  H_n
Y_J = w_J                  H_j
Y_N = v_N = y_N + B^t q     FULL
72 helpers = independent arbitrary dirt, FULL
```

The required exit, in the same registers, is `X=x` FULL, `Y=w` in each indexed `H_i`, with all helpers unchanged. There is no free role permutation, sign change, clean scratch, erasure or cross-chart arithmetic. Every lift/drop is explicit; every arithmetic source and recipient is FULL. All statements are coordinatewise over the Gaussian dyadic ring `Z[i,1/2]` for finite arrays. A lift/drop uses the inherited formal chart semantics; a physical arbitrary-integer signed-floor implementation is not inferred.

## Why the 192 additions disappear

After lifting the same 96 `X_N` arrays, PR3940 first computes

```
Y_N -= X_N       # v_N - w_N
Y_N -= B^t q     # -x_N
X_J += B Y_N     # x_J
```

Each nonpivot pair is then `(w_n,-x_n)`. Its three unit updates
`X_n-=Y_n; Y_n+=X_n; X_n-=Y_n` produce `(x_n,w_n)`. Thus the direct work is four additions per nonpivot: the first subtraction plus the three-update return.

PR3943 instead first computes `Y_N -= B^t q`, leaving `(w_n,y_n)`. Two unit updates `X_n-=Y_n; Y_n+=X_n` immediately give `(x_n,w_n)`. It then restores the pivots with `X_J -= B X_N`. Both words finally descend the same `Y_N` arrays. Both have two B traversals containing 384 signed-half entries each, lowered by halving and restoring the same number of donors. The difference is therefore exactly `(4-2)*96=192` additions; no changed boundary or unpriced operation explains it.

The common inverse equations, already supplied by PR3882, are

```
x_N = w_N - v_N + B^t q
x_J = q - B x_N
y = w - x.
```

They show that the encoded fields are algebraically independent; checking all 280 encoded basis inputs proves the adapter identity for all formal inputs, including every dirty helper. The two predecessors' stored endpoint digest strings use different sparse/dense serializations. They must not be compared directly. This package compares normalized coefficient matrices and chart labels instead.

## Source binding and verification

Five unchanged source exports retain both proofs, both schedule-building sources and their shared 672-byte geometry. SHA256 digests and original Git blobs are recorded in SOURCES.json; `verify.py` authenticates hardcoded SHA256 pins before replay. The retained geometry is byte-identical in both packages, from PR3882 `9d56eeedbed5e3e9bbbc8c189d66f14cf15b6067`. These exported bytes are runtime inputs; the original remote commits are provenance, not hidden checkout/network dependencies.

`verify.py` extracts **only** `return_adapter` and, for PR3940, `scatter` from the pinned source AST. It executes those schedule builders with restricted builtins to obtain their actual literal words. It imports neither predecessor evaluator, geometry routine nor endpoint oracle. A separate root enumeration reconstructs B; an independently written sparse Fraction interpreter checks every arithmetic frame, coefficient, final physical location, helper and operation count. This is a source-bound comparative replay, not a wholly code-disjoint reconstruction of the two schedules.

`test_verify.py` separately reconstructs the block identities on symbolic dense rational vectors, including non-half B entries in deliberately abstract test cases. Those cases check the algebra, not a claimed half/ADD lowering for other geometries. Behavioral controls challenge the literal-word replay and source binding. Both checkers use explicit failures that remain active under `-O`. They were prepared in separate AI contexts; no independent human or proof-kernel review is claimed.

From a complete contribution checkout, standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p104-return-contract-match
python3.12 -B scripts/check_research_commit.py --package research/p104-return-contract-match --check-source-history
```

Git-free replay, including a read-only export:

```sh
python3.12 -I -B research/p104-return-contract-match/verify.py
python3.12 -I -O -B research/p104-return-contract-match/test_verify.py
```

Expected marker: `PASS_P104_RETURN_CONTRACT_MATCH`, with 280 independent inputs, 72 helpers, 384 B nonzeros, counts in the table and `new_kappa=false`. Default replay does not write sources or receipts. Exact execution evidence, environment and publication head belong in the PR handoff.

The complete original 4058-event channel prefix, actual binary hyperplane geometry, native recipes/global phases, signed-floor precision, physical owners/holding/routing/control/tapes, opposite orientation, selected cold replay and complete supplier admission are **not rerun or proved here**. The source-bound adapter comparison relies on the stated encoded entrance, which the predecessor packages supply. Matching chart labels is not independent verification of their physical realizability. The 192 transport floor and failed coverage budgets are credited predecessor results; this audit neither strengthens them nor supplies a new lower-bound model.

## Task selection and stopping decision

Handoff-first refinement of `p104-side-correction`, canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority 6. The card was retrieved after selecting the released handoff; there was no random task draw. All 654 open PR bodies including drafts were refreshed across seven pages at entry, and the repository overlap helper searched that cache. Current handoffs and start-here conventions were read; full Discussion/closed-diff coverage is not claimed. TASK.json records the exact scope and freshness.

**NARROW / stop:** close this comparison and release the claim. Do not start another scalar census or dependent supplier implementation: fewer additions do not delete a recursive child. The already-failed optimistic coverage screen is unchanged.

## Open next questions

The comparison request is closed within the formal contract. New parallel [PR3954](https://github.com/CrocSwap/integer-mult-bounds/pull/3954), head `a17ecc832b8c0c022f7cf39a33d77c02d0bdbc4a`, supplies proposed two-axis endpoint equations and a rejected scaffold; its PR explicitly excludes this 960/1152 comparison. Its claims were read at submission, not mathematically replayed here. Do not repeat that fixed scaffold as an open implementation task. The consequential next task is a **changed** all-role entrance/exit encoding or consumer with a favorable complete owner/progress/profile ledger. First specify actual outputs, frames, owners, dirty returns and the whole paid invoice, and show which recursive work disappears. Physical admission and a favorable complete allowance are blockers. Further optimization of this closed adapter alone does not justify construction expansion.

## Credit

Chris R / Clear1nsight with substantial OpenAI assistance supplies PR3882's residual representation and both PR3940/PR3943 return schedules; PR3943 owns the 960-ADD construction. Retain their Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940, terminal-floor/occupancy, Josie Elliston/E8, Sagar Thakrar/PR1012, Douglas Colkitt, Dominik Scholz, actual caller and native/compiler lineage. The unchanged exported proofs retain their detailed notices and attribution. No predecessor construction or supplier rejection is claimed as newly discovered.

Credit Clear1nsight's parallel PR3954 for the distinct two-axis compatibility and scaffold question, inspected as pending source context. New comparative audit, interpreter and tests by ToikY with substantial OpenAI Codex assistance, including separate AI algebra review and test implementation. Apache-2.0. No merge, frontier update or scientific admission is implied.
