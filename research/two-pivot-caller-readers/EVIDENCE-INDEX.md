# Evidence index

Start with the [README](README.md), the [all-q proof](source/caller/HANDOFF-FAMILY-PROOF.md),
the [tail proof](source/native-frames/HANDOFF-FAMILY-TAIL-PROOF.md), and the
[fixed-chart proof](FIXED-CHART-PROOF.md). Then read [verify.py](verify.py) and
the replay dependencies below. Large historical receipts need not be read as
new proofs to review this package.

This index describes the unchanged verifier and frozen evidence first published
at `896e2a2e89fd2b54d4defafaef3b91bb4b33b493`. It is a reading guide, not a new
manifest or a change to verification coverage. The classifications follow the
six entrypoints at the end of `verify.py`, their transitive calls, and an observed
direct replay. They do not describe every optional historical script entrypoint.

## Required files versus replay coverage

**Keep every file in [BINDINGS.json](BINDINGS.json).** Before doing mathematics,
`verify.py` checks all 59 retained files against their SHA-256 pins. A missing or
changed archival file fails this integrity gate too. “Archival-only” below means
its mathematical contents are not consumed by the registered replay; it does
not mean optional for running or exporting this package. No frozen receipt,
source, original, notice, or pin was changed to add this index.

The 29 retained JSON files divide as follows. Line counts describe frozen bytes;
the five top-level JSON metadata files are outside this table.

| Role in the registered replay | Files | Lines | Bytes |
|---|---:|---:|---:|
| Mathematical inputs, expected receipts, or fixed certificates | 14 | 151,471 | 2,570,030 |
| Status-only dependency, not a replay of its mathematical body | 1 | 36,969 | 611,360 |
| Archival-only mathematical receipts, checked for byte integrity | 12 | 83,356 | 1,477,217 |
| Attribution/provenance JSON, checked for byte integrity | 2 | 181 | 7,146 |

Hashes establish retention relative to this publication, not correctness or
independent authentication. A saved `PASS` status is not a fresh proof. The
written all-q argument, finite fixture replay, fixed-chart certificate and
supplier-admission obligations remain distinct. No new κ is claimed.

## Replay entrypoints

All paths below are relative to this package. In the inventories, **input** means
mathematical fields are consumed, **expected** means the replayed result is
compared with the saved mathematical body, and **certificate** means fixed
choices or witnesses are checked. A file can have more than one role.

| Entry in `verify.py` | Main implementation | What the replay checks |
|---|---|---|
| `replay('handoff_family', 'prove', ...)` | [handoff_family.py](source/caller/handoff_family.py) | Reconstructs the retained family fixtures and compares the mathematical receipt. The written induction supplies the all-q claim. |
| `replay('review_handoff_family', 'run', ...)` | [review_handoff_family.py](source/root-chronology/review_handoff_family.py) | Combines the saved family prefixes and tails for q=2,3,4; checks all original columns, inverse orders, paid-progress control and full-stock-plus-8f bills. |
| `charts()` | [native_chart_search.py](source/root-chronology/native_chart_search.py), [signed_chart_optimization.py](source/root-chronology/signed_chart_optimization.py), [batch_paid_progress.py](source/root-chronology/batch_paid_progress.py) | Recompiles fixed signed choices for six/eight banks, checks equivalent complete words and bills 72f/128f; rebuilds the six-bank graph and checks 36 edge-disjoint odd Eulerian subgraphs and a duplicate-cycle rejection. |
| `replay('audit_encoded_complete', 'run', ...)` | [audit_encoded_complete.py](source/root-chronology/audit_encoded_complete.py) | Decodes the triangular prefix/tail literal circuits; checks each unary rank, full target, inverse orders and omitted-Q rejection; compares the retained receipt reporting 138f. The total 138f is a literal in this producer, not a recomputed sum. |
| `replay('balanced_physical_replay', 'produce', ...)` | [balanced_physical_replay.py](source/caller/balanced_physical_replay.py) | Constructs the balanced word using a regenerated prefix and saved tail; checks literal phases/ranks, full target, inverse orders and the 138f receipt. |
| `saved_quadratic()` | [quadratic_charts.py](source/root-chronology/quadratic_charts.py), [audit_encoded_complete.py](source/root-chronology/audit_encoded_complete.py) | Recompiles both saved quadratic choices; checks serialized events, target, inverse orders, rank mass 130f and omitted-query rejection. |

