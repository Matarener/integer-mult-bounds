# The five-cell floor depends on the basis

**Partial. No new exponent.**

Three private lines and one block of dimension 4 give `n_1 = 3` and
`n_3 = 4`. The VVV floor is `n_1 + 3 n_3 = 15`. The MMM tariff is
`2 n_1 + 3 n_3 = 18`.

The cells are `A_pin`, `A_free`, `B_pin`, `B_free` and `C_pin`. The changed
basis is `f_j = sum_{i ≠ j} e_i`. Each `f_j` has self-product 1 over `F_2`,
and distinct vectors have product 0. The only set of free cells with block
weight 4 is `{A_free, B_free}`. In the changed basis, `e_0 · f_2 = 1`, so
those cells are adjacent and the floor is missed. Replacing each `f_j` by
`e_j` removes that edge, and the same set attains 15.

## What was executed

The checker rebuilds the bases, the edges and the weight equation. It does
not rerun the assignment census.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the five-cell example in PR 3596,
head `d92d37b6b875cc2c4d73606a3df8298c44e7d54c`.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to this
graph. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/five-cell-basis-obstruction/verify.py
python3.12 -B research/five-cell-basis-obstruction/test_verify.py
python3.12 -B scripts/research_package.py --package research/five-cell-basis-obstruction
```

## Open next questions

This cell graph is the example. The assignment census would leave it.

## Credit

Nick Petalas stated the five-cell example in the mixed-basis attainment note.
Philippe Van Velzen and Arham Tahir supplied earlier steps of that criterion.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
