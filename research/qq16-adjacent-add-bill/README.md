# Adjacent F0 ADD after the first rank-positive climb

**Partial frame bill. No new κ.** Selected conditional κ stays
`0.001672660197076918`.

On the pinned forward core, event 9894 is the word's first climb:
`L546` from frame 0 (`[]`) to frame 4 (`[459]`), rank 1. Event 9895 is
`L546 -= L561` in frame 4. `L561` enters in frame 4 and is not climbed or
written before that ADD. Both operands already sit in the annotated frame, so
the retained nested-frame contract accepts the ADD with no second climb.

The coefficient `-1/1` costs 4 scalar work steps and 8 real steps under the
retained bit-clear / bit-add / halving count. The sign does not add a step.
The climb is the pair's only rank child (`+1` at rank 1). Replaying every
climb and every `L` scalar in the forward word reproduces `final`.

The in-frame inverse `L546 += L561` is legal at the same 4-step cost and
restores only the post-climb value. The pinned Clifford table has no child
`(4, 0)`. Both registers end at frame 1, not at `L546`'s entrance frame 0.

This does not assign six-tape windows, meter the climb's kernel, or price a
consumer. Unknown physical layout cost is not zero. PR #3932 bound event 9894
and left this ADD unpriced. PR #4114 ledgers rays `L359` and `L112`; it does
not replay this pair.

## Scope and evidence

Task `joint-query-controller`, scope **refined** to this one pair. The card's
allowed variation is one changed first pair. Base
`bb4bccbf42844d2801487450727c2f63e10d1d0f`, priority revision 6. Pins are in
[SOURCES.json](SOURCES.json). The argument is checked by
[verify.py](verify.py), not by a separate prose proof.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/qq16-adjacent-add-bill
```

Expected:

```text
PASS_QQ16_ADJACENT_ADD_BILL climb=9894 add=9895 frame=4 axis=459 rank_child=1 scalar_work=4 real_steps=8 climbs_before_pair=0 reverse_child=absent word_climbs=3486 word_scalars=20089 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/qq16-adjacent-add-bill outcome=partial
```

Controls inside the verifier: the published final-frame vector, a unit / `3/1` /
`1/2` work triple, rejection of the ADD with the climb deleted, and rejection
if `L561` enters in frame 0.

## Credit

The forward word and frame table are the pinned joint-query / selected-replay
sources. PR #3932 (Chris R / Clear1nsight) named event 9895 as the unpriced
successor of event 9894. The nested-frame rule is the retained local checker
contract. New check by unpaidmoon, with substantial Cursor Grok assistance.
Apache-2.0. No independent human or formal-kernel review.

## Open next questions

1. What physical head moves does this ADD cost once `L546` and `L561` are
   placed on real six-tape windows? Same-frame legality does not meter layout
   or the climb's kernel. The blocker is PR #3932's unbound intervals and head
   positions.
2. Which cleanup child returns `L546` from frame 4 to entrance frame 0? The
   in-frame inverse does not. The forward contract only admits strict rank
   increases, and no recipe child `(4, 0)` is present.
