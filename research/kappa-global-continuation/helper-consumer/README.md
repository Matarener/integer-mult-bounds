# Routed records and an explicit dirty-state inverse

This package makes a concrete improvement to the preceding consumer work:
**alternating one Gaussian sign gives a dyadic left inverse for all 72 routed
query-image directions in the 128 extra output fields.** The earlier fixed
normalization used only 64 effective record channels. The new claim is about
the actual common routes of the zero-label ports, not an assumption that the
ordinary port routes are equal.

It also gives an ordered, finite terminal inverse which restores arbitrary
initial extra-port values. Its physical query and image maps are explicit
native obligations. They have not been lowered to a profitable recursive
invoice. **No new kappa is admitted here.**

The native local sign variant and the complete nine-stage data geometry are
in the neighboring `symmetric-transition` package. The present package binds
their emitted payloads and supplies the record/consumer algebra. The geometry
does not supply a new full 128-port helper allocation by itself.

## 1. A sign change closes the record-image rank gap

Let `R` be the actual eight-query matrix from the authenticated PR3734 word.
The native reconstruction gives

\[
RR^T=56I_8,\qquad K=R^T/4.
\]

Use the two Gaussian-dyadic alphabets

\[
Q_j=[R,\alpha_j I_8,8iI_8],\qquad
\alpha_j=\begin{cases}4&j\text{ even},\\-4&j\text{ odd}.\end{cases}
\]

Both have `Q_j Q_j^T=8I`. Thus

\[
D_j=I-\tfrac14 Q_j^TQ_j
\]

is a symmetric involution. The bilinear transpose is intended; no unitary
norm statement follows. The ordinary 112-by-112 block remains `I-KR`.

The neighboring native certificate implements each odd word by signs on
eight promoted source ports and the corresponding eight target ports at
the existing common I/FULL boundaries. Each changed invocation adds 64 real
scalar primitives and no native child. Both providers retain rank mass 5070.
The source/helper contents and all 91 owned-zero buffers are included in that
local certificate; it is not a zero-dirt assumption on promoted inputs.

Let the ordinary controller's input-normalized rank-eight stage factors be

\[
E_j=I+U_jV_j,\qquad
U_j=-\tfrac14 a_j\otimes\widehat Q_j^T,\quad
V_j=b_j^T\otimes\widehat Q_j.
\]

Here the hats include the actual stage/port owner routes. The vectors
`a_j,b_j` are reconstructed from the retained nine-call recipe, and
`b_j^T a_j=1`. Consequently `V_j U_j=-2I_8`.

Write `S_b,T_b` for the two groups of eight extra ports in bank `b`. All 16
zero-label ports have the same route at a given stage; call it `rho_j,0`.
For a stage query block `q_j`, set `r_j=P(rho_j,0)^-1 q_j`. Its image in
the zero ports is

\[
\Delta S_b=\sum_j(-1)^{j+1}a_{j,b}r_j,\qquad
\Delta T_b=-2i\sum_j a_{j,b}r_j.
\]

Set, bankwise,

\[
E_b=-\Delta S_b/2+i\Delta T_b/4,
\qquad O_b=\Delta S_b/2+i\Delta T_b/4.
\]

These separate even and odd stage images. The exact inverse is

\[
\begin{aligned}
r_0&=E_{X0}+E_{Y0}-E_{Y1}+E_{Y2}-E_{Y3},\\
r_2&=-E_{Y0},&r_4&=-E_{Y1},&r_6&=-E_{Y2},&r_8&=-E_{Y3},\\
r_1&=O_{X0}+O_{X1},&r_3&=O_{X1}+O_{X2},\\
r_5&=O_{X2}+O_{X3},&r_7&=O_{X3}.
\end{aligned}
\]

Finally apply the actual `P(rho_j,0)` to each recovered block. The checker
verifies the scalar 9-by-16 left inverse, every common-zero-route equality,
and the actual route inverses. Algebraically the image on zero ports is

