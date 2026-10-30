# Geometry of shared queries and nonidentity native transport

Dugongue, with substantial OpenAI Codex assistance. This volume contains 25 proved informal construction statements, ten finite research questions and five routes. The underlying linear algebra and symplectic tools are classical. The proposed contribution is their application to changed Gaussian interfaces with explicit physical bills; neither worldwide novelty nor a new κ is asserted.

## Current scope and predecessors

The selected helper-subspace P104 checkpoint and the pending paid-meeting/retained-copy words are distinct from the old seven-axis A/B/C provider. A theorem about one is not automatically a theorem about the other. Pending PR 5774 reports a retained-native-copy construction; PR 5751 constructs paid meetings; PR 5718 uses different input and output helper bases; PR 5739/5756 changes a scalar block's chart. Their source and target counts are prerequisites for any application below.

Several easy-looking routes are already covered. PR 5772 classifies the canonical chart for its fixed scalar block. PR 5779 gives sharp detour tariffs for a fixed helper/query pair, including arbitrary intermediate Clifford charts. PR 5676 proves a complete positive residual for the identity-native path contract. PR 5783 implements global binary submodular optimization, crediting earlier general coframe-cut work and PR 5698. Thus another single-chart optimization, fixed-endpoint helper detour, or identity-native local invoice is not presented here as a new funding route.

The routes below change explicit contracts: keep nonidentity logical natives and solve their shared transport equations; allow noncommuting ordinary operations on spectator multiplicities; exploit proved relations in owned snapshots; optimize extensions off actual tensor support; or change several query/target interfaces together. Every changed physical operator, owned lifetime and original target must be counted. These statements supply constructions, not unpriced gadgets.

The earlier algebra atlas supplies recovery, dirty mediation, support restriction and low-rank inverse tools. The prior joint-coframe notes supply the inverse-Lagrangian convention and signed costs. They are recovered and credited background. Local linked-tree sources read include `Mathproof.SymplecticTI`, `Mathproof.SymplecticTIEncoding`, `Mathproof.LibraryBridges.Claude.TIModuleIso20260905`, `Mathproof.WeightedTIStabilizerShears20260906`, `Mathproof.Abstraction.LinearInvariantSynthesis`, and `Mathproof.LinearAlgebra.SchurBlockElimination`. Source inspection is not a fresh kernel audit.

## Conventions

All vector spaces are finite dimensional over a field K. Where halves are used assume char K is not two; the physical dyadic model uses Q or C. Products act rightmost first. A physical Gaussian call Q is an explicit admitted operator on one payload field, including identity spectators. An ordinary operation has a supplied literal finite implementation: being a matrix over K alone does not make it ordinary. Owned fields start with a paid scrub and end with a paid clear; they are never productive targets. Every original public input remains arbitrary.

A symplectic space has dimension 2m and computational Lagrangian Z. An exact Clifford H has inverse computational Lagrangian Lambda(H)=S_H^(-1)Z. The retained Clifford lowering is required to supply the complete phase and two-sided positive Gaussian matcher, not just a binary symplectic matrix.

## Route I Nonidentity transports as a linked representation

### G01 Tree propagation of a shared transporter

**Statement.** On an oriented connected graph let A_e and B_e be explicit invertible maps for each edge u to v. Choose a root and a spanning tree, with path products A_v and B_v from the root to v. Every family satisfying P_v A_e=B_e P_u on tree edges is uniquely of the form

    P_v=B_v P_root A_v^(-1).

If P_root is invertible, every P_v is invertible.

**Proof.** The edge equation solves P_v=B_e P_u A_e^(-1). Induct along the unique tree path; the displayed product results. Conversely these products satisfy each tree equation by cancellation, including when the path uses an edge backward. Uniqueness follows from the same induction. Products of invertible maps are invertible. QED.

**Use and scope.** Replace separate guesses for hundreds of shared native maps by one root variable. This keeps the nonidentity maps A_e and B_e; it is not the identity-native specialization excluded by PR 5676.

### G02 Cycle equations give the complete shared-map contract

