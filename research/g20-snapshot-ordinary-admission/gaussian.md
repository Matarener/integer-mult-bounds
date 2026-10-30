# Coherent complement flags in the actual Gaussian frame compiler

Dugongue, with substantial OpenAI Codex assistance. Informal proofs from local source reading only. No mathematical script, numerical evaluation, source replay, solver, Lean run or external search was used. The main positive result removes a flag-coherence assumption for the source's canonical nested transports. It also gives exact rank-one replacements for a rank-eight centre with one full-Gaussian endpoint gauge. This does not yet supply a compatible complete provider gauge or a funded κ ≥ 0.0035.

## 1. The actual canonical frame convention

The retained native Clifford source defines `basis_extend(cols,n)` by first retaining an independent basis of the supplied subspace and then testing e₀,e₁,... in order, appending an axis exactly when it increases the span. Its `canonical_frame` uses

    G = the full basis matrix,
    Q_G = I + G⁻ᵀG⁻¹,
    K_G = diagonal_chirp(Q_G) · permutation(G),
    F_U = K_G R_[0,r) K_G⁻¹,       r = dim U.

Products here act right to left. This order follows the source's `then` convention. The full frame is R, the product of the n coordinate Gaussian C gates. The source uses n = 9 locally. All ranks in the proof below are binary symplectic ranks; all operator identities retain their literal Clifford phases.

Let C(U) denote the span of the standard axes appended by `basis_extend`. Thus U ⊕ C(U) = V, where V is the n-dimensional binary address-direction space. This is a direct complement, not necessarily the orthogonal complement U⊥.

## 2. The source's greedy complements are coherent

**Theorem 1.** For any subspaces S ⊂ T, the actual greedy complements satisfy

    C(T) ⊂ C(S).

This holds independently of the particular independent bases supplied for S and T.

**Proof.** Just before the test of e_j, the current span in the completion of U is U + span(e₀,...,e_(j−1)). Earlier rejected axes are already in that span, so they do not change this description. Therefore e_j is appended exactly when

    e_j ∉ U + span(e₀,...,e_(j−1)).

If it is appended for T, it is outside the displayed larger span with U = T and hence outside the smaller span with U = S. It is therefore appended for S. Every generating standard axis of C(T) consequently belongs to the selected generating list of C(S). ∎

This is a property of the actual source constructor. It is not an assumed existence of a compatible flag to be supplied later. The complement map need not be involutive, and no assertion C(U) = U⊥ is made.

## 3. The Lagrangian description and exact nested rank table

For U ⊂ V define the Lagrangian

    L_U = {(u,u+w) : u ∈ U, w ∈ U⊥}.

In particular L₀ is the Z-Pauli Lagrangian and L_V is the full-Gaussian image of L₀. Binary orthogonality refers to the standard dot product.

**Lemma 2.** The source K_G maps L_U to L_(GU), fixes L₀ and L_V, and the source frame satisfies

    F_U L₀ = L_U,
    F_U⁻¹ L₀ = L_U,
    F_U L_V = F_U⁻¹ L_V = L_(C(U)).

**Proof.** Its symplectic action is

    (x,z) ↦ (Gx, Q_G Gx + G⁻ᵀz).

For z = x+w the identity Q_G G + G⁻ᵀ = G gives the image (Gx,Gx+G⁻ᵀw). This is exactly L_(GU). Hence both endpoint Lagrangians are fixed. The partial coordinate Gaussian interchanges the Lagrangians for the coordinate prefix and its coordinate complement. Conjugating it by K_G gives the displayed images for U and its actual appended-axis complement. Its symplectic action is an involution, so replacing F_U by its inverse does not change these Lagrangian identities. ∎

**Lemma 3.** For arbitrary A,B ⊂ V,

    dim(L_A ∩ L_B) = n − dim A − dim B + 2 dim(A ∩ B).

**Proof.** In the common expression (x,x+w), x lies in A ∩ B and w lies in A⊥ ∩ B⊥ = (A+B)⊥. These two choices are independent. The dimension formula follows from dim(A+B) = dim A + dim B − dim(A∩B). ∎

Let S ⊂ T and E = F_T F_S⁻¹. Write r = dim T − dim S. A full physical row gauge is R. The changed request is R^b E R^(−a), with input gauge bit a and output bit b.

