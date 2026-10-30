# Exact central-query run compression and a source-specific retiming

Dugongue, with substantial OpenAI Codex assistance. Informal mathematics only. All proofs below are symbolic; no numerical computation, solver, Lean process, source replay, web search or network access was used. The source was read as text from the retained repository.

The positive results are a complete compiler for finite central-query runs, a reciprocal-dual tariff theorem for that compiler, and an exact one-query retiming of an actual controller bridge. They preserve every arbitrary input and the full physical operator. They do not establish the Q64 budget, Gaussian saving 0.0036, ordinary BIT saving 0.0037 or κ ≥ 0.0035.

## 1. Physical setting

Let K contain i and have characteristic zero. A role field lies in an address-vector space V. The actual central Gaussian Q is symmetric and satisfies

    Q² = J,       J² = I,

where J is its explicit ordinary translation, including phase. At positive column width f, these are the actual all-column operators. No equality Q² = I is used. A scalar role matrix acts on a finite bank of V-valued fields and commutes with Q and J.

A central-query run is a finite program built from invertible scalar role matrices, known ordinary powers of J, and query shears I + c Q^k e_a e_b^T with a ≠ b and integer k. Scratch is owned and may be initialized and cleared; original fields remain arbitrary. Full fresh-axis Gaussian LOCALs are excluded from the run. Their D factors are not declared ordinary merely because they commute with Q.

## 2. Complete finite-run compilation

**Theorem 1.** A supplied finite central-query run has an exact all-input implementation using

    r = max(rank B₊, rank B₋)

rank-one Gaussian requests, finite ordinary work and cleared owned storage. Here its exact operator has the normal form

    W(Q) = A(J) + B(J) Q,
    A(J) = A₀ + A₁ J,       B(J) = B₀ + B₁ J,
    B₊ = B₀ + B₁,          B₋ = B₀ − B₁,

with explicitly obtainable finite scalar matrices. The construction uses one entry snapshot for the whole run, rather than fresh observations after every literal shear.

**Proof.** Multiply the finite supplied operator word symbolically over K[q,q⁻¹]. Scalar role matrices commute with q, so every entry is a finite Laurent polynomial. Reduce exponents modulo four, retaining q² = J and q³ = Jq. Negative exponents are reduced by the same exact q⁴ = 1 identity. Group the even and odd powers to obtain the displayed A and B. This is an operator equality with all coefficients and phases retained.

Let E₊ = (I + J)/2 and E₋ = (I − J)/2. These complementary ordinary address projectors commute with Q and every scalar role matrix. The odd part is

    B(J)Q = (B₊E₊ + B₋E₋)Q.

Choose scalar rank factorizations B₊ = U₊V₊ and B₋ = U₋V₋. Pad both inner dimensions with zero rows and columns to r. Define

    U = U₊E₊ + U₋E₋,
    V = V₊E₊ + V₋E₋.

Complementarity gives UV = B(J), and Q commutes with U and V. From the unchanged input snapshot x form the r combinations Vx in owned zero buffers. Apply Q to each buffer once and spread by U. Independently form the ordinary term A(J)x. Their sum is exactly W(Q)x.

Accumulate the output in an owned bank while retaining x until its final read. Swap the output bank into the main roles and clear the old input bank and temporary combinations. The main operator equals the original invertible W(Q), so every arbitrary original direction is preserved. Only owned storage is erased. Projector evaluation uses the actual ordinary J and division by the fixed scalar 2, with its native coefficient cost retained. The program is finite and effective. This proves the theorem at every positive width f. ∎

This is a sufficient emitted tariff, not a lower bound for every algorithm using the concrete Q. It is a whole-run extension of sector multiplexing: reducing each shear separately first can obscure shared odd row spaces and cancellations.

## 3. The inverse and reciprocal-dual run have the same tariff

**Theorem 2.** For the run class above, the normal-form compiler of Theorem 1 gives the same value of r for the literal inverse and for the reciprocal transpose W(Q)⁻ᵀ.

**Proof.** Evaluate the formal run at a scalar fourth root λ of unity. Every scalar boundary remains invertible, and each query shear remains invertible because (e_a e_b^T)² = 0. Thus the scalar matrix W(λ) is invertible for λ = 1, −1, i, −i.

Fix ε in {1,−1} and choose λ² = ε. Put A_ε = A₀ + εA₁ and B_ε = B₀ + εB₁. Then

    W(λ) = A_ε + λ B_ε,
    W(−λ) = A_ε − λ B_ε.

