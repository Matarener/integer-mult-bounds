# Native coprime-grid construction and exact tensorization

This proof establishes the finite returned-object contract and an eventual polynomial setup theorem. It does not establish a new integer-multiplication exponent. All logarithmic asymptotics below concern growing input parameters; constants are independent of the target widths.

## 1. Imported number theory and model

Use the classical theorem of Henryk Iwaniec, *On the problem of Jacobsthal*, Demonstratio Mathematica 11 (1978), 225–232, [DOI](https://doi.org/10.1515/dema-1978-0121): there is an absolute constant C such that every interval of at least C (r log(r + 2))^2 consecutive integers contains an integer coprime to G, whenever G has r distinct prime factors. Enlarging C covers small r and integer rounding. This is an imported theorem, not reproved here. [Carl Pomerance, Coprime Matchings, section 3](https://math.dartmouth.edu/~carlp/coprime11_12rev.pdf) gives a modern use of Iwaniec's stronger interval estimate. The original publisher PDF was not retrieved successfully during this session; the attribution and bound were checked through that primary research source. No effective numerical C is extracted.

Use a random-access machine with W = c p bits per word for a fixed sufficiently large c, unit-cost word addition, subtraction, comparison, multiplication, division/remainder and random-access memory. Signed intermediates fit in W bits. If division is not a primitive, binary long division uses O(p) of the remaining word operations and only enlarges the polynomial setup bound below. Neither the linear address-stream bound nor its recurrence uses division after setup. Python implements these algorithms as an exact reference; Python timing is not a unit-cost Word RAM timing claim.

Take p = 1 + sum_i log2(t_i) for power-of-two target axes. Words(8 times a slightly larger integer bit bound) in the implementation is a conservative reference guard. Products of selected moduli are below product_i t_i; arithmetic used for gcd, extended gcd, square roots, bands and CRT weights has O(p) bits. For example, even a conservative bound of the square of the full product for an extended-gcd intermediate fits a constant multiple of p bits. Loop counters and addresses also fit. There is no unbounded integer packed into a single fixed-size word.

## 2. Greedy selection lemma

Let intervals J_i of positive integers lie below t_i, with lower endpoints at least 3, and let their lengths be at least H = ceil(C' p^2 log^2(p + 2)). There is a deterministic greedy algorithm selecting an odd s_i in J_i with pairwise gcd 1, using O(D p^3 log^2(p + 2)) native operations when division is available.

Proof. Initially G = 2. At stage i, G = 2 product_{j<i} s_j, so log2(G) ≤ p and its number of distinct prime factors is at most p. Iwaniec's theorem supplies a coprime integer in the last H positions of J_i. That integer is odd because 2 divides G. Descend through odd candidates and compute gcd(candidate, G), taking the first value with gcd 1. There are O(H) tested candidates. Euclid takes O(p) divisions on O(p)-bit integers (each two remainder steps shrink the positive argument by at least a factor of 2). Multiply G by the accepted value. Induction proves pairwise coprimality. Repeating for D stages gives the stated time and O(D) stored words. A finite unsuccessful search raises an error and supplies no completed grid. The proof concerns the algorithm, not a promise that every small interval succeeds. ∎

A prescribed nonnegative candidate budget is a separate resource cap; reaching it fails explicitly. No analytic constant is needed to execute a given bounded finite search. The universal eventual runtime statement imports the non-numerical constant above.

## 3. Guard-safe composite grids

Let D ≥ 1, d = D + 1, and t_i in {2^ell, 2^(ell−1)}. Set

    L_i = floor(t_i (3d−1)/(3d)) + 1,
    U_i = floor(t_i (4d−1)/(4d)).

Whenever these intervals meet section 2's length premise, the algorithm produces pairwise-coprime odd axes satisfying

    t_i (1 − 1/(3d)) < s_i ≤ t_i (1 − 1/(4d)).       (1)

The intervals have length t_i/(12d) + O(1). To guarantee every axis composite, instead search odd a_i in [ceil(sqrt(L_i)), floor(sqrt(U_i))], coprime to twice the product of previous roots, and set s_i = a_i^2. Their root intervals have length Ω(sqrt(t_i)/d), because sqrt(U) − sqrt(L) = (U−L)/(sqrt(U)+sqrt(L)). Pairwise-coprime roots give pairwise-coprime squares; a_i ≥ 3 gives proper factors. Integer square roots are computed by bounded binary search in O(p) word operations per endpoint.

Consequently, for every fixed 0 < ε < 1 and any growing family with D = Θ(p^ε), ell = Θ(p^(1−ε)), and p = 1 + sum_i log2(t_i), both ordinary and square construction succeed for all sufficiently large p in polynomial(p) setup time. Exponential growth of 2^(ell/2) dominates every polynomial in p and D. The constants and an explicit starting p are not supplied. This asymptotic regime is a sufficient family, not a proof that a complete multiplication caller meets all its hypotheses. ∎

## 4. Complete production-axis inequalities

The pinned method production_axis has three mathematical guards. Write g = t − s. From (1), g ≥ t/(4d) and g < t/(3d), with s < t. Thus

    4d g ≥ t > s,
    (2d−1) g < ((2d−1)/(3d)) t < ((3d−1)/(3d)) t < s.

For the period guard, impose the separate sufficient premise

    target_halo + 2w ≤ 2^(ell−3).

Since t ≥ 2^(ell−1), (1) gives s > (1−1/(3d)) 2^(ell−1) > 2^(ell−2), which is at least 2(target_halo + 2w). All three strict comparisons hold. source_guard.py executes the complete pinned method with a host Count adapter, checking the actual method's comparisons rather than an independently typed copy. Finite fixtures use halo = width = 1. They do not replace the universal argument or show any physical tape execution.

Let T = product_i t_i and S = product_i s_i. The band gives

    T/S < (1−1/(3d))^(−(d−1)) < 3/2.

For the last inequality, product_i(1−1/(3d)) ≥ 1−D/(3d) > 2/3. This is the predecessor bound, not a new improvement. PR5152 already supplies the sharper exp(1/3) envelope. Choosing axes very close to t_i generally fails the first guard; the verifier rejects an explicit such example. Therefore the separate near-dyadic construction in grid.build is not silently substituted into the original caller. No statement is made here about production_common, including its Gaussian or precision conditions. ∎

## 5. Optional near-dyadic variant

For B = 2^k and p = 1 + Dk, greedy search downward from B−1 yields deficits δ_i = B−s_i = O(p^2 log^2(p + 2)) whenever B is sufficiently large. For Δ = sum_i δ_i < B,

    product_i s_i / B^D = product_i(1−δ_i/B) ≥ 1−Δ/B,
    B^D / product_i s_i ≤ B/(B−Δ).

This follows by induction from (1−a)(1−b) ≥ 1−a−b for a,b in [0,1]. For even k, selecting roots below 2^(k/2) and squaring gives deficits O(2^(k/2) p^2 log^2(p + 2)). In the stretched-exponential regime of section 3 the relative volume loss tends to zero. This useful standalone grid has a different gap contract: it is not accepted by all the source's production-axis guards.

## 6. Exact CRT and Good–Thomas identity

For any returned coprime grid put N = product_i s_i, M_i = N/s_i, and u_i = M_i^(-1) modulo s_i. Define

    a(x) = sum_i x_i M_i u_i modulo N,
    b(y) = sum_i y_i M_i modulo N,

for 0 ≤ x_i,y_i < s_i. The first map has residues x_i. The second has residues y_i M_i, a bijective coordinate rescaling because M_i is a unit modulo s_i. Both maps are bijections.

Expand a(x)b(y). For i ≠ j, M_i M_j is divisible by N. For i = j, M_i u_i = 1 modulo s_i, so M_i^2 u_i = M_i modulo N. Therefore

    a(x)b(y) = sum_i x_i y_i M_i modulo N.           (2)

Let ζ be exp(2πi/N) and ζ_i = ζ^(M_i). Reindex the finite DFT sum by a(x); at output b(y), (2) factors its phase as product_i ζ_i^(x_i y_i). This is precisely the tensor product of the axis DFTs. No primality of s_i is used. The input and output maps are different: using a(y) as the output map is generally false. The negative control exhibits this error. The same group isomorphism proves cyclic convolution equals product-group convolution. These are classical CRT/Good–Thomas facts, supplied here with explicit conventions and a scoped executable use; they are not claimed as new algebra. ∎

## 7. Linear native address streams

For the input stream use weights c_i = M_i u_i; for the output stream c_i = M_i. Both satisfy 0 < c_i < N and s_i c_i = 0 modulo N. Maintain mixed-radix digits and one current address. On each digit increment, add c_i and subtract N once if needed. When the digit rolls from s_i−1 to 0, the same addition is correct because −(s_i−1)c_i = c_i modulo N. Then carry to the next digit.

Among N emitted positions, the number of first-coordinate changes is at most N−1; second-coordinate changes are at most N/s_1, third at most N/(s_1 s_2), and so on. Since all radices are at least 2, the total is strictly below 2N. Each change costs O(1) word operations and no division. Initialization costs O(D) after the CRT weights are prepared; Euclid and the weight construction are polynomial in p. This gives O(N + D) native stream work and O(D) metadata. Applying the stream to an array costs O(N) loads/stores, requires O(N) data memory, and relies on the model's random-access instruction. There is no free arbitrary permutation or tape simulation hidden in this statement.

The coordinates=True testing option copies D digits per emitted item and is deliberately excluded from the linear stream bound. The reference word counter records arithmetic calls, not every control instruction or interpreter cost. ∎

## 8. Exact scope of the result

Sections 2–4 supply a sufficient algorithm for guard-safe coprime axis selection. Sections 6–7 supply an exact native tensorization/permutation contract. Together they remove primality testing from this specific setup and CRT interface, including an all-composite construction. They do not replace any other theorem that may rely on prime axes, establish numerical Gaussian error bounds, implement an efficient axis transform, admit a native supplier, or recover the integer product with a smaller recurrence.

In particular, polynomial setup in log N versus an inherited subleading setup does not change the dominant exponent. A new κ needs a changed dominant paid recurrence and a complete exact or controlled-precision caller. No such conclusion is derived from this package.
