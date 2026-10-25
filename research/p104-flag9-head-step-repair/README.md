# Flag 9's delivering update can be co-hosted for exactly two added rank units

**Finite repaired words with an exact bill, plus a sharp order-preserving floor. No new exponent.**

Open [#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443) shows that
on the published 4,058-event P104 word, present-head flag 9 (`X4` → `Y23`,
basis head `196`) never updates `Y23` while both endpoints list the head. Its
open question asks what a changed schedule that co-hosts the head would cost.
The same question is open for this flag in
[#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) and was released
without a submission. Flag 1's repair is the separate open
[#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532); this package
does not recompute it. Flag 43's zero-mass repair is the method being followed,
not the result: flag 9 has no zero-mass order-preserving repair.

## Result

The published source "drop" at event 500 does not remove `196` from the span.
The after-list is `[8, 64, 132, 260]` and `64 XOR 132 = 196`. All 7 source
frames and all 21 events that name `X4` span `196`. The obstruction is on
`Y23` only.

The only `Y23` update that carries `X4` is event 3124, `Y23 += D28/4`. It
delivers `-1/2` and settles `Y23`'s final `X4` coefficient. Two repaired words
make that ADD co-host `196` while `X4` is in its rank-9 chart and still has
five later reads. The published `check_native.validate()` passes on both.

- **R0 (order-preserving).** `D28` and `Y23` enter the published 3124 chart
  plus `196`. The ADD runs there. One inserted transport drops `D28` back
  before `Y28` reads it. `Y23` keeps the head until its terminal transport.
  Added rank mass is `+2`, all of it on `D28`.
- **R1 (relocation).** The delivering ADD moves into `D28`'s full-chart window
  just after event 3634. `Y23` lifts from `[447, 127]` to the full chart, takes
  the ADD, and drops to its final frame. No event is added or removed. Added
  rank mass is `+2`, all of it on `Y23`.

| Bill term | Published | R0 | R1 |
|---|---:|---:|---:|
| Events | 4,058 | 4,059 | 4,058 |
| Scalar ADDs | 2,624 | 2,624 | 2,624 |
| Transport occurrences | 1,410 | 1,411 | 1,410 |
| Rank mass | 2,368 | 2,370 | 2,370 |
| Distinct native edges | 740 | 742 | 741 |
| Where the +2 sits | — | `D28` | `Y23` |
| Paid profile delta | — | `-H1 + 2H2 + H4 - H5` | `H7 - H5` |

Under an affine price `H(r) = a + b r`, R0 costs `a + 2b` and R1 costs `2b`.
Under `H(r) = r^2`, R0 costs `-2` and R1 costs `+24`. R1 is cheaper when each
event has a positive price. R0 can be cheaper for a steep convex rank price.

In the order-preserving class (published events kept in order, endpoint frames
kept, nested rank-gap transports, insertions allowed), added rank mass is even,
and zero is impossible: keeping `196` on `D28` through event 3126 forces it
into `Y28`, whose final frame excludes it, and dropping it before 3126 costs
2 on `D28`. R0 meets the floor. The same closure obstructs all nine `Y23`
updates. Reordering those reads is not ruled out and is not given a zero-mass
schedule here.

Selected κ stays `0.001672660197076918`. The argument is in [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -I -B research/p104-flag9-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/independent.py
python3.12 -I -O -Werror -B research/p104-flag9-head-step-repair/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag9-head-step-repair
```

`verify.py` is read-only. It loads the pinned `check_native.py` by path and runs
its `validate()` on each repaired word built in memory. Admission goes through
`need()` and still fires under `-O`. `independent.py` imports neither `verify.py`
nor the native checker. `test_package.py` corrupts temporary copies and checks
that both scanners reject all 10 mutations, including deletion of R0's return
transport and an undercharged terminal rank. `build.py` is the producer and is
not part of the replay.

## Credit

Credit #3443 for flag 9's published literal chronology, #3451 for the span
reading on flag 1, and #3508 for the head-step repair method and the class-P
closure rule. Credit #3349 for the present-head census. Credit Nick Petalas /
#2981 for the flag matching, and the reviewed #1991 native channel (Chafik
Boukhalfa) for the witness, checker and compiler. #3532 is the flag-1 repair
this package deliberately does not repeat; its open question 3 asks for this
flag. Prepared by unpaidmoon with substantial Cursor Grok assistance. No
independent human or formal-kernel review is claimed. Apache-2.0.

## Open next questions

1. Is there a zero-added-mass co-hosting repair that reorders `D28`'s reads?
   Every partner whose final frame excludes `196` would have to read `D28`
   before `196` enters, and `196` would then have to stay on `D28`'s monotone
   path to the full chart. R1 still pays `+2`, so the exhibited relocation is
   not that schedule.
2. Can a side correction use R0's chart `[447, 127, 192, 196]` at the repaired
   index 3124, or R1's full chart at 3633, to restore `X4` into `Y23`, and what
   does the `I - G/2` correction cost at that cut?
3. Which of R0 and R1 is cheaper under the channel's actual per-rank weights?
   Affine prices prefer R1; `H(r) = r^2` prefers R0.
