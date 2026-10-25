# A sharp tariff for the closed three-port orbit alphabet

This note proves an exact formal query count. It does not identify an arbitrary
native caller with this alphabet, price scalar bridges, or construct a physical
supplier. The finite root census motivates the alphabet; it does not imply that
all E8 callers reduce to it. The rank-specialization method is inherited from
earlier group-algebra query arguments; sharpness and the returned-spectator
extension below are the bounded additions to the preserved C09 note.

## The model and the complete endpoint

Let `B>=1` and `h>=0` be integers and put `n=6B+h`. Work first over

`R=F2[C2^3]=F2[x,y,z]/(x^2-1,y^2-1,z^2-1)`.

There are `2B` labeled public banks of three independent rows each, followed by
`h` independent, arbitrary dirty scalar rows. Matrices act on column vectors;
events listed first execute first, so the total matrix is the product in reverse
event order. A free gate is any parameter-independent member of `GL_n(F2)`.
One paid gate is a matrix with diagonal `(z,x,y)` on each of two distinct public
banks and identity elsewhere, with optional parameter-independent invertible
scalar factors on the left and right. The factors may mix public and spectator
coordinates. Equivalently they may be included among the free bridges. Each
such local gate costs one formal query, regardless of the scalar factors.

The required **complete** endpoint is

`T=diag(xyz I_(6B), I_h)`.

Thus every public output has the specified operator on its own independent
input, every dirty spectator is returned to its own entrance value, and all
cross coefficients vanish. No zero, correlated, or discardable helper is
assumed. Optional fixed scalar entrance/exit factors preserve the lower bound
below. With those factors the displayed restoration refers to the normalized
endpoint; a raw same-frame restoration claim requires that the factors actually
be applied. They are free only in this formal tariff.

**Theorem.** The minimum number of paid queries is exactly `3B`, for every
finite `h`. The upper bound already holds with `h=0`.

## Lower bound, uniformly in the number of dirty spectators

Use the algebra homomorphism

`phi_x: R -> F2[epsilon]/(epsilon^2), x |-> 1+epsilon, y,z |-> 1`.

It respects the defining relation because `(1+epsilon)^2=1` in characteristic
two. Write `phi_x(M_j)=A_j+epsilon B_j`. All `A_j` are invertible: scalar gates
are invertible, and a local diagonal specializes to identity. Free gates have
`B_j=0`. A local query has exactly two nonzero diagonal derivative entries,
one `x` port in each active bank. Its left and right scalar factors preserve
that derivative rank, so its rank is two.

For an arbitrary word, including all free bridges, the exact first coefficient
is

`[epsilon](M_m ... M_1) = sum_j A_m ... A_(j+1) B_j A_(j-1) ... A_1`.

Each paid summand has rank at most two and each free summand is zero. Rank
subadditivity gives `rank([epsilon]M)<=2L`. On the required complete endpoint
the coefficient is `diag(I_(6B),0_h)`, of rank `6B`. Therefore `L>=3B`.
Left/right fixed scalar endpoint factors do not change this rank.

The argument holds for every finite `n`; it does not enumerate a maximum helper
count or assume that spectators stay untouched during the word. Arbitrary
parameter-independent scalar borrowing is allowed. It is the complete
returned-spectator target, not a clean-helper test, that fixes the target rank.
The `B=4,L=9` candidate consequently fails this alphabet since `18<24`.

## An attaining word in the actual alphabet

Fix one disjoint pair of banks and write `D=diag(z,x,y,z,x,y)`. Let `P` be the
scalar permutation that rotates the three row positions identically in the two
banks, leaving every other row fixed. No generator is renamed. The three
queries in

`D (P D P^-1) (P^2 D P^-2)`

are permitted scalar conjugates. Their three diagonal entries on each row are
a permutation of `x,y,z`. All commute, hence the product is `xyz I_6` on that
pair and identity outside it. Applying this to `B` disjoint pairs gives `T`
using exactly `3B` queries and `4B` nonidentity scalar permutation events in
the displayed literal implementation. Every scalar permutation is invertible.
There is no use of a source/address automorphism in this construction.

