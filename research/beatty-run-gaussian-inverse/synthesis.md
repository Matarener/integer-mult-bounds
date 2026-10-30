# Geometric annihilators with dimension-independent normalization

Dugongue, with substantial OpenAI Codex assistance. Informal mathematics; no numerical experiments, Lean checking, or external searches accompany these arguments.

The purpose is a concrete bridge between the rounded Gaussian interpolation problem and ordinary polynomial operations. The results below supply normalized coefficient, reciprocal, and sampled-value bounds that do not grow exponentially with the number of roots. They do not identify the different normalizations with each other for free. In particular, they do not yet prove a complete fast native Gaussian inverse or a larger κ.

## Local precedents and the exact mathematical interface

The linked tree contains `Mathproof/GenVandermonde.lean`, `Mathproof/ExpSumRoots.lean`, and `Mathproof/TotalPositivity.lean`. They develop classical exponential-kernel nonvanishing and total positivity. The DAG has both historical checked entries and current source-only entries under differing namespace histories. Their existence is a discovery lead, not a fresh proof check. We restate and prove the needed elementary statements here.

`Mathproof/Meta/Problem18PolynomialToeplitzProduct20261002.lean` identifies a literal Toeplitz product with polynomial coefficients and proves full coefficient recovery. It supplies an exact algebraic precedent; its matrix identity is not a fast native algorithm. CatCrypt Contributors' `CatCryptCore/Crypto/Lattice/CyclicConvolutionGeneric.lean` and `NTTFullInversionGeneric.lean` supply cyclic-convolution and inverse-transform identities. The mathematical bounds below are independently written informal arguments, not claims that those libraries already contain them.

The inherited `research/native-kappa-30201655/modern-sources/BILATERAL-LDU.md` already uses partition bounds for normalized elementary symmetric sums and reciprocal bounds for complete homogeneous sums. R2 and R4 below rederive those inherited ideas explicitly; they are not claimed as new project discoveries. The additional contribution is their finite scaled-division/error interface, the two-sided normalized nodal weights, and the shared logarithmic convolution formula. The missing-node construction in `analysis.md` needs products over subsets of a geometric grid. Fix h > 0 and q = exp(−h), so 0 < q < 1. Define F_0(q) = 1 and F_k(q) = product over 1 ≤ j ≤ k of (1 − q^j). Empty products are 1. All coefficient indices in this note begin at zero.

## R1. A uniform finite product bound

**Theorem.** For every integer k ≥ 0,

    exp(−2/h) ≤ F_k(exp(−h)) ≤ 1.

**Proof.** For 0 ≤ z < 1, integrate the geometric series from 0 to z, or take increasing partial sums of that integral, to obtain −log(1−z) = sum over l ≥ 1 of z^l/l. All terms are nonnegative. Hence

    −log F_k(q)
      = sum_(j=1)^k sum_(l≥1) exp(−hjl)/l
      ≤ sum_(l≥1) 1/[l(exp(hl)−1)]
      ≤ (1/h) sum_(l≥1) 1/l²
      ≤ 2/h.

The penultimate inequality uses exp(u)−1 ≥ u. For the last inequality, separate l = 1 and compare each term 1/l², l ≥ 2, to the integral of x^(−2) over [l−1,l]; the resulting tail is at most 1. Finite partial sums justify every rearrangement by monotonicity; the displayed bound proves convergence. Exponentiation gives the lower bound, and every factor is at most 1. ∎

This deliberately elementary constant avoids importing a numerical evaluation of the Basel sum.

## R2. Elementary symmetric coefficients after extremal normalization

**Theorem.** Let g ≥ 1 and x_0 < ... < x_(g−1) be positive with x_(j+1)/x_j ≥ exp(h). For 0 ≤ k ≤ g let e_k be their kth elementary symmetric sum, and let W_k be the product of the k largest roots, with W_0 = 1. Then

    1 ≤ e_k/W_k ≤ 1/F_k(q) ≤ exp(2/h).

**Proof.** For k = 0 both sides are 1. For k > 0, a selected subset has indices j_1 < ... < j_k. Its extremal comparison indices are b_l = g−k+l−1, l = 1,...,k. Put δ_l = b_l−j_l. These are nonnegative and δ_1 ≥ ... ≥ δ_k because adjacent j indices differ by at least 1. Geometric separation gives

    product_l x_(j_l) / W_k ≤ q^(δ_1+...+δ_k).

