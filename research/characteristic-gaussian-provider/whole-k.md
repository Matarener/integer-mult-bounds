# A smaller whole-K/E primitive from faithful radical completion

Dugongue, with substantial OpenAI Codex assistance. This is informal mathematics based only on local DAG, linked Lean sources and retained proof notes. No numerical experiment, executable mathematical check, Lean run or external search is used. The result below constructs a changed local Gaussian provider with smaller ambient dimension and an explicit paid profile. It does not claim that its coded negative terminal has become an independent profitable Gaussian output.

## Sources and exact interface

The source `research/odd-e8-whole-k-native/PROOF.md` describes the whole-K geometry, actual native source/reader paths and real normalizers; the retained central-Q package reproduces those source statements. The retained `research/odd-e8-lowrank-e-native/E-PROOF.md` describes the ordinary mode recodings, the owner identity KC=−C, and the paid modal query. The retained `research/central-q-decoder/PROOF.md` and `E-COMPOSITION.md` give a complete paid terminal repair and its invoice. Credit THU New Media Research Center/PR5464, Ali Romman/PR5439, Dugongue, Dillon Amburgey, Cinna Davis, Ryanson Jonathan, Cao Yifan, Jacob Alan Sussman, Chris R/Clear1nsight, zxv and the native/Clifford/compiler/analytic lineage.

The local TI/symplectic proof tree was inspected for its distinction between preserving a tensor's actual support and merely preserving pairwise contractions: `Mathproof/SymplecticTI.lean`, `Mathproof/LibraryBridges/Claude/TISpTransporterFibers.lean`, and `Mathproof/SymplecticTITOCIBalancedCoevaluation20260901.lean`. The compression below uses an injective isometry of a degenerate binary support, not an algorithm for tensor isomorphism and not an assertion that pairwise Gram equality alone preserves that support. The finite-form and Clifford tools are classical. The contribution here is their concrete provider reconstruction with its true changed outputs.

All binary spaces below are over F₂. Write I_n for F₂^n with its usual dot product. Its characteristic vector is χ_n=(1,...,1), characterized by x·χ_n=x·x for every x. The complex Gaussian on a coordinate is C=((1+i)I+(1−i)X)/2. In a native block of ambient dimension n, R_n is the complete n-axis Gaussian, Q the first-axis Gaussian and D_n=R_n Q^(−1).

## K1. The product cube has a small faithful support

**Theorem.** Suppose one base eight-port cube has two four-port classes. Their spans have dimension three and Gram rank one, the two spans are orthogonal, and their intersection is their common two-dimensional radical. For an odd integer m, form the m-fold product cube and split its 8^m labels by total selector parity. Then each class spans a 3m-dimensional Gram-rank-one space; the two spaces are orthogonal and intersect in a common radical of dimension 3m−1. Their joint span has dimension 3m+1 and Gram rank two.

**Proof.** In a base cube let the two spans be U,V and their intersection R. The source geometry gives dim R=2. Orthogonality implies R is contained in the radical of each three-space, hence equals each radical. Choose norm-one vectors u in U and v in V. They are orthogonal and

    U=<u> direct_sum R,    V=<v> direct_sum R.

The four distinct labels in a class are exactly its affine coset u+R or v+R, since each coset has four elements. Across m factors put R_all equal to the direct sum of the m two-dimensional radicals and w_j=u_j+v_j. A product label has the form

    u_1+...+u_m + sum_j σ_j w_j + r,

with r in R_all. Two such labels of total selector parities ε and δ have dot product 1+ε+δ: in each factor their contribution is one for equal selector classes and zero for opposite classes, and m is odd. Thus equal-parity labels pair to one and opposite-parity labels pair to zero.

Within a parity class the differences span R_all together with all even sums of the independent w_j. This has dimension 2m+(m−1)=3m−1. Adjoining one norm-one label gives dimension 3m and rank one. The two classes have that common difference space as their intersection; adjoining a label from the other class adds one dimension and one independent norm-one quotient direction. Their joint dimension is 3m+1 and rank two. ∎

For m=3 the dimensions are 9,9 and 10, with radical dimension 8. The base common-radical hypothesis can also be recovered from the retained three-factor support statement: a base affine-difference space has dimension at least three, since it contains the two-dimensional class radical and one interclass difference. The full three-factor affine-product span has dimension one plus the sum of those difference-space dimensions. The retained dimension ten forces each to have dimension three. Therefore the two class radicals coincide and have dimension two. This proves the support structure used here instead of treating the global 25-dimensional realization as a minimal one.

