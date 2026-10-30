# The selected P112 cut is a scatter

The selected native cut updates targets by `d <- d + S p`. Under a target
basis change `z = U d`, its coefficient matrix must become **`U S`**.
The valid abstract reader identity uses `U^{-T} S`; installing that reader
as a scatter does not implement this selected forward map.

This package binds that distinction to all 176 literal cut instructions and
gives a reachable arbitrary-dirty counterexample. On the first tetrad, one
coefficient is `-1/2` for the correct scatter, `-1/4` for the inverse-transpose
reader, and `0` for the proposed hybrid. The reader identity itself is valid.

It also constructs a restored literal sandwich
`U; scatter(U S); U^{-1}`. The exact same-frame identity
`U^{-1}(U d + U S p) = d + S p` holds for every dirty target and every
512-address complex vector. All 704 normalized ordinary scalar columns,
common-frame conditions, final ordinary labels and private zero endpoints
are checked for both concrete cases:

| Changed tetrads | Cut ADDs before/after | Extra ADDs | Extra sign scales | Extra scalar operations | Recursive histogram delta |
|---|---|---:|---:|---:|---|
| 3 | 176 / 181 | 167 | 18 | 185 | zero |
| 14 | 176 / 214 | 794 | 84 | 878 | zero |

These totals include both basis directions, expanded swaps and every changed
cut coefficient. They are an invoice for this word, not scalar optimality.
No extra helper, private stream or recursive call is introduced.
**There is no new κ or recursive saving.** Rounded execution, intermediate
magnitude bounds and unchanged precision admission remain unproved.

See [PROOF.md](PROOF.md) for reachability, the complete restoration argument
and the exact covered domain. This is a finite certificate plus a written
operator proof, not a formal-kernel or full multiplication theorem.

## Source and audit boundary

Canonical base: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Audited pending [PR #3604](https://github.com/CrocSwap/integer-mult-bounds/pull/3604)
head: `9a56309846c262238de04138d14d8bc32ec83d77`.
Its consumer verifier is byte-identical to the initially reviewed
`30968c83f160011b5f435380746f0e57e64517d0`. The current README's input-side
correction and square-completion discussion do not change its reversed
canonical-prefix and `B`-projection operands. This is a source-specific
correction, not an exclusion of all changed decoder producers.

The later head `7156bb98f78b7492002010e8729d59fe38b92e60` adds a separate
abstract co-delivery screen and leaves these audited literal consumer bytes
unchanged. That screen is outside this correction's conclusions.

[SCATTER-SOURCES.json](SCATTER-SOURCES.json) binds original Git blobs, SHA256
hashes, and the selected archive members. The six pending source/credit files
are retained unchanged under `vendor/`, with their Apache-2.0 license.
Only the integer basis definitions and the literal port map are reused from
those files. Their original checkers are not run or endorsed here. The live
main geometry supplies root/frame definitions, not a rerun of its full screen.

The pending originals were read with `GIT_NO_REPLACE_OBJECTS=1`. They are
authenticated by their complete bytes and original Git-blob formula at replay;
they are not hidden runtime dependencies on unmerged Git commits. The generic
source-history gate binds the task/selected record and two live inputs to the
base ancestry. The standalone replay requires neither Git nor network access.

The selected canonical archive is a declared live input, not duplicated here.
Its unchanged Clifford recipes are reused. The fresh checks are the changed
scalar word, frames, endpoints and independent cut parser; they do not
reexecute the unchanged native compiler. The all-vector boundary argument is
explicitly distinct from such a compiler replay.

## Reproduce

From a checkout containing the package and its two declared inputs:

```sh
python3.12 scripts/research_package.py --package research/p112-scatter-orientation --check-only
python3.12 scripts/research_package.py --package research/p112-scatter-orientation
```

For a Git-free source export, or an explicit optimized-parent check:

```sh
python3.12 -I -O -B research/p112-scatter-orientation/verify.py --out /tmp/p112-scatter-fresh
```

The output directory must be fresh; omit `--out` for temporary output.
Expected status: `PASS_P112_SCATTER_ORIENTATION_NO_NEW_KAPPA`.
Python 3.12, standard library only; one registered command has a 600-second cap.
The parent uses fail-closed checks under optimization. Its unoptimized child
interpreters use private bytecode namespaces; geometry/basis definitions are
compiled directly from authenticated source bytes. Sources are rechecked after
execution. Generated receipts do not replace the fresh computation.

Controls reject a reversed opcode event, the wrong scatter coefficient,
omission of the dirty-basis entrance in each full word, and the hybrid scatter
in each full word. The latter four preserve the frame labels and recursive
bill while failing endpoint coefficients. An independently written parser
checks all 176 native/canonical bindings without importing the producer.

## Open next questions

- Supply a changed producer with correctly oriented readout/scatter and complete
  dirty restoration, then derive its full recursive bill. A matrix kernel alone
  does not identify a paid operation that disappears.
- If a favorable complete bill justifies expansion, derive the new word's
  magnitude, rounding, storage, whole-call hosting and all-size transfer bounds.
  This exact arithmetic sandwich has not received those admissions.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Credit

Prepared by Ross Richardson with substantial OpenAI Codex assistance, including
separate AI-agent review of the proof and a separately implemented cut parser.
No independent human review is claimed. Gonzalo Mier's P112 consumer, tetrad
basis and port-map work retain the attribution in the vendored source READMEs.
The P112 geometry, selected gauge44 construction and native-lift authors retain
the attribution in their source packages and the selected-source record.
New work is Apache-2.0. Frozen predecessors and the selected record are unchanged.
