# Stable Gaussian inversion and completion on geometric grids

An informal mathematical contribution for the native Word RAM route. No theorem in this note was checked in Lean or established by numerical experiments. The arguments below are complete on their stated finite-matrix domains. No new integer-multiplication κ is asserted.

The main positive result is an exact inverse of every finite Gaussian Toeplitz matrix as two Toeplitz convolutions and three diagonal maps, with dimension-independent conditioning when the Gaussian is sufficiently narrow. A second construction turns interpolation on the actual rounded geometric-node subset into interpolation on its complete geometric grid. The second construction is exact algebra; its fast, stable implementation on the nonuniform caller remains a distinct mathematical question.

## Provenance and reuse

The local source inspection used `Mathproof/GenVandermonde.lean`, especially `RealTau.Chebyshev.TotalPositivity.det_expMatrix_pos` and `det_expMatrix_submatrix_pos`; `Mathproof/TotalPositivity.lean`, including `totallyPos_expKernel` and positive row/column scaling; and `Mathlib/LinearAlgebra/Vandermonde.lean`, including `Matrix.det_vandermonde_ne_zero_iff`. These are source precedents, not new kernel evidence. Their own source notes identify the exponential total-positivity theorem as classical.

The existing `research/native-word-fft/GAUSSIAN-CHIRP.md` supplies the inherited centered Gaussian convolution route. `research/native-kappa-30201655/modern-sources/BILATERAL-LDU.md` supplies the inherited finite-origin and bilateral factorization of the actual rounded-node Gaussian map, and explicitly leaves a fast upper-factor algorithm unproved. The source Gaussian resampling lineage is credited there to Harvey and van der Hoeven and retained repository contributors. This note expands the finite uniform-node specialization into an explicitly bounded convolutional inverse and develops the missing-node completion identity. The elementary q-binomial, Vandermonde and Toeplitz ideas are classical; no claim of historical or exhaustive project novelty is made.

## A1. Gaussian total positivity by positive scaling

**Theorem.** Let a > 0, and let x_0 < ... < x_(m−1) and y_0 < ... < y_(n−1) be real. The rectangular matrix G_ij = exp(−a(x_i−y_j)^2) is strictly totally positive: every square minor with increasing row and column selections has positive determinant.

**Proof.** Write G_ij = exp(−a x_i²) exp(2a x_i y_j) exp(−a y_j²). The middle kernel is the exponential kernel from the cited generalized-Vandermonde result, with increasing exponent list 2a x_i and increasing node list y_j. Every increasing minor of that kernel has positive determinant. Multiplying its selected rows and columns by the displayed positive factors multiplies its determinant by a positive number. This proves the assertion. In particular every square principal submatrix is nonsingular. ∎

This result supports existence and ordered elimination. It does not bound a fast algorithm's intermediate precision, and those bounds will be proved separately for the uniform case.

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

## A9. Positive completion of interpolation on a geometric-node subset

Let r > 1, T ≥ S ≥ 1, and let K be an S-element subset of {0,...,T−1}. Suppose values y_k are given at x_k = r^k for k in K. Put

    R(X) = product_(k not in K) (X−x_k).

**Theorem.** The unique polynomial P of degree less than S with P(x_k) = y_k for k in K is constructed as follows: prescribe T full-grid values z_k = R(x_k)y_k for k in K and z_k = 0 otherwise; interpolate the unique polynomial Q of degree less than T on all T geometric nodes; divide Q exactly by R. The quotient is P and the remainder is zero.

**Proof.** The nodes are distinct. Ordinary Vandermonde nonsingularity gives existence and uniqueness of Q. For every missing node, Q vanishes there. Each corresponding linear factor divides Q, and distinct linear factors are pairwise coprime; therefore their product R divides Q. Write Q = R P. Since deg Q < T and deg R = T−S, the quotient has degree less than S. At a selected node R(x_k) is nonzero, so Q(x_k) = R(x_k)y_k implies P(x_k) = y_k. The selected-node Vandermonde matrix is nonsingular, proving uniqueness. ∎

