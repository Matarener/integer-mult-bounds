# Scalar-demand gain transfer and the complete bridge-reader family

These are separate deductions, audited in
[INDEPENDENT-PROOF.md](INDEPENDENT-PROOF.md) and
[INDEPENDENT-MIXED-PROOF.md](INDEPENDENT-MIXED-PROOF.md). They use the
gain-incidence rank arguments in [PROOF.md](PROOF.md) and
[MIXED-ORIENTATION.md](MIXED-ORIENTATION.md),
but require no common reader support and no row gauge: their demands are
singleton coordinates in the canonical target basis. The executable checks
the exact bridge kernel, particular endpoint, and coefficient identities
that describe every reader matrix. The universal transfer and tariff
conclusions remain written proofs, not a finite enumeration of readers.

## Scalar-demand transfer lemma

Let C have nonempty, pairwise disjoint indicator columns c_j, let M=C C^T, and suppose M=(C A) R over Q. Assume every column of A has at most two nonzero entries. A may be dependent; actual reader columns may differ arbitrarily.

For any actual reader column at a port of c_j, injectivity of C gives A r=e_j. Select an independent query basis inside that reader's active coefficient-column set, solve for e_j and delete zero coefficients. Its active gain graph has only one nonempty component, containing j: another active component would yield a nontrivial zero combination of independent columns. That component cannot be an ungrounded tree, whose nonzero switching annihilator forbids a singleton demand. It is therefore an unbalanced unicyclic component or a tree with a unit column.

