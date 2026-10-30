# Inherited Gaussian q-LDU and bounded-word convolution proofs

These are mathematical prerequisites reproduced from the preceding Beatty-run deliverable by Dugongue with substantial OpenAI Codex assistance. Their original section identifiers and source attributions are retained. They are not new results of this continuation. Classical q-binomial, Gaussian, Fourier and numerical-linear-algebra identities remain credited as classical. No experiments or formal checks are asserted here.

## A2. A uniform lower bound for the q-products

Fix 0 < q ≤ 1/2. Put Q = q², F_0 = 1 and F_k = product_(r=1)^k (1−Q^r).

**Lemma.** For every nonnegative integer k,

    2/3 ≤ F_k ≤ 1.

**Proof.** For numbers a_r in [0,1], induction gives product_(r=1)^k (1−a_r) ≥ 1−sum_(r=1)^k a_r: multiplying the inductive lower bound by 1−a_(k+1) adds the nonnegative cross term a_(k+1) sum_(r=1)^k a_r. Hence F_k ≥ 1−sum_(r≥1) Q^r = 1−Q/(1−Q). Since Q ≤ 1/4, this is at least 2/3. The upper bound follows because every factor lies in (0,1]. ∎

The estimate holds uniformly in k. Thus the diagonal maps with entries F_k or 1/F_k require no growing magnitude budget merely because a line gets longer.

## A3. The finite q-binomial identities needed below

For 0 ≤ k ≤ i define B(i,k) = F_i/(F_k F_(i−k)); set B(i,k) = 0 outside that range.

**Lemma.** These coefficients satisfy

    B(i,k) = B(i−1,k) + Q^(i−k) B(i−1,k−1),
    product_(j=0)^(m−1) (1+z Q^j)
      = sum_(r=0)^m Q^(r(r−1)/2) B(m,r) z^r.           (3)

**Proof.** For the first identity, reduce the two right-hand terms to the common denominator F_k F_(i−k). Their numerators are respectively F_(i−1)(1−Q^(i−k)) and Q^(i−k) F_(i−1)(1−Q^k). Their sum is F_(i−1)(1−Q^i) = F_i. Endpoint cases follow directly from B(i,0) = B(i,i) = 1. For (3), use induction on m. On multiplying the polynomial for m−1 by 1+z Q^(m−1), the coefficient of z^r becomes

    Q^(r(r−1)/2) [B(m−1,r) + Q^(m−r) B(m−1,r−1)],

which is Q^(r(r−1)/2) B(m,r) by the recurrence. The constant empty product proves the m = 0 base case. ∎

A second identity is

    sum_(k=0)^min(i,j)
       Q^((i−k)(j−k)) F_i F_j / [F_k F_(i−k) F_(j−k)] = 1.       (4)

**Proof.** Denote the sum by S(i,j), write each term as Q^((i−k)(j−k)) B(i,k) F_j/F_(j−k), and expand B(i,k) by the first recurrence. In the part with B(i−1,k), each summand is its S(i−1,j) summand multiplied by Q^(j−k). In the other part replace k by l+1. Its summand is the l-th S(i−1,j) summand multiplied by 1−Q^(j−l), because F_j/F_(j−l−1) = (F_j/F_(j−l))(1−Q^(j−l)). The factors add to 1. A boundary term with l = j vanishes through 1−Q^0; all other out-of-range binomial terms are zero. Consequently S(i,j) = S(i−1,j). Iterating reaches S(0,j) = 1. ∎

## A4. Exact finite Gaussian LDU

Let n ≥ 1 and define the n by n matrix

    A_ij = q^((i−j)^2),       0 ≤ i,j < n.

Let D = diag(F_0,...,F_(n−1)) and define a unit lower triangular matrix L by

    L_ik = q^((i−k)^2) F_i/[F_k F_(i−k)]   if k ≤ i,
    L_ik = 0                              if k > i.

