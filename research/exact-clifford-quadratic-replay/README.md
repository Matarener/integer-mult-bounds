# Exact Clifford replay with polynomial state storage

The complete PR5698 replay runs in **11.15 seconds instead of 57.62 seconds** in
three alternating fresh-process rounds on this host: **5.17x faster**. The prior
PR662 table accelerator takes 17.59 seconds on the same fixture, so the new
engine is **1.58x faster** than that baseline. Every run returns the same complete
scientific result. This changes verification time only; **no new kappa is claimed**.

The engine represents the exact state by independent binary support columns,
a quadratic phase over Z/4 and an exact Gaussian-dyadic scalar. It keeps at
most n support variables after each gate. It preserves absolute phase and every
zero/nonzero amplitude without constructing a 2^n-entry vector. The all-width
induction and conservative polynomial resource bound are in [PROOF.md](PROOF.md).
The method is classical stabilizer simulation, with repository-specific exact
implementation, source integration and measured evidence.

## Replay

Python 3.12 and the standard library suffice. Run from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/exact-clifford-quadratic-replay
```

Expected markers are `PASS_EXACT_CLIFFORD_QUADRATIC_REPLAY`,
`PASS_ALL_ACTUAL_NATIVE_STATES` and `PASS_REGISTERED_RESEARCH_PACKAGE`.
Registered commands run the new proof checks normally and with `-O`, plus the
complete actual-state cross-check. Direct commands use absolute source paths
and also work in a read-only Git-free export. They do not regenerate evidence.

For the faster complete source replay alone:

```sh
python3.12 -I -W error -B research/exact-clifford-quadratic-replay/run.py
```

This checks the complete source RESULT, with SHA256
`a501b899b5f70e7cde6a10af4e4c2530cf9f4cb6ba53504828bf855ed3b74093` for its canonical
JSON. `--engine literal` runs the original frozen verifier. `--engine tables`
uses the credited PR662 evaluator through the explicit integration. No class
or source module is patched at runtime.

## Evidence and complete coverage

The consumer is [PR5698](https://github.com/CrocSwap/integer-mult-bounds/pull/5698),
head 024e43cdd1b942059c87446a76235c3f0b681c34. Its full source proof is retained:
all chronological records and independent inputs in both orientations, 4268
oriented native maps, 24 distinct helper normalizers, all 408 helper debits,
query caps, paid histograms, exact cut certificates, power/tail bounds and all
11 old rejection controls. [BINDING.json](BINDING.json) and binding.py bind the
entire derived proof to the frozen source syntax, allowing only the explicit
state-evaluator and path changes. Omitted grade or tail checks reject.

[RESULT.json](RESULT.json) records 7322 literal state comparisons and 618544
amplitude entries across widths 0 through 9, with all basis inputs through width 4.
Both the original evaluator and the prior table evaluator agree with the new
certificates. The checks also include 2728 affine,18724 product and 6096 phase
substitution assignments, 160 exact inverse checks, 13 malformed-input controls,
five semantic controls and two omitted-proof controls. Full-support width 16,32
and 64 examples pass exact inverse and absolute-phase checks. The width 64 state
has 2^64 nonzero amplitudes,64 support columns and 2048 phase terms.

[CROSS.json](CROSS.json) gives a separate direct literal-vector comparison for
all 8634 state evaluations and 4420608 amplitude entries in the complete native replay, including its
absolute-phase rejection control. It checks every vector entry and denominator,
then compares the complete scientific receipt. This does not depend only on
matching the final pass marker.

Thirty-five source files are byte-exact and authenticated before source import.
INPUTS.json and SOURCES.json give their commits, Git objects and SHA256 hashes.
The new code uses explicit checks under optimized Python. The existing source
construction, coefficients, cuts, profiles and scientific RESULT are unchanged.

## Measurement

[BENCHMARK.json](BENCHMARK.json) contains all nine fresh-process timings,
environment details, orders and identical output hashes. The medians are:

| Complete replay engine | Seconds | Relative to quadratic |
| --- | ---: | ---: |
| Original literal vectors | 57.624 | 5.17 |
| Charles Bethin PR662 tables | 17.591 | 1.58 |
| New quadratic states | 11.149 | 1.00 |

The observed ranges are 50.95–73.75,13.67–21.11 and 10.96–15.88 seconds,
respectively. Host load varies. Operating-system caches are not flushed. The
benchmark includes imports, frozen-source admission, all unchanged source checks
and complete result equality. It excludes the additional independent engine
suite and literal cross-check. It does not measure full-frontier verification,
physical native execution or integer multiplication.

To repeat it, use a fresh output path:

```sh
python3.12 -I -W error -B research/exact-clifford-quadratic-replay/benchmark.py --rounds 3 --output /tmp/fresh-clifford-benchmark.json
```

## Limits and next questions

The exact state proof covers every valid finite circuit in the stated grammar.
Operator equality also requires valid constructor-derived full Pauli tableaus;
no arbitrary supplied tableau is trusted. The code makes no claim to optimal
stabilizer complexity. The measurements are from one macOS arm64 host and
Python 3.12.14. Hosted CI, independent human review and proof-kernel acceptance
are separate. Full-history ancestry preflight is unavailable in the shallow
checkout; exact current source pins and committed bytes are checked.

The actual Gaussian construction keeps its local deficit 1680. A compatible
funded caller, uniform native/ROW implementation, complete machine fees,
precision, storage, routes and compiler thresholds remain open. Selected
conditional kappa .00310045 and priority revision 7 are unchanged on canonical
base df0137efd35e11b4445734bf612bdd4c7ebc330c.

## Open next questions

- Use the explicit engine in one additional named source replay after binding
  its gate grammar, full tableau checks and source receipt. Retain all failures
  and measure the complete consumer on the same inputs.
- Use polynomial phase verification to test a wider native construction only
  after its physical interface and full paid bill are specified. Faster checking
  does not provide those missing costs or admit a new supplier.

Credit Charles Bethin PR662, Ali Romman PR5698, Dugongue PR5687, the retained
Clifford compiler and native/frame/ROW/controller lineage, BigCactusLabs PR702,
Joshua Snider's quadratic-wrapper certificate, and classical stabilizer methods.
See [NOTICE.md](NOTICE.md) and the proof for exact boundaries and references.
New implementation and verification: Ali Romman with substantial OpenAI Codex
assistance; no subagents. Apache-2.0. No global literature-priority claim.
