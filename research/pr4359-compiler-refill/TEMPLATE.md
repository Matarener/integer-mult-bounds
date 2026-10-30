# A tighter sufficient rank for the same finite uniform supplier

This is a quantitative refinement of PR4359 at
`da637c87c89482bc4c86be36bd0071b3d400dbed`. It retains the native finite
compiler, source/exit recurrence, delayed BIT cover, and conditional outer
interfaces. The source integer lockstep construction is Jacob Alan Sussman's
Theorem 1G, as attributed and preserved by PR4359. Apache-2.0; substantial
OpenAI/Codex assistance.

The improvement is to the specified sufficient template rank. It does not
materialize the winning word, reduce the number of gates in an already
materialized word, establish practical running time, or itself improve kappa.

| Family | Uniform saving | PR4359 rank | New sufficient rank |
| --- | ---: | ---: | ---: |
| Complex | 0.002304 | `2^276540184361` | `2^1546084442` |
| BIT before cover | 0.002760 | `2^6552928412` | `2^42843607` |

Thus the exponent specifying the complex rank is smaller by a factor greater
than 178, and the BIT exponent is smaller by a factor greater than 152. Both
new ranks are still enormous. The compiler's exact batching algorithm defines
the new finite widths, leaf counts, and instruction words at these ranks; no
claim is made that their sizes are monotone in the ambient rank.

## The induction needs the actual complement coefficient

Use PR4359's notation and proven conditional recurrence:

```
L(n) = sum_s w_s L(n-s) + sum_e x_e L(e),
sum_s w_s = 1,                    L(n) <= n,
sum_e x_e e^t <= sum_s w_s s^t,
n/m < s <= n,                    m E(n)/n < 16 n^(-h).
```

Here `0<t<z0<z<1`, `h>0`, `delta=z0-t`, and every exit and nonzero
complement has smaller rank. Let

```
eta = z0*m^(z0-1).
```

PR4359's concavity inequality gives

```
n^z0 - sum_s w_s (n-s)^z0 >= eta*sum_s w_s s^z0,
sum_e x_e e^z0 <= (16 n^(-h))^delta * sum_s w_s s^z0.
```

Its explicit-rank argument replaces `eta` by `1/4` and requires the exit
coefficient to be at most `1/8`. Induction only requires the exit coefficient
to be at most `eta`. Set

```
H0 = ceil((4*delta*log(2) - log(eta))/(h*delta*log(2))),
n0 = 2^H0,                       A = n0^(1-z0),
H1 = floor(H0*(1-z0)/(z-z0))+1,  N = 2^H1.
```

Choose an effective rational upper enclosure for the expression defining
`H0`; the verifier below proves the resulting integer meets the inequality.
For every `n>=n0`,

```
(16 n^(-h))^delta <= eta.
```

For `n<=n0`, the bound `L(n)<=n` implies `L(n)<=A*n^z0`. Above this range,
strong induction and the two inequalities give

```
L(n) <= A*(sum_s w_s (n-s)^z0 + sum_e x_e e^z0) <= A*n^z0.
```

The strict choice of `H1` then gives `L(N)<N^z`. The proof applies to every
integer rank, including the entire base range; it does not extrapolate from
finite samples or assume a numerical approximation to the mixed root.

## Exact certified choices

Keep PR4359's tested savings, intermediate midpoint, and rational exit
exponents. No supplier moment or native invoice changes:

| Family | Tested saving `1-t` | `1-z` | `h` | New `H0` | New `H1` |
| --- | ---: | ---: | ---: | ---: | ---: |
| Complex | 0.002305 | 0.002304 | 1/10 | 335449 | 1546084442 |
| BIT | 0.002769 | 0.002760 | 1/16 | 69740 | 42843607 |

The strict final power gaps `H1*(z-z0)-H0*(1-z0)` are respectively
`1/2000000` and `3/2000000`. The complex case is sensitive to the strict
integer rounding: `H1=1546084441` gives equality and is rejected.

The standalone standard-library checker independently encloses logarithms
using the positive series

```
log x = 2 sum_(j>=0) u^(2j+1)/(2j+1),  u=(x-1)/(x+1),  1<=x<=2.
```

After 96 terms the omitted tail is at most
`2*u^193/(193*(1-u^2))`. Reciprocal and power-of-two reduction cover all
arguments. Rational Taylor bounds independently verify the two tested mixed
moments. No binary floating-point calculation chooses either rank.

The checker verifies that decreasing either new `H0` or `H1` by one fails
its respective sufficient inequality, and that these source profiles do not
support the separate test saving 0.004. The one-less controls prove tightness
only for this fixed midpoint and this sufficient-bound calculation; they do
not establish globally minimal template ranks.

Run from the repository root:

```sh
python3 -I -B research/pr4359-compiler-refill/template_bound.py
```

The parent package verifier binds all literal profiles and old ranks to the
exact PR4359 input bytes. The original source paths are
`research/kappa-rebuild/controller/EXPLICIT-TEMPLATE-BOUNDS.json`,
`research/kappa-rebuild/controller/EXPLICIT-TEMPLATE-BOUNDS.md`, and
`research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md`.

## Consequences and remaining obligations

For the new complex template, substitute its own finite `W,P,U` into
PR4359's new scalar, owned-storage, row-stock, and semantic-precision
constants. For the new BIT template, select an allowed prime using its new
`N` and the same strict covered-saving gap. All needed values remain
effectively defined finite constants, fixed before the multiplication input
varies. The positive-rank, arbitrary-input, spectator, adapter, owned-field,
common-weight, and physical-routing obligations are unchanged.

The next quantitative questions are to optimize the intermediate `z0`,
replace the common exit constant 16 by a sharper certified value, and exploit
the actual source-rank distribution. Each should preserve the exact compiler
and prove an effective sufficient threshold. Materializing a near-threshold
word or improving the mixed job tariff remains a separate task.
