# Encoded residual weights and the completed leaf invoice

This is a source-bound refinement and cost audit, not a new normal form. It
adapts the generated-weight grammar and completed weighted leaf of Jose Manuel's
PR2697 and David Arias's PR2753, and supplies a concrete interface for Nick
Petalas's conditional residual/CALL theorem (PR3041) and the current-source
translation audit PR3986. The new executable evidence uses the actual R437/OQ4
rank-26 ancestor and rank-seven COPY specification, nonzero high fields and the
unchanged encoded evaluator. The invoice descends through `stream.add_pass`:
**each leaf atom requires six closed coefficient evaluations per physical
prefix**, not the three symbolic ADD requests visible in `trace.leaf`.

Sources and exact predecessor pins are in SOURCES.json. The normal forms,
weighted leaf identity, word arithmetic, source construction and earlier
conditional correspondence remain credited predecessor results. This note
makes their current interface and previously opaque preparation multiplicities
explicit; it does not claim to have first discovered the weighted-swap identity.

## 1. Domain and remaining primitive contracts

Let R=Z/(q^w), for an admitted odd prime q and w>=1. The algebra below actually
works for every odd prime; finite q=3 and q=5 controls are outside the selected
supplier's large-prime admission domain. A compiled source specification has
m=64, rank 1<=r<=42, invertible low header, and a fixed preparation invertible
modulo q. Each frozen raw high field is canonical, with entries in
[0,q^(w-1)). Thus H=(low+q high)B is invertible over R. Its projector is
E=H diag(I_r,0)H^-1. The source code, preparation, rank and good/fallback label
are authenticated, not supplied by an untrusted event.

The root weight is a unit u, the Program is chronological, and every generated
size is positive and is exactly r floor(n/64), floor(n/64), or
floor(floor(n/64)/2), as declared. Fields retain their complete original source
codes and ordinals. Numerical words have the source's arithmetic margins.

We use the established word arithmetic and record-codec contracts: encoded
operations compute their stated ring/integer operations and preserve borrowed
inputs, with sufficient scratch capacity. We also retain the physical
`atom_swap`, `add_pass`, `sign_address`, packet-copy and counter contracts when
lifting address algebra to complete Boolean packets. This note proves neither
a new implementation nor a sublinear tariff for those primitives. No payload
independence, zero initialization, distinct prefix values, or distributional
assumption is used. The separate recursive stock, NODE/hosting/return,
parking, source production and complete visited-cell premises remain open.

## 2. Exact generated coefficient, including pair order

Let a_l(i) be the weight at coordinate i after l STEP records, with
 a_0(i)=u. For a STEP from width n put f=floor(n/64). Define
 b(j,t)=a_(l-1)(jf+t) for j<64, and b(j,t)=1 for j>=64.
Let d_k denote the good pivots, or d_j and pi the fallback diagonal and row
permutation, computed from that STEP's frozen projector.

The exact recurrence is:

* GOOD: a_l(i)=d_floor(i/f) a_(l-1)(i), 0<=i<rf.
* UNIT, with either half flag: a_l(i)=1 on its declared width.
* PAIR field j: put t=i if j<64 and t=f-1-i otherwise. Then
  a_l(i)=d_j b(pi(j),t) / b(j,t), 0<=i<f.

The reversal is fixed by `Callback.step`: a PAIR field j must have
`reverse == (j>=64)`. A half flag is admitted only for UNIT. In particular a
half reset does not inherit the root unit or an ancestor coefficient.

Every quantity in this recurrence is defined and is a unit. A good low class
has nonzero leading pivot minors modulo q; the same pivot denominators remain
units at every high lift. A split rank-r projector with these pivots has zero
Schur block, so `good_pivots`' full-ring check succeeds. For fallback, the
unweighted two-bank residual W_E satisfies W_E^2=I. Unit-pivot elimination over
the local ring therefore produces a diagonal of units. An entry is a unit
exactly when its reduction modulo q is nonzero; induction through the finite
elimination steps shows that the first-unit pivot choices and permutation are
those of the fixed low-class plan. Skipping an exactly zero elimination is
algebraically identical to subtracting its zero multiple. Thus all high lifts
share the compiled itinerary. These are the retained local-ring facts, here
applied to the exact source objects consumed by the callback.

Induction on l now proves the unit claim. Every head ancestor coordinate is
less than 64f<=n; a tail operand is the constant one. GOOD coordinates are less
than rf<n. Hence each recursive VALUE is in range and strictly decreases its
encoded level; no future field is read.

To connect this recurrence to the actual `Callback.weight`, use its two-stack
invariant. VALUE(level,i) leaves precisely one RETURN value equal to a_level(i).
A root VALUE pushes u; UNIT pushes one. GOOD first pushes MULTIPLY(d) and then
its ancestor VALUE, so the multiplication executes after that value returns.
PAIR first pushes PAIR(d), then operands in the source order (j,pi(j)). Since
pending is LIFO, pi(j) evaluates first; the values stack consequently holds
b(j,t) above b(pi(j),t). The PAIR branch pops the denominator first and
numerator second. It computes exactly d*b(pi(j),t)/b(j,t). CONSTANT tail
operands push one. This proves the recurrence for the literal control flow,
not an assumed completed child. Stack records own copies of their operands,
which are freed after their final use; successful completion leaves both
stacks empty and exactly one owned residue result.