The odd coefficient of the inverse on this sector is

    B_inv,ε = [W(λ)⁻¹ − W(−λ)⁻¹]/(2λ)
            = −W(λ)⁻¹ B_ε W(−λ)⁻¹.

The last equality is the elementary inverse-difference identity, with its operator order preserved. Both outer factors are invertible, so rank B_inv,ε = rank B_ε. The normal form is recovered uniquely from the four scalar evaluations, since characteristic zero makes their interpolation denominators nonzero. Therefore the inverse has the same pair of odd-sector ranks and the same maximum r.

Taking a physical transpose reverses the finite word. The actual Q and J are symmetric, and scalar matrix transposition preserves rank. Hence W(Q)⁻ᵀ also has the same two odd-sector ranks. Apply Theorem 1 to the inverse and transposed words. Their ordinary words and fixed coefficient heights may differ, but their paid Gaussian rank-one tariff is the same. No scratch COPY or CLEAR transcript is reversed as if it were an invertible map. ∎

The hypothesis concerns supplied finite words whose scalar specializations are invertible. It is stronger than knowing an arbitrary operator happens to be invertible on one particular finite address space. That stronger hypothesis is satisfied by the stated shear/boundary run class.

## 4. A complete one-query retiming in the actual bridge

The retained controller's forward bridge B between pairs j and k = j + 1 is the chronological pair of ordinary additions

    X_j ← X_j + X_k,
    Y_k ← Y_k − Y_j.

Its following thin forward query S is

    Y_j ← Y_j + Q⁻¹ X_j.

All other fields are preserved. Operator products act right to left.

**Theorem 3.** The actual chronological program B then S can be replaced by the following program with exactly one paid rank-one request:

1. Form t = Q⁻¹(X_j + X_k) from the current pre-bridge snapshot in owned storage.
2. Add t to both Y_j and Y_k.
3. Execute the unchanged bridge B.
4. Clear the owned temporary after its final read.

This equality holds on every arbitrary input and preserves all helper fields.

**Proof.** The original program sends the four relevant fields to

    X_j' = X_j + X_k,
    X_k' = X_k,
    Y_j' = Y_j + Q⁻¹(X_j + X_k),
    Y_k' = Y_k − Y_j.

In the replacement, after the two additions the Y fields are Y_j + t and Y_k + t. The bridge then changes the latter to

    (Y_k + t) − (Y_j + t) = Y_k − Y_j,

while X_j becomes X_j + X_k. The other three displayed outputs agree literally. The one inverse query is implemented by the actual positive Q followed by J, since Q⁻¹ = JQ; no phase is discarded. Every source read precedes its required overwrite, and the owned temporary is erased only after both uses. No helper is touched. ∎

Equivalently, with S' the pre-bridge shared query, SB = BS'. Algebraically

    B⁻¹ e_(Y_j) = e_(Y_j) + e_(Y_k),
    e_(X_j)^T B = e_(X_j)^T + e_(X_k)^T.

Thus the conjugated transvection has a rank-one odd coefficient even though it updates two output rows. Theorem 2 supplies its inverse and actual reciprocal-dual tariff without a second query.

This is a source-specific completed rewrite, not a claim of a cheaper complete caller. It makes the actual legal shared observation explicit: Q⁻¹(X_j + X_k) on the pre-bridge snapshot. A redesign may now reason about that observation at its real deadline instead of moving a query informally across mutable data.

## 5. What the source chronology actually permits

The text of `research/kappa-rebuild/bit/complex_controller_factor.py` places the following events for an interior j:

    backward LOCAL(2j+1,j),
    an optional initial IDLE on the next pair,
    bridge(j,j+1,+1),
    forward LOCAL(2j+2,j),
    bridge(j,j+1,−1).

`research/query-thinned-controllers/controller.py` replaces that even forward LOCAL by QUERY_SHEAR and removes its fresh multiplier. Its `replay_events` definition makes the thin query source X_j with coefficient Q⁻¹. The preceding bridge already reads X_j. The optional IDLE on the next pair does not supply a central query on Y_j.

For comparison, the actual raw coupled offer from `research/native-rank8-helper-provider/PROOF.md`, retained inside the independent audit capsule, has upper-triangular main/mode endpoint

    X = D x − R y + R W h,
    Y = D y,
    H = D(h − Z y),       R = QD.

