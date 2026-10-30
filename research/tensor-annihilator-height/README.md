# Exact coefficient heights for the growing-support tensor annihilator

This scoped written proof determines every coefficient denominator in the
Gaussian-rational annihilator from [zxv's PR #5436](https://github.com/CrocSwap/integer-mult-bounds/pull/5436).
It also proves that its primitive Gaussian-integer coefficient list has
quadratic maximum bit height and cubic uncompressed storage. This is a new
arithmetic step toward that package's open coefficient-pricing question.
The predecessor's tensor identity and support theorem are cited, not replayed.
No physical implementation, complete price, new kappa or supplier admission is
claimed. Independent human and formal proof-kernel review are unclaimed.

## Exact result

Let `f>=1`, `n=f+1`, `S=f(f+1)/2`, `pi=2+i`, `rho=2-i`, and
`alpha=pi/rho=(3+4i)/5`. Write

```text
p_f(z) = product_(k=0)^f (z-alpha^k) = sum_(j=0)^n c_j z^j,
P_f(z) = rho^S p_f(z)
       = product_(k=0)^f (rho^k z-pi^k) = sum_(j=0)^n d_j z^j.
```

For each `0<=j<=n`, put

```text
a_j = binom(n-j,2),  b_j = binom(j,2),  e_j = S-b_j.
```

Here `binom(0,2)=binom(1,2)=0`. The exact prime valuations are

```text
v_pi(c_j)=a_j,        v_rho(c_j)=-e_j,
v_pi(d_j)=a_j,        v_rho(d_j)= b_j.
```

In particular every coefficient is nonzero. Its Gaussian denominator ideal is

```text
{delta in Z[i] : delta*c_j in Z[i]} = rho^e_j Z[i].
```

The least positive ordinary integer clearing both real and imaginary
denominators of `c_j` is exactly `5^e_j`. The common Gaussian denominator ideal
of the whole monic list is `rho^S Z[i]`, and its least positive ordinary integer
common denominator is `5^S`. These are exact equalities, not sufficient bounds.

`P_f` is primitive over `Z[i]`. Every nonzero Gaussian-integer polynomial of
degree at most `f+1` vanishing at `1,alpha,...,alpha^f` is a nonzero
Gaussian-integer multiple of `P_f`. Thus global scalar renormalization cannot
reduce its primitive coefficient height. This statement fixes consecutive
powers and the degree bound; it does not cover other sparse annihilators.

The following height bounds hold, with the usual complex absolute value:

```text
5^((a_j+b_j)/2) <= |d_j| <= binom(n,j) 5^(S/2),
5^(S/2) <= max_j |d_j| <= 2^n 5^(S/2),
sum_j log_2 |d_j| >= log_2(5) binom(f+2,3).
```

The last lower bound and the displayed upper bound imply `Theta(f^3)` bits
for a dense explicit binary list of the primitive coefficients, with real and
imaginary integers stored separately. The largest coefficient needs
`Theta(f^2)` bits. This concerns that representation. A factored description
or on-demand generator need not store the dense list.

For calibration, at `f=1` the primitive polynomial, in ascending order, is
`[(2+i), -4, (2-i)]`. At `f=2` the exact ordinary denominator exponents of the
monic coefficients are `(3,3,2,0)`.

## Proof

The Gaussian integers have a Euclidean norm `N(x+iy)=x^2+y^2`, hence unique
factorization. The norm-five elements `pi,rho` are distinct primes. Their
coprimality also follows from the explicit identity
`-pi+(1+i)rho=1`. Consequently valuations at these two primes extend to
`Q(i)`, with `v_pi(alpha)=1` and `v_rho(alpha)=-1`.

The coefficient `c_j` is the signed sum of `alpha^(sum_(k in T) k)` over
all subsets `T` of `{0,...,f}` of size `n-j`. At `pi`, the unique summand of
least valuation uses the smallest `n-j` exponents, namely
`0,...,n-j-1`. Their sum is `a_j`. A unique least-valuation term cannot cancel:
after division by that prime power it is nonzero modulo the prime, and every
other term is zero. Thus `v_pi(c_j)=a_j`.

At `rho`, the unique summand of least valuation uses the largest `n-j`
exponents, namely `j,...,f`. Their sum is `e_j`, so
`v_rho(c_j)=-e_j`. This includes the empty subset at `j=n` and the full
subset at `j=0`. No denominator prime other than `rho` occurs, since every
summand belongs to `Z[i,rho^-1]`. It follows that
`rho^e_j*c_j` is integral and is not divisible by `rho`. Primality then gives
the asserted denominator ideal, including necessity of its exponent.

For an ordinary integer `m`, complex conjugation gives
`v_pi(m)=v_rho(m)`. Since `pi*rho=5` and the primes are coprime,
`rho^e_j` divides `m` exactly when `5^e_j` divides `m` in `Z`.
This proves the ordinary denominator statement. The maximum `e_j` is `S`.
Multiplying by `rho^S` gives the stated valuations of `d_j`.

The leading and constant coefficients of `P_f` are respectively
`rho^S` and `(-1)^n pi^S`. They are coprime, so the coefficient list is
primitive. The powers of `alpha` are distinct: if `alpha^t=1` then its `pi`
valuation is `t=0`. Any polynomial of degree at most `n` vanishing at all
`n` distinct powers is a scalar multiple `lambda p_f`, or zero. If its
coefficients are Gaussian integers then its leading coefficient `lambda` is
in `Z[i]`. The common denominator ideal forces `lambda=u rho^S` with
`u in Z[i]`. For nonzero `u`, `|u|>=1`, which proves the normalization claim.

A nonzero Gaussian integer divisible by `pi^a_j rho^b_j` has modulus at
least `5^((a_j+b_j)/2)`. The coefficient formula has `binom(n,j)` summands,
each of modulus one before multiplication by `rho^S`; the triangle inequality
gives the upper bound. The endpoints give the maximum-height lower bound.
Finally

```text
sum_(j=0)^n (a_j+b_j) = 2 binom(n+1,3) = f(f+1)(f+2)/3.
```

Taking logarithms proves the total-height bound. For a Gaussian integer `x`,
`max(|Re x|,|Im x|)>=|x|/sqrt(2)`. Thus a binary coordinate-list encoding
has at least this total logarithmic height minus `(n+1)/2` bits, up to its
fixed per-coordinate conventions. The upper bound is `O(f^3)` as well.
This proves the asserted storage order without a computation model for
factored or compressed output.

## Evidence and reproduction

`verify.py` constructs the new integer polynomial directly from its integral
linear factors and independently constructs the monic polynomial with pairs
of exact `Fraction` values. For `f=1,...,32` it checks all 592 coefficients,
both exact prime valuations, the ordinary and Gaussian denominator exponents,
normalization, and both coefficient-height inequalities. A separate subset
sum oracle enumerates 1,020 terms at `f=1,...,8`. Forty-two controls reject
changed endpoints, nonprimitive scaling, conjugated coefficients, omissions,
zero coefficients and out-of-range widths. Checks stay enabled under `-O`.
These are finite corroborations of the written all-width proof.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/tensor-annihilator-height/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/tensor-annihilator-height
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/tensor-annihilator-height --check-source-history
```

Any CPython 3.12 interpreter with the standard library can replace the absolute
interpreter path. The verifier prints `PASS_TENSOR_ANNIHILATOR_HEIGHT` in a
fresh JSON receipt bound to all five package files and both source documents.
It creates no output files. Registered normal and optimized runs execute the
same complete check. No stored receipt is accepted as evidence.

## Scope and implementation constraints

The exact claims concern one Gaussian-rational geometric progression and its
minimum-degree annihilator. They give neither a useful productive transform
nor a lower bound for arbitrary native programs. Different supports, higher
degree, other generators, approximate identities and factored representations
remain outside scope. No original native engine, selected supplier replay,
physical coefficient arithmetic, compiler/tape/ownership contract, recovery
proof, Lean or Docker check is run.

The checker has no recursion and every loop has a finite bound. The largest
width is 32, each polynomial has at most 34 coefficients, subset enumeration
uses at most 512 subsets per width, and integer-power exponents are capped at
1,024. Prime division strictly reduces the positive norm and has a bit-length
iteration bound. Python's managed arithmetic allocates during computation;
this is an explicit fixed-allocation deviation, bounded here by those limits.
Functions are below 60 lines. Warning-strict normal and optimized replay are
the available runtime diagnostics; no static type-checking dependency is added.

## Open next questions

- Can an actual productive consumer use this annihilator without storing the
  dense coefficient list? First specify its factored or streaming coefficient
  interface and count all arithmetic, field passes and restoration. A priced
  productive consumer is absent.
- Can a different support of `f+2` powers have smaller primitive coefficient
  height? First fix the allowed integer exponent set and compare its exact
  Vandermonde minors. This proof's consecutive-degree uniqueness does not
  answer that optimization problem.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.
Credit zxv's PR #5436 for the fixed-generator tensor escape, the existing
quadratic upper bound and the explicit pricing question; Anthony Chefles for
classical multi-copy independence; and classical Gaussian-integer valuation
and polynomial methods. The source retains Chris R, Ali Romman, Dillon
Amburgey, David Ganz, Cinna Davis, Cao Yifan, Jacob Alan Sussman and the native,
geometry, compiler and verification lineage. Their results are cited as
predecessors; no new verification or authorship of those results is claimed.