The subset-to-δ map is injective. Sum over all partitions with at most k parts, allowing more partitions than occur in the finite root list. Writing ν_l = δ_l−δ_(l+1) with δ_(k+1) = 0 gives sum_l δ_l = sum_l lν_l. Therefore the sum of these bounds is

    product_(l=1)^k sum_(ν≥0) q^(lν) = 1/F_k(q).

The extremal subset itself contributes exactly 1. Apply R1. ∎

## R3. One uniform variable scaling makes the annihilator small

**Theorem.** Under R2 let X = x_(g−1), let r_j = x_j/X, and set

    E(z) = product_(j=0)^(g−1) (1−r_j z)
         = sum_(k=0)^g (−1)^k a_k z^k.

Then a_k ≥ 0 and

    a_k ≤ q^(k(k−1)/2)/F_k(q),
    sum_(k=0)^g a_k ≤ exp(1/(1−q)).

In particular, the coefficient magnitudes have bounds independent of g.

**Proof.** The kth largest normalized root is at most q^(k−1), so the product of the k largest normalized roots is at most q^(k(k−1)/2). Apply R2 to these roots. Also, the coefficient sum is E(−1) = product_j(1+r_j). The normalized roots in decreasing order are bounded by 1,q,q²,... . Using 1+u ≤ exp(u), the product is bounded by exp(sum_(j≥0)q^j) = exp(1/(1−q)). ∎

This is a single change of variable, not a coefficient-by-coefficient transformation. It preserves the ordinary polynomial convolution law.

## R4. The reciprocal has uniformly bounded coefficients

**Theorem.** In the ring of formal power series over the reals, write

    1/E(z) = sum_(k≥0) b_k z^k.

For every k ≥ 0,

    1 ≤ b_k ≤ 1/F_(g−1)(q) ≤ exp(2/h).

**Proof.** Expand each (1−r_j z)^(−1) by its formal geometric series. The coefficient b_k is the complete homogeneous symmetric sum over nonnegative multiplicities whose total is k. The largest root r_(g−1) equals 1, so choosing that root k times contributes 1. To bound the sum, specify the multiplicities of all other roots; the multiplicity of the largest root is then determined, if it is nonnegative. Drop that restriction to enlarge the sum. The other roots, in decreasing order, are at most q,q²,...,q^(g−1). Thus

    b_k ≤ product_(j=1)^(g−1) sum_(m≥0) q^(jm)
        = 1/F_(g−1)(q).

For g = 1 the product is empty and b_k = 1. R1 completes the proof. ∎

## R5. Stable truncated division in the stated coefficient convention

**Theorem.** Fix L ≥ 0 and input coefficient vectors y_0,...,y_L. The unique coefficients c_0,...,c_L satisfying

    E(z)c(z) = y(z) modulo z^(L+1)

are given constructively by

    c_k = sum_(j=0)^k b_j y_(k−j).

If max_k |y_k| ≤ Y, then max_k |c_k| ≤ (L+1)exp(2/h)Y. If the input changes by at most δ in each coefficient while E is exact, the output changes by at most (L+1)exp(2/h)δ. Conversely, multiplication by E has coefficient sup-norm at most exp(1/(1−q)).

**Proof.** E(0) = 1, so the formal reciprocal exists and determines the unique quotient modulo z^(L+1). Multiplication by the reciprocal gives the displayed finite convolution. Apply R4 and the triangle inequality to each coefficient. Apply the same argument to the difference of two input vectors. For forward multiplication use the coefficient sum in R3. ∎

This is a fully specified finite convolution, and a direct implementation uses at most a triangular number of scalar products. A faster convolution implementation may replace it when its actual arithmetic and precision costs are available. No faster multiplication algorithm is assumed in this theorem. With exact kernel coefficients, requesting output error at most 2^(−P) is sufficient if input error is at most 2^(−P)/[(L+1)exp(2/h)]. The resulting precision overhead is at most log2(L+1)+2/(h log 2), plus the chosen rounding margin.

For division by a monic polynomial R(w) = product_j(w−x_j), reverse the coefficient arrays. The reversed polynomial is product_j(1−x_j z) = E(Xz). Substituting z/X reduces the formal quotient identity to the one just proved. This algebraic reduction is exact. Its stability conclusion applies to inputs already expressed in that scaled convention; converting arbitrary unscaled data can have a large norm and must be accounted for separately.