A completion that would reuse an existing observation QY needs that observation on this actual current clean Y bank before the first use requiring corrected X. The inspected thin query is instead Q⁻¹X, after a bridge has already read X. Theorem 3 legally retimes it, but its source becomes X_j + X_k; it does not become Y_j.

Consequently this note does not count interior occurrences as eligible sites for free QY-assisted helper promotion. That conclusion concerns this actual event pattern; it does not exclude changed producers, a redesigned controller or a different genuine consumer. The positive contribution is the exact alternative pre-bridge shared-query word, with its complete proof and unchanged invoice.

## 6. Exact useful scope and remaining target

Theorem 1 can replace any supplied finite ordinary/thin-query run whose odd sector matrices have low rank. Theorem 2 gives the same tariff in both actual reciprocal orientations. Theorem 3 instantiates that compiler in the real bridge and supplies a new legal query deadline and source expression.

A full fresh-axis LOCAL is not part of this scalar-coefficient compiler. The ordinary maps W,Z in the raw mode offer intertwine the full R; they are not assumed to intertwine Q or D separately. In particular this note never pushes Q through those maps to force the missing clean-bank observation. No saving in P or change in productive T has been proved for the selected full caller, and no positive complete C★ moment is claimed. The Q64 reduction, the ordinary BIT companion and the full outer/compiler obligations remain unfulfilled by this note.

## Attribution and proof-tree precedents

The actual controller and query thinning retain Cinna Davis's paired path/native work, zxv's retained native/controller and tail-completion lineage, Jacob Alan Sussman's mixed-target compilation, Cao Yifan's native words and all source notices. The raw coupled provider is Dillon Amburgey's PR5402 construction, with Chris R / Clear1nsight's PR5407 audit and PR5413 completion; retain Ali Romman's relation mechanism and Cinna Davis's center-free lineage. Classical Laurent reduction, scalar rank factorization and inverse-difference identities are not claimed anew.

The prior informal `typed-provider.md`, T6, supplies the sector-packing construction. The extension here compiles a complete Laurent query run and proves inverse/reciprocal-dual price equality; it also gives the literal bridge instantiation. The linked modules `Mathproof/LinearAlgebra/SchurBlockElimination.lean` and `Mathproof/SymplecticTITOCIBalancedCoevaluation20260901.lean` are precedents for exact elimination and reciprocal bookkeeping. No Lean verification or worldwide priority claim is inferred from their use.

## 7. Two source-bound owned-retirement constructions

The next constructions use the literal forward source in `research/native-center-free-code/CODED-WORDS.json.gz` and the first-departure theorem in `research/native-helper-query-bank/PROOF.md`. The compressed word was viewed only as text, with each instruction displayed on its own line. No instruction was evaluated and no mathematical census was run. This is a different coded forward ABI from the selected raw backward supplier; it cannot be substituted into that caller solely by comparing profiles.

**Theorem 4. Collective cold-bank retirement with 198 actual deletions.** In the stated center-free forward source, designate all 358 ground-chart cold helpers as owned zero fields. Retain its 50 other independent helpers and all arbitrary main inputs. Then 198 specified first-departure H1 children can be deleted, with zero retags at their original boundaries. The main coded operator and all 50 retained helper operators are unchanged. Every retired cold field can be zero on return.

**Proof.** The cited source theorem gives the actual first-departure row of every cold owner as a scalar linear combination solely of the 358 cold original inputs, with empty native words. Those rows are zero after the entire cold bank is initialized to zero, independently of all main and hot-helper inputs. In particular, its 198 funded H1 first departures on odd noncharacteristic lines act on zero. Replacing each such child by physical identity and its zero chart retag leaves the complete physical state exactly equal to the original source state after that event. Induction through the unchanged intervening instructions proves equality at all subsequent cuts. This is not an assumption that one individual cold helper stays zero when other cold inputs remain arbitrary.

The source's independent helper endpoint is block diagonal and has zero helper-to-main blocks. Thus initializing the retired bank to zero does not alter the final main operator or any retained helper job. Every retired output is the source's invertible helper transform applied to zero, hence zero. Initial and terminal owned clearing preserve unrelated fields. All equalities are the retained all-column source identities, so the construction holds at every positive width. ∎

The honest inventory change is

    paid:       P_cf → P_cf − 198 H1,
    productive: debit 26 H4 + 6 H8 + 326 H9.

