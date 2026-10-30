# No paid query in the frozen local word can use only its past history

## Precise interface

Use the literal PR5580 local word. The 735 public inputs are arbitrary.
Owned fields are initialized before their first use. Freeze every paid
argument, scalar operation, contact frame and event order. A replacement
must return the same field value that the paid event returns, before the
source continuation uses it. Grant all earlier input values, completed
paid results, scalar values and owned values for free. Retain them even
after the source overwrites or clears their slots.

The decoder is any finite linear circuit over scalar operations and
native monomials. Each native monomial is the repeated-column tensor
lift M^(tensor f) of a one-column, nine-axis affine/quadratic Clifford
monomial. Scalar coefficients stay outside the tensor lift and may
depend on f. Arbitrary finite products, sums and owner mixing are
allowed. All their storage, routing and arithmetic costs are granted
free. No additional Gaussian result is supplied.

There are 3,454 paid events. None can be replaced in this model, for
any f>=40. The same statement holds for the complete bilinear transpose
word, including owned COPY/CLEAR. This is a local site-emulation result,
not an optimum for all circuits with the same final endpoint.

A different monomial in each address column, general inter-column maps,
nonlinear maps, internal states of recursive children, prior-caller
observations, changed paid arguments, and changed continuations are
outside this result. Earlier exact or rounded arithmetic is not silently
substituted for an ideal linear map. The error statement below concerns
the ideal replacement of one requested value, not the final multiplier.

## Scalar rows describe all histories

Write G_U for the source's canonical chart of a binary subspace U. For
input i in chart E_i put z_i=G_(E_i)^-1 x_i. This is a change of variables
in the proof; it grants no physical Gaussian operation. All z_i remain
independent and arbitrary. At every source event each field has form

    G_U^(tensor f) sum_i a_i z_i.                 (1)

The coefficients a_i are the literal rational scalar row. A native
MOVE from U to V changes G_U to G_V and keeps the row. ADD, COPY and
SCALE operate on rows at a common chart. INIT and CLEAR give the zero
row. This proves (1) by induction, including every owned lifetime.

For each frame class U let S_U be the rational row span of all earlier
values in that class. Initialize it with all original inputs. Every
scalar value is already in S_U, so only paid outputs can increase it.
The exact checker also verifies this inclusion after every scalar
operation; it does not omit scalar histories by assumption.

Different basis labels for the same binary subspace are combined. Their
chart quotient is monomial. A label-sensitive cache would be weaker.

## Other charts cannot supply the missing coefficient

The retained source-bound frame law gives

    rank_Gaussian(G_V G_U^-1)
      = dim(U)+dim(V)-2dim(U intersection V).

In particular, G_V G_U^-1 is monomial exactly when U=V. Thus the left
cosets H G_U are disjoint for distinct frame classes, where H is the
full one-column monomial Clifford group. The same fact holds for the
dual charts G_U^-T used by the bilinear transpose word. Transposition
preserves Gaussian rank and the monomial class.

The credited pointwise Clifford theorem in inputs/pointwise-PROOF.md
states that projectively distinct n-axis Clifford tensor lifts are
linearly independent at every f>=4n+4. Their normalized tensor Gram
matrix is at least I/9. The retained independent audit is also included.
Here n=9, so f>=40 suffices. This theorem is an explicit predecessor
premise; the present package does not re-prove or re-audit it.

Every ordinary circuit on the retained history is a linear combination
of M G_U applied to earlier rows. Combine equal projective operators,
including their tensor phases. Distinct left cosets cannot cancel at
these widths. To produce G_V w exactly, the coefficient of the
projective class G_V must therefore have row w. Only prior histories
in frame class V can contribute to it. Hence a necessary condition is

    w belongs to S_V.                            (2)

Within this model (2) is also sufficient: use the scalar combination
of retained values at V, with the ordinary maps between equal-subspace
chart labels. Extra ordinary buffers and intermediate computations do
not enlarge this span.

## Exact causal certificate

