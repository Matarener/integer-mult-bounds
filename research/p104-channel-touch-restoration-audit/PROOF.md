# Chronology and frame restoration of the published P104 word

## Claim

Under the pinned #2981 208-flag matching and the #1991 4,058-event channel witness, every target register is first touched at or before event 410, every source register is first touched at or after event 488, no event names both an X register and a Y register, and zero of the 104 source frames and zero of the 104 target frames return to their initial frames.

No new κ is claimed. The selected conditional result remains κ = 0.001672660197076918.

## Why this package exists

Pinned canonical main is `6f100d4bb5083f8c35d96fd95a539811c62f245c`. On that tree, `research/p104-pooled-cut-independent` is Nick Petalas's PR #3259 at `b572b0c25569898579041200e95731c5a43c9189`. Its registered verifier already certifies the PR #3182 fixed-cover cut: exactly one missing required pair among 4,992, `C[71,102] = -1/2`, with a forward cone of 1,725 edges and a disjoint backward cone of 37 edges, under the immutable-X, unread-Y, independent-dirt, monotone equal-frame contract. That certification is not repeated here.

The live gap named after that cut is chronological realization and dirty restoration of the published word. PR #3242 (`research/p104-flag-channel-schedule`, `f3c7e5229d1ce856fe3d6fa5467b10679c0fda14`, jwr404) states the first-touch separation and records that the worked pair X0/Y34 is not restored. Its scientific review was still open on the pinned map, and no second package replays the claim. This note is that replay, plus the restoration census for every endpoint.

## Contract

Sources and targets are the names fixed by the pinned geometry lines

```
sources = [paths[f'X{s}'] for s in range(104)]
targets = [paths[f'Y{t}'] for t in range(104)]
```

A register is touched by an event when its name occurs as a top-level field of that event. Event indices are zero-based positions in `program`. The first touch is the least such index, and the last touch is the greatest. An event is joint when it names at least one X register and at least one Y register.

The matching is the 208 helpers in Nick Petalas's #2981 certificate. Each helper names a source, a target, and a basis whose first vector is the basis head. There are 208 distinct source/target pairs. Each source index and each target index occurs twice.

A register is frame-restored when its initial frame and final frame are equal as sets of integers. Frames in the witness have no repeated vectors, so sorted-tuple equality and set equality coincide. This is a statement about the recorded frames of the published word. It does not track logical coefficients, and it does not say that some other schedule is unable to restore them.

## Chronology

The witness has 4,058 events, and every `X0`–`X103` and `Y0`–`Y103` occurs at least once. The forward scan and the index-list scan agree on the following.

The latest first touch of a target is event 410, attained only by `Y103`. The earliest first touch of a source is event 488, attained only by `X74`. The population gap is 78. Every target first touch is at most 410, and every source first touch is at least 488. Therefore every target begins before every source. In particular, all 208 matched targets are first touched before their matched sources, and no matched pair shares a first index.

No event is joint. The two scanners also compare the full touch sets of each matched pair and find 0 meetings. The smallest matched gap is 84, on source 58 and target 102 (target first at 405, source first at 489). The population gap of 78 is the separation between `Y103` and `X74`, which are not a matched pair.

Flag 0 is source 0, target 34, basis head 232. `X0` occupies events 591 through 3954. `Y34` occupies events 129 through 3500. Their add coefficients are `{-2, 2}` and `{-1/4, 1/4}`. These fields match the pinned #3242 receipt. The coefficient lists in this certificate are sorted lexicographically; #3242 stores the same sets in a different order.

## Frame restoration

Every source initial frame is a singleton, and every source final frame is the coordinate basis `(1, 2, 4, 8, 16, 32, 64, 128, 256)`. Every target initial frame is empty, and every target final frame has rank 8. None of the 104 sources and none of the 104 targets is frame-restored. All 208 matched pairs therefore have both endpoints unrestored.

All 208 source initial frames are exactly the singleton of that flag's basis head. The target final contains that basis head for only four flags: `(0, Y34, 232)`, `(0, Y7, 232)`, `(4, Y23, 196)`, and `(21, Y59, 15)`. The worked #3242 pair is one of those four. It is not the shape of the other 204 flags.

`X0` starts at `[232]` and does not finish there. `Y34` does not start empty-equal to its final frame, and 232 does lie in that final frame. That is the #3242 restored flag, read as frame inequality.

## What this does not prove

A first-touch order is not subspace support. The #3259 cut remains the support statement for `C[71,102] = -1/2` under its own contract; this package does not re-prove it. A changed frame is not a logical identity. Exact coefficient delivery, restoration of arbitrary dirty inputs, native lowering, precision, physical hosting, and a complete channel-plus-correction invoice stay open. Nothing here admits a supplier or changes κ.

## Credit

Nick Petalas supplied the 208-flag certificate in PR #2981 and the independent support-cut certification in PR #3259. dcharb78 supplied the cut itself in PR #3182. jwr404 supplied the chronology reading audited here in PR #3242. The channel witness is the reviewed #1991 word those packages pin. Their files and notices are not modified.
