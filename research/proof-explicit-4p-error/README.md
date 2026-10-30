# Explicit dimension exponent for the 2^{-4p} sentence

**Scoped audit of one #4100 sentence. No new κ. #4100 is not accepted.**

## Result

In Cinna Davis's `research/unconditional-batched-crt/PROOF.md`, the source-transform
error claim says that polynomially many full-array norm changes cost at most
`2^{O(p)}`, because `T=2^{Θ(p)}`, and that a sufficiently large fixed `C` then
makes every absolute coefficient error smaller than `2^{-4p}`.

That product reading does not follow from the size section. With the parameters
PROOF.md defines, `log2 T` is within two bits of `b=p/6`. Charging `p` factors
of `T` therefore costs `2^{Θ(p^2)}` bits, not `2^{O(p)}`. The cited sentence does
not determine a working-precision coefficient.

The same size section does determine the exponent. For every integer `n≥4`,
`b=ceil(log2 n)`, `p=6b` and `T` the unique power of two in `[4n/b, 8n/b)`:

    b − floor(log2 b) + 1 ≤ log2 T ≤ b + 2 − floor(log2 b).

Both ends are attained (`n=5` gives the lower bound, `n=4` the upper). In
particular `log2 T ≤ p/6 + 2 − floor(log2 b)`. For `b≥8` this is at most `b−1`,
so `T<2^b`, which is the cutoff already checked by #4320.

Under the **one-factor** reading — at most `m` factors of `T`, times a fixed
`constant · p^{degree}` — an explicit `C` is enough:

| Charge | `C` | Holds for every bucket |
| --- | ---: | --- |
| one `T` | 5 | `b≥2` |
| one `T` and `p^{10}` | 5 | `b≥13` |
| one `T` and `p^{10}` | 8 | `b≥2` |
| `16 p^2 · T` | 5 | `b≥3` |
| `16 p^2 · T` | 6 | `b≥2` |
| `512 p^5 · T` | 5 | `b≥8` |
| `512 p^5 · T` | 7 | `b≥2` |
| six factors of `T`, times `p^{10}` | 5 | never, through `b<400` |
| six factors of `T`, times `p^{10}` | 6 | `b≥9` |

The `16 p^2` and `512 p^5` rows are what GAUSSIAN.md's displayed dominance
bounds give for one inverse, **if** the row gap is at least `1/(16p^2)` and the
bandwidth is an integer `≤ p−1`. They are not a count of how many such inverses
the circuit applies. Six factors at `C=5` leave no linear room: each factor
costs about `p/6` bits, and `4 + 6/6 = 5`.

#4320's open question 1 asked for this constant and said the row gap blocked
it. The product-reading failure and the exponent lemma do not use the row gap.
The row gap remains the hypothesis that turns GAUSSIAN.md's inverse into the
polynomial `16 p^2` or `512 p^5`.

## Scope

Card `uniform-transfer-audit`, refined to PROOF.md's `2^{-4p}` amplification
sentence at the parameters of its size section. Priority revision 7. Base
`12fa8c5c844be21bfefb38a19503fbd867a11244`. The #4100 text is the retained
package at that commit (head `337d04939571a637aeab54a0f58f54fde811663a` on the
source PR). Selected κ stays `0.001672660197076918`.

