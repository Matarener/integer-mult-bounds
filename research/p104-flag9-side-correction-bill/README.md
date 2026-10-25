# Flag 9's `I − G/2` entry costs +2 rank mass at the published end-cut (attaining T/S/T48; private P = +1)

**Exact bill plus a sharp obstruction. No new exponent.**

Open [#3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614)
finds that flag 9's primary present-head entry needs non-private +2 on the
published word (feeder `X58:333` at leave 745; 25/25 insertion classes
zero-mass obstructed) but constructs no attaining correction. Merged
[#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443) pins the
published chronology `X4 → Y23`, head 196. The deferred flag-9 head-step
repair is not reopened. This package answers #3614's flag-9 bill question on
the **published** native word only.

## The entry

`G[23,4] = <r23, r4> = −1`, and the channel leaves `X4` in `Y23` with
coefficient `−1/2`. The corresponding entry of `I − G/2` is `+1/2`. Applying
it leaves `Y23` with `X4` coefficient `0`. `Y23` is never read, so the
correction changes no other row.

## Result

Every correction below replaces the published terminal `Y23` transport at
event 3489 (`A3 → F23`, rank 5), where `A3 = [447,127,192]` and `F23` is
`Y23`'s final rank-8 frame.

| Word | Correction | Δ events | Δ ADDs | Δ transports | Δ rank mass | Profile Δ vs published | Edges |
|---|---|---:|---:|---:|---:|---|---:|
| **T** | `Y23: A3→FULL`, `Y23 += X4/2` in FULL, `Y23: FULL→F23` | +2 | +1 | +1 | **+2** | `H1 − H5 + H6` | 741 |
| **S** | published transport, then `X4: FULL→F23`, ADD in F23, `X4: F23→FULL` | +3 | +1 | +2 | **+2** | `2H1` | 742 |
| **P** | one private lifetime: zero `C` at FULL, copy `X4`, `C: FULL→F23`, ADD, erase | +5 | +1 | +1 | **+1** | `H1` | 741 |
| **T48** | T's lift, carrying all 48 off-diagonal entries `−G[23,s]/2` of row 23 | +49 | +48 | +1 | **+2** | `H1 − H5 + H6` | 741 |

The published `check_native.validate()` runs unchanged on each word with the
inserted coefficients set to `0`. It passes every native edge, including the
three newly lowered `A3 → FULL` and `FULL ↔ F23` recipes, all 208 endpoint
adapters, all 280 framed rows and the restoration of the 72 dirty helpers.
On the real word, the same checker fails only at
`full physical boundary endpoint Y23`. Exact rational replay confirms that
`Y23` is the only row that changes:

- in T, S and P it changes by exactly `+1/2 X4`;
- in T48, `Y23`'s final row becomes exactly `y23 + x23`, the identity row.

Head 196 is absent from `Y23`'s before-frame at the cut (it arrives only in
the terminal after-frame, per #3443) and is present in every correction
chart.

## Obstruction: no zero-mass placement exists

Insert one correction ADD between `X4` and `Y23` anywhere in the class that
keeps published events/ADDs, endpoint frames, free retarget/insert of
transports, and `C`'s published private lifetimes. Its added rank mass is
never zero.

- **Forcing leave.** At event 745 (`G7 −= 2·X4`), `X4`'s forced frame leaves
  `F23` carrying `X58`'s head `333` along the carrier path
  `631: G7 ← X58`, `729: G16 ← X58`, `731: G16 ← X35`, `745: G7 ← X4`.
  `G[23,58] = 0`, so `333` lies outside `F23`.
- **Every insertion point.** A least-lower-bound frame sweep checks all 25
  insertion classes; every class is obstructed (before 746 via early forced
  hosting of other targets; from 746 on immediately at `Y23`).
- **Parity.** Each nested transport changes rank by exactly its cost. So a
  non-private register's added mass is even. The strict minimum is therefore
  exactly **2**, and T, S and T48 attain it.

This feeder and the 25/25 obstruction match open #3614's leave-alone census
(recomputed here; not imported).

**Private route.** P relies on the inherited private-copy contract, under which
`C` is discarded while still holding a copy. Under that contract +1 is the
minimum for one added lifetime that copies `X4`: all 7 early delivery classes
before `C`'s published span are blocked. Whether this contract is admissible
for a correction is open.

Selected κ stays `0.001672660197076918`. Details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag9-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-side-correction-bill/verify.py
python3.12 -I -O -Werror -B research/p104-flag9-side-correction-bill/independent.py
python3.12 -I -O -Werror -B research/p104-flag9-side-correction-bill/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag9-side-correction-bill
```

`verify.py` is read-only. It loads the pinned `check_native.py` by path. Its
admission checks go through `need()`, so they still fire under `-O`.
`independent.py` imports neither `verify.py` nor the native checker.
`test_package.py` corrupts temporary copies and checks that both scanners
reject all 14 corruptions. `build.py` is the producer and is not part of the
replay.

## Credit

Credit [#3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614) for
the forcing census / feeder (leave-alone; recomputed), [#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443)
for flag 9's published chronology, and open [#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601)
/ [#3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610) as format
priors (leave-alone; scientific novelty is the flag-9 attaining bill). Credit
`research/p104-side-correction-rank-obstruction` for the end-cut round-trip
invoice pattern. Credit Nick Petalas / #2981 for the flag matching. Credit the
reviewed #1991 native channel (Chafik Boukhalfa) for the witness, checker and
compiler, and Rohan Arun / PR1972 for the scalar channel. Prepared by Wentao Li
with substantial AI assistance.

## Open next questions

1. Is the +1 private-copy route P admissible as a physical correction?
2. If a co-hosted flag-9 repair later lands, does the end-cut +2 discount?
3. Full-row forcing census on Y7/Y23/Y59 (~48 sources) — #3614 OQ1.
