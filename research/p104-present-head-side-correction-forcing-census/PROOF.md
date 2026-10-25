# Proof sketch — present-head side-correction forcing census

## Setup

Let `W` be the published native-channel program pinned by
`research/p104-native-channel/inputs/LOWRANK-WITNESS.json` (4058 events).
Let `G` be the P104 Gram matrix rebuilt from the pinned fixture by the
standard E8-line enumeration. Present-head flags are those whose basis
head lies in the matched target final; the published hit set is
`{0,1,9,43}`. This census takes `{1,9,43}` (flag 0 remains with the
coefficient cascade) and, for each flag target `t`, checks the primary
flag source together with five further indices `s ≠ t` with `G[t,s] ≠ 0`.

An `I−G/2` side-correction entry at `(t,s)` asks for a common-chart ADD
that moves coefficient `−G[t,s]/2` from `Xs` into `Yt`. A **zero-mass
placement** at cut `u` is a least-frame merge of the live frames of `Xs`
and `Yt` at time `u`, followed by ordinary common-chart ADD closure for
the rest of `W`, with no added transports.

## Obstruction (class Z)

For each checked entry and each insertion class `u` (the cut `0` together
with every time after an `add`/`copy` that touches `Xs` or `Yt`), the
forward sweep returns a first register whose forced frame is not contained
in that register's endpoint frame. In all 18×(class count) cases the
sweep returns a nonempty obstruction. Therefore no checked entry admits a
zero-mass common-chart placement on the published word.

## Forcing heads

Independently of the insertion sweep, replay ADD closure on `W` and let
`τ` be the first event at which the live frame of `Xs` is not contained
in the final frame of `Yt`. At time `τ` at least one initial X-head `h`
lies in `Xs` and outside the target final. The census records a carrier
path of ADDs taking `h` from its birth register into `Xs` by time `τ`.

Primary feeders:

- Flag 1 `(7,0)`: `τ = 1074`, feeder `X7` head `387` (Gram `G[7,7] = 2`).
- Flag 9 `(23,4)`: `τ = 745`, feeder `X58` head `333` (Gram `G[23,58] = 0`).
- Flag 43 `(59,21)`: `τ = 884`, feeder `X12` head `131` (Gram `G[59,12] = 0`).

These match the leave-alone samples of open #3610 and #3601 for flags 1
and 43; flag 9 is new on the published chronology.

## Parity floor

Any endpoint-restoring non-private correction that temporarily lifts a
register into a common parent chart and returns it must pay nested
transport rank on the way up and on the way down. That contribution is
even. Combined with the zero-mass obstruction, every checked entry has
strict non-private side-correction floor `+2`.

Private-copy (`+1`) paths and co-hosted repair discounts are out of
scope; #3610 already shows an R1 free-ride for flag 1, which does not
refute the published-word strict floor.

## Theorem

All 18 checked present-head strict entries need `+2`. No counterexample
entry was found. Selected κ is unchanged.
