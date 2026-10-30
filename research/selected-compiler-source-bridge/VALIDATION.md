# Validation and reproducibility boundary

## Result and exact scope

Author checks on **18 October 2026**, Windows x86-64, CPython **3.12.6**, passed
for the candidate described here. The PR identifies the published commit and
its committed-byte/export recheck. This is local executed evidence, not a
hosted-CI pass, independent human certification or maintainer admission.

| Check | Observed result |
|---|---|
| Registered metadata and source pins | Pass; 152 live inputs, plus three historical-provenance rows |
| Bounded Python checks | Pass normally and with `-O`; complete substantive result trees agree after excluding only elapsed time and interpreter-version fields |
| New Python controls | 9 replay/inventory test methods, 30 census/import/lifetime test methods, 7 capacity test methods; all pass in both modes |
| Original PR3391 receipt | Unchanged scientific SHA-256 `c1bc50f54937cd3b2efae61bb5b655b55859b3ed7ddcf1a2e9bbd8682fc88f3d` in both modes |
| Selected interval certificate | Fresh `extract_census.py --check` passes; retained JSON and generated Lean data unchanged |
| Independent census | q = 3, all 32 replicas, 7,843,392 local events, 28,278 request IDs, 19 groups including the empty group; 904,896 projected visits per LOW |
| Tiny original compiler census | 48 visits, 24 keys, multiplicity two; exact order and empty checkpoint checked |
| Tiny original lifetime fixture | Per compilation: T = 16, B = 32, 64 direct references, 16 distinct wrappers; separate warm-cache compilations and weak-reference lifetimes checked |
| Capacity arithmetic | `bit_length(|GL64(F3)|) = 6492`; `bit_length(2T) = 6512`; `2T > 2^6500`, beyond conventional CPython sequence limits |
| Lean runner unit tests | 17 methods pass normally and with `-O`; no Lean execution in these tests |
| Fresh Lean compile | Seven unchanged PR3391 modules and `CompilerAudit.SourceBridge` compile into one fresh external build root |
| Lean contracts | Exact bridge statement and baseline main contract checked; all 27 required bridge theorem axiom reports accepted, with no missing/duplicate/extra names |
| Kernel replay | `leanchecker --verbose CompilerAudit.SourceBridge` succeeds and reports exactly that leaf module |
| Lean controls | Concrete positive contract passes; duplicate-wrapper/freshness counterexample and wrong retained coefficient are rejected at their intended obligations |

The independent Python implementation does not import PR3391's accounting,
source-audit, verifier or census implementation. The orchestration command also
runs the original verifier separately to check preservation of its receipt.
Those are distinct checks, not two names for one implementation.

## Lean source and environment binding

Candidate `lean/CompilerAudit/SourceBridge.lean` SHA-256:

```text
cb7ce5a50357fe01d4e9bf0a6c65d8767e431d3124d3e14d06e90f0bd46c38fa
```

Prior locally checked source: `6027af1a083bbca309f406762dc7526e11aac6f4c4cdb90d9aa7427ad04182f9`.
Only the opening explanatory comment changed. The bytes after that comment
are identical; both comment-stripped formal texts hash to
`d1900d991547da0aa0c2f6b380ec2a60707d66907c36c39dca7eb4e3602f760a`.
The fresh candidate run, not merely the prior run, passed.

