# Whole-fiber coverage and the conditional helper-sharing gate

## Named model and source boundary

This is a scoped theorem for selecting whole calls from the proposed 104 by
104, nine by nine tensor scaffold of PR3954, head
`f1e2839819959cd0534d008be91ed5b79ec55a6a`. It does not embed that scaffold in
the selected h=28 producer. The pinned canonical native-channel witness has
104 X ports, 104 Y ports and 72 arbitrary dirty helpers. A whole local word
uses every port. Its source and target dimension increments are eight each,
and its helper increment is nine: P=104*8+104*8+72*9=2312. The witness has
rank mass2368. We conditionally grant the corrected mass M=2368+208=2576
from PR3882/3894/3940, including the unproved opposite orientation. No native
correction is independently recompiled here.

As in PR3954, let p_i be the 104 distinct odd physical root labels in F2^9.
Each grid pair is the nondegenerate line span(p_i tensor p_j), in dimension
m=81. A first-axis call fixes j and uses every i; a second-axis call fixes i
and uses every j. Swapping the names row and column has no effect below.
This study uses only those exact incidence sets. It neither chooses a new
physical gauge nor grants a free permutation, source decoder or owner move.

The retained caller in notes/copied-centers-complex.tex fixes two logical
stages S(x,y)=(x,x+y), R(x,y)=(x-y,y); the required composition is
R S(x,y)=(-y,x+y), before its paid physical correction and phase wrappers.
We grant the corrected calls this ideal unencoded logical interface to make
the pruning test favorable. Actual encoded boundaries remain obligations.

## Whole-call closure theorem

Select a row set A and column set B, of sizes a and b (0<=a,b<=104).
Their whole-word incidence union is

    U = (A x [104]) union ([104] x B),
    N = |U| = 104(a+b)-ab.

Exactly ab pairs receive both calls. Exactly

    d = 104(a+b)-2ab = a(104-b)+b(104-a)

pairs receive one call. These are dangling endpoints. On any such pair the
logical map is S or R rather than R S. The differences are nonzero on arbitrary
inputs: at (x,y)=(1,0), S=(1,1), R=(1,0), and R S=(0,1). Chart changes cannot
turn this logical endpoint equality into a proof; any changed physical
completion must be established and billed separately.

Consequently, if every touched pair must receive the retained two-stage
endpoint and no replacement completion is supplied, d=0 is necessary and
sufficient at the incidence level. Since each summand in d is nonnegative,
nonempty A forces b=104 and nonempty B forces a=104. The only closed masks
are empty or all208 calls. This is not an impossibility theorem for paid
native completion or a new partial-port word. A rectangle A x B is not the
support of these whole calls: removing its other incident ports changes the
word/interface. Treating them as padding still incurs their acquisition,
return and physical inventory obligations.

## Most favorable complete-cost gate for every mask

Now permit arbitrary replacement completion of dangling endpoints. Grant one
initial rank unit at every touched pair, including pairs whose retained
second stage is absent. This is an optimistic relaxation, not an established
physical initial/final boundary for the pruned caller. Let H be any number of
physical helper owners and W=2N+H. Helper owners may be reused at disjoint
times, provided the stated entrance/exit and progress hypotheses are retained.

The named hypotheses are: every persistent owner must finish under full F;
touched data sources receive the N initial rank credits; each whole call has
mass at least M and net persistent progress at most P; remaining work has rank
tariff at least its net persistent dimension progress; child ranks are <=81;
and the equal physical-role normalization is1/W. Unknown acquisition,
intertwiners, completion, copy/add/disposal, routing, holding, control, tape,
precision and admission costs are nonnegative and additional. This is the
same conditional progress accounting used by PR3954; changed translated
frames that invalidate its P cap require a new proof, not this bound.

For c=a+b calls, persistent progress required is81W-N. Remaining paid rank is
at least max(0,81W-N-cP). Therefore

    total rank >= cM + max(0,81W-N-cP)
               >= 81W + c(M-P)-N.

The excess over capacity is at least

    Delta = 264(a+b)-[104(a+b)-ab] = 160(a+b)+ab.

Every nonempty mask has Delta>=160>0. Thus pruning whole calls cannot rescue
the unchanged corrected profile even with optimistic initial credits and free
new boundary work. For 0<=alpha<1 and 0<=r<=81,
(r/81)^(1-alpha)>=r/81, so the complete moment also exceeds one.
The full mask gives44096, reproducing the named source model as a boundary
case of the new all-mask theorem, not as its only evidence.

H cancels from Delta. Hence reducing the number of helper owners by reuse,
while retaining these hypotheses, cannot reverse the rejection. This does
not establish legal helper reuse. In the actual retained caller arbitrary
dirty helpers are original inputs and must receive full F, including after
their last local use. Calling their local last use 'retirement' does not erase
the remaining endpoint. Deleting b such owners while retaining their b
independent arbitrary input arrays would contradict injectivity; transferring
their information to other owners changes capacity and requires a paid map.
Aliasing independent helpers across different calls reduces the declared
input space and is a different owner contract, which the conditional H-bound
already grants if all other hypotheses hold. Private COPY disposal is a
separate question and is not audited or newly lower-bounded here.

## Exact criterion after an actual profile change

Let e_R=M_R-P_R and e_C=M_C-P_C be proved per-call excesses for the two axes.
Let A>=0 denote additional paid rank with no already-counted progress. The
same relaxed numerator is

    Delta(a,b) = (e_R-104)a+(e_C-104)b+ab+A.

At A=0 this is bilinear. Over [0,104]^2 its minimum occurs at a corner, by
minimizing each affine coordinate in succession. Equivalently its value is
the bilinear convex interpolation of its four corner values. Therefore a
nonempty mask can have negative relaxed Delta iff e_R<104 or e_C<104.
If at least one call from each axis is required, the corresponding corners
are (1,1),(1,104),(104,1),(104,104). Testing those four is exact. If the retained
two-shear endpoint must be incidence-closed, only the full corner remains:

    Delta_full = 104(e_R+e_C-104)+A.

For a common excess e, a two-axis partial mask can pass the relaxed test iff
e<207/2=103.5, whereas an incidence-closed caller requires e<52 (and must pay A).
The first statement follows from ab/(a+b)>=1/2 for positive integers a,b,
with equality only at a=b=1; the second follows from a=b=104.

A concrete discrimination control is e_R=e_C=100. Selecting one call per axis
produces relaxed Delta=-7, yet leaves206 dangling pairs. The complete closed
mask has Delta=9984. This is a warning against treating a passing sparse
relaxation as a constructed caller, not a lower bound on every possible paid
completion of those206 pairs. Even forgiving all208 correction units per call
leaves e=56, for which the closed-mask excess is832. That conditional arithmetic
is not a new COPY floor; PR3045 and the concurrent private-COPY audit own the
literal lifetime question. The earlier #3620 threshold concerns a different
caller and is not used in this proof.

## Decision and remaining obligations

NARROW: stop expansion of unchanged-profile partial-fiber and inventory-only
reuse variants. A reopening result must supply a changed excess/coverage law,
or disprove one named progress hypothesis with an actual translated call.
For sparse candidates it must also implement each dangling endpoint and all
encoded/physical owner boundaries, and include those costs in A. No scalar
incidence theorem proves physical supplier execution, signed-floor or finite
precision correctness, recursive admission, a new kappa or a universal P104
barrier. No selected files or shared verification controls are changed.
