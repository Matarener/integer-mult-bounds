# Proof: flag-1 head-step repairs, their bill, and the zero-mass obstruction

## Setup

Pin CrocSwap main `6f100d4bb5083f8c35d96fd95a539811c62f245c`. Inputs:

- The #2981 flag matching (`research/p104-joint-unit-flags/CERTIFICATE.json`).
  Flag 1 has source 0, target 7 and basis `[232, 256, 7, 11, 19, 35, 64, 2, 1]`.
- The reviewed #1991 witness, recipes and checker in `research/p104-native-channel/`.

All of these are hash-pinned. The channel semantics are those of
`research/p104-native-channel/PROOF.md` §2–§3, as in #3508:

- Each register carries a binary frame.
- A transport is nested (up or down) and pays rank `|dim B - dim A|`.
- An ADD needs both registers in the same frame, and it changes only the
  destination's row.

A register *hosts* `232` when `232` lies in the GF(2) span of its frame.

#3451 proves that on the published word no `Y7` update hosts the head, while
every `X0` annotation spans it. That chronology is cited, not re-derived. This
package rechecks only the one-line consequence it needs.

## 1. The delivering update and its commutation window

The rational replay finds that among the six `Y7` updates (19, 20, 2013, 2146,
2526, 2797), only 2797 (`Y7 += D17/4`, chart `[95, 486]`) carries any `X0`
entry. It carries `-1/2`, which is `Y7`'s final `X0` coefficient. `D17` is the
destination of exactly two events, 2497 (`D17 += C`) and 3613 (`D17 += -Q4`).
No event reads `Y7`.

So placing the ADD anywhere after 2497 and before 3613 gives the same final rows.
This window has 1,115 slots besides the published one.

## 2. The repairs

Write `A2 = [95, 486]`, `A3 = A2 + [232]` and `FULL` for the rank-9 chart.

**R0** replaces these published events (later indices shift by one):

| Event | Published | R0 |
|---|---|---|
| 2795 | `D17: [486] -> A2`, rank 1 | `D17: [486] -> A3`, rank 2 |
| 2796 | `Y7: [95] -> A2`, rank 1 | `Y7: [95] -> A3`, rank 2 |
| 2797 | `Y7 += D17/4` in `A2` | same ADD in `A3`, then inserted `D17: A3 -> A2`, rank 1 |
| 3473 | `Y7: A2 -> final`, rank 6 | `Y7: A3 -> final`, rank 5 |

`span(A3)` lies in `final(Y7)`, so `Y7` stays monotone and its mass is unchanged
(`1 + 6 = 2 + 5`). `D17` goes up and back down once, which adds exactly 2.

**R1** deletes published 2796, 2797 and 3473. After 3612 (`D17: W5 -> FULL`) it
inserts three events: `Y7: [95] -> FULL` (rank 8), `Y7 += D17/4` in `FULL`, and
`Y7: FULL -> final` (rank 1, downward). `Y7`'s mass goes from `1 + 1 + 6` to
`1 + 8 + 1`, adding 2. No other register changes, and the event count is
unchanged.

**Native validation.** `verify.py` builds each word in memory. It assembles a
recipe set from two parts: the published recipes for every edge still in use,
and the committed `REPAIR-RECIPES.json` for each of the six new edges (four in
R0, two in R1). It then calls the published `check_native.validate()`
unchanged. That function:

- checks every edge's full Clifford operator, phase included;
- binds every transport to its recipe and rank;
- checks all 208 endpoint adapters;
- runs the framed scalar induction over all 280 inputs.

The induction includes the common-chart rule, the restoration of every source
and dirty helper, and each target's final row and frame. Both words pass.
`independent.py` replays both words with exact rational rows and finds all 280
final rows equal to the published ones.

**Co-hosting.**

- In R0, the ADD at 2797 runs in `A3`, which spans `232`.
- In R1, it runs in `FULL` (new index 3611).
- In both, `X0` is in its rank-9 frame and has four later events, all reads.
- In both, this is the only co-hosted `Y7` update, and it delivers `X0`'s
  `-1/2`.

## 3. The bill

All counts come from the validated words.

| | Events | ADDs | Transports | Rank mass | Edges | Profile delta |
|---|---:|---:|---:|---:|---:|---|
| R0 | +1 | 0 | +1 | +2 | 742 | `-H1 + 2H2 + H5 - H6` |
| R1 | 0 | 0 | 0 | +2 | 741 | `-H6 + H8` |

For affine `H(r) = a + b·r` the deltas are `a + 2b` and `2b`. For nondecreasing
`H`, `H8 - H6 >= 0`. R0's delta equals `H2 + (H2 - H1) - (H6 - H5)`. It is at
most `H2` for convex `H`, and its sign is not fixed: it is `+2` at `H = r` and
`-4` at `H = r²`. The private register `C` has identical events in all three
words.

