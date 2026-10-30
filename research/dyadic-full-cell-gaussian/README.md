# A certified dyadic full-cell Gaussian reference and inverse

The exact broad Gaussian cell now has an explicit inverse guard from p=16
and a complete numerical preparation algorithm. It constructs one banded
dyadic reference A and a dyadic inverse R with certified error at most
2^(-t), for every requested t>=0. Both the maximum absolute row sum and
column sum are controlled. No new kappa is claimed.

The uniform guard is `5p^6`. A finite q-product enclosure gives a much tighter
guard for actual preparation, with its infinite tail charged. The algorithm
checks every retained Gaussian coefficient by rational intervals and every
inverse residual entry by integer arithmetic. A Decimal proposal is accepted
only after these exact checks. Exact rational elimination completes the
algorithm if that proposal fails.

[PROOF.md](PROOF.md) gives the full quantifiers, finite constants, error ledger
and preparation costs. [prepare.py](prepare.py) implements the construction.
[RESULT.json](RESULT.json) records complete 256- and 299-column cell checks.
[SOURCES.json](SOURCES.json) retains the exact analytic sources.

## Scope and connection to the source

The source is the full cell `N=floor(1/theta)`, with
`alpha=ceil(sqrt((4/pi)log(16p)))` and
`1/(4p^2)<=theta<=1/p^2`. Its half-grid phase and dilation are unchanged.
The algorithm receives the source alpha and rational theta; source-prime
selection and parameter setup remain upstream work. It checks sufficient
conditioning guards and does not silently alter those parameters.

JoyboyBrian's PR5479 proves sharper eventual conditioning but leaves a
rounded reference and its preparation open. This package closes that
numerical implication with finite constants. It does not install the table
in a native supplier, admit a capped RawGaussian API, or price a physical
caller. Coefficient storage, exact elimination, and numerical proposal work
are explicit costs. Page delivery, tape movement, stock reuse, preparation
amortization, online reversible execution and outer recovery remain open.
The main transform still limits the selected conditional kappa 0.00310045.

## Verification

Python 3.12 and the standard library suffice.

```
python3.12 -B scripts/research_package.py --package research/dyadic-full-cell-gaussian
python3.12 -B scripts/check_research_commit.py --package research/dyadic-full-cell-gaussian
```

Expected: `PASS_DYADIC_FULL_CELL_GAUSSIAN`,
`PASS_REGISTERED_RESEARCH_PACKAGE`, and `PASS_RESEARCH_COMMIT_BYTES`.
Both normal and optimized modes rebuild the complete cells. The 299-column
case uses the primes p=17, s=599 and t=601, with theta=t/s-1; this t is the
source-prime name, not the requested accuracy. Its floor remains 299.
Requested accuracy bits are 4 on the 256-column case and 12 and 40 on the
299-column case. The literal source ceiling is checked separately.

The checks include independent rational exponential enclosures, exact
integer residuals, all input columns, three small exact inverse cases with
row pivoting, and mutants for wrong coefficients, inverse entries, cell
size, domain and conditioning. Retained sources are authenticated first.
The fixed result is mandatory and never rewritten by verification.

The large cells use certified Decimal proposals. A large exact rational
completion run is not claimed. The universal theorem is the written proof,
not an inference from these cells. The same assistant wrote the proof and
checker; there is no independent human or formal proof-kernel review.
No native or selected cold replay, whole outer admission, full historical
suite, Lean or Docker run was used. Full-history preflight is unavailable
in this shallow checkout.

## Open next questions

1. Which actual full-cell consumer can use this exact common reference
   while paying its complete page, route, precision, stock and outer bill?
   A numerical inverse table does not provide that physical implementation.
2. Can a structured inverse application reduce the dense table and exact
   completion costs without weakening the same residual certificate?
   The current implementation stores dense arrays and prices them as such.

## Credit

JoyboyBrian's [PR5479](https://github.com/CrocSwap/integer-mult-bounds/pull/5479)
supplies the production full-cell source and uniform q-product estimates.
The retained half-line and Gaussian source notes preserve Jose Manuel,
Vlado Vojdanovski, Cinna Davis, Ryanson Jonathan, Nick Petalas and the
classical q-LDU/product lineage. The earlier eventual bound is not new here.
New effective guard, certified dyadic preparation, exact residual check,
proof and implementation: Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0.

Base: canonical main `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority 7.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19188471).
No selected-frontier file is changed.
