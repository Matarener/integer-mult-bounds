# The complete marked d=0 invoice

Prepared by conorholds, with substantial OpenAI Codex assistance. Apache-2.0.

## Main theorem

Use the root, label, code, basis and invoice definitions of Section 1 below.
Let S contain C, dim(S)=8+t for t in {2,3}, and let F be ANY actual basis of S
whose restricted dual functionals xi_j are all nonzero. Put
T=span{q in S:w(q)<=7} and assume C intersect T=0. Let v be a nonframe root,
and suppose a marked basis index k and a word g satisfy

    xi_k(h)=gamma(r_v,h), gamma!=0,
    g in S, g|O_v=0, phi_k(g)!=0,
    O_v={v} union {s in P:(r_s,r_v)=0}.

Define I=sum_(q in F)w(q)-n_c and epsilon=[ell_v in U(q_k)]. Then

    I-epsilon >=64.

This is a scoped characteristic-zero theorem. Its intrinsic statement does
not assume N8, K2, a pre-existing rigid basis shape, a minimum actual basis,
or distinct corrected LOW frame indices. It does not assert that every
masked/two-sided P112 decoder falls into these hypotheses. The explicit
actual-factorization consumer and its remaining global boundary are derived
in [CONSUMER.md](CONSUMER.md).

[UNMARKED.md](UNMARKED.md) additionally proves I>=64 without a marked root
or g, enabling the consumer to cover both paid and free singleton pivots.
[RAW-COUNT.md](RAW-COUNT.md) supplies a raw marked correction cap valid for
every d; the full marked inequality below retains its explicit d=0 scope.

Proof structure: Sections1-7 derive the raw shape, actual Sigma<=8 and rule
out every actual Sigma=8 profile when I<=64. Section 8 handles Sigma7 and
[SMALL.md](SMALL.md) handles every Sigma<=6, including the actual marked g
coefficient at the last equality boundary. This first establishes I>=64
for BOTH epsilon values; only then is I=64,epsilon=1 excluded.

## 1. Sources and the declared model

Scientific source pins:

* PR3154: `708f0ad8928c383de8294aea3c126e9461d2066d`, `research/p112-reduction-to-conjectures/checks/CONJ-G/NOTES.md`, Section 0 (basis, restricted duals, raw corrected ledger, marked root row), and `checks/CONJG2/NOTES.md` (the d=0 target). We do not invoke its N8 statement or its already-derived rigid shape.
* PR2832: `0da81b22178e70dbf59a23dda02371c6201fa4f3`, `research/decoder-floors-reduction/README.md`, Sections1,2.2,2.3,3.4 (weight/model conventions, actual versus projected normalization, correction catalogue). No actual normalization conclusion is transferred to the projected decoder here.
* PR3166: `7c2a62363ad4945e8803fedea6ead78e1ad412b2`, `research/e8-d0-root-swaps/{PROOF.md,EXTENSION.md,verify.py,extension_check.py,geometry_audit.py}`. Inherited geometry is enumerated explicitly in Section 2 below.

The working baseline is archive main `24db9bfffd4a7c812545ea6ae58853cb9ef094b2`; its materialized PR3166 files are byte-identical to the prior `463113d675af7410ac91d53a4fed51ec6494eb9a` baseline. These frozen files are the local source used by the bounded probes. PR3191/K2 is not a premise.

Let E be the 120 E8 root lines and let F0={f_1,...,f_8} be the fixed orthogonal frame, with representatives of squared norm2. Put P=E minus F0. Work over an arbitrary characteristic-zero field K. All fixed roots and the frame have rational coordinates, and their rational bilinear pairing extends to K.

Write

    p_h(t)=(r_t,h), t in P,
    C={p_h:h in K^8}.

Evaluation is injective, so dim C=8. Each root/frame line has its standard leading-one label ell_t in V=F2^9; write z_i=ell(f_i). The labels are distinct, and no z_i occurs in P. For a vector q in K^P define

    U(q)=span_F2{ell_t:q(t)!=0},
    w(q)=dim_F2 U(q).

