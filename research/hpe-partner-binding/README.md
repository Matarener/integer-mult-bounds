# The selected HPE binding accepts a self-partner tail gate

**Partial. No new exponent.**

The hyperplane-end label statement requires the cleanup gate `h -= p` to use
two different registers. The instance checker rejects `h == p`. The selected
binding script does not read the partner index. It accepts a tail gate when
the operation is `add`, the coefficient pair is `[-1, 1]`, the helper's final
frame is the gate's terminal, and the named recipe equals one of the three
Lean pair monomials.

On a synthetic tail of 38 gates using all three pairs, one gate has the helper
as its own partner. Those binding rules accept it. The same tail with every
partner moved off the helper is also accepted. Changing the coefficient to
`+1` is rejected. This word is not an emitted supplier word.

## What was executed

The checker parses `pair1`, `pair2` and `pair3` from the Lean source and
applies the binding's published gate rules. It does not import that script
and it does not run Lean.

## Scope and evidence

Original card: `formal-interface-lemma`, priority revision 6, refined to the
distinct-register hypothesis of the hyperplane-end label statement.
[TASK.json](TASK.json) records the scope change. [RESULT.json](RESULT.json) is
the executed receipt and is not rewritten. [SOURCES.json](SOURCES.json) pins
the binding script, the Lean pairs, the instance checker and the proof note.
No selected frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:10 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3536 note at 2026-10-18
05:07 UTC, was released work. Draw seed `746e1554aeb802fed04786675ba8de6e`,
track `independent-verification`, first card `formal-interface-lemma`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/hpe-partner-binding/verify.py
python3.12 -B research/hpe-partner-binding/test_verify.py
python3.12 -B scripts/research_package.py --package research/hpe-partner-binding
```

The replay finishes in under a second.

## Open next questions

The binding gap is this synthetic self-partner gate. The instance checker
already states the corresponding rejection, and this package does not replay
an emitted word.

## Credit

Jeremy Kothe's hyperplane-end note states the distinct-register label
hypothesis and the three Lean pairs. The instance checker states the `h == p`
rejection. The selected binding script states the coefficient and recipe
comparison.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
