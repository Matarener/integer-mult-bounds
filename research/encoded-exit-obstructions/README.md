# Structural levers and the encoded-output exit: exact obstructions (no κ claim)

This screens the structural targets of zxv's #5428 against the selected #5413 caller. The raw root is 0.00302728824993955878, and the fixed-profile ceiling is U = 0.00302728825, only 6·10⁻¹⁴ above it. So **any** legal paid-profile improvement would beat U. The obstacle is legality, not size.

## Main result: buying b = Z·Q·Y needs ≥ 112 paid jobs (`r17-zqy-producer-bound/`)

If the backward FULL could exit with the observation b = Z·Q·Y, the bound would rise to about 0.00714 (#5415, #5428 target 1). The break-even purchase cost is τ = 63.5226717504634927 H1-equivalents per backward FULL.

**Theorem.** Every exact, width-uniform producer of b from post-return data needs **at least 112 paid jobs per backward FULL**. Post-return data means X, Y, H, the helpers, owned zeros, and anything independent of the FULL's inputs. The bound holds for jobs of any rank or type (Clifford or not) and any sharing pattern, including:
- shared higher-rank intermediates;
- Hadamard or Fourier butterflies over ports;
- block transforms;
- joint diagonalisation.

The whole #5415 exit needs at least **120**. So #5415's constructive 120-H1 exit is **optimal**, and no producer reaches τ. This extends #5427, which shows b is not free, to paid producers.

- **Lemma 1:** tensor powers of distinct operators are linearly independent across fibre widths.
- **Lemma 2:** each paid job adds at most one vector to the span of non-base right-monomial-coset values.
- **Target:** the target needs 112 independent coset directions, 56 per mode. These are computed exactly over ℚ with the repository's `clifford_exact` evaluator, including absolute phase, in all four K conventions.
- **Controls:**
  - identity port maps give 8;
  - b written in y-coordinates gives 8;
  - the monomial target Z·Y gives 0;
  - 300 random programs never beat Lemma 2;
  - making one C gate free breaks the lemma.

**Open:** a **pre-return** copy of y or h allows an 8×H8 producer. It costs 63.598, just above τ = 63.523, so its root is 0.0030223874 < U. Beating it means beating 8 rank-8 transforms by more than 0.076 H1-equivalents per FULL. That is the centre-interface lever (#4694/#4698/#4700), which is not covered here.

## Other levers (`r16-structural-levers/`)

| Lever | Value if legal | Result |
|---|---|---|
| Split rank-9 productive helpers into independent products | +1.358e-6 per split (0.00353 if all) | **no free split point in either orientation** (exact row replay on all 632 registers; positive control passes). A non-free split recreates the relation lever closed by #5462 |
| Encoded exit via conjugated queries (term by term) | up to 0.00714 | no port or mode map commutes with Q or D; the 112 port conjugates lie in 112 distinct monomial cosets, so ≥ 120 H1 (strengthened to every producer above) |
| Larger coupled provider with a bought exit | — | needs ≥ 15 modes per FULL; the #5402 family has 8 |
| Productive centre payload; query-shear deletion; query/local fusion | — | earns 0, breaks rank-mass balance, or is illegal |
| New helper factorization (defragmentation) | ceilings 0.00499 (helpers) / 0.00371 (mains) | closed at a fixed operation set (#5426/#5422/#5465); a new operation set means a new native word and a rebuilt #5383 → #5402 → #5413 pipeline |

**What a real gain still needs:** either a new native operation set whose helper threads read port lines at frames they already visit, or the centre-interface lever.

## Reproduce

Python 3.12. The tools expect a checkout of main as the working directory; see each README.

```sh
python3.12 -B research/encoded-exit-obstructions/r17-zqy-producer-bound/tools/exit_lb.py
python3.12 -B research/encoded-exit-obstructions/r17-zqy-producer-bound/tools/lemma_sim.py
python3.12 -B research/encoded-exit-obstructions/r17-zqy-producer-bound/tools/price17.py
```

Expected outputs are stored next to each script (`*.txt` / `*.json`).

**Credits.** zxv (#5428 targets, #4359 paradigm, coded-native caller and `clifford_exact`), the #5415 and #5427 authors, Dillon Amburgey (#5402), Clear1nsight (#5413), aliromman (#5398/#5383), Cao Yifan (#4610 word), and the reviewers of the p19 line (#5270/#5440): jwr404, zxv, Matarener and Clear1nsight. Prepared by Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic) via Claude Code. Apache-2.0.