**Theorem 4.** The exact Gaussian child rank is

| Input bit a | Output bit b | Rank |
| --- | --- | --- |
| 0 | 0 | r |
| 0 | 1 | n − r |
| 1 | 0 | n − r |
| 1 | 1 | r |

This table holds for every source-canonical nested pair, including noncoordinate or isotropic subspaces.

**Proof.** A Clifford operator A has Gaussian rank n − dim(L₀ ∩ A L₀). Pulling intersections back by F_T gives the following intersections for the four cases:

    (0,0): L_T ∩ L_S;
    (0,1): L_(C(T)) ∩ L_S;
    (1,0): L_T ∩ L_(C(S));
    (1,1): L_(C(T)) ∩ L_(C(S)).

For the first, nestedness and Lemma 3 give dimension n−r. For the second, C(T) ∩ S = 0 because S ⊂ T and C(T) complements T; its Lagrangian intersection dimension is r. For the third, T + C(S) = V, so dim(T∩C(S)) = r; Lemma 3 again gives r. For the fourth, Theorem 1 gives C(T) ⊂ C(S), so Lemma 3 gives n−r. Subtracting each dimension from n proves the table. ∎

The ranks alone are not phase certificates. Each changed operator is the explicit Clifford word R^b F_T F_S⁻¹ R^(−a). Applying the source's fixed exact Clifford elimination to this specified word gives a rank-rank-table child between ordinary monomial maps, including its global phase. This is a constructive finite algebraic factorization prescription; it has not been numerically run here. The same literal one-column factorization lifts columnwise at every positive width, with its scalar phase raised once per column.

## 4. A literal rank-one replacement for every old H8 centre

Let n = 9, let U have dimension eight and let its literal frame be

    F_U = K R_[0,8) K⁻¹.

Put T_K = R K R⁻¹. It is an ordinary monomial because K fixes L_V. Its exact phase is determined by the source's full-basis monomial construction; it is not replaced by a projective tableau.

**Theorem 5.** The following exact factorizations use just one proper Gaussian direction:

    F_U R⁻¹ = K R_8⁻¹ T_K⁻¹,
    R F_U   = T_K R_[0,8)² R_8 K⁻¹.

Here R_8 is the Gaussian on the single omitted coordinate and R_[0,8)² is its actual ordinary translation on the other eight coordinates.

**Proof.** Insert R⁻¹R next to K⁻¹ in the first expression and use R_[0,8)R⁻¹ = R_8⁻¹. For the second, move R past K using RK = T_KR, and use R R_[0,8) = R_[0,8)²R_8. No phases or even powers are discarded. ∎

Thus the old eight-axis centre request costs H1 if its input and output full-gauge bits differ. This is an actual finite all-input centre bridge. It is not an assertion that the neighbouring source and receiver fields already have the required gauges.

For a concrete phase prescription, let K e_x = i^φ(x)e_(Gx), a_j = G⁻¹e_j, and define d_j by

    2d_j = φ(a_j) + wt(a_j) − 1  modulo 4.

The right side is even because K stabilizes L_V. Its phase at zero is the source's literal normalized value one. Then

    K R⁻¹|0⟩ = Z_d R⁻¹|0⟩,
    T_K|0⟩ = (−i)^wt(d) |d⟩.

The first identity follows by comparing the Gaussian kernel at each basis axis and its stabilizer character; the second is the exact conjugation of Z_d by R. Together with the signed symplectic action this fixes T_K's complete ordinary P/D/X/phase word. This is the analytic anchor used in the retained whole-K frame construction, not a new numerical phase evaluation.

## 5. Actual native warp events need an additional incidence test

The source does not execute a bare logical K_G as its physical warp event. The phase-admission source explicitly defines the physical event as

    E_G = F_B K_G F_A⁻¹,

with G A = B. This event is ordinary in the retained word. Conjugating only its bare middle factor by R is insufficient to price the changed event.

**Theorem 6.** Suppose dim A = dim B = k. The rank table for this physical warp is

    rank(E_G) = 0,
    rank(R E_G) = rank(E_G R⁻¹) = n,
    rank(R E_G R⁻¹)
      = 2[(n−k) − dim(G C(A) ∩ C(B))].