## K2. An explicit faithful embedding into an even ambient space

**Theorem.** A binary space S with an orthogonal decomposition

    S=<u,v> direct_sum R,
    u·u=v·v=1, u·v=0, dim R=r,

where R is its radical, embeds injectively and isometrically into I_(2r+2). Its norm-one labels are not the ambient characteristic vector. For the product cube of K1 this gives ambient dimension 6m; at m=3 it gives I_18.

**Proof.** Map u to e_1, v to e_2, and a basis r_1,...,r_r of R to

    e_3+e_4, e_5+e_6, ..., e_(2r+1)+e_(2r+2).

These images are linearly independent. They have exactly the required pairings: the first two vectors have Gram I₂, every paired sum has norm zero, and all pairings between distinct displayed generators vanish. The linear map is therefore an injective isometry. The ambient characteristic vector has norm 2r+2=0 in F₂, while every port label has norm one, so no port equals it. Apply r=3m−1 from K1. ∎

The absence of a norm-one ambient characteristic vector is helpful here, not an obstruction. The native source requires its port labels to be norm one and different from χ_n; it does not require the distinguished central coordinate to equal χ_n. Adding one extra coordinate gives the conservative odd ambient 6m+1, but that addition is unnecessary for this reconstruction.

The embedding is faithful on the whole degenerate span. Simply identifying every label of a parity class would preserve its pairwise Gram values but collapse its radical and change the physical code more drastically; K2 does not make that identification.

## K3. Dimension-free canonical frames and their complete paths

**Theorem.** In ambient I_n, the source's canonical-frame construction works for every subspace S, including a degenerate one. Its image of the computational Z Lagrangian is

    L_S={(x,z): x belongs to S and z+x belongs to S-perp}.

For S contained in T, the Gaussian rank of the transition is dim T−dim S. Consequently, if a source parity class has dimension k and an opposite reader label q is norm one and orthogonal to that class, the four source/reader paths have ranks

    k−1, k, n−1−k, n−k.                            (1)

**Proof.** Choose any full binary basis G whose first dim S columns span S, write A=G^(−1), and use the source's computational monomial K_G=D_J P_G with J=I+A^T A. The frame is K_G C_[0,dim S) K_G^(−1). Its symplectic image is the displayed L_S by the direct calculation in the source: the X component lies in S and adding it to the Z component is orthogonal to S. This calculation has no condition that n be odd or that the restriction of the dot product to S be nondegenerate.

If S is contained in T, a vector in L_S intersect L_T has x in S and z+x in T-perp. Thus the intersection dimension is dim S+n−dim T. The Gaussian rank is n minus that dimension, giving dim T−dim S. A full flag extending S inside T gives the literal partial-Gaussian implementation, with computational monomial chart normalizers.

For (1), the source line has dimension one and is contained in the k-dimensional common class, giving k−1. The reader starts at ground and reaches that common class with rank k. Since q is orthogonal to the class, q-perp of dimension n−1 contains it, giving n−1−k for the reader exit. The source exits to the full n-space with rank n−k. These are the four actually executed Gaussian children, not a rank of a scalar coupling matrix substituted for a child. ∎

For n=6m and k=3m, (1) becomes

    3m−1, 3m, 3m−1, 3m.

At m=3 it is 8,9,8,9. The original ambient-25 construction instead has 8,9,15,16.

## K4. The ordinary wrappers and their absolute phases survive

**Theorem.** For every norm-one noncharacteristic port q in I_n there is an explicitly constructed real signed monomial L_q sending the central line to the q line and commuting exactly with R_n. Therefore the native line-service input and reader-output wrappers of the source can be constructed in ambient 6m, with no extra unpriced Gaussian child. The all-width statement includes absolute phase.

**Proof.** An even-vector orthogonal transvection is T_w(x)=x+(x·w)w, with w·w=0. If the central coordinate of q is zero, T_(e_0+q) sends e_0 to q. If it is one, either q=e_0 or choose j>0 with q_j=0, possible because q is not characteristic; then T_(e_j+q) T_(e_0+e_j) sends e_0 to q. This gives a binary orthogonal matrix G_q.

For row j of G_q put z_j=(wt(row_j)−1)/2 modulo two and let L_q=Z_z P_Gq. Orthogonality implies the finite weight identity

    wt(G_q^(−1)x)−wt(x)=2 z·x modulo four.

