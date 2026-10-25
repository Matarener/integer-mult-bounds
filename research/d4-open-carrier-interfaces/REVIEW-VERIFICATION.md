# Exact carrier and source-control review

Status: PASS for the reviewed mathematical sources, authenticated runtime and
complete-record controls. The final package snapshot separately delimits the
integrated documentation and metadata.
This review is limited to the fixed twelve-port D4 geometry and the declared
local words. It does not complete C02, the unrelated C14 controller claims, a
P112-wide uniform-width construction or a recursive supplier.

## Mathematical review

The physical public boundary has blocks

```
W = [[S,0],[J,T]],
T = F C_p^-1 C_q^-1,    J = F X_p,    F = X_33 F_7.
```

For OPEN, S has native rank five; for the full-source variant, S=J has rank
seven. Their literal inverses and inverse-transpose duals follow by block
multiplication. In particular

```
W^-1  = [[S^-1,0],[-T^-1 J S^-1,T^-1]],
W^-T  = [[S^-T,-S^-T J^T T^-T],[0,T^-T]].
```

For a unitary native operator U, `U^-T` is its entrywise conjugate, so the
same-chronology dual replaces each native operator by its conjugate and each
signed ADD by the opposite-direction negative ADD. This is distinct from the
literal reverse inverse. All four orientations are explicit.

The native checker represents each of the 28 independent field columns as an
integer linear combination of exact Clifford operators. Equality of signed
Pauli images plus a phase-sensitive zero-state image identifies a Clifford
operator including its global phase. Matching each complete operator-valued
column therefore proves the map on all 28 times 128 ADDRESS basis inputs; it is
not a claim to have simulated every basis input separately. A changed operator
key alone is not a physical counterexample: rejecting mutations additionally
produce an actual Gaussian coefficient discrepancy on an ADDRESS basis vector.

The ordinary four-helper bus and OPEN have the same complete public block.
The bus's remaining four rows contain only their respective arbitrary helper
inputs through `H_j=F C_(q_j)^-1 E_A^-1`, each of native rank three. Thus the
local factorization is a direct sum. It does not turn the helper's transformed
output into literal restoration, nor allow the same helper progress to be
credited twice. Fixed-physical-slot rank-one helper query products and
moved-value rank-three helper channels describe different contracts.
Appending the four actual `H_j^-1` queries gives literal physical helper
restoration in all four orientations. Its four extra rank-three queries
raise the mass from 148 to 160. This is a separately paid tail, not part
of the mass-148 transformed-helper contract.

The normalizer proof checks the split-Lagrangian criterion: if
`r(S)=r(T)=n-d` and `r(S F^-1)=r(T F^-1)=d`, then `L(S)` and `L(T)` split
across the two transverse Lagrangians `Z` and `F^-1 Z`. Choose B mapping the
Z summands and let G=`B^-T`. The symplectic matrix

```
P = [[G,0],[G+G^-T,G^-T]]
```

preserves both Lagrangians and carries `L(T)` to `L(S)`. Its exact Clifford
lift uses `Q=I+G^-T G^-1`. Consequently P, its common-F conjugate and
`post=T P^-1 S^-1` are monomial. This written proof covers all dimensions
under the displayed hypotheses; it does not assert the stronger inverse-B
property for all such P.

For the four fixed h7 witnesses the latter property is separately checked.
With `K=T^-1 J P`, the complete inverse-B wrapper uses
`AB=T K^-1 T^-1 K^-1`, `BB=T AB^-1 T^-1`, and T squared on both outputs.
Direct multiplication gives the cross block `-T K^-1` and both diagonal
blocks T. The physical and logical kernels remain distinct:
`A=C_q^-1 K C_p=C_p^-1 P C_p`. The same logical pre-X and post-Y `A^-1`
corrections work in both orientations; their physical implementations use
their actual entry and exit frames.

The supplementary output-wrapper lemma is also correct in every dimension
under its native assumptions. Inverting AB yields
`BB=(T K)^2 T^-2=(F X_p P)^2 T^-2`. With `M=X_p P`,
this is `(F M F^-1) F^2 M T^-2`. The exact identities
`F^2=X_eta` and `T^2=X_(eta+p+q)` make all four factors monomial whenever
P and its common-F conjugate are monomial. Thus BB's monomiality is automatic
in that family; AB's rank-zero property remains the additional finite
witness obligation. BB still has to be executed and paid.

