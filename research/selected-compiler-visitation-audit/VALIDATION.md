# Python validation and scope record

This records the Python audit and its original review. The later, explicitly
invoked Lean supplement has a separate [scope and replay record](lean/README.md);
it does not convert these finite Python checks into an end-to-end formal proof.

## Baseline and environment

- Canonical main: `463113d675af7410ac91d53a4fed51ec6494eb9a`; priority revision 6.
- Selected-record SHA256:
  `bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
  The selected conditional result and all predecessor sources are unchanged.
- Author-checked on 2026-10-17 UTC, CPython 3.12.6, 64-bit Windows 11,
  standard library only. No dependencies were installed.
- The source-bound Python replays were run serially, with a 180-second deadline
  for each replay subprocess. These Python runs performed no native build, Lean
  run, full selected GL64 expansion or historical scientific replay. The later
  Lean model checks are separate.

## Observed acceptance checks

The repository metadata check and registered normal/optimized replay passed:

```sh
python3.12 -B scripts/research_package.py --package research/selected-compiler-visitation-audit --check-only
python3.12 -B scripts/research_package.py --package research/selected-compiler-visitation-audit
```

The registered commands are exactly the two argument arrays in VERIFY.json.
The complete scientific results agree with EXPECTED.json in both modes; no
scientific fields are dropped for comparison. Its platform-independent digest
is SHA256 of `json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()`:

```
c1bc50f54937cd3b2efae61bb5b655b55859b3ed7ddcf1a2e9bbd8682fc88f3d
```

The LF-formatted EXPECTED.json file has SHA256
`68d9a80dd341f03b4d9d3c674aa9444ba87a81afd68bd66dd88525002fe401a5`.
Console/container byte hashes are not substitutes for this complete JSON
comparison; Windows console line endings may differ from the committed file.

| Check | Observed scope |
|---|---|
| Live source authentication | 121 exact SHA256 and Git-blob pins, checked before source imports and again after replay; all observed repository-local module paths declared |
| Actual selected census | All 32 replicas; 28,278 requests; 7,843,392 local metadata events; 8,877,079 explicit metadata predicates |
| Abstract grouped word | 4,068 schedules; independent stable-sort word oracle; per-key multiplicity and fresh-wrapper/reference model |
| Identity model | 121 additional small histories; 64-call boundary; 20 invalid arguments rejected |
| Order controls | One counts-preserving wrong-order witness, plus two rejected static AST shape mutants |
| Input controls | Eight corrupt **manifest objects** rejected; these are not eight edits to source files |
| Tiny original compiler | GL2(F3), 48 LOWs and 14 requests; 672 factory visits per trace, exact complete visit order |
| Axis fixture | 5,591 operations, 672 blocks, 2,016 direct wrapper references |
| Cursor fixture | One shared **good** plan, 6,935 operations, 2,016 blocks, 3,360 direct wrapper references; not fallback/child-path coverage |
| Reference lifetimes | Every tiny block/end uses its current begin wrapper by identity; direct tuple references equal `2T+B` |
| Public factory receiver cut | Two equal-key calls to the unmodified method give equal-valued, nonidentical wrappers; not a selected Specifications constructor/endpoint replay |
| Direct runtime cut | 22 Machine methods inspected; stored-operation fetch and absence of direct compiler/residual/sync calls, not a transitive runtime-cost theorem |

## Portable, read-only replay

The source-audited final code and expected receipt were also copied into a fresh
Git-free export and replayed in normal and optimized mode. Both returned the
same complete scientific receipt. The export contained **134 files**: 121 live
inputs, 12 package files, and the export inventory. Original notices, the root
NOTICE, upstream license and upstream provenance manifest are included.

The qualification used the absolute Python executable with an **empty PATH**,
no `.git` directory, and Windows ACLs denying source writes. Both opening an
existing file for writing and creating a new file were rejected by the OS.
The complete file inventory and every file hash were unchanged after each run.
No private workspace path, Git executable, network request or source-tree write
was needed. Temporary bytecode namespaces live outside the read-only export.

This tests the audit replay, not every predecessor runtime suite. The direct
verifier authenticates live bytes and the export inventory. Historical task-card
provenance is deliberately checked by the Git-backed repository hook, not claimed
to be independently resolved from an export with no Git history. Files remain
source-bound: a later changed input must be repinned/reviewed, not silently reused.

On Windows, `InventoryPath` makes the inherited verifier's relative inventory
spelling POSIX while checking that each configured path resolves to the same
file. No source validator, factory or topology function is replaced. This is a
pathname adaptation, not a waiver of original hash/inventory predicates. Imports
use a fresh empty private bytecode prefix: `-B` alone would not prevent reading
old source-adjacent `.pyc` files.

## Review, attribution, and overlap

Claude Opus 5.5 independently read the proof/source correspondence and package
code, cross-checked the HOST metadata as data, and compared source pins. Its one
must-fix finding was missing upstream attribution in the proposed export. The
unchanged root NOTICE, upstream license and provenance were added to the pinned
inputs, and the reviewer closed that finding on the repaired LF source snapshot.
The explicit prime-q domain and direct block-reference controls were also
reviewed. GPT 6 Astra supplied the bounded arithmetic implementation and a
separate documentary overlap review. These are **AI reviews**, not independent
human or formal-kernel verification. Final execution/export integration and this
validation record are the main agent's responsibility, not certified by those
source-review reports. The subsequent Lean model is separately checked by its
compiler and explicit kernel-replay tool.

The overlap checkpoint read 34 initial and seven closing updated PR bodies
(40 distinct PRs) through #3271, scoped current Discussion windows, five targeted
predecessor PR bodies, and the nearest PR2989/3041 claim/proof/receipt/code
portions. Main was freshly fetched unchanged; the closing Discussion/predecessor
reads reached 20:18 UTC. The historical repository overlap helper was also run
on a copied, explicitly stale cache. No equivalent explicit default wrapper/key/
reference census was identified **within that coverage**. Ordering, numerical
factors, the compiler architecture and retained-object accounting all have the
predecessors credited in README.md.

Coverage is not exhaustive: last-30/first-20 and targeted last-10/first-10
comment/reply windows can omit older edits and replies; a stale helper search
cannot establish novelty. A transient PR2989 TLS failure was retained, then a
bounded retry succeeded. Neighboring mathematical claims were not replayed or
adopted. Publication still requires a fresh overlap check and donor authorization;
this work remains local, with no Discussion post, push, PR, merge or closure.

During development, a missing two-file input declaration and the required exact
README section heading were rejected by the checks and corrected. No acceptance
predicate was disabled. Failed observations and review versions are retained in
the local work log, not substituted for successful receipts or copied into this
focused package. The prior frozen packages and all eight preserved source
checkouts were separately checked unchanged; they are not replay dependencies.

## Not established

No all-q source admissibility/LOW-bijection proof, complete selected GL64 program,
fallback/runtime endpoint audit, safe wrapper-interning refinement, total Python
heap size, native traffic/cell tariff, concrete selected stock coefficient,
precision bound, outer multiplication transfer or improved kappa is established.
The source's fixed-q compilation allowance and existing refinement theorems are
not contradicted. The receipt records the results of the listed finite checks
on the pinned inputs; it is not itself a kernel-checked proof. The separate Lean
theorems apply only to their declared model and certificate.
