# Independent static review of the eventual pointwise scalar extension

**Decision: PASS_SCOPED_EVENTUAL_POINTWISE_HISTORY_BOUND. No mathematical correction is required.** The sealed proposed lemma, SHA256 `ac2a5a7c2e98b9dc3b19fbe0112003b37edf94dc13c0dc1411805cf52200c1e4`, proves `m(f)>=q` at every integer width **f>=2p−1**, where p is the number of projective classes of the one fixed finite ordinary one-column group G. It permits arbitrary width-dependent exterior coefficients in K=Q(i), arbitrary input-independent finite straight-line words and finite dirty-input counts at each eligible width. It does not require one uniform word or coefficient sequence across widths.

For the retained standalone canonical-conversion target, q=120 follows subject to the unchanged source, ownership, geometry and full-current-input premises. This is an eventual pointwise bound, **not a bound at all small widths**, a practical-width certificate, an incremental claim at an actual paid-history cut, or a new kappa result.

This review consists of manual mathematical reasoning and text/hash inspection. No source/checker/rank/class/tableau/native/phase/price/Powers/log/exp/solver/emitter/Lean program, scientific run, new agent or public action occurred. The proposed lemma and all earlier accepted/clarification artifacts were preserved. No primary-literature feed was duplicated; the elementary separating-functional proof was checked directly.

## Precise hypotheses and projective scalar quotient

V is a fixed nonzero finite-dimensional K-space. G is a fixed finite subgroup of actual invertible one-column matrices, with fixed geometry independent of f. At width f the ordinary address maps are exactly lifts g^(tensor f), up to a common prescribed layout conjugation; arbitrary exterior coefficients c(f) are in K and independent of input data. Ordinary ADD/COPY/CLEAR and arbitrarily long but finite words may be used. Each paid call returns one actual K-linear transformed whole-field row at the same capacity. Its operator may depend on f and its input may depend on earlier paid responses.

Let Z be the actual scalar-matrix subgroup of G and p=|G/Z|. If g=lambda g_j, then its lift is lambda^f g_j^(tensor f). These projectively proportional matrices give one line, not separate independent directions. In particular per-column iI contributes i^f I and is merged into the fixed-width scalar coefficient. The correct dimension here is p, not the formal group-algebra dimension |G| used by the earlier all-width proof.

The required targets are invertible fixed one-column h_i, on distinct independent input coordinates vi, satisfying **h_i outside K^times G**. This stronger condition is essential. A target lambda g is implementable as the ordinary g lift followed by the freely allowed exterior scalar lambda^f; merely excluding h_i from G would give a false lower bound. Nonmonomial source h_i remain outside every scalar multiple of a monomial, so the retained source satisfies the stronger exclusion when G is enlarged to the allowed finite monomial group.

## 1. Tensor separation at one width

For s nonzero pairwise nonproportional vectors a_j in a finite-dimensional K-space, choose, for each j and l!=j, a K-linear form ell_(j,l) that kills a_l but not a_j. It exists because the pair is linearly independent. Choose eta_j nonzero on a_j. At a fixed f>=s−1, tensor the s−1 separating forms and f−(s−1) copies of eta_j.

On a_k^(tensor f) this functional is zero for every k!=j because its ell_(j,k) factor vanishes; on a_j^(tensor f) every factor is nonzero. Applied to a linear relation, it isolates its j-th coefficient. This proves independence for every individual f>=s−1. No norm, numerical rank or varying-width coefficient identity is used. The forms may differ between tensor positions, which is legitimate under the natural finite-dimensional tensor pairing.

This is the classical tensor/projective independence observation, not a new theorem claimed by this package. The sole literature worker owns the Chefles primary-reference fit. The elementary K-linear proof above is sufficient for this application and does not need to import the paper's Hilbert-space or discrimination interpretation.

## 2. The actual ordinary image algebra has dimension p

Define `R_f=span_K{g^(tensor f):g in G}` inside End_K(V^(tensor f)). This span contains I and is closed under multiplication, since `(g^(tensor f))(g'^(tensor f))=(gg')^(tensor f)` and gg' belongs to G. Arbitrary ordinary word length therefore does not enlarge it; arbitrary fixed-width exterior scalars and sums stay within the same algebra.

The p projective representatives span R_f. At f>=p−1, their lifts are independent by the preceding lemma, giving dimension p. The proposed guard f>=2p−1 is stronger and positive. R_f is an actual matrix-image algebra; it need not be an untwisted K[G/Z]. Products of representatives can carry width-dependent scalar phase factors, all correctly retained. Zero divisors are harmless for the later vector-space dimension comparison.

## 3. Target separation uses exactly 2p classes

Right multiplication by an invertible h_i preserves projective equivalence, so G h_i has exactly p projective classes. No such class meets one from G: `g h_i=lambda g'` would imply `h_i=lambda g^-1 g'` in K^times G. Thus G union G h_i has exactly2p projectively distinct representatives.

Apply the tensor lemma in E=End_K(V), using the natural isomorphism `E^(tensor f)=End_K(V^(tensor f))`. At every f>=2p−1 those2p lifts are independent. With H_i=h_i^(tensor f), this proves

```
R_f intersect R_f H_i = {0},
dim_K(R_f H_i)=p.
```

The second equality also follows from right multiplication by the actual invertible matrix H_i. This cancellation is by a unit in the ambient matrix algebra, not an arbitrary nonzero ordinary element.