The normalizer's 32 rank-zero implementations are independently replayed on
all 128 ADDRESS basis columns each. Their lowering includes actual Gaussian
phases, not only binary symplectic matrices. The in-place cycle construction
retains every coordinate, uses one pivot swap per nonleader and pays three
ADDs and one negation per swap. Its written all-f tensor/cycle argument is
separate from the finite 4096-column replay and from a physical tape schedule.

The eight A/B ports have the explicit phase-free address normalizer
`R=I+w w^T`, where `w=q+r` is nonzero and isotropic. It fixes p and exchanges
q,r. Put `epsilon=wt(w)/2+1 mod2`. When `w·x=1`, the weight difference is
`wt(w)-2 wt(w∩x)`, hence `2 epsilon mod4`; when `w·x=0`, R fixes x.
Since the character eigenvalue of F7 is `i^wt(x)`, this proves
`R F7 R^-1=X_(epsilon w) F7` exactly. The zero character fixes the scalar
phase. Every actual row satisfies `w·33=epsilon`, so the translation in the
actual F cancels that correction and `R F R^-1=F`.

It follows that `P=post=R` normalizes the actual A/B source boundary.
The physical kernel is `K=C_q C_p^-1 R`, whereas the logical kernel and
both physical common-code corrections are R. The physical K is not an
involution. Also `(T K)^2=X_127`, giving
`AB=BB=X_(p+q)` and `T^2=X_(127+p+q)` with their exact phases.
These are the eight fixed star rows, not an assertion about unrelated ports.
Across positive f, R has `(2^(7f)-2^(6f))/2` two-cycles and every nonzero
lifted translation has `2^(7f-1)` two-cycles. Thus the unfused forward and
backward wrapper spellings cost respectively `2(N-2^(6f))` and
`4N-2*2^(6f)` swaps, where `N=2^(7f)`: 128 and 384 at f=1. Each swap is
paid as three signed complex ADDs and one NEG. The one extra magnitude-bit
bound is for that local swap's sum, not a whole-network precision theorem.

The star checker covers 1024 character cases and 8192 lowered monomial
basis-address cases. The latter uses the authenticated compiler's literal
evaluation; it is not an independent replay of all full native histories.
The separate native specialist's `REVIEW-STARS.md` records 96 independently
reconstructed exact identities across these eight ports. This source review
checked its final source/receipt pins and mathematical derivation; those
96 executed comparisons are that specialist's evidence, not this review's
additional run.

## Sources and executable binding

The scientific pin is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The source audit checked all 24
historical `FINAL-FREEZE.json` entries and identified the omitted elementary
`d4_geometry.py` dependency. Original source files are preserved as context;
the final wrapper does not execute their historical path-based loaders.
`SOURCE-AUDIT.md` and `SOURCE-CLOSURE.json` delimit the provenance and the
selected intact block's relation to the larger 120-label tiling.

The wrapper reads and authenticates each new checker once, then sends those
captured bytes to an isolated Python process. It compiles with
`dont_inherit=True, optimize=0`. Each checker also captures and authenticates
the exact compiler bytes before compiling that buffer with assertions
retained. Neither layer uses a bytecode cache to execute the scientific source.
The compact controls replace a disposable source path after capture and
confirm the captured bytes execute. Direct and nested assertions remain live.

The JSON gate rejects duplicate keys and nonfinite numbers and compares
entire canonical JSON objects, retaining Boolean/integer/float distinctions,
list order and nested fields. Each stage must compare its exact one-record
inventory with neither duplicates nor omissions. The expected records are
frozen inputs, never regenerated on a missing-record failure. Compressed
containers and their original decompressed bytes have separate digest checks.

All generated data and mutation fixtures use external temporary directories.
The wrapper checks its full frozen inventory before and after each stage.
No historical search, original geometry-generation main or unpublished
external dependency is silently invoked.

The reviewed runtime pins are:

