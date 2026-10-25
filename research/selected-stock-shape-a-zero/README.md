# Selected stock shape: A = 0 at the m=73 complex producer

**Card `selected-stock-envelope`, scope refined** to the missing shape constant
A left open by [`research/selected-stock-envelope-m73`](../selected-stock-envelope-m73/)
(PR [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113)). That
package already bound the finite per-level stock allowance `B_bits = 2642` and
the halving guard; this package does not recompute those. It proves that the
retained finite-stock candidate for the per-level divisor `C(w)` is independent
of atom width `w`, so

```text
log_2 C(w) <= A * w + B
```

holds with **A = 0** and **B = 2642**. The leaf constant `rho` stays unbound.
No new kappa (selected decimal `0.001672660197076918`).

```sh
python3.12 -I -B research/selected-stock-shape-a-zero/verify.py
```

Expected:

```text
PASS_SELECTED_STOCK_SHAPE_A_ZERO A=0 B_bits=2642 rho=unbound no_digit_tower_lift no_new_kappa
```

Python 3.12, standard library only. Default verify is read-only: it re-hashes
six pinned inputs, admits against `CERTIFICATE.json`, and rejects mutation
controls. Admission uses `need()` and stays enforced under `python -O`.

## Why A is zero here and positive for ordinary BIT

| Producer | Level cover | Atom-width factor | Shape A |
|---|---|---|---:|
| Ordinary BIT m=64 | `GL_m(Z/q^w Z)` | `q^{m^2(w-1)}` digit tower | ≥ 4096 |
| Complex m=73 | finite `Sp(72,2)` / `O(·,2)` over `F_2` | none | **0** |

The ordinary digit tower and the bound `log_q W_q(w) < 4096 w + 1` are cited
from [`research/selected-bit-parent-reserve`](../selected-bit-parent-reserve/)
(PR [#2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084)) and
`notes/three-stage-cover-bit.tex`. The complex cover note parametrizes Sp→O
lifts by `u ∈ U`, `c ∈ F_2` and retains finite role counts; it has no `W(w)`
and no `q^{m^2(w-1)}`. The selected invoice charges fixed `|Sp(72,2)|` and
fixed 14,826 families — already reduced to `B_bits = 2642` by #3113 — with
zero discrete slope across atom widths.

## Composition under A = 0

```text
sigma <= (43/26) * (1 - s) * 2642 + rho
```

This collapses the `(A+B)` term but is not a closed envelope: `rho` remains
open, and adopting the finite stock as uniform `C(w)` is still the admission
named in `research/selected-coarse-depth-stock/PROOF.md`. Historical `57604`
and slack `252` are not substituted.

## Reproduce

```sh
python3.12 -I -B research/selected-stock-shape-a-zero/verify.py
python3.12 -I -O -B research/selected-stock-shape-a-zero/verify.py
python3.12 -I -B research/selected-stock-shape-a-zero/independent.py
python3.12 -I -B research/selected-stock-shape-a-zero/test_package.py
python3.12 -B scripts/research_package.py --package research/selected-stock-shape-a-zero
```

`test_package.py` rejects duplicate JSON keys, a temp-corrupted certificate
(`shape_A` flipped to 1), hash failures, and a fake `w` injected into the Sp
formula, and checks that package files are unchanged after replay.

## Open next questions

1. **Bind `rho` (or prove `rho = 0`).** With A = 0 the composition is
   `(43/26)*(1-s)*2642 + rho`. First step: locate a complex analogue of the
   ordinary completed-leaf hypothesis. Blocked by: no per-leaf recurrence in
   the retained complex sources.
2. **Adopt finite stock as uniform `C(w)`.** A = 0 is for that candidate.
   First step: exhibit one selected residual that consumes a fresh complete
   physical-role packet whose cardinality equals the finite stock at every w.

## Credit

Aaron Wang / #3113 bound `B_bits = 2642` and recorded the missing shape lemma.
Sricharan Vagvala / #2105 supplied the coarse `43/26` depth and conditional
ledgers. Adam Gall / #2084 bound the ordinary BIT parent envelope that supplies
the positive-A contrast. The complex cover note and selected Sp(72,2) invoice
lineage are retained predecessors. Their notices are unchanged.

Prepared by Wentao Li with substantial AI assistance.
