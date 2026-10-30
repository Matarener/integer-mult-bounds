# Carrying central state across an invocation boundary

Douglas Colkitt, with OpenAI Codex assistance. October 9, 2026. Apache-2.0.

**Neither of the two schedules supplies a cheaper recursive profile. Stop
this bounded round. No new supplier or κ is certified.** The selected
conditional witness remains `κ=0.000661885549259598`.

The [interaction-family design](../interaction-family-design/REPORT.md)
identified copied central readout as a costly interface. This follow-up
tests two changes: postpone scalar cleanup across invocations, and replace
copied readout by moving the target to the center's frame. The second admits
a useful endpoint obstruction even when intermediate invocation cuts are
removed. Neither test replaces the working scalar cancellation with the
previously excluded matched encode–shear–decode construction.

## 1. What is actually charged at the existing boundary

The completed-core sharing contract in
[paired-cube-sharing.tex](../../notes/paired-cube-sharing.tex) includes old
dirty-value corrections, copied centers and full-frame inverse cleanup.
The physical auxiliary bank is already shared among three disjoint active
blocks; its scalar values are arbitrary at every entrance.

Three distinct costs must not be conflated:

- The copied central readout contributes positive recursive rank.
- Moving a source or center into its full active frame can contribute rank.
- Subtracting the restored source from the center **at that already common
  frame** is pointwise scalar work, not a recursive child.

Deleting that last subtraction does not itself delete either preceding
charge. A boundary-sharing proposal must specify which frame transitions
also disappear, how subsequent old-value corrections work, and how the
final arbitrary auxiliary values are restored.

## 2. Schedule A: defer cleanup through the three-shear exchange

Let `C=UV` over F2 and `S=I+C`. A forward identity shear has the scalar word

```
y += U z                 # subtract original dirty response (XOR)
y += S x
z += V x
y += U z
z += V x                 # cleanup
```

It adds x to y and restores every arbitrary z. Keep the old response and
the side map, but omit the cleanup in each of the three successive shears
`Y+=X`, `X+=Y`, `Y+=X`.

### A genuine scalar cancellation, under a precise alignment hypothesis

If **the same physical injection map V** is used each time, the injected
source values are `x`, `x+y`, `y`. Their sum is zero. Therefore the final
auxiliary bank restores itself, while the data banks exchange exactly.
This is not a clean-workspace argument; z was arbitrary throughout.

The exact control uses all ten triples of [5], with

`V_iS=1_(i∈S)`, `C_ST=|S∩T| mod 2`, `S=I+C`.

The central matrix has rank **5 over F2 and 10 over Q**. Thus the actual
characteristic-dependent incidence identity is retained. On all 25
independent scalar inputs, the ordinary word has 450 XOR gates and the
deferred word has 360. Both give exactly the full swap and unchanged dirty
bank. Removing the old-response corrections fails.

### Keeping the frame obligations yields no recursive saving

We also realize both words with noncommuting rational triple projectors.
Each scalar gate has an actual common frame, each center copy is transformed
only once per invocation and shared across its target reads, and all endpoint
maps are checked. A deleted cleanup leaves its frame-alignment operations
in place, since this proposal has not justified deleting them.

Both complete small words have the **identical** histogram

`125×[1] + 120×[2] + 30×[3] + 40×[4] + 30×[5]`.

Their total rank is 765: 60 from copied reads, 665 from other internal
frame paths, and 40 from final endpoints. This is a diagnostic word with
25 roles in dimension five, not the selected supplier or a competitive
construction. Full-width calls are allowed for the unfavorable control;
they are not admitted as a shrinking recurrence. The relevant result is
histogram equality, not its comparison with the production profile.

For physical source frames `(P_s,0,0)` and sinks `(I,I−P_s,I)`, the scalar
exchange has full interchange on every original input: the two data actions
are `D_I` and `D_(I−P_s)D_(P_s)=D_I`, and auxiliaries have action `D_I`.
Common-frame gates and exact frame transitions establish these identities
for arbitrary streams, not only on zero inputs.