The remaining independent helper profile is 2 H4 + 7 H7 + 41 H8. No discarded direction is retained as a productive job, and no moment improvement is claimed for this large retirement. All 358 retired slots are actual owned storage; they are not silently removed from the physical allocation. The complete linear algorithm, including initialization and return, may be transposed to give its literal adjoint coded ABI at the same paid ranks. That adjoint must not be relabelled as the selected standard main ABI without its actual wrappers.

**Theorem 5. A literal two-leg retirement of helper 550.** On the same forward coded source, helper owner 550 can instead be retired alone at the exact inventory change

    paid:       P_cf → P_cf − 2 H2,
    productive: debit H8.

Every other original input remains arbitrary and every other independent endpoint is unchanged.

**Proof.** The source's relevant owner-550 instructions are as follows; all references to this owner were viewed, including its warps and paid climbs.

    at frame 114:    main 120 += (1/2) helper 550;
    paid H2:         550 climbs 114 → 825;
    at frame 825:    helper 550 += helper 395;
    paid H3:         550 climbs 825 → 1201;
    at frame 1201:   helper 550 -= 2 helper 454;
    paid H1:         550 climbs 1201 → 1032;
    at frame 1032:   main 120 -= (1/2) helper 550;
    paid H2:         550 climbs 1032 → FULL;
    at FULL:         550 receives additions from 454, 236 and 395.

There are no additional source reads of owner 550 after the displayed frame-1032 main read, and no writes to it before the displayed frame-825 incoming write. Initialize this owner to zero. Its initial outgoing addition is then zero, and the first H2 acts on zero; omit that H2 and retag its zero chart. Keep all middle instructions unchanged. Immediately after the final outgoing read at frame 1032, clear the now-owned field, delete its final H2 and omit its remaining target-only additions. Those operations have no effect on any other field. The source helper's complete rank is eight; its original input/output autonomy guarantees that every other endpoint is independent of its now-retired original input. The middle physical states and every external use agree with the source initialized at this input zero. The owner is zero on return. ∎

This concrete construction is not a profitable single-frame retirement. Its exact target-minus-paid change is 2·2^t − 8^t, which is negative for 1/2 < t < 1 because 4^t > 2. It therefore cannot be booked as a contribution toward the target saving. Its value here is the complete physical deletion contract and the explicit distinction between removable boundary legs and the necessary middle H3 + H1 traversal. The larger current-caller retirement route still needs an actual cohort whose full signed invoice is favorable.

## 8. A literal zero-output pivot deletes a main H4 and H1

This witness uses the actual modified backward word in `research/native-rank8-helper-provider/WORD.json.gz`, including its inserted caches. Owner 226 is outside the source's 122-owner mode basis and remains an autonomous original helper with ground entrance and full exit.

**Theorem 6.** Designating original helper 226 owned zero permits an exact rewrite deleting main owner 18's H4 climb 301 → 254 and its terminal H1 climb 254 → FULL, with its now-dead intervening subtraction omitted. Every retained original input stays arbitrary and has its prescribed output. The productive debit is helper 226's original H9 job.

**Proof.** The actual last pre-suffix update of main owner 18 is the adjacent pair

    H4: 18 climbs 301 → 254;
    at frame 254: 18 -= 92.

Owner 92 is already at frame 254. No instruction reads owner 18 between this pair, and after the subtraction no instruction reads or writes it before its terminal H1 in `cleanup_tail`.

After owner 226 has received its current 449 and 483 contributions, write a for its value, d for current owner 40 and e for owner 18 just after its terminal H1. The next relevant ordinary operations

    226 += 40;       40 -= 226;       226 += 40

leave owner 226 equal to d. Its next relevant instructions are exactly

    226 -= 18;
    18 *= -4;
    226 += 18;
    18 -= 226;
    226 += 18.

They leave owner 226 equal to −4e: successive substitution gives d−e, d−5e and finally −4e. Intervening source instructions do not change owners 18 or 226. Owner 226 has no later reference in the complete modified word. Thus this is its final physical helper row.

The retired autonomous helper's final output is zero for all retained inputs, so e = 0. Its terminal H1 is invertible. Therefore owner 18 was already zero immediately after its frame-254 subtraction. The preceding H4 result, had it been evaluated, would equal the then-current owner 92.

At the omitted H4/subtraction pair, install an owned zero buffer as owner 18's post-subtraction field, carrying its frame-254 zero tag. A whole-field swap moves its old, now-dead value into the owned slot; that obsolete copy is cleared. Every other physical state equals the original source at this cut. This is owned disposal after an exact state-reconstruction argument, not erasure of an independent original input. Replace the later zero H1 by a physical zero retag. Induction through the unchanged suffix proves all retained endpoints. The original helper-226 slot is initialized and returned as owned storage. All added moves and clearing are finite ordinary work. The scalar proof and source identities hold at every positive width. ∎

