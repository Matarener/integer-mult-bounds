# Copy cost for the 336-plane spectral decoder

This is a proof over any scalar field of characteristic zero, with an exact
finite certificate. The spectral calculation is over the reals; its rational
matrix ranks and nonzero integer minors persist in every such scalar field.
The binary address form is separate from the scalar field.
The result does not cover all fitting matrices or overcomplete factorizations.

## 1. Ports and native operation

Let V be the even-weight subspace of F2^7, with the standard dot product.
It has dimension six. Its form is alternating and nondegenerate: its
orthogonal complement in F2^7 is the span of the odd all-ones vector.

Let the ports be all nondegenerate planes E in V. Each plane has three
nonzero vectors a, b, c=a+b, with a.b=1. The count is 63*32/6=336.
Two ports are adjacent when their planes are orthogonal. Let A be this
adjacency matrix, with zero diagonal. Each row has 20 neighbors, the
nondegenerate planes in a nondegenerate four-space.

The native plane operation is a prior construction. In the retained binary
Gaussian convention, C_v=((1+i)I+(1-i)X_v)/2. Commuting translations give

    Q_E = C_a C_b C_c = (-I+X_a+X_b+X_c)/2,
    Q_E^2 = I.

Its unsigned upper-right block is

    P_E = aa^t + bb^t + cc^t = ab^t + ba^t.

This is the orthogonal projector onto E. It has rank two, and I+P_E has
rank five in the seven-dimensional ambient space. Q_E commutes with F_7.
Thus Q_E and F_7 Q_E have Gaussian ranks two and five. The finite checker
checks the exact phase coefficients, square and ranks at all 336 ports.
The native rank interpretation comes from the retained compiler and
`p104-translated-progress/PROOF.md`, Section 4. No new native operator or
uniform implementation theorem is claimed here.

## 2. Exact spectral certificate

The checker constructs A from the planes and checks the integer identity

    (A+8I)(A+4I)(A-2I)(A-8I)(A-20I) = 0.

Since A is real symmetric, it is diagonalizable. Its eigenvalues therefore
belong to the five displayed roots. The checker computes traces of A^k for
k=0,...,4 and solves their Vandermonde system over the rationals. This gives

| Eigenvalue | Multiplicity |
| --- | ---: |
| -8 | 27 |
| -4 | 105 |
| 2 | 168 |
| 8 | 35 |
| 20 | 1 |

For every real c, I+cA is a fitting matrix: its diagonal is one and all
forbidden off-diagonal entries are zero. Its minimum rank is 168, attained
only at c=-1/2. Set K=I-A/2. Its kernel is the eigenvalue-two space.

The orthogonal projector R onto this kernel has numerator

    N = (A+8I)(A+4I)(A-8I)(A-20I)
      = A^4 - 16A^3 - 144A^2 + 1024A + 5120I,
    R = N/6480.

The polynomial identity and the five distinct roots prove this projector
formula. In particular, Im(K)=ker(N). These conclusions hold over C as well
as R, by scalar extension of the real matrices.

## 3. Every nonzero image vector spans at least five address dimensions

For a four-dimensional binary subspace W of V, let S(W) be the set of ports
contained in W. The checker proves that N[S(W),S(W)] is nonsingular over Q
for every W. It does so by checking full rank modulo the prime 65537.
A nonzero determinant modulo a prime is a sufficient exact certificate that
the integer determinant is nonzero. The checker also verifies primality.

This is a complete census. Orthogonal complementation in V is a bijection
between its two-dimensional and four-dimensional subspaces. The 651
two-dimensional subspaces are generated as the distinct triples
{a,b,a+b}, for distinct nonzero a,b in V. Their complements give:

| Number of four-spaces | Ports in the four-space | Principal rank modulo 65537 |
| ---: | ---: | ---: |
| 315 | 16 | 16 |
| 336 | 20 | 20 |

Suppose a nonzero vector u in Im(K) has port support whose binary plane span
has dimension at most four. Extend that span to a four-space W. All entries
of u outside S(W) are zero. Since Nu=0, restriction to S(W) gives

    N[S(W),S(W)] u[S(W)] = 0.

Nonsingularity forces u=0, a contradiction. Thus every nonzero vector in
Im(K) has binary plane span of dimension at least five. This assertion is
about the span of the full planes, not the number of nonzero coordinates.

## 4. The copy floor for exactly 168 terms

Use the additive full-plane tariff of `plane-port-global-rank-dual`: a term
u v^t costs the binary rank of the dot pairing between the plane spans of
the supports of u and v. One term carries one independent scalar total.

Suppose K=UV is a factorization with exactly 168 columns of U and 168 rows
of V. Since rank(K)=168, both factors have rank 168. Consequently
col(U)=Im(K), and row(V)=row(K)=Im(K)^t. Every factor column and row is
nonzero and satisfies Section 3. Their two binary support spans have
dimensions at least five inside the same nondegenerate six-space.

For subspaces L,M of that space, the pairing rank is

    dim(L) - dim(L intersection M^perp)
      >= dim(L) + dim(M) - 6.

Each term therefore costs at least four, and the additive copy mass obeys

    C >= 168*4 = 672 = 2*336.

In a model that funds copies from two unpaid coordinates per port, these
factors cannot leave a positive rank surplus. Extra routing, restoration
and other charges cannot reduce this lower bound. This conclusion does not
assume that any global controller realizes that funding model.

## 5. Positive control and boundaries

The 336-term column factorization K=sum_i K[:,i] e_i^t has tariff two for
each term. Its source planes are E_i and its orthogonal neighbors, and its
reader span is E_i. Their pairing has rank exactly two. The checker verifies
all 336 tariffs, for total 672. This is a factorization and tariff control;
it does not implement a copy program or prove attainment with 168 terms.

For more than 168 terms, factor columns need not belong to Im(K).
Section 3 therefore does not apply to each term. No floor for those
factorizations is proved. Other c values, nonuniform fitting matrices,
changed ports, non-additive prices and joint array interfaces also remain
outside the cost theorem. The spectral rank statement alone does not price
those alternatives.

No complete supplier, productive target credit, caller, recursive moment,
BIT improvement, precision/tape bound or new kappa follows from this result.
