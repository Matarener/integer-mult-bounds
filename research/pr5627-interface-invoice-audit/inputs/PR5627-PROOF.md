# Independent helper splits and the complete cost

This proof changes the helper input and output contract of the exact PR5601
word. It composes released relay and boundary changes, nine independent
splits and two prepared queries. Every main endpoint is retained. Every
owned operation and removed target is checked and charged. Scalar identities
are rational; the native check supplies exact phases at every positive width.

## 1. A split criterion

Let a group of helpers have the same initial chart U and final chart V.
The complete source word returns each of these helpers unchanged in normalized
coordinates and has no helper contribution to any other output.
Let F be a strict intermediate chart, with U contained in F and F contained
in V. At one chronological cut, let P be the scalar prefix matrix and S the
scalar suffix matrix. The matrices include every public input and output.
Owned fields follow the source initialization and erasure contract.

Suppose a row a and a column b use only fields at chart F. Suppose c and d
use only the specified helper group, and

```math
aP=c,\qquad Sb=d,\qquad ab=cd=1.
```

Choose a helper role p at F. There are invertible scalar matrices G and J
with

```math
e_p^T G=c,\quad Gd=e_p,\qquad e_p^T J=a,\quad Jb=e_p.
```

Here G acts only on helpers with boundary charts U and V. J acts only on
fields at F. The construction emits these matrices as ADD and dyadic-unit
SCALE operations. Its row and column elimination uses the unit pairings.
The emitted program and its inverse are explicit; no dense matrix operation
is assigned zero implementation cost.

Apply G inverse at the input. At the cut, apply J. Role p then contains the
independent coordinate t=c h. Retain p as an output at F. Introduce one new
independent input z at F. Use its new role in place of p in J inverse and in
the complete suffix. Finally apply G at V, with the same role substitution.
The suffix state changes by b(z-a P h), so its helper output is

```math
h+d(z-ch).
```

The final change of basis gives

```math
G[h+d(z-ch)]=Gh+e_p(z-t).
```

Thus the former p coordinate is replaced by the independent z coordinate;
all other helper coordinates and every main output retain their required
values. The old t coordinate has already been returned at F. This replaces
one U-to-V target by a U-to-F target and an F-to-V target.

This uses a new input, not two outputs computed from one input. It does not
assume a helper is zero. The early output is a public field and stays live
until the caller returns. The successor input is public from the start and
is first used at the cut. The split itself introduces no new COPY, CLEAR
or owned lifetime.
The source's owned erasures remain charged under the inherited contract.

All three basis changes use common physical charts. They therefore commute
with the relevant chart operator. Native normalization gives ranks
`dim(F)-dim(U)` and `dim(V)-dim(F)` with their exact phases. Scalar coefficients
stay outside the tensor substitution. The frame induction applies at every
positive width; it is not a test at width one alone.

## 2. Five released boundary relations

The geometric input is PR5601 at `8f7e870b22885a367b347dc12791da98fd53f83d`.
The PR5605 constructor at `4a57d245ac3918ccc9947a867ece24573605e243` first
reconstructs its exact relay word on the common PR5580 source. Its eight
changed intervals give paid change `H6-H1-H2-H3`.
The unchanged PR5612 constructor at
`faa9f6dbe6b8cc4a996d3edeca71823056453e1a` then delays helper 696's preparation
through the complementary component in helper 700. It removes the remaining
owned-738 contact into 159. Four initial ADDs cancel the nuisance input sum
on outputs 159 and 222; nine full-frame operations restore helpers 696,
697, 698, 700 and 703. Its exact source and output hashes are checked.
The paid delta is `H4+H7-H5-H6`, with every target retained.

The combined relay's 13 changed intervals are disjoint from PR5601's 21
changed intervals, including insertions. A strict merge rejects overlap,
retains PR5601's frame metadata, and replays the complete result. Both
sources' input corrections and late cleanup remain in the merged program.
The retained PR5602 constructor and witness come from
`6c224aa720203c4f4615e6538d8038a275387db8`. No coefficient, helper, frame,
cancellation vector or output vector in those relations changes. Only the
chronological cut indices change, with explicit event anchors in `BOUNDARIES.json`.

For a forward boundary relation, the complete prefix gives a helper input
combination after cancellation by coframed fields. A scalar input basis
makes this combination one independent input. The helper has no later source
read, so it can finish at that frame. The reverse relations supply the
corresponding early-input rule. The source constructor uses an algebraic
transpose to derive that rule; it does not execute the owned program backward.
The final program restores the eight COPY opcodes. Its complete subsequence
of operations involving owned fields equals the original chronological
subsequence of the merged relay source, byte for byte, before the independent
splits rename owned roles. The final preparation adds its own owned role.