## 4. The zero-mass obstruction

**Classes.** Both classes keep:

- every ADD (same registers and coefficients);
- every endpoint frame;
- `C` completely unconstrained.

Transports of non-private registers may be inserted, retargeted or removed
freely.

- **Class Z₀** keeps the published relative order of all ADDs and copies.
- **Class Z₁** is Z₀, except that the delivering ADD may sit at any slot of its
  commutation window (§1).

**Parity lemma.** Take a non-private register's nested path from `init` to
`final`. Its mass is `sum |Δ_i|`, which is at least `|sum Δ_i| = rank(final) -
rank(init)` and has the same parity. Equality holds iff every step goes up,
which means the frames grow by inclusion. All 280 non-private registers meet
this floor on the published word (checked). So a repair whose non-private mass
equals the published mass has monotone non-private paths. Any other repair adds
an even amount, at least 2.

**Least-frame sweep.** Fix a placement of the ADDs and a forced ADD `u`. Walk
the ADDs in order with `L(r) = init(r)`, skipping any ADD that involves `C`. At
each ADD between `a` and `b`, set both `L(a)` and `L(b)` to `L(a) + L(b)`, and at
`u` add `232` as well.

By induction, in any monotone solution each register's frame at each ADD
contains its `L`, so the final frame must contain the end value of `L`. If some
`L(r)` is not inside `final(r)`, no zero-surcharge repair of that placement
co-hosts at `u`. Skipping `C`'s ADDs only removes constraints, so this verdict
stays sound with `C` free. With nothing forced, the published word passes this
check.

**Results** (exact lists are in `CERTIFICATE.json`):

| Placement | Infeasible registers | First (sorted) |
|---|---:|---|
| Z₀, update 19 / 20 | 56 / 56 | `Y0` |
| Z₀, update 2013 / 2146 | 54 / 52 | `Y1` |
| Z₀, update 2526 | 23 | `Y103` |
| Z₀, update 2797 | 14 | `Y103` |
| Z₁, slots after 2497–3365 (868) | 23 down to 1 | `Y103` in every slot |
| Z₁, slots after 3366–3612 (247) | 0 | — |

#3508's head-closure rule gives the same verdict for all six Z₀ updates. It
finds 56, 56, 56, 56, 23 and 14 registers whose final frame excludes the head,
the first being `Y8` each time. `independent.py` recomputes both tests with
separate code, including a fresh full replay for every Z₁ slot.

**Consequences.**

1. No Z₀ repair with zero added non-private mass co-hosts at any `Y7` update.
   By parity, every co-hosting Z₀ repair adds at least 2, and R0 adds exactly 2.
2. Neither does any Z₁ placement before 3366, so the same floor of 2 holds
   there.
3. For placements after 3366 the relaxed sweep is feasible, so no bound is
   claimed. R1 sits in this window at +2.

The least solution there leaves `D17` empty at all of its reads. The published
word instead holds `D17` at rank 2, then 4, then 5. Realizing a low-frame word
would need re-framing large parts of the schedule. The direct attempt
intersects every frame in `D17`'s backward cone with `final(Y7)`. It reaches 208
registers, including `C`, and needs 56 source initial frames inside `final(Y7)`,
which they are not. So that attempt fails. Open question 1 asks whether some
other construction succeeds.

## Controls

`test_package.py` copies the package and the six pinned inputs into a temporary
tree and runs both scanners there under `-O`. The clean tree must pass and stay
byte-identical. Seventeen mutations must be rejected by both scanners:

- ten certificate fields (bill, profile, register mass, co-hosting, delivery,
  closure, sweep, scan window, scan count, κ);
- a duplicate JSON key, a witness byte flip, and a phase flip in a new recipe;
- R0 without the inserted drop, and R0 with only `Y7` lifted. Both must fail at
  the common-chart rule.
- an undercharged 2795 transport;
- R1 placed after `D17`'s restoration at 3613, which breaks `Y7`'s final row.

## Limits

This is a statement about finite repaired words for one flag.

- It does not build or price the `I - G/2` side correction or a supplier.
- It does not perform global hosting or precision analysis.
- It does not change κ.

"Co-hosting" means span membership in annotated frames. `H_r` is left symbolic.
The obstruction covers Z₀ and Z₁ before 3366, with `C` relaxed. It does not
cover:

- reorders of other events;
- changed ADDs or endpoint frames;
- the 247 late slots.

The +2 floor is stated for non-private mass. Both repairs leave `C` unchanged,
so their total and non-private surcharges agree.
