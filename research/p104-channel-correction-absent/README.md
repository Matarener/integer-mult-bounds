# The channel word leaves the coefficient at 1/2

**Partial. No new exponent.**

The native channel witness is one program of 4,058 events. Its opcodes are
`add`, `transport`, `zero`, `copy` and `erase`. `X0` enters `Y34` at event
2815 with coefficient `1/2` and keeps that value through event 4057. The
package states that no `I-G/2` side word is supplied.

## What was executed

The witness has three sections: `initial_frames`, `final_frames` and `program`.
The program counts are 2,624 additions, 1,410 transports, and eight each of
`zero`, `copy` and `erase`. Those addition and copy counts are the counts in
`EXPECTED.json`. No other opcode appears.

The addition replay records `X0` inside `Y34` from event 2815 onward. Every
recorded value is `1/2`.

`EXPECTED.json` says the scope contains no `I-G/2` side correction. The task
blocks on the sentence "No complete compatible side word or fully charged
profile supplied."

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
reading of the channel word. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the expected receipt, the channel task, the
witness and the task catalogue. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-channel-correction-absent/verify.py
python3.12 -B research/p104-channel-correction-absent/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-channel-correction-absent
```

The replay finishes in under a second.

## Open next questions

A later package may contain the side word that this channel does not. The next
reading is one event in such a package that changes an off-diagonal `G/2`
coefficient.

## Credit

Chafik Boukhalfa supplied the native channel and its task statement. Rohan Arun
supplied the scalar channel through PR 1972, as that package credits it.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