**Statement.** In G01 a non-tree edge u to v is compatible exactly when

    P_root H_A,e=H_B,e P_root,
    H_A,e=A_v^(-1) A_e A_u,
    H_B,e=B_v^(-1) B_e B_u.

Consequently the admissible root maps form a linear solution space; any explicitly supplied invertible member gives a complete coherent family.

**Proof.** Substitute G01 in P_v A_e=B_e P_u. Multiply on the left by B_v^(-1) and on the right by A_u, obtaining the displayed equation. It is linear in the entries of P_root. If all such equations hold, every edge holds, because tree equations already hold. QED.

**Use and overlap.** This is simultaneous module-intertwiner algebra, closely related to the linked module-isomorphism formalization. PR 5492 already exhibits an actual native cycle defect; PR 5058 treats relative operators for four graph frames. This result supplies a complete constructor for a supplied graph, not an assertion that the current graph admits a cheaper solution.

### G03 A determinant witness can be chosen from a finite grid

**Statement.** Let V be a linear space of n by n candidate root matrices, with explicit basis X_1,...,X_d. If the determinant polynomial det(sum t_i X_i) is not identically zero, and K contains at least n+1 distinct elements, then some combination with all t_i in any fixed set of n+1 distinct field elements is invertible.

**Proof.** The determinant has degree at most n in each variable. A univariate nonzero polynomial of degree at most n cannot vanish on n+1 points. Induct on d: if the polynomial vanished on the whole product grid, view it as a polynomial in the last variable, so every coefficient polynomial vanishes on the lower-dimensional grid, and induction makes every coefficient zero. This contradicts the premise. QED.

**Use.** A downstream search can return a small explicit invertible combination and its determinant, rather than an unspecified isomorphism oracle. Small fields require their own exact invertibility witness; passing to an extension has a real representation cost.

### G04 Shared idempotents split all transport equations

**Statement.** Suppose explicit idempotents E_v satisfy E_v A_e=A_e E_u on every edge, and put F_v=I-E_v. Then each A_e restricts to isomorphisms im E_u to im E_v and im F_u to im F_v. The whole representation is the direct sum of these two subrepresentations.

**Proof.** If x=E_u x, then E_v A_e x=A_e E_u x=A_e x. Thus A_e x lies in im E_v. Apply the same argument to A_e^(-1). The identity for F follows by subtraction. Every vector splits uniquely as E_v x+F_v x, since an idempotent's image and kernel are complementary. QED.

**Use.** Optimize a true shared native block on each invariant summand, then include the actual input/output basis change. It is essential that the idempotents intertwine every edge; unrelated local eigenspaces cannot be independently glued.

### G05 The dual block can be transported simultaneously

**Statement.** For an invertible P define its Levi lift L(P)=diag(P,P^(-T)) on U direct-sum U*. It is symplectic. If P_v A_e=B_e P_u, then

    L(P_v)L(A_e)=L(B_e)L(P_u).

**Proof.** The canonical alternating pairing is psi(x)-phi(y). Inserting P and P^(-T) cancels P^(-1)P in both terms, so the pairing is preserved. Levi lifts multiply as L(PQ)=L(P)L(Q); apply this identity to the given equation. QED.

**Use and credit.** This is classical Levi lifting, explicitly marked prior art in the TI formalization. It gives a proof-preserving symplectic completion of the coherent maps in G02. Both P and P^(-T), including their scalar/movement costs, must have explicit physical implementations.

## Route II Noncommuting spectator matrix units

PR 5626 proves an exact query minimum in its declared commuting-involution coefficient alphabet. The next statements enlarge that alphabet. They do not invalidate its theorem. A scalar owner matrix tensored with spectator identity receives no automatic reduction from the larger algebra.

### G06 Two ordinary anticommuting involutions give matrix units

**Statement.** Let S^2=T^2=I and ST=-TS. Set P_0=(I+S)/2, P_1=(I-S)/2 and

    E_ab=T^(a xor b) P_b,  a,b in {0,1}.

