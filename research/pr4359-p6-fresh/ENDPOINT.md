# Conditional p6 outer saving 0.00267987

The source-bound p6 native construction in `NATIVE.md` and its finite tensor
construction in `TENSOR.md` support the proposed conditional bound

```
T(n) = O(n (log n)^(1-kappa)),       kappa = 0.00267987.
```

This improves the exponent saving by `0.00037987` over PR4359's `0.0023`
and by `0.00020232` over the preceding all-fresh p3 point `0.00247755`.
These are differences between exponent savings, not measured runtimes.

The result remains conditional on the documented all-column native,
whole-job adapter, spectator, finite compiler, storage, precision, analytic,
fixed-tape, and recovery hypotheses inherited from zxv's PR4359 at
`da637c87c89482bc4c86be36bd0071b3d400dbed`. The new p6 geometry and native
ownership are checked independently in this package; finite checks do not
constitute a full formal multiplication-theorem proof. The selected frontier
is unchanged. Apache-2.0; substantial OpenAI assistance.

The native source and p6 Laurent factorization are credited to zxv's
PR4359. The integer mixed flow is Jacob Alan Sussman's Theorem 1G. The
outer slack family and executable ledger are retained from PR4405, commit
`873d1b3c96a83b701a5c0bba8e37a861e6672fef`, with its attribution to
@Vlado-V's PR1673, @jeremykothe2's PR1758, @chafreaky's PR1786 and their
cited predecessors.

## The new native invoice and its strictification

The exact all-fresh p6 invoice is

```
targets = {5:364, 6:234, 7:728, 8:1209, 9:2769,
           25:448, 41:448, 57:224, 105:224},
paid    = {1:32331, 2:9269, 3:2912, 4:1326, 5:260,
           8:1224, 16:448, 32:448, 48:224}.
```

Its target and paid rank-one moments are 108769 and 108257, leaving surplus
512. Its paid ranks overlap and exceed some target ranks, so the raw rule
does not directly meet the source compiler's strict separation condition.

At the exact saving `C_test=0.00267988`, put `tau=1-C_test` and write
`P_tau,T_tau` for these two moments. The exact certificate proves

```
alpha = P_tau/T_tau < 1 - 1/10^8,
gamma = 108257/((19/4)^C_test*T_tau) < 9999/10000.
```

Use the chronological native tensor construction with `v=150000` copies,
then split each paid rank into consecutive disjoint pieces of size at most

```
J = floor((19/4)^v).
```

Since `J >= (19/4)^v/2`, the normalized paid moment is below
`alpha^v+4*gamma^v`. The certificate checks
`(9999/10000)^10000 < 1/2`, and consequently

```
alpha^v+4*gamma^v
  < 1/(1+150000/10^8) + 4/2^15 < 1.
```

Every paid rank is now at most `J<5^v`, while productive target ranks range
from `5^v` to `105^v`. Thus the finite mixed word meets strict separation
and the tested superpotential. Its positive rank-one surplus is
`108769^v-108257^v`; splitting preserves total rank. No claim about uniqueness
or global optimality of a raw mixed root is required.

## Explicit uniform rank

Choose the outer target and slack family

```
kappa   = 0.00267987,
d       = (C_test-kappa)/7 = 1/700000000,
uniform = kappa+6*d = 375183/140000000,
t       = 1-C_test,
z       = 1-uniform,
z0      = (t+z)/2,
delta   = z0-t = 1/1400000000.
```

The new rank parameters have `m=105^v`, `k_min=5^v` and
`r_max<=floor((19/4)^v)`. The exact integer inequality

```
19^32 < 4^32*5^31
```

proves that the source compiler's exit exponent is below `31/32`. Set
`h=1/32`. For ambient rank `x>=m`, its exit bound gives

```
m E(x)/x < m^h*r_max*x^(-h)
          < 2^B*x^(-h),            B=(79/32)*v=740625/2.
```

Here `(19/4)^4<2^9` follows from `19^4<2^17`, and `105<2^7`. The exact
complement coefficient is `eta=z0*m^(z0-1)`. Since `z0>1/2`,

```
-log2(eta) < 1+7*v*(1-z0) = 11259493/4000.
```

Therefore the entirely rational sufficient choices

```
H0 = ceil((B*delta+1+7*v*(1-z0))/(h*delta)),
H1 = floor(H0*(1-z0)/(z-z0))+1
```

give

```
H0 = 126106333450000,
H1 = 473129651134046950001,
N  = 2^473129651134046950001.
```

The verifier checks `H0>=7*v`, covering every finite base rank. Above
`2^H0` the exit coefficient is below the complement coefficient. Below it,
the positive rank-one surplus gives `L(x)<=x`. The same strong induction as
the source compiler then yields `L(x)<=A*x^z0` for all positive integer
ranks, with `A=(2^H0)^(1-z0)`. The strict final power gap is
`1/1400000000`, proving `P_N/B_N<N^(1-uniform)`.

This specifies a finite exact uniform program at a very large rank. Neither
the tensorized mixed word nor its uniform compilation has been materialized.
The integer batching, scalar word and owned banks are defined by the finite
algorithms, and their full constants must be computed from this new recipe.
The one-less-integer controls only test these sufficient formulas; they do
not establish a globally minimal template rank.

## Outer transfer and replacement constants

Use the same positive-slack family with

```
b=kappa+5*d,  a=kappa+4*d,  q=kappa+3*d,
epsilon=1-d, beta=1-3*d, r0=d/10, stop=d, layout=d.
```

Retain the ordinary BIT saving `0.0027`, atom exponent `0.003`, Strassen
exponent `45/16`, theta power `2`, halo power `48` and core power `128`.
The effective saving `a` is strictly below both the new complex saving and
the admitted BIT saving. The preserved ledger recomputes all nine outer
cost rows and checks all 54 named predicates plus three additional
functional predicates. The limiting main-transform margin is exactly
`262265511/61250000000000000 > 0`. Their exact receipt is generated by
`endpoint.py`.

This uses the current predicate set audited in PR4405. Its comparison to the
older 63-row ledger showed that the 13 omitted rows were historical endpoint
comparisons, with all 50 shared predicates and all nine cost formulas
agreeing. The larger kappa preserves those historical comparisons.

Apply the source precision and stock theorem to the new p6 word and its
tensor/compiled word counts, rather than carrying over the p3 raw scalar
or movement counts. All fixed constants, rational denominators and owned
storage come from the new recipe. The positive precision, stopping,
support-reservoir and fine-prime spare powers checked by the ledger absorb
these fixed constants after an effective input threshold. The unchanged BIT
template retains its separately compiled and delayed-cover construction.

## Replay and next questions

```
python3 -I -O -B research/pr4359-p6-fresh/endpoint.py
```

The integrated command checks the new native invoice and geometry, the
rational-cutoff tensor moment, the explicit uniform rank, and every outer
predicate. Mutation controls reject closing the precision or uniform gap,
asking for the unfunded tested endpoint as kappa, and reducing the BIT
saving below the effective saving. Package source authentication is a
separate complete verifier stage.

Further work includes improving the native controller family, reducing the
tensor power and sufficient rank, independently formalizing native tensor
closure, and reviewing the inherited all-size outer hypotheses. The bounded
controller search is not an optimality proof.
