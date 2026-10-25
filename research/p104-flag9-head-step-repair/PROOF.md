# Proof: flag-9 head-step repair, its bill, and the order-preserving floor

## Setup

Pin CrocSwap main `bb4bccbf42844d2801487450727c2f63e10d1d0f`. Inputs:

- The #2981 flag matching (`research/p104-joint-unit-flags/CERTIFICATE.json`).
  Flag 9 has source 4, target 23 and basis head `196`.
- The reviewed #1991 witness, recipes and checker in `research/p104-native-channel/`.

All of these are hash-pinned. The channel semantics are those of
`research/p104-native-channel/PROOF.md` §2–§3: a transport changes only the
frame and pays the absolute dimension gap; an ADD is allowed only in a common
frame and changes only the destination row.

#3443 records that the published word lists `196` on `Y23` only in the
after-frame of the terminal transport at event 3489, and that the generator
list of `X4` drops `196` at event 500. This note does not rerun that literal
census. It uses span membership, which is the chart-independent reading.

## 1. The source drop is a chart change

Event 500 transports `X4` from `[196]` to `[8, 64, 132, 260]`. The after-list
does not contain `196`, but

```text
64 XOR 132 = 196.
```

So `196` stays in the span. Direct inspection of all 7 source frames (the
initial frame and six transports) and of the live frame at all 21 events that
name `X4` finds `196` in every one. From event 1326 on, that frame is the
rank-9 full chart. The present-head obstruction on this flag is entirely on
the target side. This is the same phenomenon #3451 found for flag 1, which
#3443's generator-only wording does not record.

`Y23` does not span `196` at any of its nine ADDs. Its final frame does.
`Y28`'s final frame does not.

## 2. The delivering update

The only ADD into `Y23` that carries a nonzero `X4` coefficient is event 3124,

```text
Y23 += D28/4    in the chart [447, 127, 192].
```

`D28`'s row contributes `-1/2`, and that ADD leaves `Y23`'s `X4` coefficient
at its final value `-1/2`. No earlier `Y23` ADD carries `X4`. The next event
that names `D28` is 3126, `Y28 += D28/4`, in the same chart. Event 3125 does
not name `D28`.

## 3. Repair R0

Let `CH3 = [447, 127, 192]` and `CH4 = CH3 + [196]`. Rank(`CH3`) is 3 and
rank(`CH4`) is 4. `CH4` is contained in `Y23`'s final frame. R0 keeps every
published event in order, with the same ADD registers and coefficients, and
inserts one transport:

| Published index | Published | R0 |
|---|---|---|
| 3122 | `D28: [447, 192] -> CH3`, rank 1 | `D28: [447, 192] -> CH4`, rank 2 |
| 3123 | `Y23: [447, 127] -> CH3`, rank 1 | `Y23: [447, 127] -> CH4`, rank 2 |
| 3124 | `Y23 += D28/4` in `CH3` | same ADD in `CH4`, then `D28: CH4 -> CH3`, rank 1 |
| 3489 | `Y23: CH3 -> final`, rank 5 | `Y23: CH4 -> final`, rank 4 |

Every changed transport is nested, and its rank equals the frame gap. `Y23`
has no event between 3124 and 3489, so it stays in `CH4` until the terminal
transport. `D28` is back in `CH3` before event 3126, so `Y28`, `Y29`, `Y22`,
`Y31` and `Y103` keep their published charts.

`verify.py` builds this word in memory and calls the published
`check_native.validate()` unchanged. That checks every native edge (two
published edges drop out and four new ones enter; 742 distinct edges), all
208 endpoint adapters, and all 280 framed rows, including restoration of the
72 dirty helpers. `independent.py` replays both words with exact rational rows
and finds all 280 final rows equal to the published rows. In R0 the ADD at
index 3124 runs in `CH4` while `X4` is in the full chart, and `X4` still has
reads at repaired indices 3696, 3803, 3855, 3959 and 4010.

Per-register rank mass changes only on `D28`, by `+2` (the extra rank on the
way into `CH4`, and the rank-1 drop back). `Y23`'s entry grows by 1 and its
terminal transport shrinks by 1. The paid-profile delta is

```text
-H1 + 2 H2 + H4 - H5.
```

For an affine price `H(r) = a + b r` this is `a + 2b`: one added transport
occurrence and two added rank units. For `H(r) = r^2` the same delta is `-2`.
The sign is not uniform across convex prices.

## 4. Repair R1