In particular the two-flip event is ordinary exactly when G C(A) = C(B).

**Proof.** A monomial physical event has zero Fourier rank. Multiplying it on either side by the full rank-n Gaussian preserves rank n because monomial boundaries preserve Fourier rank. For two flips, pull back the Lagrangian intersection to obtain L_(C(B)) ∩ K_G L_(C(A)) = L_(C(B)) ∩ L_(G C(A)). Their direction spaces both have dimension n−k. Lemma 3 yields the displayed formula. Equality of these spaces is exactly the zero-rank condition. ∎

This is the remaining source-bound distinction between coherent nested transports and arbitrary native-map incidences. The greedy constructor proves C(T) ⊂ C(S) for an inclusion; it does not prove G C(A) = C(B) for an arbitrary invertible G mapping A to B.

A map built by matching a full basis of A followed by its appended standard axes to the corresponding full basis of B does satisfy the second incidence. A prescribed additional line a ↦ b can impose another condition: relative to the direct sums A ⊕ C(A) and B ⊕ C(B), both its zero/nonzero components must match. The actual round-three `line_matching_map` includes such extra constraints and the final freeze may retain an older map. No uninspected family of all native warp events is declared free under the new gauge.

## 6. Whole-word use and the actual funding boundary

Assign a gauge bit to every live field version. At a scalar contact, operands with the same gauge still share the same exact physical frame, so the original scalar instruction is ordinary. A gauge mismatch requires its own emitted correction or a proved whole-boundary compression. It cannot be ignored because the centre itself became cheaper. A COPY of a nonzero field also needs its actual matched gauge; only an independently known zero owned boundary can be retagged without a request.

For a complete finite gauged word, telescope the literal factors to compute its exact original-input endpoint. Retain every original independent helper unless it is explicitly retired and fully debited. Price every nested child by Theorem 4, every actual physical warp by Theorem 6, and every mismatched scalar boundary by its actual emitted program. Productive endpoints require their own complete physical normalizers and inventory; a local gauge does not preserve their ranks automatically. Transposition of the whole exact linear construction supplies the actual reciprocal orientation with the same paid child ranks, provided its real endpoint and helper normalizers are retained.

For one old H8 centre the isolated reduction is 8^t − 1. This subtotal is not the complete price change. Main H4 contacts, late H1 requests, modified warp ranks, cache readers, whole-job targets, ordinary maps, storage and precision all remain in the full invoice. The existing eight raw zero retags remain source-specific known zero boundaries; their preceding cached H4 values still have live readers.

No complete new source gauge assignment is supplied here. Accordingly, no favourable whole Gaussian profile and no Gaussian funding at 0.0035 are claimed. The proved improvement in scope is the source-specific coherent-complement theorem and exact rank-one centre bridge, together with the complete physical-warp price needed to use them honestly.

## Source credit

The actual constructor and phase source are `research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py`, `research/warp-interface-20261022/verify_candidate.py`, `research/kappa-round3-warp-20261022/{PROOF.md,constrained_map.py,freeze_candidate.py}` and `research/odd-e8-whole-k-native/PROOF.md`. They were read as text. Preserve the retained exact Clifford compiler notices, Cinna Davis's native/frame lineage, Cao Yifan's round-three construction and source-map changes, Dugongue's physical interface work, Ali Romman's owned relations and controllers, Dillon Amburgey's coupled provider, Chris R / Clear1nsight's audits, Ryanson Jonathan, zxv, Jacob Alan Sussman and all native, scalar, Gaussian, compiler and analytic contributors.

Classical Lagrangian intersections, greedy basis extension and Clifford elimination are not claimed as new general mathematics. The contribution is their explicit application to this exact source constructor, removing an assumed flag-coherence obligation while retaining the separate actual-warp incidence obligation. No formal verification or worldwide novelty claim is made.

## 7. A different construction: right-frame gauges and free-word reassignment

Left multiplication of a physical field by R, used in Sections 3–5, is distinct from replacing its reference frame by F_U R. Confusing them gives an incorrect tariff. The following theorem explicitly changes the physical transport requests; relabelling their headers alone would change no cost.

### The actual inherited free-word premise