The finite fixtures with `h>0` additionally append a scalar shear
`d_0 += public_0` and its inverse. This redundant, fully recorded free pair
returns arbitrary dirt and makes omission of the return a genuine semantic
defect. It is unnecessary for the upper bound. Its two free shears are not
silently counted as physical zero-cost operations.

## Independent tensor generators: the precise all-f statement

For every integer `f>=1`, replace the ring by `F2[C2^(3f)]`, with independent
commuting involutions `x_j,y_j,z_j`, and define

`X=product_(j=1)^f x_j`, `Y=product_j y_j`, `Z=product_j z_j`.

Stipulate the same one-query local diagonal `(Z,X,Y)` on two banks and the
target `diag(XYZ I_(6B),I_h)`. Send `x_1` to `1+epsilon` and every other
generator to one. The same two-versus-`6B` rank argument applies. The cyclic
word also applies verbatim, so its formal optimum is `3B` for every `f,B,h`
in this domain. The local aggregate diagonal is one paid query by the stated
alphabet; this statement does not price the work required to produce it.

The attaining identity remains true under **every** operator representation of
these rings. The lower bound is a full formal-ring identity obstruction, or an
operator obstruction after a separately proved faithful realization. Order two
or order four alone does not make a chosen native representation faithful as
an algebra. In particular, this theorem does not assert a fixed-f native lower
bound merely from the orders of some concrete transforms.

## Separate complex order-four model

Over `K[C4^3]`, with `K=Q(i)` or `C`, use the same alphabet and arbitrary
parameter-independent invertible scalar bridges over `K`. Compare the two
algebra homomorphisms `(x,y,z)=(1,1,1)` and `(i,1,1)`. These are legitimate
evaluations because `i^4=1`. They are not a differentiation of `x^4=1`.

For arbitrary evaluated factors `A_j` and `A'_j`,

`A_m ... A_1 - A'_m ... A'_1`

`= sum_j A_m ... A_(j+1) (A_j-A'_j) A'_(j-1) ... A'_1`.

A free factor has zero difference. Each local query has difference rank two,
while the complete target difference is
`diag((i-1)I_(6B),0_h)`, of rank `6B`. Thus again `L>=3B`. The same cyclic
construction attains it. In fact its finite identity is checked over
`Z[C4^3]`, before either Gaussian evaluation; every one of the 64 coefficients
is retained. For `f` independent order-four triples, evaluate `x_1=i` and all
other generators at one; the preceding all-f formal conclusion is unchanged.

A source rotation cannot be treated as a scalar bridge in this single-character
evaluation if it rotates the parameters. The following model treats that
covariance explicitly.

## The specified C3 evaluation cover

On a three-dimensional cover with basis `e_0,e_1,e_2`, set

`X_lambda=diag(lambda,1,1)`, `Y_lambda=diag(1,lambda,1)`,
`Z_lambda=diag(1,1,lambda)`, and `O e_j=e_(j+1 mod3)`.

Directly,

`O X_lambda O^-1=Y_lambda`, `O Y_lambda O^-1=Z_lambda`,
`O Z_lambda O^-1=X_lambda`, `O^3=I`,

and `X_lambda Y_lambda Z_lambda=lambda I_3`. This is the regular action of
`C3` on the orbit of the chosen evaluation; it is not asserted to be a faithful
representation of the entire `C2^3` or `C4^3` group algebra.

Replace each scalar row by a cover block. The actual local query has blocks
`(Z_lambda,X_lambda,Y_lambda)` on each of two banks. At `lambda=1+epsilon`
over the dual numbers its derivative has rank six. At `lambda=1` versus `i`
over `Q(i)` its difference has rank six. The complete public target derivative
or difference has rank `18B`; all `3h` arbitrary spectator coordinates have
zero target variation. Thus the respective rank argument gives `L>=3B`.

