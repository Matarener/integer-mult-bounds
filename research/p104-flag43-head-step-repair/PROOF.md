# Proof: flag-43 head-step repair, its bill, and the forced closure

## Setup

Pin CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`. Inputs:

- The #2981 flag matching (`research/p104-joint-unit-flags/CERTIFICATE.json`).
  Flag 43 has source 21, target 59 and basis `[15, 387, 6, 18, 32, 67, 128, 1, 2]`.
- The reviewed #1991 witness, recipes and checker in `research/p104-native-channel/`.

All of these are hash-pinned.

The channel semantics are those of `research/p104-native-channel/PROOF.md` §2–§3:

- Each register carries a binary frame `W` with canonical chart `Gamma_W`.
- A transport is nested, changes only `W`, and pays one positive child of rank
  `|dim B - dim A|`.
- An ADD is allowed only when both registers have the same frame. It changes
  only the destination's logical row.

A register *hosts* `15` when `15` lies in the GF(2) span of its frame.

Leave-alone priors are cited only. #3456 proves that on the published word none
of the 15 `Y59` updates runs in a chart that spans `15`, while every `X21`
annotation spans it. This package rechecks only the one-line consequence it
needs: no published `Y59` update hosts the head.

## 1. The repair R0

Let:

- `W4 = [95,447,6,32]` and `W4' = [95,447,32,20]`;
- `W5 = [95,447,6,32,20]` and `W6 = W5 + [15]`;
- `V5 = [95,447,6,32,192]`, `V6 = V5 + [20]` and `W7 = V6 + [15]`.

R0 replaces exactly these published events (indices are unchanged):

| Event | Published | R0 |
|---|---|---|
| 3362 | `D17: W4 -> W5`, rank 1 | `D17: W4 -> W6`, rank 2 |
| 3363 | `Y59: W4' -> W5`, rank 1 | `Y59: W4' -> W6`, rank 2 |
| 3364 | `Y59 += D17/4` in `W5` | same ADD in `W6` |
| 3365 | `Y103: W4' -> W5`, rank 1 | `Y103: W4' -> W6`, rank 2 |
| 3366 | `Y103 += D17/4` in `W5` | same ADD in `W6` |
| 3460 | `D28: V5 -> V6`, rank 1 | `D28: V5 -> W7`, rank 2 |
| 3461 | `Y103: W5 -> V6`, rank 1 | `Y103: W6 -> W7`, rank 1 |
| 3462 | `Y103 += D28/4` in `V6` | same ADD in `W7` |
| 3525 | `Y59: W5 -> final`, rank 3 | `Y59: W6 -> final`, rank 2 |
| 3569 | `Y103: V6 -> final`, rank 2 | `Y103: W7 -> final`, rank 1 |
| 3612 | `D17: W5 -> FULL`, rank 4 | `D17: W6 -> FULL`, rank 3 |
| 3634 | `D28: V6 -> FULL`, rank 3 | `D28: W7 -> FULL`, rank 2 |

The final frames of `Y59` and `Y103` both contain `W6`. `Y103`'s also contains
`V6` and hence `W7`. So every changed transport is nested, and its rank equals its
frame gap. `D17` and `D28` have no other events between their changed transports.

**Native validation.** `verify.py` builds the R0 word in memory. It assembles a
recipe set from two parts: the published recipes for every edge still in use, and
the committed `REPAIR-RECIPES.json` for every new edge. Eight published edges drop
out and eight new ones enter. Edge `W4' -> W6` is shared by events 3363 and 3365,
as `W4' -> W5` was. The script then calls the published `check_native.validate()`
unchanged. That function:

- checks every edge's complete Clifford operator, including phase, against the
  independent interpreter;
- binds every transport event to its recipe and rank;
- checks all 208 intrinsic endpoint adapters;
- runs the framed scalar induction over all 280 inputs.

