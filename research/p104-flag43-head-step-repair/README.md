# Flag 43's basis head can be co-hosted at its delivering target update at zero added channel cost

**Finite repaired word with an exact bill, plus a forced-closure obstruction. No new exponent.**

Open [#3456](https://github.com/CrocSwap/integer-mult-bounds/pull/3456) shows that
on the published 4,058-event P104 word, present-head flag 43 (`X21` → `Y59`,
basis head `15`) never updates `Y59` while both endpoints host the head. Its first
open question asks what a changed schedule that fixes this would cost. The
matching questions in [#3451](https://github.com/CrocSwap/integer-mult-bounds/pull/3451)
(flag 1) and [#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443)
(flag 9) are open for the same reason. This package answers it for flag 43 and
cites those chronologies without re-deriving them.

## Result

**Repair R0** keeps every published event in its published order, with the same
ADD registers and coefficients. It changes only the frames of nine existing
transports and the chart fields of three ADDs. From the forced event on, each
changed register's frame is its published frame plus `15`:

| Register | Retargeted transports | Published ranks | Repaired ranks |
|---|---|---|---|
| `Y59` | 3363, 3525 | 1, 3 | 2, 2 |
| `D17` | 3362, 3612 | 1, 4 | 2, 3 |
| `Y103` | 3365, 3461, 3569 | 1, 1, 2 | 2, 1, 1 |
| `D28` | 3460, 3634 | 1, 3 | 2, 2 |

The published native checker `check_native.validate()` passes unchanged on the
repaired word. That covers every native edge (eight swapped for eight newly
lowered edges, still 740), all 208 endpoint adapters, and all 280 framed rows,
including the restoration of the 72 dirty helpers.

In R0, `Y59`'s last update (event 3364, `Y59 += D17/4`) runs in the rank-6 chart
`[95, 447, 6, 32, 20, 15]`. At that moment `X21` is in the rank-9 full chart and
has four later reads. That ADD carries `X21` coefficient `1/2` and settles
`Y59`'s final `X21` coefficient. The earlier `+1/2` at 3076 is cancelled at
3231. So the update that delivers the matched source now runs in a chart that
co-hosts the basis head.

| Bill term | Published | R0 | R1 (comparison) |
|---|---:|---:|---:|
| Events | 4,058 | 4,058 | 4,059 |
| Scalar ADDs | 2,624 | 2,624 | 2,624 |
| Transport occurrences | 1,410 | 1,410 | 1,411 |
| Rank mass | 2,368 | 2,368 | 2,368 |
| Distinct native edges | 740 | 740 | 742 |
| Paid profile delta | — | `-3H1 + 5H2 - H3 - H4` | `+2H2 - H4` |

R0 adds nothing to any counted bill term. Its only change is the rank profile:
the nine changed ranks `{4,3,3,2,1,1,1,1,1}` become `{3,2,2,2,2,2,2,1,1}`. The
published multiset majorizes the repaired one, so for every convex per-rank price
`H` the delta `5H2 - 3H1 - H3 - H4` is at most zero. It is exactly zero for every
affine price, and positive only for a strictly concave one.

**Comparison R1** touches only `Y59` and `D17`. It moves `Y103`'s transport and
update (3365–3366) ahead of `Y59`'s and gives `D17` one added rank-1 lift. This
costs one event and one transport occurrence, with rank mass unchanged. R1 is
also natively validated.

## Obstruction

Consider the class of repairs that:

- keep the published event order and ADDs,
- keep the endpoint frames,
- add no rank mass.

All 280 non-private registers already sit at their rank floor, so in this class
every such path stays monotone. Inserting refinement transports is allowed. Within
this class, only event 3364 among `Y59`'s 15 updates can be made head-hosting.

- Each of the other 14 forces the head into a register whose final frame excludes
  it. The first such register is `Y67`, `Y96`, `Y26`, `Y56` or `Y22`, depending
  on the update. At 3231 the single obstruction is `Y56` at event 3348.
- At 3364 the forced must-change set is exactly `Y59` and `D17` (from 3364),
  `Y103` (from 3366) and `D28` (from 3462).

If no events are inserted, all nine transports R0 retargets are forced to change.
R0 therefore uses the minimum number of changed transports and registers in that
class.

Selected κ stays `0.001672660197076918`. Proof details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag43-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag43-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag43-head-step-repair/independent.py
python3.12 -I -O -Werror -B research/p104-flag43-head-step-repair/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag43-head-step-repair
```

`verify.py` is read-only. It loads the pinned `check_native.py` by path and runs
its `validate()` on each repaired word built in memory. Admission goes through
`need()` and still fires under `-O`. `independent.py` imports neither `verify.py`
nor the native checker. `test_package.py` corrupts temporary copies and checks
that both scanners reject every corruption. It also checks that three truncated
cascades (target only; without `Y103`; without `D28`) fail at the common-chart
rule. `build.py` is the producer and is not part of the replay.

## Credit

Credit #3456 for flag 43's published chronology and the `D17` common-chart first
step, which this package follows. Credit #3451 and #3443 for the flag-1 and
flag-9 present-head obstructions, and #3349 for the present-head census. Credit
Nick Petalas / #2981 for the flag matching, the reviewed #1991 native channel
(Chafik Boukhalfa) for the witness, checker and compiler, and #3363 for the relay
census whose coefficient convention is reused. Prepared by Wentao Li with
substantial AI assistance.

## Open next questions

1. Do flags 1 and 9 admit the same event-preserving head-step repair, or is their
   forced closure obstructed? Answer this in a separate package that cites #3451
   and #3443.
2. Can a side correction use R0's co-hosted head chart at 3364 to restore
   `X21`'s contribution to `Y59` dirtily, and what does the `I - G/2` correction
   cost at that cut?
3. Is R0's profile majorization-minimal among event-preserving monotone repairs?

[TASK.json](TASK.json) gives first steps and blockers.
