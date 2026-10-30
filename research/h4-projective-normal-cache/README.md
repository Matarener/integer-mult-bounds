# Complete H4 replay takes 45.2% less wall time

This contribution was produced by Nick Petalas. Apache-2.0.

Exact projective-normal reuse reduces the complete H4 certificate replay's
local median wall time from **2.462 s to 1.350 s**, a **45.2% reduction**.
Five alternating fresh-process pairs emit identical complete stdout, with
zero errors. This is a measured verifier improvement with a scoped
implementation-equivalence proof and finite conformance evidence.
No new mathematical bound or kappa is claimed.

Jose Manuel / jmbarrancoml's [PR1867](https://github.com/CrocSwap/integer-mult-bounds/pull/1867)
retains the H4 theorem, geometry, witness construction and complete
scientific checks. Its source remains unchanged. This package supplies an
opt-in accelerated command. It does not replace the predecessor's default
replay or provide a new scientific review of its theorem.

## Change and evidence

The complete-command profile puts 4.805 of 6.493 profiled seconds in
hyperplane construction. Different spanning triples repeatedly produce
normals for the same hyperplane. The accelerator computes an exact
primitive integer key for each normal's Q(sqrt(5)) projective class.
It scans the sixty roots only on the first occurrence of a class.

All 34,220 triples still undergo cofactor construction. The 33,300
nonzero normals still undergo the original annihilation checks against
their three generating roots. There are 1,320 distinct projective classes,
so the change avoids 31,980 repeated root scans. It retains the first
original normal, every flat mask and dictionary insertion order.
[PROOF.md](PROOF.md) proves exactness of the key and complete output.

Conformance checks cover:

- 624 nonzero test vectors, 272 projective classes and 6,864 nonzero
  golden-field scalings against a separate exact rational-division key.
- Four complete original/accelerated flat dictionaries, using the original
  order, reverse order, a cyclic order and alternating root signs. Every
  mask, first normal and insertion position agrees.
- Byte-identical complete historical replay, including its 5,280 checked
  representative support witnesses, reflection orbits, budget checks and
  eight inherited corruption rejections.
- Eight new rejections for malformed normals, capacity overflow, a
  deliberately colliding key and changed source bytes. The exact capacity
  boundary is also accepted.

The preserved support-witness digest is
`8b0a00c1e8bc012e7f9b620e0ed2c23384f08ea51f7a023f03279e34e9704ab6`.
The complete stdout digest is
`54a65418396d5d8e4989ae02c13e0abe0b34760e6cc43ee3d0e7382ef4482853`.
These are inherited output identities, not new theorem certificates.
The new verifier generates its own source-hash-bound receipt on stdout.

## Measurement

CPython 3.12.15, macOS 27.0.1 arm64, eighteen logical CPUs. The opening
load averages were 2.55, 2.73 and 2.60. Other research processes may share
the host. Timed commands run serially, with pair order alternating to
limit drift. Profiling runs are excluded. A preliminary timing run that
overlapped conformance was discarded.

Each sample includes interpreter startup and the complete replay.
Both sides use `-I -W error -B`, the same interpreter and the same source
domain. The accelerated side also pays for source authentication and
loading. Each subprocess must exit zero, emit no stderr and produce the
same complete stdout. The cache starts empty in each process.

| Pair | Order | Baseline seconds | Accelerated seconds |
| --- | --- | ---: | ---: |
| 1 | baseline, accelerated | 2.444386166 | 1.366814083 |
| 2 | accelerated, baseline | 2.438297166 | 1.409753166 |
| 3 | baseline, accelerated | 2.462136750 | 1.349535167 |
| 4 | accelerated, baseline | 2.559169750 | 1.342320875 |
| 5 | baseline, accelerated | 2.469625000 | 1.329154208 |

Baseline range is 2.438 to 2.559 seconds; accelerated range is 1.329 to
1.410 seconds. All five pairs improve. The measured reduction is below
the share spent in the changed component. This is a single-host result,
not a portable performance guarantee. No timing threshold runs in CI.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/h4-projective-normal-cache/replay.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/h4-projective-normal-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/h4-projective-normal-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/h4-projective-normal-cache
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/h4-projective-normal-cache --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/h4-projective-normal-cache/benchmark.py --pairs 5
```

Another CPython 3.12 installation may replace the displayed interpreter.
The registered normal and optimized conformance commands each have a
120-second limit. Direct replay and verification write only stdout.
The benchmark also emits its generated timing receipt only to stdout.
The committed-byte check requires a committed package and full Git history.

## Scope, provenance and constraints

Base is canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision 8. The source-binding orientation passed. Selected kappa remains
`0.003125804`. The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272415)
and [TASK.json](TASK.json) record this original replay-runtime question.
Live handoffs, open and merged PRs, recent account work, reservations and
distinctive main README searches were checked. Sparse local-note coverage,
unpublished work and arbitrary historical diffs remain limitations.

[SOURCES.json](SOURCES.json) authenticates the one executed predecessor
file by SHA256 and Git blob. The loader reads those exact bytes and
compiles them with optimization disabled, including when this driver uses
`-O`. The cache is invocation-local and cannot outlive its source instance.
Source changes reject before execution. It does not infer dependencies of
a changed future predecessor.

New functions are at most 42 physical lines. The fixed sixty-line domain
bounds triple loops by 34,220 iterations and the production cache by 1,320
classes. Integer input coefficients are bounded by 2^32. The standalone
key tests have 624 vectors and eleven scalars. Benchmarking permits five
through fifteen pairs, with a sixty-second timeout for each subprocess.

Power of Ten deviations are explicit. CPython and its libraries allocate
dynamically; finite input and collection bounds replace a fixed-allocation
guarantee. The authenticated predecessor retains its existing recursive
clique search, bounded here by clique size thirteen. Source execution and
the one function replacement use dynamic dispatch over exact, pinned
source; the conformance and source-corruption controls exercise that
boundary. These exceptions do not expand the inherited search domain.
Warning-strict normal and optimized runs, syntax/function-size inspection
and the repository package checks supply the diagnostics used here.

Native implementation, ownership, physical caller, precision, compiler,
outer admission and a complete multiplication theorem are outside this
tooling change. The selected cold replay, Lean and Docker were not run.
Independent human and formal proof-kernel review are unclaimed.

## Related open work

No open PR found at the pre-claim checkpoint studies H4 projective-normal
reuse or this complete H4 replay. Other replay-engineering work uses
different sources and bottlenecks. This statement is refreshed in the PR
body before publication.

## Open next questions

Can exact cofactor construction be shortened after scan reuse? First
profile the complete accelerated command, then compare an exact algebraic
replacement while retaining all normal and witness outputs. No replacement
or performance result is supplied here. This is a separate future task;
the present contribution stops after its first measured improvement.

## Credit

Jose Manuel / jmbarrancoml retains PR1867's mathematical results,
coordinates, complete support checks, witness search and implementation.
Its credited Denney, Bao, Thiago Goulart / Tuafo, Joel Pulikkan,
DreamingOfClouds and retained decoder/accounting predecessors keep their
attribution. Primitive integer normalization, quadratic-field conjugation
and projective equality are classical. The new contribution is this exact
reuse implementation, its equivalence proof, conformance checks and
complete-command measurements. No predecessor credit line was edited.
