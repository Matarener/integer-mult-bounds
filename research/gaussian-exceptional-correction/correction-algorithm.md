# An exact pruned-butterfly compiler for the Gaussian exceptional correction

Dugongue, with substantial OpenAI Codex assistance. This note gives a complete ordinary algorithm for the exceptional operator in the preceding Gaussian spectral transport. It replaces a dense rank-one implementation by two explicitly pruned Walsh passes, and proves their precision, storage and bit-cost bounds. The correction is constructed for every input, rather than assuming that its measurements are already available. This is an informal mathematical result; no numerical experiment, mathematical evaluator, solver or Lean check was used.

## 1 Exact operator and actual output grid

Let π = 1+i, n ≥ 1, N = 2^n and

    C = [[i,1],[1,i]],     A_n = (C/π) tensor ... tensor (C/π).

Choose integers 0 ≤ R < n and 0 ≤ a ≤ n−R. The case R = n, a = 0 has zero correction and is omitted below. Put

    g(X) = i^a sum_(h=0..R) (i−1)^h binom(X−a,h),
    E = A_n − g(W),
    W = (1/2) sum_(j=1..n) (I−X_j),

where X_j swaps coordinate bit j. For λ,s in {0,1}^n let

    H_(λ,s) = (−1)^(λ dot s).

Thus H^2 = N I, and A_n has Walsh eigenvalue i^|λ|. Let

    T = {λ : |λ| < a or |λ| > a+R},
    d_j = i^j − g(j).

The exact identity is

    E = 2^(−n) H diag(d_|λ| 1_(λ in T)) H.

A coefficient can vanish outside the interval too. Keeping it in T is harmless; no equality between rank and |T| is asserted. The normalized operator need not take integral inputs to integral outputs. Its actual integral numerator is

    G_T = π^n E = C^(tensor n) − π^(n−R) G_B,
    G_B = π^R g(W).

The preceding note proves that G_B is Gaussian integral. Therefore G_T is Gaussian integral as well. This algebraic identity will justify the exact quotient used by the algorithm; a division of an arbitrary dirty field is never assumed.

## 2 A uniform valuation dividend in every exceptional coefficient

**Theorem C1.** For every integer j, including j < a,

    d_j is divisible by π^(R+1) in Z[i].

**Proof.** Set z = i−1 = iπ and b = j−a. For b ≥ 0, expand (1+z)^b by the finite binomial theorem. The difference from its terms of degree at most R is divisible by z^(R+1). For b < 0, the same conclusion holds modulo z^(R+1): in the finite quotient Z[i]/(π^(R+1)), 1+z is a unit and its negative integer powers equal the truncated formal binomial series. This follows either by multiplying by the positive power or by the finite geometric inverse of 1+z. Its coefficients binom(b,h) are integers. Since 1+z = i and i^b is an actual Gaussian unit, the congruence is an ordinary Gaussian-integer congruence. Multiply by i^a. QED.

Define the actual Gaussian integers

    e_j = d_j / π^(R+1),     L = 2n−R−1.

Since 2^n = (−i)^n π^(2n),

    E = i^n π^(−L) H diag(e_|λ| 1_(λ in T)) H.       (1)

There is no odd denominator in (1). The only remaining denominator is the declared power of π. Gaussian coefficient preparation uses integer binomial coefficients, additions, shifts and exact divisions by π. It is not an oracle for a rational matrix.

For instance, a safe integer bound on the scalar coefficients is obtained from

    G = (R+1) [2(n+a+R+1)]^R,
    B = 3 + ceil(log2(G+1)).

The elementary product bound for binom(j−a,h) gives |g(j)| ≤ G on 0 ≤ j ≤ n. Hence each real or imaginary coordinate of e_j has fewer than B bits. This deliberately loose bound is adequate for binary constant synthesis. These constants can be prepared once per weight j, rather than once per Walsh label. A finite Pascal table for generalized integer binomial coefficients, followed by exact π division, supplies all of them without invoking multiplication by a rational scalar.

## 3 An output-pruned Walsh circuit with a proved operation bound

For a nonempty frequency set U ⊆ {0,1}^n let p_d(U) denote the number of its distinct prefixes of length d. Define

    A(U) = N sum_(d=1..n) p_d(U)/2^d.

This is an integer: a prefix at level d carries an array of length N/2^d. If U is empty, A(U) = 0.

