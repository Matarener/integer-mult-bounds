# The restore recipe matches the reverse frame operator

**Partial. No new exponent.**

Event 5807 returns `Y34` from the full frame to its rank-8 frame. The stored
rank-1 recipe for that restoration has the same signed Pauli action and the
same exact global phase as the operator of those physical frames.

## What was executed

The restore record for target 34 has compressed columns

```text
[1, 2, 4, 8, 16, 32, 64, 128, 256]
  -> [499, 23, 232, 32, 112, 15, 7, 2]
```

and physical columns

```text
[256, 128, 64, 32, 16, 8, 4, 2, 1]
  -> [257, 129, 64, 32, 16, 8, 4, 2]
```

The channel equation builds `adjoint(frame(old, 9))` followed by `frame(new, 9)`.
The recipe has 9 gates and that operator has 21. Their Pauli tableaus agree,
and so do their exact global phases.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
one restore recipe. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the channel checker, the native interpreter,
the tail word and the compiled transports. No selected frontier file changes.
This reading does not name an owner for the source read at event 5759.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-tail-flag0-restore/verify.py
python3.12 -B research/p104-tail-flag0-restore/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-tail-flag0-restore
```

The replay finishes in under a second.

## Open next questions

Both frame changes of this target match native operators. The add at event
5759 still needs an owner for its read of `X0`.

## Credit

Cinna Davis supplied the stored restore recipe. The operator equation is the
native channel's, credited there to Ali Romman's PR 1862.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
