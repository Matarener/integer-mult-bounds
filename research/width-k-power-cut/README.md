# The width floors differ on perfect 500th powers

**Partial. No new exponent.**

The matched-layer note sets `d = floor(p^(1/40))` and `g = d - 1`. Its old
layout uses `K = floor(d^(1/500))`. The actual-width plan uses
`K = floor(g^(1/500))`. For every integer `d >= 2`, those floors differ
exactly when `d` is a perfect 500th power.

The smallest such width is `d = 2^500`. Then the old floor is 2 and the
actual-width floor is 1, because

```text
1^500 <= 2^500 - 1 < 2^500
```

The next width, `2^500 + 1`, keeps both floors equal. The same locus holds
for exponent 3 on every width from 2 through 299.

Truncation, layout and host serialization stay unpriced, so this package
does not build the physical wrapper.

## What was executed

The checker proves the integer case split and evaluates the witness. It does
not run the matched-layer replay.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the handoff's K cut in
discussion 1166, recorded against PR 3623 head
`328c40966b650f60b1d62cfb0b1d67b2b755eb62`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
power cut. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/width-k-power-cut/verify.py
python3.12 -B research/width-k-power-cut/test_verify.py
python3.12 -B scripts/research_package.py --package research/width-k-power-cut
```

## Open next questions

This power cut is the interface fact. The physical wrapper would leave it
while the return oracles stay unpriced.

## Credit

Clear1nsight stated the cut in the matched-layer note, incorporating Sagar
Thakrar's diagonal pass. The actual-width plan is PR 3599's.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
