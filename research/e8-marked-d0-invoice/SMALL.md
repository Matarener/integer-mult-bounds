# The coefficient-preserving small-total argument

Prepared by conorholds, with substantial OpenAI Codex assistance. Apache-2.0.

This is the Sigma<=6 part of PROOF.md. The rigid shape is derived there;
its assumptions are displayed again to keep this argument reviewable.

## 1. Rigid small-total statement

Use the norm-two E8 model and its orthogonal frame f_1,...,f_8. Let E be the
120 root lines and P=E minus the eight frame lines. Choose representatives
r_s. Write

    ell_s = (1,r_s mod 2 Lambda),
    beta((a,x),(b,y)) = ab + (x,y) mod 2,
    z_i = ell_(f_i),       p_h(s) = (r_s,h),
    C = {p_h:h in K^8} subset K^P.

K is any characteristic-zero field. Root coordinates and their geometric
ranks are rational; geometric statements about the fixed roots are unchanged
by extending scalars to K. For a word q, w(q) is the binary rank of the labels
in its support, and cost(T) is the minimum basis-weight sum of T.

Assume S=C direct-sum T, dim T=t in {2,3}, and that the ACTUAL decoder-column
basis F of S has the form

    b_1,...,b_t, q_1,...,q_8,
    (b_a) a basis of T,
    q_l = p_(h_l)+tau_l, tau_l in T,
    h_1,...,h_8 a basis of K^8,
    w(q_l) in {8,9}.

Let phi_j be the functionals dual to this actual basis and let x_j(h) be
phi_j(p_h). Every x_j is nonzero. For high indices x_l=mu_l, the basis dual
to (h_l). A basis member j is corrected when, for some i,

    x_j(h)=gamma_j(f_i,h), gamma_j != 0,
    z_i belongs to U_j := span_F2{ell_s:s in supp(q_j)}.

For low indices q_j means b_j. Set

    Sigma = sum_a w(b_a) <= 6,
    n_T = number of corrected low members,
    n_8 = number of corrected weight-eight high members,
    c_9 = number of weight-nine high members,
    c_9,corr = number of corrected weight-nine high members,
    I = 64+Sigma-n_T-n_8+(c_9-c_9,corr).

This I is the exact corrected one-sided invoice, not a lower-bound surrogate.
Finally suppose v is a nonframe root line and k is a marked basis index with

    x_k(h)=gamma(r_v,h), gamma != 0,
    g in S_v := {s in S:s|O_v=0}, phi_k(g) != 0,
    O_v = {s in P:(r_s,r_v)=0} union {v},
    epsilon_k = [ell_v in U_k].

**Theorem.** Under these hypotheses, I-epsilon_k>=64.

More precisely, Sigma=5 or 6 and the Sigma=4 case n_T=1 have I>=65 without
using g or epsilon. In the remaining cases I>=64, and the marked hypothesis
excludes I=64,epsilon_k=1. Equality I=64,epsilon_k=0 is permitted.

The assumptions about the original decoder are exhausted by these displayed
contracts. In particular the marked row is a nonframe root row and therefore
is not a corrected frame row. No projected-row merging is performed.

## 2. Explicit inherited geometric inputs

The proof uses these existing results from conorholds' PR3166, exact head
7c2a62363ad4945e8803fedea6ead78e1ad412b2, package
research/e8-d0-root-swaps/:

1. PROOF.md Theorem A: for any correction space L on E, the real/K rank of
   its exact-swap eligible root directions is at most cost(L). A root r is
   eligible when a word tau in L is nonzero at r and zero at every OTHER
   root coordinate orthogonal to r. Extend words on P by zero on the frame
   when applying this theorem.
2. PROOF.md Section 4 root-only lemma: cost(T)<=6 and
   w(p_h+tau)<=8, tau in T, h!=0 imply that h is a root direction, possibly
   a frame root. This is an independent geometric statement, with none of
   the C1 normalization assumptions in EXTENSION.md Section 3.
3. PROOF.md Section 4 remainder fact: the 56 nonself nonorthogonal roots of
   any root r span W_r=ell_r^(perp_beta), of binary dimension eight, and
   every nonzero character of W_r has at least 24 nonzero values on them.
4. EXTENSION.md Theorem E: if |supp(tau)|<=24 and p_h+tau vanishes on O_v,
   with h!=0, then h is proportional to r_v.