This is a complete exact-arithmetic reduction, with multiplication by sample weights, full geometric interpolation and polynomial division all explicit. No operation is declared free. It becomes a complexity improvement only after those maps have been priced with adequate intermediate precision.

## A10. Application to the actual rounded-node Gaussian finite section

Fix a > 0 and 1 < ρ ≤ 2. Put q_i = floor(ρi+1/2), β_i = ρi−q_i, and consider a finite section indexed by 0 ≤ i,j < S,

    G_ij = exp(−a[(ρj−q_i)²−β_j²]).

**Theorem.** G is an explicitly scaled Vandermonde matrix at a subset of a full geometric grid. Precisely, with

    r = exp(2aρ),     x_i = r^(q_i),
    d_i = exp(−a q_i²),
    e_j = exp(−aρ² j² + aβ_j²),

one has G_ij = d_i x_i^j e_j. The integers q_i are strictly increasing and lie in {0,...,T−1} for T = q_(S−1)+1. Consequently solving G u = b reduces exactly to A9 with selected grid indices q_i and data b_i/d_i, followed by coefficient division by e_j.

**Proof.** Expanding the exponent gives −a q_i² + 2aρ q_i j − aρ² j² + aβ_j², which is the exponent of the displayed factorization. Since ρ > 1, increasing i by one increases floor(ρi+1/2) by at least one; q_0 = 0, so all selected indices are distinct and in the stated grid range. If P(X) = sum_(j=0)^(S−1) e_j u_j X^j, then G u = b is exactly P(x_i) = b_i/d_i. Apply A9, then recover u_j from the coefficients of P by division by the known nonzero e_j. ∎

The same statement holds for an arbitrary finite integer interval after shifting the polynomial powers and its row diagonal by the interval's left endpoint, as required by the inherited finite-origin factorization. This is not the infinite periodized caller: finite-section inversion and periodization cannot be interchanged without a separate argument.

## Mathematical scope and forward direction

A4–A8 prove a complete uniform-grid Gaussian inverse with explicit convolutional structure, bounded intermediate maps and sufficient error bounds. This supports replacing a dense uniform Gaussian inverse by polynomial/convolution operations without the usual global Vandermonde magnitude blow-up. It does not state that the actual rounded-node section is Toeplitz.

A9–A10 give a complete exact reduction for that rounded-node section. The synthesis note's normalized annihilator estimates control several otherwise huge diagonal quantities. To obtain the stronger native Word RAM result, the remaining positive theorem should construct a fast *scaled* completion/interpolation/division circuit whose intermediate map norms are bounded by exp(O(P)) at target accuracy 2^(−P). Ordinary unscaled polynomial interpolation can lose far more precision, so that theorem is neither assumed nor hidden inside the word “interpolate.” No better κ follows until the complete transform and multiplication recurrence are assembled.

## A11. A constructive run decomposition for the actual periodic inverse

The following extension uses the actual rounded-node Gaussian formula, rather than replacing it by a Toeplitz matrix. It is a positive theorem with a full informal derivation and manual mathematical review. Its finite-word corollary imports the already documented ordinary bounded-word convolution and near-identity band-solve constructions; neither is treated as a new multiplication oracle.

### A11.1. Setup and exact Beatty runs

Let S,T be positive integers with S < T ≤ 2S; set ρ = T/S, θ = ρ−1, and g = T−S = Sθ. For all integers i put

    q_i = floor(ρi+1/2),      β_i = ρi−q_i.

Thus −1/2 ≤ β_i < 1/2, q_(i+S) = q_i+T, and β_(i+S) = β_i. For a > 0 define the bilateral kernel

    G_ij = exp(−a[(ρj−q_i)²−β_j²]).

Its periodic matrix is N_ij = sum_(k in Z) G_(i,j+kS), after choosing one representative of each coordinate class modulo S. Absolute Gaussian decay makes every row sum converge.

For each integer c define the run I_c = {i in Z : q_i−i = c}.

**Lemma.** Every I_c is a consecutive nonempty integer interval of length either floor(1/θ) or ceil(1/θ), and I_(c+g) = I_c+S. One may choose a length-S fundamental interval that is the union of exactly g complete consecutive runs.

