# A finite-state consumer for coded Gaussian terminals

## Status and source precedents

This note gives informal mathematical constructions, with no numerical experiments, executable verification or new Lean formalization. The main proposal is to absorb a terminal's invertible code into the multiplication tensor, rather than demand separately decoded Gaussian outputs. The resulting cyclic-convolution tensor has an explicit finite-state carry representation. This is a changed consumer architecture, not a claimed new value of κ. A fast contraction bound for arbitrary dense inputs remains unproved.

The following local linked-tree sources were read as mathematical precedents:

- `Mathproof/SymplecticTI.lean`: `levi_isSymplectic`, `msupp_map`, and `map_eq_of_eqOn_msupp`. The module distinguishes its mode-support argument from classical Levi embeddings and the earlier orbit-closure padding of Lysikov–Walter. Those attributions remain in force.
- `Mathproof/SymplecticTITOCIBalancedCoevaluation20260901.lean`: `dualTensorHom_map_contragredient` and `identityAnchor_invariant`, identifying the cancellation between primal and reciprocal-dual gauges.
- `Mathproof/External/IntegerMultBounds20261008/Matrix/GaussianTensorExecution.lean`: the recursive tensor-power construction and `execute_inverse_forward_exact`. Its file explicitly proves arithmetic composition, rather than physical runtime.
- `Mathproof/Abstraction/VPVNPSubsetConvolution.lean`: exact disjoint-split convolution on squarefree components. It is a useful contrast: integer convolution has carry states, so it must not silently be replaced by carry-free subset convolution.

The retained central-Q proof note supplies the actual endpoint `Q⁻¹ P D`, owner-controlled normalizers and the whole-K involution. Its paid two-Q repair remains valid; nothing here reprices that repair as free. Credit THU New Media Research Center for the whole-K data, Ali Romman for the odd-E8 geometry, Dugongue for the native-code interfaces, and the retained Dillon Amburgey, Cinna Davis, Ryanson Jonathan, Cao Yifan, Jacob Alan Sussman, Chris R/Clear1nsight, zxv and source08 lineage. No external literature or GitHub search was performed for this note, so no world-novelty or exhaustive project-novelty claim is made. General tensor-coordinate changes and finite-state carry representations are classical mathematics; the proposed contribution is their precise combination with the coded Gaussian terminal contract.

Throughout, algebraic vector spaces are finite-dimensional over a field K. Statements involving unitarity or the concrete Gaussian Q use K = C. A transpose pairing is bilinear; it is not a Hermitian inner product.

## 1. Reciprocal gauges preserve the consumer pairing

**Theorem A1 (balanced pairing).** For an invertible matrix G and any vectors x,y,

    (Gx)ᵀ(G⁻ᵀy) = xᵀy.

More generally, if S is any linear operator, then

    (Gx)ᵀ(G⁻ᵀ S G⁻¹)(Gy) = xᵀ S y.

**Proof.** In the first identity, expand the left side as xᵀGᵀG⁻ᵀy and cancel the two middle factors. In the second, the two inverse pairs cancel separately. No commutation assumption is needed. ∎

This is the coefficient form of the linked coevaluation-invariance theorem. It gives an exact alternative contract when the downstream result is a family of bilinear pairings. It does not say that the transformed matrices S are inexpensive to apply.

**Theorem A2 (bilinear consumer transport).** Let β : V × W → U be bilinear and G,H,K be invertible operators on V,W,U respectively. Define

    β[G,H,K](z,w) = K β(G⁻¹z,H⁻¹w).

For every x,y,

    β[G,H,K](Gx,Hy) = K β(x,y).

If β has coefficient tensor T with T[c,a,b] giving output coordinate c, the transported coefficients are

    T'[c,a,b] = Σ_(k,i,j) K[c,k] T[k,i,j] G⁻¹[i,a] H⁻¹[j,b].

**Proof.** Substitute z = Gx and w = Hy in the definition. For the coefficient formula, expand each input and output linear map and collect the coefficient of z_a w_b. Every sum is finite, so rearrangement is legitimate over any field. ∎

The formula is a complete mathematical construction. It is not an algorithmic claim that a dense transformed tensor can be applied cheaply. The following results show why the special multiplication tensor retains much more structure.

## 2. Cyclic convolution is an exact two-state carry tensor