Then E_ab E_cd equals E_ad when b=c and zero otherwise; E_00+E_11=I. If Q commutes with S and T, it commutes with every E_ab.

**Proof.** P_0,P_1 are complementary orthogonal idempotents. Anticommutation gives T P_b=P_(1-b) T, so E_ab maps the b summand into the a summand, with the two off-diagonal maps inverse to each other. If b differs from c the two intermediate projectors multiply to zero; if b=c their T powers cancel to the displayed E_ad. Commutation with Q follows from the formulas. QED.

**Use.** These are literal coefficients for a full Mat_2(K) ordinary algebra, not merely two independent Boolean sectors. The projectors use dyadic ADD/SCALE/COPY/CLEAR work and carry positive ordinary cost.

### G07 A passive address bit realizes the algebra

**Statement.** Suppose the actual payload address set is {0,1} times D. On functions define

    (Sf)(epsilon,z)=(-1)^epsilon f(epsilon,z),
    (Tf)(epsilon,z)=f(1-epsilon,z).

These are monomial involutions with ST=-TS. If Q acts only on D and identically on epsilon, it commutes with both. P_b is exactly the projector onto addresses with epsilon=b.

**Proof.** Applying either map twice restores f. The sign used by S changes under T, giving STf=-TSf pointwise. Since Q does not alter epsilon and its coefficients do not depend on epsilon, Q commutes with both pointwise sign and bit permutation. Substitution in (I+(-1)^b S)/2 gives the projector. QED.

**Physical condition.** The bit must be a genuine passive factor of the actual source embedding. It cannot be manufactured by treating an odd-sized address set as two equal pieces. Any padding, new spectator, source-column expansion and routing must be declared and charged.

### G08 Several passive bits realize arbitrary constant matrix units

**Statement.** On {0,1}^s times D, let P_b project onto spectator word b and let T_a flip exactly the bits in a. Then

    E_ab=T_(a xor b) P_b

are matrix units for Mat_(2^s)(K), and commute with any Q acting only on D. Each projector has the exact dyadic character formula

    P_b=2^(-s) product_(i=1..s)(I+(-1)^(b_i) S_i).

**Proof.** The product projector is one on spectator word b and zero on every other word, by a zero factor at the first unequal bit. E_ab then copies only the b piece into the a piece. Multiplying two such maps proves the matrix-unit rules exactly as in G06. QED.

**Use.** Constant s gives a fixed finite ordinary implementation of coefficient matrices. If s grows with input size, every phase, bit permutation, projection and required pass must enter the actual complexity estimate; no constant-overhead claim is made in that regime.

### G09 The Q-square sectors remain compatible with spectator mixing

**Statement.** If J=Q^2 is an ordinary involution, W_+ and W_- defined by the projectors (I+J)/2 and (I-J)/2 are Q-invariant, and Q^2 is respectively I and -I on them. Any spectator matrix units commuting with Q preserve both sectors. If those matrix units identify each sector with K^r tensor V_sigma, then Q=I_r tensor q_sigma there. Its coefficient pair I,q_sigma is linearly independent exactly when q_sigma is not scalar.

**Proof.** Q commutes with its square, so it preserves J eigenspaces and satisfies the displayed quadratic relation. A map commuting with Q commutes with J and its projectors. In a matrix-unit decomposition, commutation with every E_ab forces each diagonal corner of Q to be the same q_sigma and all off-diagonal corners zero. Linear dependence of I,q_sigma is precisely scalarity of q_sigma. QED.

**Use.** The algebra volume's exact coefficient-rank query theorem may be applied sectorwise only after this faithfulness condition is proved. At small widths one Q sector can collapse; observing Q^2=J alone is insufficient. The concrete packing construction G10 needs only commutation, so its upper bound does not rely on this quadratic reduction.

### G10 One actual query implements two conditional updates

**Statement.** Under G06, with invertible Q commuting with S,T, the desired all-input map on two original fields is

    x'=(P_1+Q P_0)x,  y'=(P_1+Q P_0)y.

It has a one-Q implementation. Scrub two owned fields h,w. Pack

    h=P_0 x+T P_0 y,

