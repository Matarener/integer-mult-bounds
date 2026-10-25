# Joint log_q coefficient under the complex layer's leaf hypothesis

**Conditional coefficient identity. No new κ.** Selected κ stays
`0.001672660197076918`. Every `actual_stock_coefficient` in the bootstrap
receipt stays null.

Two merged notes give the two factors of the coarse-depth envelope and do not
state the coefficient that uses both.

- [`research/selected-stock-logq-parent`](../selected-stock-logq-parent/README.md)
  (PR [#4141](https://github.com/CrocSwap/integer-mult-bounds/pull/4141)) proves
  that on every prime `q > 2^80`,

  ```text
  log_q C < 2642/80 = 1321/40,
  ```

  and writes the sufficient parent term `T(s) = (43/26)*(1-s)*(1321/40)`.
  It leaves `rho` unbound. A one-digit leaf shows that `rho = 0` does not
  follow from the parent term alone.

- [`research/selected-stock-rho-ledger`](../selected-stock-rho-ledger/README.md)
  (PR [#3667](https://github.com/CrocSwap/integer-mult-bounds/pull/3667))
  concludes, from the selected complex layer, that external completed leaves
  take no row stock: `S_leaf = 1` and `rho = 0`. Its published reading-(a)
  coefficient still multiplies the base-2 length,

  ```text
  sigma <= (43/26)*(1-s)*2642 ≈ 4362.14
  ```

  at native stage 1. That substitution is a valid but loose digit bound. It is
  exactly 80 times `T(s)`.

## Result

Assume the coarse-depth expansion

```text
log_q S_parent(e,w)
  <= (43/26)*(1-s)*log2(e)*log_q C(w) + log_q S_leaf(e,w)
```

together with `log_q C < 1321/40`, `S_leaf = 1`, integer atom width `w >= 1`
and width `e >= 2`. Then

```text
log_q S_parent(e,w) < T(s) * w * (1 + log2(e)).
```

So `T(s)` is a sufficient envelope coefficient. The rho-ledger's reading-(a)
value on the same saving is exactly `80*T(s)`, not a different shape.

The shape step does not depend on a numerical logarithm. For `A = 0` and
`L = log2(e) >= 0`,

```text
w*(1+L) - L = w + (w-1)*L.
```

The constant term `w` and the slope `w-1` are both nonnegative for every
integer `w >= 1`. For `e >= 2` one has `L >= 1`, so the difference is at
least `1` and the embedding is strict. The digit bound on `C` is already
strict, so the stock inequality is strict as well.

`rho = 0` is the leaf hypothesis `log_q(1) = 0`. It is not the claim that a
one-digit external leaf would fit: `log_q(q) = 1` is still outside that
bound. The layer hypothesis is what supplies `S_leaf = 1`.

Both recorded savings reproduce the receipt's stock gap `1-s`:

| Branch | Joint coefficient `T(s)` | Published reading (a) |
|---|---|---|
| `bootstrap` | `174485626749443905524883973467613250556094475116027 / 3200000000000000000000000000000000000000000000000` | `80*T(s)` |
| `conservative_bootstrap` | `4362140668748600743658666134074946636014640956718493 / 80000000000000000000000000000000000000000000000000` | `80*T(s)` |

Both joint values are strictly below `64`. Stage-1 headroom remains
`6562783`. That comparison does **not** adopt an envelope: the receipt
coefficient stays null, and the rho-ledger already records that no selected
bootstrap step calls this complex layer.

## What this does not establish

- It does not choose `actual_stock_coefficient`.
- It does not re-prove the layer closure. `S_leaf = 1` is #3667's conditional
  conclusion from PR2287, PR2250, PR2234 and PR2899. Those texts are not
  replayed here.
- It does not show that the assembler charges `|Sp(72,2)|*14826` as `C(w)`
  at two atom widths. That identification remains the finite-stock hypothesis
  named by the coarse-depth proof.
- It does not rerun cutoff margins or change κ.
- The selected bootstrap coefficient, if it is the ordinary BIT producer's,
  is a different object. #3667 already separates that producer from this layer.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/selected-stock-logq-rho-joint/verify.py
python3 -B research/selected-stock-logq-rho-joint/test_verify.py
python3 -B scripts/research_package.py --package research/selected-stock-logq-rho-joint
```

Expected marker:

```text
PASS_SELECTED_STOCK_LOGQ_RHO_JOINT digits=1321/40 factor=80 ... rho=0 S_leaf=1 coefficient=null layer_not_bootstrapped headroom_not_adoption no_new_kappa
```

## Open next questions

1. **Does a later selected assembler bootstrap this complex layer?** The joint
   coefficient becomes a stage obligation only for a call that actually uses
   the layer. The pinned rho-ledger says the current assembler does not.
   First step: re-read that call if `code/assemble.py` changes. Blocked by:
   the retained assembler builds the bit chain and passes the complex root
   only as a saving cap.
2. **Match `C(w)` at two atom widths before treating `T(s)` as charged.**
   Both factors above still assume the finite stock is the uniform divisor.
   First step: read the open stage-one recurrence audit rather than starting
   another divisor search. Blocked by: the complex cover note still has no
   `W(w)` formula, and this package does not add one.

## Credit

The corrected parent term is unpaidmoon's
`research/selected-stock-logq-parent`, from Wentao Li's base-2 shape
`A = 0`, `B_bits = 2642` and Sricharan Vagvala's coarse-depth composition.
The leaf conclusion `S_leaf = 1` and the loose coefficient
`(43/26)*(1-s)*2642` are Mainzu's `research/selected-stock-rho-ledger`.
The stage receipt is Josie Elliston's, as retained by the bootstrap stock
audit. The prime floor `q > 2^80` is the selected bootstrap scope map.
This package adds the shape comparison and the exact factor-80 identity
between those two published coefficients. It does not replace either proof.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No
independent human review is claimed. Apache-2.0.