**Theorem C2.** The vector ((Hx)_λ : λ in U) can be computed by an explicit source-preserving ordinary circuit using exactly A(U) additions or subtractions, before copies, routing and cleanup. Its transpose computes H times a vector supported on U using O(A(U)+N) ordinary additions, copies and signs. Both circuits can use O(N+|U|+n) Gaussian storage cells.

**Proof.** At the root, split the input array into its two spatial halves. For each frequency bit that occurs as a first bit of U, form either their sum or difference. A requested child array has N/2 entries. Continue recursively: a requested frequency prefix of length d requires one sum or difference array of length N/2^d from its parent. There are p_d(U) such prefixes, proving the exact addition count. At depth n, the leaves are precisely the requested Walsh coefficients. Every leaf is a sum of the correct input coordinates with the correct signs, by the ordinary Walsh recursion.

For the transpose, start with the selected leaf values. Reverse the graph, accumulating each sum/difference node into its two parent pieces with the corresponding signs. This is the exact transpose of a finite linear circuit. Alternatively, recursively synthesize the two child arrays and join them as [v_0+v_1,v_0−v_1], with zero for an absent branch. No inverse Walsh operation is being claimed here: the circuit emits the unnormalized H response. Both descriptions use a constant number of reads, writes and additions per forward node, plus the N output writes.

A depth-first forward traversal retains only arrays on a path, whose lengths sum to less than 2N, together with the |U| output cells. A depth-first transposed traversal retains one completed sibling while computing the other; the same geometric bound gives O(N) additional cells. Input x is read but never overwritten. The circuits run successively, so their workspace can be reused. Clear every owned live cell afterwards, or retain the work and reverse it under the host's charged reversible convention. QED.

There is a real dense source read whenever U is nonempty. The theorem does not replace arbitrary input access by a rank-|U| oracle. A tape implementation must also pay for the actual routed subarray accesses; the stated operation count is for a literal indexed ordinary array model.

### Exact useful bounds on the prefix sum

Write t = |U| ≥ 1. Since p_d ≤ min(2^d,t),

    A(U) ≤ N min(n, floor(log2 t)+2).                (2)

Indeed the summands are at most one up to floor(log2 t), and the remaining geometric tail is at most two. In particular the constructed method is O(N log(t+1)), rather than the O(Nt) incidences of separate dense measurements.

For a low-weight cap U = {λ : |λ| ≤ k},

    A(U) ≤ (2k+1)N.                               (3)

To prove (3), p_d/2^d is Pr[Bin(d,1/2) ≤ k]. The sum of those probabilities for d ≥ 0 is the expected number of trials before the (k+1)-st success, namely 2(k+1). This identity can equally be proved by summing the geometric waiting-time series for the k+1 successes. Removing the d = 0 term and truncating at n proves (3). The upper-weight version follows by complementing every bit.

For the actual union T, the two cap parameters are

    k_low = a−1,     k_high = n−a−R−1.

A negative cap is absent. Apply (3) separately and use the fact that the prefix set of a union is contained in the union of the prefix sets. This gives an explicit additional bound by the sum of (2k+1)N over the nonempty caps. Bounds (2)–(3) can always be intersected with A(T) ≤ nN. They are algebraic inequalities, not a newly executed count or benchmark.

## 4 The complete correction algorithm and its exact precision

Fix a target Gaussian precision p ≥ 1 and an arbitrary Gaussian-integer input x. Set

    Q = p+L = p+2n−R−1,
    m = n−R−1 ≥ 0.

Execute the following finite ordinary algorithm.

1. Run the output-pruned Walsh analysis of x for λ in T modulo π^Q.
2. Multiply each selected coefficient by its prepared Gaussian integer e_|λ| modulo π^Q.
3. Run the transposed pruned circuit modulo π^Q to obtain z = H diag(e) Hx modulo π^Q.
4. Divide the resulting z exactly by π^m, multiply by i^n, and retain the answer modulo π^(p+n). This answer is G_T x modulo π^(p+n).
5. Deliver the declared output numerator, preserve x, and perform charged cleanup of the analysis bank, synthesis buffers and coefficient work fields.

**Theorem C3.** This is an exact ordinary correction compiler for every input. It recovers E x modulo π^p on its declared π^(−n) output grid. It requests no Gaussian primitive and creates no new productive target.

**Proof.** The first three steps compute the integral vector in (1) with additive error divisible by π^Q. Multiplying (1) by π^n gives

    G_T x = i^n π^(−m) z.

Since G_T is Gaussian integral, z is divisible by π^m for every Gaussian-integer x. Any representative of its residue modulo π^Q has the same divisibility because Q ≥ m. Exact quotienting therefore determines z/π^m modulo π^(Q−m) = π^(p+n). This proves step 4. The final π^(−n) header gives error divisible by π^p in the fractional output, as required. QED.

