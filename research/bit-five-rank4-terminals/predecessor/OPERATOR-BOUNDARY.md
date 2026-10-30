# Five rank-four terminals: exact stream boundary and remaining admission

The independent finite audit passes for the word with uncompressed SHA256
`3bca74a2a8427eb18e86566baa19de597f10d0bc40c30b7443febd499ee2189a` and geometry
SHA256 `a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022`.
This is a new local mixed-terminal operator under the exact stream operations
below. It is not an improved conditional kappa or a completed supplier admission.

## Predecessors and changed interface

The source is the pinned R438 transported word. The generic frame simulation
argument is credited to PR540 FramedReplay/OwnerTransport and its source-bound
PR589 extension in `research/pr589-five-helper-hosting/PROOF.md`, at canonical
20ecf2891d80b5acf18d980b2164fb44ea7faa90. The new construction moves helper
preconditioning to ZERO and replaces the old FULL literal A/B cleanup by an
early SOURCE cleanup plus a different signed tail. It therefore must not claim
that the old syntactic H4 checker passed unchanged.

PR1194 (2e39c98238f543d988f9efc1b076590a4b780dca) and PR1311
(a2875c1834b9c9ef42a84eda4890d5462cc98fa5) are relevant semantic-prefix
predecessors. Their stated substitution preserves H4; they do not directly
admit these changed terminal frames and cleanup. The novelty here, if retained,
is the explicit source-bound word, not elementary preconditioning or the
generic simulation lemma. Existing complex-side heterogeneous restoration in
`research/e8-prefix-restoration` is also prior art for that general mechanism.

## Exact stream interpretation

For a frame projector P on K^8 define the address involution

    D_P(x,y)=((I-P)x+Py, Px+(I-P)y).

Here K is any field of characteristic other than two. The independent checker
constructs all636 actual rational projectors by Gram-Schmidt, verifies their
dyadic entries and basis identities, and checks all2394 nested pairs used by
the word in either orientation. Idempotence and symmetry follow directly from
the orthogonal-basis formula. If P<=Q, their relative operation D_P D_Q is the
partial swap D_(Q-P), with rank dim(Q)-dim(P). Its exact rank survives odd
characteristic specialization: the dyadic characteristic polynomial of each
idempotent is t^(8-r)(t-1)^r. This supplies exact address operations, not their
physical compiler or tape implementation.

Take660 arbitrary Boolean-valued input functions, one for every persistent
source, target and helper. The one private function starts zero. For each row
i let Gamma_i=D_Pi at its current frame and let the decoded function be
c_i=f_i composed with Gamma_i, where f_i is the physical payload. These are
bookkeeping bijections; no input is reset or assumed independent in value.

A MOVE from Gamma_a to Gamma_b transports the physical payload by
Gamma_a Gamma_b^-1, so it preserves c_i. An ADD at a common frame changes the
decoded destination by the decoded source. Signed integer ADDs give the stated
integer lift; their reductions are XOR for Boolean values. A fresh COPY
transports the source into the private frame and copies its decoded function.
Every ERASE in the candidate sees precisely that unchanged decoded source and
the corresponding private snapshot; bijectivity yields the physical equality
needed for erasure. The private row is zero before its next reuse.

Induction over every literal event therefore gives the decoded matrix checked
by `verify_word.py`. That independent implementation imports no producer or
predecessor checker. It tests all660 independent persistent input columns,
the PRIVATEZERO contract, exact integer source/helper restoration, the Boolean
public shear, and both signed forward/inverse roundtrips. The statement is for
all input functions, including arbitrarily correlated dirty helper contents.

## Endpoint

The source/target entrance and exit frames equal the old CLEAN R438 frames,
and the decoded Boolean endpoint is x'=x, y'=y+x. Thus their physical public
operator is unchanged. For helpers462,463,464,467,470 the decoded value is
exactly its original arbitrary helper value, but its physical residual is
D_E for the explicit terminal rank-four frame E. The other433 helpers retain
the old rank-eight residual. No dirty output is discarded, and no initial
native query is hidden in the1765 ZERO helper ADDs.

In a reflected embedding, replace the local gauge by D_(I-P) times the shared
exterior factor. The relative endpoint from frame0 to E is still D_E, since
D_I D_(I-E)=D_E. The same induction and signed inverse apply. An actual owner
must map each E residual into its assigned pending coordinates; rank alone
does not construct the required orthogonal chart or chronological placement.

The complete local histogram is

    H={1:1322,2:1342,3:79,4:39,5:102,6:11,7:18}.

Its rank mass5101 equals111*14+433*8+5*4+63. All36005 ADDs and nine rank-seven
COPY calls remain paid. The lost20 helper ranks exactly equal the removed
query mass; they are not an extra unearned deficit.

## Gates still open

The conservative forward/reverse positive envelopes are8402567 and630744.
The inherited expressions64 F^3 R^2 and2^18 F^5 R^4 require114 and211 bits,
respectively, and fail the old104/192-bit caps. Exact signed prefix row norms
1302 and1446 are recorded diagnostics, not an automatic replacement for the
old defect and COPY/ERASE error analysis.

This proof closes the arbitrary-input endpoint in the stated exact stream
model. Explicit residual isometries, whole-owner chronological hosting,
physical scalar/address routes, rounded-child errors, precision charges,
all-size dispatch, storage/tape costs and joint outer assembly remain separate.
The checker is finite exact evidence; this document is a written induction,
not a formal-kernel certificate. No new kappa is claimed.

Apache-2.0; substantial OpenAI Codex assistance.