The five fixed relations use helpers 652, 341, 596, 668 and 684. Each replaces
one H9 helper target by H4 and removes one paid H5. The complete arbitrary-input
interface is checked after every relation. The sixth PR5602 relation uses a
frame-597 contact absent from the PR5565 cascade; it is not used.

## 3. Nine independent splits

After those five changes, the first split uses the cut after zero-based
event 12520, chart 306 of dimension four, and pivot 259. Its helper group
has initial chart 3 (dimension zero) and final chart 127 (dimension nine).
With e_r the coordinate at role r, the exact vectors are

```math
a=e_{261}^T+(e_{256}^T+e_9^T)/2+2e_{259}^T,\qquad b=e_{259}/2,
```

```math
c=2(e_{259}^T+e_{61}^T+e_{265}^T),
```

```math
d=(e_{262}-e_{270}+e_{265}+e_{264}-e_{256}-e_{271}+e_{263})/2.
```

The complete prefix gives aP=c; the complete suffix gives Sb=d.
Both pairings are one. The boundary basis has 14 scalar events and the
local basis has four. With their inverses, this adds 30 ADDs and six dyadic
SCALEs. It replaces one H9 target by independent H4 and H5 targets.
`SPLITS.json` gives every subsequent cut and all four exact vectors.

`check_cut` reconstructs each prefix functional and propagates each suffix
column. It checks zero support on every other input and output. Full row
replay checks each intermediate construction. A separate dense-integer
transpose replay checks all 565,504 entries of the final 752 by 752 interface.

The nine splits are two H9 to H4+H5, five H9 to H2+H7, and two H9 to H1+H8.
They add nine independent inputs before preparation. The 735 public fields
become 744, with 536 helpers and 208 main fields. The source has 25,132 events;
the relay has 25,179; the boundary step has 25,184; the split word has 25,440.
The split step adds 256 scalar events. Its helper profile is

```text
{1:2, 2:5, 4:91, 5:6, 7:5, 8:16, 9:411}.
```

The verifier replays the retained PR5580 and PR5565 words. It checks the
PR5565 paid delta `-8H1-H3-2H4+4H5` and helper delta `-H8+H9`, then the
PR5601 paid delta `-2H2+2H3-2H4+H5` and helper delta `H4-H5`. These are
credited source changes, not new discoveries in this package.

For 0<t<1, define `g(a,b)=a^t+b^t-(a+b)^t`. Strict concavity gives g(a,b)>0.
The preparation below adds one more strictly positive term. Against the
consumed PR5601 word, the complete target-minus-paid moment increases by

```math
18[7g(4,5)+5g(2,7)+2g(1,8)+g(1,2)+g(3,3)+g(1,1)
  +5^t+6^t-4^t-7^t].
```

The five boundary relations supply five g(4,5) terms. The nine splits supply
the next two g(4,5), five g(2,7) and two g(1,8) terms. The relay supplies
`g(1,2)+g(3,3)=1+2^t+3^t-6^t`. Preparation supplies `g(1,1)=2-2^t`.
The delayed relay supplies `5^t+6^t-4^t-7^t>0`, since strict concavity gives
`5^t-4^t>7^t-6^t`.
Every target debit and removed paid call enters the final invoice. The old
components' reported kappa gains are not added.

## 3a. Prepare the rank-two prefix

PR5606 supplies two exact value identities for prefix helper 573. In the
new split word, its input is set to zero. At events 13651 and 13676, the
complete normalized rows satisfy

```math
r_{573}=r_{572}-2r_{732} \quad\hbox{at chart 595},
```

```math
r_{573}=r_{572}+2r_{710} \quad\hbox{at chart 603}.
```

The suppliers are live in the destination chart at each site. These are
checks on the new word; they are not assumed from the old source. Each
rank-one query is replaced by CLEAR, INIT, COPY and ADD. The helper is owned
from the start, and its final normalized row is zero before the last CLEAR.
The rank-two productive target is removed. Thus the local paid profile loses
two H1 calls, and the target profile loses one H2.

The constructor renames retired role 573 to owned role 751. Public roles above
573 shift down by one; the eight original owned roles shift down by one.
All main roles are below 573 and keep their labels. The final word declares
nine owned roles, eleven initialization/erasure lifetimes and peak occupancy
two. Earlier frozen inputs retain their original eight-role format. The
checker derives matrix width and ownership bounds from this declared inventory.

