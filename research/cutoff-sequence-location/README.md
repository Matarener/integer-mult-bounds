# The two cutoff sequences are the two witness calls

**Partial. No new exponent.**

The frozen assembler computes its bootstrap cutoffs inside `outer_witness`.
That function is defined once and called at lines 221 and 226, once for the
conservative complex lower and once for the native complex lower. `cuts.append`
appears once. Across the 57 retained Python members, `cuts.append` and
`cutoff_log2` together appear twice.

With `beta = 10^-24`, both `(1 - beta) * complex_lower` and
`(1 - beta) * conservative_complex_lower` are strictly below the bit lower.
The assembler's minimum is therefore the discounted complex lower on both
branches.

## What was executed

The checker reads the frozen member and the two recorded lowers. It does not
recompute the fourteen stages.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the location in PR 3742, head
`89f6af270c550dd02bdb05d7a69987159aa110f2`.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to
this location. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the assembly receipt,
and the frozen archive. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/cutoff-sequence-location/verify.py
python3.12 -B research/cutoff-sequence-location/test_verify.py
python3.12 -B scripts/research_package.py --package research/cutoff-sequence-location
```

## Open next questions

This location is the two call sites. Recomputing the fourteen stages would
leave them.

## Credit

petalas located the two sequences in the frozen assembler.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
