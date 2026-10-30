# Commuting full calls need at least half as many thin maps as leaves

Retain the paired-star contract in PROOF.md. Suppose all full-call projectors
commute, including projectors from different stages. Thin maps can still be
arbitrary and can have any rank.

**Theorem.** A successful word needs at least `ceil(g/2)` thin maps.
This count is sharp when their ranks are unrestricted.

## Proof

For g>=2, each full projector commutes with every other full-stage support E_k.
For a different star edge k, this forces its off-diagonal block B to zero.
The remaining A projectors commute. Commuting idempotents have a common
eigenbasis over the base field, since each minimal polynomial divides
`x(x-1)`. Use this same basis on the core and all leaves.

Fix one coordinate in that basis. Exactly one half of each stage acts on
this coordinate. Read these g active stage events in chronological order.
The pure stage prefix is diagonal. Its entries are monomials in the
independent D_j. The e coefficient of the whole word, after removal of
its pure stage product, is exactly

```text
sum_i prefix_i^(-1) R_i prefix_i.
```

This calculation is in the Laurent polynomial ring. The original polynomial
ring embeds in it, so an exact equality here proves the original endpoint.

For the entry from leaf j to the core, the full query in stage j contributes
one monomial. Its exponent records which other stage events precede j.
The D_j exponent cancels because both endpoints receive D_j together.
A thin map can cancel this term only if it occurs immediately before or
after event j in the induced active-event sequence. Every other gap has a
different monomial in the independent stage variables. There is no other
full query in this matrix entry.

One thin map lies in one gap of this sequence. It can therefore cancel the
required entry for at most the two neighboring events. The target has zero
in every such off-diagonal entry. All g events need a cancellation, which
gives `2m>=g`. Cross-coordinate entries in thin maps cannot alter this
argument: diagonal conjugation preserves each matrix entry separately.

For g=1, no thin map would leave the full query sum T_1, which is not I.
Thus at least one thin map is required in that case too.

This excludes five thin maps at both 13 and 31 leaves, regardless of their
ranks or the number of coupled ports. Those targets need noncommuting full
projectors, a changed stage frame, or a different endpoint contract.

## A complete construction at the count bound

Choose the same coordinate half projection A in every stage and B=0.
Run both halves of stage 1, then both of stage 2, and continue in order.
After each odd-numbered stage j, insert one thin map. If j<g, it contains
both directions between the core and leaves j and j+1, with identity blocks
and no other entries. If j=g, use only leaf j. For even g, also put identity
on the core diagonal of the first thin map.

The map between stages j and j+1 cancels both full-query off-diagonal terms
in the normalized Laurent sum. The last singleton cancels its own terms.
The diagonal full-query sum is I when g is odd. When g is even, it lacks
the core identity, which the first thin map supplies. The resulting sum is
exactly I. The pure stage product is the required diagonal product. Thus
the complete endpoint is correct for every g>=1 and every q>=1.

Every thin map has rank 2d=4q, including the even-g correction and singleton.
There are `ceil(g/2)` maps. They are not asserted to have square zero.
An arbitrary rank decomposition gives the stated rank-one query tariff;
native transport and frame costs are separate. The complete recursive price
loses for g>=3. This is a sharp map-count construction, not a profitable caller.

## Exact replay

WORD31.json contains all matrices and their order for g=31,q=2. The checker
first checks projectors, ranks, resolutions and each prescribed query.
It then collects every Laurent monomial in every matrix entry. Exactly the
128 diagonal identity terms remain. There is no truncation of stage degree.

A separate literal interpreter evaluates the dual-number word on a Cartesian
grid of three distinct F4 values per stage. Each stage occurs twice, so its
degree is at most two. Polynomial interpolation makes this a complete check
for the small fixtures, including the retained noncommuting eight-field word.
The control `D^2+D` shows why the two binary values alone would be insufficient.
Deleted and moved thin queries fail the long endpoint check.

The count argument and sharp construction are part of the present research.
Credit the retained star contract and source lineage in PROOF.md. Ali Romman
with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
