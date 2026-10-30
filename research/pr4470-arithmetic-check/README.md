# Independent arithmetic check of #4470 (conditional κ = 0.00302015)

**Claim type:** an independent arithmetic check with certified interval logarithms. **No new κ.** It
covers 1337isnot1337's [#4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470) (head
`b9a13c16`), which proposes conditional κ = 0.00302015 through joint helper boundaries. It follows my #4455,
which checks the p17 chain #4440–#4453, and reuses that package's interval helpers, copied here so this
package is self-contained.

## What is checked

1. **The p16 invoice.** 64,620 paid jobs and 10,928 productive fields. Rank masses 239,886 (target) and
   239,134 (paid), surplus 752.
2. **The local change against #4447.** The B/480 paid profile shared by #4447 and #4453 (per #4453's
   table) changes from {1:2254, 2:514, 3:444, 4:103, 5:40, 8:8} to {1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}.
   That is **53 fewer paid jobs** per local call. The helper profile changes from
   {4:26, 5:2, 7:29, 8:42, 9:309} to {4:28, 7:7, 8:47, 9:326}. Both rank masses rise by **37**.
3. **The surplus-gain polynomial.** It is `17 + 126·2^t − 50·3^t − 42·4^t + 2·5^t − 22·7^t + 5·8^t + 17·9^t`,
   derived independently from the two profiles. It vanishes at `t = 1`, and **its derivative is certified negative on
   `[0, 1]`** by interval bounds on 256 subintervals. So the gain is positive on `(0, 1)`, matching #4470's
   own derivative-cover proof by independent code.
4. **The raw root.** With certified intervals, `T_t > P_t` at 0.0030201659770 and `T_t < P_t` at
   0.0030201659771, which reproduces #4470's enclosure.
5. **The tails** at the tested saving `604031/200000000`, `u = 1/5`, cutoff 20, floor 21:
   - `α < 1 − 10⁻⁹`;
   - `γ = 0.956176646498 < 0.97`;
   - `δ = 0.958284435309 < 0.97`.

   All three match #4470's printed values. Since `0.97^{1024} < 2^{−32}`, the normalized paid bound
   `1/(1 + 1024·10⁻⁹) + 4·2^{−32} = 2097152001953127/2097154147483648 < 1` also reproduces exactly.

6. **The logarithmic compiler**, at ambient `145^{1024}` (the largest target rank), `θ̄ = 63/64` and
   `p = 1000`:
   - `θ = log 20/log 21 < 63/64`;
   - `2^{b−a}r^b ≤ m^a`;
   - `θ̄^p < η`;
   - `m^{1−t} < 2^p`;
   - `z − t = 1/1400000000` exactly;
   - the stated `H = 64,215,200,000,000` satisfies `(1+H)^p < 2^{(z−t)H}`.

7. **The outer ledger.** All nine outer rows reproduce **exactly** from #4470's printed parameters
   with the FINE-PRIME row formulas:

   | Row | Formula |
   | --- | --- |
   | main transform | `εq` |
   | global router | `a` |
   | fused Gaussian | `1−ε+qβ` |
   | group bit router | `1−ε+aβ` |
   | group scans | `1−ε+β` |
   | polynomial products | `ε` |
   | sparse union movement | `ξ+1/2−ε` |
   | micro-box faces | `79−ε−β` |
   | boundary algebraic matrix | `3/32+ξ−ε` |

   The binding row is the main transform, at `κ + 4195771787/1960000000000000000`.

## Not covered
- The native word and the controller replay.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4470-arithmetic-check --check-only
python3.12 -B scripts/research_package.py --package research/pr4470-arithmetic-check
```

The verifier prints `PASS_PR4470_ARITHMETIC_CHECK` in about 2 seconds, using only the standard library.

## Open next questions

1. **None arithmetic.** What remains for #4470 is the native word and the controller replay.

## Credit

- The construction and the claim are 1337isnot1337's (Cinna Davis, #4470).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
