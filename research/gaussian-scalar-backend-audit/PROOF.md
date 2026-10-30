# Independent rational Gaussian scalar oracle

## Claim and independence boundary

For every rational `f >= 0` and integer `bits >= 16`, the oracle returns
closed rational intervals containing `pi` and `exp(-pi*f)`, each of
absolute width at most `2^-bits`. The exponential interval lies in `[0,1]`.
Zero has the exact interval `[1,1]`.

The implementation was constructed solely from the assigned contract and
ordinary mathematical identities. Before the first freeze it has not read
predecessor modules, source code, source proofs, source receipts, integration
code, source-generated queries, or source-produced numeric intervals.
The contract suggested the distinct arcsine and negative-Taylor approach;
root subsequently described the source approach in words, without supplying
its implementation or numeric results. That description did not change
the algorithm. The first freeze records code, this proof, and independently
generated self-test receipts before any external query is consumed.

After freezing, input-only rational queries may be processed. Source outputs
remain outside this oracle's independence boundary. Query evaluation does
not modify the frozen code or proof. Independence is a provenance statement,
not a claim that two approaches necessarily agree on every possible bug.

## Representation and output

All certificate arithmetic uses Python integers and `fractions.Fraction`.
There are no floating-point or Decimal certificate calculations, external
packages, source imports, or unverified numerical libraries. JSON floating
numbers and constants are rejected. Factors are integers or exact rational
strings; negative factors, booleans, and precisions below 16 are rejected.

The input is one `{id,factor,bits}` object, a list of such objects, or
`{"queries":[...]}`. Fields must be exactly those three. IDs are strings or
integers. Rational output strings always use the reduced `numerator/denominator`
form with positive denominator. Every query returns `pi` and
`exp_negative_pi_factor`, each with `lower` and `upper` endpoints, plus
algorithm diagnostics. Canonical JSON sorts keys, uses ASCII, and omits
whitespace other than one final newline. `--output` is the only file-writing
option. Without it, the full JSON goes to stdout. With it, stdout contains
only a compact summary and SHA256 of the complete JSON.

The API `certified_pi(bits)` returns `(lower,upper,metadata)`.
The API `certified_exp_pi(Fraction(f),bits)` returns
`(exp_lower,exp_upper,pi_lower,pi_upper,metadata)`.

## Positive rational pi series

The binomial expansion of `(1-z)^(-1/2)`, integrated from `0` to `1/2`,
gives the absolutely convergent arcsine series. Since `arcsin(1/2)=pi/6`,

`pi = 3 * sum_(k>=0) binom(2k,k) / (16^k * (2k+1))`.

Write the summands, including the factor three, as `a_k`. Then `a_0=3` and

`a_(k+1)/a_k = (2k+1)^2 / (8*(k+1)*(2k+3)) < 1/4`.

The inequality follows because
`2*(k+1)*(2k+3) - (2k+1)^2 = 6k+5 > 0`.
After adding terms `a_0,...,a_(K-1)`, let their sum be `S_K` and let
`a_K` be the next term. Positivity and the uniform ratio bound prove

`S_K < pi < S_K + (4/3)*a_K`.

These are the exact rational endpoints returned by `pi_bounds` once the
tail bound is at most its rational tolerance. Since `a_K < 3*4^-K`, the
loop terminates for every positive rational tolerance. No endpoint or
geometric-tail expression is evaluated approximately.

Put `epsilon = 2^-bits`. For an ordinary query the pi tolerance is
`epsilon/(16*max(1,f))`, so multiplication by `f` gives an exponent interval
`[x_L,x_U]` with width at most `epsilon/16`. For a large-factor shortcut,
pi is independently computed with tolerance `epsilon/16`, without a need
to multiply pi by a possibly enormous factor. Both choices meet the
advertised pi precision.

## Ordinary negative-exponential enclosure

For a nonnegative exponent interval `[x_L,x_U]` of width at most
`epsilon/16`, choose the least nonnegative integer `s` for which
`x_U/2^s <= 1/4`; put `D=2^s` and `y_L=x_L/D`, `y_U=x_U/D`.

For each endpoint, use the alternating series

`exp(-y) = 1-y+y^2/2!-y^3/3!+...`, for `0<=y<=1/4`.

Odd partial sums are lower bounds and even partial sums are upper bounds.
Their consecutive gap is the exact positive Taylor term. Terms decrease
to zero because each successive ratio is `y/(k+1) <= 1/4`, and the usual
alternating-series remainder theorem applies. The loop stops when each
endpoint's bracket has width at most

`tau = 2^-(bits+s+6) = epsilon/(64*D)`.

Use the lower endpoint bound evaluated at `y_U` and the upper endpoint
bound evaluated at `y_L`. Monotonicity of `exp(-y)` proves this interval
encloses `exp(-y)` for every `y` in the range. Since its derivative has
absolute value at most one on the nonnegative axis, the unrounded width
is at most

