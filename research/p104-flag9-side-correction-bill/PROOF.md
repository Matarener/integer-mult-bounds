# Proof notes: flag-9 end-cut side-correction bill

## Setup

Let `G` be the P104 Gram matrix of the 104 ports. Flag 9 matches source `X4`
to target `Y23` with basis head `196` (#2981; identity checked against the
pinned joint-unit-flags certificate). The published native word has 4,058
events. `Y23`'s terminal transport is event 3489:

```text
transport Y23  [447,127,192]  →  F23 = [467,27,196,12,124,3,7,1]   rank 5
```

`G[23,4] = −1`, so the `(23,4)` entry of `I − G/2` is `+1/2`. The channel
leaves `Y23` with coefficient `−1/2` on `X4`; applying the entry zeros that
coefficient. `Y23` is never read as a source, so only that row changes.

## Corrections

Each word replaces event 3489.

- **T.** `Y23: A3 → FULL` (rank 6), `Y23 += (1/2) X4` in FULL, `Y23: FULL → F23`
  (rank 1). Added rank mass `(6 + 1) − 5 = 2`.
- **S.** Keep the published transport; `X4: FULL → F23` (rank 1), ADD in F23,
  `X4: F23 → FULL` (rank 1). Added rank mass `2`. `X4`'s next read is at
  event 3695 in FULL, so the detour restores before that read.
- **P.** Keep the published transport; open one private lifetime on `C` at
  FULL, copy `X4`, descend `C` to F23, ADD, erase. Added rank mass `1` on `C`.
- **T48.** Same lift as T, but every off-diagonal nonzero `−G[23,s]/2` is
  added in FULL (48 ADDs). Added rank mass `2`; final `Y23` row is
  `y23 + x23`.

## Native validation

For each word, set every newly inserted ADD coefficient to `0` and run the
published `check_native.validate()` with the published recipe set plus the
three committed new-edge recipes (`A3 → FULL`, `FULL → F23`, `F23 → FULL`).
Chart legality, endpoint adapters and framed-row checks do not depend on the
coefficient. Each coefficient-0 word passes. Each real word fails only at
`full physical boundary endpoint Y23`. Exact rational replay confirms the
row change stated above.

## Obstruction

Work in the class that keeps published events and ADD coefficients, keeps
every endpoint frame, may retarget or insert transports, and keeps `C`'s
published private lifetimes `(2461, 2524)`.

**Leave.** Replay ADDs under least monotone frames (private `C` unconstrained).
At event 745 (`add G7 X4 −2`), `X4`'s frame first leaves `F23`. The outside
head of `X`-singleton origin with `G[23, ·] = 0` is `333` from `X58`, carried
along

```text
631: G7 ← X58,  729: G16 ← X58,  731: G16 ← X35,  745: G7 ← X4.
```

**Classes.** The 25 insertion classes are the cut-points immediately after
every ADD/copy that touches `X4` or `Y23`, plus the start of the word. A
least-frame sweep that forces `X4` and `Y23` to share a frame at each class
obstructs all 25. From class 746 onward the obstruction is immediate at
`Y23` (merged frame already contains `333`).

**Parity.** Endpoint-restoring non-private nested transports contribute even
rank mass. Hence the strict non-private minimum is exactly 2. T, S and T48
attain it.

**Private.** Forcing `Y23` to host head `196` at each of the 7 early delivery
cuts before `C`'s published span is obstructed. Under the inherited
private-copy contract, +1 is therefore the minimum for one added lifetime.

## Consistency with #3614

Open #3614 reports the same primary feeder `X58:333` at leave 745 and the
same 25/25 zero-mass obstruction for entry `(23,4)` on the published word.
This package recomputes those facts from the pinned witness/Gram and does not
import #3614's certificate. It does not reopen the deferred flag-9 head-step
repair.

## Limits

- No co-hosted discount is claimed; the deferred repair is leave-alone.
- P's admissibility as a physical correction is open.
- Only the primary flag-9 entry is priced; full-row (~48) census is #3614 OQ1.
- Selected κ is unchanged: `0.001672660197076918`.
