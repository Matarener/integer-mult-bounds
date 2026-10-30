# In-place encoding across two invocations: scalar savings, no rank saving

Douglas Colkitt, with OpenAI Codex assistance. October 9, 2026. Apache-2.0.

**Stop the matched encode–shear–decode proposal. No new supplier or κ.**
The small schedule is correct for arbitrary original data and eliminates
independent scratch inputs. Sharing the encoding across two invocations
reduces its scalar gate count from 22 to 14. Nevertheless, a rational-lift
argument proves that every frame assignment for this template consumes at
least the entire available rank capacity before the endpoint correction.

This closes more than the particular frames tested: it permits distributed
gate frames, arbitrary matched reversible encoders and arbitrary idempotent
data labels. It does **not** close all use of original data as producer
storage. A characteristic-dependent circuit or changed outer contract need
not admit the rational lift used in this proof.

The selected conditional witness remains `κ=0.000661885549259598`. This is
a research diagnostic, not a modification of the selected finite word.

## First determine the allowance

The [preceding block screen](../higher-rank-sixteenth/REPORT.md) grants zero
central loss and ideal within-macro batching in a hypothetical two-axis
compiler. Let `M₀` be its moment with no auxiliary roles, and let

`A=(r/d)^(1−s)+(1−r/d)^(1−s)`.

If `ρ` is auxiliary roles per label per axis and `E` is any extra
unnormalized moment cost per data pair, contraction requires

`2ρ(A−1)+E < 2(1−M₀)`.

The following strict upper thresholds are enclosed by exact rational
intervals. They are necessary budgets, not constructions:

| Rank ratio | Supplier target | Maximum `ρ`, with `E=0` | Maximum `E`, with `ρ=0` |
| --- | ---: | ---: | ---: |
| `5/11` | bit `0.08` | 0.01039366186 | 0.001178559524 |
| `5/11` | complex `0.075` | 0.13839490484 | 0.01468607971 |
| `1/2` | bit `0.08` | 0.39239780895 | 0.04474750837 |
| `1/2` | complex `0.075` | 0.54584232520 | 0.05825342388 |

Thus merely reducing a one-role-per-label producer somewhat is insufficient
in these examples. At ratio `5/11`, the bit budget permits barely one
auxiliary role per hundred labels, even with every other extra cost erased.
The half-rank row is an optimistic control, not an available useful geometry.
The failed sunflower geometry is not reopened by these arithmetic budgets.

These allowances prompted a zero-independent-scratch attempt. Its actual
changed profile is charged below; deleting a role does not entitle us to
retain the old profile or its normalization.

## The explicit two-invocation schedule

Take `N` source registers `x` and `N` target registers `y`. Every original
register is arbitrary. Let `L` be an invertible XOR word acting in place
on a bank. Use the same `L` on both banks:

1. Encode `x←Lx` and `y←Ly`.
2. Execute `y←y+x` on corresponding encoded registers.
3. Execute `x←x+y` on corresponding encoded registers.
4. Decode both banks with `L⁻¹`.

The result over `F₂` is `(x,y)↦(y,x+y)`, exactly the two successive scalar
shears. No original value was assumed zero and no auxiliary role was added.

For the concrete three-label test, `L` consists chronologically of
`z₁+=z₀; z₂+=z₁`. Each invocation implemented separately encodes both
banks, applies one vector shear, and decodes both: 11 scalar gates. The
shared schedule has four encoding gates, six shear gates, and four decoding
gates: 14 in total. It removes actual repeated computation, not just storage.

The separate comparison here means **two independently encoded versions of
this same proposal**, not the selected PR186 supplier or its gate count.

## Outer cuts and complete physical obligations

For each label `i`, retain a rational idempotent `U_i` in dimension `m`.
The two banks have source frame labels `(U_i,0)` and sink labels
`(I,I−U_i)`, as in the inherited two-stage construction. For a projector
`P`, the partial interchange is represented on addresses by

`D_P = [[I−P,P],[P,I−P]]`.

It is an involution. A transition from frame `P` to frame `Q` has relative
address matrix `D_Q D_P`, whose off-diagonal block is

`(Q−P)(I−2P)`.

Since `(I−2P)²=I`, its rank is exactly `rank(Q−P)`. The screen grants a
single recursive child of that rank for each transition. This is favorable
rank-only accounting, not a new theorem implementing arbitrary full batching
or admitting nonreducing children into the production recurrence.

At the sink cuts, the physical outputs for each pair are

`X_i=F y_i`, `Y_i=F x_i+D_(I−U_i)y_i`, where `F=D_I`.

The retained endpoint correction transforms a **dependent copy** of `X_i`
by `D_(U_i)` and adds it to `Y_i`. It costs rank `rank(U_i)` and produces
`(F y_i,F x_i)`. The copied stream is discarded and does not enlarge the
number of independently varying roles or the recurrence normalization.

The finite-address replay uses three noncommuting rational line projectors,
`m=2`, and the eligible address prime three. It checks all 486 independent
input bits simultaneously across six roles and 81 addresses. Both separate
and fused words give the required outputs exactly. Removing the correction,
an address transition, or a decoder gate produces incorrect outputs.

## A paid higher-rank fragment

For an explicit larger ledger, let `p_t` project onto the line `(1,t)` in
`Q²`, for `t=0,1,−1`. Put `P_t=p_t⊗I₂` and `U_t=P_t⊗P_t`.
Thus the three data labels have rank four in dimension sixteen and are
not all commuting. Use intermediate cuts `E_t=I₄⊗P_t` and `E_t−U_t`.
These labels are controls for the schedule, not a claimed new finite core.

