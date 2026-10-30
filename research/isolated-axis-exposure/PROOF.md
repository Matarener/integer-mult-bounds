# Isolated-axis exposure by complete B1 calls

Nick Petalas. Apache-2.0.

## Exact contract and result

An axis order is a permutation of the distinct labels `0,...,p-1`.
At a completed boundary, one B1 call exchanges two disjoint contiguous
intervals of equal positive length `b`, preserving order inside each
interval and fixing the prefix, intervening gap and suffix. It has the
binary-stream endpoint `[P][2^b][G][2^b][S]`. All packet data and complete
spectators are present. This is the interface of the pinned PR2899
`binary.py` and PROOF section 7. We use its endpoint as a contract; we do
not reprove its conditional physical implementation.

Fix disjoint sets of positions `S={s_1,...,s_g}` and `T={t_1,...,t_g}`,
with `g>=1`, such that no two positions in `S union T` are adjacent.
Specify the ordered exposure `s_i -> t_i`. An allowed completed extension
fixes every position outside `S union T`. Equivalently, its support has
at most `2g` positions: the prescribed exposure already forces all these
`2g` positions to move. Calls between the initial and final boundaries
may move arbitrary other positions.

**Theorem.** Every such completed extension requires at least `g` B1
calls. The minimum over allowed extensions is exactly `g`, attained by
the disjoint single-bit exchanges `(s_i,t_i)`. The theorem does not say
that every completion has a `g`-call factorization.

## Four-cut invariant

For an order `a`, append the fixed sentinels `-1` and `p`. A bond is an
adjacent pair `(x,y)` with `y=x+1`. Let `B(a)` be the number of adjacent
pairs that are not bonds, including both sentinel boundaries. Initially
`B=0`.

Write one equal-block exchange as

```
A X M Y Z -> A Y M X Z,       |X|=|Y|=b.
```

Every adjacency internal to one displayed segment survives. Only the
four joins between segments can change. Empty exterior segments use the
sentinel joins. If `M` is empty, there are only three joins. Consequently

```
B(after) <= B(before)+4.
```

This is valid for every intermediate permutation, irrespective of which
spectators have moved. After `k` calls, `B<=4k`. The argument is an
elementary cut count, not a new general permutation-sorting theorem.

At a completed allowed exposure, each position in `T` contains its
specified, different source label. All original source labels have
therefore left `S`. Since positions outside `S union T` are fixed, the
remaining labels at `S` are exactly the original target labels, in some
order. Every position of `S union T` moves.

For a moved position `j`, its neighbors are fixed because support is
isolated. If its new label is `x!=j`, neither `(j-1,x)` nor `(x,j+1)`
is a bond. The same argument uses the sentinel at either endpoint.
These two joins are distinct for all `2g` moved positions. All other
joins are unchanged bonds. Hence `B=4g` for every completion. It follows
that `4g<=4k`, or `k>=g`.

For the upper bound, apply the `g` disjoint exchanges `(s_i,t_i)`, each
of width one. Their product has the prescribed exposure and fixes all
other positions. Thus the minimum is `g`.

## Complete-scan consequence

Suppose an adapter realizes this exposure solely by sequential completed
calls to the existing B1 binary wrapper on the whole same-volume packet.
Each call returns a distinct owned output of `V` payload bits. Materializing
that return alone costs at least `V` writes in the unit-head-step model.
The implementation also pads, restricts and transfers complete packets;
none of those extra passes reduces this lower bound. Consumed outputs
can be reused between calls, but they must first exist.

The adapter therefore costs at least `Vg` writes. Conversely `g`
width-one calls cost `O_q(Vg)` under the retained fixed-prime B1 contract.
This proves a sharp `Theta_q(Vg)` worst-case tariff for this black-box
adapter contract, conditional only for the implementation's upper bound.
It cannot meet `O_q(V g^(1-a) (log g)^C)` for any fixed `a>0` and fixed
`C>=0`, since `g^a/(log g)^C` is unbounded.

This is a call-boundary lower bound. It does not charge a new fused
physical router as a succession of completed B1 outputs. It does not
exclude changing address views, permitting a larger-support extension,
restructuring the consumer, or another primitive. It is not a lower bound
for all implementations of a sparse bit permutation.

## Compatibility with the actual-width question

The public actual-width T74 proposal in Discussion 2612 asks for an
exposure supported on at most `2g` axes, with targets `rho+jK`, where
`K=floor(g^(1/500))` and `1<=g<=floor(p^(997/1000))`. This motivates the
audit; its unpublished implementation is not a premise of the theorem.

The isolated hard family occurs inside that stated range. For every
integer `K>=4`, choose

```
g=K^500, p=g^2, rho=0,
t_i=iK, s_i=iK+2,                 0<=i<g.
```

The computed spacing is exactly `K`. Neighboring support positions are
at distance at least two, and the largest source position is below
`gK<=p`. Also `p^997=g^1994>=g^1000`, so the exact integer root condition
`g<=floor(p^(997/1000))` holds. The target block occupies at most `p`
bits. Complete remaining coordinates may be spectators, and arbitrarily
long coefficient records can meet a separately supplied long-record
condition. No huge array or width is materialized in this existence proof.

Thus the missing router cannot be discharged by merely citing the
completed B1 exponent for a width-`g` interval. A literal union-supported
block-exchange implementation has a linear tariff on this family.
The actual-g root, its endpoint and its conditional cost theorem remain
separate. This result changes no selected frontier or integer exponent.

## Assumptions are necessary

For adjacent support, swapping two adjacent blocks of length two exposes
two axes in one B1 call. For larger allowed support, one exchange of two
halves exposes several isolated sources and moves intervening spectators.
For a new arbitrary-support simultaneous-swap primitive, `g` isolated
transpositions may by definition take one call with `4g` broken bonds.
The exact controls exhibit all three distinctions. None contradicts the
four-cut theorem within its stated contract.

The all-size result is the argument above. The finite programs independently
challenge the cut invariant, supported completions and shortest words;
finite success alone does not prove its quantifiers. Independent human
and formal proof-kernel review are unclaimed.
