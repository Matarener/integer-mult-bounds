# H25 bookkeeping optimization plan

Complete the three bookkeeping priorities for the frozen historical H25 verifier: reuse triple sets, reduce runtime guard overhead, and reduce trace encoding allocations. Four Astra xhigh agents work concurrently on research, independent design, and disjoint implementation paths. The parent owns integration, every compiler/scientific run, and Chrome publication.

## Baseline and success

Use PR5995 publication `4f4159820c37f01d245784d1186bd51fcbc8ebb6`, specifically its **native C configuration with the existing complete checks**, as the baseline. The older Python arm is not the baseline for a further gain. Its recorded 28.636256246-second wall and 28.46-second CPU medians provide orientation; a new claim requires fresh same-session baseline runs. Preserve the original package and its 123 protected files.

The combined target is **at least a further 15% reduction in both complete wall and CPU time**, after every new control, conversion, compilation, binding, observation, serialization and cleanup cost. Individual priorities may contribute smaller increments. Never add percentages from separate components or earlier workloads.

A priority is finished when it has an independently reviewed contract and either a correctness-validated implementation with its measured disposition, or a reproducible scoped negative finding. The performance goal is achieved only when all three priorities have final dispositions, the combined target and noise gates pass, and required delivery checks and handoffs are complete. If the target fails, report it as unmet and keep the goal incomplete; a stopped experiment is not a performance win.

This work concerns the complete frozen historical H25 caller with retained observations. The old additional-15%-over-PR5864 objective is separate. Kappa research, Work1/2 mathematics, unrelated feeds and automations remain paused.

## Concurrent swarm and ownership

| Lane | Owner | Owned directory | First research question |
|---|---|---|---|
| P1 Set reuse | `bookkeeping_sets` | `priorities/set-reuse/` | Can private sets be constructed once per admitted triple while every original pairwise check and result remains identical? |
| P2 Runtime guards | `bookkeeping_guards` | `priorities/runtime-guards/` | Which duplicate identity records and successful-path message allocations can disappear while every distinct live check still occurs at the same boundary? |
| P3 Trace encoding | `bookkeeping_trace` | `priorities/trace-encoding/` | Can fewer temporary objects and crossings produce exactly the same canonical record bytes, prefix hashes, counters and errors? |
| R Independent review | `bookkeeping_review` | `research/independent-review/` | Do the designs preserve ownership, callbacks, fallbacks, check independence and a complete cost bill, both separately and in combination? |
| Parent coordination | Main agent | `control/`, `integration/`, `validation/`, `publication/`, `runtime/`, `stages/` | Which reviewed candidates deserve the next bounded run, and does the integrated result improve the complete verifier? |

Start fresh compact GPT-6-astra agents at xhigh effort, keeping completed earlier agents idle. Reuse these new-round agents for later follow-ups. Assign additional agents only to a distinct named obligation and owned path. Every worker is told that others share the workspace, must not revert their edits, and must accommodate concurrent changes. Workers do not edit the baseline, shared harness, working plan or another lane's files.

Research runs in parallel, including source inspection, bounded live overlap research, primary CPython/C-API documentation when needed, alternatives, fixture design and independent review. Implementation may also run concurrently after each design passes its gate, because the lane paths do not overlap. Shared adapter changes belong solely to the parent. Each lane supplies a written adapter contract before integration.

Compilers, scientific imports, corpus generation/execution, finite correctness runs, profiles and performance measurements use **one parent-owned queue and execution lock**. Agents prepare source and fixtures rather than executing them. No local CPU- or memory-heavy work runs alongside timed processes. This preserves useful concurrency without contaminating measurements or producing competing artifact writers. Chrome writes also have one owner.

## G0 Establish the shared contract

1. Refresh canonical upstream main, compare current guidance and priority revision, and check live PR/discussion overlap before substantial implementation or experiments. Keep scientific baseline PR5995 frozen even if current main changes; record compatibility rather than silently migrating inputs.
2. Create an isolated branch/worktree from refreshed main. Populate the index from the base before staging; assert that the diff contains only the intended package. Preserve all previous checkouts, threads, failed attempts and ledgers.
3. Record the full baseline source closure, compiler/interpreter/environment, native configuration, full certificate/stdout, exact typed return, ordered witness/rank/complement identities and all existing controls.
4. Freeze a common interface and observation contract for the three candidates. Keep the original baseline/reference implementation distinct from candidate helpers. Do not let a baseline call silently use an optimized guard or encoder. Finalize replacement helper/trace bindings and runtime closure-cell identities before capturing guard state; no post-capture mutation.
5. Parent may run one bounded post-C attribution diagnostic if it can discriminate among these mechanisms. Treat profiled timings as diagnostic; do not scale nested profile totals into promised savings.

