# Flag 1's `I − G/2` entry rides free on #3532's relocated co-host, but costs +2 at its order-preserving one

**Exact bill plus a sharp obstruction. No new exponent.**

Open [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532) gives
two repairs of the published P104 word that co-host flag 1's basis head `232`
at `Y7`'s delivering update (`Y7 += D17/4`, published event 2797):

- R0 keeps the published order and runs the ADD in `A3 = [95,486,232]`;
- R1 relocates it into `D17`'s full-chart window (new index 3611).

Each costs +2 rank mass. #3532 leaves the `I − G/2` side correction open. Open
[#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601) priced flag
43's entry at #3508's co-hosted cut and found a co-host discount of 0. This
package prices flag 1's entry at both of #3532's co-hosted charts. It cites
#3532, #3601 and [#3451](https://github.com/CrocSwap/integer-mult-bounds/pull/3451)
without re-deriving R0, R1 or the published chronology. #3532's two input files
are vendored byte-identically from its head (see [PROOF.md](PROOF.md)).

## The entry

Flag 1's entry is `(t, s) = (7, 0)`. `G[7,0] = <r7, r0> = −1`, so the channel
leaves `X0` in `Y7` with coefficient `−1/2`, all of it delivered at 2797. The
`I − G/2` entry is `+1/2` (the opposite sign from flag 43's `−1/2`). Applying it
leaves `Y7` with `X0` coefficient `0`. `Y7` is never read, so no other row
changes.

## Result

| Word | Base | Correction | Δ events | Δ ADDs | Δ transports | Δ rank vs base | Δ rank vs published |
|---|---|---|---:|---:|---:|---:|---:|
| **E** | R1 | one ADD `Y7 += X0/2` in FULL right after the relocated delivering ADD | +1 | +1 | 0 | **0** | **+2** |
| **Erow** | R1 | E carrying all 48 off-diagonal entries `−G[7,s]/2` of row 7 | +48 | +48 | 0 | **0** | +2 |
| **T** | R0 | `Y7: A3→FULL`, ADD in FULL, `Y7: FULL→F7` | +2 | +1 | +1 | **+2** | +4 |
| **S** | R0 | R0's transport, then `X0: FULL→F7`, ADD, `X0: F7→FULL` | +3 | +1 | +2 | **+2** | +4 |
| **P** | R0 | one private lifetime: zero `C`, copy `X0`, `C: FULL→F7`, ADD, erase | +5 | +1 | +1 | +1 | +3 |
| **Trow** | R0 | T carrying all 48 row-7 entries | +49 | +48 | +1 | +2 | +4 |
| **Tend** | published | end-cut control: `Y7: A2→FULL`, ADD, `Y7: FULL→F7` | +2 | +1 | +1 | +2 | +2 |

Here `F7` is `Y7`'s final rank-8 frame. In R1, `Y7` is already in FULL at the
relocated delivering ADD, and so is `X0`, so E needs no transport. In R0, `Y7`
sits in the rank-3 chart `A3` until its terminal transport, which is where T, S
and P act.

The published `check_native.validate()` runs unchanged on all seven words with
the inserted coefficients set to `0`. It passes every native edge, including
three newly lowered recipes (`A3→FULL`, `A2→FULL`, `F7→FULL`), all 208 endpoint
adapters, all 280 framed rows and the restoration of the 72 dirty helpers. On
each real word the same checker fails only at
`full physical boundary endpoint Y7`. Exact rational replay confirms that `Y7`
is the only row that changes:

- in E, T, S, P and Tend it changes by exactly `+1/2 X0`;
- in Erow and Trow, `Y7`'s final row becomes exactly `y7 + x7`, the identity row.

**Co-host discount.** On the published word, the end-cut correction Tend
costs +2.

- At R0's chart `A3` the correction also costs +2, so the discount is **0**,
  as for flag 43.
- At R1's full chart it costs 0, so the discount is **2**.

## Obstruction

**Forcing chain.** Event 1074 is `G18 −= 2·X0`. By then the head `387` of `X7`,
the target's own source, has reached `G18` along the time-ordered chain
`X7 –616– G11 –679– X20 –1070– G18`. In any repair where those registers add no
rank, `X0`'s frame contains `387` from event 1074 on. From event 1690 it is the
full chart. Since `G[7,7] = 2` is even, `387` is outside `F7`. Of the 56 source
heads outside `F7`, `X7`'s is the only one that reaches `X0` by 1074.

**Strict correction.** Take the class that:

- keeps every published ADD;
- lets the delivering ADD sit anywhere in its 1,116-slot window;
- inserts one correction ADD between `X0` and `Y7`;
- moves transports freely;
- keeps every endpoint frame and `C`'s published events.

No member of this class has zero added rank mass. A least-frame sweep with the
delivering ADD dropped checks 18 insertion classes. Dropping the ADD only
removes constraints, so the sweep covers every placement of it.

- For the 4 classes up to event 841, the meeting puts `232` into `Y7` early.
  `Y7`'s own updates then push it into `Y8`, at event 22, 23 or 2014.
- For the 14 classes from 1075 on, the merged frame contains `387` and leaves
  `F7` at once.

Each register's added mass is even, so the strict minimum is exactly **2**.
Tend and R1+E attain it.

**Joint co-hosting and correction.**

- **With relocation:** the joint minimum is **2**, attained by R1+E. It cannot
  be lower, because the correction alone already costs 2.
- **Order-preserving:** if the delivering ADD stays at 2797 and co-hosts, the
  joint non-private minimum is **4**, attained by R0+T and R0+S. A joint +2
  would leave exactly one register non-monotone. The census rules that out:
  - letting any single one of the 280 non-private registers move freely still
    blocks co-hosting, except for `D17`;
  - with `D17` free, all 19 correction classes stay blocked.

So for flag 1, co-hosting and correcting can share one +2 excursion, but only
when the delivering ADD is relocated (`Y7`'s lift to FULL pays for both).
Order-preserving co-hosting cannot share it.

**Private route.** P relies on the inherited private-copy contract, under which
`C` is discarded while still holding a copy. Under that contract, the cheapest
added private lifetime costs exactly 1. Copies taken after event 1074 carry
`387`. Copies taken earlier must be delivered before `C`'s published lifetimes
start at 2461, and all 5 such delivery classes are blocked at `Y8`.

Selected κ stays `0.001672660197076918`. Details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag1-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag1-side-correction-bill/independent.py
python3.12 -I -O -Werror -B research/p104-flag1-side-correction-bill/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag1-side-correction-bill
```

`verify.py` is read-only. It loads the pinned `check_native.py` by path, and
its admission checks go through `need()`, so they still fire under `-O`. It
takes about one minute. `independent.py` imports neither `verify.py` nor the
native checker. `test_package.py` corrupts temporary copies and checks that
both scanners reject all 18 corruptions. `build.py` is the producer and is not
part of the replay.

## Credit

Credit #3532 for R0, R1 and the delivering-update window (vendored inputs,
cited only), #3451 for flag 1's chronology, and #3601 and #3508 for the
side-correction bill format, class Z and the least-frame sweep reused here.
Credit `research/p104-side-correction-rank-obstruction` for the end-cut
invoices. Credit Nick Petalas / #2981 for the flag matching. Credit the reviewed
#1991 native channel (Chafik Boukhalfa) for the witness, checker and compiler,
and Rohan Arun / PR1972 for the scalar channel. Prepared by Wentao Li with
substantial AI assistance.

## Open next questions

1. Is there a co-hosted and corrected word for flag 1 with joint added mass 1?
   It would need a zero-mass late relocation (#3532's open question 1) plus a
   private route like P, so it is open exactly when that question is.
2. Does every other row with a present-head flag need +2 for its correction?
   Flag 43 and flag 1 both do, each through a different forced head. Running
   this sweep over all `(t, s)` with `G[t,s] ≠ 0` would decide whether strict
   per-target corrections cost 208 in total.
3. Which repair is cheaper under the repo's actual per-rank weights: R1+E
   (profile `H8 − H6`) or the uncorrected R0 (profile `−H1 + 2H2 + H5 − H6`)?
   With relocation the correction adds no rank, so it is now part of that
   comparison.

[TASK.json](TASK.json) gives first steps and blockers.
