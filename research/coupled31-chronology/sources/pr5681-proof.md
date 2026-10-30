# The static connector rank cut is sharp

This package checks the proof in the retained PR5673 source. It also gives
new static witnesses at its rank lower bound. A static witness gives the
thin query maps, their sum, ranks and leaf signatures. It does not give a
chronological word. No new kappa follows.

## 1. Audit of the source implication

Use the source contract, over a field of characteristic two. Each stage j
has full projectors P_jh supported on the core and leaf j. They give an
orthogonal resolution of that support. They commute with the local query
T_j, whose four blocks are I. Their queries are R_jh=P_jh T_j.
A thin map Z has no stage variable. All stage variables are independent.
The target is the stated product of full stages, times the scalar 1+e,
where e squared is zero. These hypotheses are required.

Put x_j=D_j+1. Work first in the quotient which also sets x_j squared to
zero and every other x to zero. This quotient supplies necessary conditions
only. Read the literal calls in application order. If R_< and R_> are the
sums before and after a full call (P,R), the coefficient of e x_j contributed
by that call is

```text
P R_< + R_> P + P R.
```

The coefficient of e first gives sum R=I. Since P R=R, the expression becomes
`P + P R_> + R_> P`. Summing the stage projectors gives E_j. The target has
e x_j coefficient E_j. Thus its defect is exactly the sum of commutators
`P R_> + R_> P`. No pure higher coefficient or endpoint converse is assumed.

Commutation with T gives P=[[A+B,B],[B,A+B]]. The idempotent and orthogonality
relations imply that the A matrices in each stage are orthogonal idempotents
with sum I. Add block rows core and j, then take leaf column k, where k!=j.
The right product R_> P has no such column. A later stage k contributes
A_jh A_kl. Other full stages contribute zero. A thin map contributes
`A_jh (Z_0k+Z_jk)`. This proves the source restriction even when there are
other leaves, noncommuting stage flags and arbitrary blocks outside the
chosen three columns.

If three leaf columns of every thin map agree, the thin contribution does
not depend on which of the other two leaves is k. Therefore S_jk=S_jl,
where S_jk is the sum of A_jh A_kl for jh before kl. For a given call A_jh,
orthogonality within j gives `A_jh S_jk=A_jh(I+P_k)`, with P_k the earlier
prefix of stage k. Thus A_jh P_k=A_jh P_l. Its own earlier prefix is
annihilated. The total prefix S obeys A_jh S=0.

For a formal central variable x, this gives
`(I+xA)(I+xS)=I+x(A+S)` at every step. The product of factors is therefore
`(1+x)I`, since the three final stage prefixes each equal I. Each idempotent
of rank r has determinant (1+x)^r: its image and kernel give a direct sum
basis. Each stage contributes total rank d. The same determinant would have
to be both (1+x)^(3d) and (1+x)^d. These polynomials have different degrees
for d>0. This is a contradiction over every field of characteristic two.
Transpose and reverse the whole word for the row version. The target is
preserved by this operation because its full stage supports commute.

No mathematical gap was found in this implication under these hypotheses.
The source does not exclude a different stage support, an incomplete stage,
a different target or a characteristic-zero caller. This audit does not
supply human review or a proof-assistant theorem.

## 2. Rank cut and its exact static realization

Let F have q elements, where q is a power of two. Let d,h be positive
integers. Put

```text
g = 2 q^(d h) - 1,        W = F^d + (F^d)^g.
```

Index the leaves by all h-by-d matrices M over F: use the zero matrix once
and every nonzero matrix twice. On W, define F_i to send coordinate i of
every leaf to core coordinate i. Define G_i to send core coordinate i to
coordinate i of every leaf. Both have rank one and square zero. Put

```text
K = sum_i (F_i+G_i).
```

This is the required thin sum for odd g. It has rank 2d. Its image consists
of the core and the diagonal leaf space. Its row space consists of the core
and the leaf-sum space.

