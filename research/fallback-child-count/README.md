# Sharp fallback child count for the retained BIT fallback program

FALLBACK.md in `research/unconditional-batched-crt` (#4100) bounds the
fallback program at m = 64 by 16637 swaps and 3 × 16637 = 49911 reversed
children. PR4215's second open question notes that the bound is not sharp:
under `paid_children`, a swap between opposite banks uses one child, not three.
This package gives the exact count for every header and its sharp maximum:

```text
m = 64, f >= 2:  at most 33269 children   (FALLBACK.md: 49911)
                 at most 16637 swaps      (FALLBACK.md's count is attained)
```

Claim type: **scoped proof with a finite certificate**. It concerns one
tape-cost term. No new κ, no audit of the rest of #4100, no supplier admission
and no change to the selected frontier.

## Setting

Use the retained program `vendor/fallback_program.py` and
`vendor/descriptor.py` from `research/selected-bit-recursive-closure`,
unchanged. Fix an odd prime q, w ≥ 1, R = Z/q^w, 2 ≤ m ≤ 64, an invertible
header chart and r = |axes| with 1 ≤ r < m. Then P is a rank-r idempotent
modulo q. `prepare` eliminates the 2m × 2m residual
`[[I-P, PC], [CP, I-CPC]]` with the unnormalized rule from `elimination`. At
step k it takes the first row p ≥ k with a unit in column k, swaps it to k if
p ≠ k, then clears column k in every other row. `compile_program` then emits:

- two swaps (i, 2m−1) for each i < 2m−1 (the diagonal-pair word);
- one swap for each elimination swap;
- two swaps around each upper shear i < k. Every ordered slot is kept, so
  there are exactly m(2m−1) of these.

Positions below m form the head bank and the rest form the tail bank. Under
`paid_children`, a swap within one bank pays one child of width f, plus two
children of width ⌊f/2⌋ when ⌊f/2⌋ > 0. A swap between banks pays one child
of width f.

## Theorem

Let s be the number of same-bank elimination swaps. Then:

1. **Rank law.** The elimination makes exactly r opposite-bank swaps, and
   s ≤ 2m − 1 − r.
2. **Closed forms.** The program has `N = (2m−1)(2m+2) + r + s` swaps.
   Of these, `S = 2(m²−1) + s` are same-bank. For f ≥ 2 it pays
   `N + 2S = 8m² + 2m − 6 + r + 3s` children, and for f = 1 it pays N.
   The total child width is `fN + 2⌊f/2⌋S`.
3. **Sharp maximum.** For every header, `N ≤ (2m−1)(2m+3)` and
   `S ≤ 2(m−1)(m+2)`. So there are at most `8m² + 8m − 11` children
   when f ≥ 2, and the width is at most `f(2m−1)(2m+3) + 4⌊f/2⌋(m−1)(m+2)`.
   All three bounds are attained together by the rank-one header with chart
   `G = I + (1 − e₀)e₀ᵀ`, where 1 is the all-ones vector, so P = 1·e₀ᵀ. This
   holds for every odd q, every w and every 2 ≤ m ≤ 64.

At m = 64 this gives 16637 swaps, 8316 same-bank swaps and 33269 children,
with width `16637f + 16632⌊f/2⌋`. For f = 1 the count is 16637, so
FALLBACK.md's swap count is sharp. For f ≥ 2 its child bound exceeds the
maximum by 16642. Both counts are below the retained allowance 32·64² = 131072.

## Proof

*Fixed slots.* The diagonal-pair word has 2(2m−1) swaps. Partner 2m−1 is
in the tail bank, so the m−1 indices i ∈ [m, 2m−2] give 2(m−1) same-bank
swaps. Upper shears give 2·m(2m−1) swaps. A pair i < k lies in one bank for
2·C(m,2) = m(m−1) of them, which gives 2m(m−1) same-bank swaps. Adding
these up gives (2m−1)(2m+2) fixed swaps, of which 2(m−1)(m+1) are same-bank.
Item 2 follows by counting children per swap.

*Reduction to F_q.* An element of R is a unit exactly when its residue mod q
is nonzero. Every pivot decision therefore depends only on the image mod q,
and that image follows the same elimination over F_q.

*Rank law.* During steps k < m, the head positions k..m−1 hold only
original head rows that have not been used. A swap at an earlier step j < k
moves a row from position j to position p. If p < m, the moved row is an
original unused head row. If p ≥ m, the moved row leaves the head bank.
Restrict all rows to the first m columns. The head rows span H = rowspace(I−P),
of dimension m − r. Let V_k be the span of the pivot rows chosen before step k.
This span is in echelon form on the first k coordinates, so V_k ∩ Z_k = 0,
where Z_k is the set of vectors vanishing on those coordinates. The reduced
unused head rows lie in Z_k, and together with V_k they span H + V_k. Hence
they span a space of dimension D_k = dim(H + V_k) − k.

At step k a head pivot exists exactly when some reduced unused head row has a
nonzero k-th coordinate, and the elimination then takes it, because head
positions come first. In that case the new pivot lies in H + V_k, so
D_{k+1} = D_k − 1. Otherwise every reduced unused head row lies in Z_{k+1}.
The chosen tail row t then has t_k ≠ 0. If t were in H + V_k, its
representative in Z_k would lie in the span of the reduced head rows, and
hence in Z_{k+1}. That would be a contradiction, so t ∉ H + V_k and
D_{k+1} = D_k. Since D_0 = m − r and D_m = 0 (V_m is everything), exactly
m − r head-phase steps take a head pivot and exactly r take a tail pivot.
Each tail pivot comes from a position p ≥ m > k, so it is an opposite-bank
swap. Tail-phase steps k ≥ m can only swap within the tail bank. The final
step 2m − 1 cannot swap. So there are at most 2m − 1 elimination swaps,
and s ≤ 2m − 1 − r.

*Maximum.* By item 1, r + s ≤ 2m − 1 and s ≤ 2m − 2, which gives both
bounds in item 3. For the witness, `verify.py` runs the elimination of the
integer residual of P = 1·e₀ᵀ over Q. Every entry stays in {−1, 0, 1}
throughout, for every 2 ≤ m ≤ 64, and the swaps are (k, k+1) for
k = 0..2m−2. Since 0 and ±1 keep their unit status modulo every odd prime
power, the modular run is the reduction of this one. It therefore makes
2m − 1 swaps, the single opposite one at k = m−1, so r = 1 and s = 2m − 2. ∎

## Evidence

`verify.py` imports the unchanged retained program after checking the SHA256
pins in `SOURCES.json`. It checks the following:

- **Witness family.** For every 2 ≤ m ≤ 64, the integer replay passes. Then
  `prepare` and `paid_children` are run with f ∈ {1, 2, 3}: on (q,w) = (3,1)
  for every m, and also on (3,2), (5,1) and (7,2) at m ∈ {2, 3, 64}. Each run
  matches the closed forms and attains the maximum.
- **Complete censuses.** For (q,m) = (3,2), (3,3), (5,2) and (7,2), every
  invertible chart with axes 0..r−1 is enumerated. This yields all 332
  rank-r idempotents, and the number per rank is checked against
  q^{r(m−r)}·[m choose r]_q. The rank law and closed forms hold on each one.
- **Seeded headers.** Twenty-four seeded random m = 64 headers with ranks
  from 1 to 61 satisfy the same law. These are a control, not a proof.
- **Controls.** FALLBACK.md's 16637 and 49911 are recomputed, and the witness
  attains 16637. The bank interchange `[[0, I], [I, 0]]` is invertible but
  makes 64 opposite swaps, so the rank law depends on the residual structure.

Observation, not proved: in every census the largest s for rank r is
2(m − r). If that held in general, the exact rank-r maximum would be
8m² + 8m − 6 − 5r.

Reproduce from the repository root with any CPython 3.12:

```sh
python3.12 -W error -B research/fallback-child-count/verify.py
python3.12 -W error -O -B research/fallback-child-count/verify.py
```

The expected status is `PASS_FALLBACK_CHILD_COUNT`. Each command takes about
25 seconds locally.

## Limitations

The result counts the children that `paid_children` charges for the
retained program. It does not execute the physical reversals, price
preparation or parking, or decide which headers reach the fallback in the
recursion. It also does not audit BIT.md's recurrence or any other #4100
premise. The maximum is attained only at rank one in the censuses, so a
caller's actual toll may be lower. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

1. Prove s ≤ 2(m − r) for every rank-r header, or find a counterexample. This
   would give the exact rank-dependent maximum 8m² + 8m − 6 − 5r.
2. Bind the auxiliary BIT recurrence's fallback branch to its header ranks.
   Then substitute the rank-dependent count for the uniform 49911.

## Credit

This package was produced by Nick Petalas. The fallback program, descriptors
and covariance algebra are retained from source527, commdata2338, Ross
Richardson (PR2159/PR2188) and Jose Manuel's continuation. FALLBACK.md and its
49911 bound come from #4100. The question was raised in PR4215 and in the
open questions of PR4228's package. Apache-2.0.
