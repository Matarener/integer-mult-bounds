# The flag-0 add runs on the promoted frame

**Partial. No new exponent.**

`X0` already holds the full frame the channel recorded as its final frame, and
the tail never writes `X0`. Event 5758 promotes `Y34` from its rank-8 channel
frame to that same full frame. Event 5759 adds `-1/2` times `X0` there. Event
5807 restores the rank-8 frame.

## What was executed

The channel's recorded final frames are

```text
X0   [1, 2, 4, 8, 16, 32, 64, 128, 256]
Y34  [499, 23, 232, 32, 112, 15, 7, 2]
```

The tail word's first 4,058 events are the channel word. Walking the listed
transports of these two registers ends the prefix on those same frames. After
the prefix, `X0` is never the destination of an event. `Y34` has two later
transports:

```text
5758  rank 1  channel frame -> full frame
5807  rank 1  full frame -> channel frame
```

The add at 5759 lists the full frame for both registers. All 48 tail adds into
`Y34` sit strictly between those two transports. The XOR span of the eight
channel vectors has 256 elements and sits inside the 512-element span of the
full frame.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to these
listed frames. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the channel witness and the tail word. No
selected frontier file changes. This reading does not compile the transport
as a native recipe or assign an owner to the source read.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-tail-flag0-frames/verify.py
python3.12 -B research/p104-tail-flag0-frames/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-tail-flag0-frames
```

The replay finishes in under a second.

## Open next questions

The listed frames meet at the add. The next reading is whether event 5758 is
one record in the tail package's compiled native transports.

## Credit

Cinna Davis supplied the tail word. The channel frames come from the native
witness credited to Chafik Boukhalfa and, through that package, to Rohan Arun's
PR 1972.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
