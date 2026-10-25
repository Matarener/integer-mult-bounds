# The E8 label alphabet cannot emit a local child of rank above 9

**Scoped obstruction. No new κ.** Selected κ stays `0.001672660197076918`.

On the 120 root lines of E8, the PR717 label pairing
`B_ij = (<r_i, r_j> + 1) mod 2` has `F_2` rank 9. Every row lies in that
9-dimensional row space, so every support pair has pairing rank at most 9.
Nine basis lines against all 120 columns attain rank 9. The argument is in
[PROOF.md](PROOF.md).

On the selected template pinned by
`research/complex-local-word-ceiling/RESULT.json` (width 73, 896 families,
nine stages, centre 64, local mass 5586, idle mass 1646, idle cap 51), the
cheapest local histogram whose children have rank at most 9 is the fractional
profile `{9: 5586/9}`. Its relaxation at `a = 1/99` is strictly above 1, and
its ceiling on the pinned `1e-15` grid is the bracket
`(1409316073/488281250000, 577255863501/200000000000000)`, whose upper end is
strictly below `1/99`. The integer
histogram `{9: 620, 6: 1}` fails the same saving. A fractional rank-44
histogram passes that one-point screen, so the failure is specific to the cap.

This is the catalogue method “bound the best effective child rank for one
fixed support alphabet,” narrowed to the PR717 label pairing. Frame,
restoration and copy children that are not pairing-rank terms of `B` are
outside the alphabet. Inside it, those extra children of rank at most 9
cannot repair a moment that is already above 1.

## Scope and evidence

Original card: `complex-rank-shape-decoder`. Scope is **refined**: one
alphabet and the favorable rank-cap screen, not a block-climb construction.
The connection to the bottleneck is the rank-shape lever. Rank-1 children are
about half of the selected recursive cost; this alphabet cannot replace them
by children of rank 10 or more, and rank 9 still misses `a = 1/99` before any
frame or restoration charge.

`verify.py` rebuilds the 240 roots, checks the pairing rank and the row-space
certificate, and evaluates the pinned `ceiling.py` enclosures. It does not
import the frame-pair decoder package.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/e8-label-pairing-rank-cap
```

Expected marker:

```text
PASS_E8_LABEL_PAIRING_RANK_CAP
```

The registered replay also repeats the checker under `-O`. Direct
`python3 -B research/e8-label-pairing-rank-cap/verify.py` prints the witness
line indices, the `1/99` relaxation lower bound and the ceiling bracket.

## Open next questions

1. Does exactness of an eight-term all-pairs decoder force every term’s
   pairing rank to be at most 8, or does some live support attain 9? A single
   dual-basis term of rank 9 would show the alphabet cap is realized by an
   exact term; a proof that exactness stops at 8 would tighten this screen.
   No decoder search is run here.
2. Can a block-climb child whose rank is a multiplication width, rather than
   a pairing rank of `B`, exceed 9 on this template without leaving the
   coverage law? The first step is one legal width-10 child with its frame
   and restoration bill. This package has no such itinerary.

## Credit

The E8 line model and the rank-9 pairing fact are the PR717 alphabet as
recorded by themilkman216 in `research/complex-frame-pair-decoders`. The
selected-template ceiling engine and the published local mass are Douglas
Colkitt’s `research/complex-local-word-ceiling`, with Claude assistance. The
rank-cap question left open by that ceiling is Nick Petalas’s discussion
comment on PR #3701. New rank-space certificate and screen by unpaidmoon,
with substantial Cursor Grok assistance. Apache-2.0. No independent human or
formal-kernel review is claimed.
