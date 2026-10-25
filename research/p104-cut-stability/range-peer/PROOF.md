# Finite all-interval range appendix

This separately closes the integer-range caveat in the earlier sealed
selected-row review. It does not modify that review or claim a recursive
backend, fixed-tape implementation, stock theorem, κ improvement or adoption.

## A simultaneous bound for every interval start

Regard each exact logical scalar/ownership event as a 743-by-743 matrix,
including arbitrary owned residuals. COPY is the chosen ADD implementation;
INIT and CLEAR zero only their owned rows; MOVE is logical identity.
Let `M[j,i]` be the product from cut i to cut j, with `M[j,j]=I`.
Maintain nonnegative integer exponents e_r with the invariant

`sum_s |M[j,i][r,s]| <= 2^e_r` for every i in 0..j.

Initially e_r=0. The newly starting identity interval at every event requires
a baseline of 1; it is not a fictitious input or productive credit.

For ADD/COPY `d += q s`, older intervals have row norm at most
`2^e_d + |q| 2^e_s`. Put h=ceil(log2|q|). Then
`2^e_d + |q| 2^e_s <= 2^(1+max(e_d,e_s+h))`.
This upper bound is also at least 1. Thus the proposed ADD recurrence is
valid simultaneously for every interval start, although different source
rows may attain their bounds at different starts. No claim of exactness is
needed. q=0 leaves the exponent unchanged.

SCALE gives `max(1,|q| 2^e_r)` and hence exponent
`max(0,e_r+ceil(log2|q|))`; q=0 gives exponent zero. INIT/CLEAR give exponent
zero because all older intervals have a zero owned row, while the new empty
interval has an identity row. Unchanged roles keep their exponents. These
arguments inductively establish the invariant after every event.

Taking E to be the largest computed exponent at any cut/role therefore gives
`||M[j,i]||_infinity <= Gamma=2^E` for every ordered pair of logical cuts.
This is an O(events) conservative envelope, not an exhaustive O(events²)
calculation of exact interval maxima. A separate implementation on the exact
published WORD obtains E=296, first attained at cut24859 / role146. Its small
seven-event control directly enumerates all interval products and includes
negative/contracting coefficients, exact reset, ADD-COPY and zero SCALE.

## Physical cuts and native interiors

At semantic cuts the exact physical interval is
`diag(Phi_j) M[j,i] diag(Phi_i^-1)`.
Each chart and inverse has component-sup norm at most N^9, N=2^f, so every
semantic physical interval has norm at most Gamma N^18. This is a coordinate
bound with no spectator-volume factor.

For cuts inside different native MOVE recipes, the remaining first recipe
and the initial last recipe each contribute at most N^9. The intervening
semantic interval contributes Gamma N^18, giving Gamma N^36. If both cuts
belong to the same MOVE, the contiguous recipe segment contains at most
nine C layers per column and has norm <=N^9 directly, also below the stated
bound. Monomial recipe factors have norm 1. Exact scalar accumulators are
handled by their separate local guard; rounded error layers are placed only
after complete scalar linear forms or native butterfly layers.

## Explicit finite integer part

Suppose initial real/imaginary components have magnitude <=2^b. Let p be
the number of fractional bits, so every rounded layer injects coordinate
error at most delta=2^-p. Let K bound the number of rounded layers and
k=ceil(log2 K). The already checked exact prefix bound at all native-layer
cuts is `LambdaP N^20`, with LambdaP=2^17. The perturbed state therefore has
magnitude at most

`2^(b+17+20f) + K Gamma N^36 2^-p`
`<= 2^(b+17+20f) + 2^(k+E+36f-p)`.

Choose the fixed number of **integer magnitude bits**

`I = 2 + max(0, b+17+20f, k+E+36f-p)`.

Then every stored component has magnitude strictly below 2^I throughout the
flat trace. A fixed-point word with one sign bit, I integer magnitude bits
and p fractional bits suffices for all stored components. In particular the
fractional precision needed for the final-error result need not be increased
to 36f. An alternative sufficient condition `p>=k+E+36f+2` merely makes
the accumulated intermediate perturbation at most 1/4.

For a completed-service-only model, exact prefixes use N^14 and every
service interval uses Gamma N^18. The corresponding stored integer bound is

`I_service = 2 + max(0, b+17+14f, k+E+18f-p)`.

That service model assumes the retained completed-native output-error ABI;
it does not prove native recursive internal arithmetic.

The actual scalar coefficients have dyadic denominator at most 2^16 and
numerator magnitude at most 65537. A further fixed +35 accumulator bits
beyond the stored word conservatively cover exact numerator multiplication,
denominator alignment and addition before one final rounding. These local
accumulators are also finite; no unbounded-integer storage is assumed.

The literal layer count is `K(f)=21688+5894f`, while the completed service
count is 25312 including input/output layers. Expanding native transforms
into those literal butterflies is a precision witness; its runtime is not
the recursive invoice. Physical word allocation, record movement, uniform
recursive implementations and the five framework premises remain separate.

Prepared for thu-nmrc with OpenAI Codex assistance. Apache-2.0. The original
P104/Cinna Davis/Ali Romman/Cao Yifan/zxv/native/compiler lineage is retained;
the exact source word is not changed.
