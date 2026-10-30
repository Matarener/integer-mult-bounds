# Fine-gap Gaussian inversion without the large run gauge

Dugongue, with substantial OpenAI Codex assistance. This note contains informal mathematics only. It uses local proof-tree and DAG precedents; no numerical experiment, external search, solver or Lean run establishes any statement here.

The completed result is a constructive inverse for the actual periodic rounded Gaussian in the fine-gap regime. It removes the exp(a/θ) intermediate range of the preceding whole-run construction. This substantially enlarges that construction's parameter domain. It does not manufacture a stronger Gaussian provider or claim that a complex-only quotient word has already satisfied a different native caller contract.

## Source precedents and scope

The preceding Beatty-run note, `research/beatty-run-gaussian-inverse/analysis.md`, gives the exact Gaussian q-LDU and the periodic run/boundary decomposition. Its Theorem A11 used aρ θ bounded below and paid the full run similarity range a/θ.

The retained `research/native-kappa-30201655/modern-sources/BILATERAL-LDU.md` gives the same actual Gaussian kernel and finite/bilateral inverse formulas. `LOG-A-PHASE-SCHUR-AUDIT.md` records the sharper nearest-neighbor diagonal-dominance bound and the physical phase-cell Schur geometry. `research/native-word-fft/NATIVE-BANDED-INVERSE.md` supplies the constructive elimination/residual argument. `NATIVE-ASSEMBLY.md` already reaches every saving strictly below its admitted provider saving, subject to its retained source contracts. Consequently a new inverse algorithm must not be counted as a new numerical κ merely because its individual cost is lower.

Classical Gaussian elimination, q-binomial identities, geometric recurrences, FFT convolution and Schur complements retain their classical status. The new application here is to factor the exact finite-run inverse so that its long-range part is a stable first-order recurrence and its remaining convolution is short and locally well scaled.

## 1. Actual matrix and fine-gap regime

Let S<T≤2S be positive integers. Put ρ=T/S, θ=ρ−1, q_i=floor(ρi+1/2), and β_i=ρi−q_i. For a>0 define

    G_ij = exp(−a[(ρj−q_i)^2−β_j^2]),
    N_ij = sum_(k in Z) G_(i,j+kS).

Thus β_i belongs to [−1/2,1/2), β_(i+S)=β_i, and N is the actual periodic Gaussian inverse matrix from the retained reduction.

For the asymptotic corollary use a master parameter p tending to infinity, constants c_1,c_2,A_1,A_2>0, and

    c_1 p^(−2) ≤ θ ≤ c_2 p^(−2),
    A_1 log p ≤ a ≤ A_2 log p,

where A_1≥4. Requested accuracy is 2^(−P), with P=O(p), and the input magnitude is at most exp(O(p)). Parameters have explicit polynomial-time certified approximations, as for the production choice a=π α² with prescribed integer α. The native model is the same explicit extended Word RAM as the preceding note: O(p)-bit words, bounded-word arithmetic, multiplication/division, indexed memory and fixed-point rescaling shifts. Raw products fit before rescaling. This does not claim an implementation in the smaller tcslib ISA.

## 2. Exact run blocks and their q-LDU

The sets I_c={i:q_i−i=c} are integer intervals of length floor(1/θ) or ceil(1/θ). A cyclic relabeling gives S consecutive indices partitioned into g=T−S=Sθ complete runs. The proof is the interval identity

    I_c = Z intersect [(c−1/2)/θ,(c+1/2)/θ),
    I_(c+g)=I_c+S.

Within one run define D_i=exp(aβ_i²/θ). Its full, unperiodized principal block is

    B = D A D^(−1),        A_ij=q^((i−j)^2),
    q=exp(−aρ).

Expanding both exponents proves the equality; on the run β_i−β_j=θ(i−j).

Set F_0=1 and F_r=product_(k=1)^r(1−q^(2k)), and let F denote the diagonal matrix with entries F_i after translating the run origin to zero. Define the lower Toeplitz matrix H with coefficients

    h_r=(−q)^r/F_r,       r≥0.

The exact finite q-LDU identity from the preceding note gives

    A^(−1)=F^(−1) H^T F H F^(−1).

Since D commutes with F, the actual run inverse is therefore

    B^(−1)=F^(−1) J_+ F J_- F^(−1),
    J_-=D H D^(−1),       J_+=D H^T D^(−1).          (1)

The former algorithm formed D and D^(−1) separately. The construction below never does so.

## 3. A generating-function identity removes the slow tail

**Theorem 1.** In formal power series, and hence for every finite nilpotent shift Z,

    H(z) = (1+qz)^(−1) H(q²z).

**Proof.** The coefficient of z^r in (1+qz)H(z), for r≥1, is

    (−q)^r[1/F_r−1/F_(r−1)]
      = (−q)^r q^(2r)/F_r,

