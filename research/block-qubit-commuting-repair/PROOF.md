# Sharp repair for a common decomposition into small blocks

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and cited input

Let A_1,A_2,A_3 be Hermitian contractions on C^d. Suppose a common
orthogonal invariant decomposition is given, with m blocks of dimension two
and s blocks of dimension one, so d=2m+s>0. Put w=2m/d, and use

$$
\|M\|_{2,d}^2=\operatorname{Tr}(M^*M)/d,\qquad
\delta^2=\sum_{i<k}\|[A_i,A_k]\|_{2,d}^2.
$$

Let E be the minimum of
`(sum_i ||A_i-B_i||_(2,d)^2)^(1/2)` over all pairwise commuting Hermitian
contractions B_i. These competitors need not preserve the given blocks.
Let E_dec denote the same minimum restricted to competitors preserving them.
Then

$$
E\le E_{\rm dec}\le (w/3)^{1/4}\sqrt\delta.
$$

For each fixed m>=1 and s>=0, the constant `(w/3)^(1/4)` is sharp even for
unrestricted competitors and arbitrarily small positive delta. No exponent
greater than one-half works uniformly near zero for that class. For m=0
the original matrices already commute and E=E_dec=delta=0.

The only local repair input is Nick Petalas's
[qubit theorem, PR #5245](https://github.com/CrocSwap/integer-mult-bounds/pull/5245),
retained at `895e3db4982ad4bba6af3fbfbc6caf7b5f97ae1f`.
For a two-dimensional block, write A_i=a_i I+v_i dot sigma and let
lambda_1>=lambda_2>=lambda_3 be the eigenvalues of `sum_i v_i v_i^T`.
The cited theorem gives a contraction-preserving commuting repair with
squared error e=lambda_2+lambda_3 and squared commutator aggregate q>=3e^2.
It also proves this e is the local minimum. We use this theorem without
auditing it. David Ganz's atlas B099 supplies the ambient repair question
and its normalized-Hilbert-Schmidt convention.

## Weighted assembly and an exact gap identity

For block j, denote those local quantities by e_j and q_j. Keep each scalar
block unchanged. The direct sum of the cited local repairs consists of
commuting Hermitian contractions. The weights of the two-dimensional blocks
are alpha=2/d. Consequently

$$
E_{\rm dec}^2=\alpha\sum_{j=1}^m e_j,\qquad
\delta^2=\alpha\sum_{j=1}^m q_j,\qquad w=m\alpha.
$$

The formula for E_dec follows because the constrained objective separates
over the blocks, and every cited local minimum is attained. No assertion
that a general global minimizer preserves the blocks is needed.

The following identity tracks both sources of slack exactly:

$$
w\delta^2-3E_{\rm dec}^4
=\alpha^2\left[
m\sum_{j=1}^m(q_j-3e_j^2)
+3\sum_{j<k}(e_j-e_k)^2\right]\ge0.
$$

Indeed, expand the left side and use
`m sum_j e_j^2-(sum_j e_j)^2=sum_(j<k)(e_j-e_k)^2`.
Each summand is nonnegative by the cited local inequality. Taking fourth
roots proves the stated bound, including its scalar-padding factor w.
This is a dimension-uniform statement for the declared block class.

## Sharpness against competitors that mix blocks

Fix m>=1, s>=0 and 0<r<=1. On the two-dimensional blocks take identical
scaled Pauli triples `(rX,rY,rZ)` and put zero on every scalar block.
Equivalently, up to a coordinate permutation, these are

$$
A_i=r(\sigma_i\otimes I_m)\oplus0_s.
$$

All three matrices are Hermitian contractions. Literal Pauli multiplication
gives delta^2=12wr^4. The commuting repair `(0,0,A_3)` has squared error
2wr^2. We now show that every commuting Hermitian triple has at least that
error, even if its common eigenbasis mixes the supplied blocks.

Let xi be a unit vector, with active component `(x,y)` in `C^m direct-sum C^m`,
and let t=||x||^2+||y||^2. The scalar component accounts for the rest of its
norm, so 0<=t<=1. Its three Pauli expectations divided by r form the real
vector

$$
b=\left(2\operatorname{Re}\langle x,y\rangle,
2\operatorname{Im}\langle x,y\rangle,
\|x\|^2-\|y\|^2\right).
$$

Changing the inner-product convention changes the second sign only.
An exact expansion and Cauchy-Schwarz give

$$
|b|^2=t^2-4\left(\|x\|^2\|y\|^2-|\langle x,y\rangle|^2\right)
\le t^2\le t.
$$

For any orthonormal basis xi_1,...,xi_d, the active orthogonal projection
has rank 2m, hence `sum_k t_k=2m`. It follows that

$$
\sum_{i=1}^3\sum_{k=1}^d
|\langle\xi_k,A_i\xi_k\rangle|^2\le 2mr^2.
$$

Now take any commuting Hermitian competitors B_i and simultaneously
diagonalize them in such a basis. Write their real diagonal entries beta_ik
and the corresponding diagonal entries of A_i as a_ik. Orthogonal projection
onto this diagonal matrix space gives the exact identity

$$
\sum_i\|A_i-B_i\|_{2,d}^2
=\sum_i\|A_i\|_{2,d}^2
-\frac1d\sum_{i,k}a_{ik}^2
+\frac1d\sum_{i,k}(\beta_{ik}-a_{ik})^2.
$$

The first term is 3wr^2, the subtracted term is at most wr^2 and the last
term is nonnegative. Thus the error is at least 2wr^2. This lower bound
even allows competitors without a contraction constraint. The attaining
repair above is a contraction, so the required global minimum is exactly

$$
E^2=E_{\rm dec}^2=2wr^2,\qquad
\frac{E^4}{\delta^2}=\frac w3.
$$

This proves sharpness for every prescribed pair `(m,s)`. Sending r to zero
keeps the ratio fixed and proves that no smaller constant works near zero.
For an exponent gamma>1/2, `E/delta^gamma` is a positive fixed factor times
`r^(1-2gamma)`, which diverges. This proves the exponent assertion.

## What is and is not established

This is a written proof over complex matrices in every dimension satisfying
the common-block hypothesis. The new contributions are weighted assembly,
the gap identity and unrestricted sharpness with scalar padding. The local
qubit minimum and its proof remain credited predecessor results.

The proof gives an explicit optimal block-preserving repair from local
eigenvectors. It does not give a formula for the unrestricted optimum of
an arbitrary decomposable triple. It does not cover general irreducible
blocks of dimension three or higher, or an approximate rather than exact
common decomposition. It does not settle general atlas B099, supply a
physical multiplication construction or change kappa. Finite corroboration
is separate from the universal proof. Independent human and formal
proof-kernel review are unclaimed. Global literature priority is unclaimed.