Exact division by π of a known-divisible Gaussian integer is the explicit map

    a+bi -> ((a+b)/2) + ((b−a)/2)i.

Its two halves are integers under the stated divisibility. There is a faster exact binary implementation of the entire quotient. Write m = 2k or 2k+1. If m is odd, apply the displayed π division once. Next divide both integer coordinates by 2^k and multiply by the phase (−i)^k. Indeed π^(2k) = 2^k i^k. The coordinate divisions are exact because the vector was proved divisible by π^m. A binary right shift and copy performs each in O(Q+1) bit reads/writes, including its output, rather than m successive whole-operand passes. These are charged operations on an owned numerator, and the host must realize their stated routing; no inverse primitive acts on an original operand.

One can implement modulus arithmetic with a standard rectangular residue pair: use the even Gaussian precision Q' = 2 ceil(Q/2), retain the two integer coordinates modulo 2^(Q'/2), and discard the at-most-one extra Gaussian precision unit at the end. Since (π^Q') = (2^(Q'/2)), all additions, phases and binary scalar syntheses are exact in that representation.

### Literal bit and word costs

Let t = |T| and let B be the coefficient bound from Section 2. Repeated doubling and signed addition multiplies a payload by e_j in O(B) Gaussian additions, with ordinary multiplication by i for the imaginary part. Thus the constructed correction has scalar operation count

    O(A(T) + N + tB + preparation),

where an exact binary shift/coordinate conversion is charged by its actual operand traffic. If a more restrictive scalar instruction set permits only successive exact π divisions, use its alternative Nm scalar-pass bill instead. Source reads and output writes contribute N even for one exceptional frequency.

With binary schoolbook additions and the explicit binary quotient above, a safe bit-operation bound is

    O((Q+1)[A(T)+N+tB] + preparation_bits),          (4)

and owned storage is

    O((Q+1)(N+t+n)) bits,

plus the stored scalar constants. On a word RAM with w-bit words, replace the Q+1 factor for arithmetic and scanning by O(ceil((Q+1)/w)), keeping all index arithmetic and routing costs. This is a model-specific statement, not a conversion of a bit-time κ into a word-operation κ.

For coefficient preparation, all n+1 values can be built using generalized Pascal recurrence, powers of i−1, and exact π division. Their bit heights are bounded by a fixed polynomial in n+R times B; this is finite ordinary preprocessing, which is charged once for a fixed public operator and again when its parameters change. It is never charged zero merely because the coefficients are constants in an informal formula.

The previous rank-one implementation has t independent dense analyses and t dense scatters. C2 replaces their Nt scalar incidences by O(N log(t+1)), apart from coefficient synthesis and the stated normalization work. This is a universal constructed improvement in the correction implementation. It does not establish that bulk plus correction beats the fastest complete Gaussian transform: a full Walsh butterfly remains an available O(nN) alternative, and the true normalized precision Q in (4) can be larger than the p+n raw-source precision.

## 5 A further precision-aware pruning theorem

The uniform dividend C1 is not the end of the construction. Let

    beta_λ = v_π(e_|λ|),

with beta_λ = infinity when e_|λ| = 0. Remove leaves with beta_λ ≥ Q, since their contribution to the integral vector z is zero modulo π^Q. Call the remaining frequency set U. For each prefix v of U put

    b_v = min_(λ extends v) beta_λ,
    q_v = Q−b_v.

These are explicit quantities of the displayed scalar coefficients, not assumed favorable values. When no child exists, its contribution is zero.

**Theorem C4.** The exact correction can be computed with forward prefix v stored only modulo π^(q_v), and with transposed prefix v stored after removing its common factor π^(b_v), again modulo π^(q_v). Its bit-work for the two butterfly passes is bounded by a constant times

    sum_(v a nonempty prefix of U) (N/2^|v|)(q_v+1),

plus source and output traffic, leaf coefficient synthesis, exact final quotient and cleanup at their actual stated precisions.

**Proof.** Every descendant leaf requires Hx only modulo π^(Q−beta_λ): its subsequent multiplication by e_|λ| restores beta_λ powers. A parent prefix has q_parent ≥ q_child because a minimum over fewer descendants cannot decrease. The forward sum/difference array may therefore be reduced to each child's smaller modulus before descending, with no effect on the final z modulo π^Q.