| File | SHA256 |
| --- | --- |
| `verify.py` | `ff5e3a887ddfbb67ec2214a57b0b7d94c8fc78c7b01160f86d1fd509714989dd` |
| `check_native.py` | `6fbf626bc5712816045249fd4cbafc386949e65580514aa6b1b1b9517b1d03d0` |
| `check_normalization.py` | `5793faa7808220de3a84b5c9b6baaf1a9cbc224ee9de65de319c2d904316cf70` |
| `check_stars.py` | `2f02cee8b75f630851f3a6c4ab3014c43e119bf54ee7f0036300bc9c02d7c88a` |
| Complete uncompressed native receipt | `25bb13506c7a81f6a42699fb7eba8a256f065495bd373dfbd051163ca438b0be` |
| Complete uncompressed normalization receipt | `61f0e8c55c015a15ccfcd37a2086c17cb8e0735f28bea48cba789ea6151f8634` |
| Complete uncompressed star receipt | `d7a382016abfcf3a62ab13773cd1b09188c624c2b0e3bc93f53aeaac6e11008b` |

## Acceptance controls

The normalizer executes nine malformed operators per port through its actual
equality or zero-rank predicate. It records 36 intended rejections and four
executed phase-check deletions. A global-i error preserves signed Pauli images
and is accepted when only the phase comparison is removed; the scoped check
deletion therefore distinguishes tableau equality from exact operator equality.
The omitted-chirp rejection has an explicit failure on unexpected acceptance.

The native controls mutate actual emitted gates, including raw cleanup,
contact subtraction, delivery, dirty-helper leakage and a native return phase.
They must reject through the same all-column predicate as the valid word,
with an actual Gaussian basis witness and exact intended failure code.
An exception caused by a source hash or unrelated implementation failure is
not counted as a mathematical rejection.
The final native control set has 14 such endpoint rejections, three executed
phase-check deletions and one invoice rejection. The latter inserts a cancelling
ADD pair at a genuine common-frame delivery cut: the endpoint is still
accepted, while the shared full invoice predicate rejects 62 ADDs against
the claimed 60. Omission of an actual inverse query in the optional helper
tail yields an explicit helper-coordinate defect.

The star checker executes 28 intended equality-predicate rejections and eight
phase-guard deletions. The mutations cover output global-i phase, omitted AB,
and physical K substituted for its inverse at each port, plus omission of
the invariant-F translation at precisely the four epsilon-one ports.
Each rejection matches the named signed-Pauli or exact-phase gate; an
unexpectedly accepted defect raises outside its exception handler.

Compact wrapper controls exercise all three scientific receipts, including
deep nested mutation and omission in each. They also execute the authenticated
normalizer's production equality and rank predicates at port `(117,7)`, with
the actual output global-i and omitted-chirp defects. The gate extraction is
only a compact review test; the registered scientific stages execute their
complete main audits. Full-stage mathematical controls and compact provenance
controls are reported separately.

The final compact controls passed on the bundled CPython 3.12.14 in ordinary and optimized
outer modes, each of which also exercises ordinary and optimized child modes.
The complete two outer receipts are byte-identical. There are 53 intended
rejections and three executed check deletions per inner mode; all three full scientific receipts
receive nested mutation and omission controls. The native operator-index test
forces an index collision between distinct exact payloads and requires the
production collision guard to reject it. Fixtures reaching the actual native
and star compiler loaders confirm their nested assertions survive optimization.
Their deliberately changed compiler files first fail the intended byte-pin
checks; only a disposable module's fixture pin is rebound to reach its assertion.
`CONTROL-VALIDATION.json` records this validation without claiming another
complete scientific replay. Earlier two-stage controls on Homebrew 3.12.12
and 3.14.6 are preserved separately; they are not relabelled as three-stage runs.

## Limits and remaining owner

Tensor products preserve the displayed fixed local operator identities for
every positive chunk size. They do not make native-zero wrappers, scalar
scans, source access, storage, copying or physical head movement free.
The parent owns final package integration, repository gates, committed
Git-free replay and publication. Separate native and normalizer reviewers own
their full mathematical replays. Hosted CI and independent human or
formal-kernel acceptance are not established by this source review.