Let S contain C, let dim S=8+t for t in {2,3}, and let F=(q_1,...,q_{8+t}) be a basis of S. Let phi_j be its dual basis, and identify its restriction to C with x_j in K^8 by

    phi_j(p_h)=(x_j,h).

Thus, for every h,

    p_h=sum_j (x_j,h)q_j.                                      (1)

Assume every x_j is nonzero, as in the main theorem. Call j corrected if x_j is a nonzero scalar multiple of some frame f_i and z_i belongs to U(q_j). Set

    n_c=#{corrected j},
    I=sum_j w(q_j)-n_c.                                       (2)

Equation(2) defines the intrinsic invoice; CONSUMER.md derives it as the exact projected decoder cost in its explicit actual-factorization class. No assertion that distinct corrected rows have distinct frame indices is made.

Let

    T=span_K{q in S:w(q)<=7},
    d=dim_K(C intersect T).

Assume d=0 and I<=64. Finally assume some marked index k satisfies

    x_k=gamma r_v, gamma!=0, v in P.                           (3)

A nonframe E8 root has four nonzero frame pairings, so x_k is not a frame row and is uncorrected. Sections2-7 derive the raw shape, cap and Sigma8 exclusion using only this marked root row. The main theorem additionally requires g, which is used in SMALL.md and the final assembly; it cannot be omitted.

## 2. Exact geometric inputs

The following inputs concern only the fixed E8/P112 geometry. They are separated from the new decoder deductions.

**G1: leading-one labels and support caps.** For rank r=1,...,8, a set of live labels spanning rank at most r has cardinality at most

    g(r)=(1,2,4,8,12,20,36,64).                              (4)

These are PR3166 PROOF Section 4's full-E8 caps, which also bound P. Its text gives the signed quadratic/Gauss-sum argument; its checkers bind the root model and low-rank cases. In particular a binary rank-eight hyperplane contains at most 64 live points.

A corrected vector has weight at least 3. Indeed a rank-one/two space generated by live leading-one labels has only one/two points in its leading-one affine slice, namely the generating live labels; it cannot contain an excluded frame z_i. A corrected vector of weight3 has support EXACTLY three live roots: its leading-one slice has four points, one is z_i, and its support needs at least three independent live labels. Thus its three support labels XOR to z_i. These last assertions follow directly from the leading-one model, not an additional census.

**G2: frame support and matched carrying cuts.** For every frame f_i, |Off_P(f_i)|=56, and if H is any binary hyperplane containing z_i, then

    |Off_P(f_i) minus H| >=24.                               (5)

Here and below a set of roots is identified with its labels in H. This follows from PR3166 PROOF Section 4's full-root remainder character bound24: the frame remainder is exactly its 56-point P support. It is also checked as `frame_minimum_deletions=24` by EXTENSION Section 6 / `frame_plane_checks`.

Consequently, if q=p_{f_i}+tau has w(q)=8 and contains z_i in its label span, then |supp tau|>=24: use H=U(q), and every nonzero p_{f_i} coordinate outside H must be canceled by tau. Scalar multiples of p_{f_i} give the same conclusion. An unperturbed frame codeword is uncorrected.

**G3: two-/three-frame matched cut bounds.** Let h be one of

    f_i+/-f_j,
    f_i+/-f_j+/-f_l,

with distinct indices, with arbitrary overall nonzero scalar, and let H be a binary hyperplane containing z_i. Then

    |Off_P(h) minus H| >=24.                                 (6)

Both finite implementations check (6) directly, with sharper matched minima34 and 28. This agrees with the predecessor catalogue: the norm-four exceptional12-cut is the hyperplane ker[(a,x) -> a+(f_i+/-f_j,x) mod2], which contains no frame label, since all frame pairings with this normal are even. All other cuts in that catalogue are at least 32. PR3166's norm-six Off80 row has minimum deletion24 over all hyperplanes. No source N8 premise is involved.

The registered replay checks every matched normal/index pair and all 255 hyperplanes containing its matched z_i in two algorithms, obtaining minima34 for two-frame sums and 28 for three-frame sums. The proof below needs only the inherited weaker24.

**G4: two-frame non-axis deletion rank, including one-point deletion.** For every ordered pair i!=j, each of the three support strata represented by

    h=f_i+f_j, f_i-f_j, f_i+2f_j,

