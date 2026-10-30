# Proof of the sharp ten-call minimum

## Statement and boundary

Let G=AGL_2(F2), with composition acting on the rightmost argument first.
Write points as (x0,x1) and set

```text
a(x0,x1)  = (x0+x1,x1),      b(x0,x1)  = (x0,x0+x1),
tx(x0,x1) = (x0+1,x1),       ty(x0,x1) = (x0,x1+1),
s = aba,   h = s tx,         h^-1 = tx s.
```

For any finite R>=4, work in M_R(F2[G]). Every data and spectator role has
arbitrary initial contents. The required complete endpoint is

```text
T = diag([h],[h^-1],[tx],[ty],1,...,1).
```

A paid call is D_N(g)=I+([g]+1)N, with g in {a,b,tx,ty}, N=uv^T over F2,
and v^T u=1. Arbitrary scalar GL_R(F2) maps are free and may be interleaved.
The exact minimum paid length is ten, independently of R. No other address
maps, clean allocations, singular scalar operations, COPYs, resets or residual
couplings are allowed. This is a formal algebra theorem, not a native tariff.

The upper word and four-role target are Cinna Davis's PR #1745. The new result
is the matching lower bound, including arbitrary finite restored dirty roles.
The proof separates the two disjoint classes of paid letters.

## At least six a/b calls

The homomorphism G -> GL_2(F2) forgets the translation. It sends tx and ty
to the identity and sends both h and h^-1 to s. Extend it linearly to the
group algebras and entrywise to the role matrices. A putative circuit becomes
a circuit for diag([s],[s],1,...,1), with only its a/b calls remaining.
The six-call lower bound for this two-swap endpoint is already established
by commdata2338's PR #1414. The following cut restates the needed bound
without importing a predecessor executable or finite search.

The group L=GL_2(F2) has the six distinct elements

```text
1, a, b, ab, ba, s=aba=bab.
```

Use its left regular representation, and split the address basis into
H={1,a,b} and K={ab,ba,s}. Direct multiplication gives

```text
a H = {a,1,ab},    b H = {b,ba,1},    s H = {s,ab,ba}=K.
```

Thus each of a and b has crossing rank one from H to K, while s has
crossing rank three. Include every scalar role in each address half. For
any represented matrix M let q(M)=rank(M[K,H]). Block multiplication gives

```text
(AB)[K,H] = A[K,H] B[H,H] + A[K,K] B[K,H],
q(AB) <= q(A)+q(B).
```

A scalar role map never changes the address and has crossing block zero.
The crossing block of D_N(a) or D_N(b) is N tensor E, where E is the
one-entry crossing matrix of that letter. It has rank one. A projected
translation call is the identity. The complete endpoint has two disjoint
s blocks, hence crossing rank 3+3=6. Identity spectators contribute zero.
Subadditivity proves that the original word contains at least six a/b calls.
This argument does not bound or compress the number of roles.

The cut-rank method is standard. Adam Gall's PR #1941 and the odd-dihedral
joint-tariff package provide related all-register cut arguments. The two-swap
minimum itself is predecessor work, not a newly claimed result here.

## At least four translation calls

Use the homogeneous representation

```text
rho(A,t) = [ A  t ]
           [ 0  1 ].
```

After applying rho entrywise and grouping all 2R coordinate rows before the
R homogeneous-coordinate rows, every represented operator has block form

```text
M = [ L  U ]
    [ 0  C ].
```

Here U is a 2R-by-R matrix over F2. Define tau(M)=rank(U). For two such
matrices,

```text
U(M1 M2) = L1 U2 + U1 C2,
tau(M1 M2) <= tau(M1)+tau(M2).
```

This rank inequality requires no commutation or independence of intermediate
data. Scalar GL_R mixing has U=0, since it acts as B tensor I2 on coordinate
rows and as B on homogeneous rows. Calls with labels a or b also have U=0.
A translation call with nonzero vector t has

```text
U(D_(uv^T)(t)) = (u tensor t) v^T.
```

Both vectors are nonzero, so this block has rank one. The dot-product
condition is required by the paid alphabet, though nonzero rank alone is
enough for this part of the lower bound. Consequently tau of the final
endpoint is at most the number of tx/ty calls.

The four nonzero translation vectors of h,h^-1,tx,ty are, respectively,
(0,1), (1,0), (1,0), (0,1). Each occupies a different role. Thus the first
four columns of U(T) have disjoint nonempty coordinate supports, and all
other columns are zero. They are linearly independent, so tau(T)=4.
Every complete circuit therefore contains at least four tx/ty calls.

These translation calls are disjoint from the a/b calls counted above.
The total paid length is at least 6+4=10. The two representations are used
only for necessary lower bounds. Neither is a sufficient endpoint oracle.

## Attainment and conclusion

Use coordinate role projectors. In chronological order execute

```text
role 0: tx, a, b, a
role 1: a, b, a, tx
role 2: tx
role 3: ty
```

The first row produces s tx=h, the second produces tx s=h^-1, and the last
two produce their indicated translations. Every other role is untouched.
These are exactly the predecessor's direct ten paid factors, written in
chronological order. There is no extra scalar operation, workspace, inverse
or unpaid restoration in this upper word. It attains the lower bound.

This closes PR #1745's eight/nine-call question negatively. Changing the
paid labels or allowing clean-only endpoints requires another argument.
For example, one unit h label would itself have charges q=3 and tau=1;
the separated unit-price proof would no longer apply. Native implementation,
physical costs, recursive interfaces and multiplication exponents are not
consequences of this formal minimum. The proof has not been checked by a
formal proof kernel or independently reviewed by a human.
