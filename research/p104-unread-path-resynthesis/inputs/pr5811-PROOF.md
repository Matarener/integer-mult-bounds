# Compatibility and complete price of the accumulated-block composition

This proof concerns a fixed composition of PR5802 and PR5795, including
PR5796 through PR5795, followed by the separately released role92 accumulation.
It introduces no elementary accumulation or block-reframing identity. The full final-word replay checks exact scalar/transpose compatibility, role92 mutation controls, all 2919 distinct native maps with absolute phase, 1124 helper normalizers, 208 main adapters, the complete physical caller and the interval-price/compiler/outer calculation. Every
multiplication-exponent conclusion retains the five assumptions in Section 6.

## 1. Exact sources and the two-block intermediate

Let W be PR5802's word at
`9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62`. Its three accumulation steps are
already present. Block plans and the constructor are PR5795 at
`206cb717c0c07737d61637b93f7502ca48850348`, containing R22 edits from PR5739
at `b93d749a0a895d260e87887170af5162bda461a4` and the second-block plan from
PR5796 at `4b30391e633ba0c7c674f03586ae97d443e9bc9c`.

The block constructor is applied to W with its exact owned-label assertion
adapted from 25 to 28. This acknowledges W's existing buffers; the block stage
adds none. All eight R22 old runs match uniquely and their intervals are
disjoint. Endpoint joins are checked against their old charts. Existing chart
1090 is reused only after verifying its exact basis `[265,194,164,75]`.

The second block matches the released 90-operation and 12-operation scalar
runs on roles 57,81,92,224,225,227,229,234,742. Their 102 operations move from
chart 267 to new chart 1092, basis `[11,21,38,448]`; helper 742 starts and helper
225 ends there. Existing chart 1091 has basis `[11,21,51,469]` and is retained.
The constructor records 16 required native-edge changes, preserving earlier
edges in query chains and every unrelated query's order.

Call this intermediate V. It has 25,982 events and canonical JSON SHA256
`99d30f1ad0861259378630443a0c430f147f6156a5443d1d1cb72a420a7e05c3`.
The role92 step below is applied to V, not directly to the earlier source.

## 2. Block compatibility and retained COPY values

Decoded field values distinguish the logical state from its native encoding.
In a common frame, ADD and SCALE induce the stated rational linear maps.
A legal MOVE from encodings J_A to J_B must implement exactly J_B J_A^-1,
including absolute phase. Scalar matrix equality alone does not prove this
native obligation.

For each R22 replacement, the old and new rational transfer matrices agree
on the union of scalar operands. The largest is 9-by-9; the other nonempty
scalar matrix is 2-by-2; the remaining edits contain only native moves. No
replaced run contains COPY, INIT or CLEAR. Therefore, under the native-map
obligation, each replacement preserves the complete decoded state at its exit
for arbitrary entry values. Induction over the disjoint runs preserves the
state at every outside observation and lifetime boundary.

The second block preserves all scalar operands, coefficients and order. It
changes common frames, their required native connections and the two stated
helper boundaries. Its decoded scalar transfer is identical once those native
maps are established. The entire ordered INIT/COPY/CLEAR subsequence equals
that in W. All 23 source COPY operations retain their exact decoded payloads,
including the thirteen retained native copies. No arbitrary public helper
input is treated as a free zero. Exact forward replay on V covers all 798 coordinates and 636,804 coefficients.
The separate reverse-chronological transpose check is run on the final word below.

## 3. Realizing the released role92 plan after composition

The [released plan](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19205168)
was discovery evidence on exact PR5786, canonical word SHA256
`45e3f8efd004f2a6d2c02a2ac2ebe3dd9ce04c887641ec9ab31e47f8c7f41e1b`.
Its event and chart-node indices cannot be copied blindly to V. The remapping
matches the actual scalar observations by operands and coefficients. Old node
824 splits into nodes 824 and 1637, and old node 2002 becomes 2008; all other
selected nodes keep their indices. Both pieces of node 824 are included. The
resulting changed-node set is

