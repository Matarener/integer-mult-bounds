# Sharp codimension guarantee for partial query acquisition

Scoped proof, with exact finite corroboration, produced by Nick Petalas.
Apache-2.0. No new kappa or complete multiplication theorem is claimed.

A cheapest basis of an entire query span can be wasteful for a proper target
subspace. Pruning that basis has a sharp approximation factor determined by
**target codimension plus one**, rather than by the number of target vectors.
This quantifies the partial-target boundary left open in
[Ali Romman's PR #5791](https://github.com/CrocSwap/integer-mult-bounds/pull/5791).
The result does not audit that PR or run its producer/checker.

## Contract and theorem

Let E be a finite indexed query pool over any field, of span V and rank r.
Each query e has a finite nonnegative acquisition cost c(e). Duplicate and
zero queries are allowed. Pay each acquired query once, and grant all linear
reconstruction for free. Let T be a target subspace of V, of dimension
1 <= d <= r. Define

```
OPT(T) = min { sum(c(e) for e in S) : S subset E, T subset span(S) }.
```

Choose **any** minimum-cost basis B of V from E. Let C be the union of the
supports, in B coordinates, of the vectors of T. Equivalently, C is the unique
smallest subset of B whose span contains T. It can be found from any basis of
T; redundant target generators do not change it.

**Theorem.** The pruned cost satisfies

```
c(C) <= (r-d+1) OPT(T).                                      (1)
```

This holds for every tied minimum basis B, including zero-cost queries.
If T is zero, C is empty and its acquisition cost is exactly zero.
For T=V, (1) is equality with the full-span optimum.
The factor r-d+1 cannot be reduced, even over F2 with positive integer costs
and a unique minimum-cost full-span basis. In that stricter class it is a
sharp supremum. Thus exact full-span optimization gives no constant-factor
partial-target guarantee independent of the target codimension.

## Proof by price thresholds

The only predecessor ingredient is the classical minimum-basis cheap-prefix
property, also explained by Ali Romman in
[the pinned #5791 guide](https://github.com/aliromman/integer-mult-bounds/blob/cd314cb7f14511196060fc3c6261e2bf5fb80de4/docs/research/binary-query-basis.md).
For completeness, it follows directly from a one-element basis exchange.
Fix a real threshold tau >= 0 and put

```
E_low = {e in E : c(e) <= tau},  L=span(E_low),  l=dim L,
B_low = {b in B : c(b) <= tau}.
```

Every e in E_low is in span(B_low). Otherwise its B-expression contains some
b of cost greater than tau; replacing that b by e gives a cheaper full-span
basis, a contradiction. Hence L=span(B_low), and exactly r-l basis entries
are expensive at this threshold. This holds for any minimum basis, without a
specified tie rule.

Fix an optimal partial acquisition S. Let k be the number of entries of S
with cost greater than tau, and let a=dim(T intersect L). Projection to V/L
annihilates the cheap entries of S, so

```
d-a = dim(image of T in V/L) <= k.                            (2)
```

Write m for the number of expensive entries of C. If k=0, (2) gives T subset L.
Since L=span(B_low), uniqueness of B coordinates forces m=0. If k>=1, then

```
m <= r-l <= r-a <= r-d+k <= (r-d+1)k.                        (3)
```

The last inequality is equivalent to (r-d)(k-1)>=0.
This bounds the expensive support count at **each** threshold, before summing
costs. For any finite set A with nonnegative costs,

```
c(A) = integral from 0 to infinity of |{e in A : c(e)>tau}| d tau.
```

Integrating (3), together with the k=0 case, proves (1). All sets are finite,
so this is simply a finite sum over price intervals; no limiting interchange
or positive-cost assumption is needed. The proof is independent of the field.

## Sharp family with a unique cheapest basis

Fix 1<=d<r and write s=r-d+1>=2. In any field take the r+1 queries

```
e_1,...,e_r, z=e_d+...+e_r,
T=span(e_1,...,e_(d-1),z),
c(e_i)=1 for i<d,
c(e_i)=M-1 for i>=d,
c(z)=M, where M is any integer >=3.
```

The target dimension is d. The only dependence is
z-e_d-...-e_r=0. Every full-span basis contains the first d-1 entries and
omits exactly one entry of this dependence. Since z is strictly its most
expensive entry, B={e_1,...,e_r} is the unique cheapest full-span basis.
The target supports use every entry of B. Therefore

```
c(C) = (d-1)+s(M-1).
```

Any acquisition spanning T must buy e_1,...,e_(d-1). It must also either buy
z, or buy all s remaining coordinate queries. The latter cost is s(M-1)>M
for s>=2 and M>=3. Thus

```
OPT(T) = (d-1)+M,
c(C)/OPT(T) = ((d-1)+s(M-1))/((d-1)+M) -> s as M -> infinity.
```

This proves sharpness under positive integer costs and uniqueness, without a
tie-breaking artifact. For r=d the factor one is already exact. No assertion
of literature-wide priority is made for weighted-basis or approximation theory;
the contribution is this scoped sharp guarantee at the repository's
whole-span/partial-target boundary.

## Verification and reproduction

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/partial-query-basis-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/partial-query-basis-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/partial-query-basis-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/partial-query-basis-gap --check-source-history
```

The standalone standard-library verifier enumerates new partial-target cases.
For the eight binary queries (1,2,4,8,3,5,10,15), it covers all 256 assignments
of costs in {0,3}, all 67 target subspaces of F2^4, and every minimum-cost
full-span basis. It computes OPT by enumerating every acquisition subset,
and computes pruned supports separately by unique coordinate expressions.
It checks both (1) and the pointwise threshold inequality. It also enumerates
30 sharp positive-integer fixtures, all 2<=r<=5, 1<=d<r and M in {3,11,101},
checking uniqueness and both closed-form costs against subset optima.

Three controls break the minimum-basis, pruning, and proposed factor r-d
premises. Four malformed-input controls reject negative or Boolean costs,
dependent basis entries, and an out-of-span target. Explicit exceptions keep
these checks enabled under optimized Python. The all-field statement rests on
the written proof; binary finite checks are corroboration.

Optional `--receipt /absolute/path/outside/checkout.json` writes a generated
receipt containing executed counts and SHA256 of all five package files.
Normal replay writes nothing. No hand-written receipt is used. Source metadata
pins only the catalogue and selected orientation record, as provenance.
The pending #5791 guide is an exact-head citation, not a live executable input
or an unpublished-history dependency.

Power-of-ten scope: the verifier uses structured iteration, no recursion,
functions under 60 lines, explicit contract failures and bounded domains.
The exhaustive pool has 256 subsets and targets have at most 16 elements;
sharp fixtures have at most 64 subsets and 32 ambient vectors. Python's
managed allocations are a declared deviation from fixed allocation; collection
sizes are bounded by these finite domains. There is no imported project code,
external runtime input, solver or dynamic code generation. Warning-strict
normal and optimized replays provide the applicable interpreter diagnostics.

## Scope, overlap and credit

The `formal-interface-lemma` card is changed to an algebraic side result about
query acquisition, rather than a selected caller formalization. The card's
first baseline command passed with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.
The five selected framework assumptions remain untouched.

Credit Ali Romman #5791 for posing the partial-target boundary and for the
whole-span acquisition contract. Weighted linear-matroid greedy selection,
the cheap-prefix property and basis exchange are classical. Those ingredients
are cited and used; they are not claimed as new or independently audited here.
The new argument adds target dimension to the price-threshold count and gives
the matching unique-basis family. No predecessor code or numeric receipt is
replayed, and predecessor attribution is unchanged.

Overlap checks consulted live open PRs, this account's recent PRs, handoffs,
active Discussions, local reservations, all-main README text and distinctive
merged-PR searches. The cached scan covered 426 open PRs and 5,333 Discussion
records; its local scan omitted 7,634 sparse HEAD notes. Separate all-main Git
searches address relevant omitted README text. Closed PR bodies, code diffs
and unpublished work remain coverage limits. The advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19214980)
records the scope; no exclusive priority over unknown work is asserted.

## Open next questions

Can a target-aware algorithm improve the r-d+1 factor while keeping a similarly
small certificate? Start with a fixed positive codimension and an explicit
query pool; compare an acquisition subset against a proved lower bound.
The sharp family rules out improving that factor merely by changing the
full-span basis tie rule, since its full-span minimum is unique.

Can one source caller supply actual targets and additive acquisition prices
that satisfy this model? Name that caller and price linear reconstruction,
physical delivery, restoration and owned storage separately. None of these
costs is implicitly zero in a supplier claim. There is no native operator,
physical compiler, rounded execution, Lean proof or supplier admission in
this package, and no selected cold replay is warranted by this side result.
Stop this contribution at the theorem above.
