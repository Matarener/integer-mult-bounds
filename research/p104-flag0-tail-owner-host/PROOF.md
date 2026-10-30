# Proof: self-owned flag-0 tail host schedule without endpoint repayment

## Claim

On the published #2089 augmented witness, events 5758/5759/5807 form a
promote/add/restore triple for target `Y34` with source read `X0` at
coefficient `-1/2`. Schedule S0 assigns owner `X0` on host chart `FULL`. This
schedule is legal for the published ADD, uniquely determined among registers
named by that ADD, touches no dirty helper in the window, and leaves both
endpoint frames at their unrestored channel finals. Restoring `X0` to its
initial frame before the ADD conflicts with the published common-chart
annotation. No new κ.

## Inputs

Pinned at CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`:

- `research/p104-native-channel/inputs/LOWRANK-WITNESS.json` (#1991 channel)
- `research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz` (#2089)
- `research/p104-tail-side-correction-seed749717/CORRECTION-ROWS.json`
- `research/p104-tail-flag0-owner/RESULT.json` (prior: no owner field)
- `research/p104-channel-touch-restoration-audit/CERTIFICATE.json` (#3349)

Hashes are in [SOURCES.json](SOURCES.json).

## Setup

Write `FULL = [1,2,4,8,16,32,64,128,256]` and
`RANK8 = [499,23,232,32,112,15,7,2]`. The channel leaves `X0` at `FULL` and
`Y34` at `RANK8`. Neither equals its initial (`[232]` and `[]`). #3349 records
that this unrestored pattern holds for every endpoint; this package cites that
census and rechecks only the flag-0 pair.

The tail word's first 4,058 events equal the channel program. Event 5758 is
`transport Y34: RANK8 → FULL` (rank 1). Event 5759 is
`add Y34 X0 -1/2 FULL`. Event 5807 is `transport Y34: FULL → RANK8` (rank 1).
Between them sit exactly 48 `Y34` adds.

## Schedule S0

Assign:

- `owner(5759) = X0`
- `host_chart(5759) = FULL`
- no additional host register

**Legality.** A forward frame walk from the tail initials reaches `X0 = FULL`
and `Y34 = FULL` at event 5759, matching the ADD's chart field. The common-chart
rule holds.

**Uniqueness on the published word.** The ADD names exactly `{Y34, X0}`. The
write target cannot own the source read. The only remaining named register is
`X0`. So among event-named registers, S0 is the unique owner assignment. (A
copied host using an unnamed helper would be a different word; see open
questions.)

**Dirt.** Scan events 5758 through 5807. No top-level field is a dirty helper
name (`D*`, `G*`, `Q*`, or `C`). The channel's dirty-helper restorations are
therefore undisturbed by this window. Arbitrary dirt that the channel already
restored stays restored; S0 introduces no new dirty host.

**Endpoint repayment.** After event 5807 the walk gives `X0 = FULL` and
`Y34 = RANK8`. These equal the channel finals and differ from the initials.
Define repayment as a transport that returns an endpoint to its initial frame.
Neither endpoint is so returned. The promote/restore pair is a temporary lift
of `Y34` that ends at the channel final, not at `[]`.

**Coefficient.** `CORRECTION-ROWS.json` row 34, source 0, stores coefficient
`-1/2`, matching the ADD.

## Obstruction: pre-read X0 restoration

Suppose one restores `X0` to `[232]` before event 5759 while keeping the
published ADD, whose chart annotation is `FULL`. Then the live `X0` frame is
not `FULL`, so the common-chart rule fails. Hence any schedule that repays
`X0`'s unrestored endpoint before the read is incompatible with the published
word. (Repayment after 5807 is outside this certificate and would cost
positive descent rank from `FULL` toward `[232]`.)

## What this does not prove

- A global owner/host map for all 4,992 source reads
- A copied-host construction or its rank-mass floor
- Integration with the #1940 chronological schedule
- A supplier admission or a new κ
- Anything about the deferred #3669 OQ1 +2 head-span repair at event 3369

## Independence

`verify.py` walks frames in program order. `independent.py` builds per-register
indexes and reconstructs frames from transport subsequences alone. Neither
imports the other or the native checker. Both compare against
[CERTIFICATE.json](CERTIFICATE.json). Temp-copy corruptions of that certificate
and of the gzipped witness are rejected under `-O`.
