# G20 controller-query rank binding

**Independent source-bound verification; no new multiplication bound.**
PR #5955 explicitly takes the WHOLE_IDLE and THIN controller ranks as given.
This checker derives those ranks under the retained G20 coordinate model,
then matches every controller-level QUERY in both #5679/#5708 literal streams.
It complements #6042's MAIN target-rank check; it does not repeat that audit.

Each candidate has **4,995** controller queries: **3,330** whole-idle jobs
and **1,665** thin jobs, with total rank mass **124,431**. Their ordered
controller components agree exactly. RESULT.json records the full histogram.

## What is checked

The retained address model is a central line plus disjoint seven-dimensional
blocks for the thick stages. Multiply the diagonal stage reflections on every
coordinate. An idle on S acts as -1 exactly on its selected stage blocks;
P=(I-R)/2 has an identity minor on those columns and zero elsewhere. Its
address-projector rank is 7|S|. The central reflection instead has rank one.
These are native job ranks, not ranks of FUNCTION permutation matrices.
The code evaluates the signed coordinates rather than reading an invoice rank.

The controller determines the chronological sequence of query kinds, stage
sets, original banks and 111 ports per bank. Every corresponding GLOBAL record
must have that identity and derived rank. For each thin query, the checker
also requires the literal copy/query/delivery/owned-clear sequence, the correct
source and destination under either controller orientation, and clean owned
scratch before copying. Cleanliness is conservatively tracked from explicit
CLEARs; arbitrary cancellation-to-zero is not inferred. Local native queries
are excluded from the component, not repriced or newly certified.

A thin episode on clean owned scratch computes y <- y + Zx while preserving
x and returning scratch to zero, under the retained complete linear-job and
erasure contract. The checker binds that declared episode; it does not newly
implement or admit its physical COPY, query, erasure, ROW or tape operations.

## Reproduce and evidence

```sh
python3.12 -B scripts/research_package.py --package research/g20-controller-query-ranks
```

Expected marker: `PASS_G20_CONTROLLER_QUERY_RANKS`. Both registered commands
use 60-second limits and only the standard library. Normal and optimized
checks authenticate eight inputs before parsing, run both actual consumers,
and recompute the committed result. Self-contained tests cover multiple port
counts, both orientations, projector boundaries and 17 semantic mutations;
two actual-stream wrong-rank controls and changed-source rejection also run.
No predecessor implementation is imported. Ordinary verification writes no
package output; `--write-result` explicitly regenerates the receipt.

The checker retains the physical orthogonal-block/native interpretation,
all-column/whole-job adapters, ownership and erasure contracts, and compiler,
stock, precision/tape and outer assumptions. It does not replay the global
FUNCTION endpoint, prove native faithfulness, certify every paid local rank,
change an invoice, or admit BIT. Hosted CI is separate from local evidence.

## Sources and credit

Base a5bff3bf133e482541c09eba4e773884bdb2b1b7; exact source bytes and Git pins
are in SOURCES.json. The source constructions are Ali Romman's #5679 and
#5708 with Dugongue, ai-nanachi and the retained G20/controller/native lineage.
Matarener's #5955 supplied the explicit unchecked input. JoyboyBrian's #5039
already proves related charging for the complex 112-port/eight-dimensional
stage contract; this result is the specific G20 111-port/seven-dimensional
component and its two literal candidate streams. The rank formulas are standard,
not claimed as new mathematics. No frozen source or selected record changes.

## Open next questions

Bind one exact G20 job to its physical all-column/spectator/ROW and
routing contract, with every fee and borrowed return. That separate native
review is required for admission; the structured question is in TASK.json.
Coordination: https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19273649

New implementation and explanation by Dennis / antunishdPursuit with substantial
OpenAI Codex assistance, no subagents. Apache-2.0. No independent human or
formal proof-kernel review is claimed.