then apply Q to h once. Using the same owned work field w sequentially, execute

    w=P_0 h-P_0 x;  x += w;  CLEAR w;
    w=T P_1 h-P_0 y;  y += w;  CLEAR w;
    CLEAR h.

**Proof.** After the query, P_0 h=Q P_0 x because the packed y term lies in the P_1 summand. Similarly T P_1 h=T Q T P_0 y=Q P_0 y. The first original-field update replaces only x's P_0 component; the second does the same for y. Thus the outputs have the desired form on all arbitrary inputs, with owned fields zero on return. The output map is invertible since P_1+Q P_0 has inverse P_1+Q^(-1)P_0. QED.

**Complete ordinary recipe.** A projected source ADD into a distinct destination uses half-scaled ADDs before and after an S pass on that destination, undoing the pass, so no third field is needed: d += z/2; S d; d += z/2; S d implements d += (I+S)z/2. Change a sign for P_1. Compose with T where required, or transport the destination by T and undo it. Packing and both returned updates use only such literal reversible ADD routines. There is no nonunit overwrite of an original field. One packed field h and a separately scrubbed work field w suffice. Every copy or ADD, sign, flip, half-scale, route and clear is charged. The queried field is owned and earns no productive credit. The original two outputs remain independent targets only if the enclosing program's exact final matcher proves their required jobs.

**Frontier effect.** In the commuting-sector alphabet, the odd coefficient has owner rank two on sector zero and zero on sector one. The extra T uses unused spectator capacity and changes that alphabet. This is a concrete possible query reduction, not a claim that an actual P104 boundary already has this shape. A scalar boundary B_owner tensor I_r has no such free capacity: its expanded coefficient rank is r times rank B_owner.

## Route III Reachable snapshot graphs as a stabilizer resource

The current retained-copy words supply exact version identities rather than free caches. A proved graph relation in owned copies can create a large family of semantically invisible ordinary rewrites. These constructions do not assume that any arbitrary original field is zero.

### G11 Recovery from an actually sufficient observation

**Statement.** Given explicit H:X to Y and F:X to Z with ker H contained in ker F, construct D:Y to Z with DH=F.

**Proof.** Define D(Hx)=Fx on im H. Equal observations differ by an element of ker H and hence have equal F values, so this is well defined. Extend a basis of im H to Y and set D to zero on the added basis vectors. QED.

**Use and credit.** Recovered from the earlier algebra atlas A001. It permits a source consumer to request only its actual observation, but producing H and implementing D are still priced. It is not permission to replace independent original helpers by related inputs.

### G12 All automorphisms fixing an owned snapshot graph

**Statement.** Let S_L={(x,Lx)} in X direct-sum Y and T_L=[[I,0],[L,I]]. Every linear automorphism fixing every point of S_L is exactly

    P=T_L [[I,B],[0,E]] T_L^(-1),

where B:Y to X is arbitrary and E is invertible on Y.

**Proof.** T_L sends X direct-sum zero to S_L. A linear map fixing X direct-sum zero pointwise has first column blocks I and zero, hence is [[I,B],[0,E]]. It is invertible exactly when E is. Conjugate by T_L. QED.

**Use.** Parameterize an entire family of rewrites at a proved live snapshot relation h=Lx. If L is an ordinary stored-version map and B,E,E^(-1) have actual ordinary words, this family can be searched without changing the actual cut state. Its action on arbitrary ambient garbage need not be identity, but its own implementation is invertible.

### G13 A square-zero subgroup has an explicit inverse

**Statement.** In G12 choose E=I and put N=T_L [[0,B],[0,0]] T_L^(-1). Then N^2=0, P=I+N and P^(-1)=I-N. The determinant is one.

**Proof.** The square of the middle strictly upper block is zero. Conjugation preserves this equality, so (I+N)(I-N)=I. In the T_L coordinates the matrix is block upper triangular with identity diagonal, hence determinant one. QED.

**Use.** This supplies a finite cheap subfamily of snapshot stabilizers. It can be implemented using the supplied words for L and B and their sign reversals; no inverse oracle or odd denominator is introduced by this formula.

