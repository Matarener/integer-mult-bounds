# Proof: the flag-1 side-correction entry at #3532's co-hosted charts

## Setup

The base is CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The
requested pin `6f100d4b…` is an ancestor of it. The newer base contains merged
#3508 and #3451, which this package cites.

Inputs, all hash-pinned:

- the reviewed #1991 witness, recipes and checker in
  `research/p104-native-channel/`;
- the #2981 flag matching (flag 1: `X0 → Y7`, basis head `232`);
- #3532's `CERTIFICATE.json` (R0 and R1 splices) and `REPAIR-RECIPES.json`.

#3532 is still open, so neither file is on main. Both are vendored
byte-identically under `inputs/pr3532/` from #3532's head
`8fecbf7df7b48c9004bd10a0da6a81f33d455737`. `SOURCES.json` records their Git
blobs at that head (`head:` pins), and both scanners check their SHA-256.

The channel rules are those of `research/p104-native-channel/PROOF.md` §2–§3,
as in #3508, #3532 and #3601:

- A transport is nested and pays `|dim B − dim A|`.
- An ADD or copy needs both registers in one frame.
- The private register `C` is created by zero, filled by copy and closed by
  erase.

At the end, each target row is `y_t + Σ_s G[t,s] x_s / 2`. The side correction
must add `(I − G/2)x`. Flag 1's entry is `(7, 0)`. Since `G[7,0] = −1`, the
entry is `+1/2`. `Y7`'s only `X0` delivery is 2797 (`Y7 += D17/4`, carrying
`−1/2`). No event reads `Y7`.

## 1. The corrected words

Let `F7` be `Y7`'s final frame `[484,232,12,55,75,24,7,2]`. It has rank 8 and
contains `232`. Let FULL be the rank-9 chart, `A2 = [95,486]` and
`A3 = [95,486,232]`.

