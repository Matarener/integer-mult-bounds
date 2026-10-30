# Count every finite-field connector chart repair rank

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with finite corroboration. For fixed maps
B0,B1:V -> F_q^n, this package gives the complete histogram of
rank(B1-R B0) over R in GL_n(F_q). It depends only on the two ranks a,b,
their row-space intersection dimension c, n and q. A Gaussian-binomial
containment count followed by triangular inversion gives every coefficient.
[PROOF.md](PROOF.md) proves the formula over every finite field.

If s=min(a,b), u=max(a,b), and
J_q(d,k)=product_(i=0..k-1)(q^d-q^i), the exact fraction of charts attaining
the minimum rank u-c is

```text
q^(c(u-c)) J_q(u-c,s-c) / J_q(n,s).
```

The minimum rank is the cited result of ywz65's
[PR #2680](https://github.com/CrocSwap/integer-mult-bounds/pull/2680).
The new contribution counts the entire distribution and the density of its
minimizers. No predecessor executable or certificate is imported or replayed.

For q=2,n=3,a=b=2,c=1, the 168 charts have repair-rank histogram
`(0,8,96,64)` at ranks zero through three. Thus exactly 1/21 attain rank one.
With c=2 instead, the histogram is `(4,60,104,0)`. This distinguishes chart
multiplicity from the minimum-rank value and from distinct residual maps.

## Evidence and reproduction

The verifier computes the counting formula using integer arithmetic and
compares it with direct matrix subtraction, multiplication and elimination.
Its complete finite domains are:

- 110 canonical parameter cases over F2,F3,F4,F5, with every codomain
  dimension through three for F2 and through two for the other fields.
  Every feasible a,b,c occurs, and every invertible chart is enumerated.
  These cases make 15,090 individual chart comparisons.
- All 4,096 pairs of binary two-by-three maps and all 6,561 pairs of ternary
  two-by-two maps. The combined 10,657 arbitrary pairs make 339,504 chart
  comparisons. The formula must give every histogram entry, rather than
  only its first nonzero entry. These domains include some canonical cases.
- Six invalid-parameter controls and four mathematical controls cover
  omitted inversion, omitted chart multiplicity, F4 arithmetic and the
  exact minimum-density fixture. F4 is F2[t]/(t^2+t+1), not Z/4.

From the repository root, using CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/connector-chart-rank-distribution/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/connector-chart-rank-distribution/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connector-chart-rank-distribution
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connector-chart-rank-distribution --check-source-history
```

The direct marker is `PASS_CONNECTOR_CHART_RANK_DISTRIBUTION`.
Registered commands have separate 120-second limits. Another CPython 3.12
path can replace the local path. Both modes use explicit exceptions, and
both are read-only. Each stdout receipt binds all six package files with
SHA256. No receipt is handwritten or stored in the package. Provenance
pins authenticate historical source bytes, not predecessor mathematics.

## Scope and code constraints

The universal claim is the written counting proof. Finite execution
corroborates its declared domains; independent human and formal proof-kernel
review are unclaimed. The computational formula accepts prime powers
2<=q<=256 and 0<=n<=12. The written theorem has no such upper bounds.

The chart distribution is over the full general linear group. A restricted
native alphabet, chart synthesis cost, scalar work, physical producer,
restoration, storage, precision and a complete supplier invoice are outside
scope. These costs remain unknown. No particular selected caller is claimed
to need this statistic, and no downstream construction campaign follows.
No new kappa, selected-frontier change or complete multiplication theorem
is claimed. Selected scientific cold replay, Lean and Docker were not run.

All functions are below 60 physical lines, use direct calls and have no
recursion, generated code or external processes. Formula loops have at most
13 iterations per dimension. Field-order validation tries at most 255
divisors and eight divisions per selected divisor. Oracle matrices have at
most six rows/columns, enumerate at most 625 candidate charts at a time,
and retain at most 81 maps in the arbitrary-pair scan. The largest pair
scan has 6,561 iterations, each with at most 48 charts. Invalid field orders,
rank parameters and dimension overflow raise explicit errors. Warnings are
errors in both registered commands. No external static analyzer is required
or claimed.

Power of Ten rule 3 deviation: CPython and its standard library allocate
integers, tuples and elimination rows dynamically. The enforced formula
capacity and fixed oracle domains above bound live memory. Each comparison
releases its temporary matrices; only bounded collections and counters
persist. Both modes exercise the finite scans and capacity rejection. A
fixed-allocation port would be needed before native or long-lived use.

## Open next questions

1. For a named physical caller with a legal restricted chart alphabet, how
   much of this minimum-rank density survives? Begin by specifying that
   alphabet and its complete chart, injection and restoration prices. The
   unrestricted distribution is a reference count, not a physical tariff.
2. Can one sample a minimum-rank chart uniformly without enumerating GL_n?
   The injective-lift proof suggests a constructive sampler. An exact
   uniformity proof and the actual caller's selection cost are still needed.
   This package does not reserve or implement that extension.

## Credit and assignment

Credit ywz65 #2680 for the paid residual-rank interface and minimum theorem,
woklerx for the equal-kernel dirty-chart contract, and Ross Richardson #943
for the dirty-query and complete-call context. Gaussian coefficients,
subspace-intersection counting and triangular inversion are classical.
This is a new application and formula in that interface, with no claim of
literature-wide priority. All predecessor files and credit lines are unchanged.

The `connector-alphabet-change` card is explicitly changed to an algebraic
side result about chart multiplicity. It adds neither a connector operation
nor a favorable completed budget. The user's original-work restriction
supersedes the card's predecessor-replay example. Current selected-binding
orientation passed; it is metadata evidence only. Live claims, open PRs,
merged-PR searches and main README searches were used for overlap. The
cached helper covered 416 open PRs and 5,307 Discussion records, but sparse
local coverage omitted 7,622 notes. Targeted searches of all main READMEs
supplemented that cache; unpublished work and arbitrary diffs remain outside
coverage. Lack of a matching record does not establish novelty.
