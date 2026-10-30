# Checked SAT proofs for four seven-source B cases

This package independently excludes the four simple22 pattern-B templates
listed in `RESULT.json`. It supplies a new Boolean translation and a replay
that generates and checks an UNSAT proof for each case. It does not give a
new value of f(7), a complete independent B exclusion, or a new kappa.

The predecessor already excludes all 77 B cases with its native engine.
Its source-bound `TASK.json` reports an additional Z3 check with three UNSAT
results and 74 timeouts, without identifying those cases. We therefore mark
the prior SMT status of **each named case as unknown**. We do not claim a
newly resolved named case. The contribution is independent, checked proof
evidence for these four inherited native exclusions. The other 73 B cases
were not run with this encoding in this contribution.

## What is independent

`model.py` imports no predecessor solver or verification code. It enumerates
all 112 ordered simple Q3 paths, retaining even the six pairs that the native
engine identifies by a common signature. It generates the 77 low templates
by position subsets and the explicit rotation, reversal and permutation group.
A separate test compiles the unchanged native source and confirms its template
IDs match these independently generated words.

The CNF uses exact path selections, endpoint joins, coordinate totals and the
actual occupied vertices of F2^7. Every nonzero difference must occur between
two occupied vertices. It uses its own Boolean cardinality encoding. It does
not use the native gap enumeration, capacity tests, domain propagation or
branching. [PROOF.md](PROOF.md) proves the translation equivalence.

PySAT 1.8.dev24 runs CaDiCaL 1.9.5 in a fresh subprocess for each case.
A solver return alone is insufficient: the separately pinned DRAT-trim source
must accept the binary proof against the freshly generated DIMACS file.
`RESULT.json` binds each exact low word and CNF hash. `OBSERVED.json` records
the actual local proof hashes and byte counts. Proof bytes may vary between
environments; every replay checks the fresh proof. Large CNFs and proofs are
disposable outputs, regenerated and removed after their checks. `--retain`
keeps the small raw solver and checker transcripts.

The proof reader flushes the native C trace before reading it. An early run
exposed a truncated buffered tail, which DRAT-trim rejected. A control now
checks native trace finalization and rejects an empty trace. This lifecycle
handling is exercised alongside an interrupted solver, whose result cannot
be admitted as an exclusion.

## Reproduce

Requires Python 3.12, `python-sat==1.8.dev24`, and installed C99 and C++17 compilers.
The tested platforms are POSIX; the proof trace uses libc `fflush` and the
pinned adapter's binary `prfile`. Use a new external output directory:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/my-connector-sat-replay"
mkdir -p "$RUN"
uv venv --python 3.12 "$RUN/venv"
uv pip install --python "$RUN/venv/bin/python" 'python-sat==1.8.dev24'
TMPDIR="$RUN" "$RUN/venv/bin/python" -I -Werror -B \
  research/connector-b-occupancy-sat/verify.py --controls --retain "$RUN/evidence"
TMPDIR="$RUN" "$RUN/venv/bin/python" -I -Werror -B \
  research/connector-b-occupancy-sat/test_model.py
TMPDIR="$RUN" "$RUN/venv/bin/python" -I -O -Werror -B \
  research/connector-b-occupancy-sat/test_model.py
TMPDIR="$RUN" "$RUN/venv/bin/python" -I -B scripts/research_package.py \
  --package research/connector-b-occupancy-sat
```

The generic `research_package.py` hook checks source and CNF bindings only,
and explicitly prints `no_UNSAT_replay`. PySAT is outside its supported dependency
set. Full proof acceptance uses the separate `REPLAY.json` environment and
[dedicated native workflow](../../.github/workflows/connector-b-occupancy-sat.yml),
which installs the pinned solver and runs the three scientific commands above.
The generic hook is not evidence of an UNSAT check.

The scientific replay prints `VERIFIED_B 1` through `VERIFIED_B 4`, then
`PASS_CONNECTOR_B_OCCUPANCY_SAT`. Its exact receipt has 25,969 variables in
each case, 278,978 clauses in B1 and 278,962 in B2, B3 and B4. An incomplete
solver, bad proof, process timeout, changed input or different CNF fails.
No proof hash is substituted for a proof check.

Thirteen semantic test groups include exhaustive small cardinality truth tables,
fixed and unfixed universal simple24 SAT controls, a noncover simple22 that is
SAT only without coverage, a repeated-prefix rejection, wrong counts, wrong
initial translation, invalid symmetry use, incomplete-solver rejection,
certificate truncation and the actual native template numbering. The checker
also receives valid, empty and forged proof controls. Normal and optimized
Python checks stay active. Hosted CI is separate from these local observations.

## Scope and credit

Scientific base is canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
The native subject has SHA256
`597844fc32cde19c1d4104633fa6d3eb0d28c1ca140f8f3d2ba2cb632ecd30d1`.
Exact input blobs and source hashes are in `SOURCES.json`; prior solver status
and its lookup limit are in `PRIOR-STATUS.json`.

Credit conorholds / PR3058 for the original covering-code construction, native
B exclusions and swapped-Gray fixtures; Krzysztof Wojt / PR3261 for the complete
representation audit; Nick Petalas / PR3276 and the caller audit for branching
and exhaustion obligations; commdata2338 and the retained capacity/propagation
lineage; Nicholas Stone, Aaron Wang, James Reed, Ross Richardson / PR943 and
Douglas Colkitt / PR1185 for the model, correction and predecessor bounds.
PySAT and CaDiCaL supply the proposal solver. Marijn Heule and the DRAT-trim
contributors supply the independent certificate checker, whose MIT source and
license are preserved under `vendor/`. New material by Nick Petalas is
Apache-2.0. Substantial automated assistance was used; there is no independent
human review or proof-assistant formalization of the translation.

This package does not audit the published coding/classification premises,
the 21-prefix reduction, all 77 B cases, a native multiplier, physical hosting,
restoration, precision, a supplier invoice or the selected cold replay.
It leaves every predecessor and the selected frontier unchanged.

## Engineering boundaries

Build the Lever produced the independent CNF generator and repeatable proof
replay. Prove It Works requires actual DRAT acceptance. Test Behavior, Not
Implementation led to literal word controls and incomplete-result rejection.
Separate Before Serializing Shared State kept the package and outputs in one
owned worktree/session, with shared Git writes under an advisory lock.

New loops have finite bounds: ten blocks, 112 ordered paths, eight origins,
77 templates, 128 vertices and 127 differences. The model enforces 60,000
variables and 500,000 clauses; the emitted DIMACS is at most 16 MiB and each
proof at most 256 MiB. Each solver subprocess has a 90-second limit and a
300,000-conflict budget; each proof checker has a 75-second process limit.
Python functions remain under 60 physical lines in normal formatting.

Power of Ten deviations concern managed allocation, the fixed local module
loader, the pinned adapter's binary trace, libc flush and the immutable native
solver/checker implementations. Their allocations and internal loops are not
reimplemented here; finite input capacities, isolated processes and the separate
proof check constrain their role. The imported C checker retains its upstream
compiler warnings, recorded by every build with `-Wall -Wextra -Wpedantic`.
New Python passes Ruff diagnostics without suppressions. Replacing the pinned
adapter or increasing the domains requires revisiting these limits and controls.

## Open next questions

Can the remaining 73 B cases receive equally independent checked proofs within
a bounded replay budget? Start with the same translation and one named template;
keep resource-limited results inconclusive. The blocker is the remaining solver
and proof-checking budget, not a new native pruning rule. This contribution
stops after its four certified cases and does not start another construction
round. A full independent B result would still leave the coding/classification
and earlier reduction obligations separate.
