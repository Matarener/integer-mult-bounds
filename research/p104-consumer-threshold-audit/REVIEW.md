# Step-by-step review of PR3620 PROOF.md sections 1 and 3

Object: [PR #3620](https://github.com/CrocSwap/integer-mult-bounds/pull/3620)
(Clear1nsight), head `5a4354c669dc05a9368f58321b1951ebac36d80d`, file
`research/p104-caller-feasibility/consumer/PROOF.md`, lines 1-7 and 18-165
(section 1, the coverage grant, and section 3, the deletion threshold), plus the
matching paragraph of PR3620's `research/p104-caller-feasibility/README.md`
(lines 28-41). Out of scope: section 2 beyond its use in
section 3, section 4 (the PR3605 T740 bracket), section 5, and the `physical/`
format half of PR3620.

The verifier was written from the model stated in PROOF.md and in
`research/p104-all-pair-consumer-budget/README.md` on main. PR3620's `budget.py`
was not opened. Line numbers below refer to PR3620's PROOF.md unless stated.
Method A is an independent implementation of the series technique PR3620's
PROOF.md describes for `budget.py`; method B (Decimal closed form) is the
methodologically distinct check.

Verdicts: **valid** (correct as written), **confirmed** (a numerical or
source statement reproduced independently), **valid as scoped; clarified**
(correct within the scope its sentence states; the audit adds context that
changes how the number should be quoted), **invalid** (false). No step is
invalid.

## Notation

For a pair count `p >= 1`: `m = 16p+9`, `W = 208p`, `P = 3014`, forward calls
`p+1`, dual calls `p`. `F` is the forward profile, `D` the changed full dual,
`D_d = D - d H1`. A child of rank `r <= m` costs `m^a r^(1-a) = r (m/r)^a` in
normalised units. With `B >= 0` fully paid banks the moment test passes iff

```
N - m(W+B) < 0,   N = sum_r [(p+1) F_r + p D_{d,r}] r (m/r)^a + max(0, J_B),
J_B = (m-1)W + mB - (2p+1)P.
```

## Section 1: inputs and the coverage grant

| Step | Statement (line) | Verdict | Evidence |
| --- | --- | --- | --- |
| 1.1 | F = (1216,74,86,104,48,42,68,8), mass 3070 (table, lines 23-35) | confirmed | Read from `research/p104-consumer-budget-audit/RESULT.json` on main (PR2744), sha256 `08705a91...`: census `forward2458`, 1646 transports, mass 3070. This binds PR2744's recount of the PR2458 forward. It is not recounted again here. |
| 1.2 | D = (1316,61,74,86,33,25,46,8,93), 1742 calls, mass 3542 (table) | confirmed | Read from PR3609's `RECEIPT.json` at `13f974da` (git blob `6faa5157...`, sha256 `6d06db04...`), `invoice.changed_full`. It is the sum of the unchanged PR3446 projection (1597 calls, mass 2653) and the new entrance completion (`52 H1 + 93 H9`, 145 calls, mass 889). This is the author's executed receipt from an open, unreviewed PR. It was not recounted from `PROGRAM.json`/`NATIVE.json`. |
| 1.3 | `W = 208p` families, one unpaid coordinate each (lines 37-40) | valid, inherited | `W = (s-1)·104` with `s = 2p+1`. This is the PR2744/all-pair consumer law and does not depend on the dual's histogram. PR2744's contract is exactly its `p = 4` instance (`m = 73`, `W = 832`, 5 forward and 4 dual calls, one unpaid coordinate per family). PR3609's own consumer stop also uses `W = 832`, `m = 73`. `E` decreases by one per family, so a larger `W` would favour the candidate. Nothing in PR3609 adds families or unpaid coordinates (`new_private_Gaussian_banks = 0`). |
| 1.4 | Grant `P = 3014` to every call, even after deletion (lines 40-42) | confirmed favourable (conditional on PR3609's frame claim) | PR2744's checker defines per-call persistent progress as `Σ (len(final) - len(initial))` over the 358 role fields, whose boundary dimensions are fixed: X `(1,9)`, Y `(0,8)`, dirty `(0,9)`. So `3014 = 104·8 + 104·8 + 150·9` is the progress of every word with those initial and final frames (PR2744 reports it as `maximum_original_progress_per_call`). PR3609 states, and its receipt records a check of, the same complete physical endpoint map and all 358 final frames as the original word (PR3609 PROOF.md lines 9-12; this audit did not re-run that check). Given that claim, the changed dual's progress is exactly 3014 per call. `E` decreases in `P`, so granting 3014 to every call, including the forward calls (2312 + 702 recounted) and the post-deletion duals, is exact for the dual and an over-credit after deletion. |
| 1.5 | No double count of the completion's children | confirmed | The 145 completion calls are inside D and are charged once at their native moment. Their progress falls on the same 358 fields, so it lies inside the capped credit. `J_B` is the residual after the full credit. This is PR2744's hypothesis 3: a child that supplies remaining progress is charged once. No child is charged both in D and in `J_B`, and no progress is credited beyond the cap. |

Conditionality of section 1: the coverage law itself (one unpaid coordinate per
family, the per-role caps, retention of the full credit after deletion, and
residual children of rank `m`) is inherited and labelled optimistic by PR3620.
Neither PR3620 nor this audit realises it. Two items matter only for the passing
direction: PR3609's temporarily writable Y sources and every other unpriced
obligation (ownership, routing, scalar work).

## Section 3: the threshold

| Step | Statement (line) | Verdict | Evidence |
| --- | --- | --- | --- |
| 3.1 | `r^(1-a) - (r-δ)^(1-a) <= δ` for integer `0 <= δ <= r`, `0 < a < 1` (line 99) | valid | The unit increments of the concave `x^(1-a)` decrease. The first one, from 0 to 1, equals one. A run of δ increments therefore totals at most δ. Finite certificate: `verify.py` checks every `1 <= δ <= r <= 9` at `a = κ` and `1/596` with rational intervals, with strict inequality for `r >= 2`. |
| 3.2 | Deleting `d` rank-one children dominates every pattern `Σ δ_j <= d` (lines 101-104) | valid, with stated premises | The saving is additive over children, so any pattern saves at most `Σ δ_j <= d`, which is exactly what `d` rank-one deletions save. Implicit premises, all met: `D_1 = 1316 >= d`; each dual call may use its own pattern (the bound applies per call); forward calls are fixed. Outside the lemma, as PR3620 says: coarsening (`H1+H1 -> H2`), raising ranks and adding children. |
| 3.3 | `E_d(p,a) = (16p+9)^a (p U_d + V) - 6236p - 3014` (line 117) | valid | Substituting unclamped `J_B` into `N - m(W+B)` gives `m^a(pU_d+V) - W - (2p+1)P`, and `W + 2P = 6236`. Method B evaluates this closed form. Method A evaluates the clamped model numerator and capacity. They agree to below `1e-40` at five points. |
| 3.4 | Clamping only raises the bound; zero-bank clamp adds 4050 at `p = 1`; `mB` cancels (lines 120-124) | valid | `max(0,J) >= J`. `J_0(1) = 24·208 - 3·3014 = -4050`. `mB` appears in both `J_B` and the capacity. Checked: the clamped model at `p = 7` is identical for `B = 0, 1, 17, 10^6`. "Adds 4050" refers only to `B = 0`, as written. |
| 3.5 | Strict convexity in real `p` (lines 128-136) | valid | Re-derived: `E'' = 16a(16p+9)^(a-2)[(16(1+a)p+18)U_d - 16(1-a)V]`. Since `U_d > V > 0`, the bracket exceeds `18U_d - 16V > 0` for every `p >= 0`. So the integer sequence has strictly increasing forward differences. |
| 3.6 | Enclosures `E_425(6,κ)`, `E_425(7,κ)`, `E_425(8,κ)` (table, lines 142-146) | confirmed | Method A gives 2.623221066338944…, 1.600686410509596… and 1.973543616715320…, each inside the stated interval. Method B agrees. |
| 3.7 | Rejection for every integer `p >= 1`, every finite `B`, every `d <= 425` (lines 148-151) | confirmed (two proofs) | (A) Convexity plus `E(7) < E(6), E(8)` and `E(7) > 0`. (B) No convexity: exact evaluation for `p = 1..23` (all positive, minimum at `p = 7`), and for `p >= 24` the bound `E >= p·c1 + c0` from `exp(x) >= 1+x` with `c1 >= 1.450277187` and `24·c1 + c0 >= 116.699003021`. The clamp and `B` only raise `E`. `E_d` decreases in `d`, by `p·m^a` per extra rank-one deletion. |
| 3.8 | Rejection persists at any larger required saving (line 151) | valid | Each child cost `r(m/r)^a` is nondecreasing in `a` because `r <= 9 < m`. Residual rank-`m` children cost `m` whatever `a` is. |
| 3.9 | `-4.55707137 < E_426(7,1/596) < -4.55707136`, `D_{426,1} = 890` (lines 153-158) | confirmed | Value -4.557071360876949… (truncated toward zero; enclosure in RESULT.json), inside the interval. The clamp is inactive (`J_0(7) = 129510`). 426 also passes at `κ`: `E_426(7,κ) = -5.455691507045708…`. |
| 3.10 | `1/596 > κ` and `a/(1+a) = 1/597 > κ` (lines 160-162) | confirmed | Exact rational comparison. |
| 3.11 | "Four additional normalized cost units still pass; five already fail" (lines 162-163) | valid as scoped; clarified | PR3620 states this at `p = 7`, `a = 1/596`, where it holds: `E_426(7,1/596) + 4 < 0 < E_426(7,1/596) + 5`. Context: at `(p = 8, a = 1/596)`, `E_426 = -5.040108017937…`, and at `(p = 7, a = κ)`, `E_426 = -5.455691507045…`, so five units pass at those points. That matters only for the readings in 3.12. |
| 3.12 | "the abstract profile's total extra-cost allowance is only 4.557071360876949…, across the entire seven-pair bill" (lines 163-164) and "leaves less than 4.558 units" (line 7); PR3620's README `research/p104-caller-feasibility/README.md` lines 35-38 | valid as scoped; clarified | Valid as scoped: lines 163-164 are scoped to the seven-pair bill at `a = 1/596`, and line 7 inherits `a = 1/596` from line 155. Context for quoting them (all optimistic ceilings under the named law, truncated toward zero). Under the retained limiting conversion `κ = a/(1+a)` (bottleneck brief; PR3620's "outer ratio"), an improvement needs `a > a_req = κ/(1-κ)`; `E` increases in `a` (3.8), so the sharp ceilings are the values at `a_req` (suprema, not attained), and values at `κ` are looser rejection-side figures. For `d = 426`, `E` is strictly convex in `p`; the passing set is `6 <= p <= 10` at `1/596` and `6 <= p <= 11` at `a_req` (also at `κ`). (i) For an extra cost proportional to the number of dual calls, the best pair count is p = 7: 0.710094403780 per dual call at `a_req`, 0.651010194410 at `1/596` (0.779384501006 at `κ`); charged per call of either kind (`2p+1`), p = 7 is also best (0.331377388430 / 0.303804757391 / 0.363712767136). So PR3620's seven-pair point is the binding pair count for such costs. (ii) At p = 7 the ceiling at `a_req` is 4.970660826462, more than the 4.557071360876 at PR3620's test point. (iii) A purely fixed extra cost is best at p = 8: 5.524500277810 at `a_req`, 5.040108017937 at `1/596` (6.092563673846 at `κ`). (iv) A mixed cost `c0 + c1·p` passes iff `c0 + c1·p < -E_426(p,a)` for some `p`; a large fixed part can make p = 8 the only passing count (at `a_req`, `5 + 0.05p` passes only at p = 8; at `1/596`, `4 + 0.1p` passes only at p = 8). |
| 3.13 | Fixed `p = 4`: 427 fails at `κ`, 428 passes at `1/596` (lines 164-165) | confirmed | `E_427(4,κ) = 1.740333669596917…` and `E_428(4,1/596) = -1.822408282623730…`. |

## Consequence

The decision quantity that PR3620 supplies to the P104 gate holds under its
conditions. With PR3609's dual and the named law, a realised correction that
deletes at most 425 rank units per dual call fails at every pair count and
with every finite number of fully paid banks. Deleting 426 rank-one children
in every dual call is the least uniform per-call deletion that passes the
relaxation, and it passes for 6 <= p <= 10
at `a = 1/596` (6 <= p <= 11 at `κ/(1-κ)` and `κ`). This covers corrections
that act by rank-unit deletion from D; other replacement profiles must pass
PR3620 section 2's criterion. The excess depends only on the total deletion
over the `p` dual calls: with uneven calls, a total of `7·425+3 = 2978` passes
at `p = 7` (at both `a_req` and `1/596`; 2977 fails), so some call must delete
more than 425 but not every call must reach 426.

PR3620's slack sentences are correct as scoped. How to quote them: the
figures are optimistic ceilings under the named law, not realised allowances.
The retained conversion `κ = a/(1+a)` fixes the requirement `a > κ/(1-κ)`, so
the sharp ceilings are the values there. For a correction whose extra cost is
proportional to the number of calls, such as a deletion network in every dual
call, seven pairs is the best pair count and the ceiling is about 0.710094
units per dual call (0.651010 at PR3620's `1/596`); at seven pairs the total is
4.970660 (4.557071 at `1/596`). A purely fixed extra cost is best at eight
pairs (5.524500, or 5.040108 at `1/596`), and a mixed cost passes iff
`c0 + c1·p < -E_426(p,a)` for some `p`. None of this changes the 426 threshold
or the qualitative stop decision.

Tiny reproducer for the fixed-cost reading in 3.12(iii) (from the repository root):

```sh
python3 -I -B -c "import sys; sys.path.insert(0,'research/p104-consumer-threshold-audit'); import verify as v; F,D,_=v.load_sources(); print(v.model_excess_A(v.default_params(F,D), 8, 426, v.A596)[1] + 5 < 0)"
```

It prints `True`: at `p = 8`, `a = 1/596`, adding a fixed five units to the
426-deletion bill still passes. The per-call reading 3.12(i) is the claim
`finding_d426_per_dual_call_slack_max_at_p7` in `verify.py`.
