# Proof: present-head flag 9 late-only target hosting

## Setup

Pin CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`, the #2981
208-flag matching (`research/p104-joint-unit-flags/CERTIFICATE.json`), and the
reviewed #1991 channel witness
(`research/p104-native-channel/inputs/LOWRANK-WITNESS.json`, 4,058 events).

A register annotation is a transport before/after frame or an add frame naming
that register. The basis head of a matched flag is the first vector of its
basis. Open #3349 records that the target final contains that head for exactly
the flag indices `(0, 1, 9, 43)`. This note audits index 9.

## Statement

Let flag 9 have source `X4`, target `Y23`, and basis head `196`. On the published
word:

1. `X4` begins at `[196]` and first transports at event 500 from `[196]` to
   `[8, 64, 132, 260]`, dropping the head.
2. No later `X4` annotation contains `196`.
3. No `Y23` annotation with event index strictly less than 3489 contains `196`.
4. Event 3489 is the last `Y23` event. It is a transport whose before-frame
   excludes `196` and whose after-frame equals the target final and contains
   `196`.
5. No event names both `X4` and `Y23`.
6. Neither endpoint frame returns to its initial frame.

Therefore the published channel hosts the basis head on the matched target only
at the terminal transport after-frame, 2,989 events after the source drop. It
never co-hosts that head on a live source frame and the matched target at the
same chronological cut. Logical dirty restoration of the source singleton line
into `Y23` along co-hosted basis-head geometry is unavailable on this word.

## Checking method

Two independent scanners read the same pinned inputs. The primary scanner walks
annotated frames in program order. The second accumulates frozensets per
register. Both reject duplicate JSON keys, enforce source SHA-256 pins, and
admit through `need()` under `python -O`. Their receipts are byte-compared to
the committed certificate.

## Soft overlap

Open #3363/#3365/#3371/#3372 record algebraic coefficient delivery for the
channel/relay/Gram/tail path and concentrate worked examples on flag 0. Open
#3392 proves the complementary absent-head obstruction on flag 2. Open #3349
counts the present-head class but does not pin late-only hosting on flag 9.
This package does not recompute those coefficient identities or re-audit flag 2.

## Limits

This is a statement about the published annotated frames of one matched flag.
It does not price a repair, construct a changed schedule, or claim a new κ.
A schedule that co-hosts `196` on `X4` and `Y23` before the source drop is
outside this certificate.
