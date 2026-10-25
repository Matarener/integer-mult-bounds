# Recognize multiplication tensors with nilpotents

This package recognizes multiplication in any finite-dimensional commutative
unital algebra from a square tensor over a prime field, up to independent
changes of basis in its two inputs and output. It returns the algebra table
and all three changes of basis. The new test checks regularity of both nucleus
modules when the algebra has nilpotents.

Composing this reconstruction with apoursh's PR #5502 recognizer gives a
necessary-and-sufficient test, recovered heights and explicit transporters for

    F_p[x_1,...,x_r] / (x_i^(p^h_i)),  h_i >= 1,

from an arbitrary square tensor. This closes the three-factor reconstruction
handoff in that PR. An empty height list represents F_p. The procedure is
deterministic polynomial time for each fixed prime p. There is no new kappa,
physical supplier or general tensor-isomorphism algorithm.

## Exact sources and interface

Canonical base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.
The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19174752)
follows the completed supplied-table and finite-etale claims. Full cached
coverage at entry included 398 open PRs, 4,820 Discussion records and every
tracked local research note. Relevant all-state PRs and canonical handoffs
were also read. These checks do not prove global novelty.

`recognize.py` exports `recognize_commutative(t,p)` and
`recognize_frobenius(t,p)`. Both return `(certificate, None)` on acceptance
or `(None, reason)` on mathematical rejection. Invalid shapes, composite p
and entries outside the canonical residues raise `ValueError`. Use
`t[i][j][k]` for the coefficient of output k on input basis vectors i,j.
The input dimension must be positive. Maps U,V,W are matrices with basis
images in their columns, and satisfy `t(Ua,Vb)=W*mu(a,b)`.

Three source files are copied without changes and authenticated before use.
`INPUTS.json` records their original repository, path, commit, Git object and
SHA256. No network or unmerged Git object is needed for a replay.

