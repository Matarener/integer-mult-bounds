# #4416's p7 invoice, rebuilt from its literal controller word

**Claim type: an independent exact replay and assembly. No new κ.** It
answers the open question of my
[#4420](https://github.com/CrocSwap/integer-mult-bounds/pull/4420) for the
part of #4416's invoice that is new.

## Object

#4420 certified #4416's strictification inequalities at κ = 0.00268647, but
took its invoices from #4416's inventory. There `α` clears its requirement by
only `5.6·10⁻⁹`, while one extra rank-one paid call would move `α` by about
`7.6·10⁻⁶`. So the invoice itself is the weak link:

```text
T = {5:420, 6:270, 7:840, 8:1395, 9:3195, 25:448, 41:448, 57:448, 121:224},
P = {1:37305, 2:10695, 3:3360, 4:1530, 5:300, 8:1464, 16:448, 32:448, 48:448}.
```

## Result

**The invoice is rebuilt exactly** from `P7-FACTOR.json`'s literal word, the
112 port recipes on main, and the supplier receipt.

1. **Laurent identity.**
   - **The replay.** All 70 physical events are replayed as an exact
     Laurent matrix `M` over `Q, D0..D14`, under #4416's stated native
     contract (`F_s = D_s S_y(Q⁻¹)`, `B_s = D_s S_x(−Q)`).
   - **The scalar programs.** The left and right programs replay to the
     stored matrices.
   - **The identity.** `left · M · right` equals the stated diagonal of 14
     monomials exactly, and every replayed coefficient matrix equals the
     stored one.
2. **Main targets.**
   - Each role's rank is `1 + 8·(number of D exponents)`, over the 112 ports,
     giving `{25:448, 41:448, 57:448, 121:224}`.
   - The exponent alphabet is `Q^±1` with `D_s ∈ {0,1}`.
3. **Paid idles.**
   - The 12 retained windows are exactly the literal `IDLE` events, and the
     keep mask 232127 selects exactly those windows.
   - Each window pays rank `8·|stages|` on both roles of its pair at every
     port, giving `{8:1344, 16:448, 32:448, 48:448}`.
4. **Supplier.** Over the 15 native calls:
   - the THREE-base helper widths `{5:28, 6:18, 7:56, 8:93, 9:213}` give the
     helper targets;
   - its unsplit paid profile `{1:2487, 2:713, 3:224, 4:102, 5:20, 8:8}`
     (forward equal to backward) gives the rest of the paid calls.
5. **Total.** `T` and `P` equal #4416's invoice. The rank-one masses are
   131,723 and 131,115.

**Control.** Flipping one reversed native call breaks the Laurent identity.

## Method and independence

- **No #4416 code.** Nothing is imported or run from #4416. The Laurent
  polynomials, scalar programs and assembly are my own code. The native call
  contract is #4416's stated input, replayed and not derived.
- **Inputs.** `P7-FACTOR.json` and the supplier receipt are the files whose
  SHA256 values #4416's own RESULT.json records. All three are vendored
  byte-identically. The port recipes are `adaptive-kernel-demotion`'s
  `DATA-PHASES.json` on main, with the same SHA256.

## Not covered

- **The supplier's numbers.** Its helper widths and paid profile are taken
  from its receipt, part of #4359's lineage. Its native replay is not redone
  here.
- **The physical premises.** The native local contract itself, and the
  121-axis physical admission of contacts, endpoints and phases.
- **Downstream.** The tensor, completion and outer arguments.

## Reproduce

```sh
python3.12 -B research/pr4416-invoice-rebuild/verify.py
```

It prints `PASS_PR4416_INVOICE_REBUILD` in under a second, using only the
standard library.

## Open next questions

1. **Replay the THREE-base supplier's paid profile from its native
   certificate.**
   - *Why it matters:* it contributes `15 · 2487` rank-one calls, so a
     difference of one call per invocation moves `α` well past its margin.
   - *First step:* census
     `THREE-base-FULL-IDENTITY-NATIVE.json.gz` with separate code.
   - *Blocked by:* nothing.

## Credit

The controller, word and invoice are 1337isnot1337's (#4416, with OpenAI
Codex assistance), building on zxv's #4359. Prepared by Ryanson Jonathan with
substantial Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
