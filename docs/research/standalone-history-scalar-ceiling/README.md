# Standalone paid-return histories with scalar extensions

For an exact standalone linear program, q invertible target rows on distinct independent input coordinates can require at least q new paid whole-field returns, even when paid calls use earlier responses. This note gives two precise versions of that history-dimension statement. Both start with **ordinary initial history only**, keep one fixed field capacity, and count one actual new output row per paid call.

The paid-history principle is inherited from [the standalone finite ordinary-module argument in #5425](https://github.com/Clear1nsight/integer-mult-bounds/tree/00005c8c5e81c7f27b5769f9309ff88758e26f51/research/fanout-optimality-support), at exact head `00005c8c5e81c7f27b5769f9309ff88758e26f51`. That predecessor permits finite feedback and overwritten rows within its fixed-word, fixed-capacity, ordinary-initial-history contract. The additions here are the central c·2^(n f) scalar extension, the eventual pointwise arbitrary-c(f) extension with nonuniform finite words and N(f), and the separate conditional q=120 nomination. The predecessor's 112-output application is not transferred, and no new paid-history principle is claimed.

The first version permits fixed exterior powers-of-two normalizers in a fixed finite word. The second permits arbitrary width-dependent exterior scalars and nonuniform finite words, but applies only at each sufficiently large width **f ≥ 2p−1**, where p is the number of actual projective classes of one fixed finite ordinary group. That threshold can be astronomical. Neither version establishes a new-call charge at a parent cut already holding paid/native/cached observations, a practical-width certificate, a physical supplier or a new κ.

## General statement and the two width domains

Let K=Q(i), let V be a fixed nonzero finite-dimensional one-column space, and let G be a fixed finite group of actual invertible ordinary matrices on V. A width-f field is V tensor-powered f times, up to one prescribed common layout conjugation. Whole-field ADD, COPY and CLEAR and the declared ordinary address lifts are allowed. The program is exact and linear on its full independent current-input space; its choices and coefficients are independent of input values.

The q targets have fixed invertible one-column maps h_i on **distinct** input coordinates v_i, possibly plus ordinary initial backgrounds. Different h_i need not occupy different ordinary cosets. Each paid call transforms one actual current whole-field row and returns one new row at the same capacity. Keeping a copy of its old input does not create a second paid return. No commutation or ordinary-module linearity of the paid operator is assumed.

| Statement | Allowed scalar/program dependence | Width requirement | Target exclusion |
| --- | --- | --- | --- |
| [Central Laurent](proofs/central-lemma-v1.md) | One fixed finite columnwise word; exterior c·2^(n f), with c in K and integer n fixed per instruction independently of f; paid one-column operators fixed | Exactness at every positive width, or throughout a consecutive infinite tail | h_i is outside `<2I>G` |
| [Eventual pointwise](proofs/pointwise-lemma-v1.md) | Arbitrary exterior c(f) in K; finite ordinary words, their lengths and finite independent dirty-input counts may vary arbitrarily with f; ordinary G and geometry remain fixed | **Each integer f ≥ 2p−1**, with p=\|G/(G∩K×I)\| | h_i is outside `K×G` |

Under the respective hypotheses, the program needs at least q paid returns. The pointwise statement needs neither a common word across widths nor exactness at consecutive widths once its guard is met. It does not assert a bound at arbitrary smaller widths. For the conservative fourth-root monomial enlargement on a d-dimensional V, p=4^(d−1)d!; in the nominated source geometry d=2^625. These are symbolic finiteness bounds, not a computation of a usable cutoff. No application at f=1, f=2 or f=1024 is certified.

## Why actual returned rows give the bound

At one eligible pointwise width, the actual ordinary image algebra

```
R_f = span_K {g^(tensor f) : g in G}
```

has dimension p after exact proportional phases are merged. Classical tensor separation applied to the 2p projective classes in G and G h_i gives `R_f ∩ R_f h_i^(tensor f) = {0}`. Only G and one target coset are separated at a time; distinct input coordinates supply the separation among targets.

Retain every actual paid output row t_j conceptually, including overwritten or cleared rows. Starting with N independent inputs, the history is contained in

```
M = R_f^N + R_f t_1 + ... + R_f t_m.
```

Each actual return contributes at most p dimensions. The q target rows require q additional p-dimensional summands on distinct input coordinates. Thus `(N+q)p ≤ dim_K M ≤ (N+m)p`, so m≥q. A finite N(f) cancels separately at each eligible width. This analysis does not grant the paid operation for free on every earlier row.

For the central variant, fixed Laurent support is first expanded and exact all-width/consecutive-tail identities are promoted to formal row identities. Central localization then replaces K by K(τ), leaving an ordinary algebra of dimension |G| over that field. The analogous dimension comparison gives the same paid-return count. Localization is a proof device; it grants no physical division by a rational function of 2^f. The two self-contained proofs and their exact hypotheses are retained unchanged in the appendices.

## Conditional nominated example: 120 target coordinates

The [LOCAL source report](source/standalone-local-report.md) and [conversion obligation](source/conversion-obligation.md) nominate a particular canonical-conversion interface, rather than an upstream-admitted BC supplier. After the specified ordinary entrance and reciprocal typed source rule, its current output is `w=A Jbar^-1 z` and its required semantic output is `A z`. The uniquely required post-map on the full current-input space is therefore

```
T = A Jbar A^-1.
```

On each of 120 distinct v-owner coordinates, the nominated one-column block contains `h=Q J Q^-1`, with the stated factorwise lift and ordinary aliases. The retained source identity `Phi581=L2 h Q² R1` has four nonzero entries per row; multiplication by the monomial units and tensoring with invertible factors preserve nonmonomial support. Consequently each nominated h_i is invertible and outside every scalar-monomial ordinary class.

The source-owner argument uses invertible genuine-original prefixes, disjoint original banks, the unchanged-owner no-write interval and invertible normalization to make these current coordinates simultaneously arbitrary. The copied source documents state that argument and its premises. This note does **not** freshly validate the physical ABI, native implementation, source phases, owner scan or compiler application. Under those inherited nominated premises, q=120 specializes the general statement, subject to its exact width/scalar contract.

The optional fixed-profile comparison is also conditional. Hold exactly

```
P = {1:2201, 2:412, 3:510, 4:127, 5:40},
T = {4:28, 7:7, 8:159, 9:438}.
```

T generously includes the unadmitted 120H8+120H9 main grant and the retained helpers. If this standalone converter is added without changing any other calls or genuine targets, its positive-rank paid returns cost at least 120 in a rank moment. The copied source proof gives `F(t)=T_t−P_t−120`, `F(1)=−8`, and `F(t)/6^t<−4/3` for 0<t<1. For the pointwise variant, this consequence is only at eligible widths. It is neither a new numerical certificate nor a uniform recursive cost theorem for arbitrary nonuniform families.

## Scope, review status and provenance

Both initial histories contain only ordinary combinations of the independent current inputs, independent dirt and zero scratch. Correctly versioned target observations supplied from earlier paid work can make an **additional** conversion charge zero. Input surjectivity does not remove those observations. Standalone bounds cannot be added across shared conversions. Growing ordinary groups or geometry, general cross-column maps, changed capacity, several outputs per paid call, dependent inputs, nonunit/partial targets, approximation and nonlinear programs require separate analysis. Exact algebraic independence supplies no conditioning or precision bound.

The central and pointwise lemmas received separate independent AI static mathematical reviews without a required correction. Their original PROPOSED headings are historical: the [acceptance reports and review decisions](EVIDENCE-INDEX.md) record the later status without changing the sealed bytes. These are written proofs and reviews, not independent human validation, a formal-kernel proof or a scientific replay. No verifier, numerical RESULT or registered replay is part of this documentation note.

Planning canonical context is `32890bc5de034ab8fc93ac88ead7279a6a416d04`. The theorem, source and review snapshots have LOCAL provenance, explicitly recorded in [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json); they are not fabricated canonical input roots. The [evidence index](EVIDENCE-INDEX.md) supplies working copied-file links and an original-label remap. Historical workspace labels inside frozen appendices are provenance text, not promises of a bundled native runtime closure.

The sole-monitor checkpoint 1347 covered current all-author/all-state PR metadata through 2026-10-24 13:33:40 UTC, with selective body/source review. At cached PR5436 head `4c31fd7d4eee61ff9fd59533549a67ef1a25b449`, zxv supplied the support-width prompt and a distinct four-control 2705-source corollary. This note does not adopt that source application, its proof, finite calibration or execution claims. The contribution here is the paid-return history-dimension application and its nominated-source fit, not a new classical tensor theorem or a universal novelty claim.

The sole monitor's prepublication refresh covered the 100 recent all-state PR-metadata/body records through 2026-10-24 16:50:42 UTC, with a subsequent static locator addendum. Main, governing guidance and selected κ were unchanged. No new changed nearby exact-scope claim was identified in that bounded incremental pass; it is not exhaustive Discussion, unpublished-work or novelty coverage. The receipt hash and exact adjacent heads are recorded in the [evidence index](EVIDENCE-INDEX.md) and [source manifest](SOURCE-MANIFEST.json).

Adjacent [#5441](https://github.com/CrocSwap/integer-mult-bounds/commit/11fedb46fa199283f78282187c10aea432d8b0bb) addresses fixed physical transfer-table endpoint and cut-dimension bounds, not this paid-return resource count. [#5442](https://github.com/CrocSwap/integer-mult-bounds/commit/19e8f0452c09cbfe99511ea697fa239c1f457314) states a general finite-group all-width lifting lemma; its claimed complete-body closure is [challenged by zxv's review](https://github.com/CrocSwap/integer-mult-bounds/pull/5442#issuecomment-6385984727). Neither that closure claim nor its executable certificate is a dependency of this note. The conditional LOCAL source nomination and the self-contained scalar-extension proofs remain separate. A small-width affine criterion for a different operator family cannot replace the fixed ordinary-group and target-coset separation hypotheses here.

## Open next questions

The smallest application question is the actual cut's available history module, with correctly versioned owners, retained paid observations and lifetimes. Determine whether the required target rows lie in its ordinary closure, and charge production/retention and opportunity costs once. That question is not answered by the standalone theorem. A smaller source-specific sufficient width guard would require a separately justified ordinary subgroup or span argument; none is computed here. Any recursive use also needs its own uniform cost, precision, stock and productive-target contract.

## Credit and references

Anthony Chefles supplies the classical multi-copy/projective tensor-independence precedent: *Unambiguous Discrimination Between Linearly Dependent States With Multiple Copies*, Physical Review A 64, 062305 (2001), [DOI](https://doi.org/10.1103/PhysRevA.64.062305), Section II, Eq. (2.3). The field-linear proof used here is stated and proved directly, without attributing a printed generic-field theorem to the paper.

Peter Kropholler and Karl Lorensen's *Group-graded rings satisfying the strong rank condition*, Journal of Algebra 539 (2019), 326–338, [DOI](https://doi.org/10.1016/j.jalgebra.2019.08.014), Theorem A, corroborates the central route. The elementary central-localization proof is self-contained and does not assume a domain/Ore property for a finite group algebra or amenability of the paid-operator group. The evidence index records the sole literature worker's fit-note hashes; no paper PDF or text is redistributed.

Credit the #5425 finite-feedback ordinary-module proof and its independent reviewer directly, and zxv for the current support-width prompt; the scalar-extension and source authors; root's localization and paid-history application question; the independent reviewers and sole literature worker; and the BC/native/Clifford/product/compiler/precision/analytic lineage. Preserve Ali Romman, Dillon Amburgey/dillona, Cao Yifan, Cinna Davis, zxv, Dugongue, Jacob Alan Sussman, Chris R/Clear1nsight and the notices in the retained appendices. This work uses substantial OpenAI Codex assistance. The independent reviews are AI static reviews, not independent human or formal-kernel verification. No new physical construction, supplier admission or κ gain is claimed.
