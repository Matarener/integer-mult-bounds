# Exact sharp fixtures and normalization boundaries

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
These constructions establish nonvacuity and sharpness in the stated spaces;
they do not prove a universal decoder lower bound.

## All odd characteristics, every k from one through eight

Use the full E8 root-evaluation code `C`, norm-two root representatives,
the fixed dense binary labels, and an orthogonal root frame `h_1,...,h_8`.
Write `E_i=E(h_i)`, `d_i=delta_{h_i}`, `A={h_1,...,h_k}`,
`R=E_1-4d_1`, and `H=E_1-2d_1`. Over every field of characteristic other
than two, take the following `9+k` corresponding columns:

```
P=(H; E_b/2-R/4 [2<=b<=k]; R/4;
   -E_b/2 [2<=b<=k]; E_j/4 [j>k]; d_1),
Q=(d_1; d_b [2<=b<=k]; R+sum_{b=2}^k d_b;
   d_b-E_b/2 [2<=b<=k]; E_j [j>k]; H).
```

For each b, its unit and hole terms give

```
(E_b/2-R/4)d_b^t-(E_b/2)(d_b-E_b/2)^t
    =E_b E_b^t/4-R d_b^t/4.
```

The final summands cancel the added units in the middle Q column. Moreover
`H d_1^t+R R^t/4+d_1 H^t=E_1 E_1^t/4`. Thus the product is
`sum_i E_i E_i^t/4=G/2`, with all scalar constants explicit.

The coefficient list `(E_1,...,E_8,d_1,...,d_k)` is independent. One way to
see the only nontrivial part is to show that off-frame roots span the scalar
root space: each E8 root has 56 nonself nonorthogonal root lines, so for
each frame root h_i choose a nonorthogonal nonframe root r;
its reflection `r' = r-(r dot h_i)h_i` is also nonframe and
`r-r'=+h_i` or `-h_i`. Hence a codeword supported only on the frame vanishes.
The root frame itself has Gram `2I`, so this argument works over every odd
characteristic. Consequently `C intersect D_A=0`.

P contains d_1, recovers E_1 from H, and recovers each other frame direction;
its actual rank is nine and its actual space is `C+K d_1`. Q contains every
d_i, recovers E_b from the holes and E_1 from R, and contains the remaining
E_j. Its actual rank is `8+k` and its actual space is exactly `C+D_A`.
Every term is active. Distinct coefficient patterns prove each factor family
is pairwise nonproportional: code-only directions use different E_i, all mixed
b columns use their own E_b, and the two E_1-bearing mixed directions have
different d_1 coefficients. Their difference is a unit multiple of two,
so no projective collision appears in characteristic three.

The root-hole support identities are those of PR3755 `SPARSE-PAIR.md` section 2:
`U(E_i)=Lambda` and `U(d_i-E_i/2)=u_i^perp`, in every odd characteristic.
The two H/unit pairings cost zero. Each unit d_b costs one, since its P
factor has value one at b and the dense pairing has diagonal one. Each b-hole
costs eight against its full-support-span codeword. The middle R term and
untouched frame terms cost nine: R has exactly the support of E_1, and the
added orthogonal units do not cancel it. The sorted profile is

```
0,0, 1^(k-1), 8^(k-1), 9^(9-k),             COPY=72.
```

At k=2 this is the sharp eleven-term profile `(0,0,1,8,9^7)`, attaining
`7*9^q+8^q+1` for `0<q<1`. No concave sharpness for fixed k>2 is asserted.
A distinct eleven-term construction is also
retained as an independent checker control: its b/E3 shear gives the same profile.
All identities use only powers of two as denominators.

## Why activity, normalization and actual Q matter

Let `a=h_1`, choose a nonorthogonal root b, and put `H_a=E(h_1)-2d_a`.
Append to the ordinary eight-term frame the four atoms

```
(d_a,H_a), (-d_a,H_a), (d_a,d_b), (-d_a,d_b).
```

Every factor is nonzero, their four products cancel, and all four costs are
zero: H_a annihilates the binary label of a, while nonorthogonal a,b have
binary pairing zero. Raw ranks are `(9,10)` and raw Q is the full coordinate
pair extension. Yet the bill is still `8*9^q`. The repeated left ray violates
normalization; merging it deletes all four padding atoms and leaves ranks
`(8,8)`. Thus a strict moment conclusion for arbitrary raw ranks is false.

The k=1 normalized fixture supplies a separate boundary. Its ranks are
`(9,9)` and its bill is `8*9^q`. It lies inside every larger ambient
coordinate extension containing a, but does not span that larger space.
Ambient containment cannot replace actual full-Q equality in the normalized
full-coordinate theorem.

