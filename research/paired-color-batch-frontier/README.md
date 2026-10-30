# Exact paired-color batch frontier

**Scoped written proof with finite corroboration; no new kappa.**
For two targets of each of `m` colors and capacity-three fixed-width
batches, the exact frontier is

```text
ceil(2m/3) <= B <= m,     I_min(B) = 2m-B.
```

Here `I` counts occupied colors across batches. For bill `A B+C I`, one
batch per color is optimal when `A<C`; minimum batch count is optimal
when `A>C`. Every frontier point ties when `A=C`.

At the declared exchange-only prices `A=6,C=12`, minimizing batch count
can cost a sharp `10/9` times the optimum: three colors cost `60` instead
of `54`. The better grouping removes 10% of this exchange sub-bill.
[PROOF.md](PROOF.md) gives the quantified proof and explicit groupings.

This answers a scoped optimization step motivated by unpaidmoon's
[PR #5538](https://github.com/CrocSwap/integer-mult-bounds/pull/5538),
first Open next question. Its occupied-color result is cited, not audited
or replayed. The new point is that minimizing batches and minimizing color
macros can conflict; both statistics must enter the objective.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/paired-color-batch-frontier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/paired-color-batch-frontier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/paired-color-batch-frontier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/paired-color-batch-frontier --check-source-history
```

The direct checker emits `PASS_PAIRED_COLOR_BATCH_FRONTIER`. It independently
enumerates every capacity-three set partition for `1<=m<=5`, constructs every
frontier point through `m=256`, checks rational positive-price optima against
the enumerated partitions through `m=5`, checks every ratio equality through
`m=256`, and rejects fourteen
malformed inputs. `--receipt /absolute/scratch/path.json` writes generated
evidence bound to SHA256 hashes of all six package files. No receipt is
hand-written or required as an input.

Local normal and optimized checks pass 64,098 enumerated partitions,
11,136 attaining groupings, 245 rational price cases and fourteen rejection
controls. Both registered commands pass. Hosted CI is reported separately
in the contribution PR.

The verifier is read-only unless given that output option. The enumeration
uses an iterative stack with an exact finite node bound, at most ten target
levels and no recursion. Python's managed allocations are a Power-of-Ten
deviation: live enumeration state has at most 101 stack entries, with at
most ten blocks of at most three integers each; constructed instances have
at most 512 targets. No native build, Lean or Docker run is required.

## Scope and limits

The mathematical result allows unrestricted grouping and holds a common
reservoir width fixed. Only the six placement and twelve per-color shuttle
exchanges are priced in the `6B+12I` example. No actual layout is regrouped,
and no production color multiplicity, legal physical reorder, invariant
position-mod-K colors, complete tariff or caller is established.

The selected frontier and the five framework assumptions are unchanged.
Independent human and formal proof-kernel review are unclaimed. Metadata
and source-history checks authenticate provenance and publication bytes;
they do not prove the theorem. The finite enumeration corroborates the
written proof rather than replacing its unbounded quantifiers.

## Open next questions

1. Does a source-bound CRT region admit any nontrivial regrouping with a
   common reservoir width and stable colors? First identify one legal
   tree/control/reservoir region and price its movement, restoration,
   additions and repair. Blocker: this package supplies no such caller.
2. What is the analogous exact frontier for other capacities or unequal
   color multiplicities? Start with capacity four and explicit multiplicity
   vectors. It would improve abstract screening; physical relevance still
   requires the first question. No larger search is included here.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.
Credit unpaidmoon #5538 for the occupied-color tariff and its open question;
Cinna Davis #4100 for the CRT construction and exchange counts; Hiroki
KUMAZAKI #4174 for the layout; and Ryanson Jonathan #4329 for the guard and
placement context. Their work is retained unchanged. Exact main-source
pins are in [SOURCES.json](SOURCES.json); [TASK.json](TASK.json) records the
changed scope relative to the current `uniform-transfer-audit` card.
The frontier proof, attaining family and standalone finite checks are new
in this contribution. No literature-priority claim for colored packing is made.
