# PR6030 uniform compiler and outer rows: independent source binding

**Result (no new κ).** Every numerical hypothesis that the selected PR6030 record
(κ = 781451/250000000 = 0.003125804) uses from the uniform compiler holds. So do
the nine outer savings and 24 of the 54 strict outer checks. This package
recomputes them with stdlib code that imports no repository engine. It does not
use PR6030's `pricing.py`, `higher-moment-strictification/verify.py`,
`mixed_target_probe.py` or the outer `ledger()` code. Each check is tied to the
written statement it instantiates. No discrepancy was found. The claimed complex
uniform rank N = 2^65807000000000 is the first passing point of the stated grid.

This answers open question 1 of PR6043 (the corroborating PR6030 audit): "can the
outer conditions and the compiler threshold be recomputed by code that does not
descend from PR5827's `pricing.py`?" The compiler half is answered in full. For
the outer half, the limiting rows now come from written sources, and 30 strict
checks stay open (Part B).

## Part A: compiler hypotheses

Sources: `research/higher-moment-strictification/README.md` §2 (higher-moment
paid-tail theorem) and §4 (logarithmic majorant with any power p > 0). The
definitions of m, k_min and r_max come from its vendored
`FINITE-PRECOMPILATION.md` (m = largest target rank). The invoice is the
`targets`/`paid` histogram in `research/p104-helper470-twin-rung-removal/RESULT.json`.
The verifier checks the statement fragments it relies on by text, and all six
inputs by SHA256.

| Theorem hypothesis | PR6030 instance | Checked here |
|---|---|---|
| §2: 0<C<1, u ≥ C, σ = t+u ≥ 1 | C = .0031258090, u = 1/7 | exact |
| §2: 1 < c < b < m, integer v | c=16, b=17, m=145, v=1024 | exact |
| §2: α = P_t/T_t | α < .99999999740808018176 < 1 − 10⁻¹² | interval |
| §2: γ_u = P_(t+u)/(c^u T_t) | γ < .97556235104746729785 < 125/128 | interval |
| §2: δ = Bb/(c^C T_t), B = 13,444 | δ < .95062864224216952441 < 125/128 | interval |
| §2: α^v + 2γ^v + 2δ^v < 1 | (125/128)^128 < 1/16, 1/(1+1024·10⁻¹²) + 4·2⁻³² < 1 | exact |
| §4: θ = log r_max / log k_min < θ̄ | r_max = 16^v, k_min = 17^v: 16^64 < 17^63 | exact |
| §4: 2^(b−a) r_max^b ≤ m^a | 2·(16^1024)^64 ≤ (145^1024)^63 | exact (big integers) |
| §4: θ̄^p < η = t·m^(t−1) | ln η − 1024 ln(63/64) > 0.19351 | interval |
| §4: m^(1−t) < 2^p | 145^(1024C) < 2^1024 | interval |
| §4: (1+H)^p < 2^((z−t)H) | z−t = (C−κ)/7 = 1/1400000000 = uniform-saving gap; (1.4·10⁹ j + 1)^1024 < 2^j | exact, j = 47005 passes, 47004 fails |
| claim row | H = 1.4·10⁹ · 47005 = 65807000000000 and N = 2^H in `CLAIM.json` | exact |

The same pass also recounts 13,444 productive fields, 66,834 paid calls and a
rank-mass surplus of 760. Extreme ranks are 72 paid and 145 productive. The
author's 30-digit intervals for α, γ, δ and η contain the enclosures computed here.

Real quantities are enclosed with directed-rounding interval arithmetic at 90
digits. Addition, subtraction, multiplication and division use decimal contexts
that round toward −∞ or +∞. Python documents decimal's `ln`/`exp` as correctly
rounded, so each such result is widened outward by |r|·10⁻⁸⁹, which exceeds half
an ulp. Every real comparison (α, γ, δ, η, the initial range and the least p)
uses the appropriate endpoint. The smallest real margin is about 2.6·10⁻⁹ (α
against 1 − 10⁻¹²).

**First passing grid point.** g(j) = j ln 2 − p ln(1 + 1.4·10⁹ j) has g(0) = 0,
g′(0) < 0 and g″ > 0. The passing grid points therefore form a single final ray,
so 47005 is the first one, as the author states. Like the source, this is a
sufficient threshold for this majorant. It is not a least native program.

**Headroom (information only).** At θ̄ = 63/64 the least admissible logarithm
power is 1012, so p = 1024 has a margin of 12. The finite threshold does not
affect κ.

## Part B: outer savings from written sources

The nine outer savings and their strict checks are computed from two written
sources, not from ledger code:

- PR1673's cost table (`research/selective-borrowing-outer-retune/vendor/pr1673/capped-phase-fusion/OUTER-AUDIT.md`,
  "Cost ledger"). This gives the main transform, global router, Gaussian, grouped
  BIT router, group scans and polynomial rows, and the Strassen bound ω < 45/16
  (checked by 7^16 < 2^45).
- `research/selective-borrowing-outer-retune/outer/FINE-PADDING-COMPOSITION.md` §1–2.
  This gives the PR1786 halo/core powers 48/128 that replace PR1673's 3/8 in the
  core-face row. It also gives ξ = ε(1+q) − c + s with c = 3/32, boundary = main + s,
  union = main + s + 13/32, and the list of ε/β constraints.