because F_r=F_(r−1)(1−q^(2r)). This equals the coefficient in H(q²z). The constant coefficients are both 1. At a finite shift the same coefficient identity holds after all powers at or above the run length vanish. ∎

Let Z be the lower coordinate shift on the run and M_-=q D Z D^(−1). Conjugating Theorem 1 gives

    J_-=(I+M_-)^(−1) R_-,
    R_-=D H(q²Z)D^(−1).                              (2)

For the upper orientation use the upper shift Z^T, producing J_+=(I+M_+)^(−1)R_+. These are exact finite identities, not asymptotic expansions.

## 4. The first factor is a stable scalar recurrence

**Theorem 2.** Every nonzero entry of M_- or M_+ has absolute value at most exp(−aθ). Applying (I+M_±)^(−1) is an explicit first-order forward or backward recurrence with O(length of the run) arithmetic work and

    ||(I+M_±)^(−1)||_∞ ≤ 1/[1−exp(−aθ)].              (3)

Its rounding and coefficient perturbations have only polynomial amplification in θ^(−1) in the fine-gap regime.

**Proof.** For adjacent positions in the same run,

    D_i/D_j = exp(a(i−j)(β_i+β_j)) ≤ exp(a).

Since q=exp(−aρ), multiplying by q gives exp(−aθ). The lower solve is y_i+μ_i y_(i−1)=z_i; compute in increasing order, with the analogous decreasing order for the upper solve. Expanding the recurrence gives a finite geometric majorant with ratio exp(−aθ), proving (3). With a local additive residual at most η in every recurrence equation, the same expansion bounds the output error by η/[1−exp(−aθ)]. An error in μ_i contributes at most its size times the current solution bound. Hence choosing coefficient and arithmetic errors smaller by a further polynomial in [1−exp(−aθ)]^(−1) proves the stated stability. In the fine-gap regime this quantity is polynomial in p. ∎

This step is not a dense triangular inverse and does not multiply the input by an exponentially large diagonal.

## 5. The residual has a short, uniformly summable tail

For r=|i−j| on a run, the residual coefficients in the relevant triangular orientation are

    (R_±)_ij = (−q³)^r D_i/[F_r D_j].

**Theorem 3.** If a≥1, then

    |(R_±)_ij| ≤ (3/2) exp(−a(3ρ−1)r).

Consequently truncating each residual to r≤L has row-sum error at most

    (3/2) exp(−a(3ρ−1)(L+1)) /
        [1−exp(−a(3ρ−1))].                           (4)

In the fine-gap regime, errors of size exp(−O(p)) times any prescribed inverse polynomial in p are obtained with L=O(p/log p).

**Proof.** Since q≤exp(−1)<1/2, the finite product estimate F_r≥2/3 applies. The run identity gives D_i/D_j≤exp(a r). Multiply that estimate by q^(3r) and sum the resulting geometric tail. Its exponent has a(3ρ−1)≥2a, which is Θ(log p) in the stated regime. Taking logarithms of (4) gives the length claim. ∎

## 6. Local recentering makes the residual an ordinary bounded convolution

**Theorem 4.** A length-L truncation of R_± can be applied with O(S log(L+2)) native work over all runs, after input-independent preparation, using additional magnitude and accuracy reserve

    O(aθL² + log p + log(S+1))

beyond the target precision and the input magnitude. In the fine-gap regime with L=O(p/log p), the term aθL² is O(1/log p).

**Proof.** Partition each run into consecutive blocks of length at most L. An output block of a triangular bandwidth-L operator meets at most two input blocks. For any such input/output rectangle, choose an anchor u in their common run, with every participating index within 2L of u. Write

    D_i = const × exp(2aβ_u(i−u)) × exp(aθ(i−u)²),

where β_u=θu−c lies in [−1/2,1/2]. The constant cancels from every ratio. Absorb the linear factor into the Toeplitz kernel. Its new rth coefficient is

    (−q³ exp(±2aβ_u))^r/F_r,

whose magnitude is at most (3/2)exp(−a(3ρ−1)r). The remaining diagonal values are between 1 and exp(4aθL²). Thus the rectangle is two bounded diagonal maps around one explicitly specified linear convolution. Zero padding and the radix-two FFT compute it in O(L log(L+2)) operations; the ordinary butterfly norm/error argument requires only O(log L) guard bits beyond the logarithms of the displayed magnitudes. No coordinate is padded in the final array: padding belongs only to a temporary one-dimensional convolution.

There are O(S/L) such rectangles, plus a bounded number of shorter endpoint rectangles per run. A shorter run may instead use one such rectangle; in the fine-gap regime full runs have length Θ(p²)≫L. Summing gives O(S log(L+2)). Every anchor, kernel transform and diagonal table is input independent and belongs to preparation. The identity uses local differences and β_u; it never evaluates the global exponent aβ_i²/θ. Finally aθL²=O((log p)p^(−2)(p/log p)²)=O(1/log p). ∎

