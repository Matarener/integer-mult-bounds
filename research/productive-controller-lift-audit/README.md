# Operator-level audit of the productive-controller line (#4359 cover, #4440, #4441, #4447)

**Independent verification; no new κ.** The conditional κ = 0.00296 – 0.00300123 claims rest on two
formal identities: a controller word that diagonalises over *commuting* formal variables
(Q, D_0 … D_2p), and a native word checked in the free word algebra, where frame transports
are bookkeeping. This package executes both on concrete operators, at column multiplicity f,
with semantic controls. It also checks the #4359 delayed BIT cover algebra and #4447's new
transports, and screens for further frame retimings. The ledgers are not re-derived here;
#4446, #4448 and #4450 do that.

Base: canonical main `2a13eb1827784206202db90e5dc8327cf8a250db`. PR heads read:
#4440 `40e22a83`, #4441 `5f9d871c`, #4447 `322e0ec7`. Their four small input files are copied
in `vendor/`, byte for byte (Git blobs listed below, SHA256 checked by `verify.py`).

## Results

**A. #4359 delayed cover** (PROOF-REVIEW §3).
`Q_S D_P Q_S⁻¹ = D_(SPS⁻¹)`, with `D_P = [[I−P, PC],[CP, I−CPC]]` and `Q_S = diag(S, CSC)`.
Exhaustive over every S, every idempotent P and every involution C in GL₂(F₂), GL₂(Z/4) and
GL₂(F₃), and over 30 sampled S with all P and C in GL₃(F₂), about 118,000 cases in all.
Random cases over Z/2⁸, Z/2¹⁶, Z/2³⁰ and Z/3⁵ (n up to 12). Rank is preserved, and routing a
fibre by g ↦ gS is a bijection matching equal-rank jobs.
Controls: a lower block S instead of CSC fails in most cases; any C with C² ≠ I fails.

**B. #4440 controllers on concrete operators.** The emitted p17 complex word (19 full calls,
16 query shears) and p16 BIT word (18, 15) are replayed block-row by block-row. Every
generator is lifted to G^⊗f, f = 1, 2, 3. Complex uses simultaneously diagonalisable random
operators; BIT uses commuting involutions over F₂. In both, `L·A·R` equals the advertised
diagonal of monomials. Each query shear executed literally through an owned stream (clear,
copy, Q^∓1, add, uncompute) returns the stream to zero and matches S_y(Q⁻¹) / S_x(−Q).
Rejected controls:
- Q instead of Q⁻¹ in a query shear;
- one query shear deleted;
- one D_s not commuting with the rest (complex and BIT);
- Q not an involution (BIT);
- **D0 = F·q⁻¹ with [F, q] ≠ 0** (off-diagonal error about 72). The same shape with
  [F, q] = 0 passes.

So the controller identity needs the stage-zero premise **[D0, Q] = 0**. The source states
D0 = F9·Q⁻¹ (`kappa-rebuild/bit/complex_controller_factor.py`). The premise holds when the
nine-axis multiplier F9 is a product of one-axis gates that includes the central gate Q, as
`canonical_frame` builds full frames. The Laurent check cannot see it, because all its
variables commute by construction. We record it as an explicit premise.

**C. #4447 native word on physical frames.** The retimed THREE-base word has #4441's 117
entrances, 42 exits and 395 gate retimings, plus #4447's frame 1159. It is synthesised by
this package's own code, which reproduces the L-role bill
{1:2254, 2:514, 3:444, 4:103, 5:40}. Every one of the 1,160 frames is realised as a random
invertible matrix; a climb a → b applies C_b·C_a⁻¹ and a warp applies C_b·G·C_a⁻¹. All
632 inputs are independent. Both orientations meet the source endpoint at f = 1, 2, 3, and
the centres are cleared.
Rejected controls: one climb into the new frame skipped; the new frame realised differently
on one incident transport.
Positive control: realising frame 1159 everywhere as old frame 732 also passes, which is
#4447's common-frame lemma.

**D. #4447 transports and phases.** Each new transport C_b·C_a⁻¹ (360 → 1159, 364 → 1159,
1159 → 736, 1159 → 692) is built here as a dense 512 × 512 matrix from the gate list. Every
column has exactly 2^r nonzero entries of modulus 2^(−r/2), with r = 1, 1, 2, 4 as declared.
The package's own lowering (monomial · Fourier · monomial with its phase gates) equals the
transport exactly, global phase included, in both orientations. Also exact: C(q, −1) =
X^q·C(q, +1), and D⁻¹ = Z^α·D for diagonal Gaussians. This is the "Gaussian followed by a
Pauli translation" reading of Q⁻¹ in #4440.

**E. Frame screen after #4447.** For a gate or a whole constant-frame component, every legal
common frame g lies between the sum of the incoming frames and the intersection of the
outgoing ones. Paid mass is fixed, so the moment change depends only on dim g. The screen
was run at t = 0.997 and t = 0.9999.
- Positive control: on #4441's state the screen finds exactly #4447's move (gate B/480,
  span ⟨45, 133, 336⟩).
- After #4447, none of the 17,253 retimeable gates and none of the 1,073 constant-frame components
  improves. Most gates have no slack at all.

## What this does not cover

It does not re-derive invoices, moments, tensor completion, the compiler or the outer
predicates. Nor does it decide whether the physical stage-zero multiplier satisfies
[D0, Q] = 0 at every caller; that is open question 1. The cover check is algebra only:
the rational BIT charts and the common external weight remain #4440's stated premises.
Joint moves of several adjacent components are not screened.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/productive-controller-lift-audit
python3.12 -B research/productive-controller-lift-audit/verify.py          # PASS_PRODUCTIVE_CONTROLLER_LIFT_AUDIT
python3.12 -B research/productive-controller-lift-audit/verify.py --write  # regenerate RESULT.json
```

Needs numpy 2.2.6. Runtime is a few minutes; the GL₃(F₂) and GL₂(Z/4) cover cases take most of it.

Vendored inputs (Git blob, from the PR heads above):
`pr4440-COMPLEX-CONTROLLER.json` 39318f6a, `pr4440-BIT-CONTROLLER.json` 89c400d5,
`pr4441-CHANGES.json` 45744fed (identical at #4447's head), `pr4447-PATCH.json` f96d295d.

## Open next questions

1. **Is every full call's stage-zero multiplier exactly F9 = Q ⊗ F8, so that [D0, Q] = 0?**
   The controller identity fails without it. First step: read the initial native call's
   nine-axis frame operator in the THREE-base word and check that it factors through the
   central-axis gate. Blocked by: nothing.
2. **Do joint retimings of adjacent constant-frame components help after #4447?** Single
   gates and whole components do not. First step: screen nested frame pairs over adjacent
   component pairs by dimension. Blocked by: nothing.

## Credit

The audited constructions are 1337isnot1337's #4440/#4441/#4447 (with OpenAI Codex
assistance), on zxv's #4359 native and controller work. `clifford_exact.py` defines the
frame operators and is used only as the comparison object in D. Mark (Matarener), with
substantial Claude Code (Claude) assistance. Apache-2.0.
