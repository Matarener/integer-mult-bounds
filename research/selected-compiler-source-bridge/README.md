# Selected compiler: conditional source-to-model bridge

**Successor verification package to [PR3391](https://github.com/CrocSwap/integer-mult-bounds/pull/3391).
It adds a conditional Lean bridge and bounded Python source checks; it does not
verify Python, the GL64 codec or any multiplication theorem.** The archived
package [`research/selected-compiler-visitation-audit`](../selected-compiler-visitation-audit/README.md)
remains byte-identical to publication `eb89e7a7884ccacb82b5d5120d7f83be269748c0`.
This package was prepared from canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The selected conditional
κ = 0.001672660197076918 (priority revision 6) is unchanged.

## What this adds

PR3391 proved its counts for a *defined* model trace, `Selected.word N`, and
connected that model to the Python emitter through hash pins, a metadata
census and prose. This package adds `CompilerAudit.SourceBridge.selected_source_transport`.
It starts from a separately defined, source-shaped trace and primitive premises:

- per-event request projections that match the 19 certified groups and their view/nesting flags;
- LOW objects enumerated as `unrank(0..N-1)`, with `rank (unrank o) = o` for `o < N`;
- one begin/blocks/end segment per factory call, in trace order, whose block budget depends only on the renamed key;
- pairwise-distinct wrapper identities, with all other operations free of wrapper references.

From these premises, Lean **derives** the following:

| Conclusion | Value |
|---|---:|
| Ordered trace after renaming LOWs by `rank` | equal to `Selected.word N` |
| Distinct `(request, view, LOW)` source keys | `28,278 N` |
| Retained wrapper identities | `904,896 N` |
| Direct wrapper references in operations | `1,809,792 N + B` |

The final trace equality and the totals are not hypotheses. The trace equality is
literal list equality, including order. A count-only match cannot satisfy it.
`B` is the sum of emitted `block` operations. It is an operation count, not
native cost, memory size or a stock coefficient.

The exact premises, their source locations and their evidence status are in
[CONTRACT.md](CONTRACT.md) and [OBLIGATIONS.json](OBLIGATIONS.json).

## Interpretation and limits

**The trace is idealized and unbounded.** A complete selected `Code` cannot be
created on conventional 32- or 64-bit CPython. At the smallest admissible
radix, q = 3, `N = |GL64(F_3)|` has 6,492 bits. The begin/end references alone
need `2T = 1,809,792 N` list entries, a 6,512-bit number above `2^6500`.
Other resource failures may occur sooner; no first-failure point is claimed.
This limit does not contradict the conditional formulas or the Lean model.
It also does not constrain lazy or regional representations, or multiplication
algorithms generally.

Other qualifications are inherited or newly made explicit:

- `Specifications` already caches source records and plans. The wrappers are
  fresh per call. This package does not show that wrapper sharing is safe.
- The q-dependent fixed overhead allowed by the predecessor construction is not
  contradicted. No zero runtime or source-validation work is claimed: runtime
  hooks still use specifications.
- The bridge covers only well-formed, guard-successful source events. The Lean
  event types are hand-written abstractions of the Python loops, not a Python
  operational semantics.
- The inverse property of the actual GL64 LOW codec is **not proved by this
  package**. It remains hypothesis `hinv`. This is not a claim that no proof exists
  elsewhere: [PR2569's retained proof](https://github.com/CrocSwap/integer-mult-bounds/blob/20ecf2891d80b5acf18d980b2164fb44ea7faa90/research/selected-source-packets/PROOF.md#L44-L65) already gives a
  written prefix-count induction and bijection argument for the same codec.
  This package does not formalize or independently replay that argument.
- No κ, stock, native-space, precision or full-theorem claim changes.

## Evidence

The publication candidate passed a fresh local Lean run on 18 October 2026:
seven unchanged predecessor modules and this bridge compiled with Lean
`v4.34.1`; the exact main statement, baseline main contract and fixed 27-name
axiom inventory checked; and `leanchecker --verbose CompilerAudit.SourceBridge`
replayed the bridge module. Its axiom reports use only `propext`,
`Classical.choice` and `Quot.sound`. One positive and two rejecting bridge probes
passed their expected outcomes. [VALIDATION.md](VALIDATION.md) records the
candidate hash, commands, trust boundary and publication verification. The
prior bridge's formal text is unchanged; only its header comment was clarified.

Python checks are bounded and use the standard library only:

- **Census.** It checks all 32 replicas at q = 3: 28,278 request IDs, 19 groups
  and 904,896 projected visits per LOW, without enumerating GL64. The archived
  PR3391 census used q = 7 metadata.
- **Lifetime.** It runs on tiny seeded fixtures and checks 16 distinct wrappers,
  32 blocks and 64 direct references in normal and optimized mode. It is not a
  cold 64-dimensional initialization and does not validate numerical endpoints.
- **Windows path adapter.** On Windows, the census check uses an in-memory
  path-spelling adapter. It changes only one inventory-path expression in the
  original verifier to its POSIX spelling. Authentication predicates are
  unchanged, and no adapter is installed on POSIX.
- **Lifetime importer.** The lifetime check does not call the original
  `loader.authenticate`. A source-only importer hashes the original module
  bytes, imports them and marks the original loader active. Therefore, this
  check does not test loader authentication or original initialization.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python -B scripts/research_package.py --package research/selected-compiler-source-bridge
```

The registered command runs the bounded source checks normally and with `-O`,
as listed in `VERIFY.json`; it never runs Lean. For a single direct run with
saved diagnostics:

```sh
python -I -B research/selected-compiler-source-bridge/verify.py --output /absolute/fresh/external/dir
```

Use `-O` as an additional interpreter option for an optimized direct run, with a
different output directory. The optional `--output` must name a new absolute
directory outside the repository; it receives logs and `RESULT.json`.
Provenance is checked before publication and by the registered command in a Git
checkout. Each direct invocation checks only its own interpreter mode.

To create a portable copy, use the repository's shared exporter
([guide](../../docs/research/package-export.md)). Do not use a package-specific
exporter:

```sh
python scripts/export_research_package.py export --package research/selected-compiler-source-bridge --ref COMMIT --output /absolute/bridge.tar
python scripts/export_research_package.py check /absolute/bridge.tar
```

The archive contains the package and its 152 declared external inputs. Export
and `check` require `scripts/export_research_package.py` and
`scripts/research_package.py`. After the check passes, extract the archive into a
fresh directory and run the direct verifier from there. Git is not required for
that replay:

```sh
cd /absolute/fresh/extracted
python -I -B research/selected-compiler-source-bridge/verify.py
python -I -B -O research/selected-compiler-source-bridge/verify.py
```

In this replay, the verifier also checks the inventory and bytes recorded in
the extracted `.research-export.json`. That manifest provides transport
integrity only. It is not authenticated Git provenance, so obtain the archive or
its source commit through a trusted channel.
Lean is opt-in and uses an existing toolchain and package cache:

```sh
python research/selected-compiler-source-bridge/lean/check.py \
  --output /absolute/fresh/external/dir --toolchain TOOLCHAIN_ROOT --packages PACKAGES_ROOT
```

The checker does not download or install dependencies. It freshly compiles the
seven predecessor modules and this bridge, uses eight pinned dependency library
roots, and checks all nine dependency source revisions (`Cli` is tooling-only).
Cached compiled library objects are not rebuilt cold and remain an explicit
trust assumption. See [VALIDATION.md](VALIDATION.md) for the tested environment.
## Open next questions

Structured scope, stop rules and overlap status are in [TASK.json](TASK.json).

1. **Can the written LOW inverse argument be bound to the actual implementation
   in a proof assistant?** [PR2569's proof](https://github.com/CrocSwap/integer-mult-bounds/blob/20ecf2891d80b5acf18d980b2164fb44ea7faa90/research/selected-source-packets/PROOF.md#L44-L65)
   already gives the prefix-count induction. Its codec bytes match the frozen
   codec used here. First audit those invariants against `low_codes.py`, and
   recheck live overlap before formalizing them. Tiny codec fixtures are not a
   GL64 inverse proof; the prior written result should not be rediscovered or
   described as absent.
2. **Can a prefix version of the transport describe what CPython can actually
   run?** First, state the transport for a source trace truncated at a visit
   index against a prefix of `Selected.word N`. Then check whether the tiny
   lifetime fixture fits that statement.
3. **Can equal-key wrappers share identity under a stated observer contract?**
   This is inherited from PR3391. First, audit identity-sensitive consumers such
   as `Machine.geometry`. Cached plans alone do not establish safety.

## Status and attribution

PR3391 was merged for archival intake. It remains `partially_reviewed`, and its
independent scientific review is still open. This package does not change that
status and makes no claim of maintainer acceptance or human review.

**Submitter of this successor and PR3391:** Kewin Talaga (`PellaML`). PR3391 acknowledges substantial OpenAI
Codex, Claude Opus 5.5 and GPT 6 Astra assistance.

**Predecessors credited by PR3391:**

- Jose Manuel (`jmbarrancoml`): public fixed-role physical caller, emitter,
  runtime and numerical codec; the ordered 28,278-request catalogue from PR2234
  and its PR2697 metadata.
- David Arias: logical selected caller and stock/endpoint chain from PR2753.
- Jose Manuel's PR2569: the prior written LOW bijection and source packets;
  PR2769 supplies the retained numerical codec.
- ywz65: parking-controller predecessor PR2635.
- Nick Petalas: compiler-ordering and residual/CALL audits PR2989 and PR3041.
- Matthieu Pascal: the 904,896 paid-child factor in PR1806, which uses a
  different counting unit.
- Ross Richardson: retained-backing/lifetime accounting method.
- Douglas Colkitt and the selected construction's other contributors.

The fresh overlap pass also read the conditional enclosing NODE/MERGE follow-up
[PR3223](https://github.com/CrocSwap/integer-mult-bounds/pull/3223). Roger Sato's
parallel [PR3634](https://github.com/CrocSwap/integer-mult-bounds/pull/3634) addresses
primed-name axiom reports in the shared checker; [PR3602](https://github.com/CrocSwap/integer-mult-bounds/pull/3602)
addresses raw-string scanning. This package's fixed-name local harness is not a
claim of priority for those tooling issues, and it changes no shared checker.
The portable export uses Tekalign's shared exporter. These contributors keep
their existing credit. Original notices are preserved.

**AI assistance:**

- An earlier local cross-review used three GPT 6 Astra agents and three Claude
  Opus 5.5 agents. The Astra agents reconstructed the census, checked lifetime
  behaviour and audited reproducibility. The Opus agents reviewed the written
  proof and Lean trust boundary, and one Opus agent drafted the bridge module and
  its contract.
- OpenAI Codex integrated and repaired that work and ran the local checks.
- Current OpenAI Codex packaging-assistant workers prepared this package.

AI review is not independent human or proof-assistant certification of the
correspondence premises. New work is under Apache-2.0.