```text
742,753,754,755,761,823,824,825,826,827,828,829,830,1637,2008.
```

The six source observations move from indices
`12850,12852,12854,12856,12858,12860` to
`12856,12858,12860,12862,12864,12866` in V. They add, with coefficient +1,
the current values of roles `63,61,103,18,45,108` to destination 92. These are
values at their actual observation times, not assumed unchanged initial inputs.

The declared nodes are assigned anchor chart 1091. Let A be chart 267,
with basis `[1,4,10,16,34,64,128,256]`, and B be chart 1091. Exact subspace
checks give B⊂A, with dimensions 4 and 8 respectively. The literal constructor
verifies all common scalar frames and nested directions after this chart
change. It also checks that between the first and last selected additions:
no ADD/COPY reads destination 92, and every operation writing that destination
is one of the six declared additions. A MOVE, SCALE, INIT, CLEAR or undeclared
write of that destination would fail the same contract.

Introduce owned role 798, initialized to zero in A. Replace the six additions
by additions to that buffer at the same observation times. After the last,
pay its rank-four native MOVE A→B, add it to role 92 in B, and CLEAR it in B.
The buffer contains the exact sum of the six observed values. Until delivery,
role 92 differs by the pending sum, but that difference is unobservable because
of the checked read barrier. Every other decoded value agrees by induction.
Delivery restores role 92 before any later read. The new buffer's erasure is
explicitly charged under the retained owned-erasure assumption.

The final overlay includes frame changes inside the intermediate block region;
its validity is not inferred from the intermediate's old physical maps.
Every new map and phase must be replayed. All 83 old lifecycle opcodes, roles and coefficients remain; their charts may refit,
and a separately computed trace confirms all 23 COPY payloads. The final word
has 25,984 events, 770 arbitrary public inputs, 29 owned labels, 31 lifetimes
and peak 13 live owned fields. It fits the unchanged 26,000-event and 1,000-slot
caps. The one explicit local checker capacity adaptation is `owned <= 28` to
`owned <= 29`; scalar allowance is recomputed as 225038. All other checks are
retained. Forward and separate dense transpose checks cover 799 coordinates
and 638,401 coefficients. Nine controls reject missing sum components/query,
delivery or CLEAR, an unallocated buffer, wrong sign, stale helper boundary,
an undeclared pending write and an early destination read.

The final canonical word SHA256 is
`a06445539ad73fe16deae66fef8c52ffc39f5f14c765eab3dc3d98e0e2d8074c`.
The literal plan is ROLE92-PLAN.json. HUNKS.json binds both intermediate and final canonical hashes. These hashes include the package schema strings; the earlier scratch receipts used predecessor schema names.

## 4. Local signs and complete caller invoice

Write H_r(t)=r^t. The final local profiles are

| Kind | Exact profile |
|---|---|
| Paid | 2226H1 +456H2 +498H3 +99H4 +162H5 +9H6 +6H7 |
| Helpers | 18H1 +7H2 +4H3 +107H4 +14H5 +9H7 +18H8 +385H9 |

For the block stage alone, direct recount relative to W gives

\[
\Delta P_B=2H_1+2H_4-2H_5,\qquad
\Delta T_B=-2H_1+2H_4+2H_5-2H_8.
\]

Thus its signed gain is `g(t)=-4+4·5^t−2·8^t`. It is not positive on all
`0<t<1`: g(0)=-2 and g(1)=0. Exact outward log/power bounds give
`g'(t) < −0.8479` throughout `[0.9966,1]`.
Consequently g(t)>0 for `0.9966≤t<1`, including the working exponent.

For the role92 overlay, the independently recounted changes relative to V are

\[
\Delta P_R=-5H_1-H_4+5H_5,\qquad
\Delta T_R=-4H_1+4H_5.
\]