Give every coefficient-space two-port query its own independent formal gain over F2(t_e), and retain unit columns. Every possible simple cycle has nontrivial holonomy, so each selected support remains full-row-rank. Thus every actual singleton demand is recoverable within its old support, independently for every actual reader column. This yields A'R'=C^T over the characteristic-two field, and hence (C A')R'=C C^T. Disjoint columns of C ensure that support(C A')=support(C A): changing a nonzero coefficient cannot cancel across different canonical columns. Reader supports shrink. Full physical-group tariffs therefore do not grow, and the retained I334 expansion gives the canonical invoice floor.

The conclusion permits arbitrary query dependence and arbitrary copy-asymmetric readers, but requires each query to be a combination of at most two complete canonical columns. It is different from requiring at most two literal scalar ports. It does not cover arbitrary queries in the canonical span.

## Mixed coefficient-query and actual-reader transfer

Let C again have nonempty disjoint indicator columns and let

    (C A) R = C C^T

be a rational exact-endpoint factorization. Suppose that for every term t,
either its coefficient column A[:,t] has at most two nonzero **mark entries**,
or its actual reader row R[t,:] has at most two nonzero **scalar ports**.
The choice may vary by term. Then there is a characteristic-two factorization
`(C A')R'=C C^T` with both A' and R' supported entrywise inside A and R.
Disjoint marks imply that the physical query supports in C A' also shrink.
Thus the exact canonical endpoint is preserved without increasing any
monotone complete-group tariff.

Injectivity of C gives the rectangular coefficient equation A R=C^T.
Orient each term according to its sparse side, freeze that side, and vectorize
the complete equation as in [the mixed strict-fit proof](MIXED-ORIENTATION.md).
The coefficient rows are now positions (mark j, actual port p). Its active
columns are gain links or units, with one shared gain per frozen factor.
Choose an old independent column basis. The repeated-gain argument transfers
its grounded and unbalanced cyclic components, and preserves its tree ranks.

The required output C^T is zero except for a prescribed one at each marked
position. A selected tree cannot contain exactly one prescribed position:
its old output would be a singleton, contradicted by its switching
annihilator. A tree with two or more prescribed positions can recover
nonzero values at all of them and zero elsewhere, using the same
characteristic-two weighted-sum construction. A component with no prescribed
position receives zero; a full-rank component recovers its prescribed ones.
This produces A'R0 with the exact zero pattern of C^T and nonzero values at
its prescribed positions, using only old active factor entries.

Every actual output column of C^T has at most one prescribed nonzero entry,
because the marks are disjoint. Scale each marked output column of R0 by
the inverse of that entry. These independent column scalings do not conflict,
preserve all factor supports, and restore A'R'=C^T exactly. Columns outside
all marks have zero target and need no normalization. Multiplication by C
then gives the asserted exact physical endpoint. Disjointness also proves
physical support containment: at a port in mark j the query value is exactly
the jth coefficient, so no cross-mark cancellation is being assumed.

For C equal to the pinned full P112 canonical target matrix, its
characteristic-two expansion is I334. Therefore this mixed coefficient/actual
reader class has invoice at least 334. A cheaper exact decoder whose queries
all lie in this canonical span must have a term combining at least three
canonical marks and using at least three actual reader ports in that same
term. This statement requires the canonical-span hypothesis and the exact
canonical endpoint; it is not a theorem about arbitrary exterior queries or
arbitrary changed strict fits.

A replacement of three ordinary paired targets within their canonical span
can be completed by the unchanged canonical terms at cost 316. Those extra
queries are coefficient singletons, including the three-copy residual mark,
so this mixed coefficient theorem gives the local floor 18 without any
common-reader premise. The literal sparse completion in PROOF.md uses the
separate, also valid residual 6+1 refinement.

The F4 tree control in `mixed_controls.py` also normalizes reader columns
rather than source rows, checking the endpoint-preserving normalization used
here. The quantified transfer remains the written argument above and its
separate independent audit; no new physical input is introduced.

## Exact application to the seven-query bridge family

Let c0=e0+e3, c1=e1+e4, c2=e2+e5. The six triangle queries are

    q0=e0+e1, q1=e1+e2, q2=e2+e0,
    q3=e3+e4, q4=e4+e5, q5=e5+e3,

and q6=c0. The first six columns form an invertible Q6. Write

    D = Q6^{-1} [c0 c1 c2]
      = (1/2) [[1,1,-1],[-1,1,1],[1,-1,1],
                [1,1,-1],[-1,1,1],[1,-1,1]].

One reader solution is R0=[D C^T; 0]. The one-dimensional query kernel is spanned by

    k=(-1/2,1/2,-1/2,-1/2,1/2,-1/2,1)^T.

Consequently every exact reader matrix is R=R0+k z^T for arbitrary rational z on the actual reader ports (including extra zero-target columns if desired). Both R0 and k have identical entries on corresponding rows e and e+3, for e=0,1,2. Thus those reader rows are identical for every z.

Coalesce each equal-reader pair of terms into one term. Its query becomes

    q0+q3=c0+c1,
    q1+q4=c1+c2,
    q2+q5=c2+c0,

and the bridge remains c0. The endpoint is unchanged. Each coalesced source support is a union of the old source supports, with the same reader; binary pairing rank subadditivity proves its tariff is at most the sum of the two old tariffs. This comparison remains true when distinct scalar vertices occupy the same physical triad.

All four remaining queries mix at most two complete canonical target columns, so the scalar-demand transfer lemma applies regardless of z and regardless of copy-asymmetric readers. The coalesced invoice is at least the canonical local invoice18. Therefore the original seven-query family has invoice at least 18 for every rational reader matrix, every literal embedding into three ordinary paired targets, and every number of extra zero-target reader columns. The stated queries have no exterior source vertices; arbitrary query-column rescalings can be absorbed before applying the proof.

This is a whole-family obstruction without a coefficient or geometry grid. It does not assert that invoice18 is attained in the seven-query representation or close different dependent-query architectures. Earlier particular invoices 36 and 39 are not needed by this proof and are not asserted to be optima.

## Relation to the stronger strict-fit result

The bridge's original seven queries already touch at most two literal ports.
The mixed strict-fit theorem therefore gives its local floor 18 directly after
the zero-overhead canonical completion described in PROOF.md, including the
residual pair/unit refinement. The coalescing proof above remains useful as
an endpoint-preserving derivation and an example of coefficient-space sparse
queries whose literal source supports may have four or more ports.
