# Native transport discriminant and isolated handoff obstruction

This is a bounded semantic and cost test, not a changed selected word. It uses
the inherited native Clifford contract. OpenAI Codex assisted the analysis;
Apache-2.0. The successor-handoff motivation is GamingPuzzled's PR5472 at
`ce96fe9747ea0643bd8c30d448c1ba8e2b30ac30`; its toy construction is not re-tested
or claimed here.

## Exact native contract

Write `T_U` for the actual Clifford representative of frame `U`. The physical
operator for unchanged logical data moving from `U` to `V` is
`T_V T_U^-1`. Its Fourier rank is

`d(U,V) = dim(U) + dim(V) - 2 dim(U ∩ V)`.

For a native invertible binary map `G` with `GU=V`, the physical warp is
`W = T_V K_G T_U^-1`. It has Fourier rank zero, but changes the logical data
by the exact noncommuting operator `K_G`. Its backward counterpart uses the
retained dual orientation. A `phase` marker in the word is not a phase
correction: exact phase belongs to the operator recipe. Rank-zero operators
still have movement/scalar costs under the retained physical tariff.

Sources: `notes/general-clifford-frames.tex`,
`research/transported-warp-frames/PROOF.md`,
`research/kappa-round3-warp-20261022/PROOF.md`,
`research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py`, and
`research/kappa-rebuild/complex/rebuild_native.py`.

## Minimal discriminating examples

`verify.py` authenticates the selected provider, canonical frames, and retained
exact Gaussian-dyadic Clifford compiler. It constructs two coordinate
permutations, whose native quadratic phase is zero:

* In two dimensions, exchange axes 0 and 1, carrying line `<1>` to `<2>`.
* In the actual nine-dimensional source, exchange axes 0/2 and 4/6, carrying
  frame21 `<273>` to frame57 `<324>`. The source provider enters helper300's
  line273 at event9044, and helper295 leaves line324 at event9105. The proposed
  permutation is a new test operator, not an existing registered source warp.

Both fixtures check exact Pauli action and absolute phase. The small fixture
also checks every literal input column. The physical warp has rank zero, while
the unchanged-data transport has rank two. The exact correction

`R = T_V K_G^-1 T_V^-1`

has rank two and satisfies `RW = T_V T_U^-1`. Thus one rank-two recursive job,
with two exact monomial adapters, suffices for this one-way repair. No return
trip is included or needed for the lower-bound comparison. The warp itself
has one monomial recipe. Ordinary adapter movement and scalar work are additional
nonnegative costs. The recursive debit alone already rejects this repair against
the stated allowance; no zero ordinary-cost assumption or new uniform physical
implementation is used to reach that decision.

A warp on the source before `y += x`, followed by its inverse on the source,
leaves `y += K_G x`, not `y += x`. A literal input column detects this defect.
A phase-only mutation is also rejected despite preserving the tableau and
Fourier rank. Normal and optimized Python produce identical reports.

## Why free warps do not supply the missing handoff contact

Consider one conduit holding `h + a` at frame `U`, and a port holding `a` at
frame `V`, for independent arbitrary inputs `h,a`. Suppose rank-zero physical
adapters `D_h,D_x` bring both to one frame `F`, followed by scalar cancellation.
Their logical operators are

`P = T_F^-1 D_h T_U`, `Q = T_F^-1 D_x T_V`.

Purity of `P(h+a) - q Q a` for every `a` forces `P=qQ`. Therefore

`T_V T_U^-1 = q^-1 D_x^-1 D_h`

is monomial, which forces `d(U,V)=0`, or `U=V`. This argument allows a changed
pure helper output gauge `Ph`, arbitrary nonzero scalar `q`, and finite
compositions of free monomial adapters. It does not assume the helper must
return as `h` in its old chart. For native `K_G` warps specifically, the same
point is that proportional exact logical operators induce the same binary
map, and an invertible common map cannot make distinct frames equal.

Consequently an isolated free-warp patch cannot turn the existing disjoint
port/conduit flags into PR5472's clean cancellation contact. A one-leg exact
identity repair between distinct equal-rank lines costs at least one H2, as
the examples attain. More general isolated positive-rank repairs cost at least
one H1. The budget check prices these obligations against the full allowance;
neither adapter movement nor changed producer/consumer obligations are zeroed.