Indeed quadratic cross terms cancel, leaving precisely the displayed linear coefficients. Hence the real signed monomial L_q commutes with R_n exactly, by substituting the coefficients of the tensor Gaussian on each basis label.

The literal source wrappers are Φ_[q] L_q Q^(−1) on the source input, L_q on the reader input, L_q^(−1) on the source output, and D_n L_q^(−1) Φ_(q-perp)^(−1) on the reader output. Their computational monomiality follows from their identical computational Lagrangian images. No scalar phase is discarded: the source's dimension-free anchor is

    R_n^(−1)|0> = ((1−i)/2)^n sum_x i^(wt(x)) |x>,
    R_n K_G R_n^(−1)|0> = (−i)^(wt(d)) |d>,

with d_j=floor(wt(G^(−1)e_j)/2) modulo two. The same finite weight calculation proves that anchor for every n. It determines the phase of each full monomial word, and the remaining line/hyperplane wrappers use the source's two-one-axis low-rank defining expressions.

Finally tensor the one-copy operator identities over f positive digit columns. Scalar owner coefficients occur once per field; monomial phases sum over columns and the fixed scalar phase is raised to f. No tensor power of a sum is asserted. This proves the all-width endpoint with absolute phase. ∎

The claim is a mathematical construction of the wrappers. No new source file, program replay or formal proof check is being claimed.

## K5. A compressed complete local whole-K service

**Theorem.** For each odd m, let K_owner be a real symmetric involution on the 8^m owners whose nonzero entries join opposite total-selector parity classes. Use the faithful K2 geometry and K4 wrappers. Then the actual arbitrary-input two-bank endpoint is

    F_K = diag(D_n,D_n) L(C_K Q^(−1)),
    (C_K)_ij=(K_owner)_ij L_i^(−1)L_j,
    n=6m,

with no independent helper input and with paid profile, per owner,

    2 H_(3m−1) + 2 H_(3m).

C_K is a real symmetric involution and commutes R_n.

**Proof.** At the common parity-class frame, execute the ordinary scalar ADDs Y_i +=(K_owner)_ij X_j for all nonzero coefficients. Opposite classes have identical required contact frames by K3. Every source is read before its value is changed; every reader retains its arbitrary old value. The geometric endpoint is the same source/reader formula as in the retained proof, now in ambient n.

After the K4 wrappers the source output is D_n x_i because L_i commutes R_n. The reader output is

    D_n y_i + sum_j (K_owner)_ij D_n L_i^(−1)L_j Q^(−1)x_j,

which is exactly the claimed triangular map. It is invertible on arbitrary independent x,y. K3 supplies the four paid paths. Writing L=diag(L_i), one has C_K=L^(−1)(K_owner tensor I)L, so its square, symmetry and commutation with common R_n follow from the stated real orthogonality and K_owner identities. No paid query input is credited as an independent helper output. ∎

The actual odd-majority owner code has the required parity support. To see this generally, define K_owner as the odd-majority function of m commuting symmetric involutions K_1,...,K_m. Its eigenvalues are ±1, so it is a symmetric involution. Replacing all K_j by −K_j changes the majority sign, so its multilinear Fourier expansion contains only odd products. Each K_j flips one selector parity; every odd product therefore flips total parity. This supplies the hypothesis. At m=3 it is precisely (K_1+K_2+K_3−K_1K_2K_3)/2 from the source.

For m=3 every new product-cube word thus has paid profile

    {8:2v_cube, 9:2v_cube},    v_cube=512,

rather than {8:v_cube,9:v_cube,15:v_cube,16:v_cube}. This is a changed local service: D_n has rank 17 rather than 24, and its physical C_K depends on the new normalizers. It is not the old rank-24 endpoint implemented for the smaller price.

## K6. Cross-cube ordinary modes can be rebuilt consistently

**Theorem.** All product cubes can be reconstructed in one common I_18 for m=3, while retaining separate independent owner fields. Let K_owner be their block-diagonal scalar code and let C_owner be the retained ordinary owner matrix with K_owner C_owner=−C_owner and spectrum {0,98,−1078}. Put

    C_new=L^(−1)(C_owner tensor I)L,
    E_new=C_K (I−C_new)^(−1).

Then all algebraic and modal-query steps of the source E adapter remain valid on this newly constructed physical service. Each corrected orientation has paid profile

    {8:2v, 9:2v, 18:h},
    v=112^3, h=20480.

