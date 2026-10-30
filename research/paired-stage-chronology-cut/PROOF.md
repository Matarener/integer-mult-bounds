# Pair parity and the missing chronology cut

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Scope and result

Use the binary normalized controller model of PR #5617, at commit
6c088037e13b87faf7cfe3233c53d0ae51850dd8. There are n main fields per port,
L = n+2 = 2m full calls, m independent stage blocks, and two calls per
block. Each block has eight axes. Helpers are fresh independent jobs.
There are no thin calls or idle maps. Ports stay separate. Each normalized
query is R_i = u_i v_i, with R_i squared zero and sum R_i = I. Each call
has a rank-two idempotent P_i with P_i R_i = R_i P_i = R_i. The target
stage projectors E_c are diagonal in one common basis.

Let r_c = rank E_c and D = 4m - sum r_c. Then:

- D >= 2 for every m >= 4.
- D >= 4 for every odd m >= 5.
- At kappa >= 0.003, the complete PR #5599 bill excludes every m <= 47,
  and every odd m <= 89. These are n <= 92 and odd m with n <= 176.
  The original P104 bill gives m <= 50 and odd m <= 93.
- The previous rank and intersection cuts cannot force a loss that grows
  without bound: an explicit compatible family has D = 8 for every odd
  m >= 5. It passes those cuts, but fails a mixed coefficient condition.

The small m <= 3 exclusions are inherited from PR #5617. None of these
claims supplies a native caller or changes kappa. The written proofs
apply over any field of characteristic two. The executable controls use F2.

## 1. The rank of a pair is even

