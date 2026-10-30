# Sharp two-plane COPY mass with arbitrary coefficients and term count

This is a written algebraic proof, supported by finite source checks. It is
not a proof-assistant verification, native implementation, or multiplication
theorem. The two fields below must not be confused: geometry and COPY ranks
are binary; payload coefficients may belong to **any field**.

## 1. Exact contract

Fix two of the 56 matched planes in PR1825's selected-port matching. Their
ordered label bases have Gram matrices `I_2` over `F_2`. There are four
independent payload coordinates, two assigned to each plane. For a nonzero
coefficient vector `u`, let `S(u)` be the set of planes it touches. A touched
plane contributes its **whole two-dimensional label span**, even if only one
of its two payload coefficients is nonzero. This is precisely the expansion
in PR3990's `plane_mask` / `pairing_costs` and PR3997's support screen.

An allowed scalar message contributes `u v^T` to the four-by-four transfer
matrix and is charged

\[
 t(u,v)=\operatorname{rank}_{\mathbb F_2}
 B[\operatorname{closure}(u),\operatorname{closure}(v)],
\]

where `B` is the binary label pairing. Charges add across messages. Ordinary
transpose is used, including over the complex numbers. Zero factors can be
discarded. There is no restriction on the remaining finite number of terms,
their scalar values, cancellations, or whether their factors form bases.

The main endpoint is `sum u_j v_j^T = I_4`, as in PR3990/3997. We also cover
the strict paired-plane mask of PR1889: diagonal two-by-two blocks are `I_2`;
off-diagonal blocks must be zero unless the two planes are orthogonal, in
which case they are free. This extension is proved below, not assumed from
the identity result.

## 2. Binary rank inequality

The argument works for whole-block closures of sizes `p,q`, with self Gram
matrices `I_p,I_q`. Write

\[
 G=\begin{pmatrix}I_p&C\\C^T&I_q\end{pmatrix},\qquad
 c=\operatorname{rank}_{\mathbb F_2} C,\quad
 r=\operatorname{rank}_{\mathbb F_2}G.
\]

Block row elimination gives

\[
 r=p+\operatorname{rank}(I_q+C^TC)
 \ge p+q-\operatorname{rank}(C^TC)\ge p+q-c. \tag{1}
\]

For completeness, `rank(I+M) >= q-rank(M)` follows from
`I=(I+M)-M` and rank subadditivity. Also `rank(C^TC) <= rank(C)`.
These statements do not require that the joint span be nondegenerate, or that
the two blocks have disjoint label spans. The label lists are distinct payload
positions; possible linear dependence of their binary labels is allowed.

Let `A`, `B`, `AB` denote touching the first block, second block, or both.
All nine geometric charges are determined by `p,q,c,r`:

| Source closure / reader closure | A | B | AB |
| --- | ---: | ---: | ---: |
| A | p | c | p |
| B | c | q | q |
| AB | p | q | r |

For example the `A,AB` matrix is `[I_p C]`, of rank exactly `p`.

## 3. A rank functional that bounds every message

For a payload matrix `M` over an arbitrary field `F`, split it into the same
two coordinate blocks and define

\[
 L(M)=(p-c)\operatorname{rank}_{F}M_{AA}
       +(q-c)\operatorname{rank}_{F}M_{BB}
       +c\operatorname{rank}_{F}M. \tag{2}
\]

All three weights are nonnegative, since `c <= min(p,q)`. For a nonzero
rank-one atom `M=u v^T`, its full rank is one. Its `AA` block has rank one
exactly when both vectors touch `A`; its `BB` block behaves likewise. Thus:

- If the factors touch a common first block only, `L(M)=p`, matching its tariff.
- If they touch a common second block only, `L(M)=q`, matching its tariff.
- If they touch both blocks on both sides, `L(M)=p+q-c <= r` by (1).
- If their closures are disjoint, `L(M)=c`, matching the cross tariff.

These cases exhaust the nine entries of the table, so `t(u,v) >= L(u v^T)`.
Rank subadditivity and nonnegative weights imply, for **every finite** sum,

\[
 \sum_j t(u_j,v_j)\ \ge\ \sum_j L(u_jv_j^T)
                 \ \ge\ L\!\left(\sum_j u_jv_j^T\right). \tag{3}
\]

This argument is independent of support realizability or cofactor genericity.
In particular, rational specializations with cancelled cofactors and
overcomplete complex factorizations are included.

For the identity endpoint, (2) gives

\[
 L(I_{p+q})=(p-c)p+(q-c)q+c(p+q)=p^2+q^2. \tag{4}
\]

The coordinate identity decomposition uses `p` messages of tariff `p` and
`q` messages of tariff `q`, attaining (4). Hence the sharp minimum is
**`p^2+q^2`**, and for two matched planes it is **8**.

For the strict paired-plane masked endpoint, if `c>0` the planes are not
orthogonal and the endpoint is `I_4`; the same proof applies. If `c=0`, the
two diagonal blocks still have rank two, and the full-rank term in (2) has
weight zero. Therefore `L(K)=2*2+2*2=8`, even if free off-diagonal entries
make `rank(K)<4`. The identity still attains eight. Thus arbitrary allowed
off-diagonal choices do not reduce this two-plane mass floor either.

## 4. Binding all selected pairs

The replay authenticates the exact selected archive and its data-phase member,
and the retained matching certificate. It checks the 112 distinct nine-bit
labels, the 56-plane partition, and each self Gram `I_2` before pricing.
Every one of the 1,540 unordered pairs is then checked against (1) and all nine
atom inequalities. The resulting `(c,r)` inventory is:

| Cross rank c | Joint rank r | Number of pairs |
| ---: | ---: | ---: |
| 0 | 4 | 109 |
| 1 | 3 | 304 |
| 1 | 4 | 575 |
| 2 | 2 | 144 |
| 2 | 4 | 408 |

Seed 27 selects lexicographic pair index 27, namely plane indices `(0,28)`,
ports `(0,1)` and `(86,37)`. It has `(c,r)=(1,4)` and weights `(1,1,1)`.
The proof exposed the same nine-entry test for every pair, so the complete
small finite geometry was checked; no coefficient search was extended.

The separate checker recomputes binary ranks by enumerating images of linear
maps, rather than pivot elimination. It then constructs all 225 nonzero binary
rank-one atoms and solves exact shortest paths to the identity in the 65,536
possible binary four-by-four matrices, for each geometry class. Its answer is
eight; an underpriced-copy control changes that answer to six.
The primary replay also checks all binary cross matrices for `1 <= p,q <= 3`.
These are corroborating finite checks. Equations (1)–(4), not that census,
provide the general-dimensional, all-field and arbitrary-term proof.

## 5. Full optimistic budget decision

Restrict the 56 planes to any partition into 28 disjoint pairs, and require
each pair-local decoder to have no payload support outside its assigned pair.
Each pair pays at least eight, so total COPY mass is at least `28*8=224`.
Singleton planes, if retained, cost four and give the same total. This does
**not** sum pair bounds for overlapping or globally mixed messages.

Under PR2203's explicitly favorable two-unpaid-coordinate coverage model,
retain `m=73`, `W=896` productive families and `N=9` calls. Grant ideal hosting
and set all additional expenses to zero. Even then,

\[
 P\ge (m-2)W+224N=65,632>65,408=mW,
 \qquad P/(mW)=293/292. \tag{5}
\]

Here the base `(m-2)W` retains the source/target and idle-completion coverage;
the term `224N` is the decoder's separate COPY invoice. Additional source
access, coefficient arithmetic, adapters, shared-frame preparation, dirty
restoration, private lifetimes and owner costs are nonnegative and cannot
rescue (5). They are **not implemented or asserted to be zero**. PR2203's
direct local word already prices the baseline `{7:224,2:112}` with rank mass
1792; this package neither replaces it nor transfers its native realization
to arbitrary factorizations.

For each retained child `0<r<m` and saving `a>=0`,
`(r/m)^(1-a) >= r/m`. Thus the completed supplier moment is at least the
zero-saving ratio (5), and cannot be strictly below one. Any other supplier
or outer constraint can only add an obligation; the complex side already
fails this optimistic test. There is no benefit to a larger synthesis in this
pair-local, unchanged-coverage model. A changed coverage law, shared primitive,
or genuine cross-pair message requires a new ledger.

The ratio 293/292 and the independent-plane 224 baseline are predecessor
results, credited to ctoth's team and PR2203. The new implication is that
**arbitrary pair-local mixing and arbitrarily many scalar messages cannot
lower that mass or evade that particular rejection**.

## 6. Essential limit: mass is not concave power cost

The theorem does not say every cost measure is unchanged. For an orthogonal
pair (`c=0,r=4`), let `e_1,...,e_4` be the payload coordinate vectors. There
is an exact six-term factorization

\[
 I_4=(e_1+e_3)(e_1+e_3)^T+(e_2+e_4)(e_2+e_4)^T
 -e_1e_3^T-e_3e_1^T-e_2e_4^T-e_4e_2^T. \tag{6}
\]

Its separate geometric tariffs are `(4,4,0,0,0,0)`. The four cross terms
have zero **COPY** tariff, not zero physical execution cost. At a concave
power `0<tau<1`, its COPY-only bill is `2*4^tau < 4*2^tau`, while both
mass bills equal eight. For example at `tau=1/2`, the positive squared
bills are 16 and 32. At `tau=1`, they agree. Deleting the cross terms leaves
the valid orthogonal-plane masked fit `[[I_2,I_2],[I_2,I_2]]`, of rank two,
but fails the identity endpoint; the distinction is tested explicitly.

This is a boundary fixture, not a native supplier or new global optimization.
Even this favorable larger-child distribution cannot repair (5). Scalar
fitting rank, additive COPY mass and a concave COPY-only bill are different
quantities. Nonlinear messages, different readers/closures, shared charging,
three or more jointly mixed planes, and full physical realization remain out
of scope. No new kappa is established.

## Credit and status

Gonzalo Mier's PR3990 and PR3997 supply the exact two-plane tariff and finite
binary/generic/signed-ternary screens; they explicitly leave the coefficient
cancellation and overcomplete questions answered here. Cinna Davis's
PR1825/PR2126 supply the matching and identity endpoint. Adam Gall/PR1889
supplies the strict scalar mask. Jeremy Diviney/PR2203 supplies the native
payload distinction and budget; ctoth's team and Philippe Van Velzen retain
their earlier baseline/one-total credit. Nick Petalas/PR3383 proves a distinct
224 tariff for recodings inside the fixed grouped-fit row space, using a
one-total principal-Gram tariff; we neither reprove nor invoke it.
His PR3489's four-term two-indicator floor and PR3505's characteristic-two
matroid transfer criterion are also related. Here both factors stay on two
whole planes, but term count and coefficient field are unrestricted and no
matroid representability assumption is needed. The F2 shortest-path check
corroborates the fixture; it is not presented as a new general F2 floor.

Prepared for @CubeJerry with substantial OpenAI Codex assistance in derivation,
implementation, verification and writing. No independent human review or
formal proof kernel is claimed. Apache-2.0.
