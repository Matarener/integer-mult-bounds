# Pointwise standalone history bound with arbitrary exterior scalars

Status: **PROPOSED SCOPED POINTWISE EXTENSION; STOP FOR INDEPENDENT STATIC REVIEW.**

For a fixed finite ordinary one-column group G, put p=|PG|, its number of actual projective matrix classes. The proposed result is that the source-bound natural canonical converter needs at least 120 new paid whole-field returns **at each width f>=2p-1**, even when exterior coefficients, the ordinary instruction sequence, its finite length, and the finite number of independent dirty inputs vary arbitrarily with f. The ordinary operators must remain columnwise lifts from this one fixed G. The target operators and one-column field geometry remain fixed.

This is a pointwise history-dimension application of classical tensor-power independence. It does not duplicate PR5436's four-control/support corollary, classify its 2705 source count, or claim a new tensor-separation theorem. It does not extend the actual parent cut's available paid-history contract. All earlier standalone and central-Laurent artifacts remain unchanged.

## 1. Fixed geometry and pointwise program contract

Let K=Q(i), let V be a nonzero finite-dimensional K-vector space, and let G be a fixed finite subgroup of GL(V,K). Let

```
Z = G intersect {lambda I : lambda in K, lambda != 0},
PG = G/Z,                 p = |PG|.
```

Equivalently, p is the number of equivalence classes under g~g' if g=lambda g' for some nonzero lambda in K. Z is central. In the source's permitted enlargement, G is the finite group of computational-basis monomial matrices with fourth-root entries. This is a group of actual matrices, not formal word labels. A fixed-width field is U_f=V^(tensor f), up to the declared common layout conjugation.

At any particular f, allow an arbitrary finite exact linear straight-line program with these resources:

* Ordinary address operators g^(tensor f), g in G; arbitrary exterior coefficients c(f) in K; whole-field ADD, COPY and CLEAR. The coefficients and gate choices can depend arbitrarily on f, but not on input values. There is no uniform bound on the finite ordinary word length.
* N=N(f) arbitrary independent initial current fields, including any finite number of independent dirty inputs. Fixed-width initial ordinary combinations and zero scratch are allowed. Correlated nonordinary observations from earlier paid work are excluded from this standalone initial history.
* Paid calls on one actual current field, each returning one new K-linear transformed whole-field row at the same capacity. Their inputs may use earlier responses. The history proof needs neither commutation with ordinary operators nor a uniform choice of the paid operators across widths. In the source application these are the allowed positive-rank Gaussian calls. A preserved old input is not a second new paid return.

The fixed target has q distinct current-input coordinates v_i and invertible one-column maps h_i satisfying

```
h_i notin K^times G = {lambda g : lambda != 0, g in G}.
```

The program must supply the q rows h_i^(tensor f) w_vi, possibly with an ordinary initial background added. It must be correct on the full independent current-input space at the particular width under consideration. Different h_i need not occupy different projective G cosets. The same target input coordinate cannot be counted twice.

**Proposed theorem:** For every integer f>=2p-1, any such exact program uses m(f)>=q paid returns. Thus q=120 gives the desired eventual pointwise standalone bound. The theorem is about each eligible width separately; it requires neither a common word across widths nor exactness on consecutive widths. It asserts no bound for an arbitrary smaller width.

## 2. Classical separation lemma, with a direct proof of the needed cutoff

Let a_1,...,a_s be nonzero vectors in a finite-dimensional K-space E, no two proportional. For each index j and each l!=j, there is a K-linear form ell_(j,l) with

```
ell_(j,l)(a_l)=0,             ell_(j,l)(a_j)!=0.
```

Such a form exists because a_j and a_l are linearly independent. Choose also a linear form eta_j with eta_j(a_j)!=0. For f>=s-1, apply the tensor functional consisting of the s-1 forms ell_(j,l), followed by f-(s-1) copies of eta_j, to a_k^(tensor f). Its value is zero if k!=j and nonzero if k=j. Applying these functionals to any proposed linear relation proves that

```
a_1^(tensor f),...,a_s^(tensor f) are linearly independent for f>=s-1.
```

For s=1 the claim follows directly from nonzeroness at every positive width. In the application below s=2p>=2, so f>=2p-1 is positive. Tensor factors of these functionals need not be equal; their evaluation on a pure power is just the product of scalar evaluations. No numerical rank calculation, norm bound, or all-width constant-coefficient inference is used.

