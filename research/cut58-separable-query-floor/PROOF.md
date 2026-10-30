# Sharp query tariff for the earlier six-bank cleanup

For every integer `f>=2`, the exact cut58 target requires native mass at least
`22f` in the separable response class below. The existing suffix attains that
bound. Arbitrary scalar bank coupling and literally restored dirty banks do
not reach the proposed `16f` target within this class. This is a written
all-parameter proof supported by finite exact certificates, not a formal-kernel
proof or a lower bound for arbitrary Clifford circuits.

## Contract and charged class

Fix the q2 cut58 matrix from PR4082 at
`ff277e8a958829954f371c85bdc447672266edbd`. Its six current physical inputs
`(a,u,b,r,z,c)` are independent arbitrary fields, each of internal dimension
`D=2^(12f)`, including spectators. The actual signed Gaussian families are
`K=i k^(tensor f)`, `W=w^(tensor f)`, and `T=i t^(tensor f)`. Both global
factors `i` are outside the tensor powers. The old operators act on four bits
per tensor coordinate; `T` acts on a disjoint fresh pair. Other coordinates
are spectators. Exact substitution gives `K^2=T^2=-I`, `W^8=I`, and
`[K,T]=[W,T]=0`. `W` is not an involution. Both `KW` and `WK` have native
rank `2f`, although `W` has rank `4f`; these potential fusions motivate the test.

For any finite bank count `B>=6`, permit arbitrary invertible scalar
`GL_B(Q(i))` couplings and one-bank responses `h T^e`, with `h in H=<K,W>`
and `e in {0,1}`. Coefficients, length and topology may depend on `f`.
Every extra bank has arbitrary entering dirt and must return literally to it,
with no cross terms: the full endpoint is `M direct-sum I`. All banks have
the same physical volume. Global Gaussian scalar multiples are harmless.
Scalar scans remain payable; ignoring them here weakens the lower bound.

The native tariff is at least the response's binary polar rank, namely
`f(r(h)+2e)` by disjoint support. This includes the source's native primitives.
The only free internal adapters covered here are rank-zero members of this
generated class. General external monomial/Clifford adapters are excluded.

## Actual represented algebra and its f=1 exception

Exact action-table closure gives 128 signed all-f elements of `H`, with only
the scalar families `I` and `z=-I`. The 64 projective representatives have
consistent K-word and W-word parities `(p,q)`. The following table counts all
128 signed elements, not only the 64 representatives:

| Parity | Rank 0 | Rank 2 | Rank 4 |
| --- | ---: | ---: | ---: |
| `(0,0)` | 16 | 0 | 16 |
| `(1,0)` | 0 | 16 | 16 |
| `(0,1)` | 0 | 0 | 32 |
| `(1,1)` | 0 | 32 | 0 |

Therefore `r(h)>=2[q+(p xor q)]` for every old response. Group characters
alone do not justify twisting physical matrix equalities. At `f=1`, the
independent certificate retains a 16-term zero matrix relation whose W-sign
twist has entry `(0,0)=-8i`. This directly rejects an unqualified character
proof without relying on a numerical span-dimension claim.

Let `v_j` be the 16-by-16 one-coordinate matrices of the 64 representatives,
with fixed global phases stripped. Their tensor-square Hilbert-Schmidt Gram
matrix has entries `tr(v_i^* v_j)^2`. Its Gaussian integer determinant is
nonzero modulo 101 under `i->10`, so the tensor squares are independent over
`C`. A separate implementation certifies a nonzero 64-by-64 matrix-entry minor
modulo five under `i->2`; it does not reuse the Gram computation.

Independence persists at every larger tensor power. Choose a linear functional
`ell` nonzero on every `v_j`, possible over an infinite field. Applying `ell`
to one factor of a relation at degree `f+1` gives a relation among the
independent degree-`f` tensors, with coefficients multiplied by nonzero
`ell(v_j)`. Induct from `f=2`. The actual global phases only rescale vectors.

