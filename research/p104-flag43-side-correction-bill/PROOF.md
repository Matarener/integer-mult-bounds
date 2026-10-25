# Proof: the flag-43 side-correction entry at R0's co-hosted cut

## Setup

The base is CrocSwap main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The
requested pin, `6f100d4b…`, is an ancestor of it. The newer base is used because
#3508's R0 package is one of the inputs.

Inputs, all hash-pinned:

- the reviewed #1991 witness, recipes and checker in
  `research/p104-native-channel/`;
- the #2981 flag matching (flag 43: `X21 → Y59`, basis head `15`);
- #3508's `CERTIFICATE.json`, which contains the R0 splices, and its
  `REPAIR-RECIPES.json`.

The channel rules are those of `research/p104-native-channel/PROOF.md` §2–§3:

- A transport is nested and pays `|dim B − dim A|`.
- An ADD or copy needs both registers in the same frame.
- The private register `C` is created by zero, filled by copy and closed by
  erase. These are inherited private-copy semantics.

At the end, each target row of the channel is `y_t + Σ_s G[t,s] x_s / 2`, where
`G[t,s] = <r_t, r_s>` and `G[t,t] = 2`. The side correction must add
`(I − G/2)x`. Flag 43's entry is `(59, 21)`. Since `G[59,21] = 1`, the entry is
`−1/2`.

## 1. The corrected words

Let `F59` be `Y59`'s final frame `[499,27,228,32,112,15,7,1]`. It has rank 8
and lies inside the hyperplane orthogonal to `Y59`'s physical root. Let FULL be
the rank-9 chart. In R0:

- `Y59` is in `W6` from event 3363 until 3525;
- 3525 is `Y59: W6 → F59` (rank 2), and `Y59` has no later events;
- `X21` is in FULL from 1518 and has no events between 3364 and 3705;
- `C` has no lifetime after 2524;
- `Y59` is never the source of an ADD or copy.

Every correction replaces event 3525:

- **T:** `Y59: W6 → FULL` (rank 3); `Y59 += −1/2·X21` in FULL;
  `Y59: FULL → F59` (rank 1).
- **S:** `Y59: W6 → F59` (rank 2); `X21: FULL → F59` (rank 1);
  `Y59 += −1/2·X21` in `F59`; `X21: F59 → FULL` (rank 1).
- **P:** `Y59: W6 → F59`; `zero C` in FULL; `copy C ← X21` in FULL;
  `C: FULL → F59` (rank 1); `Y59 += −1/2·C` in `F59`; `erase C` in `F59`.
- **T48:** as T, but with all 48 ADDs `Y59 += −G[59,s]/2 · X_s`, one for each
  `s ≠ 59` with `G[59,s] ≠ 0`. All 104 sources are in FULL at 3525.

`W6 → FULL` is #3508's committed recipe, which R0 already uses for `D17` at
3612. `FULL → F59` and `F59 → FULL` are lowered by `build.py` with the pinned
compiler. They are committed in `CORRECTION-RECIPES.json`.

**Native validation.** `check_native.validate()` hard-codes the `G/2` endpoint
rows, so `verify.py` uses two runs per corrected word:

1. It runs `validate()` unchanged on the word with each inserted ADD
   coefficient set to `0`. This checks:
   - every edge's complete Clifford operator, including phase;
   - every transport binding and rank;
   - the 208 endpoint adapters;
   - the full framed induction. Every ADD and copy must be in a common chart,
     every endpoint frame must match, and all 280 rows must close, including
     the 72 dirty helpers and `C`'s storage.

   All of these conditions are independent of the ADD coefficients.
2. It replays the real word with exact rational rows and compares every final
   row with R0's.

In T, S and P, only `Y59` changes, and its change is exactly `−1/2·X21`. In
T48, `Y59`'s final row is exactly `{Y59: 1, X59: 1}`. As a control, the
unchanged `validate()` rejects each real word with
`full physical boundary endpoint Y59`.

**Bill.** All counts come from the validated words. R0 equals the published
word in events, ADDs, transport occurrences, rank mass and edge count.

| | events | ADDs | transports | rank mass | profile Δ vs R0 | added rank by register |
|---|---:|---:|---:|---:|---|---|
| T | 4,060 | 2,625 | 1,411 | 2,370 | `+H1 − H2 + H3` | `Y59: 2` |
| S | 4,061 | 2,625 | 1,412 | 2,370 | `+2H1` | `X21: 2` |
| P | 4,063 | 2,625 | 1,411 | 2,369 | `+H1` | `C: 1` |
| T48 | 4,107 | 2,672 | 1,411 | 2,370 | `+H1 − H2 + H3` | `Y59: 2` |

P raises the private zero, copy and erase counts from 8 to 9 each.

Comparing T and S: `T − S = H3 − H2 − H1`.

- If `H` is convex with `H(0) = 0`, then `H3 − H2 ≥ H2 − H1 ≥ H1`, so
  `T − S ≥ 0`: S is weakly cheaper.
- If `H(r) = a + br`, then T is cheaper by `a`, because it uses one fewer
  transport occurrence.

## 2. Obstruction

**Class Z₁.** A repair is in class Z₁ when it meets all of these conditions:

1. it keeps the published events in their published order, with the same ADD
   and copy registers and coefficients;