This conservative cutoff is a standard consequence of multi-copy/projective tensor independence. Anthony Chefles, *Unambiguous Discrimination Between Linearly Dependent States With Multiple Copies*, Physical Review A 64, 062305 (2001), DOI [10.1103/PhysRevA.64.062305](https://doi.org/10.1103/PhysRevA.64.062305), Section II, Eq. (2.3), gives the stronger rank-refined complex-state sufficient condition C>=N-D+1 for N distinct rays spanning dimension D. The sole literature worker inspected that theorem, its proof and the appendix lemma in [quant-ph/0105016v3](https://arxiv.org/abs/quant-ph/0105016). The elementary K-linear argument above proves exactly the weaker cutoff used here, without computing any source span rank or presenting the paper as a generic-field theorem. Its classical attribution is retained.

## 3. Projective phases and the actual ordinary algebra

Fix f>=2p-1 and choose one representative g_1,...,g_p of PG. A group element g=lambda g_j has lift

```
g^(tensor f)=lambda^f g_j^(tensor f).
```

At this fixed f, lambda^f is an ordinary scalar in K. Thus scalar phases are merged with their exact lifted factors. In particular iI contributes i^f I and is not counted as an additional independent direction. The formal group-algebra dimension |G| from the earlier all-width proof is deliberately not used here.

Define the actual matrix algebra

```
R_f = span_K {g^(tensor f) : g in G} subset End_K(U_f).
```

It contains I and is closed under multiplication because G is a group and tensor lifts preserve composition. Any number of ordinary operations at this width remains in this algebra. The p chosen lifts span it. They are linearly independent once f>=p-1, by Section 2; our chosen threshold is at least that large. Therefore

```
dim_K R_f = p.
```

This is an image algebra, not an assertion that it is the untwisted group algebra K[PG]. Multiplication among chosen representatives may carry width-dependent scalar phase factors. Their exact coefficients do not affect the dimension conclusion.

For a target h_i, right multiplication by its inverse shows that G h_i has exactly p projective classes. No class of G h_i meets a class of G: an equality g h_i=lambda g' would imply h_i=lambda g^-1 g' in K^times G. Consequently the combined set G union G h_i has exactly 2p projectively distinct representatives.

Identify End_K(V)^(tensor f) with End_K(U_f). Section 2 applied to these 2p representatives gives linear independence at the single width f>=2p-1. With H_i=h_i^(tensor f), it follows that

```
R_f intersect R_f H_i = {0}.                         (SEPARATION)
```

Right multiplication by the invertible H_i is a K-linear isomorphism on the matrix space, so dim_K(R_f H_i)=p. This cancels a genuine invertible matrix, not an arbitrary nonzero ordinary algebra element. R_f may contain zero divisors.

The same cutoff works for all q target owners. It is not multiplied by q: each separation is between G and one G h_i, while different owner coordinates will supply the other direct-sum separation. No independence across all combined target cosets is required.

## 4. Actual paid history at this width

Represent each current field as a row in End_K(U_f)^N acting on the N independent current inputs. This representation and the target row equations are valid because correctness holds on the full input space at this width. Put

```
I_f = R_f e_1 + ... + R_f e_N = R_f^N.
```

Retain conceptually every initial row and each actual paid output row t_j, even after physical overwrite or CLEAR. After m calls set

```
M_m = I_f + R_f t_1 + ... + R_f t_m.
```

Ordinary operations preserve this span, regardless of their number or arbitrary fixed-width coefficients. A paid call applies its actual K-linear operator to its actual current input and creates one new row, which is then adjoined. It is not assumed to be R_f-linear and is not allowed to transform all prior ordinary combinations for one charge. The paid operators need not themselves belong to a fixed finite matrix group for this history argument.

Each cyclic contribution R_f t_j is the image of the p-dimensional K-space R_f. Therefore

```
dim_K M_m <= (N+m)p.                                  (UPPER)
```

Every target H_i e_vi lies in M_m after subtraction of its ordinary initial background. Define W_i=R_f H_i e_vi. Each W_i has dimension p by target invertibility. Equation (SEPARATION) makes its intersection with I_f zero in coordinate vi; the distinct coordinates make the W_i mutually independent. Hence

```
I_f + sum_i W_i = I_f direct-sum W_1 direct-sum ... direct-sum W_q,
dim_K M_m >= (N+q)p.                                  (LOWER)
```

Since p is finite and positive, UPPER and LOWER imply m>=q. This argument applies independently for each f>=2p-1. A finite N(f) that grows with f cancels at each width; known-zero scratch contributes no independent input row. No localization, formal group-algebra faithfulness, common coefficient sequence, uniform program length or uniform paid-history support bound is used.

## 5. Source application and exact scope of the advance

The sealed canonical-conversion report `../REPORT.md`, SHA256 `6dc97b31c69d7ca4ff49f649fc55d85c1e01e46cdbf7923f880811220f2e80d9`, supplies the natural T=A Jbar A^-1 output map, 120 independent full-current-input v coordinates, and invertible nonmonomial target blocks h_i. Its source equation Phi581=L2(QJQ^-1)Q²R1 gives four nonzero entries per row for the central factor; the specified factorwise lift and monomial aliases preserve nonmonomial support. These are retained source/ownership/surjectivity premises, not freshly executed classifications.

Every element of K^times G is monomial, so the source h_i satisfy the strengthened target exclusion. The 625 binary-axis grid is fixed per column, with amplitude dimension 2^625. The child and matcher overlap on their actual canonical U row; no disjoint-factor commutation is introduced. A common prescribed layout conjugation does not change matrix independence or the history dimensions.

It follows that, subject to those retained premises and the stated ordinary group, every exact standalone implementation at f>=2|PG|-1 needs at least 120 new paid returns, even with arbitrary exterior c(f), width-dependent ordinary gate choices and finite word lengths, and finite N(f). This closes those particular uniformity exceptions **eventually in width**, while keeping the same finite one-column ordinary group and full input interface.

The threshold is explicit and finite, but may be enormous. No practical-width cutoff or source-optimal threshold is asserted. For the conservative all-monomial enlargement on a d-dimensional one-column space, |G|=4^d d! and p=4^(d-1)d!, with d=2^625 here; this is a symbolic finiteness bound, not a numerical computation or proposed census. A smaller known finite ordinary subgroup could give a smaller sufficient cutoff. No subgroup/class/rank search was performed.

For positive-rank Gaussian calls, the count again supplies a charge of at least 120 at every eligible width in any 0<t<1 rank moment. If the original basic P and conditional target T are held fixed, its earlier analytic inequality T_t-P_t-120<0 therefore remains an eventual per-width necessary obstruction. This does not claim that an arbitrary nonuniform family already has a valid recursive cost theorem or a single fixed invoice. No powers, price, funding or κ calculation is performed.

## 6. Boundary checks and what is not proved

* **Projectively ordinary targets:** if h=lambda g, its target is the ordinary operation lambda^f g^(tensor f). Zero paid calls suffice. Merely h outside G is not an adequate target condition.
* **Small widths:** take G={I,X} on K^2 and Q=((1+i)I+(1-i)X)/2. At f=1, Q is an ordinary linear combination of I and X, although Q is invertible and nonmonomial. It needs no Gaussian call under this ordinary-span model. The proposed result only applies above its sufficient threshold and does not misstate a pointwise all-width bound.
* **Changing ordinary algebra:** allowing arbitrary cross-column ordinary maps on U_f can make their span all of End_K(U_f). For example all signed permutations of the full width-f basis span every matrix unit, using diagonal sign projectors and permutations. Then targets can be ordinary and the conclusion fails. These are not lifts of one fixed finite one-column G. A growing projective ordinary alphabet likewise needs its own separation/dimension proof; it is not covered by this fixed-G result.
* **Existing paid observations:** if h_i^(tensor f) w_vi are supplied as correctly versioned initial rows, the extra-call count can be zero. Source-input surjectivity alone does not remove that history. The theorem is not an incremental bound at the actual parent cut and cannot be added independently across shared conversions.
* **Other interfaces:** dependent current fields, nonunit or partial-field targets, changing field capacity, several independent new outputs per paid call, data-dependent nonlinear programs, and approximation require separate analysis. Exact independence alone is not a conditioning or precision bound. New genuine productive outputs also change the fixed profile comparison.

The finite-G assumption is the decisive remaining ordinary-language restriction. Unbounded ordinary word length is harmless here only because arbitrary products still belong to G and arbitrary sums still belong to its fixed-width image algebra. This is different from PR5436's moving-support four-control theorem, whose operators may range more broadly under a separate expanded-support bound. Neither result is claimed as an automatic application of the other source-specific corollary.

## 7. Review request, provenance and stop

The smallest required review checks the tensor separating functionals, the 2p projective-class count and exact phase merging, the closure and dimension of actual R_f, the unit-based target separation, and the actual-row history argument with nonuniform m(f),N(f). It should reject any transfer that lets G or its one-column geometry grow silently. This package stops at that written review gate; no source/rank/checker or scientific execution is requested.

The prompt for this question was the cached PR5436 body at author head `4c31fd7d4eee61ff9fd59533549a67ef1a25b449`, `outputs/upstream-monitor-resume-20261024/pr5436at1333.json`. Only that cached body was read here; its author proofs, finite controls, 2705 count and execution claims were not replayed or independently adopted. Classical tensor independence is credited to Chefles and retained tensor-separation predecessors. Root proposed this separate paid-history dimension application; the sole literature worker supplied the exact primary theorem fit. Credit for the canonical-conversion source and earlier history arguments remains as listed in the sealed reports, including the BC/native/Clifford/product/compiler/precision/analytic authors. Substantial OpenAI Codex assistance; no new classical theorem, selected frontier, physical construction or κ is claimed.