The support capacities needed below are only (1,2,4,8,12) at binary ranks
(1,2,3,4,5), proved in PROOF.md Section 4. The maximum small-Sigma union is
therefore 13: among positive partitions of total at most six into two or
three parts, (5,1) gives 12+1, and all others give at most 10. Denote the
union of ACTUAL low-basis supports by B; thus |B|<=13. Every tau in T is
supported on B. In particular Theorem E applies whenever it is used below.

Elementary E8 facts used explicitly are: ell_s are distinct with leading bit
one; beta(ell_s,ell_s)=1; for distinct root lines beta(ell_s,ell_u)=0 iff
their real roots are nonorthogonal; the lattice is integral, even, and has
minimum nonzero squared norm two. Its residue quadratic form is

    Q(x mod 2 Lambda)=(x,x)/2 mod 2,
    Q(x+y)=Q(x)+Q(y)+(x,y) mod 2.

Every root residue, including every frame residue, has Q=1.

## 3. Consequences of the actual decoder basis

### 3.1 The coefficient map has fixed low rows

Define the linear map A:K^8 -> T by A(h_l)=tau_l. Expanding p_h in the actual
basis gives

    p_h = sum_a x_a(h)b_a + sum_l mu_l(h)(p_(h_l)+tau_l).

The code parts in the last sum already equal p_h. Therefore

    A(h) = -sum_a x_a(h)b_a.                         (A)

Consequently if b_a is corrected with frame f_i, its coefficient in A(h)
is EXACTLY -gamma_a(f_i,h). Its nonzero status is fixed by that pairing;
the swap witnesses cannot choose independent low-basis coefficients.

### 3.2 Corrected weight-eight highs are actual nonframe root swaps

The root-only lemma applies since cost(T)<=Sigma<=6. Let h_l be a root
direction r, rescaling its high basis member so that h_l=r if necessary.
For nonframe r exactly four of its 56 nonself nonorthogonal roots are frame
roots. Remove those four and at most |B|<=13 further roots. Fewer than 24
roots have been removed, so the surviving P remainder still spans W_r.
Its coordinates are unchanged by tau_l and nonzero in q_l. Since w(q_l)=8,

    U_l = W_r.

The label of r and the labels of all other roots orthogonal to r lie outside
W_r. Hence q_l is zero at those coordinates. In particular

    tau_l(r)=-(r,r) != 0,
    tau_l(s)=0 for s!=r with (r_s,r)=0.              (SW)

This is an actual swap witness. Arbitrary initial scaling of h_l only
rescales this witness and does not change any zero condition or evaluation
test used below.

If r is instead the frame f_i, all 56 remainder roots already lie in P,
and the same argument gives U_l=W_i. A corrected high dual row is a frame
f_j and mu_l(h_l)!=0; frame orthogonality forces j=i. But z_i is not in W_i,
contradicting correction. Thus every corrected weight-eight high has a
NONFRAME root normal and satisfies (SW).

### 3.3 High frame indices are distinct; n_8<=4

The eight mu_l form a basis. Thus all corrected high frame indices,
including those of weight nine, are distinct. This follows from high
duality and does not assert distinctness of corrected low indices.

For a nonframe root r, its eight pairings (r,f_i) are 0 or +/-1 and their
squared sum is four. Thus its frame-incidence set has exactly four indices.
Two nonframe incidence sets have even intersection: twice the integral
inner product is the signed sum on the intersection.

For m corrected weight-eight root normals r_l with matched frame indices
j_l, duality gives

    (r_l,f_(j_l)) != 0,
    (r_l,f_(j_s)) = 0 for s!=l.

Each incidence set uses its own matched index and three unmatched indices.
For m>=6 there are too few unmatched indices. For m=5, every root uses all
three unmatched indices, so two incidence sets intersect in three places,
also impossible. Hence n_8<=4.

If n_8=4, then c_9,corr=0. Indeed, adding even one corrected weight-nine
frame index leaves at most three unmatched indices; the same intersection-
three contradiction applies to the four corrected root normals.

More generally, as soon as n_8>=2 the total number of corrected HIGH frame
indices is at most four. Each of the two root supports has a three-element
tail outside all corrected-high indices. If there were at least five such
indices, at most three unmatched axes would remain, so both tails would be
the same three-set. Their support intersection would then have odd size
three, a contradiction. The generic finite-incidence derivation, including
the quartet structure below, is formalized in formal/PrivateIncidence.lean.
The E8 incidence and actual high-duality instantiation remain explicit
written inputs to that formal theorem.

