# Both boundary ranks for mixed negative Q8 targets

## Statement

Work in the full formal group algebra R=F2[Q8], with distinct elements
1 and z, relations i^2=j^2=z, z^2=1 and ji=z ij. Every role contains
independent arbitrary dirty input. Binary scalar GL mixing is free.
Each paid factor is

```text
D_l=I+(1+[g_l])u_l v_l^T,  g_l in {i,j},  v_l^T u_l=1.
```

The endpoint is diagonal, with t_i copies of zi, t_j copies of zj and
identity on every other role. Set t=t_i+t_j>0, n=n_i+n_j, where n_i
and n_j count the two positive paid labels. The number of restored
roles is any finite integer.

**Theorem.** Every exact word satisfies

```text
2n+n_i >= 6t-t_i,       2n+n_j >= 6t-t_j,
therefore 5n >= 11t.
```

These are necessary constraints, not a sufficient or sharp count region.
They complement PR3578's stronger homogeneous 5t/2 bound. In particular,
the remaining two-zi/two-zj eight-call case is impossible. Its exact
minimum belongs to {10,12}; neither existence nor exclusion at ten is
proved here. The same {10,12} conclusion now holds for every choice of
four inverse-generator targets.

This is an author-written proof with finite corroboration. Independent
human and formal proof-kernel acceptance are unclaimed. It does not
supply physical execution, a complete supplier or a new kappa. The
selected frontier is unchanged.

## Ordered calls and the two cubic identities

The following identities are inherited from Nick Petalas/PR3570 and
PR3578, with the sign-sensitive chronology of PR3536 and cyclic
subspace method of PR3558. Their exact proof bytes are retained under
inputs/. We rederive the premises needed here.

Conjugate each paid projector by its accumulated free scalar mixing.
It remains a binary rank-one idempotent. Augmentation sends every paid
factor and the endpoint to I, so the remaining scalar map is I. Let X
contain the columns u_l and Y the rows v_l^T. Define L as the strictly
lower triangular part of the full-role matrix YX, with later calls in
later rows. Only after forming L, restrict X to the t active output
coordinates and Y to the t active input coordinates. Write E_i,E_j
for the complementary diagonal projectors onto the two call labels.
Write X_g,Y_g for the corresponding rectangular submatrices of X,Y.
The first-order identities are

```text
X_i Y_i=P_i,       X_j Y_j=P_j,       XY=I_t,
rank(P_i)=t_i,     rank(P_j)=t_j.
```

For clarity, put x=1+[i], y=1+[j], tau=1+[z], q=xy. The elements
1,x,y,tau,q,tau*x,tau*y,tau*q form a basis. Their masks in the group
basis 1,i,j,ij,z,zi,zj,zij are 1,3,5,17,15,51,85,255. Their successive
elimination pivots are 0,1,2,4,3,5,6,7, proving independence. Direct products give

```text
xx=yy=tau,       yx=q+tau+tau*x+tau*y+tau*q.
```

Every four-increment product is zero or tau*q, and every five-increment
product vanishes. For a pair of increments, the tau coefficient is
c(a,b), where c(i,i)=c(j,j)=c(j,i)=1 and c(i,j)=0. Its two cubic
coefficients have zero sum. For triples, in latest-to-earliest order,
the sum of the tau*x and tau*y coefficients is

```text
labels       iii iij iji ijj jii jij jji jjj
cubic sum      1   1   0   1   1   0   1   1.
```

This equals c(a,b)c(b,c)+[a=i and c=j]. Define

```text
H=L+E_i L E_j,       K=I+H,       C=E_i L^2 E_j.
```

H is strictly lower triangular, so K is invertible. The chronological
pair contribution is XHY. The cubic sum is X(H^2+C)Y. Neither formula
commutes role matrices: a chronological triple c>b>a contributes
u_c(v_c^T u_b)(v_b^T u_a)v_a^T with exactly that order.

The endpoint increments are zi+1=x+tau+tau*x and
zj+1=y+tau+tau*y. Their tau coefficient and cubic sum both equal I_t
on the active coordinates. Thus XHY=I_t and X(H^2+C)Y=I_t. With XY=I_t,

```text
XKY=0,       XK^2Y=XCY.                           (1)
```

Swapping i and j is an automorphism of Q8. It sends ij to ji=z ij,
which the swapped basis accounts for. Repeat the exact derivation in
that basis, keeping the same X,Y and full chronological L. This gives

```text
H'=L+E_j L E_i,   K'=I+H',   C'=E_j L^2 E_i,
XK'Y=0,          XK'^2Y=XC'Y,                     (2)
```

