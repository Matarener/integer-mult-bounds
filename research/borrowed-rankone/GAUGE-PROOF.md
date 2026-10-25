> Retained predecessor proof from #4499. Its 686 / 674 totals and 320-column validation describe that predecessor; the current package receipt is RESULT.json, with 666 and 160 source-column checks. The general gauge construction below is retained as the fallback proof.

# Exact sufficient construction and optimality certificate

All statements concern exact dyadic linear arithmetic with the retained native primitive_allowance, not floating-point evaluation. Sources X_i and destinations Y_j are disjoint persistent fields in one common frame. Other fields may contain arbitrary dirty values.

## Lemma 1: the dyadic ADD allowance is an absolute valuation cost

Write a nonzero dyadic q uniquely as o · 2^v, where o is a signed odd integer and v is an integer. Substitution into the native price gives

A(q) = 2(2 + bit_length(|o|) + popcount(|o|)) + 2|v|.

Proof. For v ≥ 0 the denominator is 1, the numerator bit length increases by v, and popcount is unchanged by the left shift. For v < 0 the odd numerator is unchanged and the denominator bit length minus 1 is −v. These are precisely the two branches of the formula. A positive SCALE by 2^e costs 2|e|, so its scale/unscale pair costs 4|e|. ∎

## Theorem 2: arbitrary integer gauges give an exact zero-scratch replacement

For any dyadic matrix M and integer source/target exponents a_i,b_j, scale X_i by 2^a_i and Y_j by 2^b_j. For each nonzero matrix entry execute ADD from X_i to Y_j with coefficient M_ji · 2^(b_j−a_i). Unscale all fields. This maps

X ↦ X,  Y ↦ Y + MX

for arbitrary initial X,Y, preserves every exterior field, and needs no owned scratch or recursive calls. Its scalar allowance equals C + F(a,b), where

C = Σ_nonzero 2(2 + bit_length(|odd(M_ji)|) + popcount(|odd(M_ji)|)),

F(a,b) = 4 Σ_i |a_i| + 4 Σ_j |b_j| + 2 Σ_nonzero |v_ji + b_j − a_i|.

Proof. At the ADD stage each source is 2^a_i X_i and each target begins as 2^b_j Y_j. The adjusted coefficient contributes 2^b_j M_ji X_i, so unscaling yields exactly the stated persistent map. Sources are never ADD destinations. Lemma 1 charges all adjusted ADDs and both SCALE instructions for every nonzero exponent. No positivity or clean-entry assumption on the data is used. ∎

## Theorem 3: an exact signed circulation certifies a globally optimal gauge

Use an anchor node 0, source nodes and target nodes. Put an oriented edge 0 → each field with capacity c=4 and cost k=0. For each nonzero M_ji put an edge source i → target j with c=2 and k=−v_ji. A signed flow f obeys −c ≤ f ≤ c and zero divergence. Set p_0=0, p_X=a and p_Y=b.

For any such flow and any potential p, conservation implies

−Σ_e k_e f_e = Σ_e f_e(p_v−p_u−k_e) ≤ Σ_e c_e |p_v−p_u−k_e| = F(a,b).

Thus a feasible flow attaining equality proves optimality over all integer gauges (indeed over real potentials). The verifier reconstructs these edges directly from M and checks capacities, divergence and equality using integers. It does not trust the optimizer's reported objective.

Existence and termination of the included algorithm: start at f=0. For an edge f, forward residual capacity is c−f with cost k and reverse capacity is c+f with cost −k. Augment an integral bottleneck around a negative residual cycle. Each augmentation decreases integral total cost by at least 1; total cost is bounded below by −Σ c|k|, so this process terminates. Bellman–Ford with a zero-distance super-source either finds a negative cycle or returns integer shortest distances p. At termination, a forward residual edge implies p_v−p_u−k ≤ 0; a reverse residual edge implies the opposite inequality. Therefore each unsaturated edge has zero reduced potential, while a saturated edge has the sign that makes f_e(p_v−p_u−k)=c_e|p_v−p_u−k|. Summing gives equality. Normalize the anchor by subtracting its distance. All distances are integers, so Theorem 2 emits legal native powers of two. ∎

The algorithm is finite and exact; no strongly polynomial complexity claim is made. Disconnected nonzero patterns are harmless because each field has an anchor edge. Zero matrix entries are omitted, including in C and the flow graph.

## Corollary 4: dual orientation and inherited rank-one alternative

For the inverse-transpose block −Mᵀ, source gauges −b and target gauges −a preserve every absolute valuation term, and C is unchanged. Thus optimal gauge allowances agree in both orientations. The executable independently compiles and checks both authenticated source orientations.

If M=u vᵀ with dyadic u,v, the predecessor's owned-field construction clears T, accumulates Σ_i v_i X_i into T, adds u_j T to each Y_j, and clears T again. This has the same persistent map and a zero owned-field exit for arbitrary dirty entry, at allowance 4 + Σ_i A(v_i) + Σ_j A(u_j). Zero coefficients are skipped. The included implementation only accepts an exact rank-one factor with legal dyadic coefficients. It selects this alternative only if cheaper, and reuses one field between disjoint windows. This is #4489/#4494's mechanism, not a second newly invented construction here. ∎

## Source specialization and limits

The four windows are authenticated by source hashes, phase, common frame, actual native program indices, persistent ordinals and exact role sets. Each window contains only contiguous scalar ADDs with disjoint sources and destinations, so Theorem 2 applies without moving a recursive operation. The finite symbolic executor verifies every independent local data column, including arbitrary dirty owned entry, in both modes and orientations: 320 column checks in total. Scalar prices are evaluated with the actual pinned source function. This proves the local 686 and 674 bills and exact interface replacements. It does not prove a full rewritten multiplication program's coefficient/norm/stock invariants or a new κ.