At a leaf write e_|λ| = π^(beta_λ) u_λ with u_λ integral and unit. Store u_λ (Hx)_λ modulo π^(Q−beta_λ). On upward synthesis, a child v has already removed π^(b_v). To combine its response at parent w, multiply its stored response by π^(b_v−b_w), which is a nonnegative integral power, and add or subtract the two child responses. This computes the parent response after removing π^(b_w), modulo π^(Q−b_w). Induction proves the exact root z after its root factor is restored. Its final quotient is the one already proved in C3. Every retained prefix handles N/2^|v| coordinates at q_v precision, proving the displayed bill. QED.

The theorem jointly prunes frequencies and precision. It never promotes a valuation upper bound to a lower bound. Safe proven lower bounds may replace the exact beta_λ, giving a weaker but still correct construction. Computing exact valuations and masks is ordinary coefficient preparation and must be included in a runnable implementation; this note supplies no executed mask or count.

## 6 Shared input batches and actual supplier installation

Suppose several consumers have the SAME unchanged input x and request residuals of the same Walsh basis with different stated spectral multipliers. Their analysis bank Hx on the union of requested frequencies can be computed once and reused. The union bank is stored to the maximum precision requested at each leaf; Theorem C4 gives its forward precision profile. Each consumer still pays its own multiplier application, transposed delivery, output grid, cleanup and endpoint reconciliation. If a consumer changes x, reuse requires the actual version update, not an alias to the old bank.

This is an explicit universal shared-bank construction. It is applicable to a supplier only after identifying its literal source vectors, coframes and requested outputs. The source-independence of the final multiplication targets remains unchanged: analysis coefficients and intermediate modes are correlated data and earn no additional productive credit.

For a complete current supplier replacement, combine the actual bulk compiler G_B at modulus π^(p+R) with C3 or C4 for G_T at modulus π^(p+n), then use

    π^n A_n x = π^(n−R) G_B x + G_T x.

Every term is an actual ordinary numerator. This identity closes the exceptional algebraic correction for arbitrary integral input and arbitrary dirty exterior fields when the ordinary word touches only its owned arrays and the specified input/output windows. It is stronger than merely observing a small residual rank: it supplies the whole missing correction word.

The sufficient whole-caller comparison is consequently concrete. Take its old full paid Gaussian list and productive list; replace only the selected actual response by the ordinary word just constructed; charge (4), bulk synthesis, routing, coefficient preparation, borrowed input storage, guards and cleanup in the ordinary budget; retain every unchanged paid job and productive target. If the resulting total ordinary budget and all first/higher-moment and analytic admission inequalities hold at a declared C, the ordinary correction is a valid supplier at that C. No favorable inequality, free full-vector read, cheap dense repair or new κ is assumed in this statement.

## 7 Comparison with the integral triangular alternative

The companion note gives an exact Smith-type factorization of C using integral triangular matrices and diagonal factors 1,π^2. Its tensorization avoids introducing Walsh inversion denominators. It is a distinct positive candidate and should be compared using actual bit costs, not just rank.

The same prefix-pruning proof applies to a triangular tensor transform: a prefix chooses one of two affine branches, with one branch possibly a direct copy. For the RAW tensor C^(tensor n) modulo π^P, diagonal channels with 2|λ| ≥ P vanish. The surviving low-weight cap therefore has k < P/2, yielding O(N min(n,P)) scalar-operation upper bound for each triangular pass and the safe bit bound O(N P min(n,P)), before normalization and physical movement. This is useful at genuinely low raw precision.

For the normalized A_n response at precision p, however, raw precision is p+n. Replacing P by p+n in that formula does not remove the n-dependent bit cost. Early triangular prefixes may still require the larger modulus for their lower-weight descendants. A new interleaving argument would be needed to improve that prefix precision bill. Neither this note nor the companion construction should claim a complete asymptotic speedup from channel counting alone.

## Attribution and scope

The previous package supplies the actual Gaussian tensor matrix and its spectral interpolant, denominator debt and ordinary bulk compiler. OpenAI's pinned October 25, 2026 preprint supplies the concentrated swap-spectrum interpolation architecture. Walsh transforms, transposed linear circuits, generalized binomial series and geometric waiting-time sums are classical. The present note combines them into a fully priced exceptional compiler and precision-aware prefix construction for the specified Gaussian residual. No worldwide novelty claim is made for the component facts.

Credit the existing source authors and all preceding Gaussian, precision, ownership, source-matching, BIT and analytic work. This note creates no new complete κ certificate and performs no independent source replay or kernel audit. New prose is Apache-2.0 with substantial OpenAI Codex assistance.
