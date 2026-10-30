# Caller-bound reservoir placement for the balanced CRT

This audits Section 3 of Cinna Davis's
[PR4100 CRT construction](../unconditional-batched-crt/CRT.md), retained at
`337d04939571a637aeab54a0f58f54fde811663a`. Its actual caller is the three
padded conversions in [PROOF.md, “Address isomorphism”](../unconditional-batched-crt/PROOF.md).
The result supplies the dependency, placement and coordinate bookkeeping
required before a compact switch batch. It does not certify the complete
CRT machine or its time bound.

Generic reservoir exchanges, coordinate conjugation and recoloring are
predecessor methods: see Vlado Vojdanovski's
[PR1673 support router](../capped-phase-fusion/SUPPORT-ROUTER.md), lines 84–104,
and Jose Manuel's [physical support router](../physical-support-router/PROOF.md),
lines 110–146. Here the source functions may depend on entire CRT child
groups, so avoiding the two endpoints of a matching edge is insufficient.

## 1. Quantified layout and dependence

Let `p` be a positive integer, `d` a power of two with `d>=51200`, and let

```
ell >= max(2, ceil(log2(p+2))),
w_i in {ell-1,ell} for i=0,...,d-1,
L = sum_i w_i,
G = 64(ell+ceil(log2(p+2))),
r_max = floor(L/(100G)),  H = r_max G.
```

All fields range over their complete binary domains, including invalid
padded CRT coordinates. No borrowed field is initialized.

Number physical positions from the front of the address, starting at zero:
position `v` is integer bit `L-1-v`. Logical axes occur in physical order
`d-1,...,0`. Axis `i` occupies

```
I_i = [a_i,a_i+w_i),  a_i = sum_(k>i) w_k.
```

Its local arithmetic bit `q` is at physical position `a_i+w_i-1-q`.
Consecutive logical groups remain contiguous physical intervals.

Fix one balanced tree level and one synchronized Beneš switch layer.
For a right-child axis `i`, let `A(i)` be its node's left-child axes.
The caller's control `f_i` depends only on `A(i)` and the non-target
bits of axis `i` (`CRT.md:78–92`). The conservative dependency region
is the union of the *whole* axes `A(i) ∪ {i}`. This overapproximation
also includes the target bit for allocation purposes. The actual control
omits that bit and every other active target at this layer.

The promised conclusion is a partition into at most 25,600 batches,
each with at most `r_max` targets, and an explicit placement of three
complete `H`-bit fields omitted by every control in the batch.
Three disjoint equal-width exchanges suffice for placement and three
for restoration. All original axes admit a reconstruction descriptor
with at most `d+12` fragments after placement.

## 2. Integer budget and number of batches

Since `ell>=2` and `G<=128ell`,

```
L >= d(ell-1) >= d ell/2,
L/(100G) >= d/25600 >= 2.
```

For real `x>=2`, `floor(x)>=x/2`; hence

```
r_max >= d/51200 >= 1,   H>=G,   H<=L/100.                 (1)
```

At a nonroot tree level, each node lies entirely within one logical
global half. Separate targets by that half. Each half contains exactly
`d/4` right-child axes, possibly with identity switches in the padded
schedule. Partition each list into consecutive batches of at most
`r_max` axes.

At the root, the target axes are the right half `[d/2,d)`. Split them
into `[d/2,3d/4)` and `[3d/4,d)`, and partition each quarter in the same
way. Both cases therefore use at most

```
2 ceil((d/4)/r_max) <= 2*12800 = 25600                    (2)
```

batches per synchronized switch layer. The partition of axes may be
reused at each switch layer of the tree level. Formula (2) is a constant
batch bound, not a claim of only 25,600 batches for the entire CRT.

## 3. A contiguous omitted interval

For a nonroot batch, choose the opposite global half as the reservoir
interval `I`. Both each active axis and its entire left child are in the
batch's own half, so `I` is disjoint from every conservative dependency.

For a root batch, choose the inactive quarter of the right half as `I`.
The common left-child controls lie in `[0,d/2)`, and each active axis lies
in the other right quarter. Again `I` is disjoint from every dependency.
Choosing the *left half* at the root would fail this argument: it supplies
the modular-rotation offsets through `k_A`.

Each chosen interval contains at least `d/4` axes. With arbitrary allowed
width assignments, not just equal widths,

```
|I| >= (d/4)(ell-1) >= d ell/8 >= L/8.                    (3)
```

This reasoning depends on coordinate positions, not coordinate values.
Invalid padded addresses, and tests for invalid left-child values, do
not introduce dependencies outside the same left-child axes.

