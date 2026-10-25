# The checker and exporter diverge on 3,492 gates

**Partial. No new exponent.**

On six registers, every source list of length at most 4 gives 9,330 gates.
The symbolic checker accumulates a pre-gate XOR and writes once. The exporter
applies one sequential add per source. They agree on all 4,686
destination-free gates and on 1,152 gates that contain the destination. They
diverge on the other 3,492.

The checker's nonempty distinct-operand guard accepts 1,230 gates, matching
`6 * (5 + 20 + 60 + 120)`. A simple-support guard admits 1,350 divergent
gates. The algebraic contract rejects none of the gates on which the two
operators agree.

## What was executed

The checker compares the two operators with the coefficient condition on this
domain and reads the pinned source lines. It does not scan the selected word.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the gate contract in PR 3738,
head `19fa53f4f10bde32e20e59f1d11e0c1d344f4386`.

## Scope and evidence

Original card: `supplier-boundary-audit`, priority revision 6, refined to
this domain. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the two operator
sources. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/gate-operand-agreement/verify.py
python3.12 -B research/gate-operand-agreement/test_verify.py
python3.12 -B scripts/research_package.py --package research/gate-operand-agreement
```

## Open next questions

This contract and these counts are the boundary. A longer source list would
leave them.

## Credit

petalas compared the checker and exporter operators.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
