# The ten-term factorization meets COPY cost 72

**Partial. No new exponent.**

The checker rebuilds the 120 A8 root lines and binds them to the standard E8
representatives. From the dual pair with normals `(1, 1, 0, 0, 0, 0, 0, 0)`
and `(1, 0, 1, 0, 0, 0, 0, 0)`, it builds the published two-sided extension.
That factorization has ten terms. Neither side has a zero factor or two
proportional factors. Both factor ranks are 9. The COPY cost, read as the
binary rank of the label pairing on each term, is 72. The sum of the ten
products equals the root Gram divided by 18. The stated bound
`9 * (10 - 1 - 1)` is also 72, so this example meets it with equality. The
selected kappa is unchanged.

## What was executed

The checker rebuilds this factorization. It does not exhaust the 130,305
character pairs and it does not replay the Lean files.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the ten-term equality example in
PR 3755, head `9ab51a1a90da57a55d1ef75f20ecd4b2705b3f52`.

## Scope and evidence

Original card: `complex-rank-shape-decoder`, priority revision 6, refined to
this factorization. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/ten-term-copy-cost/verify.py
python3.12 -B research/ten-term-copy-cost/test_verify.py
python3.12 -B scripts/research_package.py --package research/ten-term-copy-cost
```

## Open next questions

This factorization is the equality example. A character-pair census would leave it.

## Credit

conorholds published the ten-term decoder.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
