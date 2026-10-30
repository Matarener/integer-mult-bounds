# Integer replay and canonical formatting: source-only feasibility handoff

Status: **SOURCE_ONLY_READY_FOR_PARENT_SERIAL_FEASIBILITY; no compilation,
execution, qualification, timing, complete speedup, or kappa claim.**

This worker owns only `integer-format/` and this report. It read the project
AGENTS instructions, current working plan, opportunity record, saved complete
profile, literal integer/reference source and frozen PR5864 boundary code.
It did not modify any synced source, frozen package, Fraction oracle, feed,
automation, mathematical research, Git state, or browser state. One initial
static read used the wrong filename `source/precision.py`; the actual source
is `source/reference_precision.py`. That failed read caused no execution.

## Source pins and scope

- Frozen complete PR5864: head `3f15c943e4ad6479f03e674c80fff1269a16ccfe`.
- Literal integer source:
  `outputs/c-native-opportunities-20261027/source/integer.py`;
  SHA256 `82a73e4bcf1835bfdd510c7ad5538625c1b380c559b671e6a67be490615a743a`.
- New C source:
  `integer-format/integer_format.c`;
  SHA256 `804cc25bd9ad0912de81fe97bc65b95ebcb0dec06453739e1d4863e7946c4f3d`.
- `finite_probe.py` SHA256
  `1b804c882833e2628d843bade00dfcbb282e0f53f6712e2d978af9b5c1ce8378`.
- `native_loader.py` SHA256
  `2592bef50e5338ad562d9a69bca1183ef0d88a4d34bdc497af4452304dca25c3`.
- `integer_binding.py` SHA256
  `dd3e4387dfb8882a524d938d866ed7ae04cd5ac938bbbcbec4eefd15f4bdcc9d`.
- `micro_probe.py` SHA256
  `f1d39f830987fcabe8ca5453ddbb1eca1df10a9670a95db510efbe5f21dd76aa`.

This is a derivative of Ali Romman's integer replay, with substantial OpenAI
Codex assistance, under Apache-2.0. The new feasibility source credits Chris R /
Clear1nsight and OpenAI Codex assistance. Preserve the full predecessor NOTICE,
including PR5848/5839/5816/5818/5832/5761 lineage and existing native cache
attribution. It is not a novel arithmetic algorithm or an independent human
review. No code was copied from CPython's integer implementation.

## Headroom and bounded decision

The profile is an instrumented complete PR5864 replay. Its recorded 91.703902
seconds inside the profiling scope is diagnostic, not the unprofiled complete
32.771297-second published median. The following are individual observations;
these cumulative figures must not be summed with their nested helpers:

| Function | Calls | Self seconds | Cumulative seconds |
| --- | ---: | ---: | ---: |
| integer `error_trace` | 121 | 3.576433853 | 8.431311677 |
| integer `reverse_all` | 121 | 0.483597588 | 3.187265222 |
| integer `ideal` | 4 | 0.400506658 | 2.622130628 |
| integer `multiply` | 3,357,683 | 1.185891057 | 1.419735399 |
| integer `add_row` | 56,819 | 0.390191792 | 0.833139426 |
| integer `update_hash` | 775,218 | 1.092006952 | 2.669192520 |

There is enough repeated Python traversal and formatting to justify one bounded
finite/micro feasibility test. There is **not** presently a defensible claim that
this route alone can save the approximately five complete seconds needed for a
further 15% improvement over PR5864. Cumulative regions retain setup, Fraction
boundary construction, sorting, hashing, outer Python control and output work.
The prototype also pays full exact-type validation, row copies, returned tuple
allocations, list conversions, and a second cold native build. Instrumentation
may disproportionately inflate the Python calls being removed. Do not convert
profile shares or the synthetic batch into promised whole-run savings.

The integer/format route is a candidate for one bounded test, not an admitted
complete construction. Stop if finite correctness fails. If the fixed micro
comparison is unhelpful after its full allocation/copy costs, do not expand to a
full candidate. If it is helpful, the parent's declared complete-cost/noise rule
must decide whether one fresh full pair is justified. Preserve all attempts and
failures. No automatic retry or benchmark selection. A successful incremental
saving below 15% would remain below this round's user-requested complete target.

