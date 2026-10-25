# A paid finite interface: one avoided materialization

This is a finite `f=1` construction, not a native supplier admission or a lower bound on all implementations. At the actual fifth PR3945 native event, retaining an unmaterialized lender through its three immediate consumers and composing its next right monomial saves **1024 caller-real writes** against a stronger materialized implementation that already shares source loads and phase negations. Reads, negations, additions and exact halves are equal. Address/control cost, cycle preparation and the native tariff remain unresolved. A weaker, stage-separated implementation is reported only for comparison.

## Literal boundary and exact operators

Both pinned providers have `warps[4]=(1081,333,G,U,E)`. Immediately afterward, B1081/B1082/B1083 add lender333 to registers656/657/658 with coefficients −1,−1,+1 in frame E. No intervening scalar or native event touches333 before B1097, whose incoming lender frame V has rank6. We replace only these immediate output updates and the lender's pending frame transition; intervening instructions receive exactly the same destination values, and the lender cannot be observed until its next transition.

Let M=T_E K_G T_U†. The retained PR3987 signed recipe gives a monomial with affine translation458 and global phase i³, not a homogeneous permutation. Let A=T_V T_E†=L C₀ R, with the exact rank-one child. BOUNDARY.json contains all matrix rows, offsets, quadratic phase coefficients and global phases. The sparse credited evaluator independently checks both identities on all512 input columns. The new dense evaluator uses full signed512-entry tables, including translations and global phases; it does not import the lowering compiler.

For input arrays v,d₁,d₂,d₃, the materialized circuit returns

- d₁−Mv, d₂−Mv, d₃+Mv;
- source L C₀ R Mv.

The lazy circuit updates each destination at p_M(x) with i^q_M(x)v[x], and then applies the signed composition F=R∘M followed by C₀ and L. The four outputs therefore coincide. The verifier checks all2048 complex basis columns (all four arrays), not only the source column. All three implementations are complex-linear, so these columns establish equality for arbitrary complex caller contents. Two additional dense nonzero dirty-input challenges verify inverse return of all four arrays. Inverse integer ×4 alignment merely compares common-denominator representations; inverse operation counts are not used in the forward bill.

## PR4002 phase compensation, on these actual frames

Write D|x⟩=i^wt(x)|x⟩ and J_B=D P_B D†. The source kernel is K_B=J_B Z_t, with
`t_j=(q_B(2^j)−wt(B2^j)+1)/2 mod2`.
The verifier checks the full512-point identity, rather than guessing a phase-free matrix. For a canonical frame with r coordinate factors,

T_U=J_B (Z_t C_[r] Z_t) J_B†.

A flipped axis satisfies Z C_j Z=i C_j†. Consequently the adjointed factors require their central global i. The actual completed bases give tags7,14,31 for U,E,V, flipped axes [0,1,2], [1,2,3], [0,1,2,3,4], and global powers3,3,1. All512 columns of each compensated actual frame are checked. Dropping central compensation or its global phase is rejected. The PR4002 K-only composition law is not extrapolated to affine M: F is composed from the full signed tables directly.

## Strong materialized comparator

A fair comparator can combine materializing M with its consumers. During each permutation cycle, save the original source pair, preserve the following original pair, prepare both negatives once, and select the M-store and consumer operands from those four signed components. This shares the extra source load and phase negations that a stage-separated implementation wastes. `materialized_consumers()` implements precisely that comparator. It then applies R,C₀,L.

The lazy implementation's sole caller-data advantage over this comparator is deletion of M's512 complex stores. All actual M,R,F coordinates are active; L has511 active coordinates. The final counts are in RESULT.json. This is not a globally optimal compiler claim: further downstream fusion could change both implementations. It is an exact comparison of three declared loop schedules at one genuine source boundary.

## Scalar and storage microcontract

A caller-real read/write accesses one real component. ADD performs a real sum; NEG a sign change; HALVE denotes an exact dyadic division. A phase quarter-turn uses swaps via operand selection plus the explicitly counted negations. The consumer kernel prepares −a,−b once per original source pair for both implementations. The child computes four sums/differences then four output combinations:8ADD,4NEG,4HALVE per pair. Dyadic values are exact; no rounding is modeled. If all caller components initially have absolute value at most B, consumer outputs are bounded by2B, and child integer numerators by4B. This needs two guard bits and one fractional bit; word size is a declared finite contract, not a general-f precision proof.

Eight private real words are a constructive schedule upper bound, **not measured Python storage**. The witness harness `scratch_schedule.py` checks the following overwrite plans and explicit zero return from arbitrary private initial data:

- Cycles with materialized consumers: slots0–1 saved,2–3 following,4–5 negatives,6–7 current destination. The signed routing selects aliases of slots0,1,4,5; update slots6–7, store, and reuse them for the next destination. Preserve slots2–3 until the cycle advances.
- Lazy consumers need only saved, negatives, destination (six words); monomial cycles fit within the same eight-word allocation.
- Child: slots0–3 hold a,b,c,d; slots4–7 receive a+c,b+d,a−c,b−d; overwrite0–3 with the four output numerators; store those slots with the exact half interpretation.

The whole forward program reserves eight private words, clears them at entry and return (16 CLEAR operations), and reuses them throughout. It does not borrow or restore an extra dirty caller array. Python's lists are proof representations, not a claim about interpreter memory. Caller arrays are genuinely arbitrary and their prescribed transformed outputs, not their original contents, are preserved by the forward circuit; the inverse returns their inputs.

## Routing setup is not free

Each implementation retains three signed tables of512 entries×(9 destination bits+2 phase bits)=16896 bits. The lazy consumers still need M's full tags; they cannot erase them. The lazy set is M,F,L; materialized is M,R,L. Cycle-leader storage is792 versus252 bits; runtime leader reads are88 versus28. Each runtime reads1536 routing entries. These are explicit metadata categories, not a conversion to real arithmetic cost.

Constructing F adds1024 table-entry reads,512 writes and512 mod4 additions; its temporary table is5632 bits. Cycle decomposition additionally visits512 points and uses512 visited bits plus leader records. The certificate lists this preparation separately and does not price its control/address arithmetic, allocation, cache behavior or hardware latency. The runtime write saving is therefore **not a net total physical-cost or amortization claim**. A native tariff with these terms, a general-f lift, and a fresh whole-supplier replay remain required before any asymptotic inference. Recursive child count and owner width remain unchanged.

## Rejection and independence boundaries

Eight semantic controls reject omitted affine translation, all phases, global i³, the adjoint warp, reversed R/M composition, missing central frame compensation, missing compensated global i and a changed source-bound recipe. Checks use explicit exceptions and also run with Python optimization enabled. The independent sparse evaluator was authored in PR3987 with substantial OpenAI assistance and is retained byte-for-byte; the lowering compiler is used only by optional generate.py. The new dense implementation is a different evaluator, not a fresh human review or proof-kernel certificate. Frozen native author receipts are not promoted to a full fresh supplier replay.
