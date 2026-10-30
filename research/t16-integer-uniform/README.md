# Uniform sharp pooled T16 integer packing

For every real `0 <= a <= 1/7`, put `p=1-a`. In the fixed selected-T16
pooled integer pattern model, the exact minimum idle cost is

`2431 + 17^p + 4887*48^p`.

This answers [PR3352](https://github.com/CrocSwap/integer-mult-bounds/pull/3352)'s
second open question by extending its certified interval
`0.00167689 <= a <= 0.00167690`. The optimizer and integer witness are unchanged.
The new result is a continuum proof, not another numerical root calculation.
No physical owner map, new supplier, improved kappa or selected-frontier change
is claimed. The earlier necessary packing cap is unchanged.

The same 37-state potential fails at `a=3/20`: its edge from residue 3 to 6,
pattern 36 in the declared enumeration, has slack
`37*(2*5^(17/20)-8^(17/20)-2) < -11/250`.
This rejects an extension of this fixed potential. It does **not** prove that
the integer optimizer changes there, nor that `1/7` is a sharp endpoint.

## Model, exact sources and attainment

Capacities `(8,16,32,48)` have bin counts `(10752,7168,7168,7168)`.
Whole helper widths `(4,5,7,8,9)` have occurrence counts
`(8064,4608,4320,17568,34560)`. Each bin receives an integer multiset of
helpers of total width at most its capacity; its residual is the unused width.
Pattern multiplicities are nonnegative integers satisfying all nine inventory
equations. Timing, owner identity, offsets and family compatibility are relaxed.
Split helpers and overlapping reservations change this contract.

The verifier recounts the source inventories from the literal PLAN/SPEC, checks
their hashes against selected PR1094's source manifest, and enumerates all
1,163 patterns. Base `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
The selected pointer and original task card are pinned historical provenance.
SOURCES.json records exact Git blobs and SHA256 hashes.

CERTIFICATE.json is retained byte-for-byte from PR3352 commit
`ff0531431ff54eb75919a1529134b5834069a69e`, with its source blob and byte hash.
It contains the dual, 37 potential paths and ten attaining integer patterns.
Those bytes are committed here so cold replay does not require an unmerged
Git object or an extra fetch. No predecessor code is imported. All nine
integer equations are rechecked; the witness idle histogram is exactly
`{1:2431,17:1,48:4887}`, of total rank mass 237,024.

## Residue reduction

Use the predecessor numerator vectors, capacity rows followed by helper rows:

```text
A = (8,16,32,0, -4,-41,-19,-8,3)
B = (6,12,24,37, -3,-3,-5,-6,-7)
```

For a pattern of residual r, summing its capacity and helper coefficients gives
`A_j+48*B_j=37*r`. Its reduced cost is
`g_j=37*r^p-A_j-B_j*48^p`. Integer inventories force total dual coefficients
`89952,180832`, and `180832 mod 37 = 13`.

The stored paths give potentials `P_s` on residues modulo 37. Every pattern
gives an edge `s -> s+B_j`. There are 43,031 edge slacks
`P_s+g_j-P_(s+B_j)`, which reduce to 5,304 distinct integer spectra
`F(a)=sum c_r*r^(1-a)`. Each satisfies `sum c_r*r=0` exactly.

The proof below certifies every edge uniformly. Summing along any integer
packing telescopes to `sum g_j >= P_13`, and the certificate checks
`P_13=37*17^p-5-13*48^p`. Thus

```text
37*idle - 89952 - 180832*48^p >= 37*17^p - 5 - 13*48^p
idle >= 2431 + 17^p + 4887*48^p.
```

The checked integer witness attains this. At `a=0`, all feasible packings have
the same idle rank mass, which also proves that endpoint directly.

## Uniform sign proof

There is one symbolic zero spectrum, used by 829 edges. The remaining 42,202
edges have strictly positive slack for `0<a<=1/7`.

For 5,228 distinct spectra, the verifier checks the integer hinge sums
`H(t)=sum c_r*min(r,t)` at every integer `1<=t<=48`. All are nonnegative and
at least one is positive. For any function f on these integer ranks with
`f(0)=0`, direct telescoping gives

```text
f(r) = r*(f(48)-f(47))
       + sum_(t=1)^47 min(r,t)*(2*f(t)-f(t-1)-f(t+1)).
```

Multiply by `c_r` and sum. The linear term vanishes. For `f(r)=r^p`,
`0<p<1`, every discrete curvature is strictly positive. Since `H(48)=0`,
the positive hinge occurs before 48, proving strict positivity. This part
actually works for every `0<a<1`.

The remaining 75 spectra have a negative hinge, so that sufficient condition
does not apply. Set `L_r=log(48/r)`, with `0<=L_r<4`, and define

```text
G(a) = sum c_r*r*(exp(a*L_r)-1)/a
F(a) = a*48^(-a)*G(a).
```

The formula for G has its continuous value at zero. Expand through exponential
degree 20. The resulting polynomial in a has degree 19 and coefficient
`sum c_r*r*L_r^(k+1)/(k+1)!` at degree k. Every coefficient has a rational
lower bound using certified logarithm intervals.

For `0<=a<=A=1/7`, the absolute omitted tail after division by a is at most

`T = sum |c_r*r| * 3*A^20*4^21/21!`.

Indeed the Lagrange remainder is bounded by `exp(a*L_r)*(a*L_r)^21/21!`.
Here `exp(a*L_r) <= 1/(1-4/7) < 3`. This also handles the continuous endpoint.

Write the lower polynomial on `[0,A]` in the degree-19 Bernstein basis.
Its coefficient j is exactly
`sum_(k<=j) lower_k*A^k*binom(j,k)/binom(19,k)`.
The verifier subtracts T from every Bernstein coefficient and checks all
1,500 resulting rationals are positive. Their common lower bound exceeds
`224787/250000`. Bernstein basis functions are nonnegative and sum to one,
so `G(a)>0` throughout the interval. This proves the 75 remaining spectra.

Logarithms use the positive atanh series. For `1<=q<=2`, set
`z=(q-1)/(q+1)` and sum `2*z^(2k+1)/(2k+1)` for `0<=k<64`.
The omitted tail is at most `2*z^129/(129*(1-z^2))`. Reduce general q by
at most five powers of two, then round the rational endpoints outward to
160 fractional bits. No floating point, grid sampling, optimizer or external
mathematical library enters acceptance.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/t16-integer-uniform
python3.12 -I -O -Werror -B research/t16-integer-uniform/verify.py
python3.12 -I -O -Werror -B research/t16-integer-uniform/test_verify.py
```

`verify.py --write` regenerates only this package's RESULT.json. Ordinary replay
compares the whole fresh receipt. Seven control groups check a separate
width-frontier enumeration, inventory violations, forged paths/duals, the
discrete identity, logarithm domains, analytic rejection and 192 rational-power
brackets by direct integer-power comparisons. A larger-domain failure is
enclosed by exact 20th-root integer arithmetic. All guards survive `-O`.

## Limits

This is a theorem about a finite aggregate integer relaxation. The physical
selected word, owner-map admission, paid local profile, numerical moment root,
bit supplier, full native invoice, outer inequalities, all-size/compiler,
precision, stock/tape/recovery and analytic premises are not newly replayed.
No proof-assistant or independent human review is claimed.

## Open next questions

- What is the actual maximal optimality interval of this integer profile?
  At `a=3/20`, try another residue potential or find a better feasible integer
  inventory. Failure of the present potential is the blocker, not a proved
  change in the optimal packing.
- Can an actual chronological T16 owner map attain the pooled profile?
  Start by assigning the ten patterns to literal bins and checking every
  helper-family/window conflict. The omitted physical compatibility is the
  blocker. This question is separate from current helper-cycle searches.

## Credit and engineering scope

PR3352 supplies the retained residue certificate and integer witness. Ali
Romman's PR1129 supplies the fractional optimum and dual, following Chafik
Boukhalfa's signed prices. Hanson Sun's PR1914 independently binds that model
to selected T16 inputs and asks about the integer gap. Credit Rohan Arun/PR1094,
Jeremy Kothe, Hao Yan/PR858 and the retained selected-source lineage. New
material is Apache-2.0. Development used substantial automated assistance in
derivation, implementation and checking. No tool is assigned authorship.

Build the Lever led to the standalone exact proof checker. Prove It Works led
to whole-receipt comparison, semantic controls and a cold source export.
Separate Before Serializing Shared State led to an isolated branch and
process-held advisory locks for shared Git and task reservations.

Power of Ten applies to this verifier and its tests. Functions are below 60
physical lines; explicit bounds cover patterns, 37 states, 49 ranks, 64 log
terms, 20 Taylor coefficients and 135 root bisections. Input guards use
exceptions, and exact endpoint/inventory invariants are checked during replay.
Rule 3 has a managed-runtime deviation for Python integer/Fraction allocation.
Live data is bounded by 1,163 patterns, 5,304 spectra with at most 49 ranks,
48 logarithms and 20 Bernstein coefficients per current spectrum. Python's
internal allocation is not inspected. Tests cover domain exhaustion and bad
inputs; a native rewrite would be reconsidered only for a long-lived service.
Rules 8/9 have a test-only deviation for runpy, restricted to this sibling
verifier with no plugin targets. Static diagnostics and optimized controls
cover those paths. No selected or predecessor code is changed.
