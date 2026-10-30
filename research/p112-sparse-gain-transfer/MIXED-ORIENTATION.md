# Mixed two-port orientations transfer across every strict fitting mask

## Statement

Let M be any rational square strict fitting matrix: every diagonal entry is
one, a prescribed set of off-diagonal entries is zero, and the remaining
entries are free. Suppose

    M = sum_t q_t r_t^T,

where **each term** satisfies `|support(q_t)| <= 2` **or**
`|support(r_t)| <= 2`. The choice of sparse side may differ between terms.
There is a characteristic-two factorization of another strict fit N with
termwise source and reader supports contained in the original supports.
Free entries and fitting rank may change; the original exact endpoint need
not be preserved. There is no restriction on rank, term count, dependence,
or cancellation of forbidden entries between the two orientations.

For the pinned P112 complete-group mask, every characteristic-two strict fit
expands to I334. Consequently **every factorization satisfying this mixed
condition has full-group invoice at least 334**. Any cheaper rational decoder
must contain at least one term with at least three literal source ports
**and at least three literal reader ports in that same term**.

The separate [uniform-side theorem](PROOF.md) retains its explicit equality
of sparse-side supports when one entire factor family is two-port. The
[common-recovery companion](COMMON-RECOVERY.md) retains its exact-endpoint
conclusion under its additional premise. The
[mixed coefficient/reader companion](SCALAR-DEMAND-AND-BRIDGE.md) preserves
the exact canonical endpoint when every query lies in the canonical span
and each term is sparse on its coefficient-mark side or actual-reader side.

## 1. One linear problem on complete matrix positions

Delete zero terms and orient each remaining term once. Put it in A if its
query is two-port and in B if its reader is two-port; a term qualifying for
both may be assigned arbitrarily. Freeze Q_A and R_B. Only the originally
nonzero entries of R_A and Q_B are allowed to vary. The map

    (X,Y) -> Q_A X + Y R_B

is linear in those allowed variables. Its coefficient matrix L has rows
indexed by complete matrix positions (p,q). A variable X[t,q] contributes
q_t in the positions of matrix column q. A variable Y[p,t] contributes r_t
in the positions of matrix row p. Every column of L therefore has one or two
nonzero entries.

Normalize each frozen two-port factor once as e_u-g_t e_v, with nonzero
rational gain g_t, and each frozen singleton factor as a unit vector.
Absorb the nonzero scalar into that term's unfrozen factor. This preserves
the original matrix and all supports. Repeated columns of L coming from
one frozen factor use the same orientation and gain.

Choose a column basis of the allowed L columns and express vec(M) in it.
Discard columns whose coefficients are zero. The remaining set is
independent and still represents the complete M, including every
cross-orientation cancellation at forbidden positions.

View a two-entry column as a gain link between its two matrix-position
vertices and a unit column as a ground. Every connected component of an
independent set is an ungrounded tree, a grounded tree with exactly one unit,
or an unbalanced unicycle. Indeed, connectivity requires at least v-1 links
on v vertices and independence permits at most v columns. A tree has a
one-dimensional left kernel with every coordinate nonzero; grounding it
removes that kernel. A unicycle is nonsingular precisely when its cycle
gain product is not one. Parallel links and two-edge cycles are included.

## 2. Repeated gains and old unbalanced cycles

Work over F2(u,{x_t}), with one independent nonzero gain indeterminate x_t
per original frozen two-port factor and one spare indeterminate u. Replace
e_u-g_t e_v by e_u-x_t e_v in that factor. Every replicated column of L'
uses the same x_t; copies are not assigned independent gains.

The holonomy of any selected cycle is a Laurent monomial in the x_t. If it
were identically one, every exponent would vanish. Substituting the old
rational gains into that same Laurent word would then give one, contradicting
the cycle's old unbalance. Therefore every old selected unbalanced cycle
remains unbalanced. Repeated-gain cycles that are identically balanced could
not have been present in the original independent basis.

This argument includes the signs: the normalized rational column is
(1,-g_t), so its relation gain is g_t. Reversing an edge replaces the gain by
its reciprocal. An exponent-zero word has no additional odd-cycle sign.
Consequently the selected L' stays independent with the same component
rank pattern. No assertion that every replicated cycle becomes unbalanced
is needed.

## 3. Recover nonzero diagonals and forbidden zeros

For a selected component, let D be its vertices that correspond to diagonal
matrix positions. Every diagonal position lies in one selected component,
because the old represented matrix has diagonal one. Components with D empty
may be assigned output zero.

For a full-row-rank component, recover output one at every vertex of D and
zero everywhere else.

For an ungrounded tree, let z be its switching annihilator, nonzero at every
vertex. Its image consists exactly of vectors w satisfying z dot w=0.

- If D has one vertex d, the old component output cannot have support {d}:
  its old annihilator would contradict the nonzero diagonal. Some other
  vertex b therefore has nonzero old M output. Since the complete M is a
  strict fit, b is a permitted free off-diagonal position. Set w_d=1,
  w_b=-z_d/z_b and all other values zero.
- If D has at least two vertices, choose nonzero weighted contributions
  z_d*w_d summing to zero and set output zero outside D. For an even number
  of vertices, use pairs (1,1). For an odd number at least three, use
  (1,u,1+u) and pairs (1,1) for the rest. These are nonzero elements of the
  chosen characteristic-two field; division by each z_d is permitted.

