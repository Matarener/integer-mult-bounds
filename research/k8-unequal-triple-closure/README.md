# Every improving PR1322 constant-gauge move needs four helpers

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped computer-assisted negative proof with an exact finite certificate.**
In both orientations, the final historical k8 gauge vector of
[PR1322](https://github.com/CrocSwap/integer-mult-bounds/pull/1322) cannot
improve under independently chosen integer shifts of any three eligible
helpers. Every improving move in this fixed constant-gauge model must
change at least four helpers. No new kappa is claimed.

PR1322 proved closure for common shifts on triples and left unequal shifts
open. It also left arbitrary pair stationarity at its final vector unclaimed.
The new result closes both gaps. It cites the predecessor tariff and vector;
it does not audit that contribution or rerun its scientific suite.

## Result and evidence

Write k for the retained vector and F for the complete scalar gauge
objective, including both boundary scales and the unit-coefficient discount.
For every integer displacement d with at most three changed helpers,

```text
F(k+d) - F(k) >= 8 sum_h max(0, |d_h|-3) >= 0.
```

[PROOF.md](PROOF.md) gives the clipping lemma, its exact finite premises,
the singleton/pair decomposition and the disconnected-component argument.
Each outward clipping step beyond magnitude three costs at least eight
real-component primitives. This reduces the infinite domain to [-3,3]
without relying on a solver's failure to find a witness.

The standard-library verifier independently extracts the valuation graph
from the retained source archive and consumes PR1322's final vector. In each
orientation it checks all 1,540 clipping rows, with minimum lower bound 8,
and obtains minimum zero on every tested block:

| Class | Blocks | Independent shift assignments checked |
| --- | ---: | ---: |
| Singletons | 237 | 1,659 |
| Pairs | 27,966 | 1,370,334 |
| Connected triples | 49,898 | 17,115,014 |

The graph has 2,414 interaction edges and 15,619 incident ADD records per
orientation, with multiplicity. Disconnected triples reduce to their
singleton/pair components. The theorem covers all 2,190,670 three-helper
subsets; the verifier does not execute all shift assignments on every
disconnected triple. Forty synthetic graphs supply 13,720 literal-objective
comparisons, and tariff controls exercise the zero-exponent discount and
paid boundaries. One rejection control prevents clipping without its
premise. Thirty-two complete-objective controls include shifts of magnitude
2^32. The stdout receipt is generated and bound to input and
package hashes; no receipt is handwritten.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/k8-unequal-triple-closure/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/k8-unequal-triple-closure/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/k8-unequal-triple-closure
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/k8-unequal-triple-closure --check-source-history
```

Another CPython 3.12 executable can replace that local path. The direct
marker is `PASS_K8_UNEQUAL_TRIPLE_CLOSURE`. Each registered command has a
120-second limit and writes no files. The committed-byte/history command
requires a committed package and full Git history. Direct replay also works
from an official Git-free export containing its two declared live inputs.

## Scope, credit and provenance

Philipp / mightyOil supplies PR1322's open question, final vector, objective,
common-shift triple result and graph decomposition, following PR1310/1263.
Hanson Sun / bbMisk supplies PR1214's exact pair method; woklerx supplies
PR1161's constant gauge mechanism; Sagar Thakrar supplies the retained
copy-init lowerer. Jeremy Kothe, Rohan Arun, Hao Yan / icekylinx, Douglas
Colkitt and the original supplier/frame/native/compiler lineage retain their
credit. Their files and credit lines are unchanged. The new contributions
are the two-neighbor clipping certificate and unequal-triple closure at
this final vector. General integer-cost decomposition is not claimed as
a new mathematical technique.

Scientific base is canonical main
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the historical source archive, vector,
question, task catalogue and selected record. The current selected binding
orientation passed at kappa 0.003125804. This historical scalar result does
not transfer automatically to that changed P104 supplier. The card's scope
is explicitly changed in [TASK.json](TASK.json).

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279574)
was preceded by live handoff, reservation, open/merged PR, recent-account
and main README searches. The overlap cache covered 337 open PRs and 5,949
Discussion records with complete remote pagination; only 89 of 8,623 local
notes were materialized. Main README searches supplemented those sparse
notes. These checks do not exclude unpublished work or establish global
novelty. The time-dependent ADD-once bipartite model of PR6130 is different
from this fixed cyclic graph with constant gauges.

Four or more changes, temporal gauges, a changed graph or lowerer, native
integration, ownership, full precision, stock and tape costs remain outside
scope. No circuit, recursive paid profile, selected frontier or inherited
framework assumption is changed. Selected scientific replay, predecessor
scientific suites, Lean and Docker were not run. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

Can at least four independently changed helpers improve this final vector?
Start with one explicit displacement and the complete boundary-inclusive
objective. A strict witness would identify the next coupled move; no such
witness or larger-support optimality certificate is supplied. This result
does not authorize an automatic larger historical construction campaign.

## Implementation constraints

The new verifier is nonrecursive, uses exact integers, has no subprocess,
network, dynamic import or file-write path, and keeps every function below
60 physical lines. Source hashes are checked before parsing. The source
domain has at most 25,000 events per orientation, 16,000 retained terms,
237 helpers, clipping radius 40 and 60,000 connected triples. The largest
bounded census has 60,000 times 343 assignments. Input handles have scoped
cleanup, failures propagate, and explicit checks remain active under -O.

Power of Ten rule 3 has a managed-runtime deviation. CPython, JSON and tar
parsing allocate dynamically during this finite command. Reads are capped
at 64 MiB per authenticated input, each decoded member at 16 MiB, and live
tables are bounded by the domains above. This is not a fixed-allocation or
real-time claim. A streaming parser/fixed-storage representation is required
before admitting unbounded data or a persistent service. Warning-strict
normal/optimized execution and in-memory compilation provide diagnostics;
no external linter or type analyzer is claimed.
