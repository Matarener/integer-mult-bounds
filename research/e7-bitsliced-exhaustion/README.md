# Exact E7 exhaustion in bit lanes

The complete E7 minimum-support classifier runs 17.53 times faster in the
recorded local comparison: median 13.816 seconds becomes 0.788 seconds.
All six fresh-process outputs are byte-identical. All 134,217,727 nonzero
codewords remain covered. Complete kappa is unchanged.

The [proof](PROOF.md) establishes the exact iterator for arbitrary independent
binary generators. [binary.py](binary.py) computes Hamming weights in parallel
integer bit lanes. [classify.py](classify.py) is the complete derived consumer.
Only its source-root path and minimum-support function differ from the frozen
verifier; the registered check compares every other syntax node.

[RESULT.json](RESULT.json) records all scientific checks.
[BENCHMARK.json](BENCHMARK.json) records alternating fresh-process timings on
Python 3.12.14, macOS arm64. [VALIDATION.md](VALIDATION.md) states the limits.
[SOURCES.json](SOURCES.json) binds all eleven retained input files.

## Reproduce

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/e7-bitsliced-exhaustion
```

Expected markers:

```text
PASS_E7_BITSLICED_EXHAUSTION
PASS_REGISTERED_RESEARCH_PACKAGE
```

The registered verifier covers all 1,381 independent unordered generator sets
in F2^4, all five weight bounds and five batch sizes: 34,525 comparisons.
It also checks 108 wide-code cases, sixteen domain and invalidation controls,
the full original classification result, and a second full E7 basis.
The full classification retains all reflection, frame, rational-rank,
ambient-pivot and corruption controls from the predecessor.

For a separate timing run, use an output path outside the package:

```sh
python3.12 -I -B research/e7-bitsliced-exhaustion/benchmark.py --output /tmp/e7-timings.json
```

The timing command alternates three complete old and three complete new
fresh-process replays on the same interpreter. It checks exact output equality.
Runtime ratios are local measurements, not a universal hardware guarantee or
a physical multiplication speedup. The iterator still exhausts an exponential
coefficient space. Its bounded bit-lane storage avoids a full word table.

## Credit and scope

[PR #5669](https://github.com/CrocSwap/integer-mult-bounds/pull/5669), exact head
700efb538a3d919409c9506d117846b7895b02ea, supplies the complete classification,
consumer and receipt. Its retained [PR #5238](https://github.com/CrocSwap/integer-mult-bounds/pull/5238)
source supplies Nick Petalas's frame-code geometry and minimum-support proof.
The complete predecessor notices and attribution remain unchanged in `source/`.
The new bit-lane implementation, proof and independent small-code oracle are
by Ali Romman with substantial OpenAI Codex assistance. No subagents.
Apache-2.0. The consumer uses the same assistant family as its predecessor;
no independent human or proof-kernel acceptance is claimed.

No new geometry bound, physical supplier, selected-frontier change or complete
kappa gain is inferred. The value is faster exact verification for the E7/E8
deletion and decoder work. No other consumer is silently changed.

## Open next questions

- Bind another actual deletion or decoder code to the iterator. Compare all
  old checks and outputs, then measure its full replay. No other installation
  or speed claim is included here.
