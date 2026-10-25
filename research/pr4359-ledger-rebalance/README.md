# Rebalancing #4359's ledger: far smaller explicit ranks at the same κ

**Claim type:** an exact parameter rebalancing inside zxv's
[#4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359) ledger, with certified
explicit ranks. **No new κ:** κ stays at #4359's 0.0023, and #4359 is not accepted. This
answers the open question of my [#4410](https://github.com/CrocSwap/integer-mult-bounds/pull/4410).

## Observation

In #4359's `controller/outer_parameters.py` (head `da637c87`, SHA256 prefix `af26f4ff`), the two
compiler savings enter the 54-predicate outer ledger in only one place each:

- **The complex uniform saving.** It appears only in `new_complex_uniform_saving_above_b`, as
  `0.002304 − b`.
- **The BIT saving.** It appears only in `actual_bit_above_effective`, as `bit_saving − a` with
  `a = 0.0023025`. It reaches that predicate through the cover fallback `C1 < C0` and the atom
  conversion `a_BIT = (1 − 3/1000)·C1 + (3/1000)·a_old`.

The nine outer cost rows do not depend on either saving. Elsewhere, #4359 quotes the savings only
descriptively: `FINITE-TEMPLATE-CLOSURE.md` computes its constants from whichever finite template
is chosen. #4359 picked 0.002304 and 0.00276, far above what the ledger needs. Because the rank
exponent `H1` grows like `1/δ²`, where `δ` is half the gap between the tested mixed saving and
the uniform saving, that choice is what makes the ranks astronomical.

## Rebalanced choice

| Parameter | #4359 | Here |
| --- | --- | --- |
| `b` | 0.002303 | 0.00230255 |
| complex uniform saving | 0.002304 | 0.0023026 |
| BIT `C0` (before cover) | 0.00276 | 0.002311 |
| BIT `C1` (after cover) | 0.00275 | 0.00231 |
| exact ordinary BIT saving | 0.0027418653797 | 0.0023031853797 |
| admitted BIT saving | 0.0027 | 0.002303 |
| cover prime rule | `q > 2.56·10⁷ N⁵` | `q > 2.56·10⁸ N⁵` |

All 54 ledger predicates stay strictly positive. The tightest is `stop`, at 10⁻⁸ and unchanged. Next come
`(1−stop)b − a` and `uniform − b`, both about `5·10⁻⁸`. The BIT conversion conditions also hold: `atom > a_BIT > admitted`,
`atom < 1 − a_BIT`, and a strict fallback moment. The nine outer margins are unchanged, so κ
stays 0.0023.

## Ranks

The superpotentials are certified at #4359's unchanged tested savings, 0.002305 and 0.002769.
Ranks use #4405's refined induction, which my #4410 checked:

| Family | #4359 | #4405 | **rebalanced** |
| --- | --- | --- | --- |
| Complex | `2^276540184361` | `2^1546084442` | **`2^268300549`** |
| BIT | `2^6552928412` | `2^42843607` | **`2^14664`** |

The BIT exponent drops by a factor of about 2,900 from #4405's, and the complex exponent by a
factor of 5.8. The verifier also recomputes both earlier columns from their own formulas, as
controls.

## Transfer-audit functional checks

The 19 functional checks in #4359's `transfer-audit/outer_transfer_audit.py` are also transcribed.
They include `new_uniform_complex_above_selected_b`, `actual_ordinary_BIT_above_effective`, the
`λ` gaps and the guards. All 19 are positive both at #4359's values and at the rebalanced ones.

## Transcription control

The ledger is transcribed, with credit to #4359, and parameterized by `b` and the two savings.
At #4359's values it reproduces the nine published margins exactly, from main transform
0.00230197698 to microbox 77.00004, and all 54 predicates. It also reproduces #4359's exact BIT
conversion, 27418653797/10¹³.

## Not covered

- **Every hypothesis of #4359:** native closure, adapters, the delayed cover, and the precision
  and storage closure. Those constants must be recomputed for these different finite templates,
  exactly as #4359 requires for its own.
- **The 13 historical-endpoint predicates** of the inherited 63-predicate ledger. #4405 reports
  that they compare only κ against earlier endpoints, which this rebalance leaves unchanged.
- **An actual winning template.** None is materialized.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4359-ledger-rebalance --check-only
python3.12 -B scripts/research_package.py --package research/pr4359-ledger-rebalance
```

The verifier prints `PASS_PR4359_LEDGER_REBALANCE` in about one second, using only the standard
library.

## Open next questions

1. **How small can the complex rank get at κ = 0.0023?**
   - *Why it matters:* the complex tested saving can rise toward the root 0.00230509, and `b`
     toward `a`.
   - *First step:* jointly optimize `(t, b, uniform)` under the ledger.

## Credit

- The construction, ledger and invoices are zxv's (#4359).
- The refined induction is 1337isnot1337's (#4405).
- Theorem 1G is Jacob Alan Sussman's (#4268).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