### 3.4 Geometry of a private quartet

Suppose n_8=4, and let R={r_1,...,r_4}. Let J be their four matched frame
indices and K its four-element complement. Every r_i uses its own J index
and three K indices. Two roots cannot omit the same K index, since their
incidence intersection would then have size three. Thus the four omitted
K indices are distinct.

Every J-axis is nonorthogonal to exactly one member of R; every K-axis is
nonorthogonal to exactly three. In particular every frame root is
perpendicular to at least one member of R.

No frame root belongs to the real span of R. For a K-axis, private J
coordinates force all four coefficients in a putative combination to zero.
For a J-axis, those coordinates leave only its own root coefficient; that
root still has three nonzero K coordinates, a contradiction. This also
proves real independence of R. No enumeration of quartets or completion of
the other four high normals is required here.

### 3.5 Binary private labels exclude every frame label

This useful fact holds for any number m of private corrected roots. Let L be
the leading-coordinate functional. Then L(ell_r)=L(z_i)=1 and

    beta(ell_(r_i),z_(j_s))=1-delta_(i,s).

The linear functional d_s(x)=L(x)-beta(x,z_(j_s)) recovers the i-th
coordinate on these root labels: d_s(ell_(r_i))=delta_(i,s). They are
therefore binary independent. Every frame label z has d_s(z)=1-1=0 for
all s. If z were a combination of the private root labels, all its
coefficients would be zero, contradicting L(z)=1. Thus no frame label
belongs to their span. This generic argument is formalized in
formal/PrivateLabels.lean; its displayed E8 instantiation is a written
argument and is also checked in the two finite coordinate models.

## 4. Carrier triples and the actual coefficient obstruction

### 4.1 Corrected weight-three carriers have three support roots

A binary rank-one or rank-two support cannot carry an excluded frame label:
the leading-one part of its span contains only its one or two actual root
labels. Hence every corrected low member has weight at least three.

A rank-three support has at most four root labels. If there are four, they
are the whole leading-one affine plane of that three-space; it contains no
additional frame label. Thus a corrected weight-three member b has exactly
three support roots a,b,c, and its matched frame satisfies

    z_i = ell_a+ell_b+ell_c.                        (C3)

### 4.2 A corrected carrier triple cannot act alone at a corrected root

Let b be a corrected weight-three low member with matched frame f_i. If a
nonzero multiple of b is a swap witness at a support root a, the other two
support roots are nonorthogonal to a. From (C3),

    beta(z_i,ell_a)=beta(ell_a,ell_a)=1,

so f_i is perpendicular to a. But (A) says that the actual coefficient of
b in A(a) is -gamma(f_i,a)=0. This contradicts a nonzero pure-carrier
witness. The same reasoning works on the carrier coordinates whenever
auxiliary supports are disjoint from the triple, even if the full witness
also has auxiliary coordinates elsewhere.

## 5. Sigma=6

Write E_9=c_9-c_9,corr>=0. If I<=64, the ledger gives

    n_T+n_8 >= Sigma+E_9.                          (L)

Each corrected low costs at least three, so at Sigma=6 we have n_T<=2.
Together with n_8<=4, (L) forces n_T=2,n_8=4,E_9=0,I=64. The only actual
profile is (3,3), with t=2. Section 3.3 then forces c_9=c_9,corr=0.

Let the two carrier triples have matched frames f_i,f_j, allowing i=j.
By (A), A(r) is a fixed nonzero scalar times (f_i,r)b_1 plus a fixed nonzero
scalar times (f_j,r)b_2. In the private quartet choose r perpendicular to
f_i. Its actual witness is either zero or a nonzero pure multiple of b_2.
Zero cannot cancel its self-coordinate; a pure multiple is impossible by
Section 4.2. Thus I<=64 is impossible. This proves I>=65 for Sigma=6.

## 6. Sigma=5

Now n_T<=1, so (L) forces n_T=1,n_8=4,E_9=0,I=64. Again c_9=0. The actual
profiles are (4,1), (3,2), or (3,1,1). Let R be the private quartet.

### 6.1 Profiles (3,2) and (3,1,1)

Let b be the corrected carrier triple, C its three-point support, and E the
union of the auxiliary supports. The capacity bound gives |E|<=2.

