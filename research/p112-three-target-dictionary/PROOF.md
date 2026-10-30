# Seven subset-sum directions cannot improve any literal target triple

## Statement

Use Tekalign's PR3370 sixteen-group partition of the 112 pinned P112 labels.
Pair consecutive ports in each group into Gram-I2 planes. Each group's two
alternating halves give disjoint scalar indicators, making 32 indicators in
all. Fix three distinct indicators a_0,a_1,a_2 and their complete-group sizes
m_0,m_1,m_2. Two indicators may belong to the same group.

Over an arbitrary coefficient field F, consider any finite exact factorization

    sum_(j=0)^2 a_j a_j^T = sum_i u_i q_i^T.

Every q_i is zero or proportional to a nonempty subset sum of the three a_j.
Every u_i lies in their span. Thus both factors are constant on each selected
indicator's scalar support and zero elsewhere. Reader coefficients may have
any signs or denominators. Query repetitions and term count are unrestricted.

For a vector v, cl(v) includes both ports of every matched plane touched by its
nonzero entries. Charge each term its actual-reader tariff

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

The exact minimum total tariff is m_0+m_1+m_2 for every one of the 4,960
indicator triples. The original three terms attain it. Consequently disjoint
triple replacements of this kind cannot lower the original whole-K tariff 224.
This is a finite, source-specific bound. It is not a general theorem for other
geometries, arbitrary query directions or nonconstant readers.

## Reduction from arbitrary finite lists outside characteristic two

Number the seven subset sums by their nonzero binary masks s=1,...,7, with
q_s=sum_j bit_j(s) a_j. Absorb any nonzero proportionality constant into u_i;
discard zero queries. Merge all terms on the same ray into u_s q_s^T. This
cannot increase cost. The merged reader support lies inside the union of the
old supports, and binary rectangular rank is subadditive under column union:

    rank Gram(S,union_i T_i) <= sum_i rank Gram(S,T_i).

Complete-plane closure respects unions and inclusion. Cancellation within a
merged reader can only delete support. There are now at most seven terms.

Write u_s=sum_j b_(j,s) a_j. Disjoint indicator supports make the operator
identity equivalent to the three vector equations

    e_j = sum_s b_(j,s) bitvector(s), j=0,1,2.

For each j, choose an inclusion-minimal subset of its nonzero-coefficient
support whose dictionary vectors span e_j. Such a subset is linearly
independent: a dependent vector could be removed without changing its span.
It therefore has at most three elements. The unique expression of e_j in
this subset has no zero coefficient, since otherwise a smaller subset works.
Replacing each coefficient row separately by this expression only deletes
reader support in each q_s term. It cannot increase any tariff.

This reduction also covers redundant lists with arbitrarily many original
terms. It is not an a priori bound on the original term count.

## Complete finite enumeration

The primary verifier enumerates all subsets of sizes 1,2,3 of seven directions,
solves each over exact rational numbers, and keeps independent supports with
all expression coefficients nonzero. There are nine for each axis. For e_0,
the direction-mask supports and corresponding coefficients are:

| Masks | Coefficients |
| --- | --- |
| 1 | 1 |
| 2,3 | -1,1 |
| 4,5 | -1,1 |
| 6,7 | -1,1 |
| 2,4,7 | -1,-1,1 |
| 2,5,6 | 1,1,-1 |
| 3,4,6 | 1,1,-1 |
| 3,5,6 | 1/2,1/2,-1/2 |
| 3,5,7 | 1,1,-1 |

Permuting coordinates gives the other two lists. The sole half-integral
branch in this table must not be rejected by reducing the scalar solve modulo
two. The independent replay tests rational span by integer cross products and
3-by-3 determinants, over every one of the 127 nonempty dictionary subsets,
then retains inclusion-minimal spanning subsets. It obtains the same nine.

The Cartesian product gives 9^3=729 distinct reader-support patterns. For
pattern r, bit j of r_s says that u_s has a nonzero a_j coefficient. The query
closure for s and the reader closure for r_s are unions of the corresponding
complete groups. Thus the exact bill depends only on the three group IDs,
not on which alternating half was selected. This remains true when two IDs
coincide. No replacement of actual readers by query self-cost is made.

Enumerating the original 32 choose 3 indicator triples gives 800 group types:
560 distinct-group triples with multiplicity eight, and 240 repeated-group
types with multiplicity two. No group contains three distinct indicators.
The primary verifier evaluates all 800 times 729 = 583,200 bills using packed
binary Gaussian elimination. The independent replay recomputes all of them
using explicit coordinate Gram matrices and a separate row elimination.
Every minimum equals m_0+m_1+m_2. Both implementations reproduce every row
of RESULT.json and the same digest of the complete ordered bill stream.

Each receipt row is `[g0,g1,g2,multiplicity,minimum,number_of_minimizers,digest]`.
The digest hashes the 729 integer bills in lexicographic reader-pattern order,
one byte per bill. Rows use lexicographic group-ID order. The aggregate digest
hashes those bill streams in that order. This specifies all search coverage;
the digest authenticates agreement, while the recomputation checks the claim.

## All coefficient fields

For the seven binary 3-vectors, the 35 three-column determinants have absolute
values 0 six times, 1 twenty-eight times and 2 once. The independent replay
checks this exact inventory. Every two-by-two minor is 0,1 or -1, and every
one-by-one minor is 0 or 1. Thus the rank of every dictionary subset is the
same over the rationals and over any odd-characteristic field. Appending a
target axis only repeats a dictionary vector, so the same statement decides
all target-axis span requests. The nine minimal supports and their nonzero
coefficients therefore persist over every odd-characteristic field, including
its extensions. The same finite tariff computation proves the stated bound.
Characteristic-zero fields contain the rationals, so their ranks and the
nonzero rational coefficients are unchanged as well.
Actual F3 and F5 controls separately check all 381 subset/axis span requests.
No homomorphism into characteristic two is assumed.

In characteristic two, apply the retained expanded-identity argument directly.
Expand scalar port p to its two plane coordinates. A term u q^T expands to
blocks u(p)q(r) times the binary Gram block of the planes at p,r. Selecting,
repeating and scaling reader rows and query columns factors this expanded
term through Gram(cl(u),cl(q)). Its F-rank is at most the binary tariff,
since extending the prime field F2 to F preserves a binary matrix's rank.
Append all untouched literal indicator terms to the triple factorization.
Their expansion, together with the three-target sum, is I224, as checked
entry by entry. The untouched tariff is 224-m_0-m_1-m_2. Rank subadditivity
therefore gives the desired lower bound in characteristic two. This branch
does not use the half-integral scalar expressions.

The original three indicator terms attain equality over every field. The
statement consequently covers all coefficient fields, with no finite-field
size restriction. Characteristic other than two uses the finite dictionary census;
characteristic two uses the expanded-identity rank argument.

## Scope and decision

PR3463 proves a different result for arbitrary finite pair-span lists and
arbitrary readers, for any even orthonormal partition. Its extension-field
transfer does not prove this triple statement. PR3383's spanning-query theorem
bounds query self-cost, which is a different quantity. PR3398/3414 allow an
external query dimension while replacing only two target indicators; that is
also different from the present three-target identity wholly inside its span.

This result closes the elementary seven-ray triple dictionary on the literal
fixture. Pause this dictionary as a cost-improvement mechanism. Another round
needs a changed direction or reader contract, plus an explicit lower-cost
factorization before native construction. It supplies no source acquisition,
coefficient execution, frame, dirty restoration, hosting, precision, complete
supplier, outer transfer, new kappa or selected-frontier claim. Independent
human and formal proof-kernel review are unclaimed.
