# Two words realize the central triple

**Partial. No new exponent.**

The group `UT_3(F_4)` has order 64 under

`(a, b, c)(a', b', c') = (a+a', b+b', c+c'+a b')`.

The four labels `X_1`, `X_w`, `Y_1` and `Y_w` are involutions. Their
commutators are the central values `Z_1`, `Z_w` and `Z_{w^2}`, and
`Z_1 Z_w = Z_{w^2}`.

The diagonal word applies four calls on each of three registers:

`X_1 Y_1 X_1 Y_1`, `X_1 Y_w X_1 Y_w`, and `X_w Y_w X_w Y_w`.

That is 12 calls, six of X type and six of Y type. On every group element
it sends the three registers to `Z_1`, `Z_w` and `Z_{w^2}`. A fourth register
that the word does not touch stays fixed.

The earlier schedule uses the same four calls for `Z_1`, four calls
`X_w Y_1 X_w Y_1` for `Z_w`, and the six-call composite
`X_1 X_w Y_1 X_1 X_w Y_1` for `Z_{w^2}`. That word has 14 calls and realizes
the same three outputs. In the 6-by-6 nilpotent picture, a product is nonzero
only when an X block follows a Y block. The selected kappa is unchanged.

## What was executed

The checker multiplies both words on all 64 group elements. It does not
search shorter words.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the twelve-call word in
PR 3774, head `713c28c1b0ebbdf3f30d7887fcb173e7a786f245`.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to
these two words. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/twelve-call-central-triple/verify.py
python3.12 -B research/twelve-call-central-triple/test_verify.py
python3.12 -B scripts/research_package.py --package research/twelve-call-central-triple
```

## Open next questions

These words attain the diagonal. A shorter word would leave them.

## Credit

Wentao Li recorded these two words. The two-register minimum and the
fourteen-call composite are credited there to Cinna Davis.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
