# Native evidence transfer to the P104 successor

This package answers the [PR5573 handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/5573#issuecomment-6402512076).
It binds Matarener's PR5572 native evidence to GamingPuzzled's PR5569 word.
It adds exact finite operator checks. It makes no new kappa claim.

## Exact scope

The successor has 3,131 named tasks and 3,130 distinct operator specifications.
The difference is one identical specification shared between task kinds.
The inventory binds all 4,189 occurrences:

| Occurrence | Count |
|---|---:|
| Paid MOVE, including owned returns | 3,454 |
| Helper endpoint | 527 |
| Main input adapter | 104 |
| Main output adapter | 104 |

The predecessor receipt covers 3,188 tasks and 3,187 distinct specifications.
Exact equality permits reuse for 2,631 successor specifications and 3,578 occurrences.
The remaining 499 specifications cover 611 occurrences.
The verifier compares all 512 columns for each remaining specification.
It also repeats four retained specifications as positive controls.

Helper 706 illustrates the distinction. Its new endpoint pair `(3, 559)` needs a fresh comparison.
Its final paid pair `(549, 559)` already has exact predecessor evidence.
All 11 owned returns also retain exact predecessor evidence.

`RESULT.json` records the result and controls. `BINDINGS.json` records every occurrence and its evidence.
Each reused specification names its predecessor tasks and matrix digest.
Each fresh specification records its new matrix digest.

## Why reuse applies

For a frame pair A, B, the literal operator is `chart(A)^* chart(B)`.
The compiler lowers this operator to a native recipe.
The independent interpreter compares that recipe with the literal gate sequence.
Main adapters use their actual input or output frame and native port.

A reusable specification contains the following data:

- Dimension nine and the ordered frame basis vectors, or the adapter frame and port.
- The complete lowered recipe, including phases and offsets.
- The actual recipe gates, the literal expected gates, and the expected rank.

SHA256 indexes specifications. Canonical descriptor bytes must also match exactly before reuse.
Frame numbers and equal ranks alone never authorize reuse.
The compiler, literal definitions, interpreter, and predecessor word must match the prior source manifest.
The complete prior receipt must cover exactly the reconstructed predecessor tasks.

These conditions preserve both sides of each previously compared finite matrix identity.
The occurrence inventory then binds that identity to the successor's actual event or endpoint.
The inventory verifies MOVE chronology, nesting, ownership flags, scalar charts, and final frames.
It does not reprove the complete scalar endpoint identity or the physical caller.

All fresh comparisons use exact integer real and imaginary parts with a dyadic denominator.
They check every matrix column, absolute phase, unit norm, and support size `2^rank`.
The matrix digest uses the exact serialization from PR5572.
The retained positive controls must reproduce their original digests.

Controls reject incomplete or duplicate evidence, unknown tasks, incorrect ranks, changed phases, and incorrect child signs.
Additional controls distinguish unchanged frames under new labels from changed frames under unchanged labels.
An owned-return flag change fails the occurrence inventory.
All acceptance predicates in this package remain active under `python -O`.

## Reproduction

Run the registered checks from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-successor-native-binding
```

The manifest runs normal and optimized Python serially. Each command uses at most two worker processes.
The package needs Python 3.12 and its standard library.
The direct command also works in a committed export without Git:

```sh
python3 -B research/p104-successor-native-binding/verify.py
```

Use `--jobs 1` for serial operator execution.
Use `--write` to regenerate both scientific receipts.
The `--inventory-only` mode reports coverage without a mathematical pass.

## Validation

CPython 3.12.3 on Linux passed the final normal receipt generation in 219.15 seconds.
The registered normal and optimized commands passed serially in 365.99 seconds.
Both commands reproduced the same scientific receipts and all 14 controls.
The package outcome is `partial` because complete supplier admission remains outside its scope.

The committed-byte and source-history checks passed for all 16 package and input files.
The export integrity check also passed at scientific commit `907876616f90ce65af6f5abfc23c865f568296e2`.
Optimized replay passed in 146.61 seconds in a read-only, Git-free export whose path contains spaces.
All 16 exported file hashes remained unchanged.
Separate word and prior-receipt corruption controls failed authentication before operator replay.
Hosted validation remains separate from these local checks.

## Sources and limits

The base is canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority revision seven.
The selected PR5413 record remains unchanged.

| Source | Exact commit |
|---|---|
| PR5569 successor word | `af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf` |
| PR5572 prior receipt, verifier, and source manifest | `dba3cf67c800f32f04c80437138a51310dc08c1b` |

`inputs/` retains these four files byte for byte. `INPUTS.json` records their original paths, Git blobs, commits, and SHA256 hashes.
Their bytes were compared with those Git objects before publication.
The retained copies make replay independent of unmerged predecessor branches.
`SOURCES.json` binds the four canonical inputs and the original task context.

The 2,631 reused results remain inherited PR5572 evidence.
This package does not repeat that entire historical computation.
The four fresh positive controls do not independently certify every inherited digest.
The full predecessor evidence must remain trusted within this explicit boundary.

This result concerns finite nine-axis matrices at the exact listed sources.
It does not prove tensor substitution at every width, whole-caller admission, owned erasure, or compiler closure.
Precision, fixed-tape costs, stock, funding, and analytic recovery remain separate obligations.
The package does not transfer evidence automatically to another successor.

The final overlap check found concurrent PR5580 at `6efa248cf456d6101d757e9d09ba29711d18a13a`.
That contribution changes one contact in the PR5569 word.
This package retains its exact PR5569 scope. PR5580 needs its own descriptor and occurrence comparison.

## Open next questions

The next useful task is complete admission of the exact successor caller.
Its first step is a join between this occurrence inventory and the physical caller and funding evidence.
This matters because matrix equality alone does not establish a legal, funded supplier.
The inherited framework assumptions remain blockers. `TASK.json` records this question and the overlap scope.

A separate next step is native evidence transfer to PR5580.
Start with its exact word and compare every descriptor and occurrence against this package.
Fresh comparisons are necessary for unmatched specifications. The present receipt does not authorize automatic transfer.

## Credit and license

GamingPuzzled / Joel Pulikkan supplied PR5569. DreamingOfClouds supplied PR5561 and the earlier successor mechanism.
thu-nmrc supplied PR5551. Ali Romman supplied the P104 word lineage in PR5544 and PR5545.
Matarener / Mark supplied the PR5572 full native receipt.
Chris R / Clear1nsight supplied the PR5548 dense interpreter, PR5550 caller audit, and PR5573 handoff.
The Clifford compiler, native definitions, controller, geometry, and analytic contributors retain their existing source credit.

The new occurrence binding and replay package are by Scratch-net, with substantial OpenAI Codex assistance.
Apache-2.0 applies. Frozen source files retain their original attribution.
