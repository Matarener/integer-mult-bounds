# Retained native copies

## Source and claim

The source is PR5751 at `8483f9a679d06c1e270141dbc686a7e76e7a7522`.
Its package is `research/p104-paid-meeting-splits`. The source claim is
conditional kappa 0.00311301600. This package claims conditional kappa
0.00312192127 under the same five framework assumptions.

The complete source export is retained and authenticated before import.
PLAN.json binds the source word and each of the nine changes by canonical SHA256.
A canonical hash uses sorted JSON keys and compact separators.

All scalar rows below refer to decoded values. A native frame specifies the
physical encoding of each value. The public endpoint is

```text
T = I + sum e_(r+112) e_r^T, over the 104 live ports r.
```

Every helper input is arbitrary. Owned input columns are erased by INIT and
must be zero at exit. COPY does not turn a public helper into a free zero.

## Changed contact contract

The source requires a scalar operation to use fields in the same native frame.
The new construction can supply its source operand from a retained converted copy.
It does not assume that an earlier value remains available.

A chart node is the interval between successive MOVE, INIT or CLEAR operations
on one field. A scalar update does not change that field's chart node.
The constructor assigns a fixed new frame to each selected node.
Each main input and output keeps its source frame.

A source version is the interval after one write or native MOVE and before the
next such operation on that field. The constructor groups scalar reads by the
actual source role and version. For each group, it compares the source frame
with the frames of its consumers.

If the frames differ, the fixed plan has one other consumer frame B. Let A
be the source frame. Each accepted cache has B strictly contained in A.
The constructor emits these operations before its first changed use:

```text
INIT  cache at A
COPY  cache = source at A
MOVE  cache from A to B, as a paid owned query
```

It then uses cache for every source operand in B. It emits CLEAR after the
last such use. The source value has no write between these uses. The cache
also has no scalar write between COPY and CLEAR. Thus every redirected read
has exactly the decoded value of the original read.

The native MOVE changes the physical encoding and preserves the decoded value.
Its rank is dim(A)-dim(B). The verifier checks its exact native map and phase.
All changed public queries remain strictly forward and nested. All changed
owned queries remain strictly reverse and nested. A MOVE whose two frames
become identical is removed; it is the identity operator.

Induction over the scalar program proves the same decoded endpoint T. Each
inserted COPY reads a current value, and each CLEAR occurs after all uses.
Changing a helper boundary changes its native Gaussian target, so its new rank
must replace the old productive credit. The main endpoint and its adapters
remain fixed. The exact forward replay and a separate dense transpose replay
check every public and dirty owned input column.

## Fixed construction

The first four changes retain a dimension-four copy of a dimension-eight value.
Each copy serves one existing owned path and four helper corrections.
The next four changes retain intermediate copies for those paths. The last
change serves the remaining helper 705 contact. The table identifies the plan;
WITNESS.json gives each exact role, version, event interval and use list.

| Step | New frame | Added cache lifetimes | Removed identity transports |
|---|---:|---:|---:|
| 1 | 1090 | 1 | 0 |
| 2 | 1091 | 1 | 0 |
| 3 | 240 | 1 | 0 |
| 4 | 243 | 1 | 0 |
| 5 | 260 | 2 | 3 |
| 6 | 394 | 2 | 3 |
| 7 | 431 | 2 | 3 |
| 8 | 470 | 2 | 3 |
| 9 | 549 | 1 | 1 |

Frame 1090 has basis `[265,194,164,75]`. This basis is credited to Joel Pulikkan /
GamingPuzzled in PR5739. Frame 1091 has basis `[11,21,51,469]`. Its span is the
sum of the relevant source subspaces. The R22 block edits are not used here.
The other frame definitions are unchanged source data.

There are thirteen new paid conversions and thirteen removed identity
transports. The final word has 25,882 instructions, 767 public inputs and
22 owned labels. It has 24 owned lifetimes and peak 12 live owned fields.
The scalar replay checks all 789 input columns. The transpose checks the same
622,521 endpoint coefficients by a separate arithmetic implementation.

