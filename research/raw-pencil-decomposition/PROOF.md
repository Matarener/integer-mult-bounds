# Raw finite-field pencil decomposition

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

## Claim and interface

Let K be a supplied finite field. For any two m by n matrices A and B over K,
the algorithm returns the full Kronecker block list and invertible matrices
R and Q such that A Q = R A0 and B Q = R B0. Thus the strict action is
(R^-1, Q); the slice map is the identity. Zero rows, zero columns, zero-index
blocks, dependent slices and the zero pencil are allowed. There is no need
for an invertible slice over K.

The output uses these models for s A0 + t B0:

- Right index e: e by e+1, A0 has a unit diagonal and B0 a unit superdiagonal.
- Left index e: the transpose of that right block.
- Finite primary (f,e): (companion(f^e), I), with monic irreducible f.
- Infinity of length e: (I, companion(x^e)).

The code gives a deterministic algorithm polynomial in m+n for each fixed K.
It uses field tables and exact row reduction. A coarse bound is
O_K((m+n+1)^10) field operations and O_K((m+n+1)^4) live field entries.
No bound polynomial in log(|K|), fast canonical-form bound, or numerical
stability claim is made. The executable shares the usual finite memory and
Python recursion limits. The written algorithm has no dimension bound.

This completes the raw-input boundary for the supplied-model character
interface. It does not compute the character formulas of that interface.
It does not prove a physical supplier, native map, route, restoration schedule,
precision bound, repeated preparation cost or complete kappa improvement.
The selected .00310045 result and its main-transform bottleneck are unchanged.

## 1. Shortest chains and singular blocks

A polynomial right kernel vector of degree e has coefficients v0,...,ve with
A v0=0, A vi+B v(i-1)=0 and B ve=0. Solve this homogeneous linear system in
increasing e. If a right block exists, the first nonzero solution occurs at
its least minimal index. Search through min(m,n-1); a right block of index e
uses e rows and e+1 columns, so this range is complete.

Use the classical Kronecker decomposition to justify the splitting step.
A shortest chain has zero component on every regular or left block, and on
every right block with larger index. There is no smaller right block. On each
right block with the least index, it is a scalar multiple of its generator:
a nonconstant multiplier would increase the degree. At least one scalar is
nonzero. A change among equal-index copies makes this chain one direct
summand. This also proves that its e+1 domain vectors and e image vectors
are independent. No search through all vectors of K^n is required.

Set ui=(-1)^i v(e-i), and wi=A ui for 0<=i<e. The chain equations give
A ui=wi and B u(i+1)=wi, with the two endpoint zeros. These are precisely the
stated right block. Let U and W contain these columns. Recover its complement
by the linear equations

```text
F U = I, G W = I, G A = Ablock F, G B = Bblock F.
```

A solution exists because the embedding splits. The bases [U,ker F] and
[W,ker G] put both coefficient matrices in block diagonal form. The code
checks this identity before it recurses. For index zero, W has zero columns
and G has zero rows; the same equations split an isolated zero column.

After all right blocks are removed, apply the same step to the transpose.
If At Qt=Rt Ct, then A Rt^-t=Qt^-t Ct^t. This gives the correct row and
column maps for each left block, including an isolated zero row. The residue
has no left or right polynomial kernel, hence is square and regular by
Kronecker theory. This reasoning credits that theorem; it is not a new proof
of its existence or uniqueness.

## 2. Infinity without a rational invertible slice

For the regular residue, start V0=0 and form V(i+1)={v:Bv is in A Vi}.
Each step is a nullspace of [B,-A Vi] followed by projection onto the v
coordinates. The increasing sequence stabilizes in at most n steps.

On a finite block (C,I), every Vi is zero. On an infinity block (I,N),
Vi=ker(N^i). Thus its limit is exactly the whole infinity space. A is
injective there and its image W has the same dimension. B V is in W.
Use W=A V to obtain the local pair (I,N), then solve the same linear
projection equations to split this direct summand. The residual B is
invertible. Normalize it to (B^-1 A,I). This proves the step even when each
of the q+1 rational directions gives a singular matrix. No scalar search
is used to select a global chart.

## 3. Finite-field factorization and primary cyclic summands

