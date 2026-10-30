# Compare a power invoice over the whole exponent interval

An inconclusive concave-order result does not prove that a power cost changes
sign. When all changed ranks are powers of one integer, this tool gives an exact
answer for **every** exponent `0 < t < 1`:

```sh
python3 -B scripts/compare_power_polynomial.py OLD.json NEW.json
```

The inputs use the [recursive invoice schema](recursive-invoice-preflight.md).
Their contracts must match. The tool first cancels equal rank terms in
`(new paid-new targets)-(old paid-old targets)`. It then finds an integer base
`b > 1` such that each remaining rank is `b^j`. Rank one has exponent zero. A
constant or zero difference uses base two by convention. Unsupported ranks fail
with exit code2; the tool does not round them to a common base.

The report binds the exact input bytes by SHA256. It gives the signed polynomial
coefficients in ascending order, endpoint multiplicities, exact root counts and
a rational sample. All arithmetic uses integers and fractions. No grid sampling,
floating-point roots or precision choice determines the result.

| Classification | Meaning for the new cost minus the old cost |
|---|---|
| `uniformly_lower` | Strictly negative for every `0 < t < 1`. |
| `uniformly_higher` | Strictly positive for every `0 < t < 1`. |
| `nonpositive_with_equality` | Never positive, with at least one interior zero. |
| `nonnegative_with_equality` | Never negative, with at least one interior zero. |
| `crossing` | Both signs occur in the open exponent interval. |
| `equal` | The signed rank difference is zero. |

For example, old paid jobs `{"2":2}` and new jobs `{"1":1,"4":1}` give
`P(x)=(x-1)^2`. General concave order is inconclusive, but the new power cost is
strictly higher for every `0 < t < 1`. By contrast, old jobs `{"2":12}` and new
jobs `{"1":9,"4":4}` give `(2x-3)^2`: the result has one interior equality and
is not strict throughout the interval. Old jobs `{"1":3}` and new jobs `{"2":2}`
give `2x-3`, so the cost crosses zero. These are declared arithmetic examples,
not new legal circuit replacements.

## Exact reduction and proof

Let `d_r` be the signed difference after paid and target terms are combined.
Write each remaining rank as `r=b^j`, and set

`P(x) = sum_j d_(b^j) x^j`.

The map `x=b^t` is a continuous, strictly increasing bijection from `(0,1)` to
`(1,b)`. Thus `sum_r d_r r^t = P(b^t)`, with the same signs and zeros. Factoring
the first nonunit rank and dividing its prime exponents by their greatest common
divisor gives its primitive integer base. Repeated exact division checks every
other rank. If a common integer base exists, that primitive base also works.

The zero polynomial gives `equal`. For a nonzero polynomial, first divide out
every factor `x-1` and `x-b`. These zeros lie outside the open domain. Record
their multiplicities; do not count them as interior equalities. All later GCDs
divide this reduced polynomial, so neither endpoint can become a root again.

For any remaining nonconstant polynomial `G`, compute `D=gcd(G,G')` and the
square-free quotient `S=G/D`. Its roots are the distinct roots of `G`. Form the
Sturm sequence `S,S',-rem(S,S'),...`, stopping at a nonzero constant. At an
endpoint, omit zero values before counting adjacent sign changes. The difference
between the variation counts at1 and b is the number of distinct interior roots.
All divisions are exact operations in Q. Clearing denominators and dividing by
positive content preserve the signs needed by Sturm's theorem.

To obtain multiplicity parity, repeat with `G <- gcd(G,G')`. Let `n_j` be the
distinct interior root count at step j, starting with j=0. A root of multiplicity
m appears in exactly the first m counts. Hence its contribution to

`n_0 - n_1 + n_2 - n_3 + ...`

is one if m is odd and zero if m is even. This sum counts odd-multiplicity
interior roots. Each such root changes the sign of a real polynomial. Its
presence proves `crossing`. If none exists, the sign is constant away from the
interior roots. One nonzero rational sample determines that sign. A polynomial
of degree d cannot vanish at d+1 distinct sample points, so the bounded sample
selection must succeed. With no interior roots the order is strict. With only
even-multiplicity interior roots the order is weak, with equality at those roots.

This uses classical Sturm theory, not a new root-count theorem. See Philippe
Pebay, J. Maurice Rojas and David C. Thompson,
[Sturm's Theorem with Endpoints](https://arxiv.org/abs/2208.07904). This tool
removes endpoint factors before the count to make its open-domain convention
explicit. The small polynomial implementation uses standard-library fractions;
the shared invoice tools and CI do not require a computer-algebra installation.

## Verification and limits

The independent low-degree oracle checks all343 quadratics with coefficients in
`{-3,...,3}` by their exact extrema and monotone intervals. A second oracle checks
288 products with known endpoint, repeated interior and nonreal roots. Further
checks cover irrational interior roots, degree29, target credits, cancellation,
large coefficients, unsupported ranks and the isolated optimized CLI.
An optional independent check uses SymPy1.14.0 root isolation on64 further
polynomials, including24 dense degree29 cases with coefficients near the input
limit. That check is skipped when SymPy is not installed; the other tests and
the tool need only the standard library.

```sh
python3 -B -m unittest discover -s tests -p 'test_research_power_polynomial.py' -v
```

The invoice rank limit10^9 bounds the polynomial degree by29. The existing count,
input-size and contract limits still apply. Only uncancelled ranks need a common
base. This can help reject or price a proposed rank exchange before a full
construction replay. It does not authenticate a circuit, detect an omitted
source charge, establish ownership or native legality, or admit a compiler or
kappa claim. Even `uniformly_lower` concerns only the declared common tariff.

The [pointwise power comparator PR5732](https://github.com/CrocSwap/integer-mult-bounds/pull/5732)
handles arbitrary supported ranks at one rational exponent. The
[concave witnesses PR5731](https://github.com/CrocSwap/integer-mult-bounds/pull/5731)
explain the broader tariff screen. Those tools are complementary; this tool
does not depend on their unmerged code. The source invoice interface retains
zxv's comparator, mightyOil's T16 audit and all credited predecessors.

## Open next questions

The [multi-candidate region checker](candidate-power-regions.md) uses this
reduction to choose among up to eight complete invoices across the domain.

- Can an actual proposed exchange with an inconclusive concave screen use this
  certificate? Supply the complete changed paid and target terms and the same
  consumer contract before applying the tool.
- Can noncommensurate rank differences receive a uniform sign certificate?
  This polynomial reduction does not answer that question. A finite exponent
  sample must not be treated as a proof over an interval.

New reduction, implementation and checks: Ali Romman with substantial OpenAI
Codex assistance. Apache-2.0. No independent human or proof-kernel review is claimed.
