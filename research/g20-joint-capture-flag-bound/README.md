# All-subset bound for G20 first-read helper captures

**No new κ.** On the exact PR5708 word, simultaneous first-read capture of
**any subset of all 415 retained helpers** cannot improve the local BIT signed
moment for `0 <= C <= 0.01` (`t=1-C`). This includes the 180 helpers with an
early rank-2 query and both partial rank-4 helpers. Every captured rank-8
helper loses strictly more than `(5/128)*4^t` in the optimistic bill. Subsets
containing only partial helpers have gain at most zero.

The result grants arbitrary native-linear injected payloads and free setup,
source access and restoration. It closes a fixed-schedule larger-set question
left by [PR6113](https://github.com/CrocSwap/integer-mult-bounds/pull/6113), so
further work on this mechanism must change that schedule or another stated
premise. It is a scoped negative result, not an improved supplier or a general
impossibility theorem.

## Evidence and what is new

[PROOF.md](PROOF.md) reduces capture to an entry substitution on constant-input
parities. Its kernel projects injectively onto captured coordinates. A new
**flag-constrained weighted partition** respects three different helper tariffs:
64 unrestricted independent colors, 28 avoiding partial-helper coordinates,
and 16 also avoiding early-rank-2 coordinates. This prices all subsets without
enumerating their payloads. Exact integer powers extend the comparison over
the full exponent interval; there is no floating-point acceptance decision.

[PARTITION.json.gz](PARTITION.json.gz) covers 64,274 tokens from 2,216 queries
and 1,945 rows. In particular it includes three cross-helper early queries
(6231, 6291, 6510) that cannot simply be excluded from a uniform token census.
[RESULT.json](RESULT.json) records the exact counts and row digest.

PR6113 supplied the native-payload/individual-capture model, single/pair census
and an unweighted token bound, but explicitly left larger sets with multiple
rank-2 frees open. Its numerical pair findings are not contradicted here.
PR5604's entry-subspace capacity bound concerned a different, static model
and older word. This package adds a dynamic first-read graph-kernel argument,
a tariff-sensitive certificate covering all helper sets, and exact uniform
moment inequalities. No predecessor implementation is imported.

## Reproduce

From the repository root, using Python 3.12 and only its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/g20-joint-capture-flag-bound
```

Both normal and explicit isolated optimized runs must print
`PASS_G20_ALL_SUBSET_FIRST_READ_FLAG_BOUND`. Each run authenticates the three
live inputs, checks all 14,794 events, compares integer-mask and set replays,
checks every token and both Gaussian-elimination directions, verifies seven
entry-substitution fixtures, and rejects eight corruptions: omitted tokens,
duplicate/dependent color rows, both wrong flags, omitted cross-helper event
6291, a forged query rank and changed source bytes. The fixtures support the
written lemma; they are not a proof by exhaustive testing.

The optional deterministic discovery command is separate from verification:

```sh
python3.12 -B research/g20-joint-capture-flag-bound/discover.py /tmp/g20-partition.json.gz
```

It stops at the first verified 108-color partition, a 1,200-second deadline,
or exhaustion of its augmenting-path search. A timeout/failure is not an
impossibility claim. Reproduction compares decompressed JSON, not gzip bytes.
The successful discovery used 2,062 augmentations after the greedy stage.
The verifier requires neither discovery nor any third-party solver.

## Pins, boundaries and coordination

Scientific and branch base: `721c03822c421b7f7fcbb2598993b947c4d88419`.
[SOURCES.json](SOURCES.json) pins the exact word, frames and local invoice by
Git blob and SHA256. Historical predecessor heads are PR5708
`829d01fc031f7323ffcfa423fdfd1f24dcbe3190`, PR6113
`f6712095d07d555969b6e67b792a0e98e8eea8d3`, and PR5604
`b7c27a263b9e57d4e04b5e2dcb7b3199cc8c4170`. PR6113 is a credited research
lead, not a live executable dependency. The selected certificate at the base
is PR6030, conditional κ=781451/250000000; no selected record is changed.

Only first-read individual capture schedules, coordinate ownership, native
permutation-linear payloads and this exponent interval are covered. Later
joint-dead captures, changed words and other input contracts remain open.
Native/adjoint endpoints, the complete caller and recursive construction were
not replayed. The selected theorem's native, owned-erasure, compiler,
precision/tape and analytic-recovery assumptions are unchanged. This is an
exact certificate plus a written proof, not a formal theorem audit.

[TASK.json](TASK.json) records seed 08 (bit supplier), three candidate tasks,
scope selection, checkpoint freshness and overlap limits. The local overlap
inventory covered 8,348 research records; connected GitHub reads covered the
latest 100 open PR bodies, focused searches and predecessor heads. Visible
handoff posts were checked, not all discussion pagination or PR code diffs.
No pinned sprint issue was found. The available connector cannot post to
Discussions and the browser was signed out; an advance claim was recorded
locally at 10:39 UTC rather than represented as a public reservation.

## Open next questions

- Can a jointly dead interval support a **later** reinjection whose complete
  target and paid bill improves? Start with a triple extending PR6113's five
  joint-dead pairs; emit an exact changed word and native endpoint before a
  large search. The present graph-kernel proof does not apply after propagation.
- Can this flag-certificate technique bound a different changed word? First
  recompute early tariffs, query rows and projection flags on its exact source.
  The current witness cannot be transferred by matching aggregate profiles.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Credit

Jerry Chen (@CubeJerry), with substantial OpenAI Codex assistance in research,
proof drafting, implementation and verification. No subagents. Apache-2.0.
Credit Matarener for PR6113 and its explicit larger-set handoff; Ali Romman for
PR5604, PR5679 and the PR5708 word; ai-nanachi for PR5512's G20 construction;
and Dugongue for the underlying refinements and late-binding work. The source
packages and their original notices are unchanged. Binary matroid partition
and augmentation are standard methods; the source-specific flag allocation,
all-subset proof and finite witness are this contribution.