`replay()` compares the entire mathematical body after removing only the
explicitly enumerated provenance keys in `verify.py`; raw input bytes are checked
separately. The certificate routines check their stated fields and properties,
not every historical claim in their JSON. No optimization search is rerun or
solver bound trusted. Historical absolute paths are provenance labels resolved
through `BINDINGS.json`, not directories a reviewer must recreate.

## JSON used by mathematical replay

These are the 14 mathematical dependencies, including expected outputs. Each is
also hashed by the initial integrity pass.

| File | Role and consumer |
|---|---|
| [caller/HANDOFF-FAMILY.json](source/caller/HANDOFF-FAMILY.json) | **Expected** for `handoff_family.prove`; **input** prefixes for `review_handoff_family.run`. |
| [native-frames/HANDOFF-FAMILY-TAIL.json](source/native-frames/HANDOFF-FAMILY-TAIL.json) | **Input** tails for `review_handoff_family.run`. |
| [root-chronology/INDEPENDENT-HANDOFF-FAMILY.json](source/root-chronology/INDEPENDENT-HANDOFF-FAMILY.json) | **Expected** complete-family receipt for `review_handoff_family.run`. |
| [root-chronology/INDEPENDENT-HANDOFF-SIX.json](source/root-chronology/INDEPENDENT-HANDOFF-SIX.json) | **Input** six-bank source word for `charts()`, including its cycle graph. |
| [root-chronology/HANDOFF-COMPLETE-Q3.json](source/root-chronology/HANDOFF-COMPLETE-Q3.json) | **Input** eight-bank source word for `charts()`. |
| [root-chronology/SIGNED-CHART-HANDOFF-SIX.json](source/root-chronology/SIGNED-CHART-HANDOFF-SIX.json) | **Certificate** of fixed six-bank choices/events and matching 72f bill, checked by `charts()`. |
| [root-chronology/SIGNED-CHART-HANDOFF-Q3.json](source/root-chronology/SIGNED-CHART-HANDOFF-Q3.json) | **Certificate** of fixed eight-bank choices/events and matching 128f bill, checked by `charts()`. |
| [root-chronology/CHART-CYCLE-PACK-HANDOFF-SIX.json](source/root-chronology/CHART-CYCLE-PACK-HANDOFF-SIX.json) | **Certificate** of 36 odd Eulerian subgraphs, checked by `charts()`; the written fixed-chart proof supplies the general cost implication. |
| [caller/ENCODED-PHYSICAL-PREFIX.json](source/caller/ENCODED-PHYSICAL-PREFIX.json) | **Input** literal triangular prefix for `audit_encoded_complete.run`; also read for provenance hashes by the balanced producer. |
| [native-frames/ENCODED-STAGE-TAIL.json](source/native-frames/ENCODED-STAGE-TAIL.json) | **Input** literal tail for `audit_encoded_complete.run` and `balanced_physical_replay.produce`. |
| [root-chronology/INDEPENDENT-ENCODED-COMPLETE.json](source/root-chronology/INDEPENDENT-ENCODED-COMPLETE.json) | **Expected** for `audit_encoded_complete.run`; **input** original triangular word for `saved_quadratic()`. |
| [caller/BALANCED-PHYSICAL-REPLAY-Q3.json](source/caller/BALANCED-PHYSICAL-REPLAY-Q3.json) | **Expected** for `balanced_physical_replay.produce`; **input** original balanced word for `saved_quadratic()`. |
| [root-chronology/CLUSTER-INDEPENDENT-ENCODED-COMPLETE-ALLPAIRS.json](source/root-chronology/CLUSTER-INDEPENDENT-ENCODED-COMPLETE-ALLPAIRS.json) | **Certificate** of saved triangular quadratic choices/events and 130f bill, checked by `saved_quadratic()`. |
| [root-chronology/CLUSTER-BALANCED-PHYSICAL-REPLAY-Q3-ALLPAIRS.json](source/root-chronology/CLUSTER-BALANCED-PHYSICAL-REPLAY-Q3-ALLPAIRS.json) | **Certificate** of saved balanced quadratic choices/events and 130f bill, checked by `saved_quadratic()`. |

