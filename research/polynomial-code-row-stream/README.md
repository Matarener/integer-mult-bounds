# Incremental polynomial-code rows in the complete affine/vector replay

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: measured verifier improvement with a scoped equivalence proof
and exact finite conformance evidence. No new kappa is claimed.

The complete nine-screen affine/vector certificate takes a median
0.802367 seconds with the incremental row engine, compared with
0.870415 seconds using Ross Richardson's published mask-cache method.
That is an additional 7.82% reduction on this host. The original source
takes 2.723721 seconds; most of that larger improvement comes from the
credited mask-cache method.

Five fresh-process samples per engine alternate in original/cached/incremental order. Every complete
output is byte-identical, with zero errors. The ranges are 0.800517 to
0.811994 seconds incremental, 0.868530 to 0.872415 seconds cached, and
2.705994 to 2.787996 seconds original. [BENCHMARK.json](BENCHMARK.json)
contains the generated raw samples and implementation hashes. These are
local macOS arm64 / CPython 3.12.15 measurements, not a cross-host guarantee.

## Changed mechanism

For the same base row, the XOR-index permutation identity is

```text
P_i(base) = P_(i xor j)(P_j(base)).
```

The adapter keeps one preceding result and chooses the cheaper of the
direct and incremental paths. [PROOF.md](PROOF.md) proves the exact
invariant, including changed bases, widths and repeated indices. The
3,074 original production row requests use 5,501 block swaps instead of
12,949. Every full row remains in the original order and every original
elimination and certificate check still runs.

This answers the polynomial-code performance question in
[Victor Li's PR2210](https://github.com/CrocSwap/integer-mult-bounds/pull/2210),
Open next question 1 in the retained production package. Ross Richardson's
[PR1075](https://github.com/CrocSwap/integer-mult-bounds/pull/1075) already
provides mask caching. The new result is the additional incremental row
step and its application to the complete four-code/five-Leech replay.
No predecessor mathematical result is audited as this deliverable.

## Evidence and reproduction

From the repository root, use the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/polynomial-code-row-stream/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/polynomial-code-row-stream/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/polynomial-code-row-stream
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/polynomial-code-row-stream --check-source-history
```

Another CPython 3.12 path may be substituted. The final command requires
committed package bytes and full Git history. The expected direct marker
is `PASS_POLYNOMIAL_CODE_ROW_STREAM`, in a generated stdout receipt bound
to all package-file hashes. Default replay writes no artifacts.

The verifier checks 2,122 exhaustive small row/index pairs, 21,865 wider
and interleaved-history fixtures, one maximum-width fixture, all 3,074
production rows, and the complete certificate with all three engines.
Twelve invalid warm-state inputs reject before mutation. Two deliberately
corrupted internal states produce different rows under the literal oracle.
All scientific checks remain enabled under `-O`.

The opt-in accelerated command is

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/polynomial-code-row-stream/replay.py
```

Add `--engine cached` or `--engine original` for the two comparators.
`benchmark.py` performs five alternating fresh-process triples and prints a
new timing receipt. Source authentication, imports, all nine screens,
full certificate comparison and output are inside every timed process.
The slower differential verifier is outside that timing comparison.

The profile places the original dominant cost in XOR permutation. The
adapter removes repeated geometry division and then reduces block swaps;
the untouched Leech screens and binary elimination limit further gains.
The host had 18 logical cores and load averages 2.22, 3.12 and 2.54 at
entry. Other work may share the host, so timing is interleaved and descriptive.
Profiler runs and preliminary timings are excluded from BENCHMARK.json.

## Scope and provenance

The exact base is canonical main
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8.
[SOURCES.json](SOURCES.json) binds 41 live inputs, including the complete
local import closure, unchanged fixture/certificate, retained cache engine
and upstream files read by the original certificate. Provenance-only rows
retain the source question and predecessor notes. No historical package,
production source, certificate, selected record or upstream file changes.

The original `replay-runtime` card is refined to this historical verifier
cost. [TASK.json](TASK.json) records the scope and
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272230).
Live PRs, recent account work, handoffs, active Discussions, merged-PR
searches and all-main README terms were checked. The overlap helper's
sparse local-note coverage is incomplete; no novelty guarantee or global
literature-priority claim follows.

The adapter admits widths through 2^21 and is used here only by the four
fixed polynomial-code witnesses. It temporarily replaces one module
reference in a standalone process. Concurrent use and production adoption
are outside the contract. The original screen conclusions are inherited;
this package preserves their finite computation rather than strengthening
them. Independent human and formal proof-kernel review are unclaimed.
Native, compiler, precision, tape, BIT, outer and selected cold replays are
unrun. The five selected framework assumptions retain their status.

## Open next questions

Can this incremental engine be adopted in the production polynomial-code
caller after a source-bound compatibility review? Begin with one explicit
caller substitution and regenerate all affected pins and certificates.
The opt-in replay makes this reviewable, but production integration and
its dependent source manifests are outside this package. No further
optimization or scientific construction search is reserved.

## Credit

Douglas Colkitt supplied the original affine/vector screens, coefficient
codes, XOR operation and certificate. Jerry Chen / CubeJerry supplied
PR898's Leech byte lanes. Victor Li / VictorLiwentao supplied PR2210's
production wiring and the explicit polynomial-code performance question.
Ross Richardson supplied PR1075's mask-cache implementation, retained
unchanged as the stronger comparator. The permutation group identity and
incremental traversal are standard techniques. The new implementation,
scoped consumer proof and complete-command evidence were produced by
Nick Petalas. Every predecessor file and credit line remains unchanged.
