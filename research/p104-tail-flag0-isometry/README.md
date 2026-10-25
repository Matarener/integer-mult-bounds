# The witness frames map to the stored physical columns

**Partial. No new exponent.**

The channel's stored label isometry sends both frames of event 5758 to the
physical columns stored with target 34's promote recipe.

## What was executed

Event 5758 transports `Y34` from `[499, 23, 232, 32, 112, 15, 7, 2]` to
`[1, 2, 4, 8, 16, 32, 64, 128, 256]`. The isometry is the one stored in the
channel recipes: multiply by the stored dual Gram, then expand in the stored
orthonormal basis. Each image is reduced by the compiler's pivot rule.

The images are

```text
rank 8  [257, 129, 64, 32, 16, 8, 4, 2]
full    [256, 128, 64, 32, 16, 8, 4, 2, 1]
```

Those are the physical columns of the promote record. The stored dual Gram
equals the native checker's inverse of the stored compressed Gram. The
orthonormal basis is the stored one; this run does not search for another.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to these
two images. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the channel recipes, the transform and basis
formulas, the native inverse, the tail word and the compiled transports. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-tail-flag0-isometry/verify.py
python3.12 -B research/p104-tail-flag0-isometry/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-tail-flag0-isometry
```

The replay finishes in under a second.

## Open next questions

The promotion now ties the witness frames to the checked operator. The restore
at event 5807 has the swapped frames, and its recipe has not been compared
with that operator.

## Credit

Chafik Boukhalfa supplied the channel isometry and its formulas. Cinna Davis
supplied the stored physical columns.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