For 1<=a<=h, let u_a have zero core and leaf block equal to row a of M,
viewed as a column. Let v_a have zero core and the same leaf entries as a
row. Put E_a=u_a v_a. Each E_a has rank one. Every nonzero signature occurs
twice, so

```text
sum_leaf u_a = 0,      sum_leaf v_a = 0,      v_a u_b = 0
```

for all a,b. Consequently E_a E_b=0; F_i E_a=E_a F_i=0; and
G_i E_a=E_a G_i=0. In particular all these maps have square zero.
Take the following thin maps, with both copies of each E_a charged:

```text
F_0,...,F_(d-1), G_0,...,G_(d-1), E_1,E_1,...,E_h,E_h.
```

Their sum is K and their total rank is exactly 2d+2h. Their image span and
row span each have dimension 2d+h. To see independence of the extra h
vectors modulo the diagonal space, first inspect the zero-signature leaf.
It forces any diagonal component to vanish. Then inspect signatures with
one nonzero matrix entry; these force each coefficient of u_a to vanish.
The row proof is the same.

Two leaves have the same block columns in all thin maps exactly when their
matrices M agree. Indeed the F/G columns are constant across leaves, and
E_a recovers row a of M because u_a is nonzero. The row statement uses v_a.
Thus there are exactly q^(dh) signatures; each occurs once or twice.
No forbidden triple occurs.

The source Sylvester bound is R>=2d+a+b, with extra image and row dimensions
a,b. Both equal h here, so equality holds. The source signature bound asks
for the least z such that g<=2q^(dz). For this g, that least z is h.
Thus **both bounds are attained together by square-zero maps**, for every
q,d,h above. This proves sharpness of these static bounds at an unbounded
family of sizes. It does not prove sharpness for complete chronological
words.

## 3. Five rank-two maps for the 31-leaf target

When h=1 and d>=2, write E=E_1 and group the charged rank-one maps as

```text
Z_0 = F_0 + E,
Z_1 = G_1 + E,
Z_(i+1) = F_i + G_((i+1) mod d),    1<=i<d.
```

Each has rank two. The two images and the two row directions are independent.
All squares are zero. For the last group, the two indices differ, so both
cross products vanish. The sum is still K. The union of images and row
spaces still has dimension 2d+1: E is separate from the core/diagonal spaces,
and each rank-two image and row space contains both rank-one directions.
The first map detects the entire leaf column signature, and the second
detects the entire row signature. Therefore all static bounds still pass.

For F2,d=4,h=1 this gives **31 leaves and five rank-two maps**, with total
thin rank ten. For F2,d=2,h=3, the ungrouped construction gives **127 leaves
and ten rank-one maps**. These are exactly the two source search targets.
Their static query maps now have an explicit formula. We do not replay or
admit their source optimistic tariff, and we do not supply either word.
A rejection of these targets must use an additional condition, such as the
chronology equations or the complete polynomial endpoint.

## 4. Verification boundary

The separate checker imports no source code or certificates. It multiplies
literal factors in the truncated polynomial ring and compares the extracted
blocks in 72 words, with 55 noncommuting stage flags and 48 words that have
external stages. It checks all 19,440 ordered three-stage rank-one flag words
in dimension two over F2. Every word fails the prefix condition. A formal
polynomial determinant computation is separate from that census.

Six full static matrix fixtures include both target sizes and an F4 case.
The F4 matrices use the exact regular representation from x^2+x+1; binary
ranks are twice the stated F4 ranks. Each fixture checks every matrix entry,
square, rank, sum and signature. Deleted queries and added identity maps are
rejected. These finite checks support the written general proof; they do
not replace it. No native lift, frame adapters, ownership/tape bill, complete
caller or kappa improvement is established.

Credit the retained PR5673 proof and its source lineage for the obstruction
and rank bounds. The sharpness construction and separate audit code are new
here. Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
