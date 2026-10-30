# The core side exponent falls from 400 to 80

**Claim type:** exponent arithmetic for HALO's sparse volume.
**No new κ.** The agreement distance `p^{26}` and the ideal gaps stay
hypotheses. The selected record remains `23/10000`.

## Question

#4481 leaves the core side `L = 2^{ceil(400 log2 p)}` untouched. HALO compares
the two sparse powers in

```text
O(V [d/g + d g A^3/L + d A p^2/L] polylog p)
```

at `A = p^{48}` and `L ≥ p^{400}`. Both are negative for group exponents
`ε, β < 1`. What is the smallest integer `C` for which `L ≥ p^C` still makes
both powers negative when `A = p^{26}`?

## Lemma

Let `A = p^{26}` and let `d = p^ε`, `g = p^β` with real exponents `ε < 1` and
`β < 1`. For an integer `C` and `L ≥ p^C`, the two sparse powers are

```text
ε + β + 78 - C,    ε + 28 - C.
```

Both are negative for every such pair if and only if `C ≥ 80`. Thus 80 is
the smallest uniform integer with that property. The same `C = 80` also gives
`p^{80} > 4 p^{26}` for every integer `p ≥ 2`, and `g A/L` has exponent
`27 - 80 < 0` whenever `g ≤ p`.

The written choice 400 still works, and it is larger than 80. At the corner
`ε = β = 1` its first power would have slack 254. Exponent 79 does not work:
at `ε = β = 3/4` the first power equals `1/2`.

## Proof

`A^3 = p^{78}` and `A p^2 = p^{28}`, since `3 · 26 = 78` and `26 + 2 = 28`.
Dividing by `L ≥ p^C` subtracts `C`.

If `C ≥ 80`, then

```text
ε + β + 78 - C < 2 + 78 - C = 80 - C ≤ 0,
```

and the inequality is strict because `ε + β < 2`. The second power satisfies

```text
ε + 28 - C < 1 + 28 - 80 = -51 < 0.
```

If `C ≤ 79`, the pair `ε = β = 3/4` is strictly below 1 and

```text
4(3/4 + 3/4 + 78 - 79) = 2 > 0,
```

so the first power equals `1/2`. Smaller integers are larger still. The second
power is not the binding one: it is negative for every `ε < 1` as soon as
`C ≥ 29`, and it is already positive at `ε = 1/2` when `C = 28`.

The corner value of the first power is `80 - C`. It is strictly negative at
`C = 80`, and it is at most `-1` for every pair only when `C ≥ 81`. So 80
does not reproduce the uniform slack that 400 has at `A = p^{48}`.

For the two side conditions in the same paragraph, `p^{80} / (4 p^{26}) = p^{54} / 4`
and `2^{10} > 4`, so the ratio is greater than 1 for every integer `p ≥ 2`.
For `g ≤ p` the enlargement exponent is `1 + 26 - 80 = -53`.

The older arithmetic is the same shape: `3 · 48 = 144` and `2 + 144 = 146`,
so `400 - 146 = 254`.

## Not covered

- A proof that the agreement distance is `p^{26}` for every prime. This
  comparison uses that distance as the value of `A`.
- The tensor error `g p^{10 g} exp(-p^2)`. The volume exponent does not
  change that factor.
- Replacing the written core side in the #4100 notes.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-core-side --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-core-side
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-22, from the snapshot fetched at 00:47 UTC, matched this
draft, the #4481 handoff, the locality audit that keeps side 400, and the
union-head note that cites the same core side. It did not find another
assignment of 80. A search miss is not a novelty certificate. #4481 is the
Schur margin. HALO is the volume formula.

## Open next questions

1. **Does the tensor error still need the factor `p^{10 g}`?** The volume
   side can use `C = 80`, while the core error is still written as
   `g p^{10 g} exp(-p^2)`. The first step is to replace `p^{10}` by the
   inverse ceiling `10 p^2` and check whether `g log p = o(p)` still leaves
   the error below `2^{-C p}` for every fixed `C`.

## Credit

- The volume formula and the written side 400 are #4100's.
- The agreement distance `p^{26}` is the conditional halo exponent from #4452
  and #4481.
- The question is the open step of #4481.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