`children.extend` serializes the actual next STEP, retaining all parent records
and increasing depth by one. `children.coefficient` validates the parent,
extends it, validates the leaf view with precisely the old/current fields,
then evaluates the requested coordinate. Consequently its result is a_l(i),
or -a_l(i)^-1 when `negative_inverse` is set. The leaf view reads exactly the
existing frozen prefix; it does not manufacture a fresh current high field.
The parent Program and Fields remain borrowed and unchanged.

This establishes a concrete coefficient premise of PR3041. It does not prove
the correctness of an internal recursive child just because its generated
coefficient is correct.

## 3. Literal weighted leaf and arbitrary dirty packets

For one coordinate i, write a=a_l(i), and let x,y be the corresponding head
atom and reversed tail atom. The literal eight-stage sequence is

    swap; ADD(a); swap; ADD(-a^-1); swap; ADD(a); swap; sign(second).

Reading after successive ADDs gives (y,x+ay),
(x+ay,-a^-1 x), and (-a^-1 x,ay). The last swap and sign therefore give

    (x,y) -> (a y, a^-1 x).

Every pair is disjoint, so a width-c leaf applies this formula simultaneously
to i=0,...,c-1 with tail coordinate c-1-i. The full coordinate map is a
bijection and an involution. Extend it by the identity on each complete prefix
ordinal, unused-row ordinal, and before/gap/suffix coordinate. Composition then
acts on every Boolean payload by the corresponding address permutation.
This is a pointwise statement, so repeated prefixes and arbitrary correlations
or dirty input bits do not change it. Preservation of spectators is stronger
than a volume-only equality.

For a same-bank fallback child, the retained two half UNIT resets reverse its
second row before and after the main invocation. If f is odd the unpaired
middle atom is a spectator; if f=1 no reset is emitted. PR3041 proves this
geometry and the literal residual/CALL continuation. Its substitution premise
can use the coefficient and leaf contracts above. A width c>=64 still needs
the complete smaller-node contract, original-width stock and physical
CALL/RETURN hypotheses. Strong induction becomes available only after the
completed-primitive and capacity premises of the existing
NODE/hosting/merge implication are discharged; width descent alone
is not that proof.

## 4. Exact preparation multiplicity and complete component invoice

Fix one physical prefix and one leaf coordinate. Let the evaluation tree of
a_l(i) contain G GOOD nodes, P PAIR nodes, U UNIT leaves, R root leaves, and C
tail CONSTANT leaves. This tree is the literal callback tree: identical
ancestor coordinates are counted twice when visited twice.

Beyond arithmetic internal to preparing matrices, it performs exactly:

| Component inside one `weight` call | Count |
| --- | ---: |
| `prepare` plus `good_pivots` | G |
| `prepare` plus `fallback` | P |
| Scalar multiplications combining returned values | G+2P |
| Pair denominator inversions | P |
| Pending VALUE pops / STEP reads | G+P+U+R / G+P+U |
| Pending MULTIPLY, PAIR and CONSTANT pops | G+P+C |

Root and UNIT copies, all typed-stack serialization and clearing, index
arithmetic, level/coordinate guards, field/code scans and head resets are also
charged. They are not included in the scalar arithmetic column. At depth l,
G+P<=2^l-1. This is a work bound, not a simultaneous matrix-storage bound.
No root-depth/current-width coupling is used to absorb this exponential
ancestor work into a current-width linear tariff. Such an absorption requires
its own complete source assumptions.
For pi(j)=j<64 the answer simplifies algebraically to d_j, but
`Callback.weight` still evaluates the identical head ancestor twice. The
separate `Page.child_weight` shortcut is not on the production
`selected_coefficient` child path. The encoded fixed-field control below
observes preparations at slots [1,0,0], with answer one.

Define K_pi(i) to be the complete elementary cost of one positive
`children.coefficient` call on that prefix and coordinate. Its definition
includes two prime-power checks and two Callback constructions/closures,
parent and extended-program validation, all program copying in `extend`,
complete numerical and stack work above, and clearing the temporary program.
The two admissions validate exactly h+(h+1)=2h+1 STEP records for parent depth
h. The legacy seek-from-start implementations charge every intervening record
scan; no random access is free. Matrix preparation includes reading the entire
4096-entry field, raw-header construction, rational constants, inversion and
products. Let J_pi(i) be the additional inverse, negate and disposal cost when
`negative_inverse` is true. K and J are actual costs, not unit-time oracles.

There are three symbolic ADDs per leaf coordinate. But `stream.add_pass`
executes `traverse(False)` and `traverse(True)`, **each** calling
`prepare_coefficient`. Therefore the exact coefficient contribution is

    sum over physical prefixes pi and i<c: 6 K_pi(i) + 2 J_pi(i).

