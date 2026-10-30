# General-rank power order from a finite root budget

Compare the complete paid-minus-target invoice for every `0<t<1`:

```sh
python3 -B scripts/compare_power_variation.py OLD.json NEW.json
```

The inputs use the existing [invoice contract](recursive-invoice-preflight.md).
Ranks need not be powers of one base. The report hashes both input files and
keeps target debits. It can certify strict uniform order or isolate every
interior crossing. It returns `inconclusive` when its root budget is not fully
used. This is a conservative certificate, not a complete classifier for all
exponential polynomials. It verifies invoice arithmetic, not a construction,
source extraction, native operator, compiler endpoint or new κ.

For example, old paid jobs `2,3` and new jobs `1,6` have difference
`(2^t-1)(3^t-1)>0` throughout the open interval. The concave-order screen is
inconclusive and the common-base tool rejects these ranks. The new tool proves
strict order from a double zero at t=0 and a two-root global budget. Reversing
the invoices gives a strict improvement.

The integer difference `6-4*2^t-3*3^t+2*6^t` factors as
`2*(2^t-3/2)*(3^t-2)`. It has two interior crossings even though both endpoint
values are1. The default grid gives certified brackets `(37/64,19/32)` and
`(5/8,41/64)`. A coarse two-cell grid returns inconclusive. Matching signs on a
finite sample do not prove uniform order.

## What the report means

- `equal`: every signed rank coefficient cancels exactly.
- `uniformly_lower` or `uniformly_higher`: strict order at every `0<t<1`, with
  no interior equality. A rational interior value fixes the sign.
- `crossing`: all interior roots are isolated, simple and accounted for. Each
  bracket contains exactly one root; there are no other interior roots.
- `inconclusive`: unaccounted roots, a possible touching root, inadequate grid
  resolution or an unresolved interval sign prevent a certificate. It is not
  evidence that the proposal is bad or that two invoices are equal.

Root witnesses contain exact rational endpoint intervals. An exactly zero
interval at an interior grid point gives an exact root witness. Otherwise only
strict opposite signs on adjacent grid points certify a root. Unknown signs
are never rounded to zero. `interior_roots` is null until the count is proved;
the separate lower and upper bounds remain valid.

`--bits` selects16..256 dyadic bits, default128. `--grid` selects2..256 equal
cells, default64. The grid is used to locate roots, not to justify their total
count. The bound applies to all real exponents, so roots outside `(0,1)` can
leave an unspent budget. Endpoint multiplicities above2 and touching interior
roots can also remain unresolved. Use the exact common-base Sturm classifier
when it applies; keep its stronger complete handling of repeated roots.

At most512 uncancelled ranks are allowed; exact cancellation happens before
this limit. Existing invoice byte, rank, coefficient and contract limits apply.
The arithmetic cache has at most32,768 power intervals. No external library,
source producer or scientific replay is needed.

## Proof of the global root bound

Let `F(t)=sum c_i r_i^t` with distinct increasing positive ranks and nonzero
real coefficients. Let V be the number of sign changes in the ordered c_i.
The classical generalized Descartes rule gives at most V real zeros, counted
with multiplicity. The following Rolle argument proves the form used here.

Divide by the positive function `r_0^t`. The result is
`G(t)=c_0+sum_(i>0)c_i(r_i/r_0)^t`. Its derivative has the signs of
`c_1,...,c_n`, because every `log(r_i/r_0)` is positive. Induct on the number
of terms; the one-term case has no zero. Multiplication by a nonzero exponential
and the change of exponent do not change zero multiplicities.

If c_0 and c_1 have opposite signs, the derivative has V-1 variations. Rolle's
theorem, including multiplicities, bounds the zeros of G by one plus the zeros
of G', hence by V. If their signs agree, the derivative has V variations.
As t tends to minus infinity, G has the sign of c_0 and G' the sign of c_1.
Before the first zero of G, the derivative must take the opposite sign to
reach that zero. It therefore has an extra zero before it. Together with
between-root zeros and multiplicities, this gives at least as many derivative
zeros as function zeros. The same bound V follows. Infinite zero sequences
would give arbitrarily many derivative zeros and contradict the induction.
All functions are analytic; these zeros have finite multiplicity unless F is
identically zero. Distinct exponential terms are linearly independent by the
same lowest-term limit, so only the cancelled invoice is identically zero.

## Exact endpoint multiplicities and certificate closure

At e=0 or1, `F(e)=sum c_r r^e` is an exact integer. If nonzero, there is no
endpoint root. If zero, the multiplicity is at least1. Also

```
F'(e) = sum c_r r^e log r
      = log(product_p p^(sum_r c_r r^e v_p(r))).
```

Unique prime factorization makes this derivative exactly zero if and only if
all integer prime exponents vanish. The program sums those exponents; it does
not construct huge powers. A zero derivative certifies multiplicity at least2.
It does not claim this lower bound is always the exact multiplicity.

Each strict sign-change bracket or exact interior zero uses at least one of
the V available roots. Adjacent brackets have disjoint interiors and nonzero
endpoints; exact zeros cannot be counted again in a bracket. Subtract the
endpoint multiplicity lower bounds. If the interior witnesses consume every
remaining root, each witness has multiplicity exactly1 and all endpoint lower
bounds are exact. There are no other real roots. In particular, each interior
root is simple and crosses sign. With no interior root, continuity and one
strict interior interval establish the uniform sign. Without exhaustion the
program reports inconclusive. This is the step that a sampled plot lacks.

## Verification and credit

```sh
python3 -B -m unittest discover -s tests -p 'test_research_power_variation.py' -v
```

The tests compare610 common-base profiles against the separate exact Sturm
classifier and16 mixed-rank factored profiles against integer-power root tests.
They cover double endpoint zeros, two crossings with matching endpoint signs,
missed crossings on a coarse grid, touching roots, exact grid roots, roots
outside the interval, coefficients of magnitude10^60, target debits, cancelled
support, malformed input, contract mismatches and the real isolated optimized
CLI with byte hashes. The tests require substantial successful certification;
an implementation that always returns inconclusive does not pass.

Credit the classical Descartes/Rolle argument, woklerx's specialized
[T16 unique-crossing proof](../../research/t16-unique-crossings/README.md),
mightyOil's moment-order audit, zxv's signed-invoice interface and their retained
predecessors. Reuse the directed-integer power engine and retain the common-base
Sturm tool as a separate stronger method on its domain. New shared integration
and checks by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
[Discussion5784](https://github.com/CrocSwap/integer-mult-bounds/discussions/5784)
records scope and verification. No independent human or formal-kernel review
is claimed. More exact roots or a better comparison do not admit a supplier.

## Open next questions

Can exact additional root witnesses settle a useful source invoice that remains
inconclusive? Start with a pinned complete bill and the reported unused budget.
A proof of any touching-root multiplicity or an outside-domain root is needed;
finer sampling alone does not resolve that obligation.
