# Endpoint reconstruction for retired helpers

Dugongue, with substantial OpenAI Codex assistance. This is informal mathematics based on retained source notes. No mathematical computation, numerical source replay, solver, Lean run or external search is used. The result is an explicit finite reconstruction algorithm; it is not a claim that an unspecified profitable source cohort exists.

## 1. A retired output can determine a different current field

Work over a field of characteristic zero, or over F₂ for the BIT model. A field below means one complete data array, with its actual ROW and spectator coordinates. Suppose a finite source program has independent retained inputs x and helper inputs h. Its desired final action on the helpers selected for retirement is an invertible autonomous operator Γh, with no x contribution. Set those helper inputs to zero using initialized owned storage, debit their entire original productive targets, and retain all other inputs arbitrarily.

At a cut of the unchanged source, let z be a bank of n complete fields in one actual physical frame. Suppose the remaining action on that bank is an explicitly ordinary invertible scalar matrix M. Any role-dependent monomial normalizers are executed explicitly before this scalar suffix; they are not treated as scalar entries in the matrix inversion. For a missing field, reconstruct its normalized value first and then use the stated ordinary inverse normalizer when needed. Different physical frames cannot be silently identified. Let R select m final helper rows whose outputs are zero on this restricted input domain. Choose any m current columns J for which the square matrix M_(R,J) is invertible. Write K for the other current columns. J need not consist of the retired physical owner slots.

### Theorem 1. Exact missing-value reconstruction

If the values z_K are available, the current missing values are exactly

    z_J = − M_(R,J)^(-1) M_(R,K) z_K.                 (1)

Consequently, a preceding independently scheduled batch of Gaussian requests producing only z_J can be omitted, if no observer needs those request results before this cut. Compute (1) with ordinary operations, then execute the original suffix M. Every retained desired endpoint is unchanged.

**Proof.** Autonomous retired outputs are zero, hence 0 = M_(R,J) z_J + M_(R,K) z_K. The inverse hypothesis gives (1). This is an identity of entire data arrays at the stated common physical frame, for every retained input, not a relation inferred from a sampled coefficient column. The reconstructed z_J is therefore exactly the value that the full source program would have produced. Substituting it before the unchanged suffix preserves that complete suffix state and all its outputs. No future output is read as an oracle: only current z_K and fixed explicitly supplied scalar coefficients are used. ∎

The proof also explains its limits. Retiring an output row does not generally allow deleting the last query on the same physical owner. M_(R,R) can be singular while M_(R,J) is invertible for another column set J. Conversely, a late observer or an unknown inverse matrix cannot be omitted from the hypothesis.

### Theorem 2. A literal implementation without clearing a productive slot

Under Theorem 1, the replacement can use owned zero temporaries, ordinary scalar combinations, whole-field swaps and erasure only of owned storage. It preserves every independent retained input direction in its final action.

**Proof.** Initialize an owned bank, compute the right side of (1) there from immutable snapshots of z_K, and swap each computed field into its destination in J. The overwritten old destination values move into the owned bank and can be erased there. Theorem 1 proves that the new live destination equals its exact required source value. Thus all remaining final outputs agree with the source on every independent retained input. The discarded old current values are redundant for those outputs on this restricted domain; no independent retained original input is removed from the map. Retired original helpers receive no target credit. All copied snapshots and swap banks are cleared after their last reads. The storage reserve, scalar arithmetic and payload scans are real finite work. ∎

A row relation inferred from final zero is not permission to CLEAR an arbitrary productive slot in the old word. The owned swap implementation and the proof of exact current-state reconstruction are part of the construction.

## 2. Backward zero anchors and query-output substitution

### Theorem 3. A zero interval removes its native transport

Suppose an actual source value w is known to be zero at event b on the restricted retirement domain. Between events a and b it undergoes only explicitly invertible homogeneous transforms and has no incoming writes. Then it is zero throughout that interval. Those transforms may be omitted with zero-only frame bookkeeping, provided every outgoing use is reproduced as a read of zero.

**Proof.** Invert the product of the homogeneous transforms to obtain w_a = 0. Every prefix of that product also sends zero to zero. Other operations reading the field receive their original zero value, so their effects agree. ∎

### Theorem 4. Reconstructing a child output before an immediate cancellation

Suppose a proper Gaussian request produces v = G u in physical frame F, immediately followed by an ordinary update

    v ← v + A d,

where d is already available in the same frame F. Suppose the result of that update is known to be zero, with an actual all-input proof. If there is no intervening observer of G u, omit the request and instead install v = −A d using the owned implementation of Theorem 2. Execute the update. Every later live value is unchanged, and the paid child G is removed.

**Proof.** The zero identity gives G u = −A d on every retained input. Its right side is available at the required time and frame. The replacement thus supplies exactly the old post-query value before its next update. No intermediate result is skipped because the stated interval has no observer. ∎

The donor must exist at the query deadline. An equality that uses a later cache first produced from G u is circular and does not satisfy the theorem. This distinction matters for the actual cached Gaussian source.

## 3. The exact bill and reciprocal scope