Before every paid event, rational elimination gives a vector u with

    a dot u = 0 for every a in S_V,
    w dot u != 0.                                (3)

The verifier checks (3) against every earlier basis row, then inserts
the new paid row. It includes every event, not only rank-one requests.
It checks the complete arbitrary-input endpoint in both orientations.
A second pass uses the field of 2^61-1 elements and eliminates coordinates
in the opposite order. Every frame dimension, paid count and final
endpoint agrees. The rational pass supplies the proof; the modular pass
is independent arithmetic evidence, not a substitute for rational rank.

Each orientation has 735 initial independent rows and 3,454 strict rank
increments, across 1,002 frame classes. Total available dimension is
4,189. The paid histogram in each orientation is

    {1:2211, 2:459, 3:494, 4:94, 5:164, 6:18, 7:14}.

RESULT.json gives the full certificate hashes and weakest explicit
separating input in each orientation. The code rechecks every separator
on every replay. The count includes register 711's moment-neutral job;
removing its target is a different contract, already identified in PR5590.

Native wrapper boundaries add no missing history. The input wrapper of
a child is an ordinary map of its available input; its output wrapper
is invertible and ordinary. Values before or after those wrappers are
ordinary images of the same rows and cosets. A recursive child's internal
algorithm is not part of this local availability contract.

## Bilinear transpose and owned fields

Reverse the source instruction order. Transpose each ADD by exchanging
source and destination, keep its coefficient, and keep SCALE. The
transpose of COPY d<-s is ADD s+=c*d followed by CLEAR d. INIT and CLEAR
are zero projections and transpose to themselves. The owned inputs are
cleared before use; every owned final row is zero. The verifier checks
all 735 returned public rows.

Use dual charts G_U^-T. A source transition G_V G_U^-1 transposes to
G_U^-T G_V^T, exactly the reverse transition in dual charts. This is
bilinear transpose, not an assertion that the original complex charts
are real. Its paid ranks and distinct frame classes are unchanged.
Standard ordinary boundary maps for an admitted reciprocal orientation
do not create a new Gaussian history. No new caller is admitted here.

## A quantitative site-error floor

For a certificate (3), choose original chart inputs z_i=u_i v. All
prior same-frame observations vanish. Other-frame observations and any
ordinary decoding remain in projective Clifford classes distinct from
G_V. The Gram lower bound gives

    ||(desired-decoded) on this input subspace||_op
       >= |w dot u| / (3 ||u||_2).

Indeed normalized Hilbert-Schmidt norm is at least |w dot u|/3; for an
operator returning one address field it is at most the operator norm.
The exact desired row has operator norm ||w||_2, because its input
charts and output chart are unitary. Thus its squared relative operator
error is at least

    |w dot u|^2 / (9 ||u||_2^2 ||w||_2^2).        (4)

The minimum of the supplied certificates is 1/1,990,170 forward and
1/43,200 in the transpose orientation. These are proved lower bounds,
not the optimal distances to the observation spaces. They allow any
complex, width-dependent ordinary coefficients. They do not bound errors
that a changed later program deliberately cancels.

## Decision and remaining work

Unlimited passive retention cannot supply even one frozen requested
value for free. A useful query-sharing construction must change the
actual source arguments, availability supplied by the surrounding caller,
or the allowed operator interface. This answers one concrete first test
in PR5586 P1/P4/C1. It does not disprove those changed-source targets.
No full caller, compiler/precision/tape or outer proof is repeated, and
no kappa improvement or selected-frontier change is claimed.

Credit Dugongue for PR5586's target atlas; the retained PR5526 theorem and
independent Clifford audit; PR5590's frame binding; GamingPuzzled,
DreamingOfClouds, thu-nmrc, Gareth Davidson, David Arias, Cinna Davis and
the P104/native/compiler lineage. Native transpose/COPY rules retain
PR5392 and classical linear transposition credit. New source application,
exact certificates and this proof: Ali Romman with substantial OpenAI
Codex assistance. Apache-2.0.
