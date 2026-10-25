# The checked saving is half the consumed saving

**Partial. No new exponent.**

The pinned certificate checks `complex.saving = 717/20000000` in the mutant,
while the assembly still consumes

```text
a_complex = 717/10000000 = 2 · 717/20000000
```

The mutant changes one count, from `[756, 516232080]` to `[756, 516232085]`.
The denominator stays `m = 784` and `W = 537696432`, and `0 < 756 < 784`.

For each ratio `m/r = 2^k y` with `1 ≤ y ≤ 2`, the checker lowers `log y` by
24 positive terms of its odd series, rounds that bound down on the `10^30`
grid, and lowers the exponential by the degree-4 Taylor polynomial. On the
mutant counts at the consumed saving, that lower bound is greater than
`1 + 4/10^10`.

## What was executed

The checker reads the pinned certificate and computes this bound. It does not
run the historical arithmetic checker. That checker's saved receipt already
rejects a mutated certificate; this package does not repeat that rejection.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the saving pair in PR 3646, head
`22dce8f7e3f12bc7f3d627784a81e45bee950ece`.

## Scope and evidence

Original card: `supplier-boundary-audit`, priority revision 6, refined to this
saving pair. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the climbed-48
certificate. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/supplier-saving-half/verify.py
python3.12 -B research/supplier-saving-half/test_verify.py
python3.12 -B scripts/research_package.py --package research/supplier-saving-half
```

## Open next questions

This gap and this lower bound are the audit. Running the historical checker
would leave them.

## Credit

roger-sato published the supplier-saving binding audit and the two rational
values.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
