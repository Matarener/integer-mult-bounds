# Each side of the central triple needs six calls

**Partial. No new exponent.**

The target corner is

`I_2 ⊗ (E_00 + E_22) + M_w ⊗ (E_11 + E_22)`.

It is a symmetric 6-by-6 matrix of rank 6. Every column splits into two
3-bit halves, and the nonzero halves are exactly the three coordinate
vectors. The same is true of the rows.

A call whose coefficient is `1` or `w` places its vector in one half or the
other. Those halves are disjoint, so the stacked rank is the sum of the two
subspace ranks, on all 16 subspaces of the 3-bit space. The three coordinate
vectors therefore force each stacked rank to be at least 3.

Rank-nullity holds for every subspace of the 5-bit and 6-bit spaces: the
annihilator rank plus the subspace rank equals the dimension. Two ranks of 3
sum to 6, so five calls cannot carry both. The X calls and the Y calls each
number at least 6. The selected kappa is unchanged.

## What was executed

The checker builds the corner and counts these dimensions. It does not search
shorter words.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the rank bound in
PR 3774, head `713c28c1b0ebbdf3f30d7887fcb173e7a786f245`.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to this
floor. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/central-triple-rank-floor/verify.py
python3.12 -B research/central-triple-rank-floor/test_verify.py
python3.12 -B scripts/research_package.py --package research/central-triple-rank-floor
```

## Open next questions

This floor is the complementary-coefficient count. A coefficient outside
`{1, w}` would leave it.

## Credit

Wentao Li recorded this rank floor. The two-register minimum is credited
there to Cinna Davis.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
