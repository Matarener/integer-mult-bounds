# A three-helper cycle on the selected T16 word

## Literal construction

The starting map is PR3338 at
`dba99522cef0028eaeda1da408a23ea9eec37df2`, not a newly selected frontier.
`predecessor.patch.json` reconstructs its complete owner payload from the
canonical PR2169 map. The 169 changed rows have checked preimages. The SHA256
of the entire canonical JSON result is checked against the exported PR3338
payload digest, not just the changed rows. `SOURCE-EXPORT.json` records the
original source blob, container digest, representation and retained-file hashes.
No unmerged Git object is needed by replay.

Write a bin as owner replica, idle child, port. The three original placements are:

| Row | Call time | Helper | Width | Bin | Capacity | Free rank |
|---|---:|---:|---:|---|---:|---:|
| 1811 | 3 | 371 | 5 | 0,0,63 | 16 | 2 |
| 2977 | 6 | 97 | 4 | 2,4,109 | 32 | 1 |
| 531 | 1 | 51 | 4 | 9,2,103 | 16 | 0 |

Move row 1811 into row 2977's bin, row 2977 into row 531's bin, and
row 531 into row 1811's bin. Each role retains its stage, source replica,
call time, helper and width. Copy all five physical placement fields together.
Compact only those three bins, in stable old-offset order. The free ranks,
in the table's bin order, become 3, 0, 0. Exactly three rows relocate and
four other rows change offsets. No role is split or reordered in its call.

The independent PR1091 owner auditor checks the complete 69,120-row map,
including actual event-derived windows, active-pair exclusion, one physical
family per helper per call, disjoint prefix slices and exact whole profile.
The original map passes the same audit. The unchanged PR1087 strict pipeline
then rebuilds the dispatch and physical charts and checks its own full contract.
The cycle is a witness, not a classification of all possible cycles or an optimum.

## Strict gain

For every `0 < p < 1`, strict concavity with the continuous value at zero gives

```text
(3/73)^p + 0 + 0 < (2/73)^p + (1/73)^p + 0.
```

Every other recursive child remains unchanged. Thus the complete complex
moment strictly decreases whenever the inherited physical charges stay fixed.
That last condition is checked by comparing the entire newly emitted selected
invoice with the selected invoice, excluding only its three rebound source
identifiers. All other keys, including future keys, must agree.

The resulting complete profile is
`{1:349718,2:60198,3:62320,4:20448,5:11808,7:2,8:1152,16:2,48:4880}`.
Rank mass remains 1,041,408 and deficit remains 5,120. The local word, helper
inventory, 144-call order and selected supplier contracts are unchanged.

## Full finite composition

Two exact moment engines check the native and conservative complex endpoints.
The retained bit endpoint remains
`1733427039589844234749/1000000000000000000000000`.
The native complex endpoint is
`419106571991632694507/250000000000000000000000`.
The complex side binds. The seven-step bootstrap and strict outer assembly give

```text
kappa = 2677792938271/1600000000000000
      = 0.001673620586419375.
```

This exceeds PR3338 by exactly `1047762837/10^18` and the selected headline
by exactly `960389342457/10^18`. The conservative path gives
`0.001673620583566572`. Actual chart count remains 10,008, global prefix
397 is still paid at 512, and physical row coefficient remains 16,469.
The full strict pipeline retains controls 69, 12, 6 and 15; the separately
implemented owner auditor adds eleven rejection controls. Ten package
behavioral groups run normally and with Python assertions disabled.

The fixed-word relaxation computed by `ceiling.ceiling()` gives
`kappa < 1690054109089/1001690054109089`. The exact fraction attained by
this witness is recorded in `RESULT.json`. This ceiling does not prove
attainability or global packing optimality.

## Scope

This is one conditional finite composition under the selected all-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
exact recovery, analytic transfer and bit H1-H5 premises. The selected native
ancestry is reused by source binding, not rebuilt cold. The unchanged strict
pipeline does rebuild the changed whole-owner controller, charts, finite invoice
and both supplier compositions. No unconditional multiplication theorem,
formal-kernel verification, independent human review or selected-frontier
update is claimed. Larger pending claims may use different unadmitted sources.
