# A complete two-parameter complement family is excluded

This is a fixed-anchor obstruction, not a decoder construction or a new
integer-multiplication bound. It extends the selected-frame trace obstruction
to an infinite family of inequivalent complements, including a singular flag
pairing that the generic proof cannot specialize to.

`family.py` rebuilds all literal frames and physical tariffs, verifies
the identities as formal rational functions, and compares the result with `FAMILY-RESULT.json`.
It uses only Python's standard library and the existing exact helper file
`verify.py`. The helper is SHA-256 authenticated and compiled directly from
its source bytes; no cached bytecode or transitive project import is used. Run:

```
python -I -O -Werror -B research/p112-alternate-frame-trace/family.py
```

The two declared external source inputs and local `FIXTURE.json` are SHA-256
pinned by that helper. Default commands do not change files; the explicit
`--write-receipt` option is reserved for receipt maintenance. No coefficient
samples or geometry samples are used. The independent verifier does not
import either producer's algebra.

## Exact scope and conventions

The asymmetric rank-eight anchor is fixed on the ordered groups

```
(A,B,C,D) = (1,2,27,28).
```

Write its rational factorization as `mathcal A = U V`, where `U` has eight
columns and `V` has eight rows. The literal factorization is reconstructed
from the first independent rows and columns of the pinned anchor. Each group
has three scalar coordinates, numbered 0,1,2. Thus `U_C0` is a row and
`V_C0` is a column.

We consider rank-nine extensions with new groups 3 and 4 and own block `I6`,
whose common source and reader complement spaces are

```
H_t = span(U_C0 + t U_C1, U_A1, U_D2),
K_s = span(V_C0 + s V_C1, V_A1, V_D2),
c = 1 + ts != 0.
```

Their pairing is `diag(c,1,1)`. Each has the required nested incidences with
the C three-space and the A+C six-space. The claim quantifies over **every
rational split of the common six-dimensional new-pair space** in this
complement family, not over finitely many coefficients. The excluded `c=0`
does not have the nondegenerate pairing required by this family model.

Masks refer to the six groups `(A,B,C,D,3,4)` in that order. The four physical
binary tariffs used below are regenerated from the pinned port labels:

| Source mask | Reader mask | Groups | Tariff |
|---|---|---|---:|
| 34 | 34 | B+4 to itself | 4 |
| 22 | 22 | B+C+3 to itself | 6 |
| 28 | 28 | C+D+3 to itself | 7 |
| 5 | 28 | A+C to C+D+3 | 5 |

The rank-nine common-pair model, its saturated individual flags, and the
Schur-complement tariff interpretation are the same as in
`PROOF.md`. All four flags are regenerated directly from the
literal anchor and physical tariff data in this replay. No claim is made
about different anchors, arbitrary H,K flags, or decoders not described by
this rank-nine common-pair model.

## The family cannot be normalized to two selected frames

A label-preserving anchor automorphism consists of four invertible scalar
basis changes `G_A,G_B,G_C,G_D`. The own blocks are identities, so the reader
change is the inverse source change. Consequently the block diagonal matrix
`G` must commute with the literal anchor.

Solving the complete linear centralizer equations gives exactly

```
G_A = diag(l,l,a),
G_B = G_C = diag(l,M2),
G_D = diag(l,l,d0),
```

where `l,a,d0` are nonzero and `M2` is an invertible two by two matrix. The
centralizer has dimension seven. The replay verifies equality of the full
36-variable nullspace with this explicit seven-dimensional space.

Let `Pi=K(HK)^-1 H` be the complement projection and `Z_g=V_g U_g`.
An induced ambient automorphism commutes with each `Z_g`; hence

```
tau = tr(Pi Z_A Pi Z_C)
```

is invariant. On this family the exact value is `1/c`. Thus label-preserving
automorphisms cannot reduce this entire family to two isolated frames. This
is a statement about that automorphism action, not a classification of all
possible physical group permutations or all admissible complements.

The diagonal special case scaling the C/B scalar coordinate 1 by `alpha`
maps `(t,s)` to `(alpha t,s/alpha)`. In particular every point `ts=-2` is
equivalent to `(t,s)=(1,-2)`, because `t` is then nonzero. This fact will
cover the exceptional locus without dividing by a vanishing flag pairing.

## Generic locus: c != 0 and d=c+1 != 0

Put

```
u=(1,s,0)^T, v=(1,t,0)^T, e0=(1,0,0)^T,
E=u v^T/c, S=I-u v^T/d, S^-1=I+u v^T.
```