The two positive ADDs account for four K calls; the negative-inverse ADD
accounts for two K+J calls. No coefficient is shared across split/merge, leaf
stages, repeated prefixes or atoms. An invoice using 3K+J prices the trace
requests, not this physical implementation.

Here is a complete component accounting interface. Let V be the whole selected
packet size and Pfx the number of complete physical prefixes. For each of the
8c primitive passes, retain its actual complete-fibre action tariff, excluding
coefficient evaluation in ADD, and its geometry/count/setup/cleanup tariff.
Then add the following outer `packet_engine.run_generator` work explicitly:

* 4c atom-swap passes, 3c ADD passes and c sign passes, on all Pfx fibres;
* 16cV copied payload bits: current-to-local and changed-to-output for each pass;
* 16cV cleared local/changed payload bits, plus (8c-1)V cleared prior owned
  current payload bits when the leaf starts with borrowed source;
* 8c complete directory scans, 8cPfx prefix copies and their erasure, complete
  counters, geometry extents, all head movements/resets and ENTER/RETURN work;
* the 6K+2J coefficient sum above and the final owned output (not silently erased).

These are exact payload-bit visit multiplicities at the named outer routines,
not an exact elementary-time value: delimiters, tests, counters and rewinds
are retained in their explicit tariffs. If a leaf starts after another owned
packet in a larger run, the first prior-output erasure is additionally V.
The primitive tariffs include their internal temporary streams: e.g. ADD's
left/right partitions, offsets and both traversals, and the ordinary swap's
w radix-digit passes and q^2 buckets. The inherited implementations therefore
retain O_q(wV) swap work and O_q(V) sign work; there is no new H2 saving.

The formula accounts for every invoked component of this completed leaf while
leaving unresolved physical tariffs visible. It is not a closed numerical
bound for the entire caller, source production, original-width stock or gamma.
An independent admission-cursor optimization can replace the two validation
tariffs only after its own exact source pin and equivalence proof are supplied.

## 5. Evidence and limits

`check.py` computes independent integer-matrix inverses, projectors, good
pivots and fallback elimination, then propagates an entire coefficient vector
forward. The production path instead runs the actual encoded `children.coefficient`
and its two continuation stacks with `Word.inspect` forbidden. The actual
catalogue/low-code/compiler definitions are inherited through PR3967's pinned
adapter. No oracle function implementing the tested coefficient recurrence is
imported into the independent calculation.

Six controls use q=3, modulus9, root width2048 and unit2, actual native
IDLE27776/rank26 followed by common COPY1603/rank7. Nonzero canonical high fields
are present at both levels. They cover GOOD, fixed-field PAIR duplication,
head/tail PAIR orientations, negative inverse, and UNIT half reset. The native
vector and encoded results agree, original program/field bytes and heads are
restored, arenas close, and preparation counts are exactly 2,2,3,2,2,0.
These coefficient requests include internal-sized generated children; they
do not execute their whole recursive payloads.

The literal source leaf trace is checked on 3,575 finite address instances at
widths1,2,7,26,63 and moduli3,9,25. Omitted sign and wrong reciprocal-sign controls
fail. A one-expression mutation of the actual Callback.weight PAIR branch
replaces its numerator by its denominator and changes the source-bound answer
from5 to1; the independent vector comparison rejects it after cleanup. Direct actual ADD controls establish its two independent coefficient
preparations and whole-fibre dirty-payload address permutation. The finite
cases are implementation controls; the universal statements rest on sections
1–3. Neither finite address coverage nor the algebra proves all retained
primitive implementation contracts or complete production admission.

## 6. Next obligations and credit

The next useful join is PR3223's already established conditional
NODE/peel/split/merge refinement with PR3041's recursive substitution and
PR3986's current-source whole-word ordering, using this explicit
leaf/coefficient contract. The conditional node theorem is not a new open
problem; its remaining completed-primitive and capacity premises are. Price source preparation, retained
parent state and every complete physical consumer with original-width stock.
An optimization of the fixed-permutation pair branch may avoid duplicate
ancestor evaluation, but it must preserve exact accepted programs, errors,
ownership and numerical capacity; no such runtime change is made here.

Credit: the selected construction/local-ring normal forms and generated
coefficients are from the retained source527/PR2160/2159/2234/2310/2332/2405
chain, Jose Manuel's PR2697, David Arias's PR2753, and the fixed-role caller;
Nick Petalas supplied PR2989/3041's conditional correspondence;
commdata2338 supplied PR2399's substitution and PR3223's node/stock refinement; zxv's PR3690
and Chris R's PR3967 supplied the current adapter/binding; PR3950 supplies the
rank-seven reduction and conditional cost boundary. PR3980 supplies a separate
current chart/owner lemma, PR3983 the resource envelope, PR3986 the complete
current skeleton check. PR3993 audits ScratchPool leases and does not discharge
this coefficient algebra. This package leaves those distinct scopes intact.
Substantial OpenAI Codex assistance was used under Chris R / Clear1nsight's
direction for research, implementation and this same-session AI review.
