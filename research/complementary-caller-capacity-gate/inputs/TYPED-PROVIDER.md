# Typed Gaussian providers, subspace gauges and sector-multiplexed queries

Dugongue, with substantial OpenAI Codex assistance. Informal mathematics based only on local source and proof-tree scans. No numerical experiment, solver, web search or Lean check was used. The constructions below have complete all-input operator proofs on their stated domains; they do not assert an unproved profitable provider or a larger numerical κ.

## Sources and actual starting contract

The actual local sources are `research/native-dual-suppliers/HETEROGENEOUS-CONTROLLER.md`, `FREE-ENDPOINT-GAUGES.md`, `DUAL-PROVIDER.md` and `ROUND3-IMPROVEMENT.md`; the scalar event definition in `research/kappa-rebuild/bit/complex_controller_factor.py` was read as text and was not executed. The preceding mathematical continuation supplies `boundary.md` and `consumer.md`. The linked symplectic balanced-coevaluation and mode-support notes motivate reciprocal-dual and invariant-subspace bookkeeping; no fresh formal verification is inferred from those sources.

The admitted B and C local words have 112 independent main pairs, 408 independent helper fields, and respectively 56 A plus 56 B or C ports. Their exact main types are

    A = D [[1,0],[Q^(-1),1]],
    B = D [[1,0],[1,Q]],
    C = D [[Q,0],[1,1]],

where D acts on seven fresh axes and Q on the common central axis. Helpers and paid Gaussian jobs retain their individually stated profiles. Arbitrary main-pair permutations place the exceptional ports but do not identify helper inputs. Backward calls use the actual inverse-transpose endpoints with their even-power monomial corrections.

Credit Cao Yifan for the retained native round-three word, DaysSky for the quotient construction, Cinna Davis and the controller lineage, Nick Petalas and Ryanson Jonathan for endpoint analysis, Dugongue for transported/repaired interfaces, zxv and Jacob Alan Sussman for compiler foundations, and all retained Gaussian/Clifford/source08 contributors. Ordinary rank factorization, projector decomposition, nullity and elementary matrix identities are classical. The new applications here are the precisely stated fusion, projection-gauge and sector-query interfaces.

## T1. Complete exceptional-port extraction and two-call fusion

Let S_y(t)=[[1,0],[t,1]], and suppress the common commuting D factor for a moment.

**Theorem.** Exceptional B and C ports have the exact ordinary-boundary extractions

    S_y(−1) B = D diag(1,Q),
    C S_y(−1) = D diag(Q,1).

For two calls on the same pair, with arbitrary commuting fresh factors D_1,D_2,

    C_2 B_1 = D_2 D_1 Q S_y(2Q^(-1)),
    S_y(−1) B_2 C_1 = D_2 D_1 Q S_y(Q^(-1)).

**Proof.** In the first identity subtract the first output row of B from its second. In the second replace the first input contribution in C's second row by its difference with the second input. Both are the stated elementary shear and give the displayed diagonals on arbitrary independent inputs.

For the two-call products multiply the two explicit matrices:

    [[Q,0],[1,1]] [[1,0],[1,Q]] = [[Q,0],[2,Q]],
    [[1,0],[1,Q]] [[Q,0],[1,1]] = [[Q,0],[1+Q,Q]].

Factor out the common Q; in the second product the remaining shear is S_y(1+Q^(-1)), whose ordinary S_y(1) factor is removed on the left. Restore the commuting D factors. ∎

The direct B extraction is inherited predecessor work, including the PR4660 extraction discussion; it is not claimed anew. The combined formulas supply explicit homogeneous-shear fusion rules. The ordinary A-A pair is D_2D_1 S_y(2Q^(-1)), and scalar diagonal conjugation normalizes its factor 2 without Gaussian work.

The common Q in the exceptional two-call formula is the existing central coordinate. Repeating the construction produces powers of that same Q, whose even powers are ordinary monomials. It does not create one fresh Gaussian rank per fused block. Likewise the free extraction on 56 ports does not diagonalize the other 56 A ports. A full caller must retain these exact facts when adding targets and costs.

## T2. A Gaussian gauge on an ordinary role subspace

Work over a field K of characteristic not 2 and let V be the data space. A scalar role projector P is an idempotent n by n matrix over K. It acts only on the n role indices, and therefore commutes with a common Gaussian Q on V. Define

    G_P(Q) = I + (Q−I)P.

