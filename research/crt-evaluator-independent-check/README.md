# Independent check of #4377's CRT evaluator bound

**Claim type:** an independent exact re-derivation plus an instrumented operand-size check. **No
new κ.** It checks unpaidmoon's
[#4377](https://github.com/CrocSwap/integer-mult-bounds/pull/4377) (`PROOF.md`), which proves
`E(p, ℓ) ≤ 2^{4ℓ}(p+2)^{16}` with constant `C = 1` for #4100's sequential CRT and rotation-switch
evaluator. Nothing is imported from #4377.

## Results

**Part A: the arithmetic holds.** All of these were re-derived with exact integers:

- the schoolbook and restoring-division tariffs, `8ab`, for `a, b ≤ 64`;
- the Euclid tariff `64b³`;
- the six cost terms;
- the bound `7·max ≤ B` and the sum bound `≤ B`, on `p = 2..200` and `ℓ = 1..40`;
- the guard amortization `2^{−G}E ≤ 2^{−60ℓ}(p+2)^{−48}`.

The largest ratio of the six terms' sum to `B` is `1.96·10⁻³`, at `p = 2, ℓ = 1`. The closing
inequality has a factor of about 500 of slack.

**Part B: the per-axis bill holds, tightly.** An instrumented copy of #4100's retained
`decode_group` and `balanced` offset step charges every multiplication, division, inverse and
addition at its **actual** operand bit lengths. It uses #4377's tariffs, with the quotient length
of each division. The source is `check_batched_crt.py`, pinned, and its result is compared with
the retained function's output. The check covers 653 axes:

- groups with `W ≤ p` at `ℓ = 3..12`;
- long-moduli cases at `ℓ = 14..32`, with `m ∈ {1, 2, 4}` and a full right-child prefix.

Every axis is within #4377's per-axis bill `128mW² + 128mℓ³ + 16mW`. The bill is nearly tight,
though. At `m = 1` the ratio rises steadily from 0.950 at `ℓ = 14` to 0.977 at `ℓ = 32`. The two
modular inverses, one in `decode_group` and one for the target, use the whole `2m·64ℓ³` inverse
budget. Any extra inverse in an implementation would exceed the per-axis bill. It would still
pass the closing inequality, given the factor-500 slack.

**Part C: one non-load-bearing slip.** `PROOF.md` prices one rotation-table wire at
`9(ℓ+2)²`, as "one addition and one restoring division of integers of at most `ℓ + 2` bits". Its
own tariffs give `4(ℓ+2) + 8(ℓ+2)²`. That exceeds `9(ℓ+2)²` exactly when `ℓ = 1`, where it is
84 against 81. With the corrected step, the per-network bound `25(ℓ+2)²2^ℓ + 64ℓ2^{2ℓ}` still
holds for every `ℓ ≤ 40`, so nothing downstream changes. A one-line fix is to state the wire cost
as `4(ℓ+2) + 8(ℓ+2)² ≤ 12(ℓ+2)²`. A smaller fix uses the true quotient length of at most 3 bits.

## Not covered

- The tape model and the head-movement accounting of indexed scans.
- The Beneš scan recurrence, which is only re-derived here, as in #4377.
- Reservoir placement, sparse repair and the outer theorem.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/crt-evaluator-independent-check --check-only
python3.12 -B scripts/research_package.py --package research/crt-evaluator-independent-check
```

The verifier prints `PASS_CRT_EVALUATOR_INDEPENDENT_CHECK` in under a second, using only the
standard library.

## Open next questions

1. **Does any #4100 caller use more than `m + 1` modular inverses per axis?**
   - *Why it matters:* the per-axis bill has almost no room left at `m = 1`.
   - *First step:* trace the inverse macro's own offset computation, which #4377 prices as a
     second pair of networks.
   - *Blocked by:* nothing.

## Credit

The proof and its tariffs are unpaidmoon's (#4377). The CRT construction and the retained
`decode_group`/`balanced` code are Cinna Davis's (#4100). ToikY's #4192 is the predecessor Beneš
audit.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
