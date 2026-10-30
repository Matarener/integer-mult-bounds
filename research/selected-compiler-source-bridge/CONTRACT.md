# Source-to-model correspondence contract

This contract states exactly what `CompilerAudit.SourceBridge.selected_source_transport`
proves, what it assumes, and how each assumption relates to the pinned Python
source. The machine-readable form is [OBLIGATIONS.json](OBLIGATIONS.json).
Execution results for this package are in [VALIDATION.md](VALIDATION.md).

## 1. Provenance

| Item | Value |
|---|---|
| Archived predecessor | `research/selected-compiler-visitation-audit` at `eb89e7a7884ccacb82b5d5120d7f83be269748c0` ([PR3391](https://github.com/CrocSwap/integer-mult-bounds/pull/3391), Kewin Talaga), unchanged |
| Base | canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90` |
| Emitter source | `research/selected-bit-physical-caller/macro_code.py`, SHA-256 `f626b018124747a5f17c1603bea36cd74c00a69a0647fd7b10e9c4e2964caea8`; the other cited modules are under that package's `inputs/pr2753/predecessor/` |
| Bridge origin | Drafted by a Claude Opus 5.5 agent during a local six-agent review of PR3391 on 18 October 2026 and compiled serially by the integrating OpenAI Codex session. |
| Repairs before local proof checks | Two tactic-script errors and some deprecation warnings were repaired. The definitions and the main statement were not changed. |
| Previously verified snapshot | SHA-256 `6027af1a083bbca309f406762dc7526e11aac6f4c4cdb90d9aa7427ad04182f9`, Lean `v4.34.1` and the PR3391 mathlib pin `d13f23b723b8a846827a245b89c10fc7d3f11612` |
| Previous checks | 27 declarations. The exact statement type in Section 3 was checked. Axiom reports were limited to `propext`, `Classical.choice` and `Quot.sound`. An explicit `leanchecker --verbose CompilerAudit.SourceBridge` replay also passed. |
| Imported libraries | Trusted cached artifacts, not rebuilt cold |
| Candidate source | Header comments were corrected after the previous check. The formal text is identical. Its hash and rerun status are recorded in [VALIDATION.md](VALIDATION.md). |

The bridge imports `CompilerAudit.Result` from the PR3391 Lean model. It does
not modify that model or its main theorem.

## 2. Semantics: idealized, not realizable CPython

For prime q ≥ 3, `N = |GL64(F_q)| ≥ |GL64(F_3)|`; the latter has 6,492 bits. A
complete selected `compile_node` would need at least `2T = 1,809,792 N`
operation entries. Already at q = 3, this has 6,512 bits and exceeds `2^6500`. That exceeds the list
limit of conventional 32- and 64-bit CPython. On the reviewing interpreter,
`sys.maxsize` has 63 bits. A complete selected `Code` therefore cannot be
constructed there. No claim is made about which resource fails first.

Accordingly:

- **D. Denotational trace.** Every statement here is about the trace that the
  loop nest denotes under unbounded list and heap semantics. In this semantics,
  every guard is assumed to succeed and every `Cursor` loop and plan
  compilation to terminate. The phrase "one complete successful compilation"
  is meaningful only for D at the selected size.
- **P. Prefixes.** A bounded prefix is a separate possible implementation
  target. No prefix correspondence, resource-feasibility or termination theorem
  for an actual CPython run is provided.

This limit does not falsify the conditional formulas or the Lean model. It is
not an argument against lazy or regional representations or multiplication
algorithms generally.

## 3. Formal statement

The formal types are hand-written abstractions of the Python loops:

- `LocalEvent` stores `op` and `request`.
- `Event` has the cases `sweep`, `idle` and `silent`.
- `Seg W` represents one factory call. It stores the number of wrapper-free
  operations before the call, the call's wrapper and its block count.
- `SrcOp W` has the cases `begin`, `block`, `finish` and wrapper-free `other`.

The `sourceTrace` definition transcribes the source loop nest. It is not a copy
of the model's `visitWord`.

The theorem is stated over an arbitrary LOW type `α`, which uses value equality,
and an arbitrary wrapper type `W`, which represents identity.

```lean
(hlows  : lows = (List.range N).map unrank)
(hinv   : ∀ o, o < N → rank (unrank o) = o)
(hsched : List.Forall₂ (Matches SelectedData.replicaCount) (residualEvents sched) Selected.groups)
(hbud   : segs.map Seg.blocks =
            (sourceTrace lows SelectedData.replicaCount sched).map fun k => blocks (rename rank k))
(hfresh : (segs.map Seg.wrapper).Nodup)
⊢ (sourceTrace lows SelectedData.replicaCount sched).map (rename rank) = Selected.word N
∧ (sourceTrace lows SelectedData.replicaCount sched).toFinset.card = 28278 * N
∧ (srcRetained (emitSrc segs tail)).card = 904896 * N
∧ (srcRefs (emitSrc segs tail)).length = 1809792 * N + Result.blockTotal N blocks
```

`Matches` describes only one event's projected request list for every replica
and its view and nesting flags. It does not mention LOWs, `N`, the trace or any
count. The four conclusions are derived from the hypotheses. In particular:

1. The renamed trace equality is ordered list equality. Order-changing mutants
   with equal counts do not satisfy it.
2. Distinct keys are counted over LOW objects **before** ranking. This count
   uses the rank injectivity that follows from `hlows` and `hinv`.
3. Retained identities follow from one segment per trace entry, which follows
   from `hbud`, and pairwise-distinct wrappers, given by `hfresh`.
4. Reference counts allow wrapper-free operations before any segment and at the
   end.

`B = Result.blockTotal N blocks` counts block operations. It is not native cost,
heap size or a stock coefficient.

## 4. Correspondence premises

The source lines below refer to `macro_code.py`.

| ID | Lean premise | Python fact | Evidence and boundary |
|---|---|---|---|
| L1 | `sourceTrace` / `eventTrace` definitions | Sweep loops run in the order schedule → replica → `low_classes()` → event position. Idle loops run in the order schedule → replica → identifier → LOW. Bridge and exchange events do not call `residual`. There are three call sites, at lines 66, 71 and 87. | The PR3391 AST check pins the call sites and loop tuples. The semantic transcription is informal. |
| L2 | `LocalEvent.emits` | `accept` returns `event[:2]`. `residual` is called only for op ∈ {0, 2} (MOVE/COPY), with key `(requests[p], True, low)`. Idle calls use `(id, False, low)`. | Source reading. The treatment of malformed events is a Lean totalization; see Section 5. |
| L3 | `Matches` for all `r < 32` | `call(stage, r)` takes events and identifiers from the cached `recipe(stage)`, which does not read `r`. | Structural by source reading. The census checks all 32 replicas at q = 3. |
| L4 | `hsched` | Non-silent schedule events correspond, in order, to the 19 certified interval groups and their flags. | Python census and certificate pins. This is not a formal Python proof. Cross-group disjointness depends on the pinned template, not on the code structure. q independence is argued from the source. |
| L5 | `hlows` | `low_classes()` yields `unrank(o)` for `o in range(size)`. Its size is `∏(q^64 − q^k) = N`. | Source reading |
| L6 | `hinv` | `rank(unrank(o)) = o` for `o < N` on GL64(F_q). | **Not proved by this package.** The tiny codec fixtures do not prove this all-size property. [PR2569's retained proof](https://github.com/CrocSwap/integer-mult-bounds/blob/20ecf2891d80b5acf18d980b2164fb44ea7faa90/research/selected-source-packets/PROOF.md#L44-L65) supplies a written prefix-count/bijection argument for byte-identical codec source. That argument was located and read, not formalized or replayed here. |
| B1 | `Seg` / `emitSrc` shape and `hbud` alignment | Each call appends `residual_begin`, then `b ≥ 0` blocks, then `residual_end`, contiguously (lines 38–47). | Source reading. `Cursor` termination is assumed in D. |
| B2 | `hbud` budget equation | In mode 0, `b` is determined by `Specifications.plan(code)`. The code `encode(i, c, low)` depends only on `(i, c, rank low)`, and plans are cached deterministically. | Source reading. It assumes deterministic plan compilation and no external cache mutation. |
| B3 | `hfresh` | `SelectedBinding.residual` constructs a new `Residual` on every call. Every returned wrapper remains in `Code.operations`. | Python identity semantics. The tiny-fixture lifetime check observes this behaviour. It is not formalized. |
| B4 | `SrcOp.other` carries no wrapper | No non-residual operation tuple directly holds a `Residual`. `compile_owner` returns tuple matrices and `Route` values. | Discharged for direct slots by source inspection. Transitive object graphs are outside the counting unit. |
| B5 | `srcRefs` | A direct reference is slot 2 of `begin`/`end` or slot 1 of `block`. | Definition. It is not `sys.getrefcount`, transitive size or native storage. |

The Lean theorem uses every hypothesis. Mathematically, the premises are needed
unevenly:

- Ordered trace equality needs `lows.map rank = range N`.
- The call and direct-reference counts, `T = 904,896 N` and `2T + B`, need only
  `N` LOWs per pass, together with segment alignment.
- Identifying `T` with the number of distinct retained wrappers additionally
  needs freshness, given by B3.
- The `28,278 N` distinct-key count needs LOW injectivity, which follows from
  L5 and L6.
- Freshness of `Specifications` is not needed for any count. It can affect only
  cache contents, and therefore possibly `B`.
## 5. Scope of events

The bridge covers well-formed, guard-successful events only:

- opcodes in {0, 1, 2, 3};
- integer request IDs at every MOVE and COPY;
- request IDs and view flags that pass the `need` checks.

For a missing request or an opcode other than MOVE/COPY, `LocalEvent.emits`
returns no emission as a total Lean definition. This does not model Python
guards or exceptions: no equivalence is asserted for malformed raw events.

## 6. Python check boundaries

- **Census.** The census reconstructs requests and groups from metadata at
  q = 3 for all 32 replicas. It does not enumerate GL64 LOWs or execute the
  selected compiler.
- **Lifetime.** The lifetime check uses tiny seeded fixtures with the original
  factory and compiler functions. It is not a cold 64-dimensional
  `Specifications` initialization and does not validate numerical endpoints.
- **Windows adapter.** On Windows only, an in-memory adapter changes one
  inventory-path expression in the original verifier to its POSIX spelling.
  All authentication predicates are unchanged.
- **Loader bypass.** The lifetime importer bypasses `loader.authenticate`. It
  hashes the original module bytes, imports them and marks the loader active. It
  is therefore not a test of loader authentication.
- **Export.** Portable copies are made with the shared
  `scripts/export_research_package.py`, using the committed package and its 152
  declared inputs. The direct verifier checks the extracted
  `.research-export.json` inventory and bytes. The manifest provides transport
  integrity only and is not authenticated Git provenance. Provenance is checked
  before publication and by the registered metadata command in a Git checkout.
- **Lean.** The check freshly compiles seven predecessor modules and the bridge,
  uses eight dependency library roots, and checks nine pinned dependency source
  revisions. It trusts cached compiled library objects rather than rebuilding them.

## 7. Not established

This contract does not establish any of the following:

- Python parser, operational semantics or compiler correctness;
- that the premises in Section 4 hold formally for the pinned source;
- the GL64 LOW codec inverse (L6);
- complete realizable CPython execution;
- prefix theorems;
- safety of wrapper sharing;
- native space, storage lifetime, stock or precision;
- zero runtime or source-validation work;
- any contradiction of the predecessor construction's q-dependent fixed overhead;
- the full multiplication theorem;
- any change to κ or the selected frontier.

Separate AI implementations and kernel checks are not independent human review.