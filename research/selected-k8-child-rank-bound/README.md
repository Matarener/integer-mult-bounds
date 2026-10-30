# Largest paid child rank of the selected k8 word

**Scoped rank bound. No new κ.** The selected conditional result stays
`0.001672660197076918`.

The rank-cap handoff on the selected complex local word asks for the largest
child rank a physical word on that template can emit, counting frame climbs
and the cone restrictions that restoration imposes. On the selected k8 word,
content hash `c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`,
the answer is **8**.

## Contract

Frames are subspaces of `F2^9`. A legal assignment may change the frame of any
A, B or early-cleanup gate inside its forward/backward interval. Frames stay
nested along each register. Centre and target pins, start and end frames, and
the low-end cone ceilings stay fixed. This is the frame contract of the
selected word's native auditor, enlarged only by charging a climb into a pin
instead of requiring that climb to be zero.

A paid child is one of two things:

- a strict climb of dimension `d = dim(F') - dim(F)` on one register edge;
- one of the eight centre descents, read off the fixed centre frames and the
  cut.

Each register pays its own climb. Idle packing at rank up to 51 is not a child
of this word.

## Result

Every legal assignment obeys the following, recomputed from the pinned word:

| Fact | Value |
|---|---|
| Largest graph climb | **5** |
| Centre descents | eight children, each of rank **8** |
| Largest paid child rank | **8**, attained by those descents |
| Rank 44 emitted | no |
| Free / forced gates | 1,741 / 3,672 |
| Interval sizes | 1,098 gates with 2 frames, 613 with 5, 30 with 16 |
| Edges whose interval allows a jump above the recorded jump | 3,222 (multiplicity) |
| Same climb cap with cone ceilings removed | still 5 |

The 82 register-edges that can jump by 5 are exactly the support of rank 5.
Their interval minima are 5 (32 edges), 4 (26) and 3 (24). The recorded word
uses jump 5 on all 82, so rank 5 is attained and no legal assignment adds
another rank-5 climb. Fifty of those edges can drop. Other edges can rise
only as far as 4. No edge interval contains a jump of 6 or more. Reassignment
can move mass among ranks 1 through 5. It cannot create a paid child of rank
9, 16, 44 or 51.

A second walk, charging the recorded sections the way the native auditor does,
reproduces the published profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`.
The two routes share no climb loop. The free-gate and interval counts match
the census already published for this word's moment bound.

The ambient lemma is separate and weaker: any nested pair of subspaces of
`F2^9` jumps by at most 9. The edge intervals give 5. A vector with bit 9 set
is rejected. A claimed cap of 4 is rejected because 82 edges allow 5.

## What this does not say

This is the native climb alphabet of one fixed scalar word. It does not price
a different child identity that bundles several rank-1 climbs into one block
child, and it does not rerun the moment duals. A block whose rank is the
number of gathered payloads would be a changed tariff. The recorded word has
no single-gate incoming climb mass above 8, but that observation is not a
census of multi-gate co-frame groups. Changed gates, entrances or end frames
can leave this interval data.

No supplier, invoice, native admission or selected-frontier change is claimed.

## Reproduce

Python 3.12, standard library only, from the repository root. About two
seconds.

```sh
python3.12 -I -B research/selected-k8-child-rank-bound/verify.py
python3.12 -B scripts/research_package.py --package research/selected-k8-child-rank-bound
```

Expected final line:

```text
PASS_SELECTED_K8_CHILD_RANK_BOUND max_paid_rank=8 max_climb=5 centre=8x8 rank44=0 free_gates=1741 increasable_edges=3222 no_new_kappa
```

`verify.py --write` regenerates `RESULT.json`. Without `--write` the checker
requires that receipt byte for byte.

## Open next questions

- **Can one co-frame block on this same word have rank above 8?** The native
  alphabet charges each climb separately, so a block child is a different
  identity. The frames needed for that census are the intervals built here.
  Owned temporary lifetimes are still not in the word archive, which is the
  remaining blocker named by the co-frame gate screen.
- **Does one legal scalar edit open a register edge of jump 6 or more?** The
  cap of 5 is a property of this gate list and these pins. A rewrite has to
  change an interval before the rank bound moves.

## Credit

The word, the `F2^9` frame contract and the published interval census are the
selected k8 frame-ceiling package (PR #1671, Gareth Davidson, using navinor's
frame method and the gauge44 auditor). The rank-44 threshold this bound is
compared with is the open question in Discussion #1166 comment 19021222,
recorded from PR #3701. The separate block-reblocking tariff is PR #3039,
PR #3066 and `research/rank-shape-coframe-bill-seed850bc3`. This package does
not import those programs.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human or formal-kernel review is claimed. Apache-2.0.
