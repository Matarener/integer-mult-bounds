# Recode a Gaussian reader using an arbitrary borrowed centre

Dugongue, with substantial OpenAI Codex assistance. These are informal constructive proofs. No numerical evaluation, executable mathematics, source replay, Lean check or web search was used.

## 1. A four-shear implementation with no extra bank

Let A be the data-field module and Z a k-field centre module over the admitted coefficient field. All fields are complete functions on the same address domain, including the actual ROW and spectators. Fix admitted ordinary maps J:Z→A and D₀,D₁:A→Z with

    D₀J = I_Z = D₁J.

Define Δ = D₁−D₀. Then ΔJ = 0. All maps below must be emitted in their actual common physical frame, or through already supplied physical adapters; a scalar formula is not a licence to identify differently routed frames.

### Theorem 1. Reversible recoding with an arbitrary centre baseline

For arbitrary independent data a and centre z, execute the four chronological ordinary shears

    z ← z + Δa,
    a ← a + Jz,
    z ← z − Δa,       using the UPDATED a,
    a ← a − Jz.       using the UPDATED z

The exact endpoint is

    (a,z) ↦ ((I_A+JΔ)a, z).                           (1)

The word uses two gathers by Δ and two scatters by J. It introduces no additional field bank, Gaussian request, COPY, CLEAR or initialization. It restores the arbitrary borrowed centre input, not only a centre initially zero.

**Proof.** Let a₀,z₀ be the original values. After the first two shears,

    z₁ = z₀ + Δa₀,
    a₁ = (I+JΔ)a₀ + Jz₀.

Since ΔJ=0, Δa₁=Δa₀. The third shear therefore gives z₂=z₀. The fourth gives a₂=(I+JΔ)a₀. This proves every field of (1) on arbitrary inputs. ∎

### Theorem 2. Inverse and actual reader identities

Put K=I+JΔ. Then

    K⁻¹=I−JΔ,      KJ=J,      D₀K=D₁.

Changing the signs of the two data shears in Theorem 1 implements diag(K⁻¹,I_Z) and again restores every arbitrary centre baseline. For the lossless section swap

    S(J,D)(a,z)=((I−JD)a+Jz, Da),

one has the complete operator identity

    S(J,D₁) = diag(K⁻¹,I_Z) S(J,D₀) diag(K,I_Z).      (2)

Both outside recodings in (2) can use the same existing centre bank, first at its original value and then at its post-swap value. Neither recoding assumes that value to be zero.

**Proof.** (JΔ)²=J(ΔJ)Δ=0, proving the inverse. The two reader identities follow by direct multiplication. For the inverse word, after z₁=z₀+Δa₀ and a₁=a₀−Jz₁, the updated gather still gives Δa₁=Δa₀; the last two shears restore z₀ and give (I−JΔ)a₀.

To verify (2), apply its right-hand side to arbitrary a,z. The centre component is D₀Ka=D₁a. The data component is

    K⁻¹[(I−JD₀)Ka+Jz]
      = a−JD₁a+Jz,

using K⁻¹J=J. This is exactly S(J,D₁). Each K word preserves the centre state supplied to it, even after the section swap has changed that state. ∎

This is a constructive cost refinement of the reader conjugacy: the two recodings need eight explicit ordinary shears and no new scratch bank, rather than a new dense-matrix storage implementation. Translation views, coefficients and field passes are paid ordinary work.

## 2. The actual rank-30 interface

Use the retained rank-30 response E=I+UV and its fixed-reader translation inverse. In the source's notation,

    Q⁴=I,   B=VU,   T=VQ²U,
    J=Q²U,  D₀=T⁻¹V,  D₁=B⁻¹VQ².                  (3)

The actual Q² operations are simultaneous Pauli translations. The retained source supplies the finite all-width inverse T⁻¹ and the scalar inverse B⁻¹. They are not assumed as unknown gadgets. The direct calculations

    D₀J = T⁻¹VQ²U = I,
    D₁J = B⁻¹VQ⁴U = I

verify the hypotheses. Thus Theorems 1–2 give an explicit conversion of that fixed-reader section to the moving-reader section, using its existing thirty-field centre and no additional Gaussian requests or arrays.

Under the source's actual admitted common advance A=FQ⁻¹ on data and F on the centre, where F has the stated commutation/typing properties, the corrected section transports to

    J_out=QU,       D_out=B⁻¹VQ⁻¹.

The old fixed reader transported to T⁻¹VQ. Those expressions are different. Equations (2)–(3) supply an actual input recoding that corrects the difference; they do not simply rename the old reader.

The separate sixteen-row joined D25 services are not these thirty-row sections. Nor does a reviewed output conjugation through completed F_t supply an input conjugation through F_(t−1) on newly introduced fresh directions. This construction is at the source's admitted common-frame section interface. It does not claim an otherwise unproved interstage physical adapter.

## 3. Uniform finite translation kernels

The fact that the recoding is ordinary at every positive width needs more than a one-column numerical coincidence. Here is a constructive sufficient theorem for the actual operator class.

Let H be a fixed subgroup of F₂ⁿ. For v∈H let X_v translate a one-column binary address by v. At width f, let X_v^[f] translate every one of the f columns by v simultaneously. This is the tensor lift of the translation, not a sum of per-column operations. These satisfy

    X_u^[f] X_v^[f] = X_(u+v)^[f],    (X_v^[f])²=I