This does **not** exclude a new native word that reallocates existing paid
climbs, uses additional jointly changed rows, or changes productive boundary
interfaces with a complete owner/controller proof. In particular, it does not
repeat the fixed-window floor or prove a global handoff impossibility.

The concrete remaining construction requirement is a clean middle contact
funded by already-paid work, with the successor's arbitrary-input
pre-subtractions available at that frame, followed by new exact helper
operators, owned relations, caller admission and strict compiler accounting.
No such selected-source replacement was constructed in this bounded test.


---

# Line21 successor, entrance rebasing and multiport cancellation

This note separates a legitimate changed-interface proposal from an unproved
target credit. It is not a larger-window search. Exact source pins are those
in `verify.py`; PR5472 at `ce96fe9747ea0643bd8c30d448c1ba8e2b30ac30` supplies
the successor-handoff motivation. OpenAI Codex assistance; Apache-2.0.

## What the proposed split would earn

Helper300 starts at frame0 and ends at full frame1. Its selected backward
paid climbs are at events9044,9104,9135,13289,14793,14800,16155, with ranks
`1,1,1,3,1,1,1`: altogether `6 H1 + H3`, rank mass 9.

A valid retirement just after the first climb at frame21 `F=<273>` would
give one independent rank-one target. A fresh arbitrary successor beginning
at F and inheriting every later climb would give a rank-eight target at the
full exit. The ideal change is therefore **H9 → H1 + H8**, with the old helper
paying H1 and the successor paying `5 H1 + H3`. The scalar edits, successor
ownership, consumer pre-subtractions, changed targets and caller admission
remain obligations. This is a conditional ledger, not an admitted split.

## The source coordinate at the cut

The selected backward prefix before event9044 equals the inherited backward
prefix. Exact reverse substitution gives

```
x300 = h300 + (Y113 − Y123 + Y128 − Y135 − Y140 − Y145
              − Y162 + Y163 − Y174 − Y183 + Y190 + Y194
              − Y203 − Y205 + Y216 − Y221)/2.
x19  = x19_initial.
```

For comparison only, the inherited forward prefix at the same index has
`x300 = h300 + h293/2 − h298 + h505/4`, and x19 is again pure. The two
orientations must not be confused. The backward helper has already absorbed
main-input terms at events2343–2374; its column subsequently reaches other
helpers in the zero-frame assembly around events7072–7153.

The prefix is invertible. Thus x300 is an independent coordinate of the full
transformed tuple, despite this mixture. There is no inference “mixed implies
dependent.” The issue is which input coordinates the productive-job and
caller contracts identify, and which physical basis changes are admitted.

In particular, all 17 fields in the displayed backward shear begin at frame0.
The entrance change `E: h300 ← h300 + R(Y)` is a legal invertible scalar shear.
The corresponding forward shear on h300,h293,h298,h505 is also coframed at
entrance. An entrance basis change is therefore a real escape to investigate,
not an invalid proposal merely because the prefix row is mixed.

## Minimal full-column cut contract

Let p_r be every original prefix row at the proposed handoff, in the original
independent input variables. Add an independent successor input s0 at F, and
let τ exchange the variables h300_initial and s0. A sufficient exact cut
contract for simply renaming the later helper300 role to the successor is:

* the retired old helper contains exactly h300_initial at F;
* the successor contains τ(p_300) at F;
* every other active row r contains τ(p_r), with its required frame unchanged.

The renamed suffix then produces τ of the original endpoint. Original main
outputs and other restored helpers have no final h300 dependence, so they
are unchanged; the successor is restored on its own independent input. Exact
native endpoint operators then give the two independent targets of ranks1,8.

This contract tracks **every outside holder of the old helper-input column**.
If p_300=h0+R, retirement must remove R and the successor must acquire it.
For another row whose coefficient of h0 is C_r, the required replacement
changes that row by C_r(s0−h0). Those changes can sometimes be made by early
pre-subtractions, but the successor starts at F, so a source contact at frame0
cannot simply read it. The local window beginning9044 does not certify these
earlier source and later restoration obligations. This is an algebraic cut
interface, not a claim that a particular larger interval is minimal or viable.

More general cut intertwiners are possible. With a declared invertible input
basis E_in and an explicitly realized output decoder E_out, the candidate
physical word W must satisfy

`E_out W E_in = D_new`

on all independent inputs, where D_new is the desired main operator together
with independent productive targets H1,H8 and the other retained jobs. A free
input shear does not itself certify E_out. Its admissible frames, exact
operators, charges, owned relations and effect on the selected caller must be
proved. The existing selected caller does not automatically establish this
new factorization.