**Theorem.** A = L D L^T.

**Proof.** The (i,j) entry on the right is the sum over k ≤ min(i,j) of

    q^((i−k)^2+(j−k)^2) F_i F_j/[F_k F_(i−k) F_(j−k)].

Subtracting (i−j)^2 from the exponent leaves 2(i−k)(j−k). Therefore that sum is q^((i−j)^2) times the left side of (4), which is 1. This proves every entry equality. Since each F_k is positive and L is unit triangular, this also proves positive definiteness and invertibility, independent of A1. ∎

The determinant is product_(k=0)^(n−1) F_k. Although that determinant can decrease with n, it does not imply an unbounded inverse norm; A6 gives a uniform norm bound.

## A5. Exact inverse as two convolutions

Let H be lower triangular Toeplitz with

    H_ik = (−q)^(i−k)/F_(i−k)    for i ≥ k,
    H_ik = 0                     for i < k.

**Theorem.**

    L^−1 = D H D^−1,
    A^−1 = D^−1 H^T D H D^−1.                         (5)

Thus A^−1 b is obtained by applying, in order, D^−1, H, D, H^T and D^−1.

**Proof.** Put T_ik = q^((i−k)^2)/F_(i−k) for i ≥ k and zero otherwise. The definition of L gives L = D T D^−1. Products of finite lower triangular Toeplitz matrices multiply their coefficient sequences by truncated convolution. The coefficient of degree m in T H is

    sum_(r=0)^m q^(r²) (−q)^(m−r)/[F_r F_(m−r)]
      = (−q)^m/F_m * sum_(r=0)^m (−1)^r Q^(r(r−1)/2) B(m,r).

By (3) with z = −1, the last sum is product_(j=0)^(m−1)(1−Q^j). It is 1 for m = 0 and zero for m ≥ 1, since then its j = 0 factor is zero. Hence T H = H T = I. It follows that L^−1 = D H D^−1. Inverting A = L D L^T gives

    A^−1 = L^−T D^−1 L^−1
          = D^−1 H^T D D^−1 D H D^−1
          = D^−1 H^T D H D^−1.

This is (5). H b is a truncated linear convolution with h_r = (−q)^r/F_r. H^T b is the reversal of such a convolution on the reversed input. Both are explicit finite sums; no inverse oracle occurs. ∎

## A6. Dimension-independent conditioning and intermediate magnitudes

All vector and matrix norms in this section are maximum-coordinate and maximum absolute-row-sum norms.

**Theorem.** For 0 < q ≤ 1/2 and all n,

    ||D|| ≤ 1,       ||D^−1|| ≤ 3/2,
    ||H|| ≤ 3,       ||H^T|| ≤ 3,
    ||A^−1|| ≤ 81/4.

For ||b|| ≤ B, the five intermediate vectors in (5) have norms at most respectively

    (3/2) B, (9/2) B, (9/2) B, (27/2) B, (81/4) B.

**Proof.** A2 gives the first two estimates. Every absolute row sum of H or H^T is bounded by sum_(r≥0) q^r/F_r ≤ (3/2)/(1−q) ≤ 3. Multiplying the five operator-norm estimates yields the displayed bound (3/2)·3·1·3·(3/2) = 81/4, and multiplying the prefix estimates gives each intermediate-vector bound. Every partial dot product is bounded by the corresponding sum of absolute values, so the same argument controls partial sums in a direct convolution implementation. ∎

This is the positive conditioning result missing from a naive global Vandermonde factorization. The inverse is recovered without factors of size exp(constant times n²). An implementation of the convolutions may have its own intermediate growth; for an FFT or polynomial multiplication implementation, that separate arithmetic analysis must be included. A6 does not declare a free stable FFT.

## A7. A fully specified perturbation theorem for the five-factor inverse