**Proof.** The equality q_i−i = floor(θi+1/2) gives

    I_c = Z intersect [(c−1/2)/θ, (c+1/2)/θ).

The interval length is 1/θ ≥ 1, so it contains either its floor or ceiling number of integers and is nonempty. Its translation after adding g to c is by g/θ = S. Choose the first integer of I_c as the beginning of the fundamental interval. The disjoint consecutive runs I_c,...,I_(c+g−1) fill the interval ending immediately before I_(c+g), which is its translate by S. ∎

All subsequent indices refer to these chosen lifts. This is an explicit cyclic relabeling, not an assertion that a run boundary happens to be at index zero.

### A11.2. A physical-coordinate contraction estimate

**Lemma.** For every i and every nonzero integer h,

    G_(i,i+h) ≤ exp(−aρθ h²).

Consequently

    ||N−I||_infinity ≤ 2/[exp(aρθ)−1].                 (6)

In particular aρθ ≥ log 17 implies ||N−I|| ≤ 1/8.

**Proof.** Since β_i = ρi−q_i, the expression in the exponent is

    (ρh+β_i)²−β_(i+h)².

Using |β_i| ≤ 1/2 and |β_(i+h)| ≤ 1/2 gives a lower bound

    (ρ|h|−1/2)²−1/4
      = ρ|h|(ρ|h|−1)
      ≥ ρθ h².

For the last inequality, subtract ρθh²: the difference is ρ|h|(|h|−1) ≥ 0. The h = 0 term is exactly 1. Each periodic row includes the remaining bilateral entries exactly once; thus its excess row sum is at most 2 sum_(h≥1) exp(−aρθh²). Since h² ≥ h, this is at most 2/(exp(aρθ)−1), proving (6). At the stated threshold the last quantity is at most 1/8. ∎

This estimate bounds the actual matrix in physical coordinates. It does not infer conditioning from a large diagonal similarity.

### A11.3. Every whole run is an exactly solvable Toeplitz similarity

**Lemma.** The unperiodized principal matrix B_c = (G_ij)_(i,j in I_c) equals

    B_c = D_c A_c D_c^−1,
    (A_c)_ij = exp(−aρ(i−j)²),
    (D_c)_ii = exp(a β_i²/θ).

In particular 1 ≤ (D_c)_ii ≤ exp(a/(4θ)).

**Proof.** On I_c one has q_i = i+c and β_i = θi−c. Expanding gives

    −a[(ρj−i−c)²−(θj−c)²]
      = −aρ(i−j)² + (a/θ)[(θi−c)²−(θj−c)²].

Exponentiating is exactly the claimed diagonal similarity. The range of β_i proves the diagonal bounds. Translating the indices of A_c to start at zero does not change their differences, so A4–A8 apply with q = exp(−aρ). Under aρθ ≥ log 17 and θ ≤ 1, this q is less than 1/2. ∎

Thus a run inverse is a diagonal map, the two-convolution inverse from (5), and another diagonal map. Its exact application uses two length-|I_c| Toeplitz convolutions and O(|I_c|) other scalar operations. The large similarity costs O(a/θ) additional magnitude/accuracy bits, as opposed to an unbounded global index-square guard.

### A11.4. A sparse boundary coupling with a rigorous tail

Choose an integer w ≥ 1 such that every run has length at least 2w+1. Retain every G_ij within the same chosen run, with no within-run truncation. For different runs, retain only lifts satisfying |j−i| ≤ w, including a lift across the cyclic seam if appropriate. Periodize this retained kernel to obtain A. Let B be the block diagonal matrix formed by the complete B_c blocks, and set E = A−B.

**Lemma.** With η = 2/[exp(aρθ)−1] ≤ 1/8,

    ||B−I|| ≤ η,       ||A−I|| ≤ η,       ||E|| ≤ η,
    ||B^−1||, ||A^−1||, ||N^−1|| ≤ 1/(1−η),
    ||N−A|| ≤ 4 exp(−a w(w+1)).                      (7)

