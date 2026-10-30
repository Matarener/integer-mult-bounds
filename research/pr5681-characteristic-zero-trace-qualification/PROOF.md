# Two characteristic-zero trace qualifications of the PR5681 static fixture

This note applies the classical first-order trace identity to two specified additional characteristic-zero contracts suggested by the [PR5681](https://github.com/CrocSwap/integer-mult-bounds/pull/5681) static fixture. It is a conditional source-qualification argument, not a contradiction in the source construction. The elementary trace identity is not new.

The primary source texts are the unchanged [PR5681 proof](inputs/PR5681-PROOF.md), sections 2–3, and its retained [PR5673 proof](inputs/PR5673-PROOF.md), section 1. Their immutable source pins are in [SOURCES.json](SOURCES.json). PR5681 works over characteristic two and supplies a static recipe, not a complete chronological word or a native lift. Its selected fixture has 31 leaves, block dimension four, and five square-zero thin maps of rank two over F2. Copying binary entries to another field is not asserted to preserve those properties.

## 1. Common additional characteristic-zero contract

Let F be a field of characteristic zero. Let

$$
W=W_0\oplus\cdots\oplus W_{31},\qquad \dim_F W_j=d=4,
$$

so that W has dimension 128. Use ordinary finite matrices over the free dual-number polynomial ring

$$
F[e,x_1,\ldots,x_{31}]/(e^2),\qquad x_j=D_j+1.
$$

The variables x_j are independent and central. All query matrices and projectors are constant over F. The element e is central and nonzero, and 1,e are linearly independent over F[x_1,…,x_31]. No additional quotient kills or identifies the first-order coefficient. This is an ordinary trace contract, not a graded or supertrace contract. Transferring the argument to a physical representation would require proof that it faithfully preserves this normalized coefficient identity.

For stage j let E_j be identity on the core W_0 and leaf W_j, and zero elsewhere. Each stage has a finite full resolution by idempotent orthogonal projectors P_jh satisfying

$$
\sum_h P_{jh}=E_j,
$$

with the source support conditions and commutation with its stage kernel T_j. A full call is

$$
(I+x_jP_{jh})(I+eR_{jh}),\qquad R_{jh}=P_{jh}T_j.
$$

A thin call is I+eZ_l. Consider any finite ordering of all the declared full and thin calls. The required complete endpoint is

$$
(1+e)\prod_{j=1}^{31}(I+x_jE_j).
$$

The stage supports commute; no commutation among query matrices is assumed. Five thin calls is the selected fixture contract. The first case also holds for any finite number of square-zero thin derivatives.

A claimed polynomial endpoint identity can be specialized at x_j=0 for every j, because the variables are independent. In characteristic zero this means **D_j=−1**, not D_j=1. The latter agrees only in the source characteristic-two setting.

At this specialization every full-stage prefactor becomes identity. Writing Q_l for the query derivative of each full or thin call in its actual order gives

$$
\prod_l(I+eQ_l)=I+e\sum_lQ_l,
$$

since e²=0. The specialized target is I+eI_W. The free coefficient requirement therefore implies the necessary identity

$$
\sum_{\mathrm{full}}R_{jh}+\sum_{\mathrm{thin}}Z_l=I_W. \tag{E}
$$

Order cannot affect this particular coefficient. This is only a necessary condition; no converse or chronological construction follows.

## 2. Case A: all query derivatives are square zero

**Additional hypothesis A:** every full and thin query derivative is square zero over F. This may require a changed full-stage kernel. The verbatim source kernel is not identified with a square-zero matrix over characteristic zero.

For example, if a newly supplied T_j satisfies T_j²=0 and commutes with its idempotent projectors, then

$$
(P_{jh}T_j)^2=P_{jh}^2T_j^2=0.
$$

For a square-zero matrix Q, image Q is contained in kernel Q. A basis adapted to these subspaces gives a matrix with zero diagonal, so tr Q=0. Taking ordinary traces in (E) would give

$$
0=\operatorname{tr}(I_W)=128,
$$

which is impossible in characteristic zero.

Thus no word satisfies this 128-dimensional scalar target when all full and thin query derivatives are square zero over F. The conclusion needs no rank-two hypothesis or bound on stage splits or call order. It applies to the stated all-query-square-zero contract and is not a general assertion about complex callers.

The hypothesis concerns Q²=0 for the derivative matrix over F. Automatic (eQ)²=0 says nothing about Q, because e²=0 holds for every Q. Likewise I+eQ is invertible with inverse I−eQ for arbitrary Q. Neither automatic nilpotence of eQ nor this invertibility implies derivative nilpotence or zero trace.

## 3. Case B: verbatim full-stage kernel and square-zero thin derivatives

**Additional hypothesis B:** keep the full-stage kernel verbatim on core and leaf j,

$$
T_j=\begin{pmatrix}I_d&I_d\\I_d&I_d\end{pmatrix},
$$

retain the full resolutions, and require all five thin derivative matrices Z_l to remain square zero over F. Here T_j²=2T_j. Full-query nilpotence is not assumed.

The full resolution gives

$$
\sum_hR_{jh}=\left(\sum_hP_{jh}\right)T_j=E_jT_j=T_j.
$$

Hence the total full-query trace is

$$
\sum_{j=1}^{31}\operatorname{tr}T_j=2gd=2\cdot31\cdot4=248.
$$

The target trace in (E) is (g+1)d=128. Consequently every successful word under the verbatim-full-stage contract must satisfy

$$
\sum_{\mathrm{thin}}\operatorname{tr}Z_l=(g+1)d-2gd=(1-g)d=-120.
$$

Square-zero thin derivatives have total trace zero, giving a contradiction. Thus no word satisfies this same target with the verbatim full-stage kernels, full resolutions and square-zero thin derivatives over characteristic zero.

This conclusion assumes no nilpotence of the full derivatives. If arbitrary thin matrices are permitted instead, this argument supplies only the necessary equation Σthin tr Z_l=−120. It does not prove that arbitrary thin maps or a complete word are impossible.

## 4. Source boundary and consequences

PR5673 expressly permits arbitrary thin matrices Z. Its general theorem does not assume square-zero thin maps. Square-zero thin derivatives are additional hypotheses in the two proposed lifts above, motivated by the selected characteristic-two static fixture.

The valid F2 witness is unaffected: 128,248 and120 vanish in characteristic two. Neither proof challenges its static ranks, signatures or source theorem. Neither proves that literal copying of its binary matrix entries preserves nilpotence over characteristic zero.

These qualifications exclude neither all characteristic-zero/complex callers nor arbitrary-thin PR5673 contracts. They establish no general Fourier-character or native Gaussian obstruction, graded/supertrace extension, different-dimensional or changed-target exclusion, nonfull-stage result, or paid-idle-multiplier result. A different representation or contract requires its own endpoint and complete-cost argument.

The useful result is the exact distinction between two source-bound counterfactuals: all-query nilpotence has trace zero against target 128; verbatim full T with full resolutions requires thin trace −120 against square-zero thin trace zero. It identifies an assumption that must change before these proposed chronological constructions could succeed. No actual word, native phase, frame adapter, ownership/stock/precision/tape bill, paid profile, complete caller, compiler/outer admission or κ follows. The selected frontier is unchanged.

The classical trace identity receives no novelty claim. Credit Ali Romman's PR5681 static construction/audit and retained PR5673 proof, Cinna Davis's controller lineage, PR5617/5631/5649's query-frame and fixed-star line, and the retained P104/native/helper/compiler predecessors. Formulation B was independently identified during review of formulation A. Prepared with substantial OpenAI Codex assistance, including independent local AI paper review; no human-independent scientific acceptance or proof-assistant theorem is claimed.
