# Public selected compiler: visits, retained wrappers, and the runtime boundary

**Scoped source audit; no new bound, compiler replacement, or defect claim.**
For the public default `SelectedBinding`, one successful complete mode-0
compilation makes **904,896 N** residual-factory calls and retains that many
separate `Residual` wrapper objects, although it visits only **28,278 N**
distinct source keys. Here `N = |GL64(F_q)|`; the inherited LOW bijection and
source-admissibility hypotheses remain premises. The selected GL64 word is
**not** expanded by this replay.

**Assurance level:** The source audit combines a written conditional argument
and finite Python checks with a [Lean-checked trace/allocation model](lean/README.md)
and selected-data certificate. The Lean proof does not verify Python semantics,
the LOW rank/unrank algorithm, or the complete multiplication theorem. The full
selected GL64 word is not executed, and the inherited source premises remain.

This is a small accounting result about the literal Python emitter. It is
**not** a native-space lower bound, a concrete selected stock coefficient, a
challenge to the predecessor's allowed q-dependent fixed overhead, or an
improvement to the selected conditional kappa. `Specifications` already caches
source records and plans; it is the **Residual wrappers** that are not cached.

## Result and why it is useful

The actual selected topology/control metadata has 32 replicas, 26,199 MOVE,
81 COPY and 1,998 IDLE request IDs. Its 19 chronological residual groups contain
nine groups of 2,920 requests, nine of 222, and one empty group. We check every
replica, disjoint/exhaustive request coverage and the exact local/idle order.

| Quantity for one successful complete default compilation | Exact value |
|---|---:|
| Distinct `(request, common/native, LOW)` keys | `28,278 N` |
| Factory calls and separately retained `Residual` instances | `904,896 N` |
| Visits to each key | `32` |
| Direct operation references to wrappers | `1,809,792 N + B` |

`B` is the number of emitted `block` operations; their plan-dependent cost is
not evaluated here. The ambient specification constructed before compilation
is not an extra `Residual` instance. Local groups visit **replica / LOW / event**;
idle groups visit **replica / request / LOW**. Counts alone cannot distinguish a
wrong loop order, so the checks include a counts-preserving order mutant.

The distinction between *keys*, *cached plans*, *wrapper instances*, and
*operation references* is useful when pricing a literal emitter or proposing
an alternative representation. It does not prove that sharing wrappers is safe:
`Machine.geometry` observes identity inside a residual, and observer/callback
contracts must also be considered. No optimization is installed here.

The pinned `Machine` reads stored `Code.operations`, and its methods contain no
direct residual-factory or compiler call. Runtime binding hooks still validate
and compute coefficients using specifications. **No zero-runtime-source-work
claim follows.** Compilation/reuse frequency, route emission, native installation,
full runtime costs, stock, precision and outer transfer remain outside this audit.