`research/kappa-rebuild/complex/FULL-IDENTITY.md` supplies the original complete full-identity local words with constant normalized endpoints

    F_I(X,Y,h) = (X,Y+X,h),
    B_I(X,Y,h) = (X−Y,Y,h).

All 632 persistent inputs are arbitrary; the single owned centre is zero on return. These right-hand sides contain no native warp generators. The formal source convention is spelled out in `research/native-center-free-code/CODED-PROOF.md`: identities live in Q[FreeGroup72], rather than only in a one-column numerical operator algebra. Its `native_core.py` defines each original input as a separate formal column, appends the signed native generator at a warp, cancels only adjacent inverse letters, and compares with the constant endpoint. Positive and negative occurrences are actual inverses; the backward source uses its own consistently conjugated generator assignment. `fresh-helper-boundary/PROOF.md` retains this same formal-word convention under frame retiming.

The theorem below uses this recorded universal source certificate. It is not a claim of a fresh full-word replay here. The corresponding statement would not preserve a target whose prescribed right-hand side itself depended on those generators. Nor does a sampled matrix identity establish the premise.

### Theorem 7. A source-compatible physical right-frame compiler

For one fixed source orientation choose the matching full Gaussian R: use the conjugate literal word throughout for a conjugated backward frame convention. Assign a bit g to every live field version, and replace that version's physical frame by

    H_(U,g) = F_U R^g.

Require all of the following finite conditions:

- Every scalar contact and nonzero COPY uses one common original frame U and one common bit on all its source and target versions, unchanged across that scalar event.
- For each positive native generator j there is one ordered pair (a_j,b_j) used at every positive occurrence. Every negative occurrence uses the reversed pair (b_j,a_j).
- Every independent productive input and final output has bit zero. Owned zero boundaries may be retagged; every nontrivial zero retag must have a universal formal zero-row proof at that site.
- At an original proper transport U → V, actually replace the child by the literal operator H_(V,b) H_(U,a)⁻¹, with its full phase and monomial factors. Do not merely retag the old nonzero child.

Keep each physical native warp event unchanged. Then the resulting complete program has exactly the same physical independent-input endpoint as the source. Every ordinary operation, child replacement and owned return is specified; the new paid profile is the multiset of those replacement child ranks.

**Proof.** At a physical warp E_j = F_V K_j F_U⁻¹, using the new source and target frames gives its exact logical action

    H_(V,b)⁻¹ E_j H_(U,a) = R^(−b) K_j R^a.

