# A sharp size bound for binary scalar pattern pools

For every d-dimensional off-diagonal pattern space over F2, the pool of
rank-one idempotents with a nonzero pattern has at most `2^d+d-1` elements,
independently of the number of registers. A common-row construction attains
the bound whenever at least d+1 registers are available. In particular,
two-dimensional spaces have at most five noncoordinate projectors.

Claim type: scoped written mathematical proof with finite exact corroboration.
This contribution was produced by Nick Petalas. Apache-2.0. Independent human
and formal proof-kernel review are unclaimed.

[PROOF.md](PROOF.md) gives the complete argument. Deleting the diagonal has
one lift per realizable nonzero pattern, except a single directed edge has
two. A d-dimensional space contains at most d distinct edge patterns. The
exact count is the number of realized nonzero patterns plus the number of
matrix units in the space. No predecessor scientific suite is imported or run.

## Evidence and reproduction

The read-only standard-library verifier enumerates binary projectors on five
and six registers. A separate oracle tries every diagonal completion for
every realized pattern, including the zero-pattern boundary. It also checks
all pairs of distinct realized five-register patterns, explicit attaining
stars through dimension ten with padded spectators, and semantic controls.
These checks corroborate the new proof, rather than reproducing the
four-register flag classification.

Local CPython 3.12.15 checks pass for 2,501 noncoordinate projectors,
141,888 diagonal completions, 110,685 spanning pairs and 55 attaining star
shapes containing 4,237 literal projectors. Five malformed dimensions and
seven semantic control groups pass. Three disposable optimized-code mutants
reject a missing edge charge, missing second lifts and admitted nilpotents.
The two registered commands took 0.305 and 0.261 seconds in individual local
runs, below their 120-second limits. These timings check the replay budget.

From the repository root, run:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pattern-pool-cardinality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/pattern-pool-cardinality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/pattern-pool-cardinality
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/pattern-pool-cardinality --check-source-history
```

Any CPython 3.12 executable may replace this installation path. A direct run
prints `PASS_PATTERN_POOL_CARDINALITY` followed by a generated JSON receipt
with exact counts and SHA256 hashes of all six package files. Save stdout
outside the checkout. There is no handwritten scientific receipt. Direct
replay works without Git or network; provenance validation needs full Git
history. The verifier does not read predecessor files at runtime.

## Sources, scope and stopping decision

The source question is the Open next questions section of woklerx's
[PR1456](https://github.com/CrocSwap/integer-mult-bounds/pull/1456), at
`83b6ad2ace819a96128131a3600ee914a66dd0dd`. Its cyclic-pattern uniqueness
argument and arbitrary-role Laurent method retain their credit. Ali Romman,
eumemic and the register-model lineage remain predecessor credit.
woklerx's [PR1846](https://github.com/CrocSwap/integer-mult-bounds/pull/1846)
supplies the separate finite four-role flag classification. Neither result
is audited here. Exact retained source blobs are pinned in SOURCES.json.

Base canonical main is `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority
revision eight. The selected-baseline metadata control passed. The card is
changed to a scalar reconstruction side result. It supplies a bounded pool
before word synthesis, and meets no native supplier acceptance gate.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19217787)
records this scope. Stop at the sharp size theorem; no word search is reserved.

The joint image of the pool has dimension at most its size, giving a proper
common invariant subspace when the ambient dimension exceeds the bound and
the pool is nonempty. Coordinate projectors are excluded. Interleaving them
can destroy this particular invariant subspace. This does not eliminate a
complete two-relation word or extend the rational span-six obstruction of
PR5231, which has different premises and a different conclusion.

Entry searches covered live open PR bodies, recent account PRs, active
Discussions and the latest handoff comments, the cached card search, merged
pattern/dihedral searches, and all main package READMEs for distinctive
pattern/fiber/count terms. The cached helper reports sparse local omissions;
Git searches cover committed READMEs, not arbitrary nested code, unpublished
work or every historical PR body. No match is not proof of novelty.

The selected frontier is unchanged. Rational address frames, chronology,
full native/physical/precision/tape/ownership costs, independent targets,
compiler admission and the complete multiplication theorem remain outside
scope. No Lean, Docker, historical scientific replay or selected operator
replay is run. The universal result rests on the written proof.

## Open next questions

- Which pattern spaces attain the maximum? Begin by imposing equality in
  both the realized-pattern and edge counts, then classify the resulting
  directed-edge sets. This could remove redundant extremal search families;
  the present proof supplies an attaining family without classifying all of them.
- What is the sharp joint-image dimension at fixed d? The cardinality bound
  gives a finite ambient threshold for irreducible pools, but can be loose.
  Start with d=2 and retain every possible diagonal lift. Adding coordinate
  gates to full words is a separate obstacle.

Structured questions and blockers are in TASK.json.

## Verifier implementation limits

All loops have fixed finite domains. Exhaustive oracle widths are five and
six; stars use at most eleven registers and dimension ten. The plane pass
accepts at most 500 realized patterns and counts spanning pairs, not distinct
planes. No recursion, subprocess, network or scientific output write occurs.
Python dynamically allocates bounded tuples/maps; static allocation is not
available in this runtime. At most the fixed projector/fiber tables, a
64-completion oracle set and one star of at most 1,033 projectors are live.
Functions are below sixty physical lines. Explicit exception checks survive
optimized execution, and registered commands make warnings errors. Package
hashing reads exactly six bounded source files.
Syntax compilation and the standard-library indentation check pass. No
dedicated linter is installed on this host.