The honest signed change is

    paid:       P → P − H4 − H1,
    productive: debit H9.

It is not claimed profitable. The witness shows why final-output constraints can delete requests on another owner, even when a retired helper has late external reads.

The eight existing zero retags do not automatically yield another eight H4 deletions. The actual modified owners 9 and 11 are copied into retained caches immediately after H4 and read by six other outputs before center subtraction. Their H4 intermediates are observed. Owner 288 likewise has an inserted cache COPY immediately after its H4; a predecessor-only scan misses that use. In the raw mode construction each cache feeds C0 at a removed-center site, and C0 participates in main updates. Retiring the final coupled mode output does not remove this earlier main-correction use.

## 9. An explicit two-row reconstruction for hot helpers 626 and 627

These are the two hot rank-4 autonomous helpers. Their common birth frame 1160 has basis [7,51,82,136,264], and they end at FULL. Their four rank-one path legs are actual source requests. Both owners lie outside the cold mode basis. The following construction applies the terminal-suffix idea with a fully supplied ordinary reconstruction, without an unspecified matrix inverse.

**Theorem 7.** Retire original helpers 626 and 627 as owned zero inputs. Their final H1 requests can be omitted and their post-query FULL values reconstructed by integer scalar operations from six other actual FULL fields. All other outputs retain their exact source operators.

**Proof.** Hoist each involved role's final FULL climb before its first FULL scalar use. This is legal because no earlier FULL-suffix instruction has read or changed that role: its original climb was its first FULL preparation. The protected climbs are retained and paid. At the resulting common FULL snapshot write

    a = u626, b = u627, c = u622, d = u623,
    e = u624, f = u625, p = u401, q = u403.

For a and b these denote the source's expected post-query values; they will be reconstructed instead of queried. The actual first FULL instructions involving these owners are

    401 -= 625/2;       625 += 401;
    624 -= 403/2;       403 += 624;
    623 -= 626/2;       626 += 623;
    622 -= 627/2;       627 += 622.

The source also adds current 627 to 334 and current 626 to 332 and reads 625, 624, 623 and 622 into other owners. These reads do not alter the displayed source fields. The last writes to the two retired rows are

    627 -= 625;         627 += 624;         627 -= 623;
    626 -= 625;         626 -= 624;         626 += 622.

There are no later references to 626 or 627. The full reference lists for 401 and 403 show no earlier FULL write before their displayed first exchanges. Their subsequent mixing and native FULL warps occur after these final retired-row writes. Thus direct substitution gives the actual final rows

    out626 = (a − b − f + q)/2 + c + d − e − p,
    out627 = (a + b − f − q)/2 + c − d + e − p.

Retiring both autonomous inputs makes both outputs zero for all retained inputs. Adding and subtracting these equations gives

    a = f − 2c + 2p,
    b = q + 2d − 2e.

The six right-hand inputs are protected FULL snapshot fields already supplied by their unchanged and paid paths. They precede any suffix use of a or b. Evaluate these two explicit scalar combinations in owned initialized output buffers; use them in place of the two omitted H1 results. They are exactly the source's post-query values on the input specialization. The remaining literal suffix therefore sees its original physical state on every field and returns all original retained outputs. All overwritten dead versions and temporary combinations occupy owned slots before erasure. The retired helper fields finish at zero. Source all-column identities and ordinary integer coefficients give the construction at every positive width. ∎

The complete signed change is

    paid:       P → P − 2 H1,
    productive: debit 2 H4.

Its power-moment change is 2 − 2·4^t, so this terminal-only construction is not a favorable supplier change. It is a fully instantiated reconstruction witness, including late protected outgoing reads.

The hoped-for larger deletion on SOURCE120 or SOURCE138 is not established by this witness. Those source fields finish in non-FULL hyperplanes 150 and 168 and do not occur as columns in the two displayed FULL rows. In particular, SOURCE120's H5 from 519 to 1032 precedes a live read into helper 550 and a write to SOURCE138; SOURCE120 is then itself changed before its final hyperplane step. Protected helper625 later contains that changed source value. Recovering an earlier SOURCEH5 result from these later states would require an additional causal construction. The terminal reconstruction above does not supply it.
