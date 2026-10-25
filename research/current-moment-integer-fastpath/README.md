# Exact integer fast path for the selected moment engine

**Tooling result; no new κ.** An opt-in adapter returns the same exact rational
intervals as the selected #5413 caller's 72-term-log / 40-term-exp engine.
It removes intermediate Fraction reductions from the exponential sum. The
Taylor degree, positive remainder, range reduction, negative reciprocal,
10^65 grid, and every outward-rounded squaring stay identical. See [PROOF.md](PROOF.md).

On Windows / CPython 3.12.2, three alternating fresh-process pairs give median
**4.1874 s → 0.2770 s (15.12×)** for 24 actual invoice ranks × 12 distinct
exponents, complete paid/productive moments and strict homogeneous allowances.
All six mathematical receipts have SHA256
`fd2027763821b8623d579c37a7826a686d2725c0fdd18c193e59a64e481a98fd`.
[Final samples](benchmark-final-windows.json) and [earlier samples](benchmark-windows.json)
are retained. Timings exclude source loading/imports but include cold logarithm
and power caches. They measure this pricing workload, not a full caller replay.
The earlier instrumented 288-power profile took 4.538 s, with 3.345 s in gcd;
it motivated this change but is not used for the speedup ratio.

## Reproduce and use

Python 3.12 standard library only, from repository root:

```sh
python3.12 -B scripts/research_package.py --package research/current-moment-integer-fastpath
python3.12 -B research/current-moment-integer-fastpath/benchmark.py --pairs 3 --output /tmp/fresh-moment-benchmark.json
```

The benchmark refuses an existing output path. Each sample uses a fresh subprocess
and fresh caches; a differing receipt aborts the timing comparison. No unstable
wall-time threshold is a CI acceptance condition.

For exploratory pricing, put this directory on the Python import path and call
`from fast_moments import load_engine; engine = load_engine()`.
Use its unchanged `moment`, `minus`, `power` and `homogeneous_limit` interfaces.
`load_engine(False)` loads the authenticated reference. Both inputs are local
snapshots with SHA256 rejection before evaluation; no cached mathematical result
or external checkout is needed. Installing into arbitrary engines is unsupported.

The verifier compares the complete workload, all 600 exponential invocation/result
records, 121 boundary/seeded rational arguments, exact unrounded polynomial and
remainder parts, and 35 signed/zero-exponent rank cases. It checks the selected
positive lower point and rejected raw ceiling. Executed degree, tail and inward
rounding mutations, source/fixture tampering, an omitted charge and an invalid
rank are detected. The same explicit checks run under normal and optimized Python.

The frozen source and invoice provenance are in [SOURCES.json](SOURCES.json).
`inputs/invoice.json` is exactly the `histograms` object extracted from the pinned
invoice receipt. The unchanged source is copied byte for byte. The grid and source
hash are fixed deliberately: a new source version needs a new review, not a silent
cache reuse. The source's other acceptance logic remains compiled with assertions
enabled. Native identity, target independence, physical admission, full compiler,
precision and outer-theorem checks are outside this adapter. No full-caller,
whole-repository, Lean, or independent-human verification is claimed.

## Overlap and credit

Chris R / Clear1nsight supplies the exact arithmetic and #5413 completion.
Dillon, Ali Romman, Cao Yifan, Dugongue, Cinna Davis, zxv and the retained lineage
supply the selected construction. Their existing notices are preserved.

This is an adaptation of a classical integer Taylor recurrence, not a new
mathematical method. Related exact-output integer kernels already occur in
[PR672](https://github.com/CrocSwap/integer-mult-bounds/pull/672) (a different,
degree-16 / 200-bit engine; its full owner check saved only 2–3%) and
[PR2552](https://github.com/CrocSwap/integer-mult-bounds/pull/2552).
This package targets the currently selected 72/40 engine and its actual invoice,
without editing a frozen predecessor or substituting one engine's truncation
parameters for another's. Live title/body overlap searches are partial coverage,
not a novelty proof. New material: Joseph Anglada with substantial OpenAI Codex
assistance, Apache-2.0; no independent human or proof-kernel review.

## Open next questions

- How much does this save in a complete caller replay? First build a source-bound
  adapter that substitutes only this arithmetic and compare complete receipts in
  matched fresh processes. Native validation and other replay costs may dominate;
  a separate full replay budget and adapter review are needed.
- Can a changed physical word earn a better κ? First supply a literal changed word
  and complete paid/target invoice, then use this kernel for exact screening.
  Operator identity, independent targets, restoration, ordinary work, precision and
  compiler/outer funding remain the gates. Faster pricing alone changes no κ.