First-invocation encoder and cross-bank gates use the participating target's
`U_i` frame. Second-invocation gates use `I−U_i`. The separate word decodes
and crosses the intermediate cut; the fused word removes that cut and
retains the encoded registers through both shears. Every wire transition
from its previous frame is counted, including the final cuts.

There are six independent roles, so capacity is `Wm=96`:

| Schedule | Scalar gates | Rank before correction | Rank including correction |
| --- | ---: | ---: | ---: |
| Two separately encoded invocations | 22 | 344 | 356 |
| Shared distributed encoding | 14 | 232 | 244 |
| All gates at frame zero, sharpness control | 14 | 96 | 108 |

The shared schedule's optimistic bit moment at saving `0.08` is
approximately `2.6521703908`, far above one. Its child histogram including
correction is nine width-four, fourteen width-eight and six width-sixteen
children. Full-width calls are granted contribution one **only to make the
rejection favorable**; they do not define an admissible shrinking supplier.

The explicit frames are not optimized. The following proof is the reason
not to spend a frame-search budget: even the optimal rank total cannot
contract. The all-zero-frame control shows the lower bound is sharp before
correction, although its child splitting still prevents contraction.

## Why every matched encoder pays at least capacity

Use the rank-telescoping argument from the repository's
[characteristic-zero screen](../../docs/research/stronger-rank-screens.md).
That argument bounds

`rank(M_out(C⊗I_m)−(C⊗I_m)M_in)`

by the sum of frame-edge ranks. **Its telescoping identity does not require
`C` to be a permutation.** The earlier monomial condition was a sufficient
way to make the endpoint discrepancy full rank.

Every reversible CNOT encoder has an invertible rational lift `L_Q`: lift
forward additions to rational additions and lift each inverse word with
the corresponding subtraction. Choose the same lift for both banks.
Lift the second shear as `x←x−y`. Modulo two these are precisely the
original gates. At the rational scalar level, the complete word is

`(x,y)↦(−y,x+y)`.

This follows because `diag(L_Q,L_Q)` commutes with the two-bank shear
composite. The rational operations only certify an obstruction on the
same gate incidences; no rational scalar multiplication algorithm is being
substituted for the XOR circuit.

Reorder the terminal blocks by data pair. With the retained cuts, the
endpoint discrepancy for pair `i` is

`D_i = [[0,−I],[I−2U_i,I−U_i]]`.

It is invertible, with explicit inverse

`D_i⁻¹ = [[I−U_i,I−2U_i],[−I,0]]`.

Only `U_i²=U_i` is used. No symmetry, rank-one hypothesis, common basis or
commutation between different labels is required. Thus the total discrepancy
has rank `2Nm`.

At each scalar gate all its incidences share a frame, so its rational scalar
operation commutes with that frame. The only contributions to the telescoped
discrepancy are wire changes. Each edge contributes

`(b_e a_eᵀ)⊗(M_head(e)−M_tail(e))`,

whose rank is at most that edge's frame-difference rank. Subadditivity gives

`Σ_e rank(M_head(e)−M_tail(e)) ≥ 2Nm = Wm`.

This applies to **all** common-gate frame assignments on every matched
encode–shear–decode graph with this rational lift and these outer cuts.
It is not limited to a common frame for the entire computation. The small
checker independently reconstructs every edge's influence contribution and
verifies the complete nonpermutation telescoping matrix identity.

For `0<s<1` and widths `t≤m`, `(t/m)^(1−s)≥t/m`. Therefore capacity-level
rank already forces a raw moment at least one, even granting full-width
children and ideal packing. The paid endpoint correction only worsens it.
Granting that correction for free would not rescue this template.
This uses the retained full-volume rule: each charged child acts on one
original role's `V/(2N)` stream. A proved implementation with smaller-volume
or different typed children would change the hypothesis, not contradict it.

## Scope and next decision

This test genuinely borrowed original data registers, crossed an invocation
boundary, removed repeated gates and allowed different internal frames.
Those freedoms are insufficient when the completed scalar computation still
has the rational lift above. The previous two-gate common-frame rejection
alone would not have justified this all-frame conclusion.

Do not enlarge the encoder or tune its frames. A worthwhile in-place
successor must instead change a premise, for example by preserving the
existing characteristic-two-only central/side cancellation while sharing
physical data storage, rather than replacing it with matched invertible
encoding. Changing the outer cuts or the charged child contract would also
require a new complete implementation. None is supplied in this round.

The failure is **not** a proof that every in-place producer has a rational
lift, or that characteristic-dependent data borrowing is impossible. No
complex construction is claimed; the bit-side obstruction stops this
specific proposal before a complex implementation is justified.

Stop here: no larger solver search or second candidate was launched.

## Reproduction and provenance

```sh
python3 -B research/inplace-producer-sixteenth/audit.py --check research/inplace-producer-sixteenth/certificate.json
python3 -B -m unittest discover -s research/inplace-producer-sixteenth -p 'test_*.py'
make selected-record-check
```

The receipt pins the inherited block budget, two-stage endpoint source and
rank-screen argument. The two-stage and copied-correction construction
retains Aurel Prosz's, Zhihao Chen's, icekylinx's and its other contributors'
recorded provenance. The rational-lift screen follows the earlier external
research-agent suggestion and repository audit. This pass contributes a
scoped application to a nonpermutation boundary and a paid schedule check;
it asserts no priority for reversible conjugation or rank telescoping.
