# Proof: present-head flag 43 late-only target hosting, with tail co-hosting

## Setup

Pin CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`, the #2981
208-flag matching (`research/p104-joint-unit-flags/CERTIFICATE.json`), and the
reviewed #1991 channel witness
(`research/p104-native-channel/inputs/LOWRANK-WITNESS.json`, 4,058 events).

A register annotation is a transport before- or after-frame, or an add frame,
naming that register. The basis head of a matched flag is the first vector of its
basis; the other eight vectors are its *tail*. Open #3349 records that the target
final contains the head for exactly flags `(0, 1, 9, 43)`. This note audits
flag 43.

Labels are vectors in the nine-dimensional binary space, written as integers
below 512. `research/p104-native-channel/PROOF.md` §2–§3 treats each frame as a
binary frame `W` with canonical chart `Gamma_W`: every transport is nested and
changes only `W`, and a scalar addition is allowed only in a common chart and is
the only operation that changes the destination's row. A register *lists* a
vector when it is one of the frame's vectors. It *spans* the vector when the
vector is a GF(2) sum of frame vectors. Listing depends on the chosen
generators. Spanning does not.

## Statement

Flag 43 has source `X21`, target `Y59`, basis head `15` and tail
`[387, 6, 18, 32, 67, 128, 1, 2]`. On the published word:

1. `X21` begins at `[15]`. Its first event, transport 570, goes from `[15]` to
   `[3, 4, 8, 128, 256]`. This removes `15` from the list. No later `X21`
   annotation lists `15`.
2. The event-570 after-frame spans `15` through the unique decomposition
   `3 ^ 4 ^ 8`. All 22 `X21` annotations span `15`, so in span the source never
   drops the head. `X21` is never an add destination; 12 of its 17 events are
   reads (adds with `X21` as the second register).
3. `Y59` starts empty. Its preterminal frames are `[]`, `[500]`, `[127, 500]`,
   `[447, 127, 52]`, `[95, 447, 32, 20]` and `[95, 447, 6, 32, 20]`. None of
   their spans contains `15`; the largest has rank 5 (32 elements).
4. Event 3525 is the last `Y59` event. It is a rank-3 transport from
   `[95, 447, 6, 32, 20]` to the target final `[499, 27, 228, 32, 112, 15, 7, 1]`.
   This after-frame is the first `Y59` annotation that lists or spans `15`. The
   literal gap from the source drop is 2,955 events.
5. `Y59`'s row changes only at its 15 adds as destination. Ten (events 223–227,
   2099, 2191, 2275, 2341 and 2393) run in the empty chart. Five (2698, 2891,
   3076, 3231 and 3364) run in non-empty charts of ranks 1 to 5. All 15 charts
   exclude `15` from their span.
6. **Tail co-hosting.** `Y59`'s span first contains a tail vector at the
   after-frame of event 3230 (`32`). From the after-frame of event 3363 it
   contains `6`, `18 = 6 ^ 20` and `32`. The adds at 3231 (chart rank 4) and
   3364 (chart rank 5) therefore run in charts that span `{32}` and
   `{6, 18, 32}` but not `15`. At both adds, `X21`'s live frame (replayed from
   its initial frame through its transports) is the rank-9 coordinate frame, so
   it spans the head and every tail vector. Both endpoints co-host part of the
   flag's basis geometry at `Y59`'s last two updates, but never the head.
7. No event names both `X21` and `Y59`, and no `zero`, `copy` or `erase` event
   names either. `X21` has four events after 3525 (3705, 3760, 3811 and 3863);
   all are reads and none names `Y59`.
8. All 11 endpoint transports (five on `X21`, six on `Y59`) are nested upward.
   Each transport's paid rank (its fifth field, which
   `research/p104-native-channel/check_native.py` binds to the compiled recipe
   rank) equals the rank increase. `Y59`'s steps are `1, 1, 1, 1, 1, 3`.
9. Neither endpoint frame returns to its initial frame. `X21` goes from rank 1
   to rank 9 and `Y59` from rank 0 to rank 8.

By items 2 and 4, the first chronological cut at which both endpoint frames
host the head direction is the after-frame of event 3525. By items 4, 5 and 7,
the published word has no `Y59` event after that cut and no `Y59` update at or
after it. So no target update, and no event touching the target, happens while
both endpoints host the basis-head direction. Logical dirty restoration of the
source line into `Y59` along co-hosted basis-head geometry is unavailable on
this word. Under listing alone the same conclusion holds with a 2,955-event gap.

Item 6 sharpens this. The obstruction is not that `Y59` is geometrically empty
of the flag while it is updated: at its last two updates both endpoints already
co-host up to three tail directions. Only the head direction is missing, and it
arrives in the single terminal step.

This answers #3451's second open question for flag 43: in span the source keeps
the head direction throughout, and the target gains it only at its terminal
transport.

## Not a reprint

Both scanners carry the drop/arrive/gap tuples published by open #3451 (flag 1:
591/3473/2882) and #3443 (flag 9: 500/3489/2989) and refuse to admit a flag-43
chronology equal to either. Flag 43's tuple is 570/3525/2955. Its target `Y59`
has 15 updates and 6 transports; #3451's certificate records 6 updates and 3
target transports for `Y7`. Item 6 has no counterpart in either prior: #3451's
certificate records `Y7`'s largest preterminal span as `{0, 95, 441, 486}`,
which contains none of flag 1's basis vectors.

The source side is a near-template repeat. `X21` has the same event shape as
#3451's `X0` (17 events, 22 annotations, five transports, rank 1 to 9, four
events after the target's terminal event); only the frames and the decomposition
`3 ^ 4 ^ 8` differ. The new content is on the target side.

## Checking method

Two scanners read the same pinned inputs. The primary scanner walks annotations
in program order, decides span membership by pivot-indexed row reduction, tracks
combinations to return the head's decomposition, and carries `X21`'s live frame
forward, checking that each transport's before-frame equals it. The second
scanner indexes events per endpoint first, builds each span as an explicit XOR
closure (at most 512 labels), finds the decomposition by exhaustive subset
search, and reads `X21`'s live frame at a target event by bisecting its
transport list. Both reject duplicate JSON keys and dependent frames, enforce
the SHA-256 source pins, and admit through `need()` under `python -O`. Their
receipts must equal the committed certificate.

`test_package.py` copies the package and its inputs into a temporary tree. It
mutates six certificate fields, injects a duplicate key and flips one byte of
the witness. Both scanners must reject each change under `-O`. A negative
control edits an in-memory witness so that `Y59`'s frame from event 3363 onward
is `[95, 447, 27, 32, 20]`, which spans `15 = 20 ^ 27` without listing it while
keeping every transport nested with the same rank steps. The listing count stays
at zero, but the span fields move: hosting starts at 3363, the add at 3364 now
runs in a head-hosting chart, and it leaves the tail-without-head list. A
reprint guard injects flag 43's own tuple as a prior and checks that both
scanners stop with `reprint of a prior`.

## Soft overlap

Open #3349 already names `(21, Y59, 15)` as a present-head triple and records
that every endpoint frame is unrestored (item 9). Merged #3242 records that no
matched pair shares an event (item 7's joint count). This package reuses those
facts and adds the span chronology of `X21` and `Y59`, the update-chart split
and the tail co-hosting.

Open #3363 records relay delivery for all 208 flags, which implicitly includes
flag 43's delivery coefficient. This package recomputes no coefficient and does
not identify the delivering add. Conditional on #3363, the delivery into `Y59`
changes `Y59`'s row, so by the channel's addition rule it occurs at one of the 15
adds of item 5 and hence in a head-free chart. That remark is not certified here.
Open #3365/#3371/#3372 work on flag 0 and `Y34`; this package says nothing about
either. Open #3392 (flag 2), #3443 (flag 9) and #3451 (flag 1) are not
recomputed.

## Limits

This is a statement about the published frames of one matched flag. "Hosting"
means the vector is listed in, or spanned by, an annotated endpoint frame. The
package does not model what the head direction means inside the relay registers
(`G`, `Q`, `D`, `C`). It does not price a repair, construct a changed schedule,
or claim a new κ. Because the 3525 transport is nested and `15` is listed in the
final frame, the rank-6 frame `[95, 447, 6, 32, 20, 15]` lies inside `Y59`'s
final span; whether a schedule can use it before event 3364, and at what cost, is
outside this certificate.
