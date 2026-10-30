# Sharp spectral envelope for a shared support block

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let F be any field of characteristic two, let r >= 1, and let D in M_r(F)
be idempotent of rank k. For a matrix X, let z(X) be the algebraic multiplicity
of zero in its characteristic polynomial, equivalently dim ker(X^r).
Consider every ordered pair A,B in M_r(F) satisfying A+B=D. Then

```text
max [z(A)+z(B)] = r        if k=r;
                   2r-1   if 0<k<r and k is odd;
                   2r     if 0<=k<r and k is even.
```

The maximum exists and can always be attained by binary matrices after putting
D into its coordinate basis. Thus the formula is independent of the particular
characteristic-two field. In the original basis, conjugate both witnesses by
the same change of basis that carries diag(I_k,0) to D.

There is also a rigidity statement. If r >= 3 is odd, k=r-1, and the maximum
2r is attained, both A and B have exactly one nilpotent Jordan block of size r.
In particular, A^(r-1) and B^(r-1) are nonzero. The high zero multiplicity
cannot in this case be attained by replacing either summand with only short
nilpotent chains.

This is a local matrix theorem. It imposes no chronological support history,
external response conditions or physical realization on A,B.

## Upper bounds

Every r-by-r matrix has z <= r. This proves the 2r bound when k is even.
If k is odd, tr(A)+tr(B)=tr(D)=1 in F. Two nilpotent matrices have trace zero,
so at least one summand has z <= r-1. Consequently z(A)+z(B) <= 2r-1.

When k=r, an invertible idempotent is I, so B=I+A. The zero primary subspace
of B is the one primary subspace of A. The zero and one primary subspaces of A
have direct sum inside F^r, since t and t+1 are relatively prime. Their
dimensions are z(A) and z(B), respectively. Therefore z(A)+z(B) <= r.
These arguments apply over F itself; algebraic closure is not required.

## An explicit even-rank construction

First take even k and dimension n=k+1, so n is odd. Let J_n be the all-ones
matrix, let U be its strictly upper triangular part, and let L be its strictly
lower triangular part. In characteristic two,

```text
U+L = I_n+J_n = D_0,
J_n^2 = n J_n = J_n,
D_0^2 = D_0.
```

Both U and L are nilpotent. The kernel of D_0 is the all-ones line, and its
image is the coordinate-sum-zero subspace. Thus rank(D_0)=n-1=k.
For a literal coordinate endpoint, use the ordered basis

```text
e_1+e_n, ..., e_(n-1)+e_n, (1,...,1).
```

It is a basis: if a linear combination vanishes, its first n-1 coordinates
force all coefficients on the first n-1 vectors to equal the last coefficient.
The last coordinate then forces that coefficient to vanish, because n is odd.
The first n-1 vectors are fixed by D_0 and the last is killed. If S has these
basis columns, then

```text
S^-1 D_0 S = diag(I_k,0),
A_0=S^-1 U S, B_0=S^-1 L S,
z(A_0)=z(B_0)=k+1.
```

For any r>k, append r-k-1 zero coordinates to both matrices. This attains 2r
for every proper even rank, including k=0.

For odd 0<k<r, use the even-rank k-1 construction in dimension k. Add one
scalar coordinate with A=0, B=1, and then r-k-1 zero coordinates. Move the
core's zero coordinate after the added one coordinate. The endpoint is
exactly diag(I_k,0). Now A is nilpotent and B has precisely one nonzero
eigenvalue, so z(A)+z(B)=r+(r-1). Finally, for k=r take A=0 and B=I.
All entries and basis maps used here lie in F2 and remain valid after scalar
extension to F.

This explicit construction uses the classical method of splitting a zero-diagonal
matrix into two strict triangular parts. General trace-zero/nilpotent-sum
classification is not claimed as new. For context see Simion Breaz and Grigore
Calugareanu, [Sums of nilpotent matrices](https://math.ubbcluj.ro/~calu/su-ni.pdf),
Proposition 3, and the classical prescribed-diagonal theorem credited there.
The displayed special construction and the upper bounds make this proof
self-contained; no result from that paper is needed for verification.

## Forced full-length chains at corank one

Suppose r is odd, k=r-1 and z(A)+z(B)=2r. Both matrices are nilpotent. Put
E=I+D; since D is idempotent of rank r-1, E has rank one. If
v is in ker(A) intersect ker(E), then Dv=v and

```text
Bv = (D+A)v = v.
```

Nilpotence of B forces v=0. Hence E is injective on ker(A), giving
dim ker(A) <= rank(E)=1. A nilpotent matrix on a positive-dimensional space
has nonzero kernel, so dim ker(A)=1. Its nilpotent Jordan form has one block,
of size r. Interchange A and B for the other conclusion. This also proves
that the explicit corank-one construction has the necessary chain lengths.

## Consequence for larger support blocks

JoyboyBrian's [PR #5507](https://github.com/CrocSwap/integer-mult-bounds/pull/5507),
head `1691a6024b60bdf28d7a2eed13cb32d78e2ea5b4`, proves a complete two-owner
four-support funding obstruction. Its Section 3 studies exactly
A+B=diag(t), with k the number of Q flags. For r<=3 it bounds the sum by
2r-k except for the genuine r=3,k=2 exception. The global proof compensates
that exception through native chains and disjoint support classes.

The new envelope identifies the precise loss from using 2r-k in larger
local blocks. At a proper even rank the possible excess is k; at a proper
odd rank it is k-1. This excess is unbounded as support size grows. In
particular, r=5,k=4 has maximum 10, whereas 2r-k is 6. A binary coordinate
witness, whose rows are encoded with bit j as column j, is

```text
A = (11,25,13,21,10),
B = (10,27, 9,29,10).
```

It satisfies A+B=diag(1,1,1,1,0), A^5=B^5=0 and A^4,B^4 != 0.
The theorem supplies both the local ceiling and a necessary full-length-chain
condition in this corank-one family. It neither refutes #5507's four-support
theorem nor generalizes its global compensation. A larger caller still needs
its exact chronology, support ownership, native-chain restrictions and complete
paid/target invoice. No new controller or multiplication saving follows.

## Evidence boundary

The written proof carries all dimensions and all characteristic-two fields.
The standalone checker constructs every (r,k) with 1<=r<=33, 0<=k<=r.
Its small census enumerates every binary A through dimension four with D
fixed to each coordinate rank, so every ordered pair B=A+D is covered.
For each enumerated A, it compares dim ker(A^r), computed by binary matrix
powers and elimination, with the order at zero of a separate Leibniz
characteristic polynomial. It also checks every corank-one extremizer in
that census for the forced full chain. The finite checks are corroboration,
not a formal proof of the quantified theorem.

No predecessor verifier is imported or replayed. No native implementation,
rounded execution, supplier admission or complete multiplication theorem is
asserted. Independent human and formal proof-kernel review are unclaimed.
