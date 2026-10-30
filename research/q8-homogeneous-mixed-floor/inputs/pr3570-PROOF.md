# Mixed positive-Q8 cubic count inequalities

## Model and result

Work in the full formal group algebra F2[Q8], with
`i^2=j^2=z`, `z^2=1` and `ji=z ij`. The symbols z and 1 are distinct.
All roles contain independent arbitrary dirty inputs. A paid factor is

```text
D_l=I+([g_l]+1) u_l v_l^T,  g_l in {i,j},  v_l^T u_l=1.
```

The vectors and free scalar GL mixing are binary. Call zero acts first.
The diagonal endpoint has t_i copies of zi, t_j copies of zj and identity
on every other role, which must restore. Put `t=t_i+t_j>0`,
`n=n_i+n_j`, where n_i and n_j count the paid labels.

**Theorem.** With any finite number of restored dirty roles,

```text
n+min(n_i,n_j)>=3t,
equivalently 2n_i+n_j>=3t and n_i+2n_j>=3t.
```

These are necessary count constraints, not an attainable-count
classification. Together with the inherited `n>=2t` and label parities,
they force n_i=n_j=t whenever n=2t. Thus equality requires t, t_i and t_j
all even. In particular the exact minimum for three zi targets and one
zj target, or with i/j exchanged, is **ten or twelve**, with arbitrary
finite restored dirt. Neither length is decided here.

This is an author-written mathematical proof with finite corroboration.
Independent human and formal proof-kernel review are unclaimed. No
physical caller, complete supplier, multiplication theorem or kappa
improvement is established.

## Normalization and chronological call space

As in Nick Petalas/PR3517 and PR3536, conjugate each paid projector by
its accumulated binary scalar mixing. Augmentation sends each paid
factor and the endpoint to I, so the remaining scalar factor is I.
This preserves the label counts, order and rank-one idempotence.

Let X have the columns u_l, Y the rows v_l^T, and `A=YX`.
Let L be the strictly lower triangular part of A. Let E_i and E_j be
the complementary diagonal call-space projectors onto the two labels.
The first-order x and y coefficients of the endpoint give

```text
X E_i Y=P_i,   X E_j Y=P_j,   XY=P=P_i+P_j.
```

Here P_i and P_j are the active coordinate projectors, and rank(P)=t.
The separate rank inequalities give `n_i>=t_i`, `n_j>=t_j`.
Taking traces gives `n_i=t_i mod 2`, `n_j=t_j mod 2`, since every paid
projector has trace one. In particular `n=t mod 2`.

Define

```text
c(i,i)=c(j,j)=c(j,i)=1, c(i,j)=0,
H[b,a]=L[b,a] c(g_b,g_a),
H=L+E_i L E_j,       K=I+H.
```

H is strictly lower triangular, so K is invertible. PR3536's quadratic
coefficient identity is `XHY=P=XY`, hence `XKY=0`. The next section
rederives it while retaining the two cubic coefficients.

## The exact seven-dimensional quotient

In F2[Q8] put `x=1+[i]`, `y=1+[j]`, `tau=1+[z]` and `q=xy`.
The following eight elements form a basis:

```text
1, x, y, tau, q, tau*x, tau*y, tau*q.
```

Their masks in the group basis `(1,i,j,k,z,zi,zj,zk)` are respectively
`(1,3,5,17,15,51,85,255)`. Successive new pivots, or the explicit
256-element binary coordinate bijection in the replay, prove independence.
The element `tau*q` is the sum of all eight group elements. It spans a
two-sided ideal, annihilates x and y on either side, and is unchanged by
multiplication by a group element. Quotient by that ideal. The remaining
seven displayed elements are a basis of an associative quotient algebra.

The positive-increment pair identities in this quotient are

```text
xx=yy=tau,  xy=q,  yx=q+tau+tau*x+tau*y.
```

Both tau and q are quadratic. Every product of four increments is zero
in the quotient. This follows directly by reducing the sixteen four-letter
products with the displayed Q8 relations: in the full algebra they are
zero or tau*q. Multiplying by a further increment gives zero already in
the full algebra. Thus no term with four or more paid increments can
contribute to the two cubic coefficients.

The tau coefficient of a pair is c, giving `XHY=P`. The two cubic
coefficients of the pair yx are both one, so their sum is zero; every
other pair has cubic sum zero as well. In a single increment the sum
is also zero. For three increments, listed latest to earliest, the
sum of the tau*x and tau*y coefficients is

| Labels | iii | iij | iji | ijj | jii | jij | jji | jjj |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cubic sum | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 |

Equivalently for labels a,b,c this sum is

```text
c(a,b)c(b,c) + [a=i and c=j].
```

The complete exact products in the full algebra are respectively
`tau*x`, `tau*y`, `tau*x+tau*y+tau*q`, `tau*x`, `tau*y`,
`tau*x+tau*y+tau*q`, `tau*x`, `tau*y`. These also show the four-letter
claim above without relying on an uncomputed filtration assertion.

