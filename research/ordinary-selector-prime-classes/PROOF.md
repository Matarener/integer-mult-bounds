# Complete scalar admission classes for the retuned ordinary selector

Fix a prime `q > 2^80` and an integer original width `e >= 1`. Use the
retuned profile `(numerator, denominator, dimension, child_rank, row_factor)`
equal to `(1, 577, 64, 42, 269241600)`. Put

```
c = 1/577,                  R = 269241600,
w = min{z >= 1 : z^577 >= e},
D(e) = 0                         if e < 64,
D(e) = 1 + D(42 floor(e/64))      otherwise,
P(q) = product_(i=1)^64 (1-q^-i),
K = R q^(4096w) P(q),       S = K^D(e),
k = min{j >= 0 : q^j >= S},
m(q) = ceil(log_q(R^19 P(q)^19)).
```

All minima here are over integers. The logarithms describe exact integer
comparisons, not floating-point computations. Define `fits(e,q)` by the two
tests in the retained selector: first `2k < e`, then
`floor((e-k)/w) >= 64`. If the first test fails, the second is not executed.

**Theorem.** For every prime `q > 2^80`, `1 <= m(q) <= 7`, and for every
integer `e >= 1`,

```
fits(e,q)  if and only if  e >= 311297 + 2m(q).             (1)
```

Thus the only possible cutoffs are `311299, 311301, 311303, 311305, 311307,
311309, 311311`. The exact class of a prime is determined by the strict
lower and weak upper comparisons in section 2. Section 7 describes the
separate prime certificates establishing that every class is nonempty.

This is a theorem about the scalar decision specified above. Its connection
to the program is conditional on the scalar abstraction of the inherited
Count operations; section 8 gives that boundary. It does not execute or
certify the Count primitives, native payload, operator, source access,
restoration, physical costs, or supplier admission.

## 1. Sources, binding, and earlier work

The source base is `12fa8c5c844be21bfefb38a19503fbd867a11244`.
[SOURCE-PINS.json](SOURCE-PINS.json) and [SOURCES.json](SOURCES.json) bind the
exact input bytes. The relevant mathematical program is
[`encoded.atom_width` and `encoded.select`](../physical-ordinary-interchange/encoded.py).
The profile is set by
[`retuned-ordinary-coupling/interface.py`](../retuned-ordinary-coupling/interface.py)
and by
[`t74-retuned-physical-layer/retuned_native.py`](../t74-retuned-physical-layer/retuned_native.py).
[`Ordinary.run`](../physical-ordinary-interchange/ordinary.py) passes the
original width, fixed `q`, and that profile to `select`, and `execute_plan`
chooses the fitted or fallback branch from the returned `fits` value.
[`production_native.py`](../physical-complex-controller/production_native.py)
uses the fixed prime `q* = 213*2^80+1` and requires `q > 2^80` in its
constructor. No constructor is run here.

The earlier contribution by Aakash (`@aakashthakkar`) with substantial
OpenAI Codex assistance,
[`bit2234-stock-threshold/README.md`](../bit2234-stock-threshold/README.md),
Git blob `ede0d322c477af91d4c2cc33db0fd10958f45eab` at the source base,
already proves that **311311 is the least uniform strict borrowing cutoff**
for the prescribed stock with the older coupling `17/10000`. It gives the
depth staircase, the four upper intervals, a dyadic tail argument, and a
prime witness at `q*`. Those facts and that proof method are credited here,
not claimed as new. Both couplings have `w=2` on the decisive finite range.

The result here classifies the **complete retuned scalar selector for every
original width and every permitted prime**, including all lower-width
rejections, its body-size guard, the exact dependence on `q`, and the seven
attainable cutoff classes. In particular, it does not claim a new uniform
constant of 311311. The original-width reserve and strict borrowing rule
come from Jose Manuel's PR2234 and the retained ordinary backend. The
retuned profile comes from PR3562/PR3599, including Nick Petalas's work,
and their named predecessors. Their generic stock, borrowing and depth
arguments remain credited to those sources.

