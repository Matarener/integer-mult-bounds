# A sharp separator bound for an even-subset cube

## Claim and class

Let k >= 2 be even, and put N = 2^(k-1). Use the standard binary dot product
on F2^(2k+1). There is one coordinate 0 and k disjoint coordinate pairs
(a_i,b_i). For a selector e in F2^k, put

```text
q_e = e_0 + sum_i e_(a_i if e_i=0 else b_i).
delta_i = e_ai + e_bi;        b = q_0.
```

Each q_e has norm one. Split the selectors into their even and odd parity
halves. Each half has N elements. For all selectors e,f,

```text
q_e dot q_f = 1 + parity(e+f).
```

The inherited even-subset kernel restricts to this cube as

```text
K(e,f) = binomial((k - wt(e+f))/2, k/2).
A = I - K = [0, B; B^transpose, 0].
```

The binomial is a polynomial, also at half-integer arguments. Every entry of
B is nonzero. The results for one oriented cross block are:

```text
rank_Q(B) = N - binomial(k,k/2)/2.
minimum separating-frame rank-one factor count = N.
minimum sum of the two endpoint hull dimensions = 2*k*N.
```

Here is the exact factor class. Write B as a sum of scalar rank-one matrices.
For each nonzero factor, let E and F be its nonzero row and column supports.
It must have nondegenerate binary subspaces U and V that contain the label
spans of E and F, respectively, with U perpendicular to V. Its dimension
charge is dim U + dim V. Coefficients can be arbitrary real or complex
numbers, and factors can cancel. Extra orthogonal ambient coordinates are
allowed. Dimensions are charged separately for each factor. No carrier or
frame is shared between factors in this definition.

This class is a necessary binary-frame test for some separate gather/scatter
plans. It is not a definition or lower bound for every native implementation.
In particular, it does not check the stronger historical orthonormal-residual
conditions. Its upper bounds below give binary hulls, not physical programs.
No full recursive invoice, supplier, or new kappa follows.

## The inherited kernel and its exact rank

PR #2225 defines q_S = 1 + 1_S for k-subsets of an odd n-coordinate set,
and K(S,T) = binomial(|S intersection T|/2,k/2). Take one element of each
of k disjoint pairs, with n >= 2k+1. The complement labels have a fixed
part on the remaining n-2k coordinates. That part has odd norm and is
orthogonal to every pair coordinate. It can serve as e_0. Exchange the names
in each pair to obtain exactly the labels above. Thus this is a restriction
of that prior kernel, not a new kernel or a new port family.

Put d=k/2 and g(z)=binomial((k-wt(z))/2,d). Its value at zero is one.
It is zero at every other even-weight z. At each odd weight its d factors
are nonzero half-integers, so its value is nonzero. These facts prove the
stated block form and the full support of B.

For s in F2^k, the character chi_s(z)=(-1)^(s dot z) is an eigenvector of
K, with eigenvalue lambda_s=sum_z g(z) chi_s(z). As a polynomial in the
Boolean coordinates of z, g has degree at most d. Replacing each coordinate
by (1-chi_i)/2 shows that lambda_s=0 when wt(s)>d. Also,

```text
lambda_s + lambda_(s+1^k)
  = sum_z g(z) chi_s(z) (1 + (-1)^wt(z)) = 2.
```

The value of lambda_s depends only on wt(s), by permutation symmetry. When
wt(s)=d, s and its complement have the same weight, so lambda_s=1. When
wt(s)<d, its complement has weight greater than d, so lambda_s=2. Therefore
A has eigenvalues -1, 0, 1, of multiplicities

```text
(2^k-binomial(k,d))/2,  binomial(k,d),  (2^k-binomial(k,d))/2.
```

The rank of the displayed off-diagonal block matrix is twice the rank of B.
This proves the rank formula. It holds over Q, R and C. A scalar spectral
factorization does not supply binary frames or a native side computation.

## Label spans and separation

Let E be a nonempty subset of one parity half, and choose a in E. Let L_E
be the span of {e+a:e in E} in selector space, and let d_E=dim L_E. Every
vector in L_E has even parity. The map delta sends a selector to the sum
of its delta_i. It is injective. The label span has the direct sum

```text
S_E = <q_a> + delta(L_E).
```

All delta vectors pair to zero. Also q_a dot delta(l)=parity(l)=0 for
l in L_E, and q_a has norm one. Hence S_E has dimension d_E+1, restricted
form rank one, and radical delta(L_E). Since E is contained in the affine
space a+L_E, its cardinality is at most 2^d_E.

For a support F in the other parity half, the same statements hold. Further,

```text
S_E intersection S_F = delta(L_E intersection L_F).
```

To see this, a shared vector with coordinate 0 equal to zero lies in the
stated intersection. A shared vector with coordinate 0 equal to one would
give a+b in L_E+L_F for a in E and b in F. The left side has odd parity
and the right side has even parity. Thus that case cannot occur.

If U and V are nondegenerate with U perpendicular to V, then U intersection
V is zero. A common vector would be in U intersection U^perp. This is the
prior common-span obstruction. Applied here it gives

```text
L_E intersection L_F = 0;
d_E + d_F <= k-1;
|E|*|F| <= 2^(d_E+d_F) <= N.                     (1)
```

