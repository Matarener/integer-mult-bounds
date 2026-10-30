# Audit of PR6114's controller income bound

**Independent adversarial audit; no new κ; the selected record is unchanged.**

[PR #6114](https://github.com/CrocSwap/integer-mult-bounds/pull/6114) (Matarener, head `3183c655`) proves a
theorem about the literal p16 Laurent caller alphabet of
[`research/p104-productive-controller/caller.py`](../p104-productive-controller/caller.py). Starting from a
constant invertible boundary, a caller word with `s` paid odd shears (`LOCAL`, `QUERY_SHEAR`) twists at most
`s − 1` outputs. So the controller income per port is at most `thick calls − 1`, and the three retained controllers
attain this (17 = 18 − 1). This package checks that theorem independently.

## Result

* **The theorem holds** for the literal alphabet. I re-derived the proof, and a separate engine reproduces every
  number. That engine is written here without importing `caller.py` or PR6114's code. It runs an exact symbolic
  Laurent replay of all three controllers to the declared odd diagonal. It also tracks the even-part rank after
  every event under a different specialization: `Q² → 13/7, 19/11`, with random nonzero stage values where
  PR6114 sets `D_s → 1`.

  | Controller | thick + thin | twisted | even-rank trace | lifts = Σ\|S_i\| | income |
  |---|---:|---:|---|---:|---:|
  | `kappa-backward-controller-20261023` | 18 + 15 | 32 | 32, 32, 31, …, 0 | 194 | 17 |
  | `joint-helper-lattice` | 18 + 15 | 32 | 32, 32, 31, …, 0 | 194 | 17 |
  | `p104-productive-controller` | 18 + 15 | 32 | 32, 32, 31, …, 0 | 194 | 17 |

* **Two gaps in the written proof, both closed** ([PROOF.md](PROOF.md) A1–A2). First, the last inequality uses
  zero rows of `L·M`, not of `M`. A left-kernel argument repairs it, and `L` need not be invertible. Second, the
  invoice step "every output stage was paid once as a lift" was asserted, not proved. It follows from the
  determinant, stage by stage, for every word whose outputs form the full monomial diagonal. The verifier checks
  all 33 stages and the central exponent on each controller.
* **The scope claim needs correcting** (A4). PR6114 says a paid primitive touching several banks or ports is
  "the only way" to beat the bound. For a paid job `A = A_e + Q·A_o`, Sylvester's inequality bounds the even-rank
  drop by `(n − rank A_e) + rank A_o`. When no odd content exists yet, the bound is `n − rank A_e`. From that:
  * Every paid job that writes **one** row `y ← u·y + Σ f_j·x_j` obeys PR6114's bound exactly, including the
    `− 1`. This needs the self-coefficient `u` to be nonzero and even. The sources can be any number of banks,
    and the `f_j` can be any Laurent coefficients.
  * Three escapes exist, each with an exact control: a paid **one-bank** odd translation `y ← Q·y` (1 twist from
    1 job); a **Laurent entry boundary** (2 twists from 2 shears); and a **two-row** job (2 twists from 1 job).
    None of them is in the literal alphabet, so PR6114's conclusion stands.

Not audited: the surplus formula `M = v·income − n_thick·c` and `c = 56`/`760` on the PR5907 word, and the
moment side.

## Reproduce

```sh
python3.12 -B research/p104-controller-income-audit/verify.py
python3.12 -B scripts/research_package.py --package research/p104-controller-income-audit
```

The run takes under a second and uses only the standard library. Engine: [audit.py](audit.py). Evidence:
[RESULT.json](RESULT.json), compared in full. The random one-destination words (n = 2, 4, 6; 3,909 paid jobs)
never exceed the bound. In 41 of them the even-rank deficit `n − rank E` equals `s − 1`. This counts the rank
deficit only; the test builds no twisted outputs. They support the A4 proof and do not replace it.

## Open next questions

1. **Can Escape 1 or 2 be realized physically at the P104 caller?** A legal paid odd translation `Q^{±1}`, or a
   supplier boundary that already carries odd content, would lift the cap from `thick − 1` to `thick` per port.
   That is up to 104 rank units on the PR5907 word, before the primitive's own charge is paid. First step: price
   `Q^{±1}` as a native job in the terms of `caller.py`'s `physical()`. Blocker: the literal alphabet rejects it
   as a free event, and no native realization is known here.
2. **What twist capacity do the available multi-row paid jobs have?** For any candidate job, compute
   `(n − rank A_e, rank A_o)` before searching, and compare the result with its paid rank. Blocker: there is no
   priced inventory of multi-bank primitives.

## Credit

PR6114 and its theorem: Matarener (prepared with Claude). The retained controllers come from Cinna Davis (p16/a7
lattice) and Ali Romman (PR5398 replay, all-forward wrapper). The binary predecessor theorem is Cinna Davis's
`research/productive-controller-basis-search`. Audit by Josie Elliston, prepared with Claude Code (Opus 5.5).
Apache-2.0.
