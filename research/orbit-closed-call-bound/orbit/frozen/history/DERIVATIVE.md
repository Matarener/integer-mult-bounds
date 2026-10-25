# Paired BIT orbit geometry and an early controller screen

Canonical scientific source: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This is local research, not a new supplier or conditional kappa.

The coordinate rotation `(124)(365)` fixes coordinates zero and seven and
preserves the 120 real E8 root lines. Exactly 54 lines satisfy `p dot O p=0`.
They form 18 orthogonal triples `(p,O p,O^2 p)`. For each triple, the paired
residual `I-P_p-P_Op` is the sum of the third root-line projector and a common
rank-five orthogonal spectator projector. These statements are checked over
the rationals from the pinned actual root file.
The pinned chart uses extended-Hamming supports. The superficially similar
permutation `(012)(345)` does not preserve that file and is not used here.

This geometry does not establish a global arity `3+5L`. In the following
restricted, orbit-closed algebra it already imposes a call-count condition.
Use the exact BIT involutions on the three common axes, represented by the
group ring `F2[C2^3]` with commuting variables `x,y,z`. There are `2B`
independent banks, each with the three orbit ports, and no auxiliary values.
Each local invocation, up to parameter-independent invertible scalar factors,
has diagonal `(z,x,y)` on exactly two banks and identity on all other banks.
All intervening free operations are parameter-independent scalar invertible
matrices. The requested endpoint is `xyz` on all `6B` data rows, up to such
scalar factors.

Map `x` to `1+e`, `y,z` to `1` in `F2[e]/(e^2)`. This is well-defined because
`(1+e)^2=1`. Write the image of every gate as `M0+e M1`, with `M0` invertible.
The first-order coefficient of a product is the sum of the conjugated local
first-order coefficients. Each local invocation contributes rank at most two:
one x-coordinate on each of the two active banks. Thus the product's
first-order coefficient has rank at most `2L`. The requested endpoint has
coefficient rank `6B`, since `xyz` maps to `1+e`. Necessarily `L >= 3B`.
In particular `B=4,L=9` fails this grammar regardless of the scalar bridge word.

There is a finite two-evaluation version that also applies to complex C4
variables, without differentiating the relation `x^4=1`. Compare the evaluations
`(1,1,1)` and `(i,1,1)`. For matrices A_j and their evaluations A'_j, the exact
telescoping identity for the difference of two products bounds its rank by
`sum rank(A_j-A'_j)`. Each local variation has rank two and the endpoint
variation `(i-1)I` has rank `6B`. Thus the same bound follows over the complex
numbers, allowing arbitrary dyadic scalar coefficients in the free matrices.

Covariant order-three address rotations can be included on a regular cover.
Represent x,y,z by three-by-three diagonal matrices whose single varying
coordinate rotates, and represent O by the cyclic permutation matrix. These
matrices obey the semidirect covariance relation. On this cover the local
variation rank is six and the endpoint variation rank is `18B`, again giving
`L>=3B`. For BIT the varying entry is `1+e`; for complex it is i. This is an
algebraic representation argument, not an assertion that every native
Clifford adapter factors through this representation.

The result is not a universal native obstruction. Other address automorphisms,
cross-orbit mixing, changed consumers, extra paid gates, and auxiliary carriers
lie outside the stated model. A complete native reduction to this grammar is
an additional obligation. The independent complex lane is checking its own
covariant route semantics. In particular arbitrary phase adapters cannot be
declared parameter-independent scalar gates without that reduction.

Reproduce with `python3 geometry_derivative.py` in this directory. The receipt
includes exact source hash, all eligible oriented triples, call screens for
`B=1..8`, and a control showing that a paid complete common transform has the
full missing derivative rank and violates the local-gate hypothesis.