and every binary hyperplane H containing z_i, put D=Off_P(h) minus H. Then

    rank_F2 labels(D)=8,
    rank_F2 labels(D minus {u})=8 for EVERY live point u.      (7)

This is precisely PR3166 EXTENSION Section 6's frame-plane no-coloop input, checked in `extension_check.py:frame_plane_checks`. Its complete domain is56 ordered pairs times3 non-axis strata times255 hyperplanes=42,840 cases. The generic stratum covers every ratio outside0,+1,-1 over any characteristic-zero K, since all nonframe-root frame pairings are0,+1,-1. The inherited two-model check uses independent Euclidean and Cartan label constructions. The new independent Gram-row implementation additionally checks all 42,840 cases by a dual-functional no-coloop criterion, instead of predecessor dependency-mask elimination.

**G5: root/frame incidence.** Each nonframe root pairs nontrivially with exactly four frame roots, with pairings +/-1. Distinct four-element incidence blocks have even intersection. These are E8 integrality facts: r=(1/2)sum_i(r,f_i)f_i and (r,r)=2 imply four nonzero pairings; (r,s)=(1/2)sum_i(r,f_i)(s,f_i) is integral, giving even intersection. Frame reflections independently flip the four signs, so each block has eight projective root lines. There are112/8=14 blocks. No three indices can occur in two blocks (intersection3 would be odd);14*binom(4,3)=binom(8,3), so every triple occurs in exactly one block. This is the S(3,4,8) incidence property, derived here from the root facts.

## 3. A restricted three-frame cancellation lemma

**Lemma3.1.** Let q=p_h+tau satisfy w(q)=8 and z_i in U(q). Suppose the i-th frame coefficient of h is nonzero and h is supported on at most three frame axes. If |supp tau|<=23, no such q exists.

**Proof.** H=U(q) is a binary hyperplane containing z_i. Outside H all nonzero coordinates of p_h must be canceled, hence

    Off_P(h) minus H subset supp tau,
    |Off_P(h)|<=64+23=87.                                   (8)

The following restricted-form multiplicities follow from G5; the signs are projective, so a form and its negative are identified.

| Number of selected axes | Restricted root forms and multiplicities on P |
|---|---|
|1|zero56, single-axis56|
|2|zero24; each singleton32; each signed pair12|
|3|zero8; each singleton16; each signed pair8; each signed triple2|

For example, for a fixed triple of axes the 14 incidence blocks meet it in zero,one,two,three indices with multiplicities1,6,6,1. There are two singleton blocks per index and two pair-only blocks per pair; the eight sign patterns per block give exactly the displayed row. The one-/two-axis rows follow similarly.

For two nonzero coefficients a,b, the Off size is76 if a=+/-b, and 88 otherwise. For three nonzero coefficients a,b,c, it is80 if all coefficients are equal up to signs. Otherwise it is at least 94: if exactly one pair is equal up to sign, there is one zero pair-form and at most one zero triple-form, leaving at least 48+40+6=94 live points; if no pair is equal up to sign, all six pair-forms survive and at least three triple-forms survive, giving at least 48+48+6=102. Two zero triple-forms would force a coefficient to vanish or a signed pair equality. These arguments are linear identities over K and do not use an ordering or absolute values in K.

Thus (8) forces h to be a frame axis, a signed equal two-frame sum, or a signed equal three-frame sum. Its matched i lies in its nonzero support. G2/G3 then give |Off_P(h) minus H|>=24, contradicting |supp tau|<=23. QED.

In particular the lemma applies with two frame axes and support<=23.

## 4. Raw rigidity without N8 or K2

Let f=|F intersect T|. Since C intersect T=0 and C+T lies in S, dim T<=t,
hence f<=t. For each actual basis member put e(q)=w(q)-[q is corrected].
Every e(q)>=1: an uncorrected nonzero word has positive weight, and a
corrected word has weight at least 3 by G1. Every member outside T has
weight>=8, and therefore e(q)>=7. Consequently

    I >= f+7(8+t-f)=56+7t-6f.

