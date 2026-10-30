# Whole-role signs across the P104 word

This is an exact linear-circuit simplification of the frozen PR5599 word,
not a new multiplication exponent or a proof of a rounded implementation.
Ross Richardson's PR919 and Scratch-net's PR1153 already establish useful
same-frame sign-normalization precedents. The application here transports
signs through the complete P104 native itinerary and owned assignments.

## Invariant and native transport

Let x_r be the original state of role r and y_r the emitted state. Initially
x_r=y_r, including arbitrary public inputs and arbitrary owned input data
before its stipulated initialization. Maintain x_r=s_r y_r, s_r in {1,-1}.

* For `SCALE(r,q)`, emit `SCALE(r,abs(q))` unless abs(q)=1, and replace
  s_r by sign(q)s_r. Positive magnitudes, including every halving/doubling,
  remain charged.
* For `ADD(r,s,q)`, emit `ADD(r,s,q*s_r*s_s)`. Then
  s_r(y_r+q*s_r*s_s*y_s)=x_r+q*x_s. The operand roles, chronological order,
  frame, and coefficient magnitude remain the same.
* For `COPY(r,s,q)` into a cleared owned role, retain the operation and its
  coefficient and set s_r=s_s. This is an assignment, not an ADD into an
  arbitrary dirty destination. The source's zero/owned condition is checked.
* For `INIT` and `CLEAR`, retain the original operation and set s_r=1. Both
  circuits obey the same inherited owned-erasure contract. No input is
  presumed clean before INIT, and no discarded residual is claimed free.
* For `MOVE` applying a linear native operator U_r to one whole role,
  U_r(s_r y_r)=s_r U_r(y_r). Retain the exact ordered MOVE bytes, including
  charts and private/public flag. This works with the existing phases,
  spectators and any positive tensor width.

Finally, explicitly negate each public output with s_r=-1 at its final
chart. Every correction is priced. All owned lifetimes already ended under
the original contract. The complete physical linear map and every output
therefore agree, rather than only agreeing modulo output signs.

The sign is on the **whole field**, outside any tensor power. Replacing a
one-column native factor U by -U is a different operation:
(-U)^(tensor f)=(-1)^f U^(tensor f). It fails to supply a whole-field minus
at even f. No native recipe or one-column phase is edited here.

At every aligned source cut the whole-state maps differ by a block diagonal
matrix with entries ±I. In exact arithmetic this preserves the induced
maximum-coordinate norm, and in scalar coordinates each role's coefficient
l1 norm. The implemented check compares every updated sparse row at every
source cut; unmodified rows retain the previous relation. It also compares
all per-role maxima and checks the complete endpoint. This does not check
bit-level negation overflow, a rounding rule, or a new tape realization.

## Complete scalar invoice

Use precisely the real-component allowance in the pinned source `local.py`.
For nonzero q=n/d in lowest terms, with d a power of two:

* ADD/COPY: 2(3 + floor(log2|n|) + popcount(|n|) + log2 d).
* SCALE by a signed power of two: 2(|log2|q|| + [q<0]).
* INIT and CLEAR: 2 each.

ADD/COPY coefficients keep their absolute values, so their source-access,
binary-Horner coefficient and shift charges are unchanged. All positive
SCALE magnitudes also keep their charges. There are 599 negative source
SCALEs; all their minus signs are deferred. There are 112 final public
corrections. Thus the exact allowance reduction is

    2*(599-112) = 974 real primitives per complete local invocation.

Of the 599 negative scales, 334 are pure -1 and disappear entirely; 265
retain a positive nonunit magnitude. Therefore total events become
25475-334+112=25253. The independently counted scalar allowance is
220232-974=219258. All 21247 ADDs, 3447 MOVEs and 8 each of INIT/COPY/CLEAR
remain. The final 112 corrections require no new fields or frame changes.

The selected caller invokes this word 18 times, all forward. Substitution
saves 18*974=17532 in those local scalar charges. It retains the 748 public
fields, 540 productive helpers, eight owned lifetimes with peak one, all
6014 paid local rank mass, exact chart changes and scalar growth bound.
Main normalizers, source access, caller wrappers, query/idle jobs and every
recursive child remain as priced by the predecessor. This does not subtract
17532 from an unrelated coarse global upper bound or claim a wall-clock gain.

The paid and productive target histograms are identical, hence every
recursive moment is identical. The selected conditional kappa remains
0.00310045; no root search, compiler retuning or outer admission is needed
to justify the stated **ordinary scalar** saving. The original conservative
allowance still dominates the replacement. Fresh full caller execution,
native recipe replay and production adoption are not supplied by this note.

## Verification boundary

The source hash binds the actual selected word. A separate sparse Fraction
interpreter checks 25475 aligned cuts and 905501 nonzero row coefficients,
plus the final restorations. The per-role maxima agree; the largest scalar
row l1 norm is 131072. A dense integer/dyadic reverse interpreter, following
the predecessor's transpose method, checks all 571536 entries of the final
756 by 756 map, including owned columns. The two arithmetic representations
and forward/reverse directions are complementary; neither is human or
proof-kernel review. No predecessor executable is imported by the package.

The original predecessor checker was also executed separately as a comparison
on both words during preparation. Its complete frame, endpoint and tariff
receipts agree with the new counts. It is credited as reused verification,
not a wholly independent method.

Controls reject an omitted final sign, a wrong ADD sign, reversed MOVE,
changed native itinerary, lost owned COPY sign, and absorbing a whole-role
sign into a tensor factor. Source-byte, receipt and candidate-word mutation
controls are run in temporary exported copies during validation. Finite
checks support this circuit substitution; the inherited native all-column,
owned-erasure, compiler, precision/tape and analytic-recovery assumptions
remain unresolved here.
