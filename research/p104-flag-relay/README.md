# Each matched source reaches its target through a relay

**Partial. No new exponent.**

Under the channel's addition rule, all 208 published flags deliver their source
value into the matched target. The final coefficient is `1/2` for 153 flags and
`-1/2` for 55. Every delivery happens after that source's first event. `X0`
reaches `Y34` at event 2815 with coefficient `1/2`.

## What was executed

The pinned checker updates a destination by `coefficient * source` and replaces
a destination on a copy. This replay uses that rule and does not import the
checker. Registers begin holding themselves.

`X0` is first touched at event 591. Its value then moves as follows.

| Event | Operation | Effect on the X0 coefficient |
|---:|---|---|
| 1311 | `G0 += -2 * X0` | `G0` receives `-2` |
| 1564 | `Q0 += 1 * G0` | `Q0` receives `-2` |
| 2462 | copy `Q0` into `C` | `C` receives `-2` |
| 2497 | `D17 += 1 * C` | `D17` receives `-2` |
| 2815 | `Y34 += -1/4 * D17` | `Y34` receives `1/2` |

The final coefficient in `Y34` is the same `1/2`. The same scan gives a nonzero
final coefficient for every matched pair, and in every case the first arrival
is at or after the source's first event.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
relay. [TASK.json](TASK.json) records the scope change. [RESULT.json](RESULT.json)
is the executed receipt and is not rewritten. [SOURCES.json](SOURCES.json) pins
the flag certificate, the channel witness, the addition rule, the register
naming and the task catalogue. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-flag-relay/verify.py
python3.12 -B research/p104-flag-relay/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-flag-relay
```

The replay finishes in under a second.

## Open next questions

The channel checker treats this final combination as the physical boundary and
places the side correction outside the replay. Comparing `1/2` with the Gram
entry for source 0 and target 34 is the remaining identity.

## Credit

Nick Petalas supplied the 208-flag certificate. The addition rule and the
channel witness are the native-channel files that certificate's lineage pins.
Chafik Boukhalfa supplied that channel through PR 1991, as credited there.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