The component outputs are simultaneous because their vertex sets are
disjoint. Their combined vector has every diagonal nonzero and every
forbidden entry zero. Recover it in the selected columns of L', placing the
coefficients only into the corresponding originally active slots of X',Y'.
Thus

    N0 = Q'_A X' + Y' R'_B

uses termwise subsets of the original factor supports. Finally multiply row
p of N0 by its nonzero diagonal entry's inverse, and apply that same scaling
to row p of every source factor in both orientations. This preserves those
supports and all forbidden zeros while making every diagonal one. The
result is the claimed strict fit N.

The proof uses the complete matrix M throughout. It never assumes the A and
B subsums separately satisfy the mask, and it never performs incompatible
independent transfers on those two subsums.

### Optional preservation of the complete zero pattern

The same argument can preserve the entire endpoint zero/nonzero pattern.
Instead of using only diagonal vertices, let D be every old nonzero matrix
position in each selected component. An old tree cannot have exactly one
such position, by its everywhere-nonzero annihilator. For at least two,
choose nonzero values at every position in D with weighted sum zero as above;
a full-rank component recovers ones on D. Set all other positions to zero.
The resulting matrix has exactly the old zero/nonzero pattern. Final row
normalization preserves that pattern and fixes every diagonal to one.

This stronger variant still permits the values of free entries to change.
It does not preserve their old coefficients or the exact canonical endpoint.
The fixed formal characteristic-two field supplies all required choices.

## 4. The P112 invoice consequence

The [authenticated expansion argument](PROOF.md#the-universal-i334-implication-for-p112)
and [independent expansion audit](INDEPENDENT-PROOF.md) show that every
characteristic-two strict fit of the fixed physical mask expands to I334.
Each lifted rank-one term has rank at most its full binary source/reader
pairing tariff. Rank subadditivity therefore gives

    sum_t rho(source_t,reader_t) >= 334.

The transferred supports only shrink, and binary pairing rank is monotone
under deleting complete source or reader groups. The original rational
invoice is consequently at least 334 as well. The existing standalone
geometry checks authenticate all 111,556 expansion coefficients, including
all permitted free entries; this extension adds no unverified geometry
premise.

A common within-group gauge also qualifies. Let G be one invertible rational
block-diagonal matrix on the 37 triads and residual line. The similarity
M -> G M G^-1 preserves own identity blocks and forbidden whole zero blocks.
It changes each factor to `(G q_t)(G^-T r_t)^T` without changing either
whole-group support or tariff. If every transformed term has a two-port
side, possibly a different side for different terms, the same 334 floor
applies. Separate gauges chosen independently per term are not covered.

## 5. The stronger splitting budget

For each arbitrary original term, choose a partition of its source scalar
support into chunks of size at most two, retaining the original reader.
Independently choose a partition of its reader support into chunks of size
at most two, retaining the original query. Define

    delta_source(t) = sum_source_chunks rho(chunk,reader_t)
                      - rho(source_t,reader_t),
    delta_reader(t) = sum_reader_chunks rho(source_t,chunk)
                      - rho(source_t,reader_t).

Both are nonnegative by row/column rank subadditivity, including when several
chunks touch the same physical group. For each term, expand on whichever of
these two chosen partitions is cheaper. The endpoint stays exactly unchanged
and every new term has a two-port side. Mixed orientations are allowed, so

    C + sum_t min(delta_source(t),delta_reader(t)) >= 334.

This holds for every selection of the two partitions per term. A proposed
C <= 296 decoder requires at least 38 units of this mixed splitting overhead.
One may also minimize each side over partitions, but no partition optimizer
or feasible decoder is supplied here. The earlier uniform-side budget tests
remain valid consequences.

## 6. Finite controls, attribution and scope

The quantified argument above is a written proof independently reviewed by
separate AI agents; see [INDEPENDENT-MIXED-PROOF.md](INDEPENDENT-MIXED-PROOF.md).
It is not a proof-assistant formalization or an independent human review.
`mixed_controls.py` checks literal finite-field examples against the compact
[MIXED-CONTROLS.json](MIXED-CONTROLS.json) receipt, read-only by default:

- A replicated-gain commuting square stays balanced, testing why independent
  gains cannot be assigned to each vectorized copy.
- A selected old unbalanced repeated-gain cycle remains nonsingular over an
  explicit F4 specialization.
- A five-term mixed I3 factorization has dense factors on opposite sides of
  different terms, with forbidden off-diagonal cancellations across the two
  classes, and a support-preserving characteristic-two realization.
- A three-diagonal tree uses F4 to obtain nonzero diagonal values, followed
  by one consistent global row scaling to diagonal one.

These controls test the proof's failure modes. They do not replace its
universal repeated-gain and diagonal-recovery arguments. Existing input pins,
full-group tariffs, residual 6+1 completion and endpoint-preserving companions
are unchanged.

Signed-incidence rank, switching and circuits are standard; see Thomas
Zaslavsky, [Signed Graphs and Geometry](https://people.math.binghamton.edu/zaslav/Tpapers/sggm.pdf),
Theorems 3.1 and 3.5-3.6. We prove the required arbitrary-gain facts directly;
the mixed strict-mask transfer is not attributed to that signed-only survey.
No unrestricted 334 floor, changed physical mask, chosen-endpoint preservation,
native schedule, storage bound, all-size supplier or new multiplication upper
bound is claimed. Prepared by flyingviper with substantial OpenAI Codex
assistance and separate AI-agent mathematical checks. Apache-2.0.