The induction requires every ADD to run in a common chart. It also requires each
source and each of the 72 dirty helper rows to end equal to its original input,
and each target row to end equal to `y_t + sum_s <r_t,r_s> x_s / 2`, with every
final frame matched. R0 passes. `independent.py` separately replays the published
and repaired words with exact rational rows. It finds all 280 final rows equal to
the published ones.

**Head co-hosting.** In R0, `Y59`'s updates are the published ones. The last,
3364, runs in `W6`, which lists `15`. At 3364, `X21`'s live frame is the
rank-9 full chart. It has later events 3705, 3760, 3811 and 3863, all of them
reads. The rational replay gives the `X21` entries of the rows `Y59` reads:

| Event | Partner | `X21` carried | `Y59`'s `X21` coefficient after |
|---|---|---:|---:|
| 3076 | `D10` | `1/2` | `1/2` |
| 3231 | `D5` | `-1/2` | `0` |
| 3364 | `D17` | `1/2` | `1/2` |

So the ADD that leaves `Y59` with its final `X21` coefficient runs in a chart
co-hosting the basis head, while the source hosts it and is still live. #3363's
relay census records the final coefficient. The event-level split is reported
here only because the co-hosting statement needs it.

## 2. The bill

Counts come from the validated words:

- events, scalar ADDs and transport occurrences are unchanged: 4,058, 2,624 and
  1,410;
- rank mass is unchanged at 2,368;
- distinct native edges are unchanged at 740;
- endpoint adapters are unchanged at 208.

The paid profile changes from `{1:1074, 2:58, 3:86, 4:104, ...}` to
`{1:1071, 2:63, 3:85, 4:103, ...}`. The ranks of 5 to 8 are unchanged.

Per register, the profile changes are:

- `Y59`: `-H1 - H3 + 2H2`;
- `D17`: `-H1 - H4 + H2 + H3`;
- `Y103`: no change, since `{1,1,2}` becomes `{2,1,1}`;
- `D28`: `-H1 - H3 + 2H2`.

The total delta is `Delta = -3H1 + 5H2 - H3 - H4`.

Sorted in decreasing order, the nine changed ranks go from `(4,3,3,2,1,1,1,1,1)`
to `(3,2,2,2,2,2,2,1,1)`. Both sum to 17, and the repaired prefix sums never
exceed the published ones. So the published vector majorizes the repaired one.
By Karamata's inequality, `Delta <= 0` for every convex rank price `H`.
Directly: convexity gives `2H2 <= H1 + H3` and `3H2 <= 2H1 + H4`, and these two
inequalities add up to `Delta <= 0`. `Delta = 0` for every affine `H(r) = a + br`.

**R1.** R1 replaces published events 3363–3366 by:

1. `Y103: W4' -> W5`
2. `Y103 += D17/4` in `W5`
3. `D17: W5 -> W6`, rank 1 (added)
4. `Y59: W4' -> W6`, rank 2
5. `Y59 += D17/4` in `W6`

It also sets 3525 to `Y59: W6 -> final` (rank 2) and 3612 to
`D17: W6 -> FULL` (rank 3). The two reads of `D17` into distinct targets commute,
and nothing between them touches `D17`, `Y59` or `Y103`. R1 passes the same native
validation. Its bill:

- +1 event and +1 transport occurrence;
- rank mass and ADDs unchanged;
- profile delta `+2H2 - H4`;
- 742 distinct edges.

R1 avoids the `Y103`/`D28` cascade by giving up event preservation.

## 3. Forced closure

**Class Z.** A repair is in class Z when:

1. it keeps the published events in their published order, with the same ADD
   registers and coefficients, and may insert transports;
2. it keeps every initial and final frame;
3. it adds no rank mass.

`verify.py` checks that every one of the 280 non-private registers has published
rank mass equal to `rank(final) - rank(initial)`. A register's rank mass is at
least that floor, and equals it only for a monotone path. So by condition 3 every
non-private register's path in a class-Z repair is monotone. The private register
`C` is reported separately and never counted as an obstruction.

