# Complete G20 replay with low compression

This package reduces the measured cost of the complete PR5708 replay.
Default gzip level 1 gives a local median of 17.8863 seconds, compared with
22.2141 seconds for the unchanged source: **1.242x**. The source receipt,
all twelve scientific output comparisons and every rejection check remain.
This is a verification cost result. It gives no new kappa or supplier admission.

## Source and change

The source is [PR5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708)
at 829d01fc031f7323ffcfa423fdfd1f24dcbe3190. All 102 tree entries equal the
archived package on base de5ec2e7a6074068452f45b1a191b5c72832df4a.
[SOURCE-AUDIT.json](SOURCE-AUDIT.json) records this comparison.
[SOURCES.json](SOURCES.json) binds every retained file. All live inputs also
appear in [VERIFY.json](VERIFY.json).

The profile identified maximum gzip compression as a large replay cost:
6.942 seconds of 14.283 profiled seconds in the global producer. These times
include profiler cost. See [PROFILE.json](PROFILE.json).

The two files in producers/ are explicit source variants. A complete text
comparison permits only one import and one compression keyword in each file.
The arithmetic, event generation, duplicate stream encoding, prefix hashes,
native checks and all other statements must equal the pinned source.
The replay copies authenticated inputs to a temporary directory, installs these
two variants and writes the selected integer level to a local options module.
It then runs the **unchanged source verify.py**. No module is monkeypatched.
The retained source and published compressed outputs stay unchanged.

Default level 1 is a measured time/space choice. The --level option accepts 0
through 9. Each mode must pass the full source verifier. A level changes only
the temporary gzip containers. It does not change a source hash or a payload
comparison. Level 0 stores uncompressed data inside gzip containers.

## Full replay evidence

The source verifier rebuilds all four stages and compares all twelve outputs.
It compares exact GLOBAL JSONL bytes. It compares the other decoded JSON
values and omits only the source's existing CPU_seconds field. It retains:

- All 3484 cancellations and 45 conjugations, including the two productive steps.
- All 685 forward and adjoint columns at moduli 101 and 10201, and the complete
  common-frame helper split search in the source's declared domain.
- All 317004 global events, 11022 independent inputs, 48 dirty fields,
  2529 owned episodes and 56223 chronological query descriptors.
- The full target debit, paid bill, two moment engines, finite fees,
  compiler margins and five ordinary backend levels.
- The source's wrong-conjugation, wrong-rank, stale-epoch, lost-target-debit
  and pricing rejection controls.

The added binding check rejects six producer mutations: a changed check
function, a changed level binding and an extra exit statement in each file.
The source receipt hash is
`a92d0889565baa30c9307c4e8160f88e0e65500ce6d241dcf90f8d8867878ea8`.
All twelve timed processes returned this receipt. The source verifier also
checks that its temporary source copy and frozen inputs did not change.
The outer wrapper checks the 102 retained source hashes before and after replay.

## Measured tradeoff

[BENCHMARK.json](BENCHMARK.json) contains twelve fresh serial processes:
three unchanged-source runs and three runs at each of levels 1, 2 and 0.
The order alternates. The complete wrapper cost is included for each new mode.
The operating-system cache was warm. No profiler ran during this benchmark.

| Mode | Median complete seconds | Total bytes in three temporary gzip files |
| --- | ---: | ---: |
| Unchanged source, level 9 | 22.2141 | 7004565 |
| Level 1, default | 17.8863 | 9577889 |
| Level 2 | 22.0032 | 9234726 |
| Level 0 | 25.7129 | 132034590 |

The individual times vary. Source runs range from 20.17 to 36.92 seconds;
level 1 runs range from 15.02 to 25.74 seconds. Each of the three matched
source/level 1 blocks improves, by 1.24x to 1.43x. These observations do not
establish a speed guarantee on another host or a global optimum over levels.
Level 0 was fastest in the last block but slowest by the overall median.
Level 1 avoids its large temporary files.

[CODEC-BENCHMARK.json](CODEC-BENCHMARK.json) separately checks the three
exact payloads at levels 0, 1, 2, 3, 6 and 9, with three samples per level.
The sum of median compression-plus-decompression times is 9.7232 seconds
at level 9 and 0.7536 seconds at level 1. These codec times exclude the rest
of the proof replay; they are not the complete speedup.

## Reproduction

Use Python3.12 and its standard library. Run the registered check:

```sh
python3.12 -B scripts/research_package.py --package research/g20-compression-replay
```

Direct isolated and optimized replay:

```sh
python3.12 -I -O -B -W error research/g20-compression-replay/verify.py
```

Optional serial performance audit:

```sh
python3.12 -I -B research/g20-compression-replay/benchmark.py --output /tmp/g20-times.json
python3.12 -I -B research/g20-compression-replay/codec_benchmark.py --output /tmp/g20-codec-times.json
```

The benchmark is separate from registered correctness checks. Source corruption,
normal replay, and a sealed optimized export with an empty PATH are checked
before publication. [VALIDATION.json](VALIDATION.json) records the exact tested
commit and export hash. The export needs no Git, network access or writable sources.

## Scope and limitations

This is an opt-in replay of one frozen component. It does not replace the
original registered command. The source's conditional ordinary value remains
.003507719059749. No selected frontier file changes. The retained native,
compiler, stock, precision, tape and recovery premises still apply.
The enormous all-size program is not executed. This is not independent human
review. Full publication ancestry verification is unavailable in this shallow
checkout; exact source blobs and sealed replay do not prove that property.
Hosted scientific success is not claimed by the local evidence.

The current priority is 8. The portable-replay card's scope changed to measured
replay cost after the exact payload audit. The initial CI proposal was released
because PR5749 overlapped. See the canonical
[Discussion5790](https://github.com/CrocSwap/integer-mult-bounds/discussions/5790).

## Credit

Ali Romman prepared this optimization with substantial OpenAI Codex assistance.
No subagents were used. The two producer variants retain their exact notices.
Credit Dugongue for the source refinements and late bindings, ai-nanachi for
PR5512, the PR5679/5708 contributors, and all native, controller, helper,
ordinary and stock authors named in the retained source. The source package
contains all predecessor notices. Python and zlib supply the codecs.
Apache-2.0.

## Open next questions

- Does the time/space choice hold on hosted Linux Python3.12? Run the same
  twelve-process audit and retain all receipts before making that claim.
- Can new producers accept a replay compression setting from the start?
  Check one new package and keep its publication compression separate.
