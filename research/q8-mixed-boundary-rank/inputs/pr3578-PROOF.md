# A homogeneous mixed-Q8 rank bound

## Statement and model

Work in the full formal group algebra R=F2[Q8], where
`i^2=j^2=z`, `z^2=1`, `ji=z ij`, and z differs from 1.
Every role starts with independent arbitrary dirty data. Binary scalar GL
mixing is free. Each paid factor is

```text
D_l=I+(1+[g_l]) u_l v_l^T,   g_l in {i,j},   v_l^T u_l=1.
```

The endpoint is zi on t>0 distinguished roles and identity on all other
roles. The number of restored dirty roles is any finite integer. Let n_i
and n_j be the positive paid-label counts and n=n_i+n_j.

**Theorem.** Every such exact word satisfies

```text
2 n_i+n_j >= 4t,       2 n_i+3 n_j >= 6t,
2n >= 5t,             n_i=t (mod 2), n_j=0 (mod 2).
```

For the homogeneous zj endpoint exchange i and j throughout the count
inequalities. In particular, four identical inverse-generator targets
require ten or twelve calls. Ten is possible under these necessary
constraints only with six calls of the target's positive generator and
four of the other generator. Neither a ten-call construction nor an
exclusion is supplied. At equality 2n=5t, the counts must be
`n_i=3t/2, n_j=t`; trace parity forces t divisible by four.

This is an author-written proof with finite corroboration. Independent
human and formal proof-kernel acceptance are unclaimed. The theorem is
about a formal model, not a physical supplier or a new multiplication
exponent. In particular the selected frontier is unchanged.

## Inherited ordered-call identities, rederived

Push all free scalar maps through the paid calls. Each resulting binary
projector still has rank one and v_l^T u_l=1. Augmentation sends each
paid factor and the endpoint to I, so the remaining scalar map is I.
This is the normalization used in Nick Petalas/PR3517 and PR3570.

Let X contain the u_l columns and Y the v_l^T rows, and let L be the
strictly lower part of YX, with later calls indexing rows. Restrict Y
to the t active input coordinates and X to the t active output
coordinates. We continue to write X,Y for these compressed maps. L
still uses the original full-role YX; compression does not change it.
Group call coordinates by label, retaining order within each group:

```text
X=(X_i X_j),       Y=(Y_i; Y_j),
L=(L_ii L_ij; L_ji L_jj),
K_i=I+L_ii,       K_j=I+L_jj.
```

Both K_i and K_j are invertible, since L_ii and L_jj are strictly lower
triangular in their inherited chronological orders.

Put x=1+[i], y=1+[j], tau=1+[z] and q=xy. The eight elements
`1,x,y,tau,q,tau*x,tau*y,tau*q` form a basis of R. In the group basis
`1,i,j,k,z,zi,zj,zk`, their binary masks are
`1,3,5,17,15,51,85,255`. The exact products give

```text
xx=yy=tau,       yx=q+tau+tau*x+tau*y+tau*q.
```

All four-increment products are zero or tau*q, and five-increment
products vanish. The target increment zi+1 is x+tau+tau*x. Thus
first-order coefficients imply

```text
X_i Y_i=I_t,       X_j Y_j=0.
```

Set `H=(L_ii 0; L_ji L_jj)`. The tau coefficient gives
`XHY=I_t`; the q coefficient gives
`X_i L_ij Y_j+X_j L_ji Y_i=0`. Adding the latter relation gives the
second form `XH'Y=I_t`, with
`H'=(L_ii L_ij; 0 L_jj)`. Since XY=I_t, we obtain two triangular
quadratic identities:

```text
X_i K_i Y_i + X_j(L_ji Y_i+K_j Y_j)=0,             (Q)
X_i K_i Y_i + (X_i L_ij+X_j K_j)Y_j=0.            (Q')
```

The cubic sum, meaning the sum of the tau*x and tau*y coefficient
matrices, has triple coefficient, latest label first,

```text
iii iij iji ijj jii jij jji jjj
 1   1   0   1   1   0   1   1.
```

Every pair has cubic sum zero. The triple table is
`c(a,b)c(b,c)+[a=i,c=j]`, where
`c(i,i)=c(j,j)=c(j,i)=1` and `c(i,j)=0`. Consequently its complete
matrix is `X(H^2+C)Y`, where `C=E_i L^2 E_j`. No terms of degree four
or higher contribute. The target cubic sum is I_t. With K=I+H,