## 4. Three literal disjoint exchanges

The destination fields in physical coordinates are

```
U=[0,H),  T=[H,2H),  B=[L-H,L),
D=U ∪ T ∪ B.
```

They are disjoint by (1). Let `J=I ∩ [2H,L-H)`. This intersection is a
single interval, and removing the end regions costs at most `3H`.
Consequently

```
|J| >= L/8-3H >= 9.5H.
```

If `J=[j0,j1)`, set `s=H ceil(j0/H)`. Alignment loses less than `H`,
so `[s,s+3H)` lies inside `J`. Use the adjacent blocks

```
S_k=[s+kH,s+(k+1)H),  k=0,1,2,
```

and exchange them respectively with `U,T,B`. All six blocks are mutually
disjoint. Each exchange is a coordinate translation on its two blocks
and identity elsewhere; their product `P` is an involution. In particular,

```
P^-1(D) = S_0 ∪ S_1 ∪ S_2 ⊂ I.                           (4)
```

No source is overwritten by a preceding placement swap. This construction
does not require `H` to divide `L`, any axis width, or an endpoint of `I`.
Alignment is merely a convenient explicit choice.

## 5. Transported controls and split-axis descriptors

Use the convention that the bit originally at `v` moves to `P(v)`.
For the placed address `z=P(x)`, define

```
f'_i(z) = f_i(P^-1(z)).
```

Equation (4) and dependency avoidance show that `f'_i` omits all three
destination fields. Every active target is outside the source blocks,
so its image lies in the middle field `Y=[2H,L-H)`. If its image has
physical position `v'`, its arithmetic bit index within that field is

```
j_i = L-H-1-v'.                                           (5)
```

Recompute these indices before guard coloring. Original physical
positions, global integer bit indices and the local indices in (5)
are different quantities.

Placement can split an axis. Cut the original axis partition at every
endpoint of the six exchanged blocks. There are at most twelve additional
cut points, so the refined partition has at most `d+12` fragments.
On every fragment `P` is a translation or the identity. Record its
original axis, original local interval and translated physical interval.
Reading the translated fragments in their original order reconstructs
each original axis exactly, with its original bit significance.

This gives a complete descriptor for inverse coordinate interpretation;
whole axes need not remain contiguous. Only the axes needed by a control
must be reconstructed to evaluate it. Their fragments never enter `D`.
The descriptor contains `O(d)` intervals with `O(log(L+1))`-bit endpoints.
This size bound does not assert a full fixed-tape control-generation tariff.

## 6. Restoring every dirty address

Let `A` be the ideal simultaneous switch on the batch's original target
positions. Assume the invoked, completed switch implementation on the
placed fields realizes exactly

```
A' = P A P^-1
```

on **every** address. Its source functions and target positions are those
above. Then placement, execution and inverse placement have endpoint

```
P^-1 A' P = A.
```

Since `A` changes only active targets, every original borrowed coordinate
and every other non-target coordinate returns to its initial dirty value.
This includes all invalid padded addresses and arbitrary record payloads.

The all-address premise is essential. For the compact implementation it
means the completed macro **including exceptional repair**, not its raw
word restricted to good states. The preceding
[PR4169 arbitrary-source audit](https://github.com/CrocSwap/integer-mult-bounds/pull/4169)
addresses that separate algebraic boundary; it is context, not an imported
executable dependency here. Any implementation satisfying the stated
all-address contract suffices. Elementary tail switches remain a separate
callee obligation.

## 7. Scope, verification and credit

The quantified argument establishes the CRT caller's field availability,
omitted dependencies, exact position transport, constant batch bound and
conditional full-state restoration. Finite allocator and reconstruction
checks corroborate their implementations; they do not replace the proof.
Testing reduced examples outside (1) cannot establish the stated asymptotic
family, and the production constants must not be silently reduced in it.

The placement invoice is at most six width-`H` ordinary exchanges per
batch, in addition to the switch's own operations. No exchange is free.
This package does not implement or reprove the ordinary callee, the
large-guard control evaluator, exceptional sorting, last-`K` tail branch,
complete time/space tariff, numerical precision, or multiplication theorem.
It does not change the selected frontier.

Cinna Davis supplies the audited construction and its original reservoir
claim. Vlado Vojdanovski, Jose Manuel, RaD/hipotures, Zhihao Chen,
Douglas Colkitt and the retained routing/compact-control lineage retain
their predecessor credit. This scoped audit is by Hiroki KUMAZAKI
(@kumagi), with substantial OpenAI Codex assistance, under Apache-2.0.
It is neither independent human review nor proof-assistant formalization.
