# Normalization-stable partial quotients and high right rank

Use PROOF.md's fixed full-E8 scalar code C, binary labels, COPY tariff and
singleton left space C+Kδ_v. All results here are in characteristic zero.
No claim is made that these are all possible right spaces. Actual spaces
and ranks always discard zero-factor terms as specified in PROOF.md.

## 1. Statements

**Theorem Q (partial coordinate quotients).** Every finite raw exact
factorization PQ^t=N0 satisfying

```
col(P)⊂C+Kδ_v,       col(Q)⊂C+D_A
```

has COPY≥72 in either of the following cases:

1. |A|≤13 and u_v∉span_F2{u_a:a∈A}; or
2. A⊂H_v and |A|≤28, with no further binary-rank assumption.

The second statement uses the new relative nonroot 27-deletion theorem,
the root weight-seven threshold 29, and a low-budget support argument,
proved and certified in RELATIVE.md. The first
allows coordinates scalar-orthogonal to v and uses only the inherited
global root-only threshold 14. Both statements handle arbitrary proper
subspaces of the coordinate quotient, including those created by merging
proportional encoder columns. They are stronger than requiring the actual
right space to be a full coordinate extension.

**Theorem H (high actual rank).** If the exceptional left P rays each
occur at most once, any scalar-active exact PQ^t=N0 with col(P)⊂C+Kδ_v and actual
rank Q≥24 has COPY≥72. No coordinate hypothesis is imposed on Q.
In particular this holds after left proportional merging if that actual
rank is still at least 24. A lower bound on an unnormalized raw rank is
not enough.

Theorem H follows immediately from the strict basis floor in FINITE.md
and PROOF.md's strict-floor corollary. Its one-sided counting premise is
an additional-slack consequence of the PR2962 relaxation. The remainder
of this file proves Theorem Q, whose equality-basis argument is different.

## 2. Reduction to the actual coefficient space

Apply left proportional merging as in PROOF.md §8. The actual reader
space S still contains C by exactness and satisfies S⊂C+D_A. Since
|A|≤28<57 and the code distance is 57, C∩D_A=0. Thus

```
S=C⊕D',       D'=S∩D_A,       e=dim_K D'.
```

Indeed the C component of every vector belongs to S, so subtracting it
leaves its D_A component in S. This is the ACTUAL D' after merging;
we do not replace it by D_A or by its coordinate support.

In either case of Theorem Q, u_v is outside U_A=span_F2{u_a:a∈A}.
For neighbors, U_A⊂u_v^⊥ whereas β(u_v,u_v)=1. Consequently every pure
D' vector has w≤8, v∉A, and no pure vector can have u_v in its binary
support span.

If e≤1, both actual factor ranks are at most nine and PR3755's existing
all-odd theorem gives COPY≥72. Suppose e≥2 from now on.

## 3. Mixed low vectors and the feasible normal-rank budget

In case 1, every mixed q=E(h)+d with w(q)≤8 has exactly weight eight
and admits

```
h=c r_a,   a∈A, c≠0,    U(q)=u_a^⊥,
d(a)=−2c,  d(x)=0 at every x≠a orthogonal to r_a.       (1)
```

Choose a nonzero binary annihilator z. Then Off(h)∩O_z⊂A. A nonroot
has at most 42 zero root lines and |O_z|≥56, so it requires at least 14
cancellations. Every nonmatching root character requires at least 24.
Under |A|≤13 only the root's own character can occur, proving (1), with
no mixed vector of weight at most seven. The same actual d∈D' witnesses
that root's eligibility in PR3166 Theorem A.

In case 2, **no mixed vector has weight at most seven** through |A|≤28.
A nonroot E(h) has support at least 78, so after 28 corrections it retains
at least 50 sites, exceeding the binary-weight-seven capacity 36. For a
root normal, RELATIVE.md §8's exact two-character argument says at least
29 neighbor corrections are required for binary weight at most seven.
This assertion is weaker than an eligible-root-only classification of
weight-eight words; that stronger classification already fails at 24.
Nonroot weight-eight words can occur at 27 and are allowed here.

