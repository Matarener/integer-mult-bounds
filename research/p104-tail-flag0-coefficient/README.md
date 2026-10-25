# The tail add for flag 0 is minus one half

**Partial. No new exponent.**

The published tail word keeps the 4,058-event channel and later contains one
add of `X0` into `Y34`. Event 5759 is `Y34 += -1/2 * X0`. The channel prefix
ends with coefficient `+1/2` for the same pair, and the two coefficients sum
to `0`.

## What was executed

The 104 ports are the 120 sorted eight-coordinate roots with the fixture's
`F0` and `C` lines removed. Port 0 is `[0, 0, 0, 0, 0, 2, 0, -2]` and port 34
is `[1, -1, -1, -1, -1, 1, -1, -1]`. Their normalized inner product is 1.

The published row formula is `coefficient[t,s] = delta[t,s] - G[t,s]/2`. For
target 34 and source 0 that value is `-1/2`. The same roots and coefficient
appear once in `CORRECTION-ROWS.json` and once in the tail word, at event
5759. The first 4,058 tail events are the channel word. The channel addition
replay ends at `+1/2`, so the published pair sums to the off-diagonal identity
entry.

The first add after the prefix is a different pair: event 4059 adds `-1/2`
times `X2` into `Y0`.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
one tail event. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the channel witness, the fixture, the tail
word and the correction rows. No selected frontier file changes. This reading
does not replay the 280-column identity or assign hosts to the tail.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-tail-flag0-coefficient/verify.py
python3.12 -B research/p104-tail-flag0-coefficient/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-tail-flag0-coefficient
```

The replay finishes in under a second.

## Open next questions

The coefficient is the identity residual when `X0` and `Y34` are still legally
readable at event 5759. The next reading is the frame on that event against
the frames the channel left behind.

## Credit

Cinna Davis supplied the tail word and the row formula. The channel prefix is
the native witness credited to Chafik Boukhalfa and, through that package, to
Rohan Arun's PR 1972.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
