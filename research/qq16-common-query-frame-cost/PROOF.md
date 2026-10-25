# Common input-frame changes do not reduce this Schur normalization bill

Tekalign (tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
Canonical source base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Exact object and deliberately limited circuit class

Chris R / Clear1nsight's PR4003, head
`309189077d0f760248bbdaadab42ecbff4f3ea2d`, derives the actual missing query
`Q2(X_T) − M21 Q1(Y)` in the PR2707/2681 recovery boundary, where

    M21 = (1/4) Σ_(p∈U+T) r_p r_pᵀ [h_p],   h_p = g_(2,p) g_(1,p).

Its scalar `13I` substitute fails, and its restricted parallel expression needs
104 distinct owner routes. Those logical results and the query-surjection
argument are credited to that source, not newly proved here. This contribution
prices the phase defects after allowing a shared change of input-query frame.

There are eight independent retained queries in F17. Consider an arbitrary
common quadratic frame Γ for them, including arbitrary mixing of the planes
in the λ-lift defined below, and **fix the output query
frame at the actual F16**. A circuit in the class forms each nonzero branch's
scalar channel combination, applies its one owner route h_p, normalizes that
branch into F16, and accumulates it. Constant channel mixing and affine alignment
are granted free. Each branch is normalized separately; no joint native across
branches, Fourier projection, hidden sum of owner routes, changed producer or
changed output frame is included. Splitting a branch does not improve the
lower bound: at least one copy of each required nonzero route still needs its
own normalized payload in this class. This is a specified implementation family,
not all possible circuits for M21. The 104 h_p are fixed; a genuinely different
owner-route decomposition is outside this result.

Grant every rank-k phase normalizer, with either sign and arbitrary normal
subspace, at optimistic native-moment price k^s, s=1−a. Its binary polar update
has rank at most k. Extra monomial moves may conjugate that update but preserve
its rank. This is a prescribed formal recursive-moment charge, **not a lower
bound on wall-clock or bit/tape work**. Alternative implementations require
their own complete invoice. Granting all such factors relaxes native availability.
All other actual obligations
(input acquisition/change/retention, scalar operations, helpers, cleanup, full
owner movement, precision, control and outer consumption) remain nonnegative
costs; only for this **lower-bound screen** are they granted free. No physical
upper tariff, admitted caller or complete supplier follows.

**Theorem.** For every positive integer λ and 0≤a≤10/13, the sharp
normalization-only lower envelope of this class on the certified template's
Kronecker lift is `104 λ^(1-a)`, attained by the unmodified input polar frame.
Every nonzero common polar perturbation has strictly larger native moment,
even when frame preparation is free. The perturbation may mix the λ planes.
For λ=1 and 0≤a≤1/2, the stronger lower bound is **strictly greater than 144**,
versus baseline104. No native saving follows from this common-frame mechanism.

## Binary phase invariant

Write χ_u(v)∈{0,1} for binary parity. A frame list F=((u_l,c_l)) represents
`f_F(v)=Σ c_l χ_(u_l)(v) mod 4`. Its symmetric binary polar matrix is

    B(F) = Σ (c_l mod 2) u_l u_lᵀ.

The diagonal is `f_F(e_i) mod 2`; off-diagonal entries are obtained by polarizing
`f_F(e_i+e_j)−f_F(e_i)−f_F(e_j)` and dividing by 2 modulo 2. Hence the matrix
is independent of a frame-list spelling. An even character/affine shift changes
no B. An owner G sends B to G B Gᵀ. A rank-k native phase factor contributes a
matrix of rank at most k. For any sequence returning the prescribed owner,
rank subadditivity therefore gives `Σ k_j ≥ rank(D)` for its net polar defect D.
For 0<s≤1, subadditivity of x^s gives

    Σ k_j^s ≥ (Σ k_j)^s ≥ rank(D)^s.

This is a lower bound for the stated phase-normalizer alphabet, not for arbitrary
Gaussian kernels or address-valued operations outside that alphabet.

Let G17=B(F17), G16=B(F16), and Δ=B(Γ)+G17. The exact source identities are

    h_p G17 h_pᵀ = G16 + q_p q_pᵀ,     q_p ≠ 0.

The verifier checks their full Z4 frame ancestors, including both actual affine
shifts, and checks that the negative C_(q_p) returns exactly F16. The new defect is

    D_p(Δ) = h_p Δ h_pᵀ + q_p q_pᵀ.

Put `u_p=h_p⁻¹ q_p`. CERTIFICATE.json records all 104 actual u_p. They are pairwise
distinct. Every branch coefficient matrix r_p r_pᵀ/4 is nonzero; the source also
has 104 distinct images h_p(1), so this is not a list inflated with zero or
identical branches. Source extraction authenticates all canonical input bytes
before executing any retained checker.

## All common matrices, without a frame search

Let r=rank(Δ). We allow **every** symmetric binary 73-by-73 Δ, enlarging the
realizable frame class if necessary. There are 2^2701 such matrices; they are
not enumerated. The following rank argument handles them all.

* **r=0.** Each D_p=q_p q_pᵀ has rank 1, so the moment is at least 104.
  The actual 104 negative H1 normalizers attain this phase-only bill. Even
  linear differences between frame spellings are already free in the relaxation.
* **r=1.** Over F2, a nonzero symmetric rank-one matrix is uuᵀ. Its branch
  defect is vvᵀ+q_p q_pᵀ, v=h_pu. This has rank 0 if v=q_p and rank 2 otherwise:
  distinct nonzero vectors are independent, and their two-column matrix has
  rank 2. Cancellation requires u=u_p, which occurs for at most one branch.
  The moment is at least `103·2^s`.
* **r=2.** For symmetric A and q outside im(A), `rank(A+qqᵀ)=rank(A)+1`.
  One proof writes A=U C Uᵀ on a full-column basis of its image, with C invertible;
  appending q gives a full-column factor with invertible block diag(C,1).
  Here q_p is outside im(h_pΔh_pᵀ) exactly when u_p is outside im(Δ).
  A two-dimensional binary image contains only three nonzero vectors. At least
  101 of the distinct u_p are outside, giving rank 3; every other defect has
  rank at least r−1=1. The moment is at least `101·3^s+3`.
* **r≥3.** A rank-one update changes rank by at most one. Every D_p has rank
  at least r−1≥2, giving moment at least `104·(r−1)^s`.

For s∈[1/2,1], every nonzero case is >144. The certificate uses exact inequalities:

    2·103² > 144²,
    sqrt(3) > 7/5,   101·(7/5)+3 = 722/5 > 144,
    2·104² > 144².

Thus no nonzero Δ ties the baseline, and any actual nonnegative preparation or
restoration expense can only increase its bill. This is not a failed finite
search. It is a quantified rank argument using a finite exact source certificate.

## All λ and arbitrary plane mixing

PARTITION.json splits the actual 104 pulled-back directions into **12 linearly
independent groups**. Eight groups have size9 and four size8. Their full span
has rank9, so at least ceil(104/9)=12 independent groups are necessary: this
certificate has the minimum group count. The bounded, seeded balanced-greedy
construction found it on its first restart; exact group ranks and coverage are
checked independently. The theorem needs the certificate, not a search premise.

For the λ-lift, owners are H_p=h_p⊗I_λ and the source defect is
`(q_p q_pᵀ)⊗I_λ`. Allow **any** symmetric 73λ-by-73λ common perturbation Δ.
Conjugate each defect back by H_p⁻¹. Its rank equals the rank of

    Δ + (u_p u_pᵀ)⊗I_λ.

Put r=rank(Δ), V=im(Δ), and E_p=u_p⊗F2^λ, a λ-dimensional subspace.
For symmetric matrices A,B, with image-intersection dimension t,

    rank(A+B) ≥ rank(A)+rank(B)−2t.

Indeed the map x↦(Ax,Bx) has rank dim(im(A)+im(B)), because symmetry identifies
its kernel with that sum's orthogonal complement. Addition can lose at most t
more dimensions: its kernel on im(A)×im(B) is {(z,z):z in their intersection}.
Thus, writing t_p=dim(V∩E_p), the branch defect rank satisfies

    d_p ≥ r+λ−2t_p,       d_p ≤ r+λ.

Within each certified independent group, the E_p form a direct sum. Their
intersections with V also form a direct sum inside V, so Σ_group t_p≤r.
Across 12 groups, Σ_p t_p≤12r. Therefore

    Σ_p d_p ≥ 104λ + 80r.

For a=1−s and d_p≤λ+r, `d_p^s ≥ d_p/(λ+r)^a` (including d_p=0). The normalization
moment is consequently at least

    (104λ+80r)/(λ+r)^a
    = 104 λ^(1-a) · (1+(10/13)x)/(1+x)^a,     x=r/λ.

For 0≤a≤10/13 and x>0 this ratio is strictly greater than1. At a=0 it is
immediate. Otherwise strict concavity gives `(1+x)^a < 1+a x ≤ 1+(10/13)x`.
At r=0 it is exactly the baseline. This proves the all-λ theorem, including
nonuniform changes coupling different planes. No lifted frame census is used.
The positive replay includes a genuinely plane-mixing rank-one Δ at λ=2;
the written dimension argument, not that finite fixture, proves the general case.

The source lift and this tariff alphabet are specified algebraically. Applicability
to a production recursive caller retains its all-size/compiler and execution
correspondence premises. We do not supply them or execute a production lift.

## Open interfaces

Sequential sharing between branches, joint normalizations, different query
producers, a changed output frame, paid harmonic projections and other native
alphabets remain open. In particular, address-valued ADD/scan constructions can
trade native queries for other work; the paid-scan control in PR4023 is a related
warning against extending query lower bounds to a different alphabet.

The 104-branch theorem of PR4003 alone was not a native lower bound; this proof
adds a native-moment obstruction **only under the explicitly separately normalized
branch contract and phase-normalizer tariff**. It does not repair the missing
Q2(X_T) term, supply retained-query lifetimes, evaluate a complete physical
invoice, or establish an improved κ.

## Evidence and credit

The primary certificate checks every complete source phase identity and both
route inverses. A separate implementation executes no inherited code: it reads
the authenticated original recipe, builds row matrices, and polarizes direct
character evaluations at all 73 basis and 2,628 pair characters per port.
Small symmetric matrices through dimension 4 test the rank-one lemmas; all
symmetric matrix pairs through dimension3 test the image-intersection inequality;
these tests are guards, not the proof of their general statements. Negative
controls cover reversed route order, wrong normals, missing branches, corrupted
source bytes, diagonal omission and typed-receipt changes. No Lean/human acceptance
or full multiplication-theorem verification is claimed.

Credit Ali Romman's QQ16/native lineage, ywz65's PR2707, Arham Tahir's PR2681,
Chris R / Clear1nsight's exact PR4003 residual and failed bypass, and all retained
native/compiler/geometry notices. PR3985 (`400df7fca8f60c19bf163c77564fe3fbe9154b04`)
is the cost comparison's source; its executable is not imported. The related
streamed storage work PR4015 is distinct and supplies no free frame conversion.
