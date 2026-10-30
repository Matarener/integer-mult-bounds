# A common-F monomial normalization criterion

This is an all-dimension symplectic lemma for the changed OPEN source
boundary. It does not construct a complete recursive caller. The scalar field
for the actual circuit is the Gaussian dyadic ring. The symplectic calculation
below is over F2; an exact Clifford implementation must additionally check its
Pauli signs and global phase.

Let Z be the computational Lagrangian and let F be the positive full native
transform, whose binary symplectic matrix in coordinates (x,z) is

    F = [ I  I ] .
        [ 0  I ]

Multiplying F by a Pauli, as in the actual invariant gauge Ftilde=X_33 F7,
does not change this symplectic matrix. Z and F^-1 Z are transverse. Write
L(G)=G^-1 Z for a Clifford G, and let r(G) be its Bruhat rank. Then

    dim(L(G) intersect Z)       = n-r(G),
    dim(L(G) intersect F^-1 Z) = n-r(G F^-1).

Suppose S and T obey, for one integer d,

    r(S)=r(T)=n-d,
    r(S F^-1)=r(T F^-1)=d.

Their intersections with the two transverse Lagrangians have dimensions d
and n-d, so each L(S), L(T) is exactly the direct sum of these intersections.
Isotropy says that the second summand is the annihilator of the first under
the perfect pairing between Z and F^-1 Z.

Choose an invertible binary B mapping U_T=L(T) intersect Z onto
U_S=L(S) intersect Z. Set A=B^-T. The symplectic matrix

    P = [ A          0    ]
        [ A+A^-T    A^-T ]

preserves both Z and F^-1 Z. On Z its action is B, and on F^-1 Z its action
is the pairing-dual A. It therefore maps L(T) onto L(S). Consequently

    post = T P^-1 S^-1

preserves Z, and hence is monomial. P is monomial, and F P F^-1 is monomial
as well. Thus

    post S P = T

admits a source input monomial that is also free at a genuine common-F cut.
The conclusion concerns the native child-query count. The monomial address
and phase scans must still be charged in the literal implementation.

An explicit monomial realization has address matrix A followed by a
quadratic phase with binary symmetric matrix

    Q = I + B B^T.

Indeed diag(Q) perm(A) has lower-left block Q A=A+A^-T. The pinned compiler
uses the execution order `perm(A).then(diag(Q))`. Its linear phase and global
phase can be fixed by the exact Clifford representation; the normalization
identity must be checked using both the tableau and a phase-sensitive state.

For the actual four OPEN C ports in the h7 D4 chart, the relevant values are
n=7, d=2, r(S_C)=r(T)=5, and r(S_C Ftilde^-1)=r(T Ftilde^-1)=2. This criterion
therefore proves that the positive output ranks of the earlier finite
normalizer search are properties of those selected gauges, not an obstruction
to a common-F-free forward normalization. The parent owns the fresh explicit
normalizer producer and its exact phase verification.

For an arbitrary chunk parameter k, a verified base identity lifts by
tensoring every native and monomial operator over the k bit positions. In
particular `(post S P)^(tensor k)=T^(tensor k)`. Monomial operators remain
address permutations with Gaussian unit phases; no expansion of a native
operator into 4^k scalar translations is used. This lift alone does not prove
that a particular recursive chronological cut admits that common F, does not
give an inverse-B caller, and does not provide owner, precision, rounding or
physical-tape bounds.