Let the omitted children in Theorem 1 or Theorem 4 have ranks a_j. Let the retired independent original helper jobs have ranks k_i. Include every other added recursive child in a separate multiset B; ordinary work and owned stock are recorded separately. The exact target-minus-paid change at exponent 0 < t < 1 is

    Δ(t) = Σ_j a_j^t − Σ_i k_i^t − Σ_(b in B) b^t.    (2)

There is no additional target for the reconstructed bank or its snapshots. A child site used by more than one zero relation is deleted once. Formula (2) may be negative even when the algebraic rewrite is correct.

For the standardized Gaussian main block

    S = [[D,−R],[0,D]],   R = DQ = QD,

and canonical independent helper outputs, a correct retired implementation has same-profile inverse and reciprocal orientations with finite ordinary wrappers. Indeed, with A = diag(−I,I),

    S^(-1) = diag(D^(-2),D^(-2)) A S A.

Here D and R are the canonical symmetric Gaussians, D^T = D and R^T = R. The factors D^(-2) are the actual ordinary even-power Gaussian reflections. Each canonical helper G_k has G_k^(-1) = G_k² G_k, where G_k² is ordinary; S transposes by a whole-bank swap. Apply these wrappers to the already correct retained endpoint, with fresh owned initialization, rather than reversing destructive erasures. For a different coded main block, its actual reciprocal implementation must be supplied separately; equality of rank profiles does not establish it.

## 4. Source-bound Gaussian example and its honest debit

Literal reading of the PR5402 backward source's final scalar cleanup gives a useful nonprincipal pivot. After its final proper request on main owner 18 and the indicated cleanup, the original helper owner 226 has final value −4u₁₈, where u₁₈ is main 18 immediately after its terminal rank-1 request. This owner is outside the 122-H9 helper-basis support. Retiring its original rank-9 input therefore makes that final helper output zero, so u₁₈ = 0.

The local suffix calculation is explicit. Let a be current helper 226, d be current main 40 and e be main 18 before the suffix operations. The three updates

    226 += 40;   40 -= 226;   226 += 40

send 226 to d and 40 to −a. Then

    226 -= 18;   18 *= −4;   226 += 18;
    18 -= 226;   226 += 18

send helper 226 to −4e. There is no later reference to that helper in the source. These are literal scalar operations, with their actual full-frame interpretation; no inverse matrix was numerically computed.

Main 18 has no incoming write between its earlier rank-4 request followed by `18 -= 92` and its terminal rank-1 request. Main 92 is already at that actual rank-4 output frame. Thus Theorems 3–4 permit removal of the terminal H1 and replacement of the preceding H4 output by the current main-92 value. This is a concrete source-level use of a retired row whose pivot is a different current owner.

Its isolated inventory change is paid −H4−H1 and productive debit −H9. Therefore its change is 4^t + 1 − 9^t. It is not supplied as a profitable cohort or a κ improvement. The final physical owner binding and all normalizers must be retained from the exact standardized source; the example is a source-level reconstruction contract, not permission to apply it to a different emitter by event number alone.

An attempted additional deletion on owner 288 was rejected during source binding: the **modified** raw word contains a new COPY into cache C8 immediately after its H4. Looking only at the predecessor SOURCE-WORD missed that live reader. The cache subsequently feeds the main center correction. The H4 is therefore not deleted or counted here. No abandoned saving enters (2) or a headline.

## 5. Finite implementation and precision

All matrices in Theorem 1 are fixed before the external input size grows. If the specified pivot inverse has effective finite rational coefficients, ordinary reconstruction uses finitely many scalar field passes and initialized arrays; an odd denominator requires an explicit finite-precision coefficient routine and its charged error, not a free exact division. Dyadic pivots avoid that extra arithmetic issue.

For each fixed program, take a finite product bound K on its elementary operator norms, including reconstruction and suffix inverses when used. Let M count actual rounding sites and V bound scalar coordinates at a site. Coordinate error at most 2^(−B) per site gives final Euclidean error at most K M √V 2^(−B). Thus

    B ≥ P_target + log₂(KM√V) + 2

is sufficient for the displayed output error target, with separate scaling for coefficient errors and the actual input-magnitude envelope. If log V, requested precision, log M and input-range bits are O(p), the guard requirement is O(p). The field-volume conversion is retained.

This is a sufficient all-width finite-error construction. Its new scalar fees, owned stock, word widths and exact outer compiler parameters must be proved for a claimed exponent. An exact Gaussian-query saving alone does not establish κ ≥ 0.0035.

## Predecessor credit

The actual Gaussian word and phase-bound interfaces are Dillon Amburgey's PR5402, Chris R / Clear1nsight's PR5407 and PR5413, Ali Romman's PR5383/PR5398 relations and controller, Cinna Davis's PR4694/PR4698 center/helper lineage, Cao Yifan's native construction, and the retained Clifford, compiler, precision, BIT and analytic sources. The original source and the changed cached word are different frozen artifacts and must remain distinguished.

The linked Schur-elimination and symplectic transporter notes are design precedents for explicit block recovery and physical support. They do not prove an uninspected source pivot or a profitable cohort. The construction here is ordinary elimination on known zero autonomous outputs, with arbitrary current pivot columns, exact deadlines and a complete productive debit.
