# The mixed coefficients do not lower the twelve-call floor

**Partial. No new exponent.**

The four-label floor counts calls whose coefficients lie in `{1, w}`. The two
remaining coefficients are `w^2 = 1 + w`. Each of the six labels is an
involution. For every nonzero pair `(α, β)`, the four-call word

```text
X_α, Y_β, X_α, Y_β
```

equals the central element `(0, 0, αβ)`. The same twelve-call schedule as the
four-label word therefore still realizes `Z_1`, `Z_w` and `Z_{w^2}` on three
registers.

In the six-by-six expansion, an `X` label of any nonzero coefficient occupies
only the first off-diagonal block, and a `Y` label occupies only the second.
The product of two nilpotents is nonzero only when an `X` follows a `Y`, and
that product is the corner whose coefficient is `αβ`. The contragredient
reverses the order: only a later `Y` after an earlier `X` fills the opposite
corner. Squares vanish.

A call with coefficient `1`, `w` or `w^2` contributes the stacked column
`(u, 0)`, `(0, u)` or `(u, u)`. For spans `A`, `B` and `C` of those three
families, the stacked image has dimension

```text
dim A + dim B + dim C - dim(A ∩ B ∩ C),
```

which is at least `dim(A + B + C)`. The target corner's two components have
joint column space of dimension 3, so each side's stacked image and its dual
span both have dimension at least 3. The kernel count then requires at least
six `X`-type calls and six `Y`-type calls. The inequality holds for all
300,763 triples of subspaces of a four-bit space. The selected kappa is
unchanged.

## What was executed

The checker evaluates the nine commutators, the twelve-call word, the
nilpotent table, the 28 projector products and the subspace inequality. It
does not search words.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the open mixed-coefficient
question in PR 3774, head `713c28c1b0ebbdf3f30d7887fcb173e7a786f245`.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to this
six-label floor. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

Overlap search on 2026-10-18 covered 491 open pull requests and 2,509
discussions. The matches are earlier uses of this card, including the
four-label floor. This package changes the question to the two mixed
coefficients.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/six-label-central-floor/verify.py
python3.12 -B research/six-label-central-floor/test_verify.py
python3.12 -B scripts/research_package.py --package research/six-label-central-floor
```

## Open next questions

The six-label formal minimum is twelve. A physical embedding would be a
different contract.

## Credit

Wentao Li left the mixed-coefficient question open in the four-label floor.
Cinna Davis recorded the fourteen-call composite. The rank-one call model is
credited there to eumemic and woklerx.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
