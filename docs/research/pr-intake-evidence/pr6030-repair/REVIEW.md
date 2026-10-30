# PR6030 portability repair and primary replay

Construction: DreamingOfClouds, original PR6030 head
`772dd10a5859a1d15f4851feb371519789213ad8`.
Repair: Douglas Colkitt with OpenAI Codex assistance, commit
`746ee5e1160ae64a15a81b2a432d5566142db850`.

## Scope

The original hosted Linux run [40597285594](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/40597285594)
failed on regenerated gzip-container equality. This repair compares the entire
decompressed payload byte for byte against the canonical serialization of the
regenerated word. Immutable base-word and archive authentication remains exact.
The source-delta receipt records the eleven unchanged original files, including
the word, edit, expected result, source archives and pricing. Four original files
change (constructor comparison, verifier comparison, manifest, README), and a
portability-control test is added. No shared production code changes.

Seven controls pass in normal and optimized Python: gzip header variants,
compression levels/timestamps/filenames, changed events/fields, boolean/integer
substitutions, extra payload, corrupt containers and immutable-input pins.
The controls are also registered in optimized mode in the package manifest.
Package metadata/pins and git diff whitespace checks pass.

## Full primary replay

The bounded macOS replay used Python 3.12.8, serial execution, a 600-second timeout
and a sampled descendant-RSS ceiling of 1 GiB. It passed in 228.42 seconds,
peak sampled RSS 572032 KiB; the command and log hash are in primary.json.
The retained watchdog is run_bounded.py. Paths in that receipt describe the
original scratch environment; no scratch paths are scientific dependencies.

The full verifier passes exact regeneration/storage, all 799 input columns and
separate transpose, signed native maps, absolute phases, adapters, complete
physical caller, both rational engines, completion, compiler and outer costs.
It reproduces conditional kappa 0.003125804 and raw crossing interval
(0.00312581155791, 0.00312581155792), with the committed expected result unchanged.

Hosted Ubuntu 24.04 / Python 3.12 run [40612825047](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/40612825047)
passed at the exact repaired source commit. Job 122569871206 passes all seven
optimized controls and the complete registered primary replay. The scientific
replay took about 313 seconds. Tracked-source preservation passed. Full run
metadata and the package-job log are retained in hosted-run.json and hosted.log.
The cross-platform execution gate is resolved.

## Acceptance boundary and credit

This is a portability repair with a maintainer execution of the author's complete
primary verifier. It is not an independently derived application proof, a Lean
verification, a discharge of the five inherited framework assumptions, or a
selected-frontier promotion. The selected result remains 0.00310045 (PR5599).
A promotion review must still independently assess the changed word, physical
caller/interface application and complete assembly with source-bound evidence.

DreamingOfClouds retains the PR6030 construction and PR5907 predecessor credit.
Ali Romman supplies the pinned PR5827 verifier lineage, with Mason Hale (PR5811),
Pierre-Loic Doulcet (PR5565), and all notices retained in the source archives.
Matarener's PR5960 independently reported the predecessor gzip issue.
Maxime Fleury's reproducibility work and Antoine Olivier's replay findings
underlie the repository's existing payload-comparison policy.