The parent owns the single runner, 180 seconds per command, 1 GiB sampled
process-group RSS, 600 seconds initial feasibility and 1,500 seconds shared
round budget. This worker used none of that scientific execution slot.

## Native API and semantics

All coefficient arithmetic uses public Python number APIs on **exact built-in
arbitrary-size int** objects. No coefficient, numerator, denominator or score is
converted to a fixed-width C arithmetic type. `Py_ssize_t` is used only for
container length/indexing, which is already bounded by Python sequence storage.
The test source includes 8,192-bit values, exceeding both 64 and 4,096 bits.

| API | Return | Use |
| --- | --- | --- |
| `add_row(dst, src, numerator, exponent)` | fresh dict | Ideal/reverse sparse row update |
| `error_row(dst, src, numerator, exponent, scores, weights)` | `(fresh dict, three-score tuple)` | Signed forward sparse update and score changes |
| `scale_row(row, numerator, exponent)` | fresh dict | Exact dyadic scaling |
| `coefficient_bytes(row, scale)` | bytes | Complete descending-event coefficient hash input |
| `coefficient_item_bytes(event, value, scale)` | bytes | One signed coefficient hash chunk |
| `score_bytes(event, scores, units)` | bytes | Exact three-value score stream |
| `reverse_updates(column, scores, wa, wc, event, scale)` | list of `(index, score tuple, bytes)` | Reverse contributions in source insertion order |

The row/scoring methods return fresh objects and leave every supplied object
unchanged even when a later source entry fails exact division. This handles
`dst is src`, aliased score rows, and shared input integer objects without
mutation. No claimed optimization depends on undocumented alias exclusions.
A cost is the destination copy and validation on every call; those costs are
part of the candidate, not omitted setup.

Exact built-in dict/list/tuple/int guards reject bool, integer subclasses,
container subclasses and other foreign objects before their user methods can
run. Only accessed weight/score rows are validated; validating the whole
25,984-entry weight table on every sparse update would create an avoidable
quadratic bill. The source/destination sparse rows are fully validated. The
public typed setup/word guards remain in literal integer.py.

A row multiplication computes an arbitrary-size product and exact `divmod` by
`2**exponent`; any nonzero remainder raises `ValueError('exact dyadic division')`.
Negative values retain Python's exact signed arithmetic. Negative exponents are
rejected. Scale-row retains zero entries, matching the original comprehension;
sparse addition deletes zero sums, matching the original loop. No fixed-width
narrowing or silent signed overflow is present in the design.

For a nonzero signed integer `v`, `v & -v` is the positive power-of-two factor
in `v`. The factor common to `v` and a checked positive power-of-two `scale` is
the smaller of that value and `scale`. Dividing both by this factor creates the
same normalized pair as `Fraction(v, scale)`. Zero is explicitly `0/1`.

The two byte contracts are deliberately distinct:

- Coefficients always encode `event:numerator/denominator;`, including `/1`.
  Final row bytes include **every entry**, sorted by descending event exactly
  as the original hash loop. Combining those chunks into one bytes argument
  preserves the ordered digest input.
- Scores encode `event:a,b,c;` using Fraction string conventions, omitting `/1`
  for integers. Negative signs, zero and separators are unchanged.

All decimal conversion goes through Python integer string conversion; its
configured decimal-digit guard is neither disabled nor bypassed. The reverse
batch returns signed coefficient bytes in column dict insertion order. The
outer reverse event loop remains unchanged, preserving per-hash event order.
No digest, peak, score, witness, or PASS result is cached between invocations.

## Fresh candidate binder and independence

