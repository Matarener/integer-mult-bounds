# Same-frame signed-column factor for H6 compensation

## 1. Inputs and precise claim

Use the doubled-coordinate H6 ports of the frozen PR606 lineage: two pure
E8 projective squared-norm 16 shells of 1080 ports and mixed ports
`s+=(u,v), s-=(u,-v)` for 120 projective squared-norm 8 root lines in each block.
There are 30,960 ports. Define `tau=t·s/4`,
`f(z)=(z^3-4z)/48`, `K_ts=f(tau)`, and `C=I-K`.

The inherited binary-label isometry satisfies
`p(t)·p(s)=1+tau (mod2)`. Every source has line `P_s=span(p(s))`,
every target has cap `Q_t=p(t)^perp`, in dimension 17. Compatible means
`p(t)·p(s)=0`, hence **odd tau**. Compatible C entries are nonzero;
the result removes proportional columns, not zero columns.

We prove a new indexed factor `DG=C` by changing only mixed-source columns
within a fixed target-label bucket. It has 123,632,640 ordinary helpers,
instead of 227,312,640. Under the complete K-word and frame/erasure contracts
of `h6-compensation-network/contract/THEOREM.md`, it gives the same exact
arbitrary-dirt data map with the helper path `[1,15,1]`. This is a scoped
factor/construction proof conditional on those inherited contracts, not a
formal or unconditional multiplication theorem.

## 2. Same actual source frame

In doubled E8, `v-(-v)=2v`, so v and -v have identical lattice coset mod2.
Equivalently every root pairing signature is unchanged. The source's
`binary_labels` selects an invertible mod-two root Gram basis and applies
an injective affine isometry. Thus `p(s+)=p(s-)`, with identical packed
labels, not merely isomorphic abstract lines.

The source pure fibers have 135 labels of multiplicity 8 per block; the
mixed fibers have 14,400 labels of multiplicity 2. Root, pure and zero cosets
are disjoint and exhaust the 256 E8/2E8 classes. The primary enumeration
uses all 120 pairing signatures. Independently, for doubled E8 vectors q,r,
`(q-r)/2` belongs to doubled E8 iff the coordinate differences are all 0
or all 2 modulo 4 and their sum is 0 modulo 8. Hence a direct coset key is
`(min(q mod4, (q+2*ones) mod4), sum(q) mod8)`.
The independent implementation confirms the exact same pure partition.

The canonical native compiler uses `ce.cgate(H,p)` as its source
representative. Equality of p therefore gives equality of actual source
operators, including phase. At a target bucket all targets likewise have
the same actual cap representative. Reusing a surviving helper's existing
zero→line→cap→FULL recipes introduces no new native conversion family.
This argument inherits the correctness of those recipes; the present
replay does not recompile or independently verify all native operators.

## 3. Complete two-column classification

For target mixed pair `(a,b),(a,-b)`, put `A=u·a/4`, `B=v·b/4`.
Each lies in `{-1,0,1,2}` for canonical root lines. Its C block is

```
delta - [[f(A+B), f(A-B)],
         [f(A-B), f(A+B)]],
```

where delta is the identity only for `A=B=2`, and otherwise zero.
The sixteen attainable ordered classes are recorded exactly in the receipt.

* If B=0 and A odd, the columns are equal; take sigma=+1.
* If A=0 and B odd, f is odd, so the columns are opposite; take sigma=-1.
* If one pairing is 2 and the other odd, the block has rank 2 with determinant
  of absolute value 3/32. Keep both original helpers.
* All remaining blocks are zero, including the diagonal block after I-K
  cancellation. No compatible nonzero entry is discarded.

The rank 1 entries all have magnitude 1/16. For a pure target `(w,0)`,
the two columns are equal; for `(0,w)` they are opposite. In a compatible
pure target bucket, Cauchy gives `|u·w/4|<=sqrt(8)`, and odd integrality
then gives magnitude 1 pairing, hence every C entry has magnitude 1/16.
The whole eight-port target bucket has the same pairing parity.

For a nonzero rank 1 block write its columns as `[v,sigma*v]`. Replace
`G=I_2, D=[v,sigma*v]` by `G=[1,sigma], D=v`. Exactly
`D G=[v,sigma*v]`. This changes no other block; full-rank mixed blocks
keep the original identity capture, and every pure-source helper is kept.
Summing over disjoint source-label/target-label blocks proves **DG=C**
for the complete indexed matrix.

## 4. Arbitrary dirt, frames and both orientations

Allocate an independent ordinary helper for each surviving factor row h.
Let its arbitrary logical entrance be e_h; correlations with other inputs
are allowed. Its G row uses only sources at one common line P_h, and its
D column uses only targets at one common cap Q_h. Nonzero C compatibility
gives `P_h subset Q_h`. Perform these complete phases:

1. At ZERO, `y -= D e`.
2. Helpers climb to their source line and capture `Gx` there. Both reads
   of a signed pair are emitted and paid; helper values are `e+Gx`.
3. Run the **complete unchanged** arbitrary-input K word on its disjoint
   data and private registers. It maps y to `y+Kx`, returns logical x,
   places sources at FULL and targets at their actual caps, and restores
   its own auxiliary dirt under its paid contract. Its internal source
   mutation is allowed. Do not move sources to FULL before this word.
4. Helpers climb line→cap and add `D(e+Gx)` to target buckets.
5. Helpers climb cap→FULL and subtract `Gx` at FULL.

The helper ranks are 1,15,1, and both operands in every addition use
the identical actual frame. Data paths and K children are unchanged.
The forward output is

