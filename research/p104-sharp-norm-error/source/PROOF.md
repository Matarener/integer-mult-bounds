# Pending sums with one native conversion

## Exact source

The source is PR5786 at `6b936acd68a7e0f9062037900f0fe9bc4b6fdd25`.
Its complete 19-file export is retained. The source loader authenticates each
byte before import. PLAN.json binds the source word and each intermediate
word by canonical SHA256. Canonical JSON has sorted keys and compact separators.

Every public input is arbitrary. The decoded endpoint is

```text
T = I + sum e_(r+112) e_r^T, over the 104 live ports r.
```

All helper outputs are independent targets. Owned input columns are erased
by INIT and are zero at exit, under the retained owned-erasure assumption.
No public helper is treated as a free zero.

## Accumulation identity

Consider additions `d += q_i*s_i` between two reads of destination d.
There is no other write, SCALE, MOVE, INIT or CLEAR of d inside the chosen
interval. No operation reads d inside that interval. A fixed chart change
places d in frame B and each source s_i in frame A, where B is a strict
subspace of A.

Initialize an owned buffer h to zero in A. Replace the selected additions
by `h += q_i*s_i`, in their original order and at their original times.
After the last addition, execute

```text
MOVE h from A to B, as a paid owned native query
ADD  d += h in B
CLEAR h in B
```

Before delivery, h has decoded value `sum q_i*s_i`, with each source read at
its actual time. The value of d can differ from its original intermediate
value, but no operation can observe that difference. All other decoded values
remain equal by induction. Delivery restores d's complete value before its
next read. Thus the changed block has the same arbitrary-input endpoint.

The constructor checks this read barrier in the literal source. It does not
infer a barrier from a net matrix identity or a source label. Each scalar
operation uses its actual common frame. The native query has rank
`dim(A)-dim(B)` and preserves the decoded value. Its exact map and absolute
phase are checked by the retained Clifford compiler and a separate interpreter.

## Three fixed blocks

A chart node is a field interval between MOVE, INIT or CLEAR operations.
The fixed plan changes selected chart nodes. Main input and output frames
stay fixed. The source event indices below belong to the input of that step.

| Step | Destination | Sum frame | Destination frame | Source additions | Query rank |
|---|---:|---:|---:|---|---:|
| 1 | 146 | 531 | 529 | 13104,13110 | 1 |
| 2 | 173 | 559 | 549 | 13478,13484 | 1 |
| 3 | 151 | 543 | 541 | 13290,13296 | 1 |

Every sum frame has dimension 8; every destination frame has dimension 7.
The additions retain their source operands and coefficients. The three new
buffers have explicit INIT, their two ADDs, MOVE, delivery and CLEAR.
Changing the other chart nodes makes five source queries identities, so those
queries are removed. Every other public query remains forward and nested;
every other owned query remains reverse and nested.

The final word has 770 public inputs and 28 owned labels. Its 30 owned lifetimes
have peak13 simultaneous live fields. All798 input columns are checked in a
forward replay and a separate dense transpose replay, for 636804 coefficients.
The local operation count stays below 26000, and all 798 labels fit the retained
1000-slot allowance. The source scalar-growth bound remains applicable.

## Strict gain throughout the concave interval

Write H_r=r^t, with 0<t<1. The exact local changes are

```text
Delta P = -6H1 + 4H2 + 2H6 - 2H7,
Delta T = -2H1 + 2H2 + 2H7 - 2H8.
```

Paid call count falls by two. Target count and both rank masses stay fixed.
The signed gain is

```text
Delta(T-P) = 2*((2H1-H2)+(2H7-H6-H8)).
```

The first bracket is positive because 2^t<2. The second is positive by strict
concavity at the distinct points 6 and 8. Thus the gain is strict for every
0<t<1. A separate padded-majorization check compares

```text
[1,1,1,1,7,7,7,7] and [0,0,2,2,6,6,8,8].
```

Both sums are 32. The ascending prefix differences are
`[1,2,1,0,1,2,1,0]`. The zero entries contribute zero for every permitted t.
This arithmetic argument does not replace the complete compiler checks.

The final local paid profile is
`{1:2229,2:456,3:498,4:98,5:159,6:9,7:6}`.
The helper profile is
`{1:24,2:7,3:4,4:105,5:8,7:9,8:20,9:385}`.
The paid rank mass remains 5918. The scalar allowance is 225026.

## Complete caller and price

The source p16/a7 caller still makes 18 forward local calls,15 query shears
and 3120 whole idle jobs. The complete paid count falls from 66906 to 66870.
There are 13444 targets and rank surplus 760. No local call, idle or thin query
is omitted. The largest target rank is 145; the largest paid rank is 72.

Two rational interval engines check the full invoice. The declared kappa is
0.00312336057; the tested saving is 0.003123360575. RESULT.json contains the
strict raw crossing enclosure and the derivative bound that proves uniqueness
on [0,0.0034]. That crossing is a ceiling for this fixed full invoice, not a
universal limit on accumulation or native words. It is the applicable
replacement for historical fixed-inventory packing caps.

The completion choices remain cutoff 16, floor 17, offset 1/7, power 1024,
reserve 10^-12, decay 125/128 and tail block 128. All three strict tail ratios,
completion, splitting, rounding, complement capacity and the finite compiler
threshold are checked. The exact outer ledger has 54 strict and four functional
checks. The unchanged admitted BIT saving 0.0034 exceeds the tested saving.

All copies, scalars, normalizers, adapters, owned operations and routes remain
charged. The local ordinary allowance stays below 10^7 and the whole ordinary
allowance below 10^9. The only local verifier cap change is 25 to 28 owned labels.
The public, operation, peak-live and scalar-growth caps stay fixed.

## Overlap and limits

The verifier preserves the event subsequences and public boundaries for the
original R22 roles and PR5796's 102-contact roles. All23 source COPY operations
keep their roles, coefficients and exact decoded values. Some physical COPY
frames change with the new chart plan; the native and scalar checks cover them.
No R22 composition is claimed. The larger provisional role 92 accumulation
was excluded because it touches the parallel block investigation.

Controls remove a sum component, query, delivery, CLEAR or owned slot; change
the delivery sign; clear before delivery; read a destination before delivery;
retain an old target credit; and falsify the complete invoice. Each must fail.
The retained caller and native phase controls also run.

The five assumptions native_all_columns, owned_erasure, compiler, precision_tape
and analytic_recovery remain. The large uniform word and rounded multiplier are
not materialized. Author checks are not independent scientific acceptance.
The selected frontier is unchanged.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
