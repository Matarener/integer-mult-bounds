# Borrowed rank-one adapters and exact cost guarantees

Work over dyadic rationals with the retained native ADD allowance A(q), omitting zero coefficients. All source roles X_i and destination roles Y_j are distinct, disjoint, and expressed in the same chart. Other fields can contain arbitrary dirty data. No scalar operation is moved across a query or chart change.

## Theorem 1: source-pivot conjugation

Suppose M=u vᵀ and a coefficient pivot v_p is nonzero, with each ratio c_i=v_i/v_p dyadic. Set d_j=u_j v_p. Then the following native program implements X ↦ X, Y ↦ Y+MX:

1. For i ≠ p with c_i ≠ 0, execute X_p ← X_p + c_i X_i.
2. For each nonzero d_j, execute Y_j ← Y_j + d_j X_p.
3. Reverse the first sequence with the negated coefficients.

Proof. After preparation, X_p equals (Σ_i v_i X_i)/v_p; every other source remains unchanged. Thus the middle sequence adds u_j Σ_i v_i X_i to Y_j. Its reads do not alter any source. Reversing preparation recovers the original X_p exactly, because the other source fields are unchanged. No temporary is allocated or cleared; no value of X_p is assumed clean, nonzero or known. Division occurs only in fixed coefficient preparation, never on runtime data. Exterior fields are untouched. ∎

The complete scalar allowance is

B_source = 2 Σ_(i≠p) A(v_i/v_p) + Σ_j A(u_j v_p).

Both preparation and its inverse are included, since A(−q)=A(q).

## Theorem 2: dirty-target conjugation

Suppose M=u vᵀ, u_p ≠ 0 and every c_j=u_j/u_p is dyadic. Set d_i=u_p v_i. For each j ≠ p subtract c_j Y_p from Y_j; next add Σ_i d_i X_i to Y_p using scalar ADDs; finally add c_j Y_p back to each other destination.

This program also implements X ↦ X, Y ↦ Y+MX with no extra field. Its allowance is

B_target = 2 Σ_(j≠p) A(u_j/u_p) + Σ_i A(u_p v_i).

Proof. Write s=Σ_i d_i X_i and let y denote the initial destination values. During the middle stage Y_p changes from y_p to y_p+s. Each other output becomes y_j−c_j y_p+c_j(y_p+s)=y_j+c_j s. The pivot output is y_p+s. These are precisely Y+MX, and no source is modified. In particular the subtraction cancels the arbitrary dirty initial y_p; omitting it would introduce unwanted cross-output terms. ∎

Source borrowing for M and target borrowing for −Mᵀ are the transpose-dual constructions. Their scalar allowances agree because transposition exchanges the two coefficient lists and sign does not change A. The verifier nevertheless derives and checks both actual native source orientations independently.

## Corollary 3: a strict sufficient saving over an owned sum

Normalize a source factor so v_p=1, with dyadic u,v. The owned-field program of #4489/#4494/#4499 clears T, accumulates Σ_i v_i X_i, reads u_j T into every output, and clears T again. It costs

O = 4 + A(1) + Σ_(i≠p) A(v_i) + Σ_j A(u_j).

Since A(1)=8, Theorem 1 gives O−B_source = 12−Σ_(i≠p) A(v_i). Therefore Σ_(i≠p) A(v_i) < 12 is a sufficient strict-saving condition; equality gives a tie. This is a quantitative sufficient result, not merely a necessary-condition test.

For v=(1,1), u=(−1,1,−1/2), the owned bill is 4+8+8+8+8+10=46. The borrowed bill is 8+8+8+8+10=42. The original six-entry direct block costs 52. The emitted forward program is

```text
X0 += X1
Y0 -= X0
Y1 += X0
Y2 -= X0/2
X0 -= X1
```

Every input is restored. Both pinned repeated-input blocks have exactly this matrix. Their dual matrices use Theorem 2 at cost 42. ∎

## Compiler correctness and scope

The implementation computes normalized coefficients from a proposed nonzero matrix entry, rejects any odd denominator, checks every entry of M equals the proposed outer product, and emits only proven legal pivots. It enumerates all source and target pivots admitted by these rules. If none is cheaper, it uses #4499's exact zero-scratch gauge program, whose retained proof is GAUGE-PROOF.md. This fallback is sufficient for every dyadic matrix, including zero maps. No claim that every dyadic rank-one matrix has a legal normalized source or target pivot is needed: for example, [[9,15],[15,25]] has neither.

Selection between valid candidates preserves the exact persistent map. The four actual source windows are disjoint and contain contiguous common-frame scalar ADDs, so replacing them preserves the local interfaces and original 632-field ABI. The verifier authenticates source bytes and selectors, prices every emitted instruction with the source primitive_allowance, checks all independent local data columns, and requires every selected instruction to name only original X/Y fields. The combined scalar allowance is 358+42+42+224=666 in each orientation.

This proves local exact replacements and their scalar bills. Finite program checks are not a full multiplication theorem: rebuilt stock/norm/coefficient, numerical precision and complete global-bound obligations remain. No new recursive calls, productive-helper credit, full supplier or new κ is established.
