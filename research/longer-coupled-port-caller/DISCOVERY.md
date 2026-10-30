# Longer coupled-port search

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

This file records discovery steps. The final result is in PROOF.md.
No new kappa is established.
Base: 6cf7a683f447b9f1e2333791907fd92be5009a63.
Claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/5593#discussioncomment-19186397

## A useful necessary condition

Work in characteristic two. Let R_i be square-zero matrices and let their
sum be a diagonal projector E. Let P_i be diagonal coordinate projectors
with P_i R_i = R_i P_i = R_i. A coordinate on which E is one must occur in
at least three P_i.

Proof: zero occurrences fail the diagonal equation. With one occurrence,
the row and column of that R_i are those of E, so its square has diagonal
entry one. With two occurrences, call their row vectors a and e_j+a,
and their column vectors b and e_j+b. Square zero gives a*b=0 and
(e_j+a)*(e_j+b)=0. But a_j=b_j, so the latter expression is 1+a*b=1.
Both cases are contradictions.

For full rank-q queries in rank-2q coordinate supports, 3*rank(E) is at
most 2*q*L. The proof does not assume separate ports or any chronology.
If every full call has a private stage axis, the target basis makes its
projector diagonal. Thus this condition applies at every coupled rank.

A second consequence applies when each stage occurs twice and has no
rank loss. Its two rank-2q projectors sum to a rank-4q idempotent. The
projectors are orthogonal. The sum of the two compatible queries is
square zero and is supported on the diagonal target stage projector.
The same three-occurrence argument applies to these grouped queries.
It rules out full stage capacity whenever 3*N > 2*q*L, at all lengths
and all coupled ranks. No chronological assumption is needed for this
necessary condition. Rank losses and noncommuting local projectors need
further work.

## Query frame complement

For sum R_i = I_N, equal rank q, write R_i=U_i V_i with V_i U_i=0.
Set U=[U_i], V=[V_i]^T, K=VU. Then UV=I and C=I-K is an idempotent
of rank h=q*L-N, with q by q identity diagonal blocks.
Factor C=A B, BA=I_h. Each B_i A_i is a rank-q idempotent and their sum
is I_h. When L is even, the complementary idempotents I_h-B_i A_i
have rank h-q and also sum to I_h. Therefore L*(h-q)>=h. In particular,
N<=q*L-q-ceil(q/(L-1)). The trace condition also requires N even over F2.
These are necessary frame conditions, not a caller construction.

## Numerical discovery screens

The initial screen used the pinned PR5599 local invoice. It assumed all
2*q*L stage incidences could be used and distributed them as evenly as
possible. For q=104, eight calls on 720 fields appeared to have a raw
crossing near .00348661. That frame is impossible: h=112, while the
complement inequality requires 8*(112-104)>=112. Other paired-stage
screens also lose capacity before an operator is built. These floating
numbers are rejected discovery hypotheses, not kappa claims.

## Next experiments

The remaining construction must use noncommuting local stage projectors
and pay for lost stage capacity, or change another stated hypothesis.
The current search keeps the local P104 supplier and independent helpers.
Use PR5631's mixed chronology condition before a full word replay.

## Completed continuation

The initial finite search checked 24^3 coupled splits in each of 144
two-sweep orders: 1,990,656 assignments, with no chronology survivor.
The rank-two coupled search used Z3 5.3.2.0 on 144 orders and found all
unsatisfiable; this result alone was not used as a proof. Exact free-algebra
witnesses then covered all 75,600 order types, with no matrix-size bound.
The final theorem and its reduction are in PROOF.md.

DISCOVERY-RESULTS.json.gz preserves all five JSON discovery reports. Its
SHA256 is ec6fbe62a74cb05750db45c24c2a14ca18cb6b4f6bfb88a8151b76df40120ef8. The retained scripts
can regenerate these reports. The registered checker uses only the exact
order witnesses and standard-library matrix checks.

Commands, from the repository root:

```sh
python3 -B research/longer-coupled-port-caller/search_star.py
python3 -B research/longer-coupled-port-caller/search_orders.py --degree 2
python3 -B research/longer-coupled-port-caller/nc_star.py --degree 3 --limit 144
python3 -B research/longer-coupled-port-caller/build_certificates.py
```

The optional search_coupled.py command requires z3-solver==5.3.2.0. It is
not a verification dependency. Its finite negative output is superseded
by the exact algebra certificates. The numeric invoice screens do not
supply an operator, compiler or kappa result.
