# Flag 43's `I − G/2` entry costs +2 rank mass at the co-hosted cut; head co-hosting gives no discount

**Exact bill plus a sharp obstruction. No new exponent.**

[#3508](https://github.com/CrocSwap/integer-mult-bounds/pull/3508) (merged)
gives a repair R0 of the published P104 word. In R0, `Y59`'s last update, event
3364, runs in the head chart `W6 = [95,447,6,32,20,15]`. At that point `X21` is
in the full chart and still live. Its open question 2 asks what the `I − G/2`
side correction costs at that co-hosted cut. This package answers that question
for flag 43's entry and for the whole `Y59` row. It cites #3508 and
[#3456](https://github.com/CrocSwap/integer-mult-bounds/pull/3456) without
re-deriving R0 or the published chronology.

## The entry

`G[59,21] = <r59, r21> = 1`, and the channel leaves `X21` in `Y59` with
coefficient `1/2`. The corresponding entry of `I − G/2` is `−1/2`. Applying it
leaves `Y59` with `X21` coefficient `0`. `Y59` is never read, so the correction
changes no other row.

## Result

Every correction below replaces R0's terminal `Y59` transport at event 3525
(`W6 → F59`, rank 2). Here `F59` is `Y59`'s final rank-8 frame, which is the
hyperplane orthogonal to `Y59`'s root.

| Word | Correction | Δ events | Δ ADDs | Δ transports | Δ rank mass | Profile Δ vs R0 | Edges |
|---|---|---:|---:|---:|---:|---|---:|
| **T** | `Y59: W6→FULL`, `Y59 −= X21/2` in FULL, `Y59: FULL→F59` | +2 | +1 | +1 | **+2** | `H1 − H2 + H3` | 740 |
| **S** | R0's transport, then `X21: FULL→F59`, ADD in F59, `X21: F59→FULL` | +3 | +1 | +2 | **+2** | `2H1` | 742 |
| **P** | one private lifetime: zero `C` at FULL, copy `X21`, `C: FULL→F59`, ADD, erase | +5 | +1 | +1 | **+1** | `H1` | 741 |
| **T48** | T's lift, carrying all 48 off-diagonal entries `−G[59,s]/2` of row 59 | +49 | +48 | +1 | **+2** | `H1 − H2 + H3` | 740 |

All four corrections run while the head is co-hosted. Before each correction,
`Y59` is in `W6` and `X21` is in FULL, and both span `15`. Every correction
chart (FULL or `F59`) spans `15` as well.

The published `check_native.validate()` runs unchanged on each word with the
inserted coefficients set to `0`. It passes every native edge, including the two
newly lowered `FULL ↔ F59` recipes, all 208 endpoint adapters, all 280 framed
rows and the restoration of the 72 dirty helpers. Chart legality does not depend
on the coefficient. On the real word, the same checker fails only at
`full physical boundary endpoint Y59`. Exact rational replay confirms that
`Y59` is the only row that changes:

- in T, S and P it changes by exactly `−1/2 X21`;
- in T48, `Y59`'s final row becomes exactly `y59 + x59`, the identity row.

## Obstruction: no zero-mass placement exists

Consider the class Z of #3508:

- keep the published events and ADDs in order;
- keep every endpoint frame;
- retarget or insert transports freely;
- keep `C`'s published private lifetimes.

Insert one correction ADD between `X21` and `Y59` anywhere in this class. Its
added rank mass is never zero.

- **Forcing chain.** Event 625 is `G9 += 2·X12` and event 884 is `G9 −= 2·X21`.
  `X12`'s head is `131`. In any repair where the registers involved add no rank,
  `X21`'s frame contains `131` from event 884 on. From event 1708 it is the full
  chart.
- **Why that blocks the meeting.** `G[59,12] = 0`, so `131` lies outside `F59`.
  `Y59` adds no rank only if every frame it passes through lies inside `F59`.
  Two frames that differ cannot host one ADD.
- **Every insertion point.** A least-lower-bound frame sweep checks all 28
  insertion classes.
  - Before event 885, the meeting forces `Y59` to host `15` early. #3508's
    closure then fails at `Y67` or `Y96`.
  - From event 885 on, the merged frame already leaves `F59`.
- **Parity.** Each step changes rank by exactly its cost. So a non-private
  register's added mass is even. The strict minimum is therefore exactly
  **2**, and T, S and T48 attain it.

**Co-host discount 0.** On the published word, detouring `Y59`'s terminal
rank-3 transport through FULL costs 4 + 1 = 5, which is also +2. R0's head chart
makes T cheaper in transports than S, but not in rank mass.

**Private route.** P relies on the inherited private-copy contract, under which
`C` is discarded while still holding a copy. Under that contract +1 is the
minimum for one added lifetime that copies `X21`:

- if the copy is taken after event 884, it carries `131`, which `Y59` cannot
  host;
- if it is taken earlier, it must be delivered before `C`'s published
  lifetimes. All 11 such delivery classes are blocked.

Whether this contract is admissible for a correction is open.

Selected κ stays `0.001672660197076918`. Details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag43-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag43-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag43-side-correction-bill/independent.py
python3.12 -I -O -Werror -B research/p104-flag43-side-correction-bill/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag43-side-correction-bill
```

`verify.py` is read-only. It loads the pinned `check_native.py` by path. Its
admission checks go through `need()`, so they still fire under `-O`.
`independent.py` imports neither `verify.py` nor the native checker.
`test_package.py` corrupts temporary copies and checks that both scanners
reject all 14 corruptions. `build.py` is the producer and is not part of the
replay.

## Credit

Credit #3508 for R0 and the co-hosted chart, and #3456 for flag 43's
chronology. Both are cited only. Credit
`research/p104-side-correction-rank-obstruction` for the end-cut round-trip and
snapshot invoices this package compares against. Credit Nick Petalas / #2981
for the flag matching. Credit the reviewed #1991 native channel (Chafik
Boukhalfa) for the witness, checker and compiler, and Rohan Arun / PR1972 for
the scalar channel. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

1. Is P's private-copy discard admissible for a correction, or must `C` be
   uncomputed? If it must, the strict +2 applies.
2. Does the same forcing pattern block a zero-mass entry for every
   `(t, s)` pair with `G[t,s] ≠ 0`? If it does, strict per-target corrections
   need 208 extra rank mass in total.
3. Can a fused correction that changes published ADD coefficients, outside
   class Z (for example by retuning `D17`'s delivery at 3364), apply the entry
   with no added rank?

[TASK.json](TASK.json) gives first steps and blockers.