**Theorem.** Let F_1,...,F_5 denote the five exact factors in their order of application in (5), each of norm at most 3. Suppose approximate factors satisfy ||Fhat_j−F_j|| ≤ ε ≤ 1, and the five evaluated maps introduce additive vector errors of norm at most δ at their outputs. Then the final vector differs from A^−1 b by at most

    1280 ε ||b|| + 341 δ.

**Proof.** Each approximate factor has norm at most 4. The difference between the approximate and exact fivefold products is a telescoping sum of five terms. Every term has one factor difference with norm at most ε and at most four remaining factors, each bounded by 4; its norm is at most 4^4 ε. Thus the product perturbation is at most 5·4^4 ε ||b|| = 1280 ε ||b||. An additive error injected after one factor passes through at most four later approximate factors, so all five errors contribute at most δ sum_(j=0)^4 4^j = 341 δ. Add the bounds. ∎

In particular, choose ε ≤ 2^(−P)/(2560(B+1)) and δ ≤ 2^(−P)/682 to obtain absolute error at most 2^(−P) for every ||b|| ≤ B. If each retained convolution coefficient is formed with absolute error at most ε/n, its matrix row-sum error is at most ε; the required coefficient precision is P + log2(B+1) + log2 n + O(1). This is a sufficient precision schedule, not an experimental extrapolation.

## A8. The q-parameter itself has a dimension-independent error budget

**Lemma.** On 0 < q ≤ 1/2, uniformly in k,

    |F_k'(q)| ≤ 64/27,
    |(1/F_k)'(q)| ≤ 16/3.

Furthermore the sum of absolute derivatives of h_r(q) = (−q)^r/F_r(q), over any finite prefix, is less than 17.

**Proof.** Logarithmic differentiation gives

    |F_k'| = F_k sum_(r=1)^k [2r q^(2r−1)/(1−q^(2r))]
      ≤ [2/(1−q²)] sum_(r≥1) r q^(2r−1)
      = 2q/(1−q²)^3 ≤ 64/27.

Here F_k ≤ 1 was used. Dividing by F_k² ≥ (2/3)² gives the second bound. For h_r,

    |h_r'| ≤ r q^(r−1)/F_r + q^r |(1/F_r)'|.

Summing the first majorant gives at most (3/2)/(1−q)² ≤ 6; summing the second gives at most (16/3)/(1−q) ≤ 32/3. Their sum is 50/3 < 17. The r = 0 derivative is zero, so its harmless inclusion in the second majorant preserves the inequality. ∎

**Corollary.** If q and qhat lie in (0,1/2], the row-sum norm errors in D, D^−1 and H or H^T caused only by substituting qhat for q are at most respectively (64/27)|qhat−q|, (16/3)|qhat−q| and 17|qhat−q|. Apply the scalar mean-value theorem to every coefficient and the preceding derivative sums. Consequently an O(2^(−P)/(B+1)) enclosure of q suffices for the parameter component of A7's final error, with an absolute constant independent of n. ∎



### A11.9. Explicit convolution and native arithmetic model

For the native corollary, also impose an effective input condition: a is an explicitly specified positive rational, π times an explicitly specified positive rational (including the actual a = πα²), or a real with a charged polynomial-time certified approximation procedure to the working precision. The integers S,T are explicitly supplied, and b is supplied as fixed-point data or certified enclosures at the stated working precision, with a supplied magnitude bound whose logarithm is O(p). The exact real identities in A11.1–A11.6 do not require this computability restriction. For the native corollary, fix the following model. A word contains W bits, with W a sufficiently large constant times the requested precision plus the displayed magnitude and guard bounds. Unit-cost operations include bounded-word addition, subtraction, multiplication, comparison, memory access, integer division, and a shift that divides by a power of two with a specified rounding convention. The word width is large enough to contain raw products before fixed-point rescaling. Complex numbers use two such fixed-point values. Thus one real or complex fixed-point addition, product, or division by a pivot bounded away from zero costs O(1) of these native operations and has a chosen O(2^(−B)) local error. This is an explicit extended Word RAM; no instruction-level realization in the more restrictive tcslib ISA is claimed. The exact field-operation count (10) and the precision requirement (12) are mathematical statements independent of that implementation choice.

