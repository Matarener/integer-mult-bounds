# Trace preservation and complete invoice change

## Domain and premise

Use a vector space over the rationals, or a module in which the source dyadic coefficients are defined. Give each input role an independent formal column. Public inputs and initial dirty owned inputs are arbitrary. INIT and CLEAR are the explicit owned erasure operations. This proof does not remove that framework assumption.

For the native lift, assume each frame f has an invertible linear map U_f. Assume an actual MOVE from frame a to frame b acts as U_b U_a^-1, and each scalar operation acts on operands in the same frame. Then the decoded value U_f^-1 x is unchanged by MOVE. A coframed scalar ADD, COPY or SCALE has its stated scalar action on decoded values. These are premises, not consequences of the finite trace audit.

## Trace invariant

Let d be one of the three distinct destinations, and let h be its new owned sum. At INIT, h is zero. Between INIT and delivery, maintain

    old[d] = new[d] + new[h].

All other old roles equal their new decoded values. For each selected update `d += c*s`, the new word performs `h += c*s`. The verifier compares the exact value of s in the two executions at that instruction. Thus both sides of the invariant change by the same value. The source can change between updates; no stored-source assumption is needed.

The verifier rejects any read, other write, SCALE or MOVE of d in this interval. It also checks the old interval for such operations. Unrelated instructions therefore preserve the invariant. The one native query on h changes its frame but preserves its decoded value under the premise above. The unit delivery `d += h` restores equality of d. CLEAR then removes h. All new owned inputs are erased before use and returned to zero.

The verifier derives these lifetimes from all uses of the three new roles in the final word. It does not trust the constructor's node list. Removing the new administrative operations and replacing each selected sum destination by d recovers the entire original scalar instruction sequence. All actual source reads, SCALE observations and 23 COPY values are checked as exact rational coefficient rows. An induction on that sequence proves the relation for every input column, not only the live shear columns.

A second replay checks the complete formal endpoint of each source word. It is identity on public helper roles, the required 104 disjoint shears on the main roles, and zero on the returned owned roles. It also checks all frame states and directions. These checks establish the decoded finite result. Under the native premise they establish the same trace relation for any common column module. They do not verify the implementation of U_f or its all-size realization.

## Why the trace check is needed

Insert `o += d` before delivery and `o -= d` before any further change of d. The two extra instructions cancel, so both complete matrices can remain correct. The first read nevertheless observes different values in the two programs. A final matrix test alone cannot establish that source reads or COPY values have been retained. The separate dense oracle constructs this case and the trace check rejects it.

## Signed invoice

Write H_r = r^t and H_0 = 0, with 0 < t < 1. The new local paid histogram changes by

    -6 H_1 + 4 H_2 + 2 H_6 - 2 H_7.

The helper target histogram changes by

    -2 H_1 + 2 H_2 + 2 H_7 - 2 H_8.

The gain in targets minus paid terms is therefore

    2 ((2 H_1 - H_2) + (2 H_7 - H_6 - H_8)).

Both terms are strictly positive by strict concavity, with H_0 = 0 for the first term. The exact integer prefix check in the receipt is an equivalent majorization certificate. Independent helper endpoints are allowed in the source contract; the audit checks their proper nested spans and charges their actual target ranks. All 208 inherited main endpoint frames remain fixed.

The pinned p16/a7 caller uses 18 local calls, 15 times 104 rank-one query shears, and the two seven/eight-step idle chains. The verifier reconstructs every rank in its complete paid and target histograms. Thus the full recursive gain is 18 times the local gain. The complete paid count falls by 36, while the target count and rank surplus remain fixed.

The nonrecursive bill also changes. The verifier uses the positive source scalar tariff, counts every owned lifetime, and includes both helper normalizers, both main adapters and the source route allowance. It does not infer a free CLEAR or a free sum query. The recorded scalar and route increases must remain in any final bound. This proof establishes a strict recursive invoice gain, not a new complete kappa value.

## Remaining obligations

The unchanged physical caller receipt is checked byte-for-structure against both sources; its action is not independently replayed here. Native all-column realization, owned erasure, compiler, precision tape and analytic recovery retain their framework status. A complete supplier admission must resolve those obligations at the exact candidate head. The audit does not change the selected result.
