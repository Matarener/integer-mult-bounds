# The actual odd-E8 negative terminal has no constant-size ordinary decoder

This is an application of the attributed fresh-stage path-separation and coordinate-contraction proof retained in `source/separation-proof.md` (Ali Romman, PR4933/5065 lineage), with a new nonzero-path certificate for the actual nonfitting E code of PR5464. The old A polynomial and proper-K terminal support cap are not premises. No new general separation theorem is claimed.

## Exact target and source

At immutable56ba6d7d609124d71c067d6a380caed573963f8f, the source has v=112^3 owners and three24-private-axis stages sharing one central binary axis. Let Q=C0, D123 the three fresh positive Gaussian products, and B=E3 E2^-1 E1. The emitted negative endpoint is Q^-1 B D123. Its specified target is Q^-1 D123 on the same original independent inputs. Since both maps are invertible, the unique postdecoder is J=Q^-1 B^-1 Q=Q^-1 E1^-1 E2 E3^-1 Q. This statement observes only the emitted negative bank plus independent workspace; no correlated original-input histories or other unpaid observations are granted. Independent extra inputs cannot change the required restriction to this bank.

Each stage E is physically L^-1 A L with owner-block diagonal signed monomials L_i and scalar A=K(I-C)^-1. Only the address monomials tensor-power with field width f; scalar owner coefficients are applied once. The source has C spectrum0,98,-1078, KC=-C, and K^2=I. Therefore E^-1 in normalized owner coordinates is K+C. This uses the actual20480-mode nonfitting E construction, not the earlier proper-K code.

## Actual nonzero path

Put j=(0,0,0), i=(1,0,0). Source root rows are M0=(1,1,1,1,0,0,0,0), M1=(1,1,0,0,1,1,0,0). Their supports belong to different cubes and their dot product is2. Let P=MM^T/4, so P00=P11=1 and P10=1/2. The scalar source code is C=(P1P2+P1P3+P2P3-P1P2P3)/2. For i,j above its entry is P10/2=1/4. The block-diagonal K has zero entry between these different cubes, hence (E^-1)_ij=1/4. Every diagonal entry of K is0, so (E^-1)_jj=C_jj=1.

The projector onto the8-dimensional active base space is MM^T/56; every diagonal entry equals1/14. For the three selector axes, the diagonal mass on exactly-two-active sectors is39/2744, and on the all-active sector1/2744. Since E=K-C(I-C)^-1 and K_jj=0,
 E_jj=39*98/(2744*97)+1078/(2744*1079)=1541/104663.
Thus the path j→j→j→i in E1^-1 E2 E3^-1 has coefficient1541/418652, nonzero. All matrices and coefficients here are exact rational source data. There is no inference from the source's smaller lambda98 toy caller to this112^3-owner claim.

## Path separation and nonmonomial support

Let V_s be the24 private binary coordinates of stage s and E the common binary line. The linear normalizer G_s,i acts only on E+V_s and sends e0 to the distinct actual product label q_i. All product labels are distinct: concatenation of the three distinct112-label coordinates is injective, and conversion through the source orthonormal basis of U25 is injective. The source rule constructs G for every norm-one noncharacteristic q; signed phases do not identify different binary maps.

Ordered products of one local map per distinct stage factor uniquely. Moving the last factors to one side puts their quotient both in GL(E+V_last) and in the subgroup supported on E plus earlier private spaces. Their intersection is GL(E,F2), which is trivial. Peel stages successively. With fixed endpoint owners, equal complete maps therefore imply equal intermediate owners, since G_i e0=q_i distinguishes owners. This is the existing separation lemma with24 private coordinates, not a census of owner paths.

Consequently the selected nonzero path cannot cancel with another path, including after absolute phases. Its complete map reduces to L_i^-1 L_j in stage1, because the other two local factors are identity. Its binary map moves e0 since q_i differs from q_j. For M|x>=s(x)|Gx>, s(x)=+/-1, direct expansion of Q^-1 M Q has four distinct destinations Gx,Gx+Ge0,Gx+e0,Gx+Ge0+e0, each coefficient of magnitude1/2. Its inverse also moves e0, giving four entries in each row. The verifier checks the actual25-axis signed normalizers and exact sparse phase columns without constructing a2^25 dense matrix.

## Quantified ordinary-cost consequence

