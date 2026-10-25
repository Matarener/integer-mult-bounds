# Shared-library and predecessor bridges

The source catalogue was queried across its registered collections for
`swap tape`, `FootprintedRuns`, and `dirty restore`, with at most eight
hits per query. The canonical frame, locality and commuting-phase sources
were inspected directly; exact hashes are in LIBRARY-BRIDGES.json.
This is bounded retrieval, not exhaustive library coverage or novelty.

| Precedent | Use in the new sufficient construction |
|---|---|
| MultitapeLocality20261014: `moveOffset_unit`, `step_locality`, `act_preserves_unscanned` | Guides literal unit-step semantics and the local scan invariant; every new template is proved directly. |
| MultitapeFrameRule20261014: `FootprintedRuns.frame`, `compose`, `lockstep` | Guides arbitrary dirty exterior, independent origins and paid composition; each stage restores the actual entry heads and buffer. |
| CommutingPhases: `xor_translation_commutes`, `raw_phase_translation_commutes` | Guides bitwise XOR composition and the explicit endpoint operator equation. Its raw phase convention is not silently identified with normalized C_q. |
| Same module: `gauge_phase_noncommuting_witness` | Prevents moving the correction through arbitrary native gauges without another proof. |
| PR3879 literal runner and dirty-record proof | Reused unchanged runner; new chunk-streaming compiler replaces repeated long single-record excursions by larger restored exchanges. |
| PR3480 and PR2297 | Source-pinned residual masks and actual C_E² handoff. Each bank is corrected separately; no shared-register cancellation is assumed. |
| PR1921/PR1958 and merged paid-permutation precedents | Related arithmetic/framing/compiler results, with different entry and restoration contracts. They prevent any first-use claim for tape XOR or paid address permutations. |

No new typed-DAG composition, compatible combined Lean import environment,
kernel run or transitive-axiom audit is claimed. A previous typed-DAG lookup
for the frame declaration returned only a `source-catalog` entry with null
typed/axiom fields; this round's source hits are likewise used as source
evidence only. The universal theorem is the explicit informal argument in
PROOF.md with the exact new transition table and resource formula.
