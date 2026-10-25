# Current-head admission audit of staged544 and R437

This is a **partial admission audit, not an admission**. It contributes a new, import-free check of the R437 OQ4 template transition and records separately classified executions of the current R437 and staged544 T385 entry points. No selected-result file, construction, or frozen predecessor input is changed.

## Result and scope

The new checker compares PR3647's complete template at `36ff441479ff9c7e70d83f0becccd44da50effb8`, the head audited by Sagar Thakrar in PR3700, with the current `a24f9ff95c12fd0b6792e3f710569237efd72db2`. Both compressed templates are retained byte-for-byte with Git blob and SHA256 pins. No predecessor verifier is imported by `verify.py`.

A backwards schedule scan rederives the idle windows from the inherited last-touch rule. A coordinate-set occupancy check verifies all 3,933 slots per replica, complete stage/helper coverage, chronological eligibility, and contiguous residual suffixes. Both complete owner maps are rebuilt, including all 125,856 helper occurrences per head and every source/target owner. The complete recursive comparison finds exactly 69 changed semantic leaves. They are the two slot fields, three residual-histogram entries, and two fields in each of 32 stage-6 helper-422 owner descriptors. Every other field, including both local programs, their hashes, the schedule, data routes, cover description, residual isometries, and physical-stock declarations, is unchanged.

The one move is `[6,210,0,8,6,422]` to `[6,209,8,8,6,422]`. It gives the residual paid-profile delta `{26: 32, 34: -64, 42: 32}`, with zero change in child count or rank mass. Seven mutants are rejected by named semantic gates, covering overlap, capacity, chronology, one stale owner in the final replica, stale residual pricing, an altered local program, and an altered cover contract. The latter two pass the geometry gates but fail the exhaustive transition gate, preventing an older identity audit from being silently carried over a changed program.

`RESULT.json` is recomputed, not an author PASS receipt. Direct replay under normal and optimised Python produced byte-identical receipts. The proof-relevant inputs for this bounded check are fully retained here; no foreign PR commit needs to exist in the reviewer's local Git object store.

## Why the moment improves

Under the inherited invoice, write the rank-dependent part as

`M_H(c) = m^(c-1)/W * sum_r n_r*r^(1-c) + fallback(N,c)`.

Here `m = 64`, `W = 28416`, and `N = sum_r n_r`. Since the checked move preserves `N`, its fallback term cancels exactly. For every `0 < c < 1`, the function `x^(1-c)` is strictly concave, since its second derivative is `-c*(1-c)*x^(-1-c) < 0`. As `(26+42)/2 = 34`, the complete change is

`32*m^(c-1)/W * (26^(1-c) + 42^(1-c) - 2*34^(1-c)) < 0`.

Thus the direction of the improvement does not depend on rounded root values. This is conditional on the unchanged invoice and physical hosting interface, not a new implementation of those interfaces. The exact current endpoint `1736646042038446578551/10^24` and failure of its next grid point were also cross-checked using Sagar Thakrar's existing PR3700 rational engine. That reuse is explicitly separate from the new independent transition checker and is not a new price implementation.

## Executions and the unfinished staged544 audit

At the pinned current R437 head, the author's self-contained cold entry point completed all 13 commands in both a clean hosted Python 3.12.15 run and a local Python 3.13.5 run. This is independent execution of author code, not an independent reimplementation of the word or whole invoice. The new checker does not re-prove PR3700's word identity, COPY contract, or precision argument.

For staged544 T385, PR3802 at `de2cd5c58009205210e3bf328b0ef5cadf3903af`, the published `full_replay.py` was run with one job, a fresh work directory, pinned dependencies, and its declared native/ancestry reuse. The imposed 780-second limit was reached during `discovery/audit`. Top-level `owners`, `parent-lift`, and `rebind` completed with exit 0, as did discovery's `bind` and `emit` substages. The retained top-level status is `PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED`. No complete discovery, outer replay, final release, or independent staged544 admission is claimed. The timeout is not a counterexample to the construction.

`EXECUTION.json` records the exact heads, environment, stage classification, hashes, and public workflow/artifact provenance. The workflow's final gate correctly failed on exit 124; the enclosing shell steps' success must not be mistaken for a successful proof replay. Existing author release receipts and this session's fresh results are distinct.

## Reproduction

```sh
python3 -B research/staged544-r437-admission-audit/verify.py
python3 -O -B research/staged544-r437-admission-audit/verify.py
python3 scripts/research_package.py --package research/staged544-r437-admission-audit --check-only
python3 scripts/research_package.py --package research/staged544-r437-admission-audit
```

The direct commands require only the standard library and read retained template data; they do not execute template instructions. The registered command covers only the new bounded transition checker, not `EXECUTION.json`'s historical author-code replays. The original execution workflow is at `Clear1nsight/integer-mult-bounds`, run `39186343975`, workflow commit `6ce5b2ec7487f8f1c2331f018fd2a2758492d407`. Source export is run `39186804067`, commit `54465a1dfba4bcb84b5de02f6c5ea611c36448d6`. Workflow artifacts expire; the two scientific template inputs are retained permanently in this package.

## Open next questions

The structured questions in `TASK.json` identify two remaining tasks. First, complete the exact T385 full wrapper in a larger fresh execution budget, preserving the native-reuse boundary and recording discovery, both outer stages, and the final release. Second, discharge a precisely identified all-size physical interface premise, including arbitrary capture dirt, SOURCE mutability, whole-call hosting, and precision/recovery. Neither another digit refinement nor an older-head PASS closes these obligations.

## Attribution and coordination

Credit ai-nanachi for PR3647's composed construction and actual templates; Sagar Thakrar for PR3700's independent old-head audit, the OQ4 placement idea, and the reused rational engine; Ali Romman for PR1043's helper470 deletion; and DaysSky, DreamingOfClouds, eumemic, and the selected chain's credited authors for the inherited hosting, word, and invoice interfaces. `UPSTREAM-NOTICE.md` and `LICENSE` are retained unchanged. This package does not claim discovery of the slot move.

Credit dataisfire for PR3734's staged544 supplier, hexapode for PR3802's T385 allocation and full-wrapper packaging, ChaloupeMusic for PR3815's independent fixed-inventory ceiling, and the native/owner/outer authors credited by those packages. Existing audits and endpoint refinements were checked before selecting the current-head gap.

New transition implementation, controls, execution, and write-up by Chris R (@Clear1nsight), with substantial OpenAI assistance. No independent human review or formal-kernel review is claimed. Canonical base is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. Live PR search and relevant PR comments were read; Discussion coverage was unavailable, and an attempted coordination comment on PR3802 was denied by the integration with HTTP 403. This is a disclosed coordination limitation, not a claim that a reservation was posted.