The guard does not acquire a factor q. Only G and one G h_i are separated at a time; distinct input coordinates provide the separation between different targets. No independence among the union of all target cosets is assumed.

## 4. Actual paid-row history and dimension inequality

Fix one eligible width and write N=N(f), m=m(f). Every current field has a row in End_K(V^(tensor f))^N because the program is linear and exact on the full independent input space. Start with I_f=R_f^N. Retain every actual paid output row t_j conceptually, including erased or overwritten rows, and set

```
M_m=I_f+R_f t_1+...+R_f t_m.
```

Ordinary operations preserve this left R_f-module. The next paid operation acts on its one actual current row and produces one actual new row, which is adjoined. It is **not** assumed to be R_f-linear, to commute with ordinary operators, or to transform an entire earlier module for one charge. Its chosen operator need not belong to a uniform finite paid group. Keeping an old input copy creates no additional paid return.

Each cyclic contribution is the image of a p-dimensional K-space R_f, so

```
dim_K M_m <=(N+m)p.
```

After subtracting an ordinary initial background, every required H_i e_vi belongs to M_m. Its R_f-span W_i has dimension p by invertibility. Target separation makes W_i disjoint from the initial ordinary span in coordinate vi. Different vi make the W_i mutually independent. Therefore M_m contains the direct sum of I_f and all q target spans:

```
(N+q)p <=dim_K M_m <=(N+m)p,
m>=q.
```

p is finite and positive. Finite N(f) can grow without a common bound and cancels at each width. Known-zero scratch adds no independent input row. Word length and coefficients can vary arbitrarily with f because no relation between widths was used. Input-dependent branching/nonlinear coefficients remain outside the exact linear straight-line hypothesis.

## Counterexamples and guard/source fit

- **Projectively ordinary target:** h=lambda g is free at each f using lambda^f. The stronger target exclusion prevents this counterexample, including h=2I or phase-scaled ordinary maps.
- **Small f:** for G={I,X}, the source one-column Q is a K-linear combination of I and X at f=1 and can be ordinary in this span model. The stated theorem does not assert a lower bound there. Its sufficient threshold is substantive.
- **Sparse widths:** the former all-width phase-alias objection does not invalidate the present result at eligible widths. Projectively proportional phases are merged first, and the dual forms prove independence at each fixed eligible f. No consecutive-tail assumption or all-width sequence promotion is used here.
- **Growing/cross-column ordinary freedom:** allowing general full-width signed permutations can make the ordinary span the full matrix algebra, rendering targets ordinary. The proof expressly keeps one fixed finite one-column G and fixed geometry; it does not cover silently growing or cross-column ordinary alphabets.
- **Paid side information:** initial target rows from earlier paid/native/cached work can make the additional call count zero. Full-current-input surjectivity does not rule out that correlated history. The standalone initial-history restriction remains essential.
- **Other interfaces:** dependent inputs, nonunit/partial-field targets, fewer requested outputs, larger/changed capacities, multiple independent paid returns, approximation and nonlinear programs need new analyses. Exact independence supplies no conditioning or precision estimate.

The source application inherits T=A Jbar A^-1, the120 independently variable v-owner inputs and invertible nonmonomial target blocks. The625 binary-axis grid has amplitude dimension2^625. The actual child and matcher overlap on the canonical U row; no disjoint-factor commutation is introduced by the pointwise algebra. This review does not reclassify the source, replay native/phase/ownership, or independently establish those geometric premises anew.

For the conservative full monomial enlargement on a d-dimensional space, there are d! basis permutations and4^d independent fourth-root row entries, so |G|=4^d d! and p=4^(d−1)d!. With d=2^625 the guard is finite but enormous. These are symbolic cardinalities, not a class/rank computation. **No practical source cutoff, f=1/f=2/f=1024 application, or smaller threshold is certified here.** A family with unbounded widths eventually enters the mathematical range, but a fixed bounded-width caller must separately meet the guard.

At an eligible width the120 positive-rank returns each cost at least1 in a rank moment. If the old fixed base P/T grant is still the exact comparison, the old `T_t−P_t−120<0` obstruction remains applicable per eligible width. This is not a proof that an arbitrary nonuniform family has the requisite uniform recursive cost/stock/precision theorem or even a single fixed complete invoice. No funding or kappa result is inferred.

## Acceptance and smallest next action

No correction is required to the sealed pointwise lemma. Its improvement over the earlier statements is specific: arbitrary width-dependent K scalars and nonuniform finite ordinary words are admitted **eventually in width**, while a fixed finite ordinary one-column group and standalone history remain required. Earlier accepted all-width and central-Laurent proofs stay unchanged and retain their original, different scopes.

Author/root may record acceptance in a new sidecar. Any actual caller application must first establish the width guard, exact ordinary group, target/input contract and its currently available paid-history module. No extra classifier, proof engine or source run is called for by this review. This result is a separate history-dimension application of classical tensor independence, not adoption of PR5436's four-control proof, its2705 count or its execution claims; none was replayed here.

Credit the extension author, root's pointwise-history application question, the sole literature worker's Chefles primary fit, classical tensor-separation predecessors, the earlier module proof/reviewer and canonical-conversion source/ownership/profile/inverse reviewers, plus the retained BC/native/Clifford/product/compiler/precision/analytic lineage. Substantial OpenAI Codex assistance. No independent human or formal-kernel verification, new classical theorem, physical construction or kappa is claimed.
