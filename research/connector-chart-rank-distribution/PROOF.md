# The finite-field chart-repair rank enumerator

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let F be a finite field of order q. Let B0,B1:V -> W be linear maps on the
same finite-dimensional source, with dim W=n. Write

```text
a = rank B0,   b = rank B1,   c = dim(row B0 intersect row B1).
```

For 0<=r<=n, let N_r count the charts R in GL(W) for which
rank(B1-R B0)=r. The row spaces are subspaces of V*. The source dimension
can be arbitrary, subject to a+b-c<=dim V. The answer depends only on
(q,n,a,b,c), not on the matrices' remaining entries or dim V.

Use the following conventions:

```text
G_q(d,k) = Gaussian binomial [d choose k]_q, or 0 if k<0 or k>d;
J_q(d,k) = product_(i=0..k-1) (q^d-q^i), or 0 if k<0 or k>d;
J_q(d,0) = 1;
gamma = J_q(n,n)/J_q(n,a).
```

For 0<=t<=n define

```text
F_t = sum_(h=0..c, 0<=j<=n-b)
      G_q(c,h) G_q(n-b,j) q^((c-h)j+t(c-h)) J_q(t,a-c+h),
      where j=t-b+c-h.
```

Define D_0=F_0 and successively

```text
D_t = F_t - sum_(r=0..t-1) G_q(n-r,t-r) D_r.
```

Then the complete chart counts are N_r=gamma D_r. In particular, if
s=min(a,b) and u=max(a,b), the exact fraction attaining the minimum repair
rank u-c is

```text
N_(u-c)/|GL_n(F)| = q^(c(u-c)) J_q(u-c,s-c) / J_q(n,s).       (1)
```

The minimum-rank value itself is ywz65's #2680 theorem, which is cited,
not a new claim. The new result is the complete distribution and its
minimum-rank density. The proof below also explains each counting factor.
Empty dimensions and zero maps obey the same formulas.

## Normalize the source coordinates

Choose a basis of the intersection of the two row spaces, extend it
separately to bases of both row spaces, and then extend their union to V*.
Let the corresponding source coordinates be shared coordinates of dimension
c, B0-only coordinates of dimension a-c, B1-only coordinates of dimension
b-c, and unused coordinates. A basis change in W makes B1's nonzero columns
on its coordinates e1,...,eb.

As R varies, C=R B0 ranges over exactly the maps whose row space equals
row B0. Equivalently, its a potentially nonzero columns form an injective
map from F^a to W. There are J_q(n,a) such maps. Each occurs for exactly
gamma charts: after fixing the images of a independent vectors, extend their
images to an ordered basis in product_(i=a..n-1)(q^n-q^i) ways. Thus it
suffices to count C, and multiply the resulting counts by gamma.

Let E=span(e_(c+1),...,e_b), of dimension v=b-c, and let
B=span(e1,...,eb). The residual B1-C contains E in its image. Its remaining
columns are e_i-C_i for the shared coordinates and -C_i for the B0-only
coordinates.

## Count residual images contained in a t-space

Fix a t-dimensional T<=W. It can contain the residual image only if E<=T.
Put h=dim(T intersect B)-v and j=t-v-h. For such T, the number of choices is

```text
G_q(c,h) G_q(n-b,j) q^((c-h)j).                            (2)
```

To see this, pass to W/E and its distinguished c-dimensional subspace B/E.
Choose the h-dimensional intersection, choose the j-dimensional image in
W/B, and choose its lift modulo the intersection. These lifts are the
linear maps from a fixed j-space to a (c-h)-space, giving q^((c-h)j).
This standard subspace-intersection count uses no independence assumption
about random charts.

The condition im(B1-C)<=T prescribes C modulo T: shared coordinates map to
e_i mod T and B0-only coordinates map to zero. This prescribed quotient map
has rank c-h and kernel dimension a-c+h. An injective lift C must map that
kernel injectively into T, giving J_q(t,a-c+h) choices. On a fixed
complement of the kernel, each of the c-h basis vectors has q^t possible
lifts, independently. Their images are independent modulo T, so these
choices introduce no further injectivity condition. There are therefore

```text
q^(t(c-h)) J_q(t,a-c+h)                                   (3)
```

injective lifts. Multiplying (2) and (3) and summing h gives F_t. Thus F_t
counts pairs (C,T) with C injective, dim T=t and im(B1-C)<=T.

## Recover the exact ranks

If im(B1-C) has dimension r, its t-dimensional superspaces are in bijection
with the (t-r)-subspaces of W/im(B1-C). Consequently

```text
F_t = sum_(r=0..t) D_r G_q(n-r,t-r),                       (4)
```

where D_r counts injective C with residual rank r. The diagonal coefficient
in this triangular system is one, so the displayed recurrence recovers
all D_r uniquely. The chart multiplicity gives N_r=gamma D_r. This proves
the full distribution for every finite field, including extension fields.

## Extract the minimum density

First assume a<=b. The residual contains E of dimension b-c. At t=b-c,
j=-h in the formula for F_t, so only h=0 is possible. Hence

```text
D_(b-c) = F_(b-c) = q^(c(b-c)) J_q(b-c,a-c).
```

No lower residual rank can occur because E is contained in every residual
image. Dividing by J_q(n,a) proves (1) when a<=b. For the other order, the
bijection R -> R^-1 preserves the residual rank after swapping B0 and B1:

```text
rank(B1-R B0) = rank(B0-R^-1 B1).
```

Apply the first case to the swapped maps. This also proves the symmetry of
the complete chart counts in a and b. There is no assertion that the
numbers of injective C, before multiplying by gamma, are symmetric.

## Worked exact example

Over F2 take dim W=3, dim V=3 and

```text
B0 = [[1,0,0], [0,1,0], [0,0,0]],
B1 = [[1,0,0], [0,0,1], [0,0,0]].
```

Here a=b=2,c=1. The containment counts are (0,2,30,42). Triangular
inversion gives D=(0,2,24,16), and gamma=4. Thus among all 168 invertible
charts the residual-rank histogram is

```text
rank       0   1   2   3
charts     0   8  96  64.
```

Exactly 1/21 of the charts have the minimum rank one. Equal map ranks by
themselves do not determine this distribution: with c=2 the same n,a,b
instead give (4,60,104,0). These are counts of charts, not distinct residual
maps, scalar circuit words, or physically legal native adapters.
