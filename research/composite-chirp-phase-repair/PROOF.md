# Rank-optimal folding and the exact phase-repair count

This is a scoped algebraic construction over the complex numbers. All inputs
are arbitrary vectors. No tape, dirty-scratch, rounded-arithmetic or selected
supplier contract is implicit in the matrix identities.

## Statement

Let n be any positive odd integer, let a,b be integers, and write

```
zeta = exp(2 pi i/n),   g = gcd(a,n),   m = n/g,
K_b[j,k] = zeta^(a(j-k)^2 + b(j-k)),   0 <= j,k < n.
```

Reducing a and b modulo n does not change the operator. The convention
gcd(0,n)=n includes a=0 and n=1.

1. K_b factors through exactly m coordinates. Its rank is m, and each of its
   m nonzero singular values is sqrt(n g). No linear factorization through
   fewer coordinates exists.
2. A sum of q scalar-weighted chirps with this fixed a, and arbitrary linear
   phase twists b, has rank at most m times the number of distinct b modulo g
   that occur, hence at most qm. An invertible sum requires at least g terms.
3. Exactly g terms suffice. The explicit sum S=sum_(b=0)^(g-1) K_b satisfies
   S* S = n g I, so S is invertible, has condition number one, and
   S^(-1)=S*/(n g). Here * denotes conjugate transpose. With one representative
   of each residue and nonzero scalar weights c_b, the singular values are
   sqrt(n g)|c_b|, each repeated m times.

The minimum repair count is for this specified family of complete chirp
operators. It is not a lower bound for circuits using different quadratic
coefficients, arbitrary additional native operations, or nonlinear encodings.

## Explicit factorization

Define the n-by-m phased replication E_b and the m-by-m reduced chirp C by

```
E_b[j,r] = zeta^(bj) if j = r mod m, and 0 otherwise,
C[s,r]   = zeta^(a(s-r)^2) = exp(2 pi i (a/g)(s-r)^2/m).
```

Then

```
K_b = E_b C E_b*.
```

Indeed, for fixed j,k only s=j mod m and r=k mod m contribute to this
matrix entry. Its exponent is bj+a(s-r)^2-bk. Since j-k=s-r+hm for some
integer h, the difference from a(j-k)^2+b(j-k) is a multiple of n. Both
2 a m h(s-r) and a m^2 h^2 are multiples of n because a m=(a/g)n.
This proves the identity entry by entry, without cancellation or numerical
approximation. Thus the program is a phased fold E_b*, the reduced chirp C,
and a phased replication E_b. It preserves every input contribution.

The columns of E_b have disjoint supports and squared norm g, hence
E_b*E_b=gI. Put a'=a/g. Since gcd(a',m)=1 and m is odd, 2a' is a unit
modulo m. Character orthogonality gives

```
(C C*)[s,t]
 = exp(2 pi i a'(s^2-t^2)/m)
   sum_(r=0)^(m-1) exp(-2 pi i 2a'(s-t)r/m)
 = m if s=t, and 0 otherwise.
```

Consequently C is nonsingular and both C C* and C*C equal mI. Because E_b
is injective and E_b* is surjective, rank(K_b)=m. Rank cannot increase
through an intermediate vector space, proving that this intermediate
dimension is optimal among all complex linear factorizations.

## Orthogonal phase classes and the sharp repair

For fixed r, the only possible overlap of columns of E_b and E_c is

```
(E_b* E_c)[r,r]
 = zeta^((c-b)r) sum_(h=0)^(g-1) exp(2 pi i (c-b)h/g).
```

It is zero unless b=c modulo g. If b=c modulo g, E_b and E_c have the
same range, because their corresponding columns differ by a nonzero
scalar. Thus there are exactly g mutually orthogonal m-dimensional ranges
V_0,...,V_(g-1), and their direct sum is the whole n-dimensional space.
The orthogonal projector onto V_b is P_b=E_b E_b*/g.

The factorization shows that the image of K_b is V_b and that K_b
annihilates its orthogonal complement. Direct multiplication gives

```
K_b* K_b = E_b C* (gI) C E_b* = n g P_b.
```

For different residues, K_b* K_c=0, because E_b*E_c=0. A sum using only
q distinct residues has image inside their direct sum and rank at most qm.
If it omits any residue it cannot be invertible. In particular, fewer
than g individual chirps cannot repair the rank defect, even if their
phases and scalar coefficients are chosen freely.

Conversely, choose b=0,...,g-1 and nonzero complex c_b. The cross terms in
the Gram matrix vanish, giving

```
(sum c_b K_b)* (sum c_b K_b) = n g sum |c_b|^2 P_b.
```

Every projector has rank m and the projectors sum to I. This proves the
weighted singular-value statement. Taking every c_b=1 proves the explicit
inverse, exact conditioning and attainment of the lower count g.

## Consequence and limits for composite axes

For n=9,a=3 the reduced dimension is three, and exactly three twists repair
invertibility. For n=45,a=15 the reduced dimension is also three, but fifteen
twists are necessary. Using several twists from the same residue class
cannot compensate for a missing class. If a is a unit modulo an odd composite
n, then g=1 and a single chirp is already nonsingular and perfectly conditioned.

These are algebraic options and obstructions for a possible composite-axis
consumer following David Ganz's PR5564. That package supplies coprime axes and
CRT streams, not this phase-only convolution or its physical implementation.
No claim is made that a particular published Gaussian resampler uses K_b.
A caller must identify its actual kernel and coefficient a before applying
this result. A real Gaussian kernel with nonconstant magnitudes is a different
operator. Physical delivery, phase manufacture, exact/rounded normalization,
movement, owned restoration, storage, recursive prices and complete recovery
remain unpriced. The selected assumptions and kappa are unchanged.

The proof uses classical finite-character orthogonality, the same elementary
ingredient behind quadratic Gauss sums. The construction and constrained
repair interface are the repository contribution; global novelty of Gauss-sum
rank or magnitude identities is unclaimed. NIST's
[Gauss-sum reference](https://dlmf.nist.gov/20.11.i) provides classical context.
No external Gauss-sum evaluation or phase formula is needed in this proof.

## Verification scope

Finite-field evaluations are exact ring images of the phase identities, not
complex numerical approximations. The verifier separately reduces literal
complex Gram polynomials modulo the integer cyclotomic polynomial Phi_n.
It also obtains finite-field ranks by dense row elimination and tests phase
subsets and the attaining inverse. These corroborate the written proof and
the bounded implementation. They do not replace the universal argument or
constitute independent human or formal proof-kernel review.