**Theorem.** G_P(Q) is invertible, with inverse G_P(Q^(-1)). It is ordinary-conjugate to Q on rank(P) role fields and identity on the other fields. It can be applied with rank(P) charged Gaussian jobs and explicit ordinary boundaries.

**Proof.** The role space is the direct sum im(P) ⊕ ker(P): x=Px+(I−P)x, and the intersection is zero. Choose a basis in each summand and combine them into an ordinary scalar basis matrix U. In that basis P is diag(I_r,0), so G_P(Q) is diag(QI_r,I). The asserted inverse and construction follow. Alternatively, multiply the two displayed polynomial expressions in P and use P²=P. ∎

This is a changed gauge representation, not a claim that Q on an arbitrary role subspace is free. The basis maps and all Gaussian requests are specified. For a fixed finite template the ordinary maps have fixed coefficient data and actual finite field-pass cost.

## T3. Coordinate-free rank tariff for an ordinary boundary

Let M be an invertible scalar role matrix, with an input projector P and output projector R. Put

    F = G_R(Q) M G_P(Q)^(-1),
    E = R M − M P.

**Theorem.** There is an explicit all-input boundary construction for F using rank(E) charged Q or Q^(-1) jobs, ordinary linear operations and O(n) owned field buffers returned to zero. If E=0, F=M and no Gaussian correction is needed.

**Proof.** Choose ordinary bases diagonalizing P on inputs and R on outputs. In those bases write M in four blocks M_00,M_01,M_10,M_11, according to the zero/one projector sectors. The physical boundary has ordinary diagonal blocks and crossed blocks M_01Q^(-1),M_10Q. The transformed E has crossed blocks −M_01 and M_10 and zero diagonal blocks; their input and output supports are disjoint, so

    rank(E)=rank(M_01)+rank(M_10).

Rank-factor each crossed scalar block. Form its inner scalar combinations in owned temporary fields from one unchanged input snapshot, query each combination once, and distribute through the outer rank factor. Accumulate both direct and crossed terms in an owned output bank, swap it into the main bank after the last read, and clear the old bank and temporaries. This produces exactly F on every independent input and preserves unrelated fields. All Gaussian calls are counted. If E=0 the intertwining identity RM=MP gives G_R M=M G_P, hence F=M. ∎

This extends the row-bit boundary tariff to arbitrary scalar role subspaces. It does not extend it to an arbitrary matrix whose entries are noncommuting address operators.

## T4. Composition and reciprocal-dual compatibility

**Theorem.** For scalar M_1,M_2 and projectors P_0,P_1,P_2, define

    E_1=P_1M_1−M_1P_0,
    E_2=P_2M_2−M_2P_1.

Then the whole-boundary defect obeys

    P_2M_2M_1−M_2M_1P_0 = E_2M_1+M_2E_1,

so its rank is at most rank(E_1)+rank(E_2). For invertible M, the reciprocal-dual defect is

    R^T M^(-T) − M^(-T) P^T
      = M^(-T) (RM−MP)^T M^(-T),

and has exactly the same rank.

**Proof.** Expand the first identity; the two terms containing M_2P_1M_1 cancel. Rank is subadditive and cannot increase under multiplication. For the second identity transpose RM−MP and multiply by M^(-T) on both sides. Invertible left/right factors preserve rank. The dual gauge is G_(P^T)(Q^(-T)), so T3 applies to the actual reciprocal-dual operator at that same tariff. ∎

The global defect can have lower rank than the sum of local defects, including exact cancellation. This justifies compressing a completed ordinary boundary as one matrix rather than pricing a chosen ADD factorization as though its separate corrections could never share.

## T5. Zero-correction endpoint gauges inside actual multiplicity spaces

Assume a complete reference word satisfies

    L M R_0 = T,

where L and R_0 are ordinary invertible scalar boundaries and T is the actual independent-output operator. Assume each target block of T commutes with the common Q. Suppose the internal entrance and exit gauges are G_A(Q) and G_B(Q), and there is a projector P such that

    R_0^(-1) A R_0 = P = L B L^(-1),
    PT=TP.

**Theorem.** The gauged interior has the exact same independent target under the same ordinary boundary maps:

    L G_B(Q) M G_A(Q)^(-1) R_0 = T.

