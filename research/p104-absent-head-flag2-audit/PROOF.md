# Matched flag 2: published channel never hosts the basis head

## Claim

Under the pinned #2981 matching and the #1991 4,058-event channel witness, matched
flag 2 has source `X1`, target `Y84`, and basis head `488`. The published word

- starts `X1` at the singleton frame `[488]`,
- drops `488` from `X1` at the first source event (transport 494),
- never annotates `488` on any of the 13 `Y84` events,
- ends with a `Y84` final frame that excludes `488`,
- and never names `X1` and `Y84` in the same event.

Therefore the published channel cannot chronologically supply a frame-hosted
basis-head coefficient, or dirty-restore the source line into the matched target
along this flag's nested geometry: the head vector is absent from every recorded
`Y84` frame, and after event 494 it is also absent from every recorded `X1` frame.

No new κ is claimed. The selected conditional result remains
κ = 0.001672660197076918.

## Why this package exists

Open PR #3349 (`research/p104-channel-touch-restoration-audit` @ `be1d09a0`) already
registers the full endpoint frame-restoration census: zero of 208 endpoint frames
restored, and the basis head meets the target final on only four flags
`(0, 1, 9, 43)`. Its open question asks to pin one absent-head flag and state the
coefficient or restoration steps that flag still lacks. This package answers that
question for flag 2. It does not extend the 208-flag census and does not rebuild
the #3259 support cut.

No registered package on pinned main closes this one-flag hosting obligation.
Open algebraic-relay notes that treat all 208 flags as delivering a scalar ±1/2
through helper registers address a different quantity: linear value transport, not
presence of the geometric basis head in the matched target's annotated frames.

## Contract

Registers are the names fixed by

```
sources = [paths[f'X{s}'] for s in range(104)]
targets = [paths[f'Y{t}'] for t in range(104)]
```

Flag 2 is helper index 2 in Nick Petalas's #2981 certificate: source 1, target 84,
departure choice 0, arrival choice 0, ordered basis beginning with `488`.

An annotated frame is a frame list recorded on a `transport` (before and after) or
on an `add` (destination annotation) that names the register. Hosting means the
basis head appears in such an annotated frame. This is a statement about the
published witness bytes. It does not track algebraic coefficients through helper
registers `G*`, `Q*`, `D*`, or `C`.

## Evidence

`X1` occupies 25 events from 494 through 4006. Event 494 is

```
["transport", "X1", [488], [8, 64, 416], 2]
```

That is the unique source annotation containing `488`. Every later `X1` annotation
uses frames drawn from the coordinate-side nest and never restores `488`.

`Y84` occupies 13 events from 325 through 3550. The union of its annotated vectors
is exactly `{1, 3, 4, 12, 44, 75, 106, 243, 484, 486}`. The basis head `488` is not
among them. The final frame is `[243, 484, 12, 44, 75, 3, 4, 1]`, which also excludes
`488`. No target among `Y0`–`Y103` ends with `488` in its final frame.

There is no joint `X1`/`Y84` event. Target first touch (325) precedes source first
touch (494), matching the #3242/#3349 chronology shape, but the new content is the
head-hosting obstruction on this absent-head flag.

## Obligation stated

For flag 2, a chronological correction that uses the nested flag's source line must
still supply

1. a moment when `488` is live in a frame that can receive or cancel dirt on that
   line at the matched target, and
2. delivery of the corresponding coefficient against that hosted direction,

neither of which the published annotated word provides. Frame inequality alone is
not a priced repair; this package only pins that the published channel cannot be
that repair for the basis-head direction of flag 2.

## What this does not prove

It does not refute helper-mediated scalar delivery of an `X1` value into `Y84`.
It does not price a changed schedule that introduces `488` into `Y84`. It does not
admit a supplier, change κ, or generalize automatically to the other 203
absent-head flags (though the same method applies). The #3259 support cut for
`C[71,102] = -1/2` is untouched.

## Credit

Nick Petalas / #2981 for the flags, the #3349 census for naming the absent-head
gap, jwr404 / #3242 for the chronology reading that census replayed, and the
reviewed #1991 channel for the witness. Their files are not modified.
