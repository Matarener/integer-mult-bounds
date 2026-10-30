# Log_q parent term for the finite m=73 stock

**Partial coefficient correction. No new κ.** Selected κ stays
`0.001672660197076918`. Every `actual_stock_coefficient` in the bootstrap
receipt stays null.

`research/selected-stock-shape-a-zero` proves that the finite stock candidate

```text
C = |Sp(72, 2)| * 14826
```

satisfies `log2(C) < 2642` with shape slope `A = 0`. It then displays

```text
sigma <= (43/26) * (1 - s) * 2642 + rho
```

inside the composition from `research/selected-coarse-depth-stock/PROOF.md`.
That composition takes `A` and `B` from a **base-q** hypothesis
`log_q C(w) <= A*w + B`, not from a base-2 hypothesis.

## Corrected parent term

For every prime `q > 2^80` (the floor in
`docs/research/selected-bootstrap-scope-map.md`),

```text
log_q C = log2(C) / log2(q) < 2642 / 80 = 1321/40.
```

The `2642` substitution is still a valid sufficient digit bound, because
`log_q C < 2642` for every `q >= 2`. On the stated prime floor it is exactly
**80 times** looser than `1321/40`.

Let `s` be a recorded branch saving and write `T(s) = (43/26)*(1-s)*(1321/40)`.
Under the coarse-depth depth bound and the finite-stock reading `C(w) = C`, any
leaf hypothesis `log_q S_leaf <= rho * w * (1 + log2 e)` gives the sufficient
envelope coefficient

```text
sigma = T(s) + rho.
```

The inequality is strict before adding `rho`, so this `sigma` dominates
`log_q S_parent`. Both recorded savings reproduce `1 - s` as the receipt's
uniform stock gap:

| Branch | Sufficient parent term `T(s)`, rho separate |
|---|---|
| `bootstrap` | `174485626749443905524883973467613250556094475116027 / 3200000000000000000000000000000000000000000000000` |
| `conservative_bootstrap` | `4362140668748600743658666134074946636014640956718493 / 80000000000000000000000000000000000000000000000000` |

Both are `< 64`. Stage 1 of each branch still has headroom `6562783`. That
comparison does **not** adopt an envelope: a large guard gap is not a selected
coefficient, and `rho` is still missing.

`rho = 0` is the homogeneous leaf bound only when `S_leaf = 1`. A one-digit
leaf has `log_q(q) = 1`, which is not `<= 0`.

## What this does not establish

- It does not choose `actual_stock_coefficient`.
- It does not prove `S_leaf = 1` or bind `rho`.
- It does not show that the assembler charges `C` at every atom width. That
  identification is the finite-stock hypothesis already named by the
  coarse-depth proof and used by the shape note.
- It does not rerun cutoff margins, import `57604` or `252`, or change κ.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/selected-stock-logq-parent/verify.py
python3 -B research/selected-stock-logq-parent/test_verify.py
python3 -B scripts/research_package.py --package research/selected-stock-logq-parent
```

Expected marker:

```text
PASS_SELECTED_STOCK_LOGQ_PARENT bits=2642 q_floor=80 factor=80 ... rho=unbound coefficient=null headroom_not_adoption no_new_kappa
```

## Open next questions

1. **Bind `rho`, or prove `S_leaf = 1`.** The corrected envelope is `T(s) + rho`.
   A one-digit leaf already rules out reading `rho = 0` off the parent term.
   First step: one complex residual whose external leaf packet is counted.
   Blocked by: no per-leaf recurrence in the retained complex sources. The
   inherited slack `252` is not that coefficient.
2. **Adopt `C` as the stage-1 divisor.** Both the base-2 shape theorem and this
   translation assume the finite stock is `C(w)`. First step: match one
   stage-1 residual to that cardinality at two atom widths. Blocked by: the
   complex cover note has no `W(w)` formula.

## Credit

The base-2 shape `A = 0`, `B_bits = 2642` is Wentao Li's
`research/selected-stock-shape-a-zero`, from Aaron Wang's
`research/selected-stock-envelope-m73`. The log_q composition and the `43/26`
depth factor are `research/selected-coarse-depth-stock` (Sricharan Vagvala's
conditional rate, as retained there). The savings and null coefficient fields
are Josie Elliston's bootstrap receipt in
`research/selected-bootstrap-stock-audit`. The prime floor `q > 2^80` is the
selected bootstrap scope map. Hiroki KUMAZAKI's stock-margin chain and Nick
Petalas's independent tie-out leave the same coefficient null; this note does
not replay their cutoff arithmetic.

Prepared by unpaidmoon with substantial AI assistance (Cursor Grok). No
independent human review is claimed. Apache-2.0.