2. it inserts exactly one correction ADD between `X21` and `Y59`;
3. it may retarget or insert transports;
4. it keeps every endpoint frame;
5. it keeps `C`'s published private events.

R0 plus T, S or T48 are in Z₁.

**Lemma 1 (parity).** Each transport changes rank by exactly its cost, so a
register's path cost is at least `|rank(final) − rank(initial)|` and has the
same parity. All 280 non-private registers are already at that floor in the
published word. So in Z₁, each non-private register's added mass is a
non-negative even integer. It is zero exactly when the register's path is
monotone.

**Lemma 2 (least frames).** Fix a zero-added-mass repair, in which every
non-private path is monotone. Define `L_r(t)` by a forward sweep:

- start from the initial frames;
- at each ADD between non-private registers `r` and `p`, set both frames to
  `L_r + L_p`.

`C` is left unconstrained, which is a relaxation. Every feasible repair has
`frame_r(t) ⊇ L_r(t)`. It is infeasible if any `L_r(t) ⊄ final_r`.

All initial frames except the sources' heads are empty. So `L_r(t)` is the span
of the heads of the sources that reach `(r, t)` through a time-respecting chain
of ADDs.

**Forcing chain.** Before 884, `G9`'s only source ADD is event 625,
`G9 += 2·X12`, and `X12`'s head is `131`. At 884, `G9 −= 2·X21` equalizes the
two lower bounds:

```text
L_X21(884) = span{15, 131}
```

`X21`'s forced rank grows to `2, 6, 7, 8` at events 884, 1063, 1246 and 1517.
It is 9 from 1708. Because `G[59,12] = 0`, the binary pairing of `131` with
`Y59`'s root is odd, so `131 ∉ F59`. By contrast, `15 ∈ F59`, since
`G[59,21] = 1`.

**Theorem.** No member of Z₁ has zero added rank mass. Its minimum added rank
mass is exactly 2.

*Proof.* The sweep gives the same outcome for every insertion point between two
consecutive `X21`/`Y59` ADD events. That leaves 28 insertion classes. For each,
`verify.py` and `independent.py` add the equality `frame_X21(u) = frame_Y59(u)`
to the sweep:

- **Classes `u ≤ 884`.** The meeting puts `15` into `Y59` from `u` on. The
  sweep fails at `Y67` (events 264–268) for `u ≤ 227` and at `Y96` (2103) for
  `228 ≤ u ≤ 884`. This is consistent with #3508's closure table.
- **Classes `u ≥ 885`.** The merged frame contains `131` and so is not inside
  `F59`. The sweep fails at `u` itself.

Zero is therefore impossible. By Lemma 1 the minimum is at least 2, and T, S
and T48 attain 2. ∎

The theorem covers one inserted ADD between `X21` and `Y59`. A correction routed
through additional inserted ADDs with other non-private registers is not
enumerated here. Any register that meets `X21` after 884 inherits `131` and
cannot later meet `Y59` without adding rank. Routes that meet `X21` before 884
are not checked.

**Co-host discount.** On the published word, event 3525 is
`Y59: [95,447,32,20,6] → F59` (rank 3). The end-cut detour through FULL costs
`4 + 1 = 5`, which is +2. On R0 the detour costs `3 + 1 − 2 = +2`. The rank-mass
discount from co-hosting the head is zero.

**Private route.** Let class Z₁ᴾ be Z₁ with the inserted ADD replaced by one
added private lifetime: zero, copy from `X21` at time `t`, transports, ADD into
`Y59` at time `t′`, erase.

- If any non-private register adds mass, that costs at least 2.
- Otherwise `C`'s path costs at least 1 unless its copy chart equals its
  delivery chart, that is, unless `frame_X21(t) = frame_Y59(t′)`.
  - For `t ≥ 885`, that chart contains `131 ∉ F59`.
  - For `t ≤ 884`, the lifetime must end before the published lifetimes start
    at 2461. Then `Y59` hosts `15` from `t′ < 2461` on. All 11 such delivery
    classes fail the sweep, at `Y67`, `Y96`, `Y26` or `Y56`.

So the minimum over Z₁ᴾ is exactly 1, and P attains it.

## Controls

`test_package.py` copies the package and its eight pinned inputs into a
temporary tree and runs both scanners there under `-O`. The clean tree must pass
and stay byte-identical. Fourteen mutations must be rejected by both scanners:

- five certificate fields, covering the bill, per-register mass, feeder head,
  full-from event and one obstruction row;
- a duplicate JSON key;
- a witness byte flip;
- a byte flip in #3508's certificate;
- a phase flip in a new recipe;
- a wrong coefficient;
- an undercharged lift;
- an ADD in the wrong chart;
- an unrestored source;
- an unclosed private lifetime.

## Limits

- This covers one entry, one target row and one cut of one finite word. It does
  not price the other 103 rows, global hosting, idle children or precision. It
  does not supply a supplier and does not change κ.
- Class Z₁ keeps every published ADD and coefficient. A fused correction that
  retunes existing deliveries, such as `D17`'s at 3364, is outside it.
- P's +1 depends on the inherited private-copy discard. The native channel
  package does not claim that this discard is reversible.
- `H_r` is left symbolic.
