# Validation record

Environment: CPython 3.12.10 (64-bit), Windows 11 build 26100.
Scientific base: 721c03822c421b7f7fcbb2598993b947c4d88419.
All commands below run sequentially; there are no concurrent scientific replays.

## Completed scientific checks

The package's registered driver completed successfully:

```sh
python -X utf8 -B scripts/research_package.py --package research/chain-cyclic-schedules
```

It ran full isolated normal and optimized replay, then the private-copy
mutation audit. Both full replays returned the same mathematical object
in EXPECTED.json. Eleven actual mutations were rejected in each mode, with
two passing unchanged probes. The parity-gate mutation is detected by the
separate literal orbit counter, not only by the retained expected table.

The initial generated replay took 13.125 seconds; the existence-classification replay took 13.672 seconds. This is one local timing,
not a benchmark against #6037 or a speedup claim. Evidence domains and
exact counts are in README.md and EXPECTED.json.

The metadata/source-pin check passed. Source bytes were read from their exact
Git objects and frozen unchanged. Six frozen source files are checked on every
scientific replay, including the predecessor table and retained license.

The card orientation check also passed:

```text
PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182
```

It is orientation only; neither that baseline nor the source W table is
presented as an independent proof of the new formulas.

## Known shared-check boundary

The unmodified canonical base fails two of the six tests in
test_research_current_status.py: current CI navigation is still for #5599,
and a current-status bold-decimal expectation does not match the fraction
format. The same failures were reproduced in this branch; none of the
affected files is changed here. The separate open
[PR #6050](https://github.com/CrocSwap/integer-mult-bounds/pull/6050),
head 41ac3a47b91b4184e6c54af417bf576bfb429926, repairs these shared docs.
A failed hosted plan must not be reported as a failed period theorem.

The selected-record verifier was attempted but could not run in this sparse
checkout because its 1,405-file selected inventory is not fully materialized.
The optional inventory materialization probe was stopped. No selected-record
verification or selected-supplier cold replay is claimed. The selected
record, its inventory and all supplier files are unchanged in this patch.

## Scope of confidence

The written proof is not checked by a formal kernel or an independent human.
The position enumerator, chronological DP and formulas have different
implementations but were written by the same assisted author. Literal
counting is exhaustive only through m=5; independent DP stops at m=8.
Numerical tables through m=24 above that range inherit the frozen #6037 counts.
No physical hosting, precision, routing, compiler or outer-bound claim is
tested or changed here.

## Source transport

The pending #6037 bytes are retained unchanged in publication ancestor
ccff0fb7ed8f53a686a3f2ecc2a5585d7bd8a505. All executable source pins now
resolve to the canonical base or this publication ancestor; original upstream
head/path/blob fields are retained separately. The optional full-history
preflight refuses this shallow checkout, so no full-history preflight pass
is claimed. Committed-byte and independent export checks are used separately.

The final registered replay after the existence classification took 52.812
seconds total. Normal and optimized result/file-hash receipts were identical;
22 mutated probes failed and two unchanged probes passed. The package file
inventory and all hashes were unchanged before and after the run.

Direct Git ancestry queries return success for both the canonical base and
retained-source ancestor. This narrower check is not presented as a pass of
the full-history preflight.

The first read-only export passed both mathematical replays, then exposed a
Windows permission issue in the mutation harness: copying read-only file
attributes prevented edits to its private copies. The harness now copies
file contents without those attributes and makes only temporary directories
writable. The original exported sources remain read-only. The same eleven
mutations still have to fail semantically, rather than on a permission error.

## Successful independent export replay

Publication snapshot `a2d0504b3937c9513dc13787cfee56a4f983ef1f` passed the
committed-byte preflight for all 19 package files and the official export
integrity/input-coverage check. Export SHA-256:
`6c58fbc92d36ff143e560060495f2dea20127dded845473eebc230ac34207826`.

That exact archive was extracted outside the repository. Every exported file
was marked read-only, and PATH contained only the Python installation, with
no Git executable. Normal replay passed in 14.360 s, optimized replay in
12.859 s, and all eleven mutation variants in both modes in 21.109 s. All
20 exported files (19 package files plus the export manifest) and their
hashes were unchanged after the three commands. The read-only-copy repair
is therefore verified on the Windows environment reported above.

Only this validation note was added after that successful snapshot; the
proof, programs, source pins, expected table and registered commands are
identical. The final publication commit receives its own byte preflight.
