# Exact ternary full-guard law for an overlapping corank-one pair

This scoped counting proof was produced by Nick Petalas. Apache-2.0.

For orthogonal rank-one idempotents U,V on F_3^m, set P=I-U and Q=I-V.
Give every complete GL_m(F_3) header equal weight. A request passes when
every leading principal minor through its rank is nonzero. With n=m-1,
the exact joint full-guard fraction is

```text
4(49^n - 2*25^n + 19^n) / [9(3^m-1)(3^m-3)3^(2m-4)].
```

This answers the ternary case of open question 1 in
[#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261), which
supplied the all-field transfer and the binary closed form. The new proof
reduces its 36 ternary states to four classes and a cubic recurrence with
modes 49,25,19. A common passing header exists for every m>=2. The two
passing events are strictly negatively correlated, and the joint fraction
is asymptotic to (4/9)(49/81)^(m-1).

[PROOF.md](PROOF.md) contains the all-dimension argument, including the
transfer derivation and equal-header-fiber argument. No pending package
code or source bytes are imported. This is a new closed form built on the
predecessor transfer, rather than an audit of that predecessor.

## Evidence and scope

The deterministic standard-library verifier checks every source row of the
36-state transfer against the four-class quotient and the exact cubic
vector identity. It also compares the closed form with both transfer
implementations for m=2..128, enumerates complete GL headers for m=2,3,
and separately enumerates all normalized pairs YX=I_2 for m=2,3,4.
These cover 11,280 headers and 511,104 normalized pairs. The exact joint
fractions at m=2,3,4 are 1/6, 14/117 and 1727/21060.
Five controls distinguish a wrong zero-factor multiplicity, a wrong
eigenvalue, a missing mode, independent marginals and first-guard-only
admission. Success prints `PASS_TERNARY_CORANKONE_PAIR_LAW` and a receipt
bound to the six package-file hashes. Both registered modes retain the
same checks when Python assertions are disabled.

The original card is `uniform-transfer-audit`, priority revision 7. The
scope is changed to original successor counting work because the assignment
excludes an audit deliverable. [TASK.json](TASK.json) records this change.
The selected record and task catalogue in [SOURCES.json](SOURCES.json) are
historical provenance. The result is self-contained and has no live external
inputs or third-party Python requirements.

Only F_3 and two orthogonal kernel lines are covered by the new formula.
The requests have overlapping images when m>2. No producer, physical
header selection or emission, dispatch, dirty return, stock or full caller
cost is supplied. This counting result changes no selected frontier or κ.
Independent human and formal proof-kernel review are unclaimed.

## Reproduce

From the repository root, use CPython 3.12. The local interpreter path is
shown explicitly; replace it with another CPython 3.12 installation elsewhere.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/ternary-corankone-pair-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/ternary-corankone-pair-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ternary-corankone-pair-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ternary-corankone-pair-law --check-source-history
```

The last command requires the publication commit. The direct verifier also
works from a standalone copy of this package. Every registered command has
a 120-second limit. No Lean, Docker, selected-supplier or all-history replay
is needed for this scoped result.

## Implementation constraints

The verifier uses explicit failures that remain active under `-O`, direct
calls and no recursion. Every loop has a fixed finite domain. The largest
matrix has 36 by 36 entries; a normalized-pair scan retains at most 81
candidate rows and streams its 505,440 m=4 pairs. Transfer and correlation
replays stop at m=128; the proof itself covers all m>=2. Functions stay below
60 lines. Rules 3 and 9 of Power of Ten have a managed-runtime deviation:
Python allocates tuples and arbitrary-precision integers, and its standard
iterators use runtime dispatch. These are restricted to the fixed domains
above, with no plugins, callbacks or dynamically loaded code. Both registered
modes and Ruff E/F/B/UP diagnostics cover the same source. A native port
would need fixed-capacity arithmetic for this bounded replay; none is claimed.

## Open next questions

1. Find a comparably small quotient for q=5 or all odd q. Start by classifying
   safe states under diagonal row/column scalings of I-A. The two-element
   nonzero set of F_3 is special; the four classes may cease to be equitable.
   This would determine how the shared-header density depends on the field.
2. Specify a real ternary producer and price the complete shared-header caller,
   beginning with selection, emission and dirty return. Those unknown costs
   block any supplier consequence. A density alone removes no paid work.

The structured versions, including first steps and blockers, are in TASK.json.

## Predecessors and related work

- Nick Petalas's #4261, head `4728fc766b3084f3ab2f5c8543a5e74e4a12b126`,
  supplies the partial-Gram transfer. This adds its ternary closed form.
- Nick Petalas's #4227/#4228 supply single-request laws; #4239/#4240/#4246
  supply earlier joint guard laws. Their common q=3,m=2 orthogonal-rank-one
  boundary is 1/6, which equals the new formula. #4259 concerns laminar
  requests; the pair here is neither nested nor orthogonal for m>2.
- The concurrently claimed three-kernel binary law has a different field
  and a different number of requests. No result of that work is presumed.
- Cinna Davis's #4100 BIT.md supplies request context. The retained normalizer
  and recursive-closure lineage credits source527, commdata2338 and Jose Manuel;
  Chris R / Clear1nsight's #3950 is earlier deterministic-counting context.

Every predecessor retains its credit. No predecessor package is modified.