### G14 Every replacement agreeing on the reachable subspace is explicit

**Statement.** Let S be a proved reachable subspace and F a specified map. Fix the quotient pi:V to V/S. All maps agreeing with F on S are precisely F+E pi, with E arbitrary.

**Proof.** Such an added term vanishes on S. Conversely, the difference between any two maps agreeing on S factors through V/S: define E([v]) by that difference, which is well defined because changing v by an element of S changes the difference by zero. QED.

**Use and credit.** This recovers the affine decoder freedom of old atlas A002 as an exact window-replacement family. An implementing solver must prove S from the actual source-version columns. The full original input space may be large even when the owned extension has many linear relations.

### G15 Snapshot stabilizers can be distributed across a whole window

**Statement.** Let M_i be a fixed linear instruction word, S_i its actual reachable subspace after step i, and let P_i be explicit invertible maps fixing S_i pointwise. Define

    M_i'=P_i M_i P_(i-1)^(-1).

The new instruction agrees with M_i on S_(i-1), and the full modified window has the same all-original-input endpoint.

**Proof.** P_(i-1)^(-1) fixes every point of S_(i-1). M_i sends that subspace into S_i, which P_i fixes. Thus the modified step returns exactly the old state on every reachable input. Induct on i. Equivalently, the whole product telescopes to P_last M_last...M_1 P_0^(-1), whose boundary factors fix the relevant actual states. QED.

**Use.** Instead of changing one canonical chart in the fixed PR 5772 contract, search several explicit snapshot stabilizers and regenerate the WHOLE instruction window. Each new physical instruction must be decomposed and priced; this theorem preserves semantics but does not claim its query cost decreases. It can change scalar assignments and shared-query structure, both outside the single-chart tariff theorem.

## Route IV Support-aware symplectic completion

### G16 Every extension of a support isomorphism is parameterized

**Statement.** Let f:S to T be an isomorphism. Choose explicit complements C,D with U=S direct-sum C=T direct-sum D. Every invertible P extending f has the block form

    P=[[f,B],[0,E]],

where B:C to T and E:C to D is invertible. Its inverse is [[f^(-1),-f^(-1)BE^(-1)],[0,E^(-1)]].

**Proof.** The restriction to S fixes the first column blocks. The induced map on the quotient complements is E, and the whole map is invertible exactly when E is. Multiply the displayed block matrices in both orders. QED.

**Use.** An input-support constraint leaves B,E as genuine optimization variables. The inverse formula makes the dual cost visible; a sparse primal extension can have an expensive inverse.

### G17 Low-rank primal corrections have a complete dual formula

**Statement.** If P=I+UV with U:K^r to U_0 and V:U_0 to K^r, and I_r+VU is invertible, then

    P^(-1)=I-U(I_r+VU)^(-1)V,
    P^(-T)=I-V^T(I_r+VU)^(-T)U^T.

**Proof.** Multiply the first candidate by I+UV and use (I_r+VU)^(-1)(I_r+VU)=I_r to cancel all nonidentity terms. The product in the opposite order is checked similarly. Transpose the equality for the second formula. QED.

**Use and credit.** Recovered Woodbury/Levi construction from old atlas A027/A045. It gives an explicit primal-plus-dual implementation through r owner coordinates when U,V and the small inverse have supplied words. Ordinary matrix rank r is not automatically the Gaussian query grade; no such identification is made.

### G18 Tensor action depends only on actual support

**Statement.** Let tensor t lie in S_1 tensor S_2 tensor S_3. If P_i and F_i agree on S_i, then

    (P_1 tensor P_2 tensor P_3)t
      =(F_1 tensor F_2 tensor F_3)t.

**Proof.** Expand t in bases of the three S_i. Each pure tensor term has all three factors in their corresponding support, where the two maps agree; apply multilinearity and sum. QED.

**Use and credit.** The local TI proof uses support restriction and explicit recovery to extend transporters. Here it licenses optimizing the off-support blocks in G16 before compiling the primal/dual maps. A supplier's arbitrary original inputs cannot simply be declared to lie in a smaller support; the tensor or cut-state support must be an actual proved property.

