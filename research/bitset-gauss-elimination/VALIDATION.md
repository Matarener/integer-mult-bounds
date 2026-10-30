# Validation and limits

This contribution was produced by Nick Petalas. The claim is a scoped
implementation equivalence proof with finite conformance and empirical
performance evidence. It is not a new approximation theorem or supplier.

## Measured complete calculation

`benchmark.py --workload projection` launches five alternating baseline and
bitset processes, each with `-I -W error -B`. Each process authenticates the
same 20 predecessor files, generates all five circuits, constructs their
normalized Choi states, builds every kernel entry, solves the exact normal
equations, checks orthogonality and prints the complete solution. The timer
starts before process creation and stops after output capture and exit.
Fresh processes share the ordinary operating-system file cache. There is no
persistent mathematical result cache or omitted matrix entry.

The new bitset implementation and the original implementation each execute
25 Gauss calls, with maximum phase dimension 128. Every complete stdout has
SHA256 `9e9ca672563db4c1d3a281be16c2fdcd798ae96de4fd9cd8c2e9ca1ce624effa`.
All ten processes exit zero. The generated BENCHMARK.json binds the exact
implementation and harness source bytes and records every raw wall time.
The two ranges are disjoint. The measurement is host-specific; no timing
threshold is a correctness or CI gate.

Separate untimed cProfile runs locate the reason for the gain. In the
baseline projection, Gauss elimination takes 0.500 of 0.962 profiled seconds.
The replacement takes 0.027 of 0.490 profiled seconds. Choi construction
still takes about 0.216 seconds under the profiler, and the remaining kernel
also performs affine substitution and binary solving. The measured 40.6%
complete-command reduction is smaller than the baseline Gauss share. These
profile times are diagnostics, excluded from the ten timing samples.

Reproduce the diagnostic separately from the timing experiment:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -m cProfile -o /absolute/scratch/projection.prof research/bitset-gauss-elimination/run_projection.py --mode baseline
~/git/integer-mult-bounds/.venv/bin/python3.12 -B -m cProfile -o /absolute/scratch/bitset.prof research/bitset-gauss-elimination/run_projection.py --mode bitset
```

## Initial prediction and the full replay

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272124)
predicted a useful improvement of the complete PR5727 inventory replay.
That prediction did not survive measurement. In its separate profile,
Gauss elimination takes 1.027 of 29.240 profiled seconds. Literal state
execution dominates instead. Five alternating complete inventory pairs
return identical stdout and zero errors, but their wall-time ranges overlap.
No measurable gain is claimed for that replay.

The [public scope update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272372)
withdraws that prediction and narrows the performance claim to the fixed
large-width calculation. No further algorithm optimization followed the
first verified gain. The inherited inventory remains a conformance test.

## Correctness checks

The direct normal and optimized checkers pass:

- 67,732 quadratic sums, exhausting every admitted polynomial through four
  variables and every constant phase. The oracle literally sums Gaussian
  integer units over the Boolean cube.
- 64 additional literal sums in dimensions 5 through 12, and 40 complete-graph
  fixtures through dimension 256. The latter use an independent binomial
  sum by Hamming weight, including zero and destructive-cancellation cases.
- Ten invalid-input rejections and four explicit cancellation, odd-sign,
  pair-edge and constant-phase controls.
- Every one of 82,237 Gauss calls in the unchanged complete consumer replay,
  compared with the original implementation on that actual input. The full
  consumer still requires its entire committed RESULT.json.
- Every Gauss call in the complete large-width projection, compared with
  the original implementation, and the timed complete output digest.

Three disposable mutations also reject locally. A changed authenticated
source byte fails before replay. Reversing the odd-diagonal sign and omitting
the paired-neighborhood diagonal correction both fail the literal oracle.
The two registered commands took 11.16 and 11.25 seconds locally, below
their 120-second bounds. Registered normal and optimized replay passed.

These checks corroborate PROOF.md. Finite agreement is not a proof for every
polynomial. Predecessor results and counts are inherited consumer contracts;
their independent re-verification is not the deliverable.

## Implementation bounds

The kernel admits at most 256 variables and 32,897 polynomial entries.
It owns two arrays of at most 256 entries. Every loop in the kernel has a
bound derived from that dimension or dictionary size; at most n elimination
iterations occur. Real and imaginary output parts have at most 257 magnitude
bits. There is no recursion or dynamic code generation in the kernel.
Every new function is below sixty physical lines. Explicit exceptions keep
the scientific checks active under optimization.

Power-of-Ten rule 3 has a managed-runtime deviation. CPython allocates
integers, dictionaries and tuples during this bounded computation. The fixed
dimension, term count and coefficient domains bound the live mathematical
state. A fixed-capacity native arithmetic implementation would be necessary
for a strict no-allocation contract.

Rules 8 and 9 have a bounded replay-adapter deviation. The wrappers load one
fixed, hash-authenticated predecessor script with runpy and replace one
function by a local callback. Their only admitted targets are the original,
bitset and differential functions. They do not accept arbitrary code paths.
PINS.json is at most 64 KiB; at most 64 regular repository-local source files
of at most 1 MiB each may be authenticated. Every scientific subprocess has
a 120-second timeout and its exit code and work count are checked.

Warning-strict normal and optimized execution and AST/function-size inspection
are the local diagnostics. No external static analyzer, independent human
review or proof-kernel review is claimed. No Lean, Docker, selected scientific
cold replay, physical-machine execution or production-search timing is run.