\[
B=C\,\operatorname{diag}(P(\rho_{j,0})^{-1}),
\]

with `C` of column rank 9 per query mode. The displayed inverse proves
**rank 72 of B over the actual operator interface**. No inverse of an odd
integer appears.

This recovers an *image difference*. It does not assert that a dirty output
`h_out` equals `Bq`: in general it equals `h_in+Bq`. The next section pays
that distinction algebraically.

## 2. Complete inverse on arbitrary data and extra inputs

All products in this section keep their order and are valid over a unital
ring of noncommuting native/owner operators. Concatenate the nine blocks as

\[
U=[U_0,\ldots,U_8],\quad V=[V_0;\ldots;V_8],\quad G=VU.
\]

Let `G_<` and `G_>` be the strictly lower and strictly upper block parts.
The diagonal is exactly `-2I`. Both strict triangular parts are nilpotent
of index at most 9. Define `T=(I-G_<)^-1`, a finite polynomial.

For `M=E_8...E_0`, expanding the chronological product gives

\[
M=I+UTV. \tag{1}
\]

For example the second chronological contribution is
`U_1(V_1+V_1U_0V_0)`; continuing this recurrence yields the lower triangular
factor T. There is no commutation assumption.

The helper-space correction in a Woodbury inverse is also explicit:

\[
I+TVU=T(-I+G_>),
\]

so

\[
(I+TVU)^{-1}=-(I-G_>)^{-1}(I-G_<).
\]

Substituting in (1) gives the particularly short inverse

\[
\boxed{M^{-1}=I+U(I-G_>)^{-1}V.} \tag{2}
\]

Every apparent dense inverse is a finite triangular word. The consumer is:

1. Gather the 72 query fields `q=V z_out` before changing any output field.
2. In descending stage order, replace
   `q_i` by `q_i+sum_(j>i) G_ij q_j`.
3. Scatter `Uq` into **all** data and extra output fields.
4. Return all owned query fields to zero by an admitted cleanup option below.

Equation (2) proves that the resulting complete state is `z_in`, including
every arbitrary extra input. It neither treats an initial extra value as
zero nor withdraws extra outputs from the productive denominator.

### Owned clear and reversible erasure are separate options

The retained native scalar grammar admits `clear` on owned C scratch:
`modern_native_component.py`, function `core_frame_check`, the scalar/clear
branch, checks that the target is C and removes its private lifetime. The
literal interpreter's scalar/clear branch sets that owned array to zero.
This is already used by the retained source codes.

The emitted IR therefore includes 72 literal
`["scalar",["clear",["C",q]],0]` events, with an exact allowance of
**144 real scalar primitives**. The new probe appends 72 simultaneous query
copies and these clear events to the actual omitted-centre word, checks its
full native frame chronology, and checks all 632 live input columns. The
copies leave every live output unchanged and all 72 owned queries finish
zero. This supplies opcode admissibility; global physical ownership still
needs the terminal allocation below.

For a consumer which must erase by additions, a stronger alternative is
also checked. After step 3, call the restored state x. The stored queries obey

\[
(I-G_<)q=-Vx.
\]

Apply `I-G_<` in descending row order, preserving the old lower-index
query blocks, then add `Vx`. Every query is exactly zero. This alternative
has **two V passes and one U pass**. It is optional in the inherited model;
the owned-clear version has one V pass and one U pass.

### Where the routed helper inverse actually goes

The Gram blocks used in both triangular words are

\[
G_{ij}=-\frac{b_i^Ta_j}{4}\left[
\sum_{p<112}R_{:,p}R_{:,p}^T
 P(\rho_{i,p})P(\rho_{j,p})^{-1}
 +(\alpha_i\alpha_j-64)I_8
 P(\rho_{i,0})P(\rho_{j,0})^{-1}
\right]. \tag{3}
\]

