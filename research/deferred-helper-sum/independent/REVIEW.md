# Independent review of the deferred pair chart

The proposed omitted rank-four visit is impossible in the fixed two-cell
temporal model below. The single-shear consumer is an exact local operator,
but both physical helper rows still reach the rank-four frame. Keeping that
same mixed chart across the next two direct source events also fails their
unchanged frame labels. These are necessary frame facts, with a sharp bound
on the pair-entry subtotal; they are not a full paid-cost optimum.

This review and `check.py` were prepared with substantial OpenAI Codex GPT-6.1
Sol assistance. The checker was written independently of the package's primary
and design implementations. It imports and executes no frozen source Python,
primary checker, or design checker. The word/frame contract was read from the
credited PR4076 `audit_core.py`; the retained source authors' mathematical
premises are not being re-certified as a new physical supplier. This is not
independent human review or a formal-kernel proof. Apache-2.0.

## Exact source and finite witness

The containing PR4096 head is
`8d1e3b9399a2a7914f1ab538242cf2e6e6c4cd9f`, with PR4076 head
`9744f9df268590295a9872b1952c695a678192b9` and canonical base
`bb4bccbf42844d2801487450727c2f63e10d1d0f`. The checker fixes the outer
`SOURCE-EXPORT.json` SHA256 to
`323edf5ff6415abbb60253f64c548c24d63cee499519787a6ffa334acd74861b`,
then verifies every listed SHA256 and Git blob and the nested PR4076 manifest.
It parses the same authenticated NEW word bytes, with duplicate JSON keys
rejected. No imported bytecode is evidence.

Coverage is exactly the two frozen `NEW-base` and `NEW-extra` providers.
The local neighborhood has eight arbitrary current values

```
x=608, y=609, z=610, w=612, s=410, t=417, u=419, v=421.
```

There are 632 live inputs and 91 separate arbitrary dirty private buffers.
Every gate before the entry cut has an explicit inverse: a shear with its
coefficient negated, a nonzero scale with its reciprocal, or an invertible
native symbol. The buffers are untouched. Thus the prefix is bijective, and
all 723 current coordinates are independent immediately after native
operations 33--36 and before B948. This argument is repeated through B961 for
the next source cut. No evolved factory value is assumed clean or correlated
with the current helper coordinates.

Column-wise execution of B948:962 gives the following complete eight-row
operator, independently compared against these hand-derived formulas:

```
x' = x-s+t+u,            y' = y-s-t-v,
z' = z-x-y+s-u+v,        w' = w-t-u-v,
(s',t',u',v') = (s,t,u,v).
```

All other 715 coordinates are unchanged by this local block. The two source
columns in the pair are

```
A = [ -1   1 ]          det A = 2.
    [ -1  -1 ]
```

This is an exact coefficient computation on arbitrary current states, not
sampling. The local block contains only scalar gates, so no commutation of
native symbols is assumed. In the chart `X=x+y, Y=y`, its exact pair rows are

```
X' = X-2s+u-v,          Y' = Y-s-t-v,
A_chart = [ -2   0 ]    det A_chart = 2.
          [ -1  -1 ]
```

The thirteen-gate consumer in `RESULT.json` realizes the full conjugated
eight-row matrix. Both chronological inverse orders compose to the identity.
An entry `x+=y` at E and exit `x-=y` at F give a legal fifteen-gate replacement
for the fourteen source gates. Every local positive paid frame change is the
same, including those of the two dirty receivers. The checker uses reduced
XOR bases for binary frames, independently of the source's point-set masks.

## The all-chart argument and its exact temporal extension

Work over Q; this includes every admitted invertible dyadic scalar chart.
Initially the physical pair is an invertible scalar chart of the raw pair
only, at

```
E=span(97,45)=span(76,45), dim E=2,
F=span(144,75,42,7),     dim F=4, E contained in F.
```

The following restrictions define the covered temporal class:

1. The pair has two mutable physical scalar cells. Every change of chart is
   physically realized by invertible pair-only scalar operations. A pair gate
   touches both operands at a common binary frame. Individual nonzero scales
   are allowed separately.
2. Frames grow by containment, and neither pair cell has a native operation
   that can reset or reorient its frame. Free physical relabeling is not an
   operation in this model.
3. The independent current source values can enter the pair only through
   outside interactions at exactly F. There is no additional external
   storage, earlier low-frame source query, substituted source recovery, or
   changed source-frame gate. The actual four external sources are read-only
   throughout this neighborhood.
4. Immediately after B961, the physical pair must equal an invertible scalar
   chart `T(x',y')`, without an external-register offset. The logical delivery
   is not postponed beyond this cut. Its source410/source417 influence matrix
   is therefore `T A`, of rank two.

For a constant chart, a nonzero row cannot annihilate both columns of A.
Consequently both rows have a nonzero source requirement. Applying that
constant-matrix argument independently at successive times would not prove a
temporal statement; the following chronological argument is needed.