Canonical main was freshly fetched during planning as `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8. Current live overlap is tracked separately in `control/UPSTREAM-REFRESH.json`.

## G1 Parallel research and design

Each priority produces `RESEARCH.md` and `PROPOSAL.json` with exact source pins, candidate and fallback contracts, removed work, retained work, new costs, negative controls, files to change, an independent comparison, open risks and a discriminating next test. Distinguish source-derived counts from measured timings. Research can reject a route without constructing it.

**P1 Set reuse.** The two existing all-pair loops imply 21.16 million set constructions for 2,300 triples. Investigate one private set per triple, scoped to the actual invocation. Retain both original intersection predicates, target order, coefficient and equality checks, exceptions and witnesses. Establish admission and fallback for unsupported or mutable/callback-bearing inputs. This is metadata reuse, not reuse of a verification answer. Do not substitute a shared arithmetic oracle for the literal independent checks.

**P2 Runtime guards.** The actual caller makes 298,644 native kernel calls with freshness checks. Begin with identity-based deduplication of repeated function records and failure-only message construction. Preserve every distinct function/global/builtin/descriptor/default/closure/native-entry check at its current call boundary, including before fallback. Never turn a per-call freshness check into a cached PASS or a once-per-run check. A C implementation is a separately costed option, requiring verified CPython APIs, correct reference/error handling and the same rejection behavior.

**P3 Trace encoding.** All 238,685 ordered complement records and 55,839,507 canonical bytes remain observed. Explore reducing tuple/dictionary/string/byte allocations, a source-bound native encoder, or bounded buffers within one record. Completed records must immediately update the public hasher, byte count and call count; inter-call deferral is outside this plan. Preserve sorted-key JSON/ASCII/newline schema, arbitrary-width fallback, exact types and vector order, counters, intermediate receipts and failure boundaries. Neither sampling nor replacing the canonical schema is an optimization within this scope.

The reviewer independently maps the common contract immediately, then reviews each proposal as it arrives. Report concrete defects and the smallest fixes. Do not demand another mathematical construction or invent an additional 15% hurdle for each lane. No implementation or scientific run passes the gate merely because unused resource budget remains.

## Repeated call reduction across all three priorities

Treat repeated calls as an explicit work item in every lane. The parent will collect a bounded diagnostic call census and each proposal must include a call budget: current calls and inputs, why repetition occurs, what can safely disappear, remaining semantic checks, replacement calls, added admission/conversion/validation work, and the evidence that makes reuse valid. Call counts support a design decision; they are not a promised wall or CPU saving.

- **P1:** reduce repeated set construction and repeated materialization of the same admitted triple metadata. Keep the current two predicate loops and all required intersection/equality checks in the primary candidate. Sharing an intersection result or fusing the loops is a distinct optional research branch: it needs a separate independence, error-order and complete-cost review before implementation.
- **P2:** eliminate duplicate records of the same function identity, successful-path `require` helper dispatch and eager message construction where an equivalent inline failure path preserves behavior. Every distinct live freshness check still executes at its original boundary; no once-per-run guard or cached PASS.
- **P3:** reduce repeated serializer/helper calls, tuple/dictionary construction, conversions and Python/C transitions within each record. The primary native encoder can replace several record-building/encoding calls with one checked call. Completed records must still update the hasher and counters immediately; no deferred inter-call batching or sampled observations.
- **Integration:** inspect repeated preparation or conversion across adapters and, where ownership and freshness permit, pass already admitted metadata or batch dispatch into a private owner. Keep separate independent verification paths and all original output, fallback, mutation and failure semantics. Do not share mutable answers or PASS receipts between calls, backends or processes.

Measure diagnostic calls separately from unprofiled qualification. Every eliminated-call claim must distinguish true deduplication, value reuse, batching and work merely moved into C. The complete candidate still pays for retained operations, new validation, marshalling, compilation and cleanup. Extend only on a source-supported benefit; avoid collecting another census that cannot change the next decision.

## G2 Concurrent implementation and serial correctness

After source/ownership/cost review, implement one primary candidate per lane in its owned path. Compare alternatives on source and cost first; execute an alternative only when new evidence distinguishes its mechanism. The parent freezes immutable stages before any run.

Run relevant finite comparisons and negative controls in the numerical queue. Cover exact types, widths, ordering, changed inputs/bindings, mutable aliases, callback/reentry boundaries where supported, fallback, errors and cleanup. Keep the live independent dense/original checks and original full assertions. Optimized interpreter mode is for finite controls; full verification remains assertion-on.

Freeze each candidate's complete validation bill before measuring it. Manual repairs get a new source/stage revision, retain the failed evidence and consume the same round budget. No automatic retries or timing rerolls.

## G3 Individual complete pilots

Schedule one complete baseline/candidate pair per source-admitted priority. Baseline B means PR5995 native C plus its unchanged controls; candidate C adds that lane and all of its new costs. Retain full outputs and every receipt. A micro improvement is not a complete improvement, and one pair is not a qualified individual factor.

Use pilots to decide integration or a scoped stop. A noisy individual result may still support a documented combined test if a specific shared-cost or interaction argument justifies it; do not label its individual saving established. Expand individual repetitions only when needed for a standalone performance claim and funded by the declared budget. Preserve all unfavorable results.

## G4 Combined integration and qualification

The parent integrates compatible, correctness-approved variants behind the frozen common interface. The reviewer checks interaction hazards: shared state, aliasing, guard placement, trace prefixes, fallback, exception paths, C-module loading and any duplicated cost. Run the full union of old and new controls, with all new costs inside the candidate bill.

Freeze source, environment, selection rules and the combined fixed cold sequence **B1 C1 C2 B2 B3 C3** before timing. Start with B1/C1 and complete the declared sequence only if the target is credible and correctness holds. Require fresh medians to improve at least 15% in both wall and CPU. Separately, each median saving must exceed the maximum of the baseline and candidate within-arm ranges for that metric. Retain every sample; instrumented diagnostics and publication checks are excluded from sample selection.

No percentage is transferred from PR5995, PR5929, PR5864 or component pilots. If the combined result fails, record the actual outcome and reassess only a materially changed, independently reviewed mechanism; do not rerun the same timings hoping for a different answer.

## G5 Delivery checks

Validate finite normal/O modes, the complete assertion-on caller, read-only Git-free execution, external output locations and failure retention. Before deleting fresh private runtime copies, make only their private directories writable after all source checks; never chmod immutable package inputs. Avoid entry names such as `profile.py` that shadow standard-library modules.

Check exact source/input manifests, raw ancestry, committed bytes and executable modes, declared inputs, canonical lossless transport, package metadata and export equality. Archive integrity/publication-wrapper costs are separately identified from the frozen scientific performance harness. A wrapper correctness run never replaces a performance sample or establishes a wrapper speed factor.

## G6 Publication and completion

Publish useful focused results through the authorized signed-in Chrome workflow, with exact pins, predecessor/license/AI credit, required template and seven-field handoffs. Do not grant maintainer secret access, merge a PR, or change the selected frontier. Read back PR text and the existing handoff index. Verify exact-head hosted planning and relevant package replay; keep hosted correctness separate from local performance.

Record each lane's final disposition, combined target/noise outcome, all failures, remaining obligations and a compact checkpoint. Mark the goal complete only when every required task is delivered and the combined performance target passes. An unresolved target remains incomplete; apply the goal tool's blocking rules only at a genuine repeated impasse.

## Resources and reporting

Use one serial guarded runner: 180 seconds per scientific command, 1 GiB sampled process-group RSS, 600 seconds initial feasibility and 1,500 seconds total for this new round. The shared ledger includes profiles, compilation, finite and full runs, publication scientific replays and all failures. Prior ledgers remain unchanged. Crossing a cap stops the affected work; it does not produce a negative scientific theorem or complete the goal.

Keep `TASK-BOARD.json`, `STATUS.json`, immutable stages and raw receipts current. Reassess after each source/cost gate, candidate result and integration result. Give concise progress updates and expose any blocker with its exact effect. No background feed work, automation or unrelated mathematical research is included.
