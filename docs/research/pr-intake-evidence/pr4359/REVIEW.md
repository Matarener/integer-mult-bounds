# PR #4359: productive helper jobs — targeted review

Reviewed source: [zxv's PR #4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359),
commit `da637c87c89482bc4c86be36bd0071b3d400dbed`.
Status: **partially reviewed; not admitted as the selected result**.
The proposal claims conditional κ = 23/10000. No source, selected-result,
README frontier, GitHub approval, merge or closure is changed by this review.

## Mechanism and attribution

The construction counts autonomous completed transforms on arbitrary helper
inputs as productive jobs. It then compiles the unequal-rank jobs into a
uniform supplier. The finite compiler builds on Jacob Alan Sussman's
Theorem 1G / PR #4268; zxv supplies the proposed native binding, controller,
delayed BIT cover and outer transfer. Retained local-word and outer-supplier
predecessors keep their source attribution.

This changes the helper endpoint obligation, so exclusions requiring every
helper to return unchanged do not automatically apply. That observation is a
reason to audit the new interface, not evidence that its bound is proved.

## Completed review scope

The imported source manifest authenticates 365 scope files and 16 canonical
main inputs. The check-only runner passed its source/claim bindings and exact
outer arithmetic. The smallest claimed outer slack is exactly
`98849/50000000000` above `23/10000`.

The accompanying `VALIDATION.json` records the successful fresh serial critical replay: all 23 stages passed in
410 seconds, and all 59 artifacts matched after the declared normalization
(none matched container bytes exactly).
It reruns the submission's checkers; it is not a second implementation of the
whole theorem. Generated compression bytes are not required to match: the
runner compares decompressed payloads with documented timing/environment and
transitive generated-hash normalization. The frozen inputs are reauthenticated.
The run uses Python directly, with no Lean, Docker or concurrent heavy suite.

Read and inspected the finite precompilation argument, ownership audit,
delayed BIT cover, finite-template closure, outer-transfer audit, critical
runner and selected owner/cover code. In the checked accounting:

- 2,856 local complex helper occurrences are distinguished from 1,570 fresh
  independent helper outputs. Uses hosted in idle windows of existing main
  arrays do not become additional independent source arrays.
- For a concrete trace, fresh owner `G0:371` has a rank-five native job on
  axes `[1,2,4,8,16]`. Its rank-six productive endpoint is accompanied by a
  paid rank-one top-up on axis `[32]` after stage zero.
- Owned copied centers receive no productive-output credit. The universal
  compiler allocates separate centers to simultaneously suspended instances.
- The proposed BIT bridge compiles the complete finite word before taking
  one ambient cover. It retains a common external weight independent of the
  fresh cover coordinate and lowers only the final rank-one leaves.
- The winning uniform programs are algorithmically specified at enormous
  fixed ranks. The small materialized examples do not attain their savings.
  This review has not materialized those winning programs.

No concrete failure was identified in this targeted pass. That is a scoped
finding, not acceptance of all universal arguments.

## Remaining admission gate

Before changing the selected frontier, complete an independent proof-level
review of the new interfaces, with an explicit obligation-by-obligation verdict:

1. The native words' autonomous endpoints and arbitrary-column lifts satisfy
   every whole-job hypothesis of the integer compiler. All simultaneous slots,
   complements, copied centers, adapters and restorations are counted.
2. Delayed covering is compatible with the retained fixed-tape routing lemma
   for the entire compiled word, including rational matchers, weighted leaves,
   bad-class fallback and stock restoration.
3. The new semantic precision and simultaneous row-reserve bounds meet the
   support-local outer wrapper, with constants fixed before input length varies.

These arguments are supplied by the PR; they are not requests for missing
files. Finite replay does not discharge their universal quantifiers or the
inherited analytic and machine-model assumptions.

[PR #4404](https://github.com/CrocSwap/integer-mult-bounds/pull/4404), reviewed
as supporting material at `77f20afb7c24286937c75cb65a7f19e24e7a567f`, reports
separately implemented mixed-flow and explicit-rank arithmetic checks. Its own
scope excludes the native, adapter, tape, precision and outer obligations above.
Do not infer its author's acceptance of #4359, or count it as a full audit.

## Reproduction and invalidation

At the reviewed PR head, run
`python3 -B research/kappa-0023-productive-jobs/verify.py --check-only`, then
`python3 -B research/kappa-0023-productive-jobs/verify.py --out NEW_DIRECTORY`
in an isolated source tree. The output must not exist and must be outside it.
Use `IMPORT.json` for the source closure. The local run extracted that closure
with `git archive` and left canonical inputs unchanged.

Reuse this receipt only for its exact source bindings and stated coverage.
A changed native word, compiler, bridge, source closure or outer dependency
requires a targeted delta review. Further work should begin with the three
admission obligations, not repeat the unchanged critical replay.