with K' invertible. The endpoint first-order sum, tau coefficient and
cubic sum remain I_t. This second orientation is essential.

## Cubic subspace bound

If XY=I_t, XKY=0 and K is invertible on n-dimensional call space, put
U=im(Y). X is injective on U and kills KU, so U and KU are disjoint.
Then KU and K^2U are disjoint as well. Both have dimension t and KU
lies in ker(X), of dimension n-t. Consequently

```text
dim(ker(X) intersect K^2U) <= n-2t,
rank(XK^2Y) >= 3t-n.                              (3)
```

This also proves n>=2t. If 3t-n is negative, the displayed lower bound
is simply weaker than nonnegativity. Apply (3) to (1) and (2). Since
C starts in j coordinates and ends in i coordinates, and C' reverses
them, r=3t-n obeys

```text
rank(X_i), rank(Y_j) >= r,
rank(X_j), rank(Y_i) >= r.                        (4)
```

No bound on the original dirty-role dimension occurs in this argument.

## Charge both ranks using the actual target product

For maps B:F2^m -> F2^t and D:F2^t -> F2^m, put a=rank(B),
b=rank(D), p=rank(BD). Restrict B to im(D). Rank-nullity gives

```text
b-p = dim(im(D) intersect ker(B)) <= m-a,
therefore a+b <= m+p.                            (5)
```

In the homogeneous predecessor p=0 for the opposite label. Here the
actual products are P_i and P_j, of ranks t_i and t_j. Using (5),

```text
rank(X_i)+rank(Y_i) <= n_i+t_i,
rank(X_j)+rank(Y_j) <= n_j+t_j.                   (6)
```

Each left side is at least 2r by (4). Hence
n_i+t_i>=6t-2n and n_j+t_j>=6t-2n, which are the theorem's two
inequalities. Adding them gives n+t>=12t-4n, or 5n>=11t.

This nonzero-product term cannot be discarded. B=D=I_2 has a+b=4,
m=2, p=2, and violates the zero-product conclusion a+b<=m. The new
step is to charge the two actual target ranks in (6), then use all
four boundary ranks from the two inherited cubic orientations.

## Four targets and scope

The full first-order identities before compression give
n_i=t_i mod 2 and n_j=t_j mod 2 by taking traces. Thus n=t mod 2.
For t=4 the theorem gives n>=9, and parity raises this to n>=10.
Twelve calls suffice by applying the corresponding positive generator
three times to each active coordinate. Every other coordinate stays
unchanged. Thus every four-target composition has exact minimum ten
or twelve. This closes only the balanced 2/2 eight-call handoff that
was left after PR3570's 3/1 and PR3578's homogeneous exclusions.

The factor 11/5 is not claimed sharp, and no admissible count pair is
claimed realizable. No ten-call word, longer-word classification,
physical caller, scalar/routing/restoration/hosting/precision invoice,
complete supplier, multiplication theorem or improved kappa is supplied.
Unknown physical costs are not zero. No dependent construction round
is started. Lean, Docker, the selected full cold replay, independent
human review and formal proof-kernel acceptance are unrun.

## Credit and source closure

Nick Petalas/PR3570 supplies the exact mixed cubic identity and subspace
lemma. PR3578 supplies the two-orientation boundary-rank method in the
homogeneous case. PR3536 supplies the sign-sensitive quadratic
chronology and PR3558 the cyclic subspace argument. Their unchanged
proof bytes, origin commit/path/blob/SHA256 and actual uses appear in
inputs/RETENTION.json. These are mathematical premises, not comparison
sources. Scientific replay needs no foreign Git objects or network.
The arguments used here are rederived above; the predecessor finite
three-role census and determinant conclusions are not premises.

The retained lineage includes Nick Petalas/PR3517's ordered-call
normalization, Tuafo/PR2900, ywz65/PR2587, PR3487, Aaron Wang/PR2318,
Cinna Davis, steph4n-gh and their credited Q8/register sources.
Arham Tahir/PR3137 and PR3461 concern separate physical/scalar costs.
No literature-priority claim is made for the standard rank inequalities.

## Open next questions

- Decide the balanced 2/2 four-target ten-call case using the complete
  eight-coefficient endpoint equations. Necessary counts alone do not
  construct a word or exclude one.
- Determine whether the uniform 11t/5 constant is sharp. First inspect
  simultaneous equality in (3) and (6), without treating finite rank
  fixtures as endpoint realizations.
- Bind any formal saving to an actual caller and full paid physical
  invoice before claiming a supplier or multiplication improvement.