This is item 2 of the [#4311](https://github.com/CrocSwap/integer-mult-bounds/pull/4311)
shortest unaudited list: PROOF.md's `2^{-4p}` precision constant. #4320 audited
the algebraic identities and left this sentence open. #4325 audited chirp head
travel. Neither derives the exponent above.

## Proof

Let `b=ceil(log2 n)≥2` and let `k` be the integer defined by
`b·2^{k−1} < 4n ≤ b·2^k`. Then `T=2^k` is the unique power of two in
`[4n/b, 8n/b)`, because a second power of two cannot fit in an interval of
ratio 2, and the displayed inequality is exactly membership.

Write `t=floor(log2 b)`.

**Upper bound.** `n≤2^b`, so `b·2^k < 8n ≤ 2^{b+3}` and
`b·2^k ≤ 2^{b+3}−1`. Also `b≥2^t`, hence
`b·2^{b+3−t} ≥ 2^{b+3} > 2^{b+3}−1`. Therefore `2^k < 2^{b+3−t}`, so
`k ≤ b+2−t`. At `n=4`, `b=2`, `t=1` and `k=3`, equal to the bound.

**Lower bound.** The smallest `n` in the bucket is `2^{b−1}+1`, so
`4n > 2^{b+1}`. Also `b<2^{t+1}`, hence `2^{b+1}/b > 2^{b−t}`. The minimizing
`k` still satisfies `2^k > 2^{b−t}`, so `k ≥ b−t+1`. At `n=5`, `b=3`, `t=1`
and `k=3`, equal to the bound.

`k` is nondecreasing in `n` inside a bucket because the interval
`[4n/b, 8n/b)` only moves right. The verifier checks that directly for every
`n` from 4 through 200000, and checks both endpoints for every bucket through
`b=4096`.

**Product reading.** Take `m(p)=p` norm changes and charge each at `T`. At
`n=2^b` the exponent is `p·log2 T`. That quotient over `p` is exactly
`14, 60, 250, 1016, 4086` at `b=16, 64, 256, 1024, 4096`. No constant `C0`
satisfies `p·log2 T ≤ C0·p` for every `b`. Replacing every norm change by the
full array dimension therefore does not cost merely `2^{O(p)}`.

**One-factor reading.** `T ≤ 2^{b+2−t}` and `p=6b`, so
`constant · p^{degree} · T^{m} · 2^{−C p} < 2^{−4p}` as soon as

    constant · (6b)^{degree} < 2^{(C−4)·6b − m(b+2−t)}.

The table is this comparison, exact, for every bucket from the stated cutoff
through `b=399`.

**Conditional inverse.** Assume `δ ≥ 1/(16p^2)` and an integer bandwidth
`w ≤ p−1`. GAUSSIAN.md's formulas give
`‖H^{−1}‖_∞ ≤ δ^{−1} ≤ 16p^2` and

    ‖H^{−1}‖_1 ≤ δ^{−1} + 2w(1−δ)δ^{−2}
      ≤ 512 p^5 − 512 p^4 − 32 p^3 + 48 p^2
      < 512 p^5.

The verifier recomputes that polynomial. It does not prove the gap, and it
does not count how many inverses, Fourier scales or tensor factors sit on one
coefficient path. PROOF.md also names an `M<2^p` scale; the exponent lemma
replaces that `p` by `p/6 + O(log b)` whenever `M≤T`.

## Evidence

`verify.py` exits only after the sentence pins, the exhaustive size check, the
product-reading ratios, the conditional table and these failure controls:

- the upper bound is false if decreased by one (`n=4`);
- `m=p` factors are not bounded by `10p` bits (`b=64`);
- `C=5` never absorbs six dimension factors on `2≤b<80`.

No proof kernel, no Gaussian circuit execution, and no claim that a particular
`m` occurs in the program.

## Reproduce

From the repository root, Python 3.12:

```sh
python3 scripts/research_package.py --package research/proof-explicit-4p-error --check-only
python3.12 scripts/research_package.py --package research/proof-explicit-4p-error
```

## Open next questions

1. Count the factors of `T` on one coefficient of the three normalized
   transforms, the pointwise product and the final `M` scale.
   The count is the integer `m` in the table. The normalized butterfly
   `H0/2` may contribute none; the final scale contributes one if `M≤T`.
   Nothing in the size section blocks the count. A Gaussian factor still
   requires the row-gap hypothesis before its norm is polynomial.
2. Make `δ ≥ 1/(16p^2)` effective after alias removal, truncation and
   rounding, which is #4217's open question 1.
   Until that holds, the `16 p^2` and `512 p^5` rows stay conditional.
   This dimension lemma does not remove that hypothesis.

## Credit

The construction and the `2^{-4p}` sentence are Cinna Davis's #4100, with
OpenAI Codex assistance, and the retained Gaussian sources named in
GAUSSIAN.md. #4320 (Ryanson Jonathan, Claude) audited the surrounding
identities, proved `T<2^b` for `b≥8`, and left this sentence open. #4311
(Ryanson Jonathan) listed it as unaudited obligation 2. This note and verifier
were prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0. No independent human or formal-kernel acceptance is claimed.
