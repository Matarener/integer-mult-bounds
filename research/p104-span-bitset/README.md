# Bitset incidence shortens the complete P104 B-form replay

The complete P104 span-fact command has a 67.09% lower local median wall time,
from 2.596 to 0.855 seconds. The scalar range is 2.437..2.918 seconds and the
bitset range is 0.832..0.873 seconds. Five alternating fresh-process pairs
produce identical normalized standard output and zero errors.

The enclosing bounded B-form verifier has an observed 8.79% lower median,
14.982 to 13.665 seconds. Its whole-caller wall-time comparison is inconclusive
because the ranges overlap and host variation exceeds the median difference.
All ten complete caller outputs still agree, with zero errors.
[BENCHMARK.json](BENCHMARK.json) contains every sample, environment details,
transcript hashes and implementation/input bindings.

Claim type: measured complete-span verifier improvement with a scoped implementation-equivalence
proof and exact finite conformance. No new mathematical bound or kappa is claimed.
This contribution is produced by Nick Petalas.

The profile locates the span command's dominant cost in repeated scalar label
parities. Integer incidence masks reuse those parities while retaining every
one of the 130,305 section pairs. The enclosing command retains the original
S1/S2' checks, biclique replay, singular-rank self-test, authenticated census logs,
result comparison, Lean-source scan and controls. The saved timing ranges are
14.120..16.949 seconds for the scalar caller and
13.123..14.272 seconds for the bitset caller.
All five paired complete-verifier samples favor the bitset implementation.
The complete ranges overlap; the exact descriptive rank-sum tail is 8/252
(two-sided p=0.031746). [STATISTICS.json](STATISTICS.json) binds that calculation
to the generated timing record. The whole-caller timing remains
inconclusive. The clear span-command improvement has no portable speed guarantee. The standalone span median equals 17.3% of the complete scalar median. The
end-to-end result is consistent with its available headroom. The remaining
singular-rank stage limits the gain. The machine had other work running;
alternating order and the recorded load averages make that limitation explicit.

[PROOF.md](PROOF.md) explains the incidence identity, the exact source adapter,
assertion preservation, resource bounds and deviations. Only the S0 count
computation changes. A raw prefix preserves an inherited literal docstring
escape while permitting warning-strict compilation. The original files remain
unchanged. All 105 live inputs are pinned. A stable checkout is required while
a command authenticates and reads its source files.

## Reproduce

From the repository root, with CPython 3.12 and numpy 2.5.4:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p104-span-bitset/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/p104-span-bitset/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-span-bitset
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-span-bitset --check-source-history --check-modes
```

Another CPython 3.12 path may replace the local path. The direct marker is
`PASS_P104_SPAN_BITSET`. Both registered commands are bounded by 180 seconds.
To execute only the faster complete consumer:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-span-bitset/replay.py --scope complete --engine bitset
```

To repeat the five alternating timing pairs for each command:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/p104-span-bitset/benchmark.py
```

The benchmark prints a generated JSON record; save new output outside the
checkout. It does not overwrite the published record. The conformance checker
validates that record's hashes, raw-sample medians/ranges, error counts and
transcripts. Its three record-corruption controls reject changed input bindings,
medians and transcript hashes.

## Evidence and limits

The literal scalar oracle checks 281 fixtures and 136,569 section pairs,
including every actual P104 section pair. Thirteen domain, section,
source-corruption and normalization controls plus three record controls remain
active under optimization. Complete scalar/bitset output comparisons execute
both the span command and its enclosing bounded verifier. Child commands run
without optimization, so the predecessor assertions remain enabled.

The performance percentage is a single-host measurement on CPython 3.12.15,
macOS arm64 with 18 logical CPUs and numpy 2.5.4. CI checks conformance and
record integrity; it does not certify this host's percentage. The predecessor
manifest pins a different numpy release. Both measured engines here use 2.5.4;
no cross-version speed comparison is made.

The enclosing bounded verifier authenticates recorded census logs. It does
not recompute the full historical census or build Lean. This package preserves
that coverage and does not claim independent acceptance of the predecessor
mathematics. Full census, Lean, selected-supplier cold replay, native/caller
admission and the complete multiplication theorem remain unrun. Independent
human and formal proof-kernel review are unclaimed. The selected frontier is
unchanged. Hosted CI is pending at publication.

## Related open work

- PR6218 supplies hand/Lean root and span facts and a different B-form reduction. This package accelerates the retained PR6188 bounded command; it does not re-check or replace PR6218's proof or compatible-plane work.
- PR6198 proves E8 span inputs over odd-characteristic fields. Its span predicates and theorem are distinct; no common numerical result is compared.
- PR6217 and PR6219 study P104 wire routing and disjoint A2 packing. They share the root geometry but do not implement this span-count substitution or measure this replay.

## Open next questions

Can the same incidence representation help another explicit finite-fact
consumer? First profile a different complete command and specify its full
output and checks. No other consumer is measured or adapted here. Further
optimization of the other B-form replay stages is left unclaimed.

## Credit

Matarener retains PR6188's mathematical facts, root model, finite domains,
original verifier, recorded evidence and attribution. DreamingOfClouds retains
the underlying nine-term decoder/geometry code and its credited predecessor
lineage. The incidence implementation, source adapter, implementation-equivalence
argument and measurements are produced by Nick Petalas. Bitset intersection
and population count are standard methods; no literature-priority claim is made.
Apache-2.0. Frozen evidence and predecessor credit lines are unchanged.
