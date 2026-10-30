# Exact phase-sensitive contractions

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

This proof binds classical affine support and quadratic Gauss sums to the
retained Gaussian-dyadic circuit grammar. It does not claim a new simulation
method. Source circuits use P, X, D, C and scalar phase gates as defined in
PR5704. The frozen engine proof establishes their exact state signatures.

## 1. Exact support intersection

A valid state has amplitude s i^q(z) at x=a+Bz, with independent binary
columns B. All other amplitudes are zero. The scalar s is a Gaussian integer
divided by a power of two. The polynomial q has coefficients modulo four,
degree at most two, and even coefficients on distinct-variable products.

For two states, solve Bz+B'w=a+a' over F2. The row elimination in `solution`
uses the highest set bit as pivot. Each pivot depends only on lower bits.
Thus increasing pivot order gives every variable as an affine form in the
free variables. Every free assignment gives one solution, and every solution
has one free assignment. A zero row with right side one proves disjointness.

Substitution gives a polynomial q'(w(t))-q(z(t)) of the same type. The
coefficient of a Boolean parity can produce even quadratic terms but no
higher terms modulo four. Twice the product of two parities has degree at
most two modulo four. The frozen `substitute` implements these identities.
There is no support multiplicity factor: independence of both support bases
makes each common address correspond to exactly one pair (z,w).

Therefore the inner product is conjugate(s) s' times the quadratic Gauss sum
on the solution variables. This includes disjoint supports and exact zero
from destructive phase cancellation.

## 2. Gauss elimination

Write the last-variable dependence as

    q(x,z) = q0(x) + a z + 2 z l(x)  (mod 4),

where l is a binary linear form. The sum over z has three cases.

* If a is odd, it is (1+i^a) i^(-a l(x)). Add -a times the Boolean form l
  to q0 and multiply the scalar by 1+i^a.
* If a is even and l is nonzero, it is twice the indicator of l(x)=a/2.
  Solve this affine equation, substitute its full solution, and multiply by two.
* If a is even and l is zero, it is two for a=0 and zero for a=2.

Each step removes at least one variable. The remaining constant gives the
last power of i. All operations use integers and exact binary arithmetic.
The implemented dictionary substitutions are polynomial in the number of
variables; no cubic-time or optimal-complexity claim is made. They retain
quadratic storage. A Gaussian numerator needs only linear bits in the number
of summed variables, in addition to the input coefficient size.

## 3. Choi state and exact trace

Let d=2^n. On two n-axis registers, apply C with translation mask e_j+e_(n+j)
for each j, then apply the diagonal phase i^(sum x_j) on the first register.
This prepares

    beta_n sum_x |x,x>,  beta_n=(1+i)^n / 2^n.

In particular |beta_n|^2=1/d. Extend each original gate to the first register
and keep the second register unchanged. P and D receive explicit identity
or zero blocks; the other masks already act on the first register. Each
original gate is validated before extension. The resulting state chi_U is
beta_n sum_x U|x> tensor |x>. The common Bell phase cancels in

    <chi_U,chi_V> = tr(U^* V)/d.

This proves `kernel` and `trace`, including their absolute phase and
conjugation order. The Choi support can have 2^(2n) entries, but its signature
has at most 2n support columns and a quadratic phase description.

## 4. Tensor residual and optimal finite approximation

For fixed circuits U_j and fixed exact coefficients c_j, set K_ij to the
normalized cross trace. The normalized squared Hilbert-Schmidt norm at
positive integral width f is exactly

    sum_ij conjugate(c_i) c_j K_ij^f.

The exponent applies to the operator trace, not to its external coefficient.
This is a real nonnegative rational number for the admitted inputs. Zero is
equivalent to equality of the complete matrices at that width. The computation
cost is polynomial in the number of expanded terms, circuit size, axes and
output bit size. It is not polynomial in a circuit description whose expansion
has exponentially many terms. Exponentiation uses repeated squaring, but
rational numerators can require a number of bits proportional to f.

For approximation of a target T from supplied sources, the Gram normal
equations are Gc=b, where G_ij=K_ij^f and b_i=K_iT^f. A Gram matrix can be
singular. The equations remain consistent: every source dependence is also
orthogonal to T. Exact row reduction sets free coefficients to zero and
returns one solution. The verifier then checks each normal equation again.
The residual is orthogonal to the entire source span. For every competing
coefficient vector, the squared error is this residual plus the squared norm
of a vector in that span. Thus the returned value is the attained global
minimum for this finite source set. Dependent sources do not invalidate it.
The coefficients may depend on f. This is not a physical readout or paid query.

As a discriminating example, C=((1+i)I+(1-i)X)/2 lies in span(I,X) at f=1.
For its f-th tensor power and the two sources I^f and X^f, the sharp normalized
squared distance is 1-2^(1-f). Tests include a duplicate I source. This checks
singular Gram handling, exact coefficients and the tensor/coefficient boundary.

## 5. Credited all-width implication

PR5526 proves that a fixed Gaussian-dyadic Clifford residual vanishes at every
positive width exactly when it vanishes at widths 4n+4 through 4n+7 for n>=1.
For n=0 the four widths are 1 through 4. Its exact proof bytes are retained.
Applying Section 4 at those widths gives `decide`. This package does not
independently reprove the uniform Clifford theorem or improve its cutoff.

For a fixed U, the residual sum_(j=0..3) i^(-rj) (i^j U)^f is zero outside
f=r modulo four and equals 4 U^f in that residue. Its squared norm is 16 in
that residue. This prevents a three-residue check from being presented as a
complete all-width decision. Width-dependent words or coefficients are outside
this implication. Arbitrary unnormalized stabilizer maps are also outside it.

## 6. Separate verification paths and limits

The replay checks every three-equation affine system through three variables,
every admitted phase polynomial through four variables, and larger sampled
polynomials by direct summation. Literal vector arithmetic independently checks
state overlaps and matrix traces. The complete one-axis group supplies all
9,216 cross traces, with all four exact scalar phases retained.

For each of the 4,268 source recipe maps, a separate signed-Pauli calculation
checks the trace magnitude. Conjugation is a signed permutation on the Pauli
basis, so |tr U|^2 equals the sum of its fixed-Pauli signs. On the fixed binary
subspace these signs form a character: the sum is zero if one basis sign is
negative and is 2^dimension otherwise. This does not determine the absolute
trace phase. Seven native examples, one per occurring recipe rank, therefore
also use all 512 literal input columns for that phase check.

The large full-support examples have 16, 32 and 64 axes and known product
traces. They test compact execution, not a dense enumeration. Source hashes,
malformed controls and full result equality remain active under Python -O.
The replay is author evidence. No human review, proof-kernel check, physical
caller, cost invoice, stock, precision or complete multiplication theorem is
supplied by this implementation.
