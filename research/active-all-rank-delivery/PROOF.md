# Complete immutable-channel exclusion

## Source contract

Use the exact source and normalized restored-Y quotient from PR5808. Its target space U is the eight-dimensional image of R^T. The source has RR^T=56I. Each paid channel keeps one frame f and one scalar payload row b in the original eight modes. Its chronological scatter gives a vector v in the exact response space S_f. Thus the required correction has the form

    M = sum_j v_j b_j^T,       im(M)=U,       rank(M)=8.

Gathering, storage, arbitrary rational scatter and helper restoration are granted. Joint output noise can cancel between channels. Initial ground-Y preconditioning has zero response in this quotient. The source native common-fixed-vector specialization is a retained premise, not a new all-address theorem.

Discard any channel whose chosen response vector is zero. Each discarded positive-rank channel costs at least H1. In the cases below, n counts the remaining channels. If the original completion had more than eight channels but at most eight remain, the rank-eight target forces exactly eight to remain, and the discarded charge gives a gap of at least H1. Thus it is enough to analyze nonzero responses.

The unchanged PR5808 census visits every change of an impulse response or its frame. It records all 22,585 events and verifies the complete initial restored-Y invariant. The new checker authenticates that implementation and its archive before use. This proof does not claim an independent implementation of that census.

## Exact cut certificate without rank eight

Temporarily exclude rank-eight channels and assume at least nine channels. Allowed nonzero responses have ranks 1 through 7 or 9. No upper bound on any channel count is used.

For a quotient by any subspace W, put d=dim((U+W)/W). Each channel whose response space lies in W disappears. Every remaining channel contributes matrix rank at most one. Therefore

    sum_(f with S_f not contained in W) n_f >= d.

Twenty-two certificate rows take W to be a span of actual response spaces. Their ranks and active frames are recomputed with exact rational elimination.

Forty-eight further rows restrict the output to eight listed coordinates. On each such coordinate set, the restriction of R^T has rank eight. The checker proves this twice: sparse rational rank and an independent integer determinant. A response space vanishes on this restriction exactly when its support misses the coordinate set. The same rank inequality therefore has right side eight. These are full target-rank cuts, not mere coordinate coverage constraints.

The final row is sum n_f >= 9. Give these 71 inequalities their positive rational weights in CERTIFICATE.json. For every allowed frame f, the total weight of active rows is at most its paid rank r_f. The checker verifies every capacity exactly. The weighted right side is

    L = 1441100759/20000000 > 72.

It follows that sum r_f n_f >= L. The ranks and counts are integers, so the rank mass is at least 73. The certificate does not use optimizer status, floating-point ranks, upper count bounds or an unproved integrality assertion.

## Rank-nine replacement

The census contains one rank-nine frame, f=1, whose response space is all of Q^112. The checker verifies all 112 unit vectors in that space. Thus every actual rank-eight response vector v can also be produced in the granted model by a rank-nine channel with the same payload b. The new scatter can use a different chronology, but it stays in that one chart. The matrix contribution v b^T is identical.

Suppose a completion has n>=9 channels and k rank-eight channels. Replace those k channels as above. The number of channels stays n and the rank mass increases by exactly k. The new completion has no rank-eight channel, so its rank mass is at least 73. Consequently the original rank mass is at least 73-k.

If k>=8, those eight channels alone cost at least 8H8. As n>=9, there is at least one additional positive charge H1. If k<=7, the original rank mass is at least 66. A weaker mass-65 consequence will suffice for a uniform strict gap below.

## All concave powers

Let n>=9, let all channel ranks be integers from 1 through 9, and suppose their total rank is at least 65. For 0<q<=1, the sum of r^q is at least

    7*9^q + 2.

To prove this, first take n<=65 and reduce ranks, if needed, to total 65 without reducing any positive rank below one. This can only reduce the price. Sort the ranks in decreasing order. The vector

    (9,9,9,9,9,9,9,1,1,0,...,0)

majorizes every such rank vector. Its first k entries have sum at least min(9k,65-(n-k)), the maximum possible first-k sum for n positive ranks. Concavity of x^q proves the claim. If n>65, the price is at least n>65, while the displayed lower bound is at most 65.

We now prove, for every q>0,

    7*9^q + 2 - 8*8^q > 1/5.

The integer inequality 9^18>8^19 gives 9^q>8^(19q/18). Put y=8^(q/18). It is enough to bound

    p(y)=7y^19-8y^18+2.

For y>=0, its derivative is y^17(133y-144). Its global minimum is at y=144/133, and equals

    2-(8/19)*(144/133)^18 > 1/5.

The final inequality is checked as an exact rational comparison. No logarithm, root or power approximation is used. Thus every completion with n>=9 and k<=7 has price greater than 8H8+H1/5. The k>=8 case has an even larger stated gap.

## At most eight channels and attainment

Fewer than eight rank-one matrix contributions cannot have target rank eight. With exactly eight, the response vectors v_j are independent and span U. Hence each v_j belongs to U. The exact census shows S_f intersect U is zero whenever r_f<8. All eight channels therefore have rank at least eight, and their price is at least 8H8.

The checker gives eight explicit rank-eight response combinations, one for each original mode direction. They lie in frames 254,274,279,280,281,619,621,624. Their mode coefficient rows are a permutation of the eight unit vectors. They therefore construct the complete target in the granted quotient using eight rank-eight channels. This proves that the quotient floor is sharp. PR5745 supplies the retained separate physical construction; its extra scalar, owned and route costs are not removed here.

## Conclusion and scope

Every mixture of every available positive rank, with any finite number of immutable channels and arbitrary joint noise cancellation, costs at least 8H8 for every 0<q<=1. More than eight channels cost strictly more than 8H8+H1/5. Ground responses are zero and cannot improve the target.

This resolves the fixed contract, not a universal multiplication bound. A changed word, a moving chart, a recomputed payload or feedback can leave the proof's hypotheses. All inherited native, owned-erasure, compiler, precision/tape and analytic assumptions retain their status. The selected frontier is unchanged.