The obstruction is unchanged if the ambient space is enlarged orthogonally.

In this cube, zero intersection is also sufficient for two simultaneous
minimum hulls. Here is an existence proof that is useful for the finite
check. Let q and t be one label from each support, and let r_i and s_j be
bases of their radicals. These vectors together are independent, q and t
are orthogonal norm-one vectors, and all radicals are orthogonal to them.
Choose vectors p_i with

```text
p_i dot q = p_i dot t = 0;
p_i dot s_j = 0;      p_i dot r_l = [i=l].
```

Such vectors exist because the listed constraint vectors are independent
and the ambient form is nondegenerate. Set U=span(q,r_i,p_i). Its Gram
matrix is nondegenerate: a vector in its radical must first have zero p_i
coefficients, then zero q coefficient, then zero r_i coefficients. Also U
is orthogonal to t and every s_j. Thus U is disjoint from span(t,s_j).
Choose p'_j with zero pairing against t and all of U, and with
p'_j dot s_l=[j=l]. The constraint vectors are again independent, so these
vectors exist. Then V=span(t,s_j,p'_j) is nondegenerate and orthogonal to U.
The dimensions are 2*d_E+1 and 2*d_F+1.

This construction only solves binary linear equations. It asserts neither
orthonormal residuals nor Gaussian phases or a literal transfer word.

## The exact factor count

Each factor can have at most N nonzero entries by (1). All N^2 entries of B
are nonzero. Their union must be covered by factor supports even when
coefficients cancel. Therefore at least N factors are required.

For the upper bound, use one row-star term for each even selector. Its
source support is one label and its target support is all odd selectors;
its coefficients are exactly that row of B. These N terms sum to B.

It remains to show that each row star has legal binary hulls. Coordinate
swaps within pairs reduce its source to b=q_0. Put b'=b+delta_k. The
following vectors form an orthonormal basis of a target hull V:

```text
b';       e_bi, e_ai+delta_k       for 1 <= i < k.
```

They all have norm one and are pairwise orthogonal. Each is orthogonal
to b. The target span is generated by b' and delta_i+delta_k for i<k;
the latter is the sum of the two displayed basis vectors for i. Thus
U=<b> and this V are separating hulls of dimensions 1 and 2k-1.
This proves the exact factor count and gives explicit attaining hulls.

## The exact endpoint dimension charge

For any subspace S in a nondegenerate space U, the map from rad(S) to
(U/S)^* given by the pairing is injective. Otherwise a nonzero vector
would be orthogonal to all of U. Hence

```text
dim U >= dim S + dim rad(S).
```

For the two supports this gives dim U+dim V >= 2(d_E+d_F)+2. Put
m=d_E+d_F. By (1), m<=k-1. Since (m+1)/2^m is nonincreasing for integer
m>=0 (including equality from 0 to 1), every factor satisfies

```text
(dim U+dim V)/(|E|*|F|)
    >= 2(m+1)/2^m >= 2k/N.
```

The sum of support sizes is at least N^2. Summing proves a total dimension
charge of at least 2kN. Each row-star term above has charge 2k, so it
attains equality. This charge counts both endpoint hull dimensions once
per factor. It is not a complete paid recursive cost or a COPY lower bound.

For the full halves, each label span has dimension k, form rank one and
the same radical of dimension k-1, generated by delta_i+delta_k. Thus the
two full halves cannot be separated. Each half alone needs a hull of
minimum dimension 2k-1. Their union has dimension k+1 and radical k-1,
so it needs a hull of dimension at least 2k. The basis

```text
b, b';       e_bi, e_ai+delta_k       for 1 <= i < k
```

is orthonormal and attains dimension 2k. A legal nondegenerate enlargement
therefore repairs each individual degenerate span, but not separation of
two spans with a shared radical.

## Corollary: exactly which targets a star can read

This corollary also follows from the prior package's exact star spans; it
is included to delimit the attempted subset-lattice side computation.
Let k<n be even, and use affine labels (1,1_S) for all k-subsets of [n].
Fix a set J of size a<k and consider all source sets S containing J.
A target k-subset T is orthogonal to every source exactly when

```text
n is odd and [n] minus J is contained in T.
```

There are binomial(a,n-k) such targets, with value zero if n-k>a.
Indeed, differences of the sources span all even vectors outside J,
so T must be constant outside J. Constant zero would give T contained
in J, which is impossible since a<k. Constant one leaves k-n+a elements
of T inside J. The pairing with every source is then 1+2k-n, which is
zero modulo two exactly when n is odd. This proves the count.

## Boundary and consequence

The theorems require even k>=2, distinct coordinate pairs, norm-one labels,
nonempty opposite-parity supports, and a separate pair of nondegenerate
orthogonal hulls for every scalar rank-one factor. The proof includes k=2:
B has scalar rank one, but requires two factors of total hull charge eight.
Odd k gives norm-zero labels and is outside the claim. Allowing degenerate
hulls removes the factor-count obstruction: both full halves are already
orthogonal. Shared chronological carriers, changed label sets, block or
operator-valued factors, and different encoded inputs are outside the class.

The scalar rank can therefore underestimate both the number of separate
binary-frame factors and their endpoint dimension charge. The result closes
that specific shortcut for the inherited cube. It neither rejects the full
even-subset family nor proves a complete native side program or kappa gain.
