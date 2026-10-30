# Sharp migration tariffs for two reusable resources

Claim type: scoped written proof with finite corroboration. This contribution
was produced by Nick Petalas. Apache-2.0.

For n>=1 consumers with fixed half-open lifetimes and nonempty fixed lists of
eligible resources from {0,1}, pointwise Hall feasibility guarantees a schedule
with at most max(0,n-2) migrations. This bound is sharp for every n. One long
flexible consumer and alternating resource-fixed short consumers attain it.
Giving the long consumer transfer price W makes the exact bill W(n-2) at n>=2.
Thus independent per-time matching can omit arbitrarily large transfer charges.
Three consumers already give the smallest obstruction to a placement that stays
fixed throughout each lifetime.

The package also constructs a minimum-cost schedule for arbitrary nonnegative
integer per-consumer transfer prices. There are at most two assignments per
elementary interval. A layered shortest path gives the optimum in O(n log n)
arithmetic operations including endpoint sorting. A path and dual arc potentials
certify optimality without repeating the optimization. See [PROOF.md](PROOF.md).

This answers the temporal-reuse boundary left outside Ali Romman's
[PR #5781](https://github.com/CrocSwap/integer-mult-bounds/pull/5781), exact head
`cb06de3a4f6e2a2c927eb3aa3f9f43a578f73a1f`, specifically its
`docs/research/compatible-resource-assignment.md` Open next questions. The
predecessor supplies the question and static interface, and is cited without
rerunning its matcher. Hall's theorem and layered shortest paths are classical
inputs. No new general matching algorithm is claimed.

## Evidence and reproduction

From the repository root, run:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-resource-migration-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/two-resource-migration-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-resource-migration-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-resource-migration-tariff --check-source-history
```

Another CPython 3.12 interpreter path can replace the absolute path. The verifier
uses only the standard library, writes no files, and emits a generated receipt
bound to the six package files by SHA-256. It enumerates all labelled lifetimes
with endpoints in {0,1,2,3,4}, all three nonempty eligibility lists and one to
three consumers, using both unit and labelled integer prices. Its independent
oracle enumerates literal assignments on every integer unit cell, including
cells without an endpoint. Additional checks cover seeded weighted timelines,
the sharp family through 512 consumers, half-open touching lifetimes, invalid
inputs and forged optimality certificates. Counts are printed by the verifier.

## Scope and limits

The executable interface accepts 1..512 consumers, integer endpoints in
0..10^6 and integer migration prices in 0..10^12. The written theorem has no
consumer bound and depends only on endpoint order; its weighted recurrence also
allows nonnegative real prices with exact comparisons.

Initial placement and release are free, and migrations are atomic. Fixed
initial/final owners, changing lists, coupled consumers, physical movement,
spare storage for exchanges and more than two resources are outside this model.
No actual caller's ownership schedule has been exported. These are abstract
transfer costs, not an admitted physical bill. No new kappa, selected-frontier
change or complete multiplication theorem is claimed. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

1. Bind one actual caller's pair of owners, fixed lifetimes and paid transfers
   to this interface. Start by exporting every live interval and legal transfer
   including restoration. A physical source adapter and transfer word are absent.
2. Determine the sharp migration count with three resources and fixed lists.
   Start with exact small timelines. A separate argument is needed; the two-state
   bound does not transfer.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Implementation limits

All production loops are bounded by 512 consumers, 1024 endpoints and two states
per cell. The independent oracle is bounded by six consumers and nine integer
time units. Functions remain below 60 lines. Python necessarily allocates dynamic
objects; the fixed input bounds limit live collections. Runtime allocation and
ordinary library dispatch are explicit Power of Ten deviations. No recursion,
dynamic code execution, external programs or inherited source imports are used.
Warning-strict normal and optimized runs keep the explicit certificate and input
checks active. The two internal assertions are redundant dimension invariants.