**Propagation lemma.** Suppose that in a class-Z repair a non-private register
`r` hosts `15` at event `t`. Then it hosts `15` at every later event, by
monotonicity. Any ADD or copy at `j >= t` that involves `r` forces its partner to
host `15` at `j`, because the two frames are equal.

Starting from a `Y59` update `u`, take the closure of this rule. A register is
*must-change* when its published frame at its forced time does not span `15`.

- If a must-change register's final frame excludes `15`, no monotone path can
  host `15` there, so no class-Z repair makes `u` head-hosting.
- If the closure is unobstructed, the published frames already satisfy every
  other forced condition, because published paths are monotone.

`verify.py` computes the closure with a worklist and `independent.py` with a
single forward sweep. For the 15 `Y59` updates:

| Update | Partner | Must-change | Obstructions | First obstruction |
|---:|---|---:|---:|---|
| 223–227 | `Q1, Q2, Q4, Q5, Q6` | 260–274 | 56 each | `Y67` (264–268) |
| 2099, 2191 | `D23, D20` | 140 | 56 | `Y96` |
| 2275 | `D10` | 140 | 56 | `Y26` at 2336 |
| 2341 | `D5` | 140 | 56 | `Y56` at 2387 |
| 2393 | `D17` | 133 | 53 | `Y22` at 2638 |
| 2698 | `D23` | 45 | 17 | `Y96` at 2706 |
| 2891 | `D20` | 31 | 12 | `Y96` at 2897 |
| 3076 | `D10` | 17 | 4 | `Y26` at 3220 |
| 3231 | `D5` | 10 | 1 | `Y56` at 3348 |
| 3364 | `D17` | 4 | 0 | none |

The exact per-update values are in `CERTIFICATE.json`. So 3364 is the only update
that any class-Z repair can make head-hosting. Its must-change set is exactly:

- `Y59` and `D17` from 3364;
- `Y103` from 3366;
- `D28` from 3462.

**Minimality in the event-preserving subclass.** With no inserted events, each
must-change register `r` with forced time `t` behaves as follows:

- its last transport before `t` must gain `15` in its after-frame, since no
  published after-frame there spans `15`;
- each later transport of `r` then has a changed before-frame.

Together these are exactly R0's nine transports: 2 for `Y59`, 2 for `D17`, 3 for
`Y103` and 2 for `D28`. At each forced ADD the shared frame must contain both
published frames and `15`. That gives `span(W5 + 15) = W6` at 3364 and 3366, and
`span(V6 + 15) = W7` at 3462. R0 uses exactly these minimal frames.

## Controls

`test_package.py` copies the package and the six pinned inputs into a temporary
tree and runs both scanners there under `-O`. The clean tree must pass and stay
byte-identical. Fourteen mutations must be rejected by both scanners:

- seven certificate fields;
- a duplicate JSON key;
- a witness byte flip;
- a phase flip in a new recipe;
- an undercharged 3525 transport;
- three truncated cascades: `Y59` lifted alone, without `Y103`/`D28`, and without
  `D28`.

Each truncated cascade must fail at the common-chart rule.

## Limits

This is a statement about one finite repaired word for one flag:

- It does not build or price the `I - G/2` side correction or a supplier.
- It does not perform global hosting or precision analysis.
- It does not change κ.

"Co-hosting" means span membership in annotated frames. It does not model what the
head direction means inside relay registers. `H_r` is left symbolic. The repo's
actual per-rank weights decide the sign of `Delta` only if they are strictly
concave somewhere on `{1,2,3,4}`. The class-Z obstruction excludes repairs that:

- reorder events (R1 is one such repair);
- add rank mass;
- change ADDs, coefficients or endpoint frames.

Optimality of R0's profile among class-Z repairs is not claimed.