Finally, zero-factor padding can manufacture raw ranks `(9,10)` with no bill
change. Conversely an active cost-zero atom generally has a nonzero product
and cannot be deleted. The independent checker rejects deletion of such an
atom, omission of a compensating shear, wrong product scaling, and the inactive
or proportional-padding hypotheses.

## Exact finite evidence

`independent_model.py` independently reconstructs the standard E8 roots in the
declared PR3755 A8 order and checks all 120 root lines and 14,400 Gram/pairing
identities. No candidate module or certificate is imported. It directly checks
every product entry, actual scalar ranks, active factors, both projective
normalizations, actual Q equality, binary support ranks and actual COPY ranks
for k=1,...,8 and the distinct earlier eleven-term fixture over Q, F3, F5 and
F7, together with six semantic controls per field. Explicit exceptions keep
checks enabled under Python optimization.

These finite-field examples check the algebra above; they do not substitute
for its all-odd-field argument. The registered package replay runs both
implementations sequentially, with source authentication.

## A noncoordinate partial quotient attains 72

This construction witnesses the neighbor-supported partial-quotient corollary
with actual normalized ranks `(9,10)`, rather than a full coordinate extension.
In standard coordinates put

```
J_i=e_0-e_i (1<=i<=5),  u=e_6-e_7,  w=e_0+e_6,  v=e_0+e_7,
q=sum_i delta_{J_i}+delta_u,        b=delta_u+delta_w,
D'=span(q,b),                      A={J_1,...,J_5,u,w}.
```

All seven A roots are nonorthogonal to v. Their scalar rank is seven but
their binary-label rank is **six**: the five J labels are beta-orthonormal,
`u_label=sum_i J_i_label`, and the w label lies outside their span.
Consequently `w(q)=5`, `w(b)=2`, and every `q+t b` with t nonzero has weight
six. The coordinate pattern of `xq+yb` is `(x,x,x,x,x,x+y,y)`, so D' has
no coordinate unit ray. Its minimum basis cost is exactly seven, attained
by q,b. Thus D' is a proper noncoordinate subspace of D_A.

The declared model orients the roots as `h_i=-J_i` for i=1,...,5,
`h_6=u`, `h_7=w`. Complete them with the scalar normal `h_8=e_7`.
This normal basis has determinant one. Its dot-product dual is explicit:

```
d_i=e_i (1<=i<=5),
d_6=-e_0-sum_i e_i+e_6,    d_7=e_0+sum_i e_i,
d_8=-e_0-sum_i e_i+e_6+e_7.
```

Set `t_i=E(d_i)/2`, `L_q=2sum_{i=1}^5 t_i`, and
`L_b=-2sum_{i=1}^5 t_i+2t_6+2t_7`. Define

```
g_i=E(h_i)-2(q-b) (1<=i<=5),
g_6=E(h_6)-2b,    g_7=E(h_7)-2b,    g_8=E(h_8),
P=(L_q-delta_v, L_b-delta_v, t_1,...,t_8, delta_v),
Q=(q, b, g_1,...,g_8, q+b).
```

The high terms satisfy
`sum_i t_i g_i^t=G/2-L_q q^t-L_b b^t`. The two low code terms compensate
this exactly; subtracting delta_v from each introduces
`-delta_v(q+b)^t`, canceled by the last atom. Thus `P Q^t=G/2`.

The ten nonpivot Q columns form an actual basis of `C+D'`: their eight code
components form a scalar basis and q,b supply the quotient. Its dimension is
ten, since a nonzero codeword has binary support span nine while D' is supported
in a label span of dimension six. P has actual space `C+K delta_v` and rank
nine. Distinct high code components prevent proportional high Q columns;
q,b,q+b are three distinct quotient rays. On P the t_i form a code basis,
delta_v is outside C, and the two mixed columns have the same nonzero outside
coefficient but different nonzero code normals. Both families are therefore
active and pairwise nonproportional.

These facts hold in every odd characteristic. The basis and dual are integral
and unimodular, and all displayed denominators are powers of two. Every g_i
for i<=7 has exactly its ordinary root-hole support: the eligible correction
cancels its own value two, while changes at the other supported A coordinates
only flip values +1 and -1. Thus these seven columns have weight eight.
The scalar normal of L_q is `sum_i e_i`, and that of L_b is
`-sum_i e_i+e_6`. Both pair to zero with h_8, whereas the root v pairs to one.
Neither mixed P column can therefore be the singleton hole; singleton
classification gives both weight nine. Every other nonzero code column has
weight nine. Finally q+b is supported on neighbors of v, so its pivot costs zero.
The exact term profile is