### The existing auxiliary routing does not supply the aligned V for free

More generally let the three physical injections be V_1,V_2,V_3. The same
deferred schedule leaves the auxiliary residual

`(V_1+V_2)x + (V_2+V_3)y`.

Automatic restoration requires both coefficient matrices to vanish.
Having isomorphic local producers is insufficient.

The [block preparation's finite routing control](../shared-core-blocks/REPORT.md)
provides a small exact test. Its data port g visits `gR_j`, whereas physical
auxiliary a visits `aH_j`. For its single local port, stage j therefore
injects data `aH_jR_j^(-1)`. On the 720-element coordinate subgroup, the
three maps differ. Every auxiliary residual contains four independent data
coordinates; the combined residual matrix has binary rank **719**. This
holds for both the rank-one and direct-sum rank-two controls. An independent
connected-component calculation verifies that rank.

This tests the proposed deferred schedule on the retained incidence
permutations. It is not an exhaustive search over alternate routing, and
does not claim that every modification of the selected reverse middle
word has this residual. It prevents treating aligned logical labels as
aligned physical auxiliary injections without checking them.

**Decision:** the aligned variant saves scalar gates but no recursive
children; the tested shared-bank routing also loses automatic restoration.
Do not scale this schedule. A successor must actually remove frame work
and provide a new routing/endpoint proof, not merely postpone cleanup.

## 3. Schedule B: direct nonzero-frame readout and a carried target

Suppose a center currently has frame R. The usual readout transforms a
dependent copy from R to zero and broadcasts it to targets at frame zero.
The proposed replacement moves each target to R, adds the center directly,
and lets the target remain there into the next invocation. It removes the
center copy and explicitly changes the invocation boundary.

For a target with eventual frame K, the local physical identity is exact:

```
copied:  y += D_R z;           y <- D_K y
direct:  y <- D_R y; y += z;   y <- D_K D_R y
```

Both produce `D_K y + D_K D_R z`, with the center retained. Here P,R,K are
rational projector frames and `D_P=[[I−P,P],[P,I−P]]`. Each partial map is
an involution, and the cross rank of `D_KD_R` equals `rank(K−R)`.
The proposed operation is correct; the question is its complete cost.

### Exact paid broadcast fragment

In the five-coordinate triple control, a coordinate star has center rank
four and serves six targets. Each target source line lies in that center
span and has complementary final frame `K=I−P_s` of rank four.

| Fragment | Complete child multiset | Rank |
| --- | --- | ---: |
| One shared center copy, then target endpoints | `1×[1]+8×[4]` | 33 |
| Direct center reads, then target endpoints | `1×[1]+6×[2]+7×[4]` | 41 |

Both rows include the center's common path `0→R→I`; source production is
identical and outside this fragment. Copied storage is dependent and earns
no independent-role capacity. Direct readout saves the one width-four copy
but adds two rank units on each of six target paths. Its moment also
increases at both illustrative target savings. Omitting the final target
return produces incorrect physical outputs.

### Why crossing the boundary cannot absorb this excursion

Let P be a rank-r rational idempotent on an m-dimensional address space.
Retain the physical Y-wire cuts `0→I−P`. Suppose it visits a gate frame R
that fixes its source image pointwise:

`RP=P`.

No restriction is imposed on other intermediate frames, including those
across later invocation boundaries. Rank subadditivity along the entire
path gives

`charge(Y) ≥ rank(R)+rank(I−P−R)`.

In a basis with `P=diag(I_r,0)`, the visited frame has form

`R=[[I_r,A],[0,B]]`.

Consequently the right-hand side is

`2r+rank(B)+rank(I−B) ≥ m+r`.

The normal endpoint floor is m−r. Thus this visit costs **at least 2r
extra**, wherever the target eventually returns. The visited R need not
be idempotent, self-adjoint or commute with P; `RP=P` suffices. Equality
is attained at R=P. Exact nonsymmetric and nonprojector controls check
the bound and its invariance under rational changes of basis.

The conservative central producer supplies the hypothesis: if a central
channel both contains the target's original source in its gather and sends
that contribution to the target, its frame fixes P. With `C_ii=1`, at least
one such channel exists for every target. This implication assumes the
retained original-source support interpretation; it does not apply to an
arbitrary encoded or cancellation-aware producer.

If **all targets** get their diagonal central contributions by such direct
visits, their paths cost at least `v(m+r)`. The X paths `P→I` cost at least
`v(m−r)`. Together the data consume `2vm`, their entire rank capacity.
With the retained auxiliary path floor `Rm` (in particular for zero-gauge
`0→I` auxiliary paths), the network costs at least `Wm`. Any other readout,
restoration or nonmonotone work only increases that bill.

Since `(t/m)^(1−s)≥t/m` for `0<t≤m` and `0<s<1`, this cannot be a
contracting supplier under the retained full-volume child rule. This is a
bit-side exclusion with stated cuts and auxiliary floor, **not** a theorem
about every possible gauged, typed-volume or distributed frame interface.
No complex implementation is needed to reject this proposed bit supplier.

### A scoped hybrid screen

For plain triple stars on h points, replacing a set of q center copies by
direct readouts in the first invocation affects the diagonal contribution
of `C(h,3)−C(h−q,3)` targets. It saves at most `q(h−1)` copied rank and
forces at least twice that target count as additional rank on their complete
minimal data paths. Thus its net extra-rank lower bound is

`2[C(h,3)−C(h−q,3)]−q(h−1)`.

This is nonnegative for every h≥5: each selected point lies in
`C(h−1,2)` triples, and no triple is counted more than three times, so the
target count is at least `q(h−1)(h−2)/6`. The checker enumerates all q
at h=5,6,23. The statement concerns this first-invocation star-subset
replacement, not all multi-stage hybrids or different central factorizations.

**Decision:** do not enlarge the direct-readout/frame-carry experiment.
Even granting arbitrary intermediate cuts, the retained outer target cut
forces the return cost. Repeating the search with larger matrices cannot
remove that obligation.

## 4. What remains open after this round

The useful distinction is now **postponing a required transition versus
changing the required operation**. The two schedules tested only postpone
cleanup or move the readout cost onto a data wire.

A genuinely different successor would have to specify at least one of:

- A readout that does not make each physical target visit a frame fixing
  its own source block—for example, a distributed encoded-target interface
  with a paid decoder and no already-excluded matched-encoding lift.
- Different outer data cuts and a complete final interchange, charging
  the operation that reconciles those cuts.
- A proved child operation on smaller volume or another changed transfer
  contract, so the full-volume rank-capacity argument is no longer the score.

These are openings in the scope, not constructions or recommended broad
searches. No surviving concrete successor was found here. Stop after these
two schedules and reassess the primitive rather than launching another
variation of deferred cleanup or whole-target frame carry.

## Validation and provenance

Eight tests cover arbitrary dirty inputs, the characteristic rank gap,
unchanged framed histograms, a separate routing-rank calculation, the
literal readout map on all 81 small addresses, failed omission of target
return, the necessity of the visited-frame hypothesis and certificate replay.

```sh
python3 -B research/boundary-readout-sixteenth/audit.py --check research/boundary-readout-sixteenth/certificate.json
python3 -B -m unittest discover -s research/boundary-readout-sixteenth -p 'test_*.py'
make selected-record-check
```

The triple central/side identity, paired-cube producer, completed-core
sharing and finite cover retain their existing upstream and community
attribution. This pass supplies scoped diagnostics and an endpoint-rank
argument; it makes no priority claim for elementary XOR cancellation or
rank subadditivity. The production supplier, verification entry points and
selected certificate are unchanged. All larger analytic-domain and assembly
obligations remain in force.