**Proof.** Cubes act on disjoint owners, so their labels may be separately embedded by K2 into the same address ambient. No two independent payloads are identified even if some newly assigned labels coincide across cubes. Each L_i commutes the same R_18. Consequently C_new, C_K and E_new commute R_18, and their scalar similarity preserves all owner spectral and inverse identities.

Acquire the nonzero C_owner modal coordinates after the ordinary L_i normalizations; apply one R_18 to each of the h actual acquired modes; scatter by the prescribed eigenvalues; undo the ordinary mode and L_i changes. This is exactly R_18 C_new applied to the original source bank. The modes are obtained from actual original inputs and are not productive helpers. The source E algebra then corrects the local shear coefficient and gives the stated forward/backward forms. The inverse-contact construction and linear transposition use the same literal source/reader incidence from K5, so their all-input endpoint and paid rank profile are unchanged by replacing the ambient dimension and actual normalizers consistently.

The K5 children give two copies each of ranks 8 and 9 per owner. Each modal query is now rank 18 and there are h of them. This proves the profile. ∎

The cross-cube owner matrix need not preserve the original geometric pairings between cubes. It is an ordinary scalar recoding, and the argument uses its new physical similarity explicitly. This is why the result is valid as a newly constructed provider and why it is not a free coordinate compression of the pinned 25-axis E operator. Claiming the latter would require a common spectator and a conjugacy preserving the old central-Q itinerary, which is not supplied here.

## K7. Complete three-stage outputs and their honest invoice

**Theorem.** Use three fresh 17-axis blocks with one common central Q, and the K6 corrected E modules. Let P=E_3 E_2^(−1)E_1. The actual two terminal operators, after the ordinary signed role swap, are

    Q^(−1) P D_123,       P D_123 Q.

The ordinary inverse P^(−1) closes the positive terminal. A complete negative repair by Q, P^(−1), Q gives independent rank-52 Gaussian outputs on both banks, with exact paid profile

    targets: 2v H_52,
    paid: 3v(2 H_8+2 H_9) + 3h H_18 + 2v H_1.       (2)

**Proof.** The source three-stage operator derivation uses only the actual corrected E interfaces, commutation with each stage's R=DQ, and identity action on other fresh blocks. Those conditions hold in K6, so its chronological product gives exactly the displayed terminals. Applying Q to the negative terminal gives P D_123; applying the ordinary reversed inverse word gives D_123; applying Q gives D_123 Q. The positive terminal needs only P^(−1). Since there are three fresh rank-17 blocks and one central line, both final Gaussian ranks are 3·17+1=52.

There are three corrected local calls, each with the K6 profile, and two additional central queries on the negative bank. All other inverse recodings are ordinary, with their finite coefficients, owned storage and error amplification still charged. This proves every term of (2). ∎

Its rank-mass surplus is −54h: the target mass is 104v, the native local mass is 102v, and the two central repairs add 2v, leaving the modal 54h. Moreover this particular complete recipe has negative target-minus-paid concave moment for every 0<t≤1. Each paid rank is at most 18<52, so r^t≥52^(t−1)r for each paid rank; hence its paid moment exceeds 52^(t−1)104v, which is exactly the target moment. This is a comparison for the explicitly supplied repair, not an impossibility theorem for other consumers or decoders.

The new code and smaller mode-query rank therefore do not alone establish a stronger κ. The mathematical result is the positive reconstructed local service and its complete paid closure, with no invented independent-output credit.

## K8. Which improvement is actually proved

For every t>0 the compressed corrected local paid moment is strictly smaller than the old one:

    v[(15^t−8^t)+(16^t−9^t)] + h(25^t−18^t) > 0.

This is immediate from strict increase of x^t. The endpoint ambient and physical code have also changed, so this local inequality cannot be substituted into an old whole-provider invoice with its rank-24 or rank-73 targets untouched. K7 rebuilds the corresponding new invoice exactly.

The actionable provider direction is now sharper: construct a cheaper complete consumer for the new 18-axis E code, or exploit its retained radical/owner structure to close a different independent-output word. The conditional screen that simply grants both negative and positive rank-52 outputs is not a theorem. Neither Gram compression, total symmetry nor nonzero support supplies that missing decoder by itself.

All matrices, modes, phases and storage discussed here have explicit mathematical definitions. The note supplies no new numerical κ, native executable, formal-kernel acceptance or claim of historical priority. Its useful sufficient construction is a full local K/E provider reconstruction and paid all-input completion at the new dimension.


