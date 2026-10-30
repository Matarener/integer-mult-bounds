# A smaller exact chart-127 scalar suffix

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: a finite exact circuit certificate with a scoped substitution
proof. On the selected PR6030 word, replace the chart-127 scalar interval
`[17461,20431)` as follows:

```text
events                    2970 -> 2851       saving 119
real scalar allowance    25988 -> 23478      saving 2510
complete-word events     22803 -> 22684
complete-word allowance 189428 -> 186918
```

All permutations, signs and power-of-two scales are charged. There are
2,402 ADDs and 449 SCALEs in the replacement, versus 2,691 and 279 before.
No additional roles are used. The ordered MOVE, INIT, CLEAR and COPY events,
productive targets and recursive paid profile are unchanged. No new kappa
or selected-frontier change is claimed.

This answers the second-disjoint-block question in CubeJerry's
[PR #6116](https://github.com/CrocSwap/integer-mult-bounds/pull/6116),
head `815dd9844f1b43a4488ad06d09141a827621078c`.
That contribution treats the separate first 9,895-event prefix. Its
construction and checks are cited, not imported or replayed here.
The new suffix circuit applies its whole-block synthesis approach to
a different exact matrix. No combined word containing both improvements
is claimed or tested.

## Exact boundary and evidence

Ordinals are zero-based and the upper endpoint is excluded. The retained
event at 20431 is `ADD 533,453,2` at chart 245. It is an observation boundary,
and the replacement stops before it. Every replacement operand is an
already available role at chart 127. It uses only invertible dyadic
ADD/SCALE operations and preserves the entire arbitrary-entry linear map.
[PROOF.md](PROOF.md) explains the substitution and exact pricing.

The constructor uses sparse Fraction rows. A separate integer-row engine
compares all **297,025 coefficients** of the 545-by-545 matrices. One role,
758, is touched by the original circuit and is identity in the final map;
the replacement leaves it untouched. Both matrices include that role.
The maximum intermediate row l1 norm relative to the local entry values
is exactly 67 for both circuits. This is a local exact bound, not a
rounded whole-word precision theorem.

Ali Romman's source-authenticated complete-word interpreter then checks
the new 22,684-event word, all 638,401 endpoint coefficients, chronological
charts and storage. It reports 770 public inputs, 29 owned fields,
31 owned lifetimes and peak 13 owned fields. The unchanged paid profile is
`{1:2219,2:457,3:496,4:100,5:163,6:11,7:6,8:1}`, with rank mass 5,952.
The target histogram is included in the generated receipt.

Eleven negative controls reject a sign fault, missing scale, wrong chart,
unavailable or aliased source, zero/non-dyadic/nonunit coefficients and
corrupted scientific inputs. A two-role hand-computed dyadic matrix and
the exact inverse block are positive controls. The synthesis stopped at
its first candidate that improved both event count and charged allowance.
No alternative pivot orders or further blocks were searched.

## Reproduction

From the repository root, with the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-chart127-suffix/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/p104-chart127-suffix/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-chart127-suffix
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-chart127-suffix --check-source-history
```

An equivalent CPython 3.12 path can replace the local path. Direct success
prints `PASS_P104_CHART127_SUFFIX events=2970->2851 allowance=25988->23478`.
Both registered commands have 180-second timeouts and use explicit checks
that remain enabled under optimization.

The direct command accepts `--receipt /absolute/external/path/result.json`
for a generated receipt bound to all package and input file hashes, and
`--emit-word /absolute/external/path/WORD.json` for the complete candidate.
Both outputs must be absent and outside the checkout. Default replay writes
nothing. No generated log, candidate word or receipt is kept in the package.
The direct verifier also runs in a Git-free export with both declared inputs.

Canonical compact sorted-key JSON hashes, excluding a trailing newline:

```text
replacement: ed9afcb5d55fe74f4306d8bc8928f59f0ee8201882597672013c90f4cb11c896
whole word:  3dac0f56a818f426d609b0bcbdf412777fb46a4bbd49a9dde0b23fe7fe978d96
```

## Scope and implementation limits

This is a local exact substitute and complete scalar-word check. The native
operators and caller are unchanged premises. Full native, physical-caller,
compiler, rounded precision, stock, tape and outer cold replays were not run.
No optimality, measured runtime gain, complete supplier admission or complete
multiplication theorem follows. All five selected framework assumptions remain.
Independent human and formal proof-kernel review are unclaimed.

The constructor uses at most 799 rows, 26,000 scalar events and 2,000 sharing
steps; the actual domain has 545 rows and 245 sharing steps. Each step removes
at least two sparse entries. Elimination has one pivot per role, and the
permutation phase has at most one charged exchange per role. Every emitted
coefficient is checked against a 16-bit numerator/denominator capacity.
There is no recursive call, solver or network access. Python allocation is
a managed-runtime deviation from fixed allocation; live matrix sizes are
bounded by these capacities. Each function is below 60 physical lines.
The only dynamic source execution is the pinned, explicitly selected
complete-word interpreter. Normal and optimized warning-strict execution
supply language diagnostics; no separate static analyzer is installed on PATH.

## Open next questions

- Can the two disjoint replacements here and in PR #6116 pass one complete
  supplier, native, caller and precision replay? Start with the emitted
  words and source-bound interval substitution. Pending independent review
  and the complete integration replay remain blockers.
- Can a changed helper or paid trajectory use the smaller scalar allowance
  without spending it in restoration or target debits? First specify a
  complete arbitrary-dirty boundary and price its full signed invoice.
  This circuit by itself changes no recursive saving.

## Credit and provenance

The new circuit, standalone constructor and certificate were produced by
Nick Petalas. CubeJerry supplies PR #6116's whole-block row-synthesis approach
and second-block question. Sparse sharing, dyadic Gaussian elimination and
elementary exchanges are classical, and no priority is claimed for them.
DreamingOfClouds supplies PR #6030 and #5907, Ali Romman supplies the retained
word/checker lineage, Matarener supplies PR #5975's global scalar-resynthesis
question, and Mason Hale supplies PR #5811. Cinna Davis, Gareth Davidson,
David Arias, Douglas Colkitt and all retained P104/native/compiler contributors
keep their predecessor credit. No predecessor file or credit line is changed.

The scientific base is canonical main
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8, with selected
conditional kappa `781451/250000000`. Source-binding orientation passed.
[SOURCES.json](SOURCES.json) pins the word and reused checker. The pending
PR #6116 is scholarly context, not a live-code or Git-history dependency.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19242050)
initially named the larger suffix `[17461,22795)` as one chart-127 block.
The [scope update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19242077)
records its intervening chart-245 event and the narrower delivered interval.
The larger interval was not synthesized. TASK.json explicitly changes the
scalar-to-moment card to a local circuit side result; its signed moment is
unchanged. Live claims, open PR bodies, main-tree notes and merged PR searches
were checked. Sparse local and arbitrary historical-diff coverage is incomplete;
a search miss is not a novelty certificate.
