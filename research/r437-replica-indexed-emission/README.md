# R437 replica-indexed emission and the physical catalogue boundary

**Partial result: complete finite local-IR emission; physical CALL/RETURN open.**

The first cross-replica move in Rohan Arun's PR #3959 cannot enter the retained
physical catalogue: stage 6/replica 1/helper 421 changes family 1097/offset 0 to
family 209/offset 16, violating the catalogue's exact replica symmetry. We execute
the actual retained guard to establish this, and supply a bounded absolute-owner
IR adapter for all 63 proposed moves. The retained emitter and its separate
retained audit encoder agree on all 7814016 events. All 125856 hosted roles and the
replica-indexed idle invoice are checked. See RESULT.json for the changed-event
count and new stream digest, and PROOF.md for the exact source boundary,
arbitrary-value/dirty-state transport lemma and complete obligation ledger.

This adds an executable emitted-IR binding beyond PR #3959's static map. It does
not implement a replica-aware physical catalogue, run a pooled native body or
claim a new κ. The existing PR #3967 physical adapter and PR #3980 owner-chart proof
are explicitly unpooled. Their results remain credited and outside this result.

## Reproduction and pins

`python3 -B scripts/research_package.py --package research/r437-replica-indexed-emission`

The replay is standard-library-only, read-only and Git-free when exported. Five
retained computation inputs plus the source notice are self-contained, byte-pinned in PREDECESSORS.json and
checked against their original Git objects before publication. Template content
must also match the source digest in POOL-MOVES. Repository-level provenance is recorded in SOURCES.json. No native rebuild, whole historical
replay, Lean, external solver or network is needed. Six negative controls reject
stale owner, wrong replica, overlap, extent, pair and duplicate-key changes.

## Scope, overlap and expansion decision

Main20ecf2891d80b5acf18d980b2164fb44ea7faa90, priority revision6. Explicit donor
assignment refines supplier-boundary-audit. The parent session checked 679 live
open PR bodies and current active/handoff discussions on 2026-10-19, then added
PR #3980/3982/3983 deltas. Broader Discussion, closed and private coverage is partial.
Live predecessor heads were checked:3959 babd2e36471422cd3e97f912a5cf2846da52a222;
3967 32af060614fefa9729c86370524c2e72265acd76;
3647 a24f9ff95c12fd0b6792e3f710569237efd72db2. The canonical scoped claim is on PR #3959. The local overlap helper examined 2492 records at 08:09 UTC with no usable remote cache; the parent live snapshot supplies the open-PR coverage. Canonical main was fetched again at the publication checkpoint and remained unchanged.

Narrow to one physical refinement boundary. Stop after the bounded emitted-IR
certificate and literal factorization counterexample; do not run a larger
packing search or infer a selected-frontier change. The primary field is
reversible compiler refinement, paired with network capacity allocation and
compositional register transport. This is a mathematical pairing of distinct
obligations, not an independent human review.

## Open next questions

TASK.json records the scoped next questions. First, compile the actual
stage 6/replica 1/helper 421 source and native chart with replica-indexed semantics,
then execute its physical return and consumers with the complete bill. Only
after that join can the full pooled supplier's inherited obligations and both
supplier budgets support an admitted κ claim. Unknown physical routing,
preparation, scratch, precision or restoration costs are not zero.

## Credit and license

Rohan Arun, PR #3959/3958/3939, supplies the 63 moves, pooled profile and conditional
endpoint; this package claims none of that packing novelty. ai-nanachi, PR #3647,
supplies R437/OQ4 and its retained emitters. Credit Ali Romman/1043,
Sagar Thakrar/3700/2423/1023, mightyOil/1281, DaysSky/442, chafreaky/444,
DreamingOfClouds/510 and the e8-bit-p111 adaptations. Preserve eumemic,
545/543/555, Dylan Crow and the upstream lineage. The physical catalogue and
adapter lineage includes zxv/3690, David Arias/2753, Jose Manuel/jmbarrancoml
2809/2899/2915/3562, ywz65/2635, Nick Petalas/2808, alephnan, Adam Gall and
Ross Richardson; PR #3967 and PR #3980 are immediate unpooled predecessors.

New code, proof and writing by Chris R / Clear1nsight with substantial OpenAI
Codex assistance. Apache-2.0; retained source headers and notices are preserved.
Passing replay is a finite certificate, not formal-kernel or human acceptance.