## 2. Full stock and the seven exact prime classes

Independent columns give

```
|GL_64(F_q)| = product_(i=0)^63 (q^64-q^i)
             = q^4096 product_(i=1)^64 (1-q^-i).
```

Consequently the definition of `K` is exactly the retained full stock,
including all matrix fibers and the factor `R`. The elementary product
inequality and the finite geometric sum give

```
1 > P(q) >= 1 - sum_(i=1)^64 q^-i > 1 - 1/(q-1) > 1/2.
```

Since `R > 2`, `R P(q) > 1`. Since `R < 2^29` and `q > 2^80`,

```
1 < R^19 P(q)^19 < 2^551 < q^7.
```

It follows that `m(q)` is one of the integers 1 through 7. More explicitly,
class `j` consists of precisely the permitted primes satisfying

```
q^(j-1) < R^19 P(q)^19 <= q^j.                            (2)
```

These are exact rational comparisons. If
`Q(q) = product_(i=1)^64 (q^i-1)`, the equivalent integer comparisons are

```
q^(39520+j-1) < R^19 Q(q)^19 <= q^(39520+j),               (3)
```

because `1+...+64=2080` and `19*2080=39520`. Thus the class definition needs
no real logarithm routine and makes the endpoint conventions explicit.

For any depth `d`, the integral main exponent separates from its correction:

```
k = 4096wd + ceil(log_q(R^d P(q)^d)).                      (4)
```

For `d>0` the correction is at least 1. The useful uniform upper bound is

```
k <= 4096wd + ceil(29d/80),                               (5)
```

since `R^d P(q)^d < 2^(29d) < q^(29d/80)`. For `d=0`, `S=1` and `k=0`.

## 3. Exact depth staircase and all lower-width rejections

Let `b_d` be the first original width with depth at least `d`. Inverting the
floor recurrence gives

```
b_1 = 64,                 b_(d+1) = 64 ceil(b_d/42).      (6)
```

Indeed, `D(e)>=d+1` holds exactly when `42 floor(e/64)>=b_d`.
The thresholds are strictly increasing. Hence `D(e)=d` exactly on
`b_d <= e < b_(d+1)`; depth zero is `1 <= e < 64`.

For `2 <= e < 2^20`, the retuned width is exactly 2: `e>1` and
`e < 2^20 < 2^577`. At `e=1`, the width is 1. For the entire depth-zero
interval, `k=0`, but the body is at most 31 for `e>=2`, and is 1 at `e=1`.
Thus the body-size guard rejects every depth-zero width, even though its
strict borrowing test passes.

At depths 1 through 18, (4) gives `k >= 8192d+1`. The following exact
integer table is obtained only from (6). Its final column equals
`16384d+2-(b_(d+1)-1)`.

| d | b_d | b_(d+1)-1 | Margin below 2k |
| ---: | ---: | ---: | ---: |
| 1 | 64 | 127 | 16259 |
| 2 | 128 | 255 | 32515 |
| 3 | 256 | 447 | 48707 |
| 4 | 448 | 703 | 64835 |
| 5 | 704 | 1087 | 80835 |
| 6 | 1088 | 1663 | 96643 |
| 7 | 1664 | 2559 | 112131 |
| 8 | 2560 | 3903 | 127171 |
| 9 | 3904 | 5951 | 141507 |
| 10 | 5952 | 9087 | 154755 |
| 11 | 9088 | 13887 | 166339 |
| 12 | 13888 | 21183 | 175427 |
| 13 | 21184 | 32319 | 180675 |
| 14 | 32320 | 49279 | 180099 |
| 15 | 49280 | 75135 | 170627 |
| 16 | 75136 | 114495 | 147651 |
| 17 | 114496 | 174527 | 104003 |
| 18 | 174528 | 265983 | 28931 |

Every margin is positive. Therefore every original width in these 18
intervals satisfies `e < 2k` and is rejected by the first test, uniformly in
the permitted prime. This covers every width below `b_19=265984`.

## 4. The exact depth-19 decision