The same proof covers both orientations. It uses the explicit convolution theorem of the preceding note, including twiddle preparation and fixed-point rescaling, not an assumed fast multiplication oracle.

## 7. A complete stable fine-gap run inverse

**Theorem 5.** In the fine-gap regime, the full block-diagonal inverse B^(−1) on all complete runs admits application cost O(S log p), after polynomial(S,p) input-independent preparation. It needs O(p) working bits when log(S+1)=O(p), target precision and input magnitude logarithms are O(p).

**Proof.** Apply (1), replacing each J_± by (2). Each orientation consists of one residual convolution from Theorems 3–4 and one first-order recurrence from Theorem 2. The three F diagonal maps have bounded norm because 2/3≤F_i≤1. The recurrence norms are polynomial in p, and the residual maps have constant row-sum bounds. Therefore all completed factors and their partial direct recurrence sums have polynomial range and error amplification. Allocate each truncation, coefficient and arithmetic error at the target tolerance divided by a sufficiently large polynomial in p and S. Its logarithmic cost is O(log p+log S), while the residual's local gauges have constant logarithmic range by Theorem 4. This proves the precision statement and the cost O(S log p). All raw products fit a sufficiently enlarged constant multiple of p bits before rescaling. ∎

This theorem removes the preceding sufficient requirement a/θ=O(p). Here a/θ is Θ(p² log p), yet it is never formed as a data multiplier.

## 8. The physical matrix remains diagonally dominant

**Theorem 6.** For the actual periodic matrix,

    ||N−I||_∞ ≤ exp(−2aθ)+5exp(−2a).                  (5)

In the fine-gap regime there is a constant c>0 such that, eventually, N and every principal/truncated matrix obtained by deleting its positive off-diagonal kernel terms have row diagonal-dominance margin at least

    δ=c aθ.

All their inverse norms are at most δ^(−1).

**Proof.** Put n_(i,h)=G_(i,i+h). For h=−1,+1, the exact nearest-integer gaps q_i−q_(i−1),q_(i+1)−q_i belong to {1,2}. Expanding the two exponent differences gives the upper bounds exp(−a(1+2θ−2β_i)) and exp(−a(1+2θ+2β_i)); if a gap is 2, its allowed β_i interval only strengthens that bound. Their sum is a convex function of β_i, so its maximum on [−1/2,1/2] is exp(−2aθ)+exp(−2a(1+θ)). For |h|≥2, the exponent difference is at least h²−|h|. Summing that Gaussian tail gives at most 4exp(−2a) when a≥1. This proves (5), including periodic diagonal aliases.

For large p, aθ≤1/2, so 1−exp(−2aθ)≥aθ. Also 5exp(−2a)≤(aθ)/2 because a≥4log p and θ≥c_1p^(−2). Thus the gap is at least aθ/2. Removing positive off-diagonal terms cannot decrease it. Principal restrictions have the same property. A matrix with row diagonal-dominance margin δ has inverse norm at most δ^(−1): at a coordinate where |x_i| is maximal, |(Ax)_i|≥δ||x||_∞. ∎

## 9. A boundary-only correction with a physical Schur system

Choose w≥1 with w=O(sqrt(p/a)) large enough to make

    4exp(−a w(w+1)) ≤ ε δ²/[4(X+1)],

where ε is the desired final inverse error and X bounds the input. Every run has length Θ(p²), so its first and last w coordinates are disjoint eventually. Keep the full within-run blocks and only cross-run kernel entries with displacement at most w; call the result A=B+E. Let J consist of those boundary coordinates, let V select them, and put K=VEV^T. Then E=V^T K V, and K couples only neighboring runs, cyclically.

**Theorem 7.** Define the block-diagonal matrix

    S_B=(V B^(−1) V^T)^(−1),

and the cyclic block-tridiagonal matrix S_A=S_B+K. The following is an exact A-solve:

    y=B^(−1)b,
    S_A z=S_B V y,
    x=B^(−1)(b−V^T K z).                             (6)

Both S_B and S_A are physical Schur complements and have row diagonal-dominance margin at least δ and bounded row sums. The inverse residual caused by replacing N by A is at most ε/2 under the displayed tail choice.

**Proof.** Eliminating all nonboundary coordinates inside each full run produces S_B, by the block-inverse identity. Because E is supported on J×J, exactly the same elimination on A adds K to that Schur complement. A scalar elimination step cannot decrease a strict row gap: the new gap is at least the old gap plus |a_ik| times the pivot row gap divided by |a_kk|. Its absolute row sum cannot increase. Thus the stated Schur properties follow from Theorem 6, with no near-identity assumption on the Woodbury matrix.