Thus the represented old algebra is faithful to `C[H]/(z+1)` for every
`f>=2`. Both parities fix `z` and descend to actual algebra automorphisms.
The disjoint fresh `I,T` are independent because `T` has a nonzero character
translation. Use the three characters

    chi_W(hT^e)=(-1)^q,
    chi_KW(hT^e)=(-1)^(p+q),
    chi_T(hT^e)=(-1)^e.

They fix scalars, including scalars chosen as functions of `f`. Their validity
is pointwise for every `f>=2`; a uniform word across sizes is not required.

## Complete target defects

Write `M=diag(T,...,T) N`, where

    N = [ K      0   0       0    0      0 ]
        [-WK     0   I-W    -I   -WK     0 ]
        [-K      0   I      -I   -K      0 ]
        [-KWK    K   K(I-W)  0   -KWK    0 ]
        [ 0      0   0       0    K      0 ]
        [ 0      0   0       0    0      I ].

Its kernel is zero: rows 0,4,5 force `a=z=c=0`, rows 2,1 force `b=r=0`,
and row 3 forces `u=0`. The separate endpoint oracle checks all 36 entries,
literal and simplified source words, all Gaussian tensor phases, the saved
inverse, and both inverse orders.

For `chi_W`, set `L=Ka+b+Kz`. After removing the common `2T`, the defect is
`(0,WL,0,KWL,0,0)`. The map to `L` is surjective and its output embedding
injective, so its rank is `D`. For `chi_KW`, the defect divided by `2T` is

    (-Ka, Wb, K(a+z), KWK(a+z)-K(u+b), -Kz, 0).

Its kernel is exactly `a=b=u=z=0`, with `r,c` free, giving rank `4D`.
Finally `chi_T(M)-M=-2M` has rank `6D`. Restored identity banks add zero
to each defect. These are all-parameter block-kernel arguments, not sampled
rank estimates.

## Sharp native bill and recursive-cost consequence

Telescope the difference between a gate product and its character twist.
Rank subadditivity bounds the endpoint defect by the sum of gate defects.
A scalar bank coupling has zero defect. A character-odd one-bank response
has defect rank `D`; a character-even response has zero defect. This also
holds with arbitrary scalar conjugations and restored dirty helpers. Hence

    n_W>=1,   n_KW>=4,   n_T>=6.

Summing the old tariff and the fresh disjoint-support charge proves

    R_f >= 2f(n_W+n_KW+n_T) >= 2f(1+4+6) = 22f.

The source's simplified suffix uses three `K`, six `T` and one `W`, costing
`3*2f+6*2f+4f=22f`; the bound is attained in this class. Reversing every
invertible gate gives the literal inverse. Inverse endpoints have identical
defect ranks and unary polar tariffs, so the inverse bound is the same.

With the unchanged `54f` prefix, whole native mass is at least `76f`, above
fixed stock `72f`. In the source's equal-volume normalization `m=12f` and six
useful public outputs, each nonzero allowed child has rank at most `6f<m`.
For `0<=b<1`, the complete native moment is therefore at least
`76/12=19/3>6`, since `(r/m)^(1-b)>=r/m`. Further scalar, owner, controller
or numerical charges cannot repair this unfavorable native budget. Identity-
restored helpers supply no additional public stock credit for this endpoint.

## Limits, provenance and next question

The proposed `16f` suffix is excluded only for this generated separable class,
for every `f>=2`. No `f=1` optimum is claimed. Outside-group physical adapters,
cross old/fresh mixing, changed gauges or endpoints, different volume, partial
or striped queries and an earlier prefix can leave the premises. One explicit
phase-correct outside-group response with a complete favorable bill is the
next useful test. No new supplier, compatible BIT, frontier or kappa follows.

The target and source native contracts come from PR4082 and its credited
lineage. The new contribution is tensor-stable represented-algebra grading
and the sharp tariff under arbitrary scalar topology. Source retention, finite
exact computation, this written proof, separate AI checking, hosted CI, and
human/formal acceptance remain separate evidence levels.
