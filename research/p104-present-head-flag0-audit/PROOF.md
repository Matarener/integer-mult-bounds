# Proof: present-head flag 0 late-only target hosting, literal and in span

## Setup

Pin CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`, the #2981
208-flag matching (`research/p104-joint-unit-flags/CERTIFICATE.json`), and the
reviewed #1991 channel witness
(`research/p104-native-channel/inputs/LOWRANK-WITNESS.json`, 4,058 events).

A register annotation is a transport before- or after-frame, or an add frame,
naming that register. The basis head of a matched flag is the first vector of its
basis. Open #3349 records that the target final contains that head for exactly
flags `(0, 1, 9, 43)`. This note audits flag 0, the coefficient-cascade target
`Y34`.

Labels are vectors in the nine-dimensional binary space, written as integers
below 512. `research/p104-native-channel/PROOF.md` §2 treats each frame as a
binary frame `W` with canonical chart `Gamma_W`, and says every transport is
nested. A register *lists* the head when the head is one of the frame's vectors.
It *spans* the head when the head is a GF(2) sum of frame vectors. Listing
depends on the chosen generators. Spanning does not.

## Statement

Flag 0 has source `X0`, target `Y34` and basis head `232`. On the published word:

1. `X0` begins at `[232]`. Its first event, transport 591, goes from `[232]` to
   `[8, 32, 64, 128, 256]`. This removes `232` from the list. No later `X0`
   annotation lists `232`.
2. The event-591 after-frame spans `232` through the unique decomposition
   `8 ^ 32 ^ 64 ^ 128`. All 22 `X0` annotations span `232`. In span, the source
   never drops the head.
3. `Y34` starts empty. Every preterminal `Y34` annotation excludes `232` from
   both its listed vectors and its GF(2) span. In particular the before-frame of
   the terminal transport is `[95, 502, 16, 32, 2]`, whose span excludes `232`.
4. Event 3500 is the last `Y34` event. It is a transport from
   `[95, 502, 16, 32, 2]` to the target final
   `[499, 23, 232, 32, 112, 15, 7, 2]`. This after-frame is the first `Y34`
   annotation that lists or spans `232`. The literal gap from the source drop is
   2,909 events.
5. `Y34`'s row changes only at adds with `Y34` as the destination: fifteen
   events from 129 through 3369. Each add runs in a common chart that excludes
   `232` from its span.
6. No event names both `X0` and `Y34`. `X0` has four events after 3500 (3642,
   3798, 3850 and 3954), and none of them names `Y34`. At event 3500, `X0`
   already sits on the coordinate basis `[1, 2, 4, 8, 16, 32, 64, 128, 256]`,
   which does not list `232` but still spans it.
7. All eleven endpoint transports (five on `X0`, six on `Y34`) are nested upward.
   Each transport's paid rank (its fifth field, which
   `research/p104-native-channel/check_native.py` binds to the compiled recipe
   rank) equals the rank increase. This matches the binary-frame reading.
8. Neither endpoint frame returns to its initial frame. `X0` goes from rank 1 to
   rank 9 and `Y34` from rank 0 to rank 8.

By items 2 and 4, the first chronological cut at which both endpoint frames
host the head direction is the after-frame of event 3500. By items 4 to 6, the
published word has no `Y34` event after that cut and no `Y34` update at or after
it. So no target update, and no event touching the target, happens while both
endpoints host the basis-head direction. Logical dirty restoration of the source
line into `Y34` along co-hosted basis-head geometry is unavailable on this word
ahead of the published `I-G/2` tail add. Under listing alone the same conclusion
holds with a 2,909-event gap; open #3575 already records the literal arrive at
3500 and the empty forward Q-relay. Item 2 shows that the literal source drop and
the coordinate-basis reading at 3500 are chart changes, not losses of direction.

## Checking method

Two scanners read the same pinned inputs. The primary scanner walks annotations
in program order and decides span membership by pivot-indexed row reduction. It
tracks combinations so it can return the decomposition of the head. The second
scanner indexes events per endpoint first, then builds each span as an explicit
XOR closure (at most 512 labels) and finds the decomposition by exhaustive subset
search. Both reject duplicate JSON keys and dependent frames, enforce the
SHA-256 source pins, and admit through `need()` under `python -O`. Their
receipts must equal the committed certificate.

`test_package.py` copies the package and its inputs into a temporary tree. It
mutates four certificate fields, injects a duplicate key and flips one byte of
the witness. Both scanners must reject each change under `-O`. A negative
control edits an in-memory witness so that `Y34`'s frame from event 3368 onward
is `[95, 95 ^ 232]`, which spans `232` without listing it. The listing count
stays at zero, but the span fields move: hosting starts at 3368 and one of the
fifteen adds now runs in a head-hosting chart. This shows the span check catches
what listing misses.

## Soft overlap

Merged #3242 already records `X0`'s first event at 591 on `[232]`, and that no
matched pair shares an event. This package reuses those facts and adds the span
reading of the source and the target-side chronology for `Y34`. Open #3575
records the literal flag-0 relay cut (drop 591, arrive 3500, empty forward
Q-relay) without span membership, head-free update counts, or nested-transport
checks. Open #3451/#3443/#3456 pin flags 1/9/43 and leave flag 0 alone; this
package does not re-audit those paths. The tail-flag0 coefficient cascade
(`research/p104-tail-flag0-*`) pins the published `-1/2` add at event 5759 on
the promoted frame; this package recomputes no coefficient and does not read
the tail word. Open #3392 (flag 2) and the #3349 census are not recomputed.

## Limits

This is a statement about the published frames of one matched flag. "Hosting"
means the head is listed in, or spanned by, an annotated endpoint frame. The
package does not model what the head direction means inside the relay registers
(`G`, `Q`, `D`, `C`). It does not price a repair, construct a changed schedule,
assign an owner to event 5759, or claim a new κ. A schedule that brings `232`
into `Y34`'s span before event 3369 is outside this certificate.