## Route V Coupled query geometry and moving interfaces

### G19 Transition rank uses inverse computational Lagrangians

**Statement.** The Gaussian rank of H_b H_a^(-1) is

    d(Lambda(H_a),Lambda(H_b)),
    d(A,B)=m-dim(A intersect B).

This d is a metric on Lagrangians.

**Proof.** For a symplectic block matrix [[A,B],[C,D]], rank B equals m minus the dimension of the intersection of Z with its image. Apply H_b^(-1) to the intersection for H_b H_a^(-1), obtaining the intersection of the two inverse computational Lagrangians. The triangle inequality follows from dim(A intersect C)>=dim(A intersect B)+dim(B intersect C)-m. QED.

**Credit.** Recovered from the prior coframe atlas; PR 5676 and PR 5779 already use the resulting metric. This is a dependency, not a new tariff claim. Earlier GLOBAL-FRAME-MINCUT notes also contain joint-move constructions; the recovered recent notes are not asserted to be the first project use of a cut.

### G20 A common isotropic part can be quotiented in geometric search

**Statement.** If K is isotropic and contained in Lagrangians A and B, then A,B lie in K-perp, their quotients in K-perp/K are Lagrangian, and

    d_m(A,B)=d_(m-dim K)(A/K,B/K).

**Proof.** Since A is isotropic and contains K, it lies in K-perp; the same holds for B. The quotient symplectic form is nondegenerate, and each quotient has half its dimension and remains isotropic. Their intersection is (A intersect B)/K, so subtract dim K from the two dimensions in the distance formula. QED.

**Use.** Compress the search certificate and its rank tables to the varying quotient. This does not by itself remove an actual physical spectator: its phase, source-column embedding and all-original-input endpoint still require exact ordinary matchers.

### G21 Explicit geodesic charts between two Lagrangians

**Statement.** Let A,B be Lagrangian, K=A intersect B and r=d(A,B). In the reduced symplectic space K-perp/K, choose any s-dimensional L contained in A/K. Let L-ann denote its annihilator in B/K. Then

    M/K=L direct-sum L-ann

defines a Lagrangian M containing K, with d(A,M)=r-s and d(M,B)=s.

**Proof.** The pairing between A/K and B/K is perfect because their intersection is zero. Thus L-ann has dimension r-s. The two summands pair to zero and are separately isotropic, so their sum is Lagrangian. Its intersection with A/K is L, and with B/K is L-ann. Insert their dimensions in d. QED.

**Use.** This gives an exact family of arbitrary Clifford meeting charts, including noncanonical ones. By PR 5779, choosing a noncanonical chart alone cannot beat its fixed-helper one-query tariff bound. The intended use is a shared query graph, changed original endpoints or several original queries with a fresh combined invoice.

### G22 Several prescribed channels can share one geodesic chart

**Statement.** In G21's quotient write a specified subspace T by its projections T_A to A/K and T_B to B/K. If every vector in T_B annihilates every vector in T_A, choose L with

    T_A contained in L contained in ann_(A/K)(T_B).

Every such L yields the explicit geodesic M of G21 containing T. A choice of dimension s exists whenever dim T_A<=s<=r-dim T_B.

**Proof.** The annihilation condition supplies the inclusion of the lower subspace in the upper. Extend a basis to dimension s inside that upper space. Every a+b in T has a in L and b in L-ann, so belongs to M/K. G21 proves the remaining properties. QED.

**Use.** A multi-helper shared meeting can impose all its channel conditions at once. This is a sufficient geometric constructor, not a proof that the resulting arbitrary helper values can be retired or that its extra queries are funded. Those require the exact scalar relation, ownership and full target delta.

### G23 Ordinary intertwiners create a commuting block code

**Statement.** Let Q_i=P_i Q P_i^(-1) and D_i=P_i D P_i^(-1), with every P_i an explicitly supplied ordinary isomorphism. For an invertible scalar owner matrix A define blocks

    C_ij=P_i A_ij P_j^(-1).