These are generally nontrivial routed sums. The proof does not replace them
by the scalar `RK=14I`, identify stage routes, or claim a diagonal helper
inverse.

For a physical gauge identification Gamma, the physical image/query maps
are `Gamma U_i` and `V_i Gamma^-1`. Their product cancels
`Gamma^-1 Gamma` **at the same global port**, before either remaining stage
route. No Gamma/route commutation is used. Thus (3) is an explicit sum of
scalar coefficients and rank-zero cover maps once the specified endpoint
identification is supplied. Its scalar, address, map, precision and tape
charges are still real obligations. The IR preserves the actual R, bank
coefficients and route-payload hash rather than dropping those sums.

The physical gathering `V Gamma^-1` and scattering `Gamma U` are the
remaining recursive boundaries. The record-rank proof does not give their
native child tariffs.

## 3. A tempting 32-channel price is not justified by bank rank

The X-side bank vectors have rank at most 4. This does not imply that the
routed physical image has only 32 scalar channels. For each ordinary port,
the nine actual owner routes send the identity cover class to nine distinct
classes. Using query inputs supported on that class, the checker exhibits:

| Actual-route scalar slice | Rank |
|---|---:|
| X-side image columns | 72 |
| X-side query columns | 64 |

The stage 8 query has no normalized X-bank component, accounting for its
eight zero query columns. Every image stage has an X component.

The nonzero modular minors certify these finite ranks over Q. They reject
compression to 32 by bank-only scalar combinations in this slice. They do
**not** bound arbitrary operator-valued factorizations using additional
cover maps, or establish a recursive-child lower bound. No 64-H8 consumer
is claimed from this calculation.

A conservative interface remains the 448 positive and 448 inverse ordinary
line normalizations from the predecessor's common-FULL terminal method.
Keeping the data normalized through gathering, both triangular words,
scattering and cleanup does not require additional line passes. Its
**896 H1** recursive tariff loses the available complete budget. This is a
fallback interface, not a new profitable consumer. The neighboring invoice
work records its price together with the changed geometry.

## 4. Owned workspace and the productive denominator

The direct inverse needs 72 simultaneous query fields. It does not use the
128 arbitrary extra outputs as clean work. Its proposed physical assignment
is `q_(8j+k)` to the corresponding first 72 fields of the retained 91-field
owned-zero bank, after all local and idle calls finish. In the standard
128-port private layout its family is `W+384+8j+k`, with
`384=376+8`. The IR also records the actual source zero-buffer role IDs.

The local native replays return all 91 buffers to zero at every complete
call boundary. A full supplier must bind that logical bank to its actual
global allocation, prove that its last earlier use precedes the terminal
consumer, and serialize replicas while sharing the query bank. This is a
physical hosting condition, not permission to remove 72 productive outputs.
The main package's independent workspace check may discharge this finite
layout condition; all-size tape hosting remains a separate inherited issue.

## 5. What the original dirty-helper route now rules out

`owner_coupled_factors.py` substitutes the predecessor's dirty involution on
one complete replica, while other replicas use ordinary calls. It reconstructs
the actual T360 clock and FILL mapping. It conjugates every changed factor
through the ordinary prefixes of every owning replica, so changed helper
contents are carried into their later uses as data.

| Replica | Touched physical families | Distinct owners | Exact scalar defect rank |
|---:|---:|---:|---:|
| 0 | 1964 | 16 | 72 |
| 179 | 2756 | 20 | 72 |
| 359 | 2552 | 18 | 72 |

For each, image and query matrices have nonzero 72-dimensional modular
minors. Equation (1) then gives exact rank 72 of `M-I`, since T is invertible.
Reverse factor order restores the nonzero dirty test input on every touched
family; wrong-order reversal is rejected. These are scalar specializations
with actual owner prefixes. Native payload operators remain unpriced, and
no rank-to-child-cost lower bound follows.

`unipotent_pair.py` adds a different local alternative:

\[
D_t=I+(tP_e-K_e)Q,\qquad
D_t^{-1}=I-\frac{(tP_e-K_e)Q}{t-13}.
\]

If `t-13` is a Gaussian-dyadic unit, the inverse coefficient `1/(t-13)` is
Gaussian dyadic. The new emitted
`t=14` pair has `(D_14-I)^2=0`, instead of the old `t=12` involution. Both
actual providers/orientations pass all 632 columns and retain rank mass 5070.
Each orientation costs 168760 real scalar primitives. The same 91-owned-zero
buffer qualification applies.

This parameter freedom does not remove an isolated final B/F defect. For
arbitrary independent interface inputs, `B_t` injects Y only by `-E^T Y`.
Following it with `F_u` therefore has X-response `-E D_u E^T=-J` rather than
`-I`, for every t,u. Its error `KR` has rank 8. Invertible native boundary
identifications cannot turn a nonzero response defect into zero. The receipt
gives an explicit nonzero input-column witness. This statement does not
exclude a separately constructed coupled boundary which prechanges those
inputs.

The actual 106 helpers in Q all have I-to-FULL boundaries. None itself
supplies the omitted forward centre's inverse rank-8-to-I endpoint.
Changing the right inverse within that support does not supply a free echo;
a changed interior program would need its own construction and bill.

## 6. A scoped lower bound on symmetric helper promotion

Within this same Gaussian-dyadic normalization, 16 source helper ports are
minimal. If an 8-by-n helper query matrix B has a dyadic right inverse and
`B B^T=-48I`, reduce modulo 3 in `F9=F3[i]`. The reduced B still has rank 8,
but its row space is totally isotropic because `-48=0` modulo 3. For a
nondegenerate bilinear form on n coordinates, a totally isotropic subspace
has dimension at most n/2. Thus n is at least 16.

This concerns the specified right-invertible symmetric normalization, not
all possible coupled native words. For example an 8-by-8 quaternion matrix
can have Gram `-48I`, but its inverse requires a factor 3 and fails the
dyadic-right-inverse premise.

## Reproduce

From the repository root, with FOLLOWUP replaced by the extracted attached
`kappa-consumer-followup` directory:

```sh
python3 -B research/kappa-global-continuation/helper-consumer/owner_coupled_factors.py --followup FOLLOWUP
python3 -B research/kappa-global-continuation/helper-consumer/unipotent_pair.py --followup FOLLOWUP
python3 -B research/kappa-global-continuation/helper-consumer/alternating_records.py --followup FOLLOWUP
```

Run the neighboring transition and alternating-sign commands first when
rebuilding their inputs. All outputs go to this package's `evidence/`.
The main receipts are `OWNER-COUPLED-RESULT.json`, `UNIPOTENT-RESULT.json`,
and `ALTERNATING-RECORDS-RESULT.json`; compressed payloads retain complete
owner factors, new local programs, and the consumer IR. Source archives and
selected repository certificates remain unchanged.

## Open next questions

The next discriminating deliverable is a literal native realization of the
physical V gather and U scatter in equation (2), with their actual owner
routes and target frames. Price the complete pair, 72 owned clears (or the
optional reversible erasure), scalar/map overhead and workspace within the
changed geometry's allowance before extending the family. The 896-H1
normalization fallback already loses, while a 32-channel price derived only
from bank rank is unsupported.

If that boundary pair fits, bind the new 128-port helper allocation and
productive outputs, then extend precision, route/tape and recursive hosting
admission. Record-image invertibility and dirty restoration algebra are now
available inputs to that work; they are not substitutes for those gates.

Prepared with substantial OpenAI Codex assistance under the user's direction.
PR3734, the retained native interpreter, controller, owner-audit, source-code
and symmetric-extension authors retain their original attribution. New work
is Apache-2.0. These are finite certificates and scoped algebraic proofs,
not an independently verified complete multiplication theorem.
