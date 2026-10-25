# The named schedule does not cite event 5759

**Partial. No new exponent.**

The tail readme points at pull request 1940 and says the tail word does not
integrate with that schedule. The merged package is
`research/p104-target-order-delivery`. None of its eight files cite event
5759 or the tail seed.

## What was executed

The audit packet for pull request 1940 lists exactly the eight files of
`research/p104-target-order-delivery`, and each blob matches the file pinned
here. The tail readme contains the pull-request URL and the sentence "does
not integrate with that schedule."

The schedule's complete-cost formula includes `C_side_corrections` and
`C_hosting_and_precision`, and the readme says those terms remain unresolved.
A scan of all eight files finds neither `5759` nor `749717`.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
one schedule. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the tail readme, the audit packet and the
eight schedule files. No selected frontier file changes. This reading does
not build an owner map.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-tail-flag0-schedule/verify.py
python3.12 -B research/p104-tail-flag0-schedule/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-tail-flag0-schedule
```

The replay finishes in under a second.

## Open next questions

The schedule the tail names does not contain the read. An owner for event
5759 would have to come from a different word.

## Credit

Adam Gall supplied the 32-chain schedule in pull request 1940, as the audit
packet records. Cinna Davis supplied the tail word that names that schedule
and declines to integrate with it.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