## The specified same-label formal exit shear is not free

Consider only a literal proposal: use the explicit zero-frame entrance shear
and apply a formal exit shear with the same 16 Y labels and coefficients,
with helper300 retired at line21. This is **not** a derived inverse of the
selected word. If its main Y output is H Y, a true decoder may require
R H^-1 rather than R, with different coefficients and support. Reversing the
sign convention for this formal shear does not change the following ranks.

All16 selected-backward Y inputs in R have final rank-eight frames containing
line273. Their final frame IDs are, in the displayed input order:

`143,153,158,165,170,175,192,193,204,213,220,224,233,235,246,251`.

In this specified same-label formal shear, the physical cross coefficient
from Y_j's output to the retired helper is a nonzero scalar times
`T_F T_final(j)^-1`. Its Fourier rank is

`1 + 8 − 2·1 = 7`.

`verify.py` derives the prefix row, checks every entrance frame, checks every
output containment and all 16 exact Clifford B-block ranks, and lowers one
concrete coefficient including absolute phase. The minimum and maximum rank
are both 7. Thus this specified formal shear is not a rank-zero output wrapper.
These 16 coefficients are not claimed to be mandatory terms of the true E_out.

Realizing even one of these coefficients as a retained single Clifford
transport incurs an H7 job plus its adapters; source restoration may add more.
This is deliberately **not** a sum of sixteen H7 charges, and is not a lower
bound for every joint decoder. Reusing earlier paid work or constructing a
different multi-row decoder remains a different mechanism with its own
invoice. The budget audit compares even this optimistic isolated debit with
the line21 split credit.

The selected frame history also confirms that **all 112** Y output fields
112–223 end in rank-eight frames. A nonzero plain-scalar coefficient from
any such field to line21 therefore has Fourier rank7 when its hyperplane
contains line273, and rank9 otherwise. There are 52 rank-seven and60 rank-nine
cases. This is a conditional coefficient-class statement: it applies if a
decoder is expressed using such plain-scalar Y-output coefficients. It neither
derives the actual decoder nor gives a lower bound for every joint decoder.

## Exact multiport criterion and the limit of the isolated no-go

Suppose the conduit contains `H h + Σ_i A_i a_i`, where h and the a_i are
independent, and available port j contains `Σ_i B_ji a_i`. After legal logical
transport operators P on the conduit and Q_j on each port, scalar cancellation
with coefficients c_j produces a pure helper exactly when

`P A_i = Σ_j c_j Q_j B_ji` for every independent input i.

Its remaining helper operator is PH, which must also satisfy the proposed
productive-interface contract. If the ports themselves contain h, their h
coefficients must be included in the resulting helper operator and checked for
invertibility and target admission. Exact gauges and global phases matter.

For separate one-input ports `B_i a_i`, this reduces to
`P A_i = c_i Q_i B_i`. The earlier isolated obstruction follows only in the
special case `A_i=B_i` (invertible) with that input cancelled through one port:
then P and Q_i are proportional, so free monomial adapters cannot coframe two
different initial frames. A sum of operator coefficients or unequal A_i,B_i
does not imply that proportionality.

A concrete algebraic escape uses the exact involutive coordinate swap K from
the two-dimensional fixture. Let U=<1>, V=<2>. If a redesigned conduit already
contains `h+K a` at U while the port contains a at V, warping the conduit by K
is free, lands at V, and gives `K h+a`; subtracting the port leaves pure Kh.
Here `P A=K K=I=Q B`, although P and Q differ. This does not contradict the
isolated h+a argument. The **preparation** of h+K a, all later consumer
coefficients, helper boundaries and final cleanup must be realized in the
actual source word; they are not free assumptions. The selected source load
at line21 carries the unchanged port coefficient I, not this new K.

For the uniform native family, these coefficient identities must hold at every
positive column multiplicity. Multiplicative identities such as K²=I lift;
a finite nine-coordinate equality of operator sums alone does not license
distributing tensor powers over addition. This is another required admission
condition for a coordinated redesigned operator word.

The true exit decoder remains unconstructed. Its coefficients, support and
additional main-output corrections must be derived through the complete
selected transformation, then implemented and priced. The verified cost of
the specified same-label formal shear must not be silently substituted for
that missing calculation.