- Lean **4.34.1**, compiler commit `5045d0056413266e57c625dcd7c365b10e377c52`.
- mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612`; all nine source revisions
  in the unchanged predecessor `lake-manifest.json` are checked, with clean
  tracked dependency checkouts. Eight library roots are used; `Cli` is tooling-only.
- The checker selects real toolchain binaries, records their hashes, rejects
  identical elan-shim proxies, and constructs a fresh environment and explicit
  `LEAN_PATH`. It rejects reserved or conflicting module roots. Existing
  `CompilerAudit` object files are not reused.
- The 27 theorem reports contain only `propext`, `Classical.choice` and
  `Quot.sound`. The parser has missing, duplicate, extra-name and foreign-axiom
  controls, including names containing apostrophes.
- The explicit leaf-module replay checks the bridge's own declarations.
  Predecessor modules are freshly compiled, but their separate historical leaf
  replays are **not** all repeated. Imported libraries are trusted cached
  artifacts: their binary-to-source correspondence is **not** established by
  a cold rebuild or by the path-and-size inventory. The same Lean kernel is used.

## Commands and publication gate

From a checkout with the committed source history:

```sh
python -B scripts/research_package.py --package research/selected-compiler-source-bridge --check-only
python -B scripts/research_package.py --package research/selected-compiler-source-bridge
python -I -B research/selected-compiler-source-bridge/lean/tests/test_check.py
python -I -B -O research/selected-compiler-source-bridge/lean/tests/test_check.py
python -I -B research/selected-compiler-source-bridge/lean/check.py --output FRESH_ABSOLUTE_OUTPUT --toolchain TOOLCHAIN_ROOT --packages PACKAGES_ROOT --timeout 180
```

The generic registered command runs Python only. The Lean command is separate,
serial and explicit; it performs no installation or download. Its output
contains `PREFLIGHT.json`, `RUNS.json`, `RESULT.json` and per-command diagnostics.
A preflight-only run is not a proof check.

Publication is gated on committed-byte/source-history checks and the shared
exporter's checked bundle, followed by replay from a fresh Git-free extraction:

```sh
python -B scripts/check_research_commit.py --package research/selected-compiler-source-bridge --ref HEAD --check-source-history
python -B scripts/export_research_package.py export --package research/selected-compiler-source-bridge --ref HEAD --output FRESH_ABSOLUTE_TAR
python -B scripts/export_research_package.py check FRESH_ABSOLUTE_TAR
# After extracting the checked bundle into a fresh directory, run there:
python -I -B research/selected-compiler-source-bridge/verify.py
python -I -B -O research/selected-compiler-source-bridge/verify.py
```

The extracted direct verifier requires `.research-export.json` when there is no
Git checkout and checks its exact file inventory, sizes and hashes before and
after execution. The shared archive check additionally checks tar modes. This
unsigned manifest is transport integrity, not authenticated provenance. Obtain
the commit or archive through a trusted channel. The declared inputs include
all 61 lifetime-allowlist files, including `scratch_pool.py`, rather than just
the older census's 121-input closure. No agent scratch directories or compiled
Lean objects are shipped.

A Windows read-only temporary Git object caused the first runner-unit teardown
to fail. Cleanup was corrected and both unit-test modes were rerun successfully.
This was a harness-cleanup error, not a failed Lean theorem. No formal proof
text or frozen predecessor files were altered to make a check pass.

## Coordination and prior coverage

Canonical main was refreshed at `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Priority revision 6 and selected conditional κ = 0.001672660197076918 are unchanged.
The 18 October overlap pass covered complete metadata pagination for 351 open
PRs, 2,964 closed/merged PRs and 2,456 discussion records (not 2,456 threads).
The entry reads of #1163, #1166 and #2319 were complete. Closing #1163/#2319
reads were complete; closing #1166 coverage was its latest 100 comments plus
exact destination rechecks after an older-page request failed. Broad open-PR
changed-path refresh timed out; seven targeted file inventories succeeded.
No duplicate successor was found within that coverage, not as a novelty guarantee.
Relevant heads and the original finding are rechecked before publication.

The read of Jose Manuel's [PR2569](https://github.com/CrocSwap/integer-mult-bounds/pull/2569)
found an existing written prefix-count/bijection proof for byte-identical LOW
codec source. Its README reports finite GL2/GL3 checks and six GL64 ordinals;
those predecessor tests were **not rerun here**. The remaining task is formal
implementation-level correspondence, not rediscovering an absent written proof.
The source refinements in #2989/#3041/#3223 and parallel shared-checker work
#3602/#3634 are credited in the README; they are not silently imported as proof
premises or superseded by this package.

PR3391 remains **archived / partially reviewed**. Its linked hosted workflow
ended `failure` with **zero jobs and zero check runs**; that was neither an
executed scientific-test failure nor a hosted pass. The successor does not
change the ledger or selected frontier. The selected-wide orientation helper
was not completed in this scoped sparse checkout because unrelated supplier
packages were absent; no selected-wide or native replay is claimed.

## Remaining limitations

The theorem is a manually modelled, idealized/unbounded trace transport, under
primitive correspondence, LOW inverse, budget-alignment and freshness premises.
The original-source fixtures are bounded and seeded, not successful cold GL64
initialization or selected numerical endpoint tests. The Windows census adapter
changes one authenticated inventory-path spelling expression only; the lifetime
importer separately bypasses loader bootstrap after source-only hash checks.

Neither the capacity argument nor the Python operational semantics is formalized
by this Lean bridge. There is no actual GL64 inverse proof here, prefix/resource
feasibility theorem, wrapper-sharing refinement, native/stock/precision invoice,
full multiplication theorem, selected κ change, or independent human approval.