**On R0** (#3532's order-preserving repair):

- `Y7` is in `A3` from 2796 until its terminal transport 3474
  (`A3 → F7`, rank 5);
- `X0` is in FULL from 1486, with later reads at 3643, 3799, 3851 and 3955;
- `C` has no lifetime after 2524.

Every R0 correction replaces event 3474:

- **T:** `Y7: A3 → FULL` (rank 6); `Y7 += 1/2·X0` in FULL; `Y7: FULL → F7`
  (rank 1).
- **S:** R0's transport; `X0: FULL → F7` (rank 1); `Y7 += 1/2·X0` in `F7`;
  `X0: F7 → FULL` (rank 1).
- **P:** R0's transport; `zero C` in FULL; `copy C ← X0`; `C: FULL → F7`
  (rank 1); `Y7 += 1/2·C` in `F7`; `erase C`.
- **Trow:** as T, but with all 48 ADDs `Y7 += −G[7,s]/2 · X_s` for `s ≠ 7`
  with `G[7,s] ≠ 0`. All 48 sources are in FULL at 3474.

**On R1** (#3532's relocated repair), event 3610 is `Y7: [95] → FULL`
(rank 8), 3611 is `Y7 += D17/4` in FULL, and 3612 is `Y7: FULL → F7`. `X0` is
in FULL there. Each R1 correction keeps 3611 and inserts after it:

- **E:** `Y7 += 1/2·X0` in FULL.
- **Erow:** the 48 row-7 ADDs in FULL. All 48 sources are in FULL at 3611.

**Control on the published word.** Tend replaces 3473 (`Y7: A2 → F7`,
rank 6) with `Y7: A2 → FULL` (rank 7), `Y7 += 1/2·X0` in FULL, and
`Y7: FULL → F7`.

`FULL → F7` and `[95] → FULL` are #3532's committed recipes. `build.py` lowers
the other three new edges with the pinned compiler: `A3 → FULL`, `A2 → FULL`
and `F7 → FULL`. They are committed in `CORRECTION-RECIPES.json`.

**Native validation.** As in #3601, `verify.py` runs the published checker
twice per word:

1. `validate()` runs unchanged on the word with every inserted ADD coefficient
   set to `0`. It checks every edge's complete Clifford operator, every
   transport binding and rank, all 208 endpoint adapters and the framed
   induction over all 280 rows. Every ADD and copy must be in a common chart,
   every endpoint frame must match, and the 72 dirty helpers and `C`'s storage
   must be restored. None of these depends on ADD coefficients.
2. The real word is replayed with exact rational rows and every final row is
   compared with its base word's.

`Y7` is the only changed row. In E, T, S, P and Tend it changes by exactly
`+1/2·X0`. In Erow and Trow, `Y7`'s final row is exactly `{Y7: 1, X7: 1}`. As a
control, the unchanged `validate()` rejects each real word with
`full physical boundary endpoint Y7`.

**Bill.** All counts come from the validated words.

| | events | ADDs | transports | rank mass | edges | profile Δ vs base | added rank by register |
|---|---:|---:|---:|---:|---:|---|---|
| published | 4,058 | 2,624 | 1,410 | 2,368 | 740 | — | — |
| R0 (#3532) | 4,059 | 2,624 | 1,411 | 2,370 | 742 | — | `D17: 2` vs published |
| R1 (#3532) | 4,058 | 2,624 | 1,410 | 2,370 | 741 | — | `Y7: 2` vs published |
| E | 4,059 | 2,625 | 1,410 | 2,370 | 741 | none | none |
| Erow | 4,106 | 2,672 | 1,410 | 2,370 | 741 | none | none |
| T | 4,061 | 2,625 | 1,412 | 2,372 | 743 | `+H1 − H5 + H6` | `Y7: 2` |
| S | 4,062 | 2,625 | 1,413 | 2,372 | 744 | `+2H1` | `X0: 2` |
| P | 4,064 | 2,625 | 1,412 | 2,371 | 743 | `+H1` | `C: 1` |
| Trow | 4,108 | 2,672 | 1,412 | 2,372 | 743 | `+H1 − H5 + H6` | `Y7: 2` |
| Tend | 4,060 | 2,625 | 1,411 | 2,370 | 741 | `+H1 − H6 + H7` | `Y7: 2` |

P raises the private zero, copy and erase counts from 8 to 9 each.

## 2. Obstruction

**Class Z_c.** A word is in Z_c when it meets all of these conditions:

1. it keeps every published ADD and copy (registers and coefficients) in
   published relative order, except that the delivering ADD 2797 may sit
   anywhere in its commutation window. That window is #3532's, bounded by
   `D17`'s writes at 2497 and 3613, and holds 1,116 placements;
2. it inserts at least one correction ADD between `X0` and `Y7`;
3. transports of non-private registers may be inserted, removed or
   retargeted;
4. every endpoint frame is kept;
5. `C`'s published events are kept.

E, Erow and Tend are in Z_c, and so are R0 plus T, S or Trow.

**Lemma 1 (parity; as in #3532 and #3601).** All 280 non-private registers sit
at their rank floor on the published word (checked). Over a nested path, mass
minus floor is even. So in Z_c each non-private register's added mass is a
non-negative even integer. It is zero exactly when the register's path is
monotone.

**Lemma 2 (least frames).** Fix a placement and suppose the non-private paths
are monotone. A forward sweep starts from the initial frames. At each ADD
between non-private registers it sets both frames to their join, and at the
correction ADD it joins `X0` and `Y7`. `C` and any register declared free are
skipped, which only removes constraints. Every feasible repair has frames that
contain the sweep's. So the placement is infeasible if any swept frame leaves
its register's final frame. Dropping an ADD from the sweep, or freeing a
register, also only removes constraints. An infeasible verdict therefore
survives adding the dropped ADD back at any position.

**Forcing chain.** `X0`'s forced rank is 2 at event 840 (`G25 += 2·X0`), 6 at
1074 (`G18 −= 2·X0`), 7 at 1311, 8 at 1485, and 9 from 1690. At 1074 the swept
frame is `[256,128,64,32,8,3]`, which is not inside `F7`. The cause is `X7`'s
head `387`. It reaches `G18` along `616: X7–G11`, `679: G11–X20` and
`1070: X20–G18` (earliest time-respecting chain), and it reaches `X0` at
`1074: G18–X0`. `G[7,7] = 2` is even, so the binary pairing of `387` with
`Y7`'s root is even and `387 ∉ F7`. Of the 56 source heads outside `F7`, all
of which have even `G[7,s]`, `X7`'s is the only one that reaches `X0` by 1074.

**Theorem 1.** No member of Z_c has zero added non-private rank mass. The
minimum added rank mass over Z_c is exactly 2, attained by Tend and by E and
Erow (each +2 over the published word).

*Proof.* Drop the delivering ADD from the sweep. The outcome is then constant
between consecutive `X0`/`Y7` ADD events, which leaves 18 insertion classes.
`verify.py` and `independent.py` sweep each one with the meeting
`frame_X0(u) = frame_Y7(u)` added:

- **`u ≤ 841` (4 classes).** The meeting puts `232` into `Y7` from `u` on.
  `Y7`'s updates then push it into `Q1`/`Q4` (events 19 and 20) or `D5`
  (event 2013). The sweep fails at `Y8` at event 22, 23 or 2014.
- **`u ≥ 1075` (14 classes).** The merged frame contains `387`, so the sweep
  fails at `u`, at `Y7`.

By Lemma 2 each verdict holds for every placement of the delivering ADD. Extra
correction ADDs, as in Erow and Trow, only add constraints. As a cross-check,
the 19 published-order classes, which include 2798, are all obstructed. By
Lemma 1 the minimum is at least 2, and Tend, E and Erow attain 2. ∎

**Theorem 2 (joint, relocated).** Among words in Z_c whose delivering ADD runs
in a chart spanning `232`, the minimum added rank mass is exactly 2. R1+E
attains it.

*Proof.* The lower bound follows from Theorem 1. R1+E co-hosts at 3611 (FULL)
and adds 2 over the published word. ∎

**Theorem 3 (joint, order-preserving).** Restrict Z_c to words that keep the
delivering ADD at 2797, with a chart spanning `232`, and add no private
lifetime. Every such word has added non-private rank mass at least 4. R0+T and
R0+S attain exactly 4.

*Proof.* By Lemma 1, a word with non-private added mass 2 has exactly one
non-monotone non-private register `r`. Free `r` (and `C`) in the sweep. The
co-hosting constraint joins `Y7`, `D17` and `232` at 2797.

- With nothing free, the co-hosting sweep fails, as in #3532.
- Free each of the 280 registers in turn. The co-hosting sweep still fails for
  every choice except `r = D17`.
- With `D17` free, adding the correction meeting at any of the 19
  published-order classes fails again: at `Y8` for `u ≤ 841` and at `Y7` for
  `u ≥ 1075`.

So no single non-monotone register suffices, and the non-private added mass is
at least 4. ∎

**Co-host discount.** Tend adds 2 on the published word.

- At R0's cut, T adds 2, so the discount is 0.
- At R1's co-hosted update, E adds 0, so the discount is 2.

**Private route.** Let Z_cᴾ be Z_c with the correction ADD replaced by one
added private lifetime: zero, copy from `X0` at time `t`, transports, ADD into
`Y7` at time `t′`, erase.

- If any non-private register adds mass, that costs at least 2.
- Otherwise `C`'s path costs at least 1 unless its copy chart equals its
  delivery chart.
  - For `t ≥ 1075`, the copy chart contains `387 ∉ F7`.
  - For `t ≤ 1074`, the lifetime must end before `C`'s published lifetimes
    start at 2461. Then `Y7` hosts `232` from `t′ < 2461` on. All 5 such
    delivery classes fail the sweep at `Y8`, with the delivering ADD dropped.

So the minimum over Z_cᴾ is exactly 1. P on R0 adds 1 over R0. The same route
at the published end cut would add 1 over the published word. P's +1 relies on
the inherited private-copy discard.

## Controls

`test_package.py` copies the package and its six pinned main inputs into a
temporary tree and runs both scanners there under `-O`. The clean tree must
pass and stay byte-identical. Eighteen mutations must be rejected by both
scanners:

- seven certificate fields (T bill, E per-register mass, forcing head, exit
  event, one strict-sweep row, the co-host rescue list, the R1 discount);
- a duplicate JSON key;
- a witness byte flip;
- a byte flip in the vendored #3532 certificate;
- a phase flip in a new recipe;
- T with a wrong coefficient, and T with an undercharged lift;
- S with the ADD in the wrong chart, and S with an unrestored source;
- P with an unclosed private lifetime;
- E with the ADD in `A3` (no common chart), and E with the wrong sign.

## Limits

- This covers one entry, one target row and the charts of two repairs of one
  finite word. It does not price the other 103 rows, global hosting, idle
  children or precision. It does not supply a supplier and does not change κ.
- Z_c keeps every published ADD and coefficient. A fused correction that
  retunes existing deliveries is outside it.
- Theorem 3 bounds non-private mass for strict words. With P's inherited
  private-copy discard, R0+P reaches 3.
- The joint minimum with an added private lifetime is between 1 and 2. It
  equals 1 only if a zero-mass co-hosting relocation exists in #3532's 247
  late slots, which is #3532's open question 1.
- R0 and R1 come from open #3532. If #3532's head changes, the vendored pins
  must be refreshed.
- `H_r` is left symbolic.
