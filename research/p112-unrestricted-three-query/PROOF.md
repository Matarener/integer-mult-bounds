# Three independent queries cannot lower a literal pair's reader tariff

## Statement

Use Tekalign's PR3370 partition of the 112 literal P112 labels into even
orthonormal groups. Within each group, consecutive ports form complete binary
Gram-I2 planes. Each of its two alternating halves defines a scalar indicator
v_c. The fixed fitting matrix is K = sum_c v_c v_c^T.

For scalar vectors q,u over a field F, let cl(q),cl(u) contain both ports of
every plane touched by a nonzero entry. Price the actual source and reader by

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

The coefficient field F and the tariff field F2 are distinct. Coefficients
need not be binary, positive, integral or rational. A zero reader costs zero.

Choose two distinct indicators a,b from groups A,B of sizes m_A,m_B. They
have disjoint scalar supports. The groups can coincide, in which case these
are the opposite halves. Suppose THREE linearly independent scalar queries
q_1,q_2,q_3 and actual readers u_i satisfy, over F,

    aa^T + bb^T = sum_i u_i q_i^T.

There is no restriction on the queries outside A union B. Then

    sum_i C(u_i,q_i) >= m_A + m_B.

The bound is sharp. Use queries a,b,z for any independent third vector z and
readers a,b,0. Consequently disjoint replacements of this kind cannot lower
the literal total 224. This is a theorem about the fixed matrix and complete
plane rectangular charge, not native execution, supplier admission or kappa.

PR3407 proved the rational case for one binary seed supported in A union B.
The new step below changes the seed separately at every port. This removes
both seed restrictions and makes the argument valid over every field. It
does not preserve the seed vector or the original query span, and it does
not need to. It constructs a cheaper integral realization of the SAME target.

## Reduction to three formal coordinates

The target row space is span_F(a,b), so it lies in the query span. Complete
a,b to a basis a,b,z of that three-dimensional span. Write each q_i in this
basis, with coefficient matrix Q. Its rows are independent, so Q is invertible.
The readers are unique and lie in span_F(a,b). They have coefficients given
by the first two rows of Q inverse. Let k_i be each query's z coefficient.
They are not all zero, and sum_i k_i u_i = 0.

Deleting source or reader ports cannot increase C. Rank subadditivity also
implies that two terms with the same reader closure have combined charge at
least the charge of the union of their source closures against that reader.
These facts involve only binary Gram matrices and do not depend on F.

## One or two nonzero seed coefficients

If exactly one k_i is nonzero, its reader vanishes. The other two queries are
an invertible recoding of a,b. For such a recoding, write the coefficient rows
as (x_1,y_1),(x_2,y_2). Its determinant is nonzero, so x_1 y_2 or x_2 y_1 is
nonzero. In the former case query 1 and reader 1 both contain the entire a
half, and query 2 and reader 2 both contain the entire b half. Their complete
closures contain A and B respectively. The orthonormal principal minors give
charge at least m_A+m_B. The other case exchanges the two terms. This proof
also applies when A=B and in characteristic two.

If exactly two k_i are nonzero, scale them to one and call them q_2,q_3.
Their readers are opposites and therefore have identical supports. The union
of their source supports contains supp(q_2-q_3), so rank subadditivity yields

    C(u_2,q_2) + C(u_3,q_3) >= C(u_2,q_2-q_3).

The original identity is now the two-query recoding with q_1,q_2-q_3. These
are independent and lie in span(a,b). The preceding argument proves the floor.
No assumption about seed values or locations entered these reductions.

## Three nonzero seed coefficients

Scale all k_i to one and inverse-scale each reader. This preserves supports.
Write q_i=z+x_i a+y_i b. The points P_i=(x_i,y_i) are noncollinear. With cyclic
indices, the cofactor formula shows that reader i has no a component precisely
when y_j=y_k, and no b component precisely when x_j=x_k. Thus preserving
coordinate equalities can only remove reader support.

### A grid triangle preserves every required equality

