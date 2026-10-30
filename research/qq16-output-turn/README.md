# The displayed output is one quarter-turn

**Partial. No new exponent.**

The source formula is `(s - i d) / 2`. Multiplying by `i` gives

```text
i · (s - i d) / 2 = (d + i s) / 2
```

because `i · (s - i d) = d + i s`. The displayed proof text therefore differs
from the pinned native formula by one quarter-turn. Component magnitudes are
unchanged.

The numeric invoice factors as follows. Each of the 11,076 axis factors pays
`4 + 2 + 4 = 10` real operations, so the lambda coefficient is

```text
11076 · 10 = 110760
```

The lambda-one total is `483082`, and `483082 - 110760 = 372322`. The 528
covers pay `528 · 4 = 2112` real transfers per `N`. Storage is
`712 · 2 + 2 = 1426` words of scale `N`, plus 12 scalar words. Thus the
published reference is `(372322 + 110760 · lambda) · N + 12`, with
`N = 2^(73 · lambda)`.

## What was executed

The checker multiplies the quarter-turn on a 5-by-5 integer grid and factors
these coefficients. It does not expand the events.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the invoice in PR 3652, head
`35f38c8482e70129860cdb174615bc8f2251b01a`.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
turn. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/qq16-output-turn/verify.py
python3.12 -B research/qq16-output-turn/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-output-turn
```

## Open next questions

This turn and this invoice are the check. Expanding the events would leave
them.

## Credit

ToikY published the independent QQ16 source certificate and the quarter-turn
comparison.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