- Ali Romman's [PR #5525](https://github.com/CrocSwap/integer-mult-bounds/pull/5525),
  [exact matrix and nucleus routines](https://github.com/aliromman/integer-mult-bounds/blob/3d5f42dc084b8c9e1ad73318458751e851752a10/research/etale-tensor-recognition/recognize.py),
  supplies the frozen arithmetic, nucleus solver and fixed-point projectors.
  Its finite-etale acceptance test is not used here.
- apoursh's [PR #5502](https://github.com/CrocSwap/integer-mult-bounds/pull/5502),
  [exact algebra classifier](https://github.com/apoursh/integer-mult-bounds/blob/c09b7a57f81f941b7f9ee6882172eb21a683ded1/research/frobenius-algebra-recognition/recognize.py)
  and [proof](https://github.com/apoursh/integer-mult-bounds/blob/c09b7a57f81f941b7f9ee6882172eb21a683ded1/research/frobenius-algebra-recognition/PROOF.md),
  supplies the final Frobenius-truncated class test and monomial transporter.
  Its theorem is a credited premise of that composed class result.
- Nick Petalas's [PR #5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252)
  supplies the nucleus and finite-etale projectors, with David Ganz's atlas
  and the retained predecessor lineage. Finite algebra decomposition and
  the nilpotent form of Nakayama's lemma are classical.

## Recognition criterion

Let t:U x V -> W be bilinear, with all three dimensions equal to n>0 over
F_p. Compute the left nucleus by linear equations:

    B = {(a,c) in End(U) x End(W): t(au,v)=c t(u,v) for all u,v}.

It is a unital algebra under componentwise composition. Require:

1. dim B=n and both projections rho:B->End(U), lambda:B->End(W) are injective;
2. B is commutative, and t has zero right kernel;
3. for every primitive component e_i of B, with residue field degree d_i,

       dim(e_i U / e_i J U) = d_i,
       dim(e_i W / e_i J W) = d_i,                     (1)

   where J is the nilpotent radical of B.

These conditions are necessary and sufficient for t to be isotopic to
commutative unital multiplication. They construct the transporter below.
All required spaces, including the two quotient dimensions, come from linear
algebra on the supplied tensor. No invertible slice is assumed or searched
by enumeration of vectors.

## Radical and primitive components

Use the faithful matrix image lambda(B) as coordinates for B. Since B is
commutative, F:b->b^p is an F_p-linear map. Let E be the least nonnegative
integer with p^E>=n. Then

    J=ker(F^E),  J^n=0.                                (2)

For completeness, nilpotent elements form an ideal in a commutative algebra.
A finite basis of nilpotent generators shows that this ideal is nilpotent.
Its power chain strictly decreases until zero: equality at two consecutive
powers would persist at every later power. Its dimension is at most n-1,
so its nth power vanishes. Thus (2) kills every nilpotent, and it kills no
other element. The reduced finite algebra B/J is a product of finite fields.

The fixed subalgebra ker(F-I) is F_p^s, one scalar for each local component.
To see surjectivity onto these scalar tuples, lift a tuple to b in B.
Then F(b)-b lies in J, so F^E(b) is fixed and has the same residue tuple.
A fixed nilpotent is zero, which proves injectivity. Hence a basis of this
fixed space separates the components. For each fixed element b and scalar
c in F_p, the polynomial

    1-(b-c*1)^(p-1)

is its exact scalar-eigenspace projector. Repeatedly multiply the current
projectors by these polynomials, and discard zero products. The surviving
projectors are the primitive e_i. Their residue degrees are
`d_i=dim(e_i B)-dim(e_i J)`. This argument also covers nonreduced B; it does
not require injective Frobenius.

## Why the top test is sufficient

For M=U or W, the quotient e_i M/e_i J M is a vector space over the field
B_i/e_i J, of F_p-dimension d_i. Condition (1) says it is one-dimensional
over that field. Choose any vector v_i in e_i M outside e_i J M. A projected
coordinate column supplies one by linear elimination. It generates this
quotient. Summing these vectors over all components gives m_0 with

    M=B m_0 + J M.

Pass to Q=M/B m_0. This says Q=JQ; iteration through J^n=0 gives Q=0.
Thus m_0 is cyclic. Since dim B=dim M=n, the surjection b->b m_0 is an
isomorphism. This proves regularity, including its constructive part.
Apply the argument separately to U and W to obtain u_0 and w_0.

Define

    alpha(b)=rho(b)u_0,   gamma(b)=lambda(b)w_0,
    Phi(v)=t(u_0,v).

The maps alpha and gamma are isomorphisms. If Phi(v)=0, the nucleus identity
and cyclicity of u_0 give t(U,v)=0. The zero right kernel gives v=0. Equal
dimensions make Phi an isomorphism. Put beta=Phi^-1 gamma. For all a,b in B,

    t(alpha(a), beta(b)) = lambda(a) gamma(b) = gamma(ab). (3)

Equation (3) gives U,V,W and the multiplication table of B.

For necessity, consider ordinary multiplication in a commutative unital A.
For a nucleus pair (a,c), setting the first input to 1 gives c(v)=a(1)v;
setting the second to 1 then gives a(u)=c(u)=a(1)u. Thus the nucleus is A,
with both regular actions. Its dimension, faithful projections, zero right
kernel and top dimensions satisfy every test. Independent basis changes
preserve these facts. This proves both directions of the criterion.

## A necessary nonregular control

Set A=F_p[x,y]/(x,y)^2, with basis 1,x,y. Its dual A* is a faithful A-module
of dimension three, but its top A*/J A* has dimension two. The tensor

    A x A* -> A*,  (a,f) -> a*f

has a commutative three-dimensional left nucleus, faithful projections and
zero right kernel. Its first module is regular; its output module is not.
It fails exactly the output-top test. Interchanging its inputs gives an
input-top failure. Thus matching dimension and faithfulness do not replace
(1). The checks include both tensors over F2, F3 and F5.

## Compose the Frobenius-truncated class transporter

The recovered algebra B is isomorphic to the left nucleus. If the original
tensor is isotopic to the target class, necessity above identifies B with
that target algebra, so the pinned PR #5502 classifier accepts. Conversely,
if it accepts, its monomial matrix C satisfies

    mu_B(Ca,Cb)=C mu_model(a,b).

Replace the maps in (3) by U C, V C, W C. These are the required independent
basis changes from the standard truncated-polynomial model to the original
tensor. The verifier checks every basis product of this composed certificate
without using the nucleus test, radical dimensions or classifier decision.
This gives a necessary-and-sufficient recognition procedure for the class.

All stages are deterministic polynomial operations at fixed p: the nucleus
uses n^3 equations in 2n^2 unknowns; Frobenius and its kernels use matrix
powering and elimination; the projector step ranges over p scalars; and
both top tests and transporter inversions use linear algebra. The final
classifier has the fixed-prime guarantee in its pinned proof. Trial-division
primality and the loop over p do not give a polynomial bound in log p when
the characteristic varies. No extension-field input format is supplied.

## Verification and limitations

Run `python3.12 -B scripts/research_package.py --package research/nonreduced-tensor-recognition`.
The standard library suffices. The registered normal and optimized commands
use isolated, warning-strict Python and print `PASS_NONREDUCED_TENSOR_RECOGNITION`.

The complete 256 binary 2x2x2 tensor domain agrees with independently generated
GL2^3 orbits. The split, field and dual-number orbits have sizes 108,12,54.
Exactly 174 tensors pass general commutative recognition and 54 pass the
Frobenius-truncated class test. The oracle uses literal products and an
explicit two-by-two inverse, independently of the nucleus acceptance path.

Forty further presentations cover primes 2,3,5,7,13, dimensions through nine,
mixed heights, nonsplit local residue fields, non-Gorenstein algebras and
multiple local components. In total, 1,736 transported basis products and
76 controls pass. The controls include six nonregular module presentations,
a noncommutative matrix algebra, 48 altered transporter entries, six invalid
inputs and three source-byte changes. All verification conditions use
explicit exceptions and remain active under `-O`.

The written proof gives the general statement; these finite checks do not
replace its review. The source class theorem is credited and its full prior
suite is not rerun. Independent human or proof-kernel acceptance, extension
fields, a selected cold replay, physical coefficient preparation, native
realization, precision, tape costs and supplier admission remain outside
this package. General literature priority is not claimed.

## Open next questions

- Add an explicit extension-field input layer. Start by distinguishing q-power
  Frobenius for decomposition from p-power Frobenius for the height flag.
  Field arithmetic and semilinear kernels require a separate contract.
- Given two accepted general commutative tensors, decide whether their recovered
  algebras are isomorphic. The present result recovers tables and transports;
  it does not solve general commutative-algebra isomorphism.
- Apply the recovered height list to the pinned determinant-character formula
  of PR #5459. Verify the tensor action convention before using orbit counts.
  This algebraic bridge supplies no physical implementation or paid budget.

New regular-module reconstruction, composition and checks: Ali Romman
(@aliromman), with substantial OpenAI Codex assistance. Source classifier:
apoursh (@apoursh). Retain Nick Petalas (@petalas), David Ganz and the cited
algebra and atlas lineage. Apache-2.0.
