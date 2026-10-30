# Eight shared-library bridges and nine mathematical concepts

These are actual source statements or explicitly labelled design precedents.
The new sufficient proofs are fully written in PROOF.md; none relies on an
unavailable spectral oracle or an assumed unknown circuit. Exact current source
hashes and historical evidence distinctions are in LIBRARY-BRIDGES.json.

| Shared source | Reusable fact or concept | Concrete use here | Limit |
| --- | --- | --- | --- |
| SchurBlockElimination | two-sided Schur system elimination | principal inverse deletion and bordering | Already used in PR3851; no novelty claim for Schur. |
| woodbury-reactor / typed DAG | `woodbury_two_sided` | a two-column/two-row update and 2×2 inverse replace a dense inverse | Historical audited algebra; combined cache is informal. |
| RobustRealTIFrames | `relative_frame_error`, exact orthogonal frames | source-label permutations transport inverse/error without changing norm | Arbitrary positive D is NOT orthogonal. |
| RobustRealTIRecovery | `pack_norm`, coordinate bijection | tensor/column flattening preserves squared energy | Does not prove spectral recovery or supply frames. |
| IntegerTensorBlockNorm | `block_energy_prefix`, `total_energy_bound` | correlated blocks use maximum local amplification, not total unrelated work | Separate inverse applications, not an unbounded product. |
| LiGuanCNOTFallout | generic `word_map` and injective word transport | fixed caller-port embedding preserves the same local-map sequence | Uses only generic monoid lemmas, not F₂-only recorder algebra. |
| MultitapeFrameRule | `FootprintedRuns.frame` | direct finite-memory exterior-frame proof and dirty-value controls | This API is not a new Lean multitape program. |
| MultitapeLocality | finite-region observational dependence | immutable old-H and injective finite port contract | Design precedent, not an instantiated new execution certificate. |

The additional numerical concept is an actual residual-to-recovery certificate:
check the full rational residual against the exact weighted old-H matrix before
asserting a numerical tolerance. It follows the shared robust-recovery practice
of checking the returned object itself; the inverse-specific proof is new here.
The exact coefficient-height/minor argument and diagonal similarity cancellation
are retained from the Gaussian predecessor, not advertised as unused inventions.

The submitted cache, two-sided residual check, weighted rounding, port-map
implementation and tensor/block controls instantiate the first six algebraic
patterns and a direct finite-memory frame. The two multitape sources remain
explicit design precedents; their Lean execution theorems are not newly applied
to this host-language algorithm. We do not inflate that boundary into a formal
tape result merely to increase the source count.

## Search coverage and unused status

The existing authoritative source catalogue contains 401,769 registered modules.
Twenty broad source queries retrieved at most 100 hits each, with bounded
MathProof-specific follow-ups; twelve typed-DAG/symbol queries and six indexed
note searches were also performed. Sources include the federated project,
downloaded libraries and registered archive notes. This is broad retrieval,
not a complete inspection or semantic search of every registered statement.
The first unrestricted ranked source query was bounded after slow common-term
search; the bounded indexed replacement preserved explicit limits.

Actual source inspection then followed the eight bridges above, the local
Woodbury mission/proof, current Gaussian source and precise predecessor APIs.
The private search packets retain indexed paths, revisions, snapshots and misses.
Only the sanitized provenance needed for review is published here.

Schur, weights, minors and Neumann reasoning are demonstrably already present
in PR3851. The scoped Woodbury sliding-cache application, its weighted residual
and fixed-port/block contracts were not located in the inspected project sources
or the 575-open-PR body scan. That is a bounded overlap finding, not a guarantee
that nobody has applied any of these standard ideas anywhere in the project.

A later actual-source comparison found that RaD's retained
`review-reusable-banded-inverse.md` already uses Woodbury for a circular wrap
correction and shares setup across right-hand sides. That predecessor is
explicitly credited. It does not describe the one-index principal-set deletion/
bordering cache checked here. Our claim is this scoped composition, not first
use of Woodbury, residuals, setup reuse or weighted Gaussian inverses.