Use the existing private-basis contraction proof with m=72 private directions in the73-axis address space. For each private basis vector x_l set y_l=G_* x_l and ell_l(N)=(Q N Q^-1)[y_l,x_l]. Orthogonality means agreement on these72 columns forces agreement on the remaining central column. By path separation the markers isolate the selected path. For f>=72, contracting the first72 tensor factors leaves a nonzero scalar times N_*^(tensor(f-72)). Each resulting row has4^(f-72) nonzero entries.

Each marker uses at most two original output rows and two input entries. If original maximum row support is S, the contracted row support is at most2^72 S. Therefore S>=2^(2f-216). A monomial address operation, SCALE, COPY or CLEAR does not increase maximum row support; a binary ADD increases it by at most two. Any exact linear ordinary program with g ADDs therefore satisfies
 g>=max(0,2f-216).
This allows arbitrary owner mixing, arbitrary independent owned/dirty workspace and f-dependent scalar coefficients or monomial permutations. It rules out a fixed finite number of ordinary field ADDs uniformly in width. It does not rule out f-dependent scalar programs, paid Gaussian calls, correlated histories, repeated stages, changed target inventories or joint whole-caller decoders. The two-common-axis and repeated-stage controls explicitly exhibit failure of the separation premises outside scope.

## Stronger eventual nonmembership for the columnwise native alphabet

For this additional claim restrict each ordinary address operation to a tensor lift gamma^(tensor f) of a single73-bit-column monomial Clifford, as in the actual native P/D/X/phase alphabet. Owner mixing and scalar coefficients may depend on f, and there is no bound on instruction count. Products of such lifted monomials remain lifted monomials in the same finite group Gamma; sums, COPY, CLEAR and arbitrarily many independent workspace rows leave each original-input/output block in their scalar linear span.

A monomial Clifford on n bits is a binary affine permutation (at most2^(n^2+n) choices) times a diagonal phase i^(c+sum a_j x_j+2sum b_jk x_j x_k), with c,a_j in Z4 and b_jk in F2. Arbitrary scalar global phases may be absorbed into the owner coefficients, so no continuous scalar phase group is counted. For the native Z4 representatives, |Gamma|<=2^(n^2+3n+n(n-1)/2+2). At n=73 the exponent is8178. Every lifted monomial has only one nonzero entry in each row, so every block in this span has row support at most2^8178. The selected owner block of J_f has support at least2^(2f-216); the contraction argument already fixes both owner endpoints. Hence J_f lies outside the entire ordinary columnwise Clifford algebra for every f>=4198. This excludes arbitrary-length f-dependent words in that alphabet, not only a constant instruction count. Multiplication by fixed ordinary invertible owner/monomial boundaries cannot change membership.

If a broader alphabet permits arbitrary one-column permutations or arbitrary phases, but still repeats the same one-column permutation across all f columns, a weaker support-only bound remains: for d=2^73 possible one-column addresses, at most d! repeated permutations give different support maps. Phases cannot enlarge those supports. Since d!<=d^d, eventual nonmembership follows whenever2f-216>73*2^73. This broader bound does not need a finite phase set. Neither argument applies to arbitrary permutations mixing tensor columns; those retain only the ADD-count lower bound above. This distinction is essential to the claimed ordinary-algebra decision.

## Complete invoice decision and remaining costs

The unchanged three-call producer pays3v each of H8,H9,H15,H16 plus61440 H25. The positive half is already decoded. Granting a second autonomous H73 half leaves the source's conditional margin about.0438207413 per port per LOCAL at selected saving. Our result rejects treating the missing specified postdecoder as a fixed-size ordinary recoding. It additionally proves eventual nonmembership in the full columnwise native algebra, but supplies no paid-child lower bound and must not be subtracted as one from that margin.

A scalar decoder growing with f must charge every ADD, route, coefficient-generation division, owned lifetime, precision guard and visited-cell cost against the complete caller. A paid decoder must retain all original-input targets and pay its children before claiming that conditional margin. No such completion is constructed here. The producer's20480 modes, source-contact histories, scalar rational denominators and field-l2/coordinatewise precision gap remain inherited open costs. No selected-frontier change or kappa claim follows.

## Open next questions

Can an already-paid IDLE or a charged f-dependent ordinary program implement J within the complete remaining budget? Can a genuinely different target or correlated-history contract remove the required conjugated inverse? First write the complete source/caller identity and invoice; do not repeat the failed naive B^-1 postdecoder or apply the proper-K support cap to E.