E has nonzero rows and columns only in the first or last w coordinates of each run; it couples only adjacent runs in the cyclic order.

**Proof.** All retained entries are nonnegative and are a subset of the corresponding entries in N; the retained diagonal is exactly 1. Hence the row sums of B−I and A−I, as well as E, are bounded by those of N−I. The inverse bounds follow from the convergent Neumann series; the series is used here only to prove a norm, not to hide an unpriced algorithm. If a retained cross-run entry has |j−i| ≤ w, both its endpoints lie within w of the shared run boundary. Since all run lengths exceed 2w, no such entry crosses two boundaries. This proves support and adjacency.

For the tail, every omitted term has nonzero displacement of magnitude at least w+1; some such terms within a run are retained as well, which only improves the estimate. The elementary bound

    (ρh+β_i)²−β_(i+h)² ≥ |h|(|h|−1)

holds because ρ > 1 and |β| ≤ 1/2. For h ≥ w+1 the successive majorants exp(−a h(h−1)) have ratio at most exp(−2a(w+1)). Under aρθ ≥ log17 one has a ≥ (log17)/2, since ρθ ≤ 2, so that ratio is less than 1/2. Therefore two tails sum to at most 4 exp(−a w(w+1)). ∎

The elementary bound for a uses ρθ ≤ 2, valid for 0 < θ ≤ 1 and ρ = 1+θ. No source estimate on an unrelated matrix is being substituted.

### A11.5. Explicit Schur system and recovery

Let J contain the first and last w coordinates of each run, let m = |J| = 2gw, and let V select these coordinates. Let K = V E V^T and U = V^T K, so E = U V. Define

    R = I_m + V B^−1 U.                              (8)

**Theorem.** R has norm-distance at most η/(1−η) ≤ 1/7 from identity. Grouping its coordinates by runs makes it cyclic block tridiagonal with block size 2w. For every b, solve

    y = B^−1 b,
    R z = V y,
    x = B^−1(b−U z).                                 (9)

Then A x = b exactly. In particular no dense application of the stored matrix B^−1 U is required at query time.

**Proof.** Selection V and embedding V^T have norm 1. Since E is supported on J×J, ||U|| = ||K|| ≤ η, and (7) gives ||R−I|| ≤ η/(1−η). B^−1 is block diagonal by runs; K couples only adjacent runs, so multiplying on the left by V B^−1 V^T preserves that adjacency. This proves the block pattern. The norm bound proves R is invertible.

From (9), x = y−B^−1 U z. Hence Vx = Vy−V B^−1 U z = z by (8). Therefore

    A x = Bx + U Vx = b−Uz + Uz = b.

The construction is explicit: U z is a sparse boundary product followed by an embedding, and the final B^−1 uses the same local convolutional block inverses as the first solve. ∎

This last recovery choice is essential for the cost. Explicitly storing B^−1 U and multiplying it by z could cost O(Sw), which is not the desired bound.

### A11.6. Boundary solve and its entire cost

**Lemma.** A matrix R as in A11.5 has an input-independent factorization with preparation cost O(m w² + w³) and per-right-hand-side solve cost O(mw + w²), using scalar arithmetic. Its inverse norm is at most 7/6, and all required ordinary-band and small correction systems are uniformly strictly diagonally dominant.

**Proof.** If there are at most two run blocks, R has size at most 4w; ordinary dense elimination gives these bounds. Otherwise cut the two cyclic corner blocks to form R_0. Since ||R−I|| ≤ 1/7, deleting selected off-diagonal blocks does not increase the absolute row sum of R−I, so ||R_0−I|| ≤ 1/7. It is an ordinary band matrix of bandwidth at most 4w. The removed corner matrix C has norm at most 1/7 and rank at most 4w. Write C = U_0 V_0 by selecting its at most 4w nonzero boundary columns, with ||U_0|| ≤ 1/7 and ||V_0|| = 1.

