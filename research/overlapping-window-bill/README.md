# Six chained windows cost 70 scalar gates

**Partial. No new exponent.**

The six write windows are `[0,1]` through `[5,6]`. The earliest-right-endpoint
rule selects three disjoint windows, so the hitting number is 3. Restoring
the connector takes an even number of source calls, which is

`2 * ceil(3/2) = 4`.

The same six windows placed on disjoint slots have hitting number 6 and use
six source calls. Closing every window by itself uses twelve.

The source matrix has weights `2 + 2 + 3 = 7`. The six output matrices
alternate weights 3 and 4. Two output calls and the source calls therefore
cost

`2 * (3+4+3+4+3+4) + 4 * 7 = 70`

scalar XOR gates. The disjoint schedule costs 84 and the separately closed
schedule costs 126. The overlap saves exactly two source calls, which is
fourteen gates. All three schedules deliver every output and restore the
connector. The data width is 24 bits. The head travel is 1456, 1572 and 1920
steps.

A weighted pair of windows with slot prices `1, 9, 1` costs 6 by calling the
two cheap slots once each. Calling the shared slot and one cheap close costs
14. The selected kappa is unchanged.

## What was executed

The checker builds these three schedules and counts their gates. It does not
rerun the 5336-case census.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the overlapping-window bill in
PR 3778, head `cc841651682e076fa8d4f2cec9b2055a8c91c5b1`.

## Scope and evidence

Original card: `connector-alphabet-change`, priority revision 6, refined to
this bill. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/overlapping-window-bill/verify.py
python3.12 -B research/overlapping-window-bill/test_verify.py
python3.12 -B scripts/research_package.py --package research/overlapping-window-bill
```

## Open next questions

This bill is the uniform chain. A physical caller would leave it.

## Credit

Yuzhou Wang recorded this six-window bill. The dirty-connector lineage is
credited there to Ross Richardson and woklerx.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
