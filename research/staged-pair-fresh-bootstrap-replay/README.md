# PR3605: complete public replay with a fresh retained bootstrap

This package records one local execution of Ross Richardson's exact PR3605 public
wrapper at `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`. It answers the outstanding
[full-wrapper replay handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19016211),
linked from the [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/3606).
The predecessor had a complete original release, but its later portable wrapper
had only been exercised through preparation. No predecessor source is changed.

**Full original execution: PASS**, exit 0, in **2,443.539 seconds (40m 43.5s)**,
from 2026-10-18 13:20:59 UTC to 14:01:42 UTC. All 18 top-level stages completed;
the 157 source/input files were unchanged, and stderr was empty. The final
release receipt is
`efc62e10c52ffd5170712d9f9edc00d79bedf73830a5111dbdfd7493726bcdc6`.
The generated package manifest is
`7a94445290bc20adecb1c8a378c73987a71aade611c1ef5b7e295ff037e674b6`.
The compact archive contains 214 members in 880,507 bytes; its exact digest and
member inventory are recorded in `EXPECTED.json`. Normal and optimized bounded
checks pass with all 15 rejection controls.

Adjacent [PR3659](https://github.com/CrocSwap/integer-mult-bounds/pull/3659)
checks the published T740 histogram and compares its root with the selected
value. This contribution instead executes the public source/native/owner/
physical/prefix/outer wrapper, including the fresh retained bootstrap.

The endpoint being checked is the existing conditional PR3605 value
`0.001730006549538841847005 - 10^-46 - 10^-70`. This is a replay contribution,
not a new construction, improved endpoint, selected-frontier update or all-size
theorem. The complete paid profile is
`{1:16417896,2:4835160,3:1540174,4:679321,5:143992,6:3,8:53280,48:283185}`.
It has 2,717,280 owner roles, 6,660 calls, 740 replicas, live stock 663,040 and
physical stock 663,549. The inherited conditional hypotheses remain open.

## What was fresh

The original command was run with `--jobs 1`, no `--retained`, and no
`--prepare-only`, into a previously nonexistent directory. It uses the exact
157 supplied package/word/dependency files, authenticated against the original
Git objects before execution and checked again afterwards. Child Git processes
inherit `GIT_NO_REPLACE_OBJECTS=1`; object-directory overrides and optimization
settings are cleared. The environment and original argv are retained verbatim.

The expected sequence contains 18 top-level stages. The retained bootstrap
executes four native chains (PR2833 base/extra and retained PR1297 base/extra),
each with all five native gates, and a fresh 16-stage retained-parent admission.
The changed staged base/extra providers are then run afresh. The final native
receipt must reference the exact bootstrap receipt produced by this run; the
seven admission stages and six independent owner/moment/outer stages must finish.

There is **no external retained-cache reuse**. Later stages correctly reuse the
native caches and parent receipt just produced in this run. The original parent
still uses retained geometry inputs and reports `parent_geometry_reuse: true`;
this is not regeneration of every ancestral geometry artifact. All original
reuse flags are preserved. The source-only predecessor `--dry-run` inside the
wrapper creates its recipe; that is distinct from the omitted top-level
`--prepare-only` shortcut.

The exact 648-file staged source manifest is
`adb145b4f36ca330c34c0dbdb847351dafdc4ca9cd7bb4e1de01ed634d96bfe1`.
The bootstrap's 541-file source manifest is
`c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f`,
and its parent manifest is
`e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4`.

## Evidence and the bounded check

`evidence.tar.gz` retains the original wrapper/claim/scope notices, execution
record, pre/post input identities, raw stage logs, exact stage scripts where
recorded, manifests, native-cache inventories, parent and final release receipts,
actual controller audit and independent endpoint result. `EXPECTED.json` binds
its exact member inventory and bytes. Original local paths and timings are
preserved as execution provenance, not required paths for the bounded replay.

`collect.py` reads the completed local run and checks every source, generated
package and native-cache file against its manifest/receipt before making this
small transcript. Large source archives, owner journals and native output files
are omitted. The retained `COLLECTION.json` records their checked inventories.
The public bounded checker checks those recorded inventories and retained bytes;
it cannot reauthenticate omitted bytes or prove that a transcript was executed.
A new mathematical replay requires the separate long command below.

```sh
python3.12 -B scripts/research_package.py \
  --package research/staged-pair-fresh-bootstrap-replay
```

The registered normal and `-O` checks use explicit failures, validate the full
ordered stage inventories, script/log bindings, actual bootstrap freshness,
bootstrap-to-final receipt chain, exact pinned endpoint and complete profile.
Their negative controls include an unfinished attempt, an external retained
argument, omitted bootstrap/parent/native gates, inconsistent reuse evidence,
corrupted logs, an empty provider map, a changed paid profile, owner/arithmetic
leaf receipts contradicting their summary, an expanded historical-difference
claim, and an endpoint
that is still above the original wrapper's `0.00173` floor. These checks do not
invoke native solvers or rerun the long scientific computation.

`SOURCES.json` pins the canonical base catalogue and selected record as historical
provenance. The foreign PR head is recorded inside the local source evidence,
not introduced as an unavailable Git dependency of the registered checker.
The retained original snippets serve source attribution and command inspection;
they are not a replacement source export for the long replay.

## Exact comparison with the original generated package

The original public `evidence/FINAL-BINDING.json` records the complete historical
652-file generated package plus its manifest. This run differs in exactly four
JSON files; the other 648 file bytes match, including every validator and the
allocation gzip containers. Two fresh `CLIFFORD-REVIEW.json` raw hashes change
because their receipts contain measured `seconds`. Their referenced canonical
word/recipe bytes and normalized semantic identities are unchanged.

The local collector restores the two historical raw phase hashes in the actual
352 MiB `new/PLAN.json`, restores the resulting PLAN hash in `new/SPEC.json`,
and restores the resulting SPEC hash in `outer/INDEPENDENT.json` and
`outer/LEDGER.json`. Each replacement occurs exactly once and reproduces the
corresponding historical SHA-256 exactly. It does not rewrite the generated run.
The original `generated_identity.py` is retained unchanged; its normalization
removes only phase timing and canonicalizes the validated word/recipe identities.

The compact archive omits PLAN. `historical.py` directly reconstructs the three
smaller retained JSON hashes, recomputes both phase semantic identities, and
checks the exact recorded PLAN replacement edges. Reauthenticating the omitted
PLAN requires its actual bytes and the collector or a full rerun. The compact
record is not a substitute for those bytes. Thus the different generated
manifest is classified as timing/provenance variation by the local execution
check, without weakening any immutable historical pin or numerical check.

## Run the original long command

Use a separate checkout at the exact PR3605 head and fetch the nine historical
commits listed in its `research/staged-644-660-conditional-release/FETCH.txt`.
These are public immutable source inputs; the original wrapper fails before
work if any object is absent. Follow its original dependency instructions.
The observed environment was Python 3.12.14 on macOS arm64, with
`numpy==2.5.4`, `scipy==1.18.1`, `sympy==1.14.0`, `mpmath==1.3.0`,
`gmpy2==2.3.2` and `psutil==7.2.2`. Use one heavy replay at a time.

```sh
# In an isolated exact-head checkout containing the historical Git objects:
env -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES \
  -u PYTHONOPTIMIZE -u PYTHONPATH \
  GIT_NO_REPLACE_OBJECTS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  /absolute/path/to/python3.12 -B \
  research/staged-644-660-conditional-release/reproduce.py \
  --repo /absolute/path/to/exact-head-checkout \
  --word-package /absolute/path/to/exact-head-checkout/research/staged-644-660-width-reduction \
  --work /absolute/path/to/new-disjoint-output \
  --jobs 1
```

No flag bypass is used. Preserve the original source and all output receipts.
The command can take tens of minutes and is intentionally outside the bounded
registered-package timeout. The original recorder is retained in the transcript
as `attempt/record_run.py`; it records full argv/environment/timestamps and input
identity checks around the original command, without modifying it. `collect.py`
accepts `--source`, `--work`, `--attempt`, and a fresh `--out` to inspect such a
completed run and export a new transcript. A newly collected transcript has its
own timing/log hashes; compression byte equality is not a mathematical claim.

## Preserved historical distinctions

The actual controller audit and generated `new/SPEC.json` require 25 rejecting
controls. The inherited high-level supplier summary still says 15; it is
retained verbatim and is not used as the authoritative count. Similarly, old
3000/3080-digit prose in the immutable template is historical: the actual modern
SPEC uses endpoint precision 24. These are predecessor-documented caveats, not
new changes to frozen receipts.

The inherited compiler/uniform-cost, common-label and mutable-source physical
realization, whole-call hosting, rounding/precision/tape, exact recovery,
analytic transfer, bootstrap-time and PR559/BIT H1–H5 hypotheses remain.
Finite replay success does not prove those all-size hypotheses, global packing
optimality, unconditional multiplication bounds or a formal-kernel theorem.

## Open next questions

- Obtain independent human review of the unchanged staged scalar words and their
  physical/operator interpretation. This replay checks the existing programs;
  it does not replace semantic mathematical review. Start from the exact PR3605
  source and current [canonical thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/3606),
  respecting the separate active review claim.
- Reproduce the same full command on another supported platform, preserving all
  source pins and comparing every proof-relevant payload. This would add platform
  evidence; first provision the documented dependencies and historical Git
  closure. Do not infer cross-platform success from this macOS run.

Structured questions and the explicit scope change from the portable-replay card
are recorded in `TASK.json`.

## Credit

Ross Richardson (@RossRichardson) authored PR3605 and its exact wrapper. The
source lineage includes dcharb78's PR3133, Jeremy Diviney's PR3148 owner/cap
machinery, Yiyang Lu's staged-kernel/flow work, Nick Petalas's copied owners,
Tekalign's independent/native checks, Marius-Paul Dumitrean's endpoint/native
work, Jeremy Kothe's preload/source work, and dataisfire's arithmetic lineage.
Retained `SOURCE-NOTICE`, `owners/SOURCE-CREDITS.md`, and source script headers
preserve their more detailed attribution. PR2833/PR1297 inherited source notices
remain unchanged in the original replay exports. The repository Apache-2.0
license applies to this new audit.

roger-sato prepared this independent execution transcript and bounded evidence
checker with substantial OpenAI Codex assistance in execution, implementation,
review and documentation. Separate AI review is not independent human or
formal-kernel review.