Define K'_j by this formula with the generator's one assigned ordered pair. The occurrence condition makes every positive occurrence use the same K'_j. A negative occurrence has logical action

    R^(−a) K_j⁻¹ R^b = (K'_j)⁻¹.

These new logical assignments are invertible. They need not be ordinary operators: they are not executed separately, since their actual physical warp events are the original already-admitted ordinary events.

Each newly emitted transport changes H_(U,a)z to H_(V,b)z and hence preserves its logical row. Every matched scalar contact has its original scalar row action. COPY and CLEAR on owned fields retain their actual meaning; the zero function is independent of its frame. Thus the changed program evaluates exactly the original formal word at the consistent invertible assignment K_j ↦ K'_j.

The inherited free-group identity has the constant prescribed right-hand side displayed above. Therefore that right-hand side is unchanged under this evaluation. Boundary bits zero make its physical input and output frames exactly the old ones. All original main and helper jobs and their exact normalizers are consequently preserved. The construction holds at every positive column width: evaluate the same formal identity in the actual lifted operators, leaving scalar owner coefficients outside the lift. Complex conjugation of the entire literal convention gives the corresponding backward statement with its correct phases. ∎

This is not physical conjugation of each paid event by a common left R. The transport requests are different, the logical native operators are reassigned consistently, and the universal constant endpoint is what certifies their full composition.

### Exact right-frame rank

**Theorem 8.** For a nested proper edge S ⊂ T, put r = dim T − dim S and δ = dim(S ∩ T⊥). Its right-frame child rank is

    r                         if a = b,
    n − r − 2δ                if a ≠ b.

The same result holds for the reverse edge and the corresponding inverse orientation.

**Proof.** Equal bits cancel R in H_(T,b)H_(S,a)⁻¹, giving the old request exactly. For unequal bits its symplectic action is F_T R F_S⁻¹, since R and R⁻¹ have the same symplectic action. The full R maps L_S to L_(S⊥). Hence its rank is

    n − dim(L_T ∩ L_(S⊥))
      = n + r − 2 dim(T ∩ S⊥).

The rank of the restricted bilinear pairing S × T is symmetric under transposition. Therefore dim(T∩S⊥) = r + dim(S∩T⊥) = r + δ. Substitution gives the formula. Taking an inverse preserves Gaussian rank and exchanges the two endpoint bits. ∎

Unlike the left-gauge table, this can be smaller than n−r. The extra saving comes from an actual orthogonal incidence S ∩ T⊥; it cannot be inferred merely from the edge's rank.

### A real eligible edge, and a global colour obstruction

One literal SOURCE 124 edge has lower frame 404 and upper frame 989, with bases

    S = span(388,51),
    T = span(256,128,64,33,18,11,4).

The source pays H5 on this edge. Vector 51 is orthogonal to every displayed generator of T, while 388 is not: its pairing with 256 is one. Since the two displayed vectors are independent, S ∩ T⊥ = span(51). Theorem 8 therefore prices this actual edge at H2 when its right-frame bits differ. This is a proved local tariff, not an already matched whole-word colour assignment.

A fixed role-colour shortcut does not supply such an assignment. In the actual backward body, helper 300 receives a main SOURCE 113 contribution at ground and later supplies receiver 19 at frame 21. If all main sources have one colour, all receivers another and each helper one fixed colour, these two scalar contacts force the source and receiver colours equal. Centre preparation and its receiver contact therefore cannot obtain opposite colours by that role-based rule alone. Version colours with proper-edge changes and the full generator occurrence conditions are needed.

No global version-colour assignment satisfying Theorem 7 and funding the target moment has been constructed here. The SOURCE 124 H5-to-H2 opportunity and the centre H8-to-H1 bridge are consequently not added to a claimed paid reduction. This theorem supplies a constructive sufficient class with the actual source's universal constant endpoint, not a hypothetical profitable provider hidden in an assumption.

**Physical-adapter condition for the source application.** Include every actual fixed entry, exit and residual adapter among the fixed boundaries of Theorem 7, with bit zero on both of its physical sides, unless its complete changed physical map is separately constructed and charged. Metadata-only source markers remain metadata; their presence does not justify treating an unpriced physical conversion as identity. With this additional explicit boundary convention the recorded old adapter words and all their phases are retained literally. A candidate that cannot satisfy it needs an expanded invoice, rather than the transport-only profile formula.

### Boundary-commutant corollary

The zero-bit boundary rule is a convenient sufficient choice. More generally, let B_in and B_out be the diagonal banks of right R powers attached to actual independent input/output cuts of the formal body. If its prescribed generator-free logical endpoint is S and

    B_out S B_in⁻¹ = S,

then the changed physical body has the same endpoint even with nonzero boundary bits:

    F_end B_out S B_in⁻¹ F_start⁻¹
      = F_end S F_start⁻¹.

This follows directly from the same free-word substitution proof. No initial R is executed: the input is the arbitrary raw physical field at the actual cut. This is a proved equality of the completed physical body, not a declaration of a free preprocessing routine. Literal external normalizers remain unchanged because the entire body operator is unchanged. Internal physical adapters still need the separate condition stated above.

For the full-identity logical main shear, a common bit on both main banks at entry and exit commutes with its scalar row matrix. Each autonomous helper may also have its own matching input/output bit because its logical block is identity. Thus all productive boundary bits one are an admitted boundary-commutant case. This does not itself reduce any cost. If all internal bits are also one, every proper transport is exactly F_T R R⁻¹ F_S⁻¹ = F_T F_S⁻¹, and every physical warp remains the old one; the invoice is unchanged.

Uniform one bits with only the centre changed at its owned CLEAR do not make a nonzero H8 centre cheaper. Its subsequent nonzero scalar preparation forces its input bit to match the prepared source fields, and its nonzero output contact forces its output bit to match the receiving fields. With those fields all one, both centre endpoint bits are one. A frame bit can change freely at a whole-zero boundary, but a nonzero prepared centre cannot be retagged as though that earlier CLEAR were still its current value. No H8 saving is inferred from this shortcut.