### Status-only dependency

[caller/ENCODED-STAGE.json](source/caller/ENCODED-STAGE.json) is parsed by
`encoded_physical.produce`, called by the balanced producer, solely to require
its saved `status` to equal `PASS_NATIVE_ZERO_ENCODED_STAGE_ALL_COLUMNS_ALL_F`.
Its bytes are also hashed. The registered replay **does not rerun
`encoded_stage.prove` or compare this receipt's mathematical body**. The complete
triangular and balanced physical words receive the separate direct checks above.
This 36,969-line file must not be counted as 36,969 lines of freshly replayed
evidence merely because the package passes.

## Archival-only mathematical receipts

These 12 receipts are retained unchanged and hashed, but their JSON mathematical
contents are not parsed or compared by the registered commands. Their original
statuses, scope limits and provenance remain historical evidence.

| File | Retained context; current replay distinction |
|---|---|
| [caller/BALANCED-STAGE-TRIAL.json](source/caller/BALANCED-STAGE-TRIAL.json) | Earlier balanced-prefix trial. The balanced producer also reads its bytes to report a provenance hash; it does not replay this trial. |
| [caller/NESTED-FAMILY.json](source/caller/NESTED-FAMILY.json) | Earlier nested-family receipt; the complete handoff-family receipts above are checked instead. |
| [caller/NESTED-SIX.json](source/caller/NESTED-SIX.json) | Earlier six-bank prefix receipt. |
| [caller/PIVOT-PLANE-PROBE.json](source/caller/PIVOT-PLANE-PROBE.json) | Bounded source-retraction screen. Its Python helper is imported, but this saved screen is not read. |
| [caller/QUADRATIC-MODEL-REVIEW.json](source/caller/QUADRATIC-MODEL-REVIEW.json) | Separate model-audit receipt. Only helper functionality from its producer is used; that producer's complete audit is not rerun. |
| [root-chronology/CHRONOLOGY.json](source/root-chronology/CHRONOLOGY.json) | Restricted local chronology screen. Algebra functions from `chronology.py` are used, not this receipt. |
| [root-chronology/ENCODED-COMPLETE-Q3.json](source/root-chronology/ENCODED-COMPLETE-Q3.json) | Earlier serialized complete encoded word; current direct checks assemble the prefix/tail and compare `INDEPENDENT-ENCODED-COMPLETE.json`. |
| [root-chronology/EXACT-CHART-RESULTS.json](source/root-chronology/EXACT-CHART-RESULTS.json) | Earlier chart-validation summary. Current `charts()` checks the underlying words/cycle witness directly; it does not compare this summary. |
| [root-chronology/INDEPENDENT-COMPLETE-SIX.json](source/root-chronology/INDEPENDENT-COMPLETE-SIX.json) | Earlier complete six-bank caller receipt. |
| [root-chronology/INDEPENDENT-SHARED-CALLER.json](source/root-chronology/INDEPENDENT-SHARED-CALLER.json) | Earlier complete four-bank shared-tail receipt. |
| [root-chronology/PAID-PROGRESS-BATCHING.json](source/root-chronology/PAID-PROGRESS-BATCHING.json) | Earlier batching receipt; current family replay calls the batching implementation directly. |
| [root-chronology/SAVED-QUADRATIC-WORDS-VALIDATION.json](source/root-chronology/SAVED-QUADRATIC-WORDS-VALIDATION.json) | Earlier saved-word validation summary. Current `saved_quadratic()` checks the two underlying certificates directly. |

## Retained Python sources

The 19 source modules below are loaded by the registered verifier. Loading a
module does not imply that its standalone driver, search or complete audit ran.
The source-byte loader authenticates and compiles the same bytes with
`optimize=0`, including when the parent verifier is run with `-O`.