[PROOF.md](PROOF.md) presents the written conditional argument and its
assumptions. [EXPECTED.json](EXPECTED.json) stores the expected test receipt;
[VALIDATION.md](VALIDATION.md) records the run results, their coverage, and
remaining obligations.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/selected-compiler-visitation-audit --check-only
python3.12 -B scripts/research_package.py --package research/selected-compiler-visitation-audit
```

The two registered commands run serially in normal and optimized mode, with a
180-second limit each. They authenticate all 121 live inputs before imports,
run the selected **metadata-only** census, execute the original compiler on its
48-element GL2(F3) fixture with a test-only tracing binding, and check arithmetic,
allocation identity, source-order and input-corruption controls. Tiny tracing
bindings/receiver fixtures do not establish selected numerical endpoint validity.
These registered Python commands do not launch Lean, native builds, solvers,
full GL64 loops or historical scientific replays. The Lean supplement has its
own explicit, pinned-environment replay; see [its guide](lean/README.md). No network access, Git writes or source-file writes are performed.

A direct replay also works in a Git-free source export:

```sh
python3.12 -I -B research/selected-compiler-visitation-audit/export.py --destination /absolute/fresh/export
cd /absolute/fresh/export
python3.12 -I -B research/selected-compiler-visitation-audit/verify.py
python3.12 -I -B -O research/selected-compiler-visitation-audit/verify.py
```

The exporter copies only this package and its pinned public inputs, preserving
paths, the root NOTICE and upstream license/provenance files; it needs no
private workspace, Git executable or network. This is an audit replay export,
not a complete runnable export of every predecessor runtime suite.
The direct verifier authenticates live source bytes and the complete export
inventory; **historical task-card provenance** is instead checked by the
Git-backed repository hook. `--integrity-only` performs no scientific replay;
`--emit` prints a newly computed receipt without accepting it as the expected
one. Fresh private bytecode-cache paths prevent stale source-adjacent `.pyc`
files from replacing the authenticated modules.

## Scope and coordination

This is an explicitly **changed-scope side result** from the
`selected-stock-envelope` card, not completion of that card. The public compiler
and its compile-before-execute architecture are predecessors' contributions;
the addition is the source-bound multiplicity/retention ledger and portable,
discriminating checks. No unpublished prepared registry or native prototype is
required or claimed to be part of the public implementation.

## Open next questions

1. **Can equal-key wrappers safely share an identity under a stated observer
   contract?** First audit all identity-sensitive consumers, then compare one
   small complete caller trace against a separately scoped sharing experiment.
   Reusing plans alone does not establish this. No such replacement is proved.
2. **How should a concrete implementation charge this q-dependent emitted
   representation and its installation/reuse?** First identify its actual
   storage/installation model and compilation policy. Object counts are not
   native cell counts, and repeated runtime nodes do not automatically repeat
   compilation. The existing asymptotic fixed-q allowance is not disputed.

Structured questions, stop rules and overlap freshness are in
[TASK.json](TASK.json). The selected frontier is unchanged. This package has been
prepared locally; there is no claim of maintainer acceptance or human review.

## Attribution

Jose Manuel (`jmbarrancoml`) supplied the [public fixed-role physical caller](../selected-bit-physical-caller/README.md),
emitter, runtime and numerical codec. David Arias supplied the logical selected
caller and its stock/endpoint source chain in
[PR2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753).
The codec comes from [PR2769](https://github.com/CrocSwap/integer-mult-bounds/pull/2769);
ywz65 supplied the parking-controller predecessor
[PR2635](https://github.com/CrocSwap/integer-mult-bounds/pull/2635).
The ordered 28,278-request catalogue is inherited from Jose Manuel's
[PR2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234), adapted in
his retained PR2697 metadata. Nick Petalas's
[PR2989](https://github.com/CrocSwap/integer-mult-bounds/pull/2989) and
[PR3041](https://github.com/CrocSwap/integer-mult-bounds/pull/3041) already audit
compiler ordering and residual/CALL refinement. Matthieu Pascal's
[PR1806](https://github.com/CrocSwap/integer-mult-bounds/pull/1806) already reports
the numerical factor 904,896 in a **paid-child** invoice, a different counting
unit. Ross Richardson's
[retained-backing/lifetime accounting](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18964380)
is a methodological predecessor. This package claims neither first discovery
of those numbers/order nor the general retained-object accounting method.

The frozen exports preserve the earlier selected-source, LOW, Word, routing,
directory and residual-lifetime contributors, including Nick Petalas, and the
attribution in their README/NOTICE files. Douglas Colkitt and the selected
construction's other contributors retain their existing credit.

The audit was developed from earlier local source-accounting notes; those notes
are not runtime dependencies or evidence that a reviewer must trust. All claims
above are bound anew to the public inputs in [SOURCES.json](SOURCES.json).
Substantial OpenAI Codex, Claude Opus 5.5 and GPT 6 Astra assistance was used in
implementation, reasoning and review. AI review is not independent human or
proof-assistant verification. New work is Apache-2.0; original notices remain.
