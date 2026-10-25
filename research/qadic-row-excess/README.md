# One q-adic level exceeds the row cap

**Partial. No new exponent.**

The closure proof fixes an odd prime `q > 2^80` and the level shape
`log_q K < 4096 w + 1 <= 4097 w`. Here `4096 = 64^2` and `4097 = 64^2 + 1`.
For every integer `q >= 3`,

`|GL_64(q)| = q^{4096} * product_{i=1}^{64} (1 - q^{-i})`,

At `q = 3` that product exceeds `1/2`, and each factor increases for every
larger integer base. Thus `|GL_64(q)| > q^{4096} / 2`. When `q > 2^80` the order is greater than
`2^{327679}`, so its bit length is at least `64^2 * 80 = 327680`.

The parent note charges the outer row allowance `2 * (64^2 + 1) = 8194`.
The same depth 2, times one level of 327680 bits, is 655360. The frozen
assembler caps the external row coefficient at 20161. The q-adic term is
larger. The selected kappa is unchanged.

## What was executed

The checker evaluates this bound. It does not recompute the fourteen stage
headrooms and it does not enumerate `GL_64`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the q-adic comparison in PR 3667,
head `ad7c0e10e5476136498b377a3a28b80640e55c08`.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to this
level. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the closure proof, the parent note and the
frozen assembler. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/qadic-row-excess/verify.py
python3.12 -B research/qadic-row-excess/test_verify.py
python3.12 -B scripts/research_package.py --package research/qadic-row-excess
```

## Open next questions

This excess is the comparison. A stage-headroom replay would leave it.

## Credit

Mainzu compared this q-adic level with the row cap.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
