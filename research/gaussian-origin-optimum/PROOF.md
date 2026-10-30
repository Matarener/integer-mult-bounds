# The unique optimal origin in the quadratic chirp family

This proof and its finite corroboration were produced by Nick Petalas.

## Model and statement

Let n >= 2, 1 <= W <= n-1 be integers, let a, theta > 0 and beta be real,
and put rho = 1+theta. Vertices are 0,...,n-1. For every real c define
the matrix N(c) to have diagonal 1, zero outside bandwidth W, and entries

```text
N(c)[i,j] = exp(-a rho h^2 - 2a beta h
                  + a theta ((i-c)^2-(j-c)^2)),  h=j-i,
0 < |h| <= W.
```

This is exactly the Gaussian chirp formula in Cinna Davis's PR #4100
gauge-free note, with t_i=i-c. We treat it as a specified mathematical
family. We do not assert that changing c is a free operation at its caller.
The individual fixed-origin results of James Reed's #4304/#4305 are
predecessors, not assumptions needed for the following optimization proof.

Write R_i(c) for the sum of off-diagonal entries in row i and
R(c)=max_i R_i(c)=||N(c)-I||_infinity. Then its unique minimum over all
real c occurs at

```text
c* = (n-1)/2 + beta/theta.                                      (1)
```

This optimizes only c. It is not a claim about all positive diagonal
scalings, nor does optimality imply R(c*)<1 in every parameter regime.

## Reflection and strict convexity

Expand the squares and put m=(n-1)/2 and u=c-c*. The exponent becomes

```text
-a ((1+2theta) h^2 + 2theta(i-m-u)h).                           (2)
```

Under i -> n-1-i, j -> n-1-j, u -> -u, both h and i-m-u change
sign. The bandwidth and endpoint truncation are preserved. Thus

```text
R_i(c*+u) = R_(n-1-i)(c*-u),    R(c*+u)=R(c*-u).                (3)
```

Each R_i is a finite sum of positive exponentials of affine functions
of c. Its second derivative is

```text
R_i''(c) = sum_(0<|j-i|<=W) (2a theta(j-i))^2 N(c)[i,j] > 0.    (4)
```

Every vertex has at least one neighbor, so the inequality is strict.
The finite maximum R is also strictly convex. Indeed, at an interior
convex combination choose a maximizing row. Its strict convexity bounds
its value strictly below the same convex combination of its endpoint
values, which are at most the corresponding endpoint maxima.

For u != 0, strict midpoint convexity and (3) give
R(c*) < (R(c*+u)+R(c*-u))/2 = R(c*+u). This proves existence and
uniqueness directly, even though R need not be differentiable.
No bounded numerical search supplies the universal quantifiers.

## A usable sufficient contraction bound

Suppose delta=1-(n-3)theta > 0. At c*, for k=|h| >= 1 the positive
coefficient q in the exponent -a q obeys

```text
q = (1+2theta)h^2 + 2theta(i-m)h
  >= (1+2theta)k^2 - theta(n-1)k
   = delta k^2 + theta(n-1)k(k-1)
  >= delta k^2.                                               (5)
```

The first inequality uses |i-m|<=m, including truncated boundary rows.
There are at most two entries for each k, hence

```text
R(c*) <= 2 sum_(k=1)^W exp(-a delta k^2)
       <= 2W exp(-a delta).                                   (6)
```

Delta>0 is sufficient for this bound, not necessary for the optimizer
or for contraction. The checker includes a regime with R(c*)>1.

## The ten-vertex prime-scale section

Use the parameters of James Reed's #4305: n=10, W=2,
theta=1/1444, beta=-1/2, a=9pi. Formula (1) gives c*=-1435/2,
and delta=1437/1444. Machin's identity and alternating arctangent
bounds give

```text
pi > 16(1/5-1/375)-4/239 > 157/50,
9pi * 1437/1444 > 28.                                        (7)
```

All terms of the exponential Taylor series are positive, and the exact
rational sum sum_(k=0)^12 7^k/k! is greater than 1024. Therefore
exp(7)>2^10 and exp(28)>2^40. Applying (6) proves

```text
||N(-1435/2)-I||_infinity < 4 exp(-28) < 2^-38.                (8)
```

The cited fixed-origin section at c=0 has the predecessor's bound 97/100.
Equation (8) is a new bound on a changed member of the same family,
not a re-computation of that predecessor. Uniqueness also proves the
actual norm strictly decreases when c moves from 0 to c*.

The scaling has a material cost. For D(c)[i,i]=exp(a theta(i-c)^2),
the ratio of its largest to smallest diagonal at c* is

```text
D(c*)[9,9]/D(c*)[0,0] = exp(81pi).                            (9)
```

Indeed, theta((9+1435/2)^2-(1435/2)^2)=9. Changing c is diagonal
similarity: N(c)=D(c) K D(c)^-1 for the same truncated Toeplitz K.
Thus the improvement of this infinity norm does not change eigenvalues.
We make no claim that its conversion, storage or precision costs fit a
physical supplier. No selected assumption is discharged by (8).
