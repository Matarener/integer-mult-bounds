# The first phase transition of pooled T16 integer packing

For every real `0 <= a <= 1/2`, put `p=1-a`. The exact minimum idle cost in
the fixed selected-T16 pooled integer pattern model is

```text
min(2431 + 17^p, 2429 + 5^p + 14^p) + 4887*48^p.
```

The predecessor profile is optimal exactly on the initial interval
`0 <= a <= a*`, where `a*` is the unique root in `(2/5,5/12)` of

```text
5^(1-a) + 14^(1-a) - 17^(1-a) - 2 = 0.
```

This answers [PR3364](https://github.com/CrocSwap/integer-mult-bounds/pull/3364)'s
first open question. Its failure at `a=3/20` was a failure of one fixed
potential: the old profile is still optimal there. At `a=1/2`, the new profile
is better by more than `7/50` units of idle cost. The exact optimum is
`2429 + sqrt(5) + sqrt(14) + 4887*sqrt(48)` at that endpoint.

This is a continuum theorem about an aggregate integer relaxation. The
numerical moment root and packing cap near the selected exponent do not
change. No physical owner map, supplier, improved kappa or selected-frontier
update is claimed.

## Model and sources

Whole helper widths `(4,5,7,8,9)` have counts
`(8064,4608,4320,17568,34560)`. Bin capacities `(8,16,32,48)` have counts
`(10752,7168,7168,7168)`. A bin receives a nonnegative integer multiset of
helpers whose total width does not exceed its capacity. A pattern's residual
`r` is its unused width and has cost `r^p`, with zero cost at `r=0`.
All nine inventory equations hold exactly. Timing, owner identity, offsets,
frame compatibility and family/window eligibility are relaxed.

The verifier recounts the inventories from selected PR1094's literal PLAN
and SPEC. It binds both to SELECTED-SOURCE.json and checks their exact hashes.
The base is canonical main `6f100d4bb5083f8c35d96fd95a539811c62f245c`,
priority revision 6. SOURCES.json records source hashes and Git blobs.
The selected review is `docs/research/community-batch1099-review.md`; its full
replay is `make frontier1094-verify`. Neither that complete replay nor a new
native supplier admission is part of this package.

PREDECESSOR.json is the exact PR3352 certificate, also retained by PR3364,
from commit `ff0531431ff54eb75919a1529134b5834069a69e`. Its original source blob,
hash, public URL and credit are recorded. No pending Git object is needed for
replay. CERTIFICATE.json contains the two attaining inventories and the new
49 path candidates. No predecessor checker is imported.

## Two integer upper bounds

Each table entry is the multiplicity of its pattern. The columns labeled old
and new satisfy every capacity and helper count independently.

| Capacity | Helpers | Residual | Old | New |
| ---: | --- | ---: | ---: | ---: |
| 8 | 8 | 0 | 10752 | 10752 |
| 16 | 8+8 | 0 | 1301 | 1300 |
| 16 | 7+9 | 0 | 4191 | 4191 |
| 16 | 4+4+8 | 0 | 1676 | 1677 |
| 32 | 7+8+8+9 | 0 | 128 | 129 |
| 32 | 5+9+9+9 | 0 | 4608 | 4608 |
| 32 | 4+9+9+9 | 1 | 2431 | 2429 |
| 48 | empty | 48 | 4887 | 4887 |
| 48 | 4+8+9+9+9+9 | 0 | 2281 | 2281 |
| 32 | 7+8 | 17 | 1 | 0 |
| 32 | 9+9+9 | 5 | 0 | 1 |
| 32 | 9+9 | 14 | 0 | 1 |

Both have idle rank mass 237,024. Taking the cheaper inventory proves the
upper bound for every parameter in the stated interval.

## Lower bound by a minimum of potentials

Enumerate all 1,163 feasible patterns. Use the predecessor integer dual
numerators, capacity rows followed by helper rows:

```text
A = (8,16,32,0, -4,-41,-19,-8,3)
B = (6,12,24,37, -3,-3,-5,-6,-7).
```

For a pattern j, let `A_j,B_j` be the sums of its capacity and helper
coefficients. Direct integer checks give `A_j+48*B_j=37*r_j`.
Set `g_j=37*r_j^p-A_j-B_j*48^p`. For every feasible packing the inventory
sums are `sum A_j=89952`, `sum B_j=180832`, and `180832 mod 37=13`.

A pattern gives an edge `s -> s+B_j mod 37` with weight `g_j`.
For each residue s, the certificate gives one or two paths starting at 0 and
ending at s, each with at most three pattern edges. There are 49 paths in
total. Let `P_s` be the minimum of those path weights. In particular,

```text
P_0 = 0
P_13 = min(37*17^p - 5 - 13*48^p,
           37*(5^p+14^p) - 79 - 13*48^p).
```

The checker proves the following precise quantifiers. For each s, EACH path
candidate L at s, and EACH pattern j, there EXISTS a candidate R at the
destination such that `weight(L)+g_j-weight(R)>=0` throughout `0<=a<=1/2`.
There are 56,987 such obligations, not merely 37 potential values sampled at
one exponent. The chosen R may depend on L and j, but its inequality holds
on the whole interval. Hence `P_s+g_j>=P_(s+B_j)` on that whole interval:
choose an L attaining `P_s` and use `P_(s+B_j)<=weight(R)`.

Now order the finitely many patterns of any feasible packing and accumulate
their residues from 0. These edge inequalities telescope to
`sum g_j>=P_13`. Therefore

```text
37*idle >= 89952 + 180832*48^p + P_13
idle >= min(2431+17^p, 2429+5^p+14^p) + 4887*48^p.
```

Together with the two integer inventories, this proves equality. At `a=0`
the linear rank identity also gives the common cost directly.

## Uniform comparison certificates

Every comparison is a spectrum `F(a)=sum c_r*r^(1-a)`, with integer
coefficients, `1<=r<=48` and `sum c_r*r=0`. There are 7,181 distinct
successful comparisons. One is identically zero. The remaining 7,180 are
strictly positive for `0<a<=1/2`.

For 6,850 spectra the integer hinges `H(t)=sum c_r*min(r,t)` are nonnegative
at all integer `1<=t<=48`, and at least one is positive. The exact identity

```text
f(r) = r*(f(48)-f(47))
       + sum_(t=1)^47 min(r,t)*(2*f(t)-f(t-1)-f(t+1))
```

holds for any integer-rank function with `f(0)=0`. For `f(r)=r^p` and
`0<p<1`, each discrete curvature is strictly positive. The linear part
vanishes in the spectrum, and `H(48)=0`, so these spectra are positive.

The remaining 330 spectra use rational Taylor/Bernstein certificates.
Write `L_r=log(48/r)`, so `0<=L_r<4`, and

```text
F(a) = a*48^(-a)*G(a)
G(a) = sum c_r*r*(exp(a*L_r)-1)/a.
```

Use the continuous value of G at zero. Expand the exponential through degree
32. G's polynomial has degree 31, with coefficient
`sum c_r*r*L_r^(k+1)/(k+1)!` at degree k. Directed logarithm intervals give
rational lower coefficients. With `A=1/2`, the absolute omitted tail is at most

```text
T = sum |c_r*r| * 9*A^32*4^33/33!.
```

Indeed `exp(a*L_r)<exp(2)<9`. The elementary series estimate
`exp(1)=sum 1/n!<3` proves the last bound, using `n!>=2^(n-1)` for `n>=2`.
The Lagrange remainder divided by a gives T, including the continuous endpoint.

In the degree-31 Bernstein basis on `[0,A]`, coefficient j of the lower
polynomial is exactly
`sum_(k<=j) lower_k*A^k*binom(j,k)/binom(31,k)`.
After subtracting T, all 10,560 rational coefficients are positive. Their
common lower bound exceeds `2320089/500000`. Nonnegative Bernstein basis
functions sum to one, so each G is positive on the whole interval.

Logarithms use the positive atanh series after at most five powers-of-two
reductions. For `1<=q<=2`, set `z=(q-1)/(q+1)` and sum
`2*z^(2k+1)/(2k+1)` for `0<=k<64`. The omitted positive tail is at most
`2*z^129/(129*(1-z*z))`. Endpoints are rounded outward to 160 fractional bits.
No floating point, sampled grid, optimizer or external math library enters
acceptance. Failed sufficient certificates are skipped only when another
candidate supplies a successful whole-interval proof of the same obligation.

## The unique first transition

Let `h(p)=5^p+14^p-17^p-2`, the new cost minus the old cost. Exact integer-power
enclosures prove `h(7/12)<0`, `h(3/5)>0` and `h(1)=0`. Moreover

```text
h'(p)/17^p = log(5)*(5/17)^p + log(14)*(14/17)^p - log(17)
```

is strictly decreasing for every real p. It has at most one zero, so h has
at most two distinct zeros by Rolle's theorem. There is one between `7/12`
and `3/5`, and another at 1, so these are the only zeros. Continuity fixes the
sign on both sides of the interior root in `[1/2,1]`. This proves the exact
initial optimality interval stated above, with a tie only at the transition
and at `a=0`. It does not classify every attaining pattern multiset.

The same exact arithmetic accepts the old profile at `a=3/20`, while
rejecting PR3364's fixed potential there with slack below `-11/250`.
At `a=1/2` it proves `h(1/2)<-7/50`. A separate rational square-root control
checks that strict win without the general power routine.

## Reproduce and coverage

Standard-library Python 3.12, from the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/t16-integer-phase
python3.12 -I -O -Werror -B research/t16-integer-phase/verify.py
python3.12 -I -O -Werror -B research/t16-integer-phase/test_verify.py
```

Expected verifier marker is `PASS_T16_INTEGER_PHASE 56987` with the proof
census in RESULT.json. Ordinary replay is read-only and compares the whole
fresh receipt. `verify.py --write` regenerates only this package's RESULT.json.
Seven test groups include a separately implemented pattern frontier, both
integer witnesses, inventory/path/dual failures, a separate discrete-identity
oracle, direct integer-power comparisons, analytic rejection and an actual
optimized CLI run with corrupted source bytes.

Point probes and the preliminary analytic probe were discovery evidence.
The production checker independently reconstructs every edge comparison,
checks the whole continuum and both inventories, and produces RESULT.json.
Computational checks corroborate the written theorem. No proof-kernel or
independent human review is claimed.

Chronology, physical owner/frame admission, the paid local word, full native
invoice, the bit supplier, outer inequalities, all-size/compiler, precision,
stock/tape/recovery and analytic-transfer premises are not newly replayed.
These pooled upper bounds cannot be substituted for a physical supplier bill.

## Open next questions

- What is the sharp pooled profile for `1/2<a<1`? First derive a supporting
  fractional dual on that domain, then require integer attainment and a
  whole-interval certificate. The present supporting prices eventually fail.
- Can physical chronology attain either pooled profile? Assign its patterns
  to literal windows and enforce owner, family and frame compatibility.
  Aggregate integer feasibility supplies none of those conditions.

## Credit and engineering decisions

PR3352 supplies the original integer witness and residue method. PR3364
supplies the earlier continuum certificate and the explicit maximal-interval
question. Ali Romman/PR1129 supplies the fractional dual and optimum,
following Chafik Boukhalfa's signed prices. Hanson Sun/PR1914 supplies the
independent selected-source inventory binding and integer-gap question.
Credit Rohan Arun/PR1094, Jeremy Kothe, Hao Yan/PR858 and the retained source
lineage. The logarithm/concavity code is adapted from PR3364 with that credit.
New material is Apache-2.0. Development used substantial automated assistance
in derivation, implementation, checking and prose. No tool is assigned authorship.

Build the Lever led to the exact proof checker. Prove It Works required the
complete fresh receipt, semantic failures and replay from committed bytes.
Separate Before Serializing Shared State kept new artifacts in one package
and serialized only shared Git and reservation mutations.

Power of Ten bounds the production computation by 1,163 patterns, 37 residues,
49 candidate paths of length at most three, at most two destination choices,
48 ranks, 64 log terms and 32 Bernstein coefficients. Functions stay below
60 physical lines. Contracts use explicit exceptions and survive `-O`.
The cache holds at most `2*49*1163` comparison spectra, each with at most 48
ranks, and one current polynomial. JSON inputs are bounded or exact-source-bound.

Rule 3 has a managed-runtime deviation for Python integer/Fraction allocation.
Python's allocator is not inspected. Finite collection, integer-root and
polynomial bounds limit the live mathematical state; scoped temporary
directories close on failures. Capacity/domain failures and optimized controls
are tested. Reconsider a fixed-capacity native implementation before reuse in
a long-lived service. Rules 8/9 have a test-only deviation for runpy and
unittest dispatch, restricted to the sibling verifier and seven named tests.
No plugin loading or dynamic target selection is introduced. Diagnostics,
normal/optimized controls and a Git-free replay cover that scope.
