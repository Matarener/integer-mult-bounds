# Axial normal form and the next structural test

21 October2026. Local deduction checked by a separate AI agent; no cheaper decoder or multiplication-bound claim. This extends the source-density floor in PROOF.md. No independent human or proof-kernel review is claimed.

## Scope and support-monotone normalization

Use exactly three ordinary two-copy canonical P112 marks in three distinct paired roles, with indicator matrix C. Let Q=C A and Q R=C C^T over Q, with arbitrary actual readers. Restrict reader columns to the six marked physical ports; every removed endpoint column was zero. This preserves the endpoint and cannot increase a full-group tariff.

A query is axial when its coefficient column is a nonzero multiple of one marked unit vector. Absorb that scalar into its reader. All axial terms for the same mark can be replaced by their single sum c_i (sum r_t)^T. The new reader support lies in the union of old reader supports. With a fixed source closure S, binary rank satisfies rho(S,union T_t)<=sum rho(S,T_t), because the union matrix is assembled from the old column blocks. Thus this merge cannot increase the invoice. Remove zero terms after merging. Let n be the remaining term count and a the number of axial terms. Then a<=3, at most one for each marked axis. These are normalized counts, not the original number of terms before restriction/merging.

## A finite term-count bound even with axial queries

The existing geometric premises give dim(V)>=k+2 for the span V of any k selected reader triads. A non-axial query uses at least two marked coordinates, so its physical source span U has dimension at least8 in the nondegenerate9-dimensional binary ambient space. Its term tariff is at least k+1.

For an axial term let k be the number of selected reader triads and h the number of its own two marked physical ports carrying a nonzero reader coefficient (h=0,1,2). Its source role spans a6-dimensional space, so its tariff is at least dim(V)-3>=k-1. Its own two physical triads are orthonormal and mutually orthogonal (the canonical expanded endpoint is I334); the h own reader triads therefore supply an I_(3h) submatrix, so the tariff is also at least3h. Since k<=6,

    tariff >= max(k-1,3h) >= k+h-2.

For h=0 or1 the second inequality follows from k-1; for h=2 it follows from6>=k. This uses only the already authenticated canonical geometry.

Let I be the sum of all reader-triad incidences after normalization, and H the sum of h over axial terms. Every marked port needs at least one reader entry. If it has only one, that query must be proportional to its own marked unit vector, hence it is counted in H. Every other port needs at least two. Therefore I>=12-H, even when some own axial readers coexist with additional terms.

Summing dense and axial term bounds gives

    cost >= I+(n-a)+H-2a >= 12+n-3a.

Consequently any local cost at most17 has n<=5+3a. Combined with the previously established no-saving result for n<=5, the only remaining normalized counts are:

- a=1: 6<=n<=8;
- a=2: 6<=n<=11;
- a=3: 6<=n<=14.

This does not prove those remaining classes save or are representable. The counts do not apply to exterior queries, repeated paired roles, singleton/residual marks or changed endpoints. The cost of the original factorization is at least the normalized cost, so an original cheap candidate would yield a cheap normalized one within these bounds.

The independently checked stronger fact dim(V)>=6 for three distinct reader triads can improve individual k=3 tariffs by one. It is not needed for this term-count bound.

## A decisive next test

For one declared physical placement, a source/reader support type has one of
7 nonempty marked-source subsets and63 nonempty actual-reader subsets, at
most441 types. Charge its exact full-group tariff. A proposed invoice<=17 must
respect the axial uniqueness and term-count limits above. Every desired entry
of A R=C^T must be covered, and a zero entry cannot be covered by exactly one
nonzero product. These are necessary constraints, not sufficient rational
realizability. An infeasibility certificate would close every coefficient
choice at that placement. A feasible support requires an exact bilinear
endpoint solution with nonzero coefficients and a fresh full invoice before
it can be called a decoder. No support-feasibility census is claimed here.

The same written proof audit checked the merge, the identity3h submatrix and
the incidence correction. Both registered geometry replays establish all
finite premises; no new computational input is required. The n>=6 part of the
remaining ranges invokes the precisely cited earlier five-term theorem, while
the upper bounds n<=5+3a follow from this proof alone. Apache-2.0.