```
(5,2,8,8,8,8,8,8,8,9,0),                COPY=72.
```

`partial_fixture.py` independently checks the actual orientations,
duality, determinant, eligibility, quotient strata, actual spaces and ranks,
normalization, all product entries and all binary charges over Q, F3, F5 and
F7. It also rejects deletion of the active free pivot, omission of a singleton
compensation, and a wrong quotient sign. The fixture works over all
odd fields; the broader partial-quotient theorem's field scope is separate.

## A cut-excluded pivot beyond the all-neighbor case

Keep the preceding A, D', dual normals, t_i, L_q, L_b and g_i. Choose a root
v whose label is outside U_A, with `beta(u_v,u_u)=beta(u_v,u_w)=0` and at
least one `beta(u_v,u_{J_i})=1`. Such a root exists: the line `e_1+e_6` is
nonorthogonal to u,w and orthogonal to J_2,...,J_5. Its label is outside U_A.
Indeed, inside the beta-orthonormal span of the five J labels and w, pairing
zero with w eliminates the w coefficient, and pairing zero with u (the sum
of the J labels) would force even binary norm, contradicting a root label's
norm one. Thus this A is not entirely supported on neighbors of v.

Use the eleven corresponding columns

```
P=(L_q, L_b-delta_v, t_1,...,t_8, delta_v),
Q=(q, b, g_1,...,g_8, b).
```

The original code compensation is unchanged. The sole new error
`-delta_v b^t` is canceled by the last atom, so the product is G/2.
The nonpivot Q columns remain an actual ten-column basis of `C+D'`.
P has actual space `C+K delta_v` and rank nine, and all its columns are
nonzero and pairwise nonproportional. In particular L_q is a sum of five
independent dual directions and is proportional to none of the t_i. The
code normal of L_b is `-sum_i e_i+e_6`, with exactly six nonzero scalar
coordinates. A standard root has either two or eight nonzero coordinates,
so this normal cannot become a root direction over any odd field. Singleton
classification therefore gives `w(L_b-delta_v)=9`.

The same support identities give term costs
`(5,2,8,8,8,8,8,8,8,9,0)`, totaling 72. The pivot is free because b is
supported on u,w, both pairing zero with u_v. However q does not vanish on
O_v, since at least one of its J coordinates lies there. The quotient is
therefore not contained in the coordinate space supported on v's neighbors.
This witnesses the broader cut-excluded partial-quotient hypothesis rather
than the all-neighbor special case. The fixture works over every odd field;
this does not enlarge the field scope of the general theorem.

This variant is normalized on the **left only**. Its two b readers on the
right are equal. Merging them replaces `(L_b-delta_v,b),(delta_v,b)` by
`(L_b,b)`, giving a ten-term, doubly normalized decoder of actual ranks
`(8,10)` with the same bill. The rank-(9,10) claim must not be attached to
that fully normalized decoder. In contrast, the preceding all-neighbor
partial fixture remains rank-(9,10) under normalization on both sides.

`cut_excluded_fixture.py` selects its pivot deterministically from the fixed
root order. Its audit checks the outside-span and nonneighbor conditions,
actual factor spaces and ranks, left normalization, repeated right readers,
all product entries and COPY ranks over Q, F3, F5 and F7. It also checks the
actual nonpivot basis cut (rank nine, exactly b vanishing), the explicit right
merge and full normalizer's rank drop, and three failed-product controls.

# A nine-coordinate equality fixture for strict-basis compensation

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
This exact construction works over every field of characteristic other than
two. Its universal identities and support argument are given below; separate
finite replays over Q, F3, F5 and F7 check the implementation.

Choose the eight standard E8 simple root lines a_i, retaining the fixed model
orientations h_i=r_{a_i}, and take v to be the line e_1-e_3, row 1 of the
fixed model, outside those eight lines. Put
`A={v,a_1,...,a_8}`. Let d_i be the dot-product dual basis, and write

```
c_i=(r_v,h_i),       beta_i=(r_v,d_i),
t_i=E(d_i)/2,        e=delta_v,         J=e-E(r_v)/2.
```

The simple-normal matrix has determinant plus or minus one. Its graph Γ,
joining nonorthogonal distinct h_i, is the connected E8 tree. Define

```
g_i=E(h_i)-2delta_{a_i}+c_i e+sum_{j adjacent i}delta_{a_j},
H_i=t_i-(beta_i/4)e,
U_i=2H_i-sum_{j adjacent i}H_j,
q_0=E(r_v)/4-e/2=-J/2.
```

Take eighteen corresponding columns