**Convolution lemma.** Two length-L complex arrays with coordinate bounds X,Y can be convolved, to absolute output error 2^(−P), using O(L log(L+2)) operations in this model and P + O(log(L+2) + log(X+1) + log(Y+1)) fractional bits, with sufficient integral bits for polynomial-in-L intermediate growth. Input-independent twiddle preparation is charged separately and has a polynomial precision-dependent cost.

**Proof.** Pad both arrays with zeros to a power-of-two length M satisfying 2L ≤ M < 4L. Choose ζ = exp(2πi/M). The geometric-series identity sum_(j=0)^(M−1) ζ^(kj) = 0 for nonmultiples k of M and M otherwise proves the DFT inverse formula. Splitting a DFT into its even and odd indices gives the radix-two butterfly recursion. There are log2 M levels, M/2 butterflies at each level and O(M log M) operations overall. Pointwise multiplication of the two DFTs followed by the normalized inverse gives their cyclic convolution; zero padding makes all its nonzero output coefficients equal the ordinary linear convolution.

Each exact butterfly has maximum-row-sum norm at most 2; each twiddle has modulus 1. At any stage exact intermediate magnitudes are at most M times the input bound. Suppose every twiddle has absolute error at most δ and each completed butterfly coordinate incurs additive arithmetic error at most 4δ. A perturbed butterfly has norm at most 2+δ. For δ ≤ 1, the forward error after r levels is at most

    δ r 3^(r−1) (X+4) ≤ δ M³ (X+4).

This follows by telescoping the stage products and summing the additive errors; r ≤ M and 3^r ≤ M². If δ ≤ M^(−3), each approximate forward transform is bounded by 2M(X+4), or 2M(Y+4). Subtracting the two pointwise products and using these forward-error bounds gives error at most

    10 δ M⁴ (X+4)(Y+4)

including one rounded pointwise product. More precisely, each forward bound is (M+1)(X+4) or (M+1)(Y+4). Since M is at least 2, their product and the pointwise rounding fit below 4M²(X+4)(Y+4). This is the input bound of the approximate inverse transform. Applying the same stage bound and then the exact 1/M normalization bounds the additional inverse-transform error by at most 5δ M⁴(X+4)(Y+4); the final fixed-point normalization adds at most δ. Therefore the complete convolution error is at most

    512 δ M⁴ (X+1)(Y+1).

Choosing δ at most both M^(−3) and 2^(−P)/[512 M⁴(X+1)(Y+1)] proves the stated fractional-bit bound. Every intermediate magnitude in the argument is polynomial in M times (X+1)(Y+1); its logarithm supplies the asserted integral bits.

The complex twiddles are not exact machine oracles. They are input-independent constants whose bounded arguments can be approximated by elementary Taylor series after range reduction, with polynomial cost in the desired precision. A sufficiently accurate π value may be supplied by the elementary arctangent identities and series already used in the inherited exponential/root preparation notes. Preparing all M twiddles to the chosen precision costs polynomial(M,P,log(X+1),log(Y+1)) work and is charged to preparation. In A11.8, M = O(1/θ) is polynomial in p; neither this preparation nor coefficient setup alters its subexponential-in-p setup classification. ∎

Apply this convolution lemma to the two Toeplitz maps in A5 and their reversals, at the extra precision required by the D_c similarity. It supplies the explicit C(L) = O(L log(L+2)) used in A11.7. The actual run solve is consequently a sufficient algorithm on the stated extended native machine, with all intermediate growth, rescaling, truncation and boundary costs paid. This is a mathematical construction, not an experimentally verified or Lean-verified program.


