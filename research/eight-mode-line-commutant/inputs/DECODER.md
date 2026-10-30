# One rank-two query closes the full-rank coded Gaussian terminal

Dugongue, with substantial OpenAI Codex assistance. These are informal mathematical proofs. No numerical experiment, solver, Lean run or external search was used.

## Starting contract and notation

Fix an integer N > 1 and a positive digit width f. An address is an f-tuple of vectors in F₂^N. For a binary direction v, let X_v translate one address column by v. Write

    a = (1+i)/2,   b = (1-i)/2,   C_v = a I + b X_v.

The superscript [f] means applying the displayed one-column operator separately in all f columns, that is its tensor lift. Thus C_v^[f] is not a I + b times the simultaneous translation on every column. Put

    Q₀ = C_e₀^[f],
    D = (C_e₁ ... C_e_(N−1))^[f],
    R = Q₀D,
    χ = e₀ + ... + e_(N−1),   Qχ = C_χ^[f].

A rank-r Gaussian child H_r acts on r independent binary directions in every address column, with identity on all other address coordinates. An explicit invertible binary coordinate change is an ordinary address permutation; conjugating a canonical child by it does not add Gaussian requests. Its real finite nonrecursive work is retained.

Let P be an explicitly ordinary invertible finite code on a bank of owner fields. Assume it commutes, separately for each column j, with translation X_(χ,j) on every field. The two actual terminal operators to be decoded are

    W₋ = Q₀^(-1) P D,       W₊ = P D Q₀.             (1)

Equation (1) is a hypothesis about the literal physical code, not a statement obtained by identifying its logical coordinates. The source application below establishes it from retained whole-K/E interfaces. This note never assumes that P commutes with Q₀ or D.

## D1. Exact translation square and inherited column symmetry

**Lemma.** C_v² = X_v, with no scalar phase. If a one-column real monomial L commutes exactly with the full local Gaussian R_s on a set of s axes, then L commutes with translation by that local set's characteristic vector. When L is lifted columnwise and fixes all other axes, it commutes with X_(χ,j) for every global column j. Finite scalar mixing between owner fields preserves this property.

**Proof.** Since X_v² = I, expand C_v². The identity coefficient is a²+b² = 0 and the translation coefficient is 2ab = 1. The coordinate Gaussians commute, so R_s² is the product of the translations on the local axes, namely translation by their sum. An L commuting exactly with R_s commutes with its square. It fixes each axis outside its local set, so it also commutes with translation by the sum of the remaining global axes. Multiplication gives the desired global translation. A columnwise lift gives this argument independently in every column. Scalar owner coefficients commute with a common address translation, and finite products, sums and inverses of commuting operators retain that commutation. ∎

Commuting only with R^[f]² would give a weaker simultaneous-column statement and would not justify the next lemma. The columnwise premise above is essential.

## D2. A second Gaussian direction in the code's commutant

**Lemma.** Under the starting contract, P Qχ = Qχ P.

**Proof.** In column j, C_(χ,j) = a I + b X_(χ,j). The hypothesized commutation with the translation therefore gives commutation with this one-column Gaussian. Multiply those identities over all f columns. ∎

This is a constructive commutant element. It does not move the source's distinguished central line to the characteristic vector, which would be an invalid shortcut for the orthogonal normalizers in question.

## D3. The full-rank negative decoder

**Theorem.** Apply, in chronological order, Qχ Q₀ and then the ordinary reversed inverse code P^(-1) to the negative terminal W₋. The result is exactly Qχ D. It is an ordinary monomial conjugate of the full rank-N Gaussian R, with no phase ambiguity. The extra paid Gaussian tariff is one H₂ per negative owner field. The positive terminal requires only the ordinary decoder P^(-1) and returns R.

**Proof.** Operator products act right to left. Lemma D2 gives

    P^(-1)(Qχ Q₀)(Q₀^(-1) P D)
      = P^(-1) Qχ P D
      = Qχ D.                                      (2)

Every equality retains its scalar phase. To implement the first factor in (2) as a single H₂, use the binary matrix A with ordered columns

    e₀, χ, e₂, ..., e_(N−1).

It is invertible: the e₁ coordinate forces the coefficient of χ to vanish in any dependence, and the remaining coordinate columns are independent. For the ordinary permutation Π_A of address labels, direct action on a basis vector gives

    Π_A X_v Π_A^(-1) = X_(Av),
    Π_A C_v Π_A^(-1) = C_(Av).

Hence Qχ Q₀ = Π_A (C_e₀ C_e₁)^[f] Π_A^(-1), a single canonical rank-2 child between explicit ordinary permutations.

Likewise the binary matrix B with columns χ,e₁,...,e_(N−1) is invertible, since the e₀ coordinate first forces the coefficient of χ to vanish. The same conjugation identity gives

    Qχ D = Π_B R Π_B^(-1).                          (3)