Write E = P+P' for the two calls of one stage. Since E is an idempotent,
PP' = P'P. Commuting idempotents split the space into their four common
image/kernel spaces. Since both have rank two,

    rank E = rank P + rank P' - 2 rank(PP') = 4 - 2 rank(PP').

Thus each r_c is 0, 2 or 4. Section 8 of the pinned predecessor proves
that D > 0 for every m >= 4. It follows that D >= 2.

For odd m, suppose only one class b is deficient. Factor the rank-two
complement of the query Gram matrix as I-K = XY, with YX = I_2. For
every full class c, the predecessor's capacity cut gives X_c Y_c = I_2.
Hence Y_c X_c = I_2. There are m-1 such classes, an even number. Therefore
Y_b X_b = I_2 as well. Both factors are invertible, so K_bb = 0 and
all off-diagonal blocks K_cb and K_bc have rank two. It follows that
U_b and V_b each have rank two.

The two projectors P,P' of class b commute. Their join is the idempotent
H = P+P'+PP'. Its image is im P + im P', and its rank is 2+r_b/2.
Compatibility gives H U_b = U_b and V_b H = V_b. But V_b U_b = K_bb = 0.
The restriction of V_b to im H has rank two. Its kernel contains the
two-dimensional image of U_b. Thus rank H >= 4, which forces r_b = 4.
This contradicts the choice of b. At least two classes are deficient;
each loses at least two ranks. This proves D >= 4 for odd m >= 5.

This argument does not prove that these lower bounds on D are attained.

## 2. Complete price consequences

Use the two exact paid and helper histograms in the pinned predecessor
RESULT.json. This package authenticates those bytes and recomputes their
net rank mass 1720 and all their nonpositive hinge sums. The predecessor
supplies the native inventory provenance; its native construction is
not replayed here.

For any normalized nondecreasing concave tariff, the complete moment is
at most

    104 * ((2m-2) + 8*(4m-D)) - 2m*1720 = 96m-208-832D.

Thus D >= 2 rejects m <= 19 for every such tariff. D >= 4 rejects odd
m <= 35 for every such tariff. For the power tariff r^t, discrete
concavity distributes the remaining block occurrences as evenly as
possible among the 2m-2 jobs. The two sharper upper bounds are

    M_2(m,t) = 104*((2m-4)*17^t + 2*25^t) - 2m*net(t),
    M_4(m,t) = 208*(m-1)*17^t - 2m*net(t),
    net(t) = sum_r (paid[r]-helpers[r])*r^t.

The verifier uses integer comparisons to enclose each power at
 t=997/1000 within 2^-48. Both bounds are affine in m. It checks their
first and last rejected values and their next positive value. For the
PR #5599 profile the rejected endpoints are m=47 and odd m=89. For the
original P104 profile they are m=50 and odd m=93. A positive upper bound
at the next value is not evidence for an attainable caller.

All negative coefficients have smaller rank than every positive
coefficient. Divide by the smallest positive rank to the power t. Each
positive term is nondecreasing in t; each negative term also is
nondecreasing in t. The normalized bound is therefore nondecreasing.
The exclusions hold for all 0<t<=997/1000, or 0.003<=kappa<1.

## 3. A constant-loss family that passes the old cuts

Let g >= 3 be odd. Take two disjoint copies of a space with basis
 e_0,e_1,...,e_g. For each copy and each j=1,...,g use

    u_j = v_j^T = e_0+e_j,
    R_j = u_j v_j,
    P_j = e_0 e_0^T + e_j e_j^T.

Pair the two copies of each j as one stage. Let w = sum_(j=1)^g e_j.
Add two calls in each copy,

    R_A = e_0 w^T,    R_B = w e_0^T,
    P_A = P_B = e_0 e_0^T + w w^T.

Pair A and B within that copy as one additional stage. Since g is odd,
w^T w = 1. All P are rank-two idempotents compatible with their rank-one
nilpotent queries. Direct addition gives sum R = I on each copy. Each
good stage E_j has rank four, on the two cores and its two leaves. Each
of the two extra stages has E=0. Thus n=2g+2, L=2g+4, m=g+2 and D=8.
All target projectors are diagonal and commute.

These are actual compatible local matrices and target derivatives.
Consequently they meet the assumptions of every old capacity and
intersection cut. The verifier also runs the unchanged predecessor
filter on g=3,5,7,15,31,511; the last case has 131328 intersection cuts.
This proves that those algebraic conditions alone cannot imply a loss
that increases without bound with m. It does not show that D=8 is the
best constant possible.

The relaxed main inventory has two jobs of rank 1+8g and 2g jobs of rank
9 per port. At g=511 and t=997/1000 its complete relaxed moment is
strictly positive for both source profiles. Exact enclosures are in
RESULT.json. This positive relaxation is an explicit false lead for a
search that omits chronology. It is not a kappa claim.

## 4. A mixed coefficient cut

Put Q=1+e and the stage under test z_c=1+d, with e^2=d^2=0. Set every
other stage to one. The normalized local gate is

    (I+d P_i)(I+e R_i)

at a call in class c, and I+e R_i otherwise. Gates act in listed order,
with later factors on the left. Expand the coefficient of de. Use
sum R_i=I and P_i R_i=R_i. That coefficient is

    E_c + sum_(i in S_c) [P_i, sum_(j>i) R_j].

The target coefficient is E_c. Therefore every valid word must satisfy

    sum_(i in S_c) [P_i, sum_(j>i) R_j] = 0.             (* )

Over F2 the commutator is AB+BA. The routine in chronology.py evaluates
this necessary condition from explicit local matrices and the call
order. A pass still does not prove the other word coefficients.

For the family above, list good calls by j, with the two copies together,
then list A,B in each copy. The verifier finds g-1 failed stages, each
with defect rank four. A separate literal polynomial interpreter checks
the mixed coefficient for g=3,5,7. A genuine six-query positive word
passes and has all sixteen expected coefficients for three stages and Q.
Deleting one query fails the query-frame check.

No reordering repairs this family. Restrict to either copy. It has
n'=g+1 fields and L'=g+2=n'+1 queries. The g good stages are private
in that copy and their projectors commute. Cinna Davis's minimum-query
private-projector lemma, retained in PR #5617 Section 4 and in the
pinned GLOBAL-PROOF.md, allows at most two such private calls for n'>=4.
Here g>=3. Every relative order fails the necessary mixed condition.
Calls in the other copy do not change that restriction. The verifier
also checks all 120 relative orders at g=3.

## Verification and remaining obligations

The proof of the unbounded statements is the argument above. Finite
matrix checks do not replace it. No proof-assistant check or independent
review is claimed. No general reduction from complex native programs to
this binary model is claimed. Coupled ports in the paired-stage case,
paid idles, mixed query ranks, partial block overlaps, main/helper mixing
and noninvolutive stages remain outside the price theorem.

The next caller search should enforce (* ) before expanding a full word.
It must then check every coefficient and retain all native, scalar,
helper, routing, restoration and compiler charges. A positive relaxed
moment is insufficient.