```
P=(J; U_1,...,U_8; H_1,...,H_8; e),
Q=(e; delta_{a_1},...,delta_{a_8}; g_1,...,g_8; q_0).
```

## Exactness and the actual pivot coordinate

The ordinary dual-basis product is `sum_i t_i E(h_i)^t=G/2`.
Expanding each g_i gives code readers `2t_i-sum_{j adjacent i}t_j` on the
a_i units and `-sum_i c_i t_i=-E(r_v)/2` on e. The displayed P adds precisely
the singleton coefficients needed to cancel the pivot e q_0^t.
Explicitly set `alpha_i=2beta_i-sum_{j adjacent i}beta_j`. Then

```
q_0=-e+sum_i (alpha_i/4)delta_{a_i}+sum_i (beta_i/4)g_i.
```

The e coefficient is exactly minus one because
`sum_i beta_i c_i=(r_v,r_v)=2`. Thus the actual e reader has encoder J,
the high encoders are H_i, and the remaining unit encoders are U_i.
This proves `P Q^t=G/2` with the free-pivot sign and all scalar constants fixed.

## Actual spaces and projective normalization

The seventeen nonpivot Q columns span `C+D_A`: the units recover all g_i's
code components. Row 0 is e_1-e_2 and belongs to the selected simple basis,
so the checker's first root outside that basis is the stated row 1.
An explicit orthogonal frame outside this fixed A is

```
e_0+e_2, e_0-e_2, e_1+e_4, e_1-e_4,
e_3+e_6, e_3-e_6, e_5+e_7, e_5-e_7.
```

Its Gram matrix is 2I, so the roots outside A span all eight scalar
dimensions over every odd field. Consequently `C intersect D_A=0` and
actual rank Q is seventeen. The checker also returns an explicit outside
frame with model indices `(2,10,17,34,52,77,95,119)` and checks its integral
Gram matrix; this is an all-odd-field rank certificate, not an extrapolation
from the three finite fields.

The eight H_i span the lifted code
`T={E(n)-(r_v,n)e/2:n in K^8}`. This space contains neither e nor J: the
code normal of J would be `-r_v/2`, whose lift has e coefficient 1/2 rather
than one. Thus P has actual rank nine. Singleton classification makes every
nonzero member of T have binary support weight nine.

In the H_i coordinates, U_i is row i of `2I-Adj(Γ)`. Each row has at least
two nonzero coordinates, and the eight closed neighborhoods of the connected
E8 tree are distinct. Therefore the U_i are pairwise nonproportional and
none is proportional to an H_i, in every odd characteristic. All sixteen
belong to T, so neither exceptional P ray collides with them. Q's seventeen
nonpivot members are a basis; q_0 is proportional to none, because its code
normal is r_v, distinct from every h_i, and it is not pure. Both full factor
families are active and pairwise nonproportional.
Here `2I-Adj(Γ)` is the chosen shear coefficient matrix; individual products
of the model-oriented roots may have either sign.

## Charges and the role of the cross shears

Every g_i lies in the root-hole hyperplane u_{a_i}^perp. Its correction at v
is allowed only when v is a neighbor; it doubles the old nonzero value.
Each other correction is at a graph neighbor and can delete at most one
nonself root-hole coordinate. Degree at most three and the remainder cut
bound 24 preserve the full binary span of dimension eight. These statements
hold in every odd field. The actual nonpivot basis weights and term costs are

```
Q basis: 1^9,8^8,                 actual basis bill=73,
COPY:    0,1^8,8^8,0,             COPY=72.
```

Thus the characteristic-zero strict basis floor 73 is sharp for this full
nine-coordinate space, and its coupled floor 72 is also sharp. The fixture
itself works over all odd fields; no general positive-characteristic strict
basis theorem is inferred.

Without the graph cross shears, U_i becomes 2H_i. That exact raw fixture has
eight repeated left rays and merges to ten terms of actual ranks (9,9).
The graph shears therefore solve a real normalization obstruction; a raw
rank assertion alone would not establish this full actual rank-seventeen
sharpness. The checker verifies this collapse as a positive control.

## Exact finite evidence

`a9_strict_fixture.py` checks all product entries, actual factor spaces and
ranks, active factors, both projective normalizations, the outside Gram
certificate, the actual pivot-coordinate expansion, all support weights and
actual COPY ranks over Q, F3, F5 and F7. It rejects deletion of either active
free atom and verifies the unsheared normalization collapse. The stated
minimum basis bill 73 is a characteristic-zero conclusion of the inherited
distance/capacity floor and this attaining actual basis. Over odd fields
the fixture certifies the actual basis bill
73 and COPY72; no universal positive-characteristic basis floor is asserted.
