# Certified enclosure of #4100's BIT recurrence moments

**Claim type: an independent certified finite check, plus exact algebra. No
new κ.** This does not accept #4100 and changes nothing in it.

## Object

Cinna Davis's [BIT.md](../unconditional-batched-crt/BIT.md) §3, in #4100 at
head `337d04939571a637aeab54a0f58f54fde811663a`, needs two inequalities to
hold at the retuned `c = 8667/5,000,000`:

- `μ_1 < 1`;
- `μ_(1−c) < 1`.

Here `μ_x = (Σ_r H_r (r/64)^x + ηF(1/64)^x)/W`, with `W = 28416` and
`η = 10^-16`. `H` is the selected PR589 profile.

These inequalities give the strong-induction bound
`T ≤ C/(1−μ_1)·n + C/(1−μ_t)·n^t w^(1−a)` with `t = 1−c`, and with it the
stage savings `a1` and `a2`. Until now they were checked only by #4100's own
`check_composition.py`, through a vendored engine. #4171 reproduces `a1` and
`a2` from `c`, but not these moments.

## Results

0. **`H`, `W` and the surcharge are the selected supplier's.** The chain runs
   from `certificates/selected-result.json`, through its SHA256-pinned
   certificate `research/community-frontier1094-audit/ASSEMBLY.json`, to
   `bit_supplier` = `research/e8-bit-p111-tuned/tune/EXPECTED.json` (Git blob
   `e293ddc5…`, checked). There `nine.profile = H`, `nine.bit.live = W =
   28416`, `maxchild = 42`, and the rank mass is 1,808,352.
   - The certificate marks the BIT moment as surcharged, and #4100's `ηF`
     term is that surcharge.
   - With it, the root of `μ_(1−a) = 1` reproduces the selected
     `bit_lower = 0.001733427039589844234749` inside a `10⁻²⁰` window.
   - Without it, the root moves by about `2·10⁻¹²`.
   - So #4100's `μ_x` is exactly the selected BIT moment, and the window
     pins `W` given `H`.
1. **`μ_1` is exact.** `μ_1 = 2874298095721977/2890625000000000`, which
   equals #4100's ledger value `bit_linear_moment`.
2. **`μ_(1−c)` is certified below 1, with a thin margin.**
   `μ_(1−c) < 0.99999991163325597`, so the margin exceeds `8.836·10⁻⁸`. The
   rational enclosure is narrower than `10⁻³⁰`. It uses the `atanh` series
   for `ln` (after reducing by powers of two, with a geometric tail bound)
   and Taylor with a Lagrange remainder for `exp`.
3. **Headroom.** The root `c*` of `μ_(1−c) = 1` lies in
   `(0.0017334270, 0.0017334271)`, bracketed by certified signs. So `c` sits
   at least `2.7·10⁻⁸` below it. This matches the selected BIT primitive's
   ≈ 0.00173343.
4. **Sensitivity.** One extra rank-1 child in `H` makes `μ_(1−c) > 1` at this
   `c` (certified lower bound). The proof needs `H` exactly as printed. `H`
   is source-bound in the selected lineage.
5. **Stage algebra.**
   - `a1 = c(1−c)` and `a2 = c(1−c) + c·a1 = c(1−c²)` equal the printed
     constants.
   - With `w = e^c` and `n = e^(1−c)`, the exponent identity
     `(1−c)² + c(1−a) = 1 − a_next` holds exactly at `a = 0` and `a = a1`.
     The `n` and `w` terms are no larger.
6. **Body word.** `D−=H; F_I; D+=H; F_I; D=−D; D+=H`, with `F_I(D,H) = (RH,
   RD)` and `R` the atom reversal, produces exactly the six printed states
   and exchanges `D` and `H`. This is checked componentwise in `Z/7³` on 200
   random instances.

## Not covered

- Rebuilding `H` from the selected word itself. This package binds `H` to
  the selected record's pinned supplier data, not to a replay of the word.
- The bad-packet rate behind `η` (#4227 and #4228 treat it).
- The stock, fixed-tape and header-route constructions of BIT.md §2–§4.
- No proof-kernel check was run.

## Reproduce

```sh
python3 scripts/research_package.py --package research/pr4100-bit-moment-enclosure --check-only
python3.12 -B research/pr4100-bit-moment-enclosure/verify.py
```

It prints `PASS_PR4100_BIT_MOMENT_ENCLOSURE` in under a second, using only
the standard library. It reads the pinned selected record, certificate and
supplier data as declared inputs.

## Open next questions

None justified here. The binding question this package first raised is
answered in result 0. Re-deriving `H` from the word is the selected record's
existing cold replay, not new coverage.

## Credit

The construction and the audited constants are Cinna Davis's #4100 (with
OpenAI Codex assistance). The profile comes from the selected PR589 lineage.
Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