The saturated new-group-3 flags in anchor coordinates are the literal row
`f=(0,0,0,0,0,0,-1,0)` and column
`k=(-1,0,0,-1,0,0,1,0)^T`. Set

```
P0=I-Pi,
a3=f P0, b3=P0 k,
a4=U_A2, b4=V_A2.
```

The exact pairings are `a3 b3=-d/c`, `a4 b4=1`, and the two cross pairings
are zero. The mandatory projector equations for the split into new group 3
are `a3 P=0`, `P b3=0`, `a4 P=a4`, and `P b4=b4`.

Since both displayed nonzero pairings are invertible, this is the complete
normal form

```
P=diag(1,Q,0), Q^2=Q, rank Q=2,
```

where Q acts on a four-space. Its first three coordinates are the image of

```
F=P0-b4 a4+(c/d)b3 a3,
X=F V_B S^-1, Y=U_B F.
```

Here `YX=I3`, `XY=F`; the fourth coordinate is the added ninth ambient
direction. These identities, the flag pairings, and every following frame
compression are verified as formal rational functions, not inferred by
specializing t or s.

In these coordinates the B source and reader frames are `[I3,0]` and
`[S;0]`. Write `A0=Q[:3,:3]`, `T=A0 S`, and `R=E+T`.

### Two determinant constraints

The own B+4 block has rank `3+rank R`, by eliminating the new group's own
identity block. Its tariff 4 implies `rank R<=1`.

For the B+C+3 block, eliminate the new group's identity and subtract B block
rows and columns from C. The remaining nonzero four by four matrix is

```
S4 = [[I-T, T u],
      [v^T T, -v^T T u]].
```

The full block has rank `3+rank S4`, so tariff 6 forces `det S4=0`.
For every rank-at-most-one R, the exact identities are

```
det S4 = c(1-tr R),
det(I3-A0) = (c+2)(1-tr R)+tr(E R).
```

For the first identity, add the first three columns times u to the last
column and then the first three rows times v^T to the last row. This gives
`[[I+E-R,u],[v^T,c]]`, whose Schur complement is `I-R`.
The second identity is a two-rank-one determinant expansion and introduces
no division by `c+2`.

Since `rank(I4-Q)=2`, its three by three principal minor is zero. Thus

```
tr R=1, tr(E R)=0.
```

In particular R has rank exactly one. Write `R=x y^T` with `y^T x=1`.

### The full C+D+3 constraint

The C+D own block is I6. Its compressed operator on the common four-space
is exactly

```
W4=diag(I3+w e0^T,0),  w=e0-u/d.
```

The fixed-one b4 direction sees zero. The full C+D+3 block therefore has
rank

```
7 + rank(Q-Q W4 Q).
```

One way to verify this equality is to factor the rank-three projector as
`J K`, `KJ=I3` and use
`rank(I6-L J K R)=3+rank(I3-K R L J)`; the fixed-one direction contributes
one to the latter rank. Tariff 7 consequently implies `Q W4 Q=Q`.

Taking trace gives `tr((W4-I)Q)=0`. The replay verifies the precise identity

```
tr((W4-I)Q) = R00-d^2/c
              +c det(I3-A0)-(d^2/c)det(S4).
```

Hence `R00=d^2/c`, which is nonzero. A trace constraint alone would not
contradict the rank-one conditions on R. The full matrix equation is needed.
Its upper-left three by three block says

```
A0 w e0^T A0 = A0-A0^2.                 (1)
```

The equality `tr(ER)=0` is
`(v^T x)(y^T u)=0`. These two exhaustive branches close (1):

* If `ER=0`, then `A0 x=x` and `v^T A0 w=-1`. Apply (1) to x. Its
  right side is zero, so `x0 A0 w=0`. The second identity makes `A0 w`
  nonzero, forcing `x0=0` and hence `R00=0`.
* If `RE=0`, then `y^T A0=y^T` and `e0^T A0 u=-d`. Apply `y^T` to (1).
  Since `y^T w=y0`, this gives `y0 e0^T A0=0`. The second identity and
  `d!=0` force `y0=0`, again `R00=0`.

Both contradict `R00=d^2/c`. These branches divide by no coordinate of x
or y, and by neither t nor s. They include c=-2 and the t=0/s=0 loci.

## Exceptional locus: c=-1, d=0, equivalently ts=-2

The generic normal form is unavailable because `a3 b3=0`. Use the proved
anchor automorphism to set `(t,s)=(1,-2)`. Reconstruct the common six-space
directly. In the exact coordinates

