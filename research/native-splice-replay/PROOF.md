# Sufficient whole-word assembly and all-input replay

## Theorem 1: guarded common-chart replacement preserves arbitrary contexts

Let a finite native program contain disjoint contiguous windows consisting only of linear scalar operations in a common chart. Suppose each replacement uses only the same persistent roles, preserves the original common chart, and has exactly the same local linear map on every original input basis vector. Then replacing those windows preserves the complete program's ideal logical map for every initial state, including arbitrary dirty inputs, helpers and owned state. It requires no additional field and preserves the exact sequence of all non-scalar events.

Proof. Equality on all local basis vectors implies equality of the linear maps on arbitrary data. Exterior fields are untouched. Thus each window and its replacement produce the same entire state at the window boundary. Apply the unchanged suffix to that equal state; repeated substitution over disjoint windows proves the whole result. The guarded installer verifies source hashes, window indices, role injectivity/disjointness, matrix coefficients and exact basis-vector equality. It emits every event outside a selected window with exactly the same parsed event payloads. It then independently checks exact non-scalar chronology and field inventory. ∎

No assumed unproved oracle or recovery gadget is used. The replacement maps are checked directly; the adapter construction is credited to #4502 and the gauges to #4499.

## Theorem 2: the free-word replay is an all-input sufficient certificate

In the retained ideal model, initialize each of the 632 persistent inputs and the owned C input as an independent formal variable. Express every register as a finite dyadic linear combination of these variables acted on by reduced words in free invertible warp symbols. Scalars perform exact linear combinations; a warp prepends a symbol and cancels its inverse; a clear sets an owned register to zero; chart transport changes the declared tag as specified by the retained interpreter. No commutation of unrelated warp symbols is permitted.

If the complete final formal rows equal the target identity shear, every helper's initial variable, and zero for owned C, the program has that action for arbitrary initial data in every representation of this ideal linear/free-warp model.

Proof. Induct on the program length. Initialization is the formal identity matrix. Each permitted event transforms the formal row exactly as it transforms the represented data; free adjacent inverse cancellation is valid for any invertible representation. Equality of all formal coefficients therefore implies equality of the represented linear maps on all inputs. The finite coefficient check is universal in the data; it is not a collection of numerical test vectors. Clear remains linear and does not require a clean owned entry. ∎

The verifier executes both pinned original and rewritten words with the retained prefix evaluator and a separate retained literal interpreter loop. The declared matrix parameter H in the generic prefix evaluator is set explicitly to I; the receipt labels the endpoint identity-shear. Every persistent target receives its corresponding source in the forward orientation, with the appropriate negative transpose shear backward. All 408 helper fields return unchanged, and the original owned C field exits zero. This is ideal chart semantics; the physical Clifford/phase and rounded-error boundaries are not silently discharged.

## Theorem 3: the rewrite retains the paid profile and stock

Because all changed events are scalar operations on existing persistent roles in their current chart, the exact ordered lists of climb, center, warp, adapter and residual_adapter events are preserved. Their paid profile remains `{1:2487, 2:713, 3:232, 4:102, 5:28}`, with 3,562 calls and rank mass 5,157, and no new owned or external field. The original one owned C field remains distinct from the zero *additional* field claim. The interpreter checks every scalar contact and transport frame against the pinned canonical chart. ∎

Surviving event indices shift. `retained_event_segments` gives each unchanged original interval and its new starting index. Every non-scalar event is checked to occur in exactly one such interval, with its full payload unchanged. Indices inside replaced scalar windows have no one-to-one image and are deliberately excluded. This is an explicit rebinding map, not a claim that every downstream phase receipt has been regenerated.

## Theorem 4: the complete scalar allowance falls by 100 per orientation

The four disjoint original windows cost 766 per orientation. Their fully charged replacements cost 666. The unchanged events contribute the same allowance, so the whole difference is exactly 100. The full forward bill is 158,120 → 158,020; the backward bill is 158,168 → 158,068. Both full sums are separately replayed and agree between the two retained loops. All SCALE/unscale and borrowed uncomputation costs are included. ∎

## Global ideal prefix envelope

Replacement endpoints do not by themselves bound new intermediate states. Therefore the prefix evaluator replays every original and rewritten event, tracking the exact formal row ℓ₁ norm, absolute coefficient, reduced numerator and denominator. It starts with the initial identity rows and updates maxima whenever a row changes; unchanged rows cannot introduce a new maximum. Frame-only transport leaves logical rows unchanged. Consequently this covers all rows at every ideal prefix, including inside the new windows.

Exact arithmetic gives identical original/rewritten maxima: forward `(457,32,32,32)` and backward `(169,5,21,64)` in the order above. These are finite exact bounds for the complete words. They are not a proof of the error incurred by rounded arithmetic: suffix amplification, error injection, recursive precision, physical receipt consumption and the complete multiplication recurrence remain separate obligations. No new κ follows here.