There are four nonconstant equality partitions of three positions. They are
001,010,011,012. A noncollinear triangle has nonconstant x and y. If each has
exactly two values, their repeated pairs must differ, or two points coincide.
There are six such ordered partition pairs. If one coordinate has three
values there are another six pairs, and if both do there is one. This gives
thirteen possible equality-pattern pairs. Extra inequalities or collinearity
of chosen numerical representatives are irrelevant to the classification.

For each pattern there is a noncollinear triangle P'_i=(x'_i,y'_i) with all
coordinates in {0,-1}, such that every old coordinate equality still holds.
Here is a construction, without a finite-search premise. If x has a repeated
pair, send its two values to 0,-1 and give the two positions in that pair
different y' values. Any y equality is with the third position, so set that
position's y' accordingly. If x has three values but y has a repeated pair,
exchange x and y in this construction. If both have three values, take any
three distinct corners. Each resulting triangle has determinant +1 or -1
after adjoining its last coordinate one.

The numerical values of old x_i,y_i impose no fixed endpoints. The construction
preserves equalities and may merge distinct values. Consequently every zero
component of an old reader remains zero in the new integral reader.

### Reassign the seed at each port

Let Q' have rows (x'_i,y'_i,1). It is unimodular over the integers. Define a
NEW binary vector z' as follows, using zeros in the ORIGINAL coefficient field.

At a port p in supp(a), if any old q_i(p)=0, set z'(p)=-x'_i. This does not
depend on which zero is selected. Two such zeros imply x_i=x_j, hence x'_i=x'_j.
If there is no old zero, choose z'(p)=0. At a port in supp(b), use the same
rule with y. Outside both supports, choose z'(p)=0.

Set q'_i=z'+x'_i a+y'_i b as integer vectors. Every old query zero is still
zero. Outside supp(a) union supp(b), all new query entries vanish. Inside an
indicator support, the chosen seed enforces exactly the old zero constraints,
and merging coordinate values can add zeros. Thus, for each term,

    supp(q'_i) subset supp(q_i),    supp(u'_i) subset supp(u_i),

where u'_i uses the first two rows of the INTEGER inverse of Q'. These support
comparisons relate integer nonzero entries to original F nonzero entries.
Cofactors and preserved equalities prove the reader inclusion even in small
characteristic. The new queries need not remain independent as actual port
vectors. Formal invertibility of Q' still gives the exact INTEGER identity

    aa^T + bb^T = sum_i u'_i (q'_i)^T.

Every new rectangular binary tariff is therefore at most its original tariff.
The integral floor below completes the proof. This argument also covers the
case in which all three old readers touch both halves; no separate rank or
binary-seed argument is necessary.

## Integral expanded-identity floor

This is the retained argument of Philippe Van Velzen and PR3345/PR3398,
recalled to make the dependency explicit. Expand each scalar port to its two
plane coordinates. Replace scalar entry K_pq by that entry times the 2-by-2
pairing block of p's and q's complete planes. For the literal K this is I_224.
A diagonal block is I2. Any other nonzero entry connects different planes in
one orthonormal group, and therefore has zero pairing block.

An integral decomposition of K reduces modulo two. Each expanded term factors
through the binary Gram matrix of its source and actual reader closures, so
its rank is at most C. Binary rank subadditivity gives total charge at least
224. To apply this to the new integral pair identity, add back every unchanged
literal indicator term. Their charges total 224-m_A-m_B. Thus the new pair
costs at least m_A+m_B, and so does its support-dominating original pair.

## Scope and evidence

The theorem covers any coefficient field, arbitrary seed values and arbitrary
seed support, for exactly three independent queries and the stated literal
two-indicator target. Universal coverage comes from the proof above. The code
checks all thirteen equality patterns, exact rational operators and small
finite-field instances. These checks do not constitute a formal proof kernel
or independent human acceptance.

Dependent query lists, four or more queries, multiple independent external
directions, a changed fitting matrix, different reader semantics and shared
native operations remain open. Source acquisition, arbitrary coefficient
execution, private-state restoration, frames, hosting/storage, stock, precision,
all-size compilation, both supplier admissions and the outer multiplication
transfer are not proved. The selected frontier is unchanged.