Find the minimal polynomial of T=B^-1 A from the first linear relation among
I,T,...,T^n. Factor it with the classical Berlekamp method. For a squarefree
polynomial f, the kernel of the q-power map minus the identity on K[x]/f
has one dimension per irreducible factor. Its elements have values in K
on each field factor. Successive gcds with b-c, for a basis b and all c in K,
separate all factors. The code checks the final number of factors against
that kernel dimension.

For non-squarefree f, recurse on gcd(f,f') and its quotient. If f'=0,
extract the p-th root of each coefficient with the inverse Frobenius power
q/p and multiply the returned multiplicities by p. Each call reduces the
degree. This includes extension fields and inseparable multiplicities.
The verification uses a separate bounded monic-divisor enumeration, in
addition to multiplying all factors back to the input polynomial.

For each irreducible f with maximal exponent e, take ker(f(T)^e). These
primary spaces have direct sum equal to the full space. On one primary space,
find its nilpotency length e and a basis vector v with f(T)^(e-1)v nonzero.
Its annihilator is exactly f^e. Its Krylov columns through degree deg(f)*e-1
are independent and give the stated companion block. A cyclic submodule of
maximal length in a direct sum of K[x]/f^j is a direct summand: a maximal
component of v is a unit modulo f, so elementary module changes make it a
generator in that component. Solve L U=I and L T=C L for its projection.
Its kernel is a T-invariant complement. Repeat. Apply the same procedure
with f=x to the infinity operator.

All these steps are exact linear algebra or polynomial arithmetic with
degrees bounded by m+n. The largest dense splitting system has O(N^2)
unknowns and equations, with N=m+n+1. The stated coarse polynomial bound
covers all degree searches, all splits, all primary steps and fixed-q
Berlekamp splitting. It does not assert that this dense implementation is
competitive with fast canonical-form algorithms.

## 4. Certificate and independent acceptance boundary

Both original equations A Q=R A0 and B Q=R B0 must hold and both maps must be
invertible. Classification also requires irreducible primary labels and the
complete block multiset; map equality alone would not justify a malformed
primary label. The algorithm obtains those labels by the factorization above.
The public `check` function checks maps to the requested model; it is not a
standalone proof that arbitrary caller-supplied labels are canonical.

The separate orbit oracle enumerates elementary invertible row and column
operations on every raw pencil in five complete domains. Elementary additions
and nonzero row/column scalings generate GL; swaps are products of these.
It checks that the block type is constant on each orbit and differs between
orbits. It does not use polynomial null chains, module decompositions or
factorization to build its orbits. Every raw input also has both coefficient
identities checked. Finite enumeration corroborates the algorithm; the
all-dimension claim uses the arguments above and the classical module theorem.

## Attribution and prior work

[Nick Petalas PR #5250](https://github.com/CrocSwap/integer-mult-bounds/pull/5250)
supplied the invertible-slice character formula and canonical-form reduction.
[apoursh PR #5672](https://github.com/CrocSwap/integer-mult-bounds/pull/5672)
supplied repeated singular blocks and explicit slice lifts.
[PR #5683](https://github.com/CrocSwap/integer-mult-bounds/pull/5683) and
[PR #5689](https://github.com/CrocSwap/integer-mult-bounds/pull/5689) supplied the
mixed singular and complete finite-field model character interfaces. They
explicitly leave raw decomposition separate. David Ganz's A030/A026/A029
atlas lineage supplies the broader tensor-orbit motivation.

The exact field and row-reduction module is retained from
[PR #5664 source](https://github.com/aliromman/integer-mult-bounds/blob/8f7773e700d468396cbf893dfb18bf3ae6c20f66/research/residue-product-tensor-recognition/vendor/local.py).
Its notice is unchanged. SOURCES.json pins its retained bytes. The remainder
of this package is new integration, proof of this implementation and checks.

Kronecker decomposition, primary module decomposition and Berlekamp
factorization are classical. See [P. Van Dooren, 1979](https://perso.uclouvain.be/paul.vandooren/publications/VDooren79.pdf)
for prior arbitrary-pencil extraction, and
[Berlekamp's polynomial-factorization account](https://math.berkeley.edu/~berlek/poly.html).
The preimage sequence is a Wong sequence; see
[The Quasi-Kronecker Form for Matrix Pencils](https://epubs.siam.org/doi/abs/10.1137/110826278).
We use their mathematical lineage, not their numerical implementations or
complexity bounds. No global literature priority, human independent review,
formal-kernel acceptance or new canonical-form theorem is claimed.
