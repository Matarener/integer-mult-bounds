# Exact packed dyadic transpose replay

The complete transpose-checkpoint command is **2.98 times faster** on the
retained selected P104 word, from median 0.5282 to 0.1770 seconds over five
alternating fresh-process pairs. Its exact checkpoint covers all 571,536
coefficients. This is an opt-in verifier-engineering result with a scoped
correctness proof, not a new kappa or an audit of the selected construction.

This contribution was produced by Nick Petalas. Apache-2.0.

## Method and evidence

[packed.py](packed.py) represents each dyadic row by one integer numerator
and a binary denominator exponent. A separate l1-bound pass chooses an
injective signed radix before the packed replay starts. Arithmetic then
updates whole rows using Python integers. [PROOF.md](PROOF.md) proves that
the final integer equalities are equivalent to every matrix coefficient
equality. This is deterministic exact arithmetic, without random probes,
modular fingerprints, machine-integer overflow or cached acceptance results.

The new backend preserves the complete scalar projection of ADD, COPY,
SCALE, INIT and CLEAR. The surrounding source checker remains responsible
for frames, ownership, erasure legality and native semantics. Every source
file stays unchanged, and the official selected reproduction command stays
unchanged. No backend is automatically installed into an existing verifier.

The direct check prints `PASS_PACKED_DYADIC_TRANSPOSE` in a generated
source-hash-bound JSON receipt. It checks:

- All 4,681 words of length zero through four over the stated eight-event
  alphabet, plus 160 deterministic forty-event words on one through eight
  roles. The independent chronological Fraction oracle compares all 22,804
  literal coefficients, including overwrite and denominator interactions.
- All 4,841 corresponding incorrect endpoints are rejected. Fourteen
  additional controls cover invalid domains, growth and memory limits,
  unsafe-radix collisions and an altered full-word endpoint.
- The retained 25,475-event word, with 22,028 non-MOVE events, has 756
  columns and 571,536 endpoint coefficients. Its planned radix width is
  111 bits. Its complete endpoint-check summary equals the unchanged dense
  checkpoint's summary.
- Both pinned inputs and the generated benchmark's code/input bindings
  match. Recorded timings are checked for internal consistency; routine
  correctness replay does not repeat the timing experiment.

The complete retained word is a workload, not a new supplier-verification
deliverable. Its predecessor endpoint, helper, native, caller, compiler and
exponent claims are credited to their existing authors.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/packed-dyadic-transpose/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/packed-dyadic-transpose/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/packed-dyadic-transpose
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/packed-dyadic-transpose --check-source-history
```

Substitute an equivalent CPython 3.12 path elsewhere. Sparse checkouts need
`research/packed-dyadic-transpose` and the two live inputs listed in
[VERIFY.json](VERIFY.json). Historical guidance and card pins in
[SOURCES.json](SOURCES.json) are provenance, not executable dependencies.

Run the optional complete timing experiment separately:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/packed-dyadic-transpose/benchmark.py
```

Its generated report is [BENCHMARK.json](BENCHMARK.json). Each subprocess
authenticates and parses the same source bytes, loads both implementations,
and executes one complete checkpoint. The inner timer includes the packed
syntax conversion, growth planning, replay and endpoint comparison. The
outer timer additionally includes process startup, imports, authentication,
decompression, parsing and result serialization. Each completed result is
consumed and compared, and all ten samples have zero errors.

## Measurement scope

The host is macOS arm64, CPython 3.12.15, with 18 logical CPUs. Other work
was running; the five dense/packed pairs execute sequentially and alternate
to share that noise. No sample is discarded. The published ranges are:

| Timed region | Dense median and range, seconds | Packed median and range, seconds |
| --- | --- | --- |
| Complete checkpoint command | 0.5282, 0.5242 to 0.5317 | 0.1770, 0.1657 to 0.1779 |
| Checkpoint function | 0.4840, 0.4791 to 0.4861 | 0.1301, 0.1229 to 0.1320 |

The checkpoint function is 3.72 times faster and accounts for about 92% of
the baseline checkpoint command. Median process peak RSS rises from
41,222,144 to 46,465,024 bytes. Separate untimed profiles identify the
baseline's columnwise parity scans and row arithmetic as its main cost.
The packed path spends its largest self time in bounded integer row steps;
syntax/Fraction conversion and the bound pass also remain payable.

These measurements concern one scalar endpoint checkpoint. They are not a
whole selected-replay speedup or a physical multiplication speedup. Ali
Romman's [PR5757](https://github.com/CrocSwap/integer-mult-bounds/pull/5757)
accelerates the complete selected replay's native quadratic states and
retains this original transpose checkpoint. Its different full-replay
timings are cited context and were not rerun here. No Linux timing claim
is made.

## Limits and credit

The implementation rejects more than 1,024 roles, 60,000 scalar events,
4,096 bits of planned numerator growth, or 128,000,000 packed coefficient
bits. These are explicit resource bounds, not a universal algorithmic
limitation. The managed-runtime allocation deviation is in PROOF.md.

Credit Ali Romman for the PR5599 helper-subspace word, dense reverse-column
checkpoint and PR5544/5545 implementation lineage; Pierre-Loic Doulcet for
the retained PR5565 source changes; David Arias for the scalar word; Cinna
Davis for private reuse; Gareth Davidson for composition; and all retained
P104/native/controller/compiler contributors. Classical Kronecker
substitution and elementary transpose algebra are not claimed as new
mathematics. Sagar Thakrar's
[PR1781](https://github.com/CrocSwap/integer-mult-bounds/pull/1781) already
uses packed exact integer matrices and the signed-radix argument for
Clifford recipes, following the retained Lean comparator. That method is
credited predecessor work. This package applies a new trace-dependent
dyadic bound planner to the scalar transpose checkpoint, including COPY
and zero-row operations. The new work is the bounded backend, correctness argument,
independent behavior checks and checkpoint measurements.

Independent human and formal proof-kernel review are unclaimed. No native
phase, physical caller, full supplier replay, rounded multiplier, stock,
compiler, tape or analytic obligation is discharged. Lean and Docker were
not run. The selected frontier is unchanged.

## Open next questions

Can this backend be installed at one complete successor replay's literal
transpose call site while retaining all surrounding controls? First bind
that call and compare the complete scientific output. This package supplies
no such integration or whole-replay measurement. That is the next question;
the first useful checkpoint improvement is shipped here without further
tuning.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228421)
records the original scope. The source base is canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priorities revision 8. The
autonomous-run playbook used an explicit first-improvement stop rule.