R1 deletes the published events 3123, 3124 and 3489 and, immediately after
`D28`'s lift to the full chart at 3634 and before `D28 += Q7`, inserts

```text
Y23: [447, 127] -> FULL, rank 7
Y23 += D28/4 in FULL
Y23: FULL -> final, rank 1
```

`D28` is not written between 3124 and 3635, so the same coefficient still
delivers `-1/2`. Nothing reads `Y23`, so moving that single ADD does not
change any other row. Event count, ADD count and transport count stay at the
published values. Rank mass grows by 2, all of it on `Y23`. The profile delta
is `H7 - H5`, which is `2b` for every affine price and `+24` for `H(r) = r^2`.
The published checker passes, with 741 distinct native edges. The co-hosted
ADD is at repaired index 3633, and `X4` still has its five later reads.

R1 is not order-preserving: it moves the delivering ADD. It matches R0's rank
mass and removes R0's extra event. Under a positive per-event price it is the
cheaper of the two exhibited repairs. Under a steep convex rank price, R0's
profile can cost less.

## 5. Order-preserving floor

**Class P.** A repair is in class P when:

1. every published event is kept, in published order, with the same opcode,
   registers and ADD coefficient (transport frames may change, ADD chart
   fields may change, and transports may be inserted);
2. every initial and final frame is kept;
3. every transport rank equals the absolute dimension gap of a nested pair.

**Parity.** On one register the sum of absolute dimension gaps is congruent
modulo 2 to `rank(final) - rank(initial)`, because every descent has to be
matched by a later ascent. All 280 non-private registers of the published word
already meet that floor, so every class-P repair adds a nonnegative even
integer of rank mass on each of them. The total added rank mass is therefore
0 or at least 2.

**Zero is impossible for the delivering ADD.** Suppose a class-P repair adds
no rank mass. Then every non-private path is monotone: a vector that enters a
frame stays in every later frame of that register. The delivering ADD is still
`Y23 += D28/4`, still followed, after whatever transports are inserted, by the
published event 3126 `Y28 += D28/4`. Co-hosting requires `196` in `D28`'s
frame at the ADD.

- If some inserted transport removes `196` from `D28` before event 3126, that
  transport is a descent, so `D28`'s mass is at least 2 above its floor.
- If not, `D28` still spans `196` at event 3126, so the common chart forces
  `Y28` to span `196` there. `Y28`'s final frame does not span `196`, and a
  monotone path cannot drop it. So `Y28`'s mass is at least 2 above its floor.

Thus every class-P repair that co-hosts `196` on `X4` and `Y23` at the
delivering ADD adds at least 2 rank units. R0 adds exactly 2, so that floor
is sharp. R0's extra unit is the descent on `D28`; `Y23` pays nothing because
its final frame already contains `CH4`.

The same monotone closure, applied to all nine `Y23` ADDs on the published
word, finds no admissible update. Each forces the head into at least one
register whose final frame excludes it:

| Update | Partner | Final-excluding registers | First |
|---:|---|---:|---|
| 74 | `Q2` | 56 | `Y24` at 77 |
| 75 | `Q5` | 56 | `Y24` at 79 |
| 76 | `Q7` | 56 | `Y24` at 80 |
| 2070 | `D20` | 56 | `Y28` at 2071 |
| 2160 | `D10` | 56 | `Y28` at 2161 |
| 2296 | `D28` | 56 | `Y28` at 2297 |
| 2640 | `D20` | 23 | `Y28` at 2642 |
| 2826 | `D10` | 14 | `Y28` at 2828 |
| 3124 | `D28` | 5 | `Y28` at 3126 |

`verify.py` computes this closure with a worklist. `independent.py` recomputes
the final-excluding part with a forward sweep. The two agree on all nine rows.

## 6. What this does not say

Class P does not include repairs that reorder ADDs, change ADD coefficients,
or change a final frame. R1 shows one legal reordering and still pays `+2`.
It does not prove that every reordering pays `+2`. A zero-mass repair would
have to introduce `196` on `D28` only after every later partner whose final
frame excludes `196` has already read `D28`, and then keep `196` on the
monotone path to `D28`'s full final frame. No such schedule is constructed
or excluded here.

Neither repair is an `I - G/2` correction, a dirty-restoration program, or a
change to the selected conditional κ `0.001672660197076918`. The channel still
implements the published `G/2` map. The co-hosted chart only removes the
geometric obstruction recorded for this one flag.