The chronological triple contribution is
`u_c (v_c^T u_b)(v_b^T u_a) v_a^T` for c>b>a. Consequently the sum of
the two cubic coefficient matrices is exactly

```text
X (H^2+E_i L^2 E_j) Y.
```

No role matrices have been commuted. The target zi has expansion
`1+x+tau+tau*x`, and zj has `1+y+tau+tau*y`. Its cubic sum is P.
Writing `C=E_i L^2 E_j` and using characteristic two gives

```text
X(H^2+C)Y=P=XY,
X K^2 Y=X C Y,       rank(C)<=min(n_i,n_j).
```

The noncommutative correction C is essential. The legal one-role word
with chronological labels `(j,i,i)` has endpoint zj and `XCY=1`, while
`XH^2Y=0`. Dropping C would therefore import the cyclic argument into
a mixed-label setting incorrectly. The replay includes this exact control.

## The subspace rank inequality

Restrict Y to the active t-dimensional input space and project X to its
active output coordinates. Write the resulting maps Y0 and X0. Then

```text
X0 Y0=I_t,       X0 K Y0=0,       X0 K^2 Y0=X0 C Y0.
```

Let U=im(Y0), so dim(U)=t and X0 is injective on U. Since X0 kills KU,
`U intersect KU={0}`. K is invertible, hence
`KU intersect K^2U=K(U intersect KU)={0}`.

Set V=ker(X0), of dimension n-t, and W=K^2U, of dimension t. The
subspace KU lies in V and is disjoint from W. Therefore

```text
dim(V intersect W)+t<=dim(V)=n-t,
rank(X0 K^2 Y0)=t-dim(V intersect W)>=3t-n.
```

This standard finite-dimensional argument also gives n>=2t from
`U intersect KU={0}`. On the other hand the cubic identity gives

```text
rank(X0 K^2 Y0)=rank(X0 C Y0)<=rank(C)<=min(n_i,n_j).
```

Combining proves the theorem. This argument works directly in the
n-dimensional call space; no finite role census, solver result,
workspace-reduction theorem or independent finite exclusion is a premise.
It extends the cyclic subspace argument in PR3558 by charging the
noncommutative cross term, rather than assuming it vanishes.

## The first asymmetric four-negative consequence

If n=2t, the theorem forces min(n_i,n_j)>=t, hence n_i=n_j=t.
The first-order trace parities then require t_i and t_j to have the same
parity as t. Their sum is t, which forces t even and both multiplicities
even. For t_i=3 and t_j=1, the inherited quadratic rank floor gives
n>=8, but n=8 would require n_i=n_j=4, contradicting the two odd label
parities. Since n=t mod 2, n>=10. Twelve calls attain the endpoint by
using three copies of each target's positive generator on its coordinate,
leaving every spectator untouched. Thus the minimum is ten or twelve.

The count relaxation permits ten, for example (n_i,n_j)=(5,5). This is
not a ten-call word. For four homogeneous targets and the 2/2 shape,
the new count relaxation still permits (4,4). The full eight-call
question for those shapes and the ten-call 3/1 question remain open.
No claim is made that the degree-two quotient realizes the 3/1 shape
at eight. PR3551 only supplied an explicit homogeneous quadratic word.

## Sources, credit and limits

Exact unchanged proof bytes of Nick Petalas/PR3536 and PR3558 and the
actual PR3551 witness are retained under inputs/, with origin commits,
paths, blobs and SHA256 in inputs/RETENTION.json. The used mathematical
premises are the quadratic chronology and cyclic subspace method;
the necessary arguments are also supplied above. The witness is a
scientific false-positive control, not a comparison-only dependency.
The replay needs no Git, network or foreign object cache.

PR3517 retains the ordered-call formulation and normalization lineage;
Tuafo/PR2900 retains image restriction, ywz65/PR2587 coefficient support,
and PR3487 the common-kernel quotient. Aaron Wang/PR2318, Cinna Davis,
steph4n-gh and the retained register-model lineage keep their credit.
Arham Tahir/PR3137 and PR3461 concern separate physical and scalar costs.

The new result is the mixed cubic identity, its label-count inequalities
and the arbitrary-dirty-workspace asymmetric four-negative exclusion.
The count polytope is not asserted sharp. No eight-call word in the
remaining shapes, ten-call witness/exclusion, actual caller, supplier,
new kappa or selected-frontier change is supplied. No solver or larger
endpoint census ran. Independent human and formal acceptance and the
selected full cold replay remain unclaimed.

## Open next questions

- Does the 3/1 shape have a ten-call word or require twelve? Start from
  its exact full-Q8 ten-call equations and the allowed label counts;
  a candidate must pass every coefficient and arbitrary dirty input.
- Can an eight-call homogeneous or 2/2 word satisfy the necessary balanced
  (4,4) paid-label condition? The cubic correction must have rank four.
  Its rank condition is necessary, and neither construction nor exclusion
  follows from the present bound.
- Could an actual caller use any improved formal word below its complete
  alternative bill? Legal scalar preparation, routing, ownership,
  restoration, hosting, precision and recursive costs remain unresolved.