No Gaussian correction at those two boundaries is needed.

**Proof.** The first projector identity gives G_A(Q)^(-1)R_0=R_0G_P(Q)^(-1). The second gives L G_B(Q)=G_P(Q)L. Therefore the left side is G_P(Q) T G_P(Q)^(-1). Since P commutes with T and the actual target blocks commute with the common Q, this equals T. All input fields remain arbitrary and independent because the complete endpoint is exactly the original T. ∎

For a scalar projector and T=diag(T_i), its commutator has entries P_ij(T_j−T_i). Thus a sufficient source of such projectors is an actual multiplicity block where the operators T_i are exactly identical. Equal Gaussian rank alone is not equality of these operators. Address-dependent normalizers must be included explicitly before applying the scalar statement.

The theorem is a constructive admission criterion. This note has not supplied A,B satisfying it for a profitable complementary-provider schedule, so no free boundary in the current provider is asserted merely from the existence of this criterion.

## T6. Sector-multiplexed Gaussian queries

Suppose Q²=J and J is an ordinary involution, J²=I. Define E_+=(I+J)/2 and E_-=(I−J)/2. These are complementary ordinary projectors commuting with Q. Let A_+,A_- be scalar role matrices, with ranks r_+,r_-, and let

    A=A_+E_+ + A_-E_-.

**Theorem.** The vector contribution A Q x can be computed using

    max(r_+,r_-)

charged Gaussian jobs, explicit ordinary operations and cleared owned storage.

**Proof.** Choose rank factorizations A_σ=U_σV_σ. Pad each inner dimension with zero rows/columns to r=max(r_+,r_-). Put

    U=U_+E_+ +U_-E_-,
    V=V_+E_+ +V_-E_-.

Scalar role matrices commute with the sector projectors. Since E_+E_-=0 and E_++E_-=I, UV=A. Form the r temporary fields Vx, apply Q once to each, and spread by U. Because Q commutes with all entries of U,V, the result is A Q x. Each temporary packs disjoint projected components, whose dimensions sum to the original data-space dimension; it does not pack two independent full data fields into one without accounting for information. Clear the owned storage after accumulation. ∎

For the actual lifted central Gaussian Q_f, Q_f² is the explicit translation that flips the selected bit in every digit column. E_± are therefore finite combinations of two ordinary monomial maps, uniformly in the lift width. The theorem has a concrete ordinary implementation and does not require a width-dependent spectral decomposition.

## T7. A complete strict query-sharing example

**Theorem.** Let Q be unitary with Q²=J as above. The invertible two-field map

    x ↦ x + (1/4)(Q+Q^(-1))x,
    y ↦ y + (1/4)(Q−Q^(-1))y

has an implementation using one Q job, plus ordinary operations and cleared owned storage. Its inverse norm is at most 2 in Euclidean norm.

**Proof.** Since Q^(-1)=QJ,

    Q+Q^(-1)=2QE_+,
    Q−Q^(-1)=2QE_-.

Form z=E_+x+E_-y in an owned temporary, query Qz once, and return x+(1/2)E_+Qz and y+(1/2)E_-Qz. Orthogonality of the complementary sectors proves the two displayed outputs. The block-diagonal perturbation of identity has norm at most 1/2, so its Neumann inverse has norm at most 2. This norm argument establishes invertibility, not an unpriced inverse algorithm. The one-query forward construction is already explicit. ∎

The literal four-term implementation uses four Q or Q^(-1) calls; merely factoring the two odd expressions separately uses two. Sector multiplexing reduces that explicit tariff to one while preserving the full stated all-input map. These outputs are not declared canonical independent Gaussian targets. To improve κ this pattern must occur inside a completed provider whose original independent endpoint remains unchanged.

## Exact contribution and κ status

T1 supplies exact fusion normal forms for the actual typed B/C operators. T2–T5 provide role-subspace gauge admission and complete boundary tariffs, including duals. T6–T7 give a concrete way to share Gaussian queries across ordinary involution sectors, with a strict full-map example.

A higher κ still requires a particular complete supplier whose actual paid profile is decreased by one of these replacements while preserving its independent target operators and uniform compiler premises. No such profitable B/C instance was established in this note. The constructions are positive, fully stated tools for that task; they are not a claim that the complex-only quotient headline has already satisfied the missing controller contract.