| Functionality | Loaded source files |
|---|---|
| Handoff construction and algebra dependencies | [handoff_family.py](source/caller/handoff_family.py), [nested_family.py](source/caller/nested_family.py), [nested_prefix.py](source/caller/nested_prefix.py), [free_ops.py](source/caller/free_ops.py), [plane_group.py](source/caller/plane_group.py), [pivot_plane_probe.py](source/caller/pivot_plane_probe.py) |
| Complete family replay and signed charts | [review_handoff_family.py](source/root-chronology/review_handoff_family.py), [chronology.py](source/root-chronology/chronology.py), [batch_paid_progress.py](source/root-chronology/batch_paid_progress.py), [native_chart_search.py](source/root-chronology/native_chart_search.py), [signed_chart_optimization.py](source/root-chronology/signed_chart_optimization.py) |
| Physical and quadratic replay | [audit_encoded_complete.py](source/root-chronology/audit_encoded_complete.py), [quadratic_charts.py](source/root-chronology/quadratic_charts.py), [balanced_physical_replay.py](source/caller/balanced_physical_replay.py), [encoded_physical.py](source/caller/encoded_physical.py), [quadratic_model_review.py](source/caller/quadratic_model_review.py) |
| Native model and inherited exact helpers | [native_model.py](source/native-frames/native_model.py), [clifford_exact.py](source/vendor/clifford_exact.py), [full_stabilizer_bound.py](source/vendor/full_stabilizer_bound.py) |

The remaining six retained Python files are **not loaded** by these entrypoints:

| File | Retention role |
|---|---|
| [caller/encoded_stage.py](source/caller/encoded_stage.py) | Historical stage producer; additionally hashed for producer provenance. Its proof routine is not executed. |
| [caller/nested_six.py](source/caller/nested_six.py) | Historical prefix producer. |
| [native-frames/lifted_algebra.py](source/native-frames/lifted_algebra.py) | Historical lifted-algebra implementation. |
| [root-chronology/verify_chart_results.py](source/root-chronology/verify_chart_results.py) | Original chart-verification driver; the portable adapter uses `charts()`. |
| [root-chronology/verify_saved_quadratic_words.py](source/root-chronology/verify_saved_quadratic_words.py) | Original saved-word driver; the portable adapter uses `saved_quadratic()`. |
| [original/native-frames/native_model.py](original/native-frames/native_model.py) | Original before the three path-only adaptations recorded in `BINDINGS.json`; retained for comparison, not execution. |

## Proofs, attribution and package controls

The two retained written proofs are
[HANDOFF-FAMILY-PROOF.md](source/caller/HANDOFF-FAMILY-PROOF.md) and
[HANDOFF-FAMILY-TAIL-PROOF.md](source/native-frames/HANDOFF-FAMILY-TAIL-PROOF.md).
They are hashed, not machine-checked written arguments. The package-level
[FIXED-CHART-PROOF.md](FIXED-CHART-PROOF.md) is likewise a written proof, separate
from the finite cycle-certificate checks.

Five retained credit/provenance files complete the 59-file binding inventory:
[NOTICE.md](source/vendor/credits/NOTICE.md),
[PR533-NOTICE.md](source/vendor/credits/PR533-NOTICE.md),
[PR531 NOTICE.md](source/vendor/credits/vendor/pr531/NOTICE.md),
[PR531 SOURCES.json](source/vendor/credits/vendor/pr531/SOURCES.json), and
[PR523-ANCESTRY.json](source/vendor/credits/vendor/pr531/inputs/PR523-ANCESTRY.json).
They are hashed, not mathematical replay inputs. Preserve all source-specific
credit and license obligations regardless of replay role.

At package level, [BINDINGS.json](BINDINGS.json) controls retained-file hashes
and original-to-portable path mappings; [VERIFY.json](VERIFY.json) registers
normal and optimized replay; [SOURCES.json](SOURCES.json) pins Git provenance;
[TASK.json](TASK.json) records the assigned/changed scope and open questions;
[RELATED-WORK.json](RELATED-WORK.json) records overlap and prior publication.
[LICENSE](LICENSE) and [NOTICE.md](NOTICE.md) retain the package's license and
credit. These controls and the written proofs are not substitutes for each other.

Use the two commands in [README: Reproduce](README.md#reproduce) for registered
replay and committed-source/history checks. The registered commands consume the
complete package, including the archival files; this index is not a reduced
export recipe and does not authorize regenerating or pruning frozen evidence.
