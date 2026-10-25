# HALO's exponents can fall under the ceiling 16 p^2

**Conditional exponent arithmetic for #4100's locality witness. No new κ.**
This answers the open question of #4403. It does not prove the ceiling for
`GAUSSIAN.md`'s rounded reference `H`, and it does not edit the #4100 notes.

## Question

#4403 showed that the written `p^10` guards need not increase. The remaining
arithmetic question is the other direction. Suppose, for an integer `p >= 2`,

```text
||H||_2 <= 16 p^2,    ||H^-1||_2 <= 16 p^2,
```

and the physical bandwidth `W` is an integer at most `p-1`. Which of HALO's
exponents 20, 42, 45 and 48, and GAUSSIAN's normalizer 100, can decrease
while the error and the row-exactness conclusions stay in force?

The ceiling `16 p^2` is `1/sqrt(delta delta_col)` when both gaps are at least
`1/(16 p^2)`. That gap for the rounded matrix is not proved here.

## Result

The same polynomial `P = p^-12 sum_{j < p^26} Q^j H*`, with
`Q = I - p^-12 H* H`, satisfies

```text
||P - H^-1||_2 < p^6 exp(-p^2),
```

and every row whose distance to a section edge is at least `p^28` equals the
global row. The normalizer `p^7`, or the dyadic factor `2^ceil(7 log2 p)`,
puts a factor at most `16 p^2` strictly below one.

| Written exponent | Smallest uniform replacement | Why it is smallest |
| --- | ---: | --- |
| 20, the spectral endpoint | 12 | `(16 p^2)^2 = 256 p^4 <= p^12`, and `256 p^4 > p^11` at `p = 2` |
| 40, the gap inside `Q` | 24 | `p^-12 * p^-12 = p^-24`, and the `p = 2` case is equality |
| 42, the length `J` | 26 | `p^26 p^-24 = p^2`, while `p^25` leaves only `p` |
| 10, the error multiplier | 6 | `16 p^2 <= p^6`, and `16 p^2 > p^5` at `p = 2` |
| 45, the bandwidth | 28 | `(2J-1)W` and `(2J+1)W` are both below `p^28` and not below `p^27` |
| 48, the halo distance | 28 | `p^28` already exceeds the sharp radius `(2J-1)W` |
| 100, the normalizer | 7 | `p^7 > 16 p^2`, while `p^6 = 16 p^2` at `p = 2` |

So 20, 42, 45, 48 and 100 can all decrease. The replacements are 12, 26, 28,
28 and 7.

## Proof

`16 p^2 <= p^6` because `p^4 - 16 = (p-2)(p+2)(p^2+4)`, which is zero at
`p = 2` and positive after that. Squaring gives the spectral interval
`[p^-12, p^12]` for `H* H`. The scalar `p^-12` is therefore an admissible
step: `Q` is Hermitian with eigenvalues in `[0, 1-p^-24]`.

The truncation identity in the halo audit is unchanged in shape,

```text
P - H^-1 = -Q^J H^-1.
```

Hence the error is at most `(1-p^-24)^J` times `16 p^2`. For `x` in `(0, 1)`,
`exp(x) = sum x^k/k! <= sum x^k = 1/(1-x)`, so `(1-x)^J <= exp(-J x)`.
At `J = p^26` the product `J p^-24` equals `p^2`, and `1/2! < 1` makes the
exponential comparison strict. The multiplier `16 p^2` is at most `p^6`.

`H*` has bandwidth `W` and `Q` has bandwidth `2W`, so `Q^j H*` has bandwidth
`(2j+1)W`. The longest term is `j = J-1`, radius `(2J-1)W`. This is the sharp
radius from the halo audit. With `J = p^26` and `W <= p-1`,

```text
p^28 - (2 p^26 - 1)(p-1) = p^26 ((p-1)^2 + 1) + p - 1 > 0.
```

The looser HALO expression `(2J+1)W` has the same uniform ceiling. For every
integer `p >= 3` the sharp radius is at least `p^27 + 1`, and at `p = 2` the
looser expression is `p^27 + 1`. Exponent 27 is therefore not enough.
`A = p^28` lies strictly beyond the radius, which is the row-exactness claim.

Dividing by `p^7` is strict because `p^5 >= 32 > 16`. Dividing by `p^6` leaves
the `p = 2` corner at one, not below one. Any dyadic factor at least `p^7`
has the same strictness. That is `2^ceil(7 log2 p)`.

The written core exponent 400 still dominates `4A`. It can itself fall to 86:
`p^86 > 4 p^28`, and for every `epsilon, beta < 1` both
`epsilon + beta + 84 - 86` and `epsilon + 30 - 86` stay negative. Exponent 85
does not, since `epsilon + beta + 84 - 85` is positive for `epsilon = beta = 3/4`.
FINE-PRIME's core exponent 128 likewise still covers a halo exponent of 28.
This package does not retune the core.

## What this does not say

- It does not prove `||H^-1||_2 <= 16 p^2` for the rounded reference. Phase
  cuts, truncation and rounding remain open, as in #4402.
- The #4100 notes keep 20, 42, 45, 48 and 100. Those values remain sufficient.
  The smaller ones are available only under the stronger ceiling.
- The selected κ is unchanged:
  `836330098538459/500000000000000000`.
- Upstream pin: main `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority
  revision 7, checked 2026-10-21T16:44:38Z.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-halo-exponents
```

## Open next questions

Do these smaller exponents hold for `GAUSSIAN.md`'s rounded reference `H`?
Only a column gap after phase cuts, truncation and rounding would put
`||H^-1||_2` under `16 p^2`. Until that transfer exists, HALO's written
exponents stay the ones the construction may use.

## Credit

The locality witness and its exponents are #4100's. The sharp radius
`(2J-1)W` is the halo audit's, PR #4217 (Nick Petalas). The ceiling
`16 p^2` is the conditional bound from #4403, which answered #4402's
guard question. The kernel comes from PR1673 (Vlado Vojdanovski).

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. No
independent human review. Apache-2.0.
