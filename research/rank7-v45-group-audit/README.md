# Measured V45 price on a monotone 61-edit walk

**Partial frame-surrogate certificate. No new κ.** Selected κ stays
`0.001672660197076918`. PR #2979's conditional κ ≈ 0.001729 is not selected
and is not re-certified here.

Upstream main checked 2026-10-20 is still `bb4bccbf42844d2801487450727c2f63e10d1d0f`
(priority revision 6). The three replay inputs have the same git blobs there.

## What the open V45 audits already cover

[PR #3911](https://github.com/CrocSwap/integer-mult-bounds/pull/3911) rebuilds
the frame walk and the stage-one ledger. It toggles the four V45 endpoints
under all 139 gate edits, checks the 15 nonempty subset profiles, and gets
margins `−53,141`, `−27,770`, `−2,399` and `+22,972`. The `+78,512` figure in
that audit is the pinned V45 `joint_delta` minus an endpoint delta of
`−4·c_1`. Its open question is to rederive that group price on a monotone
walk. The blocker it records is that the 29 edits naming helpers 249, 251,
265 or 267 are nonmonotone at register 169.

[PR #3543](https://github.com/CrocSwap/integer-mult-bounds/pull/3543) checks
the printed intersection and the declared subset margins from the price table.
[PR #3823](https://github.com/CrocSwap/integer-mult-bounds/pull/3823) records
the 128-vector triple intersection `E_7 ∩ E_42 ∩ E_45`.
[PR #3841](https://github.com/CrocSwap/integer-mult-bounds/pull/3841) records
the printed arithmetic-progression ladder (difference 25,371) and the sum of
the five joint prices. Those three do not replay an isolated word.

## What this package adds

The stage-one record has 61 edits whose new frame is contained in the declared
V45 frame and in no other declared group frame: 20 in `B` and 41 in `restore`.
Twenty-nine of them name a V45 helper. That is the same set of 29 edits named
by #3911. The other 32 name only partner registers (14 in `B`, 18 in
`restore`; new-frame dimensions 18 of rank 7, 6 of rank 5, 4 of rank 6 and 4
of rank 4).

On both PR #2942 parents, replaying those 61 gate frames is monotone.

| Endpoints lowered | Measured profile delta | Margin `−Δ − k·2,091,300` |
|---:|---:|---:|
| 0 | **+78,512** | −78,512 |
| 1 |  | −53,141 |
| 2 |  | −27,770 |
| 3 |  | −2,399 |
| 4 | **−8,388,172** | **+22,972** |

The joint delta equals the measured gate-only cost minus four rank-1 tariffs:
`78512 − 4·2,116,671 = −8,388,172`. The weights are the published surrogate.
`STAGE-PRICES.json` is not read, so the overhead is a profile cost of this
walk. The same identity gives `4·25,371 − 78,512 = 22,972`.

The 29 role edits alone, with or without the four endpoint changes, are
nonmonotone at register 169 on both parents. That agrees with the blocker
stated in #3911. Extending those 29 by any one partner edit, still with
endpoints unchanged, stays nonmonotone. Separately, every 60-edit subset of
the joint walk is nonmonotone, so each partner edit is required in the
four-endpoint witness.

Every 60-edit subset of the 61 makes the four-endpoint walk nonmonotone. Two
role edits are a gate-only exception: omitting `restore` index 137, or
`restore` index 157, keeps the no-endpoint walk monotone and raises its cost
from 78,512 to 83,508. With all four endpoints lowered, those omissions fail
at registers 267 and 265. So the joint witness uses all 61 edits, and no
60-edit subset is a joint witness.

Scalars, operators and the cleanup list stay fixed. The private-buffer count
stays 86. The joint width inventory moves four units from width 8 to width 7.

## What this does not establish

The intersection, the printed ladder, the endpoint subsets of the full
139-edit word, and the physical invoice remain the subjects of #3823, #3841,
#3543 and #3911. This package does not rerun that ledger. Matching the pinned
V45 price on one monotone walk does not show that the frame search was
optimal. Groups A–D, idle packing, native admission and both supplier caps are
unchecked. A positive local margin in this surrogate is not a multiplication
exponent.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/rank7-v45-group-audit/verify.py
python3 -B scripts/research_package.py --package research/rank7-v45-group-audit
```

Expected first line:

```text
PASS_RANK7_V45_MONOTONE_SPLIT providers=2 containment_edits=61 role_edits=29 partner_only=32 sections=20+41 role_only_nonmonotone=169 measured_overhead=78512 joint_delta=-8388172 joint_margin=22972 single_margin=-53141 leave_one_out_joint=nonmonotone one_partner_extension=nonmonotone gate_only_omit_restore_137_or_157=83508
```

## Open next questions

1. Is there a proper subset of these 61 edits, necessarily omitting at least
   two of them, that stays monotone for every endpoint subset and still
   measures `+78,512` and `−8,388,172`? Every 60-edit subset fails the joint
   walk, and the two gate-only omissions above miss the joint price. A
   compensating pair remains unchecked. The missing frame-search witness also
   leaves optimality open.
2. Do groups A–D have an exclusive-containment superset of their
   helper-touching edits that is monotone and prices the group from profile
   costs? #3911's residual method still leaves those four group prices on the
   pinned row.
3. Does this local margin survive an independent enclosure of `c_r` at
   `b = 0.001703676387993676` and the idle-width cap? Until that is done, the
   unit margin does not move κ.

## Credit

Marius-Paul Dumitrean (Dugongue / mdumitrean), PR #2979, for the words, the
V45 claim and the published weights. The parent words descend from Mason
Hale's PR #2917 and the PR #2942 extractions. Frame climb rules are Jeremy
Kothe's, from the PR #2894 lineage. 1337isnot1337, PR #3911, for the
independent frame and ledger audit whose open question this walk answers.
jwr404, PRs #3543, #3823 and #3841, for the intersection and printed-ladder
checks cited above.

Prepared by unpaidmoon with substantial AI assistance (Cursor Grok). No
independent human or formal-kernel review is claimed. Apache-2.0.
