# The written p^10 guards do not move

**Scoped ledger comparison for #4100's narrow inverse 2-norm. No new κ.**
This decides open question 2 of #4402. It does not prove a column gap for
`GAUSSIAN.md`'s rounded reference `H`.

## Question

`INVERSE-CONDITIONING.md` bounds the inverse 2-norm by

```text
sqrt((1/delta)(1/delta + 2 b rho/delta^2)).
```

#4402 replaces that, inside one phase run, by `1/sqrt(delta delta_col)`.
Do any written precision guards in the #4100 notes change?

## Callers and the exponents they write

The search is the note directory `research/unconditional-batched-crt` on
canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`. Older vendored
copies of the fine-prime note are the same inherited statement, not a second
ledger.

| Note | Role | Exponents |
| --- | --- | --- |
| `INVERSE-CONDITIONING.md` | States the bandwidth formula. For this route it records `b < p` and `delta >= 1/(16p^2)`. | No separate power of `p`. |
| `GAUSSIAN.md`, narrow paragraph | Applies the formula to `Haug` and its principal sections. | Both 2-norms `< p^10` eventually. |
| `GAUSSIAN.md`, broad paragraph | Shifted-symbol bound. It does not use the bandwidth formula. | `< p^6`, with the `p^10` allowance called ample. |
| `GAUSSIAN.md`, locality and normalizer | Repeats HALO's consequences and divides completed maps by a dyadic bound. | `p^-20`, `p^42`, `p^45`, error `p^10 exp(-p^2)`, `p^48`, `p^100`. |
| `HALO.md` | Assumes both 2-norms are at most `p^10` and bandwidth `< p`. | Spectral interval `[p^-20, p^20]`, gap `p^-40`, `J = ceil(p^42)`, bandwidth `< p^45`, error `p^10 exp(-p^2)`, `A = ceil(p^48)`, core `L >= p^400`. |
| `vendor/FINE-PRIME.md` §§4–5 | Inherited hypothesis `\|\|H\|\|_2, \|\|H^-1\|\|_2 <= p^10`. | `2^ceil(100 log2 p)`, the same halo exponents through `p^48`, and core exponent 128. |
| `PROOF.md` | Uses the halo/core pair already chosen above. | Core exponent 400 and halo 48. It does not restate `p^10`. |
| `AUDIT.md` | Names the conditioning notes. | No `p^10`. |

## Comparison

Take an integer `p >= 2`, bandwidth `b <= p - 1`, `delta >= 1/(16p^2)` and
`rho = 1 - delta`. These are the floors the notes give the lemma. At that
corner the squared bandwidth ceiling equals

```text
256 p^4 (1 + 2(p-1)(16p^2 - 1)).
```

The parenthesis expands as `32p^3 - 32p^2 - 2p + 3`, which is strictly below
`32p^3`. The resulting square is strictly below `p^20`, so the 2-norm ceiling
is strictly below `p^10`. The same corner is already at least `p^18` when
`p = 2`, so no smaller single exponent stays under the ceiling for every
integer `p >= 2`. The forward 2-norm square is strictly below `4p`, which is
also below `p^20`.

If `delta_col` meets the same floor, the column-gap ceiling is at most
`16p^2`, and `(16p^2)^2 = 256 p^4` is strictly below `p^20` as well.

Every later exponent in the table is a consequence of the hypothesis that
both 2-norms are at most `p^10`. Both ceilings satisfy that hypothesis, so
none of those exponents has to increase. This package does not decrease them.

For every integer `p >= 19` the slack is larger than the notes use. At the
`p = 19` corner the squared bandwidth ceiling is `6936029752576`, below
`19^12`, so the 2-norm ceiling is below `p^6`. The column-gap ceiling is
`5776`, below `19^3`. Their squared ratio is `207901`, below `19^6`. The
room from that bandwidth ceiling up to `p^20` is more than a factor `p^8`.

The broad `p^6` / `p^10` sentence is a different argument and does not read
the bandwidth term.

## What this does not say

- It does not prove `delta_col >= 1/(16p^2)` for the rounded matrix `H`.
  Cross-cut entries, truncation and rounding stay where #4402 left them.
- It does not say the section error, the halo, or a multiplication exponent
  moves. The selected κ is unchanged:
  `836330098538459/500000000000000000`.
- Upstream pin: main `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority
  revision 7, checked 2026-10-21T16:32:11Z. Overlap refresh
  2026-10-21T16:33:25Z covered 507 open PR bodies and 3240 discussions.
  The live neighbor is #4402. Claim:
  https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19102318

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-twonorm-guard
```

## Open next questions

If both 2-norms are assumed only up to `16p^2`, which of HALO's exponents
20, 42, 45 and 48, and GAUSSIAN's normalizer 100, can decrease while keeping
the same error and coverage conclusions? A decrease would be a ledger edit.
It is not required for correctness, and it still would not apply to `H`
until the column gap survives phase cuts, truncation and rounding.

## Credit

The conditioning lemma, the `p^10` guards and the halo exponents are #4100's.
The column-gap question is pinterbanget's, in #4402, from #4336. The narrow
kernel comes from PR1673 (Vlado Vojdanovski).

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. No
independent human review. Apache-2.0.
