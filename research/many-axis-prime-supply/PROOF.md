# Prime source supply for the newer many-axis tensor caller

ToikY, with substantial OpenAI Codex assistance. Apache-2.0.

## Scope and the source obligation

PR4024, head `e99297be6749518a1b5b85cd129ecaf204d26c63`, supplies the
encoded CRT address conversion but explicitly assumes pairwise-coprime odd
source lengths. Its numerical tensor dependency is PR3935, head
`240597ed313fc2854c0462b23c89dc3bae72aaf5`. This package supplies those lengths
for the newer many-axis asymptotic caller, subject to an explicit sufficient
cutoff and period condition. It supplies no numerical tensor composition,
integer recovery, native execution, complete supplier or new kappa.

The actual PR3935 `TensorPlan` has `dimensions=axes+1` resampled scalar axes.
Call this number `D`; its internal `d` is `D+1`. Its target lengths are
`t_i in {2^ell,2^(ell-1)}`, with the final axis always `2^ell`. In
`TensorPlan.production_axis`, putting `g=t-s`, the exact ratio predicates are

```
4d*g > s,              (2d-1)*g < s.
```

Equivalently, `t/(4d+1)<g<t/(2d)`. The same method also requires
`s>2*(target_halo+2*w)`. The source method is authenticated before its complete
AST is extracted and checked with an integer-semantic Count adapter. The
source imports and numerical engine are not executed. This is a host reference
check of the exact method, not execution of its encoded Count implementation.

The old prime-length argument in canonical source08,
`upstream/build/sections/08-assembly.tex`, uses Harvey--van der Hoeven's
prime-interval lemma with a condition of the form `log(t)>8d`. Its old small
dimension exponent makes that condition eventual. Under the newer laws
`D=Theta(p^.997)` and `ell=Theta(p^.003)`, `log(t)/d` instead tends to zero.
This is a change of admissible parameter regime, not a counterexample to the
old lemma. We replace that particular source-supply argument; the existing
CRT algebra, trial-division idea and tensor cost results retain predecessor
credit.

## Explicit prime-supply statement

Let integer `ell>=2^32`, `D>=1`, `d=D+1<=ell^334`, and let every target
`t` be `2^ell` or `2^(ell-1)`. For each of the two target sizes use the
interior interval

```
I(t,d) = (a,b],
a = t*(1-1/(3d)),       b = t*(1-1/(4d)).
```

Each interval contains at least D primes. The intervals for the two target
sizes are disjoint. Choose as many increasing primes from each as its target
flags require, then merge the two lists in the original flag order. This gives
D distinct odd primes `s_i` and therefore pairwise coprimality. For every axis,

```
t/(4d) <= t-s < t/(3d).
```

These inequalities lie strictly inside the actual source ratio predicates:
`t/(4d)>t/(4d+1)` and `t/(3d)<t/(2d)`.
Writing `S=product(s_i)` and `T=product(t_i)`, Bernoulli gives

```
S/T > (1-1/(3d))^D >= 1-D/(3d) > 2/3,
```

so `T/S<3/2<2`. No numerical approximation or search heuristic establishes
these ratio or coprimality conclusions.

For the complete source method, additionally assume

```
K = target_halo+2*w <= 2^(ell-3).
```

Since `d>=2`, each selected prime is greater than
`(5/6)*2^(ell-1)>2^(ell-2)>=2K`. Hence the period predicate also holds.
This is a separate sufficient condition; prime abundance alone does not admit
an arbitrarily large halo. In the retained newer caller, halo and `w` are
polynomial in p, whereas `2^ell` exceeds every fixed polynomial. This condition
is therefore eventual under those caller premises. Unrelated
`production_common` Gaussian, precision, separation, native and global
admissions remain outside this length-supply result.

## Imported analytic input and effective cutoff

