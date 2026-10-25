# Two complete fixed-source BIT price gates

This package closes two price questions without another discovery search.
For the fixed PR589 word, adding fresh commuting axes to any nonempty helper
set loses for every positive axis count and every tariff r^(1-C), 0<C<1.
For the retained paired-k3 p12 source in the balanced query-thinned caller,
the raw saving is below 0.002 for every positive integer controller parameter.
These are separate fixed-source scopes. Neither improves complete kappa.

Read [the proofs](PROOF.md), [exact result](RESULT.json), and
[source pins](SOURCES.json). The publication base is
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. All ten live inputs are pinned at
that base. The original investigation used the same source bytes at
`1ec1119972c9aefe42525172d07b332fcff81cb4`. The task catalogue and selected
record are historical provenance; no frozen source or selected result changes.

## Fixed helper-axis gate

The actual PR589 source has 439 rank-eight helper jobs. Each helper has an
own-register paid MOVE, and all such MOVEs have rank at most seven. A helper
that acquires k fresh axes must change at least k axis statuses along its
own paid path. Different helpers use distinct paths. Concavity and
subadditivity of the rank increments make their paid cost larger than the
rank-eight target increments they could fund. Partial axis sets are allowed. The result
holds in either orientation of the fixed word.

This fixes the source events, scalar contacts, free maps on the new axes,
and all other target credits. It does not cover a changed source word,
preloaded axes, another output contract, or a different native operation.
The former mincut results are not needed and are not rerun.

## Paired-triple gate

The source geometry parameter stays at 12: h=24, v=1760, R=19788, and centre
debt 528. The retained scalar decoder and rank compiler run on the frozen
module and matching. Both main boundary legs and all productive helper
credits are included. The caller parameter p is separate from this fixed
geometry parameter.

Exact rational calculations show negative complete margin at C=1/500 for
p=1,...,64. A decreasing concave upper bound is already negative with
negative derivative at 64, so it closes the entire remaining tail. A separate
normalized-margin argument proves that each raw crossing is below 1/500.
The retained p=11 bracket (0.00164539220,0.00164539221) is only a positive
control; this package makes no global optimum claim.

The rank compiler and its documented modular-rank argument are inherited.
No new native lift, partial-gauge optimization, source-size search, caller
construction, or ordinary supplier admission is supplied. The former floating
root search is not rerun.

## Separate source-rank appendix

For the pinned PR589 noCOPY matrix J, the minimum of rank(J+P) over every
permutation matrix P is exactly nine. The identity attains nine. The exact
511-word defect code has minimum weight 48; a hypothetical rank-eight repair
would let P move at most 34 rows, too few to remove a nonzero codeword.
This is a binary correction-rank theorem. It is not a native-cost bound.

The [retained arbitrary-invertible completion](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/kappa-rebuild/bit/pr589_minimum_completion.py)
uses a rank-three row repair and need not end in a permutation, so it is
outside this appendix. [PR #673](https://github.com/CrocSwap/integer-mult-bounds/pull/673)
prices dirty echo and restored role sharing, while
[PR #1246](https://github.com/CrocSwap/integer-mult-bounds/pull/1246) implements
paid nonzero reader-defect repair. Neither is the fixed J-to-permutation
rank problem here. They are related contracts, not executable dependencies.

## Reproduce

Use Python 3.12 and the standard library. All executable source dependencies
and their data files are declared in VERIFY.json.

```sh
python3 -B research/bit-fixed-source-price-gates/verify.py
python3 -O -B research/bit-fixed-source-price-gates/verify.py
python3 -B scripts/research_package.py --package research/bit-fixed-source-price-gates --check-only
python3 -B scripts/research_package.py --package research/bit-fixed-source-price-gates
```

Expected direct output:

```text
PASS_BIT_FIXED_SOURCE_PRICE_GATES helper_axis=all_k_C paired_k3=all_controller_p source_controls=10 new_kappa=false
```

The direct verifier also works in the committed export without Git. It checks
all ten source pins before it loads retained code. Normal and optimized runs
must give identical exact reports. Five controls reject invalid source-rank,
paid-path, target-credit, paid-charge and tail-gap assumptions. Mutating each
live source is also rejected. Two appendix controls reject a changed
decoder row and a zero-rank defect. No mincut, matching or root search runs.

No native payload, complete cover, ordinary precision/movement budget,
uniform compiler, or outer multiplication assembly is checked here. The
predecessor's standalone independent `check_paired_cube_bit.py` is not rerun;
the second gate prices the exact retained generator invoice.

## Open next questions

[TASK.json](TASK.json) records two distinct questions. A changed literal
helper path could escape the first proof's fixed-word charge. A changed
paired-cube recipe or caller could change the second complete invoice. In
either case, first provide a concrete word and every target debit. Neither
changed construction is supplied by this package.

## Credit and nearby contracts

The first source is the retained
[PR #589](https://github.com/CrocSwap/integer-mult-bounds/pull/589) and
[PR #555](https://github.com/CrocSwap/integer-mult-bounds/pull/555) word. Its
[pinned source notice](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/e8-bit-p111-tuned/NOTICE.md)
credits eumemic with substantial Anthropic Claude assistance and lists its
earlier contributors.

The second source is the retained fast paired-cube generator. Its
[SOURCE.json](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/paired-cube-bit-fast/SOURCE.json)
pins the [PR #168](https://github.com/CrocSwap/integer-mult-bounds/pull/168)
lineage and frozen p12 data. Its frame and gauge ledger retains
[PR #144](https://github.com/CrocSwap/integer-mult-bounds/pull/144) credit.
The [exact series engine](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/bit-compact-productive-controller/exact_series.py)
comes from ai-nanachi's compact productive BIT package. Cinna Davis's query-thinned
controller lineage is credited in that package's
[README](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/bit-compact-productive-controller/README.md).
Concavity and the decreasing-derivative test are standard analysis; this
contribution applies them to the complete pinned source invoices.

Nearby work has different contracts.
[PR #1931](https://github.com/CrocSwap/integer-mult-bounds/pull/1931) changes the
source with an involutive E8 reflection and boundary repairs; it does not fix
the source word and add commuting helper axes.
[PR #1998](https://github.com/CrocSwap/integer-mult-bounds/pull/1998) decodes
ordered paired dirty logs with specified intermediate observations; it is not
the paired-triple geometry or its complete invoice.
[PR #2376](https://github.com/CrocSwap/integer-mult-bounds/pull/2376) maps QQ16
observation contracts and does not prove either price gate. These are scope
comparisons, not executable dependencies.

The source-bound proofs, checks, and packaging have substantial OpenAI Codex
assistance. New files are Apache-2.0. Retained authors, notices and source files
remain unchanged. This is author-side evidence, not independent human review.
