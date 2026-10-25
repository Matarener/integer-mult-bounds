# Suggested coherent mathematical package and scope boundaries

The strongest coherent local package is a theorem about sharp fixed-support
unary tariffs, with the scalar quartic companion and an explicit boundary
counterexample. It should not be divided into a separate contribution for
each checking script or intermediate scalar proof. This is a mathematical
packaging recommendation only; upstream overlap and permission to publish
remain the parent's responsibility.

## Main theorem: order four with swap-algebra bridges

Use `fixed-support-audit/PROOF.md` as the principal prior result, supported
by this review. It strengthens the adjacent `UNARY-ORDER4-GATE.md` scalar
model by admitting GL_m(K[S]) and every finite restored dirty helper stock.
The older scalar proof is useful derivation history or a simple corollary,
not a separate headline result in the same package. The literal normalized
N_f formula gives its balanced spectrum for every f>=1.

This is an all-parameter written theorem: exact query optimum 2n, no new
kappa. Its carrier costs remain explicit premises. Retain both B=1
characters for total-bridge forcing and both B=-1 characters for the
sum-rank proof. Retain the actual two-dimensional native constituent. A
proof restricted only to the primitive B eigenvalues would lose the
zero-endpoint constraints.

## Companion theorem: quartic carrier, scalar bridges

The adjacent `QUARTIC-OPPOSITE-GATE.md` argument is valid with arbitrary
scalar bank GL, exact restoration of all dirty helpers, and all four
actual roots of z^4+1 represented. It does not assume nonexistent +/-1
augmentation characters. Work over a splitting-field extension if needed;
scalar extension preserves the relevant ranks and operator equality.

After bridge extraction the normalized word satisfies

    W(z)=C^-1 diag(z^2 I_n,I_h),
    W(z)-I=U G(z)V,   G(z)^-1=D(z)^-1-L,

where C is an arbitrary invertible scalar bank matrix and U,V,L do not
depend on z. Choose actual roots z,w with z^2=+i,w^2=-i. Then
rank(W(z)-W(w))=n, forcing rank(U),rank(V)>=n.

For opposite roots z,-z the endpoints agree. The resolvent identity is

    G(z)-G(-z)=G(z)[D(-z)^-1-D(z)^-1]G(-z).

The middle diagonal entries are -2z/(z^2-1) for a forward query and
+2z/(z^2-1) for an inverse query. Every entry is nonzero. Thus the
difference is invertible and U[G(z)-G(-z)]V=0 gives

    k>=rank(U)+rank(V)>=2n.

Two calls per output attain it. All helpers and the arbitrary total bridge
remain present. This is an all-n,m written proof, not a search theorem.

For the displayed common-one/fresh-one carrier, H_f=(ZC^-1)^(tensor f),
A_f=(H_f tensor I)S, one has H_f^2=(-i)^f I and A_f^4=(-1)^f I.
At odd f, tr(H_f)=0. The swap trace identities yield tr(A_f)=tr(A_f^2)=0;
also A_f^3=(H_f^2 tensor H_f)S has trace tr(H_f^3)=0. The polynomial
t^4+1 is separable, and these three zero moments force equal positive
multiplicity 2^(2f-2) at its four roots. This independently supplies the
mathematical actual-spectrum premise. Even f has order four and requires
the separately stated order-four scalar theorem; it is not an odd-f case.

Do not silently advertise the quartic theorem with GL_m(K[S]) bridges.
That stronger alphabet is not covered by this scalar U,V argument. The
order-four D8 proof's r>=2 constituent premise also must not be imported
into the common-one f=1 carrier, where r=1.

## Boundary counterexample: zero native queries with growing scan count

`ZERO-HELPER-SCAN-COUNTEREXAMPLE.md` gives a correct all-m,f construction on
two independent public arrays. For each internal bit j, C_j=alpha I+beta X_j
and C_j^-1=beta I+alpha X_j. The three shears

    a += C_j b;  b -= C_j^-1 a;  a += C_j b

produce (C_j b_old,-C_j^-1 a_old). A bank swap and sign on the first bank
produce (C_j^-1 a_old,C_j b_old). Each shear is exactly two ordinary
scalar/ADDRESS ADDs because its source bank is unchanged between terms.
Thus one bit costs six ADD scans, one bank swap and one sign scan. Repeating
over mf bits gives full tensor chirps on both arrays. A final ADDRESS flip
of all internal bits on the first array aligns both outputs in the forward
orientation, since C_total^2=X_all.

The exact invoice is 6mf ADD scans, mf bank swaps, mf sign scans, and one
optional final ADDRESS scan. No helper or initialized input is used. The
per-bit identity and commutation of distinct-bit factors prove all m,f>=1;
the preserved finite producer tests additionally cover all input
coefficients at (m,f)=(1,1),(1,2),(1,3),(2,2), literal inverses, and an
omitted-ADD defect.

The boundary claim is precise: zero-helper arbitrary dirty linear algebra
alone does not imply a positive native-query-mass lower bound if this
ADDRESS-valued ADD alphabet and scan count are allowed. It does not
contradict either restricted unary theorem. Its work is O(mf*2^(mf)) in
an ideal array arithmetic model, before any added physical access costs,
and it supplies no favorable constant-scan cost or improved exponent.

## Publication claim separation

| Result | Mathematical status | Claim that must stay excluded |
|---|---|---|
| Swap-algebra fixed-support 2n optimum | All-parameter written proof; finite exact witnesses | General ADDRESS/Pauli or variable-support optimum |
| Scalar quartic 2n optimum | All-parameter written proof; finite exact witnesses | Swap-algebra quartic optimum without a new proof |
| Zero-query scan construction | All-parameter per-bit identity; finite full-column checks | Constant-scan supplier, physical tape theorem, kappa gain |

The native carrier receipts supply source formulas and previously checked
lowering evidence. This review independently proves their spectral
premises but does not re-audit physical implementations or upstream
acceptance. No formal-kernel proof is present. The package should retain
the original source attribution and all no-new-kappa limits.