Let R be the span of the scalar normals of all mixed weight-eight words
in S, and let r=dim R, γ=c(D'). We claim in BOTH cases

```
r≤γ,           r≤8.                                  (2)
```

For γ≥8 this is immediate. For case 1 with γ≤7, all feasible words satisfy
(1), and PR3166's weighted root-swap Theorem A gives r≤γ.
For case 2 with γ≤7, recall e≥2. Take a minimum basis of D', with
positive weights summing to γ. The union B of its coordinate supports
has at most 21 sites: among partitions of an integer at most seven
into at least two positive parts, the largest sum of support capacities
is g(6)+g(1)=20+1=21. The verifier checks all 37 such partitions.
Every actual correction d∈D' is supported on this SAME B⊂H_v.
The relative nonroot threshold 27 and root-mismatch threshold 24 now
force (1) for every feasible mixed weight-eight word, since |B|≤21.
The weighted root-swap theorem again gives r≤γ.

This minimum basis is used only to bound the support of the entire
coefficient space. The equality-basis proof below still treats the given
actual reader basis, with no substitution. The inherited weighted
root-swap theorem is essential; capacity estimates alone do not prove
this partial-quotient invoice.

## 4. Every actual equality basis has the required low span

Let F be ANY actual basis of S. Let ℓ be its number of vectors of weight
at most seven, let κ be their weight sum, and put d=e−ℓ. The low members
are pure by the no-mixed-weight-at-most-seven conclusion of §3, hence ℓ≤e. All vectors of weight at most eight lie in
D'+E(R), whose dimension is e+r. If W is the total basis bill, counting
low, weight-eight and weight-nine members gives

```
W ≥ κ+8(e+r−ℓ)+9(8−r)
  = 72+8d+κ−r.                                       (3)
```

If fewer than e+r members have weight at most eight, this only increases
the lower bound. Complete the ℓ actual low vectors to a basis of D'.
Every added pure vector has weight at most eight, so

```
γ≤κ+8d.
```

Together with (2), (3) proves W≥72. Moreover, if d=1, e≥2 gives
ℓ=e−1≥1 and κ≥1; using r≤8 in (3) gives W≥73. If d≥2, the same bound
gives W≥80. Thus every ACTUAL bill-72 basis has d=0: its actual low
members form a basis of D', and every high basis coordinate functional
annihilates D'. This is not a substitution of a preferred minimum basis.
It also covers binary rank eight; pure weight-eight directions do not
create an omitted equality case.

## 5. The actual free-pivot cut and the marked contradiction

Take q=E(h)+d∈S supported on H_v. For case 2, d itself is supported
on H_v. Thus E(h) vanishes on O_{u_v}. Those root rows span all eight
scalar dimensions by the full-code rank input, so h=0. This proves
that the cut is pure for ANY neighbor support size, independently of
the weight-eight classification.

For case 1, if q were mixed, (1) would give U(q)=u_a^⊥⊂u_v^⊥. These
eight-dimensional hyperplanes are equal; nondegeneracy and distinct labels
force a=v, contradicting v∉A. Hence again the cut is pure. In both cases

```
S∩K^{H_v}=D'∩K^{H_v}⊂D'.                              (4)
```

For neighbor supports this equals all D'. For case 1 the intersection
may be proper. It need not be spanned by those actual basis members
individually lying in the cut; functional annihilation is sufficient.

In any actual equality basis, every pure low member has binary support
span inside U_A and cannot carry u_v. Thus every rebated basis member
j with u_v∈U(q_j) is high. Its actual coordinate functional annihilates
D', and hence the cut (4). This is exactly PROOF.md's functional cut
hypothesis. The generic coupling lemma proves COPY≥72 for the normalized
factors, and nonincrease under merging proves the original raw bound.

Equivalently, the only unpaid dangerous state has a free δ_v pivot and
one rebated J_v column, with all other readers an actual bill-72 basis.
After normalizing those encoders to δ_v and J_v, quotient exactness gives
λ_J(q_pivot)=−1. Equations (3)–(4) instead give λ_J(q_pivot)=0. These
statements concern the same actual factorization and the same basis.

## 6. Boundary and genuine tests

The sharp partial-quotient fixture in SHARPNESS.md has dim D'=2, minimum
bill seven, no coordinate unit rays, seven feasible independent root
normals, and actual ranks (9,10) with COPY=72. It is normalized on both
sides. A second pivot variant includes coordinates orthogonal to v and
has a proper cut; it is left-normalized only and its right merge lowers
left rank to eight. The verifier records that distinction.

A separate minimum-basis countercontrol shows why one cannot assume a
cut is spanned by its individually vanishing actual basis columns for
arbitrary coefficient spaces. RELATIVE.md supplies the 24-neighbor
failure of the eligible-root-only classification and the 29-neighbor
failure of the assertion that all mixed low vectors are pure. Neither control is a
counterexample to Theorem Q, whose hypotheses and supporting boundaries
remain explicit.

Open: arbitrary partial right quotients of dimensions 10–23 without these
support conditions; whether a different actual-basis argument crosses the 29-neighbor
mixed-low boundary; full formal E8 and invoice assembly. Nothing
here changes the selected frontier or proves the general two-sided C′.
