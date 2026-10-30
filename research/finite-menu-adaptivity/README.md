# Finite-menu adaptivity cannot repair an exact helper endpoint

Scoped mathematical obstruction, with finite exact corroboration. Over an
infinite field, arbitrary data-dependent selection among finitely many fixed
linear helper programs implements an exact arbitrary-input endpoint only if
one fixed program already implements it. Every dirty input and every required
restoration output must be part of the same contract.

For N wrong rational maps on d inputs, the explicit witness constructor finds
one input missed by every map after at most N(d-1)+1 tests of
(1,t,...,t^(d-1)). The polynomial-avoidance bound is already used in Sagar
Thakrar / thakrarsagar's [PR1133](https://github.com/CrocSwap/integer-mult-bounds/pull/1133)
for support descent and is credited here. A four-map example needs all nine tests and
returns (1,8,64). For a Cartesian grid with coordinate sizes s_i, a stronger
rank-sensitive obstruction is

    sum_j 1/W_j < 1,
    W_j = maximum product of s_i over a column basis of A_j-T.

For equal sizes s, this is sum_j s^(-rank(A_j-T)) < 1. Maximum-product bases
use exact greedy independence tests. The grid statement holds over any field;
the whole-space finite-menu statement requires an infinite field.
[PROOF.md](PROOF.md) gives the proofs, cost corollary and sharpness examples.

This supplies a screening rule for a proposed finite-menu escape from a
complex helper or decoder exclusion. It does not establish an exclusion for
any actual P104 menu. A paid-call cap alone need not make the menu finite.
Every fixed word must also be globally legal before the cost corollary applies.
No physical caller, complete supplier, new kappa or selected-frontier change
is claimed. The original construction card has explicitly changed scope.

## Evidence and reproduction

Use CPython 3.12 and its standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/finite-menu-adaptivity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/finite-menu-adaptivity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/finite-menu-adaptivity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/finite-menu-adaptivity --check-source-history
```

Another installed CPython 3.12 may replace that executable. Expected direct
status is `PASS_FINITE_MENU_ADAPTIVITY`. The verifier writes only stdout,
including generated SHA256 bindings to all six package files. No receipt is
handwritten and no predecessor executable or mathematical receipt is consumed.
Catalogue and selected-record pins are historical provenance in SOURCES.json.

The exact checks enumerate all 729 two-by-three matrices with entries in
{-1,0,1}, all 2,187 declared weighted grids and their 11,139 output fibers.
Rational elimination agrees with a separate determinant/permutation rank
oracle. Exhaustive column bases confirm greedy maximum products. All 2,600
three-element menus of nonzero ternary rows receive simultaneous witnesses;
their success unions are enumerated on 166,400 grid points. Scope controls
include a tight eight-point restricted grid, all 503 points of F_p^3 for
p=2,3,5,7, an infinite-menu construction on 81 rational fixtures, preservation
of required dirty outputs, rational coefficients and dimension one. Ten
invalid-domain calls reject. Checks remain active with optimization enabled.
These finite enumerations corroborate the written proof; they do not replace it.

## Scope and overlap

The scientific base is canonical main
19fdb086ea96af9a9f87936a2b888e10af4ed810, priority revision 8. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19228363)
specifies the original question and its limits. Search covered live open PRs,
recent account work, handoffs, active Discussions, distinctive main README and
proof terms, and merged-PR terms. The overlap helper reported 393 open PRs and
5,630 Discussion records with complete remote pagination. Sparse local notes
and arbitrary code diffs were incomplete; no search proves novelty.

Related work has different contracts. PR5997 bounds adaptive observation
capacity with a cited missing-dimension premise. PR5961 counts finite-field
minor selection. The retained centre-nonlinear-fresh-floor uses topological
dimension for continuous or semialgebraic observations. This package concerns
selection among fixed full endpoint maps, allows an arbitrary selector and
supplies no observation-capacity or header-price theorem. Those results are
context, not dependencies being replayed or verified.

## Open next questions

1. Apply the certificate to one actual source-bound complex helper menu.
   Export every globally legal leaf's full endpoint and complete invoice,
   then run the witness constructor. The missing menu and physical contract
   block a source-specific exclusion.
2. Bound approximate finite-menu endpoints under a physical norm and a bounded
   magnitude domain. This could inform rounded execution, but first needs a
   priced error tolerance and restoration contract. The exact theorem does
   not provide either. Structured questions are in TASK.json.

## Implementation limits and credit

The checker has no recursion or unbounded loop. The public matrix boundary caps dimensions
at eight, menus at 32 entries and input rational components at 64 bits.
The witness loop has at most 225 iterations. Minor enumeration is separately
capped at four by four, and every fixture domain is explicitly finite. All
functions are shorter than 60 physical lines. Internal checks use exceptions.

Managed-runtime allocation is a Power of Ten rule 3 deviation. Exact integers,
fractions and bounded containers allocate during this offline checker; no
fixed byte allocation guarantee is claimed. Input dimensions and coefficients,
fixed fixture inventories and 120-second registered timeouts bound the work.
Rule 9 has ten explicitly listed invalid-domain callbacks, used only by the
negative-control loop. The call targets and lifetimes are fixed. Warning-strict
normal and optimized execution and in-memory syntax inspection provide the
available diagnostics; no standalone static analyzer or global CI change is
introduced.

This contribution was produced by Nick Petalas. Classical finite-union,
polynomial-root, Cartesian-fiber and column-matroid arguments are credited
as methods rather than new general mathematics. The contribution is the
specified exact-interface application and its bounded certificate tools.
New proof and code are Apache-2.0. Independent human and formal proof-kernel
review are unclaimed.
