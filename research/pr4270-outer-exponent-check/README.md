# Independent check of #4270's conservative exponent chain

**Claim type: an independent exact check of a written arithmetic chain,
including a certified moment enclosure. No new κ.** This does not accept
#4270. It checks no physical, hosting or analytic premise.

## Object

[PR #4270](https://github.com/CrocSwap/integer-mult-bounds/pull/4270)
(Ross Richardson, head `a929a3fa36301bdfcffe82afd37434dd9e3c4887`) claims a
conditional `κ = 1/580`, above the selected `0.001672660197076918`.

Its conservative argument in `OUTER-JOIN.md` §1 and §5 rests on a chain of
explicit inequalities. Before this package, the only outside check was
thu-nmrc's comment on the PR, which replayed the registered commands under
Python 3.11 and matched the source hashes. No independent recomputation of
the chain existed.

## Results

Every link holds. Each is computed here with exact rationals from the
vendored text and the pooled fill's result file.

| Link | Margin |
| --- | --- |
| Pooled moment `Σ n_r (r/73)^(1−a)/322560` at `a = C`, against 1. The certified upper bound is `1 − 7.4158·10⁻²⁵`, and the moment exceeds 1 at the bracket's upper end `C + 10⁻²⁴`. Because it straddles 1, the bracket pins `m = 73` and `W = 322560` for #4181's profile. | `7.4·10⁻²⁵` |
| `σ* = 0.99826995 > 1 − C` (so the moment at `σ*` is below 1) | `9.3·10⁻⁷` |
| `τ = 332353/332929 < σ*` | `4.9·10⁻⁸` |
| Stopped-tree leaf exponent `σ* + θ(1−σ*) < α_layer = 0.99827`. The internal exponent and the root reservation `.998` are lower still. | `4.8·10⁻⁸` |
| `Φ = 1 − (997/1000)(1 − α_layer) = 0.99827519` exactly; full-support router `β = 41544341/41616125 < Φ` | `9.8·10⁻⁸` |
| The other cost powers stay below `Φ`: `.997`, `.9981`, `3/5`, `.997τ` (the support's second term) and `.997` (the CRT `D·Tp` term) | at least `1.75·10⁻⁴` (from `.9981`) |
| `1 − Φ > 1/580` | `6.7·10⁻⁷` |
| `1/580 >` selected `κ` | `5.1·10⁻⁵` |

**Control.** The old physical Fourier rate `.00172380303` falls short of
`1/580`, as `OUTER-JOIN.md` itself says. So the changed layer exponent is
load-bearing.

**Reading the margins.** The tightest links are `σ* − τ`, `α_layer −` leaf
and `Φ − β`, all at about `5–10·10⁻⁸`. They pass, but any upstream change to
`τ` or `β` at that scale would need this chain rechecked.

## Not covered

This package does not cover:

- the pooled native/hosting identities, the stopped-tree proof itself, the
  support and Gaussian constructions, or the analytic prime and Gaussian
  theorems — all of which #4270 states as premises;
- the derivation of `τ`, `β` or `Φ`'s form from their sources (only the
  arithmetic on them is checked);
- the cost table's row structure (only its listed powers are checked);
- any production run, or any proof-kernel check.

## Reproduce

```sh
python3 scripts/research_package.py --package research/pr4270-outer-exponent-check --check-only
python3.12 -B research/pr4270-outer-exponent-check/verify.py
```

It prints `PASS_PR4270_OUTER_EXPONENT_CHAIN` in under a second, using only
the standard library.

## Open next questions

1. **Bind `τ` and `β` to their sources.**
   - *Why it matters:* the chain's tightest margins (about `5·10⁻⁸`) sit on
     these two constants.
   - *First step:* recompute `τ = 332353/332929` from PR3599's encoded
     coupling, and `β` from the full-support router's invoice.
   - *Blocked by:* nothing.

## Credit

The audited chain is #4270's (Ross Richardson with OpenAI Codex assistance).
The pooled fill is Rohan Arun's (PR #4181). The chain cites, among others,
Jose Manuel's physical constructions and Tekalign's CRT converter. Prepared
by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