Then C commutes with diag(Q_i) and diag(D_i), and C^(-1) has the same formula with A^(-1).

**Proof.** Let P=diag(P_i). Then C=P(A tensor I)P^(-1), while the diagonal Gaussian blocks are P(I tensor Q)P^(-1) and P(I tensor D)P^(-1). The scalar owner matrix commutes with both common payload operators; conjugate these equalities. The inverse formula follows by cancellation. QED.

**Use and scope.** This is a positive decoder constructor when the ACTUAL ordinary intertwiners exist. PR 5621 excludes nonzero scalar mode-code commutation with the old source central line except its characteristic case. Merely changing the scalar owner basis does not escape that result. To use G23 one must supply changed physical maps or actual ordinary P_i for a different contract, and price all their words.

### G24 A decoder may commute on a proved reachable channel

**Statement.** Let S be invariant under C,C^(-1),D. If CDx=DCx for every x in S, then C D C^(-1)y=Dy for every y in S. Thus a pre/post C decoder is exact on that channel even if C and D do not commute on the full space.

**Proof.** For y in S, x=C^(-1)y remains in S. Then C D C^(-1)y=C Dx=DCx=Dy. QED.

**Use.** Search owned or extracted channels with an actual invariant relation, not unrestricted original receiver inputs. This changes the decoder contract relative to the full arbitrary-input scalar mode-code classification and must be verified at the exact producer/consumer cut.

### G25 Moving central operators can close a two-provider interface

**Statement.** Suppose actual paid providers supply

    B_0=[[D_0,0],[D_0,D_0 Q_0]],
    C_1^-=[[D_1 Q_1,0],[-D_1,D_1]].

If Q_1 D_0=D_0 Q_0, their chronological composition B_0 then C_1^- is

    diag(D_1 D_0 Q_0,D_1 D_0 Q_0).

No assumption Q_0 D_0=D_0 Q_0 is required.

**Proof.** The off-diagonal block is -D_1D_0+D_1D_0=0. The two diagonal blocks are D_1Q_1D_0 and D_1D_0Q_0, equal by the stated intertwiner. QED.

**Use.** This generalizes the earlier common-central-line C/B cancellation to a moving central interface while retaining exact endpoints. One can nominate Q_1=D_0 Q_0 D_0^(-1), but this algebraic expression alone does not supply an admitted rank-one native interface: its Gaussian grade, phase, ordinary matchers and actual provider must be given. If supplied, the theorem assembles them without an additional central repair query. The full cost is both complete provider lists plus their actual ordinary adapters, not a new standalone κ.

## Open next questions

These are finite research tasks for the current source families. They are not advertised as previously unknown mathematical conjectures in the literature. Each positive answer should supply its explicit words, interface proof and full signed bill.

### GQ01 A real passive-bit packing opportunity

Does an actual retained-native-copy or paid-meeting caller window have two conditional Gaussian updates with the exact same passive bit and G10's input/output partition? **First step:** extract its odd coefficient blocks including all spectators. **Payoff:** a literal two-to-one query substitution, with unchanged original targets. **Missing evidence:** actual S,T words, parent embedding, phase matchers and full ordinary allowance. A scalar role boundary B tensor I has no benefit.

### GQ02 Several spectator bits with nonuniform odd response

Can a real caller expose an odd response whose expanded coefficient rank is strictly below r times its old largest sector rank, with an explicit constant r=2^s spectator matrix-unit algebra? **First step:** compare coefficient ranks only after identifying exact source owner versions. **Payoff:** the algebra volume's noncommuting matrix-unit compiler can pack response into fewer native requests. **Scope:** no target credit follows from response rank alone.

### GQ03 Coherent nonidentity gauges from the native cycle module

For one actual P104 local word, does the G02 intertwiner space contain an explicit ordinary-admissible invertible map that improves several frame contacts together? **First step:** choose the source incidence graph and list all independent cycle products. **Payoff:** changes the coordinate family while preserving the nonidentity natives. **Missing evidence:** actual ordinary implementation and positive full invoice; an arbitrary GL solution is not enough.