After the decoder in (2), apply Π_B^(-1) on outputs and Π_B on the corresponding independent original input before executing (1). The complete operator is then exactly R, not merely an output with the same Gaussian rank. Applying the input permutation changes neither the independence nor the arbitrary values allowed for original inputs. The positive terminal satisfies P^(-1)W₊ = DQ₀ = R. The two banks are independent, so the input/output normalizers on the negative bank do not change the positive bank. ∎

Both coordinate permutations have elementary descriptions. A maps y₁=x₁, y₀=x₀+x₁ and y_j=x_j+x₁ for j≥2; B maps y₀=x₀ and y_j=x_j+x₀ for j>0. They operate in each digit column. This gives literal finite XOR-based permutations, rather than an unspecified linear-algebra oracle.

## D4. Exact reciprocal orientations and owned storage

**Theorem.** The decoded complete construction admits an inverse and a reciprocal transpose construction with the same Gaussian ranks. All original fields remain independent. Ordinary temporary storage may start dirty, is initialized before use and can be zero on return. Unrelated fields are preserved.

**Proof.** Reverse the complete word of abstract invertible main factors and use their supplied inverse routines. In particular, use the explicit ordinary P/P^(-1) code; do not try to reverse scratch initialization, COPY or CLEAR instructions, which need not be invertible. The adjoint construction below instead transposes the versioned linear straight-line DAG. The inverse of a Gaussian C_v is X_v C_v, since C_v² = X_v and C_v⁴ = I; thus its inverse has the same paid rank with an explicit ordinary translation. Coordinate normalizers invert as address permutations. This gives the literal inverse, including its ordinary coefficients.

For a transpose, reverse the linear straight-line computation into separate adjoint field buffers. Scalar accumulation transposes by the same coefficient, a monomial address map by its transposed permutation and phase, and each symmetric canonical Gaussian by itself. The conjugated-child boundary permutations are transposed in reversed order. Seed output adjoints with arbitrary dual inputs, accumulate the input adjoints, and clear working buffers after their final reads. Applying this to the inverse gives the reciprocal transpose. Each child is used once with the same rank.

For a forward implementation, compute any ordinary scalar combinations from source snapshots into initialized owned buffers, accumulate the destination and clear the no-longer-needed snapshots. Initialization of owned scratch is allowed by the starting source contract; no independent productive input is initialized or erased. The finite inverse and transpose constructions retain this distinction. ∎

This theorem uses the usual finite-field-array linear algorithm model. It does not grant the unpriced inverse of an unspecified dense address operator: P and both permutation normalizers have already been supplied as ordinary words.

## D5. Finite precision at every positive width

**Theorem.** For a fixed finite provider template satisfying the contract, the decoder has a finite all-width error envelope. If its ordinary coefficients have effective O(p)-bit descriptions, an O(p)-bit guard budget suffices when the logarithm of the field volume, the logarithm of the admitted input-magnitude envelope, and requested output precision are O(p). The square root of the field volume must be charged when a coordinate-rounding guarantee is derived from a Euclidean field-norm bound.

**Proof.** Let there be M rounded primitive sites and at most V scalar coordinates at any such site. Let K bound every relevant suffix operator norm, including the actual finite ordinary inverse P^(-1). The exact monomial permutations and Gaussian children have Euclidean norm one; finite ordinary coefficients supply a finite K independent of lift width when they are fixed scalar combinations of finitely many orthogonal monomials. If coordinate errors at a site are at most 2^(-B), the field Euclidean error is at most √V 2^(-B). By the telescoping perturbation identity and the triangle inequality, the final error is at most

    K M √V 2^(-B).

Thus B ≥ P_target + log₂(KM√V) + 2 is sufficient for output error below 2^(-P_target). This retains the field-volume term and includes all sites at which an actual implementation rounds. If the whole provider has O(p) sites or a polynomial-size width-dependent schedule, its log M is also O(p). The stated hypotheses therefore give B = O(p). Coefficient approximation errors are included as extra sites with their actual input magnitude bounds. The stated input-magnitude hypothesis and the fixed finite coefficient/norm envelope add O(p) guard bits for their scaling; absent that hypothesis, the extra input-range bits must be charged separately. No exact division is free. ∎

This is an informal sufficient precision theorem under explicit parameter-description hypotheses, not an emitted native implementation or an independent compiler acceptance certificate.

## D6. Application to the retained whole-K/E word

