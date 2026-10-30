# Flag 1's basis head can be co-hosted at its delivering target update for exactly two added rank units

**Finite repaired words with an exact bill, plus a zero-mass obstruction. No new exponent.**

Open [#3451](https://github.com/CrocSwap/integer-mult-bounds/pull/3451) is the
published obstruction for present-head flag 1 (`X0` → `Y7`, basis head `232`).
Its first open question asks whether a changed schedule can put `232` into
`Y7`'s span by its last update while `X0` is still live, and at what cost. This
package answers that question. It cites #3451's chronology without re-deriving it,
and it follows the method of open
[#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) (the flag-43
repair). The answer differs from flag 43: flag 1 has no zero-cost repair.

## Result

Event 2797, `Y7 += D17/4`, is the only `Y7` update that carries `X0`. It brings
`-1/2` and settles `Y7`'s final `X0` coefficient. `D17`'s row is fixed from its
write at 2497 until its restoration at 3613, and `Y7` is never read. So this ADD
commutes freely within that window.

Two repaired words make 2797's ADD co-host the head while `X0` sits in its
rank-9 full chart with four later reads. The published `check_native.validate()`
passes unchanged on both. It covers every native edge, all 208 endpoint adapters
and all 280 framed rows, including the restoration of the 72 dirty helpers.

- **R0 (order-preserving).** `D17` and `Y7` enter `[95, 486, 232]`, the published
  2797 chart plus the head, at their last transports before 2797. The ADD runs
  there. One inserted transport then drops `D17` back to `[95, 486]` for its 12
  remaining reads, and `Y7`'s terminal transport starts from the rank-3 chart.
- **R1 (relocation).** `Y7`'s 2796 transport, the ADD and the 3473 transport move
  into `D17`'s full-chart window between 3612 and 3613. `Y7` lifts `[95]` to the
  full chart, takes the ADD there, then drops to its final frame. No event is
  added or removed.

| Bill term | Published | R0 | R1 |
|---|---:|---:|---:|
| Events | 4,058 | 4,059 | 4,058 |
| Scalar ADDs | 2,624 | 2,624 | 2,624 |
| Transport occurrences | 1,410 | 1,411 | 1,410 |
| Rank mass | 2,368 | 2,370 | 2,370 |
| Distinct native edges | 740 | 742 | 741 |
| Where the +2 sits | — | `D17` | `Y7` |
| Paid profile delta | — | `-H1 + 2H2 + H5 - H6` | `H8 - H6` |

Under an affine per-rank price `H(r) = a + b·r`, R0 costs `a + 2b` (one transport
plus two rank units) and R1 costs `2b`. The extra cost is positive for any
positive affine price. Under convex prices R1 stays at `H8 - H6 >= 0` for any
nondecreasing `H`. The sign of R0's delta is not fixed: `+2` at `H(r) = r` and
`-4` at `H(r) = r²`. Neither repair touches the private register `C`.

## Obstruction: zero added mass is blocked

All 280 non-private registers sit at their rank floor. With no added
non-private rank mass, every non-private path is therefore monotone. Over a
register's path, mass minus floor is always even. So any nonzero surcharge is at
least 2.

Two independent tests show that zero is impossible in the classes below.

- **Head closure (the #3508 rule).** All six `Y7` updates (19, 20, 2013, 2146,
  2526, 2797) force the head into a register whose final frame excludes it. For
  2797 there are 14 such registers, the first being `Y8` at 2799, `D17`'s next
  read. Flag 43 had one admissible update (3364); flag 1 has none.
- **Exact least-frame sweep.** For each class, a forward pass computes the
  least monotone frames forced by the common-chart rule plus the head. The
  private register `C` is fully relaxed, so every infeasible verdict is sound.
  - Order-preserving class: infeasible for all six updates.
  - Relocation class (the delivering ADD moved to any of its 1,115 legal slots
    between 2497 and 3613): infeasible at 868 slots. That is every slot before
    `Y103`'s read of `D17` at 3366, `D17`'s last rank-5 read; `Y103` is the last
    blocker.

Hence R0 is mass-optimal among order-preserving repairs: +2 is the parity floor
and R0 reaches it. In the 247 slots after 3366 the relaxed sweep is feasible, so
this package does **not** exclude a zero-mass relocation there. The natural
attempt fails. It intersects `D17`'s backward cone with `final(Y7)`, cascades
to 208 registers, and pushes 56 source initial frames outside the chart. That
window is open question 1.

Selected κ stays `0.001672660197076918`. Proof details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag1-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-head-step-repair/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-head-step-repair/independent.py
python3.12 -I -O -Werror -B research/p104-flag1-head-step-repair/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag1-head-step-repair
```

`verify.py` is read-only. It loads the pinned `check_native.py` by path and runs
its `validate()` on each repaired word built in memory. Admission goes through
`need()` and still fires under `-O`. `independent.py` imports neither `verify.py`
nor the native checker. It uses reduced-basis frames, its own rational replay,
its own head closure and a from-scratch least-frame replay per slot.
`test_package.py` corrupts temporary copies and checks that both scanners reject
all 17 corruptions. Two truncated R0 cascades must fail at the common-chart rule.
Two further controls cover an undercharged transport and R1 moved past `D17`'s
restoration, where the final rows break. `build.py` is the producer and is not
part of the replay.

## Credit

Credit #3451 for flag 1's published present-head chronology, and #3508 for the
head-step repair method, the class-Z closure rule and the bill format reused
here. Credit #3443 (flag 9) and #3349 (present-head census). Credit Nick
Petalas / #2981 for the flag matching, and the reviewed #1991 native channel
(Chafik Boukhalfa) for the witness, checker and compiler. #3363's relay census
records final coefficients; only the single `X0` entry delivered at 2797 is
re-reported here. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

1. Is there a zero-added-mass co-hosting repair with the delivering ADD after
   3366? The relaxed sweep allows it, but any construction must lower `D17`'s
   rank-4 and rank-5 charts (blocks at 3182–3188 and 3362–3366) inside
   `final(Y7)` without shrinking a source's initial frame or the private
   register's charts.
2. Which choice between R0 and R1, or between other +2 repairs, is cheaper under
   the repo's actual per-rank weights? R0 wins for steep convex `H`, R1 for
   affine `H`.
3. Does flag 9 (#3443) show the same blocked-at-zero, +2-at-floor pattern? Run
   this package's head closure and least-frame sweep on its target, keeping
   #3443's generator-only source-drop limit.

[TASK.json](TASK.json) gives first steps and blockers.
