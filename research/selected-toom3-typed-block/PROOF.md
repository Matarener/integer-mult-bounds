# One literal selected block does not have the same-width Toom-only interface

## Source and exact boundary

Fix canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90` and the
selected #1094 archive pinned in `SOURCES.json`. The question is the next
experiment explicitly left open by Gonzalo Mier's #3974, head
`23bb4de61d629e3f103a65baa7882b34042ab10f`: bind one of its nine-climb windows
to ordinary degree-two Toom coefficient inputs. This is one window, not a
reclassification of all 254 reported windows.

Use the first forward phase-A group under the earliest-deadline rule adapted
from Josie Elliston's #1817. Its nine `L` registers, in order, are

`546, 560, 547, 568, 548, 558, 549, 570, 464`.

The first eight climbs are `(old,new,rank)=(0,4,1)`, where frame 4 is `[459]`;
the last is `(0,5,1)`, where frame 5 is `[75]`. Frame zero is empty. The original
zero-based event indices are `9297,9299,9301,9304,9313,9315,9317,9322,9330`.
Their legal windows meet at skeleton gap 1190; the last event's window starts
at 42, the others at zero. All nine destinations are distinct. Moving the
climbs to that gap changes no event on their own registers and crosses no
phase boundary. This is the inherited local movement model, not a new global
hosting proof.

Let `W=Q(i)^512`, the nine-bit index space of one physical payload. Write
`Z_j` for the independent unframed coordinates immediately after the entry
adapters, so physical register `j` is `T_start(j) Z_j`. These are **not** raw
initial values: for example register 512 has a residual pre-wrapper. Entry
adapters are invertible; frame coordinates do not impose a zero or clean-data
promise on a productive helper. The selected nine helpers start at frame zero,
have ordinary identity entry adapters, and end at full frame.

The pinned `INDEPENDENT-LOCAL-REPLAY.json` explicitly declares replay on
"every arbitrary data/helper column", with all 704 input columns and 480
helpers; this is the selected local replacement contract. The verifier binds
that receipt and independently checks the entire entry prefix consists of
7,344 shears, 56 nonzero scales, 464 typed frame adapters and 240 invertible
monomial residual pre-wrappers. There are no entry clears or copies. The first
1,190 phase-A events before this group are also invertible scalar operations.
Thus the full pre-cut map is invertible on all productive columns, and the
nine payload projection is surjective. This establishes independence from
the actual prefix and its arbitrary-dirty contract, not from an assumed
clean-helper initialization. A globally restricted clean-input caller would
be a different contract; it is not excluded by the dimension argument.

For the additional input-form receipt, the verifier checks that this first
phase-A prefix contains no climbs or adapters, and every scalar source and
target has the literal common frame recorded by the trace. Thus propagating
plain rational rows in the unframed coordinates is valid. The independent
surjectivity argument above already suffices for the rank obstruction. The
rational replay gives the actual incoming forms at the chosen gap:

`Z_546,Z_560,Z_547,Z_568,Z_548,Z_558,Z_549,Z_570,Z_464+Z_512`.

Their coefficient minor on the nine named variables is the identity. Thus
these are nine freely variable W-valued payloads, even when all other entrance
coordinates are fixed. None can be discarded because a helper was called
"cold": that word describes its entrance frame, not a zero value.

At this boundary the demanded map is the **linear** operator

`F = diag(T_[459],T_[459],T_[459],T_[459],T_[459],T_[459],T_[459],T_[459],T_[75])`.

It must overwrite all nine named destinations, preserve every other productive
payload, and return any additional scratch in its required initial state. The
selected event is a frame transform, not an independently named bilinear
product of two coefficient variables.

## Exact operator reconstruction

For each of the two transitions the pinned serialized recipe says
`T = L (C_[1] tensor I_256) R`, with R applied first. L and R are monomial
maps with explicit binary permutation, translation, quadratic and Z/4 phases.
The one-axis child is exactly

`C = ((1+i) I + (1-i) X)/2`.

The verifier decodes the recipe directly on every basis vector, using Gaussian
integer numerators and a single factor 2. Independently, it evaluates the
retained canonical-frame constructor on all 512 basis vectors for each frame.
All 1,024 columns agree, including global phase. A separate sparse Gram
calculation gives `T* T = I` exactly. Both operators have rank 512, and F has
rank **4,608**. For example

`T_[459] e_0 = ((1+i)e_0 - (1+i)e_459)/2`,

`T_[75] e_0 = ((1+i)e_0 - (1+i)e_75)/2`.

These explicit outputs catch replacing an omitted dirty input by zero.
The implemented checks also reject altered global phase and translation.
The retained constructor is predecessor code, not claimed newly independent;
the direct recipe decoder and Gram certificate are separate implementations.

## Declared Toom-only substitution contract

The rejected contract asks for the formal exact local operator on `W^9`,
not an encoding of a bounded finite set into wider-precision scalar words.
The latter would require its own precision and decoding contract. The
rejected contract has exactly these restrictions:

1. Each polynomial has three coefficients in a vector space of dimension 512
   over `Q(i)`. Both triples are produced by affine maps of the nine incoming
   payloads. They may have arbitrary fixed coefficients and constants.
2. The usual five Toom evaluation products, interpolation and output decoding
   receive data **only through these six coefficient blocks**. The coefficient
   multiplication may be any bilinear law; it need not be commutative.
3. The nine final payloads are functions of the coefficient blocks and fixed
   constants only. Productive inputs, other registers and scratch may not
   supply additional data to that output decoder.

Restriction 3 is material. Retaining or bypassing original payloads changes
the contract. Five recursive calls in a general circuit do **not** imply this
restriction. No lower bound on arbitrary five-child circuits is claimed.

**Proposition.** This contract cannot realize the named selected block.

**Proof.** Its affine encoding `E:W^9 -> W^6` has a nonzero linear kernel of
dimension at least `9*512-6*512=1536`. For any nonzero kernel vector h,
`E(x+h)=E(x)`, so every downstream output is the same at x+h and x. But the
selected F is invertible, hence `F(x+h)-F(x)=F(h)` is nonzero. This contradicts
exact equality on arbitrary dirty inputs. The argument permits nonlinear
interpolation or decoding as long as it receives no extra input data. If one
polynomial is fixed, only three coefficient blocks depend on x and the kernel
has dimension at least **3,072**. Equivalently the possible linear output ranks
are at most **3,072** and **1,536**, respectively, against 4,608. QED.

**Sharper ordinary-decoder corollary.** If the final decoder is affine linear
and receives only the five product blocks, the possible output differences
lie in the image of a linear map `W^5 -> W^9`, of dimension at most **2,560**.
Thus the usual product-only Toom interpolation/output decoder has an output
deficit of **2,048** dimensions. An additional affine side channel entering
that decoder must have dimension at least 2,048. This corollary has the extra
product-only/affine-decoder restrictions; the more generous six-coefficient
contract above permits direct coefficient reads and still fails.

If both operands are homogeneous linear encodings, an additional elementary
control applies: the Toom output is homogeneous quadratic, so its value at
2x is four times its value at x. The nonzero selected block doubles instead.
Affine constants remove that degree objection, but do not remove the input
kernel obstruction above.

Noncommutativity is not the obstruction. Ordinary Toom convolution works over
an associative algebra over the rationals when its indeterminate and
interpolation scalars are central: each ordered term is `A_i B_j`, and no
reversal is used. What is missing here is a typed coefficient embedding of
nine independent payloads, not a scalar identity.

## Larger rational-interface obstruction

There is a separate extension beyond affine encoders: allow **rational
encoding and rational decoding** over K=Q(i). This does not assume, or imply,
that an arbitrary set-theoretic decoder is rational.

Let x=(x_1,...,x_N) be algebraically independent over K, N=4608, and let
E=(E_1,...,E_m) be rational functions in K(x). All fixed coefficients and fixed
side information belong to K. If independent other dirty coordinates remain
visible as parameters, adjoin them to the base field and work at the generic
full cut; invertibility of the full prefix keeps the nine selected payloads
algebraically independent over that field. No special zero-valued helper
slice is required, since such a slice could annihilate a denominator.
Suppose D is rational over K, every denominator
of D remains nonzero after substitution E(x), and `D(E(x))=F x` as a generic
rational identity, where F is the exact invertible selected operator. Then

`K(x)=K(F x) subset K(E_1,...,E_m) subset K(x)`.

Indeed F inverse recovers each x_j from the coordinates of F x. The fields
are equal, but the middle field has transcendence degree at most m over K,
whereas K(x) has transcendence degree N. Therefore **m >= 4608**. Equivalently,
the chain rule on the generic domain gives `J_D(E) J_E=F`; the left side has
rank at most m and the right side rank 4608. This differential proof uses
characteristic zero and the same generic-denominator condition.

The two coefficient triples contain m=3072 scalar rational functions. A fixed
operand leaves m=1536. If the decoder receives only the five product blocks,
m=2560, so the product-only deficit is **2048 even for a nonlinear rational
decoder**. Every input-dependent bypass, retained register or side channel
visible to the decoder must be counted in m. Adding d rational side-channel
coordinates thus requires d at least 1536, 3072 or 2048 respectively; these are
information dimensions, not operation/child/native-cost lower bounds.

Ordinary Toom evaluation and interpolation are rational scalar operations.
Any fixed finite-dimensional bilinear coefficient algebra, including a
noncommutative one with structure constants in K, has polynomial multiplication
in its scalar entries. Variable inversion is rational where the element is a
unit and the corresponding denominator is nonzero. Thus this larger model
covers rational coefficient preparation, those products and rational output
recovery, while leaving nonrational operations, wider coefficient spaces,
finite-set/precision encodings and changed output contracts open. A denominator
vanishing identically on the encoded image does not define an available
rational decoder there. Pointwise injectivity over the countable field K is
not a replacement for the formal generic identity.

A small verifier fixture demonstrates a legal nonlinear rational change of
coordinates `(x/y,y/z,z)` with exact inverse `(uvw,vw,w)`, and rejects the
lost-scale map `(x/y,y/z)` and the identically undefined decoder denominator
`u-v` under encoding `(x,x)`. These fixtures check boundary failure modes;
the written function-field/chain-rule argument proves the general theorem.

## What can reopen the route

Adding an affine side channel of scalar dimension d changes the encoding to
`W^9 -> W^6 x Q(i)^d`. Injectivity then requires **d >= 1536**; with a fixed
factor it requires **d >= 3072**. These are information dimensions, **not**
native operation, child-count, storage, or time lower bounds. Already-retained
productive data could supply such a channel; its exact use and legal costs
must be specified. Wider coefficient spaces, nonrational data
encoding, a different output contract, or a new coupled recursive primitive
are also outside this proposition. A wider space must be priced at its actual
recursive size, rather than silently counted as the same five children.

The original block already pays nine rank-one frame children and its named
recipes. There is no completed replacement here. Extra data acquisition,
encoding, scratch, phase/frame conversion, dyadic precision and halving,
interpolation's non-dyadic divisions, native hosting, decoding and restoration
all remain unknown for a changed interface. Unknowns are not zero. In
particular the predecessor's 19 additions and 13 rational scales do not price
those obligations or establish legal native division by three.

**Expansion decision:** pause the same-width Toom-only substitution on this
actual group. Reopen on one explicit interface carrying the missing data,
with all nine output identities and complete restoration, then price that
module. Do not extrapolate the 254 event count into implemented savings. This
result changes neither the selected paid profile nor either supplier cap,
and establishes zero realized blocks and zero kappa improvement.

## Constructive comparison: homogeneous lane packing

The first eight selected maps do have an exact different tensor structure:

`diag(T_[459],...,T_[459]) = I_8 tensor T_[459]`.

With index `(lane,x)` encoded as `512*lane+x`, the same canonical frame `[459]`
on twelve bits realizes this identity. The verifier compares its full Pauli
tableau with the nine-bit tableau plus three idle bits, then checks its exact
zero-state vector to fix the global phase. Its Fourier B-block rank is **one**,
with payload dimension **4,096** and eight times the idle extent. This is a
constructive operator equality, not an eight-to-one paid-call conversion.

The grouping therefore has a precise alternative to Toom, but the rank-one
child must now act on eight times the payload, or a different native operator
must be supplied. No rule identifying that enlarged input with a unit-priced
rank-eight child follows from this identity. #1779's diagonal-product screen
and #1836's joint-shear screen also explicitly leave physical interfaces open;
#1836 is pinned at `0a62e3f1c0ea493ddb83f25b91c5548c87978bcc` for this comparison.
A paid enlarged-payload native call would be the next discriminating module.
This comparison supplies its exact operator and width, without assigning
unproved copy, layout, precision, restoration or supplier costs to zero.