The parameters are the review's family: d = (C−κ)/7, b = κ+5d, a = κ+4d, q = κ+3d,
ε = 1−d and β = 1−3d, with layout s = d and r₀ = d/10 as recorded. All nine
savings equal the RESULT.json values exactly. All exceed κ, and main transform
(ε·q) is the minimum, with slack 20978119357/9800000000000000000.

These 24 strict checks are recomputed and match exactly: the nine
`*_above_kappa` rows, `gaussian_above_main`, `membership_arithmetic_fits_record`,
`union_header_fits_record`, `union_tag_work_per_visit_fits_record`,
`group_below_dimension`, `global_gamma_power_slack`, `source_axis_superpolynomial`,
`cap_below_cell`, `cap_above_band`, `group_gauge_power_slack`,
`strassen_integer_power_gap`, `epsilon_positive`, `epsilon_below_one`,
`group_positive` and `positive_layout_slack`. The other 30 are not covered, and
the verifier prints them. They are the stopped-supplier and controller rows
(λ, λ′, leaf, internal, stop, q bounds), the BIT/effective rows, the halo radius
and volume rows, and the fixed constants. The 4 functional checks are also not
covered.

The cost formulas were transcribed by hand. They share their written sources
with the ledger code, so Part B is source binding and an independent evaluation,
not an independent derivation of the cost rows.

## Semantic controls

Input-sensitive controls, which run on the live inputs:

- Removing the 208 productive rank-145 jobs from the same invoice makes the
  α lower bound 1.14, so the α test rejects.
- Taking the ambient rank as the 9-qubit dimension 512 rejects p = 1024 (the
  least admissible p would then be 1269). The definition requires the largest
  target rank 145, so this misreading is caught, not silently accepted.
- The power p = 1011 = p_min − 1 rigorously fails θ̄^p < η, and j = 47004 fails
  the threshold.
- Any changed byte in the six pinned inputs, any missing statement fragment, or
  any outer value that differs from RESULT.json fails.

Fixed demonstrations, which show that the written conditions have content but do
not depend on the inputs:

- The §2 counterexample for σ < 1 (t = 1/2, σ = 3/4, R = 100, J = 1): the actual
  split charge 100 exceeds the false bound 73.25.
- Decay 127/128 fails the block test (127/128)^128 < 1/16.
- θ̄ = 45/46 fails θ < θ̄, since 16^46 ≥ 17^45.

## Reproduce

```sh
python3 -I -B research/p104-6030-compiler-binding/verify.py
```

This prints a JSON summary and `PASS_P104_6030_COMPILER_BINDING` in well under
a second, with Python 3.10–3.14 and no dependencies.

## Scope and limits

This checks the numerical instantiation of two written theorems, part of the
written outer ledger, and their binding to the PR6030 record. It does not
re-prove the theorems. §2 is in the higher-moment package; §4 extends PR4411,
whose majorant proof was independently reviewed in PR4425. It also does not
check the integer-flow batch identity, the exit bound e ≤ r_max(n/m)^θ or the
complementary-source capacity for the P104 controller's actual batches. Those
stay under the inherited compiler and native_all_columns assumptions, together
with owned_erasure, precision_tape and analytic_recovery.

The invoice is read from the author's RESULT.json rather than re-derived from the
word. The independent word-to-invoice recount is in the admission review
(Matarener's interpreter) and in PR6043. This is an agent check, not human or
proof-kernel acceptance, and it changes no selected record.

## Open next questions

- **The remaining 30 strict outer checks from written sources.** They are still
  checked by only one code lineage
  (`research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py`, from
  PR4359's `outer_parameters.py`). The λ/leaf/internal/stop rows decide whether
  the stopped supplier's internal and leaf savings fit. First step: bind them to
  the stopped support-local supplier's written statement, where
  `research/selective-borrowing-outer-retune/outer/independent_check.py` has the
  `(1-stop)*b > eff` precedent. Blocked on locating that statement.
- **Controller batches against the §4 premises.** For one small n ≥ m, bind the
  P104 controller's batch sizes to n/m < s ≤ n and its exits to e ≤ r_max(n/m)^θ.
  Blocked by the compiler framework assumption.

## Credit

DreamingOfClouds (PR6030, PR5907). Ali Romman (PR5827 and the P104 pricing chain).
zxv and Cao Yifan (interval and compiler bounds, as credited in PR6030's
`pricing.py`). Jacob Alan Sussman (productive recursion, finite precompilation).
zxv (the higher-moment strictification package and PR4411's logarithmic
majorant) and pinterbanget (the PR4425 independent review of that majorant).
Vlado Vojdanovski (PR1673 outer cost table), Chafik Boukhalfa (PR1758/PR1786
fine-prime padding and halo/core powers) and the selective-borrowing outer
package authors. Matarener and the PR6043 audit (JosieElliston) for the invoice
recount this package relies on. Douglas Colkitt with OpenAI Codex (PR6030
application review).

Prepared for JosieElliston with Claude Opus 5.5 (Anthropic) via Claude Code, in
an unattended donated session. Codex (OpenAI) gave a read-only adversarial review
that led to the directed-rounding intervals. Apache-2.0.