## R6. Perturbing the fixed reciprocal kernel

**Theorem.** Suppose the stored kernel coefficients satisfy |b_j−bhat_j| ≤ ε for 0 ≤ j ≤ L, and the stored input satisfies |y_j−yhat_j| ≤ δ with |y_j| ≤ Y. Exact convolution of the stored arrays differs from c by at most

    (L+1)[εY + (exp(2/h)+ε)δ]

in coefficient sup-norm. If each of its at most k+1 summands is additionally rounded with absolute error at most η, add (L+1)η to this bound.

**Proof.** Subtract bhat_j yhat_(k−j) from b_j y_(k−j) by first changing the kernel at the exact input and then changing the input. Each term is bounded by εY + (|b_j|+ε)δ. Sum at most L+1 terms and use R4. The additional summand errors obey the triangle inequality. ∎

The theorem charges a particular exact convolution convention; it is not a stability theorem for an arbitrary FFT implementation.

## R7. Sampled annihilator values on the same integer grid

**Theorem.** Let M be any finite subset of the integers, m an integer outside M, and x_m = exp(hm). Set

    R_M(w) = product_(n in M)(w−exp(hn)),
    U_M(m) = product_(n in M) max(exp(hm), exp(hn)),
    ν_M(m) = number of n in M with n > m.

Then

    R_M(x_m) = (−1)^ν_M(m) U_M(m) B_M(m),
    B_M(m) = product_(n in M)(1−exp(−h|m−n|)),
    exp(−4/h) ≤ B_M(m) ≤ 1.

**Proof.** In each factor, divide by its larger exponential and record its sign. This gives the equality. Every distance |m−n| is a positive integer, and each positive integer distance can occur at most twice. Adding missing factors, all in (0,1), can only decrease the product, so B_M(m) is at least product_(r≥1)(1−q^r)^2. R1, first for finite products and then their decreasing limit, bounds that infinite product below by exp(−4/h). ∎

The exponent of U_M(m) can be recorded as the integer sum over n in M of max(m,n), multiplied symbolically by h. The equality does not require materializing an exponentially large real number. It also does not make a later multiplication by U_M(m) a bounded-word operation without a representation proof.

## R8. Normalized interpolation derivatives

**Corollary.** Let S be a finite subset of the integers and P_S(w) = product_(n in S)(w−exp(hn)). At each m in S,

    exp(−4/h) ≤ |P_S'(exp(hm))| /
        product_(n in S, n≠m) max(exp(hm),exp(hn)) ≤ 1.

Its sign is (−1) to the number of nodes of S above m.

**Proof.** Differentiate the product and evaluate at its simple root exp(hm). All terms except the derivative of that root factor vanish. Apply R7 to M = S without m. ∎

Thus the normalized diagonal weights needed for barycentric interpolation have inverses at most exp(4/h), uniformly in the number of nodes. This says nothing by itself about the norm of the full interpolation map between its chosen input and output coordinates.

## R9. A finite local formula with a dimension-independent tail

**Theorem.** For an integer R ≥ 0 let B_(M,R)(m) retain only factors with |m−n| ≤ R. Then

    0 ≤ B_(M,R)(m) − B_M(m) ≤ 2 q^(R+1)/(1−q),

and its relative error with respect to B_M(m) is at most

    2 exp(4/h) q^(R+1)/(1−q).

**Proof.** Write B_M = B_(M,R) times the omitted-factor product. For numbers a_i in [0,1], induction gives product_i(1−a_i) ≥ 1−sum_i a_i. The omitted defects sum to at most 2 sum_(r>R)q^r = 2q^(R+1)/(1−q). Since B_(M,R) ≤ 1, the absolute difference has this bound. Divide by the lower bound in R7. ∎

For any requested relative error 2^(−P), it is sufficient to choose R so that

    h(R+1) ≥ P log 2 + 4/h + log(2/(1−q)).

This is a finite sufficient approximation prescription, not extrapolation from experiments.

## R10. All normalized nodal weights are one ordinary convolution

**Theorem.** Suppose M is a subset of {0,...,t−1}, with indicator μ_n. Define a finite signed-distance kernel

    ell_0 = 0,
    ell_r = log(1−q^|r|) for 0 < |r| ≤ t−1.

