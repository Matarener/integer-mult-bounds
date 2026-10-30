# A typed exclusion for the fixed PR5660 delta

## The programs and edit

Let P and Q be typed public programs with the same frame inventory. A public role's required scalar contacts follow a nondecreasing chain of subspaces; a public MOVE either changes nothing or strictly increases the subspace. Every ADD uses a common chart for both operands. These are premises on both programs. Source code declaring or checking a condition is not by itself an independent replay of an actual word.

Work in the scalar-plus-owned skeleton: omit public MOVEs, retain owned MOVEs and every scalar, lifetime and protected observation event. Public transport remains governed by the typed path premise. An observer below means a skeleton event or protected observation touching a specified role; the public MOVEs required to reach the next chart are not forbidden observers.

Write `C=165`, `H=586`, `S=733`, `X=21`. The indices are zero-based indices in the old skeleton, not full-word event indices. The exact edit deletes:

| Label | Old index | ADD | Frame | Dimension |
| --- | --- | --- | --- | --- |
| O1 | 12513 | `H += -4 S` | 597 | 1 |
| O2 | 12753 | `C += 2 S` | 597 | 1 |
| O3 | 12754 | `C += -1/2 X` | 652 | 2 |
| O4 | 12755 | `X += H` | 652 | 2 |

At the old O4 position it inserts this consecutive skeleton block:

| Label | ADD | Frame | Dimension |
| --- | --- | --- | --- |
| E1 | `C += 1/2 H` | 3 | 0 |
| E2 | `H += -4 S` | 597 | 1 |
| E3 | `X += H` | 652 | 2 |
| E4 | `C += -1/2 X` | 652 | 2 |

The bases are exactly `[]`, `[82]`, `[82,268]` for frames 3, 597, 652. Every other skeleton event is preserved unchanged and in order. Every surviving event strictly between old indices 12513 and 12755 is disjoint from `{C,H,S}`. There is no assumed isolation for X. The exact indices imply that O2,O3,O4 are consecutive, stronger than merely asserting adjacency of the last pair.

These premises are bound to [the copied witness](inputs/pr5660-WITNESS.json) and [constructor](inputs/pr5660-construct.py): skeleton at lines 20–21; frame-preserving rebuild and public monotonicity at 24–58; exact anchors/roles/replacement at 92–110; isolation and final-pair adjacency at 111–115; ordered deletion/insertion at 117–123. The frame inventory is preserved by `deepcopy` and replacement of only `program` in `rebuild` (the later schema tag is irrelevant). The published code's replay and cost checks are not premises proven here.

Let φ be the order-preserving survivor map from old events outside `{O1,O2,O3,O4}` to their unchanged new occurrences. E1–E4 are new occurrences. In particular O1 and E2 are different provenance labels even though their instruction bytes agree. Equal-looking instructions elsewhere do not define φ.

## The motif and the meaning of new incidence

Let a,b,d be distinct public roles, and let α,β be nonzero exact coefficients. The motif has four ordered scalar anchors:

$$
\begin{aligned}
M_1 &: a \mathrel{+}= \alpha b && (\dim=1),\\
M_2 &: b \mathrel{+}= \beta d && (\dim=3),\\
M_3 &: a \mathrel{-}= \alpha b && (\dim=5),\\
M_4 &: b \mathrel{-}= \beta d && (\dim=7).
\end{aligned}
$$

The middle role b follows the complete absolute dimension-zero to dimension-nine route with five positive MOVE ranks `(1,2,2,2,2)`. The four anchors are its only interior required contacts. Extra scalar contacts to b before the corridor at its unchanged dimension-zero endpoint, and after it at its unchanged dimension-nine endpoint, are allowed. Every other skeleton event or protected observation strictly between M1 and M4 is disjoint from `{a,b,d}`. The absolute starting dimension zero is essential: the rank partition alone would not fix anchor dimensions 1,3,5,7.

The familiar scalar identity replaces these four gates by `a -= αβ d`, restoring b. We assert no novelty for that identity, and prove no positive native or economic realization of it. Other retained operand, endpoint, target and native conditions can only restrict this necessary typed motif class further.

A **new incidence under this edit** is a motif in Q satisfying either:

1. One of its four anchors is an inserted E event; or
2. All four anchors are survivors under φ, with the same old role/edge/coefficient pattern, and their old corridor failed the strict observer condition solely because at least one removed O event touched `{a,b,d}`.

An old valid motif, changed economics of an existing motif, newly excused surviving observers and changed route predicates are outside this definition.

**Proposition.** For every typed P and valid Q satisfying the fixed edit, frame, isolation and adjacency premises above, there is no new incidence in this motif class.

## Case 1: an inserted anchor

The inserted dimensions are 0,1,2,2. The motif anchor dimensions are 1,3,5,7. Thus only E2 could be a motif anchor, and it must be M1. This fixes `a=H`, `b=S`, `α=-4`.

The immediately next skeleton event E3 reads H=a and writes X. It cannot be M2 or M4, whose destination must be S. It cannot be M3, whose destination/source must be H/S at dimension five. No remaining anchors fit before the immediately following event. E3 is consequently a forbidden observer inside the unfinished motif corridor. This contradiction excludes every inserted-anchor incidence. Additional endpoint contacts and intervening public transport do not remove the E3 read.

## Case 2: a removed old barrier

All anchors now survive. Let R=`{a,b,d}`. Some deleted O touches R by the case definition. The union of roles touched by the deleted events equals the union touched by the inserted block, namely `{C,H,S,X}`. Hence at least one E event touches R.

The E block is consecutive in the skeleton and contains no motif anchor in this case. It cannot lie inside the new corridor, since its R-touching event would be a forbidden observer. Therefore all motif anchors lie before the block or all lie after it. If they all lay after it, their old preimages would follow O4; every deleted event would precede the old corridor and none could be its barrier. All four anchors must therefore precede the block.

The last possible surviving old index before O4 is 12752, because 12753,12754,12755 are consecutive deleted positions. O2,O3,O4 therefore cannot lie inside this old corridor. Only O1 can be the lost barrier. This closes X-only possibilities without assuming X isolation: both deleted events involving X are in the terminal cluster, outside the corridor.

For the old corridor to contain O1, M4's old preimage lies strictly between O1 and O2, hence within the isolation interval. M4 touches b,d and survives, so both b,d lie outside `{C,H,S}`. O1 touches R but only has roles H,S. Thus `a=H` or `a=S`.

M3 touches that a in `{C,H,S}`. Isolation prevents M3 from lying strictly between O1 and O4. It precedes M4 in that interval and is a survivor, so M3 must precede O1. But M3 requires a at dimension five and later O1 requires the same a at dimension one. The typed old public chronology forbids that decrease. This contradiction excludes the removed-barrier case.

The two cases exhaust the stated definition of new incidence. The proposition follows.

## What follows from the proposition

No occurrence lookup can discover a newly created motif in this closed delta class if the premises hold. This is the useful source-specific stop decision. It neither counts nor excludes motifs already present in P, and it says nothing about other rank partitions, translated starting charts, observer contracts, changed economics, changed scalar graphs or successor releases.

The proof needs no inversion of the final WORD. Although the declared edit has a deterministic skeleton preimage once a final E block is bound, invertibility does not identify that preimage with the historical PR5650 payload. No equality with that payload is claimed. Actual word custody, typing/native validity and whole-word coverage remain separate obligations.