We use Fiori, Kadiri and Swidinsky, *Sharper bounds for the error term in the
Prime Number Theorem*, [arXiv:2206.12557v2](https://arxiv.org/pdf/2206.12557v2),
Corollary 22. Their explicit unconditional theorem implies the following
slightly weakened estimate, valid for every real `x>=2`:

```
|pi(x)-Li(x)| <= 9.2211*x*sqrt(log(x))*exp(-.8476*sqrt(log(x))).
```

Here `Li(x)=integral_2^x dt/log(t)`. The decay coefficient `.8476` is a
deliberate weakening of the corollary's more precise coefficient. This analytic
theorem is an imported mathematical input. The finite verifier does not
reprove its zeta-function analysis or claim formal-kernel verification.

Put `y=log(t)`. For `d>=2,t>=4`, both endpoints are between `sqrt(t)` and t.
Because `9.2211<10` and `.8476/sqrt(2)>1/2`, the sum of their two prime-counting
error bounds is at most `20*t*sqrt(y)*exp(-sqrt(y)/2)`. Also

```
Li(b)-Li(a) >= (b-a)/log(t) = t/(12*d*y).
```

Consequently

```
pi(b)-pi(a) >= t/(12*d*y) - 20*t*sqrt(y)*exp(-sqrt(y)/2).
```

The following two effective inequalities suffice for at least D primes:

```
480*d*y^(3/2)*exp(-sqrt(y)/2) <= 1,
t >= 24*d*D*y.
```

We now establish both uniformly without constructing a giant target integer.
For `ell>=2`, the two target sizes satisfy `ell/4<=y<=ell`, using
`1/2<log(2)<1`. Thus the first left side is at most

```
480*ell^(335.5)*exp(-sqrt(ell)/4)
   = 480*z^671*exp(-z/4),       z=sqrt(ell).
```

For `ell>=2^32`, `z>=z0=2^16`. At that endpoint, its logarithm is less than
`7+671*16-2^14 = -5641`, since `log(480)<7` and `log(z0)<16`.
The derivative of `log(480)+671*log(z)-z/4` is negative for `z>=z0`, because
`4*671<z0`. The first inequality follows for the entire domain.

For the second, `24*d*D*y<=24*ell^669`, while `t>=exp(ell/4)`.
At `ell0=2^32`,

```
log(24*ell0^669) < 5+669*32 = 21413 < ell0/4 = 1073741824.
```

The derivative of `ell/4-669*log(ell)-5` is positive in that domain, because
`4*669<ell0`. This proves the second inequality uniformly. All constants in
these threshold comparisons are checked by small exact integers/rationals.
The verifier never forms `2^(2^32)` or runs an astronomical prime search.

Finally, the newer growth laws imply
`d=O(ell^(997/3))`, and `997/3<334`. Thus `d<=ell^334` holds eventually,
including fixed constants in those growth laws. The cutoff is deliberately
conservative; no near-optimal or practically useful prime-search threshold is
claimed.

## Uniform construction and complete setup bill

This section describes a uniform fixed-tape algorithm. It is a proof of
constructibility and a conservative bill; the finite program in this package
is explicitly a host-integer reference rather than that machine.

Compute encoded integer endpoints

```
lo = t-ceil(t/(3d))+1,          hi = t-ceil(t/(4d)).
```

They enumerate exactly `(a,b]`, including nonintegral endpoints correctly.
For each target size, scan candidate integers from lo through hi in increasing
order. Test primality by division by every integer from 2 through candidate-1;
reject as soon as one remainder is zero. This deliberately simple test is
correct and avoids an unpriced primality oracle. Stop when the required quota
is reached. The proved prime count guarantees successful completion above the
cutoff. Below it the finite reference may reject insufficient intervals; it
does not manufacture a repeated or composite length.

All candidates, divisors and remainders have `O(ell)` bits. The dimension and
quota counters fit the same bound in the admitted domain; the source flags
are a packed stream, not D separate runtime tapes. Binary schoolbook division
uses a fixed number of scratch words and `O(ell^2)` symbol operations including
the scan/return costs. Two target intervals contain at most `2r` candidates,
where `r=2^ell`; each has fewer than r divisors. Their complete conservative
search cost is therefore

```
O(r^2*ell^2).
```

The two selected-prime tables use `O(D*ell)` cells. A monotone cursor in each
table, while scanning the original flags, emits the source words in the
original axis order; the final full-axis flag remains implicit exactly as in
`TensorPlan`. No random access or per-axis tape is needed. Endpoint setup,
quota counting, list copies, erasure and restoration cost
`O(poly(ell,log(d))+D*ell)` in addition to the search. A fixed inventory of
arithmetic, table and output tapes suffices, with `O(D*ell+ell)` visited
backing for this producer. The caller must consume and clear its distinct
owned output before reuse; borrowed flag and parameter heads are restored.
No source-meter constant or literal fixed-tape execution is claimed.

Computing the total source product and CRT metadata uses `O(D*ell)`-bit
integers, hence polynomial setup in p under `D*ell=Theta(p)`. With the newer
`ell=Theta(p^.003)` law, the entire setup above, including conservative table
management, is `2^O(ell)*poly(p)=2^o(p)`. The actual caller volume
`V=C*T*R`, with `log2(T)=Theta(p)` and `C,R>=1`, is at least `2^(c*p)` for a
fixed positive c. Thus setup is `o(V)` and fits the retained conversion
allowance. This does not price the unchanged router/native operations or
turn their conditional universal premises into verification results.

## Evidence and controls

The five finite cases include both target widths, nonmonotone flags, repeated
target sizes and source-order reconstruction. Every returned prime is checked
by the host trial-division reference, full source method, exact rational band,
distinctness and complete product ratio. The emitted source words have exactly
ell little-endian bits per axis; the flags omit the final implicit one.
An independent checker uses a separate Eratosthenes sieve and independently
reconstructs the complete bytes and source predicates. These small examples
corroborate the implementation and source binding; their existence does not
prove the imported analytic input or the large-cutoff theorem.

Negative controls cover insufficient supply, nonliteral flags, a missing final
full axis, an attempted giant finite run, strict source ratio failures, period
failure and a composite. Separate boundary tests exercise explicit supplied
values, source authentication, receipts and read-only exports. Exact validation
receipts distinguish host execution from the written uniform algorithm.

Credit the source08 authors and Harvey--van der Hoeven for prior prime-interval
and trial-division construction; CinnaDavis's prime-selector transfer and
Chafik Boukhalfa/PR1786 and its audit for prior selector/prime-supply work;
Fiori--Kadiri--Swidinsky for the analytic estimate; Jose Manuel/PR3935 for the
actual production predicates and newer caller; and Tekalign/PR4024 for the
explicit unresolved CRT source premise and encoded layout. Source README
credits and frozen bytes are retained. This result closes that stated length
premise, not the numerical recovery, full multiplication or selected frontier.