If C and E are disjoint, every corrected root outside E must lie in C.
Its self-cancellation needs a nonzero carrier coefficient. On the other
two carrier coordinates its witness is a pure carrier, so Section 4.2
forces that coefficient to zero. Thus all four corrected roots would lie
in E, impossible.

If C and E overlap, |C union E|<=4. The four distinct corrected roots have
nonzero self-corrections, so they all lie in this union. Hence

    C union E = R.

The carrier label z_i belongs to the span of C, hence to the span of R.
This contradicts the binary private-label lemma in Section 3.5.

### 6.2 Profile (4,1)

Write the low basis as a corrected weight-four member b and a unit delta_u,
rescaling the latter harmlessly. Let f_i be the carrier frame. For r in R,

    A(r) = -gamma(f_i,r)b + nu(r)delta_u.           (41)

Any r perpendicular to f_i must equal u, since (SW) requires a nonzero
correction at its own coordinate. If i were in J there would be three
such roots. Thus i lies in K; its unique perpendicular quartet root is u.
The other three quartet roots R_0=R minus {u} lie in supp(b).

For distinct r,s in R_0, equation (41) is nonzero at s, so (SW) makes r,s
nonorthogonal. Their three labels are beta-orthonormal. The frame label z_i
is beta-orthogonal to all three, has self-pairing one, and belongs to U_b.
Since dim_F2 U_b=4, these four labels form a beta-orthonormal basis of U_b.

If s belongs to supp(b) outside R, each of the three witnesses at R_0 is
nonzero at s. Hence ell_s is beta-orthogonal to all three R_0 labels.
In the displayed basis of U_b this forces ell_s to equal z_i, impossible
because s is a P coordinate. Therefore supp(b) is contained in R.

But z_i belongs to U_b, which is now contained in the binary span of R.
Section 3.5 excludes every frame label from that span. Contradiction.

Thus I<=64 is impossible for every Sigma=5 profile, and I>=65.

## 7. Sigma=4 with a corrected low member

Here the only actual profile is (3,1), with t=2. Let C={a,b,c} be the carrier
triple, f_i its frame, and delta_u the other basis member. We prove that at
most TWO corrected weight-eight high roots are possible. This is independent
of the marked pivot and of every weight-nine count.

If u is outside C, a corrected root in C has a witness whose restrictions
to C are a nonzero pure carrier. Section 4.2 excludes it; only u could be
corrected. Suppose instead u is in C, and write C={a,b,u}. All corrected
roots are in C. It suffices to show that a and b cannot BOTH be corrected.

If both are corrected, their carrier coefficients are nonzero. Thus
(f_i,a) and (f_i,b) are nonzero. The witness at a is nonzero at b, so a,b
are nonorthogonal. Using z_i=ell_a+ell_b+ell_u and
beta(z_i,ell_a)=0 gives

    beta(ell_a,ell_u)=1;

similarly beta(ell_b,ell_u)=1. Hence u is perpendicular to a and b, whereas
(a,b) is odd. Apply the residue quadratic form to the carrier identity:

    Q(f_i mod 2 Lambda)
      = Q(a+b+u mod 2 Lambda)
      = 1+1+1+(a,b)+(a,u)+(b,u) = 0 mod 2.

A frame root has Q=1, contradiction. Thus at most one of a,b can be
corrected; including u still gives n_8<=2. This proof needs neither an A2
classification nor a real-rank assumption on the carrier triple.

If I<=64, (L) with n_T=1 and Sigma=4 requires n_8>=3+E_9, contrary to the
bound just proved. Therefore I>=65. This excludes ALL boundaries, including
three corrected weight-eight highs with a corrected weight-nine high, and
four corrected weight-eight highs with an uncorrected weight-nine high.

## 8. No corrected low: Sigma<=4

For Sigma<=3 no corrected low is possible, since t>=2 and every corrected
low costs at least three. At Sigma=4 we now consider n_T=0. All corrected
weight-eight highs give independent actual eligible root directions by
Section 3.2. Theorem A gives

    n_8 <= rank R(T) <= cost(T) <= Sigma.

Therefore

    I = 64+Sigma-n_8+E_9 >= 64.                   (R)

This proves the needed lower bound for BOTH values of epsilon, without K2.
It remains only to exclude I=64,epsilon_k=1. Equality in (R) forces

    n_8=cost(T)=Sigma,       E_9=0.                (EQ)