Fix B ≥ 2 and f ≥ 1, and put N = B^f. Write indices a,b,c in base B, with least-significant digits first:

    a = Σ_j a_j B^j,  b = Σ_j b_j B^j,  c = Σ_j c_j B^j.

Let T_f[c,a,b] equal 1 if c = a+b modulo N, and 0 otherwise. Thus

    β_f(x,y)_c = Σ_(a+b=c mod N) x_a y_b

is ordinary cyclic coefficient convolution, including all carries.

For each digit define a local tensor with carry indices h,h' in {0,1}:

    A[c,a,b]_(h,h') = 1 if a+b+h = c+B h', and 0 otherwise.

Use initial carry h_0 = 0, and sum over either final carry h_f.

**Theorem A3 (exact carry-chain identity).** For all a,b,c,

    T_f[c,a,b] = Σ_(h_1,...,h_f) Π_(j=0)^(f−1) A[c_j,a_j,b_j]_(h_j,h_(j+1)).

In particular, T_f has a tensor-chain representation with bond dimension 2, independent of f and N.

**Proof.** At each digit, a_j+b_j+h_j lies between 0 and 2B−1. Its quotient and remainder on division by B uniquely determine h_(j+1) in {0,1} and c_j in {0,...,B−1}. Starting from h_0=0, exactly one carry path is possible for the fixed a,b. Its output digits are the low f digits of a+b. The local product is 1 exactly on this path when c has those digits; otherwise every path has a zero factor. Summing over the final carry discards the possible B^f term, giving cyclic rather than truncated convolution. This also proves the identity in every characteristic: a valid entry has exactly one contributing path, so there is no cancellation. ∎

**Theorem A4 (the two carry states are necessary).** For f ≥ 2 and each cut after k digits, 1 ≤ k < f, regroup all input/output digits below the cut as row indices and all remaining digits as column indices. The resulting matricization of T_f has rank exactly 2 over every field.

**Proof.** The carry-chain representation factors the matricization through the carry h_k, so its rank is at most 2. For a matching lower bound choose these two low-digit assignments:

1. a_low=b_low=c_low=0, which produces carry 0;
2. a_low=B^k−1, b_low=1, c_low=0, which produces carry 1.

Choose these two high-digit assignments: a_high=b_high=0 with c_high respectively 0 and 1. For the first low assignment, only the first high assignment is accepted; for the second low assignment, only the second is accepted. The corresponding 2 by 2 submatrix is the identity, giving rank at least 2 in every field. ∎

Theorems A3 and A4 also hold for **mixed radices** ρ_0,...,ρ_(ell−1), each at least 2. Put P_0=1, P_j=product_(i<j) ρ_i, and N=product_j ρ_j, and write a=sum_j a_j P_j with 0≤a_j<ρ_j, similarly for b,c. At digit j replace the transition by

    a_j+b_j+h_j = c_j+ρ_j h_(j+1).

The maximum digit sum is 2ρ_j−1, so the same two carry states and uniqueness proof apply, with h_0=0 and the final carry summed. For an interior cut j, replace B^k in A4's witness by P_j; the remaining high capacity is N/P_j≥2, so high output indices 0 and 1 distinguish the two carries. Thus every interior mixed-radix cut again has rank exactly 2. The local-gauge proof A5 applies verbatim with invertible ρ_j by ρ_j digit matrices.
Thus the carry dimension is exact, rather than an optimistic low-rank heuristic. The theorem concerns this digit regrouping, not ordinary bilinear rank and not the rank of an arbitrary dense input array.

## 3. Local terminal gauges preserve the carry structure

Identify K^N with (K^B) tensor-powered f times. Suppose

    G = ⊗_j G_j,  H = ⊗_j H_j,  K_out = ⊗_j K_j,

where each displayed B by B matrix is invertible. At each digit set

    A'[c,a,b]_(h,h')
      = Σ_(u,v,w) K_j[c,w] A[w,u,v]_(h,h')
                    G_j⁻¹[u,a] H_j⁻¹[v,b].

**Theorem A5 (local absorption of the exact terminal code).** Replacing every A by the corresponding A' gives the exact coefficient tensor of β_f[G,H,K_out]. Its bond dimension remains 2, and every interior digit-cut matricization still has rank exactly 2.

**Proof.** Expand the product of local A' tensors and interchange its finite digit sums with the carry sums. The three collections of local coefficient products are precisely the entries of G⁻¹, H⁻¹ and K_out. The remaining carry sum is T_f by Theorem A3, so Theorem A2 gives the desired tensor. At a digit cut, the changes of coordinates act as an invertible matrix on the row variables and an invertible matrix on the column variables. Such multiplication preserves matrix rank. Apply Theorem A4. ∎

For fixed B, the local coefficients can be described using a bounded number of field additions, products and inversions per digit. Thus the entire consumer description has length O(f); this is a statement about constructing a tensor description, not contracting it against arbitrary dense data.

**Corollary A6 (central-Q decoding can be moved into the consumer).** Let B=2 and let q be any invertible two-coordinate Gaussian matrix; set Q_f = q tensor-powered f times. For encoded inputs z = Q_f⁻¹x and w = Q_f⁻¹y, and desired encoded output Q_f⁻¹β_f(x,y), an explicit bond-2 consumer is given by Theorem A5 with

    G=H=K_out=Q_f⁻¹.

The construction requires no separate application of Q_f at the two input boundaries.

**Proof.** Apply Theorem A2 to these three invertible product gauges, then use Theorem A5 to construct the exact transported consumer. ∎

This corollary removes a *mathematical interface requirement*, rather than proving a free implementation of the new consumer. A Gaussian decoder has not been omitted from an unchanged circuit: the downstream bilinear tensor has changed explicitly. Extra ordinary owner codes are treated in the next section.

## 4. Actual owner-controlled recodings have bounded digit-cut rank

Let E=K^R be an owner space with basis e_1,...,e_R, and let V=(K^B) tensor-powered f times. Suppose an owner-controlled normalizer is

    L = Σ_u |u><u| ⊗ (⊗_j L_(u,j)),

with invertible digit matrices L_(u,j). For any R by R scalar matrix K_owner define

    C = L⁻¹ (K_owner ⊗ I_V) L.

This is the exact structural form of the normalized whole-K recoding in the retained proof note when its per-owner binary normalizers are tensor-lifted over digit columns.

**Theorem A7 (owner recoding expansion).** The recoding has the explicit sum

    C = Σ_(u,v) K_owner[u,v] |u><v|
              ⊗ (⊗_j L_(u,j)⁻¹ L_(v,j)).

Consequently, with the entire owner factor placed on either one side of any digit cut, the operator Schmidt rank of C is at most R². For a product of m such recodings, this rank is at most R^(2m), independently of f. Any additional product gauge Q_f has operator Schmidt rank 1 and does not enlarge the bound.

**Proof.** Multiply L⁻¹, K_owner⊗I and L using |u><u| K_owner |v><v| = K_owner[u,v]|u><v|. The digit factors multiply independently, yielding the expansion. At any cut each summand is one tensor product of an operator on one cut side and an operator on the other, placing the full owner factor on whichever side contains it; there are at most R² summands. If A=Σ_i A_i⊗B_i and D=Σ_j D_j⊗E_j, then AD=Σ_(i,j) A_iD_j⊗B_iE_j, so the numbers of summands multiply. Induct on m. A pure product gauge contributes one summand. ∎

For a controller with fixed R and fixed m while address width grows, this is a width-independent bound. It may be a very large constant, and it is not uniform when the number of stages grows. The scalar owner matrix need not be diagonal, monomial or commuting with Q. If K_owner is invertible, the same expansion applies to C⁻¹ after replacing K_owner by K_owner⁻¹, so both the terminal gauge and its inverse have the stated bound.

**Theorem A8 (finite-rank gauge composition).** Suppose a bilinear consumer tensor has digit-cut rank at most r. If the two input inverse gauges and the output gauge have operator Schmidt ranks at most s_1,s_2,s_3 at that cut, then the transported tensor has cut rank at most r s_1 s_2 s_3.

**Proof.** Expand the original tensor into r cut-separated summands. Expand each gauge into its stated number of left/right operator products. Distribute the three gauge actions over the tensor expansion. Every resulting term is again separated at the cut, and there are at most r s_1 s_2 s_3 terms. ∎

**Dimension-matched owner consumer.** The space in A7 is E⊗V, of dimension R B^f; C must not be applied as if it were an operator on V alone. For R≥2 identify its basis element e_u⊗e_a (with owner labels 0≤u<R) with index a+B^f u, and use the explicit mixed-radix cyclic convolution modulo R B^f, with f low radices B followed by the most-significant radix R. Its local owner-digit transition has the same two carry states as every other digit. The owner input and output factors are therefore actual physical legs of the tensor. In a natural low-to-high digit cut, put the entire owner factor on the high side; A7's Schmidt bound still applies. For R=1 omit the owner digit.

Combining the mixed-radix extension of A3 with A7 and A8 now constructs a finite-bond consumer on the correctly matched space E⊗V for fixed-stage owner-coded terminals, including the central Q factor. This is convolution on R B^f coefficients; it is not silently identified with R independent convolutions on B^f coefficients, and no assertion is made that the selected caller already uses this service. A caller using another ownerwise bilinear service must transport its own explicitly specified tensor. No tensor-isomorphism decision algorithm, arbitrary change-of-basis oracle, or support-extension oracle is used in the mixed-radix construction.

## 5. Positive contraction theorem for structured inputs

A vector x on f base-B digits has an explicit matrix-product representation of bond at most s if

    x_(a_0,...,a_(f−1)) = l_xᵀ X_0[a_0] ... X_(f−1)[a_(f−1)] r_x,

with compatible internal matrix dimensions at most s. Define the analogous representation Y for y with bond at most t. Scalar boundaries can equivalently be absorbed into the first and last cores.

**Theorem A9 (constructive structured-input consumer).** Given explicit tensor-chain cores A_j for a bilinear map, with bond at most r, and explicit input cores X,Y of bonds at most s,t, the output has an explicit matrix-product representation of bond at most rst. Its core for output digit c is

    Z_j[c]_(h,u,v ; h',u',v')
      = Σ_(a,b) A_j[c,a,b]_(h,h') X_j[a]_(u,u') Y_j[b]_(v,v').

The new cores can be formed with O(f B³ r² s² t²) field operations by literal finite summation, plus compatible boundary contractions. For mixed radices ρ_j the identical construction has bound O((sum_j ρ_j³) r² s² t²). For the plain or digitwise-gauged cyclic consumer, r=2.

**Proof.** Substitute the three matrix-product formulas into the finite bilinear output sum. Distribute the product over the input digit sums. At digit j, the factors involving its input digits are exactly the summands defining Z_j. The three original bond indices form one combined index (h,u,v), of dimension at most rst. Multiplying the new cores and their boundary vectors reconstructs the original sum term by term. There are at most B output digits, r²s²t² pairs of bond indices, and B² summands for each entry, proving the displayed elementary count. ∎

This is a complete sufficient algorithmic theorem for an explicitly specified input family. It does not assume a missing fast multiplier. Arbitrary dense arrays need not have small s,t, so the theorem is not an unrestricted multiplication bound. The actionable question is whether the particular recursive native caller produces intermediate arrays with bounded or slowly growing digit-cut ranks, or another contraction structure with comparable guarantees.

## 6. Global norm and support statements

**Theorem A10 (unitary gauges do not worsen the bilinear operator norm).** Over C equip all arrays with the Euclidean norm. The cyclic convolution map satisfies

    ||β_f||_(2,2→2) = sqrt(N).

If G,H,K_out are unitary, the transported map of A2 has exactly the same bilinear norm.

**Proof.** For each c, Cauchy–Schwarz gives

    |Σ_a x_a y_(c−a)| ≤ ||x||₂ ||y||₂.

Summing the N squared bounds yields ||β_f(x,y)||₂ ≤ sqrt(N)||x||₂||y||₂. Equality is achieved by x_a=y_a=1/sqrt(N): every output coordinate is 1 and the output norm is sqrt(N). Unitary inverse gauges preserve input norms and the output gauge preserves the output norm, so the supremum is unchanged under transport. ∎

The theorem controls the exact bilinear map; it does not by itself bound intermediate rounding growth of every contraction order. Its importance is that a purported exponential loss merely from applying f local unitary gauges is unnecessary at the operator level.

**Theorem A11 (support-local consumer substitution).** Let T in V⊗W and suppose two maps F,G:V→U agree on the mode support of T, meaning the span of all contractions (id⊗φ)(T) with φ in W*. Then

    (F⊗id)T = (G⊗id)T.

**Proof.** Choose a basis (w_i) of W and write T=Σ_i v_i⊗w_i. The coefficient v_i is the contraction against the i-th dual coordinate, so every v_i lies in the mode support. Thus F(v_i)=G(v_i), and the two transformed sums coincide. ∎

This restates the linked TI proof's support-substitution principle for the present consumer problem. It permits a coordinate transform to be specified only on the support actually reached by a tensor. It does not permit deletion of independent dirty inputs whose effects lie in that support.

## 7. A recursively closed coded convolution algebra

**Theorem A12 (one common gauge closes all algebraic compositions).** Fix any invertible G on K^N, and define

    z ★ w = G β_f(G⁻¹z,G⁻¹w),     1_★ = G e_0,

where e_0 is the coefficient vector of the constant polynomial 1. Then ★ is an associative, commutative, bilinear product with identity 1_★. The map x ↦ Gx is an algebra isomorphism from cyclic convolution to this product. Consequently every finite arithmetic expression built from additions, scalar multiplications, constants and cyclic convolution can be evaluated in the G gauge throughout: transform each input and constant once, replace convolution by ★, and the final result is G times the original result. No intermediate change back to uncoded coordinates is mathematically required.

If G is a digitwise product gauge, each ★ call has the explicit bond-2 carry description of A5, and 1_★ is a product vector with bond 1. For a fixed-stage owner gauge on E⊗V, take N=R B^f and use the explicitly defined mixed-radix convolution service in section 4; A7 and A8 then give an explicit finite-bond ★ description on that same space. This owner case does not apply C as an operator on K^(B^f).

**Proof.** The identity G⁻¹(z ★ w)=β_f(G⁻¹z,G⁻¹w) shows that G is a bijective product-preserving linear map. Associativity, commutativity and the unit law follow by applying G⁻¹ and using the corresponding laws of polynomial multiplication modulo X^N−1. To prove the expression statement, induct on the expression tree: G respects linear operations, transformed constants are correct by definition, and the product step is exactly the displayed identity. The local carry and unit-vector assertions follow respectively from A5 and e_0=e_0 tensor-powered f times. ∎

This is an algebraic recursive-closure theorem, not an assumed fast oracle. The ★ tensor is given explicitly above, but a low-cost contraction for arbitrary dense inputs must still be proved. It identifies an exact way that a future native caller could avoid per-stage endpoint repairs by using one common internal representation. Final requested output decoding and every implementation cost remain payable.
## 8. Exact research direction and limits

The main sufficient construction is A3+A5+A7+A8: an explicit finite-state consumer for coded convolution. A9 gives a complete positive contraction theorem whenever the inputs come with bounded-bond representations. A10 gives a useful global conditioning statement for unitary gauges; A12 supplies a recursively closed coded algebra in which intermediate decoders are unnecessary at the level of exact mathematics. These are coherent mathematical facts that can be reused without interpreting an optimistic scalar invoice as a completed multiplier.

Three questions follow directly.

1. **Dense-input contraction.** Can the special gauge-modified carry cores be contracted against arbitrary dense x,y with a fixed-power logarithmic saving over the existing complete native route? The rank-2 carry description alone does not imply this. A proof must account for reading all inputs, every recursive child, output recovery and precision.
2. **Actual caller support.** Do the native caller's intermediate operands have small digit-cut rank, or a decomposition into a controlled number of such operands? Theorem A9 would then give a concrete sufficient contraction bound. Any claimed compression must apply to the full admitted input family, rather than selected examples.
3. **Controlled owner structure.** Can the R^(2m) expansion in A7 be compressed using the actual whole-K relations while retaining phase and the two primal/dual actions? A uniform structural proof would strengthen the finite-state consumer without requiring endpoint Q repairs. General operator-Schmidt rank inequalities alone do not establish such a compression.

No improved κ, new best multiplication complexity, formal proof-kernel acceptance, or exhaustive novelty claim is made. The mathematical direction is the changed bilinear consumer, whose exact tensor and carry structure are now specified; it is not another small optimization of an existing κ invoice.

New exposition and applications: Dugongue, with substantial OpenAI Codex assistance. Existing module and predecessor attributions remain as described above. This document contains only informal mathematics and research questions.





