# Independent check of #4326's BIT moment root

**Claim type: an independent certified finite check. No new κ.** This
does not accept #4326, and it checks none of #4326's construction or caller
premises.

## Object

[PR #4326](https://github.com/CrocSwap/integer-mult-bounds/pull/4326)
(ai-nanachi, head `080f8c218d64c6d231ed6297987e39b7a912a4ef`) proposes a
conditional logical BIT supplier.

- **Root.** It claims a surcharged BIT moment root strictly inside
  `[1744853764761145849274, 1744853764761145849275]·10⁻²⁴`. That is 0.41562%
  above PR4183's upper endpoint.
- **Majorant.** It claims `T(n,w) ≤ 200·C·n + 10⁷·C·n^(1−b)·w` at
  `b = 0.00174481`.
- **Prior checks.** Its own checks are internal. No other PR or discussion
  references it.

The moment is the selected BIT moment's form:
`μ(a) = Σ n_r (r/64)^(1−a)/W + (32·64²/10¹⁶)·Σn·(1/64)^(1−a)/W`, with
`W = 28416`.

## Results

| Check | Result |
| --- | --- |
| Profile `{1:379872, 2:400000, 3:22464, 4:24416, 5:29376, 6:17088, 7:26496, 10:32, 42:672}` against the record | count 900,416 and rank mass 1,808,352, both equal to `RECORD.json` |
| `μ` across the claimed root bracket | `< 1` at the lower end, `> 1` at the upper end (certified) |
| `μ_1 < 199/200` (the 200C prefactor) | `μ_1 = 0.9943517737` |
| `μ_(1−b) < 1 − 10⁻⁷` (the 10⁷C prefactor) | `1 − μ_(1−b) = 1.42·10⁻⁷`, so it holds, but tightly |
| Gain over PR4183 | `0.415620%`, equal to the recorded `gain_lower` |
| Against the selected BIT saving `0.0017334270…` | `0.66%` higher |

**Control.** The author rejects one variant: crediting the nine private
families to `W`. Under that variant the moment stays below 1 at the upper
end, so the root moves up. The bracket therefore depends on not crediting
them.

**Not a κ change.** The selected κ is bound by the complex side, so a higher
BIT saving does not change it.

## Not covered

- Deriving the profile from #4326's word and remainders. The profile is
  transcribed from its independent pricer and matched to the record's
  aggregates. **Update:**
  [#4349](https://github.com/CrocSwap/integer-mult-bounds/pull/4349) (ToikY)
  has since rebuilt it from the literal word and owners. Its `full_profile`
  equals the profile checked here exactly, and its idle histogram equals the
  one implied by it.
- The logical supplier, fixed-tape lowering and caller premises.
- No proof-kernel check.

## Reproduce

```sh
python3.12 -B research/pr4326-bit-root-check/verify.py
```

It prints `PASS_PR4326_BIT_ROOT_CHECK` in under a second, using only the
standard library. `vendor/RECORD.json` is a byte-identical copy of #4326's
`research/bit-compact-carrier-retirement/RECORD.json` (blob `b6c69927…`);
its SHA256 is checked. The profile constant comes from
`independent_price.py` at the same head (blob `5b789483…`).

## Open next questions

None. The profile reconstruction asked for here is #4349; see "Not covered".

## Credit

The audited construction is ai-nanachi's #4326, building on Ross
Richardson's PR4183 and PR4021 and the retained BIT lineage. Prepared by
Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