If f<t, this is at least 62+t. For t=3 it already exceeds64. For t=2,
f=0 costs at least 70; only f=1,I=64 can remain. Equality forces the single
inside member to be an uncorrected unit q_0 and all nine outside members
to be corrected weight8 members. This rigidity argument needs no mark.

Group the nine corrected outside rows by their frame index. All eight
groups are nonempty: otherwise equation(1), evaluated at the missing frame
f_a, would express its 56-point codeword as a multiple of q_0. Nine objects
in eight nonempty groups give seven singleton groups. At a singleton j of
frame a, equation(1) gives

    p_(f_a)=lambda q_j+alpha q_0, lambda!=0.

Thus q_j is a nonzero scalar frame codeword plus a correction supported on
at most one point. Its corrected rank8 span contains z_a, contradicting G2's
matched carrying cut24. Therefore f=t=dim T and F intersect T is a basis
of T. Dimensions now give S=C direct-sum T, with exactly eight outside
members of weights8/9. No projected-row normalization was used.

At this stage the mark is used: its nonframe root dual is uncorrected, so

    n_c<=7+t,        sum_F w=I+n_c<=71+t.                    (9)

Before the later Sigma cap, a member of F intersect T need not itself have
weight<=7: T is a span of low-weight words. Both the effective-cost argument
and (9) used only positive actual weights, and respect this distinction.

## 5. Rigid-basis duality and the actual coefficient map

Write F_T=(b_1,...,b_t). Each high member has a unique form

    q_l=p_{h_l}+tau_l, tau_l in T,

and the eight h_l form a basis of K^8. Let mu_l be their dual row functionals, so mu_l(h_m)=delta_lm. Since high phi_l vanish on T, x_l=mu_l as functionals on C. In particular ALL corrected high frame indices are distinct; this follows from dual-basis independence, including weight9 highs, and not from N8.

There is a unique linear A:K^8->T with A(h_l)=tau_l. If psi_a is the low dual coordinate, then psi_a(p_h)=-psi_a(A(h)), hence

    A(h)=-sum_a (x_a,h)b_a.                                 (10)

This is the actual coefficient map. It permits repeated corrected-low frame indices and permits a corrected-low frame index to coincide with a corrected-high one. No such disjointness is assumed below.

The generic actual-basis/quotient derivation of this identity is formalized
in formal/ActualCoefficientMap.lean; its high coordinates are derived from
projection of the actual basis expansion, not assumed as extra coefficients.

Let J be the set of ALL corrected high frame indices. For a corrected high l with matched index i, duality gives

    (h_l,f_i)!=0,
    (h_l,f_j)=0 for j in J minus {i}.                        (11)

Therefore h_l lies in its own matched frame axis plus the 8-|J| unmatched axes. If all eight highs are corrected, J is all eight axes and each h_l is its own matched frame direction.

Define

    Sigma=sum_a w(b_a),
    c9=#{high members of weight9},
    c9_corr=#{corrected high members of weight9},
    n8=#{corrected high members of weight8},
    n_T=#{corrected low members},
    d9=c9-c9_corr>=0.

The ledger is exactly

    I=64+Sigma-n_T-n8+d9.                                   (12)

Thus I<=64 implies

    n_T+n8>=Sigma+d9,                                      (13)

and the raw marked count (9) gives

    Sigma+c9<=7+t.                                        (14)

Do not replace n8 by |J| in (12): |J|=n8+c9_corr, and weight9 corrected supports are rank9, not rank8.

**Lemma5.1 (all-high-corrected obstruction).** All eight highs cannot be corrected if n_T=t-1.

Indeed the marked row must then be the sole uncorrected low row. The other t-1 low rows are frame rows, and the marked row is a nonframe root row with four nonzero frame coordinates. Equation(10) shows A(f_i)=0 for every axis outside the union of at most(t-1)+4<=6 axes. If all eight highs are corrected, their normals are the eight frame axes. An axis outside that union therefore gives an unperturbed high frame codeword, which is uncorrected by G2. Contradiction. Repeated low frame indices only reduce the union size.

## 6. Exhaustive cap: Sigma9 and Sigma10 are impossible

By (14), Sigma<=9 for t=2 and Sigma<=10 for t=3. We now exclude the boundary values. A corrected low member has weight>=3; a corrected weight3 member has support3. The support of T is the union of the actual b_a supports.

