# Independent review of #4417's nonlinear centre-sharing floor

**Claim type:** a written proof review plus a separately implemented recomputation of the
packing screen. **No new κ.** The object is Matarener's
[#4417](https://github.com/CrocSwap/integer-mult-bounds/pull/4417) at head `2b101115`.

## Proof review

**Theorem 1 holds as stated, under the inherited premises.**

- **Injectivity.** On `V ⊂ ker H`, the history is identically 0. The decoder `D(0, E(x)) = Q(x)`
  together with `Q|_V` bijective forces `E` to be injective on `V`, which has real dimension
  `16d`.
- **Adaptivity.** Reads that depend on earlier fresh reads do not escape this. The whole
  observation is still one function `E : V → ℝⁿ`, with `n` the maximum number of reads, padded.
  In the continuous case it is a continuous injection, so invariance of domain gives `n ≥ 16d`.
- **Branching.** With finitely many semialgebraic branches, `V ∩ box` splits into finitely many
  semialgebraic pieces. One piece has dimension `16d`. An injective semialgebraic map preserves
  dimension, so again `n ≥ 16d`.

**Theorem 2** is a counting argument. Injectivity on `2^{16db}` grid points needs at least that
many values, so the widths sum to at least `16db`. Kronecker packing attains this, as `verify.py`
re-checks on six small grids.

## Screen recomputation

`verify.py` reimplements the relaxation of `research/complex-local-word-ceiling` without importing
it:

- per call, `w = 896/9`;
- coverage mass `(m−1)w + centre`;
- the idle mass goes into fractional rank-`R` children, with `R = 51` the largest rank satisfying
  `m² > 2R²` at `m = 73`;
- certified interval logarithms and exponentials;
- a bracket to `10⁻¹²`.

All six rows match #4417 to `10⁻¹¹`:

| Row | `a_hi` | ratio |
| --- | --- | --- |
| selected, 8 × rank-8 | 0.001690054109 | 1.000000 |
| 4 × rank-16 | 0.001693625547 | 1.002113 |
| 2 × rank-32 | 0.001697207887 | 1.004233 |
| 1 × rank-64 | 0.001700801148 | 1.006359 |
| ideal fractional rank-72 | 0.001701412821 | 1.006721 |
| control: halved information (4 × rank-8, centre 32) | 0.003212972894 | 1.901107 |

**Extremality of rank 72.** A child of rank `r` costs `(r/m)^{1−a} = r · r^{−a}m^{a−1}`, so the
cost per unit mass `r^{−a}m^{a−1}` is nonincreasing in `r`; the verifier checks this with
certified bounds. Any regrouping of the 64 centre units into children of rank at most
`m − 1 = 72` therefore has a moment at least that of the fractional rank-72 relaxation. That
makes +0.67% an upper bound for every packing, as #4417 states.

## Not covered

- The premises of centre-history-innovation, such as the common frame, the cover view and the
  call-10 query.
- #3918's rank-8 carrier premise.
- Terminal-only consumers.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4417-centre-review --check-only
python3.12 -B scripts/research_package.py --package research/pr4417-centre-review
```

The verifier prints `PASS_PR4417_SCREEN_REVIEW` in about 20 seconds, using only the standard
library.

## Open next questions

1. **Does a carrier other than rank-8 channels change the 64-unit centre mass?**
   - *Why it matters:* this is #4417's open question 2, and the screen caps the ideal gain at
     +0.67%.
   - *First step:* price one alternative carrier's restoration bill.

## Credit

- The theorems and the screen are Matarener's (#4417).
- The relaxation model is Douglas Colkitt's complex-local-word ceiling.
- The premises are Jose Manuel's centre-history-innovation and #3873.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