The next depth interval is

```
265984 = b_19 <= e < b_20 = 405312.
```

It still has `w=2`. Equation (4) becomes

```
k = 8192*19 + m(q) = 155648 + m(q).
```

The first test is therefore equivalent, for integral `e`, to

```
e >= 2k+1 = 311297+2m(q).                                (7)
```

All seven possible right sides lie strictly inside this depth interval.
When (7) holds, `e-k >= k+1 >= 155650`. Hence
`floor((e-k)/2) >= 77825 > 64`, so the second test also passes. When (7)
fails, the first test rejects. This proves the claimed classification
through the entire depth-19 interval, including equality at the last
rejected width `e=311296+2m(q)=2k`.

## 5. Every later finite interval passes both guards

The remaining depth intervals below `2^20` are covered by (5). The listed
`U` is the prime-independent bound `8192d+ceil(29d/80)`.

| Original widths, inclusive | d | U | First width minus 2U |
| --- | ---: | ---: | ---: |
| 405312–617663 | 20 | 163848 | 77616 |
| 617664–941247 | 21 | 172040 | 273584 |
| 941248–1048575 | 22 | 180232 | 580784 |

Each margin is positive, so `2k<e` throughout all three intervals. Since
`w=2`, `floor((e-k)/w) > e/4-1 > 64` there, proving the body guard as well.
No monotonicity of `k/e` across a depth jump is assumed.

## 6. Infinite tail, including all later width and depth jumps

This is the earlier stock-threshold dyadic argument, with its inequalities
checked for the retuned `c=1/577`; it is included to give (1) its all-size
quantifier. Two active depth reductions decrease the current width by a
factor less than one half, because `2*42^2 < 64^2`; floors can only decrease
the child. Thus `D(e) <= 2 ceil(log2 e)` for `e>=2`.

For `e>=2^20`, put `j=floor(log2 e)>=20`. Since `R<q` and `P(q)<1`,

```
log_q K < 4096w+1 <= 4097w,
D(e) <= 2(j+1),
w = ceil(e^c) <= 2e^c <= 2*2^(c(j+1)).
```

As `4097wD` is an integer, these inequalities imply, in particular,

```
k <= B_j+1,           B_j = 16388(j+1)2^(c(j+1)).         (8)
```

We show `B_j+1 < 2^(j-1)` for all integers `j>=20`. At the first index,
`21c<1/2` and `sqrt(2)<3/2`, so

```
B_20+1 < 16388*21*(3/2)+1 = 516223 < 524288 = 2^19.
```

For subsequent indices, `c<1/2` implies `2^c<3/2`; hence the ratio of
successive normalized `B` terms is

```
(B_(j+1)/2^j)/(B_j/2^(j-1))
 = ((j+2)/(j+1))*2^c/2 < (22/21)*(3/4) = 11/14 < 1.
```

The additional normalized 1 contracts by `1/2 <= 11/14`. Induction proves
the strict bound for `B_j+1`, and (8) gives `k<2^(j-1)<=e/2`.

Finally `w<=2e^c` and `k<e/2` imply

```
floor((e-k)/w) > e^(1-c)/4 - 1 > 255,
```

because `e>=2^20` and `c<1/2`. Thus the body guard passes too. This tail
covers every later ceiling jump without an enumeration. Combining sections
3–6 proves (1).

## 7. Exact class witnesses and certificate logic

Each class can be certified with small integer comparisons instead of
materializing `S`. Let `A=R^19`. Bernoulli's inequality and the bound from
section 2 give

```
A*(q-1-19)/(q-1) < A*P(q)^19 < A.
```

For an asserted class `j`, the two integer conditions

```
A*(q-20) > q^(j-1)*(q-1),       A <= q^j                 (9)
```

therefore imply (2). They are sufficient certificates; an inconclusive
sandwich is not a class decision. Formula (3) remains an exact alternative.

