# PR6030 outer rows: the remaining 30 strict and 4 functional checks bound to written sources

**Result (no new κ).** The selected PR6030 record (κ = 781451/250000000 =
0.003125804) has 54 strict and 4 functional outer checks. PR6109 tied 24 of the
strict checks to written sources. This package ties the other 30 and all 4
functional checks to written sources. Each row's formula is restated from a
written statement, evaluated with exact rationals on PR6030's parameter point,
and matched to the value serialized in PR6030's `RESULT.json`. All 34 agree and
are strictly positive. No discrepancy was found.

The code imports no repository code: not `endpoint.py`, `pricing.py` or any
outer ledger. Every file that carries a row is byte-identical to a file in the
selected source manifest `certificates/frontier6030-source.json`, sometimes at a
vendored path. The verifier checks this.

Two scope notes:

- **One hypothesis has no row.** The stopped-recursion layer theorem in the
  selected proof supplement `notes/batched-complex-rows.tex` assumes
  `max{σ+β(1−σ), 1−c, 0} < λ'`. Here c is the compact-control exponent
  (`K ≥ d^c/2`). No ledger row or parameter corresponds to c. With the selected
  K = 128G = Θ(log p), no fixed c > 0 satisfies `K ≥ d^c/2`, so the theorem's
  `1−c` term cannot be instantiated as written. The selected chain replaces it
  in PR1673's `SUPPLIER-SUPPORT-AUDIT.md` §4–6. That replacement charges exposure
  at `O(V h^(1−a) polylog p)` = `O(V h^τ polylog p)` with `h_(j+1) ≤ h_j/16`, so the
  condition needed becomes τ < λ', which the λ rows imply. This bridge is my
  reading of the sources and is **not verified here**: the verifier checks only
  τ < λ', not that PR1673's separate argument replaces the theorem's full
  `d^max(1−c,0)` charge under the selected call conditions. It is not a claimed
  gap either. PR1673 itself records that the old `K/log p → ∞` wording fails and
  gives a replacement. That file is in the source manifest but is not one of the
  selected record's proof supplements.
- **One row is stronger than the theorem.** The ledger's
  `leaf_saving_above_effective`, (1−β)b > a, is stronger than the layer
  theorem's leaf condition, which needs only (1−β)b > q. It comes from PR1673's
  note: "a strict leaf saving above a_eff and q". At β = d/b every
  checked order hypothesis of the layer theorem holds, but this row rejects.

## The stopped-recursion layer theorem

`notes/batched-complex-rows.tex`, "Stopping and weighted-tree bounds", is a proof
supplement of the selected record, and its SHA256 equals the selected record's
pin. Its hypotheses and their rows, with β = stop, σ = 1−b, τ = 1−a,
χ = τ+(1−β)max{σ−τ,0}, leaf = σ+β(1−σ), λ' = 1−q and λ = (τ+λ')/2:

| Written hypothesis | Ledger row(s) | Value at PR6030 |
|---|---|---|
| rational 0 < β < 1 | `stop_positive`, `stop_below_one` | d, 1−d |
| max{τ,σ,χ} < λ | `lambda_above_tau`, `lambda_above_sigma`, `lambda_above_internal` | d/2, 3d/2, d/2 |
| λ < λ' | `lambda_prime_above_lambda` | d/2 |
| λ' < 1 | `q_positive` | q |
| σ+β(1−σ) < λ' | `lambda_prime_above_leaf`, `q_below_leaf` (the same expression) | d(2−b) |
| 1−c < λ' | none (see above) | — |
| Ψ_c(σ) < 1 | not checked: stated for the theorem's own motif moment; the PR6030 counterpart is the complex uniform supplier's saving, and only `new_complex_uniform_saving_above_b` (b < uniform) is checked | d |
| 0 < τ < 1 (`compact-control-layout.tex`) | implied by `q_positive`, `q_below_effective` | — |