Suppose one physical row never attained exactly F. Only the other row can
receive external source influence at F directly. Before an operation first
mixes this F-bearing cell with the avoiding cell, the pair's external
coefficient matrix has rank at most one: its other row is zero. If no such
operation occurs, this remains true at the endpoint.

At the first such pair operation, its common frame G contains F by
monotonicity. If G equals F, both cells have attained F. If G strictly
contains F, both cells thereafter contain that strict superframe. Neither can
participate in a later exact-F source gate. The pair-only operations remaining
cannot increase the external rank from at most one to two. This contradicts
the rank-two endpoint `T A` in every case. Therefore **both physical cells
must attain exactly F**, even when a proposed avoidance jumps one of them
directly to a larger frame.

For `H_r=r^p`, `0<p<1`, each monotone E-to-F path has positive dimension
increments summing to two. Subadditivity gives `sum_j H_(d_j) >= H_2`.
The pair-entry subtotal is therefore at least `2H_2`, attained by the inherited
two direct raises. This does not optimize later paths, other helpers, native
operations, source access, restoration, owner placement, or a changed graph.
Replacing two rank-two increments by one rank-four increment would have
signed cost delta `H_4-2H_2<0`; this particular omitted-visit mechanism is
excluded by the stated source and endpoint restrictions.

## Persistent charts and the next source labels

The independently checked next events are

```
B962: x += 278,  U=span(266,138,75,42,26,7),
B963: y += 276,  V=span(272,144,72,41,4,3).
```

Both dimensions are six, the intersection has dimension five, and their join
has dimension seven. Explicit witnesses are `26 in U \ V` and `3 in V \ U`.
Both source labels contain F. Their current source coordinates are independent
by the same invertible-prefix argument.

This argument covers a **constant chart and direct conjugation of these fixed
source events at U and V**. Their pair update columns are `T e1` and `T e2`.
A physical row with both entries nonzero must take a U gate and then a V gate,
which is impossible for a monotone frame. Every admissible row in this fixed
event model has at most one nonzero entry; invertibility forces T to be a
scaled permutation. This is a necessary condition, not admission of every
scaled permutation as a complete supplier. The checker accepts one scaled
permutation for these two local events as a positive control.

For `T=[[1,1],[0,1]]`, the required row608 update at B963 fails U containment
in V. The independent checker reproduces this local failure. It does not
claim an independently implemented full-suffix operator replay or a universal
obstruction to source retiming, widening, recovery, temporary charts, or extra
storage.

## Controls, replay, and cross-review

```
python3 -I -B research/deferred-helper-sum/independent/check.py \
  --out research/deferred-helper-sum/independent/RESULT.json
python3 -I -O -B research/deferred-helper-sum/independent/check.py
```

Both commands pass. Every mathematical check uses explicit exceptions and
survives `-O`. Thirteen rejecting controls in total cover changed source bytes,
wrong source sign, a false rank-two minor, unpaid F-to-E mixing, an off-by-one
slice, mistaking consumer projections for complete pair delivery, and the
persistent sum's actual incompatible next-frame event, across both providers.

Ten accepted controls in total make the hypotheses concrete: dependent source
columns can leave one row low; delivering only the outside consumer can leave
one row low while failing the pair endpoint; moving source gates to a rank-five
overframe bypasses exact F; a toy third arbitrary dirty helper can carry the
second F channel; and a scaled permutation can take the two fixed U/V events.
The third helper changes the support contract and still pays a second F
channel. The overframe control is a local changed-boundary example, not a
legal or favorably priced full-source rewrite.

Two guard ablations per provider are also explicit: comparing outside rows
alone accepts the wrong pair sign, and omitting monotone containment accepts
an illegal F-to-E gate. These demonstrate sensitivity of the intended checks.
No frozen source bytes are altered for the controls.

Cross-review covered root `README.md` at SHA256
`99b67631fa83a6532416853cfba768835193b13b99ad8a0dcd7bb74e94cdc534`
and `design/DERIVATION.md` at SHA256
`c2cfbe8306ffa1953c4f73263adfa206ddc92546446b694b675c979a207777b8`.
The revised exact-F temporal argument handles the strict-superframe escape,
states the after-B961 endpoint, and limits the paid lower bound to the pair
entry. The persistent-chart argument fixes direct source labels. No known
material mathematical issue remains in those reviewed claims. The final design
text correctly calls `H4-2H2` a signed cost change; its positive saving
magnitude would be `2H2-H4`.

The primary checker owns full 723-column forward, inverse-transpose and
reverse-pullback replay, literal full cleanup, and the complete source frame
invoice using the authenticated credited source accountant/interpreters. This
independent checker supplies the local operator, frame witnesses, exact model
proof, and controls above; it does not duplicate that complete implementation.
Physical native phases, owner/source-window reuse, precision/tape bounds,
all-size existence, outer admission, and any new kappa remain unresolved.