`integer_binding.derive(path, native, expected_integer_sha256)` authenticates
one original integer source, checks exact replacement counts, and constructs a
fresh candidate module in memory. It changes only sparse row/scale loops,
forward row+score loop, integer score/coefficient serialization, and the reverse
contribution loop. It preserves the original public Engine signatures, all
setup/word guards, weights, peak updates, strict comparisons, final-role tie
breaking, Pareto ordering, witness construction and Fraction output objects.
It does not patch the original file, an existing module, or a Fraction oracle.
The old `multiply`, `dyadic` and `scaled` rejection contracts remain intact.

The frozen PR5864 `full.py` receipt explicitly emits
`integer_oracle_unchanged=True`; its NOTICE also says the independent exact
integer engine is unchanged. Those claims **must not** be carried forward as
true for this candidate. The new package must say integer backend changed and
show complete comparison against the unchanged PR5864 Fraction route. The
existing Fraction route already uses native bookkeeping/cache machinery, but
its literal built-in Fraction numerical operations stay unchanged in this
integer-only arm. Its source arithmetic must not be replaced by this helper.

Combining this integer arm with a new native rational arithmetic arm changes
both formerly cross-checking numerical paths. That requires a separately fresh
literal Fraction audit and its full paid cost; two changed C paths cannot be
called an untouched oracle. Do not silently amortize/share candidate answers,
carry over PASS receipts, or share any new arithmetic helper with the literal
oracle. A combined arm may fail headroom once that independence bill is paid.
This report supports the integer-only arm with preserved PR5864 Fraction
numerical arithmetic, not an unpriced combined admission.

Original 120-program differential, reverse/literal equality, all actual events
and coordinates, ideal/weight/error outputs, full signed witnesses and hashes,
all adopted predecessor/native controls, custody controls and Observation
contracts still need to run in the **complete** candidate. The new small probe
is additional coverage, not a replacement or a qualification receipt reuse.

## Ready commands and integration

All files are under:
`/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/c-verification-all-opportunities-20261027/integer-format/`.
The following are proposed commands for the parent's guarded serial runner;
this worker did not run them:

```sh
python3 finite_probe.py --source-sha256 804cc25bd9ad0912de81fe97bc65b95ebcb0dec06453739e1d4863e7946c4f3d
python3 micro_probe.py --mode baseline
python3 micro_probe.py --mode candidate --source-sha256 804cc25bd9ad0912de81fe97bc65b95ebcb0dec06453739e1d4863e7946c4f3d
```

The loader pins source bytes supplied by the parent, builds a read-only snapshot
using the existing compiler with `-O2 -shared -fPIC -std=c11 -Wall -Werror`, checks
empty compiler output, checks original source remained unchanged, and loads the
fresh extension in a temporary directory. It caches only the code module within
one process. Compiler children CPU must be charged by the parent's outer runner.

The finite source covers eight signed row/score differential cases, scale rows,
six ordered prefixes including all complete bytes, 8,192-bit values, alias
safety and ownership, reverse scores/signed bytes, distinct coefficient/score
formatting contracts, and 21 explicit rejection paths. It uses explicit raises,
so checks remain present under `python -O`. That is planned coverage; no PASS
has been observed by this worker.

`micro_probe.py` performs one fixed 1,024-step synthetic row+score+format batch
per process. Baseline and candidate regenerate their inputs independently.
The result digest covers complete final rows, scores and the full byte stream.
The candidate additionally pays cold build/load and finite checks before the
batch timing. The inner timing describes only the synthetic batch; compare
outer guarded process costs separately. Root controls order and repetitions;
there is no script retry or best-sample selection. This synthetic batch does
not represent an actual-word distribution and supplies no complete saving.

Suggested integration in the parent's authenticated candidate loader:

```python
native = native_loader.load(FROZEN_C_SHA256)
integer_candidate, binding_receipt = integer_binding.derive(
    authenticated_integer_path, native, FROZEN_INTEGER_SHA256)
engine = integer_candidate.Engine(unchanged_fraction_reference)
```

The parent must adapt only the candidate integer selection seam and rerun the
complete existing contract. Retain raw outputs, ordered comparisons, failed
attempts, source/binder/cold-build receipts, all memory/cost bills, and exact
changed-oracle declarations. The parent may reject this source-only candidate
without constructing or publishing a complete optimization.