**Theorem.** The ordinary physical codes E_i of the retained whole-K/E construction satisfy the column symmetry used in D1. For its three fresh-stage endpoints (1), the two full-rank negative repairs previously billed as 2 H₁ per owner may be replaced by H₂, with unchanged full independent target ranks. In the reconstructed ambient-18 provider of `whole-k.md`, the complete profile becomes

    targets: 2v H₅₂,
    paid: 3v(2 H₈ + 2 H₉) + 3h H₁₈ + v H₂,
    v = 112³,   h = 20480.                          (4)

**Proof.** In each stage, the physical code is an ordinary scalar owner matrix conjugated by the diagonal bank of actual real monomial normalizers L_i. Those normalizers commute exactly with the complete Gaussian on that stage's central-plus-fresh axes, separately at one-column level; the source's anchor identities retain the phase. Lemma D1 therefore applies to each L_i, to its inverse, and to the scalar owner recodings, including their rational E corrections. A stage fixes all fresh axes belonging to other stages. Consequently each stage code commutes with the global characteristic translation in every column. The chronological product P = E₃ E₂^(-1) E₁ and its ordinary inverse have the same property.

Here is also the literal three-stage derivation. Put H₀ = diag(I,Q₀), let L = [[1,0],[1,1]] and U = [[1,−1],[0,1]], and write A_s = E_s^(±1) D_s for the appropriate forward or backward stage. The corrected source words are H₀^(-1) diag(A_s,A_s) L H₀ and H₀^(-1) diag(A_s,A_s) U H₀. The three-stage product is H₀^(-1) diag(A₃A₂A₁,A₃A₂A₁) J H₀, with J = LUL = [[0,−1],[1,0]]. The final ordinary J^(-1) makes its two blocks Q₀^(-1) A and A Q₀. Freshness means D_s commutes with every other-stage E_t, hence A = E₃ E₂^(-1) E₁ D₁₂₃ = P D₁₂₃. This proves (1) in the actual coordinates, with genuinely ordinary P; no hidden Q₀^(-1) E Q₀ recoder remains inside P. D3 closes these terminals. In the ambient-18 reconstruction each stage contributes 17 fresh noncentral axes. Three stages plus the common central axis give N = 52. There are v independent negative fields, so the new decoder costs v H₂. The three local calls retain exactly the K6 paid profile in `whole-k.md`; this proves (4). The source field ownership and D4 preserve all independent targets. ∎

The same replacement applies to the original ambient-25 construction at its own unchanged full output rank 73. It must not be combined with the compressed local bill while retaining rank 73 targets.

## D7. The exact improvement and its scope

**Corollary.** For every concave pricing exponent 0 < t < 1, replacing the two rank-one repairs by the full-rank decoder of D3 improves target-minus-paid power moment by

    v (2 − 2^t) > 0.                               (5)

It does not improve the complete κ supplied by the explicit invoice (4).

**Proof.** The independent target profile is unchanged, and the paid repair changes from 2v to v 2^t, proving (5). The target rank mass in (4) is 104v. Its paid mass is 102v + 54h + 2v = 104v + 54h. Every paid rank is at most 18 and is strictly below 52. For 0 < t ≤ 1, each paid rank r obeys r^t ≥ 52^(t−1)r. Summing shows its paid moment exceeds the target moment 2v 52^t, since h > 0. Thus this supplied complete construction is not a profitable supplier for that exponent range. ∎

There is a further important comparison. The older single-H₁ repair can retain only rank N−1, whereas D3 retains rank N. For N > 2 and 0 < t < 1,

    [N^t − 2^t] − [(N−1)^t − 1]
      = N^t − (N−1)^t − (2^t − 1) < 0,

by strict decrease of the increments of x^t. Thus the new full-rank interface is cheaper than the previous full-rank repair, but the rank-dropping option still has the larger concave moment considered in isolation. This note does not count the full-rank closure as an already funded κ improvement.

## Predecessor credit and local proof-tree use

The starting terminal derivation and ordinary E codes come from `research/odd-e8-whole-k-native/PROOF.md`, `research/odd-e8-lowrank-e-native/E-PROOF.md`, and the retained `research/central-q-decoder/PROOF.md` and `E-COMPOSITION.md`. Credit THU New Media Research Center/PR5464, Ali Romman/PR5439, Dugongue, Dillon Amburgey, Cinna Davis, Ryanson Jonathan, Cao Yifan, Jacob Alan Sussman, Chris R/Clear1nsight, zxv and all retained native, Clifford, compiler and analytic contributors. These source relationships were read locally; this is not a claim of exhaustive literature priority.

The linked symplectic/TI sources `Mathproof/SymplecticTI.lean` and `Mathproof/LibraryBridges/Claude/TISpTransporterFibers.lean` informed the use of an explicit intertwiner and actual operator stabilizer, rather than only a scalar invariant or a rank match. Their existence does not formalize this decoder. The binary translation and elementary Gaussian identities are classical; the contribution here is this explicit full-rank terminal application and its honest complete invoice.
