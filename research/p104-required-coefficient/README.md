# The required X102 coefficient in Y71 is -1/2

**Partial. No new exponent.**

The archived fixed-cover correction has 4,992 nonzero entries. The entry for
target Y71 and source X102 is `-4`, so its coefficient is `-1/2`. The channel
path of X102 has 5 frames and the path of Y71 has 7. Those frames are
disjoint, so this pair has no direct contact.

## What was executed

The coefficient is recomputed from the frozen P104 roots and the removed F0
and C vectors. The two channel paths are recomputed from the frozen witness
transports. The archived receipt names the same coefficient, pair count and
missing pair. The pooled recurrence and its 2,309 edges are not replayed.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
coefficient and direct contact. [TASK.json](TASK.json) records the scope
change. [RESULT.json](RESULT.json) is the executed receipt and is not
rewritten. [SOURCES.json](SOURCES.json) pins the fixture, the witness and the
archived rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-required-coefficient/verify.py
python3.12 -B research/p104-required-coefficient/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-required-coefficient
```

The replay finishes in under a second.

## Open next questions

The archived layers say X102 has 16 readers at dimension one. The next reading
is that count.

## Credit

Nick Petalas supplied the archived coefficient rule in the pooled-cut checker.
dcharb78 supplied the cut claim audited there. The frozen channel witness and
fixture retain their own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
