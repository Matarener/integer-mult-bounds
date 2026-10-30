# Complete Gaussian coframe optimization by minimum cut

## Physical convention

Fix a finite exact linear program on payload fields. Original inputs are arbitrary and independent. Extra owned fields are scrubbed on entry and cleared on exit. Its logical endpoint is a fixed main map and an autonomous identity on each logical helper. A physical coframe H at a field means that physical payload equals H times logical payload. All H are explicit phase-correct Clifford words with the retained exact ordinary matching service.

For a logical identity transport from coframe H_u to H_v, execute H_v H_u^(-1). At a scalar ADD whose two operands share one chart, keep the scalar ADD. More generally, a logical ADD v += a u in different charts is executed as

    v += a H_v H_u^(-1) u.

An explicit implementation initializes owned scratch, copies u, applies the indicated transform, adds a times that scratch into v, then clears it. A positive-rank transform uses one Gaussian child with its own two-sided ordinary matcher. A rank-zero transform uses its ordinary word. The source u remains intact. Scratch never receives productive credit.

If the old source uses one coframe for an entire scalar-contact fibre, choosing one new coframe for that entire fibre keeps all its scalar ADDs ordinary. Every physical native instruction is either frozen or explicitly recompiled as described in native-specialization.md. There is no implicit free physical warp.

**Theorem 1.** Replacing every affected instruction by its explicit coframe-conjugated instruction preserves the logical program on all inputs. Freeze actual main entrance and exit coframes. A helper with entrance H_a and exit H_b has the actual autonomous physical endpoint H_b H_a^(-1). Its old productive target must be replaced by this new endpoint's actual rank and exact matcher.

**Proof.** At each instruction substitute physical = H logical and cancel adjacent H^(-1)H. The implemented instruction is exactly its old logical action. Induction over the finite chronology proves the endpoint statement. Arbitrary helper logical inputs are still independent because each entrance chart is invertible on its own input. Every owned scratch use is initialized and cleared, so arbitrary dirty incoming scratch has no effect. Helper independence follows from the source logical direct-sum endpoint, not from a new count of array names. QED.

All instruction counts, copies, clears, monomial phases, coefficients, descriptions, normalizers, scans, storage and precision bounds belong to the new finite word. An old fixed threshold is not automatically retained. Derive fresh prefix and suffix norm bounds from the actual emitted operators at each payload width, including the query normalizations and fixed coefficient heights. The finite word supplies explicit products of these bounds; it does not justify copying old precision guards or simultaneous-instance reserves.

## The inverse Lagrangian records the right rank

Let Z be the computational Lagrangian in a 2m-dimensional symplectic space. For a coframe H define

    Lambda(H) = S_H^(-1) Z,
    d(A,B) = m - dim(A intersect B),

where S_H is its symplectic action. The inverse in Lambda is essential.

**Lemma 2.** The Gaussian rank of H_v H_u^(-1) equals d(Lambda(H_v),Lambda(H_u)).

**Proof.** For a Clifford K with symplectic block matrix [[A,B],[C,D]], the Gaussian rank is rank B. Since KZ consists of vectors (Bz,Dz), its intersection with Z has dimension dim ker B; invertibility of K prevents losing dimensions. Thus rank B = m-dim(Z intersect KZ). Apply S_Hv^(-1) to the intersection for K=H_v H_u^(-1). The result is Lambda(H_v) intersect Lambda(H_u). QED.

This is a rank statement. Full phases and positive Gaussian normalizers still come from the exact retained lowering service. An unlifted symplectic matrix is not the whole physical instruction.

**Lemma 3.** d is a metric on m-dimensional subspaces. For 0<t<=1, d_t(A,B)=d(A,B)^t is also a metric, with 0^t=0.

**Proof.** Inside B, dimension counting gives dim(A intersect C)>=dim(A intersect B)+dim(B intersect C)-m. Rearrangement gives the triangle inequality. Symmetry and separation are immediate. Finally (a+b)^t<=a^t+b^t for nonnegative a,b, so taking t powers preserves the triangle inequality. QED.

## A joint binary family

