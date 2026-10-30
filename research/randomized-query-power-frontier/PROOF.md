# The exact stochastic rank-power frontier

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with finite corroboration. No physical
supplier or new kappa is claimed.

## Contract

Fix integers `1 <= R <= k`, a real exponent `0 < t < 1`, and a budget
`0 < B <= R^t`. A random complex `k` by `k` matrix `A` is chosen independently
of the input. Require `E A = I_k`, `rank A <= R` almost surely and a finite
second moment. Its declared query bill is `E (rank A)^t <= B`, with `0^t=0`.
Define the worst-input relative mean-square error by

```
omega(A) = sup_{||x||_2=1} E ||(A-I)x||_2^2.
```

This is a linear response contract. It permits arbitrary complex encoders
and decoders. It does not permit selecting the matrix as a function of the
input, bias, nonlinear decoding or an exact correction supplied for free.
Write `b=B/R^t` for the normalized expected bill.

For interpretation as a shared-query interface, the target is `k` independent
copies of a common unitary job `Q`. A fixed outcome with scalar lane response
`A` has target part `A tensor Q`, so the relative error equals the expression
above. A rank-`r` response factors through `r` linear channels. The price
`r^t` is an **assumption of this optimistic relaxation**. Lane rank is not
automatically a selected supplier's frame rank or recursive-child tariff.
Any application must prove that bridge. Granting conversion, acquisition,
randomness, workspace and restoration free does not supply that bridge.

The inequality also applies if an implementation has a larger complete bill
which dominates `E (rank A)^t`. For a single additive query layer, subadditivity
gives `sum_j r_j^t >= (sum_j r_j)^t >= (rank A)^t`, provided each query really
has response rank at most `r_j` and is charged at least `r_j^t` in the same
normalization. Products, feedback and reused observations need a fresh rank
argument. An arbitrary dirty auxiliary state cannot defeat the stated lower
bound: restrict it to zero. No constructive dirty restoration is asserted.

## Sharp theorem

The exact infimum is attained and is

```
inf omega(A) = k R^(t-1)/B - 1 = k/(b R) - 1.       (1)
```

In particular, without a proper rank cap, `R=k`,

```
B >= k^t/(1+omega).
```

For `0 < t < 1`, equality at any budget in this interval has only the two
response matrices

```
A = 0       with probability 1-B/k^t,
A = (k^t/B) I_k   with probability B/k^t.             (2)
```

Thus the exact optimizer in this price model either omits the whole job or
performs a rescaled whole job. Intermediate response ranks cannot attain it.
This is a statement about expected work and mean-square error, not an
exact-on-each-run implementation or a bound on successful recovery probability.

### Lower bound

Put `r=rank A`. For any fixed matrix let `P` be the orthogonal projection onto
its image. Since `P A=A`, Frobenius Cauchy-Schwarz gives the classical inequality

```
|tr A| = |<P,A>_F| <= sqrt(r) ||A||_F.
```

It is valid for nonnormal and nonsymmetric matrices. Set both sides to zero
when `r=0`. Applying Cauchy-Schwarz also over the probability space gives

```
k^2 = |E tr A|^2 <= (E r) E ||A||_F^2.              (3)
```

For every integer `0 <= r <= R`,

```
r <= R^(1-t) r^t,
```

strictly for `0<r<R`. Consequently `E r <= R^(1-t) B`. Unbiasedness yields

```
E ||A-I||_F^2 = E ||A||_F^2 - k.
```

The error covariance `E (A-I)* (A-I)` is positive semidefinite, and its largest
eigenvalue is at least its trace divided by `k`. Substitution in (3) proves
`omega >= k/(R^(1-t)B)-1`, which is (1).

### Attainment and equality

With probability `b` choose a uniformly random `R`-subset `S` of the `k`
coordinates, let `P_S` be its coordinate projection, and set
`A=k P_S/(bR)`. With probability `1-b` set `A=0`. Directly,

```
E A = I,     E (rank A)^t = b R^t = B,
E (A-I)* (A-I) = (k/(bR)-1) I.
```

This finite law attains the worst-input bound, not only an average over
inputs. More generally one may use any distribution of rank-`R` orthogonal
projections satisfying `E P=(R/k)I` on the nonzero branch. Uniform coordinate
sparsification and its usual `k/R-1` variance at `b=1` are classical; see
Safaryan, Shulgin and Richtarik's [compression uncertainty paper](https://arxiv.org/abs/2002.08958).
No priority is claimed for that construction or the trace inequality. The
new interface calculation includes the concave rank-power bill, random zero
branch, exact worst-input optimum and its equality restriction.

To prove (2), equality in (1) forces equality in every intervening bound.
In particular `E r=R^(1-t) E r^t=R^(1-t)B`. Strictness at intermediate ranks
forces `r` to be either zero or `R`. When `R=k`, a nonzero `A` has image the
whole space, so equality in the fixed-matrix trace inequality forces
`A=alpha I`. Equality in probabilistic Cauchy-Schwarz forces the same scalar
`alpha` on every nonzero branch, with common nonnegative trace phase.
The cost fixes its probability to `b=B/k^t`; unbiasedness then gives
`alpha=1/b`. Conversely (2) attains every bound. This includes `b=1`.

## Consequences and boundary of the obstruction

For a normalized tolerance `omega <= epsilon^2`, the unrestricted-cap
interface cannot save more than the fraction `epsilon^2/(1+epsilon^2)` of
the deterministic rank-power bill. At `epsilon=2^-g`, this is exactly
`1/(4^g+1)`. This is a normalized relative MSE tolerance; `g` has not been
identified with any selected word's precision guard. For example `g=6`
allows at most `1/4097` expected fractional saving. Zero variance permits
no saving. The explicit optimum still has a nonzero probability of returning
zero when the budget is below the full bill.

With a hard proper cap `R<k`, even the maximum allowed bill leaves the
strict error floor `k/R-1`. Independent repetition reduces variance but pays
every repetition; it does not supply a free refinement of (1).

The result rejects cheap, uniformly accurate **input-independent linear**
random compression under the stated tariff. It does not exclude adaptive or
biased approximations, low-dimensional promised inputs, nonlinear methods,
high-probability verification/retry, or another response-to-cost bridge.
There is no selected invoice, supplier, compiler or multiplication theorem
attached to this relaxation. All physical/native costs and the five selected
framework assumptions remain unresolved.

## Finite verification

`verify.py` computes complete rational means and every error-covariance entry
for the finite attainers. It also exhausts small integer matrices for (3)'s
pointwise trace bound, tests equality by literal matrix products, checks the
power-price comparison by integer powers, and rejects invalid distributions
and corrupted scales. The written proof establishes arbitrary dimensions,
complex fields and real `t`; the finite verifier does not establish those
claims by extrapolation.