```text
XY=I_t,       XKY=0,       XK^2Y=XCY.             (C)
```

This is PR3570's mixed cubic identity. Swapping i and j is an
automorphism of Q8, taking k=ij to ji=zk. Repeating the same derivation
in the swapped basis gives (C') with H' and
`C'=E_j L^2 E_i`. The homogeneous target remains an inverse generator,
so its first-order sum, tau coefficient and cubic sum are again I_t.

## The rank argument

Let `a=rank(X_j)` and `b=rank(Y_j)`. Since X_jY_j=0,

```text
a+b <= n_j.                                      (1)
```

The equation X_iY_i=I_t forces rank(X_i)=rank(Y_i)=t. Sylvester's rank
inequality and invertibility of K_i give
`rank(X_i K_i Y_i)>=2t-n_i`. Equation (Q) bounds that rank by a;
equation (Q') bounds it by b. Hence

```text
a,b >= 2t-n_i,       n_j >= 4t-2n_i.              (2)
```

For completeness, the cubic subspace lemma from PR3570 is as follows.
For maps X,Y satisfying XY=I_t and XKY=0 with K invertible, set
U=im(Y). X is injective on U and kills KU, so U and KU are disjoint.
Then KU and K^2U are disjoint too. Both have dimension t, and KU is
contained in ker(X), which has dimension n-t. Therefore
`dim(ker(X) intersect K^2U)<=n-2t`, and

```text
rank(XK^2Y)>=3t-n.                               (3)
```

For (C), rank(XCY)<=rank(Y_j)=b, because C starts in the j call
coordinates. For (C'), rank(XC'Y)<=rank(X_j)=a, because C' ends in
the j call coordinates. Applying (3) to both gives

```text
a,b >= 3t-n,       n_j >= 6t-2n.                  (4)
```

Equations (2) and (4) are exactly the two claimed count inequalities.
Adding them gives 4n>=10t. The argument is in finite call space and
places no fixed limit on the original role dimension. Restored dirty
workspace and arbitrary binary scalar mixing are already covered.

## Parity and the four-target consequence

Taking traces in the full first-order equations gives
`n_i=t mod 2` and `n_j=0 mod 2`, because every paid projector has trace
one. If 2n=5t, equality in both count inequalities forces
`n_i=3t/2, n_j=t`; the two parities force t divisible by four.

For t=4, 2n>=20 and n=0 mod 2 give n>=10. At n=10 the two inequalities
force n_i>=6 and n_i<=6. Twelve calls suffice by applying i three
times to each active coordinate, with every spectator untouched.
Thus the exact minimum belongs to {10,12}; no existence claim at ten
is made. The result closes only PR3570's homogeneous eight-call
question. The 2/2 eight-call and 3/1 ten-call questions remain open.

## Credit, source closure and limits

Nick Petalas/PR3570 supplies the mixed cubic identity and subspace
lemma. PR3536 supplies the sign-sensitive quadratic chronology and
PR3558 the cyclic subspace method. Exact unchanged proof bytes are
retained under inputs/, with origin commits, paths, blobs and SHA256
in inputs/RETENTION.json. Their necessary arguments are rederived
above. These are actual proof premises, not comparison-only sources.

PR3517 retains the ordered scalar-core normalization lineage;
Tuafo/PR2900, ywz65/PR2587, PR3487, Aaron Wang/PR2318, Cinna Davis,
steph4n-gh and the retained Q8/register-model sources keep their credit.
Arham Tahir/PR3137 and PR3461 concern separate physical and scalar costs.

The new step uses the vanishing homogeneous opposite-label block
X_jY_j=0 to charge both boundary ranks, together with the two triangular
quadratic and cubic orientations. The underlying finite-dimensional
rank inequalities are standard. No literature-priority claim is made.
The complete necessary-count region is not claimed sufficient or sharp.
No solver, minimum-length census, physical realization, complete cost
invoice, supplier or new kappa is established. The selected full cold
replay, Lean, Docker, independent human and formal proof review are unrun.

## Open next questions

- Decide the homogeneous four-target ten-call case. The only admissible
  counts are six positive target-generator calls and four opposite calls.
  Start with the exact full eight-coefficient endpoint equations.
- Decide the untouched mixed 2/2 eight-call boundary separately; this
  proof requires X_jY_j=0 and does not apply to it.
- Bind a formal saving to an actual caller and full physical bill before
  claiming any supplier or multiplication-exponent improvement.