For every m outside M in {0,...,t−1},

    log B_M(m) = sum_(n=0)^(t−1) μ_n ell_(m−n).

All these logarithms therefore occur among the coefficients of one ordinary polynomial product: multiply sum_n μ_n z^n by sum_(r=−t+1)^(t−1) ell_r z^(r+t−1), and read coefficient m+t−1. No cyclic wrap is used.

**Proof.** Taking the logarithm of the finite positive product in R7 gives the sum. Since m is outside M there is no zero-distance term from a selected root. For polynomial multiplication, a term μ_n ell_r lands at degree m+t−1 exactly when n+r = m. ∎

If two arrays of logarithmic weights have sup-norm difference at most ε, then exponentiating them changes each positive weight by a multiplicative factor in [exp(−ε),exp(ε)]. This follows directly from exp(a+δ)/exp(a) = exp(δ). Kernel generation, exponentiation, convolution arithmetic and input/output representation remain actual mathematical costs. The identity is a concrete shared-setup construction rather than a claim that these operations are free.

## R11. A complete positive precision interface for the annihilator subproblem

**Theorem.** Fix h > 0, L ≥ 0, and geometrically separated roots as in R2. Suppose normalized input coefficients are supplied with sup-norm bound Y. Truncated division by the normalized reversed annihilator admits the explicit convolution in R5, has exact output norm at most (L+1)exp(2/h)Y, and obeys R6 under kernel and input perturbations. Its associated same-grid normalized nodal weights and derivative weights lie in [exp(−4/h),1] and can be constructed by the finite products in R7–R8, by the approximation in R9, or simultaneously through R10.

**Proof.** R3 identifies the normalized reversed annihilator with E; R4 constructs its reciprocal. R5–R6 supply the finite division and error bound. R7–R10 give the diagonal factors and their constructions. These operations concern explicit finite polynomials and finite products, so no unknown transform or recovery oracle enters the assembly. ∎

The dependence of these displayed bounds is O(1 + 1/h + log(L+1)) bits beyond the input coefficient magnitude. This closes a specific coefficient-and-weight growth question. It does not prove that the actual Gaussian caller supplies its data in this convention at that precision. The coefficient scale from R3 and the nodal scale from R7 are different. Their conversion cannot be silently omitted from the global algorithm.

## R12. Why total positivity supplies the correct uniqueness statement

**Theorem.** Let a > 0 and let u_0 < ... < u_(n−1), v_0 < ... < v_(n−1) be real. The Gaussian matrix G_ij = exp(−a(u_i−v_j)^2) is invertible. More generally every increasing square minor of a rectangular such matrix is positive.

**Proof.** Factor each entry as exp(−a u_i²) exp(2a u_i v_j) exp(−a v_j²). Positive diagonal row and column scalings preserve signs of square minors. The middle matrix is the strictly totally positive exponential kernel at the increasing sequences 2a u_i and v_j. This is the exact classical result recorded in the linked GenVandermonde/TotalPositivity chain; alternatively its nonvanishing follows because a nonzero n-term real exponential sum has at most n−1 distinct real zeros, and the determinant sign follows by continuous deformation to integer exponents, where the ordinary Vandermonde determinant is positive. Thus every minor is positive and the square determinant is nonzero. ∎

Uniqueness consequently holds for the rounded-node finite interpolation construction in `analysis.md`. Quantitative inverse stability requires the separate estimates given there or additional estimates for the rounded geometry. Existence, numerical conditioning, and a lower complete operation count are distinct mathematical conclusions.

## The assembled mathematical direction

The four notes provide positive interfaces rather than a numerical frontier claim. The algebra note constructs a common-gauge convolution algebra and exact finite-bond carry tensors. The analysis note supplies a stable two-convolution inverse for finite uniform Gaussian matrices and an exact missing-node completion for rounded interpolation. This note controls the normalized annihilator coefficients, reciprocal, and sampled factors in that completion. The complexity note states exactly how actual complete service costs, preparation reuse, errors and recurrences compose.

A substantial κ gain still requires a dense-input contraction or a complete scaled rounded-interpolation application whose dominant cost satisfies the stated recurrence. Those algorithms are not assumed here. The new objects and their displayed proofs remain usable even if that final assembly is not found.