Multiplying the middle equation in (6) by V B^(−1)V^T gives (I+VB^(−1)V^T K)z=Vy. The last equation therefore has Vx=z. Multiplying it by A gives Ax=b−V^TKz+V^TKVx=b. The omitted Gaussian row tail is at most 4exp(−aw(w+1)). Since ||N^(−1)|| and ||A^(−1)|| are at most δ^(−1), the resolvent identity bounds their action difference by δ^(−2)||N−A||X, giving the stated allowance. ∎

## 10. Complete boundary solve and precision

**Theorem 8.** Preparing a bordered band elimination of S_A costs O(g w³) scalar work; applying its factors costs O(g w²) per right-hand side. Its rounding can be controlled with P+O(log(S+1)+log p+log(X+1)) bits.

**Proof.** Group the boundary coordinates by runs, each group having 2w coordinates. Retain the first group as a border and eliminate the other groups in cyclic order. At every step a pivot group is joined only to the next uneliminated group and the retained border. Its update frontier has O(w) coordinates, so each group costs O(w³) to prepare and writes O(w²) factor coefficients. A solve visits these coefficients once, including all border contributions, proving the work counts.

Simultaneous row/column reordering preserves strict row diagonal dominance. During elimination pivots remain at least δ and absolute row sums remain bounded by the original row sum. Thus every upper-factor entry is bounded, every multiplier is bounded by a polynomial in δ^(−1), and the total lower-factor row sum is at worst a polynomial in S and p. The inverse bounds for every relevant principal problem are at most δ^(−1). Consequently ||L^(−1)||≤||U||||S_A^(−1)|| and ||U^(−1)||≤||S_A^(−1)||||L|| are polynomial in S,p. The same statements hold on elimination prefixes. Expanding each computed row update literally expresses its factor residual as a sum of polynomially many local rounding errors, rather than a product of successive condition numbers. Solving with the computed factors adds another such residual. Choosing every local error at most the target tolerance divided by a sufficiently large polynomial in S,p,X therefore gives the asserted logarithmic reserve.

All coefficients are prepared from explicit finite matrices. To form S_B, one can apply the stable run inverse to its boundary basis vectors and invert the resulting 2w by 2w blocks; their inverse is the physical Schur block, whose norm is already bounded. Dense QR or exact finite elimination with sufficient rational precision supplies this input-independent finite operation. Its polynomial cost belongs to preparation, not to an unpriced oracle. ∎

## 11. Fine-gap inverse theorem

**Theorem 9.** Under the parameters of Section 1, the actual periodic N inverse can be applied to accuracy 2^(−P) with

    O(S log p + Sθ w²) = O(S log p)

native operations per right-hand side, after input-independent polynomial(S,p) preparation. It uses O(p)-bit words if log(S+1), P and log(X+1) are O(p).

**Proof.** Use Theorem 5 for both block-inverse applications in (6). The boundary product and solve cost O(gw²)=O(Sθw²), by Theorem 8. Gathering, scattering and S_B multiplication fit this count. Here w²=O(p/a), so θw²=O(1/(p log p)) in the fine-gap regime. Theorem 7 pays the truncation, and Theorems 5 and 8 pay all remaining local arithmetic and coefficient errors. Their range/precision reserves are O(p). ∎

If D=p^ε axes have log S_i=O(p^(1−ε)), for any fixed 0<ε<1, one preparation per axis is exp(o(p)). The full inverse tensor costs O(V D log p). The completed physical inverse norms are polynomial in p, so their product over D axes has logarithm O(D log p)=o(p); allocating these extra guard bits still uses O(p)-bit words. This is a sufficient constructive extension to near-linear axis counts. It does not require a simultaneous tensor fusion of the local solvers.

## 12. What this does and does not establish about κ

The new mechanisms are the exact recurrence/residual factorization of q-LDU and the physical boundary Schur recovery. They eliminate the large whole-run similarity and extend the actual inverse algorithm to fine prime gaps at logarithmic Gaussian width.

Combining this with an actual unfused forward adapter of O(S log p) gives total Gaussian adapter work O(V d log p). An actual native provider saving q, inserted into the existing main transform, gives main work O(V p d^(−q)). With d=p^ε and V=Θ(n/p), these two terms admit every κ below min(εq,1−ε), maximized symbolically at ε=1/(1+q), giving every κ<q/(1+q). This is a completed cost substitution once the named provider and the other retained caller terms really meet their contracts; it does not assume a provider with a desired q.

The mature retained fused assembly already approaches its admitted provider q itself. Therefore the new unfused transfer is a simpler sufficient route, but it does not raise the current κ using the same provider. In particular a complex-only quotient headline cannot be inserted for q while its coupled endpoint/controller obligations remain unpaid. A genuinely higher κ still needs a stronger admitted provider or another change in the main recurrence. No numerical κ improvement is asserted by this inverse note.
