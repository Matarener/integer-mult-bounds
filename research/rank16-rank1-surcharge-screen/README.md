# Rank-16 delivery survives every legal rank-1 surcharge

**Negative screen. No new kappa.** The selected record is unchanged, and
`research/complex-local-word-ceiling/ceiling.py` is not edited.

## Scope

Chooser seed `fb1b693e95073cda2220efd59e654728` drew `p104-side-correction`
first. That experiment is already open for flag 0. The same seed's unclaimed
helper 600/601 sign test is PR #4061. This package is the other bounded screen
on `complex-rank-shape-decoder`: one candidate profile, accepted only if its
ceiling beats the selected word by 5%.

The candidate is not an idle histogram of the unchanged selected word. The
published lever `{16: mass/16}` leaves idle mass at rank 51. Here that idle
mass is moved into the local profile as extra rank-1 children. The published
control that one extra rank-1 child lowers the ceiling does not say whether
the five-percent gate survives the largest legal count.

## What is established

The pinned model has selected local mass 5586 and idle mass 1646. At grid
`1e-15`:

| profile | ceiling |
| --- | --- |
| selected word | `1690054109089/1000000000000000` |
| rank-16 delivery plus 1646 rank-1 children | `285077936577/125000000000000` |

Delivering the selected local mass as rank-16 children and spending all 1646 idle-mass units on extra rank-1 children still clears the five-percent ceiling gate.

The ratio of those ceilings is `2280623492616/1690054109089`, about 1.349,
against the gate `21/20`. One further rank-1 child makes local mass exceed
the coverage law and is rejected. Ideal rank-16 delivery with no surcharge is
the lever already printed by `levers.py`; it is not restated as a new ratio.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/rank16-rank1-surcharge-screen
```

Expected marker: `PASS_RANK16_RANK1_SURCHARGE`.

## Limits

This does not construct a rank-16 decoder, price frames, restoration, or
hosting, or change the halving guard. It does not repack an idle histogram at
ranks up to 51; those favorable packings are the ceiling paper, #3811 and
#3874. A charge the coverage law cannot express as rank-1 children is outside
this screen. The selected baseline replay was not run in this partial checkout.

## Open next questions

Which sourced copy, frame or restoration histogram, outside extra rank-1
children in this coverage law, pushes rank-16 delivery under the five-percent
gate? The first step is to pin one such histogram and screen that exact
profile. No such histogram is pinned in `levers.py`.

## Credit

Douglas Colkitt's ceiling model and lever table are the pinned inputs.
Riquelme Soares (@hevlyo), with substantial AI assistance in the screen and
write-up. Apache-2.0. No independent human review is claimed.