`(x_U-x_L)/D + 2*tau <= 3*epsilon/(32*D)`.

Round this interval outwards to dyadic grid
`q=2^-(bits+s+8)=epsilon/(256*D)`. Integer floor is used on the lower
endpoint and integer ceiling on the upper endpoint. The rounding procedure
also checks the exact containment inequality. Outward rounding increases
width by less than `2*q`, so the initial dyadic bracket has width at most
`13*epsilon/(128*D)`.

Repeatedly square both nonnegative endpoints `s` times, rounding outwards
on the same grid after every square. Monotonicity of squaring on `[0,1]`
preserves enclosure. Before rounding,

`upper^2-lower^2 = (upper-lower)*(upper+lower) <= 2*(upper-lower)`.

All endpoints remain in `[0,1]`: the initial Taylor bounds are in `[0,1]`,
and zero and one are exact grid points. Thus after all `s` squarings the
width is at most

`D*(13*epsilon/(128*D)) + 2*q*(D-1) < 7*epsilon/64`.

The interval now encloses `exp(-x)` throughout `[x_L,x_U]`. Finally round
outwards on grid `2^-(bits+2)=epsilon/4`. This adds less than `epsilon/2`
to the width, yielding a final width less than

`7*epsilon/64 + epsilon/2 = 39*epsilon/64 < epsilon`.

The implementation checks the final width and `[0,1]` conditions explicitly;
these checks supplement the proof and do not rely on removable assertions.

## Zero, tiny factors, and huge factors

When `f=0`, the result is exactly `[1,1]`.

For a tiny factor with `pi_upper*f <= epsilon/4`, use the general inequality
`1-x <= exp(-x) <= 1` for `x>=0`. The interval
`[1-pi_upper*f,1]` therefore encloses the requested value. Rounding this
interval outwards on grid `epsilon/4` has width at most `epsilon/4`.
This avoids repeatedly manipulating an unnecessarily long tiny rational
denominator in the Taylor recurrence.

If `3*f >= bits`, use the interval `[0,epsilon]`. This follows from
`pi>3`, `exp(1)>2`, and the integer identity
`exp(bits)=exp(1)^bits`: `exp(pi*f) > exp(bits) > 2^bits`.
Thus `0 < exp(-pi*f) < epsilon`. The comparison involves only rational
integers. No logarithm, floating threshold, or very large exponential is
computed. Values immediately below, exactly at, and immediately above
this threshold are included in the independent tests.

## Termination and cost scope

All pi and Taylor tolerances are positive for every accepted finite input.
Their geometric/factorial remainder bounds tend to zero, so both loops
terminate. The range-reduction loop terminates for every finite rational
exponent. Every squaring and rounding operation is finite integer
arithmetic. For non-shortcut factors, `f<bits/3` and `pi_upper<4`, so
`x_U<4*bits/3` and `s=O(log(bits))`. The working dyadic precision is
`bits+s+8`. The pi loop takes `O(bits+log(bits))` terms under the simple
geometric bound, and a Taylor loop has the same conservative term bound.
Large-factor work avoids arithmetic with `pi*f` beyond the rational
threshold comparison. Exact-rational costs still depend on input bit
length and requested precision; no fixed time or memory bound is claimed.

This is an offline scalar correctness oracle. It does not certify a
Gaussian state, a coefficient generator, a normalization computation, a
preparation circuit, asymptotic physical preparation cost, or an efficient
implementation of a physical operation. No source integration, paper
publication, SAT replay, or formal proof-assistant result is claimed.

## Meaningful independent tests and controls

`--self-test` runs exact checks for zero, a factor `2^-4096`, rational
ordinary factors, near-threshold factors on both sides, equality at the
threshold, and a factor with a thousand-digit numerator. It checks every
interval's order, range, and requested width and verifies pi precision
nesting. It also checks the additive identity by overlapping enclosures
for `exp(-pi/3)*exp(-2*pi/3)` and `exp(-pi)`.

The controls are explicit:

* Omitting pi: independently enclose `exp(-1)` and verify it is greater
  than `1/3`, while the requested `exp(-pi)` enclosure is below `1/4`.
* Wrong sign: reciprocal bounds for the positive exponent are strictly
  above one and disjoint from the requested negative-exponent result.
* Pi tail omission: a low-precision partial-sum point is strictly below
  the certified higher-precision lower endpoint.
* Exponential tail omission: the degree-two even Taylor point at `y=1/4`
  lies strictly above the certified high-precision enclosure.
* Rounding direction: the non-dyadic rational `1/3` lies strictly between
  the adjacent outward dyadic endpoints; either inward point loses exact
  containment. The rounding function checks enclosure on every call.
* Invalid negative factors, small precision, boolean precision, and a
  floating factor are rejected.

The freeze procedure compares normal execution against
`-I -O -W error -B`, requires byte-identical full self-test output and
stdout receipts, checks that execution without `--output` changes no
files, and hashes the complete source/proof/test artifacts. No `assert`
statement implements any correctness check.
