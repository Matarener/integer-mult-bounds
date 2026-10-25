# Arbitrary rational three-query directions cannot lower the reader bill

## Statement and contract

Use Tekalign's PR3370 even orthonormal partition of the literal P112 labels.
Pair consecutive ports in each group into complete binary Gram-I2 planes.
For each group, its two alternating-half indicators are literal queries.
Write these 32 disjoint vectors as v_c. The fixed scalar fitting matrix is

    K = sum_c v_c v_c^T.

For a scalar vector w, cl(w) contains both ports of each plane touched by a
nonzero entry of w. For an exact term u q^T, price the actual source and reader
by

    C(u,q) = rank_F2 Gram(cl(q), cl(u)).

This is the declared complete-plane rectangular tariff. It is a combinatorial
charge, not a native execution cost. A zero reader has charge zero. Ordinary
transpose is used. Rational coefficient rescaling does not change a nonzero
support or its tariff.

Choose two distinct literal indicators a,b, from groups A,B of sizes m_A,m_B.
The groups may be equal, in which case a,b are its opposite halves. Choose an
arbitrary zero-one vector z supported in A union B such that a,b,z are linearly
independent over Q. Take ANY three rational queries q_1,q_2,q_3 that form a
basis of span_Q(a,b,z). Let their actual readers satisfy

    a a^T + b b^T = sum_i u_i q_i^T.

Then

    sum_i C(u_i,q_i) >= m_A + m_B.

The bound is sharp, attained by queries a,b,z and readers a,b,0. Consequently,
any disjoint collection of these pair replacements in K has total tariff at
least 224. Rational directions have no denominator, sign or magnitude bound.
The seed remains binary and there are exactly three independent queries.
This extends PR3398's seven canonical directions. It does not settle dependent
query lists, multiple extra dimensions, nonbinary seeds or a changed K.

Independence of the queries makes the readers unique. If Q has rows equal to
the formal query coefficients in the basis a,b,z, the reader coefficients are
the first two rows of Q inverse. Thus every reader lies in span_Q(a,b).

## Two elementary tariff facts

Deleting source or reader ports cannot increase C. If two source closures
together contain S and their reader closures both equal R, row-rank
subadditivity gives C_1+C_2 >= rank_F2 Gram(S,R). Repeated ports cause no issue.
The Gram-I_m principal block of a complete orthonormal group gives rank at
least m whenever both closures contain that group.

We also use the retained integral expanded-identity argument, with attribution
to Philippe Van Velzen and PR3345/PR3398. It is recalled here to make the proof
self-contained. Index an expanded operator by a scalar port p and either of
its plane's two binary basis labels. Replace scalar entry K_pq by K_pq times
the two-by-two pairing block of its complete planes. For the literal K the
result is I_224. Nonzero off-diagonal scalar entries connect orthogonal planes
in one group. Diagonal blocks are I2.

An integral identity K=sum u_i q_i^T reduces modulo two. Every expanded term
factors through the binary pairing matrix of its complete source and reader
closures, so its binary rank is at most C(u_i,q_i). This remains true when
reduced coefficients vanish. Subadditivity proves sum C >= 224. Adding back
the unchanged literal terms proves that any INTEGRAL pair replacement costs
at least m_A+m_B. The rational argument below does not reduce denominators
modulo two. It either constructs a support-dominated integral replacement or
uses a direct rank bound.

## At least one zero seed coefficient

Let k_i be the coefficient of z in query q_i. They are not all zero because
the three queries form a basis. Their readers satisfy sum_i k_i u_i=0.

If exactly one k_i is nonzero, that reader is zero. The other two queries are
an invertible two-query recoding of a,b. Such a recoding costs at least m_A+m_B.
To see this directly, write its coefficient rows as (x_1,y_1),(x_2,y_2).
The nonzero determinant has a nonzero product x_1 y_2 or x_2 y_1. In the first
case the first source and its reader both contain A, while the second source
and its reader both contain B, by the inverse's cofactor formula. The other
case reverses these assignments. This also covers A=B.

If exactly two k_i are nonzero, rescale those queries and inverse-rescale their
readers so both seed coefficients are one. Relabel them q_2,q_3. Their readers
are opposites, hence have the same complete closure R. The two source closures
together contain cl(q_2-q_3). Therefore

    C(u_2,q_2)+C(u_3,q_3) >= C(u_2,q_2-q_3).

