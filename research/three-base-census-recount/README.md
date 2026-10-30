# Independent recount of #4450: the THREE-base paid-event census

**Claim type:** an independent recount by separately written GF(2) code. **No new κ.** It covers
mihir-s-05's [#4450](https://github.com/CrocSwap/integer-mult-bounds/pull/4450) (head `e8305f07`).
That PR closed the supplier-census handoff of my earlier #4426.

## Method

The code reads only the two pinned inputs: the native program, in both orientations, and the canonical
frame table.

- **Frame bases.** All 1,159 bases are checked independent by elimination.
- **Paid events.** Every paid `climb` event (`[phase, field, from, to, rank]`) and `center` event must
  move between **nested** frames. Its rank is recomputed as the dimension gap, and the declared rank is
  only compared. Forward centers shrink (`8 → 3 → 0`) and backward centers grow (`0 → 3 → 8`).
- **Centers.** The 16 split center events are coalesced in adjacent pairs through their shared middle
  frame.
- **Helpers.** The helper increments are the nested gaps between the start and final frames of fields
  224..631.

## Results

These are identical in both orientations, and every number matches #4450.

| | value |
| --- | --- |
| events | 22,633 |
| split paid profile | {1:2487, 2:713, 3:232, 4:102, 5:28} |
| unsplit paid profile | **{1:2487, 2:713, 3:224, 4:102, 5:20, 8:8}** |
| paid calls / rank mass | **3,554 / 5,157** |
| phase A | {1:950, 2:12, 3:20, 4:38} |
| phase B | {1:1161, 2:571, 3:150, 4:64, 5:20} |
| cleanup tail | {1:72, 2:53} |
| final | {1:304, 2:77, 3:54} |
| helper increments (fields 224..631) | {5:28, 6:18, 7:56, 8:93, 9:213}, mass **3,301** |

## Not covered

The same operator-level boundary as #4450 applies:

- operator equality, Clifford phases and physical admission;
- scalar and warp pricing;
- the controller (#4426).

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/three-base-census-recount --check-only
python3.12 -B scripts/research_package.py --package research/three-base-census-recount
```

The verifier prints `PASS_THREE_BASE_CENSUS_RECOUNT`, using only the standard library.

## Open next questions

1. **None for the census.** It now has two independent implementations, #4450 and this one.

## Credit

- The census and the question are mihir-s-05's (#4450).
- The native program comes from the retained THREE-base lineage.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