### 6.1 t=2, Sigma9

Equation(14) forces c9=0. Equation(13) and n8<=8 require n_T>=1.

If n_T=1, then n8=8 and all highs are corrected; Lemma5.1 applies.

If n_T=2, both lows are corrected and the marked row is high, so n8<=7. Equation(13) forces n8=7. The low weight profiles are only(6,3) or(5,4), since each part is at least 3. Their union supports have sizes at most 20+3=23 or12+8=20, using G1 and the sharper carrier3 support. Seven distinct corrected high frame indices confine every corrected high normal to at most two frame axes by (11). Each of the seven members has weight8, and its span contains its matched frame. Lemma3.1 excludes it. Contradiction.

### 6.2 t=3, Sigma10

Equation(14) forces c9=0. Equation(13) requires n_T>=2.

If n_T=2, n8=8 and Lemma5.1 applies.

If n_T=3, the marked row is high and n8<=7; (13) forces n8=7. The low profile is only(4,3,3), with union support<=8+3+3=14. Seven corrected high indices again give two-axis normals, excluded by Lemma3.1.

### 6.3 t=3, Sigma9

Equation(14) permits c9=0 or1; equation(13) requires n_T>=1.

If n_T=1, then n8>=8+d9. Since there are only 8-c9 weight8 high members, this forces c9=0,n8=8. All high normals are the eight frame axes. Let i be the frame index of the corrected low. Its weight is at least 3, so the other two actual low members have positive weights of total at most 6; their union support has at mostg(5)+g(1)=13 points (all other positive partitions of total<=6 give no larger bound). For any frame axis a!=i, equation(10) makes A(f_a) a combination of those two members. Its support is at most 13. The corresponding high is a corrected frame codeword plus at most 13 cancellations, contradicting G2's24 bound.

Suppose n_T=2. If n8=8, c9=0 and Lemma5.1 applies. Otherwise (13) forces n8=7. The eighth high can only be:

* an uncorrected weight8 member (c9=0); or
* a corrected weight9 member (c9=1,c9_corr=1).

An uncorrected weight9 eighth member would have d9=1 and violate (13). In the corrected weight9 case, all eight highs are corrected, so Lemma5.1 applies. In the uncorrected weight8 case, the low profiles and support bounds are

    (5,3,1):16; (4,4,1):17; (4,3,2):13; (3,3,3):10.

These are exhaustive: two parts are corrected carriers of weight>=3; any weight3 corrected part has support3. Seven corrected high frame indices give two-axis weight8 normals, excluded by Lemma3.1.

Finally suppose n_T=3. All lows have weight3 and support3, so the actual profile is(3,3,3) and |supp T|<=9. The marked row is high. Equation(13) gives n8>=6. At least six distinct high frame indices are therefore corrected, so every corrected weight8 high normal has at most three axes by (11). Lemma3.1 excludes it. This argument covers c9=0 or1 and both statuses of a possible weight9 high.

These cases exhaust the raw cap values, proving Sigma<=8.

## 7. Complete actual Sigma=8 exclusion

Assume Sigma=8 and I<=64. Since corrected lows have weight>=3, n_T<=2. Equation(13) gives n8>=6. Hence every corrected weight8 high normal has at most three frame axes by (11).

First suppose the ACTUAL low profile is not(7,1). For t=2 the possibilities are(6,2),(5,3),(4,4), with union support bounds22,16,16. For t=3 the positive partitions of 8 are(6,1,1),(5,2,1),(4,3,1),(4,2,2),(3,3,2), all with union support at most 22. Lemma3.1 then excludes any of the required six corrected weight8 highs. This argument uses the actual basis only: no minimum-cost basis, root-only normal filter, or kappa split is needed.

It remains to handle the actual profile(7,1), necessarily t=2. Write

    T=span_K(a,delta_u), w(a)=7,
    B=supp T, |B|<=36+1=37.                                (15)

At most one low is corrected. The eight high dual rows are independent, so at most eight highs are corrected, and n_c<=9. If n_c=9, all eight highs and the weight7 low are corrected. The marked root row is the unit low, so n_T=1=t-1 and Lemma5.1 gives a contradiction. Therefore

    n_c<=8                                                  (16)

