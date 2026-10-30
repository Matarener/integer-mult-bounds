# Destination-free gates agree

**Partial. No new exponent.**

Both operators start from a valuation and write only the destination. The
symbolic operator reads every source from the original valuation, XORs those
bits, and XORs the result into the destination. The sequential operator XORs
the current value of each source into the destination, in order.

If the destination is not a source, every sequential read still sees the
original bit. On independent bits `1 << i`, five lists agree and leave every
other register untouched:

```text
(), (1), (1, 1), (1, 2, 1), (2, 3, 2, 3)
```

with destination 0. Repeats are allowed. The agreement does not depend on the
parity of a multiplicity.

If the destination occurs, the sequential operator can re-read its own write.
For sources `(0, 0)` the symbolic XOR cancels and the sequential operator
clears the bit, so an original one becomes zero. For sources `(1, 0)` the
symbolic result is bit 1 and the sequential result is zero. Both lists repeat
a register, which is the checker's distinctness rejection. The exporter does
not apply that rejection.

## What was executed

The checker compares the two operators on independent bits. It does not census
gates.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the gate identity in PR 3696, head
`0581402f978addb2eda5306fd124001486c76b08`.

## Scope and evidence

Original card: `supplier-boundary-audit`, priority revision 6, refined to this
identity. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/gate-dest-free-agreement/verify.py
python3.12 -B research/gate-dest-free-agreement/test_verify.py
python3.12 -B scripts/research_package.py --package research/gate-dest-free-agreement
```

## Open next questions

This identity is the comparison. A gate census would leave it.

## Credit

VictorLiwentao published the destination-free agreement and the two divergent lists.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