The original identity becomes a two-query recoding using q_1,q_2-q_3, both in
span(a,b). These directions are independent, since the original three were.
The preceding two-query argument proves the desired floor. No binary-seed
property was needed in these two cases.

## Three nonzero seed coefficients

Rescale every query to seed coefficient one and inverse-rescale its reader.
Write

    q_i = z + x_i a + y_i b.

The three rational points P_i=(x_i,y_i) are noncollinear. The cofactor formula
shows that reader i has an a component exactly when y_j differs from y_k, and
a b component exactly when x_j differs from x_k, for the other two indices.
Every reader is nonzero. A reader's support is a, b or their union.

Because z is binary, a zero query entry on the a half requires x_i=0 or -1.
Likewise, a zero entry on the b half requires y_i=0 or -1. A coordinate outside
the two halves has value z_p independent of x_i,y_i. Replacing a generic x or
y by 0 or -1 can therefore remove support but cannot add it. Existing values
0 and -1 must remain fixed to preserve their zeros.

### All readers contain both groups

Here the three x_i are pairwise distinct, and so are the three y_i. Assume
m_A>=m_B, exchanging the names if needed. At least one x_i is neither 0 nor
-1. Its source closure contains A, so its tariff is at least m_A. The other
two x values differ. At each a port their two query values cannot both vanish;
their complete source closures together contain A. Both readers contain A,
so their tariffs sum to at least m_A by row-rank subadditivity. The total is
at least 2m_A>=m_A+m_B. This includes opposite halves of the same group.

### At least one reader contains only one half

We construct a new noncollinear triangle in {0,-1} squared with each query
support and each reader support contained in its original support.

If both x and y have two distinct values, map each coordinate's two values
injectively to 0,-1, fixing any value already 0 or -1. Three noncollinear
points become three distinct corners of the unit square. Equalities and reader
zero components are preserved, and query support can only shrink.

The remaining case has two distinct x values and three distinct y values,
or the reverse. In the former case, relabel x_2=x_3 != x_1. Map the two x
values injectively to 0,-1 while fixing special values. Map y_2,y_3 injectively
to 0,-1, again fixing special values. If y_1 is 0 or -1 keep it; otherwise
choose either of the two endpoints. The determinant is a nonzero product of
the x difference and y_2-y_3. Thus the image triangle is nonsingular. Reader 1
still contains only a, and the other readers can lose components but gain none.
The reverse case exchanges x,y.

There is no other case. A constant x or y makes the triangle collinear.
When both coordinates have three distinct values, all readers contain both
halves, which was handled above. A duplicate point also makes it singular.

Any three distinct corners of {0,-1} squared have determinant +1 or -1 after
adding a last coordinate one. Their inverse is integral. The resulting query
vectors and readers are integral, and they still realize aa^T+bb^T exactly.
Their rectangular tariffs do not exceed the original rational tariffs, by
support containment and rank monotonicity. The integral floor completes the
proof.

## Evidence and limits

The written argument supplies infinite rational and binary-seed coverage.
The code checks its exact finite support classification. Three rational values
relative to the fixed values 0,-1 have 37 equality patterns. The 1,009 admitted
coordinate-pattern pairs include a harmless relaxation of collinearity in the
all-full-reader case. Each of the 840 mixed patterns has a support-dominated
unimodular grid triangle. The 169 full-reader patterns meet the direct rank
argument. These are pattern classes, not a numerical sample of all rationals.

The literal replay checks all 50,176 entries of I224, all 496 query-pair group
minors and eighteen exact rational UQ fixtures. Fixtures cover one, two and
three nonzero seed coefficients, same-group pairs, unequal group sizes and
noncanonical rational directions. Behavioral controls check singular and
dependent inputs, malformed seed/support data and source/receipt corruption.

All verification is author computation. It is not independent human or formal
proof-kernel review. Native acquisition, coefficient implementation, transport,
dirty private-workspace restoration, hosting, stock, precision, all-size
compilation, supplier admission and outer multiplication remain unproved here.
No new kappa or selected-frontier change follows from this local obstruction.
