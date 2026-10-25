# Verification scope and engineering decisions

The mathematical result is the unbounded serialization proof in PROOF.md.
The finite checks are corroboration and implementation checks. They do not
infer an arbitrary-size theorem from the observed counts.

## Exact checks

The registered replay runs these commands with CPython 3.12.15:

```sh
python3 -I -O -Werror -B research/independent-connector-serialization/verify.py
python3 -I -O -Werror -B research/independent-connector-serialization/independent.py
python3 -I -O -Werror -B research/independent-connector-serialization/test_package.py
```

The primary and separate full-matrix engine agree on all
`sum_(l=0)^8 4^l = 87,381` words, including exactly 8,909 valid source-only
endpoints and every serialized accepted word. Complete target/length histograms
and a digest of the entire accepted inventory agree. The accepted counts are
1 at length zero, 4 at length two, 40 at length four, 544 at length six and
8,320 at length eight. Zero-output endpoints and redundant calls are included.

The dense oracle checks 15,699 forward/inverse pairs. This includes every dirty
basis column and one mixed dirty state at widths 1,2,3 for all 37 main fixtures
before and after serialization, the credited coupled word, and the port-price
and observer controls. Width-two source maps explicitly fail commutativity;
projection maps are singular. The full expected source/root/output state is
checked in each case. Two implementations by the same contributor are not
independent human review.

Sixteen rational price fixtures independently expose all sixteen credited
one-root frontier profiles. The general lower tariff uses PR2063's retained
one-root theorem together with the new serialization theorem. The historical
945-pairing lower-bound census is not rerun or claimed as new coverage here.
The card's `universal-connector-boundary/verify.py` positive control and the
selected source-binding baseline passed before sparse narrowing. Neither is
an admitted supplier replay.

Four behavioral groups exercise the actual optimized CLI, invalid independent
dirt cancellation, immediate root identification, sixteen malformed/oversize
inputs, and an accepted boundary with eight sources, sixteen roots, 255 outputs
and 4,096 events. An actual producer mutant replaces per-root buckets by one
bucket and is rejected. Corrupted live source bytes and a counterfeit Boolean
receipt count fail. The Git-free export runs the primary and independent
checkers from an unrelated directory and verifies that no export file changes.
Default replays write no scientific artifacts. The test export is created under
an external TMPDIR and removed on exit.

Ruff 0.17.1 checks use `E4,E7,E9,F,I,B,UP,SIM,RUF`, target Python 3.12, plus
`ruff format --check`. Python runs with warnings as errors and bytecode disabled.
No runtime performance, full selected cold replay, Lean, Docker, physical
realization, hosting/precision/tape admission or hosted CI pass is claimed.

## Principle decisions

Build the Lever produced the reusable serializer and deterministic checkers.
Prove It Works required complete inventory agreement, literal dirty-column
execution and an actual faulty producer. Boundary Discipline kept strict JSON
parsing and resource limits at the CLI; the internal word is a typed record.
The serializer validates the mathematical endpoint premise before applying
the reduction and checks the resulting endpoint and counts afterward.

Power of Ten inspection found no application recursion. Every traversal is
bounded by the fixed scientific domains, the one-MiB input cap, at most eight
source rows in the source manifest or the executable program limits. The
scientific loops stream 87,381 words, retain one word at a time and accumulate
small histograms/digests. The largest dense fixture has forty data rows and
width three. Every application function stays at or below sixty physical lines.
Subprocess calls have 120-second limits and check their returned exit status.
Validation uses explicit exceptions and remains active under `-O`.

Managed Python allocation is a Rule 3 deviation. Static allocation would require
a different implementation/runtime. Each decoded input is capped at one MiB,
the program has at most 4,096 events and 279 public rows, and fixture source
bytes are pinned and bounded. No growing work queue or concurrent replay is
used. A future substantially larger domain must set a new memory budget before
expansion. Standard-library JSON recursion is confined to bounded decoding;
deep malformed input is rejected, including under optimized execution.

The frozen dataclass is a Rule 8 deviation for Python's standard record-method
generation. Its four declared fields have no custom method generation, dynamic
registration or callbacks; scientific control flow is ordinary direct calls.
A runtime that forbids this standard mechanism can replace the record with an
explicit fixed-field class without changing the proof or JSON contract.

The single `E402` suppression permits a fixed sibling import after adding the
package's own directory for isolated Python execution. The import target is
constant and tested in the Git-free export. No other lint diagnostic is muted.
Rule 10's repository-wide recurring static-analysis configuration is outside
this scoped new package. Its registered mathematical replay remains standard
library only; pinned Ruff is run before publication without changing shared
CI policy. A future repository-wide lint environment can add this exact check
without changing scientific evidence.

Private temporary exports and tool caches belong to the session output root.
Cleanup uses lstat and unlink/rmdir, never follows symlinks or changes shared
interpreter permissions. No predecessor source, selected record or frozen
archive is modified.
