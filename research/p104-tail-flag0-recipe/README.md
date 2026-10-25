# Target 34's promote recipe matches its frame operator

**Partial. No new exponent.**

The stored rank-1 recipe for target 34's promotion has the same signed Pauli
action and the same exact global phase as the operator built from its physical
frames. The recipe has 9 gates and that operator has 21.

## What was executed

Event 5758 transports `Y34` from `[499, 23, 232, 32, 112, 15, 7, 2]` to the
full frame. The compiled promote record for target 34 has those compressed
columns. Its physical columns are

```text
old  [257, 129, 64, 32, 16, 8, 4, 2]
new  [256, 128, 64, 32, 16, 8, 4, 2, 1]
```

The channel checker compares a recipe with `adjoint(frame(old, 9))` followed
by `frame(new, 9)`. Its equality test requires equal Pauli tableaus and equal
exact global phases. Both hold for this stored recipe. The label isometry that
relates the compressed columns to the physical columns is not recomputed.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
one recipe. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the channel checker, the native interpreter,
the tail word and the compiled transports. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-tail-flag0-recipe/verify.py
python3.12 -B research/p104-tail-flag0-recipe/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-tail-flag0-recipe
```

The replay finishes in under a second.

## Open next questions

The recipe matches the operator of the stored physical columns. The next
reading is whether those columns are the image of the witness frames under the
channel's label isometry.

## Credit

Cinna Davis supplied the stored recipe. The operator equation and the exact
Gaussian interpreter are the native channel's, credited there to Ali Romman's
PR 1862.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