for every positive f. A finite matrix kernel has the form

    A_f = Σ_(v∈H) A_v X_v^[f],

with fixed scalar matrices A_v applied once per field, outside the tensor product. Composition is finite convolution of those coefficient lists; its formula is independent of f.

### Theorem 3. An explicit all-width inverse criterion

Suppose the coefficient field has characteristic different from two. For every character χ:H→{1,−1}, define the finite scalar matrix

    A(χ)=Σ_v χ(v)A_v.

If every A(χ) is invertible, then a single fixed finite kernel supplies A_f⁻¹ for every positive f. Explicitly,

    B_v = |H|⁻¹ Σ_χ χ(v) A(χ)⁻¹,
    A_f⁻¹ = Σ_v B_v X_v^[f].                         (4)

Conversely, if the one-column representation contains every character of H and A_1 is invertible, every A(χ) is invertible. The regular translation action has that property.

**Proof.** The character idempotents

    e_χ,f = |H|⁻¹ Σ_v χ(v) X_v^[f]

are mutually orthogonal, sum to identity and diagonalize every translation. These facts follow by character orthogonality in the finite group H and the displayed multiplication law, equally at every f. Thus A_f=Σ_χ A(χ)e_χ,f. Multiplying by Σ_χ A(χ)⁻¹e_χ,f gives identity in both orders. Expanding that product gives (4).

If every character occurs in the one-column representation, a singular A(χ) gives a nonzero vector in the corresponding kernel of A_1. Therefore invertibility of A_1 implies all the stated finite scalar inverses. They can be specified by adjugate and nonzero determinant, so the construction does not invoke a width-dependent inverse oracle. ∎

The theorem constructs the inverse coefficients without performing any inversion in this research session. For (3), the retained source's stronger explicit T⁻¹ already supplies its particular finite coefficient and prime-avoidance information. The general theorem does not assert that an arbitrary kernel has those same denominators.

Because J,D₀,D₁ are actual finite translation kernels at the admitted section cut, Δ and K use fixed lists independent of f. Theorem 1 can lower each gather or scatter coefficient by coefficient into the corresponding ordinary translations and scalar ADDs. No tensor expansion of Q, or exponential enumeration of its per-column Gaussian choices, occurs.

## 4. Precision and nonrecursive cost

For a matrix translation kernel C=Σ_v C_v X_v^[f], define c = max_i Σ_v,j |(C_v)_ij|, summing absolute coefficients before any cancellation between translations. Every translation is a coordinate permutation, so

    ||Cw||_∞ ≤ c ||w||_∞

at every width, without a field-volume multiplier. Let j and d be such bounds for J and Δ. A shear by J has joint maximum-field norm at most 1+j, and a shear by Δ at most 1+d. Thus every prefix and suffix of the four-shear recoding has norm at most

    (1+j)²(1+d)².

These bounds apply at the mathematical shear boundaries. For the two K words and their intervening source section, multiply them by the actual source interval bounds. A coefficient-by-coefficient implementation, fixed-odd arithmetic routine or recursive primitive must additionally supply its own interior prefix and suffix bounds. Once those have actually been supplied, M rounding sites with coordinate error at most ε contribute at most M times the resulting full suffix bound times ε. Fixed rational coefficient approximation adds its explicitly bounded input-range error. Opcode-boundary bounds alone are not substituted for primitive-interior bounds. The borrowed centre's numerical error is charged along with the data error; it is not cleared or presumed zero.

Coefficient data, fixed-odd multiplication/division scans, simultaneous translations, payload movement and all coefficient passes within the four shears must be included in the real ordinary allowance. The absence of a new Gaussian child does not mean those operations cost no time. This note does not reuse an old finite compiler threshold after changing its actual word.

## 5. What has been closed

A particular rank-30 reader mismatch is repaired by a concrete, baseline-preserving, finite ordinary recoding. Its inverse, whole-state section conjugacy, all-width kernel realization and a width-independent coordinate amplification bound are proved. No new centre bank is required.

A profitable complete Gaussian caller at saving above 0.0035 is not supplied. Its stage routes, all independent target jobs, residual-code removal, precision/stock and outer join remain to be proved. The previous four-partial-helper BIT improvement likewise has a strict symbolic moment gain but has not been admitted above 0.0035. Neither missing component is taken as an assumption of a new κ claim.

## Predecessor credit

Use `research/reciprocal-native-responses` and its rank-30 annex; `research/centre-code-services` fixed-reader, moving-section and phase-inverse proofs; `research/native-centre-capture`; and the source notices for the concrete operators in (3). Their notices retain campaign-lane credit and explicit predecessor PR3133, PR3148, PR2588 and PR2226. No owning PR is inferred where the source does not name one. The corrected moving reader itself is predecessor work; the new implementation here recodes the existing fixed-reader service while preserving an arbitrary borrowed centre.

The general square-zero inverse, shear commutator and finite-character diagonalization are classical tools. The contribution is their actual source-reader application with exact borrowed-state, width and cost scope. Prepared for Dugongue with substantial OpenAI Codex assistance from four workers. No formal verification, computation, worldwide novelty or independent human acceptance is claimed. New text is offered under Apache-2.0.