`y-De+Kx+D(e+Gx)=y+(K+DG)x=y+x`,

and each helper returns to e. This proves every independent dirt column
cancels. Its **physical** endpoint is FULL applied to e, not its physical
entrance e. Any wrapper restoring literal physical entrance, copied-total
erasure or recursive reserve remains a separately paid inherited obligation.

Dualize every scalar addition in the same order, replacing
`a+=c*b` by `b-=c*a`, keeping the frame history. Initially the prefix
gives `h=e+D^T y`, capture subtracts `G^T(e+D^T y)` from x, K subtracts
`K^T y`, scatter removes `D^T y` from h, and cleanup adds `G^T e` to x.
Thus `x -> x-(K+DG)^T y=x-y`, y is unchanged, and helpers return to e.
The complete K interface, including arbitrary sources, targets, dirt and
private erasure, is essential in both orientations.

`word.py` checks all source/target/helper basis columns in one seed 83 fixture
using exact sparse rationals and source-line/cap chronology. K is an
explicit exact macro contract there, not an implemented native K tape.
The full phasewise proof above is separate from that finite replay.

## 5. Exhaustive reduced census and complete scalar invoice

For every root line, among 120 root lines exactly 63 are orthogonal,
56 have odd pairing, and one is the same line. Every root has 72 compatible
pure target-label buckets. Each pure source has 64 compatible root lines,
64 pure-label buckets, 448 pure-port pairings of magnitude 1 and 64 of
magnitude 3. The two enumerations check the complete tables, including every
one of the 1,166,400 pure/pure entries. Products of these checked degrees,
with section 3's complete class split, give full-network counts.

For each mixed source label:

| Target caps | Number | Old helpers/cap | New helpers/cap |
| --- | ---: | ---: | ---: |
| Mixed rank 1 | 2*63*56=7056 | 2 | 1 |
| Mixed rank 2 | 2*56=112 | 2 | 2 |
| Pure rank 1 | 2*72=144 | 2 | 1 |

Old helpers per mixed label are 14,624; new are 7,424. Thus removed helpers
are `M=14400*7200=103680000`. Pure-source helpers remain
`270*8*(120*64+64)=16727040`. Total helper counts are
`227312640 -> 123632640`.

Each removed mixed-target helper removes 2 D entries, and each removed pure
target helper removes 8. Therefore removed D entries are
`14400*(7056*2+144*8)=219801600`, all of magnitude 1/16.
`D_nnz:480337920 -> 260536320`; the 3,363,840 entries of magnitude 5/16
are retained. Crucially **G_nnz stays 227312640**: two reads feed one helper.
There is no halving of the G term or a free source-access operation.

The pinned signed Horner tariff is 4 for ±1, 8 for ±1/16, 11 for ±5/16.
Each D entry occurs in prefix and scatter; each G entry in capture and
cleanup. Hence the complete component primitive allowance is

`16*D_nnz + 6*D_5 + 8*G_nnz`.

It falls from 9,524,090,880 to 6,007,265,280, saving 3,516,825,600.
This includes every changed capture, cleanup, prefix and scatter; helper
frame children are counted separately. Native coordinate passes, actual
address evaluation, tape movement and physical dispatch are not part of
this semantic scalar tariff. These are prescribed upper invoices, not
minimum gate counts or measured speedups.

## 6. Conditional K and full-host deltas

PR4027 at the exact head in CONTEXT.json supplies the unchanged asymmetric
K histogram and scalar bills. Conditionally reusing those inputs, the new
full local histogram is

`{1:247265280,8:4336,9:32,15:123632640,16:59760,17:1600}`.

Rank mass falls by `17M=1762560000` from 3,865,333,216 to 2,102,773,216.
The conditional combined scalar invoices are 6,250,865,392 forward and
6,250,867,840 dual. No ordinary or private K child is otherwise changed.

The certificate also applies the unchanged fractional full-row convention
from the base pricing source: for L stages, `m=16L+1`, `q=floor(m/17)`
and `pad=m mod17`. Removing M helpers removes formal stock `ML/q`, and
mass/rank terms `(2ML,1)`, `(15ML,15)` and `(ML*pad/q,pad)` if pad>0.
Their mass sums to `mML/q`, so the formal coverage deficit is unchanged.
Stages 3,5,7 and all pad work are checked against the independently extracted
source function; repeated ranks are combined for comparison. This is a
conditional accounting identity, not a physical stock/reserve certificate.

## 7. Range, coverage and open implementation obligations

At the **forward logical capture cut**, `|e|<=E`, `|x_+|,|x_-|<=X`
give `|e+x_+ +sigma*x_-|<=E+2X`, previously E+X. Captures introduce no
new fractional denominator. One extra magnitude bit suffices relative to
that single old cut bound; this says nothing by itself about full-network
approximate-child precision, dual accumulation, or physical normalization.
Those must be propagated through every inherited child and adapter.

The exhaustive domain is the fixed H6 geometry, all 16 mixed pairing classes
and its complete counts; seed 83 only selects a bounded all-column fixture.
There is no probabilistic search, parameter sweep or optimality claim.
Pure-source compression, native recipe regeneration, a complete materialized
tape, copied-total erasure, physical restoration/placement, actual reserve,
source-access complexity and the joint BIT/complex analytic admission remain
open. No new κ follows from a smaller unnormalized rank or scalar invoice.

Credit: Dominik Scholz, DreamingOfClouds, the H6 compensation/compiler
contributors and Ross Richardson's PR4027. Prepared by Tekalign with
substantial OpenAI Codex assistance; Apache-2.0. Frozen sources are unchanged.