The allowed scalar bridges and cover rotations are represented by invertible
matrices independent of `lambda`. Products of ordinary scalar bridges lifted
by `I_3` and the displayed cover permutation satisfy this premise. The rank
bound even remains valid if this constant-matrix class is enlarged to all
invertible constant matrices of the same dimension, while retaining the
specified local query. Any proposed native map must still be proved to factor
through a parameter-independent matrix in this representation. That reduction
is not supplied by an abstract claim of covariance.

For `f` independent cover factors, use their tensor product and vary only the
first factor, setting all other factors to the identity evaluation. Then local
variation rank is `6*3^(f-1)` and target variation rank is
`18B*3^(f-1)`. Their ratio again yields `3B`. This is a conditional formal
tensor-cover statement, not an assertion about physical column counts or an
unspecified native representation. The cyclic attaining word still uses only
scalar port permutations.

## Exact finite evidence and controls

`check.py` captures and authenticates every original input before executing the
historical geometry source, with `compile(...,optimize=0)`. The original source
is unchanged on disk. Its only execution adaptations replace its absolute root
read with captured bytes, remove the historical command-line parser, and return
its result instead of writing/reading a local receipt. The complete returned
receipt is compared recursively with exact JSON types and **no excluded fields**.
Its original and executed-source hashes are retained.

The fresh census checks all 120 pinned root lines, all 54 eligible lines, all
18 oriented triples, their rational projectors and rank-five orthogonal
spectators, and all three residual identities per orbit. It preserves all
historical `B=1..8` screens and the 96 defects of the wrong chart rotation.
Only the `lines` field is used; the R865 circuit inside the retained source file
is neither executed nor recertified.

For every `B in {1,2,4}` and `h in {0,1,3}`, the new checker executes the literal
word, retains all eight `F2[C2^3]` coefficient matrices and all 64
`Z[C4^3]` coefficient matrices, and checks the complete endpoint. A separate
bit-vector implementation executes every one of the `8n` independent columns
of the faithful `C2^3` regular action. It also executes the exact derivative
product rule at every prefix, checks each literal event's derivative capacity,
and retains the full prefix rows. The all-basis specialization tables check all
64 binary and 4096 order-four basis products. Full Gaussian matrices at both
evaluations, the local rank-two differences, the full target ranks, and the
three `B=1,2,4,h=1` cover cases are retained.

Twenty-one semantic mutations are actually executed: nine omitted paid queries,
six omitted dirty returns, one wrong cyclic scalar bridge, a full-common query
that exceeds local derivative capacity, reversal of the complex phase, inverse
cover covariance, wrong root-chart rotation, and a type-corrupted historical
count. Each must fail its exact named production predicate. The same mutant
then executes successfully with **only that predicate** deleted, outside the
rejection handler. These controls check sensitivity; they are not additional
mathematical lower bounds.

The all-`B,h,f` statements above are written proofs. Finite examples and exact
controls are reproducibility evidence, not an exhaustive proof over unbounded
word length. No formal proof-assistant kernel has checked this argument.

## Boundary and attribution

Only formal query count is priced. Native scalar/address work, source access,
carrier admission, numerical precision, restored physical frames, ownership,
storage, finite-tape execution, and a complete open caller remain separate
obligations. Changed query alphabets, parameter-dependent bridges, changed
consumers, or failure of a proposed representation map reopen the obstruction.
The spectator extension concerns independent **scalar** dirty rows with the
displayed complete target, not arbitrary native auxiliary carriers.

Original C09 note/script/receipt and scientific data notices are preserved
byte-for-byte under `frozen/`; `INPUTS.json` gives exact origins and hashes.
The root chart retains its original contributor credits in `NOTICE.md` and
Apache-2.0 license. Ross Richardson with substantial OpenAI Codex assistance
prepared this extension and checker. The inherited rank/specialization method
is not claimed as a new proof technique. Package-level related-work attribution
is maintained by the parent contribution's source audit.