Let R be the actual corrected weight-eight root set. It consists of Sigma
independent roots, each contained in B by self-cancellation.

### 8.1 Equality forces actual disjoint supports and B=R

The possible actual positive profiles are

    Sigma=2: (1,1);
    Sigma=3: (2,1), (1,1,1);
    Sigma=4: (3,1), (2,2), (2,1,1).

Units in a basis are distinct coordinates. In every listed profile other
than (3,1), the support-cap sum is Sigma; containing the Sigma distinct roots
R forces equality in each cap and pairwise disjoint supports. Thus B=R.

For (3,1), let b be the weight-three piece and delta_u the unit. If b has
three support roots, the same counting proves disjointness and B=R. A
weight-three support cannot have fewer than three roots. Suppose it has
four. Its four labels XOR to zero. Pairing this equality with any one label
shows that the corresponding support root has at least one OTHER support
root orthogonal to it. Thus a pure multiple of b cannot swap any support
root.

If u is outside this support, its unit cannot cancel such an orthogonal
coordinate; at most u is eligible, contradicting four corrected roots.
If u is inside, B is that four-point support and contains the four roots R.
Section 3.5 gives binary rank(R)=4, whereas B has rank3 by w(b)=3.
This is impossible. The four-point case is excluded, so equality always
gives actual disjoint low supports and B=R.

This argument does not classify the real rank of four-point binary supports;
it covers both the real-rank-three and real-rank-four possibilities.

### 8.2 High marked k

Write g=p_h+tau with tau in T. If k is high, phi_k(T)=0 and
phi_k(g)=mu_k(h)!=0. Thus h!=0, and Theorem E forces h to be a nonzero
multiple of v. Because g vanishes on O_v, tau supplies an eligible swap at
v, including a nonzero self-correction. On the other hand

    mu_k(v)=gamma(v,v)!=0,
    mu_k(r)=0 for every r in R.

The second assertion is high-basis duality: k is not a corrected frame row,
so it differs from every high index furnishing R. Thus v is independent of
the Sigma roots R, contradicting Theorem A and cost(T)=Sigma.

A marked high of weight nine also contradicts E_9=0 immediately, since it
is uncorrected. The proof therefore includes that boundary without treating
its normal as a root direction.

### 8.3 Low marked k: the actual T_v coefficient condition

Again write g=p_h+tau. If h=0, set u=g. If h!=0, Theorem E makes h=nu*v.
Then tau is a swap witness at v, so v belongs to B=R. Let q_v denote the
actual corrected high member with normal a*v, a!=0. By (SW), q_v vanishes
on O_v. Set

    u = g-(nu/a)q_v.

In both cases u belongs to T, vanishes on O_v, and

    phi_k(u)=phi_k(g)!=0,

because phi_k(q_v)=0 for the low marked basis index. The actual low supports
are disjoint. Consequently the restriction of u to supp(b_k) is exactly
phi_k(u)b_k, nonzero at every coordinate of that support. Hence

    supp(b_k) subset P minus O_v = N(v).

Every label in N(v) lies in W_v=ell_v^(perp_beta). Since beta(ell_v,ell_v)=1,
ell_v cannot lie in U_k. Thus epsilon_k=0, contrary to the equality case
epsilon_k=1 under consideration.

No low-k extra root was assumed independent of R. When h!=0 its line was
identified with an existing actual corrected high precisely because B=R;
subtracting that actual basis member preserves the marked coefficient.

## 9. Exhaustion and conclusion

If I>=65 the theorem follows immediately because epsilon_k<=1. Otherwise:

* Sigma=6 forces the two-carrier profile (3,3), excluded in Section 5.
* Sigma=5 forces (4,1), (3,2), or (3,1,1), all excluded in Section 6.
* Sigma=4 with a corrected low forces (3,1), excluded in Section 7 without
  any assumption on c_9 or the marked data.
* Every remaining case has no corrected low, and Section 8 proves I>=64.
  At equality it proves epsilon_k=0 from the actual marked witness.

Thus I-epsilon_k>=64 for every Sigma<=6 under the explicit rigid-shape
hypotheses. Corrected low frames may coincide with each other or with high
frames wherever these hypotheses allow it. Weight-nine highs were used only
through E_9>=0, high dual-index independence, and the explicit n_8=4 exclusion;
no root-only statement was applied to them.