For each eligible fibre i, either keep its explicit old chart H_i, or replace it by one common explicit chart H_star. Write x_i=0 or 1 for these choices. Fixed fibres are constants. No ordinary native instruction may change unnoticed: freeze its incident fibres, or use an allowed paid table under the other notes.

Each paid identity-transport edge between i and j contributes the following t-moment table. Put A_i=Lambda(H_i) and A_star=Lambda(H_star):

    e00=d(A_i,A_j)^t,
    e10=d(A_star,A_j)^t,
    e01=d(A_i,A_star)^t,
    e11=0.

Edges to fixed vertices and centre queries with a single variable are unary costs. Scalar contacts that remain on one chart add no Gaussian edge. Their ordinary costs are nevertheless positive.

Assume every independent helper has at most one variable endpoint. Its productive contribution, with a minus sign in paid-minus-productive cost, is therefore a unary table. Fixed main targets and fixed work are constants. The helper target is computed from BOTH actual endpoint charts; no final-frame dimension replaces that computation.

**Theorem 4.** In this family the complete objective

    J_t(x)=complete paid t-moment - complete productive t-moment

is a submodular binary energy and is minimized by one finite minimum-cut instance. All helper upgrades and downgrades are included in J_t.

**Proof.** Lemma 3 gives e00+e11<=e10+e01. Thus every variable-variable paid table is submodular. Unary tables may have either sign and do not affect submodularity. For any submodular two-variable table write

    w=(e01+e10-e00-e11)/2 >=0,
    e(x,y)=e00+(e10-e00-w)x+(e01-e00-w)y+w|x-y|.

Add these expressions over all edges and include all unary helper terms. A term w|x-y| is a nonnegative undirected cut edge. A unary a x with a>=0 is an edge from its vertex to the sink when x=1 denotes the source side. If a<0, use a source-to-vertex edge of capacity -a and add constant a. Constants do not change a minimizer. Every cut is a complete coframe choice, and its cost differs from J_t by the same constant. QED.

**Corollary 5.** If an earlier valid coframe assignment belongs to this same legal binary family, the cut optimum has no larger complete J_t than that assignment.

**Proof.** Its bit vector is one feasible cut. QED.

The comparison is within one frozen logical template and one complete invoice convention. A new generator-identity template is a different family until its changed native costs are included. Keeping both template branches permits comparison without discarding a known good source.

A strict negative J_t proves a strict complete signed moment only for the complete program actually included in this graph. Optimizing a local supplier does not make its enclosing caller funded.

## Legality and what the theorem optimizes

Fix the intended recursive parent grade R. Every allowed paid-table entry must have rank strictly below R, and every productive job must have an actual source-admitted target interface. If a binary choice produces a forbidden rank, it cannot simply be left as a finite cut cost. An infinity entry may destroy submodularity. Restrict eligibility so all four entries are legal, or branch on the exceptional constraints and prove each retained subproblem's assumptions separately.

The cut reduction is an exact real-weighted optimization statement. At rational t, all integer-rank powers in its capacities are real algebraic numbers. A claimed exact optimum needs certified capacity arithmetic and an exact optimality argument. Independently rounding the four entries of a table may destroy its identity or submodularity. A nominated cut can instead be validated as a feasible word without claiming optimality.

Minimum cut optimizes the stated first-moment objective. It does not automatically satisfy higher-moment or completion constraints. Those are checked against the resulting COMPLETE word using funding-certificate.md. A search may use cut solutions as nominations without proving global optimality; feasibility and a strict certificate suffice for a positive result.

## Joint moves can beat isolated moves

The following exact energy example explains why one-at-a-time acceptance loses possibilities. Let a=2^t with 0<t<1. Use a paid edge with table (a,1,1,0), plus unary penalty a-1 for each collapsed endpoint. Keeping both gives a; collapsing either alone still gives a; collapsing both gives 2(a-1)<a. Thus no strict single move is visible, but the joint gain is 2-a>0.

This is a mathematical interaction example, not a claim that this exact cohort has been found in the retained source. Its unary penalty has the same signed form as replacing an H2 helper target by H1. The source task is to instantiate the complete incidence graph and target tables, rather than copy this illustrative count as a new physical witness.