### GQ04 Invariant summands shared by the complete contract

Do the native cycle operators and the required main/helper boundary operators admit a common nontrivial idempotent with an inexpensive physical basis? **First step:** solve the exact linear commutant equations and test a nominated idempotent. **Payoff:** G04 allows independent optimization of real shared blocks. **Scope:** the full boundary contract must preserve the same split.

### GQ05 A retained-copy graph stabilizer with a query saving

At an actual window in PR 5774 or its successor, find a proved owned graph h=Lx and a finite G13 stabilizer that lets the entire window use fewer Gaussian requests. **First step:** derive L from the exact source-version witness, then choose a sparse B. **Payoff:** exploits the new ownership contract rather than another fixed-frame detour. **Missing evidence:** full regenerated word and all arbitrary-input columns.

### GQ06 Several snapshot stabilizers coordinated across a long window

Can a sequence of G15 stabilizers change the scalar assignment around several queries while retaining all actual states and every original target? **First step:** select a short chain of cuts with exact row-space relations, keeping the endpoints frozen. **Payoff:** moves outside PR 5772's fixed scalar-block chart contract. **Scope:** physical operator factorization and price must be recomputed for every modified instruction.

### GQ07 Shared noncanonical meetings across several original queries

Can G22 construct one chart that supports an actual multi-helper scalar relation and replaces more than one old query at once, with a positive full delta? **First step:** express all required channels in one reduced transverse pair and test the cross-annihilation equations. **Payoff:** changes the shared graph beyond PR 5779's one-original-query tariff. **Missing evidence:** causal retirement/continuation and all lost target debits.

### GQ08 A cheap primal and dual support completion

For one actual tensor or helper observable with proved support, find parameters B,E in G16 whose complete primal-plus-dual word is cheaper than the current extension. **First step:** use the source support basis, then G17 for low-rank changes with explicit small inverse. **Payoff:** uses genuine TI support freedom without confusing orbit equivalence with a physical decoder. **Scope:** no restriction of an arbitrary original input is allowed.

### GQ09 A moving central native interface

Can actual admitted providers realize G25 with nonconstant Q_j transported by the preceding D_j, keeping their required rank-one interfaces and ordinary matchers? **First step:** construct one exact conjugated central operator and lower it through the native compiler. **Payoff:** closes a two-provider endpoint without paying a central correction. **Missing evidence:** a compatible source supplier, full inventory, spectators and complete outer caller. Conjugacy alone is not that supplier.

### GQ10 A reachable decoder channel beyond scalar commutants

Is there a produced owned/extracted channel S on which an actual code C satisfies G24, even though global commutation is excluded by PR 5621? **First step:** prove S invariant under C,C^(-1),D from the exact producer and test its commutator there. **Payoff:** a valid ordinary decoder on a changed contract. **Scope:** the unrestricted original receiver cannot be substituted for S unless S is the whole receiver space.

## Attribution and evidence

The topology of the routes is a proposal; the numbered algebraic constructions above have informal proofs. No mathematical computation, source replay, numerical pricing, solver, Lean run or new Gaussian exponent is claimed by this volume. Current PR statements are recorded as their authors' scoped claims, not independently accepted here.

Retain Ali Romman for PR 5774/5751/5772/5779/5783 and the exact sector compiler PR 5626; flyingviper for PR 5718; Joel Pulikkan/GamingPuzzled for PR 5739/5756; Dugongue for prior general coframe, auxiliary-line and uniform-provider constructions; Cao Yifan, Cinna Davis, DaysSky, Nick Petalas, Ryanson Jonathan, zxv, Jacob Alan Sussman and all retained native/Clifford/phase/ownership/controller/compiler/BIT authors. The old algebra atlas's recovery, Woodbury and support tools are explicitly recovered rather than claimed as new discoveries. Classical graph representation, idempotent decomposition, Levi, tensor-support, matrix-unit and symplectic-geodesic mathematics keeps its standard attribution. New text is Apache-2.0.