## Strict signed-moment gain

Let H_r = r^t for 0<t<1. P counts paid children and T counts productive targets.
The exact local changes are

```text
Delta P = 12H1 + 4H3 + 4H4 - 16H5 + H6 - 5H7,
Delta T = 4H3 + 12H4 + H7 - 17H8.
```

Both call counts stay fixed. Paid and productive rank mass each fall by 69.
After cancellation, the signed gain is

```text
Delta(T-P) = 8H4 + 16H5 + 6H7 - 12H1 - H6 - 17H8.
```

Form two sorted lists:

```text
x = [4 repeated 8 times, 5 repeated 16 times, 7 repeated 6 times],
y = [1 repeated 12 times, 6, 8 repeated 17 times].
```

Both lists have 30 entries and sum 154. Every ascending prefix sum of x is at
least the corresponding prefix sum of y. Their differences are

```text
3,6,9,12,15,18,21,24,28,32,36,40,39,36,33,
30,27,24,21,18,15,12,9,6,5,4,3,2,1,0.
```

Thus y majorizes x. Strict concavity of r^t gives
sum x_i^t > sum y_i^t for every 0<t<1. This proves the signed-moment gain
throughout that interval. It does not by itself prove compiler closure.

The final local paid profile is
`{1:2231,2:454,3:496,4:96,5:159,6:7,7:10}`.
The helper profile is
`{1:25,2:5,3:4,4:103,5:6,7:7,8:21,9:388}`.
The unchanged complete caller makes 18 forward local calls. It also retains
15 query shears and 3,120 whole idle jobs. The complete bill has 66,834 paid
calls,13,390 targets and rank surplus760. No idle or thin query is omitted.

## Complete conditional price

Two rational interval engines check the complete power sums. The declared
saving is 0.00312192127; the tested saving is 0.003121921275. Both are below the
certified raw crossing (0.00312192130450, 0.00312192130451). A derivative bound proves a unique
raw crossing on [0,0.0034].

The completion parameters remain cutoff 16, floor 17, tail offset 1/7,
power 1024, reserve 10^-12, decay 125/128 and tail block 128. The verifier checks
all three strict tail ratios, both decay blocks, completion, splitting,
rounding, complement capacity and the finite compiler threshold. It checks
all 54 strict and four functional outer inequalities. Admitted BIT 0.0034
remains above the tested saving.

The new finite envelope changes two source caps:22 owned labels and peak 12
live owned fields. The public and operation caps stay fixed. All789 labels
fit the retained1,000-slot allowance. Every new lifetime has INIT, COPY,
a paid native MOVE, its actual reads and CLEAR.

The scalar allowance is 224,294 units. The local route allowance is 5,291,000
units. Their sum is below 10^7. The complete ordinary bound is 184,647,552,
below 10^9. The source growth bound 2^(16*26000) still covers the scalar word.
The paid native rank mass is 5,918, and the verifier records the corresponding
tensor norm bound. These are declared bounds, not measured attained norms.

## Verification boundary

The tests check the exact source bytes, nine fixed transformations, all scalar
columns, ownership, native maps and absolute phases. They also check the full
physical caller, complete paid and target inventories, compiler and outer price.
Controls remove a paid cache query, change its copied value, clear a live cache,
omit CLEAR, omit storage, retain an old target credit and falsify the invoice.
Each control must fail in normal and optimized Python.

The search used finite common-frame graph cuts and actual source versions.
It also added subspaces from sums of neighboring native subspaces. Nine accepted
steps passed exact scalar replay. The last bounded scan found no additional gain.
This is not a global optimum or an exclusion of other retained-copy graphs.
The optimizer is not required for replay; the fixed plan supplies every choice.

The five assumptions native_all_columns, owned_erasure, compiler, precision_tape
and analytic_recovery remain. The large uniform word and rounded multiplier
are not materialized. Author checks do not establish independent acceptance.
The selected frontier is unchanged.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
