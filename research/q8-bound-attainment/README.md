# The mixed-negative Q8 bound is attained for t at most 2

**Partial. No new exponent.**

The inherited necessary conditions are `5n >= 11t` and `n ≡ t (mod 2)`. For
`t = 1`, `5 · 2 = 10 < 11 <= 15 = 5 · 3`, so the least count is 3. For
`t = 2`, `5 · 4 = 20 < 22` and `5 · 5 = 25` is odd, so parity lifts the count
from 5 to 6.

In the group, `i^2 = j^2 = z` and `z^2 = 1`. Three factors of one label
therefore multiply that role by `z` times the label: `i^3 = zi` and
`j^3 = zj`. One target takes 3 calls and two targets take 6. Both meet the
bound. The five endpoints are `(zi)`, `(zj)`, `(zi, zi)`, `(zi, zj)` and
`(zj, zj)`.

## What was executed

The checker applies the inherited inequality and multiplies one label three
times. It does not decide `t` greater than 2, and it does not re-prove
`5n >= 11t`.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the attainment in PR 3697, head
`b5fa8645bff6db3ff219815e6fc820a4f08b0572`.

## Scope and evidence

Original card: `bit-new-register-model`, priority revision 6, refined to this
attainment. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/q8-bound-attainment/verify.py
python3.12 -B research/q8-bound-attainment/test_verify.py
python3.12 -B scripts/research_package.py --package research/q8-bound-attainment
```

## Open next questions

This attainment is the comparison. Deciding `t` greater than 2 would leave it.

## Credit

Nick Petalas published the attainment for `t` at most 2.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
