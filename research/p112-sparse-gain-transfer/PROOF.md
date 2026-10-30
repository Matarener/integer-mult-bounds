# Universal two-port transfer for strict fitting masks

This is the uniform-side companion theorem. The
[mixed-orientation theorem](MIXED-ORIENTATION.md) allows the sparse side to vary
term by term; this note retains the explicit sparse-side support equality and
its separate derivation. It was derived and separately audited in this investigation. The transferred fit may change permitted
free entries; it need not preserve the original endpoint matrix. See
[INDEPENDENT-PROOF.md](INDEPENDENT-PROOF.md) for a separate derivation.
The exact scripts check literal premises and controls, not a proof-assistant
formalization of the quantified graph argument.

The endpoint-preserving theorems are separate companions:
[COMMON-RECOVERY.md](COMMON-RECOVERY.md) and
[SCALAR-DEMAND-AND-BRIDGE.md](SCALAR-DEMAND-AND-BRIDGE.md).

## General strict-mask theorem

Fix any square fitting mask over scalar ports. Every diagonal entry is prescribed 1, certain off-diagonal entries are prescribed 0, and all remaining off-diagonal entries are free. Let M=Q R be any rational fitting matrix satisfying that mask. Suppose every column of Q has at most two nonzero entries. Then over a characteristic-two extension field there is another fitting matrix M'=Q'R' satisfying the same strict mask, with

    support(Q') = support(Q),
    support(R') contained entrywise in support(R).

No rank restriction, query independence, disjoint-target decomposition, common-reader-support assumption or symmetry of M is required. Zero query columns can be retained as zero. By transposition, when every reader row has at most two nonzero entries, the analogous transfer preserves reader supports and only shrinks query supports.

## Proof

Normalize nonzero two-coordinate query columns into gain links e_u-g_e e_v, g_e nonzero rational, and one-coordinate columns into unit halfedges. Absorb the normalization in the corresponding reader rows; support is unchanged.

For each actual reader column p, choose a column basis inside its active query set and express the old output M[:,p] in that basis. Delete zero coefficients. The selected query set is independent. Each connected component of its gain graph is an ungrounded tree, a tree with one unit column, or an unbalanced unicyclic component. The latter two types are full-row-rank. Since M[p,p]=1, one selected component contains p. Discard every other component; this does not affect the pth diagonal and merely sets some previously permitted off-diagonal entries to zero.

Choose one global new query matrix over F2(t_e), with an independent nonzero formal gain t_e for every link and unit columns unchanged. Every possible simple cycle is unbalanced, because its holonomy is a nonconstant Laurent monomial in distinct edge variables. All selected cyclic and grounded components therefore stay full-row-rank.

If the selected p-component is cyclic or grounded, recover the singleton output e_p within that component. If it is an ungrounded tree, its old output cannot have support {p}: the old tree's switching annihilator is nonzero at every vertex and would rule out that output. Hence there is a vertex b!=p in the same component with old M[b,p]!=0. The fitting mask consequently declares (b,p) free.

Let z be the new tree's switching annihilator; all z_v are nonzero. The new output

    e_p - (z_p/z_b) e_b

belongs to its column span. It has diagonal entry1 and its only nonzero off-diagonal entry is at the allowed free position (b,p). Recover this output using only the selected p-component. Place the recovery coefficients in reader column p and set all other query incidences there to zero.

Doing this for every p uses one global Q', preserves every required diagonal and forbidden zero, and only deletes actual reader incidences. The resulting M' may have different permitted free entries and different matrix rank. This proves the theorem. If the original common diagonal is any c!=0, first divide the fitting matrix by c by scaling the readers; the support and tariff are unchanged.

The formal field can, if desired, be specialized to some sufficiently large
finite characteristic-two extension. Only finitely many rational functions
and required nonzero query entries/minors occur. The product of their
nonzero denominators and required nonzero numerators is a nonzero polynomial,
so it has a nonvanishing tuple over the infinite algebraic closure of F2;
that finite tuple lies in a finite extension. No efficient field-size bound
or native implementation follows from this existence statement.

All graph-rank facts above have elementary proofs: an independent connected link graph has at most n columns and at least n-1 links, so it is a tree or one-cycle graph, with at most one unit column in the tree case. A gain tree has a one-dimensional left kernel whose entries are all nonzero; a grounded tree is nonsingular; a gain cycle is nonsingular exactly when its holonomy is not 1.

## The universal I334 implication for P112

For the fixed 37-triad/one-line P112 full-group mask, every free off-diagonal scalar position joins physical group spaces E_g,E_h whose COMPLETE binary pairing block is zero. Diagonal scalar positions are prescribed 1, and their physical self-pairings are I3 orI1. Therefore expanding ANY characteristic-two strict fit by those complete physical pairing blocks gives I334, regardless of its free coefficients or fitting rank.

More explicitly, index the expanded rows by (p,a), where a ranges over the
ordered physical group G(p), and similarly index columns by (r,b). Define

    L(M)[(p,a),(r,b)] = M[p,r] * (q_a dot q_b),

where the dot product is binary and its result is embedded in the extension
field. There are 334 expanded coordinates. For p=r, orthonormality of G(p)
and diagonal coefficient1 give the appropriate identity block. For p!=r,
either the scalar entry is prescribed 0, or it is free and its entire binary
pairing block is zero. Thus every formal free coefficient disappears.
The replays check all 111,556 expanded coefficient positions, all 28 free
physical group pairs and all 420 free scalar positions, independently of the
canonical fitting matrix or its rank.

For one factor term q r^T, the corresponding expanded matrix is a row/column-scaled copy of the binary pairing rectangle on its complete source and reader group closures, with repeated physical labels allowed. Its rank over any characteristic-two extension is at most the binary whole-group tariff. Rank subadditivity implies

    sum_term tariff >= rank(I334) = 334.

Apply this to M'=Q'R'. Query closures are unchanged, reader closures shrink, and binary pairing ranks do not change under field extension. Thus the ORIGINAL rational decoder also has invoice at least 334.

The same conclusion holds if all reader rows are literal at-most-two-port vectors, by transposing the fitting mask and the factorization. The physical strict mask and pairing tariff are symmetric here.

## Canonical completion and the sparse-splitting budget

The canonical invoice is 3 H3+53 H6+H7=334. For literal sparse completion,
the residual three-copy query is split into its ordinary pair and residual
unit, with the same full three-copy reader. The exact physical charges are
6+1=7, as both replays verify. The other canonical queries are already at
most two-port. This refines the canonical endpoint into a two-port-query
factorization at the same invoice334; no new supplier is implied.

A replacement of three ordinary paired canonical targets can be completed
in this way at cost 316 outside the changed terms. If every replacement
query is at most two-port and its endpoint is exact, the strict-fit theorem
therefore gives local invoice at least 18. The seven-query bridge in the
companion note meets these premises for every exact reader matrix. The
coefficient-space companion also proves its floor by coalescing equal
reader rows, while preserving the local endpoint.

There is a necessary budget test for a dense-query candidate. Partition each
query support into disjoint chunks of size at most two, and retain that
query's reader on every chunk. The endpoint is unchanged. Write

    delta_t = sum_chunks rho(source_chunk, reader_t)
              - rho(original_source_t, reader_t).

Here rho is the binary rank of the complete physical-group pairing
rectangle. Row-rank subadditivity makes every delta_t nonnegative, even
when different chunks meet the same physical group. The refined query
family is uniformly two-port, so if the original invoice is C,

    C + sum_t delta_t >= 334.

Consequently an invoice at most 296 requires sum_t delta_t >=38 for every
such sparse partition. The reader-side transpose gives the same necessary
test. This is a certificate requirement, not a claim that partitions have
been optimized or that dense vectors with this overhead produce a saving. The
[mixed theorem](MIXED-ORIENTATION.md#5-the-stronger-splitting-budget) permits the
cheaper source/reader partition to be chosen independently for every term.

## Exact consequence and limits

No rational decoder on this fixed full-group mask can save if every query touches at most two literal scalar ports. The same holds if every reader touches at most two literal scalar ports. A successful decoder must have at least one genuinely three-or-more-port query AND at least one genuinely three-or-more-port reader. These uniform-side conditions are necessary, not sufficient. The
[mixed theorem](MIXED-ORIENTATION.md) strengthens them: the at-least-three-port
query and reader must occur in the same term.

This theorem covers higher-rank fitting matrices and arbitrary rational term counts. It does not cover changed physical masks or tariffs. It concerns literal scalar-port sparsity; arbitrary dense groupwise coordinate changes can alter that sparsity. It does not preserve a chosen fixed fitting endpoint. The earlier fixed-endpoint support-intersection theorem and scalar-demand coalescence lemma remain stronger in their own endpoint-preserving conclusions and have useful wider support-coordinate interpretations.

## Common within-group gauge corollary

Let S be any single invertible rational block-diagonal matrix respecting the 37 physical triads and residual line. If every column of S Q has at most two nonzero scalar coordinates, the same invoice floor 334 holds for the original factorization.

Indeed, conjugate the fit and factors:

    M_g = S M S^{-1} = (S Q)(R S^{-1}).

Each prescribed diagonal physical block is I, hence remains I. Every forbidden whole off-diagonal block remains zero, while every allowed block is entirely free and may change. Thus M_g satisfies the identical strict group mask. An invertible within-group map preserves whether each query or reader restriction to that physical group is zero. The complete group supports and every term's binary physical tariff therefore remain exactly unchanged. Apply the literal two-port theorem to S Q. No reduction of S modulo2 and no inverse conjugation of the transferred field representation are required.

Likewise the floor holds if a common within-group gauge makes every reader row of R S^{-1} at most two-sparse. Different gauges may establish the query-side or reader-side obstruction; one successful gauge on either side is enough. A separate coordinate change chosen independently for each term is not allowed. This corollary is an invoice result, not a support-preserving fixed-endpoint transfer back to the original literal rational coordinates.

## Attribution

Signed-incidence rank, switching and circuit descriptions are standard; see Thomas Zaslavsky, [Signed Graphs and Geometry](https://people.math.binghamton.edu/zaslav/Tpapers/sggm.pdf), Theorems3.1 and3.5-3.6. The package proves the gain-incidence facts needed here directly, and does not attribute the arbitrary-gain strict-mask transfer theorem to that signed-only survey. The universal strict-mask transfer and its P112 invoice application are local deductions in this investigation. The signed-only Bolker-Zaslavsky coefficient alphabet is not used here. This is a structural obstruction, not a new upper bound, a claimed global optimum for arbitrary decoders, or a claim of worldwide novelty.