LOCALLY in this actual(7,1) case, with no general N8 assertion.

Its raw weight is72+c9, so I<=64 and (16) force c9=0,n_c=8,I=64. At least seven of its eight weight8 highs are corrected. Let J be their distinct matched frame indices. If |J|=8, each normal is its own frame axis. If |J|=7, write j0 for the unused frame index. Each corrected normal h_i lies in span(f_i,f_j0), with a nonzero f_i coefficient.

In the latter case, any non-axis normal has the support stratum f_i+f_j0, f_i-f_j0, or generic f_i+2f_j0. Let H=U(q_i), a rank-eight hyperplane containing z_i, and put D=Off_P(h_i) minus H. Cancellation gives

    D subset supp a union {u}.

Thus labels(D minus {u}) have rank at most 7. But G4 gives rank8 even after deleting any one point. Contradiction. Consequently all corrected normals, at least seven of them, are their own distinct frame directions.

Each such corrected frame high requires at least 24 canceled coordinates from B by G2. Count these cancellation incidences over the selected distinct frames. Every live root in B pairs nontrivially with exactly four frame axes by G5, so

    7*24 <= number of required cancellation incidences
          <= sum_{r in B} #{selected f_i:(r,f_i)!=0}
          <=4|B|<=4*37=148.

But7*24=168>148. This excludes(7,1) and completes the Sigma-eight theorem. No minimality assumption on w(a)=7 was used: the actual basis profile(7,1) suffices.

## 8. Sigma seven, smaller totals, and assembly

Assume I<=64. Sections4-7 give S=C direct-sum T, dim(T)=t, an actual low
basis of total Sigma<=7, and eight high members with independent code
directions and weights8/9. Every actual low member now has weight<=6,
since t>=2 and the other members have positive weights.

If Sigma=7, cost(T)<=7 and dim(T)>=2, so PR3166 EXTENSION TheoremC forces
every weight8 high direction to be a root, including possible frame roots.
Use a minimum low basis only for the support bound |supp(T)|<=21. A frame
normal cannot give a corrected weight8 high: at least 24 cancellations would
be needed by G2. For the remaining nonframe root normals, distinct matched
HIGH frame indices follow from duality. Each root uses its own matched axis
and three unmatched axes. Six or more matched roots leave too few axes;
five force two incidence blocks to intersect in three positions, impossible.
Thus n8<=4. A corrected low costs at least 3, so n_T<=2. The ledger gives

    I=64+7-n_T-n8+d9 >=65,

a contradiction. This reuses PR3166's geometric TheoremC and elementary
incidence argument, not the N8 assumption listed for that package's old C1
corollaries.

Every remaining actual total is Sigma<=6. SMALL.md proves that either I>=65,
or I>=64 and the actual marked witness forces epsilon=0 at equality. It
permits coincident corrected LOW frame indices, arbitrary characteristic-zero
coefficients, weight9 highs and both locations of k.

Finally if I>=65 from the outset, I-epsilon>=64 since epsilon<=1. If I<=64,
the preceding exhaustive cases give I=64,epsilon=0. This proves the theorem.
The exact rational fixture in fixtures.py has I=64,epsilon=1 when g is
omitted; all its other intrinsic hypotheses hold. Thus deleting the actual
witness condition would make the main statement false.

## 9. Verification boundary

The proof is written mathematics with finite E8 inputs, not a full Lean
formalization. The registered replay authenticates and recomputes the used
PR3166 geometric inputs, checks the new restricted-frame/carrier/private-set
facts by Cartan-lattice and separate D8+ Gram-row algorithms, and checks exact
actual-factorization controls. The three-axis coefficient classification in
Section 3 is an algebraic argument over K; finite coefficient-grid examples
are only controls and are not substituted for that argument.

The generic private-incidence, private-label, carrier-parity and actual coefficient-map lemmas
are additionally formalized in Lean, with their E8 instantiation left explicit. Source-specific
credit, exact pins, bounded commands and remaining questions are in README.md,
SOURCES.json and TASK.json. No selected-frontier or global P112 conclusion is
inferred from this scoped proof.