```
(b4,b3,m0,m1,external,last),
```

the source flags are `a4=e0^T`, `a3=e5^T`, and the reader flags are the first
two coordinate columns. Thus the complete split form is

```
P=diag(1,P5),
P5^2=P5, rank P5=2, P5 e0=0, e4^T P5=0.
```

No choice of coefficients within this form has been made. Factor

```
P5=X5 Y5, Y5 X5=I2,
X5=[alpha; x0; x1; x2; 0],
Y5=[0, y0, y1, y2, beta],
```

where alpha and the x's are rows of length two, and the y's and beta are
columns. This covers every allowed P5: use any basis for its image as X5;
the forced zero row and column follow from the flag equations and
injectivity of X5. There is no assumption about any of these rows or columns
being nonzero.

The exact C+D operator on these five coordinates is

```
Z5 = [[1,0,0,0,0],
      [0,1,0,0,0],
      [0,0,1,0,0],
      [0,0,0,0,0],
      [1,-1,0,0,1]].
```

As before, tariff 7 implies `P5 Z5 P5=P5`, equivalently
`Y5 Z5 X5=I2`. Subtracting `Y5 X5=I2` gives

```
beta(alpha-x0)=y2 x2.                    (2)
```

Define

```
Xbar=[x0;alpha;x1],
Yprime=[y0-beta,beta,y1],
Fbar=Xbar Yprime.
```

Equation (2) implies `Yprime Xbar=I2`, so Fbar is a rank-two idempotent.

The cap34 residual R is again `E+L_B P R_B`, now with
`E=-(1,-2,0)^T(1,1,0)`. Direct, rank-preserving row and column operations
give

```
L0 R N0 = Fbar + e1(e0-e1)^T,
L0=[[1,1/2,0],[0,1/2,0],[0,0,1]],
N0=[[3,-1,0],[-2,0,0],[0,0,1]].
```

Their determinants are nonzero. The replay checks this full identity with
sixteen independent formal entries of X5,Y5. Therefore cap34 forces the
matrix on the right to have rank at most one.

**Rank-drop lemma.** If F has rank two and `rank(F+u v^T)<=1`, then u belongs
to the column space of F. Indeed the space spanned by the columns of
`F+u v^T` and u has dimension at most two and contains the two-dimensional
column space of F. It must equal that space, and hence contains u. For
idempotent F, this implies `F u=u`. Applied here, `Fbar e1=e1`.

As `Yprime e1=beta`, we obtain

```
x0 beta=0, alpha beta=1, x1 beta=0.
```

Consequently `X5 beta=b3+mu*external` lies in the image of P5, where
`mu=x2 beta`. If mu were zero, b3 would lie in both the image and kernel of
the idempotent P5, impossible. Thus mu is nonzero. No division by mu is used
in the following contradiction.

The image of the new-group-3 projector also contains b4. The physical
source rectangle A+C to reader C+D+3 therefore contains the column span of
the anchor columns C0,C1,C2,D0 and the two new-group columns b4 and
`b3+mu*external`. The latter has anchor source image identical to b3,
because the external direction has zero anchor source coordinates.
These six columns on the six A+C scalar rows form

```
[[1,0,0,-1,0,-1],
 [0,0,0, 1,0, 0],
 [0,0,0, 0,1, 0],
 [1,0,0, 0,0,-2],
 [0,1,0, 0,0, 2],
 [0,0,1, 0,0, 0]].
```

Its determinant is exactly -1. The rectangle therefore has rational rank
at least six, while its literal physical binary tariff is five. This
excludes every exceptional projector satisfying caps34 and28. Cap22 is
not needed on this locus.

The boundary is materially different: an analytically derived rank-two P5
does pass all three original self caps34,22,28. Its independent complete
tariff replay has twelve violations, including the forced rectangle above.
That fixture is a diagnostic control, not a proposed valid lift.

## What remains open

The family provides infinitely many inequivalent complement choices, but
does not exhaust the two dimension-eleven Schubert varieties of source and
reader complements. In particular this proof fixes the A1 and D2 directions
on both sides and varies only one C direction. No argument reduces arbitrary
H,K to this family, no general anchor automorphism orbit classification is
claimed, and the nondegeneracy and full-group incidence constraints for
other complements remain to be solved. Different rank-eight anchors and
different higher-rank fits also remain outside scope.

This result removes a complete structural escape family from the local
lower-bound-certificate problem. It neither proves a global copy-cost floor
of 334 nor supplies a decoder at or below 296.
