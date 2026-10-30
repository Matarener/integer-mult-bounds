# Exponentially large concave-invoice frontiers at fixed count and mass

Safe increasing-concave pruning can retain exponentially many distinct integer
invoices even when every candidate has the same paid call count, total rank and
target. An explicit family embeds reverse subset inclusion into invoice order.
Its middle layer has `binom(m, floor(m/2)) >= 2^m/(m+1)` mutually incomparable
candidates, each with only `2m` paid calls of rank at most `2m+1`.

For `m=10`, all 252 middle-layer invoices survive such pruning. For `m=11`,
all 462 survive. The latter already exceeds PR #5778's 256-candidate input cap,
with only 22 paid calls, paid rank mass 264, and a paid rank bound of 23.

This is a scoped mathematical proof with exact finite corroboration. It is a
new worst-case family for the declared invoice order, not a physical supplier,
a power-curve crossing, a search failure, or a new multiplication exponent.

## Contract and predecessors

[Ali Romman's PR #5778](https://github.com/CrocSwap/integer-mult-bounds/pull/5778),
head `86342a33c04c72a52ddecf70b8f4b1dcb8304cef`, retains every incomparable
candidate in a declared pool. Its reducer is cited, not replayed or audited here.
The same order and signed paid-minus-target convention appear in the pinned
[invoice guide](../../docs/research/recursive-invoice-preflight.md) and comparator
by zxv. Their classical concave-order framework is a predecessor, not new work
claimed by this package. [SOURCES.json](SOURCES.json) pins that context on main;
the standalone verifier imports no predecessor code and needs no pending commit.

Write `H_r` for one paid rank-r call. For integer `m>=1` and subset
`S` of `{1,...,m}`, define

```text
P_S = sum_{i not in S} 2 H_(2i)
    + sum_{i in S} (H_(2i-1) + H_(2i+1)).
M   = 2m(m+1).
I_S = P_S minus the common productive target H_M.
```

Each block contributes two paid calls and rank mass `4i`, whether spread or
unspread. Consequently every invoice has exactly `2m` paid calls, mass `M`,
positive paid ranks at most `2m+1 < M`, and the same one-target debit. No fee
or target changes between candidates. These are synthetic accounting objects;
the common boundary text does not assert circuit compatibility or realizability.

Let `I_S <=_c I_T` mean that `I_S` costs no more than `I_T` for every
nondecreasing concave tariff `f` on nonnegative reals with `f(0)=0`.
The theorem is the exact equivalence

```text
I_S <=_c I_T    if and only if    S contains T.
```

## Proof

For a hinge tariff `h_k(r)=min(r,k)`, the change caused by spreading block i is

```text
delta_i(k) = min(2i-1,k) + min(2i+1,k) - 2 min(2i,k)
           = -max(0, 1 - abs(k-2i)).
```

To check the identity, split `k` at `2i-1`, `2i`, and `2i+1`. The four linear
pieces have values zero, `2i-1-k`, `k-(2i+1)`, and zero, respectively. The
open intervals on which these tents are nonzero are disjoint for distinct i.
In particular, `delta_i(2j)` is -1 when `i=j` and zero otherwise.

If S contains T, pass from P_T to P_S by spreading exactly the blocks in
`S minus T`. Concavity gives
`f(2i-1)+f(2i+1) <= 2f(2i)` for each such block. Summing and subtracting
the unchanged target proves `I_S <=_c I_T`.

Conversely, if S does not contain T, choose `j in T minus S`. The cost
difference `I_S(h_(2j))-I_T(h_(2j))` is exactly +1. Every other block and the
common target cancel. This tariff disproves `I_S <=_c I_T`. If strictly
increasing tariffs are required, use `h_(2j)(r)+epsilon*r` with any
`epsilon>0`. Equal rank mass makes its extra linear contribution cancel.
This proves both directions for every m, independently of the finite replay.

Distinct sets of cardinality `floor(m/2)` contain neither one another, so their
invoices are pairwise incomparable. There are exactly `binom(m,floor(m/2))`
such sets. To obtain the exponential lower bound without an asymptotic estimate,
the ratio of successive binomial coefficients is `(m-j)/(j+1)`, so a middle
coefficient is largest. The sum of the `m+1` coefficients is `2^m`; hence
that largest coefficient is at least `2^m/(m+1)`.

For example, at `m=2`, the two single-spread paid profiles are
`H1+H3+2H4` and `2H2+H3+H5`. Both have four calls, mass 12 and target H12.
Their signed cost differences are -1 at cap 2 and +1 at cap 4.

## What this changes

Equal mass, equal call count and a modest rank range do not guarantee a smaller
concave-order frontier. Within a middle-layer input pool, every safe replacement
by another pool member fails an explicit hinge test. A reducer promising to
retain every incomparable member must retain the whole pool.

This does not prevent useful typical-case pruning or a faster implementation.
It does not show that the whole cube is a frontier: its fully spread member
dominates every other cube member and would remove them if supplied. No claim
is made about representatives outside the supplied pool, approximate pruning,
or the narrower family of power tariffs. In particular, incomparability under
all concave tariffs does not establish a power-curve crossing.

## Reproduce and evidence

From the repository root, with CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/concave-invoice-antichains/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/concave-invoice-antichains/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/concave-invoice-antichains
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/concave-invoice-antichains --check-source-history
```

The read-only verifier constructs every cube member for `1<=m<=7`, checks
count, mass, the target debit, all half-integral hinge pieces and every ordered
pair against the subset relation. It separately enumerates all unordered pairs
in the m=10 and m=11 middle layers, evaluates both counter-tariffs directly on
the complete signed histograms, and requires the exact gap +1 in each direction.
It streams a digest of those certificates and prints a generated JSON receipt
bound to SHA256 hashes of all five package files. No receipt is handwritten.

Negative controls reject invalid dimensions and subsets, false or nonpositive
counter-tariffs, changed mass or targets, a changed consumer, omitted members,
duplicate members, and a wrong-cardinality layer member. Checks use explicit
exceptions and remain active under `-O`. The universal statement is the written
proof; the finite code is corroboration, not formal proof-kernel verification.

The verifier has no recursive calls. Its constructor enforces `m<=11`, each
cube has at most 128 members, and the largest layer has 462 members. It streams
pair certificates instead of retaining them. Python's managed allocation and
the fixed callback in the rejection-control helper are power-of-ten deviations:
live storage is bounded by the 462 finite invoices, at most 31 hinge values per
cube member, and one pair certificate at a time. The callback targets are the
four named local check/constructor functions in `check_controls`; they own no
external resources. A larger replay must revise these bounds and checks first.
Warning-strict normal and optimized execution are registered in VERIFY.json.

## Open next questions

Can a source-constrained family of legal constructions force a large surviving
frontier? This matters because these synthetic invoices demonstrate an accounting
limitation, not a physical search obstruction. Start with one source's permitted
rank exchanges and prove independent realizability of two disjoint blocks, with
the full target, restoration, native and compiler bill. No such construction is
provided here.

Can the power-only order safely remove more members of these specific layers?
Start by certifying the comparison for the two displayed m=2 invoices over a
named exponent interval, then seek a theorem for the family. Hinge witnesses
alone cannot answer that question. No power comparison was run as this result.

## Credit

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Credit Ali Romman for PR #5778's frontier
contract, zxv for complete signed invoice accounting, mightyOil and the retained
predecessors for the moment-order context, and Dugongue for the existing
higher-order-exchange examples that distinguish concave order from power order.
Mean-preserving spreads, hinge tariffs and the elementary binomial identities
are classical. The contribution is the explicit fixed-count, fixed-mass integer
family, its exact order embedding and the resulting pruning obstruction.
New work is Apache-2.0. No predecessor file or credit line is changed.
