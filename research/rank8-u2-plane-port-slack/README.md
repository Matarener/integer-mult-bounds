# The plane-port u=2 screen misses the rank-8/u2 16-child slack

**Negative pricing result. No new κ.** The selected conditional result stays
`836330098538459/500000000000000000` (`0.001672660197076918`).

PR #3889 shows that the ideal cell `selected centre + all local mass at rank ≤ 8
+ two unpaid coordinates` still clears `κ = 1/99` after integer rounding, with
room for **16** added rank-1 children on the nine-call uniform pool and not 17.
That cell is not a producer. This package prices the recorded contract that
actually leaves two unpaid coordinates, and it does not fit that room.

## Result

The selected line-port word `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` has mass
5586 per call and idle 1646 under PR1012's identity `72W + 64N`. It is not a
rank-8 delivery of that mass. The recorded u=2 endpoint is ctoth's plane-port
contract (source `E → FULL`, target `0 → E⊥`), as screened in
`research/plane-port-copy-budgets`.

1. **Source-bound copy invoice.** The direct native bill in
   `research/paired-plane-native-payload` uses 112 rank-2 drops per call, so
   `C = 224`. Two unpaid coordinates free only `2·(896/9) = 1792/9` units per
   call. `224 > 1792/9`, and the demanded mass is
   `71·896 + 224·9 = 65632` against capacity `73·896 = 65408`, ratio
   **293/292**. Idle would be negative. This invoice cannot be added to any
   histogram that already meets the u=2 law, including the ideal rank-8 cell.

2. **Decoder-free screen.** Drop that invoice and remove the 224 data units as
   rank-1 children, which is the favorable `shrink` row at charge 0. Its
   relaxation moment at `a = 1/98` has lower bound strictly above 1. Charging
   each rank-1 child at the upper enclosure `(1/73)^(97/98)`, at least **68**
   such children would have to be removed before that lower bound can fall to 1.
   The same test gives **147** on the `unchanged` row. The ideal cell's moment,
   after the 16 children that still pass, remains strictly below 1, so the
   shrink screen also sits at least 68 maximum-cost rank-1 children above that
   saturated bill.

The shrink word has maximum rank 5 and mass 5298. It is not the rank-8
histogram `{8:698, 2:1}` whose nine-call repeat is the integer cell. No
source-bound rank-8/u2 producer was found in the pinned inputs.

## What was recomputed

From `research/complex-local-word-ceiling/ceiling.py` and the selected mass:

| Object | Nine-call certificate at a = 1/98 |
|---|---|
| Ideal paid `{8:6282, 2:9}` plus idle `{51:272, 46:1}` | Moment upper bound `< 1`. Adding 16 rank-1 children still passes; 17 fails. |
| Plane-port shrink, centre 0, fractional idle | Moment lower bound `> 1` by at least 68 rank-1 children. |
| Plane-port unchanged, centre 0 | Moment lower bound `> 1` by at least 147 rank-1 children. |
| Copy charge `C = 224` | Coverage overspend 224; ratio 293/292. |

The 16/17 boundary uses the same additive model as PR #3889: extra rank-1
children increase the moment and do not receive idle-mass credit. The plane-port
rows use `ceiling.relax`, whose fractional idle packing is optimistic relative
to an integer idle histogram. A failure there rules out every integer idle
packing of the same local word.

## Scope

Card `complex-new-helper-inventory`, scope **changed**. The card asks for a new
physically realizable inventory. The handoff asks for a priced rank-8/u2
contract or a stop. This is the stop. It does not construct a decoder, change
the coverage law, or admit a supplier.

Not claimed: a lower bound on every possible u=2 mechanism, a bit-side twin, or
a proof that no future rank-8 delivery exists. Joint two-array primitives
outside the one-array copy interface are a different contract. The plane-port
exactness check in discussion 1587 is used as published and is not re-run.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/rank8-u2-plane-port-slack/verify.py
python3.12 -B scripts/research_package.py --package research/rank8-u2-plane-port-slack
```

Expected line:

```text
PASS_RANK8_U2_PLANE_PORT_SLACK extra_pass=16 shrink_deficit=68 unchanged_deficit=147 above_saturated_cell=true native=293/292 no_new_kappa=true
```

`verify.py --write` regenerates `RESULT.json`. The checker hashes the pinned
ceiling engine and reads `CWORD`, `CDATA_DROP` and the template constants from
the pinned plane-port verifier without executing it. Controls reject a moved
selected κ, a rank-8 optimum other than `{8:698, 2:1}`, a line-port word that
passes `a = 1/98`, and a near-empty u=2 word that fails it.

Not run: Lean, Docker, the selected cold replay, and the plane-port bit screen.

## Open next questions

1. Is there a u=2 producer whose paid children have rank at most 8 and whose
   additive bill is at most 16 rank-1 children on this nine-call cell? That is
   the only way this integer margin could survive contact with a producer.
   First step: one literal histogram rerun at `a = 1/98`. Blocker: the selected
   line-port word pays the unpaid=1 identity, and no rank-8 delivery of mass
   5586 is pinned here.
2. Can the 112 rank-2 drops be replaced by a charge of at most `1792/9` per
   call without losing the `I_2` endpoint? `C = 224` is already impossible
   inside this coverage law. First step: one native word on the 56 matched
   planes with `C ≤ 199` and a checked transfer. Blocker: the one-array
   interface needs two totals per block; a joint two-array primitive is a
   different contract.

## Credit

The integer 16/17 boundary is Nick Petalas's question as answered by ToikY in
PR #3889 (`research/lever-integer-twins`, head
`a18b03ea76fb373aeb00acc9c4fe119ac617ac83`), on the grid in PR #3874. The
plane-port screen is ctoth's contract in discussion 1587, packaged by
JosieElliston in `research/plane-port-copy-budgets`. The copy-mass obstruction
`293/292` is the accounting in `research/paired-plane-native-payload` (Jeremy
Diviney / the PR2203 lineage) and is recomputed here. The moment engine is
Douglas Colkitt's `research/complex-local-word-ceiling`. The coverage identity
is Sagar Thakrar's PR1012.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human or formal-kernel review is claimed. New work is Apache-2.0.
