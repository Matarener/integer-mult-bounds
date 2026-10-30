# Nested swaps for an in-place XOR correction

The construction and proof were produced by Nick Petalas. Apache-2.0.
The two-tape record interface, R0/L0/W templates and serial comparison
formula are Dugongue / David Ganz's [PR #3879](https://github.com/CrocSwap/integer-mult-bounds/pull/3879).
Those are cited premises. This package does not audit that predecessor.

## Contract and theorem

Let h >= 1, N = 2^h and 0 < delta < N. Write delta = m+l, where m is a
power of two and 0 <= l < m. Let c = N/(2m). Tape zero contains

```
# w_0 # w_1 # ... # w_(N-1) #
```

with N arbitrary binary records of the same width B >= 0. Tape one
contains one arbitrary dirty record of width B, framed by two separators.
Both heads start at their opening separators, at arbitrary integer origins.
All tape cells outside these windows are arbitrary and must be preserved.
The alphabet is {0,1,#,blank}. Each transition reads both scanned symbols,
writes at most one symbol per tape and moves each head by at most one cell.

There is a finite controller that implements w'_j = w_(j xor delta),
restores the complete scratch record and both heads, and preserves both
exteriors. Its exact number of transitions is

```
H_nested = N*m + 2*(c-1)*(l+1)
T_nested = (3N/2)*(2B+3) + (B+2)*H_nested.
```

Its control has 2*H_nested + 9N/2 + 1 states including halt, and
16*H_nested + 33N/2 defined transition entries. It uses the same B+2
scratch cells, including separators, as the predecessor. The first tape's
visited window has N*(B+1)+1 cells. These statements hold for all h and B.
The executable evidence has explicit expansion bounds described below.
For delta = 0, the controller is already halted, with zero transitions.

PR #3879's serial schedule has

```
H_serial = (N-2)*m + 2N-2.
```

The new schedule saves at least (N-2)*(B+2) transitions for every nonzero
mask. The saving is strict for N >= 4. This is an exact machine invoice,
not a wall-clock measurement or a recursive rank saving. No minimum over
all possible tape machines or all swap orders is asserted.

## Schedule and arbitrary dirty scratch

List a_0 < ... < a_(q-1), q=N/2, with a_i < b_i = a_i xor delta.
These are exactly the indices whose m bit is zero. In particular a_0=0.
Let W(v) swap the record at address v with the scratch record and rewind
both heads to their entry separators. It is the predecessor's three-state
W template, costing 2B+3 transitions for arbitrary record contents.

Use this visit order, with literal R0/L0 seeks between visits:

```
a_0, a_1, ..., a_(q-1),
b_(q-1), a_(q-1), ..., b_1, a_1, b_0, a_0.
```

There are exactly 3q record swaps. There is no online stack or online
address arithmetic. The finite compiler unrolls every seek and swap.

For correctness, the subword for pair i is an opening W(a_i), followed
by all later pairs, followed by W(b_i), W(a_i). Induct on the number of
enclosed pairs. The enclosed subword acts only on its own disjoint data
pairs and restores whatever scratch value it receives. Thus it returns
the scratch value left by the opening W(a_i), even though that value is
an arbitrary original data record rather than the original scratch dirt.
The remaining two swaps finish the transposition of a_i,b_i and restore
the incoming scratch value. The induction proves the desired disjoint
transpositions, including arbitrary dirt restoration. This is the usual
star-transposition identity applied to a nested schedule.

Every data address occurs in a W, and the final visit is a_0=0. Each W
rewinds both heads. The data head therefore returns to its origin and
the scratch head never leaves its declared record. All seeks stay between
valid data-record separators. The predecessor templates write no exterior
cell. This proves the restoration, frame and visited-window statements.

## Exact travel

Put D_i=b_i-a_i>0 and d_i=a_(i+1)-a_i for i<q-1. The opening sweep costs
a_(q-1). In the closing sweep every b_i to a_i leg costs D_i, the first
closing entry costs D_(q-1), and each intervening leg costs |D_i-d_i|.
Since a_(q-1)=sum d_i, the total is

```
H = 2*sum_i D_i + 2*sum_(i<q-1) max(0,d_i-D_i).
```

The representatives form c blocks, each containing m consecutive
addresses. In block t they are 2mt+x, 0<=x<m, with partners
2mt+m+(x xor l). Since XOR permutes [0,m),

```
sum_i D_i = c*m^2 = N*m/2.
```

Inside a block d_i=1 and D_i>=1, so the positive-part term is zero.
At each of the c-1 block boundaries, the old representative is
2mt+m-1, its partner is 2mt+2m-1-l, and the next representative is
2mt+2m. The positive part is exactly l+1. Substitution gives the claimed
H_nested. No monotonicity of the partner sequence was assumed.

For comparison, the cited serial formula gives

```
H_serial-H_nested = 2*(N-m-1-(c-1)*(l+1))
                 >= 2*(N-m-1-(c-1)*m)
                  = N-2.
```

There are the same 3N/2 W macros in both constructions. Every seek crosses
one width-B record and costs B+2. Multiplication gives the exact transition
saving. Each seek contributes two states and sixteen transition entries;
each W contributes three states and eleven entries. Add one halt state.
The compiler also saves twice the crossing reduction in states and sixteen
times that reduction in transition entries. Control is not treated as free.

## Evidence and limits

The written schedule is uniform for every finite h. The supplied compiler
allows 0<=h<=9 and at most 250,000 transition entries, before allocation.
Larger controllers are not silently approximated; expansion fails. The
schedule and token-permutation checker covers every h<=9 and every mask,
including controllers too large for literal expansion. The unit-step
executor covers every mask through h=5, widths 0..3, complete one-bit
data/scratch basis fixtures through h=3, and two h=9 machines. The complete
RESULT records the enumerated counts. Its finite evidence corroborates the
proof; it does not establish the universal quantifiers by enumeration.

No predecessor executable is imported or replayed. Its transition templates
are reimplemented here with attribution. The independent executor dispatches
only literal table entries, never an address-seek or record-swap oracle.
The executable compiler stores a bounded host-side finite table; it does
not claim an unpriced fixed-control online interpreter for arbitrary h.

Acquiring an actual native return in this record layout, buffer placement,
representation conversions, the complete caller and its recursive invoice
remain open. No selected framework assumption, new kappa, complete rounded
multiplier, human review or formal proof-kernel acceptance is supplied.