Factor R_0 once by ordinary no-pivot band elimination. Strict row diagonal dominance is preserved under elimination: eliminating a pivot column from a remaining row increases its diagonal-dominance margin and decreases its absolute row sum, by the triangle inequality and the pivot row's strict margin. Thus all pivots are bounded away from zero. The factorization uses O(mw²) operations, and a triangular solve costs O(mw).

Prepare X_0 = R_0^−1 U_0 with O(w) band solves. This costs O(mw²). The correction matrix I + V_0 X_0 has norm-distance at most (7/6)(1/7) = 1/6 from identity and size at most 4w. Factor it once in O(w³) operations. Woodbury then solves R with a constant number of band solves, one O(w²) small solve and an O(mw) product X_0 z. Every term is included in the stated counts. The direct norm estimate ||R^−1|| ≤ 1/(1−1/7) = 7/6 gives the asserted uniform conditioning. ∎

For fixed-point evaluation, strict row diagonal dominance preserves the initial margin at least 6/7 and absolute row sum at most 8/7 throughout exact elimination. Thus every upper-factor entry is bounded by 8/7, every multiplier is bounded by an absolute constant, and each lower-factor row has O(w) nonzeros of bounded magnitude. Consequently ||L|| = O(w), ||U|| = O(1), ||L^−1|| = ||U R_0^−1|| = O(1), and ||U^−1|| = ||R_0^−1 L|| = O(w). The same bounds hold on leading principal subproblems, and upper-triangular suffix inverse blocks are submatrices of U^−1. They control the forward and backward partial solves. Each computed factor/solve residual is a sum of polynomially many local rounding terms; coefficient perturbations smaller than an inverse polynomial in S and w preserve a fixed positive margin. Therefore no exponential accumulation of rounding errors is assumed. The small dense correction has the same argument with size O(w). Consequently P + O(log(S+1) + log(w+1) + log(||b||+1)) bits suffice for the boundary part. This is the constructive bounded-band result already developed in the inherited `NATIVE-BANDED-INVERSE.md`, now applied to an explicitly identified matrix satisfying its hypotheses; no dense Schur inverse is supplied as an oracle.

### A11.7. The complete per-input cost and precision statement

Let C(L) be the scalar work of one explicitly chosen length-L Toeplitz convolution. The exact A-solve (9), after input-independent preparation, uses

    O(sum_c C(|I_c|) + S + g w²)                       (10)

scalar operations. Using the inherited ordinary bounded-word convolution construction gives

    O(S log(2+1/θ) + S θ w²).                          (11)

**Proof.** Both applications of B^−1 use two convolutions per run and O(S) diagonal/arithmetic work in total. Each local block length is at most ceil(1/θ). The boundary solve costs O(mw + w²) = O(gw²), and U z also costs O(gw²), because at most two adjacent w by w boundary blocks occur at each run interface. Gathering and scattering cost O(S). These prove (10); substituting C(L) = O(L log(L+2)) and summing the run lengths gives (11).

Each B_c inverse is evaluated as D_c A_c^−1 D_c^−1. The core factors have norms bounded in A6, while D_c and D_c^−1 have norms at most exp(a/(4θ)) and 1. Applying A7 at internal error level smaller by that exponential pays the similarity explicitly. Coefficient row-sum errors require at most another O(log S + log w) guard. All local and boundary operations therefore admit a sufficient precision of

    P + O(a/θ + log(S+1) + log(w+1) + log(||b||+1)).    (12)

The physical matrices B and R have constant inverse norms by A11.4–A11.6; their computed coefficients can be formed to the required row-sum accuracy by allocating per-entry errors inversely proportional to their explicitly bounded row supports. The input-independent preparation includes constructing the sparse E, forming (8) by local solves on its boundary columns, preparing convolution kernels and factoring the boundary systems. It has a polynomial bound in S, w, 1/θ and the precision, and all prepared coefficients are charged to that stage. In the intended regime S = 2^(o(p)) and all other displayed parameters are polynomial in p, this is 2^(o(p)) preparation.

