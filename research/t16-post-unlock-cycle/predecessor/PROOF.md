# A neutral swap unlocks a strict packing gain

This is a conditional finite packing construction on the literal PR3359 map,
head `3bdc260e996fd3a94dcb7560b68f2c61d2253d80`. It preserves the selected
seven-slot local word, its 480 helper widths, 144 complete calls and physical
invoice. The selected record is not changed.

## Literal exchange

An owner bin is `(owner_replica, child, port)`. Row indices are zero-based in
the complete 69,120-row owner array. The five rows are distinct.

- First swap the placements of rows 34864 and 43904. Their widths are 8 and 7.
- On the resulting map, rotate rows `(37210, 30301, 31680)` forward. Each row
  receives the placement of the next row, and the last receives the first.
  Their widths are 8, 9 and 9.
- After each step, compact offsets in each affected bin, sorted by old offset
  and then row index. The logical role, call, helper and width never change.

Only four bins change. Call their initial residual ranks `f`.

| Bin | Capacity | Initial f | After swap f | Final f |
|---|---:|---:|---:|---:|
| `(11,14,1)` | 32 | 0 | 1 | 0 |
| `(1,12,20)` | 48 | 1 | 0 | 0 |
| `(14,8,23)` | 48 | 1 | 1 | 2 |
| `(3,12,107)` | 48 | 0 | 0 | 0 |

The first step swaps the first two residuals, so its complete idle histogram
is unchanged. The second replaces two rank-one remainders by one rank-two
remainder. The shared bin `(11,14,1)` loses original rows 34864 and 37210 of
widths 8,8, and gains original rows 43904 and 31680 of widths 7,9. Its occupied
mass remains 32. This is outside a cycle contract with exactly one original
helper leaving and entering every affected bin.

Eighteen serialized rows change, including offsets; five helpers relocate.
Both the intermediate and final complete owner maps pass the independently
implemented R1-R7 and X1-X2 audit. It checks physical family identity, distinct
families within every call, chronological windows, capacity, disjoint prefix
slices, complete helper inventory and the exact profile. Both steps are
therefore legal under this fixed contract. The triple alone overfills a bin,
and is a rejection control rather than a gain on the initial map.

## Exact moment change

At every real `0 < a < 1`, the idle contribution changes by

`2^(1-a) - 2 < 0`.

The normalizing width and role count, all paid local children and every
additional invoice charge remain fixed. Rank mass stays 1,041,408 and deficit
stays 5,120. Thus the complex recursive moment strictly improves at every
such exponent. This inequality needs no floating-point search or root estimate.

Fresh exact pricing and the unchanged eleven-stage strict admission establish

`kappa = 1673627634134309 / 10^18 = 0.001673627634134309`.

The exact gain over PR3359 is `19027757 / 25000000000000000`, or
`0.000000000761110280`. The conservative path gives
`0.001673627631281533`. Both supplier bills, both seven-step bootstrap paths
and all 47 strict outer inequalities on each path pass. Complex still binds.

The complete typed physical invoice equals selected1094's invoice after
excluding only the template, owner-audit and controller-audit source hashes.
No charge, key, array order or value type is excluded. Prefix 397 remains paid
at 512 and the physical row coefficient stays 16,469. The actual chart census
is 10,005, down from 10,008; this does not reduce the retained invoice.

## Source and proof boundary

The 217-row predecessor patch reconstructs the complete PR3359 payload from
canonical PR2169 owner bytes. Its canonical hash agrees with the retained
PR3359 result. Input blobs and hashes are pinned in `SOURCES.json`, and the
unchanged PR1087 admission is extracted and authenticated from its canonical
archive. No unmerged Git object or network access is needed for replay.

The original compiler assertions remain enabled. The local provider is retained
source-bound evidence, not a fresh cold native reconstruction. This does not
prove an optimum, a universal packing obstruction, an unconditional
multiplication theorem, or new all-size/compiler, common-label/mutable-source,
whole-call hosting, precision/tape, exact-recovery, analytic-transfer or bit
H1-H5 premises. Those selected assumptions remain in force.

Credit Pierre / hexapode for PR3359's six composed cycles and its explicit
neutral-rearrangement question; Nick Petalas for PR3354/3338; Gonzalo Mier for
PR3308; Philippe Van Velzen for PR2169; and the retained Jeremy Kothe, Rohan Arun,
Hao Yan, George Lydakis and Josie Elliston compiler, owner, bit and moment lineage.
New material by Nick Petalas is Apache-2.0.
