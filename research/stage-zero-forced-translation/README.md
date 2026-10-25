# Independent check of #4464: stage-zero commutation, and the translation is forced

**Claim type:** an independent exact check plus a closed form. **No new κ.** It covers mihir-s-05's
[#4464](https://github.com/CrocSwap/integer-mult-bounds/pull/4464) (head `82c7db42`). That PR answers
open question 1 of Matarener's #4457: does the actual complex caller satisfy `[D0, Q] = 0`?

## Setting

For `a ∈ F₂⁹`, write `T_a e_x = e_{x⊕a}` and `C_a = ((1+i)I + (1−i)T_a)/2`. The character of
`C_a` is `i^{a·ξ}`. The stage-zero operator is `D0 = F9·Q^{−1}`, with `F9 = Π_j C_{2^j}` and
`Q = C_q`. At each port the source records a complement `B = (b_1..b_8)` of `q` and a translation
`t` (`translation_after` in `DATA-PHASES.json`).

## What is checked, with separately written code

1. **Orthonormality.** `{q, b_1, …, b_8}` is an orthonormal basis of `F₂⁹`. So `M = [q; B]` is
   orthogonal over `F₂`, and every column count `c_i` is odd.
2. **The character identity.** `|ξ| − q·ξ ≡ Σ_j b_j·ξ + 2·t·ξ (mod 4)` holds for all 512 characters
   at every port. That is, `D0 = T_t·G_B` with `G_B = Π C_{b_j}`. Dropping `t` changes every
   character with `t·ξ` odd.
3. **New: the translation is forced, in closed form.** Evaluating the identity at `ξ = e_i` gives
   `1 − c_i ≡ 2t_i (mod 4)`, so

       t_i = [c_i ≡ 3 (mod 4)].

   This closed form equals the recorded `translation_after` at **all 112 ports**. The translation
   is therefore determined by `q` and `B`; it is not a free choice. That explains #4464's observation
   that every rank-eight normalization needs its nonzero translation. For example, at port 0 the
   first four columns of `M` have count 3, so `t = 15`.
4. **Commutation.** `[D0, Q] = 0`, checked by exact XOR convolution of kernels in `ℚ(i)` at port 0
   and at the first weight-7 port. Each `D0` kernel has 256 entries of modulus `1/16`.
5. **The port-0 witness.** `(D0 − G_B)[0, 0] = −1/16` exactly, by independent Fourier inversion, at
   `q = 11`, `B = [13,14,7,16,32,64,128,256]`, `t = 15`.
6. **New: every idle normalization is forced.** Apply the same closed form, prepending `q` when a
   frame meets the nine port bits. It reproduces `translation_after` for **all 2,016 non-empty
   recorded idle normalizations**: ranks 8, 16, 32 and 48, across 20 entries per port, with 224 empty
   entries skipped. The orthonormality of each frame is checked as well.
7. **Profiles.** `q` has weight 3 at 77 ports and weight 7 at 35. `t` has weight 4 at 77 ports and
   weight 8 at 35. Both match #4464.

## Not covered

- #4464's binding to `P3-NATIVE-COVER.json.gz`, the THREE-base canonical word, and the #4440
  controller. This check reads only `DATA-PHASES.json`.
- Native realization, rounded implementation, BIT, and cost accounting.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/stage-zero-forced-translation --check-only
python3.12 -B scripts/research_package.py --package research/stage-zero-forced-translation
```

The verifier prints `PASS_STAGE_ZERO_FORCED_TRANSLATION` in about a second, using only the standard
library.

## Open next questions

1. **Can the native caller compute translations from the closed form instead of storing them?**
   - *Why it matters:* item 6 shows that every recorded translation is determined by its frame. A
     derived value removes one class of transcription error.
   - *First step:* replace the stored field by the formula in a copy of the phase emitter, and diff
     the outputs.

## Credit

- The audit and the question are mihir-s-05's (#4464) and Matarener's (#4457).
- The phase data come from the retained QQ16/native phase lineage recorded in #4464.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