Its gain is `H1+H4−H5`, strictly positive for `0<t<1` since
`(1+4)^t<1+4^t`. Paid local call count falls by one and helper count stays
fixed. Both rank masses increase by 16, leaving their difference unchanged;
the final local paid rank mass is 5934. In particular, the four changed helper
targets and all their new rank-five credit are accounted for explicitly.

Let P_0 and T_0 be the final local moments above. The full p16/a7 caller has

\[
P=18P_0+1560H_1+
208\sum_{\ell\in\{7,8\}}\sum_{j=1}^{\ell}H_{8(j+1)},
\]
\[
T=18T_0+208H_{145}+
208\sum_{\ell\in\{7,8\}}\sum_{j=1}^{\ell}H_{1+8(j+1)}.
\]

This retains 18 local invocations, 15 query shears and 3,120 whole idle jobs.
The result is 66,888 paid calls, 13,444 productive targets and rank-mass surplus
760. The full paid rank mass is R=239828 and the full productive rank mass
is 240588. The global precision envelope uses this full R, distinct from the
local paid rank mass 5934. Relative to PR5802, the signed moment gain is
`18·(−3H1+H4+3H5−2H8)`. Every scalar, owned, native, route, normalizer,
adapter and compiler charge still needs the actual physical caller ledger.

The separate `check_total_gain.py` recounts the actual word and the complete
invoice, authenticates all source bytes, and proves the total gain positive
throughout `0.9966≤t<1` using only rational atanh-series log enclosures and
`exp(-x)≥1-x`. Its derivative upper bound is less than −3.34908. Four
corrupt receipt controls reject omitted paid work, stale rank mass, a wrong
source head and a missing lifetime. This check complements the native replay.

## 5. Exact price and funded outer parameters

Define `F(k)=T(1−k)−P(1−k)`. Two rational interval implementations enclose the
same complete moments. Strict opposite endpoint signs give the raw crossing

\[
(0.00312418633663374,\ 0.00312418633663375).
\]

An exact negative derivative upper bound throughout `0≤k≤0.0034` proves
uniqueness in the retained admitted BIT range. The reserve margin
`(1−10^-12)T(1−k)−P(1−k)` is also strictly decreasing.
Its largest permitted tested `1e-14`-grid point is `0.00312418633564`; the next
point fails the reserve. Deducting the retained `5e-12` gap gives

\[
\kappa=0.00312418633064.
\]

The gain over PR5802's published value is exactly `0.00000082576064`.
This is a fixed-invoice, fixed-reserve calculation, not an optimum over other
words, parameters or BIT suppliers.

The pricing receipt checks cutoff 16, completion floor 17, offset 1/7, power
1024, decay 125/128, tail block 128, strict splitting/rounding margins and the
finite compiler threshold `H=80511200000000000`. All 54 strict outer
inequalities and four functional conditions are positive. The nonrecursive allowance uses all 31 owned lifetimes for routes, peak 13 live owned fields, 225038 scalar primitives and paid local rank mass 5934. Allocating 29 labels is below the retained 1000-slot allowance; the physical caller and ownership checks use the actual word. This funds the
compiler parameters under the retained compiler hypothesis; it does not
materialize the enormous uniform word or rounded integer multiplier.

## 6. Scope and attribution

The five retained assumptions are `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. The final-word native-phase, physical-caller and complete-price checks pass as author evidence within that conditional framework; this is not maintainer admission. Neither independent
human review nor formal-kernel verification is claimed. The selected repository
record is unchanged. General mixed-payload factorization and other active
construction searches are outside this fixed plan.

Ali Romman supplied PR5802, PR5795, PR5796, the original provisional role92
plan and the retained-copy/hub lineage. Joel Pulikkan/GamingPuzzled supplied R22.
Retain flyingviper, Cinna Davis, Jacob Alan Sussman, zxv, Cao Yifan and every
predecessor native/helper/controller/compiler/BIT notice. Mason Hale's new work
is the exact-source composition, role92 remapping, compatibility proof and
complete repricing, with substantial OpenAI Codex and separate-agent
assistance. The elementary identities retain their source credit. Apache-2.0.
