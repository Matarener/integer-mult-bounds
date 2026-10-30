# Choose among complete invoices across the exponent range

Use this tool to compare up to eight complete candidates with the same declared
contract. It certifies where a candidate minimizes paid cost minus target credit.
It can keep several candidates when their best regions differ.

```sh
python3 -B scripts/compare_invoice_candidates.py \
  --candidate baseline BASE.json --candidate A A.json --candidate B B.json \
  --max-nodes 255 --max-depth 24 > regions.json
```

The differences from the first invoice must use powers of one integer base b.
Shared noncommensurate terms cancel first. The [existing polynomial reduction](power-polynomial-comparison.md)
gives relative costs `P_i(x)` with `x=b^t`. Thus the open domain `1<x<b` is exactly
`0<t<1`. Reported rational boundaries are x values, not t values; the corresponding
exponent is `log_b(x)`. No rounded logarithm is used to certify a boundary.

Each `certified` cell is an open interval. Its `uniform_minimizers` are minimum
throughout that interval. A nonidentical candidate can also tie at isolated
points. The comparison records count those extra equalities; they do not locate
them. At every reported rational boundary, the tool computes the full set of
minimizers exactly. The endpoints 1 and b are marked outside the open domain.

For costs `0`, `4*x-5`, and `7-4*x`, the first nonzero candidate wins below 5/4,
the zero candidate wins between 5/4 and 7/4, and the last wins above 7/4. At each
transition the two adjacent winners tie. By contrast, `(2*x-3)^2` only touches
zero: the zero candidate stays minimum across the whole domain, with one extra
isolated tie. These are invoice arithmetic examples, not legal source operations.

## Exact cell argument

For each candidate pair, form the difference polynomial and the repeated-GCD
tower from the existing Sturm checker. At each level, use the square-free Sturm
sequence. With zero terms omitted, variation at a simple root is its right-hand
limit. Therefore `V(left)-V(right)` counts roots in `(left,right]`; subtract a
right-endpoint root to get the open interval count.

The alternating sum of the tower counts is the number of odd-multiplicity roots.
If this count is zero, a nonzero polynomial has one sign away from its even roots.
An exact nonzero rational sample determines that sign. A degree-d polynomial
cannot vanish at all d+1 distinct trial points. A candidate wins throughout a
cell only when every difference against it is identically zero or has zero odd
roots and a positive sample. Distinct root counts retain possible tangencies.

When no candidate wins throughout a cell, the tool bisects it. It returns all
leaf cells with no gaps. A node or depth limit leaves an explicit `unresolved`
cell. Its sample winner is not a certified winner on that cell. For `x^2-2`, a
finite dyadic cover retains a transition box around `sqrt(2)`; it never presents
a sampled decimal root as exact.

Limits: 2..8 candidates, 1..4095 allocated nodes, depth 0..40, and the existing
invoice limits. Degree is at most 29. The default is 255 nodes and depth 24.
All exact input hashes and relative polynomial coefficients are recorded.
Invalid or unsupported inputs exit 2 with no partial report.

## Open next questions

Supply complete candidate bills with source bindings, including all fees and
target debits. Resolve a transition box further if the target exponent lies in
it. Locate isolated ties if their exact positions matter. Noncommensurate
differences need another method. None of these comparisons proves circuit
legality, target independence, compiler admission, or a new κ.

Credits: classical Sturm theory, the common-base checker from PR5746, the signed
invoice tools, and retained predecessors. Prepared for Ali Romman with OpenAI
Codex assistance. Apache-2.0.