There is no uncharged exponential-evaluation instruction: all exponents actually generated have magnitude O(P+a/θ) on a local run or retained boundary window. Raw full within-run Gaussian entries could have exponents of order a/θ², but they are never formed: the q-LDU inverse uses only q^r with r at most the run length, q-product factors, and the diagonal values exp(aβ_i²/θ). Retained cross-run coefficients have displacement at most w and exponents O(a(w+1)²) = O(P+a). Thus no global or full-block index-square exponent is concealed in the preparation. Their values can be approximated to the stated precision by elementary range reduction, Taylor expansion on a bounded interval and repeated squaring, in polynomial precision-dependent preparation time. Likewise roots and transforms used by the ordinary convolution construction belong to charged input-independent preparation. The note does not claim the entire native instruction sequence has been emitted.

Finally, choosing w so that the last bound in (7), multiplied by ||b||/(1−η)², is at most 2^(−P−1), makes A^−1 b an approximation to N^−1 b with that error, by

    N^−1−A^−1 = N^−1(A−N)A^−1.

Allocate the remaining half of the error to (12). This proves a sufficient constructive algorithm for the actual periodic inverse, including truncation, local factors, boundary solve, recovery and precision. ∎

### A11.8. A parameter choice that improves the inverse adapter exponent

**Corollary.** Suppose a family has a target precision p, θ = Θ(p^(−1/4)), a = Θ(p^(3/4)), log(S+1) = O(p^(3/4)), and ||b|| ≤ exp(O(p)). In the extended arithmetic Word RAM defined in A11.9, all hypotheses above hold eventually, one may choose w = Θ(p^(1/8)), and the actual periodic inverse has

    O(S log p)

per-right-hand-side word work after subexponential-in-p preparation, using O(p)-bit words. If the array has D = Θ(p^(1/4)) such axes and total volume T_array, the total inverse-adapter contribution is

    O(T_array p^(1/4) log p),

apart from the separately charged preparation.

**Proof.** Here aρθ = Θ(p^(1/2)), so A11.2 gives η ≤ 1/8 eventually. The Gaussian tail cutoff needs w = Θ(sqrt(p/a)) = Θ(p^(1/8)); the minimum run length is Θ(1/θ) = Θ(p^(1/4)), which eventually exceeds 2w. Also a/θ = Θ(p), so (12) uses O(p) bits. In (11), θw² = Θ(1), and log(2+1/θ) = O(log p). This proves the per-line bound. There are T_array/S lines of length S along an axis, and D axes, giving the displayed sum. The source's asymptotic line lengths S = 2^(o(p)) make the polynomial-in-S preparation subexponential in p. ∎

This improves the inherited inverse-adapter bound obtained by ordinary reused band solves, O(T_array p^(3/8)) at D = Θ(p^(1/4)), to O(T_array p^(1/4) log p). It is a fixed-power improvement for this actual adapter, rather than a small local constant change. It is not, by itself, a new multiplication κ: forward maps, the complete transform, the native supplier and the outer recurrence still need to be assembled under their own precise contracts.



### A11.9. Explicit convolution and native arithmetic model

For the native corollary, also impose an effective input condition: a is an explicitly specified positive rational, π times an explicitly specified positive rational (including the actual a = πα²), or a real with a charged polynomial-time certified approximation procedure to the working precision. The integers S,T are explicitly supplied, and b is supplied as fixed-point data or certified enclosures at the stated working precision, with a supplied magnitude bound whose logarithm is O(p). The exact real identities in A11.1–A11.6 do not require this computability restriction. For the native corollary, fix the following model. A word contains W bits, with W a sufficiently large constant times the precision bound (12). Unit-cost operations include bounded-word addition, subtraction, multiplication, comparison, memory access, integer division, and a shift that divides by a power of two with a specified rounding convention. The word width is large enough to contain raw products before fixed-point rescaling. Complex numbers use two such fixed-point values. Thus one real or complex fixed-point addition, product, or division by a pivot bounded away from zero costs O(1) of these native operations and has a chosen O(2^(−B)) local error. This is an explicit extended Word RAM; no instruction-level realization in the more restrictive tcslib ISA is claimed. The exact field-operation count (10) and the precision requirement (12) are mathematical statements independent of that implementation choice.

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

