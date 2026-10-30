# Exact validation boundary

The cell-controller, universal physical proof and algebraic Lean theorem are
three separate kinds of evidence. [CHECKS.json](CHECKS.json) and
[RESULT.json](RESULT.json) record their exact scope. A fresh kernel/axiom audit
of the algebraic identity does not certify the tape controller or its bill.

## Mandatory Python replay

Local direct replay passed with CPython 3.13.5 on Windows. The registered replay
also passed with actual CPython 3.12.10, including the metadata/pin check and
committed-receipt comparison. The launcher received inherited `PYTHONOPTIMIZE=1`;
its normal optimization-stripping policy remained active. Hosted CI was not run.
The isolated [official Windows portable runtime](https://www.python.org/downloads/release/python-31210/)
was extracted on F: and its local `_pth` file preserved under another name to
restore normal script imports; process-only PYTHONHOME selected that runtime.
No global Python installation, configuration, package install or registry change
was made. The public package contains no interpreter binaries. A separate regular-file,
Git-free export passed the direct verifier under Python 3.12.10 with explicit
`-O`, read-only source files and TMPDIR unset; every source byte was unchanged.
All validation uses explicit exceptions rather than Python `assert` statements.
The registered launcher authenticates metadata and source pins before executing.
Normal replay compares its finite mathematical results and code hashes with the
committed receipt; environment-version reporting is separate.

A fresh receipt was produced with:

```sh
python3 -W error -B research/qq16-tagged-cover-routing/verify.py --write NEW_EXTERNAL_RECEIPT.json
```

It passed 28 cases, 9,137,626 metered cell actions and five controls. This tests
actual forward unit moves and marker-driven returns; no full 73-axis cover is
allocated. The 512 literal 73-axis maps are instead checked as exact matrices,
with separate row and column representations and a separate read-count formula.
The full physical theorem is the informal argument in PROOF.md. In a separate
Git-free copy, flipping one byte of the input certificate was rejected by the
source hash guard before decompression, including under `-O`.

## Optional pinned Lean algebra

`lean/QQ16CoverRoute.lean` proves just the semidirect push/pull inverse. It uses
Lean 4.34.1, Mathlib commit `d13f23b723b8a846827a245b89c10fc7d3f11612`,
and the nine dependency revisions in `lean/lake-manifest.json`. Both the TOML
package name and manifest root are `qq16_cover_route`; default build selects
a Lean library, with no native executable. The public configurations were
byte-compared with the isolated project actually tested locally.

A fresh direct Lean subprocess compiled the unchanged source. A separate
subprocess imported its fresh artifact and collected the theorem's transitive
axioms: exactly `propext`, `Classical.choice`, `Quot.sound`; no `sorryAx` or
custom axiom. The actual optional project also passed `lake env lean --version`,
bare `lake build`, and `lake env lean Check.lean` against an existing exact-pin
cache. This was not a new network download/bootstrap. An initial direct attempt
timed out after 90 seconds during the cold run. A subsequent bounded run
compiled successfully; the successful compilation and checks are the evidence.

From the optional project's `lean` directory, with the pinned toolchain installed:

```sh
lake exe cache get Mathlib.Data.Matrix.Mul Mathlib.Data.ZMod.Basic Mathlib.Algebra.CharP.Two
lake build
lake env lean Check.lean
```

The last command must print only the three standard axioms named above for
`QQ16CoverRoute.semidirect_pull_push`. The standalone Python replay needs no
Lean installation or Mathlib download.

## Deliberately unrun obligations

No selected full cold replay was run because the selected construction and its
inputs were not changed. Hosted CI, an actual full owner-cover allocation/run,
a complete QQ16 caller/native replay, layout conversion, consumer/idle invoice,
all-size compilation and full multiplication were not checked or supplied.
The universal physical theorem is scoped to its explicit tagged-entry and
three-clean-buffer premises. No independent human review is claimed.

## Publication byte check

The current repository enforces LF. Before publication, the new oracle and JSON
receipt were aligned with those rules. The receipt's parsed proof-relevant fields
were unchanged; its raw container hash changed. Both the registered Python 3.12
replay and read-only Git-free `-O` replay then passed on the final code hashes.
The package manifest records raw LF publication bytes. The prepared Git patch is
checked independently by applying it to a fresh private index at the pinned base
and comparing every resulting Git blob with its source file, without a commit or
identity-setting change.

In RESULT.json, each map's `relabel_reads` is q, the coefficient-bit reads only.
Stream/fence/payload scans are charged separately in the universal bound.