Here d = (C−κ)/7 = 1/1400000000. At PR6030, σ < τ, so χ = τ, as
`notes/stopped-product-assembly.tex` and ENDPOINT.md also state. Two further
rows bind to written sentences rather than to this theorem.
`q_below_internal` (χ < λ') is in OUTER-TRANSFER-AUDIT.md §6: "internal and leaf
exponents are strictly below the selected `lambda` and `lambda_prime`".
`leaf_saving_above_effective` is in PR1673's `phase_fusion_note.tex`.

## The other 19 strict rows and 4 functional rows

| Group | Rows | Written source |
|---|---|---|
| Effective-saving chain | `q_below_effective`, `complex_endpoint`, `complex_above_effective`, `actual_bit_above_effective`, `complex_below_one_over_32`, `short_record_fallback` | OUTER-TRANSFER-AUDIT.md §6 ("The effective BIT saving is below both the actual ordinary BIT saving and the selected complex saving"); PR1673 SUPPLIER-SUPPORT-AUDIT.md §6 (q < a, τ = 1−a); ENDPOINT.md (`0 < q < a < b < uniform`, `b < 1/32`, `epsilon>a`) |
| Halo and locality | `microbox_halo_volume`, `halo_covers_generic_inverse_radius`, `cap_below_phase_cell_power`, `fine_prime_halo_umbrella`, `theta_positive_polynomial_power`; functional `fixed_halo_explicit_metadata_branch` | PR1786 FINE-PRIME-PADDING.md §5 and its side conditions (`128-48-beta>0, 48>43`, `xi<2`, cost power `epsilon+beta+48-128+2`, J = p^42 and bandwidth 2WJ+W, the p^10 conditioning bound from p^2 and θ^−2 ≤ 16p^4); ENDPOINT.md (theta power 2) |
| Logarithmic guards and record geometry | `actual_logarithmic_group_guard`, `actual_logarithmic_gamma_guard`, `alpha_logarithm_absorption`, `group_key_fits_record`, `support_router_span`, `new_semantic_guard_with_C1_one`; functional `new_semantic_group_guard` | FINE-PRIME-PADDING.md side conditions (`1-epsilon-r0>0`, `1-(2xi-2)-r0-beta>0`); OUTER-TRANSFER-AUDIT.md §5–6 (`group_beta<1`; ε < 1 absorbs semantic and description constants); ENDPOINT.md (group key gap 2d) |
| BIT stock | functional `new_BIT_row_stock_sublinear_in_active_group`, `actual_new_BIT_stock_sublinear` | OUTER-TRANSFER-AUDIT.md §6 (`group_beta*(1-0.003) > 0`, "the changed BIT reserve is sublinear in the active grouped width"); the current atom 1/250 and admitted BIT 17/5000 read from `research/query-thinned-controllers/RESULT.json` |
| Reporting | `improvement_over_user_baseline` | ENDPOINT.md: "a reporting check, rather than an admission hypothesis" |

Each row has a status:

- 11 are hypotheses of a written theorem.
- 16 are inequalities a written sentence asserts.
- 3 are fixed written constants.
- 2 are implied by a stronger written margin. `actual_logarithmic_group_guard`
  and `actual_logarithmic_gamma_guard` drop the r0 that the written conditions
  `1-(2xi-2)-r0-beta>0` and `1-epsilon-r0>0` carry. The verifier computes the
  written margins too and checks that they are positive.
- 1 is substituted. `actual_new_BIT_stock_sublinear` is the written rule
  `group_beta*(1-0.003) > 0` with PR6030's current atom 1/250 in place of 0.003.
  The atom is a data input from `query-thinned-controllers/RESULT.json`, not a
  written inequality.
- 1 is a reporting check.

The verifier prints the table with values and sources. The functional
`fixed_halo_explicit_metadata_branch` is computed literally as one minus the
written paid cost power, 1 − (ε+β+48−128+2) = 79 − ε − β.

The `fine_prime_halo_umbrella` row is 10 − (2·2+2+1/2). FINE-PRIME-PADDING.md
gives the 4 (from θ^−2 ≤ 16p^4) and the 2 (the exponential factor p^2). The
extra 1/2 has no written counterpart that I found. It only makes the row
stricter, since α^5 is polylogarithmic.

## Other observations

- **ENDPOINT.md's stated premises do not hold at PR6030.** Its written family
  proof assumes `q < 0.002306` and the ordinary BIT saving 0.0027. PR6030 has
  q = 21880643/7000000000 ≈ 0.0031258 and admitted BIT 17/5000. Its closed-form
  gaps still hold as identities in d and b: (1−stop)b−a = d(1−b),
  λ'−leaf = d(2−b), λ−τ = d/2 and λ−σ = 3d/2. The general case is
  Nick Petalas's PR5984 region theorem, OLD < κ < min(U, B, 1/32). The verifier
  checks that PR6030 lies inside it.
- **Rows with identical expressions.** Grouping by value at PR6030 and at two
  points with independent parameters gives these groups:
  - `q_below_leaf` = `lambda_prime_above_leaf`
  - `q_below_internal` = `q_below_effective` (on the σ < τ branch)
  - `group_key_fits_record` = `group_below_dimension`
  - `support_router_span` = `union_header_fits_record` = functional `new_semantic_group_guard`
  - `new_semantic_guard_with_C1_one` = `actual_logarithmic_gamma_guard` = `epsilon_below_one` = `source_axis_superpolynomial`
  - `lambda_above_tau` = `lambda_prime_above_lambda`, since λ is the midpoint

  `lambda_above_internal` equals `lambda_above_tau` on the σ < τ branch. So the
  54 strict checks contain fewer distinct inequalities than rows. This is
  informational; duplicates are harmless.

## Controls

Each control changes one input, and each is rejected:

- β = 0 fails 0 < β.
- β = 1 − q/b puts the leaf exponent at λ'.
- q = a collapses λ onto τ.
- BIT saving 0.0027, PR4359's value, fails `actual_bit_above_effective`.
- β = d/b passes the layer theorem's checked order hypotheses but fails the ledger's stronger leaf ordering.
- A RESULT.json row perturbed by 10⁻³⁰ is caught.
- Halo exponent 43 fails the radius row.
- Core exponent 50 fails the core-face saving.

The last two changes go through the same row evaluator.

The verifier also fails if any pinned byte changes, if any of the 41 statement
fragments is missing, or if a written source is absent from the selected
manifest.

## Reproduce

```sh
python3 -I -B research/p104-6030-outer-row-binding/verify.py
```

This prints a JSON summary and `PASS_P104_6030_OUTER_ROW_BINDING` in under
0.1 s. It was run with CPython 3.10–3.14, with and without `-O`, and needs no
dependencies.

## Scope and limits

This checks that each outer row instantiates a written statement and that its
value at PR6030 is right. The exceptions are labelled: two rows are implied by
stronger written margins, one substitutes the current atom, and
`fine_prime_halo_umbrella` carries an extra 1/2 with no written counterpart. It does not re-prove those statements. It does not
check the layer theorem's moment hypothesis Ψ_c(σ) < 1 or its `1−c` term,
PR1673's support-local replacement,
PR1786's locality and conditioning bounds, or the outer analytic decomposition.
The five framework assumptions (native_all_columns, owned_erasure, compiler,
precision_tape, analytic_recovery) are unchanged. The formulas were transcribed
by hand from the written sources. Those sources and the ledger code share
authors, so this is source binding and independent evaluation, not an
independent derivation. This is an agent check, not human or proof-kernel
acceptance, and it changes no selected record.

With PR6109, every one of PR6030's 54 strict and 4 functional outer predicates is
now tied to a written source by code outside the PR4359 ledger lineage.

## Open next questions

- **Cite the replacement for the 1−c hypothesis.** Relevance: the selected
  supplement's layer theorem is not instantiated literally at K = 128G. First
  step: a maintainer note in the selected review citing SUPPLIER-SUPPORT-AUDIT.md
  §4–6 as the replacement of the d^max(1−c,0) term. Blocker: a maintainer
  decision. No mathematical gap is claimed.
- **Audit the PR1673 replacement itself.** Relevance: this package binds rows to
  statements and does not check them. First step: check SUPPLIER-SUPPORT-AUDIT.md
  §6's geometric sum, and its "same strict complex/leaf margin" claim, against
  the batched-complex-rows theorem. Blocker: none.
- **Controller batches against the compiler's §4 premises** (from PR6109).
  Blocker: the compiler framework assumption.

## Credit

DreamingOfClouds (PR6030, PR5907). zxv (PR4359 outer ledger, ENDPOINT.md family
proof and OUTER-TRANSFER-AUDIT.md). Vlado Vojdanovski (PR1673 capped phase
fusion, support-local supplier and SUPPLIER-SUPPORT-AUDIT.md). Chafik Boukhalfa
(PR1786 fine-prime padding, halo/core powers). icekylinx (the stopped
product-ring construction behind the internal and leaf exponents). The upstream
and compact-control authors of the stopped-recursion layer theorem in `notes/`.
Nick Petalas (PR5984 κ-region theorem, which this package cites rather than
repeats). Douglas Colkitt with OpenAI Codex (PR6030 application review). PR6109
(JosieElliston), whose open question this answers.

Prepared for JosieElliston with Claude Opus 5.5 (Anthropic) via Claude Code, in
an unattended donated session. Codex (OpenAI) gave a read-only adversarial review.
That review led to the r0-carrying written margins, the substituted-atom label,
the conditional wording of the `1−c` bridge, the explicit unchecked Ψ_c
hypothesis and the evaluator-based halo/core controls. Apache-2.0.