The accompanying receipt supplies a permitted prime and a certificate of
(9) for each `j=1,...,7`, as well as the cutoff and its rejected predecessor.
Here are the compact witness parameters; each prime is exactly
`q=h*2^n+1`, and `a` is its modular certificate base.

| Class j | h | n | a | Exact selector cutoff |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 193 | 540 | 3 | 311299 |
| 2 | 99 | 270 | 5 | 311301 |
| 3 | 7 | 180 | 3 | 311303 |
| 4 | 225 | 135 | 11 | 311305 |
| 5 | 37 | 110 | 3 | 311307 |
| 6 | 57 | 90 | 23 | 311309 |
| 7 | 213 | 80 | 7 | 311311 |

For every row, the receipt records the strict lower and weak upper integers
of (9) and the exact modular residue `q-1`. All rows have `q>2^80`, positive
odd `h<2^n`. They therefore establish all seven nonempty classes, rather
than merely listing seven possible integers.

The fixed production prime is the class-7 witness
`q* = 213*2^80+1`, so its complete scalar selector fits exactly when
`e>=311311`. The certificate checks its primality again; it does not inherit
primality merely from the earlier result.

For completeness, the witness primality certificate has the following
elementary justification. Suppose `q=h*2^n+1`, with `h` positive and odd,
`h<2^n`, and an integer `a` satisfies `a^((q-1)/2)=-1 (mod q)`. For any
prime divisor `p` of `q`, `a` is a unit modulo `p`, its order divides
`h*2^n`, and its order does not divide `h*2^(n-1)`. As `h` is odd, that
order is divisible by `2^n`. Therefore `p>=2^n+1>sqrt(q)`, contradicting
the existence of a prime divisor at most the square root if `q` were
composite. The modular equation and the integer size hypotheses are exact
checks, not probable-prime tests.

Three exact controls distinguish the theorem's decision from nearby rules:

* At `e=311296+2m(q)`, the correct rule rejects `e=2k`; replacing its first
  `<` by `<=` admits that width, since the body guard then passes.
* At `e=1`, the borrowing test passes but the correct body guard rejects
  body size 1. Omitting that guard changes the selector decision.
* If `R` is omitted from the prescribed stock, then at depth 19
  `1/q < P(q)^19 < 1`, so the logarithmic correction is 0, rather than
  `m(q)>=1`. At the actual depth-19 width `e=311297`, that changed stock
  gives `k=155648`, passes strict borrowing, and has body size 77824. The
  correct stock rejects the same width for every permitted prime. The
  lower bound follows from `P(q)^19>1-19/(q-1)>1/2>1/q`.

## 8. What the scalar source projection does and does not establish

Under the scalar abstraction, each Count represents its nonnegative integer
value, `compare` compares those values, `divide_small` computes the floor,
and `multiply_small`, `increment`, `subtract`, `product`, `fixed_power` and
`divide` have their indicated integer meanings, including exact saturation
and the quotient/remainder identity. The atom-width bisection then returns
the least integer with `w^577>=e`. The `select` cursor follows (6)'s depth
recurrence using the **original** input; its level and stock loops compute
the exact `K` and `S`; its row loop returns the least `q^k>=S`; and its
literal strict and non-strict comparisons are exactly the two guards used
above. This binds the theorem's variables to the source control flow.

The source inspection and separate scalar engines do not prove that all
inherited tape operations implement this abstraction, nor that resources
are available to execute them at arbitrary sizes. No native factory,
GL64 enumeration, payload permutation, SOURCE/history operation, return
cleanup, complete cost invoice, time exponent `tau`, full-support exponent
`beta`, or multiplication join is discharged here. In particular, the
positive body guard concerns only the chosen scalar body size and says
nothing about the correctness of running that body. Quantifying the scalar
decision over permitted primes does not show that the native factory's
separate denominator and chart hypotheses hold for all those primes.

Prepared for ToikY with substantial OpenAI Codex assistance in source review,
proof and separate exact arithmetic checks. The separate agents are AI
assistance, not independent human certification or a proof-assistant kernel.
New text is Apache-2.0; original source notices and predecessor credits
remain applicable.
