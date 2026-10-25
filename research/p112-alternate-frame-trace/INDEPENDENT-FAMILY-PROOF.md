# Independent audit of the two-parameter common-frame obstruction

The complete nondegenerate family is excluded for the fixed asymmetric
anchor. Write H_t=(C0+t C1,A1,D2), K_s=(C0+s C1,A1,D2), and c=1+st.
The combined-frame construction requires c nonzero. Other common frames,
other anchors, and general rational decoders are outside this result.

Two independent standard-library replays accompany this note:
`independent_generic.py` and `independent_exceptional.py`.
They authenticate the local `FIXTURE.json` anchor/flag records, reconstruct
their own rational factorizations, and import no producer algebra. The
registered foundational `verify.py` checks those flag spaces against the two
declared external physical inputs; the exceptional checker also consumes
those inputs directly for its tariff and all-rectangle control. The generic
calculation is formal over Q(s,t); the exceptional calculation uses sixteen
free variables for its complete factorization. Neither samples parameters. Both compare exact results against their
committed receipts by default; `--write-receipt` is explicit maintenance.

## Generic branch: d=c+1 nonzero

Let u=(1,s,0)^t, v=(1,t,0)^t, E=uv^t/c, S=I-uv^t/d. Thus v^t u=c,
E is a rank-one projector, and S^{-1}=I+uv^t. Independently constructing
the middle projector F from the combined frame and its two nondegenerate
flags gives the four-coordinate basis

    X=[F V_B S^{-1}, e_external],  Y=[U_B F; e_external^t].

The replay verifies YX=I4, XY=F, the complete flag equations, L_B=[I3,0],
R_B=[S;0], and every literal compressed matrix used below. No unrecorded
coordinate chart or pivot minor is assumed.

Every remaining split is a rank-two idempotent Q on Q4. Put A=Q[:3,:3],
T=AS and R=E+T. Cap34 gives rank R at most one. Cap22 gives the determinant
of [[I-T,Tu],[v^t T,-v^t T u]]. Add the first three columns times u to the
last column, and the first three rows times v^t to the last row. The result
is [[I+E-R,u],[v^t,c]]. Its Schur complement at nonzero c is I-R; hence

    det(S4)=c(1-tr R).

The complementary projector minor, without dividing by c+2, is

    det(I-A)=(c+2)(1-tr R)+tr(ER).

These identities hold for every rank-at-most-one R=xy^t, including zero;
the replay checks them as polynomial identities. Therefore tr R=1 and
tr(ER)=0. In particular rank R is exactly one, and y^t x=1.

The literal cap28 operator has middle block W=I+w e0^t, w=e0-u/d, and an
additional zero coordinate. Its cap requires Q diag(W,0) Q=Q. Trace and
idempotence imply e0^t A w=Q33. Since

    A=(R-E)(I+uv^t),  A w=R e0-u/c,
    tr A=1-d,  Q33=d+1,

we obtain R00=d^2/c, which is nonzero.

But tr(ER)=(v^t x)(y^t u)/c=0, so either ER=0 or RE=0. The top block of
the cap28 equation gives A w e0^t A=A-A^2.

* If ER=0 then Ax=x and v^t A w=-1. Applying the last identity to x
  forces x0=0.
* If RE=0 then y^t A=y^t and e0^t A u=-d. Left multiplication by y^t
  forces y0=0.

Either case gives R00=x0 y0=0, a contradiction. These cases include zero
coordinates and c=-2; the only divisions are by the stated nonzero c,d.

## Exceptional branch: st=-2

Simultaneously scaling axis1 of anchor groups B,C by r on the source side
and r^{-1} on the reader side fixes the literal anchor and every whole-group
rectangle rank. This sends (t,s) to (rt,s/r). Since t is nonzero here,
r=1/t reduces the entire branch to t=1,s=-2. The replay checks the literal
anchor's commutation with this block gauge by its nonzero-entry pattern.

The flag pairing becomes diag(0,1). In the complete basis
[b4,b3,m0,m1,external,last], every admissible rank-three projector is
diag(1,P5), where P5 has rank two, first column zero and last row zero.
It admits a full-rank factorization

    P5=X5 Y5,   Y5 X5=I2,
    X5=[alpha;x0;x1;x2;0],
    Y5=[0,y0,y1,y2,beta].

The zero row/column conditions propagate to X5/Y5 by their full ranks, so
this factorization omits no boundary case. The literal cap28 matrix implies
Y5 Z5 X5=I2. Set

    Xbar=[x0;alpha;x1],  Yprime=[y0-beta,beta,y1].

Direct multiplication gives Yprime Xbar=Y5 Z5 X5=I2. Consequently
F=Xbar Yprime is a rank-two idempotent on Q3. The literal cap34 residual is

    L0 [F+e1(e0-e1)^t] N0,
    L0=[[1,-1,0],[0,2,0],[0,0,1]],
    N0=[[0,-1/2,0],[-1,-3/2,0],[0,0,1]],

with both matrices invertible. The cap forces the bracket's rank at most
one. A rank-one update decreasing a rank-two matrix's rank must have its
update column in the original image: otherwise col(F) could not be
contained in the sum of the updated image and that column with rank two.
Thus e1 lies in im F, and idempotence gives F e1=e1. Since Yprime e1=beta,

    Xbar beta=e1,
    X5 beta=b3+mu*external.

The scalar mu is nonzero: otherwise the nonzero killed vector b3 would
belong to im P5, impossible for an idempotent. The group3 image contains
both b4 and this vector. They are independent and may be selected as two
of its three basis vectors. The external coordinate has zero anchor image,
so their anchor columns are exactly L b4 and L b3.

On source groups A,C and reader groups C,D,new3, select the columns
C0,C1,C2,D0,Lb4,Lb3. Their literal six-by-six determinant is -1. The
authenticated physical tariff of this rectangle, masks (5,28), is five.
Its rank is therefore at least six where at most five is required. This
excludes the exceptional branch without using cap22.

## Controls and limits

The exceptional replay reconstructs one declared rank-nine three-cap
fixture. Caps22/28/34 are exactly (6,6),(7,7),(4,4), yet twelve of all 3,969
rectangles fail, including (5,28). This is a control for why the additional
rectangle matters, not a coefficient search. Deleting the forced Lb3 column
destroys the invariant minor, as a targeted fault control.

Combined with the generic branch, this excludes every rational split in
this specified two-parameter nondegenerate common-frame family. It does
not close the general fixed-anchor gluing problem and does not change any
decoder invoice or selected bound.

## Independent automorphism supplement

The generic replay independently encodes all 144 block-commutator equations
in 36 variables. Their rank is 29, and the seven claimed block matrices
are independent commuting solutions, so they span the complete centralizer.
It also verifies the formal invariant `tr(Pi Z_A Pi Z_C)=1/(1+st)` directly
from its own rational-function complement projection. These checks support
the stated orbit distinction but are not premises of the obstruction.