The final word has 743 independent public inputs, 535 helpers and 25,448
events. Its 752 by 752 matrix includes all nine owned roles. The final helper
profile is

```text
{1:2, 2:4, 4:91, 5:6, 7:5, 8:16, 9:411}.
```

The added COPY/ADD work and all three new lifetimes enter the scalar and
route bounds. The complete bill uses the smaller target count and peak two;
it does not retain the old target credit or one-owned-field bound.

## 4. Native maps and the caller

The exact signed-Pauli and phase verifiers check every paid chart change,
every helper target and every main adapter. The local replay checks a strict
nested chart relation on each public move and the source's descending owned
moves. Each helper target is strictly productive.

Cinna Davis's p16/a7 controller and Ali Romman's all-forward implementation
from PR5544 remain literal inputs. All 18 full calls use the new local word
with fresh independent helpers. Sixteen backward main interfaces use the
retained signed exchanges and central-square translations. These wrappers
act only on the main pair. They do not alter a new helper output.

The physical caller check retains all 104 central ports, 7,488 boundary
contacts, 53,248 central-square column checks, 3,328 main Gaussian targets,
15 thin query sites and 3,120 whole idle jobs. It checks native routes,
spectators, exact phases and every whole target. The complete counts are

```text
paid calls:         66546
productive fields:  12958 = 18*535 + 32*104
rank mass surplus:  760
maximum target:     145
maximum paid rank:  72
```

The invoice is counted twice, once from literal events and once from the
controller path lengths. Input and output normalizers, added scalar basis
operations, routes, owned allocation and erasure, queries and idles are all
included. The new independent field count enters the completion-tail bound.
It is not left at the old 12,814 value.

## 5. Strictification, compiler and outer transfer

Two independent rational interval engines evaluate the complete moments.
The exact raw crossing is in (0.00310440547057, 0.00310440547058).
`RESULT.json` gives its rational endpoints and the strict tested margin. The claimed kappa is 0.00310440546 and the tested saving is
0.003104405465. Their gap funds the finite compiler and outer parameters. An exact negative
derivative bound on [0,0.0034] makes this crossing the raw ceiling for this
fixed invoice under the retained BIT cap. It is not a global optimum.

PR5613 reaches the same signed recursive moment with a different inventory:
its word has 72 more rank-five paid calls and 72 more rank-five targets. Thus the
delayed relay adds no new moment beyond that released construction. This
package retains the five fixed boundaries and nine splits and gives a smaller
complete inventory. The tighter compiler reserve below permits a saving
0.00000000546 above PR5613's rounded claim of 0.00310440. This is rounding
headroom in the common invoice, not another physical mechanism.

Power 1024, cutoff 17, target floor 18 and tail offset 1/5 are retained.
The extra independent fields require a different tail bound: both charged
tail ratios are below 39/40, and `(39/40)^128 < 1/16`. Eight such blocks still
give the retained `2^-32` remainder. The fixed reserve is `10^-12`.
The complete normalized cost is strictly less than one. The old cutoff 20
fails and is retained as a control.

The compiler checks its finite integer threshold, initial range, shifted
exits, complement capacity, logarithm power 1024 and predecessor integer point. The old logarithm
power 1000 does not meet the new complement-capacity inequality.
The ordinary BIT saving remains 0.0034. All 54 strict outer conditions and
four functional conditions are checked with exact rational arithmetic.
The scalar growth bound uses fewer than 26,000 local operations and the
retained per-operation bound. The native growth bound uses the actual sum
of local paid ranks. The complete ordinary-work allowance remains below
`10^9`; the local scalar and route allowance remains below `10^7` per call.

## 6. Scope of acceptance

The five selected framework assumptions remain: native implementation at
all widths, owned erasure, uniform compiler closure, precision and tape
cost, and analytic integer recovery. The source helper-endpoint contract
also remains. This package proves the new finite interface, the chart
identities and every new numerical condition within that framework.

The enormous uniform word and complete rounded multiplier are not
materialized. These are author-side checks by the same AI-assisted author.
They are not independent human acceptance or a proof-kernel theorem.
The final exact discovery screen tests 46 boundary groups and finds no
further candidate in its finite basis-pair class. It does not prove a maximum
over bases, cuts, scalar programs,
frames, controllers or multiplication algorithms.
