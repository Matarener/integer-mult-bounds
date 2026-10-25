# Independent check of #4416's moment and paid-tail inequalities

**Claim type: an independent certified finite check. No new κ.** This does
not accept #4416. It checks none of its native audit, outer ledger or
inherited premises.

## Object

[PR #4416](https://github.com/CrocSwap/integer-mult-bounds/pull/4416)
(1337isnot1337, head `e9058860`) claims a conditional κ = 0.00268647, the
highest open claim when this check ran. Its strictification (TENSOR.md §3–4)
needs, at saving `C = 0.00268648` with `τ = 1 − C`:

```text
alpha = P_tau/T_tau < 1 - 1/10^8,
gamma = P_1/(10^C T_tau) < 4991/5000,
delta = 7688*11/(10^C T_tau) < 2/3,
alpha^6240 + 2 gamma^6240 + 2 delta^6240 < 1.
```

Here `X_τ = Σ n_r r^τ`, over the raw p7 invoices `T` (7,688 targets) and `P`
(55,998 paid calls). No outside check existed.

## Results

Every link holds, recomputed with exact rationals and enclosure widths below
`10⁻³⁰`:

| Link | Value | Required |
| --- | --- | --- |
| `alpha` | `0.999999984403908…`, so `1 − alpha = 1.56·10⁻⁸` | `< 1 − 10⁻⁸` |
| `gamma` (`c = 10`) | `0.998191712473…` | `< 4991/5000` |
| `delta` (`b = 11`) | `0.643824709152…` | `< 2/3` |
| `(4991/5000)^390 < 1/2`, `(2/3)² < 1/2`, `6240 = 16·390` | exact | — |
| Normalized bound `1/(1 + 6240/10⁸) + 4/2¹⁶` | `10240625039/10240638976` | `< 1` |
| Gap | exactly `13937/10240638976 = 1.36095…·10⁻⁶` | as stated |

**Binding.** The invoices in RESULT.json's strictification block equal its
native-inventory block and the two lines in TENSOR.md:

- the counts are 7,688 and 55,998;
- the rank-one moments are 131,723 and 131,115, a surplus of 608;
- the ambient is 121.

All three enclosures overlap #4416's recorded intervals.

**Headroom: the tested saving is at this invoice's ceiling.** As the tensor
power grows, the construction works for every `C` with `alpha < 1`; `gamma`
and `delta` stay below 1 there. The limit saving, where `alpha = 1`, is

```text
C* = 0.002686489049…,      C* − 0.00268648 = 9.05·10⁻⁹.
```

So #4416's κ = 0.00268647 uses essentially all the headroom of this native
p7 invoice. A higher κ on this route needs a different invoice, not a larger
tensor power.

**Controls.**

- Completing every target to the full ambient (`b = 121`) gives `delta > 1`.
- The undamped rank-one tail `P_1/T_τ` exceeds 1.

So both damping choices are needed, as TENSOR.md says.

## Not covered

- The native audit that produces `T` and `P`. These are taken from #4416's
  inventory, not rebuilt from the word.
- The tensor composition, completion and splitting proofs, which are written
  arguments.
- The compiler ranks, the nine outer cost rows and every inherited physical,
  precision and analytic premise.

## Reproduce

```sh
python3.12 -B research/pr4416-moment-check/verify.py
```

It prints `PASS_PR4416_MOMENT_CHECK` in about 90 seconds, using only the
standard library. `vendor/` holds #4416's TENSOR.md and RESULT.json,
byte-identical and SHA256-checked.

## Open next questions

1. **Rebuild `T` and `P` from #4416's native word.**
   - *Why it matters:* the moment margin is only `5.6·10⁻⁹` above what
     `alpha` needs. One extra paid call of rank 1 changes `alpha` by about
     `1/131723`, far more than that margin.
   - *First step:* census #4416's p7 native word with separate code.
   - *Blocked by:* nothing.

## Credit

The construction and the invoices are #4416's (1337isnot1337, with OpenAI
Codex assistance), building on zxv's #4359, #4405, #4412 and #4414, and Jacob
Alan Sussman's Theorem 1G. Prepared by Ryanson Jonathan with substantial
Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
